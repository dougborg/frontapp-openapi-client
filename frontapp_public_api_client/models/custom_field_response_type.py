from enum import StrEnum


class CustomFieldResponseType(StrEnum):
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    ENUM = "enum"
    INBOX = "inbox"
    NUMBER = "number"
    STRING = "string"
    TEAMMATE = "teammate"

    def __str__(self) -> str:
        return str(self.value)
