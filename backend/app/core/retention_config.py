from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RetentionSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    ANALYTICS_RETENTION_DAYS: int = Field(
        default=90,
        ge=1,
        le=3650,
    )

    SECURITY_EVENT_RETENTION_DAYS: int = Field(
        default=180,
        ge=1,
        le=3650,
    )


retention_settings = RetentionSettings()
