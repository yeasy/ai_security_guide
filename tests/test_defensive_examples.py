"""Execute the manuscript's defensive examples with offline, standard-library ports."""

import ast
import asyncio
import re
import statistics
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
CANARY = "<FAKE_CANARY_123456>"


def load_definition(path, name, **ports):
    """Extract the actual named definition, never a duplicate implementation."""
    text = (ROOT / path).read_text(encoding="utf-8")
    definitions = []
    for match in re.finditer(r"^```python\s*\n(.*?)^```\s*$", text, re.M | re.S):
        source = match.group(1)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue  # Other blocks may deliberately contain top-level await.
        ast.increment_lineno(tree, text.count("\n", 0, match.start(1)))
        definitions.extend(
            node for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and node.name == name
        )
    if len(definitions) != 1:
        raise AssertionError(f"Expected one manuscript definition for {name}")
    namespace = dict(ports)
    module = ast.Module(body=definitions, type_ignores=[])
    exec(compile(module, str(ROOT / path), "exec"), namespace)
    return namespace[name]


class StreamModerationTests(unittest.TestCase):
    def run_stream(self, chunks, *, context_chars=len(CANARY), overlap=4):
        class Model:
            async def stream(self, prompt):
                for chunk in chunks:
                    yield chunk

        class Moderator:
            max_context_chars = context_chars

            async def full_check(self, text):
                return SimpleNamespace(blocked=CANARY in text)

        stream = load_definition(
            "09_io_protection/9.2_output_moderation.md", "stream_with_moderation",
            model=Model(), moderator=Moderator(), CHECK_INTERVAL=19,
            OVERLAP_CHARS=overlap,
        )

        async def collect():
            return [part async for part in stream("synthetic test")]

        return asyncio.run(collect())

    def test_split_canary_is_withheld_for_small_and_large_old_overlap(self):
        for overlap in (4, 20):
            with self.subTest(overlap=overlap):
                output = self.run_stream(["prefix:<FAKE_CANARY", "_123456>"], overlap=overlap)
                self.assertNotIn("<FAKE_CANARY", "".join(output))
                self.assertEqual(output[-1], "[内容已被过滤]")

    def test_every_split_and_single_character_chunks_block_before_release(self):
        chunks = [["prefix:" + CANARY[:split], CANARY[split:]]
                  for split in range(1, len(CANARY))]
        chunks.append(list("prefix:" + CANARY))
        for case in chunks:
            with self.subTest(chunks=case):
                output = self.run_stream(case)
                self.assertNotIn("<FAKE_CANARY", "".join(output))
                self.assertEqual(output[-1], "[内容已被过滤]")

    def test_unknown_context_buffers_entire_response(self):
        output = self.run_stream(["prefix:<FAKE_CANARY", "_123456>"], context_chars=None)
        self.assertEqual(output, ["[内容已被过滤]"])

    def test_safe_text_is_preserved_once_including_short_tail(self):
        for context_chars in (None, len(CANARY), 1):
            with self.subTest(context_chars=context_chars):
                output = self.run_stream(["safe text " * 7, "tail"], context_chars=context_chars)
                self.assertEqual("".join(output), "safe text " * 7 + "tail")


class StatisticalDetectionTests(unittest.TestCase):
    def detector(self):
        np = SimpleNamespace(mean=statistics.mean, std=statistics.pstdev)
        detector = load_definition(
            "10_operations/10.2_anomaly_detection.md", "StatisticalDetector", np=np
        )
        return detector()

    def test_stable_baseline_still_detects_a_large_deviation(self):
        self.assertTrue(self.detector().detect_anomaly(1000, [1, 1, 1]))

    def test_insufficient_history_is_not_a_normal_observation(self):
        self.assertIsNone(self.detector().detect_anomaly(1000, [1]))

    def test_stable_noise_within_tolerance_is_normal(self):
        self.assertFalse(self.detector().detect_anomaly(1 + 1e-10, [1, 1, 1]))

    def test_nonconstant_baseline_uses_z_score(self):
        self.assertTrue(self.detector().detect_anomaly(100, [1, 2, 3]))
        self.assertFalse(self.detector().detect_anomaly(2, [1, 2, 3]))


class ModelUnavailableError(Exception):
    pass


class SafetyCheckUnavailableError(Exception):
    pass


