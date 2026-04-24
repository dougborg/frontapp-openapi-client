"""Base class for domain classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frontapp_public_api_client.frontapp_client import FrontappClient


class Base:
    """Base class for all domain classes.

    Provides common functionality and access to the FrontappClient instance.

    Args:
        client: The FrontappClient instance to use for API calls.
    """

    def __init__(self, client: FrontappClient) -> None:
        """Initialize with a client instance.

        Args:
            client: The FrontappClient instance to use for API calls.
        """
        self._client = client
