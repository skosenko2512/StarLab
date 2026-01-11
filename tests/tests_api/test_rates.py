import pytest


@pytest.mark.asyncio
async def test_convert_endpoint(monkeypatch, client):
    async def fake_convert_with_snapshot(self, amount, from_currency, to_currency):
        return "200.0000"

    monkeypatch.setattr(
        "app.api.rates_router.Exchanger.convert_with_snapshot", fake_convert_with_snapshot
    )

    payload = {"amount": "200", "from_currency": "USD", "to_currency": "RUB"}

    resp = await client.post("/convert", json=payload)

    assert resp.status_code == 200
    body = resp.json()
    assert body["currency"] == "RUB"
    assert body["amount"] == "200.0000"


@pytest.mark.asyncio
async def test_export_rates_csv(monkeypatch, client):
    async def fake_get_snapshot(self):
        return {"USD": 90.1234, "RUB": 1}

    monkeypatch.setattr("app.api.rates_router.Exchanger.get_snapshot", fake_get_snapshot)

    resp = await client.get("/rates/export")

    assert resp.status_code == 200
    text = resp.text.strip().splitlines()
    assert text[0] == "currency_type,rate_to_rub"
    assert "USD,90.1234" in text


@pytest.mark.asyncio
async def test_set_manual_rates_uses_exchanger(monkeypatch, client):
    called = {}

    async def fake_set_manual_rates(self, rates):
        called["rates"] = rates

    monkeypatch.setattr("app.api.rates_router.Exchanger.set_manual_rates", fake_set_manual_rates)

    payload = {
        "rates": [
            {"currency_code": 978, "currency_type": "EUR", "rate_to_rub": "92.0938"},
        ]
    }
    resp = await client.post("/rates/manual", json=payload)

    assert resp.status_code == 204
    assert called["rates"][0].currency_code == 978


@pytest.mark.asyncio
async def test_delete_manual_rate(monkeypatch, client):
    called = {}

    async def fake_delete(self, code):
        called["code"] = code

    monkeypatch.setattr("app.api.rates_router.Exchanger.delete_manual_rate", fake_delete)

    resp = await client.delete("/rates/manual/999")

    assert resp.status_code == 204
    assert called["code"] == 999
