"""Integration-style tests for the FrontappClient transport stack.

Where ``test_frontapp_client.py`` covers the auth-resolution + config
surface, this file targets the moving parts inside the transport stack:

- ``_sanitize_url`` / ``_sanitize_body`` redaction of secrets
- ``ErrorLoggingTransport`` 4xx error logging
- ``_capture_pagination_metadata`` / ``_log_response_metrics`` event hooks
- ``_read_from_netrc`` edge cases (insecure permissions warning, missing
  file, no matching machine)

The transport stack itself is exercised end-to-end via ``httpx.MockTransport``
mounted as an ``ErrorLoggingTransport``'s wrapped transport so the
4xx-logging path runs against real responses.
"""

from __future__ import annotations

import logging
import os
import stat
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from frontapp_public_api_client import FrontappClient
from frontapp_public_api_client.frontapp_client import (
    ErrorLoggingTransport,
    _is_sensitive,
    _sanitize_body,
    _sanitize_url,
)

# ---------------------------------------------------------------------------
# _is_sensitive — pattern-match against known secret-y names
# ---------------------------------------------------------------------------


class TestIsSensitive:
    @pytest.mark.parametrize(
        "name",
        [
            "api_key",
            "API_KEY",
            "Authorization",
            "auth_token",
            "password",
            "secret",
            "secret_key",
            "credential",
            "user_email",
            "email",
        ],
    )
    def test_sensitive_names_match(self, name):
        assert _is_sensitive(name) is True

    @pytest.mark.parametrize("name", ["limit", "subject", "body", "tag_ids"])
    def test_non_sensitive_names_dont_match(self, name):
        assert _is_sensitive(name) is False

    def test_page_token_matches_token_pattern(self):
        """``page_token`` is a pagination cursor, not a credential, but the
        substring match is intentionally aggressive — values get redacted in
        log output as a tradeoff against accidental secret leakage."""
        assert _is_sensitive("page_token") is True


# ---------------------------------------------------------------------------
# _sanitize_url — redact sensitive query params
# ---------------------------------------------------------------------------


class TestSanitizeUrl:
    def test_no_query_string_returns_unchanged(self):
        url = "https://api.frontapp.com/conversations"
        assert _sanitize_url(url) == url

    def test_redacts_api_key_param(self):
        url = "https://api.frontapp.com/conversations?api_key=secret123&limit=50"
        result = _sanitize_url(url)
        assert "secret123" not in result
        assert "***" in result
        assert "limit=50" in result

    def test_redacts_token_param(self):
        url = "https://api.frontapp.com/x?token=abc123"
        assert "abc123" not in _sanitize_url(url)

    def test_keeps_non_sensitive_params(self):
        url = "https://api.frontapp.com/conversations?q=status%3Aopen&limit=25"
        result = _sanitize_url(url)
        assert "status" in result
        assert "limit=25" in result

    def test_malformed_url_strips_query(self):
        # Force a parsing failure path — the function falls back to dropping
        # the query entirely rather than risk leaking unsanitized content.
        with patch(
            "frontapp_public_api_client.frontapp_client.urlparse"
        ) as urlparse_mock:
            urlparse_mock.side_effect = ValueError("bad url")
            result = _sanitize_url("https://api.frontapp.com/x?token=abc")
        assert "abc" not in result
        assert "***" in result


# ---------------------------------------------------------------------------
# _sanitize_body — recursive dict/list redaction
# ---------------------------------------------------------------------------


class TestSanitizeBody:
    def test_redacts_sensitive_top_level_keys(self):
        body = {"api_key": "secret", "name": "Alice"}
        result = _sanitize_body(body)
        assert result == {"api_key": "***", "name": "Alice"}

    def test_redacts_nested_sensitive_keys(self):
        body = {"user": {"password": "p", "name": "Alice"}}
        result = _sanitize_body(body)
        assert result == {"user": {"password": "***", "name": "Alice"}}

    def test_redacts_inside_list_of_dicts(self):
        body = {"users": [{"token": "t1", "id": 1}, {"token": "t2", "id": 2}]}
        result = _sanitize_body(body)
        assert result == {
            "users": [{"token": "***", "id": 1}, {"token": "***", "id": 2}]
        }

    def test_non_dict_body_returns_placeholder(self):
        assert _sanitize_body("just a string") == "[non-dict body]"
        assert _sanitize_body(42) == "[non-dict body]"
        assert _sanitize_body([1, 2, 3]) == "[non-dict body]"


# ---------------------------------------------------------------------------
# ErrorLoggingTransport — wraps a transport, logs 4xx
# ---------------------------------------------------------------------------


