"""
Configuration de l'application
"""
import os
from typing import Optional

class Config:
    # Backend API
    @property
    def BACKEND_URL(self) -> str:
        return os.getenv("BACKEND_URL", "")

    @property
    def API_TIMEOUT(self) -> int:
        return int(os.getenv("API_TIMEOUT", "10"))

    # Mode de développement
    @property
    def DEVELOPMENT_MODE(self) -> bool:
        return os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"

    @property
    def USE_MOCK_API(self) -> bool:
        return os.getenv("USE_MOCK_API", "false").lower() == "true"

    # Mapbox (pour affichage côté frontend si nécessaire)
    @property
    def MAPBOX_PUBLIC_TOKEN(self) -> Optional[str]:
        return os.getenv("MAPBOX_PUBLIC_TOKEN")

    # Configuration Streamlit
    @property
    def PAGE_TITLE(self) -> str:
        return "Est-il sûr de sortir ?"

    @property
    def PAGE_ICON(self) -> str:
        return "🌬️"

    @property
    def LAYOUT(self) -> str:
        return "wide"

    # Cache
    @property
    def CACHE_TTL(self) -> int:
        return int(os.getenv("CACHE_TTL", "300"))

    # Logs
    @property
    def LOG_LEVEL(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    def is_production(self) -> bool:
        """Détermine si on est en mode production"""
        return not self.DEVELOPMENT_MODE

    def get_api_client_class(self):
        """Retourne la classe de client API appropriée"""
        if self.USE_MOCK_API:
            from services.api_client import MockAPIClient
            return MockAPIClient
        else:
            from services.api_client import APIClient
            return APIClient

    def validate_config(self) -> list:
        """Valide la configuration et retourne les erreurs"""
        errors = []

        if not self.BACKEND_URL:
            errors.append("BACKEND_URL est requis")

        if self.API_TIMEOUT <= 0:
            errors.append("API_TIMEOUT doit être positif")

        if self.MAPBOX_PUBLIC_TOKEN and not self.MAPBOX_PUBLIC_TOKEN.startswith('pk.'):
            errors.append("MAPBOX_PUBLIC_TOKEN semble invalide")

        return errors

# Instance globale à utiliser partout
config = Config()

# Variables d'environnement par défaut pour le développement
DEFAULT_ENV_VARS = {
    "BACKEND_URL": "http://backend:8000",
    "API_TIMEOUT": "10",
    "DEVELOPMENT_MODE": "true",
    "USE_MOCK_API": "false",
    "CACHE_TTL": "300",
    "LOG_LEVEL": "INFO"
}

def load_env_file(filename: str = ".env"):
    """Charge les variables d'environnement depuis un fichier"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def create_env_template(filename: str = ".env.example"):
    """Crée un fichier d'exemple de configuration"""
    with open(filename, 'w') as f:
        f.write("# Configuration du frontend Streamlit\n\n")
        f.write("# URL du backend API\n")
        f.write("BACKEND_URL=http://backend:8000\n\n")
        f.write("# Timeout des requêtes API (secondes)\n")
        f.write("API_TIMEOUT=10\n\n")
        f.write("# Mode développement\n")
        f.write("DEVELOPMENT_MODE=true\n\n")
        f.write("# Utiliser des données mockées (pour tests)\n")
        f.write("USE_MOCK_API=false\n\n")
        f.write("# Token public Mapbox (optionnel)\n")
        f.write("# MAPBOX_PUBLIC_TOKEN=pk.your_public_token_here\n\n")
        f.write("# TTL du cache (secondes)\n")
        f.write("CACHE_TTL=300\n\n")
        f.write("# Niveau de log\n")
        f.write("LOG_LEVEL=INFO\n")
