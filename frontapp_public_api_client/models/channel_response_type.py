from enum import StrEnum


class ChannelResponseType(StrEnum):
    CUSTOM = "custom"
    FACEBOOK = "facebook"
    FORM = "form"
    FRONT_CHAT = "front_chat"
    FRONT_MAIL = "front_mail"
    GMAIL = "gmail"
    GOOGLE_PLAY = "google_play"
    IMAP = "imap"
    INTERCOM = "intercom"
    LAYER_ANON = "layer_anon"
    OFFICE365 = "office365"
    SMTP = "smtp"
    TALKDESK = "talkdesk"
    TRULY = "truly"
    TWILIO = "twilio"
    TWILIO_WHATSAPP = "twilio_whatsapp"
    TWITTER = "twitter"
    TWITTER_DM = "twitter_dm"
    YALO_WHA = "yalo_wha"

    def __str__(self) -> str:
        return str(self.value)
