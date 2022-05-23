import os
import raven
from logging import getLogger
from typing import Collection
from wrapt import wrap_function_wrapper

from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap

from helios.defaults import DEFAULT_HS_API_ENDPOINT
from helios.sentry_instrumentation.src.sentry.package import _instruments
from helios.utils import encode_id_as_hex_string

HS_API_ENDPOINT = os.environ.get('HS_API_ENDPOINT') or DEFAULT_HS_API_ENDPOINT
_LOG = getLogger(__name__)


def has_helios_context(sentry_client):
    if not hasattr(sentry_client, 'context'):
        return False

    context = sentry_client.context
    if not hasattr(context, 'data'):
        return False

    return 'user' in context.data and 'Helios' in context.data['user']


def _instrument():
    def wrap_capture_call(func, instance, args, kwargs):
        span = trace.get_current_span()
        if not span or not span.is_recording():
            return func(*args, **kwargs)

        try:
            trace_id = encode_id_as_hex_string(span.get_span_context().trace_id)
            if 'user' not in instance.context.data:
                instance.context.data['user'] = {}
            instance.context.data['user']['Helios'] = {
                'Trace visualization': f'{HS_API_ENDPOINT}?actionTraceId={trace_id}'
            }
        except Exception as error:
            _LOG.debug('raven instrumentation wrap_capture_call error: %s.', error)

        result = func(*args, **kwargs)
        if has_helios_context(instance):
            del instance.context.data['user']['Helios']

        return result

    wrap_function_wrapper('raven', 'Client.capture', wrap_capture_call)


class RavenInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        _instrument()

    def _uninstrument(self, **kwargs):
        unwrap(raven, 'Client.capture')
