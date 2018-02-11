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

ALLOWED_HOSTS = ['kancmiropt.ru']

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
    'rest_framework',
    'django_filters',
    'lib',
    'mptt',
    'adminsortable2',
    'ckeditor',
    'sorl.thumbnail',
    'odinass',
    'pages',
    'orders',
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
                'pages.context_processors.menu',
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
    'backbone#1.3',
    'bootstrap#3.3',
    'devbridge-autocomplete#1.4',
    'font-awesome#4.7',
    'include-media#1.4',
    'include-media-export#1.0',
    'jquery-ui#1.12',
    'marionette#3.5',
    'normalize-css#7',
    'nouislider#10.1',
    'owl.carousel#2.2',
    'swiper#4.1',
    'underscore#1.8',
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
        'libs': {
            'source_filenames': (
                'bower_components/normalize-css/normalize.css',
                'bower_components/nouislider/distribute/nouislider.min.css',
            ),
            'output_filename': 'frontend/css/libs.css',
        },
        'frontend': {
            'source_filenames': (
                'frontend/scss/style.scss',
            ),
            'output_filename': 'frontend/css/style.css',
        },
        'styles': {
            'source_filenames': (
                'scss/styles.scss',
            ),
            'output_filename': 'css/styles.css',
        },
    },
    'JAVASCRIPT': {
        'libs': {
            'source_filenames': (
                'bower_components/jquery/dist/jquery.min.js',
                'bower_components/devbridge-autocomplete/dist/jquery.autocomplete.min.js',  # NOQA
                'bower_components/nouislider/distribute/nouislider.min.js',
            ),
            'output_filename': 'frontend/js/libs.js',
        },
        'marionette': {
            'source_filenames': (
                'bower_components/underscore/underscore-min.js',
                'bower_components/backbone/backbone-min.js',
                'bower_components/backbone.radio/build/backbone.radio.min.js',
                'bower_components/backbone.marionette/lib/backbone.marionette.min.js',  # NOQA
            ),
            'output_filename': 'frontend/js/marionette.js',
        },
        'cart': {
            'source_filenames': (
                'orders/frontend/coffee/cart/app.coffee',
                'orders/frontend/coffee/cart/models.coffee',
            ),
            'output_filename': 'frontend/js/cart.js',
        },
        'frontend': {
            'source_filenames': (
                'frontend/coffee/script.coffee',
            ),
            'output_filename': 'frontend/js/script.js',
        },
        'scripts': {
            'source_filenames': (
                'bower_components/jquery/dist/jquery.min.js',
                'bower_components/bootstrap/dist/js/bootstrap.min.js',
                'bower_components/owl.carousel/dist/owl.carousel.min.js',
                'bower_components/magnific-popup/dist/jquery.magnific-popup.min.js',  # NOQA
                'bower_components/jquery-ui/jquery-ui.min.js',
                'bower_components/devbridge-autocomplete/dist/jquery.autocomplete.min.js',  # NOQA
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


# API -------------------------------------------------------------------------
REST_FRAMEWORK = {
    # 'DEFAULT_RENDERER_CLASSES': [
    #     'rest_framework.renderers.JSONRenderer',
    # ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
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


# CELERY ----------------------------------------------------------------------
CELERY_RESULT_BACKEND = 'rpc'
CELERY_TRACK_STARTED = True
# -----------------------------------------------------------------------------
