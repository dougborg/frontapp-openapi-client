from enum import StrEnum


class CustomMessageBodyFormat(StrEnum):
    HTML = "html"
    MARKDOWN = "markdown"

    def __str__(self) -> str:
        return str(self.value)