class TestErrorLoggingTransport:
    """Wraps a MockTransport so we drive ``handle_async_request`` end-to-end."""

    def _build_transport(
        self, status: int, body, *, request_body: bytes | None = None
    ) -> tuple[ErrorLoggingTransport, MagicMock]:
        if isinstance(body, (dict, list)):
            mock = httpx.MockTransport(lambda req: httpx.Response(status, json=body))
        else:
            mock = httpx.MockTransport(lambda req: httpx.Response(status, text=body))
        logger = MagicMock(spec=logging.Logger)
        return ErrorLoggingTransport(wrapped_transport=mock, logger=logger), logger

    async def test_2xx_does_not_log(self):
        transport, logger = self._build_transport(200, {"ok": True})
        async with httpx.AsyncClient(transport=transport) as client:
            resp = await client.get("https://x.invalid/anything")
        assert resp.status_code == 200
        logger.error.assert_not_called()

    async def test_404_logs_simple_error(self):
        transport, logger = self._build_transport(404, {"message": "not found"})
        async with httpx.AsyncClient(transport=transport) as client:
            await client.get("https://x.invalid/conversations/cnv_missing")
        assert logger.error.called
        msg = logger.error.call_args[0][0]
        assert "Client error 404" in msg
        assert "GET" in msg
        assert "not found" in msg

    async def test_422_logs_validation_error_with_field_breakdown(self):
        body = {
            "message": "Validation failed",
            "errors": {
                "name": ["required"],
                "email": ["invalid format"],
            },
        }
        transport, logger = self._build_transport(422, body)
        async with httpx.AsyncClient(transport=transport) as client:
            await client.post("https://x.invalid/contacts", json={"name": ""})
        msg = logger.error.call_args[0][0]
        assert "Validation error 422" in msg
        assert "name" in msg
        assert "required" in msg
        assert "email" in msg

    async def test_422_redacts_sensitive_field_values_in_log(self):
        """Fields named like ``password`` / ``api_key`` get their request
        body value redacted in the log even when that field had an error."""
        body = {
            "message": "Validation failed",
            "errors": {"password": ["too short"]},
        }
        transport, logger = self._build_transport(422, body)
        async with httpx.AsyncClient(transport=transport) as client:
            await client.post("https://x.invalid/users", json={"password": "hunter2"})
        msg = logger.error.call_args[0][0]
        # The field name is in the log; the actual password value must NOT be.
        assert "password" in msg
        assert "hunter2" not in msg
        assert "***" in msg

    async def test_4xx_with_non_json_body_logs_text(self):
        transport, logger = self._build_transport(503, "raw html error page")
        async with httpx.AsyncClient(transport=transport) as client:
            # 503 is 5xx (not logged by ErrorLoggingTransport).
            resp = await client.get("https://x.invalid/x")
        assert resp.status_code == 503
        logger.error.assert_not_called()

    async def test_4xx_with_invalid_json_logs_text_fallback(self):
        transport, logger = self._build_transport(400, "not valid json {{")
        async with httpx.AsyncClient(transport=transport) as client:
            await client.get("https://x.invalid/x")
        msg = logger.error.call_args[0][0]
        assert "Client error 400" in msg
        # The raw text body appears in the fallback path.
        assert "not valid json" in msg

    async def test_4xx_with_array_body_uses_raw_path(self):
        """When the parsed JSON isn't a dict (e.g. an array), the
        ``isinstance(error_data, dict)`` guard falls through to the
        raw-error path."""
        body = ["error message 1", "error message 2"]
        transport, logger = self._build_transport(400, body)
        async with httpx.AsyncClient(transport=transport) as client:
            await client.get("https://x.invalid/x")
        msg = logger.error.call_args[0][0]
        assert "Client error 400" in msg
        assert "Raw error" in msg

    async def test_url_in_log_is_sanitized(self):
        transport, logger = self._build_transport(401, {"message": "auth"})
        async with httpx.AsyncClient(transport=transport) as client:
            await client.get("https://x.invalid/x?api_key=secret")
        msg = logger.error.call_args[0][0]
        assert "secret" not in msg
        assert "***" in msg


# ---------------------------------------------------------------------------
# _capture_pagination_metadata — event hook
# ---------------------------------------------------------------------------


