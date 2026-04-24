"""MCP tools for Frontapp conversations.

Exposes 8 tools covering the common read paths and the three mutations that
matter for agent workflows (reply, update status/assignee/tags, add internal
comment). Mutations use the two-step confirm pattern: call with
``confirm=False`` to preview, ``confirm=True`` to execute (which also elicits
explicit user approval via ``ctx.elicit``).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import ConfirmationResult, require_confirmation
from frontapp_public_api_client.domain import Conversation


class ConversationSummary(BaseModel):
    """Human-readable projection of a conversation, for LLM responses.

    The full ``Conversation`` domain model carries more structure than is
    useful to an LLM on every list hit. This projection keeps the context
    window small — callers can still call ``get_conversation`` for full
    detail on a specific id.
    """

    id: str
    subject: str | None = None
    status: str | None = None
    assignee_name: str | None = None
    recipient: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_private: bool | None = None
    created_at: str | None = None
    updated_at: str | None = None
    waiting_since: str | None = None


def _to_summary(conv: Conversation) -> ConversationSummary:
    assignee_name = None
    if conv.assignee:
        parts = [conv.assignee.first_name, conv.assignee.last_name]
        assignee_name = " ".join(p for p in parts if p) or conv.assignee.username
    return ConversationSummary(
        id=conv.id,
        subject=conv.subject,
        status=conv.status,
        assignee_name=assignee_name,
        recipient=conv.recipient.handle if conv.recipient else None,
        tags=[t.name for t in conv.tags if t.name],
        is_private=conv.is_private,
        created_at=conv.created_at.isoformat() if conv.created_at else None,
        updated_at=conv.updated_at.isoformat() if conv.updated_at else None,
        waiting_since=(
            conv.waiting_since.isoformat() if conv.waiting_since else None
        ),
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
        return [_to_summary(c) for c in conversations]

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
        return _to_summary(conv)

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
        return [_to_summary(c) for c in conversations]

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

    @mcp.tool(
        name="reply_to_conversation",
        description=(
            "Send an outbound reply on an existing conversation. Uses the "
            "channel the conversation was opened on. Two-step confirm: "
            "confirm=False returns a preview; confirm=True executes."
        ),
    )
    async def reply_to_conversation(
        context: Context,
        conversation_id: str,
        body: Annotated[str, Field(description="Reply body (HTML or plain text)")],
        author_id: Annotated[
            str | None,
            Field(description="Teammate id to send as; defaults to token owner"),
        ] = None,
        subject: Annotated[
            str | None, Field(description="Override subject (rarely needed)")
        ] = None,
        to: Annotated[
            list[str] | None, Field(description="Override To recipients")
        ] = None,
        cc: Annotated[list[str] | None, Field(description="CC recipients")] = None,
        bcc: Annotated[list[str] | None, Field(description="BCC recipients")] = None,
        confirm: Annotated[
            bool, Field(description="Must be true to send the reply")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)

        preview = {
            "action": "reply_to_conversation",
            "conversation_id": conversation_id,
            "body_preview": body[:200] + ("…" if len(body) > 200 else ""),
            "author_id": author_id,
            "subject": subject,
            "to": to,
            "cc": cc,
            "bcc": bcc,
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context, f"Send reply to conversation {conversation_id}?"
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        response = await services.client.conversations.reply(
            conversation_id,
            body=body,
            author_id=author_id,
            subject=subject,
            to=to,
            cc=cc,
            bcc=bcc,
        )
        return {
            "confirmed": True,
            "status_code": response.status_code,
            "note": "Front returns 202 Accepted; the message is enqueued for delivery.",
        }

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
        if not confirm:
            return {"preview": preview, "confirmed": False}

        summary = ", ".join(f"{k}={v}" for k, v in changes.items())
        result = await require_confirmation(
            context, f"Update conversation {conversation_id}: {summary}?"
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

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
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context, f"Add internal comment to conversation {conversation_id}?"
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        response = await services.client.conversations.add_comment(
            conversation_id, body=body, author_id=author_id
        )
        return {"confirmed": True, "status_code": response.status_code}
