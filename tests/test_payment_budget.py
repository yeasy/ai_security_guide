"""Executable budget invariants against real SQLite connections."""
import concurrent.futures
import pathlib
import json
import subprocess
import sys
import tempfile
import threading
import types
import unittest

from examples.payment_budget import ledger


def seeded(module, path):
    book = module.Ledger(path)
    book.add_grant("grant", "alice", "shop", 10000, 1000)
    return book


def concurrent_reservations(module, path):
    start = threading.Barrier(2)

    def request(number):
        book = module.Ledger(path)
        try:
            start.wait(timeout=5)
            try:
                return book.reserve(f"operation-{number}", "grant", "alice", "shop", 6000, now=100)
            except module.LedgerError as error:
                return str(error)
        finally:
            book.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        return list(pool.map(request, range(2)))


def assert_atomic_reservation(test, module):
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "ledger.sqlite"
        book = seeded(module, path)
        try:
            outcomes = concurrent_reservations(module, path)
            test.assertCountEqual(outcomes, ["RESERVED", "BUDGET_EXCEEDED"])
            test.assertEqual(book.balance("grant")["available_minor"], 4000)
        finally:
            book.close()


def assert_replay_binding(test, module):
    with tempfile.TemporaryDirectory() as directory:
        book = seeded(module, pathlib.Path(directory) / "ledger.sqlite")
        try:
            args = ("operation", "grant", "alice", "shop", 3000)
            test.assertEqual(book.reserve(*args, now=100), "RESERVED")
            test.assertEqual(book.reserve(*args, now=101), "RESERVED")
            test.assertEqual(book.balance("grant")["available_minor"], 7000)
            with test.assertRaisesRegex(module.LedgerError, "OPERATION_CONFLICT"):
                book.reserve("operation", "grant", "alice", "shop", 4000, now=100)
        finally:
            book.close()


class PaymentBudgetTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.directory.name) / "ledger.sqlite"
        self.book = seeded(ledger, self.path)

    def tearDown(self):
        self.book.close()
        self.directory.cleanup()

    def reserve(self, operation="operation", amount=6000, **changes):
        fields = dict(grant_id="grant", user="alice", recipient="shop", amount_minor=amount, now=100)
        fields.update(changes)
        return self.book.reserve(operation, **fields)

    def test_reserve_charges_available_budget(self):
        self.assertEqual(self.reserve(), "RESERVED")
        self.assertEqual(self.book.balance("grant")["available_minor"], 4000)

    def test_reserving_exactly_the_remaining_budget_is_allowed(self):
        self.assertEqual(self.reserve(), "RESERVED")
        self.assertEqual(self.reserve("second", amount=4000), "RESERVED")
        self.assertEqual(self.book.balance("grant")["available_minor"], 0)
        with self.assertRaisesRegex(ledger.LedgerError, "BUDGET_EXCEEDED"):
            self.reserve("third", amount=1)

    def test_two_connections_cannot_reserve_more_than_budget(self):
        assert_atomic_reservation(self, ledger)

    def test_same_operation_replay_is_bound_and_charged_once(self):
        assert_replay_binding(self, ledger)

    def test_operation_id_binds_every_business_argument(self):
        self.reserve()
        self.book.add_grant("other", "alice", "shop", 10000, 1000)
        for changes in ({"grant_id": "other"}, {"user": "bob"}, {"recipient": "other-shop"}, {"amount_minor": 5000}):
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(ledger.LedgerError, "OPERATION_CONFLICT"):
                    self.reserve(**changes)

    def test_amount_and_budget_require_positive_integer_minor_units(self):
        for value in (0, -1, True, False, 1.5, "6000", 2**63):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ledger.LedgerError, "INVALID_AMOUNT"):
                    self.reserve(amount=value)
                with self.assertRaisesRegex(ledger.LedgerError, "INVALID_AMOUNT"):
                    self.book.add_grant("bad", "alice", "shop", value, 1000)
        self.assertEqual(self.book.balance("grant")["available_minor"], 10000)

    def test_scope_and_expiry_are_checked_before_new_reservation(self):
        for changes, error in (({"user": "bob"}, "SCOPE_DENIED"), ({"recipient": "other-shop"}, "SCOPE_DENIED"), ({"now": 1000}, "GRANT_EXPIRED"), ({"grant_id": "missing"}, "UNKNOWN_GRANT")):
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(ledger.LedgerError, error):
                    self.reserve(**changes)
        self.assertEqual(self.book.balance("grant")["available_minor"], 10000)

    def test_expired_replay_returns_existing_state_without_new_charge(self):
        self.reserve()
        self.assertEqual(self.reserve(now=2000), "RESERVED")
        self.assertEqual(self.book.balance("grant")["available_minor"], 4000)

    def test_unknown_result_preserves_budget_and_blocks_new_retry(self):
        self.reserve()
        self.assertEqual(self.book.mark_unknown("operation"), "UNKNOWN")
        self.assertEqual(self.reserve(), "UNKNOWN")
        self.assertEqual(self.book.reconcile("operation", executed=None), "UNKNOWN")
        with self.assertRaisesRegex(ledger.LedgerError, "BUDGET_EXCEEDED"):
            self.reserve("retry")
        self.assertEqual(self.book.balance("grant")["available_minor"], 4000)

    def test_confirmed_execution_settles_and_keeps_budget_consumed(self):
        self.reserve()
        self.book.mark_unknown("operation")
        self.assertEqual(self.book.reconcile("operation", executed=True), "SETTLED")
        self.assertEqual(self.book.reconcile("operation", executed=True), "SETTLED")
        self.assertEqual(self.reserve(), "SETTLED")
        self.assertEqual(self.book.balance("grant")["available_minor"], 4000)
        with self.assertRaisesRegex(ledger.LedgerError, "INVALID_TRANSITION"):
            self.book.reconcile("operation", executed=False)
        with self.assertRaisesRegex(ledger.LedgerError, "INVALID_TRANSITION"):
            self.book.mark_unknown("operation")

    def test_confirmed_nonexecution_cancels_and_releases_once(self):
        self.reserve()
        self.book.mark_unknown("operation")
        self.assertEqual(self.book.reconcile("operation", executed=False), "CANCELLED")
        self.assertEqual(self.book.reconcile("operation", executed=False), "CANCELLED")
        self.assertEqual(self.reserve(), "CANCELLED")
        self.assertEqual(self.book.balance("grant")["available_minor"], 10000)
        with self.assertRaisesRegex(ledger.LedgerError, "INVALID_TRANSITION"):
            self.book.reconcile("operation", executed=True)
        self.assertEqual(self.reserve("new-operation"), "RESERVED")

    def test_confirmation_requires_boolean_or_unknown(self):
        self.reserve()
        for value in ("false", 0, 1):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ledger.LedgerError, "INVALID_CONFIRMATION"):
                    self.book.reconcile("operation", executed=value)
        self.assertEqual(self.reserve(), "RESERVED")

    def test_new_connection_observes_persisted_state(self):
        self.reserve()
        self.book.mark_unknown("operation")
        other = ledger.Ledger(self.path)
        try:
            self.assertEqual(other.state("operation"), "UNKNOWN")
            self.assertEqual(other.balance("grant")["available_minor"], 4000)
        finally:
            other.close()

    def test_grant_cannot_be_replaced_to_reset_budget(self):
        self.reserve()
        with self.assertRaisesRegex(ledger.LedgerError, "GRANT_EXISTS"):
            self.book.add_grant("grant", "alice", "shop", 10000, 2000)
        self.assertEqual(self.book.balance("grant")["available_minor"], 4000)

    def test_demo_satisfies_effect_oracles(self):
        result = ledger.run_demo()
        self.assertTrue(result["simulation"])
        self.assertTrue(result["passed"], result)
        self.assertEqual(len(result["cases"]), 5)

    def test_command_exits_nonzero_when_effect_oracle_fails(self):
        source = pathlib.Path(ledger.__file__).read_text(encoding="utf-8")
        original = "WHERE grant_id = ? AND state != 'CANCELLED'"
        self.assertIn(original, source)
        # Real database fault: a settled payment incorrectly releases its budget.
        source = source.replace(original, "WHERE grant_id = ? AND state IN ('RESERVED', 'UNKNOWN')", 1)
        result = subprocess.run([sys.executable, "-c", source], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["passed"])
        self.assertFalse(report["cases"][0]["passed"])


class PaymentBudgetMutationTests(unittest.TestCase):
    def mutated_module(self, replacements):
        source = pathlib.Path(ledger.__file__).read_text(encoding="utf-8")
        for original, replacement in replacements:
            self.assertIn(original, source)
            source = source.replace(original, replacement, 1)
        module = types.ModuleType("faulty_local_ledger")
        module._race_gate = threading.Barrier(2)
        exec(compile(source, "<local-ledger-mutation>", "exec"), module.__dict__)
        return module

    def test_same_concurrency_oracle_rejects_nonatomic_database_reservation(self):
        module = self.mutated_module([
            ('self.connection.execute("BEGIN IMMEDIATE")', 'pass  # Removed transaction lock.'),
            ('self.connection.execute("COMMIT")', 'pass  # Autocommit each statement.'),
            ('available = self._available(grant_id)', 'available = self._available(grant_id)\n            _race_gate.wait(timeout=5)  # Force both reads before either insert.'),
        ])
        with self.assertRaises(AssertionError):
            assert_atomic_reservation(self, module)

    def test_same_replay_oracle_rejects_missing_operation_uniqueness(self):
        module = self.mutated_module([
            ('operation_id TEXT PRIMARY KEY', 'operation_id TEXT'),
            ('if operation is not None:', 'if False:  # Removed replay binding check.'),
        ])
        with self.assertRaises(AssertionError):
            assert_replay_binding(self, module)


if __name__ == "__main__":
    unittest.main()
