from pydantic import Field, SecretStr, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class MLSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    ML_SERVICE_URL: AnyHttpUrl = "http://127.0.0.1:8001"

    ML_SERVICE_API_KEY: SecretStr

    ML_SERVICE_TIMEOUT_SECONDS: float = Field(
        default=60,
        ge=1,
        le=300,
    )

    ML_SERVICE_CONNECT_TIMEOUT_SECONDS: float = Field(
        default=5,
        ge=1,
        le=30,
    )


ml_settings = MLSettings()
