"""Encrypt and decrypt sensitive values in .env files using Fernet symmetric encryption."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore

ENCRYPTED_PREFIX = "enc:"
_SENSITIVE_PATTERN = re.compile(
    r"(password|secret|token|key|credential|api_key|auth)",
    re.IGNORECASE,
)


@dataclass
class EncryptionResult:
    encrypted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    already_encrypted: List[str] = field(default_factory=list)


@dataclass
class DecryptionResult:
    decrypted: Dict[str, str] = field(default_factory=dict)
    failed: List[Tuple[str, str]] = field(default_factory=list)  # (key, reason)
    plaintext: List[str] = field(default_factory=list)


def generate_key() -> str:
    """Generate a new Fernet key and return it as a string."""
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")
    return Fernet.generate_key().decode()


def _is_sensitive(key: str) -> bool:
    return bool(_SENSITIVE_PATTERN.search(key))


def encrypt_env(
    env: Dict[str, str],
    fernet_key: str,
    keys_to_encrypt: List[str] | None = None,
) -> EncryptionResult:
    """Encrypt sensitive values (or a specific list of keys) in an env dict."""
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")

    f = Fernet(fernet_key.encode())
    result = EncryptionResult()

    for k, v in env.items():
        should_encrypt = (keys_to_encrypt is not None and k in keys_to_encrypt) or (
            keys_to_encrypt is None and _is_sensitive(k)
        )
        if not should_encrypt:
            result.skipped.append(k)
            continue
        if v.startswith(ENCRYPTED_PREFIX):
            result.already_encrypted.append(k)
            result.encrypted[k] = v
            continue
        token = f.encrypt(v.encode()).decode()
        result.encrypted[k] = f"{ENCRYPTED_PREFIX}{token}"

    return result


def decrypt_env(env: Dict[str, str], fernet_key: str) -> DecryptionResult:
    """Decrypt all values that carry the encrypted prefix."""
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")

    f = Fernet(fernet_key.encode())
    result = DecryptionResult()

    for k, v in env.items():
        if not v.startswith(ENCRYPTED_PREFIX):
            result.plaintext.append(k)
            result.decrypted[k] = v
            continue
        token = v[len(ENCRYPTED_PREFIX):]
        try:
            result.decrypted[k] = f.decrypt(token.encode()).decode()
        except (InvalidToken, Exception) as exc:
            result.failed.append((k, str(exc)))

    return result
