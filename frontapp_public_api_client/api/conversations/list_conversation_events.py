from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_conversation_events_response_200 import (
    ListConversationEventsResponse200,
)


def _get_kwargs(
    conversation_id: str = "cnv_123",
    *,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["page_token"] = page_token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/conversations/{conversation_id}/events".format(
            conversation_id=quote(str(conversation_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ListConversationEventsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListConversationEventsResponse200.from_dict(response.json())

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
) -> Response[Any | ListConversationEventsResponse200]:
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
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Response[Any | ListConversationEventsResponse200]:
    """List conversation events

     List the events that occured for a conversation in reverse chronological order (newest first). The
    order will respect your company's [bump settings](https://help.front.com/t/y729th/customize-when-
    conversations-bump-up), which determine when conversations bump to the top.

    Required scope: `events:*:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | ListConversationEventsResponse200]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
        limit=limit,
        page_token=page_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Any | ListConversationEventsResponse200 | None:
    """List conversation events

     List the events that occured for a conversation in reverse chronological order (newest first). The
    order will respect your company's [bump settings](https://help.front.com/t/y729th/customize-when-
    conversations-bump-up), which determine when conversations bump to the top.

    Required scope: `events:*:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | ListConversationEventsResponse200
    """

    return sync_detailed(
        conversation_id=conversation_id,
        client=client,
        limit=limit,
        page_token=page_token,
    ).parsed


async def asyncio_detailed(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Response[Any | ListConversationEventsResponse200]:
    """List conversation events

     List the events that occured for a conversation in reverse chronological order (newest first). The
    order will respect your company's [bump settings](https://help.front.com/t/y729th/customize-when-
    conversations-bump-up), which determine when conversations bump to the top.

    Required scope: `events:*:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Any | ListConversationEventsResponse200]
    """

    kwargs = _get_kwargs(
        conversation_id=conversation_id,
        limit=limit,
        page_token=page_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    conversation_id: str = "cnv_123",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Any | ListConversationEventsResponse200 | None:
    """List conversation events

     List the events that occured for a conversation in reverse chronological order (newest first). The
    order will respect your company's [bump settings](https://help.front.com/t/y729th/customize-when-
    conversations-bump-up), which determine when conversations bump to the top.

    Required scope: `events:*:read`

    Args:
        conversation_id (str):  Default: 'cnv_123'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Any | ListConversationEventsResponse200
    """

    return (
        await asyncio_detailed(
            conversation_id=conversation_id,
            client=client,
            limit=limit,
            page_token=page_token,
        )
    ).parsed
