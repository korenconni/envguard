"""Scan .env files for hardcoded secrets and suspicious patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Patterns that suggest a value is a real secret rather than a placeholder
_SECRET_PATTERNS: List[Tuple[str, str]] = [
    (r"[A-Za-z0-9+/]{40,}={0,2}", "base64-like string"),
    (r"[0-9a-fA-F]{32,}", "hex string"),
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI-style key"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub personal access token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key ID"),
    (r"-----BEGIN [A-Z ]+KEY-----", "PEM private key"),
    (r"xox[baprs]-[0-9A-Za-z\-]{10,}", "Slack token"),
]

_SENSITIVE_KEY_RE = re.compile(
    r"(password|passwd|secret|token|api_?key|auth|credential|private_?key)",
    re.IGNORECASE,
)


@dataclass
class ScanIssue:
    key: str
    value: str
    reason: str
    severity: str  # "error" | "warning"


@dataclass
class ScanResult:
    source: str
    issues: List[ScanIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[ScanIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ScanIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def _looks_like_secret(value: str) -> str | None:
    """Return the matched pattern description if value looks like a real secret."""
    for pattern, description in _SECRET_PATTERNS:
        if re.search(pattern, value):
            return description
    return None


def scan_env(env: Dict[str, str], source: str = "<env>") -> ScanResult:
    """Scan an env mapping for hardcoded secrets."""
    result = ScanResult(source=source)

    for key, value in env.items():
        if not value:
            continue

        is_sensitive_key = bool(_SENSITIVE_KEY_RE.search(key))
        pattern_match = _looks_like_secret(value)

        if is_sensitive_key and pattern_match:
            result.issues.append(
                ScanIssue(
                    key=key,
                    value=value,
                    reason=f"sensitive key contains {pattern_match}",
                    severity="error",
                )
            )
        elif pattern_match and not is_sensitive_key:
            result.issues.append(
                ScanIssue(
                    key=key,
                    value=value,
                    reason=f"value resembles a secret ({pattern_match})",
                    severity="warning",
                )
            )

    return result
