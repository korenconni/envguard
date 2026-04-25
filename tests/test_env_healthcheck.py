"""Tests for envguard.env_healthcheck."""
import pytest
from envguard.env_healthcheck import healthcheck_env, HealthResult


def _perfect_env():
    return {
        "APP_NAME": "myapp",
        "APP_PORT": "8080",
        "APP_HOST": "localhost",
    }


def test_perfect_env_achieves_high_score():
    result = healthcheck_env(_perfect_env())
    assert isinstance(result, HealthResult)
    assert result.percentage >= 90.0


def test_perfect_env_grade_is_a():
    result = healthcheck_env(_perfect_env())
    assert result.grade == "A"


def test_total_score_does_not_exceed_max():
    result = healthcheck_env(_perfect_env())
    assert result.total_score <= result.max_score


def test_max_score_is_100():
    result = healthcheck_env(_perfect_env())
    assert result.max_score == 100


def test_four_dimensions_returned():
    result = healthcheck_env(_perfect_env())
    assert len(result.dimensions) == 4


def test_dimension_names():
    result = healthcheck_env(_perfect_env())
    names = {d.name for d in result.dimensions}
    assert names == {"lint", "security", "duplicates", "cleanliness"}


def test_lowercase_key_reduces_lint_score():
    env = {"lowercase_key": "value", "APP_OK": "1"}
    result = healthcheck_env(env)
    lint_dim = next(d for d in result.dimensions if d.name == "lint")
    assert lint_dim.score < lint_dim.max_score


def test_placeholder_secret_reduces_security_score():
    env = {"APP_SECRET": "changeme", "APP_PORT": "9000"}
    result = healthcheck_env(env)
    sec_dim = next(d for d in result.dimensions if d.name == "security")
    assert sec_dim.score < sec_dim.max_score


def test_empty_env_returns_result():
    result = healthcheck_env({})
    assert isinstance(result, HealthResult)
    assert result.max_score == 100


def test_untrimmed_value_reduces_cleanliness_score():
    env = {"APP_NAME": "  myapp  ", "APP_PORT": "8080"}
    result = healthcheck_env(env)
    clean_dim = next(d for d in result.dimensions if d.name == "cleanliness")
    assert clean_dim.score < clean_dim.max_score


def test_grade_f_on_terrible_env():
    env = {
        "bad_key": "  value  ",
        "another_bad": "  stuff  ",
        "DB_PASSWORD": "",
        "API_KEY": "placeholder",
        "SECRET_TOKEN": "changeme",
    }
    result = healthcheck_env(env)
    assert result.grade in {"D", "F"}


def test_issues_list_populated_for_bad_env():
    env = {"bad_key": "value"}
    result = healthcheck_env(env)
    lint_dim = next(d for d in result.dimensions if d.name == "lint")
    assert len(lint_dim.issues) > 0


def test_percentage_between_0_and_100():
    for env in [{}, _perfect_env(), {"x": "  ", "DB_PASS": ""}]:
        result = healthcheck_env(env)
        assert 0.0 <= result.percentage <= 100.0
