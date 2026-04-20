"""Lint .env files for common issues and style violations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envguard.parser import parse_env_file


@dataclass
class LintIssue:
    line: int
    key: str
    code: str
    message: str
    severity: str = "warning"  # "warning" | "error"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def lint_env_file(path: str) -> LintResult:
    """Run all lint checks on an .env file and return a LintResult."""
    result = LintResult()
    pairs = parse_env_file(path)
    seen_keys: dict[str, int] = {}

    with open(path, encoding="utf-8") as fh:
        raw_lines = fh.readlines()

    for lineno, raw in enumerate(raw_lines, start=1):
        stripped = raw.rstrip("\n")

        # Skip blanks and comments
        if not stripped or stripped.lstrip().startswith("#"):
            continue

        if "=" not in stripped:
            result.issues.append(LintIssue(lineno, "", "E001", "Line has no '=' separator", "error"))
            continue

        key, _, value = stripped.partition("=")
        key = key.strip()

        if key != key.upper():
            result.issues.append(LintIssue(lineno, key, "W001", f"Key '{key}' is not uppercase", "warning"))

        if " " in key:
            result.issues.append(LintIssue(lineno, key, "E002", f"Key '{key}' contains spaces", "error"))

        if key in seen_keys:
            result.issues.append(LintIssue(
                lineno, key, "W002",
                f"Duplicate key '{key}' (first seen on line {seen_keys[key]})",
                "warning",
            ))
        else:
            seen_keys[key] = lineno

        unquoted = value.strip()
        if unquoted and " " in unquoted and not (
            (unquoted.startswith('"') and unquoted.endswith('"')) or
            (unquoted.startswith("'") and unquoted.endswith("'"))
        ):
            result.issues.append(LintIssue(
                lineno, key, "W003",
                f"Value for '{key}' contains spaces but is not quoted",
                "warning",
            ))

    _ = pairs  # parsed pairs available for future checks
    return result
