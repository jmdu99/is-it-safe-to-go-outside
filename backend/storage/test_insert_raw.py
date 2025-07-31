# backend/storage/db.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Charger le .env de la racine du projet
dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path=dotenv_path)

# 2. Créer le moteur SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)


def get_connection():
    """
    Renvoie une connexion à la base.
    Usage :
      with get_connection() as conn:
          ...
    """
    return engine.connect()


def insert_raw_weather(
    city: str, measured_at: str, temperature: float, humidity: float
):
    """
    Insère une ligne dans weather_data.
    """
    query = text(
        """
        INSERT INTO weather_data (city, measured_at, temperature, humidity)
        VALUES (:city, :measured_at, :temperature, :humidity)
    """
    )
    with get_connection() as conn:
        conn.execute(
            query,
            {
                "city": city,
                "measured_at": measured_at,
                "temperature": temperature,
                "humidity": humidity,
            },
        )
        conn.commit()


def insert_raw_air_quality(city: str, measured_at: str, aqi: int):
    """
    Insère une ligne dans air_quality.
    """
    query = text(
        """
        INSERT INTO air_quality (city, measured_at, aqi)
        VALUES (:city, :measured_at, :aqi)
    """
    )
    with get_connection() as conn:
        conn.execute(query, {"city": city, "measured_at": measured_at, "aqi": aqi})
        conn.commit()
