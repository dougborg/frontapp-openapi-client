"""Base class for resource helpers.

Provides the ``FrontappClient`` reference plus the shared auto-pagination
machinery (``_paginate`` + ``extract_page_token``) used by every helper's
``iter_*`` methods.

ADR-003 documents the rationale: helper-layer iteration (not transport
rewriting) so we don't pay the JSON-parse-twice cost. ``_paginate`` walks
Front's cursor-based pagination by reading ``_pagination.next`` off each
response and feeding the extracted ``page_token`` back to the next call.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from frontapp_public_api_client.frontapp_client import FrontappClient


def extract_page_token(next_url: str | None) -> str | None:
    """Pull the ``page_token`` query param out of Front's next-page URL.

    Front returns the next page as a full URL in ``_pagination.next`` (e.g.
    ``https://api2.frontapp.com/conversations?page_token=abc123&limit=50``).
    Returns ``None`` for missing/empty/malformed URLs.
    """
    if not next_url:
        return None
    try:
        query = urlparse(next_url).query
        tokens = parse_qs(query).get("page_token", [])
        return tokens[0] if tokens else None
    except (ValueError, IndexError):
        return None


class Base:
    """Base class for all resource helpers.

    Holds the ``FrontappClient`` reference and provides ``_paginate`` —
    the shared auto-pagination iterator that resource helpers' ``iter_*``
    methods wrap.

    Args:
        client: The FrontappClient instance to use for API calls.
    """

    def __init__(self, client: FrontappClient) -> None:
        """Initialize with a client instance."""
        self._client = client

    async def _paginate(
        self,
        endpoint_call: Callable[..., Awaitable[Any]],
        *,
        projector: Callable[[Any], Any] | None = None,
        max_items: int | None = None,
        max_pages: int | None = None,
        **request_kwargs: Any,
    ) -> AsyncIterator[Any]:
        """Walk Front's cursor pagination and yield each item.

        Args:
            endpoint_call: A generated ``asyncio_detailed`` function for a
                paginated list endpoint. Must accept ``client=`` and the
                ``page_token`` query param.
            projector: Optional ``(attrs_item) -> projected`` callable
                applied to each item before yielding (typically
                ``Conversation.model_validate(item.to_dict())``). When
                ``None`` the raw attrs items are yielded.
            max_items: Stop after yielding this many items (yields a
                partial final page rather than fetching more). ``None``
                means no per-iterator limit.
            max_pages: Stop after this many page fetches. Falls back to
                the legacy ``FrontappClient(max_pages=...)`` setting when
                present, otherwise defaults to 100.
            **request_kwargs: Forwarded to every ``endpoint_call`` invocation
                (q, limit, path-id args, etc.). ``client=`` and
                ``page_token=`` are managed internally — don't pass them.

        Yields:
            Each item from ``field_results`` across all walked pages, in
            order, with ``projector`` applied (if provided).
        """
        from frontapp_public_api_client.utils import unwrap

        if max_pages is None:
            # Fallback to the client-level cap if it has one (legacy behavior),
            # otherwise default to 100. The cast keeps pyright narrow since
            # getattr returns Any.
            max_pages = cast(int, getattr(self._client, "max_pages", 100))
        logger = getattr(self._client, "logger", None)

        request_kwargs.pop("client", None)
        request_kwargs.pop("page_token", None)

        page_token: str | None = None
        page_count = 0
        yielded = 0

        while True:
            page_count += 1
            kwargs = dict(request_kwargs)
            kwargs["client"] = self._client
            if page_token is not None:
                kwargs["page_token"] = page_token

            response = await endpoint_call(**kwargs)
            parsed = unwrap(response)
            results = list(getattr(parsed, "field_results", None) or [])

            page_yielded = 0
            for item in results:
                if max_items is not None and yielded >= max_items:
                    break
                yield projector(item) if projector else item
                yielded += 1
                page_yielded += 1

            pagination = getattr(parsed, "field_pagination", None)
            next_url = (
                getattr(pagination, "next_", None) if pagination is not None else None
            )
            if isinstance(next_url, str):
                next_token = extract_page_token(next_url)
            else:
                next_token = None

            at_max_items = max_items is not None and yielded >= max_items
            at_max_pages = page_count >= max_pages
            # An empty page with a non-null cursor would otherwise infinite-loop
            # (Front shouldn't do this, but observed in practice with rapidly-
            # mutating filters). Treat it as terminal — better to under-fetch
            # than drain the rate limit.
            empty_page = not results
            no_more_pages = next_token is None or empty_page

            if logger is not None:
                if no_more_pages or at_max_items or at_max_pages:
                    reason = (
                        "max_items"
                        if at_max_items
                        else "max_pages"
                        if at_max_pages
                        else "empty_page_with_cursor"
                        if empty_page and next_token is not None
                        else "final"
                    )
                    logger.debug(
                        "Auto-pagination: page %d yielded %d items (%s); "
                        "yielded %d total across %d pages",
                        page_count,
                        page_yielded,
                        reason,
                        yielded,
                        page_count,
                    )
                else:
                    logger.debug(
                        "Auto-pagination: page %d yielded %d items (continuing)",
                        page_count,
                        page_yielded,
                    )

            if at_max_items or at_max_pages or no_more_pages:
                return

            page_token = next_token
