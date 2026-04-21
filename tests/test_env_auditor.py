"""Tests for env_auditor and audit_reporter."""
import pytest
from envguard.env_auditor import audit_env, AuditResult
from envguard.audit_reporter import format_audit_result


def test_clean_env_has_no_issues():
    env = {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "false"}
    result = audit_env(env)
    assert not result.has_issues


def test_placeholder_sensitive_key_triggers_a001():
    env = {"DB_PASSWORD": "changeme"}
    result = audit_env(env)
    codes = [i.code for i in result.issues]
    assert "A001" in codes


def test_empty_sensitive_key_triggers_a002():
    env = {"API_SECRET": ""}
    result = audit_env(env)
    codes = [i.code for i in result.issues]
    assert "A002" in codes


def test_empty_sensitive_key_is_error_severity():
    env = {"API_TOKEN": ""}
    result = audit_env(env)
    errors = result.errors
    assert any(i.code == "A002" for i in errors)


def test_placeholder_is_warning_not_error():
    env = {"DB_PASSWORD": "replace_me"}
    result = audit_env(env)
    a001 = [i for i in result.issues if i.code == "A001"]
    assert a001
    assert a001[0].severity == "warning"


def test_high_entropy_non_sensitive_key_triggers_a003():
    env = {"SOME_CONFIG": "aB3dEfGhIjKlMnOpQrSt"}  # 20 chars, mixed
    result = audit_env(env)
    codes = [i.code for i in result.issues]
    assert "A003" in codes


def test_high_entropy_short_value_not_flagged():
    env = {"SOME_CONFIG": "aB3dEf"}  # too short
    result = audit_env(env)
    codes = [i.code for i in result.issues]
    assert "A003" not in codes


def test_multiple_issues_collected():
    env = {
        "DB_PASSWORD": "changeme",
        "API_KEY": "",
        "RANDOM_FIELD": "zZ9aAbBcCdDeEfFgGhHiIjJ",
    }
    result = audit_env(env)
    assert len(result.issues) >= 3


def test_format_audit_result_clean(capsys):
    result = AuditResult()
    output = format_audit_result(result, use_color=False)
    assert "No audit issues found" in output


def test_format_audit_result_with_issues():
    env = {"DB_PASSWORD": "", "API_TOKEN": "changeme"}
    result = audit_env(env)
    output = format_audit_result(result, use_color=False)
    assert "A002" in output or "A001" in output
    assert "Summary" in output


def test_format_audit_result_summary_counts():
    env = {"SECRET_KEY": "", "API_PASSWORD": "todo"}
    result = audit_env(env)
    output = format_audit_result(result, use_color=False)
    assert "error" in output.lower()
    assert "warning" in output.lower()
