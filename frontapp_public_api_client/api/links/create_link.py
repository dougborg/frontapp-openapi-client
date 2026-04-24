from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_link import CreateLink
from ...models.link_response import LinkResponse


def _get_kwargs(
    *,
    body: CreateLink | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/links",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LinkResponse | None:
    if response.status_code == 201:
        response_201 = LinkResponse.from_dict(response.json())

        return response_201

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[LinkResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateLink | Unset = UNSET,
) -> Response[LinkResponse]:
    """Create link

     Create a link. You must supply either `pattern` or `external_url` in the request, but not both
    (`pattern` is for application objects while `external_url` is for standard links). If `pattern` is
    provided, the API call updates the application objects matching the exact pattern. Keep in mind this
    endpoint only creates or updates an existing link from an application object. It does not create new
    application objects. If the link is resolved to an installed links integration, any name retrieved
    from the integration will override the provided name in the request.

    Required scope: `links:write`

    Args:
        body (CreateLink | Unset): A link is used to connect a Front conversation to an external
            resource.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[LinkResponse]
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
    body: CreateLink | Unset = UNSET,
) -> LinkResponse | None:
    """Create link

     Create a link. You must supply either `pattern` or `external_url` in the request, but not both
    (`pattern` is for application objects while `external_url` is for standard links). If `pattern` is
    provided, the API call updates the application objects matching the exact pattern. Keep in mind this
    endpoint only creates or updates an existing link from an application object. It does not create new
    application objects. If the link is resolved to an installed links integration, any name retrieved
    from the integration will override the provided name in the request.

    Required scope: `links:write`

    Args:
        body (CreateLink | Unset): A link is used to connect a Front conversation to an external
            resource.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        LinkResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateLink | Unset = UNSET,
) -> Response[LinkResponse]:
    """Create link

     Create a link. You must supply either `pattern` or `external_url` in the request, but not both
    (`pattern` is for application objects while `external_url` is for standard links). If `pattern` is
    provided, the API call updates the application objects matching the exact pattern. Keep in mind this
    endpoint only creates or updates an existing link from an application object. It does not create new
    application objects. If the link is resolved to an installed links integration, any name retrieved
    from the integration will override the provided name in the request.

    Required scope: `links:write`

    Args:
        body (CreateLink | Unset): A link is used to connect a Front conversation to an external
            resource.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[LinkResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateLink | Unset = UNSET,
) -> LinkResponse | None:
    """Create link

     Create a link. You must supply either `pattern` or `external_url` in the request, but not both
    (`pattern` is for application objects while `external_url` is for standard links). If `pattern` is
    provided, the API call updates the application objects matching the exact pattern. Keep in mind this
    endpoint only creates or updates an existing link from an application object. It does not create new
    application objects. If the link is resolved to an installed links integration, any name retrieved
    from the integration will override the provided name in the request.

    Required scope: `links:write`

    Args:
        body (CreateLink | Unset): A link is used to connect a Front conversation to an external
            resource.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        LinkResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
