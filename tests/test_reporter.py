"""Tests for envguard.reporter."""
import pytest

from envguard.differ import DiffResult
from envguard.validator import ValidationResult
from envguard.reporter import format_diff, format_validation


def _diff(**kwargs) -> DiffResult:
    defaults = dict(missing_in_first=set(), missing_in_second=set(), value_differences={})
    defaults.update(kwargs)
    return DiffResult(**defaults)


def _vresult(**kwargs) -> ValidationResult:
    defaults = dict(missing_keys=set(), empty_keys=set(), unknown_keys=set())
    defaults.update(kwargs)
    return ValidationResult(**defaults)


def test_format_diff_no_differences():
    result = format_diff(_diff(), use_color=False)
    assert result == "No differences found."


def test_format_diff_missing_in_second():
    result = format_diff(_diff(missing_in_second={"DB_HOST"}), use_color=False)
    assert "- DB_HOST" in result


def test_format_diff_missing_in_first():
    result = format_diff(_diff(missing_in_first={"NEW_KEY"}), use_color=False)
    assert "+ NEW_KEY" in result


def test_format_diff_value_differences():
    result = format_diff(_diff(value_differences={"PORT": ("5432", "5433")}), use_color=False)
    assert "~ PORT" in result
    assert "5432" in result
    assert "5433" in result


def test_format_diff_uses_color():
    result = format_diff(_diff(missing_in_second={"X"}), use_color=True)
    assert "\033[" in result


def test_format_validation_passed():
    result = format_validation(_vresult(), use_color=False)
    assert result == "Validation passed."


def test_format_validation_missing():
    result = format_validation(_vresult(missing_keys={"SECRET"}), use_color=False)
    assert "MISSING" in result
    assert "SECRET" in result


def test_format_validation_empty():
    result = format_validation(_vresult(empty_keys={"API_KEY"}), use_color=False)
    assert "EMPTY" in result
    assert "API_KEY" in result


def test_format_validation_unknown():
    result = format_validation(_vresult(unknown_keys={"STRAY"}), use_color=False)
    assert "UNKNOWN" in result
    assert "STRAY" in result


def test_format_validation_failed_header():
    result = format_validation(_vresult(missing_keys={"X"}), use_color=False)
    assert "Validation failed" in result
