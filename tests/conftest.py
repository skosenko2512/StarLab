import json
import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import create_app
from app.redis import RATE_SNAPSHOT_KEY
from tests.tests_fixtures.fixtures import DummySession, FakeRedis


@pytest_asyncio.fixture
async def fake_redis(monkeypatch):
    redis = FakeRedis()
    monkeypatch.setattr("app.redis.get_redis_client", lambda: redis)
    monkeypatch.setattr("app.main.AsyncSessionFactory", lambda: DummySession())

    async def _noop_insert_metric(*args, **kwargs):
        return None

    monkeypatch.setattr("app.database.repositories.metrics_repo.MetricsRepo.insert_metric", _noop_insert_metric)
    return redis


@pytest_asyncio.fixture
async def app(fake_redis):
    return create_app()


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def preload_rates(fake_redis):
    async def _loader(data: dict[str, str]):
        await fake_redis.set(RATE_SNAPSHOT_KEY, json.dumps(data))
        return fake_redis

    return _loader
