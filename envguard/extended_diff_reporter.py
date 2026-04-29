"""Reporter for ExtendedDiffResult — human-readable, colour-aware output."""
from __future__ import annotations

from typing import List

from envguard.env_differ_extended import ExtendedDiffResult, ValueChange

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_RESET = "\033[0m"


def _c(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def format_extended_diff(result: ExtendedDiffResult, *, color: bool = True) -> str:
    lines: List[str] = []

    if not result.has_differences:
        lines.append(_c("No differences found.", _GREEN, color))
        return "\n".join(lines)

    if result.added:
        lines.append(_c(f"Added ({len(result.added)}):", _GREEN, color))
        for key, val in sorted(result.added.items()):
            lines.append(f"  + {key}={val}")

    if result.removed:
        lines.append(_c(f"Removed ({len(result.removed)}):", _RED, color))
        for key, val in sorted(result.removed.items()):
            lines.append(f"  - {key}={val}")

    if result.changed:
        lines.append(_c(f"Changed ({len(result.changed)}):", _YELLOW, color))
        for change in sorted(result.changed, key=lambda c: c.key):
            type_note = ""
            if change.is_type_change:
                type_note = _c(
                    f" [type: {change.old_type} → {change.new_type}]", _CYAN, color
                )
            lines.append(
                f"  ~ {change.key}: {change.old_value!r} → {change.new_value!r}{type_note}"
            )

    summary_parts = []
    if result.added:
        summary_parts.append(_c(f"+{len(result.added)} added", _GREEN, color))
    if result.removed:
        summary_parts.append(_c(f"-{len(result.removed)} removed", _RED, color))
    if result.changed:
        summary_parts.append(_c(f"~{len(result.changed)} changed", _YELLOW, color))
    lines.append("")
    lines.append("Summary: " + ", ".join(summary_parts))
    return "\n".join(lines)
