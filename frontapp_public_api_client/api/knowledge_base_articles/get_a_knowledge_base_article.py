from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.knowledge_base_article_slim_response import (
    KnowledgeBaseArticleSlimResponse,
)


def _get_kwargs(
    article_id: str = "kba_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/knowledge_base_articles/{article_id}".format(
            article_id=quote(str(article_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> KnowledgeBaseArticleSlimResponse | None:
    if response.status_code == 200:
        response_200 = KnowledgeBaseArticleSlimResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[KnowledgeBaseArticleSlimResponse]:
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
) -> Response[KnowledgeBaseArticleSlimResponse]:
    """Get a knowledge base article

     Fetches a knowledge base article.

    Required scope: `knowledge_bases:read`

    Args:
        article_id (str):  Default: 'kba_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseArticleSlimResponse]
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
) -> KnowledgeBaseArticleSlimResponse | None:
    """Get a knowledge base article

     Fetches a knowledge base article.

    Required scope: `knowledge_bases:read`

    Args:
        article_id (str):  Default: 'kba_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseArticleSlimResponse
    """

    return sync_detailed(
        article_id=article_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    article_id: str = "kba_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[KnowledgeBaseArticleSlimResponse]:
    """Get a knowledge base article

     Fetches a knowledge base article.

    Required scope: `knowledge_bases:read`

    Args:
        article_id (str):  Default: 'kba_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseArticleSlimResponse]
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
) -> KnowledgeBaseArticleSlimResponse | None:
    """Get a knowledge base article

     Fetches a knowledge base article.

    Required scope: `knowledge_bases:read`

    Args:
        article_id (str):  Default: 'kba_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseArticleSlimResponse
    """

    return (
        await asyncio_detailed(
            article_id=article_id,
            client=client,
        )
    ).parsed
