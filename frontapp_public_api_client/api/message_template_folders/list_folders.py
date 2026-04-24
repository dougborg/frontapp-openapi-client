from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.list_folders_response_200 import ListFoldersResponse200
from ...models.list_folders_sort_order import ListFoldersSortOrder


def _get_kwargs(
    *,
    sort_by: str | Unset = UNSET,
    sort_order: ListFoldersSortOrder | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["sort_by"] = sort_by

    json_sort_order: str | Unset = UNSET
    if not isinstance(sort_order, Unset):
        json_sort_order = sort_order.value

    params["sort_order"] = json_sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/message_template_folders",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListFoldersResponse200 | None:
    if response.status_code == 200:
        response_200 = ListFoldersResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListFoldersResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    sort_by: str | Unset = UNSET,
    sort_order: ListFoldersSortOrder | Unset = UNSET,
) -> Response[ListFoldersResponse200]:
    """List folders

     List the message template folders.

    Required scope: `message_templates:read`

    Args:
        sort_by (str | Unset):
        sort_order (ListFoldersSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListFoldersResponse200]
    """

    kwargs = _get_kwargs(
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    sort_by: str | Unset = UNSET,
    sort_order: ListFoldersSortOrder | Unset = UNSET,
) -> ListFoldersResponse200 | None:
    """List folders

     List the message template folders.

    Required scope: `message_templates:read`

    Args:
        sort_by (str | Unset):
        sort_order (ListFoldersSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListFoldersResponse200
    """

    return sync_detailed(
        client=client,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    sort_by: str | Unset = UNSET,
    sort_order: ListFoldersSortOrder | Unset = UNSET,
) -> Response[ListFoldersResponse200]:
    """List folders

     List the message template folders.

    Required scope: `message_templates:read`

    Args:
        sort_by (str | Unset):
        sort_order (ListFoldersSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListFoldersResponse200]
    """

    kwargs = _get_kwargs(
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    sort_by: str | Unset = UNSET,
    sort_order: ListFoldersSortOrder | Unset = UNSET,
) -> ListFoldersResponse200 | None:
    """List folders

     List the message template folders.

    Required scope: `message_templates:read`

    Args:
        sort_by (str | Unset):
        sort_order (ListFoldersSortOrder | Unset):  Example: asc.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListFoldersResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
