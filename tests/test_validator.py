"""Tests for envguard.validator and envguard.schema_loader."""

import pytest
from pathlib import Path

from envguard.validator import EnvSchema, ValidationResult, validate_env
from envguard.schema_loader import load_schema, _parse_text_schema


# ---------------------------------------------------------------------------
# validate_env
# ---------------------------------------------------------------------------

def _schema(**kwargs) -> EnvSchema:
    return EnvSchema(**kwargs)


def test_all_required_present():
    schema = _schema(required={"DB_URL", "SECRET_KEY"})
    result = validate_env({"DB_URL": "postgres://", "SECRET_KEY": "abc"}, schema)
    assert result.is_valid
    assert result.summary() == "All checks passed."


def test_missing_required():
    schema = _schema(required={"DB_URL", "SECRET_KEY"})
    result = validate_env({"DB_URL": "postgres://"}, schema)
    assert not result.is_valid
    assert "SECRET_KEY" in result.missing_required


def test_empty_required_value():
    schema = _schema(required={"API_KEY"})
    result = validate_env({"API_KEY": ""}, schema)
    assert not result.is_valid
    assert "API_KEY" in result.empty_required


def test_missing_optional_does_not_fail():
    schema = _schema(required={"DB_URL"}, optional={"LOG_LEVEL"})
    result = validate_env({"DB_URL": "postgres://"}, schema)
    assert result.is_valid
    assert "LOG_LEVEL" in result.missing_optional


def test_unknown_keys_flagged_when_disallowed():
    schema = _schema(required={"DB_URL"}, allow_unknown=False)
    result = validate_env({"DB_URL": "x", "EXTRA": "y"}, schema)
    assert result.is_valid  # unknown != invalid
    assert "EXTRA" in result.unknown_keys


def test_unknown_keys_ignored_when_allowed():
    schema = _schema(required={"DB_URL"}, allow_unknown=True)
    result = validate_env({"DB_URL": "x", "EXTRA": "y"}, schema)
    assert result.unknown_keys == []


def test_whitespace_only_required_value_treated_as_empty():
    """A value containing only whitespace should be treated as empty."""
    schema = _schema(required={"API_KEY"})
    result = validate_env({"API_KEY": "   "}, schema)
    assert not result.is_valid
    assert "API_KEY" in result.empty_required


# ---------------------------------------------------------------------------
# schema_loader
# ---------------------------------------------------------------------------

def test_parse_text_schema_basic():
    text = """
# comment
required: DB_URL, SECRET_KEY
optional: LOG_LEVEL
allow_unknown: false
"""
    schema = _parse_text_schema(text)
    assert schema.required == {"DB_URL", "SECRET_KEY"}
    assert schema.optional == {"LOG_LEVEL"}
    assert schema.allow_unknown is False


def test_load_schema_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_schema("/nonexistent/schema.txt")


def test_load_schema_from_txt(tmp_path: Path):
    schema_file = tmp_path / "schema.txt"
    schema_file.write_text("required: APP_ENV\noptional: DEBUG\n")
    schema = load_schema(str(schema_file))
    assert "APP_ENV" in schema.required
    assert "DEBUG" in schema.optional
