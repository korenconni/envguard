"""CLI command handlers for the `template` sub-command group."""
from __future__ import annotations

import sys
from argparse import Namespace

from envguard.env_templater import generate_template, write_template
from envguard.template_reporter import format_template_result, format_template_preview
from envguard.output import _supports_color


def cmd_template_generate(args: Namespace) -> int:
    """Generate a .env.template from an existing .env file."""
    color = _supports_color() and not getattr(args, "no_color", False)
    placeholder = getattr(args, "placeholder", "")
    mask = not getattr(args, "no_mask", False)

    try:
        result = generate_template(args.env_file, mask_sensitive=mask, placeholder=placeholder)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if getattr(args, "dry_run", False):
        print(format_template_preview(result))
        return 0

    output = getattr(args, "output", None) or args.env_file + ".template"
    write_template(result, output)
    print(format_template_result(result, color=color))
    return 0


def cmd_template_show(args: Namespace) -> int:
    """Print the template to stdout without writing to disk."""
    placeholder = getattr(args, "placeholder", "")
    mask = not getattr(args, "no_mask", False)

    try:
        result = generate_template(args.env_file, mask_sensitive=mask, placeholder=placeholder)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(format_template_preview(result))
    return 0
