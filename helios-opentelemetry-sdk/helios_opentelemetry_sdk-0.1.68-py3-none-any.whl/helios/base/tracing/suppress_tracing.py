from opentelemetry.context import (
    _SUPPRESS_INSTRUMENTATION_KEY,
    attach,
    detach,
    set_value,
    get_value
)


class SuppressTracing:
    @staticmethod
    def is_tracing_suppressed():
        return get_value(_SUPPRESS_INSTRUMENTATION_KEY) is True

    def __enter__(self):
        self.token = attach(set_value(_SUPPRESS_INSTRUMENTATION_KEY, True))

    def __exit__(self, exc_type, exc_val, exc_tb):
        detach(self.token)
