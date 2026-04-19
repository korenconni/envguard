"""High-level output helpers used by the CLI."""
from __future__ import annotations

import sys
from typing import TextIO

from envguard.differ import DiffResult
from envguard.validator import ValidationResult
from envguard.reporter import format_diff, format_validation


def _supports_color(stream: TextIO) -> bool:
    """Return True if the stream likely supports ANSI color codes."""
    return hasattr(stream, "isatty") and stream.isatty()


def print_diff(
    result: DiffResult,
    stream: TextIO = sys.stdout,
    *,
    force_color: bool | None = None,
) -> int:
    """Print diff result; return exit code (1 if differences exist, else 0)."""
    use_color = force_color if force_color is not None else _supports_color(stream)
    print(format_diff(result, use_color=use_color), file=stream)
    return 1 if (result.missing_in_first or result.missing_in_second or result.value_differences) else 0


def print_validation(
    result: ValidationResult,
    stream: TextIO = sys.stdout,
    *,
    force_color: bool | None = None,
) -> int:
    """Print validation result; return exit code (1 if invalid, else 0)."""
    use_color = force_color if force_color is not None else _supports_color(stream)
    print(format_validation(result, use_color=use_color), file=stream)
    return 0 if (not result.missing_keys and not result.empty_keys) else 1
