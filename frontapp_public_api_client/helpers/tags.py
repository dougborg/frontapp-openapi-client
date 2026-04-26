"""Tags helper facade — ergonomic wrappers around generated tag endpoints.

Exposes ``client.tags`` covering the workspace-level tag catalog (``tags/``)
plus the two conversation-side tag delta endpoints (``add_conversation_tag``,
``remove_conversation_tag``). Grouping tag-on-conversation operations on
this helper keeps all tag semantics in one place.

Reads list workspace, company, team, and teammate tag scopes; mutations
cover create/update/delete plus child tags and the conversation-tag deltas.

Two important semantic notes:

- **Delta vs replace.** ``apply_to_conversation`` and
  ``remove_from_conversation`` ADD or REMOVE individual tag ids on a
  conversation. ``conversations.update(tag_ids=[...])`` (when the
  conversations vertical exposes it) REPLACES the entire tag set. Use
  the delta methods when you want to nudge a single tag without
  clobbering the rest.
- **Workspace-wide blast radius.** ``delete`` removes the tag from
  every conversation that had it. ``update`` rename ripples through the
  catalog instantly. Both belong behind two-step confirm at the MCP layer.

Quirks worth knowing:

- The PATCH endpoint module is ``update_a_tag`` (``_a_`` infix flagged
  in ``api-facts.yaml`` ``summary.module_name_quirks``). The body model
  is plain ``UpdateTag``, not ``UpdateATag``.
- ``CreateTagHighlight`` and ``UpdateTagHighlight`` are separate
  generated enums with identical values; ``HighlightLiteral`` is the
  shared Literal alias the helper exposes.
- ``TagResponse.created_at`` / ``updated_at`` are unix-seconds floats
  (not ISO strings) — the ``Tag`` Pydantic projection converts them.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any, Literal

from frontapp_public_api_client.helpers.base import Base

if TYPE_CHECKING:
    from frontapp_public_api_client.domain import Tag


HighlightLiteral = Literal[
    "blue",
    "green",
    "grey",
    "light-blue",
    "orange",
    "pink",
    "purple",
    "red",
    "yellow",
]


class Tags(Base):
    """Ergonomic operations over Frontapp's workspace tag surface."""

    # -- reads --------------------------------------------------------------

    async def list(
        self,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Tag]:
        """List all workspace tags."""
        from frontapp_public_api_client.api.tags import list_tags
        from frontapp_public_api_client.domain import Tag
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client}
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_tags.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Tag.model_validate(t.to_dict()) for t in results]

    async def list_company(
        self,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Tag]:
        """List company-scoped tags (visible across all teams)."""
        from frontapp_public_api_client.api.tags import list_company_tags
        from frontapp_public_api_client.domain import Tag
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client}
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_company_tags.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Tag.model_validate(t.to_dict()) for t in results]

    async def list_for_team(
        self,
        team_id: str,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Tag]:
        """List tags scoped to a team (``"tim_abc"``)."""
        from frontapp_public_api_client.api.tags import list_team_tags
        from frontapp_public_api_client.domain import Tag
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client, "team_id": team_id}
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_team_tags.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Tag.model_validate(t.to_dict()) for t in results]

    async def list_for_teammate(
        self,
        teammate_id: str,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Tag]:
        """List tags scoped to a single teammate (``"tea_abc"``)."""
        from frontapp_public_api_client.api.tags import list_teammate_tags
        from frontapp_public_api_client.domain import Tag
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client, "teammate_id": teammate_id}
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_teammate_tags.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Tag.model_validate(t.to_dict()) for t in results]

    async def get(self, tag_id: str) -> Tag:
        """Fetch one tag by id (e.g. ``"tag_abc"``)."""
        from frontapp_public_api_client.api.tags import get_tag
        from frontapp_public_api_client.domain import Tag
        from frontapp_public_api_client.models.tag_response import TagResponse
        from frontapp_public_api_client.utils import unwrap_as

        response = await get_tag.asyncio_detailed(tag_id=tag_id, client=self._client)
        tag = unwrap_as(response, TagResponse)
        return Tag.model_validate(tag.to_dict())

    async def list_children(self, tag_id: str) -> builtins.list[Tag]:
        """List child tags of a parent tag.

        The generated endpoint takes no pagination params (Front returns
        the full child set in one shot).
        """
        from frontapp_public_api_client.api.tags import list_tag_children
        from frontapp_public_api_client.domain import Tag
        from frontapp_public_api_client.utils import unwrap

        response = await list_tag_children.asyncio_detailed(
            tag_id=tag_id, client=self._client
        )
        parsed = unwrap(response)
        results = getattr(parsed, "field_results", None) or []
        return [Tag.model_validate(t.to_dict()) for t in results]

    async def list_conversations(
        self,
        tag_id: str,
        *,
        q: str | None = None,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[Any]:
        """List conversations bearing this tag. Returns raw attrs models.

        The MCP layer projects to ``ConversationSummary`` — no domain
        ``Conversation`` projection is applied here so callers picking up
        the helper directly can choose their own shape.
        """
        from frontapp_public_api_client.api.tags import list_tagged_conversations
        from frontapp_public_api_client.utils import unwrap

        kwargs: dict[str, Any] = {"client": self._client, "tag_id": tag_id}
        if q is not None:
            kwargs["q"] = q
        if limit is not None:
            kwargs["limit"] = limit
        if page_token is not None:
            kwargs["page_token"] = page_token

        response = await list_tagged_conversations.asyncio_detailed(**kwargs)
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    # -- catalog mutations --------------------------------------------------

    async def create(
        self,
        *,
        name: str,
        description: str | None = None,
        highlight: HighlightLiteral | None = None,
        is_visible_in_conversation_lists: bool = False,
    ) -> Tag:
        """Create a new workspace-scoped tag.

        Workspace-wide change — visible to every teammate immediately.
        """
        from frontapp_public_api_client.api.tags import create_tag
        from frontapp_public_api_client.domain import Tag
        from frontapp_public_api_client.models.create_tag import CreateTag
        from frontapp_public_api_client.models.create_tag_highlight import (
            CreateTagHighlight,
        )
        from frontapp_public_api_client.models.tag_response import TagResponse
        from frontapp_public_api_client.utils import unwrap_as

        kwargs: dict[str, Any] = {
            "name": name,
            "is_visible_in_conversation_lists": is_visible_in_conversation_lists,
        }
        if description is not None:
            kwargs["description"] = description
        if highlight is not None:
            kwargs["highlight"] = CreateTagHighlight(highlight)

        body = CreateTag(**kwargs)
        response = await create_tag.asyncio_detailed(client=self._client, body=body)
        tag = unwrap_as(response, TagResponse)
        return Tag.model_validate(tag.to_dict())

    async def create_child(
        self,
        parent_tag_id: str,
        *,
        name: str,
        description: str | None = None,
        highlight: HighlightLiteral | None = None,
        is_visible_in_conversation_lists: bool = False,
    ) -> Tag:
        """Create a child tag under an existing parent tag."""
        from frontapp_public_api_client.api.tags import create_child_tag
        from frontapp_public_api_client.domain import Tag
        from frontapp_public_api_client.models.create_tag import CreateTag
        from frontapp_public_api_client.models.create_tag_highlight import (
            CreateTagHighlight,
        )
        from frontapp_public_api_client.models.tag_response import TagResponse
        from frontapp_public_api_client.utils import unwrap_as

        kwargs: dict[str, Any] = {
            "name": name,
            "is_visible_in_conversation_lists": is_visible_in_conversation_lists,
        }
        if description is not None:
            kwargs["description"] = description
        if highlight is not None:
            kwargs["highlight"] = CreateTagHighlight(highlight)

        body = CreateTag(**kwargs)
        response = await create_child_tag.asyncio_detailed(
            tag_id=parent_tag_id, client=self._client, body=body
        )
        tag = unwrap_as(response, TagResponse)
        return Tag.model_validate(tag.to_dict())

    async def update(
        self,
        tag_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        highlight: HighlightLiteral | None = None,
        parent_tag_id: str | None = None,
        is_visible_in_conversation_lists: bool | None = None,
    ) -> bool:
        """Update mutable fields on a tag (PATCH).

        Workspace-wide change — a rename ripples to every conversation
        instantly. Returns True on the documented 204 No Content.
        """
        from frontapp_public_api_client.api.tags import update_a_tag
        from frontapp_public_api_client.models.update_tag import UpdateTag
        from frontapp_public_api_client.models.update_tag_highlight import (
            UpdateTagHighlight,
        )
        from frontapp_public_api_client.utils import is_success

        kwargs: dict[str, Any] = {}
        if name is not None:
            kwargs["name"] = name
        if description is not None:
            kwargs["description"] = description
        if highlight is not None:
            kwargs["highlight"] = UpdateTagHighlight(highlight)
        if parent_tag_id is not None:
            kwargs["parent_tag_id"] = parent_tag_id
        if is_visible_in_conversation_lists is not None:
            kwargs["is_visible_in_conversation_lists"] = (
                is_visible_in_conversation_lists
            )

        body = UpdateTag(**kwargs)
        response = await update_a_tag.asyncio_detailed(
            tag_id=tag_id, client=self._client, body=body
        )
        return is_success(response)

    async def delete(self, tag_id: str) -> bool:
        """Permanently delete a tag.

        Destructive: removes the tag from every conversation that had it.
        Front does not soft-delete tags — the operation is irreversible.
        """
        from frontapp_public_api_client.api.tags import delete_tag
        from frontapp_public_api_client.utils import is_success

        response = await delete_tag.asyncio_detailed(tag_id=tag_id, client=self._client)
        return is_success(response)

    # -- conversation-tag delta operations ----------------------------------

    async def apply_to_conversation(
        self, conversation_id: str, *, tag_ids: builtins.list[str]
    ) -> bool:
        """Add tags to a conversation (delta — does NOT replace existing).

        Different from ``client.conversations.update(tag_ids=[...])``,
        which REPLACES the full tag set. Use this method to add a single
        tag without clobbering whatever tags are already attached.
        """
        from frontapp_public_api_client.api.conversations import add_conversation_tag
        from frontapp_public_api_client.models.tag_ids import TagIds
        from frontapp_public_api_client.utils import is_success

        body = TagIds(tag_ids=tag_ids)
        response = await add_conversation_tag.asyncio_detailed(
            conversation_id=conversation_id, client=self._client, body=body
        )
        return is_success(response)

    async def remove_from_conversation(
        self, conversation_id: str, *, tag_ids: builtins.list[str]
    ) -> bool:
        """Remove tags from a conversation (delta — only the named ids).

        Mirror of ``apply_to_conversation``. Other tags on the
        conversation are left intact.
        """
        from frontapp_public_api_client.api.conversations import (
            remove_conversation_tag,
        )
        from frontapp_public_api_client.models.tag_ids import TagIds
        from frontapp_public_api_client.utils import is_success

        body = TagIds(tag_ids=tag_ids)
        response = await remove_conversation_tag.asyncio_detailed(
            conversation_id=conversation_id, client=self._client, body=body
        )
        return is_success(response)


__all__ = ["HighlightLiteral", "Tags"]
