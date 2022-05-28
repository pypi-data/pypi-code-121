"""
Utility classes for implementing task queues and sets.
"""

# standard libraries
import asyncio
import copy
import queue
import threading
import typing

# third party libraries
# None

# local libraries
# None


class TaskQueue:
    def __init__(self) -> None:
        # Python 3.9+: use queue.Queue[typing.Callable[[], None]]
        self.__queue: typing.Any = queue.Queue()

    def put(self, task: typing.Callable[[], None]) -> None:
        self.__queue.put(task)

    def perform_tasks(self) -> None:
        # perform any pending operations
        qsize = self.__queue.qsize()
        while not self.__queue.empty() and qsize > 0:
            try:
                task = self.__queue.get(False)
            except queue.Empty:
                pass
            else:
                task()
                self.__queue.task_done()
            qsize -= 1

    def clear_tasks(self) -> None:
        # perform any pending operations
        qsize = self.__queue.qsize()
        while not self.__queue.empty() and qsize > 0:
            try:
                task = self.__queue.get(False)
            except queue.Empty:
                pass
            else:
                self.__queue.task_done()
            qsize -= 1


# keeps a set of tasks to do when perform_tasks is called.
# each task is associated with a key. overwriting a key
# will discard any task currently associated with that key.
class TaskSet:
    def __init__(self) -> None:
        self.__task_dict: typing.Dict[str, typing.Callable[[], None]] = dict()
        self.__task_dict_mutex = threading.RLock()

    def add_task(self, key: str, task: typing.Callable[[], None]) -> None:
        with self.__task_dict_mutex:
            self.__task_dict[key] = task

    def clear_task(self, key: str) -> None:
        with self.__task_dict_mutex:
            if key in self.__task_dict:
                self.__task_dict.pop(key, None)

    def perform_tasks(self) -> None:
        with self.__task_dict_mutex:
            task_dict = copy.copy(self.__task_dict)
            self.__task_dict.clear()
        for task in task_dict.values():
            task()


def sync_event_loop(event_loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> None:
    """Synchronize the event loop, ensuring all tasks are complete.

    Uses the current event loop if event_loop is None.
    """
    event_loop = event_loop or asyncio.get_running_loop()
    # give event loop one chance to finish up
    event_loop.stop()
    event_loop.run_forever()
    # wait for everything to finish, including tasks running in executors
    # this assumes that all outstanding tasks finish in a reasonable time (i.e. no infinite loops).
    tasks = asyncio.all_tasks(loop=event_loop)
    if tasks:
        for task in tasks:
            task.cancel()
        gather_future = asyncio.gather(*tasks, return_exceptions=True)
    else:
        # work around bad design in gather (always uses global event loop in Python 3.8)
        gather_future = event_loop.create_future()
        gather_future.set_result([])
    event_loop.run_until_complete(gather_future)


def close_event_loop(event_loop: typing.Optional[asyncio.AbstractEventLoop] = None) -> None:
    """Synchronize and optionally close the event loop.

    If a specific event loop is passed, it will be closed. Otherwise only synchronized.
    """
    sync_event_loop(event_loop)
    if event_loop:
        # due to a bug in Python libraries, the default executor needs to be shutdown explicitly before the event loop
        # see http://bugs.python.org/issue28464 . this bug manifests itself in at least one way: an intermittent failure
        # in test_document_controller_releases_itself. reproduce by running the contents of that test in a loop of 100.
        _default_executor = getattr(event_loop, "_default_executor", None)
        if _default_executor:
            _default_executor.shutdown()
        event_loop.close()
