"""Apply a set of key/value patches to an .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envguard.parser import parse_env_file


@dataclass
class PatchResult:
    source: str
    added: Dict[str, str] = field(default_factory=dict)
    updated: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)
    unchanged: List[str] = field(default_factory=list)
    output_path: Optional[str] = None

    def __bool__(self) -> bool:
        return bool(self.added or self.updated)


def patch_env(
    env: Dict[str, str],
    patches: Dict[str, str],
    source: str = "<input>",
) -> PatchResult:
    """Apply *patches* onto *env*, returning a PatchResult."""
    result = PatchResult(source=source)
    merged: Dict[str, str] = dict(env)

    for key, new_value in patches.items():
        if key not in env:
            merged[key] = new_value
            result.added[key] = new_value
        elif env[key] == new_value:
            result.unchanged.append(key)
        else:
            result.updated[key] = (env[key], new_value)
            merged[key] = new_value

    result._merged = merged  # type: ignore[attr-defined]
    return result


def render_patched_env(original: Dict[str, str], result: PatchResult) -> str:
    """Render the patched env as .env file text, preserving key order."""
    merged: Dict[str, str] = getattr(result, "_merged", {**original})
    lines: List[str] = []
    for key, value in merged.items():
        if " " in value or "#" in value:
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n" if lines else ""


def patch_env_file(
    source_path: str,
    patches: Dict[str, str],
    output_path: Optional[str] = None,
) -> PatchResult:
    """Load *source_path*, apply *patches*, optionally write to *output_path*."""
    env = parse_env_file(source_path)
    result = patch_env(env, patches, source=source_path)
    result.output_path = output_path or source_path

    if output_path:
        Path(output_path).write_text(render_patched_env(env, result))

    return result
