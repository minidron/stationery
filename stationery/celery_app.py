from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery.settings')

app = Celery('stationery')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'check_import': {
        'task': 'odinass.tasks.check_import',
        'schedule': 60 * 30,  # 30 min.
    },
}
