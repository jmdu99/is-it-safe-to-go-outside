"""
API client used by the Safe Air frontend to communicate with the backend service.

This client encapsulates HTTP requests to fetch location suggestions and risk
data. It handles timeouts and connection errors gracefully by presenting
user‑friendly messages via Streamlit. A mock implementation is provided for
testing and development without a running backend.
"""

from __future__ import annotations

import streamlit as st
import requests
import uuid
from typing import List, Dict, Optional

from utils.config import config  # use the global config instance


class APIClient:
    """Client to interact with the backend API."""
    def __init__(self) -> None:
        self.base_url = config.BACKEND_URL
        self.timeout = config.API_TIMEOUT

    def suggest_locations(self, query: str, session_token: str) -> List[Dict]:
        """Return a list of location suggestions from the backend."""
        try:
            url = f"{self.base_url}/suggest"
            params = {"q": query, "session_token": session_token}
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout – the server took too long to respond")
            return []
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection error – please ensure the backend is running")
            return []
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ HTTP error {e.response.status_code}: {e.response.text}")
            return []
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return []

    def retrieve_location(self, mapbox_id: str, session_token: str) -> Optional[Dict]:
        """Retrieve detailed information about a location using its Mapbox ID."""
        try:
            url = f"{self.base_url}/retrieve/{mapbox_id}"
            params = {"session_token": session_token}
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout while retrieving place details")
            return None
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection error – could not reach the backend")
            return None
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ Retrieval error {e.response.status_code}")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return None

    def get_risk_data(self, query: str | None = None, mapbox_id: str | None = None, session_token: str | None = None) -> Optional[Dict]:
        """Retrieve risk data based on a query string or a Mapbox ID."""
        # Always generate a fresh session token for risk requests to avoid
        # hitting stale backend cache entries.  We keep the existing
        # session_token for suggestion and retrieval requests, but here we
        # deliberately ignore it so that each call is unique.  This helps
        # ensure OpenWeather data is refreshed when the backend cache TTL
        # expires.
        fresh_token = str(uuid.uuid4())
        params: Dict[str, str] = {}
        if mapbox_id:
            params["mapbox_id"] = mapbox_id
            params["session_token"] = fresh_token
        elif query:
            params["query"] = query
            params["session_token"] = fresh_token
        else:
            st.error("❌ Either a query or a mapbox_id must be provided")
            return None
        try:
            url = f"{self.base_url}/risk"
            # Include a timestamp parameter to bypass stale caching on the backend.
            # Use an hourly granularity to respect the OpenWeather cache TTL of 3600 seconds.
            import time as _time
            params["timestamp"] = int(_time.time() // 3600)
            with st.spinner("🔄 Retrieving weather and pollution data..."):
                response = requests.get(url, params=params, timeout=self.timeout * 2)
                response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout while retrieving risk data")
            return None
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to the backend")
            return None
        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json().get('detail', str(e))
            except Exception:
                error_detail = str(e)
            st.error(f"❌ API error: {error_detail}")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return None

    def health_check(self) -> bool:
        """Check whether the backend is reachable."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code < 500
        except Exception:
            return False

    def get_api_status(self) -> Dict[str, str]:
        """Return a dictionary describing the health of the backend and its dependencies."""
        status = {
            "backend": "🔴 Offline",
            "mapbox": "❓ Unknown",
            "openweather": "❓ Unknown"
        }
        if self.health_check():
            status["backend"] = "🟢 Online"
            try:
                test_data = self.get_risk_data(query="Paris", session_token=str(uuid.uuid4()))
                if test_data:
                    status["mapbox"] = "🟢 Operational"
                    status["openweather"] = "🟢 Operational"
                else:
                    status["mapbox"] = "🟡 Potential issue"
                    status["openweather"] = "🟡 Potential issue"
            except Exception:
                status["mapbox"] = "🔴 Error"
                status["openweather"] = "🔴 Error"
        return status


class MockAPIClient(APIClient):
    """Mock implementation of the API client used for development/testing."""
    def suggest_locations(self, query: str, session_token: str) -> List[Dict]:
        import time as _time
        _time.sleep(0.5)
        mock_suggestions = [
            {"id": "mock_paris_1", "name": "Paris", "full_address": "Paris, France", "place_formatted": "75000 Paris, France"},
            {"id": "mock_madrid_1", "name": "Madrid", "full_address": "Madrid, Spain", "place_formatted": "28000 Madrid, Spain"},
            {"id": "mock_london_1", "name": "London", "full_address": "London, UK", "place_formatted": "London, United Kingdom"},
        ]
        return [s for s in mock_suggestions if query.lower() in s['name'].lower()][:5]

    def get_risk_data(self, query: str | None = None, mapbox_id: str | None = None, session_token: str | None = None) -> Optional[Dict]:
        import time as _time, random
        _time.sleep(1.0)
        return {
            "location": {
                "latitude": 40.4168 + random.uniform(-0.1, 0.1),
                "longitude": -3.7038 + random.uniform(-0.1, 0.1)
            },
            "risk_index": random.uniform(0.1, 0.8),
            "risk_label": random.choice(["Low", "Moderate", "High"]),
            "weather": {
                "timestamp": "2025-01-15T14:30:00+00:00",
                "temp_celsius": random.uniform(5, 25),
                "humidity": random.randint(40, 90),
                "wind_speed": random.uniform(1, 10),
                "raw": {"weather": [{"description": "partly cloudy"}]}
            },
            "pollution": {
                "timestamp": "2025-01-15T14:30:00+00:00",
                "components": {
                    "pm2_5": random.uniform(5, 50),
                    "pm10": random.uniform(10, 80),
                    "o3": random.uniform(20, 120),
                    "no2": random.uniform(10, 80),
                    "so2": random.uniform(1, 20),
                    "co": random.uniform(100, 1000)
                },
                "raw": {}
            },
            "norm": {
                "pm2_5": random.uniform(0, 0.8),
                "o3": random.uniform(0, 0.9),
                "pm10": random.uniform(0, 0.6),
                "no2": random.uniform(0, 0.4),
                "co": random.uniform(0, 0.3),
                "so2": random.uniform(0, 0.2),
                "temp": random.uniform(0, 0.5),
                "hum": random.uniform(0, 0.7),
                "wind": random.uniform(0, 0.8)
            }
        }

    def health_check(self) -> bool:
        return True
