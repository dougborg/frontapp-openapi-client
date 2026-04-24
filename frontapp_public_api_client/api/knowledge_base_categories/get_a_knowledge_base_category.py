from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.knowledge_base_category_slim_response import (
    KnowledgeBaseCategorySlimResponse,
)


def _get_kwargs(
    category_id: str = "kbc_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/knowledge_base_categories/{category_id}".format(
            category_id=quote(str(category_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> KnowledgeBaseCategorySlimResponse | None:
    if response.status_code == 200:
        response_200 = KnowledgeBaseCategorySlimResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[KnowledgeBaseCategorySlimResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    category_id: str = "kbc_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[KnowledgeBaseCategorySlimResponse]:
    """Get a knowledge base category

     Fetches a knowledge base category.

    Required scope: `knowledge_bases:read`

    Args:
        category_id (str):  Default: 'kbc_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseCategorySlimResponse]
    """

    kwargs = _get_kwargs(
        category_id=category_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    category_id: str = "kbc_123",
    *,
    client: AuthenticatedClient | Client,
) -> KnowledgeBaseCategorySlimResponse | None:
    """Get a knowledge base category

     Fetches a knowledge base category.

    Required scope: `knowledge_bases:read`

    Args:
        category_id (str):  Default: 'kbc_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseCategorySlimResponse
    """

    return sync_detailed(
        category_id=category_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    category_id: str = "kbc_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[KnowledgeBaseCategorySlimResponse]:
    """Get a knowledge base category

     Fetches a knowledge base category.

    Required scope: `knowledge_bases:read`

    Args:
        category_id (str):  Default: 'kbc_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseCategorySlimResponse]
    """

    kwargs = _get_kwargs(
        category_id=category_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    category_id: str = "kbc_123",
    *,
    client: AuthenticatedClient | Client,
) -> KnowledgeBaseCategorySlimResponse | None:
    """Get a knowledge base category

     Fetches a knowledge base category.

    Required scope: `knowledge_bases:read`

    Args:
        category_id (str):  Default: 'kbc_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseCategorySlimResponse
    """

    return (
        await asyncio_detailed(
            category_id=category_id,
            client=client,
        )
    ).parsed
