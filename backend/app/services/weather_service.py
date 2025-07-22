import httpx
from aiocache import cached
from datetime import datetime, timezone
from ..config import settings
from ..models import WeatherResponse

@cached()
async def fetch_current_weather(lat: float, lon: float) -> WeatherResponse:
    """
    Fetches current weather:
      - temperature in °C
      - humidity in %
      - wind speed in m/s
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": settings.openweather_key, "units": "metric"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        d = r.json()
    return WeatherResponse(
        timestamp=datetime.fromtimestamp(d["dt"], tz=timezone.utc).isoformat(),
        temp_celsius=d["main"]["temp"],
        humidity=d["main"]["humidity"],
        wind_speed=d["wind"]["speed"],
        raw=d
    )
