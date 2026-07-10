#!/usr/bin/env python3
"""Require explicit SAFE-LAB contracts for executable attack demonstrations."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTACK_DIRS = (
    "04_prompt_injection",
    "05_jailbreak",
    "06_data_model_attacks",
    "07_agent_rag_security",
)
EXECUTABLE_LANGUAGES = {
    "bash",
    "c",
    "c++",
    "cpp",
    "csharp",
    "go",
    "html",
    "java",
    "javascript",
    "js",
    "node",
    "nodejs",
    "php",
    "powershell",
    "ps1",
    "py",
    "py3",
    "python",
    "python3",
    "ruby",
    "rust",
    "sh",
    "shell",
    "solidity",
    "sql",
    "swift",
    "ts",
    "typescript",
    "zsh",
}
MARKERS = {
    "<!-- SAFE-LAB: offensive -->": "offensive",
    "<!-- SAFE-LAB: defensive-only -->": "defensive-only",
}
REQUIRED_FIELDS = (
    "authorization",
    "isolation",
    "synthetic-data",
    "budget",
    "stop-conditions",
    "disclosure",
)
OFFENSIVE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE | re.DOTALL)
    for pattern in (
        r"</system\s*>",
        r"font-size\s*:\s*0\s*;[^\n]*color\s*:\s*transparent",
        r"\[系统\]\s*:\s*新紧急指令",
        r"\bAttackerLLM\s*\(",
        r"knowledge_base\.insert\s*\(\s*malicious_doc",
        r"original_model\.generate\s*\(\s*[\"']请告诉我如何制造炸弹",
        r"train_surrogate_adapter\s*\(",
        r"\bos\.system\s*\(",
        r"https?://attacker\.com(?:/|\b)",
        r"0xAttacker\b",
    )
)
FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})\s*([^\s`~]*)?.*$")


@dataclass(frozen=True)
class SafeLabBlock:
    path: Path
    line: int
    language: str
    body: str
    classification: str
    contract: str


def contract_template() -> str:
    return (
        "> **SAFE-LAB 实验契约（执行前必读）**\n"
        "> - `authorization`: 仅在你拥有或已获书面授权的目标上测试。\n"
        "> - `isolation`: 仅在无生产凭据、无外网副作用的隔离沙箱中运行。\n"
        "> - `synthetic-data`: 只使用合成输入、虚构身份与无价值测试数据。\n"
        "> - `budget`: 预设请求数、运行时间、费用与资源消耗上限。\n"
        "> - `stop-conditions`: 出现越界访问、真实数据、异常成本或不可逆动作时立即停止。\n"
        "> - `disclosure`: 发现真实漏洞时停止扩散，按负责任披露流程报告。\n"
    )


def looks_offensive(body: str) -> bool:
    return any(pattern.search(body) for pattern in OFFENSIVE_PATTERNS)


def analyze_markdown(path: Path, text: str) -> tuple[list[SafeLabBlock], list[str]]:
    lines = text.splitlines()
    blocks: list[SafeLabBlock] = []
    issues: list[str] = []
    index = 0
    contract_lines = contract_template().rstrip("\n").splitlines()

    while index < len(lines):
        match = FENCE_OPEN.match(lines[index])
        if not match:
            index += 1
            continue
        marker = match.group(1)
        language = (match.group(2) or "").lower().lstrip("{.").rstrip("}")
        close = index + 1
        while close < len(lines):
            closing = re.match(r"^\s*([`~]{3,})\s*$", lines[close])
            if (
                closing
                and closing.group(1)[0] == marker[0]
                and len(closing.group(1)) >= len(marker)
            ):
                break
            close += 1
        if close >= len(lines):
            break

        body = "\n".join(lines[index + 1 : close])
        executable = language in EXECUTABLE_LANGUAGES or looks_offensive(body)
        if not executable:
            index = close + 1
            continue

        marker_line = lines[index - 1] if index > 0 else ""
        classification = MARKERS.get(marker_line, "")
        contract = ""
        location = f"{path}:{index + 1}"
        if not classification:
            issues.append(
                f"{location}: executable block requires an attached SAFE-LAB classification"
            )
        elif classification == "defensive-only" and looks_offensive(body):
            issues.append(
                f"{location}: offensive content cannot use defensive-only exemption"
            )
        elif classification == "offensive":
            start = index - 1 - len(contract_lines)
            if start >= 0 and lines[start : index - 1] == contract_lines:
                contract = "\n".join(contract_lines)
            else:
                issues.append(
                    f"{location}: offensive block requires the complete reader-visible SAFE-LAB contract"
                )

        blocks.append(
            SafeLabBlock(
                path=path,
                line=index + 1,
                language=language,
                body=body,
                classification=classification,
                contract=contract,
            )
        )
        index = close + 1
    return blocks, issues


def scan_attack_chapters(root: Path = ROOT) -> tuple[list[SafeLabBlock], list[str]]:
    blocks: list[SafeLabBlock] = []
    issues: list[str] = []
    for directory in ATTACK_DIRS:
        for path in sorted((root / directory).glob("*.md")):
            relative = path.relative_to(root)
            found, found_issues = analyze_markdown(
                relative, path.read_text(encoding="utf-8")
            )
            blocks.extend(found)
            issues.extend(found_issues)
    return blocks, issues


def validate_attack_contracts(root: Path = ROOT) -> list[str]:
    return scan_attack_chapters(root)[1]


def main() -> int:
    blocks, issues = scan_attack_chapters(ROOT)
    if issues:
        print("\n".join(issues))
        print(f"\n{len(issues)} SAFE-LAB contract issue(s) found.")
        return 1
    offensive = sum(block.classification == "offensive" for block in blocks)
    defensive = sum(block.classification == "defensive-only" for block in blocks)
    print(
        f"SAFE-LAB contracts passed: {offensive} offensive, "
        f"{defensive} defensive-only executable blocks."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
