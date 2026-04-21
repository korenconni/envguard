"""Tests for env_exporter and export_reporter."""
from __future__ import annotations

import json

import pytest

from envguard.env_exporter import ExportResult, export_env
from envguard.export_reporter import format_export_result


SAMPLE: dict[str, str] = {
    "APP_NAME": "envguard",
    "DEBUG": "true",
    "DB_PASSWORD": "s3cr3t",
    "EMPTY_KEY": "",
}


# ---------------------------------------------------------------------------
# export_env – JSON
# ---------------------------------------------------------------------------

def test_json_output_is_valid_json():
    result = export_env(SAMPLE, "json")
    parsed = json.loads(result.content)
    assert parsed["APP_NAME"] == "envguard"


def test_json_key_count():
    result = export_env(SAMPLE, "json")
    assert result.key_count == len(SAMPLE)


def test_json_keys_sorted():
    result = export_env(SAMPLE, "json")
    parsed = json.loads(result.content)
    assert list(parsed.keys()) == sorted(parsed.keys())


# ---------------------------------------------------------------------------
# export_env – YAML
# ---------------------------------------------------------------------------

def test_yaml_contains_all_keys():
    result = export_env(SAMPLE, "yaml")
    for key in SAMPLE:
        assert key in result.content


def test_yaml_empty_value_quoted():
    result = export_env({"EMPTY": ""}, "yaml")
    assert 'EMPTY: ""' in result.content


# ---------------------------------------------------------------------------
# export_env – shell
# ---------------------------------------------------------------------------

def test_shell_has_shebang():
    result = export_env(SAMPLE, "shell")
    assert result.content.startswith("#!/usr/bin/env sh")


def test_shell_export_keyword():
    result = export_env(SAMPLE, "shell")
    assert "export APP_NAME='envguard'" in result.content


def test_shell_single_quotes_escaped():
    tricky = {"KEY": "it's alive"}
    result = export_env(tricky, "shell")
    # single quote inside value must be safely escaped
    assert "KEY=" in result.content
    assert "it" in result.content


# ---------------------------------------------------------------------------
# exclude_empty
# ---------------------------------------------------------------------------

def test_exclude_empty_removes_blank_values():
    result = export_env(SAMPLE, "json", exclude_empty=True)
    parsed = json.loads(result.content)
    assert "EMPTY_KEY" not in parsed


def test_exclude_empty_adds_warning():
    result = export_env(SAMPLE, "json", exclude_empty=True)
    assert result.warnings
    assert "EMPTY_KEY" in result.warnings[0]


def test_exclude_empty_bool_false_when_warnings():
    result = export_env(SAMPLE, "json", exclude_empty=True)
    assert not bool(result)


def test_no_warnings_bool_true():
    env = {"KEY": "value"}
    result = export_env(env, "json")
    assert bool(result)


# ---------------------------------------------------------------------------
# unsupported format
# ---------------------------------------------------------------------------

def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_env(SAMPLE, "toml")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# format_export_result
# ---------------------------------------------------------------------------

def test_reporter_shows_format_and_source():
    result = export_env(SAMPLE, "json", source=".env.prod")
    report = format_export_result(result)
    assert ".env.prod" in report
    assert "JSON" in report


def test_reporter_show_content_includes_payload():
    result = export_env({"X": "1"}, "json")
    report = format_export_result(result, show_content=True)
    assert '"X"' in report


def test_reporter_no_warnings_message():
    result = export_env({"X": "1"}, "yaml")
    report = format_export_result(result)
    assert "No warnings" in report
