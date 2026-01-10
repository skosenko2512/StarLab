"""
CBR client.
"""

from dataclasses import dataclass
from decimal import Decimal
from xml.etree import ElementTree

import httpx

from app.settings import settings


@dataclass(slots=True)
class RateRecord:
    currency_code: int
    currency_type: str
    rate_to_rub: Decimal


class CbrClient:
    """Client for fetching currency rates from cbr.ru."""

    def __init__(self, url: str | None = None):
        self.url = url or settings.cbr_rates_url

    @staticmethod
    def _parse_rate(value_text: str, nominal_text: str) -> Decimal:
        value = Decimal(value_text.replace(",", "."))
        nominal = Decimal(nominal_text.replace(",", "."))
        return value / nominal

    def parse_xml(self, xml_text: str) -> list[RateRecord]:
        root = ElementTree.fromstring(xml_text)
        records: list[RateRecord] = []

        for valute in root.findall("Valute"):
            num_code_text = valute.findtext("NumCode")
            char_code = valute.findtext("CharCode")
            nominal_text = valute.findtext("Nominal")
            value_text = valute.findtext("Value")
            if not (num_code_text and char_code and nominal_text and value_text):
                continue
            records.append(
                RateRecord(
                    currency_code=int(num_code_text),
                    currency_type=char_code,
                    rate_to_rub=self._parse_rate(value_text, nominal_text),
                )
            )

        records.append(RateRecord(currency_code=643, currency_type="RUB", rate_to_rub=Decimal("1")))
        return records

    async def _fetch_raw_xml(self, client: httpx.AsyncClient) -> str:
        resp = await client.get(self.url, timeout=10)
        resp.raise_for_status()
        return resp.text

    async def fetch_rates(self) -> list[RateRecord]:
        async with httpx.AsyncClient() as client:
            xml_text = await self._fetch_raw_xml(client)
        return self.parse_xml(xml_text)
