from ..client import celery
from ..client import process
from .utils import get_result


def test_submit(ewoks_worker):
    assert_submit(celery)


def test_submit_local(local_ewoks_worker):
    assert_submit(process)


def assert_submit(mod):
    future1 = mod.discover_tasks_from_modules(args=("ewokscore",))
    future2 = mod.get_future(future1.task_id)
    results = get_result(future1, timeout=3)
    assert results
    results = get_result(future2, timeout=0)
    assert results
