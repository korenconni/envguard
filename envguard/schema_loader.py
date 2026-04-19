"""Load EnvSchema from a simple TOML or plain-text schema file."""

import sys
from pathlib import Path
from typing import Set

from envguard.validator import EnvSchema


def _parse_text_schema(content: str) -> EnvSchema:
    """Parse a plain-text schema file.

    Format:
        required: KEY1, KEY2
        optional: KEY3, KEY4
        allow_unknown: true
    """
    required: Set[str] = set()
    optional: Set[str] = set()
    allow_unknown = True

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()
        if key == "required":
            required = {k.strip() for k in value.split(",") if k.strip()}
        elif key == "optional":
            optional = {k.strip() for k in value.split(",") if k.strip()}
        elif key == "allow_unknown":
            allow_unknown = value.lower() not in ("false", "0", "no")

    return EnvSchema(required=required, optional=optional, allow_unknown=allow_unknown)


def load_schema(path: str) -> EnvSchema:
    """Load schema from *path*. Supports .toml (if tomllib available) and .txt."""
    schema_path = Path(path)
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")

    content = schema_path.read_text(encoding="utf-8")

    if schema_path.suffix == ".toml":
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            try:
                import tomllib  # type: ignore
            except ImportError:
                try:
                    import tomli as tomllib  # type: ignore
                except ImportError:
                    raise ImportError("Install 'tomli' for TOML schema support on Python < 3.11")
        data = tomllib.loads(content)
        return EnvSchema(
            required=set(data.get("required", [])),
            optional=set(data.get("optional", [])),
            allow_unknown=data.get("allow_unknown", True),
        )

    return _parse_text_schema(content)
