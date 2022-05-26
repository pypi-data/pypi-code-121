import os

from typing import Dict, Optional
from logging import getLogger

import requests

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.exporter.otlp.proto.http import Compression
from opentelemetry.exporter.otlp.proto.http.trace_exporter.encoder import (
    _ProtobufEncoder,
)

_LOG = getLogger(__name__)


class ForkProcessOTLPSpanExporter(OTLPSpanExporter):
    def __init__(
            self,
            endpoint: Optional[str] = None,
            certificate_file: Optional[str] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            compression: Optional[Compression] = None,
    ):
        self.process_id = os.getpid()
        super().__init__(endpoint, certificate_file, headers, timeout, compression)

    def export(self, spans) -> SpanExportResult:
        try:
            curr_process_id = os.getpid()
            if self.process_id != curr_process_id:
                _LOG.info('restarting Session object')
                self.process_id = curr_process_id
                self.init_session()
        except Exception as err:
            _LOG.error('error restarting Session object', err)
        return super().export(spans)

    def init_session(self):
        self._session = requests.Session()
        self._session.headers.update(self._headers)
        self._session.headers.update(
            {"Content-Type": _ProtobufEncoder._CONTENT_TYPE}
        )
        if self._compression is not Compression.NoCompression:
            self._session.headers.update(
                {"Content-Encoding": self._compression.value}
            )
