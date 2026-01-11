"""
StarLab currency exchange API.
"""

import time

from fastapi import FastAPI, status
from fastapi.responses import Response

from app.api import routers
from app.database.db import AsyncSessionFactory
from app.database.repositories.metrics_repo import MetricsRepo


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(title="StarLab Currency Exchange")

    @app.get("/health", tags=["service"])
    async def health() -> Response:
        """Service health check."""
        return Response(status_code=status.HTTP_200_OK)

    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        path = request.url.path
        method = request.method
        if path in ("/convert", "/rates/manual", "/rates/export"):
            async with AsyncSessionFactory() as session:
                try:
                    await MetricsRepo.insert_metric(
                        session=session, method=method, path=path, duration_ms=duration_ms
                    )
                except Exception:
                    pass
        return response

    app.include_router(routers.router)

    return app


application = create_app()
