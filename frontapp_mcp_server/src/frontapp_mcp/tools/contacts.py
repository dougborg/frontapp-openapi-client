"""MCP tools for Frontapp contacts.

Twelve tools spanning Front's three contact-related generated tags
(``contacts``, ``contact_handles``, ``contact_notes``):

- 5 reads (cached 30s): list / get / lookup-by-email / list_conversations /
  list_notes
- 7 mutations (two-step confirm): create / update / merge / delete /
  add_note / add_handle / delete_handle

The destructive mutations (``merge_contacts``, ``delete_contact``) carry
extra-stern confirmation copy because they are irreversible - merge moves
all conversations from N-1 contacts to a target and discards the rest;
delete removes the contact and its handles entirely.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.projections import (
    ContactSummary,
    ConversationSummary,
    to_contact_summary,
    to_summary,
)
from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import (
    DESTRUCTIVE,
    confirm_or_preview,
)

# Mirrors ``ContactHandleSource`` in the domain module; duplicated here
# (rather than imported) because Pydantic Field annotations are evaluated
# at runtime and the domain module already exports a ``Literal`` alias.
ContactHandleSourceLiteral = Literal[
    "custom", "email", "facebook", "front_chat", "intercom", "phone", "twitter"
]


def register_tools(mcp: FastMCP) -> None:
    """Register contact-related tools with the FastMCP server."""

    # -- reads --------------------------------------------------------------

    @mcp.tool(
        name="list_contacts",
        description=(
            "List contacts in the workspace. Pass q for partial-match "
            "search across handles/names/descriptions."
        ),
    )
    async def list_contacts(
        context: Context,
        q: Annotated[
            str | None,
            Field(description="Partial-match query against handles/names"),
        ] = None,
        limit: Annotated[
            int | None, Field(description="Page size (max 100, default 50)")
        ] = None,
        page_token: Annotated[
            str | None, Field(description="Cursor from a prior pagination.next")
        ] = None,
    ) -> list[ContactSummary]:
        services = get_services(context)
        contacts = await services.client.contacts.list(
            q=q, limit=limit, page_token=page_token
        )
        return [to_contact_summary(c) for c in contacts]

    @mcp.tool(
        name="get_contact",
        description="Fetch full details for one contact by id (e.g. 'crd_abc').",
    )
    async def get_contact(
        context: Context,
        contact_id: Annotated[str, Field(description="Contact id, e.g. 'crd_abc'")],
    ) -> ContactSummary:
        services = get_services(context)
        contact = await services.client.contacts.get(contact_id)
        return to_contact_summary(contact)

    @mcp.tool(
        name="lookup_contact_by_email",
        description=(
            "Best-effort lookup of contacts by email. Wraps list_contacts(q=email). "
            "Returns 0..n matches; alias/partial-match contacts may be missed."
        ),
    )
    async def lookup_contact_by_email(
        context: Context,
        email: Annotated[
            str, Field(description="Email to search for, e.g. 'a@example.com'")
        ],
    ) -> list[ContactSummary]:
        services = get_services(context)
        contacts = await services.client.contacts.search_by_email(email)
        return [to_contact_summary(c) for c in contacts]

    @mcp.tool(
        name="list_team_contacts",
        description="List contacts owned by a team (`team_id` like 'tim_abc').",
    )
    async def list_team_contacts(
        context: Context,
        team_id: Annotated[str, Field(description="Team id, e.g. 'tim_abc'")],
        q: Annotated[str | None, Field(description="Partial-match query")] = None,
        limit: Annotated[int | None, Field(description="Page size")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[ContactSummary]:
        services = get_services(context)
        contacts = await services.client.contacts.list_for_team(
            team_id, q=q, limit=limit, page_token=page_token
        )
        return [to_contact_summary(c) for c in contacts]

    @mcp.tool(
        name="list_teammate_contacts",
        description="List contacts owned by a teammate (`teammate_id` like 'tea_abc').",
    )
    async def list_teammate_contacts(
        context: Context,
        teammate_id: Annotated[str, Field(description="Teammate id, e.g. 'tea_abc'")],
        q: Annotated[str | None, Field(description="Partial-match query")] = None,
        limit: Annotated[int | None, Field(description="Page size")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[ContactSummary]:
        services = get_services(context)
        contacts = await services.client.contacts.list_for_teammate(
            teammate_id, q=q, limit=limit, page_token=page_token
        )
        return [to_contact_summary(c) for c in contacts]

    @mcp.tool(
        name="list_contact_conversations",
        description=(
            "List conversations involving this contact, projected to "
            "compact ConversationSummary entries."
        ),
    )
    async def list_contact_conversations(
        context: Context,
        contact_id: Annotated[str, Field(description="Contact id")],
        q: Annotated[str | None, Field(description="Front search syntax")] = None,
        limit: Annotated[int | None, Field(description="Page size")] = None,
        page_token: Annotated[str | None, Field(description="Cursor")] = None,
    ) -> list[ConversationSummary]:
        from frontapp_public_api_client.domain import Conversation

        services = get_services(context)
        items = await services.client.contacts.list_conversations(
            contact_id, q=q, limit=limit, page_token=page_token
        )
        # FastMCP serializes the ConversationSummary list; no need for manual
        # .model_dump() (one fewer pass per item on a 50-item list page).
        return [
            to_summary(Conversation.model_validate(item.to_dict())) for item in items
        ]

    @mcp.tool(
        name="list_contact_notes",
        description=(
            "List internal teammate notes attached to a contact "
            "(never visible to the customer)."
        ),
    )
    async def list_contact_notes(
        context: Context,
        contact_id: Annotated[str, Field(description="Contact id")],
    ) -> list[dict[str, Any]]:
        services = get_services(context)
        notes = await services.client.contacts.list_notes(contact_id)
        return [n.to_dict() for n in notes]

    # -- mutations (two-step confirm) ---------------------------------------

    @mcp.tool(
        name="create_contact",
        description=(
            "Create a new workspace-scoped contact. handles is required: a "
            "list of {handle, source} dicts, where source is one of email, "
            "phone, custom, facebook, front_chat, intercom, twitter."
        ),
        annotations=DESTRUCTIVE,
    )
    async def create_contact(
        context: Context,
        handles: Annotated[
            list[dict[str, str]],
            Field(description="List of {handle, source} dicts; required by Front"),
        ],
        name: Annotated[str | None, Field(description="Display name")] = None,
        description: Annotated[
            str | None, Field(description="Free-form notes about the contact")
        ] = None,
        links: Annotated[
            list[str] | None, Field(description="External profile URLs")
        ] = None,
        group_names: Annotated[
            list[str] | None,
            Field(description="Group names to assign (creates if absent)"),
        ] = None,
        list_names: Annotated[
            list[str] | None,
            Field(description="Contact list names to add to"),
        ] = None,
        confirm: Annotated[
            bool, Field(description="Must be true to create the contact")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_contact",
            "name": name,
            "handles": handles,
            "description": description,
            "group_names": group_names,
            "list_names": list_names,
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        contact = await services.client.contacts.create(
            handles=handles,
            name=name,
            description=description,
            links=links,
            group_names=group_names,
            list_names=list_names,
        )
        return {"confirmed": True, "contact": to_contact_summary(contact).model_dump()}

    @mcp.tool(
        name="create_team_contact",
        description="Create a contact owned by a team. Same shape as create_contact, scoped to a team_id.",
        annotations=DESTRUCTIVE,
    )
    async def create_team_contact(
        context: Context,
        team_id: Annotated[str, Field(description="Team id, e.g. 'tim_abc'")],
        handles: Annotated[
            list[dict[str, str]],
            Field(description="List of {handle, source} dicts"),
        ],
        name: Annotated[str | None, Field(description="Display name")] = None,
        description: Annotated[str | None, Field(description="Free-form notes")] = None,
        links: Annotated[list[str] | None, Field(description="External URLs")] = None,
        group_names: Annotated[
            list[str] | None, Field(description="Group names")
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_team_contact",
            "team_id": team_id,
            "name": name,
            "handles": handles,
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        contact = await services.client.contacts.create_for_team(
            team_id,
            handles=handles,
            name=name,
            description=description,
            links=links,
            group_names=group_names,
        )
        return {"confirmed": True, "contact": to_contact_summary(contact).model_dump()}

    @mcp.tool(
        name="create_teammate_contact",
        description="Create a contact owned by a teammate. Scoped to a teammate_id.",
        annotations=DESTRUCTIVE,
    )
    async def create_teammate_contact(
        context: Context,
        teammate_id: Annotated[str, Field(description="Teammate id, e.g. 'tea_abc'")],
        handles: Annotated[
            list[dict[str, str]],
            Field(description="List of {handle, source} dicts"),
        ],
        name: Annotated[str | None, Field(description="Display name")] = None,
        description: Annotated[str | None, Field(description="Free-form notes")] = None,
        links: Annotated[list[str] | None, Field(description="External URLs")] = None,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_teammate_contact",
            "teammate_id": teammate_id,
            "name": name,
            "handles": handles,
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        contact = await services.client.contacts.create_for_teammate(
            teammate_id,
            handles=handles,
            name=name,
            description=description,
            links=links,
        )
        return {"confirmed": True, "contact": to_contact_summary(contact).model_dump()}

    @mcp.tool(
        name="update_contact",
        description=(
            "Update mutable scalar fields on a contact. Note: handle "
            "changes go through add_contact_handle / delete_contact_handle, "
            "NOT this tool — Front's PATCH body doesn't accept handles."
        ),
        annotations=DESTRUCTIVE,
    )
    async def update_contact(
        context: Context,
        contact_id: Annotated[str, Field(description="Contact id")],
        name: Annotated[str | None, Field(description="Display name")] = None,
        description: Annotated[str | None, Field(description="Free-form notes")] = None,
        links: Annotated[list[str] | None, Field(description="External URLs")] = None,
        group_names: Annotated[
            list[str] | None, Field(description="Replace group memberships")
        ] = None,
        list_names: Annotated[
            list[str] | None, Field(description="Replace list memberships")
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        changes = {
            k: v
            for k, v in {
                "name": name,
                "description": description,
                "links": links,
                "group_names": group_names,
                "list_names": list_names,
            }.items()
            if v is not None
        }
        preview = {
            "action": "update_contact",
            "contact_id": contact_id,
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

        success = await services.client.contacts.update(
            contact_id,
            name=name,
            description=description,
            links=links,
            group_names=group_names,
            list_names=list_names,
        )
        return {"confirmed": True, "updated": success}

    @mcp.tool(
        name="merge_contacts",
        description=(
            "DESTRUCTIVE: merge multiple contacts into one. Irreversible. All "
            "conversations from the non-target contacts move to the target; "
            "the merged contacts are deleted. If target_contact_id is "
            "omitted, Front picks the target. Two-step confirm."
        ),
        annotations=DESTRUCTIVE,
    )
    async def merge_contacts(
        context: Context,
        contact_ids: Annotated[
            list[str], Field(description="Contact ids to merge (>=2)")
        ],
        target_contact_id: Annotated[
            str | None,
            Field(description="Optional: contact id to keep; Front picks if omitted"),
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "merge_contacts",
            "contact_ids": contact_ids,
            "target_contact_id": target_contact_id,
            "warning": "IRREVERSIBLE: merged contacts are deleted; their conversations move to the target.",
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        contact = await services.client.contacts.merge(
            contact_ids=contact_ids, target_contact_id=target_contact_id
        )
        return {"confirmed": True, "contact": to_contact_summary(contact).model_dump()}

    @mcp.tool(
        name="delete_contact",
        description=(
            "DESTRUCTIVE: permanently delete a contact and all its handles. "
            "Cannot be undone. Two-step confirm."
        ),
        annotations=DESTRUCTIVE,
    )
    async def delete_contact(
        context: Context,
        contact_id: Annotated[str, Field(description="Contact id to delete")],
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "delete_contact",
            "contact_id": contact_id,
            "warning": "PERMANENT: removes the contact and all its handles. Cannot be undone.",
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        success = await services.client.contacts.delete(contact_id)
        return {"confirmed": True, "deleted": success}

    @mcp.tool(
        name="add_contact_note",
        description="Add an internal teammate note to a contact (not visible to customer).",
        annotations=DESTRUCTIVE,
    )
    async def add_contact_note(
        context: Context,
        contact_id: Annotated[str, Field(description="Contact id")],
        body: Annotated[str, Field(description="Note body")],
        author_id: Annotated[
            str,
            Field(description="Teammate id authoring the note; required by Front"),
        ],
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "add_contact_note",
            "contact_id": contact_id,
            "author_id": author_id,
            "body_preview": body[:200] + ("…" if len(body) > 200 else ""),
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        response = await services.client.contacts.add_note(
            contact_id, body=body, author_id=author_id
        )
        return {"confirmed": True, "status_code": response.status_code}

    @mcp.tool(
        name="add_contact_handle",
        description="Add a handle (email/phone/etc.) to an existing contact.",
        annotations=DESTRUCTIVE,
    )
    async def add_contact_handle(
        context: Context,
        contact_id: Annotated[str, Field(description="Contact id")],
        handle: Annotated[
            str, Field(description="Handle value, e.g. 'a@example.com', '+15551234'")
        ],
        source: Annotated[
            ContactHandleSourceLiteral,
            Field(description="Channel kind"),
        ],
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "add_contact_handle",
            "contact_id": contact_id,
            "handle": handle,
            "source": source,
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        success = await services.client.contacts.add_handle(
            contact_id, handle=handle, source=source
        )
        return {"confirmed": True, "added": success}

    @mcp.tool(
        name="delete_contact_handle",
        description=(
            "Remove a handle from a contact. Pass force=true to delete the "
            "contact's last handle (would otherwise leave it unreachable)."
        ),
        annotations=DESTRUCTIVE,
    )
    async def delete_contact_handle(
        context: Context,
        contact_id: Annotated[str, Field(description="Contact id")],
        handle: Annotated[str, Field(description="Handle value to remove")],
        source: Annotated[
            ContactHandleSourceLiteral,
            Field(description="Channel kind"),
        ],
        force: Annotated[
            bool | None,
            Field(description="Allow deleting the last remaining handle"),
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "delete_contact_handle",
            "contact_id": contact_id,
            "handle": handle,
            "source": source,
            "force": force,
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        success = await services.client.contacts.delete_handle(
            contact_id, handle=handle, source=source, force=force
        )
        return {"confirmed": True, "deleted": success}


__all__ = ["register_tools"]
