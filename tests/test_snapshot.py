"""Tests for envguard.snapshot."""
import pytest
from pathlib import Path

from envguard.snapshot import (
    SnapshotError,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)

SAMPLE_ENV = {"DB_HOST": "localhost", "DEBUG": "true", "PORT": "5432"}


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path / "snaps"


def test_save_creates_file(snap_dir):
    path = save_snapshot(SAMPLE_ENV, "prod", directory=snap_dir)
    assert path.exists()
    assert path.name == "prod.json"


def test_round_trip(snap_dir):
    save_snapshot(SAMPLE_ENV, "staging", directory=snap_dir)
    loaded = load_snapshot("staging", directory=snap_dir)
    assert loaded == SAMPLE_ENV


def test_load_missing_raises(snap_dir):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot("ghost", directory=snap_dir)


def test_list_snapshots_empty(snap_dir):
    assert list_snapshots(snap_dir) == []


def test_list_snapshots_multiple(snap_dir):
    for name in ("alpha", "beta", "gamma"):
        save_snapshot(SAMPLE_ENV, name, directory=snap_dir)
    assert list_snapshots(snap_dir) == ["alpha", "beta", "gamma"]


def test_delete_snapshot(snap_dir):
    save_snapshot(SAMPLE_ENV, "old", directory=snap_dir)
    delete_snapshot("old", directory=snap_dir)
    assert list_snapshots(snap_dir) == []


def test_delete_missing_raises(snap_dir):
    with pytest.raises(SnapshotError):
        delete_snapshot("nope", directory=snap_dir)


def test_label_stored(snap_dir):
    import json
    path = save_snapshot(SAMPLE_ENV, "v1", directory=snap_dir, label="Version 1")
    data = json.loads(path.read_text())
    assert data["label"] == "Version 1"
    assert "created_at" in data
