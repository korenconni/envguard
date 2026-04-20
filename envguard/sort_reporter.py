"""Format human-readable reports for env sort operations."""

from __future__ import annotations

from envguard.env_sorter import SortResult
from envguard.reporter import _color


def format_sort_result(result: SortResult, *, color: bool = True) -> str:
    """Return a human-readable summary of a sort operation."""
    lines: list[str] = []

    if result.already_sorted:
        msg = "✔ File is already sorted."
        lines.append(_color(msg, "green") if color else msg)
        return "\n".join(lines)

    header = f"Keys require reordering ({len(result.moved)} moved):"
    lines.append(_color(header, "yellow") if color else header)

    for key, old_idx, new_idx in result.moved:
        arrow = f"  {key}: position {old_idx + 1} → {new_idx + 1}"
        lines.append(arrow)

    return "\n".join(lines)


def format_sorted_preview(rendered: str, *, color: bool = True) -> str:
    """Return a labelled preview of the sorted .env content."""
    label = "--- Sorted output ---"
    header = _color(label, "cyan") if color else label
    return header + "\n" + rendered
