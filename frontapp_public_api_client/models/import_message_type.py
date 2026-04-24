from enum import StrEnum


class ImportMessageType(StrEnum):
    CUSTOM = "custom"
    EMAIL = "email"
    INTERCOM = "intercom"
    SMS = "sms"

    def __str__(self) -> str:
        return str(self.value)
