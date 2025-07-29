# backend/app/services/mapbox_service.py

import httpx
from aiocache import cached
from typing import Optional, List
from pydantic import BaseModel
from app.config import settings

class SuggestResult(BaseModel):
    id: str
    name: Optional[str]
    full_address: Optional[str]
    place_formatted: Optional[str]

class RetrieveResult(BaseModel):
    id: str
    name: Optional[str]
    full_address: Optional[str]
    place_formatted: Optional[str]
    center: List[float]

@cached(ttl=None)
async def suggest(location: str, session_token: str) -> List[SuggestResult]:
    url = "https://api.mapbox.com/search/searchbox/v1/suggest"
    params = {
        "q": location,
        "session_token": session_token,
        "access_token": settings.mapbox_token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        suggestions = resp.json().get("suggestions", [])
        if not suggestions:
            raise ValueError("No suggestions returned")
        return [
            SuggestResult(
                id=item["mapbox_id"],
                name=item.get("name"),
                full_address=item.get("full_address"),
                place_formatted=item.get("place_formatted"),
            )
            for item in suggestions
        ]

@cached(ttl=None)
async def retrieve(mid: str, session_token: str) -> RetrieveResult:
    url = f"https://api.mapbox.com/search/searchbox/v1/retrieve/{mid}"
    params = {
        "session_token": session_token,
        "access_token": settings.mapbox_token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        fc = resp.json()
        feat = fc["features"][0]
        props = feat["properties"]
        geom = feat["geometry"]
        return RetrieveResult(
            id=props["mapbox_id"],
            name=props.get("name"),
            full_address=props.get("full_address"),
            place_formatted=props.get("place_formatted"),
            center=geom["coordinates"],
        )
