"""
Client pour l'API backend
"""
import streamlit as st
import requests
import uuid
from typing import List, Dict, Optional
from utils.config import config  # <-- Utilise l'instance, pas la classe

class APIClient:
    def __init__(self):
        self.base_url = config.BACKEND_URL  # <-- Corrigé
        self.timeout = config.API_TIMEOUT   # <-- Corrigé
    
    def suggest_locations(self, query: str, session_token: str) -> List[Dict]:
        try:
            url = f"{self.base_url}/suggest"
            params = {
                "q": query,
                "session_token": session_token
            }
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout - Le serveur met trop de temps à répondre")
            return []
        except requests.exceptions.ConnectionError:
            st.error("🔌 Erreur de connexion - Vérifiez que le backend est démarré")
            return []
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ Erreur HTTP {e.response.status_code}: {e.response.text}")
            return []
        except Exception as e:
            st.error(f"❌ Erreur inattendue: {str(e)}")
            return []

    def retrieve_location(self, mapbox_id: str, session_token: str) -> Optional[Dict]:
        try:
            url = f"{self.base_url}/retrieve/{mapbox_id}"
            params = {
                "session_token": session_token
            }
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout lors de la récupération des détails du lieu")
            return None
        except requests.exceptions.ConnectionError:
            st.error("🔌 Erreur de connexion au backend")
            return None
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ Erreur lors de la récupération: {e.response.status_code}")
            return None
        except Exception as e:
            st.error(f"❌ Erreur inattendue: {str(e)}")
            return None

    def get_risk_data(self, query: str = None, mapbox_id: str = None, session_token: str = None) -> Optional[Dict]:
        if not session_token:
            session_token = str(uuid.uuid4())
        try:
            url = f"{self.base_url}/risk"
            params = {}
            if mapbox_id:
                params["mapbox_id"] = mapbox_id
                params["session_token"] = session_token
            elif query:
                params["query"] = query
                params["session_token"] = session_token
            else:
                st.error("❌ Il faut fournir soit query soit mapbox_id")
                return None
            with st.spinner("🔄 Récupération des données météo et pollution..."):
                response = requests.get(url, params=params, timeout=self.timeout * 2)
                response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout lors de la récupération des données de risque")
            return None
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossible de se connecter au backend")
            return None
        except requests.exceptions.HTTPError as e:
            error_detail = "Erreur inconnue"
            try:
                error_detail = e.response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            st.error(f"❌ Erreur API: {error_detail}")
            return None
        except Exception as e:
            st.error(f"❌ Erreur inattendue: {str(e)}")
            return None

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code < 500
        except:
            return False

    def get_api_status(self) -> Dict[str, str]:
        status = {
            "backend": "🔴 Hors ligne",
            "mapbox": "❓ Inconnu",
            "openweather": "❓ Inconnu"
        }
        if self.health_check():
            status["backend"] = "🟢 En ligne"
            try:
                test_data = self.get_risk_data(query="Paris", session_token=str(uuid.uuid4()))
                if test_data:
                    status["mapbox"] = "🟢 Fonctionnel"
                    status["openweather"] = "🟢 Fonctionnel"
                else:
                    status["mapbox"] = "🟡 Problème possible"
                    status["openweather"] = "🟡 Problème possible"
            except:
                status["mapbox"] = "🔴 Erreur"
                status["openweather"] = "🔴 Erreur"
        return status

class MockAPIClient(APIClient):
    def suggest_locations(self, query: str, session_token: str) -> List[Dict]:
        import time
        time.sleep(0.5)
        mock_suggestions = [
            {"id": "mock_paris_1", "name": "Paris", "full_address": "Paris, France", "place_formatted": "75000 Paris, France"},
            {"id": "mock_lyon_1", "name": "Lyon", "full_address": "Lyon, France", "place_formatted": "69000 Lyon, France"},
            {"id": "mock_marseille_1", "name": "Marseille", "full_address": "Marseille, France", "place_formatted": "13000 Marseille, France"}
        ]
        filtered = [s for s in mock_suggestions if query.lower() in s['name'].lower()]
        return filtered[:5]

    def get_risk_data(self, query: str = None, mapbox_id: str = None, session_token: str = None) -> Optional[Dict]:
        import time, random
        time.sleep(1.0)
        return {
            "location": {
                "latitude": 48.8566 + random.uniform(-0.1, 0.1),
                "longitude": 2.3522 + random.uniform(-0.1, 0.1)
            },
            "risk_index": random.uniform(0.1, 0.8),
            "risk_label": random.choice(["Low", "Moderate", "High"]),
            "weather": {
                "timestamp": "2024-01-15T14:30:00+00:00",
                "temp_celsius": random.uniform(5, 25),
                "humidity": random.randint(40, 90),
                "wind_speed": random.uniform(1, 10),
                "raw": {"weather": [{"description": "partly cloudy"}]}
            },
            "pollution": {
                "timestamp": "2024-01-15T14:30:00+00:00",
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
