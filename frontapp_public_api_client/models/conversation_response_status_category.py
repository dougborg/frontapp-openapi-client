from enum import StrEnum


class ConversationResponseStatusCategory(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    WAITING = "waiting"

    def __str__(self) -> str:
        return str(self.value)
