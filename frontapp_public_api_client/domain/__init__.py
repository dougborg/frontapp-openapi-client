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

from .contact import (
    Contact,
    ContactGroupRef,
    ContactHandle,
    ContactHandleSource,
    ContactNote,
)
from .contact_list import ContactList
from .conversation import (
    Conversation,
    ConversationPageCursor,
    RecipientSummary,
    TagSummary,
    TeammateSummary,
)
from .converters import to_unset, unwrap_unset
from .draft import AttachmentSummary, Draft
from .inbox import Inbox
from .tag import Tag
from .teammate import Teammate

__all__ = [
    "AttachmentSummary",
    "Contact",
    "ContactGroupRef",
    "ContactHandle",
    "ContactHandleSource",
    "ContactList",
    "ContactNote",
    "Conversation",
    "ConversationPageCursor",
    "Draft",
    "Inbox",
    "RecipientSummary",
    "Tag",
    "TagSummary",
    "Teammate",
    "TeammateSummary",
    "to_unset",
    "unwrap_unset",
]
