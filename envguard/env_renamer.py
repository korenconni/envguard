"""Rename keys across a .env file with optional dry-run support."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envguard.parser import parse_env_file, EnvParseError


@dataclass
class RenameResult:
    source: str
    renames_applied: Dict[str, str] = field(default_factory=dict)  # old -> new
    skipped: List[str] = field(default_factory=list)  # old keys not found
    lines: List[str] = field(default_factory=list)  # final rendered lines
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.error is None


def rename_keys(
    path: str,
    renames: Dict[str, str],
) -> RenameResult:
    """Return a RenameResult with updated lines; does NOT write to disk."""
    try:
        env = parse_env_file(path)
    except (EnvParseError, OSError) as exc:
        return RenameResult(source=path, error=str(exc))

    raw_lines: List[str] = Path(path).read_text(encoding="utf-8").splitlines(keepends=True)

    applied: Dict[str, str] = {}
    skipped: List[str] = []
    key_set = set(env.keys())

    for old, new in renames.items():
        if old in key_set:
            applied[old] = new
        else:
            skipped.append(old)

    if not applied:
        return RenameResult(
            source=path,
            skipped=skipped,
            lines=raw_lines,
        )

    new_lines: List[str] = []
    for line in raw_lines:
        stripped = line.lstrip()
        if stripped.startswith("#") or "=" not in stripped:
            new_lines.append(line)
            continue
        key_part = stripped.split("=", 1)[0].strip()
        if key_part in applied:
            rest = line[line.index("="):]
            indent = line[: len(line) - len(stripped)]
            new_lines.append(f"{indent}{applied[key_part]}{rest}")
        else:
            new_lines.append(line)

    return RenameResult(
        source=path,
        renames_applied=applied,
        skipped=skipped,
        lines=new_lines,
    )


def write_renamed(result: RenameResult, dest: Optional[str] = None) -> str:
    """Write renamed lines to *dest* (or back to source). Returns the path written."""
    if not result:
        raise ValueError(f"RenameResult has error: {result.error}")
    target = dest or result.source
    Path(target).write_text("".join(result.lines), encoding="utf-8")
    return target
