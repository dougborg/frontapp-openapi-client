"""MCP resource: tool reference and workflow guide for the Frontapp MCP server."""

from __future__ import annotations

from fastmcp import FastMCP

_HELP_MARKDOWN = """\
# Frontapp MCP Server — Tool Reference

## Conversations

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `list_conversations` | `GET /conversations` | Cursor-paginated list. Pass `q=` for Front search syntax. |
| `get_conversation` | `GET /conversations/{id}` | Full detail for one conversation. |
| `search_conversations` | `GET /conversations/search/{query}` | Front search syntax as the primary filter. |
| `list_conversation_messages` | `GET /conversations/{id}/messages` | Messages in a conversation (most recent first). |
| `list_conversation_comments` | `GET /conversations/{id}/comments` | Internal teammate comments on a conversation. |
| `reply_to_conversation` | `POST /conversations/{id}/messages` | Send outbound reply on the conversation's channel. Two-step confirm. |
| `update_conversation` | `PATCH /conversations/{id}` | Archive/reopen, reassign, retag, move inbox. Two-step confirm. |
| `add_conversation_comment` | `POST /conversations/{id}/comments` | Teammate-only internal note. Two-step confirm. |

## Front search syntax (`q=` parameter)

| Query                 | Description                 |
| --------------------- | --------------------------- |
| `status:open`         | Open conversations          |
| `status:archived`     | Archived                    |
| `tag:urgent`          | Tagged urgent               |
| `assignee:me`         | Assigned to the token owner |
| `is:unassigned`       | Unassigned                  |
| `inbox:support`       | In a named inbox            |
| `after:2024-01-01`    | Updated after a date        |
| `before:2024-12-31`   | Updated before a date       |

Combine with `AND` / `OR`: `status:open AND tag:urgent`.

## Recommended workflow: triaging and replying

```
list_conversations(q="status:open is:unassigned", limit=25)
  → pick the conversation you want to handle

list_conversation_messages(conversation_id="cnv_abc")
  → read customer context

update_conversation(conversation_id="cnv_abc", assignee_id="tea_xyz", confirm=True)
  → assign it to a teammate (two-step confirm)

reply_to_conversation(
    conversation_id="cnv_abc",
    body="Thanks for reaching out…",
    confirm=False,   # preview
)
reply_to_conversation(..., confirm=True)   # actually send
```

## Mutations are always two-step

Every tool that changes data on the Front side takes `confirm: bool = False`.
- `confirm=False` returns a dict with a `preview` key showing exactly what will
  be sent. No side effects.
- `confirm=True` elicits explicit user approval via the MCP host's
  `ctx.elicit` flow, then executes.

## Rate limits

Front enforces per-endpoint rate limits documented in its API reference. The
client retries 429 responses automatically with exponential backoff — expect
~60 req/min as a working rule of thumb.
"""


def register_resources(mcp: FastMCP) -> None:
    """Register the ``frontapp://help`` resource."""

    @mcp.resource(
        uri="frontapp://help",
        name="Tool reference",
        description="Tool reference and recommended workflows for the Frontapp MCP server.",
        mime_type="text/markdown",
    )
    async def help_resource() -> str:
        return _HELP_MARKDOWN
