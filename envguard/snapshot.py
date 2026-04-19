"""Snapshot management: save and load .env snapshots for later diffing."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

DEFAULT_SNAPSHOT_DIR = Path(".envguard_snapshots")


class SnapshotError(Exception):
    pass


def _snapshot_path(name: str, directory: Path) -> Path:
    return directory / f"{name}.json"


def save_snapshot(
    env: Dict[str, str],
    name: str,
    directory: Path = DEFAULT_SNAPSHOT_DIR,
    label: Optional[str] = None,
) -> Path:
    """Persist *env* dict as a named snapshot. Returns the file path."""
    directory.mkdir(parents=True, exist_ok=True)
    path = _snapshot_path(name, directory)
    payload = {
        "name": name,
        "label": label or name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "env": env,
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_snapshot(
    name: str,
    directory: Path = DEFAULT_SNAPSHOT_DIR,
) -> Dict[str, str]:
    """Load a previously saved snapshot and return the env dict."""
    path = _snapshot_path(name, directory)
    if not path.exists():
        raise SnapshotError(f"Snapshot '{name}' not found at {path}")
    payload = json.loads(path.read_text())
    return payload["env"]


def list_snapshots(directory: Path = DEFAULT_SNAPSHOT_DIR) -> list[str]:
    """Return sorted snapshot names available in *directory*."""
    if not directory.exists():
        return []
    return sorted(p.stem for p in directory.glob("*.json"))


def delete_snapshot(
    name: str,
    directory: Path = DEFAULT_SNAPSHOT_DIR,
) -> None:
    path = _snapshot_path(name, directory)
    if not path.exists():
        raise SnapshotError(f"Snapshot '{name}' not found at {path}")
    path.unlink()
