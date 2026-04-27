"""Knowledge Base helper facade — reads + contribute path.

Wraps Front's three KB-tagged generated modules (`knowledge_bases`,
`knowledge_base_articles`, `knowledge_base_categories`) into one
ergonomic surface. Two distinct workflows the same helper supports:

1. **Retrieval** (read): list KBs → list categories → list / iter
   articles → get article body. Used to surface relevant KB content
   during a conversation or paraphrase into a reply.
2. **Contribute** (mutate): create article, update article (with
   locale-aware content), create category, update category. Used to
   convert a conversation resolution into a new KB article, or amend
   an existing article with new info.

The helper hides two generated-API quirks from callers:

- **`_a_` infix** on 11 of the 26 KB modules
  (`get_a_knowledge_base_article`, `list_articles_in_a_knowledge_base`,
  etc.). Callers see `get_article(article_id)`,
  `list_articles(knowledge_base_id)`.
- **Locale variants**: every read-with-content / create / update has
  a default-locale and a specified-locale generated module. The helper
  takes a single ``locale=None`` argument that routes to the right
  module — ``locale=None`` hits the default-locale variant; any other
  value (e.g. ``locale="fr"``) hits the specified-locale variant.

Out of scope (covered by issue #87):

- ``create_a_knowledge_base`` / ``update_knowledge_base*`` (KB-level admin)
- ``delete_an_article`` / ``delete_a_knowledge_base_category`` (destructive)
"""

from __future__ import annotations

import builtins
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Literal

from frontapp_public_api_client.helpers.base import Base

if TYPE_CHECKING:
    from frontapp_public_api_client.models.knowledge_base_article_response import (
        KnowledgeBaseArticleResponse,
    )
    from frontapp_public_api_client.models.knowledge_base_article_slim_response import (
        KnowledgeBaseArticleSlimResponse,
    )
    from frontapp_public_api_client.models.knowledge_base_category_response import (
        KnowledgeBaseCategoryResponse,
    )
    from frontapp_public_api_client.models.knowledge_base_category_slim_response import (
        KnowledgeBaseCategorySlimResponse,
    )
    from frontapp_public_api_client.models.knowledge_base_response import (
        KnowledgeBaseResponse,
    )
    from frontapp_public_api_client.models.knowledge_base_slim_response import (
        KnowledgeBaseSlimResponse,
    )


