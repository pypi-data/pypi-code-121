import logging
from functools import wraps
from typing import Optional
from celery import current_app
from celery.result import AsyncResult
from ...config import configure_app

__all__ = ["get_future", "cancel", "get_result", "get_running"]


logger = logging.getLogger(__name__)


def requires_config(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        if not current_app.conf.broker_url:
            configure_app(current_app)
        return method(*args, **kwargs)

    return wrapper


@requires_config
def get_future(task_id) -> Optional[AsyncResult]:
    return AsyncResult(task_id)


@requires_config
def cancel(task_id):
    future = get_future(task_id)
    if future is not None:
        future.revoke()


@requires_config
def get_result(task_id, **kwargs):
    kwargs.setdefault("interval", 0.1)
    future = AsyncResult(task_id)
    if future is not None:
        return future.get(**kwargs)


@requires_config
def get_running():
    inspect = current_app.control.inspect()
    task_ids = list()

    workers = inspect.active()
    if workers is None:
        logger.warning("No Celery workers were detected")
        workers = dict()
    for tasks in workers.values():
        for task in tasks:
            task_ids.append(task["id"])

    workers = inspect.scheduled()
    if workers is None:
        workers = dict()
    for tasks in workers.values():
        for task in tasks:
            task_ids.append(task["id"])

    return task_ids
