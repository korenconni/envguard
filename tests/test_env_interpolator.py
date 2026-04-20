"""Tests for envguard.env_interpolator."""
from __future__ import annotations

import pytest

from envguard.env_interpolator import interpolate, _extract_refs


# ---------------------------------------------------------------------------
# _extract_refs
# ---------------------------------------------------------------------------

def test_extract_refs_brace_syntax():
    assert _extract_refs("${FOO}_bar") == ["FOO"]


def test_extract_refs_dollar_syntax():
    assert _extract_refs("$FOO/$BAR") == ["FOO", "BAR"]


def test_extract_refs_no_refs():
    assert _extract_refs("plain-value") == []


# ---------------------------------------------------------------------------
# interpolate — happy paths
# ---------------------------------------------------------------------------

def test_simple_substitution():
    env = {"BASE": "/app", "LOG": "${BASE}/logs"}
    r = interpolate(env)
    assert r.resolved["LOG"] == "/app/logs"
    assert not r.unresolved_refs
    assert not r.cycles


def test_chain_substitution():
    env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    r = interpolate(env)
    assert r.resolved["C"] == "hello_world!"


def test_no_references():
    env = {"KEY": "value", "OTHER": "123"}
    r = interpolate(env)
    assert r.resolved == env
    assert not r.unresolved_refs


def test_self_reference_detected_as_cycle():
    env = {"A": "${A}"}
    r = interpolate(env)
    assert "A" in r.cycles


def test_mutual_cycle_detected():
    env = {"X": "${Y}", "Y": "${X}"}
    r = interpolate(env)
    assert set(r.cycles) == {"X", "Y"}


def test_missing_ref_recorded():
    env = {"FOO": "${UNDEFINED}_value"}
    r = interpolate(env)
    assert "UNDEFINED" in r.unresolved_refs


def test_partial_resolution_with_missing():
    """Known keys resolve; unknown refs remain in the value string."""
    env = {"BASE": "/app", "PATH": "${BASE}/${MISSING}"}
    r = interpolate(env)
    assert r.resolved["PATH"].startswith("/app/")
    assert "MISSING" in r.unresolved_refs


def test_dollar_syntax_substitution():
    env = {"HOST": "localhost", "URL": "http://$HOST:8080"}
    r = interpolate(env)
    assert r.resolved["URL"] == "http://localhost:8080"
