"""
API routes for rates operations.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.adapters.schemas import ConvertRequest, ConvertResponse, ManualRatesRequest
from app.domain.exchanger import Exchanger
from app.handlers.errors import handle_errors
from app.redis import get_redis_client

router = APIRouter()


@router.get("/rates/export", tags=["rates"])
@handle_errors
async def export_rates() -> StreamingResponse:
    """Export current rates snapshot as CSV."""
    redis = get_redis_client()
    try:
        exchanger = Exchanger(redis=redis)
        rates = await exchanger.get_snapshot()
        csv_content = exchanger.build_csv(rates)
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename=\"rates.csv\"'},
        )
    finally:
        await redis.close()


@router.post("/convert", response_model=ConvertResponse, tags=["rates"])
@handle_errors
async def convert_currency(payload: ConvertRequest) -> ConvertResponse:
    """Convert amount between currencies using cached rates snapshot."""
    redis = get_redis_client()
    try:
        exchanger = Exchanger(redis=redis)
        result = await exchanger.convert_with_snapshot(
            payload.amount, payload.from_currency, payload.to_currency
        )
        return ConvertResponse(amount=result, currency=payload.to_currency)
    finally:
        await redis.close()


@router.post("/rates/manual", status_code=204, tags=["rates"])
@handle_errors
async def set_manual_rates(payload: ManualRatesRequest) -> None:
    """Create or update manual rates and refresh the snapshot."""
    redis = get_redis_client()
    try:
        exchanger = Exchanger(redis=redis)
        await exchanger.set_manual_rates(payload.rates)
    finally:
        await redis.close()


@router.delete("/rates/manual/{currency_code}", status_code=204, tags=["rates"])
@handle_errors
async def delete_manual_rate_endpoint(currency_code: int) -> None:
    """Remove manual rate override by currency code and refresh the snapshot."""
    redis = get_redis_client()
    try:
        exchanger = Exchanger(redis=redis)
        await exchanger.delete_manual_rate(currency_code)
    finally:
        await redis.close()
