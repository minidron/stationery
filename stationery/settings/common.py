import os
import sys


TEST = 'test' in sys.argv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def path(*a):
    return os.path.join(BASE_DIR, *a)


# This trick allows to import apps without that prefixes
sys.path.insert(0, path('apps'))
sys.path.insert(0, path('lib'))
sys.path.insert(1, path('.'))


ROOT_URLCONF = 'stationery.urls'
WSGI_APPLICATION = 'stationery.wsgi.application'

ALLOWED_HOSTS = ['www.site.ru']

ADMINS = [
    ('Pavel Alekin', 'minidron@yandex.ru')
]

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.gis',
    'django.contrib.staticfiles',
    'django_extensions',
    'djangobower',
    'pipeline',
    'lib',
    'mptt',
    'odinass',
    'pages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

LOGIN_URL = '/admin/login/'
# -----------------------------------------------------------------------------


# TEMPLATES -------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [path('templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# -----------------------------------------------------------------------------


# INTERNATIONALIZATION --------------------------------------------------------
TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru-ru'
USE_I18N = True
USE_L10N = True
USE_TZ = True
# -----------------------------------------------------------------------------


# STATIC AND MEDIA FILES ------------------------------------------------------
STATICFILES_DIRS = [
    path('static'),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

STATIC_URL = '/static/'
STATIC_ROOT = path('../../static')

MEDIA_URL = '/media/'
MEDIA_ROOT = path('../media')
# -----------------------------------------------------------------------------


# BOWER SETTINGS --------------------------------------------------------------
STATICFILES_FINDERS += (
    'djangobower.finders.BowerFinder',
)

BOWER_COMPONENTS_ROOT = path('static')

BOWER_INSTALLED_APPS = (
    'bootstrap#3.3',
    'font-awesome#4.7',
    'jquery-ui#1.12',
    'magnific-popup#1.1',
    'owl.carousel#2.2',
)

# './manage.py bower_install' - install bower apps
# -----------------------------------------------------------------------------


# REST FRAMEWORK SETTINGS -----------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}
# -----------------------------------------------------------------------------


# PIPELINE SETTINGS -----------------------------------------------------------
STATICFILES_FINDERS += (
    'pipeline.finders.PipelineFinder',
)

PIPELINE = {
    'CSS_COMPRESSOR': None,
    'DISABLE_WRAPPER': True,
    'JS_COMPRESSOR': None,
    'SASS_ARGUMENTS': '--include-path %s' % path('static'),
    'SASS_BINARY': 'sassc',
    'COFFEE_SCRIPT_ARGUMENTS': '-b',
    'STYLESHEETS': {
        'styles': {
            'source_filenames': (
                'scss/styles.scss',
            ),
            'output_filename': 'css/styles.css',
        },
    },
    'JAVASCRIPT': {
        'scripts': {
            'source_filenames': (
                'bower_components/jquery/dist/jquery.min.js',
                'bower_components/bootstrap/dist/js/bootstrap.min.js',
                'bower_components/owl.carousel/dist/owl.carousel.min.js',
                'bower_components/magnific-popup/dist/jquery.magnific-popup.min.js',  # NOQA
                'bower_components/jquery-ui/jquery-ui.min.js',
                'js/common.js',
            ),
            'output_filename': 'js/scripts.js',
        },
    },
    'COMPILERS': (
        'pipeline.compilers.coffee.CoffeeScriptCompiler',
        'pipeline.compilers.sass.SASSCompiler',
    ),
}
# -----------------------------------------------------------------------------


# IPYTHON NOTEBOOK ------------------------------------------------------------
IPYTHON_ARGUMENTS = [
    '--ext', 'django_extensions.management.notebook_extension',
]

NOTEBOOK_ARGUMENTS = [
    '--ip=0.0.0.0',
    '--no-browser',
]
# -----------------------------------------------------------------------------


# SITE ------------------------------------------------------------------------
MPTT_ADMIN_LEVEL_INDENT = 20
# -----------------------------------------------------------------------------
