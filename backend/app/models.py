from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class SuggestResult(BaseModel):
    id: str
    name: Optional[str]
    full_address: Optional[str]
    place_formatted: Optional[str]

class RetrieveResult(BaseModel):
    id: str
    name: Optional[str]
    full_address: Optional[str]
    place_formatted: Optional[str]
    center: List[float]

class WeatherResponse(BaseModel):
    timestamp: str
    temp_celsius: float
    humidity: int
    wind_speed: float
    raw: Dict[str, Any]

class PollutionResponse(BaseModel):
    timestamp: str
    components: Dict[str, float]
    raw: Dict[str, Any]

class Coordinate(BaseModel):
    latitude: float
    longitude: float

class RiskResponse(BaseModel):
    location: Coordinate
    risk_index: float
    risk_label: str
    weather: WeatherResponse
    pollution: PollutionResponse
    norm: Dict[str, float]