class KnowledgeBases(Base):
    """Ergonomic operations over Front's ``/knowledge_bases*`` endpoints."""

    # -- knowledge bases ----------------------------------------------------

    async def list(self) -> builtins.list[KnowledgeBaseSlimResponse]:
        """List every knowledge base in the workspace.

        Front's ``/knowledge_bases`` endpoint is a flat list with no
        pagination — returns all KBs in one response. Callers that need
        to walk a *very* large set should fall back to the generated
        endpoint directly (they would have already seen this comment if
        they did).
        """
        from frontapp_public_api_client.api.knowledge_bases import (
            list_knowledge_bases,
        )
        from frontapp_public_api_client.utils import unwrap

        response = await list_knowledge_bases.asyncio_detailed(client=self._client)
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def get(
        self,
        knowledge_base_id: str,
        *,
        with_content: bool = False,
        locale: str | None = None,
    ) -> KnowledgeBaseSlimResponse | KnowledgeBaseResponse:
        """Fetch one knowledge base.

        Args:
            knowledge_base_id: ``knb_*`` id.
            with_content: When ``True``, returns the full
                ``KnowledgeBaseResponse`` (including localized body).
                When ``False`` (default), returns the slim variant
                without body content.
            locale: When ``with_content=True``, ``None`` (default) hits
                the default-locale endpoint; any other value hits the
                specified-locale variant. Ignored when
                ``with_content=False``.
        """
        from frontapp_public_api_client.utils import unwrap_as

        if with_content:
            from frontapp_public_api_client.models.knowledge_base_response import (
                KnowledgeBaseResponse,
            )

            if locale is None:
                from frontapp_public_api_client.api.knowledge_bases import (
                    get_a_knowledge_base_with_content_in_default_locale as _get,
                )

                response = await _get.asyncio_detailed(
                    knowledge_base_id, client=self._client
                )
            else:
                from frontapp_public_api_client.api.knowledge_bases import (
                    get_a_knowledge_base_with_content_in_specified_locale as _get,
                )

                response = await _get.asyncio_detailed(
                    knowledge_base_id, locale, client=self._client
                )
            return unwrap_as(response, KnowledgeBaseResponse)

        from frontapp_public_api_client.api.knowledge_bases import get_a_knowledge_base
        from frontapp_public_api_client.models.knowledge_base_slim_response import (
            KnowledgeBaseSlimResponse,
        )

        response = await get_a_knowledge_base.asyncio_detailed(
            knowledge_base_id, client=self._client
        )
        return unwrap_as(response, KnowledgeBaseSlimResponse)

    # -- articles -----------------------------------------------------------

    async def list_articles(
        self,
        knowledge_base_id: str,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[KnowledgeBaseArticleSlimResponse]:
        """List one page of articles in a KB (cursor-paginated)."""
        from frontapp_public_api_client.api.knowledge_base_articles import (
            list_articles_in_a_knowledge_base,
        )
        from frontapp_public_api_client.domain.converters import to_unset
        from frontapp_public_api_client.utils import unwrap

        response = await list_articles_in_a_knowledge_base.asyncio_detailed(
            knowledge_base_id,
            client=self._client,
            limit=to_unset(limit),
            page_token=to_unset(page_token),
        )
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def iter_articles(
        self,
        knowledge_base_id: str,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[KnowledgeBaseArticleSlimResponse]:
        """Walk every article in a KB, paginated.

        Yields slim article responses (no content body). Use
        ``get_article(id, with_content=True)`` to fetch the full body
        for a single article after picking it from the list.
        """
        from frontapp_public_api_client.api.knowledge_base_articles import (
            list_articles_in_a_knowledge_base,
        )
        from frontapp_public_api_client.domain.converters import to_unset

        async for item in self._paginate(
            list_articles_in_a_knowledge_base.asyncio_detailed,
            max_items=max_items,
            max_pages=max_pages,
            knowledge_base_id=knowledge_base_id,
            limit=to_unset(limit),
        ):
            yield item

    async def list_articles_in_category(
        self,
        category_id: str,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[KnowledgeBaseArticleSlimResponse]:
        """List one page of articles under a specific category."""
        from frontapp_public_api_client.api.knowledge_base_articles import (
            list_articles_in_a_category,
        )
        from frontapp_public_api_client.domain.converters import to_unset
        from frontapp_public_api_client.utils import unwrap

        response = await list_articles_in_a_category.asyncio_detailed(
            category_id,
            client=self._client,
            limit=to_unset(limit),
            page_token=to_unset(page_token),
        )
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def iter_articles_in_category(
        self,
        category_id: str,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[KnowledgeBaseArticleSlimResponse]:
        """Walk every article in a category, paginated."""
        from frontapp_public_api_client.api.knowledge_base_articles import (
            list_articles_in_a_category,
        )
        from frontapp_public_api_client.domain.converters import to_unset

        async for item in self._paginate(
            list_articles_in_a_category.asyncio_detailed,
            max_items=max_items,
            max_pages=max_pages,
            category_id=category_id,
            limit=to_unset(limit),
        ):
            yield item

    async def get_article(
        self,
        article_id: str,
        *,
        with_content: bool = False,
        locale: str | None = None,
    ) -> KnowledgeBaseArticleSlimResponse | KnowledgeBaseArticleResponse:
        """Fetch one article.

        Args:
            article_id: ``kba_*`` id.
            with_content: When ``True``, returns the full
                ``KnowledgeBaseArticleResponse`` including the body.
                When ``False`` (default), returns the slim variant
                without body — useful for catalog browsing.
            locale: When ``with_content=True``, ``None`` (default) hits
                the default-locale endpoint; any other value hits the
                specified-locale variant. Ignored when
                ``with_content=False``.
        """
        from frontapp_public_api_client.utils import unwrap_as

        if with_content:
            from frontapp_public_api_client.models.knowledge_base_article_response import (
                KnowledgeBaseArticleResponse,
            )

            if locale is None:
                from frontapp_public_api_client.api.knowledge_base_articles import (
                    get_knowledge_base_article_with_content_in_default_locale as _get,
                )

                response = await _get.asyncio_detailed(article_id, client=self._client)
            else:
                from frontapp_public_api_client.api.knowledge_base_articles import (
                    get_knowledge_base_article_with_content_in_specified_locale as _get,
                )

                response = await _get.asyncio_detailed(
                    article_id, locale, client=self._client
                )
            return unwrap_as(response, KnowledgeBaseArticleResponse)

        from frontapp_public_api_client.api.knowledge_base_articles import (
            get_a_knowledge_base_article,
        )
        from frontapp_public_api_client.models.knowledge_base_article_slim_response import (
            KnowledgeBaseArticleSlimResponse,
        )

        response = await get_a_knowledge_base_article.asyncio_detailed(
            article_id, client=self._client
        )
        return unwrap_as(response, KnowledgeBaseArticleSlimResponse)

    async def create_article(
        self,
        knowledge_base_id: str,
        *,
        subject: str | None = None,
        content: str | None = None,
        category_id: str | None = None,
        author_id: str | None = None,
        status: Literal["draft", "published"] = "draft",
        locale: str | None = None,
    ) -> KnowledgeBaseArticleResponse:
        """Create a new article in a knowledge base.

        Args:
            knowledge_base_id: ``knb_*`` id.
            subject: Article title.
            content: Article body (HTML or markdown — Front renders both).
            category_id: Optional category to file the article under.
            author_id: Optional ``tea_*`` id of the authoring teammate.
            status: ``"draft"`` (default) or ``"published"``.
                ``"draft"`` is the safer default for agent-authored content.
            locale: ``None`` (default) hits the default-locale endpoint;
                any other value hits the specified-locale variant.
        """
        from frontapp_public_api_client.domain.converters import to_unset
        from frontapp_public_api_client.models.knowledge_base_article_create import (
            KnowledgeBaseArticleCreate,
        )
        from frontapp_public_api_client.models.knowledge_base_article_create_status import (
            KnowledgeBaseArticleCreateStatus,
        )
        from frontapp_public_api_client.models.knowledge_base_article_response import (
            KnowledgeBaseArticleResponse,
        )
        from frontapp_public_api_client.utils import unwrap_as

        body = KnowledgeBaseArticleCreate(
            category_id=to_unset(category_id),
            author_id=to_unset(author_id),
            subject=to_unset(subject),
            content=to_unset(content),
            status=KnowledgeBaseArticleCreateStatus(status),
        )

        if locale is None:
            from frontapp_public_api_client.api.knowledge_bases import (
                create_article_in_a_knowledge_base_in_default_locale as _create,
            )

            response = await _create.asyncio_detailed(
                knowledge_base_id, client=self._client, body=body
            )
        else:
            from frontapp_public_api_client.api.knowledge_bases import (
                create_article_in_a_knowledge_base_in_specified_locale as _create,
            )

            response = await _create.asyncio_detailed(
                knowledge_base_id, locale, client=self._client, body=body
            )
        return unwrap_as(response, KnowledgeBaseArticleResponse)

    async def update_article(
        self,
        article_id: str,
        *,
        subject: str | None = None,
        content: str | None = None,
        author_id: str | None = None,
        status: Literal["draft", "published"] | None = None,
        locale: str | None = None,
    ) -> KnowledgeBaseArticleResponse:
        """Update an existing article.

        Only fields explicitly passed are sent in the PATCH; omitted
        fields preserve their current value (including ``status`` —
        leave it ``None`` to avoid flipping draft↔published).
        """
        from frontapp_public_api_client.domain.converters import to_unset
        from frontapp_public_api_client.models.knowledge_base_article_patch import (
            KnowledgeBaseArticlePatch,
        )
        from frontapp_public_api_client.models.knowledge_base_article_patch_status import (
            KnowledgeBaseArticlePatchStatus,
        )
        from frontapp_public_api_client.models.knowledge_base_article_response import (
            KnowledgeBaseArticleResponse,
        )
        from frontapp_public_api_client.utils import unwrap_as

        body = KnowledgeBaseArticlePatch(
            author_id=to_unset(author_id),
            subject=to_unset(subject),
            content=to_unset(content),
            status=(
                KnowledgeBaseArticlePatchStatus(status)
                if status is not None
                else to_unset(None)
            ),
        )

        if locale is None:
            from frontapp_public_api_client.api.knowledge_base_articles import (
                update_article_content_in_default_locale as _update,
            )

            response = await _update.asyncio_detailed(
                article_id, client=self._client, body=body
            )
        else:
            from frontapp_public_api_client.api.knowledge_base_articles import (
                update_article_content_in_specified_locale as _update,
            )

            response = await _update.asyncio_detailed(
                article_id, locale, client=self._client, body=body
            )
        return unwrap_as(response, KnowledgeBaseArticleResponse)

    # -- categories ---------------------------------------------------------

    async def list_categories(
        self,
        knowledge_base_id: str,
        *,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> builtins.list[KnowledgeBaseCategorySlimResponse]:
        """List one page of categories in a KB (cursor-paginated)."""
        from frontapp_public_api_client.api.knowledge_base_categories import (
            list_categories_in_a_knowledge_base,
        )
        from frontapp_public_api_client.domain.converters import to_unset
        from frontapp_public_api_client.utils import unwrap

        response = await list_categories_in_a_knowledge_base.asyncio_detailed(
            knowledge_base_id,
            client=self._client,
            limit=to_unset(limit),
            page_token=to_unset(page_token),
        )
        parsed = unwrap(response)
        return list(getattr(parsed, "field_results", None) or [])

    async def iter_categories(
        self,
        knowledge_base_id: str,
        *,
        limit: int | None = None,
        max_pages: int | None = None,
        max_items: int | None = None,
    ) -> AsyncIterator[KnowledgeBaseCategorySlimResponse]:
        """Walk every category in a KB, paginated."""
        from frontapp_public_api_client.api.knowledge_base_categories import (
            list_categories_in_a_knowledge_base,
        )
        from frontapp_public_api_client.domain.converters import to_unset

        async for item in self._paginate(
            list_categories_in_a_knowledge_base.asyncio_detailed,
            max_items=max_items,
            max_pages=max_pages,
            knowledge_base_id=knowledge_base_id,
            limit=to_unset(limit),
        ):
            yield item

    async def get_category(
        self,
        category_id: str,
        *,
        with_content: bool = False,
        locale: str | None = None,
    ) -> KnowledgeBaseCategorySlimResponse | KnowledgeBaseCategoryResponse:
        """Fetch one category.

        ``with_content=True`` returns the localized full response;
        ``with_content=False`` (default) returns the slim variant.
        """
        from frontapp_public_api_client.utils import unwrap_as

        if with_content:
            from frontapp_public_api_client.models.knowledge_base_category_response import (
                KnowledgeBaseCategoryResponse,
            )

            if locale is None:
                from frontapp_public_api_client.api.knowledge_base_categories import (
                    get_knowledge_base_category_content_in_default_locale as _get,
                )

                response = await _get.asyncio_detailed(category_id, client=self._client)
            else:
                from frontapp_public_api_client.api.knowledge_base_categories import (
                    get_knowledge_base_category_with_content_in_specified_locale as _get,
                )

                response = await _get.asyncio_detailed(
                    category_id, locale, client=self._client
                )
            return unwrap_as(response, KnowledgeBaseCategoryResponse)

        from frontapp_public_api_client.api.knowledge_base_categories import (
            get_a_knowledge_base_category,
        )
        from frontapp_public_api_client.models.knowledge_base_category_slim_response import (
            KnowledgeBaseCategorySlimResponse,
        )

        response = await get_a_knowledge_base_category.asyncio_detailed(
            category_id, client=self._client
        )
        return unwrap_as(response, KnowledgeBaseCategorySlimResponse)

    async def create_category(
        self,
        knowledge_base_id: str,
        *,
        name: str,
        parent_category_id: str | None = None,
        description: str | None = None,
        locale: str | None = None,
    ) -> KnowledgeBaseCategoryResponse:
        """Create a new category in a knowledge base.

        ``name`` is required. ``parent_category_id`` allows nesting
        under an existing category; ``description`` is freeform text.
        """
        from frontapp_public_api_client.domain.converters import to_unset
        from frontapp_public_api_client.models.knowledge_base_category_create import (
            KnowledgeBaseCategoryCreate,
        )
        from frontapp_public_api_client.models.knowledge_base_category_response import (
            KnowledgeBaseCategoryResponse,
        )
        from frontapp_public_api_client.utils import unwrap_as

        body = KnowledgeBaseCategoryCreate(
            name=name,
            parent_category_id=to_unset(parent_category_id),
            description=to_unset(description),
        )

        if locale is None:
            from frontapp_public_api_client.api.knowledge_bases import (
                create_knowledge_base_category_in_default_locale as _create,
            )

            response = await _create.asyncio_detailed(
                knowledge_base_id, client=self._client, body=body
            )
        else:
            from frontapp_public_api_client.api.knowledge_bases import (
                create_knowledge_base_category_in_specified_locale as _create,
            )

            response = await _create.asyncio_detailed(
                knowledge_base_id, locale, client=self._client, body=body
            )
        return unwrap_as(response, KnowledgeBaseCategoryResponse)

    async def update_category(
        self,
        category_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        locale: str | None = None,
    ) -> KnowledgeBaseCategoryResponse:
        """Update an existing category. Only specified fields are sent."""
        from frontapp_public_api_client.domain.converters import to_unset
        from frontapp_public_api_client.models.knowledge_base_category_patch import (
            KnowledgeBaseCategoryPatch,
        )
        from frontapp_public_api_client.models.knowledge_base_category_response import (
            KnowledgeBaseCategoryResponse,
        )
        from frontapp_public_api_client.utils import unwrap_as

        body = KnowledgeBaseCategoryPatch(
            name=to_unset(name),
            description=to_unset(description),
        )

        if locale is None:
            from frontapp_public_api_client.api.knowledge_base_categories import (
                update_knowledge_base_category_in_default_locale as _update,
            )

            response = await _update.asyncio_detailed(
                category_id, client=self._client, body=body
            )
        else:
            from frontapp_public_api_client.api.knowledge_base_categories import (
                update_knowledge_base_category_in_specified_locale as _update,
            )

            response = await _update.asyncio_detailed(
                category_id, locale, client=self._client, body=body
            )
        return unwrap_as(response, KnowledgeBaseCategoryResponse)
