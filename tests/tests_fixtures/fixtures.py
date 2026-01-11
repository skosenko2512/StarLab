import json


class FakeRedis:
    """Minimal async Redis stub for tests."""

    def __init__(self):
        self._store: dict[str, str] = {}

    async def get(self, key: str):
        return self._store.get(key)

    async def set(self, key: str, value: str):
        if not isinstance(value, str):
            value = json.dumps(value)
        self._store[key] = value

    async def close(self):
        return None


class DummySession:
    """Async context manager stub for DB session."""

    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeRow:
    """Simple row-like object for repo stubs."""

    def __init__(self, currency_type: str, rate_to_rub):
        self.currency_type = currency_type
        self.rate_to_rub = rate_to_rub
