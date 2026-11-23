from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    POSTGRES_USER: str = "tone_neuron"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "tone_neuron_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    RESEND_API_KEY: str
    EMAIL_FROM: str = "onboarding@resend.dev"

    OTP_EXPIRE_MINUTES: int = 3
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_COOLDOWN_SECONDS: int = 60

    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    LOGIN_MAX_FAILED_ATTEMPTS: int = 10

    LOGIN_FAILURE_WINDOW_SECONDS: int = 900  

    @property
    def DATABASE_URL(self) -> str:
        username = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)

        return (
            f"postgresql+psycopg://{username}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()