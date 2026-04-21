"""Format CompareResult objects for terminal output."""
from __future__ import annotations

from envguard.env_comparator import CompareResult
from envguard.reporter import _color

_ADDED = "green"
_REMOVED = "red"
_CHANGED = "yellow"
_NEUTRAL = "reset"


def format_compare_result(result: CompareResult, *, show_unchanged: bool = False) -> str:
    lines: list[str] = [
        _color(f"Comparing: {result.left_path}  <>  {result.right_path}", "cyan"),
        "",
    ]

    if not result.has_differences and not show_unchanged:
        lines.append(_color("No differences found.", "green"))
        return "\n".join(lines)

    for c in result.added:
        lines.append(_color(f"  + {c.key} = {c.right_value!r}", _ADDED))

    for c in result.removed:
        lines.append(_color(f"  - {c.key} = {c.left_value!r}", _REMOVED))

    for c in result.changed:
        lines.append(_color(f"  ~ {c.key}", _CHANGED))
        lines.append(_color(f"      left : {c.left_value!r}", _REMOVED))
        lines.append(_color(f"      right: {c.right_value!r}", _ADDED))

    if show_unchanged:
        for c in result.unchanged:
            lines.append(f"    {c.key} = {c.left_value!r}")

    lines.append("")
    lines.append(
        f"Summary: "
        + _color(f"{len(result.added)} added", _ADDED)
        + ", "
        + _color(f"{len(result.removed)} removed", _REMOVED)
        + ", "
        + _color(f"{len(result.changed)} changed", _CHANGED)
        + f", {len(result.unchanged)} unchanged"
    )
    return "\n".join(lines)
