"""
Base repository classes.
"""

from collections.abc import Sequence
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Base class for repositories."""

    model = None

    @classmethod
    async def base_insert(cls, *, session: AsyncSession, values: dict[str, Any]) -> Any:
        obj = cls.model(**values)
        session.add(obj)
        await session.commit()
        return obj

    @classmethod
    async def get_by_filter(
        cls,
        *,
        session: AsyncSession,
        extra_filters: Sequence | None = None,
        order_by: Sequence | None = None,
        **filters: Any,
    ):
        stmt = select(cls.model).filter_by(**filters)
        if extra_filters:
            stmt = stmt.filter(*extra_filters)
        if order_by:
            stmt = stmt.order_by(*order_by)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def update_by_filter(
        cls,
        *,
        session: AsyncSession,
        values: dict[str, Any],
        extra_filters: Sequence | None = None,
        **filters: Any,
    ) -> None:
        stmt = update(cls.model).filter_by(**filters)
        if extra_filters:
            stmt = stmt.filter(*extra_filters)
        stmt = stmt.values(**values)
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def delete_by_filter(
        cls,
        *,
        session: AsyncSession,
        extra_filters: Sequence | None = None,
        **filters: Any,
    ) -> None:
        stmt = delete(cls.model).filter_by(**filters)
        if extra_filters:
            stmt = stmt.filter(*extra_filters)
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def get_all(cls, session: AsyncSession):
        result = await session.execute(select(cls.model))
        return result.scalars().all()
