import contextlib

import pytest


@contextlib.contextmanager
def _maybe_raises(maybe_exception_class, *args, **kwargs):
    if hasattr(maybe_exception_class, "__traceback__"):
        with pytest.raises(maybe_exception_class, *args, **kwargs) as exc_info:
            yield exc_info
    else:
        yield maybe_exception_class


@pytest.fixture()
def maybe_raises():
    return _maybe_raises
