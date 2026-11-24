from typing import Literal

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class SecuritySettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    APP_ENV: Literal[
        "development",
        "testing",
        "production",
    ] = "development"

    CORS_ALLOWED_ORIGINS: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )

    MAX_REQUEST_SIZE_BYTES: int = Field(
        default=1048576,
        ge=1024,
        le=10485760,
    )

    REQUEST_LOGGING_ENABLED: bool = True

    @property
    def allowed_origins(self) -> list[str]:

        origins = [
            origin.strip()
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

        if "*" in origins:
            raise ValueError(
                "Wildcard CORS origins are not allowed."
            )

        return origins


security_settings = SecuritySettings()
