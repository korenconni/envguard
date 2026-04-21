"""Tests for env_comparator and compare_reporter."""
from __future__ import annotations

import os
import pytest

from envguard.env_comparator import compare_env_files, CompareResult, KeyComparison
from envguard.compare_reporter import format_compare_result


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


# ---------------------------------------------------------------------------
# compare_env_files
# ---------------------------------------------------------------------------

def test_identical_files_have_no_differences(tmp_env):
    left = tmp_env("a.env", "FOO=bar\nBAZ=qux\n")
    right = tmp_env("b.env", "FOO=bar\nBAZ=qux\n")
    result = compare_env_files(left, right)
    assert not result.has_differences
    assert len(result.unchanged) == 2


def test_added_key_detected(tmp_env):
    left = tmp_env("a.env", "FOO=bar\n")
    right = tmp_env("b.env", "FOO=bar\nNEW=value\n")
    result = compare_env_files(left, right)
    assert result.has_differences
    assert len(result.added) == 1
    assert result.added[0].key == "NEW"
    assert result.added[0].left_value is None
    assert result.added[0].right_value == "value"


def test_removed_key_detected(tmp_env):
    left = tmp_env("a.env", "FOO=bar\nOLD=gone\n")
    right = tmp_env("b.env", "FOO=bar\n")
    result = compare_env_files(left, right)
    assert len(result.removed) == 1
    assert result.removed[0].key == "OLD"


def test_changed_value_detected(tmp_env):
    left = tmp_env("a.env", "FOO=old\n")
    right = tmp_env("b.env", "FOO=new\n")
    result = compare_env_files(left, right)
    assert len(result.changed) == 1
    assert result.changed[0].left_value == "old"
    assert result.changed[0].right_value == "new"


def test_ignore_keys_excludes_them(tmp_env):
    left = tmp_env("a.env", "FOO=1\nSECRET=hidden\n")
    right = tmp_env("b.env", "FOO=1\nSECRET=different\n")
    result = compare_env_files(left, right, ignore_keys=["SECRET"])
    assert not result.has_differences


def test_key_comparison_status_added():
    kc = KeyComparison(key="X", left_value=None, right_value="v")
    assert kc.status == "added"


def test_key_comparison_status_removed():
    kc = KeyComparison(key="X", left_value="v", right_value=None)
    assert kc.status == "removed"


def test_key_comparison_status_unchanged():
    kc = KeyComparison(key="X", left_value="v", right_value="v")
    assert kc.status == "unchanged"


# ---------------------------------------------------------------------------
# format_compare_result
# ---------------------------------------------------------------------------

def test_format_no_differences_message(tmp_env):
    left = tmp_env("a.env", "FOO=bar\n")
    right = tmp_env("b.env", "FOO=bar\n")
    result = compare_env_files(left, right)
    report = format_compare_result(result)
    assert "No differences found" in report


def test_format_shows_added_key(tmp_env):
    left = tmp_env("a.env", "")
    right = tmp_env("b.env", "NEW=hello\n")
    result = compare_env_files(left, right)
    report = format_compare_result(result)
    assert "NEW" in report
    assert "+" in report


def test_format_summary_counts(tmp_env):
    left = tmp_env("a.env", "A=1\nB=old\n")
    right = tmp_env("b.env", "B=new\nC=3\n")
    result = compare_env_files(left, right)
    report = format_compare_result(result)
    assert "1 added" in report
    assert "1 removed" in report
    assert "1 changed" in report
