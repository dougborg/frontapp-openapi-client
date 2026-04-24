from enum import StrEnum


class AnalyticsScalarType(StrEnum):
    DURATION = "duration"
    NUMBER = "number"
    PERCENTAGE = "percentage"
    RESOURCE = "resource"
    STRING = "string"

    def __str__(self) -> str:
        return str(self.value)
