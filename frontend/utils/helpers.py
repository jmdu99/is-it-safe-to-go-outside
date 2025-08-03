"""
Utility functions for the Safe Air application.

This module centralises common helpers used throughout the Streamlit frontend.
It manages session state initialisation, formatting of timestamps and
coordinates, simple debouncing to avoid flooding the backend API, a basic
in‑memory cache stored in the Streamlit session, and some general
utility functions such as distance calculation and string sanitation.

All docstrings, comments and user‑facing messages are written in English.
"""

from __future__ import annotations

import streamlit as st
import uuid
import time
import math
import json
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional

from utils.constants import RISK_COLORS, DATE_FORMATS, COMPONENT_WEIGHTS


def init_session_state() -> None:
    """Initialise the Streamlit session state.

    This function ensures that keys used throughout the application exist in
    the session state. It is idempotent and can be called multiple times
    without overwriting existing values.
    """
    # Unique token for Mapbox API sessions
    if "session_token" not in st.session_state:
        st.session_state.session_token = str(uuid.uuid4())

    # Selected location information
    st.session_state.setdefault("selected_location", None)
    st.session_state.setdefault("current_risk_data", None)

    # Suggestions state for the search component
    st.session_state.setdefault("suggestions", [])
    st.session_state.setdefault("selected_suggestion", None)
    st.session_state.setdefault("last_search", "")
    st.session_state.setdefault("last_search_time", 0.0)

    # In‑memory cache for API responses
    st.session_state.setdefault("cache", {})
    # Debug toggle
    st.session_state.setdefault("show_debug", False)


def get_risk_color(risk_label: str) -> str:
    """Return the colour hex code corresponding to a risk label.

    Parameters
    ----------
    risk_label : str
        One of ``'LOW'``, ``'MODERATE'`` or ``'HIGH'`` (case insensitive).

    Returns
    -------
    str
        A CSS colour string. Defaults to a neutral grey if the label is unrecognised.
    """
    return RISK_COLORS.get(risk_label.upper(), "#6c757d")  # Grey by default


def format_timestamp(timestamp_str: str) -> str:
    """Format an ISO‑8601 timestamp into a human‑readable string in the
    Europe/Madrid timezone.

    The backend returns timestamps in ISO format with a UTC offset. To align
    with the user's local time (CEST/CET), the timestamp is parsed and
    converted using the zoneinfo database.

    Parameters
    ----------
    timestamp_str : str
        A timestamp string returned by the backend.

    Returns
    -------
    str
        A formatted timestamp (``dd/mm/YYYY HH:MM``) in the Europe/Madrid timezone.
    """
    try:
        # Replace trailing 'Z' (UTC designator) with '+00:00' to satisfy fromisoformat
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        dt_local = dt.astimezone(ZoneInfo("Europe/Madrid"))
        return dt_local.strftime(DATE_FORMATS["display"])
    except Exception:
        # Fallback: return the original string if parsing fails
        return timestamp_str


def format_coordinates(lat: float, lon: float, precision: int = 6) -> str:
    """Return a formatted latitude/longitude string with a fixed precision."""
    return f"{lat:.{precision}f}, {lon:.{precision}f}"


def debounce(func, delay: float = 1.0):
    """Decorator to debounce a function call.

    When applied, the decorated function will only run if it hasn't been
    called within the specified delay. This is useful for reducing the
    frequency of API calls during typing.
    """

    def wrapper(*args, **kwargs):
        current_time = time.time()
        cache_key = f"debounce_{func.__name__}_{hash(str(args) + str(kwargs))}"
        last_call = st.session_state.get(f"{cache_key}_time", 0)
        if current_time - last_call >= delay:
            st.session_state[f"{cache_key}_time"] = current_time
            return func(*args, **kwargs)
        return None

    return wrapper


# Simple in‑session cache helpers
def cache_get(key: str) -> Optional[Any]:
    """Retrieve a value from the session cache if not expired."""
    entry = st.session_state.cache.get(key)
    if entry is None:
        return None
    if time.time() > entry["expires"]:
        del st.session_state.cache[key]
        return None
    return entry["value"]


