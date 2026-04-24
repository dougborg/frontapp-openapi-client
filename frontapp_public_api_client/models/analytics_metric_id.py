from enum import StrEnum


class AnalyticsMetricId(StrEnum):
    AVG_CSAT_SURVEY_RESPONSE = "avg_csat_survey_response"
    AVG_FIRST_RESPONSE_TIME = "avg_first_response_time"
    AVG_HANDLE_TIME = "avg_handle_time"
    AVG_REPLIES_TO_RESOLUTION = "avg_replies_to_resolution"
    AVG_RESOLUTION_TIME = "avg_resolution_time"
    AVG_RESPONSE_TIME = "avg_response_time"
    AVG_SLA_BREACH_TIME = "avg_sla_breach_time"
    AVG_TOTAL_REPLY_TIME = "avg_total_reply_time"
    NEW_SEGMENTS_COUNT = "new_segments_count"
    NUM_ACTIVE_SEGMENTS_FULL = "num_active_segments_full"
    NUM_ARCHIVED_SEGMENTS = "num_archived_segments"
    NUM_ARCHIVED_SEGMENTS_WITH_REPLY = "num_archived_segments_with_reply"
    NUM_CLOSED_SEGMENTS = "num_closed_segments"
    NUM_CSAT_SURVEY_RESPONSE = "num_csat_survey_response"
    NUM_MESSAGES_RECEIVED = "num_messages_received"
    NUM_MESSAGES_SENT = "num_messages_sent"
    NUM_OPEN_SEGMENTS_END = "num_open_segments_end"
    NUM_OPEN_SEGMENTS_START = "num_open_segments_start"
    NUM_RESOLVED_SEGMENTS = "num_resolved_segments"
    NUM_SLA_BREACH = "num_sla_breach"
    NUM_UNRESOLVED_ACTIVE_SEGMENTS = "num_unresolved_active_segments"
    NUM_WORKLOAD_SEGMENTS = "num_workload_segments"
    PCT_CSAT_SURVEY_SATISFACTION = "pct_csat_survey_satisfaction"
    PCT_RESOLVED_ON_FIRST_REPLY = "pct_resolved_on_first_reply"
    PCT_TAGGED_CONVERSATIONS = "pct_tagged_conversations"

    def __str__(self) -> str:
        return str(self.value)
