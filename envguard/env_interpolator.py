"""Resolve variable references within .env files (e.g. FOO=${BAR}_suffix)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved_refs: List[str] = field(default_factory=list)  # var names missing
    cycles: List[str] = field(default_factory=list)  # var names in a cycle


def _extract_refs(value: str) -> List[str]:
    """Return all variable names referenced inside *value*."""
    return [m.group(1) or m.group(2) for m in _REF_RE.finditer(value)]


def _substitute(value: str, resolved: Dict[str, str]) -> str:
    def replacer(m: re.Match) -> str:
        name = m.group(1) or m.group(2)
        return resolved.get(name, m.group(0))

    return _REF_RE.sub(replacer, value)


def interpolate(env: Dict[str, str]) -> InterpolationResult:
    """Resolve all ``${VAR}`` / ``$VAR`` references in *env* in dependency order.

    Variables that reference unknown keys are left as-is and recorded in
    ``unresolved_refs``.  Cyclic dependencies are detected and recorded in
    ``cycles``.
    """
    result = InterpolationResult()
    resolved: Dict[str, str] = {}
    # Keys whose value contains no references can be seeded immediately.
    pending = dict(env)

    changed = True
    while changed:
        changed = False
        still_pending: Dict[str, str] = {}
        for key, value in pending.items():
            refs = _extract_refs(value)
            if all(r in resolved for r in refs):
                resolved[key] = _substitute(value, resolved)
                changed = True
            else:
                still_pending[key] = value
        pending = still_pending

    # Anything left in *pending* is either unresolvable or cyclic.
    for key, value in pending.items():
        refs = _extract_refs(value)
        missing = [r for r in refs if r not in env]
        if missing:
            result.unresolved_refs.extend(missing)
            resolved[key] = _substitute(value, resolved)  # best-effort
        else:
            result.cycles.append(key)
            resolved[key] = value  # keep raw value

    result.resolved = resolved
    result.unresolved_refs = list(dict.fromkeys(result.unresolved_refs))
    result.cycles = list(dict.fromkeys(result.cycles))
    return result
