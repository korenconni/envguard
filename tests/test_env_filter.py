"""Tests for envguard.env_filter."""
import pytest
from envguard.env_filter import FilterResult, filter_env


ENV: dict = {
    "APP_NAME": "myapp",
    "APP_DEBUG": "true",
    "DB_HOST": "localhost",
    "DB_PASSWORD": "",
    "secret_key": "abc123",
}


def test_no_filters_returns_all_keys():
    result = filter_env(ENV, source="test.env")
    assert result.matched == ENV
    assert result.excluded == {}
    assert result.match_count == len(ENV)


def test_prefix_filter_keeps_matching_keys():
    result = filter_env(ENV, prefix="APP_")
    assert set(result.matched.keys()) == {"APP_NAME", "APP_DEBUG"}
    assert "DB_HOST" in result.excluded


def test_prefix_filter_no_match_returns_empty():
    result = filter_env(ENV, prefix="NONEXISTENT_")
    assert result.matched == {}
    assert result.match_count == 0
    assert not result


def test_pattern_filter_regex_match():
    result = filter_env(ENV, pattern=r"^DB_")
    assert set(result.matched.keys()) == {"DB_HOST", "DB_PASSWORD"}


def test_pattern_filter_case_sensitive():
    result = filter_env(ENV, pattern=r"secret")
    assert "secret_key" in result.matched
    assert "APP_NAME" in result.excluded


def test_exclude_empty_removes_blank_values():
    result = filter_env(ENV, exclude_empty=True)
    assert "DB_PASSWORD" not in result.matched
    assert "DB_PASSWORD" in result.excluded


def test_exclude_empty_keeps_non_blank():
    result = filter_env(ENV, exclude_empty=True)
    assert "APP_NAME" in result.matched


def test_keys_allowlist_limits_candidates():
    result = filter_env(ENV, keys=["APP_NAME", "DB_HOST"])
    assert set(result.matched.keys()) == {"APP_NAME", "DB_HOST"}
    assert "APP_DEBUG" not in result.matched
    assert "APP_DEBUG" not in result.excluded


def test_keys_allowlist_with_prefix_filter():
    result = filter_env(ENV, keys=["APP_NAME", "DB_HOST"], prefix="APP_")
    assert result.matched == {"APP_NAME": "myapp"}
    assert result.excluded == {"DB_HOST": "localhost"}


def test_keys_missing_from_env_are_ignored():
    result = filter_env(ENV, keys=["APP_NAME", "DOES_NOT_EXIST"])
    assert set(result.matched.keys()) == {"APP_NAME"}


def test_combined_prefix_and_exclude_empty():
    result = filter_env(ENV, prefix="DB_", exclude_empty=True)
    assert result.matched == {"DB_HOST": "localhost"}
    assert "DB_PASSWORD" in result.excluded


def test_source_label_stored():
    result = filter_env(ENV, source="production.env")
    assert result.source == "production.env"


def test_bool_true_when_matches_exist():
    result = filter_env(ENV, prefix="APP_")
    assert bool(result) is True


def test_excluded_count_correct():
    result = filter_env(ENV, prefix="APP_")
    assert result.excluded_count == len(ENV) - 2
