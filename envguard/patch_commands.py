"""CLI command handlers for the patch sub-command."""
from __future__ import annotations

import argparse
from typing import List

from envguard.env_patcher import patch_env_file
from envguard.output import print_validation  # reuse generic printer
from envguard.patch_reporter import format_patch_result


def _parse_patch_pairs(pairs: List[str]) -> dict:
    """Convert ["KEY=VALUE", ...] to {KEY: VALUE}."""
    result = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"Invalid patch format {pair!r}. Expected KEY=VALUE."
            )
        key, _, value = pair.partition("=")
        result[key.strip()] = value
    return result


def cmd_patch(args: argparse.Namespace) -> int:
    """Apply key=value patches to an .env file."""
    try:
        patches = _parse_patch_pairs(args.set)
    except argparse.ArgumentTypeError as exc:
        print(f"Error: {exc}")
        return 2

    if not patches:
        print("No patches provided. Use --set KEY=VALUE.")
        return 1

    output = args.output if hasattr(args, "output") and args.output else None

    try:
        result = patch_env_file(args.file, patches, output_path=output)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}")
        return 1

    report = format_patch_result(result)
    print(report)
    return 0
