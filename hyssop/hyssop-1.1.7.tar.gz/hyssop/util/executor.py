# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

    - class Executor runs the given functions synchronously or asynchronously
    - class ExecutorFactory manages FunctionQueueWorker instances and produces the Executors.

Modified By: hsky77
Last Updated: September 3rd 2020 14:30:27 pm
'''


import time
import random
import asyncio
from typing import Any, Callable, List

from .worker import FunctionQueueWorker


class _WorkerTask():
    def __init__(self):
        self.result = None
        self.exception = None
        self.done = False

    def on_finish(self, result: Any):
        self.result = result
        self.done = True

    def on_exception(self, e: Exception):
        self.exception = e
        self.done = True


class Executor():
    def __init__(self, worker: FunctionQueueWorker, *args, **kwargs):
        self.__worker = worker

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, type, value, traceback):
        pass

    @property
    def worker(self):
        return self.__worker

    def run_method_in_queue(self,
                            func: Callable,
                            *args,
                            on_finish: Callable[[Any], None] = None,
                            on_exception: Callable[[Exception], None] = None,
                            **kwargs) -> None:
        """Run the given functions. It does not block the calling thread."""
        self.__worker.run_method(
            func, *args, on_finish=on_finish, on_exception=on_exception, **kwargs)

    def run_method(self,
                   func: Callable,
                   *args,
                   **kwargs) -> Any:
        """Run the given function. It blocks the calling thread."""
        task = _WorkerTask()
        self.__worker.run_method(
            func, *args, on_finish=task.on_finish, on_exception=task.on_exception, **kwargs)

        while not task.done:
            time.sleep(0)

        if task.exception:
            raise task.exception from task.exception
        return task.result

    async def run_method_async(self,
                               func: Callable,
                               *args,
                               **kwargs) -> Any:
        """Run the given function asynchronously."""
        task = _WorkerTask()
        self.__worker.run_method(
            func, *args, on_finish=task.on_finish, on_exception=task.on_exception, **kwargs)

        while not task.done:
            await asyncio.sleep(0)

        if task.exception:
            raise task.exception from task.exception
        return task.result


class ExecutorFactory():
    def __init__(self,
                 pool_name: str = None,
                 executor_type: Executor = Executor,
                 worker_type: FunctionQueueWorker = FunctionQueueWorker,
                 worker_limit: int = 1):
        self._pool_name = pool_name or type(self).__name__
        self._executor_type = executor_type
        self._worker_type = worker_type
        self._worker_limit = worker_limit
        self._pool = []
        self._disposed = False

    @property
    def worker_count(self) -> int:
        return len(self._pool)

    @property
    def workers(self) -> List[FunctionQueueWorker]:
        return self._pool

    def dispose(self):
        if not self._disposed:
            self._disposed = True
            for w in self._pool:
                w.dispose()

    def run_method_in_queue(self,
                            func: Callable,
                            *args,
                            on_finish: Callable[[Any], None] = None,
                            on_exception: Callable[[Exception], None] = None,
                            **kwargs) -> None:
        """Run the given func in queue. It does not block the calling thread"""
        with self.get_executor() as executor:
            executor.run_method_in_queue(
                func, *args, on_finish=on_finish, on_exception=on_exception, **kwargs)

    def run_method(self,
                   func: Callable,
                   *args,
                   **kwargs) -> Any:
        """
        Run the given func. It blocks the calling thread.
        """
        with self.get_executor() as executor:
            return executor.run_method(func, *args, **kwargs)

    async def run_method_async(self,
                               func: Callable,
                               *args,
                               **kwargs) -> Any:
        """Run the given func asynchronously."""
        async with self.get_executor() as executor:
            return await executor.run_method_async(func, *args, **kwargs)

    def get_executor(self, *args, **kwargs) -> Executor:
        """
        Create and return an executor instance.
        """
        if len(self._pool) < self._worker_limit:
            worker = self._worker_type(
                '{}_{}'.format(self._pool_name, len(self._pool)))
            self._pool.append(worker)
            return self._executor_type(worker, *args, **kwargs)

        return self._executor_type(self._pool[random.randint(0, len(self._pool)-1)], *args, **kwargs)
