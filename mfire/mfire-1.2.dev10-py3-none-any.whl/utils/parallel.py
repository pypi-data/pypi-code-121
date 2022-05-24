"""Module for safe parallel processing
"""
from __future__ import annotations
import os
import time
import traceback
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Optional, Tuple, List
from multiprocessing import get_context, TimeoutError, current_process

from mfire.settings.logger import Logger


LOGGER = Logger(name="utils.parallel")


class TaskStatus(str, Enum):
    """Possible status of a task
    """

    NEW = ("NEW", False)
    PENDING = ("PENDING", False)
    RUNNING = ("RUNNING", False)
    FAILED = ("FAILED", True)
    TIMEOUT = ("TIMEOUT", True)
    DONE = ("DONE", False)

    def __new__(cls, value: str, is_error: bool) -> TaskStatus:
        """Initialize a new TaskStatus object

        Args:
            value (str): String value of the Task Status
            is_error (bool): Whether the given status is an error

        Returns:
            Method: New TaskStatus object
        """
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.is_error = is_error
        return obj


class Task:
    """Wrapping of a task contaning a function to apply on given
    arguments and keyword arguments.
    """

    def __init__(
        self,
        func: Callable,
        args: Optional[Iterable] = None,
        kwds: Optional[Mapping] = None,
        callback: Optional[Callable] = None,
        name: Optional[str] = None,
    ) -> None:
        """Initialisation method.

        Args:
            func (Callable): Function to call.
            args (Optional[Iterable]): Arguments to pass to the function.
                Defaults to None.
            kwds (Optional[Mapping]): Keyword arguments to pass to the
                function. Defaults to None.
            callback (Optional[Callable]): Function to call when the result is ready
            name (Optional[str]): Name of the tasks (for logging its status).
                Defaults to None.
        """
        self.func = func
        self.args = args
        if args is None:
            self.args = list()
        self.kwds = kwds
        if kwds is None:
            self.kwds = dict()
        self.callback = callback
        if callback is None:
            self.callback = lambda x: None
        self.name = name
        if name is None:
            self.name = "Task"
        self.status = TaskStatus.NEW
        self.async_result = None

    def change_status(self, new_status: TaskStatus, **kwargs) -> None:
        """Changes the task's status and notify through the logger

        Args:
            new_status (TaskStatus): New status of the task
        """
        if self.status == new_status:
            return None
        old_status = self.status
        self.status = new_status
        msg = f"Task {self.name}: {old_status.value} -> {self.status.value}"
        if self.status.is_error:
            LOGGER.error(msg, **kwargs)
        else:
            LOGGER.info(msg, **kwargs)

    def run(self) -> Any:
        """Method for calling the self.func with the self.arg and self.kwds

        Returns:
            Any: The self.func(*self.args, **self.kwds) result
        """
        try:
            self.change_status(TaskStatus.RUNNING)
            result = self.func(*self.args, **self.kwds)
            self.callback(result)
            self.change_status(TaskStatus.DONE)
            return result
        except Exception as excpt:
            self.change_status(TaskStatus.FAILED)
            raise excpt

    def __repr__(self) -> str:
        return f"{self.name} (status={self.status.value})"

    def __str__(self) -> str:
        return repr(self)


