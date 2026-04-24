from enum import StrEnum


class StatusResponseCategory(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    WAITING = "waiting"

    def __str__(self) -> str:
        return str(self.value)