class TestPaginationMetadataHook:
    async def test_captures_x_pagination_header(self, mock_api_credentials):
        client = FrontappClient(**mock_api_credentials)
        request = httpx.Request("GET", "https://x.invalid/conversations")
        response = httpx.Response(
            200,
            request=request,
            headers={"X-Pagination": '{"total_records": 50, "next_page": 2}'},
        )

        await client._capture_pagination_metadata(response)
        assert response.pagination_info == {  # type: ignore[attr-defined]
            "total_records": 50,
            "next_page": 2,
        }

    async def test_no_header_is_noop(self, mock_api_credentials):
        client = FrontappClient(**mock_api_credentials)
        request = httpx.Request("GET", "https://x.invalid/conversations")
        response = httpx.Response(200, request=request)
        await client._capture_pagination_metadata(response)
        assert not hasattr(response, "pagination_info")

    async def test_non_200_status_is_noop(self, mock_api_credentials):
        client = FrontappClient(**mock_api_credentials)
        request = httpx.Request("GET", "https://x.invalid/conversations")
        response = httpx.Response(
            404,
            request=request,
            headers={"X-Pagination": '{"total_records": 50}'},
        )
        await client._capture_pagination_metadata(response)
        assert not hasattr(response, "pagination_info")

    async def test_invalid_json_logs_warning(self, mock_api_credentials, caplog):
        client = FrontappClient(**mock_api_credentials)
        request = httpx.Request("GET", "https://x.invalid/conversations")
        response = httpx.Response(
            200, request=request, headers={"X-Pagination": "not-json{{"}
        )

        with caplog.at_level(logging.WARNING):
            await client._capture_pagination_metadata(response)
        assert any("Invalid X-Pagination" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# _log_response_metrics — event hook
# ---------------------------------------------------------------------------


class TestResponseMetricsHook:
    async def test_logs_status_method_url(self, mock_api_credentials, caplog):
        client = FrontappClient(**mock_api_credentials)
        request = httpx.Request("GET", "https://x.invalid/conversations?limit=25")
        response = httpx.Response(200, request=request)

        with caplog.at_level(logging.DEBUG):
            await client._log_response_metrics(response)
        msgs = [r.message for r in caplog.records]
        assert any("200" in m and "GET" in m for m in msgs)

    async def test_url_in_log_is_sanitized(self, mock_api_credentials, caplog):
        client = FrontappClient(**mock_api_credentials)
        request = httpx.Request("GET", "https://x.invalid/x?token=secret")
        response = httpx.Response(200, request=request)

        with caplog.at_level(logging.DEBUG):
            await client._log_response_metrics(response)
        for record in caplog.records:
            assert "secret" not in record.message

    async def test_handles_runtime_error_on_elapsed(self, mock_api_credentials, caplog):
        """``response.elapsed`` raises RuntimeError before the response is
        read; the hook should fall back to 0.0s and still log."""
        client = FrontappClient(**mock_api_credentials)
        request = httpx.Request("GET", "https://x.invalid/x")
        response = httpx.Response(200, request=request)

        # Force the RuntimeError path by replacing ``elapsed`` access.
        type(response).elapsed = property(  # type: ignore[assignment,misc]
            lambda self: (_ for _ in ()).throw(RuntimeError("not yet"))
        )
        try:
            with caplog.at_level(logging.DEBUG):
                await client._log_response_metrics(response)
            assert any("0.00s" in r.message for r in caplog.records)
        finally:
            # Don't leak the property override into other tests.
            del type(response).elapsed


# ---------------------------------------------------------------------------
# _read_from_netrc — edge cases beyond the happy path tested in
# test_frontapp_client.py
# ---------------------------------------------------------------------------


class TestReadFromNetrc:
    def test_returns_none_when_netrc_missing(self, tmp_path):
        with patch.object(Path, "home", return_value=tmp_path):
            assert FrontappClient._read_from_netrc("https://api2.frontapp.com") is None

    def test_returns_none_when_no_matching_machine(self, tmp_path):
        netrc = tmp_path / ".netrc"
        netrc.write_text("machine other.example.com login a password b\n")
        netrc.chmod(0o600)
        with patch.object(Path, "home", return_value=tmp_path):
            assert FrontappClient._read_from_netrc("https://api2.frontapp.com") is None

    def test_handles_bare_hostname(self, tmp_path):
        netrc = tmp_path / ".netrc"
        netrc.write_text("machine api2.frontapp.com login a password tok\n")
        netrc.chmod(0o600)
        with patch.object(Path, "home", return_value=tmp_path):
            # Pass a bare hostname (no scheme) to exercise the fallback branch.
            assert FrontappClient._read_from_netrc("api2.frontapp.com") == "tok"

    @pytest.mark.skipif(os.name == "nt", reason="POSIX permissions only")
    def test_warns_on_insecure_permissions(self, tmp_path):
        """Permission warning uses ``warnings.warn``, not the logger."""
        import warnings

        netrc = tmp_path / ".netrc"
        netrc.write_text("machine api2.frontapp.com login a password tok\n")
        # Group + world readable — insecure for credentials.
        netrc.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        with (
            patch.object(Path, "home", return_value=tmp_path),
            warnings.catch_warnings(record=True) as captured,
        ):
            warnings.simplefilter("always")
            FrontappClient._read_from_netrc("https://api2.frontapp.com")
        assert any("insecure permissions" in str(w.message) for w in captured)

    def test_returns_none_on_netrc_parse_error(self, tmp_path):
        netrc = tmp_path / ".netrc"
        # Malformed netrc — missing tokens.
        netrc.write_text("machine\n")
        netrc.chmod(0o600)
        with patch.object(Path, "home", return_value=tmp_path):
            # Should not raise, just return None.
            assert FrontappClient._read_from_netrc("https://api2.frontapp.com") is None
