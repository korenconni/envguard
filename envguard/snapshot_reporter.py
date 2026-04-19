"""Formatting helpers for snapshot-related output."""
from __future__ import annotations

from pathlib import Path
from typing import List

from envguard.reporter import _color, format_diff
from envguard.differ import diff_envs
from envguard.snapshot import list_snapshots


def format_snapshot_diff(name_a: str, name_b: str, env_a: dict, env_b: dict) -> str:
    """Return a human-readable diff between two named snapshots."""
    result = diff_envs(env_a, env_b)
    header = (
        _color(f"Snapshot diff: {name_a}", "cyan")
        + " → "
        + _color(name_b, "cyan")
        + "\n"
    )
    return header + format_diff(result, label_a=name_a, label_b=name_b)


def format_snapshot_list(names: List[str], directory: Path) -> str:
    """Return a formatted list of available snapshots."""
    if not names:
        return _color("No snapshots found.", "yellow") + f" (directory: {directory})\n"
    lines = [_color(f"Snapshots in {directory}:", "cyan")]
    for name in names:
        lines.append(f"  • {name}")
    return "\n".join(lines) + "\n"
