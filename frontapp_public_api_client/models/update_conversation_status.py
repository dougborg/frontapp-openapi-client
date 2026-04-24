from enum import StrEnum


class UpdateConversationStatus(StrEnum):
    ARCHIVED = "archived"
    DELETED = "deleted"
    OPEN = "open"
    SPAM = "spam"

    def __str__(self) -> str:
        return str(self.value)
