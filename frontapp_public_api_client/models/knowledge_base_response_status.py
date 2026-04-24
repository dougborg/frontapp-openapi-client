from enum import StrEnum


class KnowledgeBaseResponseStatus(StrEnum):
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"

    def __str__(self) -> str:
        return str(self.value)
