from enum import StrEnum


class KnowledgeBaseCategoryResponseLocale(StrEnum):
    EN = "en"
    FR = "fr"

    def __str__(self) -> str:
        return str(self.value)
