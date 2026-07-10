import copy
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "framework_crosswalk.json"

OWASP_SOURCE = "https://genai.owasp.org/llm-top-10/?cat=253"
NIST_SOURCE = "https://airc.nist.gov/docs/playbook.json"
ATLAS_SOURCE = (
    "https://raw.githubusercontent.com/mitre-atlas/atlas-data/"
    "main/dist/v6/ATLAS-2026.06.yaml"
)
EU_ELI = "http://data.europa.eu/eli/reg/2024/1689/oj"

EXPECTED_OWASP = {
    "LLM01:2025": "Prompt Injection",
    "LLM02:2025": "Sensitive Information Disclosure",
    "LLM03:2025": "Supply Chain",
    "LLM04:2025": "Data and Model Poisoning",
    "LLM05:2025": "Improper Output Handling",
    "LLM06:2025": "Excessive Agency",
    "LLM07:2025": "System Prompt Leakage",
    "LLM08:2025": "Vector and Embedding Weaknesses",
    "LLM09:2025": "Misinformation",
    "LLM10:2025": "Unbounded Consumption",
}
EXPECTED_NIST = {
    "GOVERN": "Govern",
    "MAP": "Map",
    "MEASURE": "Measure",
    "MANAGE": "Manage",
}
EXPECTED_ATLAS = {
    "AML.T0020": "Poison Training Data",
    "AML.T0051": "LLM Prompt Injection",
    "AML.T0053": "AI Agent Tool Invocation",
    "AML.T0056": "Extract LLM System Prompt",
    "AML.T0057": "LLM Data Leakage",
    "AML.T0069": "Discover LLM System Information",
    "AML.T0070": "RAG Poisoning",
    "AML.T0080": "AI Agent Context Poisoning",
    "AML.T0086": "Exfiltration via AI Agent Tool Invocation",
    "AML.T0093": "Prompt Infiltration via Public-Facing Application",
    "AML.T0110": "AI Agent Tool Poisoning",
}
EXPECTED_MAPPINGS = {
    "owasp:LLM01:2025": ("atlas:AML.T0051", "atlas:AML.T0093"),
    "owasp:LLM02:2025": (
        "atlas:AML.T0056",
        "atlas:AML.T0057",
        "atlas:AML.T0086",
    ),
    "owasp:LLM04:2025": (
        "atlas:AML.T0020",
        "atlas:AML.T0070",
        "atlas:AML.T0080",
    ),
    "owasp:LLM06:2025": ("atlas:AML.T0053", "atlas:AML.T0110"),
    "owasp:LLM07:2025": ("atlas:AML.T0056", "atlas:AML.T0069"),
}


class FrameworkCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def entries_for(self, framework):
        return {
            entry["identifier"]: entry
            for entry in self.data["entries"]
            if entry["framework"] == framework
        }

    def test_registry_has_unique_ids_and_required_provenance(self):
        self.assertEqual(self.data["schema_version"], "1.0")
        ids = [entry["id"] for entry in self.data["entries"]]
        self.assertEqual(len(ids), len(set(ids)))
        for entry in self.data["entries"]:
            with self.subTest(entry=entry.get("id")):
                for field in (
                    "id",
                    "framework",
                    "identifier",
                    "name",
                    "version",
                    "source",
                    "verified_at",
                    "chapters",
                ):
                    self.assertTrue(entry.get(field), field)

        mapping_ids = [mapping["id"] for mapping in self.data["mappings"]]
        self.assertEqual(len(mapping_ids), len(set(mapping_ids)))
        for mapping in self.data["mappings"]:
            for field in ("id", "from", "to", "chapter", "verified_at"):
                self.assertTrue(mapping.get(field), field)

    def test_registry_uses_only_official_canonical_or_machine_readable_sources(self):
        expected = {
            "OWASP Top 10 for LLM Applications": ("2025", OWASP_SOURCE),
            "NIST AI RMF": ("1.0", NIST_SOURCE),
            "MITRE ATLAS": ("2026.06", ATLAS_SOURCE),
            "EU AI Act": ("2024/1689", EU_ELI),
        }
        for entry in self.data["entries"]:
            with self.subTest(entry=entry["id"]):
                self.assertIn(entry["framework"], expected)
                self.assertEqual(
                    (entry["version"], entry["source"]), expected[entry["framework"]]
                )

    def test_official_framework_identifiers_and_names_are_exact(self):
        actual_owasp = {
            key: value["name"]
            for key, value in self.entries_for(
                "OWASP Top 10 for LLM Applications"
            ).items()
        }
        actual_nist = {
            key: value["name"]
            for key, value in self.entries_for("NIST AI RMF").items()
        }
        actual_atlas = {
            key: value["name"]
            for key, value in self.entries_for("MITRE ATLAS").items()
        }
        self.assertEqual(actual_owasp, EXPECTED_OWASP)
        self.assertEqual(actual_nist, EXPECTED_NIST)
        self.assertEqual(actual_atlas, EXPECTED_ATLAS)

        eu = self.entries_for("EU AI Act")
        self.assertEqual(set(eu), {"Regulation (EU) 2024/1689"})
        self.assertEqual(eu["Regulation (EU) 2024/1689"]["source"], EU_ELI)

    def test_chapter_tables_match_registry_identifiers_and_names(self):
        for entry in self.data["entries"]:
            for relative in entry["chapters"]:
                with self.subTest(entry=entry["id"], chapter=relative):
                    rows = [
                        line
                        for line in (ROOT / relative)
                        .read_text(encoding="utf-8")
                        .splitlines()
                        if line.lstrip().startswith("|")
                    ]
                    self.assertTrue(
                        any(
                            entry["identifier"] in row and entry["name"] in row
                            for row in rows
                        )
                    )

    def test_owasp_atlas_crosswalk_relations_are_explicit_and_exact(self):
        actual = {
            mapping["from"]: tuple(mapping["to"])
            for mapping in self.data["mappings"]
        }
        self.assertEqual(actual, EXPECTED_MAPPINGS)

        entries = {entry["id"]: entry for entry in self.data["entries"]}
        for mapping in self.data["mappings"]:
            row_candidates = [
                line
                for line in (ROOT / mapping["chapter"])
                .read_text(encoding="utf-8")
                .splitlines()
                if line.lstrip().startswith("|")
            ]
            identifiers = [entries[mapping["from"]]["identifier"]] + [
                entries[target]["identifier"] for target in mapping["to"]
            ]
            self.assertTrue(
                any(all(identifier in row for identifier in identifiers) for row in row_candidates),
                mapping["id"],
            )

    def test_validator_rejects_duplicate_missing_and_unofficial_entries(self):
        from tools.validate_framework_crosswalk import validate_registry_data

        duplicate = copy.deepcopy(self.data)
        duplicate["entries"].append(copy.deepcopy(duplicate["entries"][0]))
        self.assertTrue(validate_registry_data(duplicate, ROOT))

        missing = copy.deepcopy(self.data)
        del missing["entries"][0]["verified_at"]
        self.assertTrue(validate_registry_data(missing, ROOT))

        unofficial = copy.deepcopy(self.data)
        unofficial["entries"][0]["source"] = "https://example.com/top-10.json"
        self.assertTrue(validate_registry_data(unofficial, ROOT))

        broken_reference = copy.deepcopy(self.data)
        broken_reference["mappings"][0]["to"] = ["atlas:AML.T9999"]
        self.assertTrue(validate_registry_data(broken_reference, ROOT))

        malformed = copy.deepcopy(self.data)
        malformed["entries"][0]["framework"] = ["OWASP"]
        malformed["mappings"][0]["to"] = [{"id": "atlas:AML.T0051"}]
        self.assertTrue(validate_registry_data(malformed, ROOT))

    def test_validator_cli_passes_repository_registry(self):
        result = subprocess.run(
            ["python3", "tools/validate_framework_crosswalk.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
