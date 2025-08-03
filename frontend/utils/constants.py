"""
Application constants.

This module defines colour palettes, pollutant thresholds, meteorological thresholds,
component weights aligned with the backend risk algorithm, descriptive information
for pollutants and weather factors, risk level descriptions and recommendations,
and various other configuration values used throughout the frontend.

All descriptions are provided in English.
"""

# Colour mapping for risk levels
RISK_COLORS = {
    "LOW": "#28a745",  # Green
    "MODERATE": "#ffc107",  # Yellow/Orange
    "HIGH": "#dc3545",  # Red
}

# Component weights matching the backend risk algorithm (sum to 1.0)
COMPONENT_WEIGHTS = {
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

# Default coordinates for fallback locations (latitude, longitude)
DEFAULT_COORDINATES = {
    "PARIS": [48.8566, 2.3522],
    "LYON": [45.7640, 4.8357],
    "MARSEILLE": [43.2965, 5.3698],
    "LONDON": [51.5074, -0.1278],
    "NEW_YORK": [40.7128, -74.0060],
}

# Air pollutant concentration thresholds (µg/m³) based on WHO guidelines
POLLUTION_THRESHOLDS = {
    "pm2_5": 25,
    "pm10": 50,
    "o3": 100,
    "no2": 200,
    "so2": 40,
    "co": 10000,
}

# Optimal ranges for weather variables
WEATHER_THRESHOLDS = {
    "temp_min": 15,  # Minimum comfortable temperature (°C)
    "temp_max": 25,  # Maximum comfortable temperature (°C)
    "humidity_min": 30,  # Minimum comfortable humidity (%)
    "humidity_max": 50,  # Maximum comfortable humidity (%) – aligned with backend
    "wind_optimal": 3,  # Optimal wind speed (m/s)
}

# Detailed information for each pollutant
POLLUTION_INFO = {
    "pm2_5": {
        "name": "PM2.5 Fine Particles",
        "description": "Particles with a diameter less than 2.5 micrometres. These penetrate deep into the lungs and are the most dangerous for respiratory health.",
        "threshold": 25,
        "sources": "Traffic emissions, industrial combustion, wood burning",
    },
    "pm10": {
        "name": "PM10 Particulate Matter",
        "description": "Particles with a diameter less than 10 micrometres. They irritate the upper respiratory tract.",
        "threshold": 50,
        "sources": "Tyre wear, construction work, soil erosion, pollen",
    },
    "o3": {
        "name": "Ozone (O₃)",
        "description": "A secondary pollutant formed via photochemical reactions. It is highly irritating to the respiratory system.",
        "threshold": 100,
        "sources": "Reaction between NOx and VOCs under sunlight",
    },
    "no2": {
        "name": "Nitrogen Dioxide (NO₂)",
        "description": "An irritating gas mainly emitted by diesel vehicles and combustion installations.",
        "threshold": 200,
        "sources": "Road traffic, thermal power stations, heating",
    },
    "so2": {
        "name": "Sulphur Dioxide (SO₂)",
        "description": "An irritating gas emitted primarily by the combustion of sulphur‑containing fossil fuels.",
        "threshold": 40,
        "sources": "Industry, oil‑fired heating, maritime transport",
    },
    "co": {
        "name": "Carbon Monoxide (CO)",
        "description": "An odourless, colourless gas resulting from incomplete combustion. It prevents oxygen binding to haemoglobin.",
        "threshold": 10000,
        "sources": "Vehicles, faulty heating systems, industry",
    },
}

# Descriptions for weather factors
WEATHER_INFO = {
    "temperature": {
        "name": "Air Temperature",
        "description": "Influences the formation and concentration of pollutants. Extreme temperatures affect the respiratory system.",
        "optimal_range": "15–25 °C",
    },
    "humidity": {
        "name": "Relative Humidity",
        "description": "Air that is too dry irritates the mucous membranes; air that is too humid promotes moulds and allergens.",
        "optimal_range": "30–50 %",
    },
    "wind_speed": {
        "name": "Wind Speed",
        "description": "Wind disperses pollutants. Weak wind favours accumulation; strong wind can resuspend particles.",
        "optimal_range": "2–6 m/s",
    },
}

# Risk level descriptions and recommendations
RISK_INFO = {
    "LOW": {
        "description": "Conditions are favourable for outdoor activities. Air quality is good and weather conditions are comfortable.",
        "recommendations": "• Enjoy outdoor activities\n• No particular precautions necessary\n• Ideal for outdoor sports",
    },
    "MODERATE": {
        "description": "Conditions are generally acceptable, but particularly sensitive people may feel minor discomfort.",
        "recommendations": "• Outdoor activities are possible\n• Take precautions if you are sensitive (asthma, allergies)\n• Reduce prolonged exposure\n• Avoid intense exertion",
    },
    "HIGH": {
        "description": "Conditions are unfavourable for prolonged outdoor activities. Respiratory irritation is possible for everyone.",
        "recommendations": "• Limit prolonged outings\n• Wear a mask if necessary\n• Avoid outdoor sports\n• Prefer indoor spaces\n• Consult a doctor if you experience respiratory discomfort",
    },
}

# Chart colour palette (unused at the moment but kept for consistency)
CHART_COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "warning": "#d62728",
    "info": "#9467bd",
}

# Standard error messages
ERROR_MESSAGES = {
    "no_data": "❌ No data available",
    "api_error": "❌ Error communicating with the server",
    "timeout": "⏱️ Timeout exceeded",
    "connection_error": "🔌 Unable to connect to the server",
    "invalid_location": "📍 Location not found or invalid",
    "rate_limit": "⚡ Too many requests, please wait",
}

# Success messages
SUCCESS_MESSAGES = {
    "data_loaded": "✅ Data loaded successfully",
    "location_found": "📍 Location found",
    "cache_hit": "⚡ Data retrieved from cache",
}

# Cache configuration keys and time‑to‑live values
CACHE_KEYS = {
    "suggestions": "suggestions_{query}_{token}",
    "location_details": "location_{mapbox_id}_{token}",
    "risk_data": "risk_{location_hash}_{timestamp}",
}

LIMITS = {
    "max_suggestions": 10,
    "min_query_length": 2,
    "max_query_length": 100,
    "debounce_delay": 1.0,  # seconds
    "cache_ttl": 300,  # seconds
}

EXTERNAL_URLS = {
    "mapbox_docs": "https://docs.mapbox.com/api/search/",
    "openweather_docs": "https://openweathermap.org/api/air-pollution",
    "who_air_quality": "https://www.who.int/health-topics/air-pollution",
    "google_maps": "https://www.google.com/maps/@{lat},{lon},15z",
}

DATE_FORMATS = {
    "display": "%d/%m/%Y %H:%M",
    "api": "%Y-%m-%dT%H:%M:%S%z",
    "filename": "%Y%m%d_%H%M%S",
}
