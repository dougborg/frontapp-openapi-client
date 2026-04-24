from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.add_conversation_followers_body import AddConversationFollowersBody


def _get_kwargs(
    conversation_id: str = "cnv_123",
    *,
    body: AddConversationFollowersBody | Unset = UNSET,
    ignore_errors: bool | Unset = False,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["ignore_errors"] = ignore_errors

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/conversations/{conversation_id}/followers".format(
            conversation_id=quote(str(conversation_id), safe=""),
        ),
        "params": params,
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

    if response.status_code == 301:
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
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    body: AddConversationFollowersBody | Unset = UNSET,
    ignore_errors: bool | Unset = False,
) -> Response[Any]:
    """Add conversation followers

     Adds teammates to the list of followers of a conversation.

    Required scope: `conversations:write`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        ignore_errors (bool | Unset):  Default: False.
        body (AddConversationFollowersBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
        body=body,
        ignore_errors=ignore_errors,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    body: AddConversationFollowersBody | Unset = UNSET,
    ignore_errors: bool | Unset = False,
) -> Response[Any]:
    """Add conversation followers

     Adds teammates to the list of followers of a conversation.

    Required scope: `conversations:write`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        ignore_errors (bool | Unset):  Default: False.
        body (AddConversationFollowersBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
        body=body,
        ignore_errors=ignore_errors,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
