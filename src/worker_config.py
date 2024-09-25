from celery import Celery
from celery.schedules import crontab

from config import app_settings

CELERY_BEAT_SCHEDULE = {
    'delete-old-users-every-hour': {
        'task': 'tasks.delete_unregistered_users.delete_unregistered_users',
        'schedule': crontab(minute=0, hour='*/1'),
    },
}

celery_app = Celery(
    'tasks',
    broker=app_settings.redis_broker,
    backend=app_settings.redis_backend,
)
celery_app.conf.update(
    timezone='UTC',
    enable_utc=True,
    beat_schedule=CELERY_BEAT_SCHEDULE,
)

import tasks  # noqa: F401, E402
