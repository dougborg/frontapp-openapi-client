from enum import StrEnum


class AnalyticsExportResponseStatus(StrEnum):
    DONE = "done"
    FAILED = "failed"
    RUNNING = "running"
    TOO_BIG = "too_big"

    def __str__(self) -> str:
        return str(self.value)
