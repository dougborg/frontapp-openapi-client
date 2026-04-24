from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_inbox import CreateInbox
from ...models.inbox_response import InboxResponse


def _get_kwargs(
    *,
    body: CreateInbox | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/inboxes",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> InboxResponse | None:
    if response.status_code == 201:
        response_201 = InboxResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[InboxResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateInbox | Unset = UNSET,
) -> Response[InboxResponse]:
    """Create inbox

     Create an inbox in the oldest active workspace that the token has access to. If you need to specify
    the workspace, we recommend using the [Create team inbox](https://dev.frontapp.com/reference/create-
    team-inbox) endpoint instead.

    Required scope: `inboxes:write`

    Args:
        body (CreateInbox | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[InboxResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: CreateInbox | Unset = UNSET,
) -> InboxResponse | None:
    """Create inbox

     Create an inbox in the oldest active workspace that the token has access to. If you need to specify
    the workspace, we recommend using the [Create team inbox](https://dev.frontapp.com/reference/create-
    team-inbox) endpoint instead.

    Required scope: `inboxes:write`

    Args:
        body (CreateInbox | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        InboxResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateInbox | Unset = UNSET,
) -> Response[InboxResponse]:
    """Create inbox

     Create an inbox in the oldest active workspace that the token has access to. If you need to specify
    the workspace, we recommend using the [Create team inbox](https://dev.frontapp.com/reference/create-
    team-inbox) endpoint instead.

    Required scope: `inboxes:write`

    Args:
        body (CreateInbox | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[InboxResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateInbox | Unset = UNSET,
) -> InboxResponse | None:
    """Create inbox

     Create an inbox in the oldest active workspace that the token has access to. If you need to specify
    the workspace, we recommend using the [Create team inbox](https://dev.frontapp.com/reference/create-
    team-inbox) endpoint instead.

    Required scope: `inboxes:write`

    Args:
        body (CreateInbox | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        InboxResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
