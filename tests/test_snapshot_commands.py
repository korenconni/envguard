"""Integration tests for snapshot CLI commands."""
import pytest
from pathlib import Path

from envguard.snapshot_commands import (
    cmd_snapshot_delete,
    cmd_snapshot_diff,
    cmd_snapshot_list,
    cmd_snapshot_save,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> str:
    p = tmp_path / ".env"
    p.write_text("APP_ENV=production\nDEBUG=false\nPORT=8080\n")
    return str(p)


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path / "snaps"


def test_save_returns_zero(env_file, snap_dir):
    assert cmd_snapshot_save(env_file, "v1", directory=snap_dir) == 0


def test_list_empty(snap_dir, capsys):
    code = cmd_snapshot_list(directory=snap_dir)
    assert code == 0
    out = capsys.readouterr().out
    assert "No snapshots found" in out


def test_list_after_save(env_file, snap_dir, capsys):
    cmd_snapshot_save(env_file, "v1", directory=snap_dir)
    cmd_snapshot_list(directory=snap_dir)
    out = capsys.readouterr().out
    assert "v1" in out


def test_diff_identical(env_file, snap_dir, capsys):
    cmd_snapshot_save(env_file, "a", directory=snap_dir)
    cmd_snapshot_save(env_file, "b", directory=snap_dir)
    code = cmd_snapshot_diff("a", "b", directory=snap_dir)
    assert code == 0
    out = capsys.readouterr().out
    assert "a" in out and "b" in out


def test_diff_missing_snapshot(snap_dir, capsys):
    code = cmd_snapshot_diff("x", "y", directory=snap_dir)
    assert code == 1
    assert "Error" in capsys.readouterr().out


def test_delete(env_file, snap_dir):
    cmd_snapshot_save(env_file, "old", directory=snap_dir)
    assert cmd_snapshot_delete("old", directory=snap_dir) == 0


def test_delete_missing(snap_dir, capsys):
    code = cmd_snapshot_delete("ghost", directory=snap_dir)
    assert code == 1
    assert "Error" in capsys.readouterr().out
