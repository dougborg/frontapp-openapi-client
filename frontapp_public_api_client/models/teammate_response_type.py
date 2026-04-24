from enum import StrEnum


class TeammateResponseType(StrEnum):
    API = "API"
    CSAT = "CSAT"
    INTEGRATION = "integration"
    MACRO = "macro"
    RULE = "rule"
    USER = "user"
    VISITOR = "visitor"

    def __str__(self) -> str:
        return str(self.value)
