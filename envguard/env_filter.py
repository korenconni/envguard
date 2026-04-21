"""Filter .env file keys by pattern, prefix, or value type."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    source: str
    matched: Dict[str, str] = field(default_factory=dict)
    excluded: Dict[str, str] = field(default_factory=dict)

    @property
    def match_count(self) -> int:
        return len(self.matched)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded)

    def __bool__(self) -> bool:
        return bool(self.matched)


def filter_env(
    env: Dict[str, str],
    source: str = "<env>",
    *,
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
    exclude_empty: bool = False,
    keys: Optional[List[str]] = None,
) -> FilterResult:
    """Return a FilterResult keeping only entries that satisfy all active criteria.

    Args:
        env: Parsed key/value mapping.
        source: Label used in reports (usually the file path).
        prefix: Keep only keys that start with this string (case-sensitive).
        pattern: Keep only keys whose name matches this regex.
        exclude_empty: When True, drop entries whose value is empty/whitespace.
        keys: Explicit allow-list of key names; when provided only these keys
              are considered (before other filters are applied).
    """
    compiled: Optional[re.Pattern[str]] = re.compile(pattern) if pattern else None

    matched: Dict[str, str] = {}
    excluded: Dict[str, str] = {}

    candidates = {k: v for k, v in env.items() if keys is None or k in keys}

    for key, value in candidates.items():
        reasons: List[str] = []

        if prefix and not key.startswith(prefix):
            reasons.append("prefix")
        if compiled and not compiled.search(key):
            reasons.append("pattern")
        if exclude_empty and not value.strip():
            reasons.append("empty")

        if reasons:
            excluded[key] = value
        else:
            matched[key] = value

    # Keys listed explicitly but absent from env are silently ignored.
    return FilterResult(source=source, matched=matched, excluded=excluded)
