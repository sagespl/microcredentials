"""HTTP middlewares for the AGPW API."""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.metrics import REQUEST_COUNT, REQUEST_LATENCY

logger = logging.getLogger("agpw.api")


def setup_middlewares(app: FastAPI) -> None:
    """Register all HTTP middlewares on the given FastAPI app."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def monitor_requests(request: Request, call_next):
        """Log every request and record Prometheus metrics for it."""
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time

        route = request.scope.get("route")
        path_template = route.path if route is not None else request.url.path

        REQUEST_COUNT.labels(request.method, path_template, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, path_template).observe(duration)
        logger.info(
            "%s %s -> %s (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration * 1000,
        )
        return response
