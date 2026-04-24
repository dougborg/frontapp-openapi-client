from enum import StrEnum


class CreateChannelType(StrEnum):
    CUSTOM = "custom"
    SMTP = "smtp"
    TWILIO = "twilio"

    def __str__(self) -> str:
        return str(self.value)
