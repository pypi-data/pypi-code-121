import json
from logging import getLogger

from opentelemetry.trace import Span
from opentelemetry.semconv.trace import SpanAttributes

from helios.instrumentation.base import HeliosBaseInstrumentor

_LOG = getLogger(__name__)


class HeliosElasticsearchInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.elasticsearch'
    INSTRUMENTOR_NAME = 'ElasticsearchInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider, request_hook=self.request_hook,
                                           response_hook=self.response_hook)

    def request_hook(self, span: Span, method, url, kwargs):
        try:
            if span and span.is_recording():
                span.set_attribute(SpanAttributes.DB_NAME, 'Elasticsearch')
        except Exception as error:
            _LOG.debug('elasticsearch request instrumentation error: %s.', error)

    def response_hook(self, span: Span, response):
        try:
            if response is None:
                return
            if span and span.is_recording():
                response_str = json.dumps(response)
                HeliosBaseInstrumentor.set_payload_attribute(span, self.DB_QUERY_RESULT_ATTRIBUTE_NAME, response_str)
        except Exception as error:
            _LOG.debug('elasticsearch response instrumentation error: %s.', error)
