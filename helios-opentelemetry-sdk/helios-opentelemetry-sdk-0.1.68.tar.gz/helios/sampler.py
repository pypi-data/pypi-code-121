from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, SamplingResult, Decision
from typing import Optional, Sequence
from opentelemetry.context import Context
from opentelemetry.trace import Link, SpanKind, get_current_span
from opentelemetry.trace.span import TraceState
from opentelemetry.util.types import Attributes
from opentelemetry.baggage import get_baggage
from helios import HeliosTags


class HeliosRatioBasedSampler(TraceIdRatioBased):
    def should_sample(
            self,
            parent_context: Optional["Context"],
            trace_id: int,
            name: str,
            kind: SpanKind = None,
            attributes: Attributes = None,
            links: Sequence["Link"] = None,
            trace_state: "TraceState" = None,
    ) -> SamplingResult:
        try:
            test_baggage = get_baggage(HeliosTags.TEST_TRIGGERED_TRACE, parent_context)
            if test_baggage is not None:
                return SamplingResult(Decision.RECORD_AND_SAMPLE, attributes, trace_state)

            span = get_current_span(parent_context)
            if span and span.get_span_context() and span.get_span_context().trace_flags.sampled:
                return SamplingResult(Decision.RECORD_AND_SAMPLE, attributes, trace_state)

        except Exception:
            # Do nothing
            pass

        return super().should_sample(parent_context, trace_id, name, kind, attributes, links, trace_state)
