"""CLI command handler for the extended-diff subcommand."""
from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path

from envguard.env_differ_extended import extended_diff
from envguard.extended_diff_reporter import format_extended_diff
from envguard.output import _supports_color
from envguard.parser import EnvParseError, parse_env_file


def cmd_extended_diff(args: Namespace) -> int:
    """Run an extended value-level diff between two .env files.

    Returns 0 when files are identical, 1 when differences exist, 2 on error.
    """
    base_path = Path(args.base)
    head_path = Path(args.head)

    for p in (base_path, head_path):
        if not p.exists():
            print(f"envguard: file not found: {p}", file=sys.stderr)
            return 2

    try:
        base_env = parse_env_file(base_path)
        head_env = parse_env_file(head_path)
    except EnvParseError as exc:
        print(f"envguard: parse error: {exc}", file=sys.stderr)
        return 2

    result = extended_diff(base_env, head_env)
    use_color = _supports_color() and not getattr(args, "no_color", False)
    print(format_extended_diff(result, color=use_color))

    if getattr(args, "strict_types", False) and result.type_changes:
        print(
            f"envguard: {len(result.type_changes)} type-change(s) detected (--strict-types)",
            file=sys.stderr,
        )
        return 1

    return 1 if result.has_differences else 0
