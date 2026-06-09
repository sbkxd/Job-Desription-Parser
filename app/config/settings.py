from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.constants import DEFAULT_APP_NAME, DEFAULT_DB_PORT, DEFAULT_LOG_LEVEL
from app.config.environment import AppEnv


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_NAME: str = DEFAULT_APP_NAME
    APP_ENV: AppEnv = AppEnv.LOCAL
    DEBUG: bool = False

    DB_HOST: str = "localhost"
    DB_PORT: int = DEFAULT_DB_PORT
    DB_NAME: str = "jd_parser"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    LOG_LEVEL: str = DEFAULT_LOG_LEVEL

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @computed_field
    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Global settings instance
settings = Settings()
