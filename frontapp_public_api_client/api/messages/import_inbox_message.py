from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...client_types import UNSET, Response, Unset
from ...models.import_inbox_message_response_202 import ImportInboxMessageResponse202
from ...models.import_message import ImportMessage


def _get_kwargs(
    inbox_id: str = "inb_123",
    *,
    body: ImportMessage | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/inboxes/{inbox_id}/imported_messages".format(
            inbox_id=quote(str(inbox_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ImportInboxMessageResponse202 | None:
    if response.status_code == 202:
        response_202 = ImportInboxMessageResponse202.from_dict(response.json())

        return response_202

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ImportInboxMessageResponse202]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    inbox_id: str = "inb_123",
    *,
    client: AuthenticatedClient | Client,
    body: ImportMessage | Unset = UNSET,
) -> Response[ImportInboxMessageResponse202]:
    """Import message

     Use this endpoint to import conversations into Front without sending data through a channel. Typical
    use cases include importing historical conversations or creating new conversations from non-standard
    sources, such as web form submissions that can't use the default Form channel (for example, forms
    that don't have static URLs or form providers that send email notifications after submission). Avoid
    using this endpoint for conversations that can be handled by a dedicated Front channel—instead, use
    the [Create message](https://dev.frontapp.com/reference/create-message) endpoint to send (rather
    than import) a new message.

    Required scope: `messages:write`

    Args:
        inbox_id (str):  Default: 'inb_123'.
        body (ImportMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ImportInboxMessageResponse202]
    """

    kwargs = _get_kwargs(
        inbox_id=inbox_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    inbox_id: str = "inb_123",
    *,
    client: AuthenticatedClient | Client,
    body: ImportMessage | Unset = UNSET,
) -> ImportInboxMessageResponse202 | None:
    """Import message

     Use this endpoint to import conversations into Front without sending data through a channel. Typical
    use cases include importing historical conversations or creating new conversations from non-standard
    sources, such as web form submissions that can't use the default Form channel (for example, forms
    that don't have static URLs or form providers that send email notifications after submission). Avoid
    using this endpoint for conversations that can be handled by a dedicated Front channel—instead, use
    the [Create message](https://dev.frontapp.com/reference/create-message) endpoint to send (rather
    than import) a new message.

    Required scope: `messages:write`

    Args:
        inbox_id (str):  Default: 'inb_123'.
        body (ImportMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ImportInboxMessageResponse202
    """

    return sync_detailed(
        inbox_id=inbox_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    inbox_id: str = "inb_123",
    *,
    client: AuthenticatedClient | Client,
    body: ImportMessage | Unset = UNSET,
) -> Response[ImportInboxMessageResponse202]:
    """Import message

     Use this endpoint to import conversations into Front without sending data through a channel. Typical
    use cases include importing historical conversations or creating new conversations from non-standard
    sources, such as web form submissions that can't use the default Form channel (for example, forms
    that don't have static URLs or form providers that send email notifications after submission). Avoid
    using this endpoint for conversations that can be handled by a dedicated Front channel—instead, use
    the [Create message](https://dev.frontapp.com/reference/create-message) endpoint to send (rather
    than import) a new message.

    Required scope: `messages:write`

    Args:
        inbox_id (str):  Default: 'inb_123'.
        body (ImportMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[ImportInboxMessageResponse202]
    """

    kwargs = _get_kwargs(
        inbox_id=inbox_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    inbox_id: str = "inb_123",
    *,
    client: AuthenticatedClient | Client,
    body: ImportMessage | Unset = UNSET,
) -> ImportInboxMessageResponse202 | None:
    """Import message

     Use this endpoint to import conversations into Front without sending data through a channel. Typical
    use cases include importing historical conversations or creating new conversations from non-standard
    sources, such as web form submissions that can't use the default Form channel (for example, forms
    that don't have static URLs or form providers that send email notifications after submission). Avoid
    using this endpoint for conversations that can be handled by a dedicated Front channel—instead, use
    the [Create message](https://dev.frontapp.com/reference/create-message) endpoint to send (rather
    than import) a new message.

    Required scope: `messages:write`

    Args:
        inbox_id (str):  Default: 'inb_123'.
        body (ImportMessage | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        ImportInboxMessageResponse202
    """

    return (
        await asyncio_detailed(
            inbox_id=inbox_id,
            client=client,
            body=body,
        )
    ).parsed
