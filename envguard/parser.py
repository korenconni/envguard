"""Parser for .env files."""
from pathlib import Path
from typing import Dict, Optional


class EnvParseError(Exception):
    pass


def parse_env_file(path: str) -> Dict[str, Optional[str]]:
    """
    Parse a .env file and return a dict of key-value pairs.
    Supports comments (#), blank lines, and values with or without quotes.
    """
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f".env file not found: {path}")

    result: Dict[str, Optional[str]] = {}

    with env_path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.rstrip("\n")

            # Skip blank lines and comments
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if "=" not in stripped:
                raise EnvParseError(
                    f"Invalid syntax at line {lineno}: '{line}'"
                )

            key, _, raw_value = stripped.partition("=")
            key = key.strip()

            if not key:
                raise EnvParseError(f"Empty key at line {lineno}")

            value: Optional[str] = raw_value.strip()

            # Strip surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            elif value == "":
                value = None

            result[key] = value

    return result
