from enum import StrEnum


class EventResponseSourceMetaType(StrEnum):
    API = "api"
    GMAIL = "gmail"
    IMAP = "imap"
    INBOXES = "inboxes"
    OAUTH_CLIENT = "oauth_client"
    RECIPIENT = "recipient"
    REMINDER = "reminder"
    RULE = "rule"
    TEAMMATE = "teammate"

    def __str__(self) -> str:
        return str(self.value)
