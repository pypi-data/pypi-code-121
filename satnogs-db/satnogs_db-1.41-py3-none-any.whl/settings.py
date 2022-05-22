"""SatNOGS DB Application django settings

For local installation settings please copy .env-dist to .env and edit
the appropriate settings in that file. You should not need to edit this
file for local settings!
"""
from pathlib import Path

import sentry_sdk
from decouple import Csv, config
from dj_database_url import parse as db_url
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from db import __version__

ROOT = Path(__file__).parent

ENVIRONMENT = config('ENVIRONMENT', default='dev')
DEBUG = config('DEBUG', default=True, cast=bool)
AUTH0 = config('AUTH0', default=False, cast=bool)

# Apps
DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)
THIRD_PARTY_APPS = (
    'bootstrap_modal_forms',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'django_countries',
    'django_filters',
    'fontawesomefree',
    'widget_tweaks',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'compressor',
    'csp',
    "corsheaders",
)
LOCAL_APPS = (
    'db.base',
    'db.api',
)

if DEBUG:
    DJANGO_APPS += ('debug_toolbar', )
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: request.environ.get('SERVER_NAME', None) !=  # noqa W504 pylint: disable=C0301
        'testserver',
    }

if AUTH0:
    THIRD_PARTY_APPS += ('social_django', )

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middlware
MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
)

if DEBUG:
    MIDDLEWARE = ('debug_toolbar.middleware.DebugToolbarMiddleware', ) + MIDDLEWARE

# Email
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=300, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@satnogs.org')
ADMINS = [('SatNOGS Admins', DEFAULT_FROM_EMAIL)]
MANAGERS = ADMINS
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Cache
CACHES = {
    'default': {
        'BACKEND': config(
            'CACHE_BACKEND',
            default='django.core.cache.backends.locmem.LocMemCache',
        ),
        'LOCATION': config('CACHE_LOCATION', default='unique-location'),
        'KEY_PREFIX': 'db-{0}'.format(ENVIRONMENT),
    }
}

if CACHES['default']['BACKEND'] == 'django.core.cache.backends.locmem.LocMemCache':
    CACHES['default']['OPTIONS'] = {'MAX_ENTRIES': 5000}

CACHE_TTL = config('CACHE_TTL', default=300, cast=int)

# Internationalization
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            Path(ROOT).joinpath('templates').resolve(),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'db.base.context_processors.analytics', 'db.base.context_processors.stage_notice',
                'db.base.context_processors.auth_block', 'db.base.context_processors.logout_block',
                'db.base.context_processors.version',
                'db.base.context_processors.decoders_version',
                'db.base.context_processors.login_button'
            ],
            'loaders': [
                (
                    'django.template.loaders.cached.Loader', [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ]
                ),
            ],
        },
    },
]

# Static & Media
STATIC_ROOT = config('STATIC_ROOT', default=Path('staticfiles').resolve())
STATIC_URL = config('STATIC_URL', default='/static/')
STATICFILES_DIRS = [
    Path(ROOT).joinpath('static').resolve(),
]
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
MEDIA_ROOT = config('MEDIA_ROOT', default=Path('media').resolve())
FILE_UPLOAD_TEMP_DIR = config('FILE_UPLOAD_TEMP_DIR', default=Path('/tmp').resolve())
FILE_UPLOAD_PERMISSIONS = 0o644
MEDIA_URL = config('MEDIA_URL', default='/media/')
CRISPY_TEMPLATE_PACK = 'bootstrap4'
SATELLITE_DEFAULT_IMAGE = '/static/img/sat_purple.png'
COMPRESS_ENABLED = config('COMPRESS_ENABLED', default=False, cast=bool)
COMPRESS_OFFLINE = config('COMPRESS_OFFLINE', default=False, cast=bool)
COMPRESS_CACHE_BACKEND = config('COMPRESS_CACHE_BACKEND', default='default')
COMPRESS_FILTERS = {
    'css': [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.rCSSMinFilter'
    ],
    'js': ['compressor.filters.jsmin.JSMinFilter']
}

