from typing import List

from environs import Env
from pydantic_settings import BaseSettings, SettingsConfigDict

env = Env()


def get_logging_config(log_level: str) -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {process} {thread} "
                "{pathname}:{funcName}:{lineno} - {message}",
                "style": "{",
            },
        },
        "handlers": {
            "layered_architecture": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "loggers": {
            "layered_architecture": {
                "handlers": ["layered_architecture"],
                "level": log_level,
                "propagate": False,
            },
        },
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    PROJECT_NAME: str = "Layered Architecture Demo"
    DESCRIPTION: str = (
        "A demo project showcasing layered architecture with FastAPI"
    )
    VERSION: str = env.str("VERSION", "0.1.0")
    DEBUG: bool = env.bool("DEBUG", True)
    LOGGING_CONFIG: dict = get_logging_config(
        log_level=env.str("LOG_LEVEL", "INFO"),
    )

    # Database
    DATABASE_URL: str = env.str(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/layered_arch",  # pragma: allowlist secret
    )
    TEST_DATABASE_URL: str = env.str(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db",  # pragma: allowlist secret
    )

    # Security
    BACKEND_CORS_ORIGINS: List[str] = env.list("BACKEND_CORS_ORIGINS", ["*"])
    ALLOWED_HOSTS: List[str] = env.list("ALLOWED_HOSTS", ["*"])


settings = Settings()
