"""Local synthetic budget ledger; no payment provider or signature verification."""
import concurrent.futures
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
import tempfile
import threading


class LedgerError(ValueError):
    """A rejected ledger operation with a stable teaching error code."""


def positive_minor(value):
    if type(value) is not int or not 0 < value < 2**63:
        raise LedgerError("INVALID_AMOUNT")


def identifier(value):
    if not isinstance(value, str) or not value.strip():
        raise LedgerError("INVALID_IDENTIFIER")


def timestamp(value):
    if type(value) is not int or not 0 <= value < 2**63:
        raise LedgerError("INVALID_TIME")


class Ledger:
    """One connection per caller to a single trusted SQLite database."""

    def __init__(self, path):
        self.connection = sqlite3.connect(path, timeout=5, isolation_level=None)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS grants (
                grant_id TEXT PRIMARY KEY,
                user TEXT NOT NULL,
                recipient TEXT NOT NULL,
                budget_minor INTEGER NOT NULL CHECK (budget_minor > 0),
                expires_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS operations (
                operation_id TEXT PRIMARY KEY,
                grant_id TEXT NOT NULL REFERENCES grants(grant_id),
                arguments TEXT NOT NULL,
                amount_minor INTEGER NOT NULL CHECK (amount_minor > 0),
                state TEXT NOT NULL CHECK (state IN
                    ('RESERVED', 'UNKNOWN', 'SETTLED', 'CANCELLED'))
            );
        """)

    def close(self):
        self.connection.close()

    @contextmanager
    def _transaction(self):
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.connection.execute("COMMIT")
        except BaseException:
            if self.connection.in_transaction:
                self.connection.execute("ROLLBACK")
            raise

    def add_grant(self, grant_id, user, recipient, budget_minor, expires_at):
        """Trusted setup only; never accept a grant supplied by the agent."""
        for value in (grant_id, user, recipient):
            identifier(value)
        positive_minor(budget_minor)
        timestamp(expires_at)
        try:
            with self._transaction():
                self.connection.execute(
                    "INSERT INTO grants VALUES (?, ?, ?, ?, ?)",
                    (grant_id, user, recipient, budget_minor, expires_at),
                )
        except sqlite3.IntegrityError as error:
            raise LedgerError("GRANT_EXISTS") from error

    def _grant(self, grant_id):
        grant = self.connection.execute(
            "SELECT * FROM grants WHERE grant_id = ?", (grant_id,)
        ).fetchone()
        if grant is None:
            raise LedgerError("UNKNOWN_GRANT")
        return grant

    def _operation(self, operation_id):
        return self.connection.execute(
            "SELECT * FROM operations WHERE operation_id = ?", (operation_id,)
        ).fetchone()

    def _available(self, grant_id):
        grant = self._grant(grant_id)
        used = self.connection.execute(
            "SELECT COALESCE(SUM(amount_minor), 0) FROM operations "
            "WHERE grant_id = ? AND state != 'CANCELLED'", (grant_id,)
        ).fetchone()[0]
        return grant["budget_minor"] - used

    def reserve(self, operation_id, grant_id, user, recipient, amount_minor, *, now):
        """Atomically bind a new operation and reserve its budget."""
        for value in (operation_id, grant_id, user, recipient):
            identifier(value)
        positive_minor(amount_minor)
        timestamp(now)
        arguments = json.dumps(
            [grant_id, user, recipient, amount_minor, "CNY"],
            ensure_ascii=False, separators=(",", ":"),
        )
        with self._transaction():
            operation = self._operation(operation_id)
            if operation is not None:
                if operation["arguments"] != arguments:
                    raise LedgerError("OPERATION_CONFLICT")
                return operation["state"]
            grant = self._grant(grant_id)
            if (grant["user"], grant["recipient"]) != (user, recipient):
                raise LedgerError("SCOPE_DENIED")
            if now >= grant["expires_at"]:
                raise LedgerError("GRANT_EXPIRED")
            available = self._available(grant_id)
            if amount_minor > available:
                raise LedgerError("BUDGET_EXCEEDED")
            self.connection.execute(
                "INSERT INTO operations VALUES (?, ?, ?, ?, 'RESERVED')",
                (operation_id, grant_id, arguments, amount_minor),
            )
            return "RESERVED"

    def state(self, operation_id):
        operation = self._operation(operation_id)
        if operation is None:
            raise LedgerError("UNKNOWN_OPERATION")
        return operation["state"]

    def balance(self, grant_id):
        # Read both fields from one transaction snapshot.
        with self._transaction():
            grant = self._grant(grant_id)
            available = self._available(grant_id)
            return {
                "budget_minor": grant["budget_minor"],
                "committed_minor": grant["budget_minor"] - available,
                "available_minor": available,
                "currency": "CNY",
            }

    def _transition(self, operation_id, target):
        with self._transaction():
            current = self.state(operation_id)
            if current == target:
                return current
            if current not in ("RESERVED", "UNKNOWN"):
                raise LedgerError("INVALID_TRANSITION")
            self.connection.execute(
                "UPDATE operations SET state = ? WHERE operation_id = ?",
                (target, operation_id),
            )
            return target

    def mark_unknown(self, operation_id):
        """A timeout reports uncertainty; it never releases a reservation."""
        return self._transition(operation_id, "UNKNOWN")

    def reconcile(self, operation_id, *, executed):
        """Trusted query result: executed, definitely not executed, or unknown."""
        if executed is not None and type(executed) is not bool:
            raise LedgerError("INVALID_CONFIRMATION")
        target = "UNKNOWN" if executed is None else "SETTLED" if executed else "CANCELLED"
        return self._transition(operation_id, target)


def run_demo():
    """Run synthetic effect oracles and return inspectable JSON data."""
    cases = []
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "ledger.sqlite"
        book = Ledger(path)
        try:
            for grant in ("normal", "race", "replay", "unknown", "cancel"):
                book.add_grant(grant, "alice", "shop", 10000, 1000)

            book.reserve("normal-op", "normal", "alice", "shop", 6000, now=100)
            state = book.reconcile("normal-op", executed=True)
            available = book.balance("normal")["available_minor"]
            cases.append(dict(case="normal", state=state, available_minor=available,
                              passed=state == "SETTLED" and available == 4000))

            gate = threading.Barrier(2)

            def request(number):
                other = Ledger(path)
                try:
                    gate.wait(timeout=5)
                    try:
                        return other.reserve(f"race-{number}", "race", "alice", "shop", 6000, now=100)
                    except LedgerError as error:
                        return str(error)
                finally:
                    other.close()

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = sorted(pool.map(request, range(2)))
            available = book.balance("race")["available_minor"]
            cases.append(dict(case="concurrent_60_plus_60", outcomes=outcomes,
                              available_minor=available,
                              passed=outcomes == ["BUDGET_EXCEEDED", "RESERVED"] and available == 4000))

            args = ("replay-op", "replay", "alice", "shop", 3000)
            first = book.reserve(*args, now=100)
            repeat = book.reserve(*args, now=101)
            conflict = "NOT_REJECTED"
            try:
                book.reserve("replay-op", "replay", "alice", "shop", 4000, now=100)
            except LedgerError as error:
                conflict = str(error)
            available = book.balance("replay")["available_minor"]
            cases.append(dict(case="replay_and_changed_arguments", states=[first, repeat],
                              conflict=conflict, available_minor=available,
                              passed=first == repeat == "RESERVED" and conflict == "OPERATION_CONFLICT" and available == 7000))

            args = ("unknown-op", "unknown", "alice", "shop", 6000)
            book.reserve(*args, now=100)
            book.mark_unknown("unknown-op")
            pending = book.reconcile("unknown-op", executed=None)
            repeat = book.reserve(*args, now=101)
            blocked = "NOT_REJECTED"
            try:
                book.reserve("unsafe-retry", "unknown", "alice", "shop", 6000, now=100)
            except LedgerError as error:
                blocked = str(error)
            held = book.balance("unknown")["available_minor"]
            settled = book.reconcile("unknown-op", executed=True)
            cases.append(dict(case="timeout_and_confirmed_execution", pending=pending,
                              repeat=repeat, new_operation=blocked, held_available_minor=held,
                              final_state=settled,
                              passed=pending == repeat == "UNKNOWN" and blocked == "BUDGET_EXCEEDED" and held == 4000 and settled == "SETTLED"))

            book.reserve("cancel-op", "cancel", "alice", "shop", 6000, now=100)
            book.mark_unknown("cancel-op")
            state = book.reconcile("cancel-op", executed=False)
            available = book.balance("cancel")["available_minor"]
            cases.append(dict(case="confirmed_nonexecution", state=state,
                              available_minor=available,
                              passed=state == "CANCELLED" and available == 10000))
        finally:
            book.close()
    return dict(simulation=True, cases=cases, passed=all(case["passed"] for case in cases))


if __name__ == "__main__":
    result = run_demo()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
