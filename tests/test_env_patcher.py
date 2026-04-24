"""Tests for env_patcher module."""
from __future__ import annotations

import pytest
from pathlib import Path

from envguard.env_patcher import patch_env, patch_env_file, render_patched_env


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


def test_add_new_key():
    env = {"A": "1"}
    result = patch_env(env, {"B": "2"})
    assert "B" in result.added
    assert result.added["B"] == "2"
    assert not result.updated


def test_update_existing_key():
    env = {"A": "old"}
    result = patch_env(env, {"A": "new"})
    assert "A" in result.updated
    assert result.updated["A"] == ("old", "new")
    assert not result.added


def test_unchanged_key_not_in_added_or_updated():
    env = {"A": "same"}
    result = patch_env(env, {"A": "same"})
    assert "A" in result.unchanged
    assert not result.added
    assert not result.updated


def test_bool_false_when_no_changes():
    env = {"X": "1"}
    result = patch_env(env, {"X": "1"})
    assert not result


def test_bool_true_when_changes_exist():
    env = {"X": "1"}
    result = patch_env(env, {"X": "2"})
    assert result


def test_render_patched_env_contains_new_key():
    env = {"A": "1"}
    result = patch_env(env, {"B": "2"})
    rendered = render_patched_env(env, result)
    assert "A=1" in rendered
    assert "B=2" in rendered


def test_render_quotes_values_with_spaces():
    env = {}
    result = patch_env(env, {"MSG": "hello world"})
    rendered = render_patched_env(env, result)
    assert 'MSG="hello world"' in rendered


def test_patch_env_file_writes_output(tmp_env, tmp_path):
    src = tmp_env("HOST=localhost\nPORT=5432\n")
    out = str(tmp_path / "patched.env")
    result = patch_env_file(src, {"PORT": "9999", "DEBUG": "true"}, output_path=out)
    assert result.updated.get("PORT") == ("5432", "9999")
    assert "DEBUG" in result.added
    content = Path(out).read_text()
    assert "PORT=9999" in content
    assert "DEBUG=true" in content


def test_patch_env_file_no_output_does_not_write(tmp_env, tmp_path):
    src = tmp_env("KEY=val\n")
    out = str(tmp_path / "should_not_exist.env")
    patch_env_file(src, {"KEY": "new"}, output_path=None)
    assert not Path(out).exists()
