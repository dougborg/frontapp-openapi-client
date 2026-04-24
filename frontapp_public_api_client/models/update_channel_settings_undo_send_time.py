from enum import IntEnum


class UpdateChannelSettingsUndoSendTime(IntEnum):
    VALUE_0 = 0
    VALUE_5 = 5
    VALUE_10 = 10
    VALUE_15 = 15
    VALUE_30 = 30
    VALUE_60 = 60

    def __str__(self) -> str:
        return str(self.value)
