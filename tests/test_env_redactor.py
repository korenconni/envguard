"""Tests for envguard.env_redactor."""
import pytest

from envguard.env_redactor import (
    DEFAULT_MASK,
    RedactResult,
    _is_sensitive,
    redact_env,
    render_redacted_env,
)


# ---------------------------------------------------------------------------
# _is_sensitive
# ---------------------------------------------------------------------------

def test_sensitive_key_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_sensitive_key_token():
    assert _is_sensitive("GITHUB_TOKEN") is True


def test_sensitive_key_api_key():
    assert _is_sensitive("STRIPE_API_KEY") is True


def test_non_sensitive_key():
    assert _is_sensitive("APP_ENV") is False


def test_non_sensitive_key_port():
    assert _is_sensitive("PORT") is False


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

def test_sensitive_values_are_masked():
    env = {"DB_PASSWORD": "s3cr3t", "APP_ENV": "production"}
    result = redact_env(env)
    assert result.redacted["DB_PASSWORD"] == DEFAULT_MASK
    assert result.redacted["APP_ENV"] == "production"


def test_redacted_keys_list_populated():
    env = {"SECRET_KEY": "abc", "HOST": "localhost"}
    result = redact_env(env)
    assert "SECRET_KEY" in result.redacted_keys
    assert "HOST" not in result.redacted_keys


def test_custom_mask_applied():
    env = {"API_KEY": "xyz"}
    result = redact_env(env, mask="[HIDDEN]")
    assert result.redacted["API_KEY"] == "[HIDDEN]"
    assert result.mask == "[HIDDEN]"


def test_extra_keys_always_redacted():
    env = {"MY_CUSTOM": "value", "NORMAL": "ok"}
    result = redact_env(env, extra_keys=["MY_CUSTOM"])
    assert result.redacted["MY_CUSTOM"] == DEFAULT_MASK
    assert result.redacted["NORMAL"] == "ok"


def test_all_values_flag_redacts_everything():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = redact_env(env, all_values=True)
    assert all(v == DEFAULT_MASK for v in result.redacted.values())
    assert result.redacted_count == 2


def test_empty_env_returns_empty_result():
    result = redact_env({})
    assert result.total_keys == 0
    assert result.redacted_count == 0
    assert not result


def test_bool_true_when_redactions_exist():
    env = {"AUTH_TOKEN": "secret"}
    result = redact_env(env)
    assert bool(result) is True


def test_bool_false_when_no_redactions():
    env = {"PORT": "8080"}
    result = redact_env(env)
    assert bool(result) is False


def test_original_env_unchanged():
    env = {"DB_PASSWORD": "real_pass"}
    result = redact_env(env)
    assert result.original["DB_PASSWORD"] == "real_pass"


def test_redact_env_raises_on_non_dict():
    """redact_env should raise TypeError when given a non-dict argument."""
    with pytest.raises(TypeError):
        redact_env(["DB_PASSWORD=secret"])


def test_redact_env_raises_on_none():
    """redact_env should raise TypeError when given None."""
    with pytest.raises(TypeError):
        redact_env(None)


# ---------------------------------------------------------------------------
# render_redacted_env
# ---------------------------------------------------------------------------

def test_render_produces_env_format():
    env = {"APP_ENV": "staging", "SECRET": "hidden"}
    result = redact_env(env)
