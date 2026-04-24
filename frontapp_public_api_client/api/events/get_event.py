from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.event_response import EventResponse


def _get_kwargs(
    event_id: str = "evt_55c8c149",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/events/{event_id}".format(
            event_id=quote(str(event_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> EventResponse | None:
    if response.status_code == 200:
        response_200 = EventResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[EventResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    event_id: str = "evt_55c8c149",
    *,
    client: AuthenticatedClient | Client,
) -> Response[EventResponse]:
    """Get event

     Fetch an event.
    Refer to the [Events](https://dev.frontapp.com/reference/events) topic for more information,
    including sorting and filtering.


    Required scope: `events:*:read`

    Args:
        event_id (str):  Default: 'evt_55c8c149'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[EventResponse]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    event_id: str = "evt_55c8c149",
    *,
    client: AuthenticatedClient | Client,
) -> EventResponse | None:
    """Get event

     Fetch an event.
    Refer to the [Events](https://dev.frontapp.com/reference/events) topic for more information,
    including sorting and filtering.


    Required scope: `events:*:read`

    Args:
        event_id (str):  Default: 'evt_55c8c149'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        EventResponse
    """

    return sync_detailed(
        event_id=event_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    event_id: str = "evt_55c8c149",
    *,
    client: AuthenticatedClient | Client,
) -> Response[EventResponse]:
    """Get event

     Fetch an event.
    Refer to the [Events](https://dev.frontapp.com/reference/events) topic for more information,
    including sorting and filtering.


    Required scope: `events:*:read`

    Args:
        event_id (str):  Default: 'evt_55c8c149'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[EventResponse]
    """

    kwargs = _get_kwargs(
        event_id=event_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    event_id: str = "evt_55c8c149",
    *,
    client: AuthenticatedClient | Client,
) -> EventResponse | None:
    """Get event

     Fetch an event.
    Refer to the [Events](https://dev.frontapp.com/reference/events) topic for more information,
    including sorting and filtering.


    Required scope: `events:*:read`

    Args:
        event_id (str):  Default: 'evt_55c8c149'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        EventResponse
    """

    return (
        await asyncio_detailed(
            event_id=event_id,
            client=client,
        )
    ).parsed
