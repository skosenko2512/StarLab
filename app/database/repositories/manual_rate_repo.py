"""
Repository for ManualRate ORM.
"""

from sqlalchemy.dialects.postgresql import insert

from app.database.repositories.base_repository import BaseRepository
from app.adapters.schemas import ManualRate
from app.database.models import ManualRateOrm


class ManualRateRepo(BaseRepository):
    model = ManualRateOrm

    @classmethod
    async def upsert_rates(cls, session, rates: list[ManualRate]) -> None:
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
            },
        )
        await session.execute(stmt)
        await session.commit()
