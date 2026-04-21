"""Tests for envguard.env_templater."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envguard.env_templater import (
    generate_template,
    render_template,
    write_template,
    TemplateResult,
)


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return str(p)

    return _write


def test_generate_template_returns_all_keys(tmp_env):
    path = tmp_env("""\
        DB_HOST=localhost
        DB_PORT=5432
    """)
    result = generate_template(path)
    assert "DB_HOST" in result.keys
    assert "DB_PORT" in result.keys


def test_sensitive_keys_are_masked(tmp_env):
    path = tmp_env("""\
        API_SECRET=supersecret
        DEBUG=true
    """)
    result = generate_template(path, mask_sensitive=True, placeholder="<secret>")
    assert "API_SECRET" in result.sensitive_keys
    assert "DEBUG" not in result.sensitive_keys
    assert result._lines["API_SECRET"] == "<secret>"
    assert result._lines["DEBUG"] == "true"


def test_no_mask_keeps_values(tmp_env):
    path = tmp_env("DB_PASSWORD=hunter2\n")
    result = generate_template(path, mask_sensitive=False)
    assert result.sensitive_keys == []
    assert result._lines["DB_PASSWORD"] == "hunter2"


def test_render_template_contains_header(tmp_env):
    path = tmp_env("FOO=bar\n")
    result = generate_template(path)
    rendered = render_template(result)
    assert "envguard" in rendered
    assert "FOO=" in rendered


def test_write_template_creates_file(tmp_env, tmp_path):
    path = tmp_env("FOO=bar\n")
    out = str(tmp_path / ".env.template")
    result = generate_template(path)
    write_template(result, out)
    assert Path(out).exists()
    assert result.output_path == out


def test_bool_false_for_empty_env(tmp_env):
    path = tmp_env("")
    result = generate_template(path)
    assert not result


def test_bool_true_for_non_empty_env(tmp_env):
    path = tmp_env("X=1\n")
    result = generate_template(path)
    assert result
