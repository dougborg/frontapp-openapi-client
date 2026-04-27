"""MCP tools for Frontapp drafts.

Drafts are the safe-by-default outbound path: an agent creates a draft, the
human reviews it in Front's UI, and the human clicks send. There is no
programmatic ``send_draft`` — sending is always human-in-the-loop.

All four mutation tools (create-on-channel, create-reply, edit, delete) use
the standard two-step confirm pattern: call with ``confirm=False`` for a
preview, ``confirm=True`` to execute (which also elicits explicit user
approval via ``ctx.elicit``).

Attachments: every create/edit tool accepts an optional ``attachment_paths``
parameter — a list of absolute filesystem paths. Each path is read at tool-
invocation time, MIME-type-inferred, and shipped to Front as
``multipart/form-data``. Paths must be absolute, exist, be regular files,
and below Front's 25 MB per-attachment limit; the preview surfaces the
filenames and sizes so the human can confirm before the upload runs.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.projections import DraftSummary, to_draft_summary
from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import ConfirmationResult, require_confirmation
from frontapp_public_api_client.helpers.attachments import (
    preview_paths,
    resolve_paths,
)


def _preview_body(body: str) -> str:
    return body[:200] + ("…" if len(body) > 200 else "")


def register_tools(mcp: FastMCP) -> None:
    """Register draft-related tools with the FastMCP server."""

    # -- reads --------------------------------------------------------------

    @mcp.tool(
        name="list_conversation_drafts",
        description=(
            "List drafts on a conversation. Drafts are unsent messages "
            "awaiting human review in Front's UI."
        ),
    )
    async def list_conversation_drafts(
        context: Context,
        conversation_id: Annotated[
            str, Field(description="Conversation id, e.g. 'cnv_abc123'")
        ],
    ) -> list[dict[str, Any]]:
        services = get_services(context)
        drafts = await services.client.drafts.list_for_conversation(conversation_id)
        # Drafts list is raw_array of attrs MessageResponse — to_dict for JSON safety.
        return [d.to_dict() for d in drafts]

    # -- mutations (two-step confirm) ---------------------------------------

    @mcp.tool(
        name="create_draft_on_channel",
        description=(
            "Create a draft message on a channel (no existing conversation). "
            "Returns a DraftSummary so the LLM can verify what was created. "
            "Two-step confirm: confirm=False returns a preview; confirm=True "
            "creates the draft (human still has to click send in Front)."
        ),
    )
    async def create_draft_on_channel(
        context: Context,
        channel_id: Annotated[str, Field(description="Channel id, e.g. 'cha_abc123'")],
        body: Annotated[str, Field(description="Draft body (HTML or plain text)")],
        author_id: Annotated[
            str | None,
            Field(description="Teammate id to author as; defaults to token owner"),
        ] = None,
        subject: Annotated[str | None, Field(description="Subject line")] = None,
        to: Annotated[
            list[str] | None, Field(description="To recipients (handles)")
        ] = None,
        cc: Annotated[list[str] | None, Field(description="CC recipients")] = None,
        bcc: Annotated[list[str] | None, Field(description="BCC recipients")] = None,
        mode: Annotated[
            Literal["private", "shared"] | None,
            Field(description="'private' (author-only) or 'shared' (all teammates)"),
        ] = None,
        attachment_paths: Annotated[
            list[str] | None,
            Field(
                description=(
                    "Absolute filesystem paths to files to attach. Each must "
                    "exist, be a regular file, and be ≤25 MB."
                )
            ),
        ] = None,
        confirm: Annotated[
            bool, Field(description="Must be true to create the draft")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        attachment_preview = preview_paths(attachment_paths)
        preview = {
            "action": "create_draft_on_channel",
            "channel_id": channel_id,
            "subject": subject,
            "body_preview": _preview_body(body),
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "mode": mode,
            "attachments": attachment_preview,
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context, f"Create draft on channel {channel_id}?"
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        draft = await services.client.drafts.create_on_channel(
            channel_id,
            body=body,
            author_id=author_id,
            subject=subject,
            to=to,
            cc=cc,
            bcc=bcc,
            mode=mode,
            attachments=resolve_paths(attachment_paths)[0] or None,
        )
        return {"confirmed": True, "draft": to_draft_summary(draft).model_dump()}

    @mcp.tool(
        name="create_draft_reply",
        description=(
            "Create a draft reply on an existing conversation. The draft "
            "appears in Front for human review and send. channel_id is "
            "required so Front knows which channel the reply will go through. "
            "Two-step confirm: confirm=False returns a preview; confirm=True "
            "creates the draft."
        ),
    )
    async def create_draft_reply(
        context: Context,
        conversation_id: Annotated[
            str, Field(description="Conversation id, e.g. 'cnv_abc123'")
        ],
        body: Annotated[str, Field(description="Reply body (HTML or plain text)")],
        channel_id: Annotated[
            str,
            Field(description="Channel to send through, e.g. 'cha_abc123'"),
        ],
        author_id: Annotated[
            str | None, Field(description="Teammate id to author as")
        ] = None,
        subject: Annotated[
            str | None, Field(description="Override subject (rarely needed)")
        ] = None,
        to: Annotated[
            list[str] | None, Field(description="Override To recipients")
        ] = None,
        cc: Annotated[list[str] | None, Field(description="CC recipients")] = None,
        bcc: Annotated[list[str] | None, Field(description="BCC recipients")] = None,
        mode: Annotated[
            Literal["private", "shared"] | None,
            Field(description="'private' or 'shared'"),
        ] = None,
        attachment_paths: Annotated[
            list[str] | None,
            Field(
                description=(
                    "Absolute filesystem paths to files to attach. Each must "
                    "exist, be a regular file, and be ≤25 MB."
                )
            ),
        ] = None,
        confirm: Annotated[
            bool, Field(description="Must be true to create the draft")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        attachment_preview = preview_paths(attachment_paths)
        preview = {
            "action": "create_draft_reply",
            "conversation_id": conversation_id,
            "channel_id": channel_id,
            "body_preview": _preview_body(body),
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "mode": mode,
            "attachments": attachment_preview,
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context, f"Create draft reply on conversation {conversation_id}?"
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        draft = await services.client.drafts.create_reply(
            conversation_id,
            body=body,
            channel_id=channel_id,
            author_id=author_id,
            subject=subject,
            to=to,
            cc=cc,
            bcc=bcc,
            mode=mode,
            attachments=resolve_paths(attachment_paths)[0] or None,
        )
        return {
            "confirmed": True,
            "draft": to_draft_summary(draft).model_dump(),
            "note": (
                "Draft created. The human reviews in Front and clicks send; "
                "there is no programmatic send_draft."
            ),
        }

    @mcp.tool(
        name="edit_draft",
        description=(
            "Edit an existing draft. Front's PATCH /drafts/{id}/ is a "
            "full-replacement — body and channel_id are required even when "
            "only changing metadata. Pass version (from a prior draft fetch) "
            "to avoid clobbering concurrent edits. Two-step confirm."
        ),
    )
    async def edit_draft(
        context: Context,
        draft_id: Annotated[
            str, Field(description="Draft id, e.g. 'msg_abc123' or 'dft_abc123'")
        ],
        body: Annotated[str, Field(description="Full draft body (replaces existing)")],
        channel_id: Annotated[
            str, Field(description="Channel id, required by Front's edit shape")
        ],
        author_id: Annotated[
            str | None, Field(description="Teammate id to author as")
        ] = None,
        subject: Annotated[str | None, Field(description="Subject line")] = None,
        to: Annotated[list[str] | None, Field(description="To recipients")] = None,
        cc: Annotated[list[str] | None, Field(description="CC recipients")] = None,
        bcc: Annotated[list[str] | None, Field(description="BCC recipients")] = None,
        mode: Annotated[
            Literal["shared"] | None,
            Field(description="Only 'shared' is accepted on edit"),
        ] = None,
        version: Annotated[
            str | None,
            Field(description="Version token from a prior draft to avoid clobbers"),
        ] = None,
        attachment_paths: Annotated[
            list[str] | None,
            Field(
                description=(
                    "Absolute filesystem paths for the new attachment set. "
                    "Front's edit semantics replace the attachment list, so "
                    "anything not listed here is dropped from the draft."
                )
            ),
        ] = None,
        confirm: Annotated[
            bool, Field(description="Must be true to apply the edit")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        attachment_preview = preview_paths(attachment_paths)
        preview = {
            "action": "edit_draft",
            "draft_id": draft_id,
            "channel_id": channel_id,
            "subject": subject,
            "body_preview": _preview_body(body),
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "mode": mode,
            "version": version,
            "attachments": attachment_preview,
        }
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(
            context, f"Edit draft {draft_id}? This replaces the current draft body."
        )
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        draft = await services.client.drafts.edit(
            draft_id,
            body=body,
            channel_id=channel_id,
            author_id=author_id,
            subject=subject,
            to=to,
            cc=cc,
            bcc=bcc,
            mode=mode,
            version=version,
            attachments=resolve_paths(attachment_paths)[0] or None,
        )
        return {"confirmed": True, "draft": to_draft_summary(draft).model_dump()}

    @mcp.tool(
        name="delete_draft",
        description=(
            "Delete a draft by id. Two-step confirm — deleting clobbers any "
            "in-progress edits in Front."
        ),
    )
    async def delete_draft(
        context: Context,
        draft_id: Annotated[str, Field(description="Draft id to delete")],
        confirm: Annotated[bool, Field(description="Must be true to delete")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {"action": "delete_draft", "draft_id": draft_id}
        if not confirm:
            return {"preview": preview, "confirmed": False}

        result = await require_confirmation(context, f"Delete draft {draft_id}?")
        if result is not ConfirmationResult.CONFIRMED:
            return {"preview": preview, "confirmed": False, "result": result.value}

        success = await services.client.drafts.delete(draft_id)
        return {"confirmed": True, "deleted": success}


__all__ = ["DraftSummary", "register_tools"]
