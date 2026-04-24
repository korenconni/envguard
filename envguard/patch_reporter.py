"""Format PatchResult for human-readable output."""
from __future__ import annotations

from envguard.env_patcher import PatchResult
from envguard.reporter import _color


def format_patch_result(result: PatchResult) -> str:
    lines = [f"Patch report for: {result.source}"]

    if not result:
        lines.append(_color("  No changes applied.", "cyan"))
        return "\n".join(lines)

    if result.added:
        lines.append(_color(f"  Added ({len(result.added)}):", "green"))
        for key, value in sorted(result.added.items()):
            lines.append(_color(f"    + {key}={value}", "green"))

    if result.updated:
        lines.append(_color(f"  Updated ({len(result.updated)}):", "yellow"))
        for key, (old, new) in sorted(result.updated.items()):
            lines.append(_color(f"    ~ {key}: {old!r} -> {new!r}", "yellow"))

    if result.unchanged:
        lines.append(f"  Unchanged ({len(result.unchanged)}): {', '.join(sorted(result.unchanged))}")

    if result.output_path:
        lines.append(f"  Written to: {result.output_path}")

    return "\n".join(lines)
