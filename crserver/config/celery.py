from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery(settings.CELERY_APP_NAME, broker=settings.CELERY_BROKER_URL)

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.beat_schedule = {
    'load_daily_exchange_rates': {
        'task': 'api.tasks.load_daily_exchange_rates',
        'schedule': crontab(hour="12"),  # Загрузка в 12:00 мск
        # 'schedule': crontab(),  # каждую минуту
    },
}
