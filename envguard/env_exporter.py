"""Export parsed .env data to various output formats (JSON, YAML, shell export)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Literal, Optional

ExportFormat = Literal["json", "yaml", "shell"]


@dataclass
class ExportResult:
    source: str
    fmt: str
    content: str
    key_count: int
    warnings: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:  # noqa: D105
        return not self.warnings


def _to_json(env: Dict[str, str], indent: int = 2) -> str:
    return json.dumps(env, indent=indent, sort_keys=True)


def _to_yaml(env: Dict[str, str]) -> str:
    """Minimal YAML serialisation without requiring PyYAML."""
    lines: list[str] = []
    for key in sorted(env):
        value = env[key]
        # Quote values that contain special YAML characters.
        if any(ch in value for ch in (':', '#', "'", '"', '\n', '{', '}', '[', ']')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}: "{escaped}"')
        else:
            lines.append(f"{key}: {value}" if value else f"{key}: \"\"")
    return "\n".join(lines)


def _to_shell(env: Dict[str, str]) -> str:
    lines = ["#!/usr/bin/env sh"]
    for key in sorted(env):
        value = env[key].replace("'", "'\"'\"'")
        lines.append(f"export {key}='{value}'")
    return "\n".join(lines)


_FORMATTERS = {
    "json": _to_json,
    "yaml": _to_yaml,
    "shell": _to_shell,
}


def export_env(
    env: Dict[str, str],
    fmt: ExportFormat,
    source: str = "<env>",
    exclude_empty: bool = False,
) -> ExportResult:
    """Convert *env* dict to the requested *fmt* string."""
    warnings: list[str] = []
    working = dict(env)

    if exclude_empty:
        removed = [k for k, v in working.items() if v == ""]
        for k in removed:
            del working[k]
        if removed:
            warnings.append(f"Excluded {len(removed)} empty key(s): {', '.join(sorted(removed))}")

    formatter = _FORMATTERS.get(fmt)
    if formatter is None:
        raise ValueError(f"Unsupported export format: {fmt!r}. Choose from {list(_FORMATTERS)}.")

    content = formatter(working)
    return ExportResult(
        source=source,
        fmt=fmt,
        content=content,
        key_count=len(working),
        warnings=warnings,
    )
