"""Pydantic models used by the respiratory risk API.

These models define the shapes of the request and response payloads used by
the various endpoints. Pydantic's type annotations enable static type
checking and validation of the data returned by external services.
"""

from __future__ import annotations

from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class SuggestResult(BaseModel):
    """Represents a single suggestion result from the Mapbox Search API."""

    id: str
    name: Optional[str]
    full_address: Optional[str]
    place_formatted: Optional[str]


class RetrieveResult(BaseModel):
    """Represents a detailed place record returned by the Mapbox retrieve endpoint."""

    id: str
    name: Optional[str]
    full_address: Optional[str]
    place_formatted: Optional[str]
    center: List[float]


class WeatherResponse(BaseModel):
    """Normalized view of current weather conditions."""

    timestamp: str
    temp_celsius: float
    humidity: int
    wind_speed: float
    raw: Dict[str, Any]


class PollutionResponse(BaseModel):
    """Normalized view of air pollution data."""

    timestamp: str
    components: Dict[str, float]
    raw: Dict[str, Any]


class Coordinate(BaseModel):
    """Geographic coordinate in decimal degrees."""

    latitude: float
    longitude: float


class RiskResponse(BaseModel):
    """Aggregate risk response combining weather, pollution and computed risk."""

    location: Coordinate
    risk_index: float
    risk_label: str
    weather: WeatherResponse
    pollution: PollutionResponse
    norm: Dict[str, float]
