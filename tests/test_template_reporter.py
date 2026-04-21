"""Tests for envguard.template_reporter."""
from __future__ import annotations

import pytest

from envguard.env_templater import TemplateResult
from envguard.template_reporter import format_template_result, format_template_preview


@pytest.fixture()
def _result() -> TemplateResult:
    r = TemplateResult(
        source_path=".env",
        keys=["DB_HOST", "API_SECRET", "DEBUG"],
        sensitive_keys=["API_SECRET"],
        output_path=".env.template",
    )
    r._lines = {"DB_HOST": "localhost", "API_SECRET": "", "DEBUG": "true"}
    return r


def test_format_result_shows_source(_result):
    out = format_template_result(_result, color=False)
    assert ".env" in out


def test_format_result_shows_counts(_result):
    out = format_template_result(_result, color=False)
    assert "3" in out  # total keys
    assert "1" in out  # masked keys


def test_format_result_lists_masked_keys(_result):
    out = format_template_result(_result, color=False)
    assert "API_SECRET" in out


def test_format_result_shows_output_path(_result):
    out = format_template_result(_result, color=False)
    assert ".env.template" in out


def test_format_preview_contains_header(_result):
    preview = format_template_preview(_result)
    assert "envguard" in preview


def test_format_preview_contains_keys(_result):
    preview = format_template_preview(_result)
    assert "DB_HOST=localhost" in preview
    assert "API_SECRET=" in preview
