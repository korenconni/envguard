"""Merge multiple .env files with precedence rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envguard.parser import parse_env_file


@dataclass
class MergeResult:
    merged: Dict[str, str]
    overrides: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)
    """Maps key -> list of (source_label, value) pairs that were overridden."""


def merge_env_files(
    sources: List[Tuple[str, str]],
    *,
    override: bool = True,
) -> MergeResult:
    """Merge env files in order.

    Args:
        sources: List of (label, filepath) pairs. Later entries win when
                 override=True (default), earlier entries win otherwise.
        override: If True last source wins; if False first value wins.

    Returns:
        MergeResult with the final merged dict and a record of overrides.
    """
    merged: Dict[str, str] = {}
    overrides: Dict[str, List[Tuple[str, str]]] = {}

    for label, path in sources:
        parsed = parse_env_file(path)
        for key, value in parsed.items():
            if key in merged:
                if override:
                    overrides.setdefault(key, []).append((label, merged[key]))
                    merged[key] = value
                # else: keep first, do nothing
            else:
                merged[key] = value

    return MergeResult(merged=merged, overrides=overrides)


def format_merge_report(result: MergeResult) -> str:
    """Return a human-readable report of the merge."""
    lines: List[str] = []
    lines.append(f"Merged {len(result.merged)} keys.")
    if result.overrides:
        lines.append("\nOverridden keys:")
        for key, history in sorted(result.overrides.items()):
            lines.append(f"  {key}:")
            for src, old_val in history:
                lines.append(f"    [{src}] {old_val!r} -> (overridden)")
    else:
        lines.append("No keys were overridden.")
    return "\n".join(lines)
