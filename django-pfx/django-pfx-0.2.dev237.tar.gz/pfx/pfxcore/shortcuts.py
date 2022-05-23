
import logging
import re

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


def f(tmpl, **kwargs):
    return tmpl.format(**kwargs)


def get_object(queryset, related_field=None, **kwargs):
    from .exceptions import ModelNotFoundAPIError, RelatedModelNotFoundAPIError
    try:
        return queryset.get(**kwargs)
    except ObjectDoesNotExist:
        if related_field:
            raise RelatedModelNotFoundAPIError(related_field, queryset.model)
        raise ModelNotFoundAPIError(queryset.model)


def get_pk(obj):
    if isinstance(obj, dict) and 'pk' in obj:
        return obj['pk']
    return obj


def delete_token_cookie(response):
    response.delete_cookie(
            'token', domain=settings.PFX_COOKIE_DOMAIN, samesite='None')
    return response


RE_FALSE = re.compile(r'^(0|false|)$', re.IGNORECASE)


def parse_bool(value):
    return value and not RE_FALSE.match(value)
