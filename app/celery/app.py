"""
Celery app.
"""

from celery import Celery

from app.celery.config import build_beat_schedule
from app.handlers.logger import get_logger
from app.settings import settings

logger = get_logger(__name__)


def create_celery_app() -> Celery:
    """Create Celery."""
    app = Celery(
        "starlab_rates",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["app.celery.tasks"],
    )
    app.conf.timezone = settings.celery_timezone
    app.conf.task_default_queue = settings.celery_default_queue

    beat_schedule = build_beat_schedule()
    if beat_schedule:
        app.conf.beat_schedule = beat_schedule
    else:
        logger.warning("Celery beat schedule not set: invalid or empty cron expression.")

    return app


celery_app = create_celery_app()
