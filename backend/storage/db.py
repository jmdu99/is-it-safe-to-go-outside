import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Build DATABASE_URL if not set
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    user = os.getenv("POSTGRES_USER", "postgres")
    pwd = os.getenv("POSTGRES_PASSWORD", "postgres")
    db = os.getenv("POSTGRES_DB", "safeair_db")
    host = os.getenv("POSTGRES_HOST", "localhost")
    DATABASE_URL = f"postgresql+psycopg2://{user}:{pwd}@{host}:5432/{db}"

engine = create_engine(DATABASE_URL, echo=False, future=True)

def get_connection():
    return engine.connect()

def _init_db():
    weather_sql = text("""
        CREATE TABLE IF NOT EXISTS weather_data (
            latitude    DOUBLE PRECISION NOT NULL,
            longitude   DOUBLE PRECISION NOT NULL,
            measured_at TIMESTAMPTZ        NOT NULL,
            temp_celsius DOUBLE PRECISION,
            humidity     INTEGER,
            wind_speed   DOUBLE PRECISION,
            PRIMARY KEY (latitude, longitude, measured_at)
        );
    """)
    air_sql = text("""
        CREATE TABLE IF NOT EXISTS air_quality (
            latitude    DOUBLE PRECISION NOT NULL,
            longitude   DOUBLE PRECISION NOT NULL,
            measured_at TIMESTAMPTZ        NOT NULL,
            aqi         INTEGER,
            co          DOUBLE PRECISION,
            no          DOUBLE PRECISION,
            no2         DOUBLE PRECISION,
            o3          DOUBLE PRECISION,
            so2         DOUBLE PRECISION,
            pm2_5       DOUBLE PRECISION,
            pm10        DOUBLE PRECISION,
            nh3         DOUBLE PRECISION,
            PRIMARY KEY (latitude, longitude, measured_at)
        );
    """)
    risk_sql = text("""
        CREATE TABLE IF NOT EXISTS risk_index (
            latitude    DOUBLE PRECISION NOT NULL,
            longitude   DOUBLE PRECISION NOT NULL,
            measured_at TIMESTAMPTZ        NOT NULL,
            risk_value  DOUBLE PRECISION,
            risk_level  TEXT,
            PRIMARY KEY (latitude, longitude, measured_at)
        );
    """)
    with get_connection() as conn:
        conn.execute(weather_sql)
        conn.execute(air_sql)
        conn.execute(risk_sql)
        conn.commit()

_init_db()

def insert_weather_data(lat, lon, measured_at, temp_celsius, humidity, wind_speed):
    sql = text("""
        INSERT INTO weather_data (
            latitude, longitude, measured_at, temp_celsius, humidity, wind_speed
        ) VALUES (
            :lat, :lon, :measured_at, :temp_celsius, :humidity, :wind_speed
        )
        ON CONFLICT (latitude, longitude, measured_at) DO NOTHING;
    """)
    with get_connection() as conn:
        conn.execute(sql, {
            "lat": lat,
            "lon": lon,
            "measured_at": measured_at,
            "temp_celsius": temp_celsius,
            "humidity": humidity,
            "wind_speed": wind_speed,
        })
        conn.commit()

def insert_air_quality_data(
    lat, lon, measured_at, aqi,
    co=None, no=None, no2=None, o3=None,
    so2=None, pm2_5=None, pm10=None, nh3=None
):
    sql = text("""
        INSERT INTO air_quality (
            latitude, longitude, measured_at,
            aqi, co, no, no2, o3, so2, pm2_5, pm10, nh3
        ) VALUES (
            :lat, :lon, :measured_at,
            :aqi, :co, :no, :no2, :o3, :so2, :pm2_5, :pm10, :nh3
        )
        ON CONFLICT (latitude, longitude, measured_at) DO NOTHING;
    """)
    with get_connection() as conn:
        conn.execute(sql, {
            "lat": lat, "lon": lon, "measured_at": measured_at,
            "aqi": aqi, "co": co, "no": no, "no2": no2,
            "o3": o3, "so2": so2, "pm2_5": pm2_5, "pm10": pm10, "nh3": nh3,
        })
        conn.commit()

def insert_risk_index(lat, lon, measured_at, risk_value, risk_level):
    sql = text("""
        INSERT INTO risk_index (
            latitude, longitude, measured_at, risk_value, risk_level
        ) VALUES (
            :lat, :lon, :measured_at, :risk_value, :risk_level
        )
        ON CONFLICT (latitude, longitude, measured_at) DO NOTHING;
    """)
    with get_connection() as conn:
        conn.execute(sql, {
            "lat": lat,
            "lon": lon,
            "measured_at": measured_at,
            "risk_value": risk_value,
            "risk_level": risk_level,
        })
        conn.commit()
