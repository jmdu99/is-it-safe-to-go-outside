from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from app.models import (
    SuggestResult, RetrieveResult,
    RiskResponse, Coordinate
)
from app.services.mapbox_service import suggest, retrieve
from app.services.weather_service import fetch_current_weather
from app.services.pollution_service import fetch_air_pollution
from app.services.risk_service import compute_risk
from storage.db import (
    insert_weather_data,
    insert_air_quality_data,
    insert_risk_index,
)

app = FastAPI()

@app.get("/suggest", response_model=list[SuggestResult])
async def suggest_endpoint(
    q: str = Query(...), session_token: str = Query(...)
):
    try:
        return await suggest(q, session_token)
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.get("/retrieve/{mapbox_id}", response_model=RetrieveResult)
async def retrieve_endpoint(
    mapbox_id: str, session_token: str = Query(...)
):
    try:
        return await retrieve(mapbox_id, session_token)
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.get("/risk", response_model=RiskResponse)
async def risk_endpoint(
    background_tasks: BackgroundTasks,
    query: str | None = Query(None, description="Location string"),
    session_token: str | None = Query(None, description="Mapbox session token"),
    mapbox_id: str | None = Query(None, description="Preselected Mapbox ID"),
):
    """
    Compute respiratory risk using the latest available data, but
    store each source’s raw data under its own timestamp.
    """

    # Require at least one way to locate the place
    if not (query or mapbox_id):
        raise HTTPException(400, detail="Either 'query' or 'mapbox_id' must be supplied.")
    token = session_token or str(uuid4())

    # Fetch place from Mapbox
    try:
        sel_id = mapbox_id or (await suggest(query, token))[0].id
        place = await retrieve(sel_id, token)
    except Exception as e:
        raise HTTPException(400, detail=f"Mapbox error: {e}")

    lon, lat = place.center

    # Fetch weather and pollution from external APIs
    weather = await fetch_current_weather(lat, lon)
    pollution = await fetch_air_pollution(lat, lon)

    # Compute risk index and label
    idx, normed = compute_risk(weather, pollution)
    label = "Low" if idx <= 0.25 else "Moderate" if idx <= 0.50 else "High"

    # 1) Insert raw weather data with its own timestamp
    background_tasks.add_task(
        insert_weather_data,
        lat,
        lon,
        weather.timestamp,
        weather.temp_celsius,
        weather.humidity,
        weather.wind_speed,
    )

    # 2) Insert raw air quality data with its own timestamp
    aqi = pollution.raw.get("main", {}).get("aqi")
    comps = pollution.components or {}
    background_tasks.add_task(
        insert_air_quality_data,
        lat,
        lon,
        pollution.timestamp,
        aqi,
        comps.get("co"),
        comps.get("no"),
        comps.get("no2"),
        comps.get("o3"),
        comps.get("so2"),
        comps.get("pm2_5"),
        comps.get("pm10"),
        comps.get("nh3"),
    )

    # 3) Determine the unified timestamp for risk = the later of the two
    latest_ts = max(weather.timestamp, pollution.timestamp)

    # 4) Insert computed risk using the unified latest timestamp
    background_tasks.add_task(
        insert_risk_index,
        lat,
        lon,
        latest_ts,
        idx,
        label,
    )

    # Return the RiskResponse immediately, background tasks will run after
    return RiskResponse(
        location=Coordinate(latitude=lat, longitude=lon),
        risk_index=idx,
        risk_label=label,
        weather=weather,
        pollution=pollution,
        norm=normed,
    )
