import itertools
from collections import deque


def to_string(obj):
    """Convert input to string"""
    if isinstance(obj, str):
        pass
    elif isinstance(obj, bytes):
        obj = obj.decode()
    
    return obj


def advance(iterator, n):
    """Advance ``iterator`` cursor by ``n`` step. If ``n`` is none, advance entirely."""
    deque(itertools.islice(iterator, n), maxlen=0)