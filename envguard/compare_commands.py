"""CLI command handlers for the compare feature."""
from __future__ import annotations

import argparse
import sys

from envguard.env_comparator import compare_env_files
from envguard.compare_reporter import format_compare_result
from envguard.parser import EnvParseError


def cmd_compare(args: argparse.Namespace) -> int:
    """Compare two .env files and print a detailed value-level diff.

    Returns 0 if files are identical (after ignoring excluded keys),
    1 if differences exist, 2 on error.
    """
    ignore_keys: list[str] = []
    if getattr(args, "ignore", None):
        ignore_keys = [k.strip() for k in args.ignore.split(",") if k.strip()]

    try:
        result = compare_env_files(
            args.left,
            args.right,
            ignore_keys=ignore_keys or None,
        )
    except EnvParseError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"File not found: {exc}", file=sys.stderr)
        return 2

    show_unchanged: bool = getattr(args, "show_unchanged", False)
    print(format_compare_result(result, show_unchanged=show_unchanged))

    return 1 if result.has_differences else 0
