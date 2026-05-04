"""MCP tools for Front's Knowledge Base — read + contribute (drafts only).

Two distinct workflows the same tool surface supports:

1. **Retrieval** — list KBs, list categories, list / get articles. Reads,
   no confirm gate.
2. **Contribute** — create / update articles + categories. Two-step
   ``confirm_or_preview`` gate on every mutation.

## Drafts only

Per the project policy (mirroring ADR-0016's drafts-first outbound
philosophy applied to KB content): **the MCP tools never publish a KB
article.** ``create_kb_article`` and ``update_kb_article`` do not accept
a ``status`` argument; the tools always pass ``status="draft"`` to the
helper for create, and omit ``status`` from update bodies so the
existing draft / published state is preserved. Publishing is a
human-in-Front's-UI action.

The Python helper layer (``client.knowledge_bases.create_article`` /
``update_article``) **does** retain the ``status`` kwarg for library
callers — Python scripts can publish programmatically. The MCP tools
are the agent-safety boundary, not the helper.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from pydantic import Field

from frontapp_mcp.projections import (
    KbArticleSummary,
    KbCategoryRef,
    KbRef,
    to_kb_article_summary,
    to_kb_category_ref,
    to_kb_ref,
)
from frontapp_mcp.services import get_services
from frontapp_mcp.tools.schemas import confirm_or_preview


def _content_preview(content: str | None, max_chars: int = 200) -> str | None:
    """Truncate content to a short preview for the confirm-gate display."""
    if content is None:
        return None
    if len(content) <= max_chars:
        return content
    return content[:max_chars] + "…"


def register_tools(mcp: FastMCP) -> None:
    """Register knowledge_bases-related tools with the FastMCP server."""

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    @mcp.tool(
        name="list_knowledge_bases",
        description=(
            "List every knowledge base in the workspace. Use to find a "
            "`knb_*` id before listing articles or categories. Returns "
            "id + name pairs."
        ),
    )
    async def list_knowledge_bases(context: Context) -> list[KbRef]:
        services = get_services(context)
        kbs = await services.client.knowledge_bases.list()
        return [to_kb_ref(kb) for kb in kbs]

    @mcp.tool(
        name="get_kb",
        description=(
            "Fetch one knowledge base by id. Set `with_content=True` to "
            "include the localized body; pass `locale='fr'` (or another "
            "locale code) for non-default locales."
        ),
    )
    async def get_kb(
        context: Context,
        knowledge_base_id: Annotated[str, Field(description="`knb_*` id")],
        with_content: Annotated[
            bool, Field(description="Include the KB body content.")
        ] = False,
        locale: Annotated[
            str | None,
            Field(
                description=("Locale code (e.g. 'en', 'fr'). None = default locale.")
            ),
        ] = None,
    ) -> dict[str, Any]:
        services = get_services(context)
        kb = await services.client.knowledge_bases.get(
            knowledge_base_id, with_content=with_content, locale=locale
        )
        return kb.to_dict()

    @mcp.tool(
        name="list_kb_articles",
        description=(
            "List articles in a knowledge base (slim — no body content). "
            "Cursor-paginated; pass `page_token` from the previous response "
            "to fetch the next page. Use `get_kb_article(article_id, "
            "with_content=True)` afterwards to fetch full body for an "
            "article you've picked."
        ),
    )
    async def list_kb_articles(
        context: Context,
        knowledge_base_id: Annotated[str, Field(description="`knb_*` id")],
        limit: Annotated[
            int | None, Field(description="Max items per page (default ~50).")
        ] = None,
        page_token: Annotated[
            str | None, Field(description="Cursor from previous page's response.")
        ] = None,
    ) -> list[KbArticleSummary]:
        services = get_services(context)
        articles = await services.client.knowledge_bases.list_articles(
            knowledge_base_id, limit=limit, page_token=page_token
        )
        return [to_kb_article_summary(a) for a in articles]

    @mcp.tool(
        name="list_kb_articles_in_category",
        description=(
            "List articles within a specific category (slim). Cursor-"
            "paginated. Use to scope retrieval to a topic-relevant subset "
            "of the KB."
        ),
    )
    async def list_kb_articles_in_category(
        context: Context,
        category_id: Annotated[str, Field(description="`kbc_*` id")],
        limit: Annotated[int | None, Field(description="Max items per page.")] = None,
        page_token: Annotated[
            str | None, Field(description="Cursor from previous page.")
        ] = None,
    ) -> list[KbArticleSummary]:
        services = get_services(context)
        articles = await services.client.knowledge_bases.list_articles_in_category(
            category_id, limit=limit, page_token=page_token
        )
        return [to_kb_article_summary(a) for a in articles]

    @mcp.tool(
        name="get_kb_article",
        description=(
            "Fetch a single article. By default returns the full body "
            "content (`with_content=True`) — the agent's primary use "
            "case is to quote or paraphrase the content. Pass "
            "`with_content=False` for catalog-style metadata only. "
            "`locale='fr'` etc. fetches a non-default locale; defaults "
            "to the workspace's default locale."
        ),
    )
    async def get_kb_article(
        context: Context,
        article_id: Annotated[str, Field(description="`kba_*` id")],
        with_content: Annotated[
            bool, Field(description="Include body content (default True).")
        ] = True,
        locale: Annotated[
            str | None,
            Field(description="Locale code; None = default locale."),
        ] = None,
    ) -> dict[str, Any]:
        services = get_services(context)
        article = await services.client.knowledge_bases.get_article(
            article_id, with_content=with_content, locale=locale
        )
        return article.to_dict()

    @mcp.tool(
        name="list_kb_categories",
        description=(
            "List categories in a knowledge base. Cursor-paginated. Use "
            "to find a `kbc_*` id before listing articles in a category "
            "or creating a new article under one."
        ),
    )
    async def list_kb_categories(
        context: Context,
        knowledge_base_id: Annotated[str, Field(description="`knb_*` id")],
        limit: Annotated[int | None, Field(description="Max items per page.")] = None,
        page_token: Annotated[
            str | None, Field(description="Cursor from previous page.")
        ] = None,
    ) -> list[KbCategoryRef]:
        services = get_services(context)
        categories = await services.client.knowledge_bases.list_categories(
            knowledge_base_id, limit=limit, page_token=page_token
        )
        return [to_kb_category_ref(c) for c in categories]

    # ------------------------------------------------------------------
    # Contribute mutations (drafts only — see module docstring)
    # ------------------------------------------------------------------

    @mcp.tool(
        name="create_kb_article",
        description=(
            "Create a NEW knowledge-base article AS A DRAFT. The agent "
            "cannot publish — drafts await human review in Front's UI "
            "(by design, mirroring drafts-first outbound for replies). "
            "Two-step confirm: confirm=False returns a preview; "
            "confirm=True creates the draft."
        ),
    )
    async def create_kb_article(
        context: Context,
        knowledge_base_id: Annotated[str, Field(description="`knb_*` id")],
        subject: Annotated[str | None, Field(description="Article title.")] = None,
        content: Annotated[
            str | None,
            Field(description="Article body (HTML or markdown)."),
        ] = None,
        category_id: Annotated[
            str | None,
            Field(description="Optional `kbc_*` to file the article under."),
        ] = None,
        author_id: Annotated[
            str | None,
            Field(description="Optional `tea_*` of the authoring teammate."),
        ] = None,
        locale: Annotated[
            str | None,
            Field(description="Locale code; None = default locale."),
        ] = None,
        confirm: Annotated[
            bool, Field(description="Must be true to create the draft.")
        ] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_kb_article",
            "knowledge_base_id": knowledge_base_id,
            "subject": subject,
            "body_preview": _content_preview(content),
            "category_id": category_id,
            "author_id": author_id,
            "locale": locale,
            "status": "draft",  # always — see module docstring
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        # Always pass status='draft' — MCP layer never publishes.
        article = await services.client.knowledge_bases.create_article(
            knowledge_base_id,
            subject=subject,
            content=content,
            category_id=category_id,
            author_id=author_id,
            status="draft",
            locale=locale,
        )
        return {"confirmed": True, "article": article.to_dict()}

    @mcp.tool(
        name="update_kb_article",
        description=(
            "Update an existing KB article. Cannot change `status` — "
            "the tool preserves whatever publication state the article "
            "already has. (To publish a draft, a human flips it in "
            "Front's UI.) Two-step confirm."
        ),
    )
    async def update_kb_article(
        context: Context,
        article_id: Annotated[str, Field(description="`kba_*` id")],
        subject: Annotated[str | None, Field(description="New title.")] = None,
        content: Annotated[str | None, Field(description="New body content.")] = None,
        author_id: Annotated[
            str | None, Field(description="New author `tea_*` id.")
        ] = None,
        locale: Annotated[
            str | None,
            Field(description="Locale code; None = default locale."),
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true to apply.")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "update_kb_article",
            "article_id": article_id,
            "subject": subject,
            "body_preview": _content_preview(content),
            "author_id": author_id,
            "locale": locale,
            "note": "status unchanged — agents cannot flip draft/published",
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        # Note: status omitted entirely — preserves the article's existing
        # publication state. Agents cannot publish or unpublish via the
        # MCP layer; that's a human-in-Front's-UI action.
        article = await services.client.knowledge_bases.update_article(
            article_id,
            subject=subject,
            content=content,
            author_id=author_id,
            status=None,
            locale=locale,
        )
        return {"confirmed": True, "article": article.to_dict()}

    @mcp.tool(
        name="create_kb_category",
        description=(
            "Create a new category within a knowledge base. Categories "
            "organize articles. Two-step confirm."
        ),
    )
    async def create_kb_category(
        context: Context,
        knowledge_base_id: Annotated[str, Field(description="`knb_*` id")],
        name: Annotated[str, Field(description="Category name.")],
        parent_category_id: Annotated[
            str | None,
            Field(description="Optional parent `kbc_*` for nesting."),
        ] = None,
        description: Annotated[
            str | None,
            Field(description="Freeform description."),
        ] = None,
        locale: Annotated[
            str | None,
            Field(description="Locale code; None = default locale."),
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true to create.")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "create_kb_category",
            "knowledge_base_id": knowledge_base_id,
            "name": name,
            "parent_category_id": parent_category_id,
            "description": description,
            "locale": locale,
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        category = await services.client.knowledge_bases.create_category(
            knowledge_base_id,
            name=name,
            parent_category_id=parent_category_id,
            description=description,
            locale=locale,
        )
        return {"confirmed": True, "category": category.to_dict()}

    @mcp.tool(
        name="update_kb_category",
        description=(
            "Update an existing KB category (name and/or description). "
            "Two-step confirm."
        ),
    )
    async def update_kb_category(
        context: Context,
        category_id: Annotated[str, Field(description="`kbc_*` id")],
        name: Annotated[str | None, Field(description="New name.")] = None,
        description: Annotated[
            str | None, Field(description="New description.")
        ] = None,
        locale: Annotated[
            str | None,
            Field(description="Locale code; None = default locale."),
        ] = None,
        confirm: Annotated[bool, Field(description="Must be true to apply.")] = False,
    ) -> dict[str, Any]:
        services = get_services(context)
        preview = {
            "action": "update_kb_category",
            "category_id": category_id,
            "name": name,
            "description": description,
            "locale": locale,
        }
        gate = confirm_or_preview(preview=preview, confirm=confirm)
        if gate is not None:
            return gate

        category = await services.client.knowledge_bases.update_category(
            category_id,
            name=name,
            description=description,
            locale=locale,
        )
        return {"confirmed": True, "category": category.to_dict()}
