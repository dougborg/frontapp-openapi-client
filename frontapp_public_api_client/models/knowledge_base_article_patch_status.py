from enum import StrEnum


class KnowledgeBaseArticlePatchStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"

    def __str__(self) -> str:
        return str(self.value)
