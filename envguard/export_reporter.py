"""Human-readable reporter for ExportResult."""
from __future__ import annotations

from envguard.env_exporter import ExportResult


def format_export_result(result: ExportResult, *, show_content: bool = False) -> str:
    """Return a summary string for *result*.

    Parameters
    ----------
    result:
        The ExportResult produced by :func:`~envguard.env_exporter.export_env`.
    show_content:
        When *True* the exported payload is appended after the summary.
    """
    lines: list[str] = [
        f"Export: {result.source} → {result.fmt.upper()}",
        f"  Keys exported : {result.key_count}",
    ]

    if result.warnings:
        lines.append("  Warnings:")
        for w in result.warnings:
            lines.append(f"    ! {w}")
    else:
        lines.append("  No warnings.")

    if show_content:
        separator = "-" * 40
        lines.append(separator)
        lines.append(result.content)
        lines.append(separator)

    return "\n".join(lines)
