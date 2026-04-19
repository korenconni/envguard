"""Formats diff and validation results for CLI output."""
from __future__ import annotations

from typing import Optional

from envguard.differ import DiffResult
from envguard.validator import ValidationResult


ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def _color(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{ANSI_RESET}" if use_color else text


def format_diff(result: DiffResult, use_color: bool = True) -> str:
    lines: list[str] = []

    for key in sorted(result.missing_in_second):
        lines.append(_color(f"- {key}", ANSI_RED, use_color))

    for key in sorted(result.missing_in_first):
        lines.append(_color(f"+ {key}", ANSI_GREEN, use_color))

    for key in sorted(result.value_differences):
        old, new = result.value_differences[key]
        lines.append(_color(f"~ {key}: {old!r} -> {new!r}", ANSI_YELLOW, use_color))

    if not lines:
        return _color("No differences found.", ANSI_GREEN, use_color)

    return "\n".join(lines)


def format_validation(result: ValidationResult, use_color: bool = True) -> str:
    lines: list[str] = []

    if result.missing_keys:
        for key in sorted(result.missing_keys):
            lines.append(_color(f"MISSING   {key}", ANSI_RED, use_color))

    if result.empty_keys:
        for key in sorted(result.empty_keys):
            lines.append(_color(f"EMPTY     {key}", ANSI_YELLOW, use_color))

    if result.unknown_keys:
        for key in sorted(result.unknown_keys):
            lines.append(_color(f"UNKNOWN   {key}", ANSI_YELLOW, use_color))

    if not lines:
        return _color("Validation passed.", ANSI_GREEN, use_color)

    status = _color("Validation failed:", ANSI_RED, use_color)
    return status + "\n" + "\n".join(lines)
