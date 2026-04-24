from enum import StrEnum


class ListTeamFoldersSortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"

    def __str__(self) -> str:
        return str(self.value)
