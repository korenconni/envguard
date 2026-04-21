"""Format AuditResult for terminal output."""
from __future__ import annotations

from envguard.env_auditor import AuditResult
from envguard.reporter import _color

_SEVERITY_COLOR = {
    "error": "red",
    "warning": "yellow",
    "info": "cyan",
}


def format_audit_result(result: AuditResult, *, use_color: bool = True) -> str:
    """Return a human-readable audit report string."""
    if not result.has_issues:
        msg = "✔ No audit issues found."
        return _color(msg, "green") if use_color else msg

    lines: list[str] = []
    header = f"Audit found {len(result.issues)} issue(s):"
    lines.append(_color(header, "yellow") if use_color else header)
    lines.append("")

    for issue in result.issues:
        color = _SEVERITY_COLOR.get(issue.severity, "white")
        badge = f"[{issue.severity.upper()}]"
        badge_fmt = _color(badge, color) if use_color else badge
        code_fmt = _color(issue.code, "cyan") if use_color else issue.code
        lines.append(f"  {badge_fmt} {code_fmt}  {issue.message}")

    lines.append("")
    error_count = len(result.errors)
    warn_count = len(result.warnings)
    summary = f"Summary: {error_count} error(s), {warn_count} warning(s)."
    lines.append(_color(summary, "red") if (use_color and error_count) else summary)

    return "\n".join(lines)
