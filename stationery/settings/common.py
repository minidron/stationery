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
DEFAULT_DOMAIN = 'https://kancmiropt.ru'

AUTH_USER_MODEL = 'accounts.User'

ADMINS = [
    ('Pavel Alekin', 'minidron@yandex.ru')
]

SERVER_EMAIL = 'no-reply@kancmiropt.ru'

INSTALLED_APPS = [
    'filebrowser',
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
    'logentry_admin',
    'colorful',
    'constance',
    'constance.backends.database',
    'hijack',
    'hijack_admin',
    'compat',
    'password_reset',

    'accounts',
    'cart',
    'odinass',
    'orders',
    'pages',
    'yandex_kassa',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'accounts.middleware.AuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

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
                'pages.context_processors.config',
                'cart.context_processors.cart',
                'pages.context_processors.Vkwidget',
                'pages.context_processors.get_footer_color',
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
    'animate.css#3.5',
    'axios#0.18',
    'bootstrap#3.3',
    'devbridge-autocomplete#1.4',
    'es6-promise#4.2',
    'font-awesome#4.7',
    'ilyabirman-likely#2.3',
    'include-media-export#1.0',
    'include-media#1.4',
    'jquery-ui#1.12',
    'jquery.maskedinput#1.4',
    'js-cookie#2.2.1',
    'normalize-css#7',
    'nouislider#10.1',
    'owl.carousel#2.2',
    'swiper#4.1',
    'vue#2.5',
)

# './manage.py bower_install' - install bower apps
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
                'bower_components/swiper/dist/css/swiper.min.css',
                'bower_components/animate.css/animate.min.css',
                'bower_components/Likely/release/likely.css',
            ),
            'output_filename': 'frontend/css/libs.css',
        },
        'frontend': {
            'source_filenames': (
                'frontend/scss/style.scss',
            ),
            'output_filename': 'frontend/css/style-2022-12-26.css',
        },
        'vue': {
            'source_filenames': (
                'kancmir/dist/css/app.css',
            ),
            'output_filename': 'frontend/css/kancmir-2020-09-20.css',
        },
    },
    'JAVASCRIPT': {
        'libs': {
            'source_filenames': (
                'bower_components/jquery/dist/jquery.min.js',
                'bower_components/nouislider/distribute/nouislider.min.js',
                'bower_components/swiper/dist/js/swiper.min.js',
                'bower_components/jquery.maskedinput/dist/jquery.maskedinput.min.js',  # NOQA
                'bower_components/Likely/release/likely.js',
                'bower_components/js-cookie/src/js.cookie.js',
                'frontend/js/jquery.popmenu.js',
            ),
            'output_filename': 'frontend/js/libs-2022-12-26.js',
        },
        'vuecart': {
            'source_filenames': (
                'bower_components/es6-promise/es6-promise.auto.min.js',
                'bower_components/axios/dist/axios.min.js',
                'bower_components/vue/dist/vue.min.js',
                # 'bower_components/vue/dist/vue.js',

                'orders/frontend/js/cart/modules.js',
                'orders/frontend/js/cart/utils.js',
                'orders/frontend/js/cart/components.js',
                'orders/frontend/js/cart/app.js',
            ),
            'output_filename': 'frontend/js/vuecart-2020-06-03.js',
        },
        'frontend': {
            'source_filenames': (
                'frontend/coffee/script.coffee',
                'frontend/js/select_user_type.js',
            ),
            'output_filename': 'frontend/js/script-2022-12-26.js',
        },
        'vue-vendors': {
            'source_filenames': (
                'kancmir/dist/js/chunk-vendors.js',
            ),
            'output_filename': 'frontend/js/vendors-2021-03-16.js',
        },
        'vue': {
            'source_filenames': (
                'kancmir/dist/js/app.js',
            ),
            'output_filename': 'frontend/js/kancmir-2021-03-16.js',
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


# REST FRAMEWORK SETTINGS -----------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'UNAUTHENTICATED_USER': 'accounts.models.AnonymousUser',
}
# -----------------------------------------------------------------------------


# SITE ------------------------------------------------------------------------
EMAIL_OPT = 'opt@kancmiropt.ru'
EMAIL_PRIVATE = 'opt@kancmiropt.ru'
MPTT_ADMIN_LEVEL_INDENT = 20
# -----------------------------------------------------------------------------


# CELERY ----------------------------------------------------------------------
CELERY_RESULT_BACKEND = 'rpc'
CELERY_TRACK_STARTED = True
CELERY_TIMEZONE = 'Europe/Moscow'
# -----------------------------------------------------------------------------


# CONSTANCE PREFERENCES -------------------------------------------------------
HIJACK_LOGIN_REDIRECT_URL = '/'
HIJACK_LOGOUT_REDIRECT_URL = '/admin/auth/user/'
HIJACK_ALLOW_GET_REQUESTS = True
HIJACK_REGISTER_ADMIN = False
# -----------------------------------------------------------------------------


# CONSTANCE PREFERENCES -------------------------------------------------------
class FileBrowserSiteHack:
    name = 'filebrowser'


FILEBROWSER_DIRECTORY = ''

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_ADDITIONAL_FIELDS = {
    'background_color': ['colorful.forms.RGBColorField', {}],
    'background_repeat': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': (
            ('no-repeat', 'Нет'),
            ('repeat', 'Повторять'),
        )
    }],
    'background_image': ['filebrowser.fields.FileBrowseUploadFormField', {
        'widget': 'filebrowser.fields.FileBrowseUploadWidget',
        'widget_kwargs': {
            'attrs': {
                'site': FileBrowserSiteHack,
            },
        },
        'required': False,
    }],
    'background_attachment': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': (
            ('scroll', 'Нет'),
            ('fixed', 'Фиксированное'),
        )
    }],
}

CONSTANCE_CONFIG = {
    'BACKGROUND_COLOR': ('#f7f7f7', 'Цвет фона', 'background_color'),
    'BACKGROUND_REPEAT': ('no-repeat', 'Заполнение фона', 'background_repeat'),
    'BACKGROUND_IMAGE': ('', 'Изображение', 'background_image'),
    'BACKGROUND_ATTACHMENT': ('scroll', 'Фиксированное изображение',
                              'background_attachment'),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'Фон': ('BACKGROUND_COLOR', 'BACKGROUND_REPEAT', 'BACKGROUND_IMAGE',
            'BACKGROUND_ATTACHMENT'),
}
# -----------------------------------------------------------------------------


# ELASTICSEARCH ---------------------------------------------------------------
INSTALLED_APPS += ['django_elasticsearch_dsl']

ELASTICSEARCH_HOST = 'localhost:9200'
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ELASTICSEARCH_HOST
    },
}
# -----------------------------------------------------------------------------


# YANDEX KASSA ----------------------------------------------------------------
YANDEX_KASSA = {
    'PAYMENT_DEFAULT_METHOD': 'bank_card',
    'PAYMENT_METHOD': [
        'bank_card',  # банковская карта
    ],
}
# -----------------------------------------------------------------------------
