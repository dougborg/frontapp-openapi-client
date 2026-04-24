from enum import StrEnum


class CreateShiftColor(StrEnum):
    BLACK = "black"
    BLUE = "blue"
    GREEN = "green"
    GREY = "grey"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    TEAL = "teal"
    YELLOW = "yellow"

    def __str__(self) -> str:
        return str(self.value)
