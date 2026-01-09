import os

from celery import Celery


def create_celery_app() -> Celery:
    broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
    result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")

    app = Celery("starlab_rates", broker=broker_url, backend=result_backend)
    app.conf.timezone = os.getenv("CELERY_TIMEZONE", "UTC")
    app.conf.task_default_queue = os.getenv("CELERY_DEFAULT_QUEUE", "rates")
    return app


celery_app = create_celery_app()
