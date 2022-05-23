import pytest
from ..client import celery
from ..client import process
from .utils import wait_not_finished
from .utils import has_redis_server


@pytest.mark.skip(reason="working in manual testing")
@pytest.mark.skipif(
    not has_redis_server(), reason="memory and sqlite do not support task monitoring"
)
def test_futures(ewoks_worker):
    assert_futures(celery)


def test_futures_local(local_ewoks_worker):
    assert_futures(process)


def assert_futures(mod):
    seconds = 2
    timeout = seconds * 4
    future1 = mod.submit_test(seconds)
    future2 = mod.submit_test(seconds)
    tasks1 = {future1.task_id, future2.task_id}
    wait_not_finished(mod, tasks1, timeout=timeout)
    tasks2 = {future.task_id for future in mod.get_not_finished_futures()}
    assert tasks1 == tasks2
    wait_not_finished(mod, set(), timeout=timeout)
