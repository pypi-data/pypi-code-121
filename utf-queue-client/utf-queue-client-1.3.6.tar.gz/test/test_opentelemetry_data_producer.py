from utf_queue_client.clients.opentelemetry_data_producer import (
    OpenTelemetryDataProducer,
)
from utf_queue_client.utils.queue_span_exporter import (
    QueueSpanExporter,
    QUEUE_SPAN_EXPORTER_TYPE_NAME,
)
from utf_queue_client.exceptions import ValidationError
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    BatchSpanProcessor,
)
from otel_extensions import (
    init_telemetry_provider,
    get_tracer,
    TelemetryOptions,
    flush_telemetry_data,
)
import pytest
import os
from contextlib import contextmanager

@contextmanager
def temporary_environment_variable_setter(var, val):
    prev_val = os.environ.get(var)
    if val is not None:
        os.environ[var] = val
    else:
        if prev_val is not None:
            del os.environ[var]
    try:
        yield
    finally:
        if prev_val is None:
            if val is not None and var in os.environ:
                del os.environ[var]
        else:
            os.environ[var] = prev_val


@pytest.fixture(params=[SimpleSpanProcessor, BatchSpanProcessor])
def queue_tracer_provider(request, amqp_url):
    resource = Resource(attributes={SERVICE_NAME: request.node.name})
    tracer_provider = TracerProvider(resource=resource)
    processor_type = request.param
    processor = processor_type(
        QueueSpanExporter(TelemetryOptions(OTEL_EXPORTER_OTLP_ENDPOINT=amqp_url))
    )
    tracer_provider.add_span_processor(processor)
    yield tracer_provider


def test_data_producer_empty_url():
    with pytest.raises(RuntimeError):
        _ = OpenTelemetryDataProducer()


def test_data_producer_central_queue(
    request,
    amqp_url,
    queue_consumer,
):
    producer = OpenTelemetryDataProducer(
        url=amqp_url, producer_app_id=request.node.name
    )
    producer.publish_telemetry_data("LOGS", b"1234")
    queue_consumer.expect_messages(1)
    producer.publish_telemetry_data("METRICS", b"1234")
    queue_consumer.expect_messages(2)
    producer.publish_telemetry_data("TRACES", b"1234")
    queue_consumer.expect_messages(3)
    with pytest.raises(ValidationError):
        producer.publish_telemetry_data("SOMETHING", b"1234")


def test_queue_span_exporter_direct(
    request, amqp_url, queue_consumer, queue_tracer_provider
):
    for i in range(1, 10):
        with trace.get_tracer(
            __name__, tracer_provider=queue_tracer_provider
        ).start_as_current_span(request.node.name) as span:
            assert span.name == request.node.name
        queue_tracer_provider.force_flush()
        queue_consumer.expect_messages(i)


@pytest.mark.parametrize('compression', [None, "gzip", "deflate"])
def test_queue_span_exporter_indirect(request, amqp_url, queue_consumer, compression):
    with temporary_environment_variable_setter("OTEL_EXPORTER_OTLP_COMPRESSION", compression):
        options = TelemetryOptions(
            OTEL_EXPORTER_OTLP_ENDPOINT=amqp_url,
            OTEL_EXPORTER_OTLP_PROTOCOL="custom",
            OTEL_EXPORTER_CUSTOM_SPAN_EXPORTER_TYPE=QUEUE_SPAN_EXPORTER_TYPE_NAME,
            OTEL_SERVICE_NAME="foo",
            OTEL_PROCESSOR_TYPE="batch",
        )
        init_telemetry_provider(options)
        for i in range(1, 10):
            with get_tracer(__name__, "foo").start_as_current_span(
                request.node.name
            ) as span:
                assert span.name == request.node.name
            flush_telemetry_data()
            queue_consumer.expect_messages(i)

def test_invalid_compression(amqp_url):
    with temporary_environment_variable_setter("OTEL_EXPORTER_OTLP_COMPRESSION", "crap"):
        with pytest.raises(ValueError):
            QueueSpanExporter(TelemetryOptions(OTEL_EXPORTER_OTLP_ENDPOINT=amqp_url))
    with temporary_environment_variable_setter("OTEL_EXPORTER_OTLP_TRACES_COMPRESSION", "crap"):
        with pytest.raises(ValueError):
            QueueSpanExporter(TelemetryOptions(OTEL_EXPORTER_OTLP_ENDPOINT=amqp_url))