from enum import StrEnum


class KnowledgeBaseArticleCreateStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"

    def __str__(self) -> str:
        return str(self.value)
