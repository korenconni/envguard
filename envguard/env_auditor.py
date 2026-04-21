"""Audit .env files for security and hygiene issues."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

# Patterns that suggest a value may be a real secret accidentally committed
_SUSPICIOUS_VALUE_PATTERNS = [
    re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|private[_-]?key)"),
]

_PLACEHOLDER_PATTERNS = [
    re.compile(r"^(changeme|replace_me|todo|fixme|xxx|your[_-].*here|<.*>|\$\{.*\})$", re.IGNORECASE),
]

_HIGH_ENTROPY_MIN_LEN = 20  # values longer than this with mixed chars are flagged


@dataclass
class AuditIssue:
    key: str
    code: str
    message: str
    severity: str  # "error" | "warning" | "info"


@dataclass
class AuditResult:
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def _is_placeholder(value: str) -> bool:
    return any(p.match(value) for p in _PLACEHOLDER_PATTERNS)


def _looks_high_entropy(value: str) -> bool:
    if len(value) < _HIGH_ENTROPY_MIN_LEN:
        return False
    has_upper = any(c.isupper() for c in value)
    has_lower = any(c.islower() for c in value)
    has_digit = any(c.isdigit() for c in value)
    return has_upper and has_lower and has_digit


def audit_env(env: Dict[str, str]) -> AuditResult:
    """Run all audit checks against a parsed env mapping."""
    result = AuditResult()

    for key, value in env.items():
        is_sensitive = any(p.search(key) for p in _SUSPICIOUS_VALUE_PATTERNS)

        if is_sensitive and _is_placeholder(value):
            result.issues.append(AuditIssue(
                key=key,
                code="A001",
                message=f"Sensitive key '{key}' has a placeholder value '{value}'.",
                severity="warning",
            ))

        if is_sensitive and value == "":
            result.issues.append(AuditIssue(
                key=key,
                code="A002",
                message=f"Sensitive key '{key}' is set but empty.",
                severity="error",
            ))

        if not is_sensitive and _looks_high_entropy(value):
            result.issues.append(AuditIssue(
                key=key,
                code="A003",
                message=f"Key '{key}' has a high-entropy value that may be a misplaced secret.",
                severity="warning",
            ))

    return result
