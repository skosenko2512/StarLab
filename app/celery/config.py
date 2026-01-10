"""
Celery configuration.
"""

from celery.schedules import crontab

from app.logger import get_logger
from app.settings import settings

logger = get_logger(__name__)


def build_beat_schedule() -> dict:
    """Create beat schedule from cron string in settings."""
    cron_fields = settings.cbr_fetch_cron.split()
    if len(cron_fields) != 5:
        return {}

    minute, hour, day_of_month, month_of_year, day_of_week = cron_fields
    return {
        "fetch-cbr-rates": {
            "task": "fetch_cbr_rates",
            "schedule": crontab(
                minute=minute,
                hour=hour,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                day_of_week=day_of_week,
            ),
        }
    }
