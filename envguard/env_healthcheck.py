"""Health check module: scores an .env file across multiple dimensions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.env_auditor import audit_env
from envguard.env_linter import lint_env
from envguard.env_duplicator import find_duplicates
from envguard.env_trimmer import trim_env


@dataclass
class HealthDimension:
    name: str
    score: int          # 0-100
    max_score: int
    issues: List[str] = field(default_factory=list)


@dataclass
class HealthResult:
    dimensions: List[HealthDimension] = field(default_factory=list)

    @property
    def total_score(self) -> int:
        return sum(d.score for d in self.dimensions)

    @property
    def max_score(self) -> int:
        return sum(d.max_score for d in self.dimensions)

    @property
    def percentage(self) -> float:
        if self.max_score == 0:
            return 100.0
        return round(self.total_score / self.max_score * 100, 1)

    @property
    def grade(self) -> str:
        p = self.percentage
        if p >= 90:
            return "A"
        if p >= 75:
            return "B"
        if p >= 60:
            return "C"
        if p >= 40:
            return "D"
        return "F"


def healthcheck_env(env: Dict[str, str]) -> HealthResult:
    """Run all health checks and return a scored HealthResult."""
    result = HealthResult()

    # --- Lint dimension (max 30) ---
    lint = lint_env(env)
    lint_errors = [i.message for i in lint.issues if i.severity == "error"]
    lint_warns = [i.message for i in lint.issues if i.severity == "warning"]
    lint_deduction = min(30, len(lint_errors) * 10 + len(lint_warns) * 3)
    result.dimensions.append(HealthDimension(
        name="lint",
        score=30 - lint_deduction,
        max_score=30,
        issues=lint_errors + lint_warns,
    ))

    # --- Audit / security dimension (max 40) ---
    audit = audit_env(env)
    audit_errors = [i.message for i in audit.issues if i.severity == "error"]
    audit_warns = [i.message for i in audit.issues if i.severity == "warning"]
    audit_deduction = min(40, len(audit_errors) * 15 + len(audit_warns) * 5)
    result.dimensions.append(HealthDimension(
        name="security",
        score=40 - audit_deduction,
        max_score=40,
        issues=audit_errors + audit_warns,
    ))

    # --- Duplicates dimension (max 15) ---
    dup = find_duplicates(env)
    dup_issues = [f"Duplicate key: {g.key}" for g in dup.groups]
    dup_deduction = min(15, len(dup.groups) * 5)
    result.dimensions.append(HealthDimension(
        name="duplicates",
        score=15 - dup_deduction,
        max_score=15,
        issues=dup_issues,
    ))

    # --- Cleanliness / trim dimension (max 15) ---
    trim = trim_env(env)
    trim_issues = [f"Untrimmed value for key: {k}" for k in trim.trimmed_keys]
    trim_deduction = min(15, len(trim.trimmed_keys) * 3)
    result.dimensions.append(HealthDimension(
        name="cleanliness",
        score=15 - trim_deduction,
        max_score=15,
        issues=trim_issues,
    ))

    return result
