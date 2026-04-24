from enum import StrEnum


class ConversationResponseStatus(StrEnum):
    ARCHIVED = "archived"
    ASSIGNED = "assigned"
    DELETED = "deleted"
    UNASSIGNED = "unassigned"

    def __str__(self) -> str:
        return str(self.value)
