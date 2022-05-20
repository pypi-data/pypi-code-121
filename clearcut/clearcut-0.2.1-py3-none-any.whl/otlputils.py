"""
Inits the OTLP framework.

TODO should we use the logger instrumenter?
"""
import asyncio
import os
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Optional

import more_itertools
from opentelemetry import propagate, trace, context
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.propagators.textmap import CarrierT
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Tracer
from opentelemetry.util.types import AttributeValue, Attributes


def init_tracer_provider():
    provider = TracerProvider()
    if "OTEL_EXPORTER_OTLP_ENDPOINT" in os.environ:
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)

    _tracer_provider_inited = True


init_tracer_provider()


def get_tracer(name: str) -> Tracer:
    return trace.get_tracer(name)


def set_attribute(key: str, value: AttributeValue):
    """Set attribute on current span."""
    trace.get_current_span().set_attribute(key, value)


def add_event(name: str, attributes: Attributes = None):
    """Add an event to the current span"""
    trace.get_current_span().add_event(name, attributes)


@contextmanager
def context_from_carrier(headers_carrier: CarrierT):
    """Set up OTEL context, and clear it after exiting block"""
    token = None
    try:
        ctx = propagate.extract(headers_carrier)
        token = context.attach(ctx)
        yield
    finally:
        if token is not None:
            context.detach(token)


def carrier_from_context() -> CarrierT:
    """Return a carrier of the current OTLP context."""
    carrier = {}
    propagate.inject(carrier)
    return carrier


def _get_tracer_for_func(func: Callable):
    """
    Get a tracer for the given function.
    """
    # Get a tracer. Ideally from the function's module...
    tracer: Optional[Tracer] = more_itertools.first([v for v in func.__globals__.values() if isinstance(v, Tracer)], None)

    # ...but otherwise, a new one with the function's module's name.
    if tracer is None:
        tracer = get_tracer(func.__module__)

    return tracer


def spanner(func: Callable):
    """
    Decorator that wraps the function as a span, with the function's name. Can also decorate async def functions (coroutine functions.)
    """

    @wraps(func)
    async def with_span_async(*args, **kwargs):
        span_name = f"{func.__module__}.{func.__name__}"
        tracer = _get_tracer_for_func(func)
        with tracer.start_as_current_span(span_name):
            return await func(*args, **kwargs)

    @wraps(func)
    def with_span_sync(*args, **kwargs):
        span_name = f"{func.__module__}.{func.__name__}"
        tracer = _get_tracer_for_func(func)
        with tracer.start_as_current_span(span_name):
            return func(*args, **kwargs)

    if asyncio.iscoroutinefunction(func):
        return with_span_async
    else:
        return with_span_sync
