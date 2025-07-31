"""Service for retrieving current weather conditions.

This module wraps the OpenWeatherMap API to fetch current weather data. It
includes caching, retry logic with exponential backoff, optional profiling
and a stubbed fallback when the API key is not configured. The returned
data is normalized into a :class:`WeatherResponse` model defined in
:mod:`app.models`.
"""

from __future__ import annotations

import httpx
from aiocache import cached
from datetime import datetime, timezone
from typing import Any, cast

from ..config import settings, logger
from ..models import WeatherResponse
from ..utils import async_retry, profile_if_enabled, get_http_client


@cached()
@async_retry(max_attempts=3)
@profile_if_enabled
async def fetch_current_weather(lat: float, lon: float) -> WeatherResponse:
    """Fetch the current weather for a given latitude and longitude.

    When the OpenWeather API key is missing, a stubbed weather response is
    returned with placeholder values. The function automatically retries on
    transient network failures using an exponential backoff strategy and
    writes profiling information when enabled via ``ENABLE_PROFILING``.

    Parameters
    ----------
    lat:
        Latitude in decimal degrees.
    lon:
        Longitude in decimal degrees.

    Returns
    -------
    WeatherResponse
        A normalized view of the current weather conditions.
    """
    if not settings.openweather_key:
        logger.warning(
            "OpenWeather API key missing; returning stubbed weather for (%s, %s)",
            lat,
            lon,
        )
        # Provide a deterministic stubbed weather response
        return WeatherResponse(
            timestamp=datetime.now(timezone.utc).isoformat(),
            temp_celsius=20.0,
            humidity=50,
            wind_speed=5.0,
            raw={},
        )

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.openweather_key,
        "units": "metric",
    }
    client = get_http_client()
    r = await client.get(url, params=params)
    r.raise_for_status()
    d = cast(dict[str, object], r.json())
    return WeatherResponse(
        timestamp=datetime.fromtimestamp(
            cast(int, d["dt"]), tz=timezone.utc
        ).isoformat(),
        temp_celsius=float(cast(dict[str, Any], d["main"])["temp"]),
        humidity=int(cast(dict[str, Any], d["main"])["humidity"]),
        wind_speed=float(cast(dict[str, Any], d["wind"])["speed"]),
        raw=d,
    )
