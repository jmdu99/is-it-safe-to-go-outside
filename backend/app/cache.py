"""Cache configuration for the backend.

This module configures the default cache used by the application via
``aiocache``. It reads configuration values from :mod:`app.config` and
registers a Redis backend. A JSON serializer is used by default. A log
message is emitted after configuration for observability.
"""

from __future__ import annotations

from aiocache import caches
from aiocache.serializers import JsonSerializer

from .config import settings, logger


# Configure the default cache backend. This uses environment variables set
# through the Settings object. See the ``Settings`` class in
# :mod:`app.config` for details on each field.
# Decide which cache backend to use. If a cache host is provided, configure
# a Redis cache. Otherwise fall back to an in‑memory cache for development
# and testing environments where Redis may not be available.

if settings.cache_host:
    caches.set_config(
        {
            "default": {
                "cache": "aiocache.RedisCache",
                "endpoint": settings.cache_host,
                "port": settings.cache_port,
                "password": settings.cache_password,
                "ttl": settings.cache_ttl_seconds,
                "serializer": {"class": JsonSerializer},
            }
        }
    )
    logger.info(
        "Configured Redis cache at %s:%s (ttl=%s)",
        settings.cache_host,
        settings.cache_port,
        settings.cache_ttl_seconds,
    )
else:
    caches.set_config(
        {
            "default": {
                "cache": "aiocache.SimpleMemoryCache",
                "serializer": {"class": JsonSerializer},
            }
        }
    )
    logger.info("Configured in‑memory cache (Redis disabled)")
