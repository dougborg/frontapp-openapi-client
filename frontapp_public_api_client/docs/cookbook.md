# FrontappClient Cookbook

Focused recipes for common Frontapp workflows. See the [guide](guide.md) for the
conceptual overview.

## List open conversations updated in the last 7 days

```python
import asyncio
from datetime import date, timedelta

from frontapp_public_api_client import FrontappClient

async def main():
    since = (date.today() - timedelta(days=7)).isoformat()

    async with FrontappClient() as client:
        convs = await client.conversations.list(
            q=f"status:open after:{since}",
            limit=100,
        )
    for c in convs:
        print(f"{c.updated_at} — {c.id} — {c.subject!r}")

asyncio.run(main())
```

## Find conversations by customer email

Front's search syntax doesn't support email-equality directly, but you can match against
subject / body text, or use the Contacts search:

```python
async with FrontappClient() as client:
    # Subject/body match
    convs = await client.conversations.search(
        query='customer@example.com', limit=25
    )

    # Or look up the contact first, then list their conversations
    # (contacts helper is on the roadmap — for now use the generated API)
    from frontapp_public_api_client.api.contacts import list_contacts
    from frontapp_public_api_client.utils import unwrap
    response = await list_contacts.asyncio_detailed(
        client=client, q="customer@example.com", limit=1
    )
    parsed = unwrap(response)
    results = getattr(parsed, "field_results", None) or []
```

## Walk a paginated list

```python
from frontapp_public_api_client import FrontappClient

async def collect_all_open(client: FrontappClient) -> list:
    all_convs = []
    page_token = None
    while True:
        batch = await client.conversations.list(
            q="status:open", limit=100, page_token=page_token
        )
        if not batch:
            break
        all_convs.extend(batch)
        # (Helper for extracting next-page token is on the roadmap — for now,
        # call the generated list_conversations directly to inspect
        # `_pagination.next` on the attrs response.)
        if len(batch) < 100:
            break
        page_token = _extract_next_token(...)  # TODO
    return all_convs
```

## Reply to a conversation

```python
from frontapp_public_api_client import FrontappClient

async with FrontappClient() as client:
    response = await client.conversations.reply(
        "cnv_abc",
        body="Thanks for reaching out — looking into this now.",
        # author_id optional; defaults to the token owner
    )
    # Front returns 202 Accepted; message is enqueued for delivery.
    assert response.status_code == 202
```

## Archive and retag in one call

```python
async with FrontappClient() as client:
    response = await client.conversations.update(
        "cnv_abc",
        status="archived",
        tag_ids=["tag_resolved", "tag_fulfilled"],
    )
    assert response.status_code in (200, 204)
```

## Add a teammate-only internal comment

```python
async with FrontappClient() as client:
    response = await client.conversations.add_comment(
        "cnv_abc",
        body="FYI: shipped from the secondary warehouse, not the primary.",
        # author_id optional
    )
    assert response.status_code == 201
```

Internal comments never reach the customer; use `reply` for outbound messages.

## Look up teammates and inboxes

Until `client.teammates` / `client.inboxes` helpers ship, use the generated API:

```python
from frontapp_public_api_client import FrontappClient
from frontapp_public_api_client.api.teammates import list_teammates
from frontapp_public_api_client.api.inboxes import list_inboxes
from frontapp_public_api_client.utils import unwrap

async with FrontappClient() as client:
    tm_response = await list_teammates.asyncio_detailed(client=client)
    teammates = getattr(unwrap(tm_response), "field_results", None) or []
    for t in teammates:
        print(t.id, t.username, t.email)

    ib_response = await list_inboxes.asyncio_detailed(client=client)
    inboxes = getattr(unwrap(ib_response), "field_results", None) or []
    for i in inboxes:
        print(i.id, i.name)
```

## Handle validation errors

```python
from frontapp_public_api_client.utils import ValidationError

try:
    ...
except ValidationError as e:
    print(f"422 from Front: {e}")
    # Front's validation responses aren't uniformly structured — the raw
    # parsed body is available on e.error_response for inspection.
    print("Raw:", e.error_response)
```

## Use `~/.netrc` instead of environment variables

```
# ~/.netrc
machine api2.frontapp.com
password your-api-token-here
```

```bash
chmod 600 ~/.netrc
```

The client will pick this up automatically if `FRONTAPP_API_KEY` is not set.

## Front search syntax reference

| Query               | Description                 |
| ------------------- | --------------------------- |
| `status:open`       | Open conversations          |
| `status:archived`   | Archived                    |
| `tag:urgent`        | Tagged urgent               |
| `assignee:me`       | Assigned to the token owner |
| `is:unassigned`     | Unassigned                  |
| `inbox:support`     | In a named inbox            |
| `after:2024-01-01`  | Updated after a date        |
| `before:2024-12-31` | Updated before a date       |

Combine with `AND` / `OR`: `status:open AND tag:urgent`.
