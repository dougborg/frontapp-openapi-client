from enum import StrEnum


class ImportMessageBodyFormat(StrEnum):
    HTML = "html"
    MARKDOWN = "markdown"

    def __str__(self) -> str:
        return str(self.value)
