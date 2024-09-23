from celery import Celery

from config import app_settings

celery_app = Celery(
    'tasks',
    broker=app_settings.redis_broker,
    backend=app_settings.redis_backend,
)

import tasks  # noqa: F401, E402
