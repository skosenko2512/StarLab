import json
import pytest

from app.domain.exchanger import Exchanger, RateNotFound
from app.redis import RATE_SNAPSHOT_KEY
from tests.tests_fixtures.fixtures import FakeRow, DummySession


@pytest.mark.asyncio
async def test_rebuild_snapshot_merges_manual_priority(fake_redis):
    class AutoRepoStub:
        @classmethod
        async def get_all(cls, session):
            return [FakeRow("USD", 100), FakeRow("EUR", 90)]

    class ManualRepoStub:
        @classmethod
        async def get_all(cls, session):
            return [FakeRow("EUR", 80)]

        @classmethod
        async def upsert_rates(cls, session, rates):
            return None

        @classmethod
        async def delete_by_filter(cls, session, currency_code):
            return None

    exchanger = Exchanger(redis=fake_redis, auto_repo=AutoRepoStub, manual_repo=ManualRepoStub)

    await exchanger.rebuild_snapshot.__wrapped__(exchanger, session=DummySession())  # type: ignore[attr-defined]

    payload = await fake_redis.get(RATE_SNAPSHOT_KEY)
    data = json.loads(payload)
    assert data["EUR"] == "80"
    assert data["USD"] == "100"
    assert data["RUB"] == "1"


@pytest.mark.asyncio
async def test_convert_raises_for_missing_rate(fake_redis):
    exchanger = Exchanger(redis=fake_redis)
    with pytest.raises(RateNotFound):
        exchanger.convert(1, "AAA", "BBB", rates={})
