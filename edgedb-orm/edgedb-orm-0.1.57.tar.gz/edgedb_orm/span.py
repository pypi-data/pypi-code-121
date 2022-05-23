import time
from contextlib import contextmanager
import os

PRINT_SPAN = bool(int(os.getenv("_PRINT_SPAN", "0")))

try:
    from sentry_sdk import start_span

    USE_SENTRY = True
except Exception:
    print("could not import sentry_sdk for span")
    USE_SENTRY = False


@contextmanager
def print_span(op: str, description: str = None):
    start = time.time()
    yield
    time_took = time.time() - start
    if PRINT_SPAN:
        print(f"{op=}, {description=} took {time_took*1_000:.2f} ms.")


@contextmanager
def safe_span(op: str, description: str = None, use: bool = True, **kwargs):
    if not USE_SENTRY or not use:
        with print_span(op=op, description=description):
            yield
    else:
        if USE_SENTRY is True:
            with start_span(op=op, description=description, **kwargs):
                yield
