#!/usr/bin/env python3
"""Require explicit SAFE-LAB contracts for executable attack demonstrations."""

from __future__ import annotations

import ast
import re
import sys
import unicodedata
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
CONTRACT_HEADER = "> **SAFE-LAB 实验契约（执行前必读）**"
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
PRIVACY_ATTACK_MARKERS = (
    "membershipinference",
    "privacyrecovery",
    "privacyextraction",
    "trainingdatarecovery",
    "trainingdataextraction",
    "trainingdatareconstruction",
    "成员推理",
    "成员归属推断",
    "成员身份推断",
    "训练数据恢复",
    "训练数据提取",
    "微调数据恢复",
    "隐私恢复攻击",
)
PERSONAL_RECORD_MARKERS = (
    "orderhistory",
    "purchasehistory",
    "transactionhistory",
    "订单历史",
    "购买历史",
    "交易历史",
)
EMAIL_PATTERN = re.compile(
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE
)
PYTHON_LANGUAGES = frozenset({"py", "py3", "python", "python3"})
JAVASCRIPT_LANGUAGES = frozenset(
    {"javascript", "js", "node", "nodejs", "ts", "typescript"}
)
ATTACK_SINKS = frozenset({"complete", "generate", "invoke", "query", "score"})
SINK_CALL_START = re.compile(
    rf"\b(?:[A-Za-z_$][\w$]*\s*\.\s*)*({'|'.join(sorted(ATTACK_SINKS))})\s*\(",
    re.IGNORECASE,
)
SIMPLE_JS_ASSIGNMENT = re.compile(
    r"^\s*(?:(?:const|let|var)\s+)([A-Za-z_$][\w$]*)\s*=\s*(.*?)\s*;?\s*$"
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
        f"{CONTRACT_HEADER}\n"
        "> - `authorization`: 仅在你拥有或已获书面授权的目标上测试。\n"
        "> - `isolation`: 仅在无生产凭据、无外网副作用的隔离沙箱中运行。\n"
        "> - `synthetic-data`: 只使用合成输入、虚构身份与无价值测试数据。\n"
        "> - `budget`: 预设请求数、运行时间、费用与资源消耗上限。\n"
        "> - `stop-conditions`: 出现越界访问、真实数据、异常成本或不可逆动作时立即停止。\n"
        "> - `disclosure`: 发现真实漏洞时停止扩散，按负责任披露流程报告。\n"
    )


def compact_semantic_text(body: str) -> str:
    """Normalize superficial case, separator, and string-splitting disguises."""

    folded = unicodedata.normalize("NFKC", body).casefold()
    return re.sub(r"[\W_]+", "", folded, flags=re.UNICODE)


def contains_privacy_marker(text: str) -> bool:
    compact = compact_semantic_text(text)
    return any(marker in compact for marker in PRIVACY_ATTACK_MARKERS)


def contains_personal_record_query(text: str) -> bool:
    compact = compact_semantic_text(text)
    contains_record = any(marker in compact for marker in PERSONAL_RECORD_MARKERS)
    contains_identity = bool(EMAIL_PATTERN.search(text)) or any(
        marker in compact for marker in ("email", "userid", "customerid", "用户")
    )
    return contains_record and contains_identity


def _python_call_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id.casefold()
    if isinstance(node, ast.Attribute):
        return node.attr.casefold()
    return ""


