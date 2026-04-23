"""Detect and report duplicate values across keys in a .env file."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateGroup:
    """A set of keys that all share the same value."""
    value: str
    keys: List[str]

    def __len__(self) -> int:
        return len(self.keys)


@dataclass
class DuplicateResult:
    """Result of scanning an env mapping for duplicate values."""
    source: str
    groups: List[DuplicateGroup] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # convenience helpers
    # ------------------------------------------------------------------ #
    def has_duplicates(self) -> bool:
        return bool(self.groups)

    @property
    def total_duplicate_keys(self) -> int:
        """Total number of keys involved in any duplicate group."""
        return sum(len(g) for g in self.groups)

    @property
    def group_count(self) -> int:
        return len(self.groups)


def find_duplicate_values(
    env: Dict[str, str],
    source: str = "<env>",
    ignore_empty: bool = True,
) -> DuplicateResult:
    """Scan *env* and return keys that share identical values.

    Parameters
    ----------
    env:
        Parsed key/value mapping.
    source:
        Label for the origin file (used in reports).
    ignore_empty:
        When *True* (default) empty-string values are excluded from
        duplicate detection, since many keys legitimately have no value.
    """
    buckets: Dict[str, List[str]] = defaultdict(list)
    for key, value in env.items():
        if ignore_empty and value == "":
            continue
        buckets[value].append(key)

    groups = [
        DuplicateGroup(value=val, keys=sorted(keys))
        for val, keys in sorted(buckets.items())
        if len(keys) > 1
    ]
    return DuplicateResult(source=source, groups=groups)
