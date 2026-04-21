"""Tests for envguard.env_renamer."""
from __future__ import annotations

import pytest
from pathlib import Path

from envguard.env_renamer import rename_keys, write_renamed, RenameResult


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _write


def test_rename_single_key(tmp_env):
    path = tmp_env("OLD_KEY=hello\nOTHER=world\n")
    result = rename_keys(path, {"OLD_KEY": "NEW_KEY"})
    assert result
    assert result.renames_applied == {"OLD_KEY": "NEW_KEY"}
    assert result.skipped == []
    joined = "".join(result.lines)
    assert "NEW_KEY=hello" in joined
    assert "OLD_KEY" not in joined


def test_rename_multiple_keys(tmp_env):
    path = tmp_env("A=1\nB=2\nC=3\n")
    result = rename_keys(path, {"A": "ALPHA", "B": "BETA"})
    assert result
    assert set(result.renames_applied.keys()) == {"A", "B"}
    joined = "".join(result.lines)
    assert "ALPHA=1" in joined
    assert "BETA=2" in joined
    assert "C=3" in joined


def test_missing_key_goes_to_skipped(tmp_env):
    path = tmp_env("EXISTING=yes\n")
    result = rename_keys(path, {"MISSING": "FOUND"})
    assert result
    assert "MISSING" in result.skipped
    assert result.renames_applied == {}


def test_comments_preserved(tmp_env):
    path = tmp_env("# comment\nKEY=val\n")
    result = rename_keys(path, {"KEY": "NEW_KEY"})
    joined = "".join(result.lines)
    assert "# comment" in joined
    assert "NEW_KEY=val" in joined


def test_write_renamed_updates_file(tmp_env):
    path = tmp_env("FOO=bar\n")
    result = rename_keys(path, {"FOO": "BAR"})
    written = write_renamed(result)
    assert written == path
    assert "BAR=bar" in Path(path).read_text()
    assert "FOO" not in Path(path).read_text()


def test_write_renamed_to_new_dest(tmp_env, tmp_path):
    path = tmp_env("X=1\n")
    dest = str(tmp_path / "out.env")
    result = rename_keys(path, {"X": "Y"})
    write_renamed(result, dest=dest)
    assert "Y=1" in Path(dest).read_text()


def test_nonexistent_file_returns_error():
    result = rename_keys("/no/such/file.env", {"A": "B"})
    assert not result
    assert result.error is not None


def test_write_renamed_raises_on_error_result():
    bad = RenameResult(source="/fake", error="oops")
    with pytest.raises(ValueError, match="oops"):
        write_renamed(bad)


def test_no_renames_returns_original_lines(tmp_env):
    content = "KEY=value\n"
    path = tmp_env(content)
    result = rename_keys(path, {})
    assert "".join(result.lines) == content
