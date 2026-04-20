"""Tests for envguard.env_sorter and envguard.sort_reporter."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envguard.env_sorter import render_sorted_env, sort_env, sort_env_file
from envguard.sort_reporter import format_sort_result


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return str(p)

    return _write


# ---------------------------------------------------------------------------
# sort_env
# ---------------------------------------------------------------------------

def test_already_sorted_returns_true():
    env = {"ALPHA": "1", "BETA": "2", "GAMMA": "3"}
    result = sort_env(env)
    assert result.already_sorted is True
    assert result.moved == []


def test_unsorted_detects_moved_keys():
    env = {"ZEBRA": "z", "ALPHA": "a", "MANGO": "m"}
    result = sort_env(env)
    assert result.already_sorted is False
    assert result.sorted_order == ["ALPHA", "MANGO", "ZEBRA"]
    assert len(result.moved) > 0


def test_case_insensitive_sort_default():
    env = {"beta": "b", "ALPHA": "a"}
    result = sort_env(env)
    assert result.sorted_order[0] == "ALPHA"


def test_group_ordering_respected():
    env = {"DB_HOST": "h", "APP_NAME": "n", "DB_PORT": "p", "SECRET": "s"}
    groups = [["APP_NAME"], ["DB_HOST", "DB_PORT"]]
    result = sort_env(env, groups=groups)
    assert result.sorted_order.index("APP_NAME") < result.sorted_order.index("DB_HOST")
    assert result.sorted_order.index("DB_HOST") < result.sorted_order.index("SECRET")


def test_keys_not_in_groups_appended_sorted():
    env = {"ZEBRA": "z", "APP": "a", "MANGO": "m"}
    groups = [["APP"]]
    result = sort_env(env, groups=groups)
    assert result.sorted_order[0] == "APP"
    assert result.sorted_order[1:] == ["MANGO", "ZEBRA"]


# ---------------------------------------------------------------------------
# render_sorted_env
# ---------------------------------------------------------------------------

def test_render_quotes_values_with_spaces():
    env = {"KEY": "hello world"}
    rendered = render_sorted_env(env, ["KEY"])
    assert 'KEY="hello world"' in rendered


def test_render_plain_values_unquoted():
    env = {"KEY": "simple"}
    rendered = render_sorted_env(env, ["KEY"])
    assert "KEY=simple" in rendered


# ---------------------------------------------------------------------------
# sort_env_file
# ---------------------------------------------------------------------------

def test_sort_env_file_round_trip(tmp_env):
    path = tmp_env("""\
        ZEBRA=z
        ALPHA=a
    """)
    result, rendered = sort_env_file(path)
    assert not result.already_sorted
    assert rendered.index("ALPHA") < rendered.index("ZEBRA")


# ---------------------------------------------------------------------------
# sort_reporter
# ---------------------------------------------------------------------------

def test_format_sort_result_already_sorted():
    env = {"A": "1", "B": "2"}
    result = sort_env(env)
    report = format_sort_result(result, color=False)
    assert "already sorted" in report


def test_format_sort_result_shows_moved_keys():
    env = {"Z": "z", "A": "a"}
    result = sort_env(env)
    report = format_sort_result(result, color=False)
    assert "Z" in report or "A" in report
    assert "→" in report
