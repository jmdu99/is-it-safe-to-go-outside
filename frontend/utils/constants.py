"""
Constantes de l'application
"""

# Couleurs pour les niveaux de risque
RISK_COLORS = {
    'LOW': '#28a745',      # Vert
    'MODERATE': '#ffc107', # Jaune/Orange
    'HIGH': '#dc3545'      # Rouge
}

# Coordonnées par défaut pour différentes villes
DEFAULT_COORDINATES = {
    'PARIS': [48.8566, 2.3522],
    'LYON': [45.7640, 4.8357],
    'MARSEILLE': [43.2965, 5.3698],
    'LONDON': [51.5074, -0.1278],
    'NEW_YORK': [40.7128, -74.0060]
}

# Seuils de pollution (µg/m³) selon les recommandations OMS
POLLUTION_THRESHOLDS = {
    'pm2_5': 25,   # Particules fines
    'pm10': 50,    # Particules
    'o3': 100,     # Ozone
    'no2': 200,    # Dioxyde d'azote
    'so2': 40,     # Dioxyde de soufre
    'co': 10000    # Monoxyde de carbone
}

# Seuils météorologiques optimaux
WEATHER_THRESHOLDS = {
    'temp_min': 15,    # Température minimale confortable (°C)
    'temp_max': 25,    # Température maximale confortable (°C)
    'humidity_min': 30, # Humidité minimale (%)
    'humidity_max': 60, # Humidité maximale (%)
    'wind_optimal': 3   # Vitesse de vent optimale (m/s)
}

# Informations détaillées sur les polluants
POLLUTION_INFO = {
    'pm2_5': {
        'name': 'Particules fines PM2.5',
        'description': 'Particules d\'un diamètre inférieur à 2,5 micromètres. Les plus dangereuses car elles pénètrent profondément dans les poumons.',
        'threshold': 25,
        'sources': 'Trafic automobile, industrie, chauffage au bois'
    },
    'pm10': {
        'name': 'Particules PM10',
        'description': 'Particules d\'un diamètre inférieur à 10 micromètres. Irritent les voies respiratoires supérieures.',
        'threshold': 50,
        'sources': 'Usure des pneus, travaux, érosion, pollen'
    },
    'o3': {
        'name': 'Ozone troposphérique',
        'description': 'Polluant secondaire formé par réaction photochimique. Très irritant pour les voies respiratoires.',
        'threshold': 100,
        'sources': 'Réaction entre NOx et COV sous l\'effet du soleil'
    },
    'no2': {
        'name': 'Dioxyde d\'azote',
        'description': 'Gaz irritant principalement émis par les véhicules diesel et les installations de combustion.',
        'threshold': 200,
        'sources': 'Trafic routier, centrales thermiques, chauffage'
    },
    'so2': {
        'name': 'Dioxyde de soufre',
        'description': 'Gaz irritant émis principalement par la combustion de combustibles fossiles contenant du soufre.',
        'threshold': 40,
        'sources': 'Industrie, chauffage au fioul, transport maritime'
    },
    'co': {
        'name': 'Monoxyde de carbone',
        'description': 'Gaz inodore et incolore résultant d\'une combustion incomplète. Empêche la fixation d\'oxygène sur l\'hémoglobine.',
        'threshold': 10000,
        'sources': 'Véhicules, chauffage défaillant, industrie'
    }
}

# Informations sur les facteurs météorologiques
WEATHER_INFO = {
    'temperature': {
        'name': 'Température de l\'air',
        'description': 'Influence la formation et la concentration des polluants. Les températures extrêmes affectent le système respiratoire.',
        'optimal_range': '15-25°C'
    },
    'humidity': {
        'name': 'Humidité relative',
        'description': 'Un air trop sec irrite les muqueuses, un air trop humide favorise les moisissures et allergènes.',
        'optimal_range': '30-60%'
    },
    'wind_speed': {
        'name': 'Vitesse du vent',
        'description': 'Le vent disperse les polluants. Un vent faible favorise l\'accumulation, un vent fort peut remettre en suspension les particules.',
        'optimal_range': '2-6 m/s'
    }
}

# Informations sur les niveaux de risque
RISK_INFO = {
    'LOW': {
        'description': 'Les conditions sont favorables pour les activités extérieures. La qualité de l\'air est bonne et les conditions météorologiques sont appropriées.',
        'recommendations': '• Profitez des activités extérieures\n• Aucune précaution particulière nécessaire\n• Idéal pour le sport en plein air'
    },
    'MODERATE': {
        'description': 'Les conditions sont généralement acceptables, mais les personnes particulièrement sensibles peuvent ressentir des gênes mineures.',
        'recommendations': '• Activités extérieures possibles\n• Précautions pour personnes sensibles (asthme, allergies)\n• Réduire l\'exposition prolongée\n• Éviter les efforts intenses'
    },
    'HIGH': {
        'description': 'Les conditions ne sont pas favorables pour les activités extérieures prolongées. Risque d\'irritation respiratoire pour tous.',
        'recommendations': '• Limiter les sorties prolongées\n• Porter un masque si nécessaire\n• Éviter les activités sportives extérieures\n• Privilégier les espaces intérieurs\n• Consulter un médecin si gêne respiratoire'
    }
}

# Configuration des graphiques
CHART_COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e', 
    'success': '#2ca02c',
    'warning': '#d62728',
    'info': '#9467bd'
}

# Messages d'erreur standardisés
ERROR_MESSAGES = {
    'no_data': "❌ Aucune donnée disponible",
    'api_error': "❌ Erreur de communication avec le serveur",
    'timeout': "⏱️ Délai d'attente dépassé",
    'connection_error': "🔌 Impossible de se connecter au serveur",
    'invalid_location': "📍 Lieu introuvable ou invalide",
    'rate_limit': "⚡ Trop de requêtes, veuillez patienter"
}

# Messages de succès
SUCCESS_MESSAGES = {
    'data_loaded': "✅ Données chargées avec succès",
    'location_found': "📍 Lieu trouvé",
    'cache_hit': "⚡ Données récupérées du cache"
}

# Configuration du cache
CACHE_KEYS = {
    'suggestions': 'suggestions_{query}_{token}',
    'location_details': 'location_{mapbox_id}_{token}',
    'risk_data': 'risk_{location_hash}_{timestamp}'
}

# Limites de l'application
LIMITS = {
    'max_suggestions': 10,
    'min_query_length': 2,
    'max_query_length': 100,
    'debounce_delay': 1.0,  # secondes
    'cache_ttl': 300        # secondes
}

# URLs utiles
EXTERNAL_URLS = {
    'mapbox_docs': 'https://docs.mapbox.com/api/search/',
    'openweather_docs': 'https://openweathermap.org/api/air-pollution',
    'who_air_quality': 'https://www.who.int/health-topics/air-pollution',
    'google_maps': 'https://www.google.com/maps/@{lat},{lon},15z'
}

# Formats de date/heure
DATE_FORMATS = {
    'display': '%d/%m/%Y %H:%M',
    'api': '%Y-%m-%dT%H:%M:%S%z',
    'filename': '%Y%m%d_%H%M%S'
}
