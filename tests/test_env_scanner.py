"""Tests for envguard.env_scanner."""
import pytest
from envguard.env_scanner import ScanIssue, ScanResult, scan_env, _looks_like_secret


# ---------------------------------------------------------------------------
# _looks_like_secret helpers
# ---------------------------------------------------------------------------

def test_hex_string_detected():
    assert _looks_like_secret("a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4") is not None


def test_base64_string_detected():
    assert _looks_like_secret("dGhpcyBpcyBhIHZlcnkgbG9uZyBiYXNlNjQgc3RyaW5n") is not None


def test_aws_key_detected():
    assert _looks_like_secret("AKIAIOSFODNN7EXAMPLE") is not None


def test_github_pat_detected():
    assert _looks_like_secret("ghp_" + "A" * 36) is not None


def test_plain_value_not_detected():
    assert _looks_like_secret("localhost") is None


def test_short_number_not_detected():
    assert _looks_like_secret("5432") is None


# ---------------------------------------------------------------------------
# scan_env — clean environments
# ---------------------------------------------------------------------------

def test_empty_env_has_no_issues():
    result = scan_env({})
    assert not result.has_issues


def test_clean_env_has_no_issues():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    result = scan_env(env)
    assert not result.has_issues


def test_empty_value_skipped():
    env = {"API_KEY": ""}
    result = scan_env(env)
    assert not result.has_issues


# ---------------------------------------------------------------------------
# scan_env — issues detected
# ---------------------------------------------------------------------------

def test_sensitive_key_with_hex_value_is_error():
    env = {"DB_PASSWORD": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"}
    result = scan_env(env)
    assert len(result.errors) == 1
    assert result.errors[0].key == "DB_PASSWORD"
    assert result.errors[0].severity == "error"


def test_non_sensitive_key_with_secret_value_is_warning():
    env = {"SOME_CONFIG": "AKIAIOSFODNN7EXAMPLE"}
    result = scan_env(env)
    assert len(result.warnings) == 1
    assert result.warnings[0].severity == "warning"


def test_multiple_issues_detected():
    env = {
        "SECRET_TOKEN": "ghp_" + "B" * 36,
        "MISC": "AKIAIOSFODNN7EXAMPLE",
        "HOST": "localhost",
    }
    result = scan_env(env)
    assert result.has_issues
    assert len(result.issues) == 2


def test_source_stored_on_result():
    result = scan_env({}, source=".env.production")
    assert result.source == ".env.production"


def test_errors_and_warnings_partitioned():
    env = {
        "API_SECRET": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",  # error
        "BUILD_HASH": "deadbeefcafedeadbeefcafedeadbeef",     # warning (non-sensitive key)
    }
    result = scan_env(env)
    assert len(result.errors) == 1
    assert len(result.warnings) == 1
