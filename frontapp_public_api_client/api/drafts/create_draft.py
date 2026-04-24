from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_draft import CreateDraft
from ...models.message_response import MessageResponse


def _get_kwargs(
    channel_id: str = "cha_123",
    *,
    body: CreateDraft | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/channels/{channel_id}/drafts".format(
            channel_id=quote(str(channel_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> MessageResponse | None:
    if response.status_code == 200:
        response_200 = MessageResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[MessageResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateDraft | Unset = UNSET,
) -> Response[MessageResponse]:
    """Create draft

     Create a draft message which is the first message of a new
    [conversation](https://dev.frontapp.com/reference/conversations).

    Required scope: `drafts:write`

    Args:
        channel_id (str):  Default: 'cha_123'.
        body (CreateDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageResponse]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateDraft | Unset = UNSET,
) -> MessageResponse | None:
    """Create draft

     Create a draft message which is the first message of a new
    [conversation](https://dev.frontapp.com/reference/conversations).

    Required scope: `drafts:write`

    Args:
        channel_id (str):  Default: 'cha_123'.
        body (CreateDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageResponse
    """

    return sync_detailed(
        channel_id=channel_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateDraft | Unset = UNSET,
) -> Response[MessageResponse]:
    """Create draft

     Create a draft message which is the first message of a new
    [conversation](https://dev.frontapp.com/reference/conversations).

    Required scope: `drafts:write`

    Args:
        channel_id (str):  Default: 'cha_123'.
        body (CreateDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageResponse]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateDraft | Unset = UNSET,
) -> MessageResponse | None:
    """Create draft

     Create a draft message which is the first message of a new
    [conversation](https://dev.frontapp.com/reference/conversations).

    Required scope: `drafts:write`

    Args:
        channel_id (str):  Default: 'cha_123'.
        body (CreateDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageResponse
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            client=client,
            body=body,
        )
    ).parsed
