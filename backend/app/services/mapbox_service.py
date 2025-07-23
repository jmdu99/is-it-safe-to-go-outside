"""Integration with Mapbox's Search Box API.

This module defines asynchronous functions for suggesting places based on a free
text query and retrieving detailed information about a selected place. The
functions include retry logic with exponential backoff, optional profiling,
caching and sensible fallbacks when API credentials are missing.
"""

from __future__ import annotations

from aiocache import cached
from typing import List

from ..config import settings, logger
from ..models import SuggestResult, RetrieveResult
from ..utils import async_retry, profile_if_enabled, get_http_client


@cached(ttl=None)
@async_retry(max_attempts=3)
@profile_if_enabled
async def suggest(location: str, session_token: str) -> List[SuggestResult]:
    """Return a list of place suggestions for a given search string.

    When the Mapbox API token is not provided, this function returns a
    single stubbed suggestion to avoid network calls during development
    and testing.

    Parameters
    ----------
    location:
        Free‑text location string entered by the user.
    session_token:
        Mapbox session token used to group autocomplete requests.

    Returns
    -------
    list[SuggestResult]
        A list of suggestion objects. At least one suggestion is always
        returned; if the upstream API yields no results a ``ValueError``
        is raised and subsequently retried.
    """
    # If no valid Mapbox token is provided, return a deterministic stubbed response
    if not settings.mapbox_token:
        logger.warning(
            "Mapbox token missing; returning stubbed suggestion for '%s'", location
        )
        return [
            SuggestResult(
                id="dummy-id",
                name=location,
                full_address=None,
                place_formatted=location,
            )
        ]

    url = "https://api.mapbox.com/search/searchbox/v1/suggest"
    params = {
        "q": location,
        "session_token": session_token,
        "access_token": settings.mapbox_token,
    }
    client = get_http_client()
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
@async_retry(max_attempts=3)
@profile_if_enabled
async def retrieve(mid: str, session_token: str) -> RetrieveResult:
    """Retrieve a single place record by its Mapbox identifier.

    Similar to :func:`suggest`, this function returns a stubbed record if
    no Mapbox API token is configured. It uses exponential backoff on
    failure and is optionally profiled when enabled via the
    ``ENABLE_PROFILING`` environment variable.

    Parameters
    ----------
    mid:
        The Mapbox identifier returned by :func:`suggest`.
    session_token:
        Mapbox session token used to group autocomplete requests.

    Returns
    -------
    RetrieveResult
        A detailed place record containing location coordinates and metadata.
    """
    if not settings.mapbox_token:
        logger.warning(
            "Mapbox token missing; returning stubbed retrieve for id '%s'", mid
        )
        return RetrieveResult(
            id=mid,
            name="Stubbed Location",
            full_address=None,
            place_formatted=None,
            center=[0.0, 0.0],
        )

    url = f"https://api.mapbox.com/search/searchbox/v1/retrieve/{mid}"
    params = {
        "session_token": session_token,
        "access_token": settings.mapbox_token,
    }
    client = get_http_client()
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
