from .logger import log
from tornado.web import RequestHandler, HTTPError
from json import JSONDecoder, JSONDecodeError
import re


class Service(RequestHandler):

    PATH = r'/*'
    VERBOSE = False

    def __init__(self, application, request, **kwargs):
        """
        Class Service: extends tornado.web.RequestHandler.
        You can add the parameter 'context' to kwargs
        """
        self.context = kwargs.pop('context') if 'context' in kwargs else None
        self.headers = dict()
        self.body = None
        super().__init__(application, request, **kwargs)

    def log_request(self):
        """
        Log given request with level debug.
        If the static parameter VERBOSE is True, this method logs all the data of request
        """
        method = self.request.method
        content_type = self.headers.get('Content-Type') or 'empty'
        content_length = self.headers.get('Content-Length') or 0
        log.debug(f'{method} request to {self.request.path} from [{self.request.remote_ip}]: '
                  f'{content_type} ({content_length} B)')
        if self.VERBOSE:
            log.debug(self.request.body)

    def prepare(self):
        """
        Copy headers in 'self.headers' and parse the body into 'self.body'
        if the content type is 'application/json'
        """
        for header in self.request.headers:
            self.headers[header] = self.request.headers[header]
        self.log_request()
        if (ct := self.headers.get('Content-Type')) is not None and re.match(r'application.+json', ct):
            try:
                self.body = JSONDecoder().decode(self.request.body.decode('utf-8'))
            except JSONDecodeError as exception:
                raise HTTPError(400, exception.msg)

    def write_error(self, status_code: int, **kwargs) -> None:
        """
        Return a custom error body as json
        """
        title = f'{status_code} {self._reason}'
        message = ''
        if (exc_info := kwargs.get("exc_info")) is not None:
            if isinstance(exception := exc_info[1], HTTPError) and exception.log_message:
                if status_code >= 500:
                    log.error(exception)
                else:
                    log.debug(exception)
                message = exception.log_message
        self.finish(dict(
            error=title,
            message=message
        ))

    def data_received(self, chunk: bytes):
        pass
