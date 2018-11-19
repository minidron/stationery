from datetime import datetime

from django.conf import settings
from django.template.loader import render_to_string

from celery import shared_task

import pytz

from lib.email import create_email

from odinass.models import Log, StatusLog
from odinass.utils import ImportManager


@shared_task(name='odinass.tasks.import_file')
def import_file(file_path):
    ImportManager(file_path, logging=True)
    return True


@shared_task(name='odinass.tasks.check_import')
def check_import():
    tz = pytz.timezone(settings.TIME_ZONE)
    now = tz.localize(datetime.now())

    start_at = now.replace(hour=10, minute=0, second=0, microsecond=0)
    end_at = now.replace(hour=22, minute=0, second=0, microsecond=0)

    if start_at < now < end_at:
        try:
            last_success_log = (Log.objects.filter(status=StatusLog.FINISHED)
                                           .latest('created'))
            delta = now - last_success_log.created

            if delta.total_seconds() // 3600 > 3:
                email = create_email(
                    'Ошибка выгрузки на сайт',
                    render_to_string('odinass/email/error_import.html', {
                        'log': last_success_log,
                    }),
                    settings.EMAIL_OPT
                )
                email.send()
        except Log.DoesNotExist:
            pass
