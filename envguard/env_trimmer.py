"""Trim whitespace and clean up values in .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from envguard.parser import parse_env_file


@dataclass
class TrimResult:
    source: str
    original: Dict[str, str]
    trimmed: Dict[str, str]
    changed_keys: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        """True when at least one value was changed."""
        return len(self.changed_keys) > 0


def trim_env(env: Dict[str, str]) -> TrimResult:
    """Return a TrimResult with leading/trailing whitespace stripped from values."""
    trimmed: Dict[str, str] = {}
    changed: List[str] = []

    for key, value in env.items():
        clean = value.strip()
        trimmed[key] = clean
        if clean != value:
            changed.append(key)

    return TrimResult(
        source="<dict>",
        original=dict(env),
        trimmed=trimmed,
        changed_keys=changed,
    )


def trim_env_file(path: str) -> TrimResult:
    """Parse *path* and trim all values."""
    env = parse_env_file(path)
    result = trim_env(env)
    result.source = path
    return result


def render_trimmed_env(result: TrimResult) -> str:
    """Render the trimmed env as .env-formatted text."""
    lines: List[str] = []
    for key, value in result.trimmed.items():
        if " " in value or "=" in value or value == "":
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def write_trimmed(result: TrimResult, dest: str | None = None) -> Path:
    """Write trimmed env to *dest* (defaults to overwriting the source)."""
    out = Path(dest) if dest else Path(result.source)
    out.write_text(render_trimmed_env(result), encoding="utf-8")
    return out
