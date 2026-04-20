"""CLI command handlers for the 'sort' sub-command group."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envguard.env_sorter import sort_env_file
from envguard.output import _supports_color
from envguard.sort_reporter import format_sort_result, format_sorted_preview


def cmd_sort_check(args: argparse.Namespace) -> int:
    """Check whether an .env file is sorted; exit 1 if not."""
    use_color = _supports_color() and not getattr(args, "no_color", False)
    try:
        result, _ = sort_env_file(args.env_file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(format_sort_result(result, color=use_color))
    return 0 if result.already_sorted else 1


def cmd_sort_show(args: argparse.Namespace) -> int:
    """Print the sorted .env content to stdout without modifying the file."""
    use_color = _supports_color() and not getattr(args, "no_color", False)
    try:
        result, rendered = sort_env_file(args.env_file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(format_sort_result(result, color=use_color))
    if not result.already_sorted:
        print(format_sorted_preview(rendered, color=use_color))
    return 0


def cmd_sort_write(args: argparse.Namespace) -> int:
    """Sort the .env file in-place."""
    use_color = _supports_color() and not getattr(args, "no_color", False)
    try:
        result, rendered = sort_env_file(args.env_file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if result.already_sorted:
        print(format_sort_result(result, color=use_color))
        return 0

    Path(args.env_file).write_text(rendered, encoding="utf-8")
    msg = format_sort_result(result, color=use_color)
    print(msg)
    written = f"✔ Written to {args.env_file}"
    print(written)
    return 0
