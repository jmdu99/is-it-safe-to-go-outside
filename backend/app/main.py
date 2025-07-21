from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query
from app.models import (
    SuggestResult, RetrieveResult,
    RiskResponse, Coordinate,
    WeatherResponse, PollutionResponse
)
from app.services.mapbox_service import suggest, retrieve
from app.services.weather_service import fetch_current_weather
from app.services.pollution_service import fetch_air_pollution
from app.services.risk_service import compute_risk

app = FastAPI(title="Respiratory Risk API")

@app.get("/suggest", response_model=list[SuggestResult])
async def suggest_endpoint(
    q: str = Query(..., description="Location string"),
    session_token: str = Query(..., description="Mapbox session token")
):
    try:
        return await suggest(q, session_token)
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.get("/retrieve/{mapbox_id}", response_model=RetrieveResult)
async def retrieve_endpoint(
    mapbox_id: str,
    session_token: str = Query(..., description="Mapbox session token")
):
    try:
        return await retrieve(mapbox_id, session_token)
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.get("/risk", response_model=RiskResponse)
async def risk_endpoint(
    query: str = Query(..., description="Location string"),
    session_token: str | None = Query(None, description="Mapbox session token"),
    mapbox_id: str | None = Query(None, description="Preselected Mapbox ID")
):
    token = session_token or str(uuid4())
    try:
        if mapbox_id:
            sel = mapbox_id
        else:
            sug = await suggest(query, token)
            sel = sug[0].id
        place = await retrieve(sel, token)
    except Exception as e:
        raise HTTPException(400, detail=f"Mapbox error: {e}")

    lon, lat = place.center

    weather   = await fetch_current_weather(lat, lon)
    pollution = await fetch_air_pollution(lat, lon)

    idx, normed = compute_risk(weather, pollution)
    label = "Low" if idx <= 0.25 else "Moderate" if idx <= 0.50 else "High"

    return RiskResponse(
        location=Coordinate(latitude=lat, longitude=lon),
        risk_index=idx,
        risk_label=label,
        weather=weather,
        pollution=pollution,
        norm=normed
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
