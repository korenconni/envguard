"""Tests for env_differ_extended and extended_diff_reporter."""
from __future__ import annotations

import pytest

from envguard.env_differ_extended import (
    ExtendedDiffResult,
    ValueChange,
    _infer_type,
    extended_diff,
)
from envguard.extended_diff_reporter import format_extended_diff


# ---------------------------------------------------------------------------
# _infer_type
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    ("true", "bool"),
    ("False", "bool"),
    ("42", "int"),
    ("-7", "int"),
    ("3.14", "float"),
    ("-0.5", "float"),
    ("hello", "str"),
    ("", "empty"),
])
def test_infer_type(value, expected):
    assert _infer_type(value) == expected


# ---------------------------------------------------------------------------
# extended_diff
# ---------------------------------------------------------------------------

def test_identical_envs_have_no_differences():
    env = {"A": "1", "B": "hello"}
    result = extended_diff(env, env)
    assert not result.has_differences
    assert result.unchanged == env


def test_added_key_detected():
    result = extended_diff({"A": "1"}, {"A": "1", "B": "2"})
    assert "B" in result.added
    assert result.added["B"] == "2"


def test_removed_key_detected():
    result = extended_diff({"A": "1", "B": "2"}, {"A": "1"})
    assert "B" in result.removed


def test_changed_value_detected():
    result = extended_diff({"PORT": "8080"}, {"PORT": "9090"})
    assert len(result.changed) == 1
    assert result.changed[0].key == "PORT"
    assert result.changed[0].old_value == "8080"
    assert result.changed[0].new_value == "9090"


def test_type_change_detected():
    change = ValueChange("FLAG", "true", "yes")
    assert change.is_type_change  # bool -> str


def test_no_type_change_same_type():
    change = ValueChange("PORT", "8080", "9090")
    assert not change.is_type_change  # int -> int


def test_type_changes_property_filters_correctly():
    result = extended_diff(
        {"PORT": "8080", "FLAG": "true"},
        {"PORT": "9090", "FLAG": "yes"},
    )
    assert len(result.type_changes) == 1
    assert result.type_changes[0].key == "FLAG"


# ---------------------------------------------------------------------------
# format_extended_diff
# ---------------------------------------------------------------------------

def test_format_no_differences_message():
    result = extended_diff({"A": "1"}, {"A": "1"})
    output = format_extended_diff(result, color=False)
    assert "No differences" in output


def test_format_shows_added_key():
    result = extended_diff({}, {"NEW_KEY": "value"})
    output = format_extended_diff(result, color=False)
    assert "NEW_KEY" in output
    assert "+" in output


def test_format_shows_removed_key():
    result = extended_diff({"OLD_KEY": "v"}, {})
    output = format_extended_diff(result, color=False)
    assert "OLD_KEY" in output
    assert "-" in output


def test_format_shows_type_annotation():
    result = extended_diff({"FLAG": "true"}, {"FLAG": "yes"})
    output = format_extended_diff(result, color=False)
    assert "type:" in output
    assert "bool" in output
    assert "str" in output


def test_format_summary_line_present():
    result = extended_diff({"A": "1"}, {"A": "2", "B": "3"})
    output = format_extended_diff(result, color=False)
    assert "Summary:" in output
