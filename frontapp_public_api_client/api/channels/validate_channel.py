from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.validate_channel_response_202 import ValidateChannelResponse202


def _get_kwargs(
    channel_id: str = "cha_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/channels/{channel_id}/validate".format(
            channel_id=quote(str(channel_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ValidateChannelResponse202 | None:
    if response.status_code == 202:
        response_202 = ValidateChannelResponse202.from_dict(response.json())

        return response_202

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ValidateChannelResponse202]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ValidateChannelResponse202]:
    """Validate channel

     Asynchronously validate an SMTP channel (this endpoint is irrelevant to other channel types). When
    you create an SMTP channel via the API, [create a
    channel](https://dev.frontapp.com/reference/post_inboxes-inbox-id-channels) with type smtp and the
    send_as set to the needed email address. You then [configure the email
    provider](https://help.front.com/en/articles/2081), after which you use this endpoint to
    asynchronously validate the SMTP settings.

    Required scope: `channels:write`

    Args:
        channel_id (str):  Default: 'cha_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ValidateChannelResponse202]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
) -> ValidateChannelResponse202 | None:
    """Validate channel

     Asynchronously validate an SMTP channel (this endpoint is irrelevant to other channel types). When
    you create an SMTP channel via the API, [create a
    channel](https://dev.frontapp.com/reference/post_inboxes-inbox-id-channels) with type smtp and the
    send_as set to the needed email address. You then [configure the email
    provider](https://help.front.com/en/articles/2081), after which you use this endpoint to
    asynchronously validate the SMTP settings.

    Required scope: `channels:write`

    Args:
        channel_id (str):  Default: 'cha_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ValidateChannelResponse202
    """

    return sync_detailed(
        channel_id=channel_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[ValidateChannelResponse202]:
    """Validate channel

     Asynchronously validate an SMTP channel (this endpoint is irrelevant to other channel types). When
    you create an SMTP channel via the API, [create a
    channel](https://dev.frontapp.com/reference/post_inboxes-inbox-id-channels) with type smtp and the
    send_as set to the needed email address. You then [configure the email
    provider](https://help.front.com/en/articles/2081), after which you use this endpoint to
    asynchronously validate the SMTP settings.

    Required scope: `channels:write`

    Args:
        channel_id (str):  Default: 'cha_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ValidateChannelResponse202]
    """

    kwargs = _get_kwargs(
        channel_id=channel_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    channel_id: str = "cha_123",
    *,
    client: AuthenticatedClient | Client,
) -> ValidateChannelResponse202 | None:
    """Validate channel

     Asynchronously validate an SMTP channel (this endpoint is irrelevant to other channel types). When
    you create an SMTP channel via the API, [create a
    channel](https://dev.frontapp.com/reference/post_inboxes-inbox-id-channels) with type smtp and the
    send_as set to the needed email address. You then [configure the email
    provider](https://help.front.com/en/articles/2081), after which you use this endpoint to
    asynchronously validate the SMTP settings.

    Required scope: `channels:write`

    Args:
        channel_id (str):  Default: 'cha_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ValidateChannelResponse202
    """

    return (
        await asyncio_detailed(
            channel_id=channel_id,
            client=client,
        )
    ).parsed
