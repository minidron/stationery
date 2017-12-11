import os

from django.conf import settings as django_settings


ODINASS = {
    'DELETE_FILES_AFTER_IMPORT': True,
    'EXPORT_FILE_LIMIT': 0,
    'IMPORT_FILE_LIMIT': 100000,
    'UPLOAD_ROOT': '1c_tmp',
    'USE_ZIP': False,
}


class AppSettings(object):
    DELETE_FILES_AFTER_IMPORT = getattr(
        django_settings, 'DELETE_FILES_AFTER_IMPORT',
        ODINASS['DELETE_FILES_AFTER_IMPORT'])

    EXPORT_FILE_LIMIT = getattr(
        django_settings,
        '1C_EXPORT_FILE_LIMIT',
        ODINASS['EXPORT_FILE_LIMIT'])

    IMPORT_FILE_LIMIT = getattr(
        django_settings,
        '1C_IMPORT_FILE_LIMIT',
        ODINASS['IMPORT_FILE_LIMIT'])

    UPLOAD_ROOT = getattr(
        django_settings,
        '1C_UPLOAD_ROOT',
        os.path.join(django_settings.MEDIA_ROOT, ODINASS['UPLOAD_ROOT']))

    USE_ZIP = getattr(
        django_settings,
        '1C_USE_ZIP',
        ODINASS['USE_ZIP'])


settings = AppSettings()
