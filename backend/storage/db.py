# backend/storage/db.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Charger .env
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Créer le moteur et la connexion
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)
def get_connection():
    return engine.connect()

# Fonction d’insertion météo
def insert_raw_weather(city: str, measured_at: str, temperature: float, humidity: float):
    query = text("""
        INSERT INTO weather_data (city, measured_at, temperature, humidity)
        VALUES (:city, :measured_at, :temperature, :humidity)
    """)
    with get_connection() as conn:
        conn.execute(query, {
            "city": city,
            "measured_at": measured_at,
            "temperature": temperature,
            "humidity": humidity
        })
        conn.commit()

# Fonction d’insertion qualité d’air
def insert_raw_air_quality(city: str, measured_at: str, aqi: int):
    query = text("""
        INSERT INTO air_quality (city, measured_at, aqi)
        VALUES (:city, :measured_at, :aqi)
    """)
    with get_connection() as conn:
        conn.execute(query, {
            "city": city,
            "measured_at": measured_at,
            "aqi": aqi
        })
        conn.commit()

# Fonction d’insertion indice calculé
def insert_risk_index(city: str, measured_at: str, index_level: str):
    query = text("""
        INSERT INTO risk_index (city, measured_at, index_level)
        VALUES (:city, :measured_at, :index_level)
    """)
    with get_connection() as conn:
        conn.execute(query, {
            "city": city,
            "measured_at": measured_at,
            "index_level": index_level
        })
        conn.commit()
