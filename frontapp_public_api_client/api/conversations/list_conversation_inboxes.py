from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.list_conversation_inboxes_response_200 import (
    ListConversationInboxesResponse200,
)


def _get_kwargs(
    conversation_id: str = "cnv_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/conversations/{conversation_id}/inboxes".format(
            conversation_id=quote(str(conversation_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ListConversationInboxesResponse200 | None:
    if response.status_code == 200:
        response_200 = ListConversationInboxesResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 301:
        response_301 = cast(Any, None)
        return response_301

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | ListConversationInboxesResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | ListConversationInboxesResponse200]:
    """List conversation inboxes

     List the inboxes in which a conversation is listed.

    Required scope: `inboxes:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | ListConversationInboxesResponse200]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
) -> Any | ListConversationInboxesResponse200 | None:
    """List conversation inboxes

     List the inboxes in which a conversation is listed.

    Required scope: `inboxes:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | ListConversationInboxesResponse200
    """

    return sync_detailed(
        conversation_id=conversation_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | ListConversationInboxesResponse200]:
    """List conversation inboxes

     List the inboxes in which a conversation is listed.

    Required scope: `inboxes:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | ListConversationInboxesResponse200]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
) -> Any | ListConversationInboxesResponse200 | None:
    """List conversation inboxes

     List the inboxes in which a conversation is listed.

    Required scope: `inboxes:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | ListConversationInboxesResponse200
    """

    return (
        await asyncio_detailed(
            conversation_id=conversation_id,
            client=client,
        )
    ).parsed
