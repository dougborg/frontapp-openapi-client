from enum import StrEnum


class KnowledgeBaseSlimResponseType(StrEnum):
    EXTERNAL = "external"
    INTERNAL = "internal"

    def __str__(self) -> str:
        return str(self.value)
