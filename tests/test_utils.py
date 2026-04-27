"""Tests for ``frontapp_public_api_client.utils`` — response unwrapping + typed errors.

The unwrap utilities are the boundary where every helper turns a
generated ``Response`` into either parsed data or a typed exception.
The dispatch happens by HTTP status code (per ADR-006), not by parsed
type — so these tests cover each branch of that dispatch matrix.
"""

from __future__ import annotations

from http import HTTPStatus
from types import SimpleNamespace
from typing import Any

import pytest

from frontapp_public_api_client.utils import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ServerError,
    ValidationError,
    get_error_message,
    handle_response,
    is_error,
    is_success,
    unwrap,
    unwrap_as,
    unwrap_data,
)


def _resp(status: int, parsed: Any) -> Any:
    """Build a minimal Response-like object with status_code + parsed.

    Uses ``HTTPStatus`` when the value is a defined member, otherwise the
    raw int — keeps tests against odd-but-valid 2xx codes (e.g. 299) working.
    """
    try:
        code: Any = HTTPStatus(status)
    except ValueError:
        code = status
    return SimpleNamespace(status_code=code, parsed=parsed)


# ---------------------------------------------------------------------------
# is_success / is_error
# ---------------------------------------------------------------------------


class TestStatusPredicates:
    @pytest.mark.parametrize("status", [200, 201, 202, 204, 299])
    def test_is_success_true_for_2xx(self, status):
        assert is_success(_resp(status, parsed={})) is True

    @pytest.mark.parametrize("status", [400, 401, 422, 429, 500, 502])
    def test_is_success_false_for_non_2xx(self, status):
        assert is_success(_resp(status, parsed={})) is False

    @pytest.mark.parametrize("status", [400, 401, 422, 429, 500, 502])
    def test_is_error_true_for_4xx_5xx(self, status):
        assert is_error(_resp(status, parsed={})) is True

    @pytest.mark.parametrize("status", [200, 201, 204, 301, 302])
    def test_is_error_false_for_2xx_3xx(self, status):
        assert is_error(_resp(status, parsed={})) is False


# ---------------------------------------------------------------------------
# unwrap — typed-error dispatch by status code
# ---------------------------------------------------------------------------


class TestUnwrap:
    def test_returns_parsed_on_2xx(self):
        body = {"id": "cnv_a"}
        result = unwrap(_resp(200, parsed=body))
        assert result is body

    def test_raises_authentication_error_on_401(self):
        with pytest.raises(AuthenticationError) as exc:
            unwrap(_resp(401, parsed=SimpleNamespace(message="bad token")))
        assert exc.value.status_code == 401
        assert "bad token" in str(exc.value)

    def test_raises_validation_error_on_422(self):
        parsed = SimpleNamespace(message="invalid", errors={"name": ["required"]})
        with pytest.raises(ValidationError) as exc:
            unwrap(_resp(422, parsed=parsed))
        assert exc.value.status_code == 422
        assert exc.value.validation_errors == {"name": ["required"]}

    def test_validation_error_str_includes_field_errors(self):
        parsed = SimpleNamespace(
            message="invalid",
            errors={"name": ["required"], "email": ["bad format", "too long"]},
        )
        with pytest.raises(ValidationError) as exc:
            unwrap(_resp(422, parsed=parsed))
        formatted = str(exc.value)
        assert "name: required" in formatted
        assert "email: bad format; too long" in formatted

    def test_raises_rate_limit_error_on_429(self):
        with pytest.raises(RateLimitError) as exc:
            unwrap(_resp(429, parsed=SimpleNamespace(message="slow down")))
        assert exc.value.status_code == 429

    @pytest.mark.parametrize("status", [500, 502, 503, 504])
    def test_raises_server_error_on_5xx(self, status):
        with pytest.raises(ServerError) as exc:
            unwrap(_resp(status, parsed=SimpleNamespace(message="oops")))
        assert exc.value.status_code == status

    @pytest.mark.parametrize("status", [400, 403, 404, 409])
    def test_raises_generic_api_error_on_other_4xx(self, status):
        with pytest.raises(APIError) as exc:
            unwrap(_resp(status, parsed=SimpleNamespace(message="nope")))
        assert exc.value.status_code == status
        # Not a more-specific subclass.
        assert not isinstance(
            exc.value,
            (AuthenticationError, ValidationError, RateLimitError, ServerError),
        )

    def test_raises_when_parsed_is_none_and_raise_on_error(self):
        with pytest.raises(APIError) as exc:
            unwrap(_resp(404, parsed=None))
        assert "No parsed response data" in str(exc.value)

    def test_returns_none_when_parsed_is_none_and_no_raise(self):
        assert unwrap(_resp(404, parsed=None), raise_on_error=False) is None

    def test_returns_none_for_error_when_no_raise(self):
        assert (
            unwrap(_resp(429, parsed=SimpleNamespace()), raise_on_error=False) is None
        )

    def test_synthesizes_error_message_when_parsed_has_no_message(self):
        with pytest.raises(APIError) as exc:
            unwrap(_resp(403, parsed=SimpleNamespace()))
        assert "Front API returned status 403" in str(exc.value)

    def test_synthesizes_error_message_when_message_is_empty_string(self):
        """Empty string is falsy; treated the same as a missing attribute."""
        with pytest.raises(APIError) as exc:
            unwrap(_resp(403, parsed=SimpleNamespace(message="")))
        assert "Front API returned status 403" in str(exc.value)


