"""Tests for envguard.env_merger."""
import os
import pytest

from envguard.env_merger import merge_env_files, format_merge_report


@pytest.fixture()
def tmp_envs(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


def test_merge_single_source(tmp_envs):
    p = tmp_envs("a.env", "FOO=bar\nBAZ=qux\n")
    result = merge_env_files([("a", p)])
    assert result.merged == {"FOO": "bar", "BAZ": "qux"}
    assert result.overrides == {}


def test_merge_override_later_wins(tmp_envs):
    a = tmp_envs("a.env", "FOO=first\nSHARED=from_a\n")
    b = tmp_envs("b.env", "BAR=second\nSHARED=from_b\n")
    result = merge_env_files([("a", a), ("b", b)], override=True)
    assert result.merged["SHARED"] == "from_b"
    assert result.merged["FOO"] == "first"
    assert result.merged["BAR"] == "second"
    assert "SHARED" in result.overrides


def test_merge_no_override_first_wins(tmp_envs):
    a = tmp_envs("a.env", "SHARED=from_a\n")
    b = tmp_envs("b.env", "SHARED=from_b\n")
    result = merge_env_files([("a", a), ("b", b)], override=False)
    assert result.merged["SHARED"] == "from_a"
    assert result.overrides == {}


def test_merge_three_sources_override_chain(tmp_envs):
    a = tmp_envs("a.env", "KEY=v1\n")
    b = tmp_envs("b.env", "KEY=v2\n")
    c = tmp_envs("c.env", "KEY=v3\n")
    result = merge_env_files([("a", a), ("b", b), ("c", c)])
    assert result.merged["KEY"] == "v3"
    assert len(result.overrides["KEY"]) == 2


def test_format_merge_report_no_overrides(tmp_envs):
    p = tmp_envs("a.env", "X=1\n")
    result = merge_env_files([("a", p)])
    report = format_merge_report(result)
    assert "1 keys" in report
    assert "No keys were overridden" in report


def test_format_merge_report_with_overrides(tmp_envs):
    a = tmp_envs("a.env", "FOO=old\n")
    b = tmp_envs("b.env", "FOO=new\n")
    result = merge_env_files([("a", a), ("b", b)])
    report = format_merge_report(result)
    assert "FOO" in report
    assert "overridden" in report.lower()
