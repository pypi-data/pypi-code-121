"""This module override some of default django configuration from the global settings."""

from django.conf.global_settings import *

####################
# LDP              #
####################

LDP_RDF_CONTEXT = 'https://cdn.happy-dev.fr/owl/hdcontext.jsonld'

MAX_ACTIVITY_RESCHEDULES = 3
DEFAULT_BACKOFF_FACTOR = 1
DEFAULT_ACTIVITY_DELAY = 3
DEFAULT_REQUEST_TIMEOUT = 10

####################
# CORE             #
####################

# https://en.wikipedia.org/wiki/List_of_tz_zones_by_name (although not all
# systems may support all possibilities). When USE_TZ is True, this is
# interpreted as the default user time zone.
TIME_ZONE = 'UTC'

# If you set this to True, Django will use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Database connection info. If left empty, will default to the dummy backend.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

# List of strings representing installed apps.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangoldp',
    'guardian'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

# Default server url
SITE_URL = 'http://localhost:8000'
BASE_URL = SITE_URL

# Default URL conf
ROOT_URLCONF = 'djangoldp.urls'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = None

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# ETAGS config
USE_ETAGS = True

# Default X-Frame-Options header value
X_FRAME_OPTIONS = 'DENY'

# The Python dotted path to the WSGI application that Django's internal server
# (runserver) will use. If `None`, the return value of
# 'django.core.wsgi.get_wsgi_application' is used, thus preserving the same
# behavior as previous versions of Django. Otherwise this should point to an
# actual WSGI application object.
WSGI_APPLICATION = 'server.wsgi.application'

##############
# MIDDLEWARE #
##############

# List of middleware to use. Order is important; in the request phase, these
# middleware will be applied in the order given, and in the response
# phase the middleware will be applied in reverse order.
MIDDLEWARE = [
    'django_cookies_samesite.middleware.CookiesSameSite',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangoldp.middleware.AllowRequestedCORSMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django_brotli.middleware.BrotliMiddleware'
]

############
# SESSIONS #
############

# Same site policy
DCS_SESSION_COOKIE_SAMESITE = 'none'

##################
# AUTHENTICATION #
##################

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend', 'guardian.backends.ObjectPermissionBackend']

OIDC_ACCESS_CONTROL_ALLOW_HEADERS = 'Content-Type, if-match, accept, authorization, DPoP'

# The minimum number of seconds a password reset link is valid for
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24 * 3