# ---------------------------------------------------------------------------
# unwrap_as — type-asserted unwrap
# ---------------------------------------------------------------------------


class TestUnwrapAs:
    def test_returns_typed_value_when_match(self):
        class Foo:
            pass

        foo = Foo()
        result = unwrap_as(_resp(200, parsed=foo), Foo)
        assert result is foo

    def test_raises_type_error_on_mismatch(self):
        class Foo:
            pass

        with pytest.raises(TypeError, match="Expected Foo, got dict"):
            unwrap_as(_resp(200, parsed={}), Foo)

    def test_returns_none_when_no_raise_and_none_parsed(self):
        class Foo:
            pass

        assert unwrap_as(_resp(404, parsed=None), Foo, raise_on_error=False) is None


# ---------------------------------------------------------------------------
# unwrap_data — list-shape extraction
# ---------------------------------------------------------------------------


class TestUnwrapData:
    def test_returns_list_when_parsed_is_list(self):
        result = unwrap_data(_resp(200, parsed=[1, 2, 3]))
        assert result == [1, 2, 3]

    def test_extracts_data_attribute(self):
        result = unwrap_data(_resp(200, parsed=SimpleNamespace(data=["a", "b"])))
        assert result == ["a", "b"]

    def test_returns_default_when_parsed_is_none_no_raise(self):
        assert (
            unwrap_data(_resp(404, parsed=None), raise_on_error=False, default=[]) == []
        )

    def test_returns_default_on_error_when_no_raise(self):
        result = unwrap_data(
            _resp(429, parsed=SimpleNamespace()),
            raise_on_error=False,
            default=[1, 2],
        )
        assert result == [1, 2]

    def test_raises_on_error_by_default(self):
        with pytest.raises(RateLimitError):
            unwrap_data(_resp(429, parsed=SimpleNamespace(message="slow")))


# ---------------------------------------------------------------------------
# get_error_message
# ---------------------------------------------------------------------------


class TestGetErrorMessage:
    def test_returns_none_for_2xx(self):
        assert (
            get_error_message(_resp(200, parsed=SimpleNamespace(message="x"))) is None
        )

    def test_returns_none_when_parsed_is_none(self):
        assert get_error_message(_resp(404, parsed=None)) is None

    def test_returns_message_string_when_present(self):
        result = get_error_message(
            _resp(401, parsed=SimpleNamespace(message="bad token"))
        )
        assert result == "bad token"

    def test_returns_none_when_message_attribute_missing(self):
        assert get_error_message(_resp(401, parsed=SimpleNamespace())) is None

    def test_returns_none_when_message_is_empty_string(self):
        assert get_error_message(_resp(401, parsed=SimpleNamespace(message=""))) is None


# ---------------------------------------------------------------------------
# handle_response — callback-style dispatch
# ---------------------------------------------------------------------------


class TestHandleResponse:
    def test_calls_on_success_with_parsed_data(self):
        body = {"id": "cnv_a"}
        result = handle_response(
            _resp(200, parsed=body), on_success=lambda d: ("ok", d)
        )
        assert result == ("ok", body)

    def test_returns_data_when_no_on_success(self):
        body = {"id": "cnv_a"}
        result = handle_response(_resp(200, parsed=body))
        assert result is body

    def test_calls_on_error_for_4xx(self):
        result = handle_response(
            _resp(404, parsed=SimpleNamespace(message="not found")),
            on_error=lambda e: ("err", e.status_code),
        )
        assert result == ("err", 404)

    def test_returns_none_on_error_when_no_callback(self):
        assert handle_response(_resp(404, parsed=SimpleNamespace())) is None

    def test_raises_when_raise_on_error_true(self):
        with pytest.raises(APIError):
            handle_response(
                _resp(429, parsed=SimpleNamespace(message="slow")),
                raise_on_error=True,
            )
