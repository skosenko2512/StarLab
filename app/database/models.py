"""
SQLAlchemy ORM models.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class AutoRateOrm(Base):
    """Automatically fetched rate relative to RUB."""

    __tablename__ = "auto_rates"

    currency_code: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    currency_type: Mapped[str] = mapped_column(String(8), nullable=False, unique=True)
    rate_to_rub: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)


class ManualRateOrm(Base):
    """User-specified override for rate relative to RUB."""

    __tablename__ = "manual_rates"

    currency_code: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    currency_type: Mapped[str] = mapped_column(String(8), nullable=False, unique=True)
    rate_to_rub: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)


class MetricsOrm(Base):
    """Stores request latency metrics per endpoint."""

    __tablename__ = "endpoint_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    method: Mapped[str] = mapped_column(String(8), nullable=False)
    path: Mapped[str] = mapped_column(String(128), nullable=False)
    duration_ms: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
