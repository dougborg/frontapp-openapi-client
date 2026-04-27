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

Every list helper has a sibling `iter_*` that walks Front's cursor pagination
automatically. The cursor plumbing (extract `_pagination.next`, feed the token back as
`page_token`, terminate on empty pages) is handled inside the client.

```python
from frontapp_public_api_client import FrontappClient

async with FrontappClient() as client:
    open_convs = []
    async for conv in client.conversations.iter_all(q="status:open"):
        open_convs.append(conv)

    # Cap the iterator to avoid unbounded fetches:
    async for conv in client.conversations.iter_all(
        q="status:open", max_items=500, max_pages=10
    ):
        ...
```

The same pattern works on every paginated helper: `client.contacts.iter_all`,
`client.tags.iter_all`, `client.inboxes.iter_all`, `client.teammates.iter_all`, etc.

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

## Draft a reply with a PDF attachment

The drafts vertical is the safe-by-default outbound path: an agent creates the draft
with attachments; the human reviews in Front's UI and clicks send.

```python
from frontapp_public_api_client import FileSpec, FrontappClient

async with FrontappClient() as client:
    draft = await client.drafts.create_reply(
        "cnv_abc",
        body="Updated proposal attached.",
        channel_id="cha_xyz",
        attachments=[
            FileSpec.from_path("/absolute/path/to/proposal.pdf"),
            # Construct directly when bytes already in memory:
            FileSpec(
                filename="cover-letter.txt",
                content=b"Hello team,\n\n...",
                mime_type="text/plain",
            ),
        ],
    )
    print(f"Draft {draft.id} created — review at https://app.frontapp.com")
```

When `attachments` is non-empty the helper bypasses the generated client and sends the
request as `multipart/form-data` (Front rejects binary content sent as JSON). When
`attachments` is `None` or empty, the standard JSON path is used. The same parameter
works on `client.drafts.create_on_channel`, `client.drafts.edit`,
`client.conversations.reply`, and `client.conversations.add_comment`.

## Download an attachment

`Attachment.url` (returned on every message attachment) is a fully-qualified download
URL on the workspace's own subdomain. The helper validates the host against the client's
`base_url` before sending the API token.

```python
async with FrontappClient() as client:
    msg = await client.messages.get("msg_abc")
    for attachment in msg.attachments:
        bytes_ = await client.attachments.download(attachment.url)
        Path(f"/tmp/{attachment.filename}").write_bytes(bytes_)
```

For large attachments, `client.attachments.stream(url)` yields 64 KiB chunks so you can
pipe them straight to disk without buffering the full payload.

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
