import pytest

from app.celery import tasks
from app.services.cbr_client import RateRecord
from tests.tests_fixtures.fixtures import DummySession


@pytest.mark.asyncio
async def test_celery_fetch_and_refresh(monkeypatch):
    rates = [RateRecord(currency_code=840, currency_type="USD", rate_to_rub=1)]

    async def fake_fetch_rates(self):
        return rates

    called = {"upsert": False, "rebuild": False}

    async def fake_upsert(session, data):
        called["upsert"] = data is rates

    async def fake_rebuild(self, session=None):
        called["rebuild"] = True

    monkeypatch.setattr("app.celery.tasks.CbrClient.fetch_rates", fake_fetch_rates)
    monkeypatch.setattr("app.celery.tasks.AutoRateRepo.upsert_rates", fake_upsert)
    monkeypatch.setattr("app.celery.tasks.Exchanger.rebuild_snapshot", fake_rebuild)
    class _RedisStub:
        async def close(self):
            return None

    fake_redis = _RedisStub()
    monkeypatch.setattr("app.celery.tasks.get_redis_client", lambda: fake_redis)

    await tasks._fetch_and_refresh.__wrapped__(session=DummySession())  # type: ignore[attr-defined]

    assert called["upsert"]
    assert called["rebuild"]
