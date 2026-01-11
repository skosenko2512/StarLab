"""
High-level error handler decorator.
"""

from functools import wraps

from fastapi import HTTPException, status


class RateNotFound(Exception):
    """Raised when currency rate is missing."""


class SnapshotUnavailable(Exception):
    """Raised when no rates snapshot is available."""


def handle_errors(func):
    """Wrap endpoint to convert known errors to HTTP responses."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RateNotFound as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except SnapshotUnavailable as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
            ) from exc
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error.",
            )

    return wrapper
