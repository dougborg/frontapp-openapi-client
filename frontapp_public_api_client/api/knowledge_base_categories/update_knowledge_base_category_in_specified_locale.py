from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.knowledge_base_category_patch import KnowledgeBaseCategoryPatch
from ...models.knowledge_base_category_response import KnowledgeBaseCategoryResponse


def _get_kwargs(
    category_id: str = "kbc_123",
    locale: str = "en",
    *,
    body: KnowledgeBaseCategoryPatch | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/knowledge_base_categories/{category_id}/locales/{locale}/content".format(
            category_id=quote(str(category_id), safe=""),
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
    if response.status_code == 200:
        response_200 = KnowledgeBaseCategoryResponse.from_dict(response.json())

        return response_200

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
    category_id: str = "kbc_123",
    locale: str = "en",
    *,
    client: AuthenticatedClient | Client,
    body: KnowledgeBaseCategoryPatch | Unset = UNSET,
) -> Response[KnowledgeBaseCategoryResponse]:
    """Update knowledge base category in specified locale

     Updates a knowledge base category for a given locale. Will republish the knowledge base if the
    knowledge base is currently published.

    Required scope: `knowledge_bases:write`

    Args:
        category_id (str):  Default: 'kbc_123'.
        locale (str):  Default: 'en'.
        body (KnowledgeBaseCategoryPatch | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseCategoryResponse]
    """

    kwargs = _get_kwargs(
        category_id=category_id,
        locale=locale,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    category_id: str = "kbc_123",
    locale: str = "en",
    *,
    client: AuthenticatedClient | Client,
    body: KnowledgeBaseCategoryPatch | Unset = UNSET,
) -> KnowledgeBaseCategoryResponse | None:
    """Update knowledge base category in specified locale

     Updates a knowledge base category for a given locale. Will republish the knowledge base if the
    knowledge base is currently published.

    Required scope: `knowledge_bases:write`

    Args:
        category_id (str):  Default: 'kbc_123'.
        locale (str):  Default: 'en'.
        body (KnowledgeBaseCategoryPatch | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseCategoryResponse
    """

    return sync_detailed(
        category_id=category_id,
        locale=locale,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    category_id: str = "kbc_123",
    locale: str = "en",
    *,
    client: AuthenticatedClient | Client,
    body: KnowledgeBaseCategoryPatch | Unset = UNSET,
) -> Response[KnowledgeBaseCategoryResponse]:
    """Update knowledge base category in specified locale

     Updates a knowledge base category for a given locale. Will republish the knowledge base if the
    knowledge base is currently published.

    Required scope: `knowledge_bases:write`

    Args:
        category_id (str):  Default: 'kbc_123'.
        locale (str):  Default: 'en'.
        body (KnowledgeBaseCategoryPatch | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[KnowledgeBaseCategoryResponse]
    """

    kwargs = _get_kwargs(
        category_id=category_id,
        locale=locale,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    category_id: str = "kbc_123",
    locale: str = "en",
    *,
    client: AuthenticatedClient | Client,
    body: KnowledgeBaseCategoryPatch | Unset = UNSET,
) -> KnowledgeBaseCategoryResponse | None:
    """Update knowledge base category in specified locale

     Updates a knowledge base category for a given locale. Will republish the knowledge base if the
    knowledge base is currently published.

    Required scope: `knowledge_bases:write`

    Args:
        category_id (str):  Default: 'kbc_123'.
        locale (str):  Default: 'en'.
        body (KnowledgeBaseCategoryPatch | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        KnowledgeBaseCategoryResponse
    """

    return (
        await asyncio_detailed(
            category_id=category_id,
            locale=locale,
            client=client,
            body=body,
        )
    ).parsed
