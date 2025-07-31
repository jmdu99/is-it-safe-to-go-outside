"""Risk computation based on weather and pollution metrics.

This module defines a set of normalization functions and a weighted risk
computation. Each function is type annotated for static analysis. The
``compute_risk`` function may be profiled when the ``ENABLE_PROFILING``
environment variable is set and logs intermediate values for debugging.
"""

from __future__ import annotations

from typing import Dict, Tuple

from ..config import logger
from ..models import WeatherResponse, PollutionResponse
from ..utils import profile_if_enabled


# Threshold weights for the final risk index. The values should sum to 1.0.
WEIGHTS: Dict[str, float] = {
    "pm2_5": 0.25,
    "o3": 0.20,
    "pm10": 0.10,
    "no2": 0.10,
    "co": 0.05,
    "so2": 0.05,
    "temp": 0.15,
    "hum": 0.05,
    "wind": 0.05,
}


def norm_temp(t: float) -> float:
    """Normalize the temperature contribution.

    Temperatures between 15°C and 25°C are considered ideal (risk 0). Values
    outside this range linearly increase risk, capped at 1.
    """
    if t < 15:
        return min((15 - t) / 15, 1.0)
    if t > 25:
        return min((t - 25) / 15, 1.0)
    return 0.0


def norm_hum(h: float) -> float:
    """Normalize the relative humidity contribution."""
    if h < 30:
        return min((30 - h) / 30, 1.0)
    if h > 50:
        return min((h - 50) / 50, 1.0)
    return 0.0


def norm_wind(v: float) -> float:
    """Normalize the wind speed contribution."""
    return min(max((10 - v) / 10, 0.0), 1.0)


def norm_pm2_5(c: float) -> float:
    return min(c / 25, 1.0)


def norm_pm10(c: float) -> float:
    return min(c / 50, 1.0)


def norm_o3(c: float) -> float:
    return min(c / 100, 1.0)


def norm_no2(c: float) -> float:
    return min(c / 200, 1.0)


def norm_co(c: float) -> float:
    return min(c / 10000, 1.0)


def norm_so2(c: float) -> float:
    return min(c / 40, 1.0)


@profile_if_enabled
def compute_risk(
    weather: WeatherResponse, pollution: PollutionResponse
) -> Tuple[float, Dict[str, float]]:
    """Compute the respiratory risk index from weather and pollution data.

    The final index is a weighted sum of normalized pollutant and weather
    components. The index is constrained to the range [0.0, 1.0]. A
    dictionary of the normalized components is also returned for display
    purposes. Intermediate values are logged for observability.

    Parameters
    ----------
    weather:
        The normalized current weather reading.
    pollution:
        The normalized current pollution reading.

    Returns
    -------
    tuple[float, dict[str, float]]
        A tuple containing the final risk index and a mapping of the
        normalized component values.
    """
    comp = pollution.components
    w = weather
    normed: Dict[str, float] = {
        "pm2_5": norm_pm2_5(comp.get("pm2_5", 0.0)),
        "o3": norm_o3(comp.get("o3", 0.0)),
        "pm10": norm_pm10(comp.get("pm10", 0.0)),
        "no2": norm_no2(comp.get("no2", 0.0)),
        "co": norm_co(comp.get("co", 0.0)),
        "so2": norm_so2(comp.get("so2", 0.0)),
        "temp": norm_temp(w.temp_celsius),
        "hum": norm_hum(w.humidity),
        "wind": norm_wind(w.wind_speed),
    }
    # Log normalized values for debugging
    logger.debug("Normalized components: %s", normed)
    idx: float = sum(normed[k] * WEIGHTS[k] for k in WEIGHTS)
    # Constrain index to 0–1
    idx = max(0.0, min(1.0, idx))
    logger.debug("Computed risk index: %s", idx)
    return idx, normed
