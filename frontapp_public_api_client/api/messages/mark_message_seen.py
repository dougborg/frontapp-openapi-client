from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.mark_message_seen_body import MarkMessageSeenBody


def _get_kwargs(
    message_id: str = "msg_123",
    *,
    body: MarkMessageSeenBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/messages/{message_id}/seen".format(
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
) -> Any | None:
    if response.status_code == 204:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any]:
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
    body: MarkMessageSeenBody | Unset = UNSET,
) -> Response[Any]:
    """Mark message seen

     Mark an outbound message from Front as seen. Note, the message seen route should only be called in
    response to an actual end-user's message-seen action. In accordance with this behavior, the route is
    rate limited to 10 requests per message per hour.

    Required scope: `messages:write`

    Args:
        message_id (str):  Default: 'msg_123'.
        body (MarkMessageSeenBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        message_id=message_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    message_id: str = "msg_123",
    *,
    client: AuthenticatedClient | Client,
    body: MarkMessageSeenBody | Unset = UNSET,
) -> Response[Any]:
    """Mark message seen

     Mark an outbound message from Front as seen. Note, the message seen route should only be called in
    response to an actual end-user's message-seen action. In accordance with this behavior, the route is
    rate limited to 10 requests per message per hour.

    Required scope: `messages:write`

    Args:
        message_id (str):  Default: 'msg_123'.
        body (MarkMessageSeenBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        message_id=message_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
