# backend/tests/test_storage.py

import pytest
from datetime import datetime
from sqlalchemy import text
from backend.storage.db import (
    get_connection,
    insert_raw_weather,
    insert_raw_air_quality,
    insert_risk_index,
)

@pytest.fixture(autouse=True)
def clean_tables():
    """
    Avant chaque test, on vide les trois tables pour partir d’un état tout propre.
    """
    with get_connection() as conn:
        conn.execute(text(
            "TRUNCATE weather_data, air_quality, risk_index RESTART IDENTITY"
        ))
        conn.commit()
    yield

def test_insert_and_select_weather():
    now = datetime.utcnow().isoformat()

    # Insertion météo
    insert_raw_weather("VilleTest", now, 21.5, 55.5)

    # Lecture directe
    with get_connection() as conn:
        row = conn.execute(text(
            "SELECT city, measured_at, temperature, humidity FROM weather_data"
        )).fetchone()

    assert row.city == "VilleTest"
    assert row.measured_at.isoformat().startswith(now[:19])
    assert row.temperature == 21.5
    assert row.humidity == 55.5

def test_insert_and_select_air_quality():
    now = datetime.utcnow().isoformat()

    # Insertion qualité de l’air
    insert_raw_air_quality("VilleTest", now, 99)

    # Lecture directe
    with get_connection() as conn:
        row = conn.execute(text(
            "SELECT city, measured_at, aqi FROM air_quality"
        )).fetchone()

    assert row.city == "VilleTest"
    assert row.measured_at.isoformat().startswith(now[:19])
    assert row.aqi == 99

def test_insert_and_select_risk_index():
    now = datetime.utcnow().isoformat()

    # Insertion indice de risque
    insert_risk_index("VilleTest", now, "jaune")

    # Lecture directe
    with get_connection() as conn:
        row = conn.execute(text(
            "SELECT city, measured_at, index_level FROM risk_index"
        )).fetchone()

    assert row.city == "VilleTest"
    assert row.measured_at.isoformat().startswith(now[:19])
    assert row.index_level == "jaune"
