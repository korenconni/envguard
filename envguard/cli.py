"""CLI entry point for envguard."""
import sys
import argparse

from envguard.parser import parse_env_file, EnvParseError
from envguard.differ import diff_envs
from envguard.reporter import print_diff_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard",
        description="Validate and diff .env files across environments.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    diff_cmd = subparsers.add_parser("diff", help="Diff two .env files")
    diff_cmd.add_argument("base", help="Base .env file (reference)")
    diff_cmd.add_argument("target", help="Target .env file to compare")
    diff_cmd.add_argument(
        "--no-values",
        action="store_true",
        help="Hide actual values in output",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "diff":
        try:
            base_env = parse_env_file(args.base)
            target_env = parse_env_file(args.target)
        except (FileNotFoundError, EnvParseError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

        result = diff_envs(base_env, target_env)
        print_diff_report(result, args.base, args.target, show_values=not args.no_values)

        sys.exit(1 if result.has_differences else 0)


if __name__ == "__main__":
    main()
