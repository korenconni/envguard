"""CLI command handlers for encryption and decryption of .env files."""

from __future__ import annotations

import sys
from pathlib import Path

from .env_encryptor import generate_key, encrypt_env, decrypt_env
from .parser import parse_env_file, EnvParseError


def cmd_encrypt(
    env_path: str,
    key: str | None,
    output_path: str | None,
    *,
    print_key: bool = False,
) -> int:
    """Encrypt sensitive values in an .env file.

    Args:
        env_path:    Path to the source .env file.
        key:         Base64-encoded Fernet key.  If *None* a new key is
                     generated and (optionally) printed to stdout.
        output_path: Where to write the encrypted file.  Defaults to
                     ``<env_path>.enc``.
        print_key:   When *True* and a key was auto-generated, print the
                     key to stdout so the caller can persist it.

    Returns:
        0 on success, non-zero on failure.
    """
    source = Path(env_path)
    if not source.exists():
        print(f"[error] File not found: {env_path}", file=sys.stderr)
        return 1

    try:
        env = parse_env_file(str(source))
    except EnvParseError as exc:
        print(f"[error] Could not parse {env_path}: {exc}", file=sys.stderr)
        return 1

    if key is None:
        key = generate_key()
        if print_key:
            print(f"Generated key: {key}")

    result = encrypt_env(env, key)

    dest = Path(output_path) if output_path else source.with_suffix(".enc")
    lines = [f"{k}={v}\n" for k, v in result.encrypted_env.items()]
    dest.write_text("".join(lines))
    print(f"Encrypted env written to {dest}")
    if result.encrypted_keys:
        print(f"Encrypted keys ({len(result.encrypted_keys)}): {', '.join(sorted(result.encrypted_keys))}")
    else:
        print("No sensitive keys detected — file written unchanged.")
    return 0


def cmd_decrypt(
    env_path: str,
    key: str,
    output_path: str | None,
) -> int:
    """Decrypt an encrypted .env file back to plain text.

    Args:
        env_path:    Path to the encrypted .env file.
        key:         Base64-encoded Fernet key used during encryption.
        output_path: Where to write the decrypted file.  Defaults to
                     ``<env_path>.dec``.

    Returns:
        0 on success, non-zero on failure.
    """
    source = Path(env_path)
    if not source.exists():
        print(f"[error] File not found: {env_path}", file=sys.stderr)
        return 1

    try:
        env = parse_env_file(str(source))
    except EnvParseError as exc:
        print(f"[error] Could not parse {env_path}: {exc}", file=sys.stderr)
        return 1

    result = decrypt_env(env, key)

    if result.failed_keys:
        print(
            f"[warning] Could not decrypt {len(result.failed_keys)} key(s): "
            f"{', '.join(sorted(result.failed_keys))}",
            file=sys.stderr,
        )

    dest = Path(output_path) if output_path else source.with_suffix(".dec")
    lines = [f"{k}={v}\n" for k, v in result.decrypted_env.items()]
    dest.write_text("".join(lines))
    print(f"Decrypted env written to {dest}")
    return 0 if not result.failed_keys else 2


def cmd_generate_key() -> int:
    """Print a freshly generated Fernet key to stdout.

    Returns:
        Always 0.
    """
    print(generate_key())
    return 0
