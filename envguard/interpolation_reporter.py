"""Human-readable formatting for InterpolationResult."""
from __future__ import annotations

from envguard.env_interpolator import InterpolationResult
from envguard.reporter import _color


def format_interpolation_report(result: InterpolationResult, *, use_color: bool = True) -> str:
    lines: list[str] = []

    if not result.unresolved_refs and not result.cycles:
        ok = _color("green", "✔", use_color)
        lines.append(f"{ok} All variable references resolved successfully.")
        return "\n".join(lines)

    if result.unresolved_refs:
        warn = _color("yellow", "WARN", use_color)
        lines.append(f"{warn} Unresolved references (key not defined in file):")
        for ref in result.unresolved_refs:
            lines.append(f"  - ${ref}")

    if result.cycles:
        err = _color("red", "ERROR", use_color)
        lines.append(f"{err} Cyclic variable references detected:")
        for key in result.cycles:
            lines.append(f"  - {key}")

    return "\n".join(lines)


def format_resolved_env(result: InterpolationResult, *, use_color: bool = True) -> str:
    """Pretty-print the fully resolved key=value pairs."""
    lines: list[str] = []
    for key, value in sorted(result.resolved.items()):
        lines.append(f"{key}={value}")
    return "\n".join(lines)
