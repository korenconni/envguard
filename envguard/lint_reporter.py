"""Format lint results for terminal output."""
from __future__ import annotations

from envguard.env_linter import LintResult
from envguard.reporter import _color

_SEVERITY_COLOR = {
    "error": "red",
    "warning": "yellow",
}


def format_lint_result(result: LintResult, path: str, *, use_color: bool = True) -> str:
    """Return a human-readable string summarising lint issues."""
    lines: list[str] = []

    header = f"Lint results for: {path}"
    lines.append(_color(header, "cyan") if use_color else header)
    lines.append("-" * len(header))

    if not result.has_issues:
        msg = "No issues found."
        lines.append(_color(msg, "green") if use_color else msg)
        return "\n".join(lines)

    for issue in result.issues:
        severity_label = issue.severity.upper()
        color = _SEVERITY_COLOR.get(issue.severity, "white")
        tag = _color(f"[{severity_label}]", color) if use_color else f"[{severity_label}]"
        lines.append(f"  Line {issue.line:>3}  {tag}  {issue.code}  {issue.message}")

    total = len(result.issues)
    err_count = len(result.errors)
    warn_count = len(result.warnings)
    summary = f"\n{total} issue(s): {err_count} error(s), {warn_count} warning(s)"
    lines.append(_color(summary, "red") if (use_color and err_count) else summary)

    return "\n".join(lines)
