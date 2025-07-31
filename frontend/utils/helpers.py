"""
Fonctions utilitaires pour l'application
"""
import streamlit as st
import uuid
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from utils.constants import RISK_COLORS, DATE_FORMATS

def init_session_state():
    """Initialise l'état de session Streamlit"""
    
    # Token de session unique pour Mapbox
    if 'session_token' not in st.session_state:
        st.session_state.session_token = str(uuid.uuid4())
    
    # Données de l'application
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = None
    
    if 'current_risk_data' not in st.session_state:
        st.session_state.current_risk_data = None
    
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = []
    
    if 'last_search' not in st.session_state:
        st.session_state.last_search = ""
    
    if 'last_search_time' not in st.session_state:
        st.session_state.last_search_time = 0
    
    # Cache simple en mémoire
    if 'cache' not in st.session_state:
        st.session_state.cache = {}
    
    # Configuration de l'interface
    if 'show_debug' not in st.session_state:
        st.session_state.show_debug = False

def get_risk_color(risk_label: str) -> str:
    """Retourne la couleur correspondant au niveau de risque"""
    return RISK_COLORS.get(risk_label.upper(), '#6c757d')  # Gris par défaut

def format_timestamp(timestamp_str: str) -> str:
    """Formate un timestamp ISO en format lisible"""
    try:
        # Parse le timestamp ISO
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime(DATE_FORMATS['display'])
    except (ValueError, AttributeError):
        return timestamp_str

def format_coordinates(lat: float, lon: float, precision: int = 6) -> str:
    """Formate les coordonnées pour l'affichage"""
    return f"{lat:.{precision}f}, {lon:.{precision}f}"

def debounce(func, delay: float = 1.0):
    """Décorateur pour implémenter un debounce sur une fonction"""
    def wrapper(*args, **kwargs):
        current_time = time.time()
        
        # Clé unique pour cette fonction et ces arguments
        cache_key = f"debounce_{func.__name__}_{hash(str(args) + str(kwargs))}"
        last_call_time = st.session_state.get(f"{cache_key}_time", 0)
        
        if current_time - last_call_time >= delay:
            st.session_state[f"{cache_key}_time"] = current_time
            return func(*args, **kwargs)
        
        return None
    
    return wrapper

def cache_get(key: str) -> Optional[Any]:
    """Récupère une valeur du cache de session"""
    cache_entry = st.session_state.cache.get(key)
    
    if cache_entry is None:
        return None
    
    # Vérification de l'expiration
    if time.time() > cache_entry['expires']:
        del st.session_state.cache[key]
        return None
    
    return cache_entry['value']

def cache_set(key: str, value: Any, ttl: int = 300):
    """Stocke une valeur dans le cache de session"""
    st.session_state.cache[key] = {
        'value': value,
        'expires': time.time() + ttl
    }

def clear_cache(pattern: str = None):
    """Vide le cache (entièrement ou selon un motif)"""
    if pattern is None:
        st.session_state.cache.clear()
    else:
        keys_to_delete = [k for k in st.session_state.cache.keys() if pattern in k]
        for key in keys_to_delete:
            del st.session_state.cache[key]

def calculate_cache_stats() -> Dict[str, Any]:
    """Calcule les statistiques du cache"""
    cache = st.session_state.cache
    current_time = time.time()
    
    total_entries = len(cache)
    expired_entries = sum(1 for entry in cache.values() if current_time > entry['expires'])
    active_entries = total_entries - expired_entries
    
    return {
        'total': total_entries,
        'active': active_entries,
        'expired': expired_entries,
        'hit_rate': getattr(st.session_state, 'cache_hits', 0) / max(getattr(st.session_state, 'cache_requests', 1), 1)
    }

def validate_coordinates(lat: float, lon: float) -> bool:
    """Valide des coordonnées géographiques"""
    return -90 <= lat <= 90 and -180 <= lon <= 180

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcule la distance entre deux points géographiques (en km)"""
    import math
    
    # Rayon de la Terre en km
    R = 6371
    
    # Conversion en radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Différences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Formule de Haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def format_distance(distance_km: float) -> str:
    """Formate une distance pour l'affichage"""
    if distance_km < 1:
        return f"{distance_km * 1000:.0f} m"
    elif distance_km < 10:
        return f"{distance_km:.1f} km"
    else:
        return f"{distance_km:.0f} km"

