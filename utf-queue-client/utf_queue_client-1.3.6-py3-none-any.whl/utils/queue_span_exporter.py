import os

from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.exporter.otlp.proto.http import Compression
from utf_queue_client.clients.opentelemetry_data_producer import (
    OpenTelemetryDataProducer,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter.encoder import (
    _ProtobufEncoder,
)
from opentelemetry.sdk.trace import ReadableSpan
from otel_extensions import TelemetryOptions
import typing
import gzip
from io import BytesIO
import zlib

__all__ = ["QUEUE_SPAN_EXPORTER_TYPE_NAME", "QueueSpanExporter"]

QUEUE_SPAN_EXPORTER_TYPE_NAME = (
    "utf_queue_client.utils.queue_span_exporter.QueueSpanExporter"
)


class QueueSpanExporter(SpanExporter):
    def __init__(self, options: TelemetryOptions):
        self.producer = OpenTelemetryDataProducer(
            url=options.OTEL_EXPORTER_OTLP_ENDPOINT, producer_app_id="QueueSpanExporter"
        )
        self.compression = os.environ.get(
            "OTEL_EXPORTER_OTLP_COMPRESSION"
        ) or os.environ.get("OTEL_EXPORTER_OTLP_TRACES_COMPRESSION")
        if self.compression and self.compression not in [
            Compression.Gzip.value,
            Compression.Deflate.value,
        ]:
            raise ValueError(
                "Invalid value for OTEL_EXPORTER_OTLP_COMPRESSION/OTEL_EXPORTER_OTLP_TRACES_COMPRESSION"
            )

    def export(self, spans: typing.Sequence[ReadableSpan]) -> "SpanExportResult":
        """Exports a batch of telemetry data.

        Args:
            spans: The list of `opentelemetry.trace.Span` objects to be exported

        Returns:
            The result of the export
        """
        serialized_data = _ProtobufEncoder.serialize(spans)  # noqa
        data = serialized_data
        if isinstance(serialized_data, str):
            data = data.encode()
        if self.compression == Compression.Gzip.value:
            gzip_data = BytesIO()
            with gzip.GzipFile(fileobj=gzip_data, mode="w") as gzip_stream:
                gzip_stream.write(serialized_data)
            data = gzip_data.getvalue()
        elif self.compression == Compression.Deflate.value:
            data = zlib.compress(bytes(serialized_data))
        try:
            self.producer.publish_telemetry_data("TRACES", data, self.compression)
            return SpanExportResult.SUCCESS
        except Exception:
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
