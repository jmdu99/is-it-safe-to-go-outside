import httpx
from aiocache import cached
from datetime import datetime, timezone
from ..config import settings
from ..models import PollutionResponse

@cached()
async def fetch_air_pollution(lat: float, lon: float) -> PollutionResponse:
    """
    Fetches air pollution data:
      - pm2_5, pm10, o3, no2, so2, co concentrations in µg/m³
    """
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": settings.openweather_key}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        entry = r.json()["list"][0]
    return PollutionResponse(
        timestamp=datetime.fromtimestamp(entry["dt"], tz=timezone.utc).isoformat(),
        components=entry["components"],
        raw=entry
    )
