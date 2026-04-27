"""
FrontappClient - The pythonic Frontapp API client with automatic resilience.

This client uses httpx's native transport layer to provide automatic retries,
rate-limit handling, and detailed error logging for all API calls without
any decorators or wrapper methods needed. Pagination is handled at the
helper layer (see ``Base._paginate`` and ``client.<resource>.iter_all``).
"""

import contextlib
import json
import logging
import netrc
import os
from collections.abc import Awaitable, Callable
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import parse_qs, quote, urlencode, urlparse, urlunparse

if TYPE_CHECKING:
    from .helpers.attachments import Attachments
    from .helpers.contact_groups import ContactGroups
    from .helpers.contact_lists import ContactLists
    from .helpers.contacts import Contacts
    from .helpers.conversations import Conversations
    from .helpers.drafts import Drafts
    from .helpers.inboxes import Inboxes
    from .helpers.messages import Messages
    from .helpers.tags import Tags
    from .helpers.teammates import Teammates

import httpx
from dotenv import load_dotenv
from httpx import AsyncHTTPTransport
from httpx_retries import Retry, RetryTransport

from ._logging import Logger
from .client import AuthenticatedClient

# Patterns used to identify sensitive query parameters and body fields in logs.
# Values matching these patterns are redacted to prevent information disclosure.
# See also: frontapp_mcp_server/src/frontapp_mcp/logging.py filter_sensitive_data()
# for the MCP equivalent.
_SENSITIVE_PARAMS: frozenset[str] = frozenset(
    {
        "api_key",
        "auth",
        "authorization",
        "credential",
        "email",
        "key",
        "password",
        "secret",
        "token",
    }
)

_REDACTED = "***"


def _is_sensitive(name: str) -> bool:
    """Check if a parameter/field name matches any sensitive pattern."""
    lower = name.lower()
    return any(pattern in lower for pattern in _SENSITIVE_PARAMS)


def _sanitize_url(url: str) -> str:
    """Redact sensitive query parameter values from a URL for safe logging."""
    try:
        parsed = urlparse(url)
        if not parsed.query:
            return url
        params = parse_qs(parsed.query, keep_blank_values=True)
        sanitized = {}
        for k, values in params.items():
            if _is_sensitive(k):
                sanitized[k] = [_REDACTED]
            else:
                sanitized[k] = values
        # Use urlencode with custom quote function that preserves * characters
        clean_query = urlencode(
            sanitized,
            doseq=True,
            quote_via=lambda s, safe="", encoding=None, errors=None: quote(
                s, safe=safe + "*", encoding=encoding, errors=errors
            ),
        )
        return urlunparse(parsed._replace(query=clean_query))
    except Exception:
        # If URL parsing fails, strip the query string entirely
        base, _, _ = url.partition("?")
        return f"{base}?{_REDACTED}"


