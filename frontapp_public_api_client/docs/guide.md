# FrontappClient Guide

The **FrontappClient** is the Python client for Front's
[Core API](https://dev.frontapp.com/reference/introduction). It extends
`openapi-python-client`'s generated `AuthenticatedClient` with an httpx transport stack
that adds automatic retries, rate-limit awareness, and log sanitization — every endpoint
inherits these for free.

The Core API is large — 139 paths and 233 operations spanning conversations, messages,
contacts, teammates, tags, inboxes, channels, rules, analytics, and more. This client
exposes **all** of them via the generated `client.api.<tag>.<operation>` surface, plus
hand-written ergonomic helpers for the most-used resources.

## Installation

```bash
pip install frontapp-openapi-client
```

```bash
# .env
FRONTAPP_API_KEY=your-api-key-here
FRONTAPP_BASE_URL=https://api2.frontapp.com  # optional
```

Get an API token at **Front → Settings → Developers → API tokens**.

## Quick Start

```python
import asyncio
from frontapp_public_api_client import FrontappClient

async def main():
    async with FrontappClient() as client:
        # High-level helper: returns Pydantic Conversation domain models
        convs = await client.conversations.list(q="status:open", limit=25)
        for c in convs:
            assignee = c.assignee.username if c.assignee else "unassigned"
            print(f"{c.id}: {c.subject!r} — {c.status} ({assignee})")

asyncio.run(main())
```

The helper methods on `client.conversations` return hand-written Pydantic domain models
(see `domain/conversation.py`). For resources that don't yet have a helper, call the
generated API modules directly and pass `client` through:

```python
from frontapp_public_api_client import FrontappClient
from frontapp_public_api_client.api.contacts import list_contacts
from frontapp_public_api_client.utils import unwrap

async with FrontappClient() as client:
    response = await list_contacts.asyncio_detailed(client=client, limit=25)
    parsed = unwrap(response)
    contacts = getattr(parsed, "field_results", None) or []  # list of ContactResponse (attrs)
```

## Available helpers today

| Helper                 | Status     | Covers                                                               |
| ---------------------- | ---------- | -------------------------------------------------------------------- |
| `client.conversations` | ✅ shipped | list/get/search/update/reply/list_messages/list_comments/add_comment |
| `client.contacts`      | ⏳ planned | See issue tracker                                                    |
| `client.messages`      | ⏳ planned | See issue tracker                                                    |
| `client.tags`          | ⏳ planned | See issue tracker                                                    |
| `client.inboxes`       | ⏳ planned | See issue tracker                                                    |
| `client.teammates`     | ⏳ planned | See issue tracker                                                    |

Anything without a helper is still fully usable via the generated API layer.

## Authentication

The client resolves the API token in this order:

1. `api_key=` constructor argument
2. `FRONTAPP_API_KEY` environment variable (including `.env` via python-dotenv)
3. `~/.netrc` entry matching the base-URL hostname:

```
machine api2.frontapp.com
password your-api-token-here
```

Run `chmod 600 ~/.netrc` to keep the file private; the client warns if permissions are
looser.

## Resilience

Every call through `FrontappClient` automatically gets:

### Retries

| Trigger               | Retried?                          |
| --------------------- | --------------------------------- |
| Network errors        | Yes (exponential backoff)         |
| 429 Too Many Requests | Yes — all methods, including POST |
| 502 / 503 / 504       | Yes — idempotent methods only     |
| Other 4xx             | No                                |

```python
async with FrontappClient(max_retries=5) as client:
    # POST/PATCH retry on 429; GET/PUT/DELETE retry on 429 + 5xx
    ...
```

POST/PATCH are retried on 429 because rate-limit responses mean the request **was not
processed** — retrying is safe, and Front's bulk-mutation endpoints especially benefit
from the automatic backoff.

### Rate-limit awareness

Front enforces per-endpoint rate limits. When a response includes a `Retry-After` header
the client honors it; otherwise retries fall back to exponential backoff.

### Cursor-token pagination

Front uses cursor-based pagination: list responses include `_pagination.next` as a full
URL. Pass the `page_token` query parameter back to the list endpoint to fetch the next
page. The helpers on `client.conversations` accept `limit=` and `page_token=` directly.
Full auto-pagination (walk all pages) is on the roadmap.

### Sensitive-data redaction

The client scrubs `Authorization` headers and any field matching common secret patterns
(`api_key`, `password`, `token`, etc.) from structured log output.

## Response Handling

Use the helpers in `frontapp_public_api_client.utils` instead of writing status-code
checks by hand.

```python
from frontapp_public_api_client.utils import (
    unwrap,
    unwrap_as,
    unwrap_data,
    is_success,
)
```

| Helper        | When to use                                                         |
| ------------- | ------------------------------------------------------------------- |
| `unwrap`      | Single-object response; raises typed exception on 4xx/5xx           |
| `unwrap_as`   | Same but asserts the parsed body is a specific type                 |
| `unwrap_data` | Wrapped list responses with a `.data` field                         |
| `is_success`  | 2xx check for POST/PATCH endpoints that return 202/204 with no body |

Front paginated list responses use `_results` which the generator renames to
`field_results` — so the typical unwrap looks like:

```python
parsed = unwrap(response)
results = getattr(parsed, "field_results", None) or []
```

Typed exceptions raised by `unwrap()`:

| Exception             | HTTP Status                    |
| --------------------- | ------------------------------ |
| `AuthenticationError` | 401                            |
| `ValidationError`     | 422                            |
| `RateLimitError`      | 429                            |
| `ServerError`         | 5xx                            |
| `APIError`            | other 4xx (400, 403, 404, ...) |

Unlike some APIs, Front does not ship a single canonical `ErrorResponse` schema — error
bodies vary per endpoint. `unwrap()` dispatches on HTTP status rather than by parsed
type, and stores the attrs/dict payload on `error.error_response` as `Any` for
inspection.

```python
from frontapp_public_api_client import FrontappClient
from frontapp_public_api_client.api.conversations import get_conversation_by_id
from frontapp_public_api_client.models.conversation_response import ConversationResponse
from frontapp_public_api_client.utils import unwrap_as, ValidationError

async with FrontappClient() as client:
    try:
        response = await get_conversation_by_id.asyncio_detailed(
            client=client, conversation_id="cnv_abc"
        )
        conv = unwrap_as(response, ConversationResponse)
        print(conv.subject, conv.status)
    except ValidationError as e:
        print("Validation failed:", e.validation_errors)
```

## Domain Models

Hand-written Pydantic models live in `frontapp_public_api_client.domain`:

- `Conversation`, `TeammateSummary`, `TagSummary`, `RecipientSummary`,
  `ConversationPageCursor`
- `FrontappBaseModel` (frozen, ignores unknown fields)

These are separate from the generated attrs models and are intended for business-logic
code, validation, and ETL. Front timestamps are unix-seconds floats on the wire; domain
models expose them as `AwareDatetime` via `field_validator`.

Convert between attrs and Pydantic / `None` representations with helpers in
`frontapp_public_api_client.domain.converters`:

- `unwrap_unset(value, default)` — unwrap `UNSET` / `None` to a default.
- `to_unset(value)` — convert `None` to `UNSET` when building a request.

## Common Workflows

### List conversations with Front search syntax

```python
async with FrontappClient() as client:
    urgent_open = await client.conversations.list(
        q="status:open tag:urgent",
        limit=50,
    )
    for c in urgent_open:
        print(f"{c.id}: {c.subject!r}")
```

### Read a conversation's messages

```python
async with FrontappClient() as client:
    msgs = await client.conversations.list_messages("cnv_abc", limit=10)
    for m in msgs:
        # m is the generated MessageResponse attrs model; call .to_dict() for JSON
        d = m.to_dict()
        print(d.get("body", "")[:80])
```

### Reply to a conversation

```python
async with FrontappClient() as client:
    response = await client.conversations.reply(
        "cnv_abc",
        body="Thanks for reaching out — we're looking into it now.",
        author_id="tea_xyz",  # optional; defaults to the token owner
    )
    # Front returns 202 Accepted; the message is enqueued.
    assert response.status_code == 202
```

### Archive + retag a conversation

```python
async with FrontappClient() as client:
    response = await client.conversations.update(
        "cnv_abc",
        status="archived",
        tag_ids=["tag_resolved"],
    )
    assert response.status_code in (200, 204)
```

### Raw generated API for uncovered resources

For resources without a helper yet (contacts, tags, messages, etc.), use the generated
API directly:

```python
from frontapp_public_api_client import FrontappClient
from frontapp_public_api_client.api.contacts import (
    list_contacts, get_contact, update_contact,
)
from frontapp_public_api_client.utils import unwrap, unwrap_as

async with FrontappClient() as client:
    # List
    response = await list_contacts.asyncio_detailed(client=client, limit=25)
    parsed = unwrap(response)
    contacts = getattr(parsed, "field_results", None) or []

    # Get by id
    from frontapp_public_api_client.models.contact_response import ContactResponse
    response = await get_contact.asyncio_detailed(
        client=client, contact_id="crd_abc"
    )
    contact = unwrap_as(response, ContactResponse)
```

## Configuration Reference

| Constructor arg  | Default                     | Notes                                                    |
| ---------------- | --------------------------- | -------------------------------------------------------- |
| `api_key`        | env / `.env` / netrc        | Raises if not resolvable                                 |
| `base_url`       | `https://api2.frontapp.com` | Or `FRONTAPP_BASE_URL` env var                           |
| `timeout`        | `30.0`                      | Per-request seconds                                      |
| `max_retries`    | `5`                         | Retry attempts before giving up                          |
| `max_pages`      | `100`                       | Cap on paginated walks (where supported)                 |
| `logger`         | module logger               | Any logger with `debug/info/warning/error`               |
| `**httpx_kwargs` | —                           | Forwarded to the transport (http2, limits, verify, cert) |
