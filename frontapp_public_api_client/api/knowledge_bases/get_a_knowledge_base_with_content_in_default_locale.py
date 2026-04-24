from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.knowledge_base_response import KnowledgeBaseResponse


def _get_kwargs(
    knowledge_base_id: str = "knb_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/knowledge_bases/{knowledge_base_id}/content".format(
            knowledge_base_id=quote(str(knowledge_base_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> KnowledgeBaseResponse | None:
    if response.status_code == 200:
        response_200 = KnowledgeBaseResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[KnowledgeBaseResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    knowledge_base_id: str = "knb_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[KnowledgeBaseResponse]:
    """Get a knowledge base with content in default locale

     Fetches a knowledge base with its content in the default locale.

    Required scope: `knowledge_bases:read`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseResponse]
    """

    kwargs = _get_kwargs(
        knowledge_base_id=knowledge_base_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    knowledge_base_id: str = "knb_123",
    *,
    client: AuthenticatedClient | Client,
) -> KnowledgeBaseResponse | None:
    """Get a knowledge base with content in default locale

     Fetches a knowledge base with its content in the default locale.

    Required scope: `knowledge_bases:read`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseResponse
    """

    return sync_detailed(
        knowledge_base_id=knowledge_base_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    knowledge_base_id: str = "knb_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[KnowledgeBaseResponse]:
    """Get a knowledge base with content in default locale

     Fetches a knowledge base with its content in the default locale.

    Required scope: `knowledge_bases:read`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseResponse]
    """

    kwargs = _get_kwargs(
        knowledge_base_id=knowledge_base_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    knowledge_base_id: str = "knb_123",
    *,
    client: AuthenticatedClient | Client,
) -> KnowledgeBaseResponse | None:
    """Get a knowledge base with content in default locale

     Fetches a knowledge base with its content in the default locale.

    Required scope: `knowledge_bases:read`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseResponse
    """

    return (
        await asyncio_detailed(
            knowledge_base_id=knowledge_base_id,
            client=client,
        )
    ).parsed