class Parallel:
    """Class wrapping the multiprocessing.pool.Pool.apply_async usages for making
    it safer by catching Exceptions and triggering timeouts.
    """

    def __init__(self, processes: Optional[int] = os.cpu_count()) -> None:
        """Initialization method of a Parallel object

        Args:
            processes (Optional[int]): number of processes to use.
                Defaults to os.cpu_count().
            logger (Optional[Logger]): Logger to use to log caught exceptions.
        """
        self.processes = processes
        self._tasks = []

    def __len__(self) -> int:
        return len(self._tasks)

    def __getitem__(self, index: int) -> Task:
        return self._tasks[index]

    def __repr__(self) -> str:
        base = f"Parallel({len(self)} tasks: "
        for status, count in self.count_status():
            if count > 0:
                base += f"{count} {status.value}; "
        return base.strip(":; ") + ")"

    def count_status(self) -> List[Tuple[TaskStatus, int]]:
        """Counts the number of tasks with each possible status.

        Returns:
            List[Tuple[TaskStatus, int]]: list containing each TaskStatus
                and the corresponding number of tasks with this status.

        """
        statuses = [task.status for task in self._tasks]
        return [(status, statuses.count(status)) for status in TaskStatus]

    def clean(self) -> None:
        """Cleanses the tasks.
        """
        self._tasks = []

    @property
    def queue(self) -> List[Task]:
        """Generator yielding the new tasks

        Yields:
            Iterator[Task]: Iteration over new tasks
        """
        return [
            t for t in self._tasks if t.status in (TaskStatus.NEW, TaskStatus.PENDING)
        ]

    def _error_callback(self, excpt: Exception) -> None:
        """Method used as an error_callback during the "get" execution.
        It is used when a sub-process fails, and then log the exception
        caught during the execution.

        Args:
            excpt (Exception): exception to log
        """
        trace = traceback.format_exception(type(excpt), excpt, excpt.__traceback__)
        LOGGER.error(f"An error has been caught {repr(excpt)}.\n" + "".join(trace))

    def apply(
        self,
        func: Callable,
        args: Optional[Iterable] = None,
        kwds: Optional[Mapping] = None,
        callback: Optional[Callable] = None,
        name: Optional[str] = None,
    ) -> str:
        """Method that loads a task to the queue following an "apply" schema,
        i.e. by providing a function and its arguments and keyword arguments.

        Warning : this method doesn't trigger a processing any kind. To run the
        the loaded task, you must self.run() after.

        Args:
            func (Callable): Function to apply.
            args (Optional[Iterable]): Arguments to pass on to the function.
                Defaults to None.
            kwds (Optional[Mapping]): Keyword arguments to pass on to the function.
                Defaults to None.
            callback (Optional[Callable]): Function to call when the result is ready.
                Defaults to None.
            name (Optional[str]): Name of the task (for logging purposes).
                Defaults to None.

        Returns:
            str: The name of the added task.
        """
        if name is None:
            name = f"Task#{len(self._tasks)}"
        task = Task(func=func, args=args, kwds=kwds, callback=callback, name=name)
        self._tasks.append(task)
        return name

    def run(self, timeout: int = None):
        """Method that launches the multiprocessing of the previously loaded tasks.

        Args:
            timeout (int, optional): Maximal duration in seconds to run all the
                tasks. Defaults to None.
        """
        start = time.time()
        keep_running = True
        remaining_time = 1
        nb_tasks, nb_success = len(self.queue), 0
        LOGGER.info(f"Starting parallel processing: {nb_tasks} to process.")
        with get_context("spawn").Pool(
            processes=max(1, self.processes - 1), maxtasksperchild=1,
        ) as pool:
            while keep_running and remaining_time > 0:
                # managing remaining time if needed
                if timeout is not None:
                    elapsed_time = time.time() - start
                    remaining_time = timeout - elapsed_time
                    if remaining_time < 0:
                        remaining_time = 0

                keep_running = False
                for task in self.queue:
                    if task.status == TaskStatus.NEW:
                        task.async_result = pool.apply_async(
                            task.func,
                            args=task.args,
                            kwds=task.kwds,
                            callback=task.callback,
                            error_callback=self._error_callback,
                        )
                        task.change_status(TaskStatus.PENDING)
                        keep_running = True

                    elif task.async_result.ready():
                        if task.async_result.successful():
                            task.change_status(TaskStatus.DONE)
                            nb_success += 1
                        else:
                            task.change_status(TaskStatus.FAILED)
                    else:
                        keep_running = True
                time.sleep(0.1)  # to prevent main CPU hogging

        for task in self.queue:
            try:
                task.async_result.get(timeout=0)
                task.change_status(TaskStatus.DONE)
                nb_success += 1
            except TimeoutError:
                task.change_status(TaskStatus.TIMEOUT)
            except Exception:
                task.change_status(TaskStatus.FAILED, exc_info=True)

        LOGGER.info(
            f"End of parallel processing.\t{nb_success}/{nb_tasks} tasks done."
            f"\tElapsed time : {time.time() - start:.3f}s."
        )


__all__ = ["current_process", "TaskStatus", "Task", "Parallel"]
