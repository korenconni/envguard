"""Compare two .env files and produce a detailed value-level comparison report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envguard.parser import parse_env_file


@dataclass
class KeyComparison:
    key: str
    left_value: Optional[str]  # None means key absent
    right_value: Optional[str]

    @property
    def status(self) -> str:
        if self.left_value is None:
            return "added"
        if self.right_value is None:
            return "removed"
        if self.left_value == self.right_value:
            return "unchanged"
        return "changed"


@dataclass
class CompareResult:
    left_path: str
    right_path: str
    comparisons: List[KeyComparison] = field(default_factory=list)

    @property
    def added(self) -> List[KeyComparison]:
        return [c for c in self.comparisons if c.status == "added"]

    @property
    def removed(self) -> List[KeyComparison]:
        return [c for c in self.comparisons if c.status == "removed"]

    @property
    def changed(self) -> List[KeyComparison]:
        return [c for c in self.comparisons if c.status == "changed"]

    @property
    def unchanged(self) -> List[KeyComparison]:
        return [c for c in self.comparisons if c.status == "unchanged"]

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def compare_env_files(
    left_path: str,
    right_path: str,
    *,
    ignore_keys: Optional[List[str]] = None,
) -> CompareResult:
    """Parse both files and produce a key-by-key comparison."""
    ignore = set(ignore_keys or [])
    left: Dict[str, str] = parse_env_file(left_path)
    right: Dict[str, str] = parse_env_file(right_path)

    all_keys = sorted(set(left) | set(right))
    comparisons: List[KeyComparison] = []
    for key in all_keys:
        if key in ignore:
            continue
        comparisons.append(
            KeyComparison(
                key=key,
                left_value=left.get(key),
                right_value=right.get(key),
            )
        )

    return CompareResult(
        left_path=left_path,
        right_path=right_path,
        comparisons=comparisons,
    )
