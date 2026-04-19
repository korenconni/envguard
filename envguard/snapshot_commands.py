"""High-level commands that power the 'snapshot' CLI sub-commands."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from envguard.parser import parse_env_file
from envguard.snapshot import (
    DEFAULT_SNAPSHOT_DIR,
    SnapshotError,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from envguard.snapshot_reporter import format_snapshot_diff, format_snapshot_list
from envguard.output import print_diff


def cmd_snapshot_save(
    env_file: str,
    name: str,
    label: Optional[str] = None,
    directory: Path = DEFAULT_SNAPSHOT_DIR,
) -> int:
    env = parse_env_file(env_file)
    path = save_snapshot(env, name, directory=directory, label=label)
    print(f"Snapshot '{name}' saved to {path}")
    return 0


def cmd_snapshot_diff(
    name_a: str,
    name_b: str,
    directory: Path = DEFAULT_SNAPSHOT_DIR,
    use_color: Optional[bool] = None,
) -> int:
    try:
        env_a = load_snapshot(name_a, directory=directory)
        env_b = load_snapshot(name_b, directory=directory)
    except SnapshotError as exc:
        print(f"Error: {exc}")
        return 1
    output = format_snapshot_diff(name_a, name_b, env_a, env_b)
    print(output, end="")
    return 0


def cmd_snapshot_list(directory: Path = DEFAULT_SNAPSHOT_DIR) -> int:
    names = list_snapshots(directory)
    print(format_snapshot_list(names, directory), end="")
    return 0


def cmd_snapshot_delete(
    name: str,
    directory: Path = DEFAULT_SNAPSHOT_DIR,
) -> int:
    try:
        delete_snapshot(name, directory=directory)
        print(f"Snapshot '{name}' deleted.")
        return 0
    except SnapshotError as exc:
        print(f"Error: {exc}")
        return 1
