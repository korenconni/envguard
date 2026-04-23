"""Tests for envguard.env_trimmer and envguard.trim_reporter."""
from __future__ import annotations

import pytest
from pathlib import Path

from envguard.env_trimmer import (
    TrimResult,
    trim_env,
    trim_env_file,
    render_trimmed_env,
    write_trimmed,
)
from envguard.trim_reporter import format_trim_result, format_trimmed_preview


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Return a helper that writes an .env file and returns its path."""

    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content, encoding="utf-8")
        return str(p)

    return _write


# ---------------------------------------------------------------------------
# trim_env (dict-based)
# ---------------------------------------------------------------------------

def test_clean_values_unchanged():
    result = trim_env({"KEY": "value", "OTHER": "123"})
    assert not result
    assert result.changed_keys == []
    assert result.trimmed == {"KEY": "value", "OTHER": "123"}


def test_leading_whitespace_trimmed():
    result = trim_env({"KEY": "  hello"})
    assert result
    assert result.trimmed["KEY"] == "hello"
    assert "KEY" in result.changed_keys


def test_trailing_whitespace_trimmed():
    result = trim_env({"KEY": "hello   "})
    assert result.trimmed["KEY"] == "hello"


def test_both_sides_trimmed():
    result = trim_env({"KEY": "  hello  "})
    assert result.trimmed["KEY"] == "hello"


def test_only_changed_keys_listed():
    result = trim_env({"A": " x", "B": "y", "C": "z "})
    assert set(result.changed_keys) == {"A", "C"}


def test_empty_value_unchanged():
    result = trim_env({"KEY": ""})
    assert not result


# ---------------------------------------------------------------------------
# trim_env_file
# ---------------------------------------------------------------------------

def test_trim_env_file_sets_source(tmp_env):
    path = tmp_env("KEY= hello \nOTHER=clean\n")
    result = trim_env_file(path)
    assert result.source == path
    assert result.trimmed["KEY"] == "hello"


# ---------------------------------------------------------------------------
# render_trimmed_env
# ---------------------------------------------------------------------------

def test_render_quoted_empty_value():
    result = trim_env({"EMPTY": ""})
    rendered = render_trimmed_env(result)
    assert 'EMPTY=""' in rendered


def test_render_plain_value():
    result = trim_env({"KEY": "value"})
    rendered = render_trimmed_env(result)
    assert "KEY=value" in rendered


# ---------------------------------------------------------------------------
# write_trimmed
# ---------------------------------------------------------------------------

def test_write_trimmed_overwrites_source(tmp_env):
    path = tmp_env("KEY= padded \n")
    result = trim_env_file(path)
    written = write_trimmed(result)
    content = written.read_text()
    assert "padded" in content
    assert " padded " not in content


# ---------------------------------------------------------------------------
# reporters
# ---------------------------------------------------------------------------

def test_format_trim_result_clean():
    result = TrimResult(source="a.env", original={"K": "v"}, trimmed={"K": "v"})
    report = format_trim_result(result)
    assert "nothing to trim" in report


def test_format_trim_result_shows_changes():
    result = TrimResult(
        source="a.env",
        original={"K": " v "},
        trimmed={"K": "v"},
        changed_keys=["K"],
    )
    report = format_trim_result(result)
    assert "K" in report
    assert "->" in report


def test_format_trimmed_preview_no_changes():
    result = TrimResult(source="a.env", original={}, trimmed={}, changed_keys=[])
    assert format_trimmed_preview(result) == "(no changes)"


def test_format_trimmed_preview_has_header():
    result = TrimResult(
        source="a.env",
        original={"FOO": " bar"},
        trimmed={"FOO": "bar"},
        changed_keys=["FOO"],
    )
    preview = format_trimmed_preview(result)
    assert "KEY" in preview
    assert "BEFORE" in preview
    assert "FOO" in preview
