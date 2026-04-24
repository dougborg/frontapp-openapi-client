from enum import StrEnum


class EditDraftMode(StrEnum):
    SHARED = "shared"

    def __str__(self) -> str:
        return str(self.value)
