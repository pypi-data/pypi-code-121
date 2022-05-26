from logging import getLogger
from opentelemetry.trace import Span
from typing import List, Optional, Tuple

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor

_LOG = getLogger(__name__)


async def _noop_def():
    # Does nothing. We use it to return an Awaitable from the request / response hook,
    # as the httpx instrumentation expects it this way for async requests.
    pass


class HeliosHttpxInstrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.httpx'
    INSTRUMENTOR_NAME = 'HTTPXClientInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider,
                                           request_hook=self.request_hook,
                                           response_hook=self.response_hook)

    def request_hook(self, span: Span, request):
        try:
            if request.stream is None:
                payload = None
            else:
                payload = request.stream.read().decode('utf-8')

            HeliosBaseHttpInstrumentor.base_request_hook(span, self.parse_headers(request.headers), payload)
            return _noop_def()
        except Exception as error:
            _LOG.debug('httpx request instrumentation error: %s.', error)

    def response_hook(self, span: Span, _request, response):
        try:
            payload = None

            # TODO: Do not extract the response body, as it drains the data and makes it inaccessible later.
            # for member in response.stream:
            #     if payload is None:
            #         payload = member.decode('utf-8')
            #     else:
            #         payload += member.decode('utf-8')

            HeliosBaseHttpInstrumentor.base_response_hook(span, self.parse_headers(response.headers), payload)
            return _noop_def()
        except Exception as error:
            _LOG.debug('httpx response instrumentation error: %s.', error)

    @staticmethod
    def parse_headers(headers: Optional[List[Tuple[bytes, bytes]]]):
        if headers is None:
            return None
        else:
            return {
                key.decode('utf-8') if type(key) == bytes
                else key: value.decode('utf-8') if type(value) == bytes
                else value for key, value in dict(headers).items()
            }
