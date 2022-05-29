from helios.defaults import DEFAULT_HS_API_ENDPOINT
from helios.instrumentation.base import HeliosBaseInstrumentor
import logging
import json

from opentelemetry.trace import (
    INVALID_SPAN,
    INVALID_SPAN_CONTEXT,
    get_current_span,
)


class HeliosLoggingInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.logging'
    INSTRUMENTOR_NAME = 'LoggingInstrumentor'

    _old_factory = None
    _log_instrumented_indicator = False

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider)

        self._inject_context_to_record_message()

    def uninstrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        if self._old_factory:
            logging.setLogRecordFactory(self._old_factory)
            self._old_factory = None

        self.get_instrumentor().uninstrument(tracer_provider=tracer_provider)

    def _inject_context_to_record_message(self):
        old_factory = logging.getLogRecordFactory()
        self._old_factory = old_factory

        def _mark_instrumentation_indicator(span):
            if not span or not span.is_recording() or self._log_instrumented_indicator:
                return

            span.set_attribute('heliosLogInstrumented', True)
            self._log_instrumented_indicator = True

        def _inject_go_to_helios_url_to_record(record):
            if hasattr(record, 'otelTraceID'):
                record.go_to_helios = f'{DEFAULT_HS_API_ENDPOINT}?actionTraceId={record.otelTraceID}'

        def _inject_context_to_record_msg(record, msg_as_json):
            if 'go_to_helio' not in msg_as_json and hasattr(record, 'go_to_helios'):
                msg_as_json.setdefault('go_to_helios', record.go_to_helios)
            if 'otelServiceName' not in msg_as_json and hasattr(record, 'otelServiceName'):
                msg_as_json.setdefault('otelServiceName', record.otelServiceName)
            if 'otelSpanID' not in msg_as_json and hasattr(record, 'otelSpanID'):
                msg_as_json.setdefault('otelSpanID', record.otelSpanID)
            if 'otelTraceID' not in msg_as_json and hasattr(record, 'otelTraceID'):
                msg_as_json.setdefault('otelTraceID', record.otelTraceID)
            return msg_as_json

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)

            span = get_current_span()
            if span != INVALID_SPAN:
                ctx = span.get_span_context()
                if ctx != INVALID_SPAN_CONTEXT:
                    # noinspection PyBroadException
                    try:
                        _mark_instrumentation_indicator(span)
                        _inject_go_to_helios_url_to_record(record)
                        if type(record.msg) is dict:
                            record.msg = _inject_context_to_record_msg(record, record.msg)
                        elif isinstance(record.msg, str):
                            record.msg = json.dumps(_inject_context_to_record_msg(record, json.loads(record.msg)))
                    except Exception:
                        pass
            return record

        logging.setLogRecordFactory(record_factory)
