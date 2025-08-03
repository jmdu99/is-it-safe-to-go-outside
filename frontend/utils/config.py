"""
Configuration management for the Safe Air frontend.

This module defines a Config class that reads environment variables to
configure the backend URL, request timeouts and other settings. It also
provides default values for development and a helper to load variables
from a ``.env`` file. All strings are provided in English.
"""

from __future__ import annotations

import os
from typing import Optional, List


class Config:
    # Backend API
    @property
    def BACKEND_URL(self) -> str:
        return os.getenv("BACKEND_URL", "")

    @property
    def API_TIMEOUT(self) -> int:
        return int(os.getenv("API_TIMEOUT", "10"))

    # Development mode
    @property
    def DEVELOPMENT_MODE(self) -> bool:
        return os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"

    @property
    def USE_MOCK_API(self) -> bool:
        return os.getenv("USE_MOCK_API", "false").lower() == "true"

    # Mapbox (if needed by the frontend)
    @property
    def MAPBOX_PUBLIC_TOKEN(self) -> Optional[str]:
        return os.getenv("MAPBOX_PUBLIC_TOKEN")

    # Streamlit page configuration
    @property
    def PAGE_TITLE(self) -> str:
        return "Is it safe to go outside?"

    @property
    def PAGE_ICON(self) -> str:
        # Use a lungs emoji to better represent the respiratory focus
        return "🫁"

    @property
    def LAYOUT(self) -> str:
        return "wide"

    # Caching
    @property
    def CACHE_TTL(self) -> int:
        return int(os.getenv("CACHE_TTL", "300"))

    # Logging
    @property
    def LOG_LEVEL(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    def is_production(self) -> bool:
        return not self.DEVELOPMENT_MODE

    def get_api_client_class(self):
        if self.USE_MOCK_API:
            from services.api_client import MockAPIClient

            return MockAPIClient
        else:
            from services.api_client import APIClient

            return APIClient

    def validate_config(self) -> List[str]:
        errors: List[str] = []
        if not self.BACKEND_URL:
            errors.append("BACKEND_URL is required")
        if self.API_TIMEOUT <= 0:
            errors.append("API_TIMEOUT must be positive")
        if self.MAPBOX_PUBLIC_TOKEN and not self.MAPBOX_PUBLIC_TOKEN.startswith("pk."):
            errors.append("MAPBOX_PUBLIC_TOKEN appears invalid")
        return errors


# Global config instance used throughout the application
config = Config()

# Default environment variables for development
DEFAULT_ENV_VARS = {
    "BACKEND_URL": "http://backend:8000",
    "API_TIMEOUT": "10",
    "DEVELOPMENT_MODE": "true",
    "USE_MOCK_API": "false",
    "CACHE_TTL": "300",
    "LOG_LEVEL": "INFO",
}


def load_env_file(filename: str = ".env") -> None:
    """Load environment variables from a file in KEY=VALUE format."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value


def create_env_template(filename: str = ".env.example") -> None:
    """Create a template .env file with example settings."""
    with open(filename, "w") as f:
        f.write("# Safe Air frontend configuration\n\n")
        f.write("# URL of the backend API\n")
        f.write("BACKEND_URL=http://backend:8000\n\n")
        f.write("# Timeout for API requests (seconds)\n")
        f.write("API_TIMEOUT=10\n\n")
        f.write("# Development mode\n")
        f.write("DEVELOPMENT_MODE=true\n\n")
        f.write("# Use mock API data (for testing)\n")
        f.write("USE_MOCK_API=false\n\n")
        f.write("# Public Mapbox token (optional)\n")
        f.write("# MAPBOX_PUBLIC_TOKEN=pk.your_public_token_here\n\n")
        f.write("# TTL for the in‑memory cache (seconds)\n")
        f.write("CACHE_TTL=300\n\n")
        f.write("# Logging level\n")
        f.write("LOG_LEVEL=INFO\n")
