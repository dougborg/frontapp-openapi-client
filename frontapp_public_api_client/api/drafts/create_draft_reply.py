from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.message_response import MessageResponse
from ...models.reply_draft import ReplyDraft


def _get_kwargs(
    conversation_id: str = "cnv_123",
    *,
    body: ReplyDraft | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/conversations/{conversation_id}/drafts".format(
            conversation_id=quote(str(conversation_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | MessageResponse | None:
    if response.status_code == 200:
        response_200 = MessageResponse.from_dict(response.json())

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
) -> Response[Any | MessageResponse]:
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
    body: ReplyDraft | Unset = UNSET,
) -> Response[Any | MessageResponse]:
    """Create draft reply

     Create a new draft as a reply to the last message in the conversation.

    Required scope: `drafts:write`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (ReplyDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | MessageResponse]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    body: ReplyDraft | Unset = UNSET,
) -> Any | MessageResponse | None:
    """Create draft reply

     Create a new draft as a reply to the last message in the conversation.

    Required scope: `drafts:write`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (ReplyDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | MessageResponse
    """

    return sync_detailed(
        conversation_id=conversation_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    body: ReplyDraft | Unset = UNSET,
) -> Response[Any | MessageResponse]:
    """Create draft reply

     Create a new draft as a reply to the last message in the conversation.

    Required scope: `drafts:write`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (ReplyDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | MessageResponse]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    body: ReplyDraft | Unset = UNSET,
) -> Any | MessageResponse | None:
    """Create draft reply

     Create a new draft as a reply to the last message in the conversation.

    Required scope: `drafts:write`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        body (ReplyDraft | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | MessageResponse
    """

    return (
        await asyncio_detailed(
            conversation_id=conversation_id,
            client=client,
            body=body,
        )
    ).parsed
