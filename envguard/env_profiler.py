"""Profile .env files: count keys, detect value types, compute stats."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

_BOOL_PATTERN = re.compile(r'^(true|false|yes|no|1|0)$', re.IGNORECASE)
_INT_PATTERN = re.compile(r'^-?\d+$')
_FLOAT_PATTERN = re.compile(r'^-?\d+\.\d+$')
_URL_PATTERN = re.compile(r'^https?://', re.IGNORECASE)
_PATH_PATTERN = re.compile(r'^[/~.]')


def _infer_type(value: str) -> str:
    if value == "":
        return "empty"
    if _BOOL_PATTERN.match(value):
        return "bool"
    if _INT_PATTERN.match(value):
        return "int"
    if _FLOAT_PATTERN.match(value):
        return "float"
    if _URL_PATTERN.match(value):
        return "url"
    if _PATH_PATTERN.match(value):
        return "path"
    return "string"


@dataclass
class ProfileResult:
    source: str
    total_keys: int
    empty_values: int
    type_counts: Dict[str, int] = field(default_factory=dict)
    longest_key: str = ""
    longest_value_key: str = ""
    uppercase_keys: int = 0
    mixed_case_keys: int = 0


def profile_env(env: Dict[str, str], source: str = "<env>") -> ProfileResult:
    """Compute a profile of the given env mapping."""
    type_counts: Dict[str, int] = {}
    empty = 0
    longest_key = ""
    longest_value_key = ""
    uppercase_keys = 0
    mixed_case_keys = 0

    for key, value in env.items():
        t = _infer_type(value)
        type_counts[t] = type_counts.get(t, 0) + 1
        if value == "":
            empty += 1
        if len(key) > len(longest_key):
            longest_key = key
        if len(value) > len(env.get(longest_value_key, "")):
            longest_value_key = key
        if key == key.upper():
            uppercase_keys += 1
        elif key != key.lower():
            mixed_case_keys += 1

    return ProfileResult(
        source=source,
        total_keys=len(env),
        empty_values=empty,
        type_counts=type_counts,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
        uppercase_keys=uppercase_keys,
        mixed_case_keys=mixed_case_keys,
    )
