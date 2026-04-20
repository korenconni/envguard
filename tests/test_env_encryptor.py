"""Tests for envguard.env_encryptor."""

import pytest

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

pytestmark = pytest.mark.skipif(not HAS_CRYPTO, reason="cryptography not installed")

from envguard.env_encryptor import (
    ENCRYPTED_PREFIX,
    DecryptionResult,
    EncryptionResult,
    decrypt_env,
    encrypt_env,
    generate_key,
    _is_sensitive,
)


@pytest.fixture()
def key() -> str:
    return generate_key()


# ---------------------------------------------------------------------------
# generate_key
# ---------------------------------------------------------------------------

def test_generate_key_returns_string(key):
    assert isinstance(key, str)
    assert len(key) > 0


def test_generate_key_unique():
    assert generate_key() != generate_key()


# ---------------------------------------------------------------------------
# _is_sensitive
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("k", ["DB_PASSWORD", "api_key", "AUTH_TOKEN", "secret"])
def test_sensitive_keys_detected(k):
    assert _is_sensitive(k)


@pytest.mark.parametrize("k", ["HOST", "PORT", "DEBUG", "APP_NAME"])
def test_non_sensitive_keys_not_detected(k):
    assert not _is_sensitive(k)


# ---------------------------------------------------------------------------
# encrypt_env
# ---------------------------------------------------------------------------

def test_encrypt_sensitive_values(key):
    env = {"DB_PASSWORD": "hunter2", "HOST": "localhost"}
    result = encrypt_env(env, key)
    assert "DB_PASSWORD" in result.encrypted
    assert result.encrypted["DB_PASSWORD"].startswith(ENCRYPTED_PREFIX)
    assert "HOST" in result.skipped


def test_encrypt_explicit_keys(key):
    env = {"HOST": "localhost", "PORT": "5432"}
    result = encrypt_env(env, key, keys_to_encrypt=["HOST"])
    assert result.encrypted["HOST"].startswith(ENCRYPTED_PREFIX)
    assert "PORT" in result.skipped


def test_already_encrypted_not_double_encrypted(key):
    token = Fernet(key.encode()).encrypt(b"secret").decode()
    env = {"DB_PASSWORD": f"{ENCRYPTED_PREFIX}{token}"}
    result = encrypt_env(env, key)
    assert "DB_PASSWORD" in result.already_encrypted
    assert result.encrypted["DB_PASSWORD"] == f"{ENCRYPTED_PREFIX}{token}"


# ---------------------------------------------------------------------------
# decrypt_env
# ---------------------------------------------------------------------------

def test_round_trip(key):
    env = {"DB_PASSWORD": "s3cr3t", "HOST": "localhost"}
    enc = encrypt_env(env, key)
    merged = {**enc.encrypted, **{k: env[k] for k in enc.skipped}}
    dec = decrypt_env(merged, key)
    assert dec.decrypted["DB_PASSWORD"] == "s3cr3t"
    assert dec.decrypted["HOST"] == "localhost"
    assert not dec.failed


def test_decrypt_invalid_token_recorded(key):
    env = {"DB_PASSWORD": f"{ENCRYPTED_PREFIX}notavalidtoken"}
    result = decrypt_env(env, key)
    assert len(result.failed) == 1
    assert result.failed[0][0] == "DB_PASSWORD"


def test_plaintext_values_passed_through(key):
    env = {"HOST": "localhost"}
    result = decrypt_env(env, key)
    assert result.decrypted["HOST"] == "localhost"
    assert "HOST" in result.plaintext
