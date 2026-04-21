"""Format template generation results for CLI output."""
from __future__ import annotations

from envguard.env_templater import TemplateResult
from envguard.reporter import _color


def format_template_result(result: TemplateResult, *, color: bool = True) -> str:
    """Return a human-readable summary of a template generation run."""
    lines: list[str] = []

    header = f"Template generated from: {result.source_path}"
    lines.append(_color(header, "cyan", enabled=color))
    lines.append(f"  Total keys   : {len(result.keys)}")
    lines.append(f"  Masked keys  : {len(result.sensitive_keys)}")

    if result.sensitive_keys:
        lines.append("  Masked:")
        for key in sorted(result.sensitive_keys):
            lines.append(f"    - {_color(key, 'yellow', enabled=color)}")

    if result.output_path:
        lines.append(f"  Written to   : {_color(result.output_path, 'green', enabled=color)}")

    return "\n".join(lines)


def format_template_preview(result: TemplateResult) -> str:
    """Return the raw template text for --dry-run style preview."""
    from envguard.env_templater import render_template

    return render_template(result)
