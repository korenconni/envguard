"""Tests for envguard.interpolation_reporter."""
from __future__ import annotations

from envguard.env_interpolator import InterpolationResult
from envguard.interpolation_reporter import format_interpolation_report, format_resolved_env


def _result(**kwargs) -> InterpolationResult:
    defaults = dict(resolved={}, unresolved_refs=[], cycles=[])
    defaults.update(kwargs)
    return InterpolationResult(**defaults)


def test_success_message_when_clean():
    r = _result(resolved={"A": "1"})
    out = format_interpolation_report(r, use_color=False)
    assert "resolved successfully" in out


def test_unresolved_refs_shown():
    r = _result(unresolved_refs=["MISSING"])
    out = format_interpolation_report(r, use_color=False)
    assert "MISSING" in out
    assert "Unresolved" in out


def test_cycles_shown():
    r = _result(cycles=["X", "Y"])
    out = format_interpolation_report(r, use_color=False)
    assert "Cyclic" in out
    assert "X" in out
    assert "Y" in out


def test_format_resolved_env_sorted():
    r = _result(resolved={"Z": "last", "A": "first", "M": "mid"})
    out = format_resolved_env(r, use_color=False)
    lines = out.splitlines()
    keys = [l.split("=")[0] for l in lines]
    assert keys == sorted(keys)


def test_format_resolved_env_key_value_format():
    r = _result(resolved={"HOST": "localhost"})
    out = format_resolved_env(r, use_color=False)
    assert "HOST=localhost" in out
