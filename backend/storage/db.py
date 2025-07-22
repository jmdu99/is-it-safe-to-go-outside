import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# 1. Charge les variables d'environnement depuis .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

# 2. Récupère l'URL de la DB
DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Crée le moteur SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)  # echo affiche les requêtes SQL

def get_connection():
    """
    Renvoie une connexion à la base.
    Usage :
      with get_connection() as conn:
          ...
    """
    return engine.connect()
