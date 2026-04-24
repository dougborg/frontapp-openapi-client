"""Pydantic domain models for Frontapp entities.

Hand-written domain models representing business entities from the Frontapp API,
separate from the generated attrs API request/response models. Use these for
business logic, validation, and ergonomic access to API data.

Example:
    ```python
    from frontapp_public_api_client import FrontappClient

    async with FrontappClient() as client:
        conversations = await client.conversations.list(limit=50)
        for conv in conversations:
            print(f"{conv.subject}: {conv.status}")
    ```
"""

from .base import FrontappBaseModel
from .conversation import (
    Conversation,
    ConversationPageCursor,
    RecipientSummary,
    TagSummary,
    TeammateSummary,
)
from .converters import to_unset, unwrap_unset

__all__ = [
    "Conversation",
    "ConversationPageCursor",
    "FrontappBaseModel",
    "RecipientSummary",
    "TagSummary",
    "TeammateSummary",
    "to_unset",
    "unwrap_unset",
]
