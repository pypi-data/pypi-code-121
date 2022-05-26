from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Any, Callable, TypeVar

from grpc import RpcError
from grpc._channel import _MultiThreadedRendezvous

from sila2.client.subscription import Subscription

T = TypeVar("T")


class GrpcStreamSubscription(Subscription[T]):
    def __init__(
        self, wrapped_stream: _MultiThreadedRendezvous, converter_func: Callable[[Any], T], executor: ThreadPoolExecutor
    ) -> None:
        super().__init__()
        self.__wrapped_stream = wrapped_stream
        self.__converter_func = converter_func
        self.__executor = executor
        self.__queue = Queue()
        self.__cancelled = False

        def looped_func():
            while True:
                try:
                    new_item = self.__converter_func(next(self.__wrapped_stream))
                except (RpcError, StopIteration):
                    break

                self.__queue.put(new_item)
                for callback in self.callbacks:
                    self.__executor.submit(lambda: callback(new_item))

            self.__queue.put(StopIteration())

        executor.submit(looped_func)

    def __next__(self) -> T:
        item = self.__queue.get()
        if isinstance(item, StopIteration):
            raise item
        return item

    def cancel(self):
        self.__wrapped_stream.cancel()
        self.__queue.put(StopIteration())
        self.__cancelled = True

    @property
    def is_cancelled(self) -> bool:
        return self.__cancelled
