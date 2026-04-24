from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.edit_draft import EditDraft
from ...models.message_response import MessageResponse


def _get_kwargs(
    message_id: str = "msg_123",
    *,
    body: EditDraft | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/drafts/{message_id}/".format(
            message_id=quote(str(message_id), safe=""),
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
    message_id: str = "msg_123",
    *,
    client: AuthenticatedClient | Client,
    body: EditDraft | Unset = UNSET,
) -> Response[MessageResponse]:
    """Edit draft

     Edit a draft message.

    Required scope: `drafts:write`

    Args:
        message_id (str):  Default: 'msg_123'.
        body (EditDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageResponse]
    """

    kwargs = _get_kwargs(
        message_id=message_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    message_id: str = "msg_123",
    *,
    client: AuthenticatedClient | Client,
    body: EditDraft | Unset = UNSET,
) -> MessageResponse | None:
    """Edit draft

     Edit a draft message.

    Required scope: `drafts:write`

    Args:
        message_id (str):  Default: 'msg_123'.
        body (EditDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageResponse
    """

    return sync_detailed(
        message_id=message_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    message_id: str = "msg_123",
    *,
    client: AuthenticatedClient | Client,
    body: EditDraft | Unset = UNSET,
) -> Response[MessageResponse]:
    """Edit draft

     Edit a draft message.

    Required scope: `drafts:write`

    Args:
        message_id (str):  Default: 'msg_123'.
        body (EditDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageResponse]
    """

    kwargs = _get_kwargs(
        message_id=message_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    message_id: str = "msg_123",
    *,
    client: AuthenticatedClient | Client,
    body: EditDraft | Unset = UNSET,
) -> MessageResponse | None:
    """Edit draft

     Edit a draft message.

    Required scope: `drafts:write`

    Args:
        message_id (str):  Default: 'msg_123'.
        body (EditDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageResponse
    """

    return (
        await asyncio_detailed(
            message_id=message_id,
            client=client,
            body=body,
        )
    ).parsed
