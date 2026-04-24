from enum import StrEnum


class RecipientResponseRole(StrEnum):
    BCC = "bcc"
    CC = "cc"
    FROM = "from"
    REPLY_TO = "reply-to"
    TO = "to"

    def __str__(self) -> str:
        return str(self.value)
