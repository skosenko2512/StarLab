"""
StarLab currency exchange API.
"""

from fastapi import FastAPI, status
from fastapi.responses import Response

from app.api import routers

def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(title="StarLab Currency Exchange")

    @app.get("/health", tags=["service"])
    async def health() -> Response:
        """Service health check."""
        return Response(status_code=status.HTTP_200_OK)

    app.include_router(routers.router)

    return app


application = create_app()
