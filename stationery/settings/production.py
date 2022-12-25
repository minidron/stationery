from .common import INSTALLED_APPS, TEMPLATES

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

INSTALLED_APPS += ['raven.contrib.django.raven_compat']

RAVEN_CONFIG = {
    'dsn': 'http://9fd1d4c4158d467ca1a98c64456761ac:369c2a99e989412b9d585b777ef837fb@sentry.kancmiropt.ru/2',  # NOQA
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'sentry': {
            'level': 'ERROR',
            'class': ('raven.contrib.django.raven_compat.handlers.'
                      'SentryHandler'),
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['sentry'],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'raven': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'stationery': {
            'level': 'ERROR',
            'handlers': ['sentry'],
            'propagate': False,
        },
        'odinass': {
            'level': 'ERROR',
            'handlers': ['sentry'],
            'propagate': False,
        },
        'yandex_money': {
            'level': 'ERROR',
            'handlers': ['sentry'],
            'propagate': False,
        },
    },
}
