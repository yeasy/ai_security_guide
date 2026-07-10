#!/usr/bin/env python3
"""Validate the canonical framework registry and its reader-facing tables."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "framework_crosswalk.json"
REQUIRED_FIELDS = (
    "id",
    "framework",
    "identifier",
    "name",
    "version",
    "source",
    "verified_at",
    "chapters",
)

OWASP = {
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
NIST = {
    "GOVERN": "Govern",
    "MAP": "Map",
    "MEASURE": "Measure",
    "MANAGE": "Manage",
}
ATLAS = {
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
EU = {"Regulation (EU) 2024/1689": "EU AI Act"}
CROSSWALK = {
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

FRAMEWORKS = {
    "OWASP Top 10 for LLM Applications": {
        "version": "2025",
        "source": "https://genai.owasp.org/llm-top-10/?cat=253",
        "entries": OWASP,
    },
    "NIST AI RMF": {
        "version": "1.0",
        "source": "https://airc.nist.gov/docs/playbook.json",
        "entries": NIST,
    },
    "MITRE ATLAS": {
        "version": "2026.06",
        "source": (
            "https://raw.githubusercontent.com/mitre-atlas/atlas-data/"
            "main/dist/v6/ATLAS-2026.06.yaml"
        ),
        "entries": ATLAS,
    },
    "EU AI Act": {
        "version": "2024/1689",
        "source": "http://data.europa.eu/eli/reg/2024/1689/oj",
        "entries": EU,
    },
}


def valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def validate_registry_data(data: Any, root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    if not isinstance(data, dict):
        return ["framework registry root must be an object"]
    if data.get("schema_version") != "1.0":
        issues.append("schema_version must be 1.0")
    if not valid_date(data.get("verified_at")):
        issues.append("registry verified_at must be an ISO date")

    entries = data.get("entries")
    if not isinstance(entries, list):
        return issues + ["entries must be an array"]

    seen_ids: set[str] = set()
    entry_by_id: dict[str, dict[str, Any]] = {}
    actual: dict[str, dict[str, str]] = {name: {} for name in FRAMEWORKS}
    root = root.resolve()

    for index, entry in enumerate(entries):
        prefix = f"entries[{index}]"
        if not isinstance(entry, dict):
            issues.append(f"{prefix} must be an object")
            continue
        for field in REQUIRED_FIELDS:
            if not entry.get(field):
                issues.append(f"{prefix}.{field} is required")

        entry_id = entry.get("id")
        if isinstance(entry_id, str):
            if entry_id in seen_ids:
                issues.append(f"duplicate entry id: {entry_id}")
            seen_ids.add(entry_id)
            entry_by_id[entry_id] = entry

        framework = entry.get("framework")
        identifier = entry.get("identifier")
        name = entry.get("name")
        specification = FRAMEWORKS.get(framework) if isinstance(framework, str) else None
        if specification is None:
            issues.append(f"{prefix}.framework is not approved: {framework!r}")
        else:
            if entry.get("version") != specification["version"]:
                issues.append(f"{prefix}.version does not match {framework}")
            if entry.get("source") != specification["source"]:
                issues.append(f"{prefix}.source is not the approved official source")
            if isinstance(identifier, str) and isinstance(name, str):
                if identifier in actual[framework]:
                    issues.append(f"duplicate {framework} identifier: {identifier}")
                actual[framework][identifier] = name

        if not valid_date(entry.get("verified_at")):
            issues.append(f"{prefix}.verified_at must be an ISO date")

        chapters = entry.get("chapters")
        if not isinstance(chapters, list) or not all(
            isinstance(item, str) and item for item in chapters
        ):
            issues.append(f"{prefix}.chapters must be a non-empty string array")
            continue
        for relative in chapters:
            path = (root / relative).resolve()
            if path != root and root not in path.parents:
                issues.append(f"{prefix}.chapters escapes repository: {relative}")
                continue
            if not path.is_file():
                issues.append(f"{prefix}.chapters is missing: {relative}")
                continue
            table_rows = [
                line
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.lstrip().startswith("|")
            ]
            if isinstance(identifier, str) and isinstance(name, str) and not any(
                identifier in row and name in row for row in table_rows
            ):
                issues.append(
                    f"{relative} has no table row pairing {identifier} with {name}"
                )

    for framework, specification in FRAMEWORKS.items():
        if actual[framework] != specification["entries"]:
            issues.append(f"{framework} identifiers or names do not match canonical set")

    mappings = data.get("mappings")
    if not isinstance(mappings, list):
        return issues + ["mappings must be an array"]
    seen_mapping_ids: set[str] = set()
    actual_mappings: dict[str, tuple[str, ...]] = {}
    for index, mapping in enumerate(mappings):
        prefix = f"mappings[{index}]"
        if not isinstance(mapping, dict):
            issues.append(f"{prefix} must be an object")
            continue
        for field in ("id", "from", "to", "chapter", "verified_at"):
            if not mapping.get(field):
                issues.append(f"{prefix}.{field} is required")

        mapping_id = mapping.get("id")
        if isinstance(mapping_id, str):
            if mapping_id in seen_mapping_ids:
                issues.append(f"duplicate mapping id: {mapping_id}")
            seen_mapping_ids.add(mapping_id)
        source_id = mapping.get("from")
        target_ids = mapping.get("to")
        if not isinstance(source_id, str) or source_id not in entry_by_id:
            issues.append(f"{prefix}.from references unknown entry: {source_id}")
        if (
            not isinstance(target_ids, list)
            or not target_ids
            or not all(isinstance(target_id, str) for target_id in target_ids)
        ):
            issues.append(f"{prefix}.to must be a non-empty string array")
            continue
        for target_id in target_ids:
            if target_id not in entry_by_id:
                issues.append(f"{prefix}.to references unknown entry: {target_id}")
        if isinstance(source_id, str) and all(
            isinstance(target_id, str) for target_id in target_ids
        ):
            if source_id in actual_mappings:
                issues.append(f"duplicate mapping source: {source_id}")
            actual_mappings[source_id] = tuple(target_ids)
        if not valid_date(mapping.get("verified_at")):
            issues.append(f"{prefix}.verified_at must be an ISO date")

        relative = mapping.get("chapter")
        if not isinstance(relative, str):
            continue
        path = (root / relative).resolve()
        if path != root and root not in path.parents:
            issues.append(f"{prefix}.chapter escapes repository: {relative}")
            continue
        if not path.is_file():
            issues.append(f"{prefix}.chapter is missing: {relative}")
            continue
        referenced = [source_id, *target_ids]
        if not all(reference in entry_by_id for reference in referenced):
            continue
        identifiers = [entry_by_id[reference]["identifier"] for reference in referenced]
        rows = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.lstrip().startswith("|")
        ]
        if not any(all(identifier in row for identifier in identifiers) for row in rows):
            issues.append(
                f"{relative} has no single table row for mapping {mapping_id}"
            )

    if actual_mappings != CROSSWALK:
        issues.append("OWASP-to-ATLAS mappings do not match the canonical registry")
    return issues


def validate_crosswalk(root: Path = ROOT) -> list[str]:
    path = root / "data" / "framework_crosswalk.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"cannot read {path}: {error}"]
    return validate_registry_data(data, root)


def main() -> int:
    issues = validate_crosswalk(ROOT)
    if issues:
        print("\n".join(issues))
        print(f"\n{len(issues)} framework crosswalk issue(s) found.")
        return 1
    print("Framework crosswalk matches official identifiers and chapter tables.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