def _sanitize_body(body: Any) -> Any:
    """Redact sensitive field values from nested dict/list bodies for safe logging."""

    def _sanitize_value(value: Any) -> Any:
        """Recursively sanitize nested structures."""
        if isinstance(value, dict):
            return {
                k: _REDACTED if _is_sensitive(k) else _sanitize_value(v)
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [_sanitize_value(item) for item in value]
        return value

    if not isinstance(body, dict):
        return "[non-dict body]"
    return _sanitize_value(body)


class RateLimitAwareRetry(Retry):
    """
    Custom Retry class that allows non-idempotent methods (POST, PATCH) to be
    retried ONLY when receiving a 429 (Too Many Requests) status code.

    For all other retryable status codes (502, 503, 504), only idempotent methods
    (HEAD, GET, PUT, DELETE, OPTIONS, TRACE) will be retried.

    This ensures we don't accidentally retry non-idempotent operations after
    server errors, but we DO retry them when we're being rate-limited.
    """

    # Idempotent methods that are always safe to retry
    IDEMPOTENT_METHODS = frozenset(["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"])

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize and track the current request method."""
        super().__init__(*args, **kwargs)
        self._current_method: str | None = None

    def is_retryable_method(self, method: str) -> bool:
        """
        Allow all methods to pass through the initial check.

        Store the method for later use in is_retryable_status_code.
        """
        self._current_method = method.upper()
        # Accept all methods - we'll filter in is_retryable_status_code
        return self._current_method in self.allowed_methods

    def is_retryable_status_code(self, status_code: int) -> bool:
        """
        Check if a status code is retryable for the current method.

        For 429 (rate limiting), allow all methods.
        For other errors (502, 503, 504), only allow idempotent methods.
        """
        # First check if the status code is in the allowed list at all
        if status_code not in self.status_forcelist:
            return False

        # If we don't know the method, fall back to default behavior
        if self._current_method is None:
            return True

        # Rate limiting (429) - retry all methods
        if status_code == HTTPStatus.TOO_MANY_REQUESTS:
            return True

        # Other retryable errors - only retry idempotent methods
        return self._current_method in self.IDEMPOTENT_METHODS

    def increment(self) -> "RateLimitAwareRetry":
        """Return a new retry instance with the attempt count incremented."""
        # Call parent's increment which creates a new instance of our class
        new_retry = cast(RateLimitAwareRetry, super().increment())
        # Preserve the current method across retry attempts
        new_retry._current_method = self._current_method
        return new_retry


class ErrorLoggingTransport(AsyncHTTPTransport):
    """
    Transport layer that adds detailed error logging for 4xx client errors.

    This transport wraps another AsyncHTTPTransport and intercepts responses
    to log detailed error information using the generated error models.
    """

    def __init__(
        self,
        wrapped_transport: AsyncHTTPTransport | None = None,
        logger: Logger | None = None,
        **kwargs: Any,
    ):
        """
        Initialize the error logging transport.

        Args:
            wrapped_transport: The transport to wrap. If None, creates a new AsyncHTTPTransport.
            logger: Logger instance for capturing error details. If None, creates a default logger.
            **kwargs: Additional arguments passed to AsyncHTTPTransport if wrapped_transport is None.
        """
        super().__init__()
        if wrapped_transport is None:
            wrapped_transport = AsyncHTTPTransport(**kwargs)
        self._wrapped_transport = wrapped_transport
        self.logger: Logger = logger or logging.getLogger(__name__)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Handle request and log detailed error information for 4xx responses."""
        response = await self._wrapped_transport.handle_async_request(request)

        # Log detailed information for 400-level client errors
        if 400 <= response.status_code < 500:
            await self._log_client_error(response, request)

        return response

    async def _log_client_error(
        self, response: httpx.Response, request: httpx.Request
    ) -> None:
        """Log 4xx client errors.

        Frontapp returns either ``ErrorResponse`` ({"message": str}) or
        ``ValidationErrorResponse`` ({"message": str, "errors": {field: [str]}}).
        We log the untyped JSON since both shapes are simple enough to render
        directly without a dedicated typed model.
        """
        method = request.method
        url = _sanitize_url(str(request.url))
        status_code = response.status_code

        request_body: Any = None
        if request.content:
            with contextlib.suppress(
                json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError
            ):
                request_body = json.loads(request.content.decode("utf-8"))

        if hasattr(response, "aread"):
            with contextlib.suppress(TypeError, AttributeError):
                await response.aread()

        try:
            error_data = response.json()
        except (json.JSONDecodeError, TypeError, ValueError):
            self.logger.error(
                f"Client error {status_code} for {method} {url} - "
                f"Response: {getattr(response, 'text', '')[:500]}..."
            )
            return

        prefix = (
            f"Validation error 422 for {method} {url}"
            if status_code == 422
            else f"Client error {status_code} for {method} {url}"
        )

        if isinstance(error_data, dict):
            message = error_data.get("message") or "(not provided)"
            log_message = f"{prefix}\n  Error: {message}"

            errors = error_data.get("errors")
            if isinstance(errors, dict) and errors:
                log_message += f"\n  Validation errors ({len(errors)} fields):"
                for field, field_errors in errors.items():
                    sent_value = (
                        request_body.get(field)
                        if isinstance(request_body, dict)
                        else None
                    )
                    if sent_value is not None and _is_sensitive(str(field)):
                        sent_value = _REDACTED
                    log_message += f"\n    - {field}: {field_errors}"
                    if sent_value is not None:
                        log_message += f"\n      Sent: {sent_value!r}"
            self.logger.error(log_message)
        else:
            self.logger.error(f"{prefix}\n  Raw error: {_sanitize_body(error_data)}")


def ResilientAsyncTransport(
    max_retries: int = 5,
    logger: Logger | None = None,
    **kwargs: Any,
) -> RetryTransport:
    """
    Factory function that creates a chained transport with error logging
    and retry capabilities.

    This function chains three transport layers:
    1. AsyncHTTPTransport (base HTTP transport)
    2. ErrorLoggingTransport (logs detailed 4xx errors)
    3. RetryTransport (handles retries with Retry-After header support)

    Pagination is handled at the helper layer (``Base._paginate`` /
    ``client.<resource>.iter_all()``), not at the transport layer.

    Args:
        max_retries: Maximum number of retry attempts for failed requests. Defaults to 5.
        logger: Logger instance for capturing operations. If None, creates a default logger.
        **kwargs: Additional arguments passed to the base AsyncHTTPTransport.
            Common parameters include:
            - http2 (bool): Enable HTTP/2 support
            - limits (httpx.Limits): Connection pool limits
            - verify (bool | str | ssl.SSLContext): SSL certificate verification
            - cert (str | tuple): Client-side certificates
            - trust_env (bool): Trust environment variables for proxy configuration

    Returns:
        A RetryTransport instance wrapping all the layered transports.

    Note:
        When using a custom transport, parameters like http2, limits, and verify
        must be passed to this factory function (which passes them to the base
        AsyncHTTPTransport), not to the httpx.Client/AsyncClient constructor.

    Example:
        ```python
        transport = ResilientAsyncTransport(max_retries=3)
        async with httpx.AsyncClient(transport=transport) as client:
            response = await client.get("https://api.example.com/items")
        ```
    """
    resolved_logger: Logger = (
        logger if logger is not None else logging.getLogger(__name__)
    )

    # Build the transport chain from inside out:
    # 1. Base AsyncHTTPTransport
    base_transport = AsyncHTTPTransport(**kwargs)

    # 2. Wrap with error logging
    error_logging_transport = ErrorLoggingTransport(
        wrapped_transport=base_transport,
        logger=resolved_logger,
    )

    # Finally wrap with retry logic (outermost layer)
    # Use RateLimitAwareRetry which:
    # - Retries ALL methods (including POST/PATCH) for 429 rate limiting
    # - Retries ONLY idempotent methods for server errors (502, 503, 504)
    retry = RateLimitAwareRetry(
        total=max_retries,
        backoff_factor=1.0,  # Exponential backoff: 1, 2, 4, 8, 16 seconds
        respect_retry_after_header=True,  # Honor server's Retry-After header
        status_forcelist=[
            429,
            502,
            503,
            504,
        ],  # Status codes that should trigger retries
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
    retry_transport = RetryTransport(
        transport=error_logging_transport,
        retry=retry,
    )

    return retry_transport


class FrontappClient(AuthenticatedClient):
    """The pythonic Frontapp API client with automatic resilience.

    Inherits from ``AuthenticatedClient`` and can be passed directly to
    generated API methods without a ``.client`` property.

    Features:
    - Automatic retries on network errors and server errors (5xx)
    - Automatic rate-limit handling (parses ``Retry-After``, falls back to
      exponential backoff on 429 since Frontapp doesn't emit the header)
    - Rich logging and observability

    Pagination is handled at the helper layer — see ``client.<resource>.list``
    (manual cursor) and ``client.<resource>.iter_all`` (automatic walker)
    for the supported resources, or ``Base._paginate`` for the underlying
    cursor-token loop.

    Usage:
        async with FrontappClient() as client:
            # Preferred: use the helper
            convs = await client.conversations.list(q="status:open", limit=25)

            # Or call the generated API directly
            from frontapp_public_api_client.api.conversations import list_conversations
            response = await list_conversations.asyncio_detailed(
                client=client, q="status:open", limit=25
            )
    """

    @staticmethod
    def _read_from_netrc(base_url: str) -> str | None:
        """
        Read API key from ~/.netrc file.

        Args:
            base_url: The base URL to extract the hostname from.

        Returns:
            The API key (password field) from netrc, or None if not found.

        Note:
            The password field in netrc is used to store the API token since
            Frontapp API uses bearer token authentication, not HTTP Basic Auth.
        """
        try:
            # Extract hostname from base_url - handle both full URLs and bare hostnames
            parsed = urlparse(base_url)
            host: str | None = None

            if parsed.hostname:
                # URL with scheme (e.g., "https://api2.frontapp.com")
                host = parsed.hostname
            else:
                # Try parsing as URL without scheme (e.g., "api2.frontapp.com")
                parsed_with_scheme = urlparse(f"https://{base_url}")
                if parsed_with_scheme.hostname:
                    host = parsed_with_scheme.hostname
                else:
                    # Final fallback: treat as bare hostname (e.g., "api.example.com")
                    # Extract just the hostname part before any path
                    host = base_url.split("/")[0] if base_url else None

            # If we couldn't extract a valid hostname, return None
            if not host:
                return None

            netrc_path = Path.home() / ".netrc"
            if not netrc_path.exists():
                return None

            # Warn if .netrc is readable by group or others (POSIX only)
            if os.name != "nt":
                mode = netrc_path.stat().st_mode
                if mode & 0o077:
                    import warnings

                    warnings.warn(
                        f"~/.netrc has insecure permissions ({oct(mode & 0o777)}). "
                        "This may expose your API key. Run: chmod 600 ~/.netrc",
                        stacklevel=2,
                    )

            auth = netrc.netrc(str(netrc_path))
            authenticators = auth.authenticators(host)

            if authenticators:
                # Return password field (which contains our API token)
                # netrc returns (login, account, password)
                _login, _account, password = authenticators
                return password
        except (FileNotFoundError, netrc.NetrcParseError, OSError):
            # Silently ignore netrc errors - it's an optional source
            pass

        return None

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 5,
        logger: Logger | None = None,
        **httpx_kwargs: Any,
    ):
        """
        Initialize the Frontapp API client with automatic resilience features.

        Args:
            api_key: Frontapp API key. If None, will try to load from FRONTAPP_API_KEY env var,
                .env file, or ~/.netrc file (in that order).
            base_url: Base URL for the Frontapp API. Defaults to https://api2.frontapp.com
            timeout: Request timeout in seconds. Defaults to 30.0.
            max_retries: Maximum number of retry attempts for failed requests. Defaults to 5.
            logger: Any object whose debug/info/warning/error methods accept
                (msg, *args, **kwargs) — the standard logging.Logger call convention
                (e.g. logging.Logger, structlog.BoundLogger). If None, creates a
                default stdlib logger.
            **httpx_kwargs: Additional arguments passed to the base AsyncHTTPTransport.
                Common parameters include:
                - http2 (bool): Enable HTTP/2 support
                - limits (httpx.Limits): Connection pool limits
                - verify (bool | str | ssl.SSLContext): SSL certificate verification
                - cert (str | tuple): Client-side certificates
                - trust_env (bool): Trust environment variables for proxy configuration
                - event_hooks (dict): Custom event hooks (will be merged with built-in hooks)

        Raises:
            ValueError: If no API key is provided via api_key param, FRONTAPP_API_KEY env var,
                .env file, or ~/.netrc file.

        Note:
            Transport-related parameters (http2, limits, verify, etc.) are correctly
            passed to the innermost AsyncHTTPTransport layer, ensuring they take effect
            even with the layered transport architecture.

        Example:
            >>> async with FrontappClient() as client:
            ...     # All API calls through client get automatic resilience
            ...     response = await some_api_method.asyncio_detailed(client=client)
        """
        load_dotenv()

        # Handle backwards compatibility: accept 'token' kwarg as alias for 'api_key'
        if "token" in httpx_kwargs:
            if api_key is not None:
                raise ValueError("Cannot specify both 'api_key' and 'token' parameters")
            api_key = httpx_kwargs.pop("token")

        # Determine base_url early so we can use it for netrc lookup
        base_url = (
            base_url or os.getenv("FRONTAPP_BASE_URL") or "https://api2.frontapp.com"
        )

        # Setup credentials with priority: param > env (including .env) > netrc
        api_key = (
            api_key or os.getenv("FRONTAPP_API_KEY") or self._read_from_netrc(base_url)
        )

        if not api_key:
            raise ValueError(
                "API key required via: api_key param, FRONTAPP_API_KEY env var, "
                ".env file, or ~/.netrc"
            )

        self.logger: Logger = logger or logging.getLogger(__name__)

        # Warn if SSL verification is disabled — risk of MITM attacks
        if httpx_kwargs.get("verify") is False:
            self.logger.warning(
                "SSL certificate verification is disabled (verify=False). "
                "This exposes the connection to MITM attacks. "
                "Only use this for local development."
            )

        # Domain helper instances (lazy-loaded via properties)
        self._attachments: Attachments | None = None
        self._conversations: Conversations | None = None
        self._contacts: Contacts | None = None
        self._contact_lists: ContactLists | None = None
        self._contact_groups: ContactGroups | None = None
        self._drafts: Drafts | None = None
        self._messages: Messages | None = None
        self._tags: Tags | None = None
        self._inboxes: Inboxes | None = None
        self._teammates: Teammates | None = None

        # Extract client-level parameters that shouldn't go to the transport
        # Event hooks for observability - start with our defaults
        event_hooks: dict[str, list[Callable[[httpx.Response], Awaitable[None]]]] = {
            "response": [
                self._capture_pagination_metadata,
                self._log_response_metrics,
            ]
        }

        # Extract and merge user hooks
        user_hooks = httpx_kwargs.pop("event_hooks", {})
        for event, hooks in user_hooks.items():
            # Normalize to list and add to existing or create new event
            hook_list = cast(
                list[Callable[[httpx.Response], Awaitable[None]]],
                hooks if isinstance(hooks, list) else [hooks],
            )
            if event in event_hooks:
                event_hooks[event].extend(hook_list)
            else:
                event_hooks[event] = hook_list

        # Check if user wants to override the transport entirely
        custom_transport = httpx_kwargs.pop("transport", None) or httpx_kwargs.pop(
            "async_transport", None
        )

        if custom_transport:
            # User provided a custom transport, use it as-is
            transport = custom_transport
        else:
            # Separate transport-specific kwargs from client-specific kwargs
            # Client-specific params that should NOT go to the transport
            client_only_params = ["headers", "cookies", "params", "auth"]
            client_kwargs = {
                k: httpx_kwargs.pop(k)
                for k in list(httpx_kwargs.keys())
                if k in client_only_params
            }

            # Create resilient transport with remaining transport-specific httpx_kwargs
            # These will be passed to the base AsyncHTTPTransport (http2, limits, verify, etc.)
            transport = ResilientAsyncTransport(
                max_retries=max_retries,
                logger=self.logger,
                **httpx_kwargs,  # Pass through http2, limits, verify, cert, trust_env, etc.
            )

            # Put client-specific params back into httpx_kwargs for the parent class
            httpx_kwargs.update(client_kwargs)

        # Initialize the parent AuthenticatedClient
        super().__init__(
            base_url=base_url,
            token=api_key,
            timeout=httpx.Timeout(timeout),
            httpx_args={
                "transport": transport,
                "event_hooks": event_hooks,
                **httpx_kwargs,  # Include any remaining client-level kwargs
            },
        )

    # Remove the client property since we inherit from AuthenticatedClient
    # Users can now pass the FrontappClient instance directly to API methods

    # Domain properties for ergonomic access
    @property
    def attachments(self) -> "Attachments":
        """Ergonomic operations over Frontapp attachments — upload + download.

        Front's draft / message / comment endpoints accept binary attachments
        as ``multipart/form-data`` (the generated client misencodes this as
        JSON; see ``helpers.attachments`` for the multipart bypass). This
        helper also exposes ``download(url)`` and ``stream(url)`` for the
        five binary-download paths that ``scripts/vendor_spec.py`` strips
        from the spec.
        """
        from .helpers.attachments import Attachments

        if self._attachments is None:
            self._attachments = Attachments(self)
        return self._attachments

    @property
    def conversations(self) -> "Conversations":
        """Ergonomic operations over ``/conversations*`` endpoints."""
        from .helpers.conversations import Conversations

        if self._conversations is None:
            self._conversations = Conversations(self)
        return self._conversations

    @property
    def drafts(self) -> "Drafts":
        """Ergonomic operations over Frontapp's draft endpoints.

        Drafts are the safe-by-default outbound path: an agent creates the
        draft, the human reviews in Front, and the human clicks send. There
        is no programmatic ``send_draft`` — sending is human-in-the-loop.
        """
        from .helpers.drafts import Drafts

        if self._drafts is None:
            self._drafts = Drafts(self)
        return self._drafts

    @property
    def contacts(self) -> "Contacts":
        """Ergonomic operations over Frontapp's contacts surface.

        Spans three sibling generated tags (``contacts/``,
        ``contact_handles/``, ``contact_notes/``). Includes ``merge`` and
        the team-/teammate-scoped create/list paths.
        """
        from .helpers.contacts import Contacts

        if self._contacts is None:
            self._contacts = Contacts(self)
        return self._contacts

    @property
    def contact_lists(self) -> "ContactLists":
        """Ergonomic operations over Frontapp's contact-list surface.

        Contact lists are named buckets of contacts used for bulk
        operations (broadcasts, segmentation). Front exposes no
        ``GET /contact_lists/{id}`` or PATCH endpoint — lists can't be
        renamed once created. See helper docstring for the full list of
        quirks (workspace-scoped create defaults, 50-contact remove cap).
        """
        from .helpers.contact_lists import ContactLists

        if self._contact_lists is None:
            self._contact_lists = ContactLists(self)
        return self._contact_lists

    @property
    def contact_groups(self) -> "ContactGroups":
        """Ergonomic operations over Frontapp's deprecated contact-group surface.

        Front has deprecated all contact-group endpoints in favor of
        contact lists; the vertical exists for workspaces still using
        groups. Prefer ``client.contact_lists`` for new code.
        """
        from .helpers.contact_groups import ContactGroups

        if self._contact_groups is None:
            self._contact_groups = ContactGroups(self)
        return self._contact_groups

    @property
    def messages(self) -> "Messages":
        """Ergonomic operations over Frontapp's ``/messages/{id}`` surface.

        Read-side companion to the conversations and drafts verticals: get
        a message by id and manage seen receipts. Outbound replies live on
        ``client.drafts`` (preferred) or ``client.conversations.reply`` —
        not here.
        """
        from .helpers.messages import Messages

        if self._messages is None:
            self._messages = Messages(self)
        return self._messages

    @property
    def tags(self) -> "Tags":
        """Ergonomic operations over Frontapp's workspace tag surface.

        Covers the workspace tag catalog (``/tags*``) plus the
        conversation-tag delta endpoints. Use the delta methods
        (``apply_to_conversation`` / ``remove_from_conversation``) when
        you want to add or remove a single tag without clobbering the
        rest of the conversation's tag set.
        """
        from .helpers.tags import Tags

        if self._tags is None:
            self._tags = Tags(self)
        return self._tags

    @property
    def inboxes(self) -> "Inboxes":
        """Ergonomic operations over Frontapp's inbox surface.

        Covers the workspace inbox catalog (``/inboxes*``). Front exposes
        no general inbox PATCH — inbox name and visibility are immutable
        after creation; only access (``grant_access`` / ``revoke_access``)
        can be changed.
        """
        from .helpers.inboxes import Inboxes

        if self._inboxes is None:
            self._inboxes = Inboxes(self)
        return self._inboxes

    @property
    def teammates(self) -> "Teammates":
        """Ergonomic operations over Frontapp's teammate roster.

        Covers list / get / update + per-teammate inbox + assigned-
        conversation lookups. Email and admin status are read-only at
        this surface — managed via Front's admin UI.
        """
        from .helpers.teammates import Teammates

        if self._teammates is None:
            self._teammates = Teammates(self)
        return self._teammates

    # Event hooks for observability
    async def _capture_pagination_metadata(self, response: httpx.Response) -> None:
        """Capture and store pagination metadata from response headers."""
        if response.status_code == 200:
            x_pagination = response.headers.get("X-Pagination")
            if x_pagination:
                try:
                    pagination_info = json.loads(x_pagination)
                    self.logger.debug(f"Pagination metadata: {pagination_info}")
                    # Store pagination info for easy access
                    setattr(response, "pagination_info", pagination_info)  # noqa: B010
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid X-Pagination header: {x_pagination}")

    async def _log_response_metrics(self, response: httpx.Response) -> None:
        """Log response metrics for observability."""
        # Extract timing info if available (after response is read)
        try:
            if hasattr(response, "elapsed"):
                duration = response.elapsed.total_seconds()
            else:
                duration = 0.0
        except RuntimeError:
            # elapsed not available yet
            duration = 0.0

        self.logger.debug(
            f"Response: {response.status_code} {response.request.method} "
            f"{_sanitize_url(str(response.request.url))} ({duration:.2f}s)"
        )