# App conf
ROOT_URLCONF = 'db.urls'
WSGI_APPLICATION = 'db.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Auth
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', )
if AUTH0:
    AUTHENTICATION_BACKENDS += ('social_core.backends.auth0.Auth0OAuth2', )

ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
LOGIN_REDIRECT_URL = 'home'
if AUTH0:
    LOGIN_URL = '/login/auth0'
    LOGOUT_REDIRECT_URL = 'https://' + config('SOCIAL_AUTH_AUTH0_DOMAIN') + \
                          '/v2/logout?returnTo=' + config('SITE_URL')
else:
    LOGIN_URL = 'account_login'
    LOGOUT_REDIRECT_URL = '/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s - %(process)d %(thread)d - %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'db': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
    }
}

# Sentry
SENTRY_ENABLED = config('SENTRY_ENABLED', default=False, cast=bool)
if SENTRY_ENABLED:
    sentry_sdk.init(  # pylint: disable=abstract-class-instantiated
        environment=ENVIRONMENT,
        dsn=config('SENTRY_DSN', default=''),
        release='satnogs-db@{}'.format(__version__),
        integrations=[CeleryIntegration(),
                      DjangoIntegration(),
                      RedisIntegration()]
    )

# Celery
CELERY_ENABLE_UTC = USE_TZ
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_RESULTS_EXPIRES = 3600
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_TASK_ALWAYS_EAGER = False
CELERY_DEFAULT_QUEUE = 'db-{0}-queue'.format(ENVIRONMENT)
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': config('REDIS_VISIBILITY_TIMEOUT', default=604800, cast=int),
    'fanout_prefix': True
}
REDIS_CONNECT_RETRY = True

# API
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend', ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'SCHEMA_PATH_PREFIX': r'/api',
    'DEFAULT_GENERATOR_CLASS': 'drf_spectacular.generators.SchemaGenerator',

    # Configuration for serving the schema with SpectacularAPIView
    'SERVE_URLCONF': None,
    'SERVE_PUBLIC': True,
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],

    # available SwaggerUI configuration parameters
    # https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },

    # we pull swagger-ui in via npm, as opposed to using their cdn
    'SWAGGER_UI_DIST': STATIC_URL + 'lib/swagger-ui-dist',
    'SWAGGER_UI_FAVICON_HREF': STATIC_URL + 'favicon.ico',
    'TITLE': 'SatNOGS DB',
    'DESCRIPTION': 'SatNOGS DB is a crowdsourced database of details about orbital \
                    satellites and data collected from them.',
    'TOS': None,
    'CONTACT': {
        'name': 'SatNOGS Developer Chat',
        'url': 'https://riot.im/app/#/room/#satnogs-dev:matrix.org'
    },
    'LICENSE': {
        'name': 'AGPL 3.0',
        'url': 'https://www.gnu.org/licenses/agpl-3.0.html'
    },
    'VERSION': '1.1',
    'SERVERS': [
        {
            'url': 'https://db-dev.satnogs.org',
            'description': 'Development server'
        }, {
            'url': 'https://db.satnogs.org',
            'description': 'Production server'
        }
    ],
    'PREPROCESSING_HOOKS': [
        'drf_spectacular.hooks.preprocess_exclude_path_format',
        'db.api.drf_spectacular_hooks.exclude_paths_hook'
    ],
    'POSTPROCESSING_HOOKS': ['drf_spectacular.hooks.postprocess_schema_enums'],
    'GET_MOCK_REQUEST': 'drf_spectacular.plumbing.build_mock_request',

    # Tags defined in the global scope
    'TAGS': [
        {
            'name': 'artifacts',
            'description': 'IN DEVELOPMENT (BETA): Artifacts are file-formatted objects \
                            collected from a satellite observation.'
        },
        {
            'name': 'modes',
            'description': 'Radio Frequency modulation modes (RF Modes) currently \
                            tracked in the SatNOGS DB database',
            'externalDocs': {
                'description': 'RF Modes in SatNOGS Wiki',
                'url': 'https://wiki.satnogs.org/Category:RF_Modes',
            }
        },
        {
            'name': 'satellites',
            'description': 'Human-made orbital objects, typically with radio frequency \
                            transmitters and/or reveivers'
        },
        {
            'name': 'telemetry',
            'description': 'Telemetry objects in the SatNOGS DB database are frames of \
                            data collected from downlinked observations.'
        },
        {
            'name': 'tle',
            'description': 'The most recent two-line elements (TLE) in the SatNOGS DB database',
            'externalDocs': {
                'description': 'TLE Wikipedia doc',
                'url': 'https://en.wikipedia.org/wiki/Two-line_element_set',
            }
        },
        {
            'name': 'transmitters',
            'description': 'Radio Frequency (RF) transmitter entities in the SatNOGS DB \
                            database. Transmitters in this case are inclusive of Transceivers \
                            and Transponders'
        },
    ],
    'EXTERNAL_DOCS': {
        'url': 'https://wiki.satnogs.org',
        'description': 'SatNOGS Wiki'
    },
    'COMPONENT_SPLIT_REQUEST': True
}

