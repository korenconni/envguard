"""Validate .env files against a schema of required and optional keys."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationResult:
    missing_required: List[str] = field(default_factory=list)
    missing_optional: List[str] = field(default_factory=list)
    unknown_keys: List[str] = field(default_factory=list)
    empty_required: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.missing_required and not self.empty_required

    def summary(self) -> str:
        lines = []
        if self.missing_required:
            lines.append(f"Missing required keys: {', '.join(sorted(self.missing_required))}")
        if self.empty_required:
            lines.append(f"Empty required keys: {', '.join(sorted(self.empty_required))}")
        if self.missing_optional:
            lines.append(f"Missing optional keys: {', '.join(sorted(self.missing_optional))}")
        if self.unknown_keys:
            lines.append(f"Unknown keys: {', '.join(sorted(self.unknown_keys))}")
        return "\n".join(lines) if lines else "All checks passed."


@dataclass
class EnvSchema:
    required: Set[str] = field(default_factory=set)
    optional: Set[str] = field(default_factory=set)
    allow_unknown: bool = True


def validate_env(
    env: Dict[str, Optional[str]],
    schema: EnvSchema,
) -> ValidationResult:
    """Validate an env dict against the given schema."""
    result = ValidationResult()
    present = set(env.keys())

    for key in schema.required:
        if key not in present:
            result.missing_required.append(key)
        elif not env[key]:
            result.empty_required.append(key)

    for key in schema.optional:
        if key not in present:
            result.missing_optional.append(key)

    if not schema.allow_unknown:
        known = schema.required | schema.optional
        result.unknown_keys = [k for k in present if k not in known]

    return result
