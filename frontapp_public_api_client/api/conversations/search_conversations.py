from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.search_conversations_response_200 import SearchConversationsResponse200


def _get_kwargs(
    query: str = "inbox:inb_123 tag:tag_345",
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
        "url": "/conversations/search/{query}".format(
            query=quote(str(query), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> SearchConversationsResponse200 | None:
    if response.status_code == 200:
        response_200 = SearchConversationsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[SearchConversationsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    query: str = "inbox:inb_123 tag:tag_345",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Response[SearchConversationsResponse200]:
    """Search conversations

     Search for conversations. Response will include a count of total matches and an array of
    conversations in descending order by last activity.
    See the [search syntax documentation](https://dev.frontapp.com/docs/search-1) for usage examples.
    **Note:** This endpoint is subject to [proportional rate
    limiting](https://dev.frontapp.com/docs/rate-limiting#additional-proportional-limiting) at 40% of
    your company's rate limit.


    Required scope: `conversations:read`

    Args:
        query (str):  Default: 'inbox:inb_123 tag:tag_345'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SearchConversationsResponse200]
    """

    kwargs = _get_kwargs(
        query=query,
        limit=limit,
        page_token=page_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    query: str = "inbox:inb_123 tag:tag_345",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> SearchConversationsResponse200 | None:
    """Search conversations

     Search for conversations. Response will include a count of total matches and an array of
    conversations in descending order by last activity.
    See the [search syntax documentation](https://dev.frontapp.com/docs/search-1) for usage examples.
    **Note:** This endpoint is subject to [proportional rate
    limiting](https://dev.frontapp.com/docs/rate-limiting#additional-proportional-limiting) at 40% of
    your company's rate limit.


    Required scope: `conversations:read`

    Args:
        query (str):  Default: 'inbox:inb_123 tag:tag_345'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SearchConversationsResponse200
    """

    return sync_detailed(
        query=query,
        client=client,
        limit=limit,
        page_token=page_token,
    ).parsed


async def asyncio_detailed(
    query: str = "inbox:inb_123 tag:tag_345",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> Response[SearchConversationsResponse200]:
    """Search conversations

     Search for conversations. Response will include a count of total matches and an array of
    conversations in descending order by last activity.
    See the [search syntax documentation](https://dev.frontapp.com/docs/search-1) for usage examples.
    **Note:** This endpoint is subject to [proportional rate
    limiting](https://dev.frontapp.com/docs/rate-limiting#additional-proportional-limiting) at 40% of
    your company's rate limit.


    Required scope: `conversations:read`

    Args:
        query (str):  Default: 'inbox:inb_123 tag:tag_345'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[SearchConversationsResponse200]
    """

    kwargs = _get_kwargs(
        query=query,
        limit=limit,
        page_token=page_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    query: str = "inbox:inb_123 tag:tag_345",
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
) -> SearchConversationsResponse200 | None:
    """Search conversations

     Search for conversations. Response will include a count of total matches and an array of
    conversations in descending order by last activity.
    See the [search syntax documentation](https://dev.frontapp.com/docs/search-1) for usage examples.
    **Note:** This endpoint is subject to [proportional rate
    limiting](https://dev.frontapp.com/docs/rate-limiting#additional-proportional-limiting) at 40% of
    your company's rate limit.


    Required scope: `conversations:read`

    Args:
        query (str):  Default: 'inbox:inb_123 tag:tag_345'.
        limit (int | Unset):  Example: 25.
        page_token (str | Unset):  Example: https://yourCompany.api.frontapp.com/endpoint?limit=25
            &page_token=92f32bcd7625333caf4e0f8fc26d920c812f.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        SearchConversationsResponse200
    """

    return (
        await asyncio_detailed(
            query=query,
            client=client,
            limit=limit,
            page_token=page_token,
        )
    ).parsed
