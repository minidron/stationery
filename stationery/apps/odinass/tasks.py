from celery import shared_task

from odinass.utils import ImportManager


@shared_task(name='odinass.tasks.import_file')
def import_file(file_path):
    ImportManager(file_path)
    return True
