from ..models import WeatherResponse, PollutionResponse

# Thresholds for normalization are in the following units:
#   pm2_5, pm10, o3, no2, so2: µg/m³
#   co: µg/m³
#   temp: °C
#   hum: % relative humidity
#   wind: m/s

WEIGHTS = {
    "pm2_5": 0.25,
    "o3":    0.20,
    "pm10":  0.10,
    "no2":   0.10,
    "co":    0.05,
    "so2":   0.05,
    "temp":  0.15,
    "hum":   0.05,
    "wind":  0.05,
}

def norm_temp(t: float) -> float:
    if t < 15:
        return min((15 - t) / 15, 1.0)
    if t > 25:
        return min((t - 25) / 15, 1.0)
    return 0.0

def norm_hum(h: float) -> float:
    if h < 30:
        return min((30 - h) / 30, 1.0)
    if h > 50:
        return min((h - 50) / 50, 1.0)
    return 0.0

def norm_wind(v: float) -> float:
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

def compute_risk(
    weather: WeatherResponse,
    pollution: PollutionResponse
) -> tuple[float, dict[str, float]]:

    comp = pollution.components
    w = weather

    normed = {
        "pm2_5": norm_pm2_5(comp.get("pm2_5", 0.0)),
        "o3":    norm_o3(comp.get("o3", 0.0)),
        "pm10":  norm_pm10(comp.get("pm10", 0.0)),
        "no2":   norm_no2(comp.get("no2", 0.0)),
        "co":    norm_co(comp.get("co", 0.0)),
        "so2":   norm_so2(comp.get("so2", 0.0)),
        "temp":  norm_temp(w.temp_celsius),
        "hum":   norm_hum(w.humidity),
        "wind":  norm_wind(w.wind_speed),
    }

    idx = sum(normed[k] * WEIGHTS[k] for k in WEIGHTS)
    idx = max(0.0, min(1.0, idx))
    return idx, normed

# Final index range: 0.00–1.00
# Label: 0.00–0.25=Low, 0.26–0.50=Moderate, 0.51–1.00=High
