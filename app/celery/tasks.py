"""
Celery tasks.
"""

import asyncio
import logging

from app.celery.app import celery_app
from app.database.db import provide_session
from app.redis import get_redis_client
from app.services.cbr_client import CbrClient
from app.database.repositories.auto_rate_repo import AutoRateRepo
from app.domain.exchanger import Exchanger

logger = logging.getLogger(__name__)


@celery_app.task(name="fetch_cbr_rates")
def fetch_cbr_rates_task() -> None:
    """Celery entrypoint for fetching rates and refreshing snapshot."""
    asyncio.run(_fetch_and_refresh())


@provide_session
async def _fetch_and_refresh(*, session) -> None:
    client = CbrClient()
    rates = await client.fetch_rates()

    redis = get_redis_client()
    try:
        await AutoRateRepo.upsert_rates(session, rates)
        exchanger = Exchanger(redis=redis)
        await exchanger.rebuild_snapshot()
    finally:
        await redis.close()
