from typing import Optional

_trace_id = None


def set_trace_id(trace_id: Optional[str]):
    global _trace_id
    _trace_id = trace_id


def get_trace_id() -> Optional[str]:
    return _trace_id
