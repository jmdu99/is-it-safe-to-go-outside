"""Utility helpers for retry logic and optional profiling.

This module exposes two decorators:

* :func:`async_retry` to automatically retry asynchronous functions on
  failure with exponential backoff.
* :func:`profile_if_enabled` to profile synchronous or asynchronous
  functions when the ``ENABLE_PROFILING`` environment variable is set.

These utilities are intentionally lightweight and have no external
dependencies beyond the Python standard library.
"""

from __future__ import annotations

import asyncio
import cProfile
import functools
import io
import logging
import os
import pstats
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar, cast

import httpx

P = ParamSpec("P")
R = TypeVar("R")


def async_retry(
    *,
    max_attempts: int = 3,
    initial_delay: float = 0.5,
    backoff_factor: float = 2.0,
) -> Callable[
    [Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]
]:
    """Retry an asynchronous function with exponential backoff.

    Parameters
    ----------
    max_attempts:
        Maximum number of attempts before giving up and re‑raising the last
        exception. Defaults to three.
    initial_delay:
        Initial delay (in seconds) before the first retry. Defaults to 0.5.
    backoff_factor:
        Multiplier applied to the delay after each failed attempt. Defaults to 2.0.

    Returns
    -------
    Callable
        A decorator that wraps the target coroutine function with retry logic.
    """

    def decorator(
        func: Callable[P, Coroutine[Any, Any, R]],
    ) -> Callable[P, Coroutine[Any, Any, R]]:
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            delay: float = initial_delay
            attempt: int = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    attempt += 1
                    # Log the error and retry if attempts remain
                    logger.warning(
                        "Error in %s: %s (attempt %s/%s). Retrying in %.2fs",
                        func.__name__,
                        exc,
                        attempt,
                        max_attempts,
                        delay,
                    )
                    if attempt >= max_attempts:
                        # Exhausted all attempts; re‑raise the exception
                        raise
                    await asyncio.sleep(delay)
                    delay *= backoff_factor

        return wrapper

    return decorator


def profile_if_enabled(
    func: Callable[P, Any],
) -> Callable[P, Any]:
    """Profile a synchronous or asynchronous function if profiling is enabled.

    Profiling is controlled via the ``ENABLE_PROFILING`` environment variable.
    When set to a truthy value ("1", "true", "True"), a cProfile profile is
    captured for each invocation of the decorated function and written to the
    application logger at the ``INFO`` level. If profiling is disabled, the
    function executes normally without overhead.

    This decorator transparently handles both synchronous and asynchronous
    functions. The decorated function signature remains unchanged.
    """

    logger = logging.getLogger(func.__module__)
    enabled = os.getenv("ENABLE_PROFILING") in {"1", "true", "True"}

    if not enabled:
        # Profiling disabled; return original function unchanged
        return func

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            pr = cProfile.Profile()
            pr.enable()
            try:
                result = await cast(Callable[P, Coroutine[Any, Any, R]], func)(
                    *args, **kwargs
                )
            finally:
                pr.disable()
                s = io.StringIO()
                pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(30)
                logger.info("Profiling result for %s:\n%s", func.__name__, s.getvalue())
            return result

        return async_wrapper

    # Synchronous function profiling
    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        pr = cProfile.Profile()
        pr.enable()
        try:
            return func(*args, **kwargs)
        finally:
            pr.disable()
            s = io.StringIO()
            pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(30)
            logger.info("Profiling result for %s:\n%s", func.__name__, s.getvalue())

    return sync_wrapper


__all__ = [
    "async_retry",
    "profile_if_enabled",
    "get_http_client",
    "shutdown_http_client",
]

#
# HTTP client management
#

_http_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    """Return a shared AsyncClient instance.

    A single httpx.AsyncClient is lazily instantiated on first use and reused
    across requests. Reusing the client enables connection pooling and reduces
    overhead from repeatedly creating and closing TCP connections.

    Returns
    -------
    httpx.AsyncClient
        A shared asynchronous HTTP client.
    """
    global _http_client
    if _http_client is None:
        # Configure reasonable defaults (timeouts etc.) here if desired
        _http_client = httpx.AsyncClient()
    return _http_client


async def shutdown_http_client() -> None:
    """Close the shared AsyncClient if it has been created.

    This should be called on application shutdown to gracefully close open
    connections. It is a no‑op if the client has not been instantiated.
    """
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None
