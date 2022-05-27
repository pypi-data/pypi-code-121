import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'supersecretkey'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

BOM_CONFIG = {
    'mouser_api_key': 'fcf41666-3812-4a67-bcb0-ee7548c44a34',
}

# google GoogleOAuth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '449904336434-d4ohvhctp3nmqc2okuddp1jnf7cmfrrb.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '-mba5LA71uF6pGjtuU5IouRC'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = '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'

# For django-money exchange rates
FIXER_ACCESS_KEY = '1a3d87f692c8310e791bfde536f1643e'