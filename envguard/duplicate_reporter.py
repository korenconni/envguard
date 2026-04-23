"""Format duplicate-value scan results for terminal output."""
from __future__ import annotations

from envguard.env_duplicator import DuplicateResult
from envguard.reporter import _color


def format_duplicate_result(result: DuplicateResult, *, color: bool = True) -> str:
    lines: list[str] = []

    header = f"Duplicate value scan: {result.source}"
    lines.append(_color(header, "bold") if color else header)
    lines.append("")

    if not result.has_duplicates():
        ok = "  ✔ No duplicate values found."
        lines.append(_color(ok, "green") if color else ok)
        return "\n".join(lines)

    summary = (
        f"  Found {result.group_count} group(s) with shared values "
        f"({result.total_duplicate_keys} keys total)."
    )
    lines.append(_color(summary, "yellow") if color else summary)
    lines.append("")

    for i, group in enumerate(result.groups, start=1):
        # Truncate long values for readability
        display_val = group.value if len(group.value) <= 40 else group.value[:37] + "..."
        heading = f"  Group {i}: value = {display_val!r}"
        lines.append(_color(heading, "cyan") if color else heading)
        for key in group.keys:
            lines.append(f"    - {key}")
        lines.append("")

    return "\n".join(lines).rstrip()
