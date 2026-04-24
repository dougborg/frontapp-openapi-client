from enum import StrEnum


class ContactHandleSource(StrEnum):
    CUSTOM = "custom"
    EMAIL = "email"
    FACEBOOK = "facebook"
    FRONT_CHAT = "front_chat"
    INTERCOM = "intercom"
    PHONE = "phone"
    TWITTER = "twitter"

    def __str__(self) -> str:
        return str(self.value)
