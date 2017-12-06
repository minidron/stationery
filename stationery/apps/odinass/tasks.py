import os

from celery import shared_task

from odinass.models import StatusLog, Log
from odinass.utils import ImportManager


@shared_task(name='odinass.tasks.import_file')
def import_file(file_path):
    ImportManager(file_path)
    filename = os.path.basename(file_path)
    log = Log.objects.get(filename=filename)
    log.status = StatusLog.FINISHED
    log.save()
    return True
