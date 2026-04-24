from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.knowledge_base_category_create import KnowledgeBaseCategoryCreate
from ...models.knowledge_base_category_response import KnowledgeBaseCategoryResponse


def _get_kwargs(
    knowledge_base_id: str = "knb_123",
    locale: str = "en",
    *,
    body: KnowledgeBaseCategoryCreate | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/knowledge_bases/{knowledge_base_id}/locales/{locale}/categories".format(
            knowledge_base_id=quote(str(knowledge_base_id), safe=""),
            locale=quote(str(locale), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> KnowledgeBaseCategoryResponse | None:
    if response.status_code == 201:
        response_201 = KnowledgeBaseCategoryResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[KnowledgeBaseCategoryResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    knowledge_base_id: str = "knb_123",
    locale: str = "en",
    *,
    client: AuthenticatedClient | Client,
    body: KnowledgeBaseCategoryCreate | Unset = UNSET,
) -> Response[KnowledgeBaseCategoryResponse]:
    """Create knowledge base category in specified locale

     Creates a knowledge base category for a given locale.

    Required scope: `knowledge_bases:write`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.
        locale (str):  Default: 'en'.
        body (KnowledgeBaseCategoryCreate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseCategoryResponse]
    """

    kwargs = _get_kwargs(
        knowledge_base_id=knowledge_base_id,
        locale=locale,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    knowledge_base_id: str = "knb_123",
    locale: str = "en",
    *,
    client: AuthenticatedClient | Client,
    body: KnowledgeBaseCategoryCreate | Unset = UNSET,
) -> KnowledgeBaseCategoryResponse | None:
    """Create knowledge base category in specified locale

     Creates a knowledge base category for a given locale.

    Required scope: `knowledge_bases:write`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.
        locale (str):  Default: 'en'.
        body (KnowledgeBaseCategoryCreate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseCategoryResponse
    """

    return sync_detailed(
        knowledge_base_id=knowledge_base_id,
        locale=locale,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    knowledge_base_id: str = "knb_123",
    locale: str = "en",
    *,
    client: AuthenticatedClient | Client,
    body: KnowledgeBaseCategoryCreate | Unset = UNSET,
) -> Response[KnowledgeBaseCategoryResponse]:
    """Create knowledge base category in specified locale

     Creates a knowledge base category for a given locale.

    Required scope: `knowledge_bases:write`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.
        locale (str):  Default: 'en'.
        body (KnowledgeBaseCategoryCreate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseCategoryResponse]
    """

    kwargs = _get_kwargs(
        knowledge_base_id=knowledge_base_id,
        locale=locale,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    knowledge_base_id: str = "knb_123",
    locale: str = "en",
    *,
    client: AuthenticatedClient | Client,
    body: KnowledgeBaseCategoryCreate | Unset = UNSET,
) -> KnowledgeBaseCategoryResponse | None:
    """Create knowledge base category in specified locale

     Creates a knowledge base category for a given locale.

    Required scope: `knowledge_bases:write`

    Args:
        knowledge_base_id (str):  Default: 'knb_123'.
        locale (str):  Default: 'en'.
        body (KnowledgeBaseCategoryCreate | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseCategoryResponse
    """

    return (
        await asyncio_detailed(
            knowledge_base_id=knowledge_base_id,
            locale=locale,
            client=client,
            body=body,
        )
    ).parsed
