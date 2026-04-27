"""Tests for ``FrontappClient`` initialization — auth resolution + config plumbing.

The client's ``__init__`` resolves credentials from four sources, in this
order: explicit ``api_key`` param > ``FRONTAPP_API_KEY`` env var (which
includes ``.env`` via load_dotenv) > ``~/.netrc``. These tests pin that
ordering and the related config knobs (base_url, timeout, max_retries,
max_pages).

Note: ``__init__`` calls ``load_dotenv()``, which walks up from CWD
looking for a ``.env`` file. Tests that need to assert the *absence* of
an env var (netrc fallback, no-credentials failure) ``chdir`` to a
fresh ``tmp_path`` first so a contributor's local ``.env`` at the repo
root doesn't pollute the result.
"""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from frontapp_public_api_client import FrontappClient


class TestAuthResolutionOrdering:
    def test_explicit_api_key_wins_over_env(self, monkeypatch):
        monkeypatch.setenv("FRONTAPP_API_KEY", "from-env")
        client = FrontappClient(api_key="from-param")
        assert client.token == "from-param"

    def test_env_var_used_when_no_param(self, monkeypatch):
        monkeypatch.setenv("FRONTAPP_API_KEY", "env-token-xyz")
        client = FrontappClient()
        assert client.token == "env-token-xyz"

    def test_netrc_used_when_no_param_or_env(self, monkeypatch, tmp_path):
        monkeypatch.delenv("FRONTAPP_API_KEY", raising=False)
        # Isolate from any local .env at the repo root that load_dotenv() finds.
        monkeypatch.chdir(tmp_path)

        netrc_file = tmp_path / ".netrc"
        netrc_file.write_text(
            "machine api2.frontapp.com login api password netrc-token\n"
        )
        netrc_file.chmod(0o600)

        with patch.object(Path, "home", return_value=tmp_path):
            client = FrontappClient(base_url="https://api2.frontapp.com")
        assert client.token == "netrc-token"

    def test_raises_value_error_when_no_credentials(self, monkeypatch, tmp_path):
        """No param, no env, no .env, no netrc → fail fast."""
        monkeypatch.delenv("FRONTAPP_API_KEY", raising=False)
        monkeypatch.chdir(tmp_path)

        with (
            patch.object(Path, "home", return_value=tmp_path),
            pytest.raises(ValueError, match="API key required"),
        ):
            FrontappClient()


class TestBaseUrlOverride:
    def test_explicit_base_url_wins(self, monkeypatch):
        monkeypatch.setenv("FRONTAPP_BASE_URL", "https://from-env.invalid")
        client = FrontappClient(api_key="x", base_url="https://from-param.invalid")
        # AuthenticatedClient stores _base_url
        assert client._base_url == "https://from-param.invalid"

    def test_env_base_url_used_when_no_param(self, monkeypatch):
        monkeypatch.setenv("FRONTAPP_BASE_URL", "https://from-env.invalid")
        client = FrontappClient(api_key="x")
        assert client._base_url == "https://from-env.invalid"

    def test_default_base_url_when_no_param_or_env(self, monkeypatch):
        monkeypatch.delenv("FRONTAPP_BASE_URL", raising=False)
        client = FrontappClient(api_key="x")
        assert client._base_url == "https://api2.frontapp.com"


class TestConfigPlumbing:
    def test_max_pages_default(self):
        client = FrontappClient(api_key="x", base_url="https://test.invalid")
        assert client.max_pages == 100

    def test_max_pages_override(self):
        client = FrontappClient(
            api_key="x", base_url="https://test.invalid", max_pages=5
        )
        assert client.max_pages == 5

    def test_logger_defaults_to_module_logger(self):
        client = FrontappClient(api_key="x", base_url="https://test.invalid")
        assert isinstance(client.logger, logging.Logger)

    def test_custom_logger_accepted(self):
        custom = logging.getLogger("custom-test")
        client = FrontappClient(
            api_key="x", base_url="https://test.invalid", logger=custom
        )
        assert client.logger is custom

    def test_token_kwarg_alias_accepted(self):
        """Backwards compatibility — older callers passed ``token=`` instead
        of ``api_key=``."""
        client = FrontappClient(token="legacy-name")
        assert client.token == "legacy-name"

    def test_token_and_api_key_both_set_raises(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            FrontappClient(api_key="a", token="b")


class TestSslVerifyWarning:
    def test_verify_false_emits_warning(self, caplog):
        with caplog.at_level(logging.WARNING):
            FrontappClient(api_key="x", base_url="https://test.invalid", verify=False)
        assert any(
            "SSL certificate verification is disabled" in r.message
            for r in caplog.records
        )

    def test_verify_true_no_warning(self, caplog):
        with caplog.at_level(logging.WARNING):
            FrontappClient(api_key="x", base_url="https://test.invalid", verify=True)
        ssl_warnings = [
            r for r in caplog.records if "SSL certificate verification" in r.message
        ]
        assert ssl_warnings == []
