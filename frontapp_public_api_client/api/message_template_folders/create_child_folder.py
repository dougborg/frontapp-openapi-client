from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.create_message_template_folder_as_child import (
    CreateMessageTemplateFolderAsChild,
)
from ...models.message_template_folder_response import MessageTemplateFolderResponse


def _get_kwargs(
    message_template_folder_id: str = "rsf_123",
    *,
    body: CreateMessageTemplateFolderAsChild | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/message_template_folders/{message_template_folder_id}/message_template_folders".format(
            message_template_folder_id=quote(str(message_template_folder_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> MessageTemplateFolderResponse | None:
    if response.status_code == 201:
        response_201 = MessageTemplateFolderResponse.from_dict(response.json())

        return response_201

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
    body: CreateMessageTemplateFolderAsChild | Unset = UNSET,
) -> Response[MessageTemplateFolderResponse]:
    """Create child folder

     Create a new message template folder as a child of the given folder

    Required scope: `message_templates:write`

    Args:
        message_template_folder_id (str):  Default: 'rsf_123'.
        body (CreateMessageTemplateFolderAsChild | Unset): A message template folder that is used
            to store message templates or other folders.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateFolderResponse]
    """

    kwargs = _get_kwargs(
        message_template_folder_id=message_template_folder_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    message_template_folder_id: str = "rsf_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateMessageTemplateFolderAsChild | Unset = UNSET,
) -> MessageTemplateFolderResponse | None:
    """Create child folder

     Create a new message template folder as a child of the given folder

    Required scope: `message_templates:write`

    Args:
        message_template_folder_id (str):  Default: 'rsf_123'.
        body (CreateMessageTemplateFolderAsChild | Unset): A message template folder that is used
            to store message templates or other folders.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        MessageTemplateFolderResponse
    """

    return sync_detailed(
        message_template_folder_id=message_template_folder_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    message_template_folder_id: str = "rsf_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateMessageTemplateFolderAsChild | Unset = UNSET,
) -> Response[MessageTemplateFolderResponse]:
    """Create child folder

     Create a new message template folder as a child of the given folder

    Required scope: `message_templates:write`

    Args:
        message_template_folder_id (str):  Default: 'rsf_123'.
        body (CreateMessageTemplateFolderAsChild | Unset): A message template folder that is used
            to store message templates or other folders.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[MessageTemplateFolderResponse]
    """

    kwargs = _get_kwargs(
        message_template_folder_id=message_template_folder_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    message_template_folder_id: str = "rsf_123",
    *,
    client: AuthenticatedClient | Client,
    body: CreateMessageTemplateFolderAsChild | Unset = UNSET,
) -> MessageTemplateFolderResponse | None:
    """Create child folder

     Create a new message template folder as a child of the given folder

    Required scope: `message_templates:write`

    Args:
        message_template_folder_id (str):  Default: 'rsf_123'.
        body (CreateMessageTemplateFolderAsChild | Unset): A message template folder that is used
            to store message templates or other folders.

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
            body=body,
        )
    ).parsed
