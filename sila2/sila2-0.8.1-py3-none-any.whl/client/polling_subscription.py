import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Callable, TypeVar

from sila2.client.subscription import Subscription

_CANCELLATION_CHECK_INTERVAL: float = 0.1

T = TypeVar("T")


class PollingSubscription(Subscription[T]):
    def __init__(
        self,
        func: Callable[[], T],
        executor: ThreadPoolExecutor,
        polling_interval: float,
    ) -> None:
        super().__init__()
        self.__queue = Queue()
        self.__cancelled = False

        n_checks_per_loop = max(1, int(polling_interval / _CANCELLATION_CHECK_INTERVAL))
        polling_interval /= n_checks_per_loop

        def looped_func():
            last_item = object()
            while not self.__cancelled:
                new_item = func()
                if new_item == last_item:
                    continue  # only emit changes
                last_item = new_item

                self.__queue.put(new_item)
                for callback in self.callbacks:
                    executor.submit(lambda: callback(new_item))

                for _ in range(n_checks_per_loop):
                    if self.__cancelled:
                        break
                    time.sleep(polling_interval)
            self.__queue.put(StopIteration())

        executor.submit(looped_func)

    def __next__(self) -> T:
        item = self.__queue.get()
        if isinstance(item, StopIteration):
            raise item
        return item

    def cancel(self) -> None:
        self.__cancelled = True

    @property
    def is_cancelled(self) -> bool:
        return self.__cancelled
