"""
Pydantic schemas for API.
"""

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


DecimalAmount = Annotated[Decimal, Field(gt=0)]  # type: ignore[arg-type]
CurrencyType = Annotated[str, Field(min_length=3, max_length=3)]


class ConvertRequest(BaseModel):
    """Request model for currency conversion."""

    amount: DecimalAmount
    from_currency: CurrencyType
    to_currency: CurrencyType


class ConvertResponse(BaseModel):
    """Response model for currency conversion."""

    amount: Decimal
    currency: CurrencyType


class ManualRate(BaseModel):
    """Manual rate input model."""

    currency_code: int
    currency_type: CurrencyType
    rate_to_rub: DecimalAmount


class ManualRatesRequest(BaseModel):
    """Request model for manual rates bulk update."""

    rates: list[ManualRate]


class ExportRate(BaseModel):
    """Export model for rates."""

    currency_type: CurrencyType
    rate_to_rub: Decimal
