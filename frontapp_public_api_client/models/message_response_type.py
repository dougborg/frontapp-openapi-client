from enum import StrEnum


class MessageResponseType(StrEnum):
    CALL = "call"
    CUSTOM = "custom"
    EMAIL = "email"
    FACEBOOK = "facebook"
    FRONT_CHAT = "front_chat"
    GOOGLEPLAY = "googleplay"
    INTERCOM = "intercom"
    INTERNAL = "internal"
    PHONE_CALL = "phone-call"
    SMS = "sms"
    TWEET = "tweet"
    TWEET_DM = "tweet_dm"
    WHATSAPP = "whatsapp"
    YALO_WHA = "yalo_wha"

    def __str__(self) -> str:
        return str(self.value)
