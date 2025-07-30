"""
Expose service functions from the services package.

Importing from this module provides a convenient facade for the individual
service functions without requiring callers to know about the underlying
modules. For example, ``from app.services import suggest`` works.
"""

from .mapbox_service import suggest, retrieve
from .weather_service import fetch_current_weather
from .pollution_service import fetch_air_pollution
from .risk_service import compute_risk

__all__ = [
    "suggest",
    "retrieve",
    "fetch_current_weather",
    "fetch_air_pollution",
    "compute_risk",
]
