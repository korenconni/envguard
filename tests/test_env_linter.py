"""Tests for envguard.env_linter and envguard.lint_reporter."""
from __future__ import annotations

import pytest

from envguard.env_linter import lint_env_file, LintResult
from envguard.lint_reporter import format_lint_result


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(content: str):
        p = tmp_path / ".env"
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _write


def test_clean_file_has_no_issues(tmp_env):
    path = tmp_env("DATABASE_URL=postgres://localhost/db\nSECRET_KEY=abc123\n")
    result = lint_env_file(path)
    assert not result.has_issues


def test_lowercase_key_triggers_w001(tmp_env):
    path = tmp_env("database_url=postgres://localhost/db\n")
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "W001" in codes


def test_duplicate_key_triggers_w002(tmp_env):
    path = tmp_env("API_KEY=first\nAPI_KEY=second\n")
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_unquoted_value_with_spaces_triggers_w003(tmp_env):
    path = tmp_env("APP_NAME=My Cool App\n")
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "W003" in codes


def test_quoted_value_with_spaces_no_w003(tmp_env):
    path = tmp_env('APP_NAME="My Cool App"\n')
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "W003" not in codes


def test_missing_equals_triggers_e001(tmp_env):
    path = tmp_env("BROKEN_LINE\n")
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "E001" in codes
    assert result.errors


def test_key_with_spaces_triggers_e002(tmp_env):
    path = tmp_env("MY KEY=value\n")
    result = lint_env_file(path)
    codes = [i.code for i in result.issues]
    assert "E002" in codes


def test_comments_and_blanks_ignored(tmp_env):
    path = tmp_env("# comment\n\nVALID=yes\n")
    result = lint_env_file(path)
    assert not result.has_issues


def test_format_lint_result_no_issues(tmp_env):
    path = tmp_env("OK=1\n")
    result = lint_env_file(path)
    output = format_lint_result(result, path, use_color=False)
    assert "No issues found" in output


def test_format_lint_result_shows_issues(tmp_env):
    path = tmp_env("bad_key=value\nDUP=1\nDUP=2\n")
    result = lint_env_file(path)
    output = format_lint_result(result, path, use_color=False)
    assert "W001" in output
    assert "W002" in output
    assert "issue(s)" in output