class FallbackTests(unittest.TestCase):
    def manager(self, primary="safe", retry="safe", backup="safe"):
        manager_type = load_definition(
            "10_operations/10.5_fallback_strategy.md", "FallbackManager",
            Request=object, Response=object,
            ModelUnavailableError=ModelUnavailableError,
            SafetyCheckUnavailableError=SafetyCheckUnavailableError,
            load_canned_responses=lambda: {},
        )
        manager = manager_type()
        events = []

        def generate(route, result):
            events.append(("generate", route))
            if isinstance(result, Exception):
                raise result
            return result

        manager.primary_model = SimpleNamespace(generate=lambda request: generate("primary", primary))
        manager.retry_with_lower_temperature = lambda request: generate("retry", retry)
        manager.use_backup_model = lambda request: generate("backup", backup)
        manager.safety_check = lambda response: events.append(("check", response)) or response == "safe"
        manager.record_success = lambda: events.append("success")
        manager.record_failure = lambda: events.append("failure")
        manager.record_safety_rejection = lambda: events.append("rejection")
        manager.record_safety_unavailable = lambda: events.append("safety_unavailable")
        manager.get_canned_response = lambda category: "canned"
        manager.route_to_human = lambda request: "human"
        return manager, events

    def handle(self, manager):
        try:
            return manager.handle_request(SimpleNamespace(category="test"))
        except (ModelUnavailableError, SafetyCheckUnavailableError) as error:
            self.fail(f"Operational failure escaped the documented fallback: {type(error).__name__}")

    def test_primary_retry_and_backup_successes_all_pass_the_same_review(self):
        for level in (0, 1, 2):
            with self.subTest(level=level):
                manager, events = self.manager()
                manager.fallback_level = level
                self.assertEqual(self.handle(manager), "safe")
                self.assertEqual(events, [
                    ("generate", ("primary", "retry", "backup")[level]),
                    ("check", "safe"), "success",
                ])

    def test_unsafe_retry_and_backup_are_not_returned(self):
        cases = (
            (ModelUnavailableError(), "unsafe", "safe", 1),
            (ModelUnavailableError(), ModelUnavailableError(), "unsafe", 2),
        )
        for primary, retry, backup, failures in cases:
            with self.subTest(failures=failures):
                manager, events = self.manager(primary, retry, backup)
                self.assertEqual(self.handle(manager), "canned")
                self.assertEqual(events.count("failure"), failures)
                self.assertIn(("check", "unsafe"), events)
                self.assertIn("rejection", events)
                self.assertNotIn("success", events)

    def test_one_unsafe_output_does_not_degrade_every_user(self):
        manager, events = self.manager(primary="unsafe")
        self.assertEqual(self.handle(manager), "canned")
        self.assertIn("rejection", events)
        self.assertEqual(manager.fallback_level, 0)
        manager.primary_model.generate = lambda request: "safe"
        self.assertEqual(self.handle(manager), "safe")

    def test_safety_outage_degrades_globally(self):
        manager, _ = self.manager()

        def unavailable(response):
            raise SafetyCheckUnavailableError()

        manager.safety_check = unavailable
        self.handle(manager)
        self.assertEqual(manager.fallback_level, 3)

    def test_l3_and_l4_have_distinct_reachable_outputs(self):
        for level, expected in ((3, "canned"), (4, "human")):
            with self.subTest(level=level):
                manager, _ = self.manager()
                manager.fallback_level = level
                self.assertEqual(manager.handle_request(SimpleNamespace(category="test")), expected)

    def test_all_model_failures_are_counted_once_and_end_in_canned_response(self):
        manager, events = self.manager(*[ModelUnavailableError() for _ in range(3)])
        self.assertEqual(self.handle(manager), "canned")
        self.assertEqual(events, [
            ("generate", "primary"), "failure", ("generate", "retry"), "failure",
            ("generate", "backup"), "failure",
        ])
        self.assertEqual(manager.fallback_level, 3)

    def test_safety_outage_fails_closed_without_model_retry(self):
        manager, events = self.manager()

        def unavailable(response):
            raise SafetyCheckUnavailableError()

        manager.safety_check = unavailable
        self.assertEqual(self.handle(manager), "canned")
        self.assertEqual(events, [("generate", "primary"), "safety_unavailable"])

    def test_operator_escalation_from_l3_reaches_human(self):
        manager, _ = self.manager()
        manager.fallback_level = 3
        self.assertEqual(manager.escalate_fallback(SimpleNamespace(category="test")), "human")


class DeploymentGateTests(unittest.TestCase):
    def test_every_selected_threshold_blocks_when_exceeded(self):
        framework_type = load_definition(
            "10_operations/10.6_modern_redteam_tools.md", "ThresholdSelectionFramework"
        )
        framework = framework_type()
        framework.get_escalation_path = lambda threshold: "security"
        for threshold in (0.01, 0.05, 0.10):
            with self.subTest(threshold=threshold):
                gate = framework.configure_ci_cd_gate("demo", threshold)
                self.assertEqual(gate["action_on_failure"], "block_deployment")


if __name__ == "__main__":
    unittest.main()
