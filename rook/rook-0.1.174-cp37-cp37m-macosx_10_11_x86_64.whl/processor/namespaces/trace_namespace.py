from .namespace import Namespace
from .container_namespace import ContainerNamespace
from rook.logger import logger
from .python_object_namespace import PythonObjectNamespace

SPAN_ATTRIBUTES = [ 'tags',
                    'metrics',
                    'service',
                    'name',
                    'resource',
                    'span_id',
                    'trace_id',
                    'parent_id',
                    '_parent',
                    'meta',
                    'error',
                    'metrics',
                    'span_type',
                    'start_ns',
                    'duration_ns',
                    'duration',
                    'operation_name',
                    'finished',
                    'context',
                    '_context',
                    'start_ns',
                    'start_time',
                    'end_time',
                    'type']


class TraceNamespace(Namespace):
    def __init__(self):
        super(TraceNamespace, self).__init__(self.METHODS)
        self.span = None

    def dump(self, args):
        if not self._load():
            return PythonObjectNamespace("Could not fetch span")

        # Check if its jaeger span since jaeger span implement variant like tags
        if self.is_jaeger_span(self.span):
            return self.dump_jaeger_span(self.span)

        return self.dump_generic_span(self.span)

    def read_attribute(self, name):
        if not self._load():
            return PythonObjectNamespace("Could not fetch span")

        if name == 'span':
            return PythonObjectNamespace(self.span)

        if hasattr(self.span, name):
            return PythonObjectNamespace(getattr(self.span, name))

        # TODO::FUTURE throw the exception
        # raise RookAttributeNotFound(name)
        logger.debug("Attribute Not Found %s", name)
        return PythonObjectNamespace(None)

    def _load(self):
        if self.span is not None:
            return True

        try_generic_opentrace = True
        try:
            # Try to fetch ddtrace first since if this will work - opentracing.tracer.active_span will work as well
            # but won't return the right span
            import ddtrace
            self.span = ddtrace.tracer.get_call_context().get_current_span()

            if self.span:
                try_generic_opentrace = False

        except ImportError:
            pass # We'll try the generic opentrace next

        if try_generic_opentrace:
            try:
                import opentracing
                self.span = opentracing.tracer.active_span
            except ImportError:
                pass

            if not self.span:
                try:
                    from opentelemetry import trace
                    self.span = trace.get_current_span()
                except ImportError:
                    return False

        if self.span:
            return True
        return False

    @staticmethod
    def is_jaeger_span(span):
        try:
            import jaeger_client
            return isinstance(span, jaeger_client.span.Span)
        except Exception:
            pass
        return False

    @staticmethod
    def dump_jaeger_span(span):
        jaeger_tags = {}

        for tag in span.tags:
            # I do not filter keys in the sdk - the fe will parse it later.
            key = tag.key
            value = None
            if tag.vType == 0:
                value = tag.vStr
            elif tag.vType == 1:
                value = tag.vDouble
            elif tag.vType == 2:
                value = tag.vBool
            elif tag.vType == 3:
                value = tag.vLong
            elif tag.vType == 4:
                value = tag.vBinary
            jaeger_tags[key] = value

        return ContainerNamespace(
            {
                "tags": PythonObjectNamespace(jaeger_tags),
                "span_id": PythonObjectNamespace(span.span_id),
                "parent_id": PythonObjectNamespace(span.parent_id),
                "operation_name": PythonObjectNamespace(span.operation_name),
                "finished": PythonObjectNamespace(span.finished),
                "start_time": PythonObjectNamespace(span.start_time),
                "end_time": PythonObjectNamespace(span.end_time),
                "context": PythonObjectNamespace(span.context),
            }
        )

    @staticmethod
    def get_span_attribute(span, attr):
        if hasattr(span, attr):
            return PythonObjectNamespace(getattr(span, attr),
                                         PythonObjectNamespace.ObjectDumpConfig.tolerant_limits(None))

        return PythonObjectNamespace(None)

    @staticmethod
    def dump_generic_span(span):
        attributes = {}
        for attribute in SPAN_ATTRIBUTES:
            attributes[attribute] = TraceNamespace.get_span_attribute(span, attribute)

        return ContainerNamespace(attributes)

    METHODS = (dump, )
