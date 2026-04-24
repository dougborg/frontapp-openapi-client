from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_articles_in_a_knowledge_base_response_200 import (
    ListArticlesInAKnowledgeBaseResponse200,
)


def _get_kwargs(
    knowledge_base_id: str = "knb_123",
    *,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["page_token"] = page_token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/knowledge_bases/{knowledge_base_id}/articles".format(
            knowledge_base_id=quote(str(knowledge_base_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListArticlesInAKnowledgeBaseResponse200 | None:
    if response.status_code == 200:
        response_200 = ListArticlesInAKnowledgeBaseResponse200.from_dict(
            response.json()
        )

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListArticlesInAKnowledgeBaseResponse200]:
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
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Response[ListArticlesInAKnowledgeBaseResponse200]:
    """List articles in a knowledge base

     List articles in a knowledge base

    Required scope: `knowledge_bases:read`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListArticlesInAKnowledgeBaseResponse200]
    """

    kwargs = _get_kwargs(
        knowledge_base_id=knowledge_base_id,
        limit=limit,
        page_token=page_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    knowledge_base_id: str = "knb_123",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> ListArticlesInAKnowledgeBaseResponse200 | None:
    """List articles in a knowledge base

     List articles in a knowledge base

    Required scope: `knowledge_bases:read`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListArticlesInAKnowledgeBaseResponse200
    """

    return sync_detailed(
        knowledge_base_id=knowledge_base_id,
        client=client,
        limit=limit,
        page_token=page_token,
    ).parsed


async def asyncio_detailed(
    knowledge_base_id: str = "knb_123",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Response[ListArticlesInAKnowledgeBaseResponse200]:
    """List articles in a knowledge base

     List articles in a knowledge base

    Required scope: `knowledge_bases:read`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListArticlesInAKnowledgeBaseResponse200]
    """

    kwargs = _get_kwargs(
        knowledge_base_id=knowledge_base_id,
        limit=limit,
        page_token=page_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    knowledge_base_id: str = "knb_123",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> ListArticlesInAKnowledgeBaseResponse200 | None:
    """List articles in a knowledge base

     List articles in a knowledge base

    Required scope: `knowledge_bases:read`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListArticlesInAKnowledgeBaseResponse200
    """

    return (
        await asyncio_detailed(
            knowledge_base_id=knowledge_base_id,
            client=client,
            limit=limit,
            page_token=page_token,
        )
    ).parsed
