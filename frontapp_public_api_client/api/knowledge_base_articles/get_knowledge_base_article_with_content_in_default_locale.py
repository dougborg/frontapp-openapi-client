from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.knowledge_base_article_response import KnowledgeBaseArticleResponse


def _get_kwargs(
    article_id: str = "kba_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/knowledge_base_articles/{article_id}/content".format(
            article_id=quote(str(article_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> KnowledgeBaseArticleResponse | None:
    if response.status_code == 200:
        response_200 = KnowledgeBaseArticleResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[KnowledgeBaseArticleResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    article_id: str = "kba_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[KnowledgeBaseArticleResponse]:
    """Get knowledge base article with content in default locale

     Fetches a knowledge base article with content in the default locale.

    Required scope: `knowledge_bases:read`

    Args:
        article_id (str):  Default: 'kba_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseArticleResponse]
    """

    kwargs = _get_kwargs(
        article_id=article_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    article_id: str = "kba_123",
    *,
    client: AuthenticatedClient | Client,
) -> KnowledgeBaseArticleResponse | None:
    """Get knowledge base article with content in default locale

     Fetches a knowledge base article with content in the default locale.

    Required scope: `knowledge_bases:read`

    Args:
        article_id (str):  Default: 'kba_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseArticleResponse
    """

    return sync_detailed(
        article_id=article_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    article_id: str = "kba_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[KnowledgeBaseArticleResponse]:
    """Get knowledge base article with content in default locale

     Fetches a knowledge base article with content in the default locale.

    Required scope: `knowledge_bases:read`

    Args:
        article_id (str):  Default: 'kba_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseArticleResponse]
    """

    kwargs = _get_kwargs(
        article_id=article_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    article_id: str = "kba_123",
    *,
    client: AuthenticatedClient | Client,
) -> KnowledgeBaseArticleResponse | None:
    """Get knowledge base article with content in default locale

     Fetches a knowledge base article with content in the default locale.

    Required scope: `knowledge_bases:read`

    Args:
        article_id (str):  Default: 'kba_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseArticleResponse
    """

    return (
        await asyncio_detailed(
            article_id=article_id,
            client=client,
        )
    ).parsed
