"""
API routes for metrics.
"""

from fastapi import APIRouter

from app.database.repositories.metrics_repo import MetricsRepo

router = APIRouter()


@router.get("/metrics", tags=["metrics"])
async def get_metrics():
    return await MetricsRepo.get_percentiles()
