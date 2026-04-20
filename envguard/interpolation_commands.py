"""CLI command handlers for the interpolation sub-command."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from envguard.env_interpolator import interpolate
from envguard.interpolation_reporter import format_interpolation_report, format_resolved_env
from envguard.output import _supports_color
from envguard.parser import parse_env_file, EnvParseError


def cmd_interpolate(args: argparse.Namespace) -> int:
    """Resolve variable references in an .env file and print the result.

    Returns 0 on success, 1 if unresolved refs or cycles were found.
    """
    use_color = _supports_color() and not getattr(args, "no_color", False)

    try:
        env = parse_env_file(args.file)
    except EnvParseError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 2

    result = interpolate(env)

    report = format_interpolation_report(result, use_color=use_color)
    print(report)

    if getattr(args, "show_resolved", False):
        print()
        print(format_resolved_env(result, use_color=use_color))

    if result.unresolved_refs or result.cycles:
        return 1
    return 0
