"""Service for retrieving current air pollution data (patched).

This module wraps the OpenWeatherMap air pollution API.  It includes
exponential backoff retry logic, optional profiling, a stubbed fallback
when no API key is configured and, importantly, an explicit TTL on the
cache decorator to ensure that air pollution data is refreshed after the
configured timeout.  Without specifying ``ttl``, ``aiocache`` would cache
responses indefinitely, causing outdated data to persist beyond the 1‑hour
window described in the documentation.  By using ``settings.cache_ttl_seconds``
we respect the intended caching duration.
"""

from __future__ import annotations

import httpx
from aiocache import cached
from datetime import datetime, timezone
from typing import Any, cast

from ..config import settings, logger
from ..models import PollutionResponse
from ..utils import async_retry, profile_if_enabled, get_http_client


@cached(ttl=settings.cache_ttl_seconds)
@async_retry(max_attempts=3)
@profile_if_enabled
async def fetch_air_pollution(lat: float, lon: float) -> PollutionResponse:
    """Fetch current air pollution metrics for a location.

    When the OpenWeather API key is missing, a deterministic stubbed
    pollution response is returned.  The function automatically retries on
    transient errors using exponential backoff and emits profiling data
    when enabled via the ``ENABLE_PROFILING`` environment variable.

    Parameters
    ----------
    lat:
        Latitude in decimal degrees.
    lon:
        Longitude in decimal degrees.

    Returns
    -------
    PollutionResponse
        A normalized view of the air pollution measurements.
    """
    if not settings.openweather_key:
        logger.warning(
            "OpenWeather API key missing; returning stubbed pollution for (%s, %s)",
            lat,
            lon,
        )
        # Provide a deterministic stubbed pollution response
        components: dict[str, float] = {
            "pm2_5": 10.0,
            "pm10": 20.0,
            "o3": 30.0,
            "no2": 5.0,
            "so2": 2.0,
            "co": 0.5,
        }
        return PollutionResponse(
            timestamp=datetime.now(timezone.utc).isoformat(),
            components=components,
            raw={"components": components},
        )

    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.openweather_key,
    }
    client = get_http_client()
    r = await client.get(url, params=params)
    r.raise_for_status()
    data = cast(dict[str, Any], r.json())
    entry = data["list"][0]
    return PollutionResponse(
        timestamp=datetime.fromtimestamp(
            cast(int, entry["dt"]), tz=timezone.utc
        ).isoformat(),
        components=cast(dict[str, float], entry["components"]),
        raw=entry,
    )