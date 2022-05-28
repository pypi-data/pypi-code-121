"""
Useful classes for handling threads.
"""

# standard libraries
import concurrent.futures
import dataclasses
import queue
import threading
import time
import typing
import weakref

# third party libraries
# None

# local libraries
# None


_ThreadPoolTask = typing.Callable[[], None]
_OptionalThreadPoolTask = typing.Optional[_ThreadPoolTask]
_QueueParam = typing.Any  # Python 3.9: queue.Queue[_OptionalThreadPoolTask]

class ThreadPool:
    """Queue as set of callbacks on a thread. Allow cancel. Allow manual iteration."""

    def __init__(self) -> None:
        self.__cancel_event = threading.Event()
        self.__queue = queue.Queue()  # type: ignore
        self.__threads: typing.List[threading.Thread] = list()

        def finalize(q: _QueueParam, threads: typing.Sequence[threading.Thread], cancel_event: threading.Event) -> None:
            cancel_event.set()
            for _ in threads:
                q.put(None)
            if len(threads) > 0:
                q.join()

        weakref.finalize(self, finalize, self.__queue, self.__threads, self.__cancel_event)

    def close(self) -> None:
        pass

    def start(self, thread_count: int = 16) -> None:
        def run(q: _QueueParam, cancel: threading.Event) -> None:
            while True:
                task = q.get()
                if task and not cancel.is_set():
                    task()
                q.task_done()
                if not task:  # do not break for cancel; need to match the final put(None)
                    break

        for _ in range(thread_count):
            thread = threading.Thread(target=run, args=(self.__queue, self.__cancel_event))
            thread.start()
            self.__threads.append(thread)

    def queue_fn(self, fn: _OptionalThreadPoolTask, description: typing.Optional[str] = None) -> None:
        if not self.__cancel_event.is_set():
            self.__queue.put(fn)

    def run_all(self) -> None:
        while not self.__queue.empty():
            task = self.__queue.get()
            if task and not self.__cancel_event.is_set():
                task()
            self.__queue.task_done()
            if not task:
                break


@dataclasses.dataclass
class DispatcherInfo:
    is_dispatching_lock: threading.RLock
    is_dispatch_pending: bool
    dispatch_future: typing.Optional[typing.Any]  # Python 3.9: Optional[concurrent.futures.Future[Any]]
    dispatch_thread_cancel: threading.Event
    cached_value_time: float


class SingleItemDispatcher:
    """Dispatch a function to the thread pool, ensuring only one is running at once."""
    def __init__(self, *, executor: typing.Optional[concurrent.futures.ThreadPoolExecutor] = None, minimum_period: float = 0.0):
        self.__executor = executor or concurrent.futures.ThreadPoolExecutor()
        self.__minimum_period = minimum_period
        self.__dispatcher_info = DispatcherInfo(threading.RLock(), False, None, threading.Event(), 0.0)

        def finalize(dispatcher_info: DispatcherInfo, s: str) -> None:
            recompute_future = dispatcher_info.dispatch_future  # avoid race by using local
            if recompute_future:
                dispatcher_info.dispatch_thread_cancel.set()
                concurrent.futures.wait([recompute_future])

        weakref.finalize(self, finalize, self.__dispatcher_info, str(self))

    def close(self) -> None:
        pass

    def dispatch(self, fn: _ThreadPoolTask) -> typing.Any:  # Python 3.9: return type is concurrent.futures.Future[Any]
        # dispatch the function on a thread.
        # if already executing, ensure the thread dispatch again.
        # may be called on the main thread or a thread - must return quickly in both cases.
        with self.__dispatcher_info.is_dispatching_lock:
            # in case thread is already running, set pending.
            # the only way the thread can end is if not pending within lock.
            # dispatch_future can only be set within lock.
            self.__dispatcher_info.is_dispatch_pending = True
            if not self.__dispatcher_info.dispatch_future:

                def dispatch_task(fn: _ThreadPoolTask, minimum_time: float, dispatcher_info: DispatcherInfo) -> None:
                    while True:
                        try:
                            if dispatcher_info.dispatch_thread_cancel.wait(0.05):  # gather changes and helps tests run faster
                                return
                            current_time = time.time()
                            if current_time < dispatcher_info.cached_value_time + minimum_time:
                                if dispatcher_info.dispatch_thread_cancel.wait(dispatcher_info.cached_value_time + minimum_time - current_time):
                                    return
                            dispatcher_info.is_dispatch_pending = False  # any pending calls up to this point will be realized in the recompute
                            fn()
                            dispatcher_info.cached_value_time = time.time()
                        finally:
                            with dispatcher_info.is_dispatching_lock:
                                # the only way the thread can end is if not pending within lock.
                                # recompute_future can only be set within lock.
                                if not dispatcher_info.is_dispatch_pending:
                                    dispatcher_info.dispatch_future = None
                                    break

                self.__dispatcher_info.dispatch_future = self.__executor.submit(dispatch_task, fn, self.__minimum_period, self.__dispatcher_info)
            return self.__dispatcher_info.dispatch_future
