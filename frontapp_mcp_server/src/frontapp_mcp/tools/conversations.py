"""MCP tools for Frontapp conversations.

Exposes 7 tools: 5 read-side (list / get / search / list_messages /
list_comments) and 2 internal-only mutations (update_conversation,
add_conversation_comment) using the standard two-step confirm pattern.

There is no direct ``reply_to_conversation`` tool — outbound replies happen
via the drafts vertical (``create_draft_reply`` etc.). Agents draft, humans
send. See ADR-0016 → "Drafts-first outbound" for the rationale.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.projections import ConversationSummary, to_summary
from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import (
    confirm_or_preview,
)


def register_tools(mcp: FastMCP) -> None:
    """Register conversation-related tools with the FastMCP server."""

    # -- reads --------------------------------------------------------------

    @mcp.tool(
        name="list_conversations",
        description=(
            "List conversations in reverse chronological order. Use q for "
            "Front's search syntax (e.g. 'status:open tag:urgent')."
        ),
    )
    async def list_conversations(
        context: Context,
        q: Annotated[
            str | None,
            Field(
                description=(
                    "Front search syntax: status:open | status:archived | "
                    "tag:urgent | assignee:me | is:unassigned | inbox:support | "
                    "after:2024-01-01 | before:2024-12-31 | combine with AND/OR"
                )
            ),
        ] = None,
        limit: Annotated[
            int | None, Field(description="Page size (max 100, default 50)")
        ] = None,
        page_token: Annotated[
            str | None, Field(description="Cursor from previous page's pagination.next")
        ] = None,
    ) -> list[ConversationSummary]:
        services = get_services(context)
        conversations = await services.client.conversations.list(
            q=q, limit=limit, page_token=page_token
        )
        return [to_summary(c) for c in conversations]

    @mcp.tool(
        name="get_conversation",
        description="Fetch full details for one conversation by id (e.g. 'cnv_abc123').",
    )
    async def get_conversation(
        context: Context,
        conversation_id: Annotated[
            str, Field(description="Conversation id, e.g. 'cnv_abc123'")
        ],
    ) -> ConversationSummary:
        services = get_services(context)
        conv = await services.client.conversations.get(conversation_id)
        return to_summary(conv)

    @mcp.tool(
        name="search_conversations",
        description=(
            "Search conversations with Front's full query syntax. Alias of "
            "list_conversations with a required q parameter; use this when "
            "your query is the main filter."
        ),
    )
    async def search_conversations(
        context: Context,
        query: Annotated[
            str,
            Field(description="Front search syntax, e.g. 'status:open AND tag:urgent'"),
        ],
        limit: Annotated[int | None, Field(description="Page size (max 100)")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[ConversationSummary]:
        services = get_services(context)
        conversations = await services.client.conversations.search(
            query, limit=limit, page_token=page_token
        )
        return [to_summary(c) for c in conversations]

    @mcp.tool(
        name="list_conversation_messages",
        description=(
            "List messages in a conversation. Returns raw message objects "
            "from Front's API (sender/recipient handles, body, attachments, "
            "timestamp). Most recent first."
        ),
    )
    async def list_conversation_messages(
        context: Context,
        conversation_id: str,
        limit: Annotated[int | None, Field(description="Page size")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[dict[str, Any]]:
        services = get_services(context)
        messages = await services.client.conversations.list_messages(
            conversation_id, limit=limit, page_token=page_token
        )
        # Attrs models have .to_dict() for JSON-safe output
        return [m.to_dict() for m in messages]

    @mcp.tool(
        name="list_conversation_comments",
        description="List internal (teammate-only) comments on a conversation.",
    )
    async def list_conversation_comments(
        context: Context,
        conversation_id: str,
    ) -> list[dict[str, Any]]:
        services = get_services(context)
        comments = await services.client.conversations.list_comments(conversation_id)
        return [c.to_dict() for c in comments]

    # -- mutations (two-step confirm) ---------------------------------------
    #
    # Outbound replies are NOT exposed here — the conversations vertical has
    # no direct-send tool. Use ``create_draft_reply`` (in the drafts vertical)
    # to draft a reply that the human reviews and sends in Front's UI. See
    # ADR-0016 → "Drafts-first outbound" for the rationale.

    @mcp.tool(
        name="update_conversation",
        description=(
            "Update a conversation: status ('open'/'archived'/'deleted'/'spam'), "
            "assignee, inbox, or tag set. Two-step confirm."
        ),
    )
    async def update_conversation(
        context: Context,
        conversation_id: str,
        status: Annotated[
            str | None,
            Field(description="'open', 'archived', 'deleted', or 'spam'"),
        ] = None,
        assignee_id: Annotated[
            str | None, Field(description="Teammate id (e.g. 'tea_abc') to assign")
        ] = None,
        inbox_id: Annotated[
            str | None, Field(description="Inbox id to move the conversation to")
        ] = None,
        tag_ids: Annotated[
            list[str] | None,
            Field(description="Full list of tag ids (replaces existing tags)"),
        ] = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        services = get_services(context)

        changes = {
            k: v
            for k, v in {
                "status": status,
                "assignee_id": assignee_id,
                "inbox_id": inbox_id,
                "tag_ids": tag_ids,
            }.items()
            if v is not None
        }
        preview = {
            "action": "update_conversation",
            "conversation_id": conversation_id,
            "changes": changes,
        }
        if not changes:
            return {
                "preview": preview,
                "confirmed": False,
                "result": "no_changes_requested",
            }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        response = await services.client.conversations.update(
            conversation_id,
            status=status,
            assignee_id=assignee_id,
            inbox_id=inbox_id,
            tag_ids=tag_ids,
        )
        return {"confirmed": True, "status_code": response.status_code}

    @mcp.tool(
        name="add_conversation_comment",
        description=(
            "Add an internal comment to a conversation (visible to teammates "
            "only — does NOT reach the customer). Two-step confirm."
        ),
    )
    async def add_conversation_comment(
        context: Context,
        conversation_id: str,
        body: Annotated[str, Field(description="Comment body")],
        author_id: Annotated[
            str | None,
            Field(description="Teammate id for the comment author"),
        ] = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        services = get_services(context)

        preview = {
            "action": "add_conversation_comment",
            "conversation_id": conversation_id,
            "body_preview": body[:200] + ("…" if len(body) > 200 else ""),
            "author_id": author_id,
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        comment = await services.client.conversations.add_comment(
            conversation_id, body=body, author_id=author_id
        )
        return {"confirmed": True, "comment": comment}
