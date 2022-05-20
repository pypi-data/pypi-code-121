import pytest
from celery.exceptions import TimeoutError as CeleryTimeoutError
from concurrent.futures import TimeoutError as ProcessTimeoutError
from ..client import celery
from ..client import process
from .utils import get_result


def test_task_discovery(celery_session_worker):
    future = celery.get_future("abc")
    assert future.status == "PENDING"
    with pytest.raises(CeleryTimeoutError):
        future.get(timeout=1e-8)


def test_task_discovery_local():
    with process.pool_context():
        future = process.get_future("abc")
        assert not future.running()
        with pytest.raises(ProcessTimeoutError):
            get_result(future, timeout=0)
