"""
Repository for AutoRate ORM.
"""

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from app.database.repositories.base_repository import BaseRepository
from app.database.models import AutoRateOrm
from app.services.cbr_client import RateRecord


class AutoRateRepo(BaseRepository):
    model = AutoRateOrm

    @classmethod
    async def upsert_rates(cls, session, rates: list[RateRecord]) -> None:
        if not rates:
            return
        values = [
            {
                "currency_code": rate.currency_code,
                "currency_type": rate.currency_type,
                "rate_to_rub": rate.rate_to_rub,
            }
            for rate in rates
        ]
        stmt = insert(cls.model).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[cls.model.currency_code],
            set_={
                "currency_type": stmt.excluded.currency_type,
                "rate_to_rub": stmt.excluded.rate_to_rub,
                "updated_at": func.now(),
            },
        )
        await session.execute(stmt)
        await session.commit()
