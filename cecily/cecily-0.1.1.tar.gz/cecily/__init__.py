import concurrent.futures
import inspect
import logging
import multiprocessing
import os
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from enum import Enum
from multiprocessing.managers import SyncManager
from queue import Queue
from typing import Any, Callable, Generic, Iterator, TypeVar, final
from uuid import UUID, uuid4

T = TypeVar('T')
RT = TypeVar('RT')

logger = logging.getLogger(__name__)


class Alias:
    WORKER = 'WORKER'
    MAIN = 'MAIN'
    OTHER = 'OTHER'
    MANAGER = 'MANAGER'


def trace(process_alias, msg, *args, **kwargs):
    current_process = multiprocessing.current_process()
    logger.debug(f'[{process_alias}] {msg} ({current_process}, pid={os.getpid()})', *args, **kwargs)


class Status(Enum):
    READY = 1
    STARTED = 2
    DONE = 3


@final
class JobFinished:
    pass


# Sentinel object that indicates that a job has finished execution
JOB_FINISHED = JobFinished()


class Job:
    id: UUID
    status: Status

    task_fn: Callable
    args: list[Any]
    kwargs: dict[Any]

    queue: Queue

    def __init__(
        self,
        job_id: UUID,
        queue: Queue,
        task_fn: Callable,
        args: list,
        kwargs: dict,
    ) -> None:
        super().__init__()
        self.id = job_id
        self.status = Status.READY

        self.task_fn = task_fn
        self.args = args
        self.kwargs = kwargs

        self.queue = queue

    def execute(self) -> Any:
        trace(Alias.WORKER, 'job starting for id=%s', self.id)
        self.status = Status.STARTED

        parameters = inspect.signature(self.task_fn).parameters
        if 'notifier' in parameters:
            self.kwargs['notifier'] = self.queue

        result = self.task_fn(*self.args, **self.kwargs)

        self.queue.put(JOB_FINISHED)
        self.status = Status.DONE

        # XXX: don't know if this is necessary
        # forcefully delete weakref to queue object
        del self.queue

        return result


@dataclass
class CecilyFuture(Generic[RT]):
    job_id: UUID
    queue: Queue

    _future: concurrent.futures.Future

    def collect(self) -> Iterator[RT]:
        if not self._future.running:
            return

        while True:
            v = self.queue.get()

            if isinstance(v, JobFinished):
                break

            yield v

    def result(self) -> Any:
        return self._future.result()


class CecilyTask(Callable, ABC):
    @abstractmethod
    def apply(self, *args, **kwargs) -> CecilyFuture:
        ...

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...


def worker(task_fn, job_id, queue, args, kwargs):
    trace(Alias.WORKER, 'init new job with task_fn=%s id=%s', task_fn.__name__, job_id)
    job = Job(job_id, queue, task_fn, args, kwargs)
    return job.execute()


@dataclass
class Task:
    app_ref: 'Cecily'
    task_fn: Callable

    def __call__(self, *args, **kwargs) -> CecilyFuture:
        trace(Alias.OTHER, 'task for task_fn=%s called', self.task_fn.__name__)

        # create id
        job_id = uuid4()

        queue_proxy = self.app_ref.manager.Queue()

        future = self.app_ref.executor.submit(
            worker,
            self.task_fn,
            job_id,
            queue_proxy,
            args,
            kwargs,
        )

        return CecilyFuture(job_id, queue_proxy, future)


class Cecily:
    spawned: bool
    executor: ProcessPoolExecutor
    manager: SyncManager

    def __init__(self, max_workers: int | None = None) -> None:
        current_process = multiprocessing.current_process()

        # XXX: determines if this app is called from the Main app's ProcessPoolExecutor
        #   by checking if the current process is spawned
        if isinstance(current_process, multiprocessing.context.SpawnProcess):
            self.spawned = True
            trace(Alias.OTHER, 'skipping app init')
            return

        trace(Alias.MAIN, 'creating app')
        self.spawned = False
        self.executor = ProcessPoolExecutor(max_workers)

        self.manager = multiprocessing.Manager()

    def task(self, fn) -> CecilyTask:
        if self.spawned:
            return fn

        logger.debug('[MAIN] registering new task: %s', fn.__name__)

        fn.apply = Task(self, fn)

        return fn

    def close(self):
        logger.debug('[MAIN] shutting down app')

        self.executor.shutdown(cancel_futures=True)
        self.manager.shutdown()

        logger.debug('[MAIN] shutdown complete')
