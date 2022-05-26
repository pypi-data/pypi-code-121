
from multiprocessing.connection import Connection
from collections import deque
from threading import Thread, Event
from typing import Any, List

class Gatherer:

    def __init__(self, external_connection: Connection):
        self._connection = external_connection
        self._result_queue: deque = deque()
        self._exit_event = Event()
        self._ready_event = Event()
        self._invocations = 0
        self._gathered = 0
        self._thread = Thread(target=self._gather_routine, args=(self._connection,), daemon=True)
        self._thread.start()

        self._result_generator = self._create_result_generator()

    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        self.kill()
        return

    def record_invocation(self):
        self._invocations += 1

    def kill(self):
        self._exit_event.set()
        self._thread.join()

    def get_result(self):
        return next(self._result_generator)

    def get_all_results(self) -> List[Any]:
        if (self._invocations == self._gathered):
            results = list(self._result_queue)
            self._result_queue.clear()
            return results

        results = []
        while self._gathered < self._invocations:
            try:
                results.append(self.get_result())
            except:
                pass
        print('using generator')
        return results   

    def _create_result_generator(self):
        while True:
            if len(self._result_queue) < 1:
                self._ready_event.clear()
                self._ready_event.wait()
            result = self._result_queue.popleft()
            yield result

    def _gather_routine(self, connection: Connection):
        while True:
            if (connection.closed):
                return
            if self._exit_event.is_set():
                return
            if connection.poll():
                result = connection.recv()
                self._result_queue.append(result)
                self._gathered += 1
                self._ready_event.set()

        