class _PythonStringFlow(ast.NodeVisitor):
    """Resolve only straight-line string constants and record attack-sink inputs."""

    def __init__(self) -> None:
        self.scopes: list[dict[str, str]] = [{}]
        self.has_attack_sink = False
        self.sink_texts: list[str] = []

    def _lookup(self, name: str) -> str | None:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _evaluate(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name):
            return self._lookup(node.id)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            return left + right if left is not None and right is not None else None
        if isinstance(node, ast.JoinedStr):
            parts: list[str] = []
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    parts.append(value.value)
                    continue
                if isinstance(value, ast.FormattedValue):
                    resolved = self._evaluate(value.value)
                    if resolved is not None:
                        parts.append(resolved)
                        continue
                return None
            return "".join(parts)
        return None

    def _bind(self, target: ast.AST, value: ast.AST) -> None:
        if isinstance(target, ast.Name):
            resolved = self._evaluate(value)
            if resolved is None:
                self.scopes[-1].pop(target.id, None)
            else:
                self.scopes[-1][target.id] = resolved
            return
        if isinstance(target, (ast.Tuple, ast.List)) and isinstance(
            value, (ast.Tuple, ast.List)
        ):
            if len(target.elts) != len(value.elts):
                return
            for child_target, child_value in zip(target.elts, value.elts):
                self._bind(child_target, child_value)

    def _visit_body(self, body: list[ast.stmt]) -> None:
        for statement in body:
            self.visit(statement)

    def visit_Module(self, node: ast.Module) -> None:
        self._visit_body(node.body)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.scopes.append({})
        self._visit_body(node.body)
        self.scopes.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        for target in node.targets:
            self._bind(target, node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is None:
            return
        self.visit(node.value)
        self._bind(node.target, node.value)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.visit(node.value)
        if not isinstance(node.target, ast.Name) or not isinstance(node.op, ast.Add):
            return
        previous = self._lookup(node.target.id)
        addition = self._evaluate(node.value)
        if previous is None or addition is None:
            self.scopes[-1].pop(node.target.id, None)
        else:
            self.scopes[-1][node.target.id] = previous + addition

    def visit_Call(self, node: ast.Call) -> None:
        if _python_call_name(node.func) in ATTACK_SINKS:
            self.has_attack_sink = True
            values = [
                value
                for value in (
                    *(self._evaluate(argument) for argument in node.args),
                    *(self._evaluate(keyword.value) for keyword in node.keywords),
                )
                if value is not None
            ]
            if values:
                self.sink_texts.append(" ".join(values))
        self.generic_visit(node)


def _split_top_level(expression: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    start = 0
    quote = ""
    escaped = False
    depth = 0
    for index, char in enumerate(expression):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in "'\"`":
            quote = char
        elif char in "([{":
            depth += 1
        elif char in ")]}" and depth:
            depth -= 1
        elif char == delimiter and depth == 0:
            parts.append(expression[start:index].strip())
            start = index + 1
    parts.append(expression[start:].strip())
    return parts


def _evaluate_javascript_string(expression: str, values: dict[str, str]) -> str | None:
    expression = expression.strip().rstrip(";").strip()
    if not expression:
        return None
    if expression.startswith("`") and expression.endswith("`"):
        unresolved = False

        def replace(match: re.Match[str]) -> str:
            nonlocal unresolved
            value = values.get(match.group(1))
            if value is None:
                unresolved = True
                return ""
            return value

        rendered = re.sub(r"\$\{\s*([A-Za-z_$][\w$]*)\s*\}", replace, expression[1:-1])
        return None if unresolved else rendered
    if expression[0:1] in {"'", '"'} and expression[-1:] == expression[0]:
        try:
            literal = ast.literal_eval(expression)
        except (SyntaxError, ValueError):
            return None
        return literal if isinstance(literal, str) else None
    pieces = _split_top_level(expression, "+")
    if len(pieces) > 1:
        resolved = [_evaluate_javascript_string(piece, values) for piece in pieces]
        return "".join(resolved) if all(value is not None for value in resolved) else None
    if re.fullmatch(r"[A-Za-z_$][\w$]*", expression):
        return values.get(expression)
    return None


def _code_position_mask(body: str) -> list[bool]:
    """Mark positions outside quoted strings and JavaScript-style comments."""

    mask = [True] * len(body)
    index = 0
    quote = ""
    escaped = False
    while index < len(body):
        char = body[index]
        if quote:
            mask[index] = False
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            index += 1
            continue
        if char in "'\"`":
            quote = char
            mask[index] = False
            index += 1
            continue
        if body.startswith("//", index):
            end = body.find("\n", index)
            end = len(body) if end < 0 else end
            mask[index:end] = [False] * (end - index)
            index = end
            continue
        if body.startswith("/*", index):
            end = body.find("*/", index + 2)
            end = len(body) if end < 0 else end + 2
            mask[index:end] = [False] * (end - index)
            index = end
            continue
        index += 1
    return mask


def _sink_argument_expressions(body: str) -> list[str]:
    arguments: list[str] = []
    code_positions = _code_position_mask(body)
    for match in SINK_CALL_START.finditer(body):
        if not code_positions[match.start()]:
            continue
        line_start = body.rfind("\n", 0, match.start()) + 1
        declaration_prefix = body[line_start : match.start()]
        if re.search(r"\b(?:def|function)\s*$", declaration_prefix):
            continue
        start = match.end()
        quote = ""
        escaped = False
        depth = 1
        for index in range(start, len(body)):
            char = body[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = ""
                continue
            if char in "'\"`":
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    arguments.append(body[start:index])
                    break
    return arguments


def attack_sink_evidence(body: str, language: str) -> tuple[bool, list[str]]:
    """Return attack-sink presence plus only statically resolved string inputs.

    Dynamic inputs remain unresolved by design. They fail closed only when the
    surrounding block independently contains privacy-attack semantics.
    """

    generic_arguments = _sink_argument_expressions(body)
    if language in PYTHON_LANGUAGES:
        try:
            tree = ast.parse(body)
        except SyntaxError:
            return bool(generic_arguments), []
        flow = _PythonStringFlow()
        flow.visit(tree)
        return flow.has_attack_sink, flow.sink_texts

    values: dict[str, str] = {}
    if language in JAVASCRIPT_LANGUAGES:
        for line in body.splitlines():
            match = SIMPLE_JS_ASSIGNMENT.match(line)
            if match is None:
                continue
            name, expression = match.groups()
            resolved = _evaluate_javascript_string(expression, values)
            if resolved is None:
                values.pop(name, None)
            else:
                values[name] = resolved
        sink_texts: list[str] = []
        for expression in generic_arguments:
            resolved_arguments = [
                _evaluate_javascript_string(argument, values)
                for argument in _split_top_level(expression, ",")
            ]
            known = [value for value in resolved_arguments if value is not None]
            if known:
                sink_texts.append(" ".join(known))
        return bool(generic_arguments), sink_texts

    return bool(generic_arguments), []


def looks_offensive(body: str, language: str = "") -> bool:
    if any(pattern.search(body) for pattern in OFFENSIVE_PATTERNS):
        return True

    has_attack_sink, sink_texts = attack_sink_evidence(body, language)
    if any(
        contains_privacy_marker(text) or contains_personal_record_query(text)
        for text in sink_texts
    ):
        return True
    return has_attack_sink and (
        contains_privacy_marker(body) or contains_personal_record_query(body)
    )


def attached_contract(lines: list[str], marker_index: int) -> str:
    """Return a complete adjacent six-field contract, allowing tailored values."""

    start = marker_index - len(REQUIRED_FIELDS) - 1
    if start < 0:
        return ""
    candidate = lines[start:marker_index]
    if candidate[0] != CONTRACT_HEADER:
        return ""
    for line, field in zip(candidate[1:], REQUIRED_FIELDS):
        if not re.fullmatch(rf"> - `{re.escape(field)}`:\s*\S.*", line):
            return ""
    return "\n".join(candidate)


def analyze_markdown(path: Path, text: str) -> tuple[list[SafeLabBlock], list[str]]:
    lines = text.splitlines()
    blocks: list[SafeLabBlock] = []
    issues: list[str] = []
    index = 0
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
        executable = language in EXECUTABLE_LANGUAGES or looks_offensive(body, language)
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
        elif classification == "defensive-only" and looks_offensive(body, language):
            issues.append(
                f"{location}: offensive content cannot use defensive-only exemption"
            )
        elif classification == "offensive":
            contract = attached_contract(lines, index - 1)
            if not contract:
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
