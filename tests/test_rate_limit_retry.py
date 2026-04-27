"""Tests for ``RateLimitAwareRetry`` — the load-bearing retry-policy contract.

Per ADR-001 and CLAUDE.md, the contract is:

- POST/PATCH retried on 429 (rate-limit response means "not processed")
- POST/PATCH NOT retried on 5xx (could have been processed; retry would
  duplicate the request)
- Idempotent methods (GET/HEAD/PUT/DELETE/OPTIONS/TRACE) retried on both
  429 and 5xx
- Status codes outside the forcelist are never retried
- ``increment()`` returns a new instance with the current method
  preserved (so the policy applies consistently across retry attempts)
"""

from __future__ import annotations

import pytest

from frontapp_public_api_client.frontapp_client import RateLimitAwareRetry


@pytest.fixture
def retry() -> RateLimitAwareRetry:
    """Build a RateLimitAwareRetry with the same config the FrontappClient uses."""
    return RateLimitAwareRetry(
        total=3,
        backoff_factor=1.0,
        respect_retry_after_header=True,
        status_forcelist=[429, 502, 503, 504],
        allowed_methods=[
            "HEAD",
            "GET",
            "PUT",
            "DELETE",
            "OPTIONS",
            "TRACE",
            "POST",
            "PATCH",
        ],
    )


# ---------------------------------------------------------------------------
# is_retryable_method — accepts everything in allowed_methods, stores method
# ---------------------------------------------------------------------------


class TestIsRetryableMethod:
    def test_post_in_allowed_methods_returns_true(self, retry):
        assert retry.is_retryable_method("POST") is True
        assert retry._current_method == "POST"

    def test_get_returns_true_and_stores_uppercase(self, retry):
        assert retry.is_retryable_method("get") is True
        assert retry._current_method == "GET"

    def test_unknown_method_returns_false(self, retry):
        # Configure a retry with a restrictive allowed_methods list
        restricted = RateLimitAwareRetry(
            total=3,
            status_forcelist=[429],
            allowed_methods=["GET"],
        )
        assert restricted.is_retryable_method("POST") is False


# ---------------------------------------------------------------------------
# is_retryable_status_code — the core matrix from ADR-001
# ---------------------------------------------------------------------------


class TestRetryMatrix:
    """The contract: 429 retries every method; 5xx only retries idempotent."""

    @pytest.mark.parametrize(
        "method,status,expected",
        [
            # 429 retries every method (rate-limit means "not processed")
            ("GET", 429, True),
            ("HEAD", 429, True),
            ("PUT", 429, True),
            ("DELETE", 429, True),
            ("OPTIONS", 429, True),
            ("TRACE", 429, True),
            ("POST", 429, True),
            ("PATCH", 429, True),
            # 5xx retries ONLY idempotent methods
            ("GET", 502, True),
            ("HEAD", 502, True),
            ("PUT", 503, True),
            ("DELETE", 504, True),
            ("OPTIONS", 502, True),
            ("TRACE", 503, True),
            # Non-idempotent methods do NOT retry on 5xx
            ("POST", 502, False),
            ("POST", 503, False),
            ("POST", 504, False),
            ("PATCH", 502, False),
            ("PATCH", 503, False),
            ("PATCH", 504, False),
        ],
    )
    def test_retry_matrix(self, retry, method, status, expected):
        # is_retryable_method primes _current_method (real RetryTransport flow).
        retry.is_retryable_method(method)
        assert retry.is_retryable_status_code(status) is expected, (
            f"{method} on {status} should {'retry' if expected else 'not retry'}"
        )

    def test_status_outside_forcelist_never_retries(self, retry):
        """200, 4xx (other than 429), and 1xx/3xx are not in status_forcelist."""
        retry.is_retryable_method("GET")
        for status in [200, 201, 204, 301, 302, 400, 401, 403, 404, 422]:
            assert retry.is_retryable_status_code(status) is False, (
                f"GET on {status} should not retry"
            )

    def test_no_method_known_falls_back_to_default(self, retry):
        """If is_retryable_method wasn't called first, behave permissively
        (parent's default)."""
        # Don't call is_retryable_method — _current_method is None
        retry._current_method = None
        # 502 is in forcelist; with no method known, returns True (parent default)
        assert retry.is_retryable_status_code(502) is True


# ---------------------------------------------------------------------------
# increment() — preserves _current_method across retry attempts
# ---------------------------------------------------------------------------


class TestIncrement:
    def test_increment_preserves_current_method(self, retry):
        retry.is_retryable_method("POST")
        assert retry._current_method == "POST"

        next_retry = retry.increment()
        assert next_retry._current_method == "POST"

    def test_increment_returns_new_instance(self, retry):
        """Each retry attempt gets its own instance (httpx-retries pattern)."""
        retry.is_retryable_method("GET")
        next_retry = retry.increment()
        assert next_retry is not retry

    def test_increment_returns_correct_subclass(self, retry):
        """``super().increment()`` cast to RateLimitAwareRetry — must
        return our subclass to keep the per-method dispatch working
        across retry chains."""
        retry.is_retryable_method("POST")
        next_retry = retry.increment()
        assert isinstance(next_retry, RateLimitAwareRetry)

    def test_method_preserved_across_chained_increments(self, retry):
        """Real retry chains call increment() repeatedly — every link
        must keep the original method so the 5xx-vs-429 dispatch stays
        consistent across attempts (without this, attempt #2 of a POST/5xx
        could silently switch to permissive mode)."""
        retry.is_retryable_method("POST")
        chain = retry.increment().increment().increment()
        assert chain._current_method == "POST"
        assert isinstance(chain, RateLimitAwareRetry)


# ---------------------------------------------------------------------------
# IDEMPOTENT_METHODS — class constant must include exactly the right set
# ---------------------------------------------------------------------------


class TestIdempotentMethodsConstant:
    def test_includes_standard_idempotent_methods(self):
        idempotent = RateLimitAwareRetry.IDEMPOTENT_METHODS
        for method in ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]:
            assert method in idempotent

    def test_excludes_non_idempotent_methods(self):
        idempotent = RateLimitAwareRetry.IDEMPOTENT_METHODS
        for method in ["POST", "PATCH", "CONNECT"]:
            assert method not in idempotent