def generate_google_maps_url(lat: float, lon: float, zoom: int = 15) -> str:
    """Génère une URL Google Maps pour des coordonnées"""
    return f"https://www.google.com/maps/@{lat},{lon},{zoom}z"

def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier pour le rendre sûr"""
    import re
    # Remplace les caractères non autorisés par des underscores
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Tronque un texte s'il est trop long"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def format_number(number: float, precision: int = 2, unit: str = "") -> str:
    """Formate un nombre pour l'affichage"""
    if abs(number) >= 1000:
        return f"{number/1000:.{precision}f}k{unit}"
    else:
        return f"{number:.{precision}f}{unit}"

def create_download_link(data: Any, filename: str, mime_type: str = "application/json") -> str:
    """Crée un lien de téléchargement pour des données"""
    import json
    import base64
    
    if isinstance(data, dict) or isinstance(data, list):
        data_str = json.dumps(data, indent=2)
    else:
        data_str = str(data)
    
    b64_data = base64.b64encode(data_str.encode()).decode()
    
    return f'<a href="data:{mime_type};base64,{b64_data}" download="{filename}">📥 Télécharger {filename}</a>'

def display_debug_info():
    """Affiche les informations de débogage"""
    if st.session_state.get('show_debug', False):
        with st.expander("🐛 Informations de débogage"):
            
            # État de session
            st.subheader("État de session")
            session_info = {
                'session_token': st.session_state.session_token[:8] + "...",
                'selected_location': bool(st.session_state.selected_location),
                'current_risk_data': bool(st.session_state.current_risk_data),
                'suggestions_count': len(st.session_state.suggestions)
            }
            st.json(session_info)
            
            # Statistiques du cache
            st.subheader("Cache")
            cache_stats = calculate_cache_stats()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", cache_stats['total'])
            col2.metric("Actif", cache_stats['active'])
            col3.metric("Expiré", cache_stats['expired'])
            col4.metric("Taux hit", f"{cache_stats['hit_rate']:.2%}")
            
            # Actions de débogage
            st.subheader("Actions")
            col1, col2, col3 = st.columns(3)
            
            if col1.button("🗑️ Vider cache"):
                clear_cache()
                st.success("Cache vidé")
            
            if col2.button("🔄 Nouveau token"):
                st.session_state.session_token = str(uuid.uuid4())
                st.success("Nouveau token généré")
            
            if col3.button("🔄 Reset session"):
                for key in list(st.session_state.keys()):
                    if key != 'show_debug':
                        del st.session_state[key]
                init_session_state()
                st.success("Session réinitialisée")

def handle_error(error: Exception, context: str = ""):
    """Gestionnaire d'erreur centralisé"""
    error_msg = f"Erreur {context}: {str(error)}"
    
    # Log de l'erreur (en production, utiliser un vrai logger)
    print(f"ERROR: {error_msg}")
    
    # Affichage utilisateur selon le type d'erreur
    if "timeout" in str(error).lower():
        st.error("⏱️ Délai d'attente dépassé. Veuillez réessayer.")
    elif "connection" in str(error).lower():
        st.error("🔌 Problème de connexion. Vérifiez que le serveur est démarré.")
    else:
        st.error(f"❌ {error_msg}")
    
    # En mode debug, afficher plus de détails
    if st.session_state.get('show_debug', False):
        st.exception(error)

def show_loading_spinner(message: str = "Chargement..."):
    """Affiche un spinner de chargement"""
    return st.spinner(message)

def create_metric_card(title: str, value: str, delta: str = None, help_text: str = None):
    """Crée une carte de métrique stylisée"""
    st.metric(
        label=title,
        value=value,
        delta=delta,
        help=help_text
    )

def export_data_to_csv(data: List[Dict], filename: str = None) -> str:
    """Exporte des données vers CSV"""
    import pandas as pd
    import io
    
    if not filename:
        filename = f"export_{datetime.now().strftime(DATE_FORMATS['filename'])}.csv"
    
    df = pd.DataFrame(data)
    
    # Conversion en CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return csv_buffer.getvalue()
