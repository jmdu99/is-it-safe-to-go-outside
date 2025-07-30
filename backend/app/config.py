"""Application configuration and logging setup.

This module centralizes environment variable management and logging configuration
for the backend. It uses ``pydantic-settings`` to load configuration from
environment variables and an optional ``.env`` file. Logging is configured
using the built‑in ``logging`` module with a simple structured format and
outputs to standard out.
"""

from __future__ import annotations

import logging
from logging.config import dictConfig
from pydantic_settings import BaseSettings, SettingsConfigDict


def _configure_logging() -> None:
    """Configure application wide logging.

    This function sets up a basic structured logging configuration. The
    formatter includes timestamps, log levels and the logger name. Logs are
    emitted to the console (stdout). The configuration is applied once when
    this module is imported.
    """
    logging_config: dict[str, object] = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }
    dictConfig(logging_config)


# Initialize logging as soon as the module is imported
_configure_logging()

# Expose a logger that can be used throughout the application
logger = logging.getLogger("respiratory_risk_backend")


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    The fields map directly to expected environment variables. Default values
    are provided to facilitate local development and testing. See the
    documentation for details on each configuration variable.
    """

    mapbox_token: str = ""  #: Token for the Mapbox Search API
    openweather_key: str = ""  #: API key for OpenWeatherMap APIs
    database_url: str = ""  #: PostgreSQL connection string
    cache_host: str = "localhost"
    cache_port: int = 6379
    cache_password: str = ""
    cache_ttl_seconds: int = 3600

    # Use pydantic‑settings to locate the .env file and load it
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Instantiate a singleton settings object on import so it can be reused
settings = Settings()

__all__ = ["settings", "logger"]
