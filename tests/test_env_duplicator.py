"""Tests for envguard.env_duplicator and envguard.duplicate_reporter."""
from __future__ import annotations

import pytest

from envguard.env_duplicator import find_duplicate_values, DuplicateGroup, DuplicateResult
from envguard.duplicate_reporter import format_duplicate_result


# ---------------------------------------------------------------------------
# find_duplicate_values
# ---------------------------------------------------------------------------

def test_no_duplicates_returns_empty_groups():
    env = {"A": "1", "B": "2", "C": "3"}
    result = find_duplicate_values(env, source="test.env")
    assert not result.has_duplicates()
    assert result.groups == []


def test_single_duplicate_group_detected():
    env = {"A": "same", "B": "same", "C": "different"}
    result = find_duplicate_values(env, source="test.env")
    assert result.has_duplicates()
    assert result.group_count == 1
    assert set(result.groups[0].keys) == {"A", "B"}
    assert result.groups[0].value == "same"


def test_multiple_duplicate_groups():
    env = {"A": "x", "B": "x", "C": "y", "D": "y", "E": "unique"}
    result = find_duplicate_values(env, source="test.env")
    assert result.group_count == 2
    assert result.total_duplicate_keys == 4


def test_empty_values_ignored_by_default():
    env = {"A": "", "B": "", "C": "real"}
    result = find_duplicate_values(env)
    assert not result.has_duplicates()


def test_empty_values_included_when_flag_off():
    env = {"A": "", "B": "", "C": "real"}
    result = find_duplicate_values(env, ignore_empty=False)
    assert result.has_duplicates()
    assert result.groups[0].value == ""


def test_source_label_stored():
    result = find_duplicate_values({}, source="prod.env")
    assert result.source == "prod.env"


def test_keys_within_group_are_sorted():
    env = {"Z": "v", "A": "v", "M": "v"}
    result = find_duplicate_values(env)
    assert result.groups[0].keys == ["A", "M", "Z"]


def test_total_duplicate_keys_counts_all_involved():
    env = {"A": "x", "B": "x", "C": "x"}
    result = find_duplicate_values(env)
    assert result.total_duplicate_keys == 3


# ---------------------------------------------------------------------------
# format_duplicate_result
# ---------------------------------------------------------------------------

def test_format_no_duplicates_contains_checkmark():
    result = find_duplicate_values({"A": "1", "B": "2"})
    output = format_duplicate_result(result, color=False)
    assert "✔" in output
    assert "No duplicate" in output


def test_format_shows_group_count():
    env = {"A": "same", "B": "same"}
    result = find_duplicate_values(env)
    output = format_duplicate_result(result, color=False)
    assert "1 group" in output


def test_format_lists_duplicate_keys():
    env = {"KEY_ONE": "shared", "KEY_TWO": "shared"}
    result = find_duplicate_values(env)
    output = format_duplicate_result(result, color=False)
    assert "KEY_ONE" in output
    assert "KEY_TWO" in output


def test_format_truncates_long_values():
    long_val = "x" * 60
    env = {"A": long_val, "B": long_val}
    result = find_duplicate_values(env)
    output = format_duplicate_result(result, color=False)
    assert "..." in output
