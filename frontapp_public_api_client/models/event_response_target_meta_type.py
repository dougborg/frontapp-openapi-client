from enum import StrEnum


class EventResponseTargetMetaType(StrEnum):
    COMMENT = "comment"
    CUSTOM_FIELD = "custom_field"
    DELETED_CONVERSATION_IDS = "deleted_conversation_ids"
    INBOXES = "inboxes"
    LINK = "link"
    MESSAGE = "message"
    TAG = "tag"
    TEAMMATE = "teammate"

    def __str__(self) -> str:
        return str(self.value)
