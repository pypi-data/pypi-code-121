"""
Django REST framework handles the following exceptions, and automatically generates error responses:
  - Subclasses of APIException raised inside REST framework,
  - Django's Http404 exception,
  - and Django's PermissionDenied exception.

More info: http://www.django-rest-framework.org/api-guide/exceptions/

We capture them here, and reformat responses to our desired style.
"""
import logging
import json

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from django_on_chain import SETTINGS
from django_on_chain.exceptions import ServiceError

logger = logging.getLogger(__name__)


def reformat_error_handler(e, context):
    if isinstance(e, ServiceError):
        content = {
            'type': e.type,
            'message': e.message,
        }
        if e.errors is not None:
            content['errors'] = e.errors
        return Response(content, status=e.suggested_http_status or status.HTTP_500_INTERNAL_SERVER_ERROR)

    response = exception_handler(e, context)  # Call default exception handler to get the standard error response

    if response is None:
        traceback = e.__traceback__ if hasattr(e, '__traceback__') else None
        logger.error('Uncaught exception', exc_info=(type(e), e, traceback), extra={
            'request': __serialize_request(context['request']),
        })

    reformat_errors = getattr(context.get('view', object()), 'reformat_errors', SETTINGS['REFORMAT_ALL_ERRORS'])

    if not reformat_errors:
        return response

    if response is None:
        return Response({
            'type': 'server_error',
            'message': _('Unknown error; please try again later'),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        message = _('Invalid request')
        if isinstance(e, exceptions.ValidationError):
            message += ': {}'.format(e.detail)
        response.data = {
            'type': 'bad_request',
            'message': message,
        }
    elif response.status_code == status.HTTP_404_NOT_FOUND:
        response.data = {
            'type': 'not_found',
            'message': _('Resource was not found.'),
        }
    elif response.status_code == status.HTTP_401_UNAUTHORIZED:
        response.data = {
            'type': 'unauthorized',
            'message': _('Request is not authorized'),
        }
    elif response.status_code == status.HTTP_403_FORBIDDEN:
        message = _('You do not have permission to perform this action.')
        if isinstance(e, exceptions.APIException):
            message = e.detail
        response.data = {
            'type': 'access_forbidden',
            'message': message,
        }
    elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        response.data = {
            'type': 'too_many_requests',
            'message': _("Too many requests"),
        }
    elif isinstance(e, exceptions.APIException):
        response.data = {
            'type': e.default_code,
            'message': force_text(e.default_detail),
        }

    return response


def __serialize_request(request):
    try:
        result = {
            'scheme': request.scheme,
            'url': request.path,
            'method': request.method,

            'content_type': request.content_type,
            'content_params': request.content_params,

            'GET': {key: values for (key, values) in request.GET.lists()},
            'POST': '',
            'COOKIES': request.COOKIES,
            'META': {key: value for key, value in request.META.items() if key.isupper()},

            'FILES': {
                key: [
                    {
                        'name': f.name,
                        'size': f.size,
                        'content_type': f.content_type,
                    }
                    for f in files
                ]
                for (key, files) in request.FILES.lists()
            },
        }

    except Exception:
        logger.exception('django-on-chain exception while serializing request object')
        result = request

    return result
