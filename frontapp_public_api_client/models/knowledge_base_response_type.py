from enum import StrEnum


class KnowledgeBaseResponseType(StrEnum):
    EXTERNAL = "external"
    INTERNAL = "internal"

    def __str__(self) -> str:
        return str(self.value)
