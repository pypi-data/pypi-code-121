import time
from contextlib import contextmanager

# For type hints
from typing import Iterator, Callable


@contextmanager
def eval_latency() -> Iterator[Callable]:
    t_start = time.time()
    timer = lambda: time.time() - t_start
    yield timer
