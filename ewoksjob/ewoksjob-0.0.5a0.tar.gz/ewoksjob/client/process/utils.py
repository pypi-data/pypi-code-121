from typing import Optional
from concurrent.futures import Future
from .pool import get_active_pool


__all__ = ["get_future", "cancel", "get_result", "get_running"]


def get_future(task_id) -> Optional[Future]:
    pool = get_active_pool()
    return pool.get_future(task_id)


def cancel(task_id):
    future = get_future(task_id)
    if future is not None:
        future.cancel()


def get_result(task_id, **kwargs):
    future = get_future(task_id)
    if future is not None:
        return future.result(**kwargs)


def get_running():
    pool = get_active_pool()
    return pool.get_running()