# Security
SECRET_KEY = config('SECRET_KEY', default='changeme')
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_PROXY_SSL_HEADER = config(
    'SECURE_PROXY_SSL_HEADER', default='', cast=Csv(post_process=tuple)
) or None
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)
CORS_URLS_REGEX = config('CORS_URLS_REGEX', default=r'^(?:/api/artifacts/.*|/media/artifacts/.*)$')
CORS_ALLOW_METHODS = config('CORS_ALLOW_METHODS', default='GET, OPTIONS', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())
CSP_DEFAULT_SRC = config(
    'CSP_DEFAULT_SRC',
    cast=lambda v: tuple(s.strip() for s in v.split(',')),
    default="'self',"
    'https://*.mapbox.com,'
    'https://kit-free.fontawesome.com,'
    'https://ka-f.fontawesome.com,'
    'https://fonts.gstatic.com,'
    "'unsafe-inline'"
)
CSP_SCRIPT_SRC = config(
    'CSP_SCRIPT_SRC',
    cast=lambda v: tuple(s.strip() for s in v.split(',')),
    default="'self',"
    'https://*.google-analytics.com,'
    'https://kit-free.fontawesome.com,'
    'https://kit.fontawesome.com,'
    "'sha256-wMIRCqWVu9YgOwizZzrYvTWAiAn0Y8PQTRdiHy2BNRk=',"  # transmitter_modal.js
)
CSP_IMG_SRC = config(
    'CSP_IMG_SRC',
    cast=lambda v: tuple(s.strip() for s in v.split(',')),
    default="'self',"
    'https://*.gravatar.com,'
    'https://*.mapbox.com,'
    'https://*.google-analytics.com,'
    'data:,'
    'blob:'
)
CSP_FRAME_SRC = config(
    'CSP_FRAME_SRC', cast=lambda v: tuple(s.strip() for s in v.split(',')), default='blob:'
)
CSP_WORKER_SRC = config(
    'CSP_WORKER_SRC',
    cast=lambda v: tuple(s.strip() for s in v.split(',')),
    default="'self',"
    'blob:'
)
CSP_CHILD_SRC = config(
    'CSP_CHILD_SRC', cast=lambda v: tuple(s.strip() for s in v.split(',')), default='blob:'
)

# Database
DATABASE_URL = config('DATABASE_URL', default='sqlite:///db.sqlite3')
DATABASES = {'default': db_url(DATABASE_URL)}

# NETWORK API
NETWORK_API_ENDPOINT = config('NETWORK_API_ENDPOINT', default='https://network.satnogs.org/api/')
DATA_FETCH_DAYS = config('DATA_FETCH_DAYS', default=10, cast=int)

