"""
Repository for endpoint metrics.
"""

from sqlalchemy import func, select

from app.database.db import provide_session
from app.database.models import MetricsOrm
from app.database.repositories.base_repository import BaseRepository


class MetricsRepo(BaseRepository):
    model = MetricsOrm

    @classmethod
    async def insert_metric(
        cls, *, session, method: str, path: str, duration_ms: float
    ) -> None:
        await cls.base_insert(
            session=session,
            values={"method": method, "path": path, "duration_ms": duration_ms},
        )

    @classmethod
    @provide_session
    async def get_percentiles(cls, *, session) -> list[dict]:
        stmt = (
            select(
                cls.model.path,
                cls.model.method,
                func.percentile_cont(0.25).within_group(cls.model.duration_ms).label("p25"),
                func.percentile_cont(0.5).within_group(cls.model.duration_ms).label("p50"),
                func.percentile_cont(0.75).within_group(cls.model.duration_ms).label("p75"),
                func.percentile_cont(0.95).within_group(cls.model.duration_ms).label("p95"),
            )
            .group_by(cls.model.path, cls.model.method)
        )
        result = await session.execute(stmt)
        rows = result.all()
        return [
            {
                "path": row.path,
                "method": row.method,
                "p25": float(row.p25) if row.p25 is not None else None,
                "p50": float(row.p50) if row.p50 is not None else None,
                "p75": float(row.p75) if row.p75 is not None else None,
                "p95": float(row.p95) if row.p95 is not None else None,
            }
            for row in rows
        ]
