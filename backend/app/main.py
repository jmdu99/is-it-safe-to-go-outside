"""FastAPI application entrypoint.

This module defines the REST API routes exposed by the backend. In
addition to delegating work to the service layer, it configures
observability via OpenTelemetry instrumentation and Prometheus metrics. It
also integrates a simple command‑line entry point to run the server with
optional profiling.
"""

from __future__ import annotations

import os
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from app.models import SuggestResult, RetrieveResult, RiskResponse, Coordinate
from app.services.mapbox_service import suggest, retrieve
from app.services.weather_service import fetch_current_weather
from app.services.pollution_service import fetch_air_pollution
from app.services.risk_service import compute_risk
from storage.db import (
    insert_weather_data,
    insert_air_quality_data,
    insert_risk_index,
)
import asyncio

from .config import logger
from .utils import shutdown_http_client

app = FastAPI()

# Apply instrumentation for tracing and metrics if enabled via environment variable and dependencies exist
if os.getenv("ENABLE_OTEL") in {"1", "true", "True"}:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor  # type: ignore
        from prometheus_fastapi_instrumentator import Instrumentator  # type: ignore

        # Instrument FastAPI and HTTPX clients
        FastAPIInstrumentor().instrument_app(app)
        HTTPXClientInstrumentor().instrument()
        # Expose Prometheus metrics at /metrics by default
        Instrumentator().instrument(app).expose(app)
        logger.info("OpenTelemetry and Prometheus instrumentation enabled")
    except Exception as exc:  # noqa: BLE001
        # Falling back to no instrumentation when optional dependencies are missing
        logger.info("Observability instrumentation unavailable: %s", exc)
else:
    logger.info("OpenTelemetry instrumentation disabled (ENABLE_OTEL not set)")


@app.get("/suggest", response_model=list[SuggestResult])
async def suggest_endpoint(
    q: str = Query(..., description="Location string"),
    session_token: str = Query(..., description="Mapbox session token"),
) -> list[SuggestResult]:
    """Return location suggestions for an autocomplete query."""
    logger.info("/suggest called with q='%s'", q)
    try:
        return await suggest(q, session_token)
    except Exception as e:
        logger.error("Error in suggest endpoint: %s", e)
        raise HTTPException(400, detail=str(e))


@app.get("/retrieve/{mapbox_id}", response_model=RetrieveResult)
async def retrieve_endpoint(
    mapbox_id: str,
    session_token: str = Query(..., description="Mapbox session token"),
) -> RetrieveResult:
    """Return detailed information about a location by its Mapbox id."""
    logger.info("/retrieve called with id='%s'", mapbox_id)
    try:
        return await retrieve(mapbox_id, session_token)
    except Exception as e:
        logger.error("Error in retrieve endpoint: %s", e)
        raise HTTPException(400, detail=str(e))


@app.get("/risk", response_model=RiskResponse)
async def risk_endpoint(
    background_tasks: BackgroundTasks,
    query: str | None = Query(None, description="Location string"),
    session_token: str | None = Query(None, description="Mapbox session token"),
    mapbox_id: str | None = Query(None, description="Preselected Mapbox ID"),
) -> RiskResponse:
    """Compute the respiratory risk index for a given location."""
    token = session_token or str(uuid4())
    logger.info("/risk called (query=%s, mapbox_id=%s)", query, mapbox_id)
    # ensure the caller supplied at least one way to locate a place
    if query is None and mapbox_id is None:
        raise HTTPException(
            status_code=400,
            detail="Either 'query' or 'mapbox_id' must be supplied.",
        )
    try:
        if mapbox_id:
            sel_id = mapbox_id
        else:
            suggestions = await suggest(query or "", token)
            sel_id = suggestions[0].id
        place = await retrieve(sel_id, token)
    except Exception as e:
        logger.error("Error retrieving location: %s", e)
        raise HTTPException(400, detail=f"Mapbox error: {e}")

    lon, lat = place.center

    # Fetch weather and pollution concurrently for efficiency
    try:
        # Launch weather and pollution requests concurrently to reduce latency
        weather, pollution = await asyncio.gather(
            fetch_current_weather(lat, lon), fetch_air_pollution(lat, lon)
        )
    except Exception as e:
        logger.error("Error fetching weather or pollution: %s", e)
        raise HTTPException(400, detail=f"Data fetch error: {e}")

    idx, normed = compute_risk(weather, pollution)
    label = "Low" if idx <= 0.20 else "Moderate" if idx <= 0.40 else "High"

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

    response = RiskResponse(
        location=Coordinate(latitude=lat, longitude=lon),
        risk_index=idx,
        risk_label=label,
        weather=weather,
        pollution=pollution,
        norm=normed,
    )

    return response


def _run_with_profiler() -> None:
    """Run the application under cProfile if profiling is enabled at startup."""
    import cProfile
    import pstats
    import uvicorn
    from io import StringIO

    pr = cProfile.Profile()
    pr.enable()
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        pr.disable()
        s = StringIO()
        pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(50)
        logger.info("Server profiling summary:\n%s", s.getvalue())


if __name__ == "__main__":
    # When executed directly, optionally run with a profiler based on an env var
    if os.getenv("ENABLE_PROFILING") in {"1", "true", "True"}:
        _run_with_profiler()
    else:
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8000)


# Register shutdown event to close shared resources
@app.on_event("shutdown")
async def _shutdown() -> None:
    """Gracefully close shared clients on application shutdown."""
    await shutdown_http_client()
