"""Human-readable reports for TrimResult."""
from __future__ import annotations

from envguard.env_trimmer import TrimResult


def format_trim_result(result: TrimResult, *, color: bool = False) -> str:
    """Return a multi-line summary of what was trimmed."""
    lines = []

    _G = "\033[32m" if color else ""
    _Y = "\033[33m" if color else ""
    _R = "\033[0m" if color else ""

    lines.append(f"Source : {result.source}")
    lines.append(f"Keys   : {len(result.original)}")

    if not result:
        lines.append(f"{_G}All values are already clean — nothing to trim.{_R}")
        return "\n".join(lines)

    lines.append(
        f"{_Y}{len(result.changed_keys)} value(s) trimmed:{_R}"
    )
    for key in result.changed_keys:
        before = repr(result.original[key])
        after = repr(result.trimmed[key])
        lines.append(f"  {key}: {before} -> {after}")

    return "\n".join(lines)


def format_trimmed_preview(result: TrimResult) -> str:
    """Return a compact before/after table for changed keys only."""
    if not result.changed_keys:
        return "(no changes)"

    col = max(len(k) for k in result.changed_keys)
    rows = [f"{'KEY':<{col}}  BEFORE                AFTER"]
    rows.append("-" * (col + 44))
    for key in result.changed_keys:
        before = repr(result.original[key])[:20]
        after = repr(result.trimmed[key])[:20]
        rows.append(f"{key:<{col}}  {before:<20}  {after}")
    return "\n".join(rows)