def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """Store a value in the session cache with a TTL in seconds."""
    st.session_state.cache[key] = {"value": value, "expires": time.time() + ttl}


def clear_cache(pattern: Optional[str] = None) -> None:
    """Clear the entire cache or only entries containing a substring pattern."""
    if pattern is None:
        st.session_state.cache.clear()
    else:
        keys = [k for k in st.session_state.cache.keys() if pattern in k]
        for k in keys:
            del st.session_state.cache[k]


def calculate_cache_stats() -> Dict[str, Any]:
    """Return statistics about the current cache usage."""
    cache = st.session_state.cache
    now = time.time()
    total = len(cache)
    expired = sum(1 for entry in cache.values() if now > entry["expires"])
    active = total - expired
    hits = getattr(st.session_state, "cache_hits", 0)
    requests = max(getattr(st.session_state, "cache_requests", 1), 1)
    return {
        "total": total,
        "active": active,
        "expired": expired,
        "hit_rate": hits / requests,
    }


def validate_coordinates(lat: float, lon: float) -> bool:
    """Return True if the provided coordinates fall within valid ranges."""
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute the great‑circle distance between two points on the Earth (in km)."""
    # Earth radius in kilometres
    R = 6371.0
    lat1_rad, lon1_rad = map(math.radians, (lat1, lon1))
    lat2_rad, lon2_rad = map(math.radians, (lat2, lon2))
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def format_distance(distance_km: float) -> str:
    """Return a user‑friendly distance string.

    Distances under 1 km are shown in metres; distances under 10 km with one decimal
    place; longer distances are rounded to whole kilometres.
    """
    if distance_km < 1.0:
        return f"{distance_km * 1000:.0f} m"
    elif distance_km < 10.0:
        return f"{distance_km:.1f} km"
    else:
        return f"{distance_km:.0f} km"


def generate_google_maps_url(lat: float, lon: float, zoom: int = 15) -> str:
    """Generate a Google Maps URL centred on the given coordinates."""
    return f"https://www.google.com/maps/@{lat},{lon},{zoom}z"


def sanitize_filename(filename: str) -> str:
    """Remove characters that are invalid in file names."""
    import re

    return re.sub(r'[<>:"/\\|?*]', "_", filename)


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate a string to a maximum length with a suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def format_number(number: float, precision: int = 2, unit: str = "") -> str:
    """Format a number with a specified precision and optional unit.

    If the absolute value exceeds 1000 it will be abbreviated with a 'k'.
    """
    if abs(number) >= 1000:
        return f"{number/1000:.{precision}f}k{unit}"
    return f"{number:.{precision}f}{unit}"


def create_download_link(
    data: Any, filename: str, mime_type: str = "application/json"
) -> str:
    """Create a data download link for JSON or arbitrary text data."""
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, indent=2)
    else:
        data_str = str(data)
    b64 = base64.b64encode(data_str.encode()).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{sanitize_filename(filename)}">📥 Download {filename}</a>'


def display_debug_info() -> None:
    """Display debug information when the debug flag is enabled."""
    if st.session_state.get("show_debug", False):
        with st.expander("🐛 Debug information"):
            st.subheader("Session state")
            session_info = {
                "session_token": st.session_state.session_token[:8] + "...",
                "has_selected_location": bool(st.session_state.selected_location),
                "has_current_risk_data": bool(st.session_state.current_risk_data),
                "suggestions_count": len(st.session_state.suggestions),
            }
            st.json(session_info)
            st.subheader("Cache")
            cache_stats = calculate_cache_stats()
            cols = st.columns(4)
            cols[0].metric("Total", cache_stats["total"])
            cols[1].metric("Active", cache_stats["active"])
            cols[2].metric("Expired", cache_stats["expired"])
            cols[3].metric("Hit rate", f"{cache_stats['hit_rate']:.2%}")
            st.subheader("Actions")
            a, b, c = st.columns(3)
            if a.button("🗑️ Clear cache"):
                clear_cache()
                st.success("Cache cleared")
            if b.button("🔄 New token"):
                st.session_state.session_token = str(uuid.uuid4())
                st.success("New token generated")
            if c.button("🔄 Reset session"):
                for key in list(st.session_state.keys()):
                    if key != "show_debug":
                        del st.session_state[key]
                init_session_state()
                st.success("Session reset")


def handle_error(error: Exception, context: str = "") -> None:
    """Centralised error handler for unexpected exceptions."""
    error_msg = f"Error {context}: {str(error)}"
    # Log to console for debugging
    print(f"ERROR: {error_msg}")
    # Display user‑friendly messages
    msg_lower = str(error).lower()
    if "timeout" in msg_lower:
        st.error("⏱️ Timeout exceeded. Please try again.")
    elif "connection" in msg_lower:
        st.error("🔌 Connection error. Ensure the backend is running.")
    else:
        st.error(f"❌ {error_msg}")
    # Show full exception if debug is enabled
    if st.session_state.get("show_debug", False):
        st.exception(error)


def show_loading_spinner(message: str = "Loading..."):
    """Return a context manager for displaying a loading spinner."""
    return st.spinner(message)


def create_metric_card(
    title: str, value: str, delta: Optional[str] = None, help_text: Optional[str] = None
) -> None:
    """Helper to create a metric card with consistent styling."""
    st.metric(label=title, value=value, delta=delta, help=help_text)


def export_data_to_csv(data: List[Dict], filename: Optional[str] = None) -> str:
    """Convert a list of dictionaries into a CSV string.

    A default filename is generated using the current date/time if one is not
    provided.
    """
    import pandas as pd
    import io

    if filename is None:
        filename = f"export_{datetime.now().strftime(DATE_FORMATS['filename'])}.csv"
    df = pd.DataFrame(data)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()


def calculate_weighted_contributions(
    norm_data: Dict[str, float], weights: Dict[str, float] = COMPONENT_WEIGHTS
) -> Dict[str, float]:
    """Calculate the weighted contribution of each normalised factor.

    Each factor value is multiplied by its weight and the result is normalised
    so that the sum of all contributions equals 1.0. If the total weight
    contribution is zero, each factor returns zero.
    """
    contributions = {
        k: norm_data.get(k, 0.0) * weights.get(k, 0.0) for k in weights.keys()
    }
    total = sum(contributions.values())
    if total == 0:
        return {k: 0.0 for k in contributions.keys()}
    return {k: v / total for k, v in contributions.items()}


# ---------------------------------------------------------------------------
# Numeric formatting helpers
def truncate(value: float, decimals: int = 2) -> float:
    """Truncate a floating‑point number to a fixed number of decimal places.

    This function does not perform rounding; it simply removes digits beyond
    the specified precision. For example, ``truncate(3.4567, 2)`` returns
    ``3.45``.  Negative values are also handled correctly.

    Parameters
    ----------
    value : float
        The number to truncate.
    decimals : int, optional
        The number of decimal places to preserve. Default is 2.

    Returns
    -------
    float
        The truncated number.
    """
    if decimals < 0:
        raise ValueError("decimals must be non‑negative")
    factor = 10**decimals
    # Use int() for truncation toward zero
    return int(value * factor) / factor


def get_status_label_color(norm_value: float) -> Tuple[str, str]:
    """Return a label (Optimal/Precaution/Risk) and colour for a normalised value.

    Parameters
    ----------
    norm_value : float
        A normalised value between 0 and 1.

    Returns
    -------
    Tuple[str, str]
        A tuple ``(label, colour)`` where ``label`` is one of ``'Optimal'``,
        ``'Precaution'`` or ``'Risk'``, and ``colour`` is ``'green'``,
        ``'yellow'`` or ``'red'`` respectively.
    """
    # Boundaries at 0.21 and 0.41: values below 0.21 are green, values below
    # 0.41 are yellow, and values 0.41 or above are red.  Decimals such as
    # 0.201 or 0.401 are considered part of the lower category.
    if norm_value < 0.21:
        return ("Optimal", "green")
    elif norm_value < 0.41:
        return ("Precaution", "yellow")
    else:
        return ("Risk", "red")
