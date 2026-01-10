"""
Rates service.
"""

import json
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AutoRateOrm, ManualRateOrm
from app.logger import get_logger
from app.redis import RATE_SNAPSHOT_KEY
from app.services.cbr_client import RateRecord


logger = get_logger(__name__)


class RatesService:
    """Service for rates persistence and snapshot building."""

    def __init__(self, session: AsyncSession, redis_client):
        self.session = session
        self.redis = redis_client

    async def upsert_auto_rates(self, rates: list[RateRecord]) -> None:
        """Upsert auto rates from CBR into the database."""
        if not rates:
            logger.warning("No rates provided to upsert: skipping.")
            return

        values = [
            {
                "currency_code": rate.currency_code,
                "currency_type": rate.currency_type,
                "rate_to_rub": rate.rate_to_rub,
            }
            for rate in rates
        ]

        stmt = insert(AutoRateOrm).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[AutoRateOrm.currency_code],
            set_={
                "currency_type": stmt.excluded.currency_type,
                "rate_to_rub": stmt.excluded.rate_to_rub,
                "updated_at": func.now(),
            },
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def rebuild_effective_snapshot(self) -> None:
        """
        Build effective rates snapshot (manual overrides auto) and store in Redis.
        Stored as JSON mapping currency_type -> rate_to_rub (stringified Decimal).
        """
        auto_rows = (await self.session.execute(select(AutoRateOrm))).scalars().all()
        manual_rows = (await self.session.execute(select(ManualRateOrm))).scalars().all()

        rates: dict[str, Decimal] = {row.currency_type: row.rate_to_rub for row in auto_rows}
        for row in manual_rows:
            rates[row.currency_type] = row.rate_to_rub

        rates.setdefault("RUB", Decimal("1"))

        payload = json.dumps({code: str(rate) for code, rate in rates.items()})
        await self.redis.set(RATE_SNAPSHOT_KEY, payload)
