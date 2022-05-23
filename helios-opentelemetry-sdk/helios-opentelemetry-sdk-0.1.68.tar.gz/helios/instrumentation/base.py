import importlib
import os
from logging import getLogger
from typing import Optional

from opentelemetry.trace import Span
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

_LOG = getLogger(__name__)


class HeliosBaseInstrumentor(object):

    MAX_PAYLOAD_SIZE = os.environ.get('HS_MAX_PAYLOAD_SIZE', 65536)
    DB_QUERY_RESULT_ATTRIBUTE_NAME = "db.query_result"

    def __init__(self, module_name: str, class_name: str):
        self._instrumentor = self.init_instrumentor(module_name, class_name)

    @staticmethod
    def init_instrumentor(module_name: str, class_name: str) -> Optional[BaseInstrumentor]:
        instrumentor = HeliosBaseInstrumentor.import_attribute(module_name, class_name)
        if instrumentor is not None:
            return instrumentor()
        else:
            _LOG.debug(f'class {class_name} was not found in module {module_name}')
            return None

    def get_instrumentor(self):
        return self._instrumentor

    def uninstrument(self):
        if self._instrumentor:
            self._instrumentor.uninstrument()

    @staticmethod
    def import_attribute(module_name: str, attribute_name: str):
        try:
            mod = importlib.import_module(module_name)
            return getattr(mod, attribute_name, None)
        except Exception as err:
            _LOG.debug(err)
            return None

    @staticmethod
    def should_drop_payload_by_length(content_length: int) -> bool:
        if HeliosBaseInstrumentor.MAX_PAYLOAD_SIZE == '-1':
            return False
        return content_length is not None and content_length > int(HeliosBaseInstrumentor.MAX_PAYLOAD_SIZE)

    @staticmethod
    def byte_size(i: any) -> Optional[int]:
        try:
            if isinstance(i, bytearray):
                return len(bytes(i))
            if isinstance(i, bytes):
                return len(i)
            return len(str.encode(str(i)))
        except Exception as err:
            _LOG.debug(err)
        return None

    @staticmethod
    def set_payload_attribute(span: Span, attribute: str, payload: any, payload_size=None):
        if payload:
            if HeliosBaseInstrumentor.should_drop_payload_by_length(payload_size or HeliosBaseInstrumentor.byte_size(payload)):
                span.set_attribute(attribute + '.dropped', True)
            else:
                span.set_attribute(attribute, payload)
