import asyncio
import threading
from concurrent.futures import Executor
from functools import partial
from typing import Callable, Optional, Union

from apscheduler.schedulers.asyncio import AsyncIOScheduler as BaseAsyncScheduler
from apscheduler.util import get_callable_name, iscoroutinefunction_partial, ref_to_obj, undefined

from dropland.storages.containers import use_engines
from dropland.tasks.remote import RemoteScheduler


class Scheduler(BaseAsyncScheduler):
    def __init__(self, remote: Optional[RemoteScheduler] = None,
                 executor: Optional[Executor] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._remote = remote
        self._executor = executor
        self._lock = threading.Lock()
        self._counter = 0
        self._thread = None

        try:
            self._eventloop = asyncio.get_running_loop()
        except RuntimeError:
            self._eventloop = asyncio.new_event_loop()

        self._eventloop.set_default_executor(self._executor)

    def _start(self, paused: bool):
        if not self._eventloop.is_running() and not self._thread:
            self._thread = threading.Thread(target=self._eventloop.run_forever, name='TaskWorkerAsync')

        if self._thread and not self._thread.is_alive():
            self._thread.start()

        super().start(paused)

        if self._remote:
            self._remote.start(paused)

    def _shutdown(self, wait: bool):
        super().shutdown(wait)

        if self._remote:
            self._remote.shutdown(wait)

        if self._thread:
            self._eventloop.call_soon_threadsafe(self._eventloop.stop)
            self._thread.join()
            self._thread = None

    def start(self, paused: bool = False):
        with self._lock:
            if 0 == self._counter:
                self._start(paused)
            self._counter += 1

    def shutdown(self, wait: bool = True):
        with self._lock:
            if 1 == self._counter:
                self._shutdown(wait)
            self._counter = max(self._counter - 1, 0)

    def pause(self):
        super().pause()
        if self._remote:
            self._remote.pause()

    def resume(self):
        super().resume()
        if self._remote:
            self._remote.resume()

    def add_job(self, func, trigger=None, args=None, kwargs=None, id=None, name=None,
                misfire_grace_time=undefined, coalesce=undefined, max_instances=undefined,
                next_run_time=undefined, jobstore='default', executor='default',
                replace_existing=False, remote: Optional[bool] = None, **trigger_args):
        if (remote is None or remote is True) and self._remote:
            method = self._remote.add_job
            target = func
            fname = name or get_callable_name(func)
        else:
            if iscoroutinefunction_partial(func if isinstance(func, Callable) else ref_to_obj(func)):
                target = Scheduler.task_sync_main if 'process' == executor else Scheduler.task_async_main
                args = (func, *(args or tuple()))
                fname = name or get_callable_name(func)
            else:
                target = func
                fname = name or get_callable_name(func)

            method = super().add_job

        return method(
            target, trigger, args, kwargs, id, fname, misfire_grace_time, coalesce,
            max_instances, next_run_time, jobstore, executor, replace_existing, **trigger_args)

    def scheduled_job(self, trigger, args=None, kwargs=None, id=None, name=None,
                      misfire_grace_time=undefined, coalesce=undefined, max_instances=undefined,
                      next_run_time=undefined, jobstore='default', executor='default',
                      remote: Optional[bool] = None, **trigger_args):
        return super().scheduled_job(
            trigger, args, kwargs, id, name, misfire_grace_time, coalesce,
            max_instances, next_run_time, jobstore, executor, remote=remote, **trigger_args)

    def modify_job(self, job_id, jobstore=None, **changes) -> bool:
        if _ := super().get_job(job_id, jobstore):
            super().modify_job(job_id, jobstore, **changes)
            return True
        if self._remote:
            return self._remote.modify_job(job_id, jobstore, **changes)
        return False

    def reschedule_job(self, job_id, jobstore=None, trigger=None, **trigger_args) -> bool:
        if self.reschedule_job(job_id, jobstore, trigger, **trigger_args):
            return True
        if self._remote:
            return self._remote.reschedule_job(job_id, jobstore, trigger, **trigger_args)
        return False

    def pause_job(self, job_id, jobstore=None) -> bool:
        if _ := super().get_job(job_id, jobstore):
            super().pause_job(job_id, jobstore)
            return True
        if self._remote:
            return self._remote.pause_job(job_id, jobstore)
        return False

    def resume_job(self, job_id, jobstore=None) -> bool:
        if _ := super().get_job(job_id, jobstore):
            super().resume_job(job_id, jobstore)
            return True
        if self._remote:
            return self._remote.resume_job(job_id, jobstore)
        return False

    def remove_job(self, job_id, jobstore=None) -> bool:
        if _ := super().get_job(job_id, jobstore):
            super().remove_job(job_id, jobstore)
            return True
        if self._remote:
            return self._remote.remove_job(job_id, jobstore)
        return False

    def remove_all_jobs(self, jobstore=None, remote: bool = False):
        if remote and self._remote:
            self._remote.remove_all_jobs(jobstore)
        else:
            super().remove_all_jobs(jobstore)

    def get_job(self, job_id, jobstore=None):
        if job := super().get_job(job_id, jobstore):
            return job
        if self._remote:
            return self._remote.get_job(job_id, jobstore)
        return None

    def get_jobs(self, jobstore=None, pending=None):
        if jobs := super().get_jobs(jobstore, pending):
            return jobs
        if self._remote:
            return self._remote.get_jobs(jobstore, pending)
        return []

    def lookup_executor(self, alias: str):
        return self._executors.get(alias)

    @staticmethod
    async def task_async_main(func: Union[str, Callable], *args, **kwargs):
        func = func if isinstance(func, Callable) else ref_to_obj(func)
        target = use_engines()(func)

        if iscoroutinefunction_partial(func):
            await target(*args, **kwargs)
        else:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, partial(target, *args, **kwargs))

    @staticmethod
    def task_sync_main(func: Union[str, Callable], *args, **kwargs):
        asyncio.run(Scheduler.task_async_main(func, *args, **kwargs))
