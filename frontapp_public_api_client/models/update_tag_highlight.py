from enum import StrEnum


class UpdateTagHighlight(StrEnum):
    BLUE = "blue"
    GREEN = "green"
    GREY = "grey"
    LIGHT_BLUE = "light-blue"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    YELLOW = "yellow"

    def __str__(self) -> str:
        return str(self.value)
