"""MCP resource: tool reference and workflow guide for the Frontapp MCP server."""

from __future__ import annotations

from fastmcp import FastMCP

_HELP_MARKDOWN = """\
# Frontapp MCP Server — Tool & Resource Reference

## Resources (slow-changing reference data, cached 60s)

| URI                               | Use it to…                                                                               |
| --------------------------------- | ---------------------------------------------------------------------------------------- |
| `frontapp://help`                 | Read this reference (you're reading it).                                                 |
| `frontapp://me`                   | Workspace identity (`cmp_*`, name). Session-start smoke test — does NOT identify teammate. |
| `frontapp://tags`                 | Translate tag names ("urgent", "vip") into `tag_*` ids.                                  |
| `frontapp://inboxes`              | Translate inbox names ("Support", "Sales") into `inb_*` ids.                             |
| `frontapp://teammates`            | Translate a teammate name or email into a `tea_*` id.                                    |
| `frontapp://teams`                | Translate a team name ("Support") into a `tim_*` id.                                     |
| `frontapp://custom_fields`        | Every custom field schema in the workspace, grouped by scope. Translate field name → `cf_*` id. |
| `frontapp://conversations/recent` | Orient at session start — 20 most recent conversations.                                  |

Read these resources before calling mutating tools — they give you the
`tag_*` / `inb_*` / `tea_*` / `tim_*` / `cf_*` ids you'll need for
`update_conversation` and similar tools without asking the user. (Only
conversation list/read tools are registered today; tags / inboxes /
teammates / teams / custom_fields are exposed only as resources.)

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

### Attachments on drafts / replies / comments

`create_draft_on_channel`, `create_draft_reply`, and `edit_draft` accept an
optional `attachment_paths=[...]` parameter — a list of ABSOLUTE filesystem
paths read at tool-invocation time. Each path is validated (must exist, be
a regular file, ≤25 MB), MIME-type-inferred, and shipped to Front as
`multipart/form-data`. The preview includes filename + size for human
review. Note: `edit_draft` REPLACES the attachment list — any file not
listed is dropped.

`add_conversation_comment` (in the conversations vertical) takes the same
`attachment_paths` parameter when you want to attach files to an internal
note.

## Attachments

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `download_attachment` | `GET /download/{attachment_link_id}` (and 4 sibling paths) | Fetch attachment bytes by URL (the value Front returns on `Attachment.url`) and write to a local filesystem path. Two-step confirm protects against unintended writes. The five `/download/...` paths are stripped from the spec because openapi-python-client can't model binary responses; this tool bypasses the generated client. |

The download tool writes bytes to disk and returns metadata only — never
the raw bytes themselves, which would explode token usage. Pass an
absolute `save_path` whose parent already exists.

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

## Contact Lists

Named buckets of contacts used for bulk operations (broadcasts, segmentation,
exports). Three creation scopes: workspace, team, teammate. Front exposes no
GET-by-id and no PATCH — lists can't be renamed once created.

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `list_contact_lists` | `GET /contact_lists` | All contact lists visible to the token. |
| `list_team_contact_lists` | `GET /teams/{team_id}/contact_lists` | Team-scoped lists. |
| `list_teammate_contact_lists` | `GET /teammates/{teammate_id}/contact_lists` | Private (teammate-scoped) lists. |
| `list_contacts_in_contact_list` | `GET /contact_lists/{id}/contacts` | Members of a list. Returns `ContactSummary`s. |
| `create_contact_list` | `POST /contact_lists` | Workspace-scoped create. **Targets oldest active workspace** — prefer `create_team_contact_list` when team is known. Two-step confirm. |
| `create_team_contact_list` | `POST /teams/{team_id}/contact_lists` | Team-scoped create. Two-step confirm. |
| `create_teammate_contact_list` | `POST /teammates/{teammate_id}/contact_lists` | Private (teammate-scoped) create. Two-step confirm. |
| `add_contacts_to_contact_list` | `POST /contact_lists/{id}/contacts` | Bulk add. Accepts `crd_*` ids OR Front resource aliases (`alt:email:foo@x.com`). Two-step confirm. |
| `remove_contacts_from_contact_list` | `DELETE /contact_lists/{id}/contacts` | Bulk remove. **Capped at 50 ids per call** by Front. Two-step confirm. |
| `delete_contact_list` | `DELETE /contact_lists/{id}` | Dissolve list; **contacts NOT deleted**. Two-step confirm. |

Workflow tip: "tag this customer as VIP" → `lookup_contact_by_email(email)` →
`list_contact_lists()` to find the VIP list id → `add_contacts_to_contact_list(list_id, [contact_id])`.

## Contact Groups (DEPRECATED)

Front has deprecated all contact-group endpoints in favor of contact lists.
Tools exist for workspaces still using groups; for new work use `contact_lists`
above. Same shape, same 50-contact cap on bulk removal, same workspace-default
caveat on `create_contact_group`.

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `list_contact_groups` | `GET /contact_groups` | All contact groups (deprecated). |
| `list_team_contact_groups` | `GET /teams/{team_id}/contact_groups` | Team-scoped groups. |
| `list_teammate_contact_groups` | `GET /teammates/{teammate_id}/contact_groups` | Private groups. |
| `list_contacts_in_group` | `GET /contact_groups/{id}/contacts` | Members of a group. |
| `create_contact_group` | `POST /contact_groups` | Workspace-scoped create. Two-step confirm. |
| `create_team_contact_group` | `POST /teams/{team_id}/contact_groups` | Team-scoped create. Two-step confirm. |
| `create_teammate_contact_group` | `POST /teammates/{teammate_id}/contact_groups` | Private create. Two-step confirm. |
| `add_contacts_to_group` | `POST /contact_groups/{id}/contacts` | Bulk add. Two-step confirm. |
| `remove_contacts_from_group` | `DELETE /contact_groups/{id}/contacts` | Bulk remove. **Capped at 50 per call.** Two-step confirm. |
| `delete_contact_group` | `DELETE /contact_groups/{id}` | Dissolve group; contacts NOT deleted. Two-step confirm. |

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

## Tags

Workspace-level reference data. The `frontapp://tags` resource is the
preferred name-to-id lookup at session start; the tools below are for
programmatic listing, single-tag deltas on a conversation, and
catalog mutations.

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `list_tags` | `GET /tags` | All workspace tags. |
| `list_company_tags` | `GET /company/tags` | Company-scoped tags (visible across teams). |
| `list_team_tags` | `GET /teams/{team_id}/tags` | Team-scoped tags. |
| `list_teammate_tags` | `GET /teammates/{teammate_id}/tags` | Teammate-scoped tags. |
| `get_tag` | `GET /tags/{id}` | Full detail for one tag. |
| `list_tag_children` | `GET /tags/{id}/children` | Child tags of a parent (no pagination). |
| `list_tagged_conversations` | `GET /tags/{id}/conversations` | Conversations bearing this tag. Returns `ConversationSummary`s. |
| `add_tag_to_conversation` | `POST /conversations/{id}/tags` | **DELTA** — adds one tag, leaves others. Two-step confirm. |
| `remove_tag_from_conversation` | `DELETE /conversations/{id}/tags` | **DELTA** — removes one tag, leaves others. Two-step confirm. |
| `create_tag` | `POST /tags` | Create workspace tag. WORKSPACE-WIDE. Two-step confirm. |
| `create_child_tag` | `POST /tags/{id}/children` | Create a child under a parent. Two-step confirm. |
| `update_tag` | `PATCH /tags/{id}` | Update name/highlight/parent. WORKSPACE-WIDE. Two-step confirm. |
| `delete_tag` | `DELETE /tags/{id}` | **DESTRUCTIVE.** Removes from every conversation. Two-step confirm. |

### Delta vs replace — important

`add_tag_to_conversation` and `remove_tag_from_conversation` operate on
a single tag without touching the others. `update_conversation(tag_ids=[…])`
in the conversations vertical REPLACES the entire tag set. Use the
delta tools when you want to nudge a single tag.

## Inboxes

Channel containers. Every conversation belongs to one. The
`frontapp://inboxes` resource is the preferred name-to-id lookup;
the tools below cover programmatic listing, per-inbox lookups, and
mutations.

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `list_inboxes` | `GET /inboxes` | All visible inboxes (no pagination). |
| `list_team_inboxes` | `GET /teams/{team_id}/inboxes` | Inboxes owned by a team. |
| `list_teammate_private_inboxes` | `GET /teammates/{id}/private_inboxes` | A teammate's private inboxes. |
| `get_inbox` | `GET /inboxes/{id}` | Full detail for one inbox. |
| `list_inbox_conversations` | `GET /inboxes/{id}/conversations` | Conversations in this inbox. Returns `ConversationSummary`s. |
| `list_inbox_channels` | `GET /inboxes/{id}/channels` | Channels routing into this inbox. |
| `list_inbox_access` | `GET /inboxes/{id}/teammates` | Teammates with access. |
| `create_inbox` | `POST /inboxes` | Create workspace inbox. Two-step confirm. |
| `create_team_inbox` | `POST /teams/{team_id}/inboxes` | Create team inbox. Two-step confirm. |
| `grant_inbox_access` | `POST /inboxes/{id}/teammates` | Grant access to teammates (preview shows count + ids). Two-step confirm. |
| `revoke_inbox_access` | `DELETE /inboxes/{id}/teammates` | Revoke access from teammates. Two-step confirm. |

Front exposes no inbox PATCH endpoint — name and visibility are immutable
post-creation. The only post-create mutations are the access grant/revoke
pair.

## Teammates

Human users in the workspace. The `frontapp://teammates` resource is the
preferred name-to-id lookup at session start.

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `list_teammates` | `GET /teammates` | Every teammate in the workspace (no pagination). |
| `get_teammate` | `GET /teammates/{id}` | Full detail for one teammate. |
| `list_teammate_inboxes` | `GET /teammates/{id}/inboxes` | Inboxes this teammate has access to. |
| `list_assigned_conversations` | `GET /teammates/{id}/conversations` | Conversations currently assigned to this teammate. Returns `ConversationSummary`s. |
| `update_teammate` | `PATCH /teammates/{id}` | Update username / first_name / last_name / is_available. Email and admin status are NOT changeable here. Two-step confirm. |

## Knowledge Base

Front's KB — articles and categories grouped under one or more KBs.
Wrapped here for two distinct workflows: **retrieval** (find content to
paraphrase in replies) and **contribute** (turn a conversation
resolution into a new article).

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `list_knowledge_bases` | `GET /knowledge_bases` | Catalog of every KB. Returns id + name. |
| `get_kb` | `GET /knowledge_bases/{id}` (`/content` variants for `with_content=True`) | Single KB detail. |
| `list_kb_categories` | `GET /knowledge_bases/{id}/categories` | Cursor-paginated categories list. |
| `list_kb_articles` | `GET /knowledge_bases/{id}/articles` | Cursor-paginated slim articles (no body). |
| `list_kb_articles_in_category` | `GET /knowledge_base_categories/{id}/articles` | Slim articles scoped to one category. |
| `get_kb_article` | `GET /knowledge_base_articles/{id}` (`/content` variants) | Full article body — defaults `with_content=True`. |
| `create_kb_article` | `POST /knowledge_bases/{id}/articles[/locales/{locale}/articles]` | Create a NEW article AS A DRAFT. Two-step confirm. |
| `update_kb_article` | `PATCH /knowledge_base_articles/{id}/content[/locales/{locale}/content]` | Edit subject/body/author. Cannot flip status. Two-step confirm. |
| `create_kb_category` | `POST /knowledge_bases/{id}/categories[/locales/{locale}/categories]` | Two-step confirm. |
| `update_kb_category` | `PATCH /knowledge_base_categories/{id}/content[/locales/{locale}/content]` | Two-step confirm. |

### Drafts only — agents never publish

`create_kb_article` always creates a `status: "draft"` article — there
is no `status` parameter on the tool. `update_kb_article` cannot change
the publication state either; the existing draft/published state is
preserved. **A human flips drafts to published in Front's UI.**

Mirrors ADR-0016's drafts-first outbound philosophy: agents draft,
humans send/publish. The Python helper layer
(`client.knowledge_bases`) does retain the `status` kwarg so library
callers (Python scripts) can publish programmatically — the MCP tools
are the agent-safety boundary, not the helper.

### Locale

Every KB tool accepts an optional `locale` arg (e.g. `"en"`, `"fr"`).
Omit for the workspace's default locale.

### Workflow recipe — "answer this customer with a KB article"

```
list_knowledge_bases() → [{id: "knb_main", name: "Public KB"}, ...]
list_kb_articles(knowledge_base_id="knb_main", limit=50)
  → [{id, subject, status}, ...]   # agent picks the relevant article by subject
get_kb_article(article_id="kba_xyz", with_content=True)
  → {subject, content: "<article body>", ...}
# Agent paraphrases or quotes content into a draft reply via create_draft_reply.
```

### Workflow recipe — "this conversation resolved a novel issue; capture it"

```
list_knowledge_bases() → pick the right KB
list_kb_categories(knowledge_base_id="knb_main") → pick a category
create_kb_article(
    knowledge_base_id="knb_main",
    subject="How to reset 2FA when phone is lost",
    content="<article body...>",
    category_id="kbc_security",
    confirm=True,  # after human approves the elicitation
)
  → {confirmed: true, article: {id: "kba_new", status: "draft", ...}}
# Article lands as a draft in Front's UI; human reviews and publishes.
```

## Analytics

Front's analytics endpoints are server-side asynchronous: the POST returns
immediately with a job id; a follow-up GET polls until `status == "done"`.
The MCP tools wrap that loop into a single call. No two-step confirm —
these are read/query operations; the server-side job is just how Front
computes the result.

| Tool | Endpoint | Purpose |
| ---- | -------- | ------- |
| `run_analytics_report` | `POST /analytics/reports` + `GET /analytics/reports/{uid}` | Compute scalar metrics over a time window. Pass exactly one filter category (`inbox_ids` OR `tag_ids` OR `teammate_ids` OR `team_ids` OR `channel_ids` OR `account_ids`) — Front rejects combined categories. Returns final dict with `metrics`. |
| `run_analytics_export` | `POST /analytics/exports` + `GET /analytics/exports/{id}` | Bulk-export teammate-activity rows (`export_type="activities"`) or message-level rows (`export_type="messages"`) to CSV. Returns a download URL. If Front responds `too_big`, narrow the date range or column set and retry. |

Both tools poll until `done`, fail (`failed` or `too_big`), or
`timeout_seconds` elapses (returns `{"status": "timeout"}`). The
server-side job keeps running on Front after a tool timeout — library
callers can resume via `client.analytics.get_report(uid)` /
`get_export(id)`.

Defaults: `run_analytics_report` polls once a second for 30s;
`run_analytics_export` polls every 2 seconds for 120s. Both honor a
`Retry-After` response header if
Front sends one.

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
