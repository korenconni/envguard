"""Extended diff utilities: value-level change detection with type awareness."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ValueChange:
    key: str
    old_value: str
    new_value: str

    @property
    def is_type_change(self) -> bool:
        """Return True when the inferred type of the value changed."""
        return _infer_type(self.old_value) != _infer_type(self.new_value)

    @property
    def old_type(self) -> str:
        return _infer_type(self.old_value)

    @property
    def new_type(self) -> str:
        return _infer_type(self.new_value)


@dataclass
class ExtendedDiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: List[ValueChange] = field(default_factory=list)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    @property
    def type_changes(self) -> List[ValueChange]:
        return [c for c in self.changed if c.is_type_change]


def _infer_type(value: str) -> str:
    if value.lower() in ("true", "false"):
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    if not value:
        return "empty"
    return "str"


def extended_diff(
    base: Dict[str, str],
    head: Dict[str, str],
) -> ExtendedDiffResult:
    """Produce a rich diff between two parsed env mappings."""
    result = ExtendedDiffResult()
    all_keys = set(base) | set(head)
    for key in sorted(all_keys):
        in_base = key in base
        in_head = key in head
        if in_base and not in_head:
            result.removed[key] = base[key]
        elif in_head and not in_base:
            result.added[key] = head[key]
        elif base[key] == head[key]:
            result.unchanged[key] = base[key]
        else:
            result.changed.append(ValueChange(key, base[key], head[key]))
    return result
