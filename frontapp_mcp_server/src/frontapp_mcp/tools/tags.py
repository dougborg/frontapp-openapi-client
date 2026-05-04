"""MCP tools for Frontapp tag management.

Spans the workspace tag catalog (``/tags*``) plus the conversation-tag
delta endpoints. All mutations use the standard two-step confirm.

- 7 reads (cached 30s): list / list_company / list_team / list_teammate /
  get / list_children / list_tagged_conversations
- 6 mutations (two-step confirm): add_tag_to_conversation /
  remove_tag_from_conversation / create_tag / create_child_tag /
  update_tag / delete_tag

Critical semantic distinction documented in tool docstrings and the MCP
``instructions`` block:

- ``add_tag_to_conversation`` / ``remove_tag_from_conversation`` are
  **delta** operations on a single tag.
- ``update_conversation(tag_ids=[...])`` (in the conversations vertical)
  is a **replace** operation on the full tag set.

The single-tag tools take ``tag_id: str`` (not a list) at the MCP layer
to reduce the chance of an agent inadvertently affecting more than one
tag.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.projections import (
    ConversationSummary,
    TagCatalogSummary,
    to_summary,
    to_tag_catalog_summary,
)
from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import (
    confirm_or_preview,
)
from frontapp_public_api_client.helpers.tags import HighlightLiteral


def register_tools(mcp: FastMCP) -> None:
    """Register tag-related tools with the FastMCP server."""

    # -- reads --------------------------------------------------------------

    @mcp.tool(
        name="list_tags",
        description=(
            "List workspace tags. Prefer the `frontapp://tags` resource for "
            "name-to-id lookups at session start; this tool is for "
            "programmatic listing with pagination."
        ),
    )
    async def list_tags(
        context: Context,
        limit: Annotated[
            int | None, Field(description="Page size (max 100, default 50)")
        ] = None,
        page_token: Annotated[
            str | None, Field(description="Cursor from a prior pagination.next")
        ] = None,
    ) -> list[TagCatalogSummary]:
        services = get_services(context)
        tags = await services.client.tags.list(limit=limit, page_token=page_token)
        return [to_tag_catalog_summary(t) for t in tags]

    @mcp.tool(
        name="list_company_tags",
        description="List company-scoped tags (visible across all teams).",
    )
    async def list_company_tags(
        context: Context,
        limit: Annotated[int | None, Field(description="Page size")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[TagCatalogSummary]:
        services = get_services(context)
        tags = await services.client.tags.list_company(
            limit=limit, page_token=page_token
        )
        return [to_tag_catalog_summary(t) for t in tags]

    @mcp.tool(
        name="list_team_tags",
        description="List tags scoped to a team (`team_id` like 'tim_abc').",
    )
    async def list_team_tags(
        context: Context,
        team_id: Annotated[str, Field(description="Team id, e.g. 'tim_abc'")],
        limit: Annotated[int | None, Field(description="Page size")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[TagCatalogSummary]:
        services = get_services(context)
        tags = await services.client.tags.list_for_team(
            team_id, limit=limit, page_token=page_token
        )
        return [to_tag_catalog_summary(t) for t in tags]

    @mcp.tool(
        name="list_teammate_tags",
        description="List tags scoped to a teammate (`teammate_id` like 'tea_abc').",
    )
    async def list_teammate_tags(
        context: Context,
        teammate_id: Annotated[str, Field(description="Teammate id, e.g. 'tea_abc'")],
        limit: Annotated[int | None, Field(description="Page size")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[TagCatalogSummary]:
        services = get_services(context)
        tags = await services.client.tags.list_for_teammate(
            teammate_id, limit=limit, page_token=page_token
        )
        return [to_tag_catalog_summary(t) for t in tags]

    @mcp.tool(
        name="get_tag",
        description="Fetch full details for one tag by id (e.g. 'tag_abc').",
    )
    async def get_tag(
        context: Context,
        tag_id: Annotated[str, Field(description="Tag id, e.g. 'tag_abc'")],
    ) -> TagCatalogSummary:
        services = get_services(context)
        tag = await services.client.tags.get(tag_id)
        return to_tag_catalog_summary(tag)

    @mcp.tool(
        name="list_tag_children",
        description=(
            "List child tags of a parent tag. Returns the full child set "
            "(no pagination)."
        ),
    )
    async def list_tag_children(
        context: Context,
        tag_id: Annotated[str, Field(description="Parent tag id")],
    ) -> list[TagCatalogSummary]:
        services = get_services(context)
        children = await services.client.tags.list_children(tag_id)
        return [to_tag_catalog_summary(c) for c in children]

    @mcp.tool(
        name="list_tagged_conversations",
        description=(
            "List conversations bearing this tag. Pass `q=` to filter "
            "with Front search syntax."
        ),
    )
    async def list_tagged_conversations(
        context: Context,
        tag_id: Annotated[str, Field(description="Tag id")],
        q: Annotated[str | None, Field(description="Front search syntax")] = None,
        limit: Annotated[int | None, Field(description="Page size")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[ConversationSummary]:
        from frontapp_public_api_client.domain import Conversation

        services = get_services(context)
        items = await services.client.tags.list_conversations(
            tag_id, q=q, limit=limit, page_token=page_token
        )
        return [
            to_summary(Conversation.model_validate(item.to_dict())) for item in items
        ]

    # -- conversation-tag deltas (two-step confirm) -------------------------

    @mcp.tool(
        name="add_tag_to_conversation",
        description=(
            "Add a single tag to a conversation. DELTA — leaves other "
            "tags untouched. For full-set replacement use "
            "update_conversation(tag_ids=[...]) in the conversations vertical."
        ),
    )
    async def add_tag_to_conversation(
        context: Context,
        conversation_id: Annotated[str, Field(description="Conversation id")],
        tag_id: Annotated[str, Field(description="Tag id to apply")],
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "add_tag_to_conversation",
            "conversation_id": conversation_id,
            "tag_id": tag_id,
            "semantics": "delta — does not replace existing tags",
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        success = await services.client.tags.apply_to_conversation(
            conversation_id, tag_ids=[tag_id]
        )
        return {"confirmed": True, "applied": success}

    @mcp.tool(
        name="remove_tag_from_conversation",
        description=(
            "Remove a single tag from a conversation. DELTA — leaves "
            "other tags untouched."
        ),
    )
    async def remove_tag_from_conversation(
        context: Context,
        conversation_id: Annotated[str, Field(description="Conversation id")],
        tag_id: Annotated[str, Field(description="Tag id to remove")],
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "remove_tag_from_conversation",
            "conversation_id": conversation_id,
            "tag_id": tag_id,
            "semantics": "delta — only removes this tag",
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        success = await services.client.tags.remove_from_conversation(
            conversation_id, tag_ids=[tag_id]
        )
        return {"confirmed": True, "removed": success}

    # -- catalog mutations (two-step confirm) -------------------------------

    @mcp.tool(
        name="create_tag",
        description=(
            "Create a workspace-scoped tag. WORKSPACE-WIDE — visible to "
            "every teammate immediately."
        ),
    )
    async def create_tag(
        context: Context,
        name: Annotated[str, Field(description="Tag name, e.g. 'urgent'")],
        description: Annotated[
            str | None, Field(description="Free-form note about the tag")
        ] = None,
        highlight: Annotated[
            HighlightLiteral | None,
            Field(
                description="Color: blue, green, grey, light-blue, orange, pink, purple, red, yellow"
            ),
        ] = None,
        is_visible_in_conversation_lists: Annotated[
            bool, Field(description="Show as a chip on conversation list rows")
        ] = False,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_tag",
            "name": name,
            "highlight": highlight,
            "is_visible_in_conversation_lists": is_visible_in_conversation_lists,
            "scope": "workspace-wide",
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        tag = await services.client.tags.create(
            name=name,
            description=description,
            highlight=highlight,
            is_visible_in_conversation_lists=is_visible_in_conversation_lists,
        )
        return {"confirmed": True, "tag": to_tag_catalog_summary(tag).model_dump()}

    @mcp.tool(
        name="create_child_tag",
        description="Create a child tag under an existing parent. WORKSPACE-WIDE.",
    )
    async def create_child_tag(
        context: Context,
        parent_tag_id: Annotated[str, Field(description="Parent tag id")],
        name: Annotated[str, Field(description="Child tag name")],
        description: Annotated[str | None, Field(description="Free-form note")] = None,
        highlight: Annotated[
            HighlightLiteral | None, Field(description="Color name")
        ] = None,
        is_visible_in_conversation_lists: Annotated[
            bool, Field(description="Show on conversation list rows")
        ] = False,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_child_tag",
            "parent_tag_id": parent_tag_id,
            "name": name,
            "highlight": highlight,
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        tag = await services.client.tags.create_child(
            parent_tag_id,
            name=name,
            description=description,
            highlight=highlight,
            is_visible_in_conversation_lists=is_visible_in_conversation_lists,
        )
        return {"confirmed": True, "tag": to_tag_catalog_summary(tag).model_dump()}

    @mcp.tool(
        name="update_tag",
        description=(
            "Update mutable fields on a tag. WORKSPACE-WIDE — a rename "
            "ripples to every conversation instantly."
        ),
    )
    async def update_tag(
        context: Context,
        tag_id: Annotated[str, Field(description="Tag id")],
        name: Annotated[str | None, Field(description="New name")] = None,
        description: Annotated[str | None, Field(description="Free-form note")] = None,
        highlight: Annotated[
            HighlightLiteral | None, Field(description="Color name")
        ] = None,
        parent_tag_id: Annotated[
            str | None, Field(description="Move tag under a new parent")
        ] = None,
        is_visible_in_conversation_lists: Annotated[
            bool | None, Field(description="Show on conversation list rows")
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        changes = {
            k: v
            for k, v in {
                "name": name,
                "description": description,
                "highlight": highlight,
                "parent_tag_id": parent_tag_id,
                "is_visible_in_conversation_lists": is_visible_in_conversation_lists,
            }.items()
            if v is not None
        }
        preview = {
            "action": "update_tag",
            "tag_id": tag_id,
            "changes": changes,
            "scope": "workspace-wide",
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

        success = await services.client.tags.update(
            tag_id,
            name=name,
            description=description,
            highlight=highlight,
            parent_tag_id=parent_tag_id,
            is_visible_in_conversation_lists=is_visible_in_conversation_lists,
        )
        return {"confirmed": True, "updated": success}

    @mcp.tool(
        name="delete_tag",
        description=(
            "DESTRUCTIVE: permanently delete a tag. Removes it from every "
            "conversation that had it. Irreversible. WORKSPACE-WIDE."
        ),
    )
    async def delete_tag(
        context: Context,
        tag_id: Annotated[str, Field(description="Tag id to delete")],
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "delete_tag",
            "tag_id": tag_id,
            "warning": (
                "PERMANENT: removes this tag from every conversation that "
                "currently has it. Cannot be undone."
            ),
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        success = await services.client.tags.delete(tag_id)
        return {"confirmed": True, "deleted": success}


__all__ = ["register_tools"]
