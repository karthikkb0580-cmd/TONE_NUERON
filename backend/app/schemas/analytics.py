from pydantic import BaseModel


class AnalyticsItem(BaseModel):
    name: str
    count: int


class DailyUsage(BaseModel):
    date: str
    count: int


class AnalyticsSummary(BaseModel):
    period_days: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    average_processing_time_ms: float
    features: list[AnalyticsItem]
    languages: list[AnalyticsItem]
    tones: list[AnalyticsItem]
    daily_usage: list[DailyUsage]
