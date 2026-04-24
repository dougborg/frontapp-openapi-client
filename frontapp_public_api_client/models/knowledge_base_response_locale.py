from enum import StrEnum


class KnowledgeBaseResponseLocale(StrEnum):
    EN = "en"
    FR = "fr"

    def __str__(self) -> str:
        return str(self.value)
