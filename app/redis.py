"""
Redis client.
"""

from redis.asyncio import Redis

from app.settings import settings

RATE_SNAPSHOT_KEY = "rates:effective"


def get_redis_client() -> Redis:
    """Create Redis client."""
    return Redis.from_url(settings.redis_url, decode_responses=True)
