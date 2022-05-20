import time
import logging
import pytest
from concurrent.futures import CancelledError
from celery.exceptions import TaskRevokedError
from ewokscore import events
from ..client import celery
from ..client import process

logger = logging.getLogger(__name__)


def test_cancel(celery_session_worker):
    try:
        assert_normal(celery)
    finally:
        events.cleanup()
    try:
        assert_cancel(celery)
    finally:
        events.cleanup()


def test_cancel_local():
    with process.pool_context():
        assert_normal(process)
        assert_cancel(process)


def assert_normal(mod):
    future = mod.submit_test(1)
    if mod is process:
        wait_running(mod, {future.task_id})
    else:
        logger.warning("memory and sqlite does not allow task monitoring")
    results = mod.get_result(future.task_id)
    assert results == {"return_value": None}
    if mod is process:
        del future
    wait_running(mod, set())


def assert_cancel(mod):
    future = mod.submit_test(1)
    mod.cancel(future.task_id)
    if mod is process:
        with pytest.raises(CancelledError):
            future.result(timeout=2)
        del future
    else:
        try:
            future.get(timeout=2)
        except TaskRevokedError:
            pass
        except Exception as e:
            if future.status == "SUCCESS":
                pytest.xfail("the task sometimes finishes")
            raise AssertionError(f"Task {future.task_id} {future.status}") from e

    wait_running(mod, set())


def wait_running(mod, expected, timeout=3):
    t0 = time.time()
    while True:
        task_ids = set(mod.get_running())
        if task_ids == expected:
            return
        dt = time.time() - t0
        if dt > timeout:
            assert task_ids == expected
        time.sleep(0.2)
