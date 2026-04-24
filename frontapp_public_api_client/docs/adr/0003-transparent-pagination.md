# ADR-003: Transparent Automatic Pagination

## Status

Accepted (partial — auto-pagination helper planned; manual cursor token support is live
today)

Date: 2026-04-24

## Context

Front's Core API uses **cursor-based pagination**. List responses include a
`_pagination` object with a `next` URL:

```json
{
  "_pagination": {
    "next": "https://api2.frontapp.com/conversations?page_token=ce787da6f075..."
  },
  "_links": { "self": "..." },
  "_results": [ ... ]
}
```

Callers extract the `page_token` query parameter from the `next` URL and pass it back to
the same endpoint on the next call. No page numbers, no `meta.total` — just a chain of
cursors until `_pagination.next` is `null`.

Characteristics:

- Default page size: 50 items
- Maximum page size: 100 items (per Front's docs)
- Cursor chains can be arbitrarily long for high-volume workspaces
- No built-in `Link` header — the cursor URL is in the JSON body

Callers need:

- A convenient way to paginate without re-extracting `page_token` manually on every
  iteration
- An opt-out for callers that want a specific page or a bounded window
- Safety limits so runaway loops don't drain rate limits

## Decision

Build pagination as a **two-tier feature**:

1. **Manual cursor support (live today)** — every list helper accepts `page_token=...`
   as a keyword argument. Callers extract it from `_pagination.next` themselves and pass
   it on the next call. This works for every paginated endpoint without special
   plumbing.

2. **Transparent auto-pagination (planned)** — an async-iterator helper on the client
   (`client.conversations.iter_all(q=..., max_items=500)`) that walks the cursor chain
   internally and yields items as they arrive. Will honor `pagination.max_pages` /
   `pagination.max_items` safety limits from the client config.

Both tiers use the same underlying helper signatures; the iterator just adds a loop. The
transport layer stays simple (no response rewriting) — pagination lives at the helper
layer where the response shape is known and cursor extraction is trivial.

### Manual cursor usage (today)

```python
async with FrontappClient() as client:
    page_token = None
    all_convs = []
    while True:
        batch = await client.conversations.list(
            q="status:open",
            limit=100,
            page_token=page_token,
        )
        if not batch:
            break
        all_convs.extend(batch)
        if len(batch) < 100:
            break  # last page
        # (A cursor-extract helper is planned; for now call the
        # generated list_conversations directly if you need the next token.)
```

### Auto-paginated iterator (planned)

```python
async with FrontappClient() as client:
    async for conv in client.conversations.iter_all(q="status:open"):
        ...   # yields Conversation domain models, bounded by max_pages/max_items
```

### Why not transport-layer aggregation?

A prior iteration of this ADR (from the template project this repo was seeded from)
implemented pagination inside the httpx transport stack — intercepting list responses,
walking the `Link` header chain, and stitching together aggregated responses. That
approach worked for the prior API's `Link`-header model but would fight Front's
cursor-in-JSON model because:

1. Extracting the cursor requires parsing `response.parsed`, which means parsing twice
   (once at the transport, once at the helper).
2. Rewriting responses so the generated attrs model looks "complete" requires
   synthesizing `_pagination.next = None`, which is spec abuse.
3. Async iteration is lost — the helper layer has to reconstruct it from the aggregated
   response instead of just yielding during the walk.
4. The LLM-context economy point is sharper: streaming items out as they arrive lets the
   MCP layer apply `max_items` naturally, whereas transport aggregation commits to
   materializing everything.

Helper-layer pagination matches Front's model and keeps the transport stack focused on
retries + rate-limit handling.

## Consequences

### Positive

1. **Simple transport layer**: no response rewriting or parse-twice
2. **Matches Front's model**: cursor-token chains translate directly to an async
   iterator
3. **Async-friendly**: iterator can yield items as they arrive, bounded by `max_items`
4. **Opt-out is free**: callers who want one page just call the non-iterator version
   with `limit=`
5. **Testable**: mocking a helper function is easier than mocking an httpx transport
   behavior

### Negative

1. **Per-resource work**: each helper needs its own iterator method. Mitigated by
   shipping them alongside the list method on every resource.
2. **Less magical**: callers have to call `iter_all` explicitly (vs. calling `.list()`
   and getting all pages transparently). We judge this to be _correct_ explicit behavior
   — the caller should know they're firing N API calls.

### Neutral

1. **Safety limits**: `max_pages` and `max_items` default to conservative values (100
   pages, unlimited items) — tune per workspace needs
2. **Today's state**: only manual `page_token` is live. The iterator is planned work;
   see issue tracker

## Alternatives considered

### Transport-layer auto-pagination (what the template had)

Intercept list responses in the httpx transport, walk Link headers or cursor chains,
aggregate into a single synthesized response.

**Rejected for Front** because the cursor lives in the JSON body (not headers) and
intercepting requires parsing `response.parsed`, which negates most of the
transport-layer-transparency benefit.

### Always auto-paginate; no opt-out

Every list call implicitly walks all pages.

**Rejected** because high-volume workspaces can have tens of thousands of conversations
— a `list_conversations()` call with no filters would fire hundreds of API requests
silently and consume significant rate limit. Explicit iteration is safer.

### Return a list wrapper type with lazy pagination

Return a `PaginatedList` object that lazy-loads pages on index access or iteration.

**Rejected** because async iteration is already the idiomatic Python form and doesn't
require a new lazy type. `PaginatedList[T]` adds API surface without clear benefit over
`async for item in iter_all(...)`.

### Rely on the raw `_pagination.next` URL

Skip token extraction entirely — accept `next_url: str | None` as the pagination
parameter.

**Rejected** because the URL contains the base URL and auth isn't carried in the URL —
callers would need to reconstruct request plumbing. Extracting `page_token` and passing
it back to the same method keeps the helper signature uniform.

## Implementation notes

### Current cursor-extraction helper

`helpers/conversations.py` includes `_extract_page_token(next_url)` as a local utility
for the planned iterator. It's a thin wrapper:

```python
def _extract_page_token(next_url: str | None) -> str | None:
    if not next_url:
        return None
    try:
        query = urlparse(next_url).query
        tokens = parse_qs(query).get("page_token", [])
        return tokens[0] if tokens else None
    except (ValueError, IndexError):
        return None
```

The same logic will go in `helpers/base.py` once we have multiple resources using
iteration.

### Safety limits (planned)

```python
class FrontappClient:
    def __init__(
        self,
        ...,
        max_pages: int = 100,
        max_items: int | None = None,
    ):
        ...
```

Used by the (planned) `iter_all` methods:

```python
async def iter_all(self, **kwargs) -> AsyncIterator[Conversation]:
    page_token: str | None = None
    pages_walked = 0
    items_yielded = 0
    while True:
        batch = await self.list(**kwargs, page_token=page_token)
        for item in batch:
            yield item
            items_yielded += 1
            if self._client.max_items is not None and items_yielded >= self._client.max_items:
                return
        pages_walked += 1
        if pages_walked >= self._client.max_pages:
            return
        page_token = _extract_page_token_from_response(...)
        if page_token is None:
            return
```

### Observability

Iteration logs at DEBUG level:

```
Auto-pagination: fetched page 1 (100 items, continuing)
Auto-pagination: fetched page 2 (100 items, continuing)
Auto-pagination: reached max_items=500, stopping
```

## References

- [ADR-001: Transport-Layer Resilience](0001-transport-layer-resilience.md) — retries
  live at the transport, pagination lives at the helper
- [ADR-006: Response Unwrapping Utilities](0006-response-unwrapping-utilities.md) —
  `unwrap(response)` + `getattr(..., "field_results")`
- [Front pagination docs](https://dev.frontapp.com/docs/pagination)
- [`helpers/conversations.py`](../../helpers/conversations.py) — current manual cursor
  support
