from pydantic import BaseModel


class PrivacySummary(BaseModel):
    conversation_history_enabled: bool
    analytics_enabled: bool
    total_conversations: int
    total_messages: int
    total_feedback: int
    registered_devices: int
    analytics_events: int


class CleanupResponse(BaseModel):
    expired_otps: int
    expired_sessions: int
    old_analytics_events: int
    old_security_events: int
