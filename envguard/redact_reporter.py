"""Format redaction results for CLI output."""
from __future__ import annotations

from envguard.env_redactor import RedactResult


def format_redact_result(result: RedactResult, *, show_preview: bool = False) -> str:
    lines: list[str] = []
    lines.append(f"Source : {result.source}")
    lines.append(f"Total keys   : {result.total_keys}")
    lines.append(f"Redacted keys: {result.redacted_count}")

    if result.redacted_keys:
        lines.append("")
        lines.append("Redacted:")
        for key in result.redacted_keys:
            lines.append(f"  - {key}")
    else:
        lines.append("")
        lines.append("No sensitive keys found — nothing redacted.")

    if show_preview and result.total_keys:
        from envguard.env_redactor import render_redacted_env

        lines.append("")
        lines.append("Preview:")
        for line in render_redacted_env(result).splitlines():
            lines.append(f"  {line}")

    return "\n".join(lines)
