from typing import List, Optional
from concurrent.futures import Future
from .pool import get_active_pool


__all__ = [
    "get_future",
    "cancel",
    "get_result",
    "get_not_finished",
    "get_not_finished_futures",
]


def get_future(task_id) -> Optional[Future]:
    pool = get_active_pool()
    return pool.get_future(task_id)


def cancel(task_id):
    """The current implementation does not allow cancelling running tasks"""
    future = get_future(task_id)
    if future is not None:
        future.cancel()


def get_result(task_id, **kwargs):
    future = get_future(task_id)
    if future is not None:
        return future.result(**kwargs)


def get_not_finished() -> list:
    pool = get_active_pool()
    return pool.get_not_finished()


def get_not_finished_futures() -> List[Future]:
    lst = [get_future(task_id) for task_id in get_not_finished()]
    return [future for future in lst if future is not None]
