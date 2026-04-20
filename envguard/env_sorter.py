"""Sort and normalize .env file keys alphabetically or by custom order."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from envguard.parser import parse_env_file


@dataclass
class SortResult:
    original_order: List[str]
    sorted_order: List[str]
    moved: List[Tuple[str, int, int]]  # (key, old_index, new_index)
    already_sorted: bool

    def __bool__(self) -> bool:
        return self.already_sorted


def sort_env(
    env: Dict[str, str],
    groups: Optional[List[List[str]]] = None,
    case_sensitive: bool = False,
) -> SortResult:
    """Return a SortResult describing how keys would be reordered.

    If *groups* is provided, keys are sorted within each group; keys not
    belonging to any group are placed at the end, sorted among themselves.
    """
    original: List[str] = list(env.keys())

    if groups:
        ordered: List[str] = []
        remaining = set(original)
        for group in groups:
            in_group = [k for k in group if k in remaining]
            ordered.extend(in_group)
            remaining -= set(in_group)
        tail = sorted(remaining, key=lambda k: k if case_sensitive else k.lower())
        ordered.extend(tail)
    else:
        ordered = sorted(original, key=lambda k: k if case_sensitive else k.lower())

    moved: List[Tuple[str, int, int]] = [
        (key, original.index(key), new_idx)
        for new_idx, key in enumerate(ordered)
        if original.index(key) != new_idx
    ]

    return SortResult(
        original_order=original,
        sorted_order=ordered,
        moved=moved,
        already_sorted=(original == ordered),
    )


def render_sorted_env(env: Dict[str, str], sorted_order: List[str]) -> str:
    """Render env dict to a .env-formatted string following *sorted_order*."""
    lines: List[str] = []
    for key in sorted_order:
        value = env[key]
        if " " in value or "#" in value or not value:
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


def sort_env_file(
    path: str,
    groups: Optional[List[List[str]]] = None,
    case_sensitive: bool = False,
) -> Tuple[SortResult, str]:
    """Parse *path*, sort its keys, and return (SortResult, rendered_content)."""
    env = parse_env_file(path)
    result = sort_env(env, groups=groups, case_sensitive=case_sensitive)
    rendered = render_sorted_env(env, result.sorted_order)
    return result, rendered
