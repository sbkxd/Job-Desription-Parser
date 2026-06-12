"""Centralized application settings using pydantic-settings."""

from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.constants import DEFAULT_APP_NAME, DEFAULT_DB_PORT, DEFAULT_LOG_LEVEL
from app.config.environment import AppEnv


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application identity
    APP_NAME: str = DEFAULT_APP_NAME
    APP_VERSION: str = "0.1.0"
    APP_ENV: AppEnv = AppEnv.LOCAL
    DEBUG: bool = False

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = DEFAULT_DB_PORT
    DB_NAME: str = "jd_parser"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    # API Keys
    MISTRAL_API_KEY: str = ""

    # Logging
    LOG_LEVEL: str = DEFAULT_LOG_LEVEL
    JSON_LOGS: bool = False

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    # ---------------------------------------------------------------------------
    # Computed / convenience properties
    # ---------------------------------------------------------------------------

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Lowercase aliases for cleaner access
    @property
    def app_name(self) -> str:
        return self.APP_NAME

    @property
    def app_version(self) -> str:
        return self.APP_VERSION

    @property
    def environment(self) -> str:
        return self.APP_ENV.value

    @property
    def log_level(self) -> str:
        return self.LOG_LEVEL

    @property
    def json_logs(self) -> bool:
        return self.JSON_LOGS

    @property
    def allowed_origins(self) -> list[str]:
        return self.ALLOWED_ORIGINS


# Global singleton (direct usage in legacy code)
settings = Settings()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached settings singleton."""
    return Settings()
