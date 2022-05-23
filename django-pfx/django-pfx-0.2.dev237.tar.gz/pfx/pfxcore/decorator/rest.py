import logging

from django.utils.translation import gettext_lazy as _

from django_request_mapping import request_mapping

from pfx.pfxcore.exceptions import APIError
from pfx.pfxcore.http import JsonResponse

logger = logging.getLogger(__name__)


def pfx_api(public=None):
    def decorator(func):
        def wrapper(self, request, *args, **kwargs):
            self.request = request
            self.kwargs = kwargs
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("")
                logger.debug("##### REQUEST %s #####", request)
                logger.debug("")
            try:
                self.check_perm(public, func.__name__, *args, **kwargs)
                return func(self, *args, **kwargs)
            except APIError as e:
                return e.response
            except Exception as e:
                logger.exception(e)
                return JsonResponse(dict(message=_(
                    "An internal server error occured.")), status=500)
        return wrapper
    return decorator


def rest_api(*dec_args, public=None, **dec_kwargs):
    _request_mapping = request_mapping(*dec_args, **dec_kwargs)
    _pfx_api = pfx_api(public=public)

    def decorator(func):
        return _request_mapping(_pfx_api(func))
    return decorator


def rest_property(string=None, type="CharField"):
    def decorator(func):
        func.short_description = string
        func.field_type = type
        return property(func)
    return decorator


def pfx_api_view():
    def decorator(cls):
        return cls
    return decorator


def rest_view(*dec_args, **dec_kwargs):
    _request_mapping = request_mapping(*dec_args, **dec_kwargs)
    _pfx_api_view = pfx_api_view()

    def decorator(cls):
        return _request_mapping(_pfx_api_view(cls))
    return decorator
