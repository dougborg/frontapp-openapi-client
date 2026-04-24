from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import Response
from ...models.message_template_folder_response import MessageTemplateFolderResponse


def _get_kwargs(
    message_template_folder_id: str = "rsf_123",
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/message_template_folders/{message_template_folder_id}".format(
            message_template_folder_id=quote(str(message_template_folder_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> MessageTemplateFolderResponse | None:
    if response.status_code == 200:
        response_200 = MessageTemplateFolderResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[MessageTemplateFolderResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    message_template_folder_id: str = "rsf_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[MessageTemplateFolderResponse]:
    """Get folder

     Fetch a message template folder.

    Required scope: `message_templates:read`

    Args:
        message_template_folder_id (str):  Default: 'rsf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateFolderResponse]
    """

    kwargs = _get_kwargs(
        message_template_folder_id=message_template_folder_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    message_template_folder_id: str = "rsf_123",
    *,
    client: AuthenticatedClient | Client,
) -> MessageTemplateFolderResponse | None:
    """Get folder

     Fetch a message template folder.

    Required scope: `message_templates:read`

    Args:
        message_template_folder_id (str):  Default: 'rsf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageTemplateFolderResponse
    """

    return sync_detailed(
        message_template_folder_id=message_template_folder_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    message_template_folder_id: str = "rsf_123",
    *,
    client: AuthenticatedClient | Client,
) -> Response[MessageTemplateFolderResponse]:
    """Get folder

     Fetch a message template folder.

    Required scope: `message_templates:read`

    Args:
        message_template_folder_id (str):  Default: 'rsf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateFolderResponse]
    """

    kwargs = _get_kwargs(
        message_template_folder_id=message_template_folder_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    message_template_folder_id: str = "rsf_123",
    *,
    client: AuthenticatedClient | Client,
) -> MessageTemplateFolderResponse | None:
    """Get folder

     Fetch a message template folder.

    Required scope: `message_templates:read`

    Args:
        message_template_folder_id (str):  Default: 'rsf_123'.


    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageTemplateFolderResponse
    """

    return (
        await asyncio_detailed(
            message_template_folder_id=message_template_folder_id,
            client=client,
        )
    ).parsed
