import pytest


@pytest.mark.asyncio
async def test_get_metrics(monkeypatch, client):
    dummy = [{"path": "/convert", "method": "POST", "p25": 1.0, "p50": 2.0, "p75": 3.0, "p95": 4.0}]

    async def fake_get_percentiles():
        return dummy

    monkeypatch.setattr("app.api.metrics_router.MetricsRepo.get_percentiles", fake_get_percentiles)

    resp = await client.get("/metrics")

    assert resp.status_code == 200
    assert resp.json() == dummy
