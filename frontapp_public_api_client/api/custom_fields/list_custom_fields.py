from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.list_custom_fields_response_200 import ListCustomFieldsResponse200


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/custom_fields",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListCustomFieldsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListCustomFieldsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListCustomFieldsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListCustomFieldsResponse200]:
    """List Contact's custom fields

     Lists the custom fields that can be attached to a Contact.

    > ⚠️ Deprecated endpoint
    >
    > This endpoint has been deprecated. Please use the fully compatible `GET /contacts/custom_fields`
    endpoint instead.


    Required scope: `custom_fields:read`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListCustomFieldsResponse200]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> ListCustomFieldsResponse200 | None:
    """List Contact's custom fields

     Lists the custom fields that can be attached to a Contact.

    > ⚠️ Deprecated endpoint
    >
    > This endpoint has been deprecated. Please use the fully compatible `GET /contacts/custom_fields`
    endpoint instead.


    Required scope: `custom_fields:read`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListCustomFieldsResponse200
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[ListCustomFieldsResponse200]:
    """List Contact's custom fields

     Lists the custom fields that can be attached to a Contact.

    > ⚠️ Deprecated endpoint
    >
    > This endpoint has been deprecated. Please use the fully compatible `GET /contacts/custom_fields`
    endpoint instead.


    Required scope: `custom_fields:read`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ListCustomFieldsResponse200]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> ListCustomFieldsResponse200 | None:
    """List Contact's custom fields

     Lists the custom fields that can be attached to a Contact.

    > ⚠️ Deprecated endpoint
    >
    > This endpoint has been deprecated. Please use the fully compatible `GET /contacts/custom_fields`
    endpoint instead.


    Required scope: `custom_fields:read`

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ListCustomFieldsResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
