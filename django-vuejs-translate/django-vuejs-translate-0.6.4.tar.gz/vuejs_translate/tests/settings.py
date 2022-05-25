from pathlib import Path

from django.utils.translation import ugettext_lazy as _


BASE_DIR = Path('..')
BASE_ROOT = BASE_DIR / '..'

SECRET_KEY = '!SECRET_KEY!'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = True

ROOT_URLCONF = 'vuejs_translate.urls'

INSTALLED_APPS = (
    'vuejs_translate',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
)

MIDDLEWARE = MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            )
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3'
    }
}

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True

SITE_ID = 1

STATIC_URL = '/static/'
STATIC_ROOT = BASE_ROOT / 'static'
MEDIA_URL = '/uploads/'
MEDIA_ROOT = BASE_ROOT / 'uploads'

LANGUAGES = (
    ('en', _("English")),
    ('ru', _("Russian")),
)

LOCALE_PATH = [
    Path(__file__).parent.parent / 'locale'
]
