"""MCP resource: tool reference and workflow guide for the Frontapp MCP server."""

from __future__ import annotations

from fastmcp import FastMCP

_HELP_MARKDOWN = """\
# Frontapp MCP Server — Tool & Resource Reference

## Resources (slow-changing reference data, cached 60s)

| URI                              | Use it to…                                                       |
| -------------------------------- | ---------------------------------------------------------------- |
| `frontapp://help`                | Read this reference (you're reading it).                         |
| `frontapp://tags`                | Translate tag names ("urgent", "vip") into `tag_*` ids.          |
| `frontapp://inboxes`             | Translate inbox names ("Support", "Sales") into `inb_*` ids.     |
| `frontapp://teammates`           | Translate a teammate name or email into a `tea_*` id.            |
| `frontapp://conversations/recent`| Orient at session start — 20 most recent conversations.          |

Read these resources before calling mutating tools — they give you the
`tag_*` / `inb_*` / `tea_*` ids you'll need for `update_conversation` and
similar tools without asking the user. (Only conversation list/read tools
are registered today; tags / inboxes / teammates are exposed only as
resources.)

## Conversations

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `list_conversations` | `GET /conversations` | Cursor-paginated list. Pass `q=` for Front search syntax. |
| `get_conversation` | `GET /conversations/{id}` | Full detail for one conversation. |
| `search_conversations` | `GET /conversations/search/{query}` | Front search syntax as the primary filter. |
| `list_conversation_messages` | `GET /conversations/{id}/messages` | Messages in a conversation (most recent first). |
| `list_conversation_comments` | `GET /conversations/{id}/comments` | Internal teammate comments on a conversation. |
| `update_conversation` | `PATCH /conversations/{id}` | Archive/reopen, reassign, retag, move inbox. Two-step confirm. |
| `add_conversation_comment` | `POST /conversations/{id}/comments` | Teammate-only internal note. Two-step confirm. |

There is intentionally no direct "send a reply" tool — outbound replies go
through the drafts vertical below. Agents draft, humans send.

## Drafts (drafts-first outbound)

Drafts are the safe-by-default outbound path. An agent creates a draft, the
human reviews it in Front's UI, and the human clicks send. Front exposes no
programmatic ``send_draft``.

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `list_conversation_drafts` | `GET /conversations/{id}/drafts` | Existing drafts on a conversation. |
| `create_draft_on_channel` | `POST /channels/{channel_id}/drafts` | Brand-new outbound draft on a channel. Two-step confirm. |
| `create_draft_reply` | `POST /conversations/{id}/drafts` | Draft a reply on an existing conversation (`channel_id` required). Two-step confirm. |
| `edit_draft` | `PATCH /drafts/{id}/` | Full-replacement edit of an existing draft (`body` + `channel_id` required). Two-step confirm. |
| `delete_draft` | `DELETE /drafts/{id}` | Discard a draft. Two-step confirm. |

## Contacts

A contact is a person identified by one or more handles (email/phone/etc.).
Spans three sibling Front tags: `contacts`, `contact_handles`, `contact_notes`.

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `list_contacts` | `GET /contacts` | Cursor-paginated list. Pass `q=` for partial-match search across handles/names. |
| `get_contact` | `GET /contacts/{id}` | Full detail for one contact. |
| `lookup_contact_by_email` | (wraps `list_contacts(q=email)`) | Best-effort email lookup. Returns 0..n matches. |
| `list_team_contacts` | `GET /teams/{team_id}/contacts` | Contacts owned by a team. |
| `list_teammate_contacts` | `GET /teammates/{teammate_id}/contacts` | Contacts owned by a teammate. |
| `list_contact_conversations` | `GET /contacts/{id}/conversations` | Full conversation history with this customer. Returns `ConversationSummary`s. |
| `list_contact_notes` | `GET /contacts/{id}/notes` | Internal teammate notes (HTTP 202). |
| `create_contact` | `POST /contacts` | Create workspace-scoped contact. `handles` required. Two-step confirm. |
| `create_team_contact` | `POST /teams/{team_id}/contacts` | Create team-scoped contact. Two-step confirm. |
| `create_teammate_contact` | `POST /teammates/{teammate_id}/contacts` | Create teammate-scoped contact. Two-step confirm. |
| `update_contact` | `PATCH /contacts/{id}` | Update name/description/links/groups. Cannot change handles. Two-step confirm. |
| `add_contact_note` | `POST /contacts/{id}/notes` | Add internal teammate note. `author_id` required. Two-step confirm. |
| `add_contact_handle` | `POST /contacts/{id}/handles` | Add handle to existing contact. Two-step confirm. |
| `delete_contact_handle` | `DELETE /contacts/{id}/handles` | Remove handle. `force=true` allows last-handle removal. Two-step confirm. |
| `merge_contacts` | `POST /contacts/merge` | **DESTRUCTIVE / irreversible.** Merge contacts; conversations move to target. Two-step confirm. |
| `delete_contact` | `DELETE /contacts/{id}` | **DESTRUCTIVE / permanent.** Delete contact + all handles. Two-step confirm. |

## Messages

Operations on individual messages by `msg_*` id. Use these when the id
comes from a webhook, audit log, or external system; for browsing inside
a known conversation prefer `list_conversation_messages`.

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `get_message` | `GET /messages/{id}` | Full detail for one message (compact dict). |
| `get_message_seen_status` | `GET /messages/{id}/seen` | Seen receipts for an outbound message (`first_seen_at` is an ISO string, not epoch). |
| `mark_message_seen` | `POST /messages/{id}/seen` | Acknowledge that the message was seen. **Rate limited: 10 req/msg/hour.** Optional `teammate_id` attribution. Two-step confirm. |

Outbound replies do not live here — use `create_draft_reply` (drafts
vertical) instead. Front exposes no programmatic `send_message`.

### Workflow recipe — "what else do we have on this customer?"

```
lookup_contact_by_email(email="customer@example.com")
  -> [ContactSummary(id="crd_abc", name="Alice", primary_email="customer@example.com")]

list_contact_conversations(contact_id="crd_abc")
  -> [{id: cnv_1, subject: "Order #1234"}, ...]

list_contact_notes(contact_id="crd_abc")
  -> [{body: "VIP customer", author: ...}, ...]
```

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

## Recommended workflow: triaging and drafting a reply

```
list_conversations(q="status:open is:unassigned", limit=25)
  → pick the conversation you want to handle

list_conversation_messages(conversation_id="cnv_abc")
  → read customer context

update_conversation(conversation_id="cnv_abc", assignee_id="tea_xyz", confirm=True)
  → assign it to a teammate (two-step confirm)

create_draft_reply(
    conversation_id="cnv_abc",
    body="Thanks for reaching out…",
    channel_id="cha_xyz",
    confirm=False,   # preview
)
create_draft_reply(..., confirm=True)
  → draft is created in Front; tell the user to review and click send
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
