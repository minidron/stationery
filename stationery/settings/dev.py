from .common import INSTALLED_APPS, MIDDLEWARE, TEMPLATES, TEST

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
YANDEX_MONEY_DEBUG = DEBUG


# DJANGO DEBUG TOOLBAR --------------------------------------------------------
INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
# -----------------------------------------------------------------------------


# LOGGING ---------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(module)s: %(message)s'
        },
    },
    'require_debug_true': {
        '()': 'django.utils.log.RequireDebugTrue',
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'stationery': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
# -----------------------------------------------------------------------------


if TEST:
    # Радикально ускоряет фабрики пользователей.
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

    INSTALLED_APPS += (
        'django_nose',
    )
