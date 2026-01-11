"""
Async database setup for Postgres.
"""

from functools import wraps
from typing import Any, Callable

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.settings import settings


class Base(DeclarativeBase):
    """Base model for SQLAlchemy ORM."""


engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


def provide_session(func: Callable) -> Callable:
    """Inject AsyncSession into a coroutine via kwarg `session`."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async with AsyncSessionFactory() as session:
            return await func(*args, **kwargs, session=session)

    return wrapper
