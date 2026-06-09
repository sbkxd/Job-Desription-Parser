import os
from unittest import mock

import pytest
from pydantic import ValidationError

from app.config.environment import AppEnv
from app.config.settings import Settings


def test_default_settings():
    settings = Settings(_env_file=None)
    assert settings.APP_NAME == "JD Skill Extraction Pipeline"
    assert settings.APP_ENV == AppEnv.LOCAL
    assert settings.DEBUG is False
    assert settings.DB_HOST == "localhost"
    assert settings.DB_PORT == 5432
    assert settings.DB_NAME == "jd_parser"
    assert settings.DB_USER == "postgres"
    assert settings.DB_PASSWORD == "postgres"
    assert settings.LOG_LEVEL == "INFO"

    expected_async_url = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/jd_parser"
    )
    expected_sync_url = "postgresql://postgres:postgres@localhost:5432/jd_parser"
    assert settings.database_url == expected_async_url
    assert settings.sync_database_url == expected_sync_url


def test_settings_env_override():
    env_mock = {
        "APP_NAME": "Test App",
        "APP_ENV": "dev",
        "DEBUG": "True",
        "DB_HOST": "test-db",
        "DB_PORT": "5433",
        "DB_NAME": "test_db_name",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password",
        "LOG_LEVEL": "DEBUG",
    }
    with mock.patch.dict(os.environ, env_mock):
        settings = Settings()
        assert settings.APP_NAME == "Test App"
        assert settings.APP_ENV == AppEnv.DEVELOPMENT
        assert settings.DEBUG is True
        assert settings.DB_HOST == "test-db"
        assert settings.DB_PORT == 5433
        assert settings.DB_NAME == "test_db_name"
        assert settings.DB_USER == "test_user"
        assert settings.DB_PASSWORD == "test_password"
        assert settings.LOG_LEVEL == "DEBUG"

        expected_async_url = (
            "postgresql+asyncpg://test_user:test_password@test-db:5433/test_db_name"
        )
        assert settings.database_url == expected_async_url


def test_invalid_env_validation():
    env_mock = {
        "APP_ENV": "invalid-env-name",
    }
    with mock.patch.dict(os.environ, env_mock):
        with pytest.raises(ValidationError):
            Settings()
