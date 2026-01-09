"""
Application settings loaded from environment.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_host: str
    app_port: int

    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    redis_url: str
    celery_broker_url: str
    celery_result_backend: str
    celery_timezone: str
    celery_default_queue: str

    cbr_rates_url: str
    cbr_fetch_cron: str

    @property
    def database_url(self) -> str:
        """Async SQLAlchemy URL for Postgres."""
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
