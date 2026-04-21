"""CLI command handlers for the 'profile' sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envguard.parser import parse_env_file, EnvParseError
from envguard.env_profiler import profile_env
from envguard.profile_reporter import format_profile_result
from envguard.output import _supports_color


def cmd_profile(args: argparse.Namespace) -> int:
    """Profile one or more .env files and print statistics."""
    files: list[str] = args.files
    if not files:
        print("envguard profile: no files specified.", file=sys.stderr)
        return 1

    exit_code = 0
    for path_str in files:
        path = Path(path_str)
        if not path.exists():
            print(f"envguard profile: file not found: {path}", file=sys.stderr)
            exit_code = 1
            continue
        try:
            env = parse_env_file(str(path))
        except EnvParseError as exc:
            print(f"envguard profile: parse error in {path}: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        result = profile_env(env, source=str(path))
        report = format_profile_result(result)
        print(report)
        if len(files) > 1:
            print()

    return exit_code
