import os

from django.conf import (
    settings,
)
from django.core.exceptions import (
    ImproperlyConfigured,
)
from django.db.utils import (
    DEFAULT_DB_ALIAS,
)


DATABASE_ALIAS = getattr(settings, 'GAR_DATABASE_ALIAS', DEFAULT_DB_ALIAS)

if DATABASE_ALIAS not in settings.DATABASES:
    raise ImproperlyConfigured(f'GAR: database alias `{DATABASE_ALIAS}` was not found in DATABASES')
elif DATABASE_ALIAS != DEFAULT_DB_ALIAS and 'm3_gar.routers.GARRouter' not in settings.DATABASE_ROUTERS:
    raise ImproperlyConfigured(
        'GAR: to use external database add `m3_gar.routers.GARRouter` '
        'into `DATABASE_ROUTERS` list in your settings.py'
    )

SUGGEST_BACKEND = getattr(settings, 'GAR_SUGGEST_BACKEND', 'gar.suggest.backends.noop')
SUGGEST_VIEW = getattr(settings, 'GAR_SUGGEST_VIEW', 'gar:suggest')
SUGGEST_AREA_VIEW = getattr(settings, 'GAR_SUGGEST_AREA_VIEW', 'gar:suggest-area')

# SUDS Proxy Support
_http_proxy = os.environ.get('http_proxy')
_https_proxy = os.environ.get('https_proxy')

PROXY = {}
if _http_proxy:
    PROXY['http'] = _http_proxy
if _https_proxy:
    PROXY['https'] = _https_proxy
