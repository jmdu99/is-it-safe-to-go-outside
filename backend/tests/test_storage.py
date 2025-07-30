"""
Tests for the storage layer.

These tests ensure that the database schema is created correctly, that
records can be inserted and retrieved using the helper functions provided
by ``storage.db``, and that the tables are not empty after insertion.
"""

import pytest
from datetime import datetime
from sqlalchemy import text
from storage.db import (
    get_connection,
    insert_weather_data,
    insert_air_quality_data,
    insert_risk_index,
)


@pytest.fixture(autouse=True)
def clean_tables():
    with get_connection() as conn:
        conn.execute(text(
            "TRUNCATE weather_data, air_quality, risk_index RESTART IDENTITY"
        ))
        conn.commit()
    yield


def test_table_schema():
    expected = {
        "weather_data": {
            "latitude": "double precision",
            "longitude": "double precision",
            "measured_at": "timestamp with time zone",
            "temp_celsius": "double precision",
            "humidity": "integer",
            "wind_speed": "double precision",
        },
        "air_quality": {
            "latitude": "double precision",
            "longitude": "double precision",
            "measured_at": "timestamp with time zone",
            "aqi": "integer",
            "co": "double precision",
            "no": "double precision",
            "no2": "double precision",
            "o3": "double precision",
            "so2": "double precision",
            "pm2_5": "double precision",
            "pm10": "double precision",
            "nh3": "double precision",
        },
        "risk_index": {
            "latitude": "double precision",
            "longitude": "double precision",
            "measured_at": "timestamp with time zone",
            "risk_value": "double precision",
            "risk_level": "text",
        },
    }
    with get_connection() as conn:
        for table, cols in expected.items():
            rows = conn.execute(text(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name=:table ORDER BY column_name"
            ), {"table": table}).fetchall()
            found = {r.column_name: r.data_type for r in rows}
            assert found == cols

            pk_rows = conn.execute(text(
                "SELECT kcu.column_name FROM information_schema.table_constraints tc "
                "JOIN information_schema.key_column_usage kcu "
                "ON tc.constraint_name = kcu.constraint_name "
                "WHERE tc.constraint_type='PRIMARY KEY' "
                "AND tc.table_name=:table "
                "ORDER BY kcu.ordinal_position"
            ), {"table": table}).fetchall()
            assert [r.column_name for r in pk_rows] == ["latitude", "longitude", "measured_at"]


def test_insert_and_select_weather():
    now = datetime.utcnow().isoformat()
    lat, lon = 48.8566, 2.3522
    insert_weather_data(lat, lon, now, 21.5, 78, 4.12)

    with get_connection() as conn:
        row = conn.execute(text(
            "SELECT latitude, longitude, measured_at, temp_celsius, humidity, wind_speed "
            "FROM weather_data"
        )).fetchone()

    assert row.latitude == lat
    assert row.longitude == lon
    assert row.measured_at.isoformat().startswith(now[:19])
    assert row.temp_celsius == 21.5
    assert row.humidity == 78
    assert row.wind_speed == 4.12

    with get_connection() as conn2:
        count = conn2.execute(text("SELECT COUNT(*) FROM weather_data")).scalar()
    assert count > 0


def test_insert_and_select_air_quality():
    now = datetime.utcnow().isoformat()
    lat, lon = 48.8566, 2.3522
    insert_air_quality_data(
        lat, lon, now, aqi=1,
        co=107.94, no=0.56, no2=2.28, o3=36.04,
        so2=0.16, pm2_5=1.79, pm10=2.66, nh3=1.63
    )

    with get_connection() as conn:
        row = conn.execute(text(
            "SELECT latitude, longitude, measured_at, aqi, co, no, no2, o3, so2, pm2_5, pm10, nh3 "
            "FROM air_quality"
        )).fetchone()

    assert row.aqi == 1
    assert row.co == 107.94
    assert row.no == 0.56
    assert row.no2 == 2.28
    assert row.o3 == 36.04
    assert row.so2 == 0.16
    assert row.pm2_5 == 1.79
    assert row.pm10 == 2.66
    assert row.nh3 == 1.63

    with get_connection() as conn2:
        count = conn2.execute(text("SELECT COUNT(*) FROM air_quality")).scalar()
    assert count > 0


def test_insert_and_select_risk_index():
    now = datetime.utcnow().isoformat()
    lat, lon = 48.8566, 2.3522
    insert_risk_index(lat, lon, now, 0.15, "Low")

    with get_connection() as conn:
        row = conn.execute(text(
            "SELECT latitude, longitude, measured_at, risk_value, risk_level FROM risk_index"
        )).fetchone()

    assert row.risk_value == 0.15
    assert row.risk_level == "Low"

    with get_connection() as conn2:
        count = conn2.execute(text("SELECT COUNT(*) FROM risk_index")).scalar()
    assert count > 0
