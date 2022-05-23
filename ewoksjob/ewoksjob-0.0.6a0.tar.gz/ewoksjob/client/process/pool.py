import sys
from typing import Mapping, Optional, Tuple
from uuid import uuid4
from contextlib import contextmanager
import multiprocessing
import weakref
from concurrent.futures import ProcessPoolExecutor, Future

__all__ = ["get_active_pool", "pool_context"]


_EWOKS_WORKER_POOL = None


def get_active_pool(raise_on_missing: Optional[bool] = True):
    if raise_on_missing and _EWOKS_WORKER_POOL is None:
        raise RuntimeError("No worker pool is available")
    return _EWOKS_WORKER_POOL


@contextmanager
def pool_context(max_workers=1, context="spawn", **kwargs):
    global _EWOKS_WORKER_POOL
    if _EWOKS_WORKER_POOL is None:
        if sys.version_info < (3, 7):
            ctx = None
        else:
            ctx = multiprocessing.get_context(context)
        with _LocalPool(max_workers=max_workers, mp_context=ctx) as pool:
            _EWOKS_WORKER_POOL = pool
            try:
                yield pool
            finally:
                _EWOKS_WORKER_POOL = None
    else:
        yield _EWOKS_WORKER_POOL


class _LocalPool(ProcessPoolExecutor):
    def __init__(self, *args, **kwargs) -> None:
        if sys.version_info < (3, 7):
            kwargs.pop("mp_context", None)
        self._jobs = weakref.WeakValueDictionary()
        super().__init__(*args, **kwargs)

    def submit(
        self,
        func,
        task_id=None,
        args: Optional[Tuple] = tuple(),
        kwargs: Optional[Mapping] = None,
    ) -> Future:
        """Like celery.send_task"""
        if kwargs is None:
            kwargs = dict()
        future = super().submit(func, *args, **kwargs)
        self._patch_future(future, task_id)
        self._jobs[future.task_id] = future
        return future

    def check_task_id(self, task_id=None):
        if task_id is None:
            task_id = str(uuid4())
            while task_id in self._jobs:
                task_id = str(uuid4())
            return task_id
        if task_id in self._jobs:
            raise RuntimeError(f"Job '{task_id}' already exists")
        return task_id

    def get_future(self, task_id) -> Future:
        future = self._jobs.get(task_id)
        if future is None:
            future = Future()
            self._patch_future(future, task_id)
        return future

    def get_not_finished(self) -> list:
        return [task_id for task_id, future in self._jobs.items() if not future.done()]

    def _patch_future(self, future: Future, task_id):
        future.task_id = self.check_task_id(task_id)
        # Warning: this causes the future to never be garbage collected
        # future.get = future.result
