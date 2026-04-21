"""Format ProfileResult for terminal output."""
from __future__ import annotations

from envguard.env_profiler import ProfileResult

_TYPE_ORDER = ["string", "int", "float", "bool", "url", "path", "empty"]


def format_profile_result(result: ProfileResult) -> str:
    lines: list[str] = []
    lines.append(f"Profile: {result.source}")
    lines.append("-" * 40)
    lines.append(f"  Total keys      : {result.total_keys}")
    lines.append(f"  Empty values    : {result.empty_values}")
    lines.append(f"  UPPERCASE keys  : {result.uppercase_keys}")
    lines.append(f"  Mixed-case keys : {result.mixed_case_keys}")

    if result.longest_key:
        lines.append(f"  Longest key     : {result.longest_key}")
    if result.longest_value_key:
        lines.append(f"  Longest value @ : {result.longest_value_key}")

    if result.type_counts:
        lines.append("")
        lines.append("  Value type breakdown:")
        for t in _TYPE_ORDER:
            count = result.type_counts.get(t, 0)
            if count:
                lines.append(f"    {t:<10} {count}")
        # any unexpected types
        for t, count in result.type_counts.items():
            if t not in _TYPE_ORDER:
                lines.append(f"    {t:<10} {count}")

    return "\n".join(lines)
