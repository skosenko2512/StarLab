"""
Domain service for currency exchange.
"""

import csv
import io
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import provide_session
from app.database.repositories.auto_rate_repo import AutoRateRepo
from app.database.repositories.manual_rate_repo import ManualRateRepo
from app.handlers.errors import RateNotFound, SnapshotUnavailable
from app.adapters.schemas import ManualRate
from app.redis import RATE_SNAPSHOT_KEY

ROUNDING = Decimal("0.0001")


class Exchanger:
    """Exchange domain service."""

    def __init__(
        self,
        redis: Redis,
        *,
        auto_repo: type[AutoRateRepo] = AutoRateRepo,
        manual_repo: type[ManualRateRepo] = ManualRateRepo,
    ):
        self.redis = redis
        self.auto_repo = auto_repo
        self.manual_repo = manual_repo

    async def get_snapshot(self) -> dict[str, Decimal]:
        payload = await self.redis.get(RATE_SNAPSHOT_KEY)
        if not payload:
            raise SnapshotUnavailable("Rates snapshot is unavailable.")
        try:
            raw = json.loads(payload)
            return {code: Decimal(str(val)) for code, val in raw.items()}
        except Exception as exc:
            raise SnapshotUnavailable("Failed to parse rates snapshot.") from exc

    def convert(self, amount: Decimal, from_currency: str, to_currency: str, rates: dict[str, Decimal]) -> Decimal:
        try:
            from_rate = rates[from_currency]
            to_rate = rates[to_currency]
        except KeyError as exc:
            raise RateNotFound(f"Missing rate for {exc}") from exc

        try:
            result = (amount * from_rate / to_rate).quantize(ROUNDING, rounding=ROUND_HALF_UP)
        except (InvalidOperation, ZeroDivisionError) as exc:
            raise RateNotFound("Invalid rate data") from exc
        return result

    async def convert_with_snapshot(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        rates = await self.get_snapshot()
        return self.convert(amount, from_currency, to_currency, rates)

    @provide_session
    async def rebuild_snapshot(self, *, session: AsyncSession) -> None:
        auto_rows = await self.auto_repo.get_all(session)
        manual_rows = await self.manual_repo.get_all(session)

        rates: dict[str, Decimal] = {row.currency_type: row.rate_to_rub for row in auto_rows}
        for row in manual_rows:
            rates[row.currency_type] = row.rate_to_rub
        rates.setdefault("RUB", Decimal("1"))

        payload = json.dumps({code: str(rate) for code, rate in rates.items()})
        await self.redis.set(RATE_SNAPSHOT_KEY, payload)

    @staticmethod
    def build_csv(rates: dict[str, Decimal]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["currency_type", "rate_to_rub"])
        for code, rate in sorted(rates.items()):
            writer.writerow([code, str(rate)])
        return output.getvalue()

    @provide_session
    async def set_manual_rates(self, rates: list[ManualRate], *, session: AsyncSession) -> None:
        await self.manual_repo.upsert_rates(session, rates)
        await self.rebuild_snapshot()

    @provide_session
    async def delete_manual_rate(
        self, currency_code: int, *, session: AsyncSession
    ) -> None:
        await self.manual_repo.delete_by_filter(session=session, currency_code=currency_code)
        await self.rebuild_snapshot()