# Mapbox API
MAPBOX_GEOCODE_URL = 'https://api.tiles.mapbox.com/v4/geocode/mapbox.places/'
MAPBOX_TOKEN = config('MAPBOX_TOKEN', default='')

# ZEROMQ
ZEROMQ_ENABLE = config('ZEROMQ_ENABLED', default=False, cast=bool)
ZEROMQ_SOCKET_URI = config('ZEROMQ_SOCKET_URI', default='tcp://127.0.0.1:5555')
ZEROMQ_SOCKET_RCVTIMEO = config(
    'ZEROMQ_SOCKET_RCVTIMEO', default='100', cast=int
)  # Time to wait for subscriber message in ms

# TLE Sources
TLE_SOURCES_REDISTRIBUTABLE = config('TLE_SOURCES_REDISTRIBUTABLE', default='manual', cast=Csv())
TLE_SOURCES_JSON = config('TLE_SOURCES_JSON', default='')
# Comma separated TLE sources name that will be ignored on latest TLE calculations
TLE_SOURCES_IGNORE_FROM_LATEST = config('TLE_SOURCES_IGNORE_FROM_LATEST', default='', cast=Csv())

# SpaceTrack.org Credentials
SPACE_TRACK_USERNAME = config('SPACE_TRACK_USERNAME', default='')
SPACE_TRACK_PASSWORD = config('SPACE_TRACK_PASSWORD', default='')

# Exported Frames
EXPORTED_FRAMESET_TIME_TO_LIVE = config('EXPORTED_FRAMESET_TIME_TO_LIVE', default=21600, cast=int)

# Influx DB for decoded data_id
USE_INFLUX = config('USE_INFLUX', default=False, cast=bool)
INFLUX_HOST = config('INFLUX_HOST', default='localhost')
INFLUX_PORT = config('INFLUX_PORT', default='8086')
INFLUX_USER = config('INFLUX_USER', default='db')
INFLUX_PASS = config('INFLUX_PASS', default='db')
INFLUX_DB = config('INFLUX_DB', default='db')
INFLUX_SSL = config('INFLUX_SSL', default=False, cast=bool)
INFLUX_VERIFY_SSL = config('INFLUX_VERIFY_SSL', default=False, cast=bool)

if AUTH0:
    SOCIAL_AUTH_TRAILING_SLASH = False  # Remove end slash from routes
    SOCIAL_AUTH_AUTH0_DOMAIN = config('SOCIAL_AUTH_AUTH0_DOMAIN', default='YOUR_AUTH0_DOMAIN')
    SOCIAL_AUTH_AUTH0_KEY = config('SOCIAL_AUTH_AUTH0_KEY', default='YOUR_CLIENT_ID')
    SOCIAL_AUTH_AUTH0_SECRET = config('SOCIAL_AUTH_AUTH0_SECRET', default='YOUR_CLIENT_SECRET')
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
    SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', 'first_name', 'last_name']

    SOCIAL_AUTH_PIPELINE = (
        'social_core.pipeline.social_auth.social_details',
        'social_core.pipeline.social_auth.social_uid',
        'social_core.pipeline.social_auth.auth_allowed',
        'social_core.pipeline.social_auth.social_user',
        'social_core.pipeline.social_auth.associate_by_email',
        'social_core.pipeline.user.get_username',
        'social_core.pipeline.user.create_user',
        'social_core.pipeline.social_auth.associate_user',
        'social_core.pipeline.social_auth.load_extra_data',
        'social_core.pipeline.user.user_details',
    )

    SOCIAL_AUTH_AUTH0_SCOPE = [
        'openid',
        'email',
        'profile',
    ]

if ENVIRONMENT == 'dev':
    # Disable template caching
    for backend in TEMPLATES:
        del backend['OPTIONS']['loaders']
        backend['APP_DIRS'] = True

# for h5 artifact uploads
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

# Django 3.2 allows for configurable db keys, we just need auto
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
