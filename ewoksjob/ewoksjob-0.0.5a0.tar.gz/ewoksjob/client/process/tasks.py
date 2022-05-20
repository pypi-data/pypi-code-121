from functools import wraps
from typing import Mapping, Optional, Tuple
from concurrent.futures import Future

from .pool import get_active_pool
from ..test_workflow import test_workflow

try:
    from ewoks import execute_graph
    from ewokscore import task_discovery
except ImportError as e:
    execute_graph = None
    ewoks_import_error = e


__all__ = ["trigger_workflow", "trigger_test_workflow", "discover_tasks_from_modules"]


def _requires_ewoks(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        if execute_graph is None:
            raise ImportError(ewoks_import_error)
        return method(*args, **kwargs)

    return wrapper


@_requires_ewoks
def trigger_workflow(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    pool = get_active_pool()
    if kwargs is None:
        kwargs = dict()
    execinfo = kwargs.setdefault("execinfo", dict())
    task_id = pool.check_task_id(execinfo.get("job_id"))
    execinfo["job_id"] = task_id
    return pool.submit(execute_graph, task_id=task_id, args=args, kwargs=kwargs)


def trigger_test_workflow(seconds=0) -> Future:
    return trigger_workflow(
        args=(test_workflow(),),
        kwargs={"inputs": [{"id": "sleepnode", "name": 0, "value": seconds}]},
    )


@_requires_ewoks
def discover_tasks_from_modules(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    pool = get_active_pool()
    if kwargs is None:
        kwargs = dict()
    return pool.submit(_discover_tasks_from_modules, args=args, kwargs=kwargs)


def _discover_tasks_from_modules(*args, **kwargs):
    return list(task_discovery.discover_tasks_from_modules(*args, **kwargs))
