"""Tests for env_profiler and profile_reporter."""
from __future__ import annotations

import pytest

from envguard.env_profiler import profile_env, _infer_type, ProfileResult
from envguard.profile_reporter import format_profile_result


# ---------------------------------------------------------------------------
# _infer_type
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    ("", "empty"),
    ("true", "bool"),
    ("False", "bool"),
    ("yes", "bool"),
    ("0", "bool"),
    ("42", "int"),
    ("-7", "int"),
    ("3.14", "float"),
    ("http://example.com", "url"),
    ("https://x.io/path", "url"),
    ("/var/log", "path"),
    ("~/projects", "path"),
    ("./relative", "path"),
    ("hello world", "string"),
    ("some-value_123", "string"),
])
def test_infer_type(value, expected):
    assert _infer_type(value) == expected


# ---------------------------------------------------------------------------
# profile_env
# ---------------------------------------------------------------------------

def test_empty_env_returns_zero_counts():
    result = profile_env({}, source="test")
    assert result.total_keys == 0
    assert result.empty_values == 0
    assert result.type_counts == {}


def test_total_keys_counted():
    env = {"A": "1", "B": "hello", "C": ""}
    result = profile_env(env)
    assert result.total_keys == 3


def test_empty_values_counted():
    env = {"A": "", "B": "", "C": "present"}
    result = profile_env(env)
    assert result.empty_values == 2


def test_type_counts_correct():
    env = {"PORT": "8080", "DEBUG": "true", "HOST": "localhost", "EMPTY": ""}
    result = profile_env(env)
    assert result.type_counts["int"] == 1
    assert result.type_counts["bool"] == 1
    assert result.type_counts["string"] == 1
    assert result.type_counts["empty"] == 1


def test_uppercase_keys_counted():
    env = {"UPPER_KEY": "v", "lower_key": "v", "MixedKey": "v"}
    result = profile_env(env)
    assert result.uppercase_keys == 1
    assert result.mixed_case_keys == 1


def test_longest_key_detected():
    env = {"SHORT": "a", "A_VERY_LONG_KEY_NAME": "b"}
    result = profile_env(env)
    assert result.longest_key == "A_VERY_LONG_KEY_NAME"


def test_source_stored():
    result = profile_env({}, source=".env.production")
    assert result.source == ".env.production"


# ---------------------------------------------------------------------------
# format_profile_result
# ---------------------------------------------------------------------------

def test_format_includes_source():
    result = profile_env({"X": "1"}, source=".env.test")
    report = format_profile_result(result)
    assert ".env.test" in report


def test_format_shows_total_keys():
    result = profile_env({"A": "1", "B": "2"})
    report = format_profile_result(result)
    assert "2" in report


def test_format_shows_type_breakdown():
    result = profile_env({"PORT": "9000", "URL": "http://x.com"})
    report = format_profile_result(result)
    assert "int" in report
    assert "url" in report


def test_format_no_crash_on_empty_env():
    result = profile_env({})
    report = format_profile_result(result)
    assert "Total keys" in report
