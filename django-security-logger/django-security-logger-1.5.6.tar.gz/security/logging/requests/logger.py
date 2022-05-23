from urllib.parse import urlparse

from django.template.defaultfilters import truncatechars
from django.urls.exceptions import Resolver404
from django.urls import resolve
from django.utils.timezone import now

from ipware.ip import get_client_ip

from security.enums import LoggerName
from security.config import settings
from security.backends.signals import (
    input_request_started, input_request_finished, input_request_error,
    output_request_started, output_request_finished, output_request_error,
)
from security.logging.common import SecurityLogger

from .utils import clean_headers, clean_queries, clean_body


class InputRequestLogger(SecurityLogger):

    logger_name = LoggerName.INPUT_REQUEST

    def __init__(self, hide_request_body=False, request_headers=None, request_body=None, user_id=None, method=None,
                 host=None, path=None, queries=None, is_secure=None, ip=None, view_slug=None, response_body=None,
                 response_code=None, response_headers=None, **kwargs):
        super().__init__(**kwargs)
        self._hide_request_body = hide_request_body
        self.request_headers = request_headers
        self.request_body = request_body
        self.user_id = user_id
        self.method = method
        self.host = host
        self.path = path
        self.queries = queries
        self.is_secure = is_secure
        self.ip = ip
        self.view_slug = view_slug
        self.response_body = response_body
        self.response_code = response_code
        self.response_headers = response_headers

    def log_request(self, request):
        try:
            view_slug = resolve(request.path_info, getattr(request, 'urlconf', None)).view_name
        except Resolver404:
            view_slug = None

        self.request_headers = clean_headers(request.headers)
        self.request_body = (
            settings.SENSITIVE_DATA_REPLACEMENT
            if request.body and self._hide_request_body
            else clean_body(request.body, settings.LOG_REQUEST_BODY_LENGTH)
        )
        self.user_id = request.user.pk if hasattr(request, 'user') and request.user.is_authenticated else None
        self.method = request.method.upper()[:7]
        self.host = request.get_host()
        self.path = truncatechars(request.path, 200)
        self.queries = clean_queries(request.GET.dict())
        self.is_secure = request.is_secure()
        self.ip = get_client_ip(request)[0]
        self.start = now()
        self.view_slug = view_slug
        input_request_started.send(sender=InputRequestLogger, logger=self)

    def log_response(self, request, response):
        if (not response.streaming
                and (settings.LOG_RESPONSE_BODY_CONTENT_TYPES is None
                     or response.get('content-type', '').split(';')[0] in settings.LOG_RESPONSE_BODY_CONTENT_TYPES)):
            self.response_body = clean_body(response.content, settings.LOG_RESPONSE_BODY_LENGTH)
        else:
            self.response_body = None

        self.stop = now()
        self.response_code = response.status_code
        self.response_headers = clean_headers(dict(response.items()))
        self.user_id = request.user.pk if hasattr(request, 'user') and request.user.is_authenticated else None
        input_request_finished.send(sender=InputRequestLogger, logger=self)

    def log_exception(self, ex_tb):
        self.error_message = ex_tb
        input_request_error.send(sender=InputRequestLogger, logger=self)


class OutputRequestLogger(SecurityLogger):

    logger_name = LoggerName.OUTPUT_REQUEST

    def __init__(self, request_headers=None, request_body=None, method=None, host=None, path=None, queries=None,
                 is_secure=None, response_body=None, response_code=None, response_headers=None, **kwargs):
        super().__init__(**kwargs)
        self.request_headers = request_headers
        self.request_body = request_body
        self.method = method
        self.host = host
        self.path = path
        self.queries = queries
        self.is_secure = is_secure
        self.response_body = response_body
        self.response_code = response_code
        self.response_headers = response_headers

    def log_request(self, request):
        from .utils import get_logged_params

        parsed_url = urlparse(request.url)
        self.is_secure = parsed_url.scheme == 'https'
        self.host = parsed_url.netloc
        self.path = parsed_url.path
        self.method = request.method.upper()[:7]
        self.queries = clean_queries(get_logged_params(request.url))
        self.start = now()
        self.request_headers = clean_headers(dict(request.headers.items()))
        self.request_body = clean_body(request.body, settings.LOG_REQUEST_BODY_LENGTH)
        output_request_started.send(sender=OutputRequestLogger, logger=self)

    def log_response(self, response):
        self.stop = now()
        self.response_code = response.status_code
        self.response_headers = clean_headers(dict(response.headers.items()))
        self.response_body = clean_body(response.content, settings.LOG_RESPONSE_BODY_LENGTH)
        output_request_finished.send(sender=OutputRequestLogger, logger=self)

    def log_exception(self, ex_tb):
        self.error_message = ex_tb
        self.stop = now()
        output_request_error.send(sender=InputRequestLogger, logger=self)
