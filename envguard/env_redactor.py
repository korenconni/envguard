"""Redact sensitive values in .env files for safe sharing or logging."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE_PATTERNS = (
    "secret", "password", "passwd", "token", "api_key", "apikey",
    "private", "auth", "credential", "cert", "key", "pwd",
)

DEFAULT_MASK = "***REDACTED***"


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in _SENSITIVE_PATTERNS)


@dataclass
class RedactResult:
    source: str
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)
    mask: str = DEFAULT_MASK

    def __bool__(self) -> bool:
        return len(self.redacted_keys) > 0

    @property
    def total_keys(self) -> int:
        return len(self.original)

    @property
    def redacted_count(self) -> int:
        return len(self.redacted_keys)


def redact_env(
    env: Dict[str, str],
    source: str = "<input>",
    mask: str = DEFAULT_MASK,
    extra_keys: Optional[List[str]] = None,
    all_values: bool = False,
) -> RedactResult:
    """Return a RedactResult with sensitive values replaced by *mask*.

    Args:
        env: Parsed key/value mapping.
        source: Display name for the origin file.
        mask: Replacement string for redacted values.
        extra_keys: Additional key names to always redact (case-insensitive).
        all_values: If True, redact every value regardless of key name.
    """
    extra = {k.lower() for k in (extra_keys or [])}
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if all_values or _is_sensitive(key) or key.lower() in extra:
            redacted[key] = mask
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(
        source=source,
        original=dict(env),
        redacted=redacted,
        redacted_keys=sorted(redacted_keys),
        mask=mask,
    )


def render_redacted_env(result: RedactResult) -> str:
    """Render the redacted env as .env-formatted text."""
    lines = []
    for key, value in result.redacted.items():
        if " " in value or "#" in value:
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines)
