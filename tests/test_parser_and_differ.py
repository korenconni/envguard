"""Tests for envguard parser and differ."""
import textwrap
from pathlib import Path

import pytest

from envguard.parser import parse_env_file, EnvParseError
from envguard.differ import diff_envs


@pytest.fixture()
def tmp_env(tmp_path):
    """Helper: write content to a temp .env file and return its path."""
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content))
        return str(p)
    return _write


class TestParser:
    def test_basic_key_value(self, tmp_env):
        path = tmp_env("FOO=bar\nBAZ=qux\n")
        assert parse_env_file(path) == {"FOO": "bar", "BAZ": "qux"}

    def test_quoted_values(self, tmp_env):
        path = tmp_env('KEY="hello world"\nKEY2=\'single\'\n')
        assert parse_env_file(path) == {"KEY": "hello world", "KEY2": "single"}

    def test_empty_value_becomes_none(self, tmp_env):
        path = tmp_env("EMPTY=\n")
        assert parse_env_file(path) == {"EMPTY": None}

    def test_comments_and_blank_lines_skipped(self, tmp_env):
        path = tmp_env("# comment\n\nFOO=1\n")
        assert parse_env_file(path) == {"FOO": "1"}

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            parse_env_file("/nonexistent/.env")

    def test_invalid_line_raises(self, tmp_env):
        path = tmp_env("INVALID_LINE\n")
        with pytest.raises(EnvParseError):
            parse_env_file(path)


class TestDiffer:
    def test_identical_envs(self):
        env = {"A": "1", "B": "2"}
        result = diff_envs(env, env.copy())
        assert not result.has_differences

    def test_missing_key(self):
        result = diff_envs({"A": "1", "B": "2"}, {"A": "1"})
        assert result.missing_keys == ["B"]
        assert not result.extra_keys

    def test_extra_key(self):
        result = diff_envs({"A": "1"}, {"A": "1", "X": "9"})
        assert result.extra_keys == ["X"]

    def test_changed_value(self):
        result = diff_envs({"A": "old"}, {"A": "new"})
        assert "A" in result.changed_keys
        assert result.changed_keys["A"] == ("old", "new")

    def test_has_differences_flag(self):
        result = diff_envs({"A": "1"}, {"B": "2"})
        assert result.has_differences
