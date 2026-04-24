from enum import StrEnum


class CreateConversationType(StrEnum):
    DISCUSSION = "discussion"

    def __str__(self) -> str:
        return str(self.value)
