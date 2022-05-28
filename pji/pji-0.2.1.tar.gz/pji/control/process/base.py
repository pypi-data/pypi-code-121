import os
import signal
import time
from abc import ABCMeta
from multiprocessing import Event, Value, Lock
from multiprocessing.synchronize import Event as EventClass
from queue import Empty, Queue
from threading import Thread
from typing import Tuple, Callable, Optional

from ..model import ProcessResult, ResourceLimit, RunResult, RunResultStatus
from ...utils import ValueProxy


class GeneralProcess(metaclass=ABCMeta):
    def __init__(self, start_time: float, resources: ResourceLimit,
                 process_result_func: Callable[[], Optional[ProcessResult]],
                 lifetime_event: EventClass, lock: Optional[Lock] = None):
        self.__start_time = start_time
        self.__resources = resources
        self.__process_result = None
        self.__process_result_func = process_result_func
        self.__result = None
        self.__lifetime_event = lifetime_event
        self.__lock = lock or Lock()

    def __get_process_result(self) -> ProcessResult:
        if self.__process_result is None:
            self.__process_result = self.__process_result_func()
        return self.__process_result

    def __get_result(self) -> RunResult:
        if self.__result is None or self.__result.result is None:
            self.__result = RunResult(self.__resources, self.__get_process_result())
        return self.__result

    def _wait_for_end(self):
        self.__lifetime_event.wait()

    @property
    def start_time(self) -> float:
        with self.__lock:
            return self.__start_time

    @property
    def resources(self) -> ResourceLimit:
        with self.__lock:
            return self.__resources

    @property
    def result(self) -> RunResult:
        with self.__lock:
            return self.__get_result()

    @property
    def ok(self) -> bool:
        with self.__lock:
            return self.__get_result().ok

    @property
    def completed(self) -> bool:
        with self.__lock:
            return self.__get_result().completed

    @property
    def status(self) -> RunResultStatus:
        with self.__lock:
            return self.__get_result().status

    def join(self):
        with self.__lock:
            self._wait_for_end()


BYTES_LINESEQ = bytes(os.linesep, 'utf8')


def read_all_from_bytes_stream(stream) -> bytes:
    return b''.join([line for line in stream])


def load_lines_from_bytes_stream(stream, loader_initialized: EventClass, queue: Queue, transformer=None):
    _middle_queue = Queue()
    _output_load_complete = Event()
    transformer = transformer or (lambda x: x)

    def _output_load_func():
        loader_initialized.set()
        for line in stream:
            _middle_queue.put((time.time(), line))

        _output_load_complete.set()

    def _item_process_func():
        while not _middle_queue.empty() or not _output_load_complete.is_set():
            try:
                item = _middle_queue.get(timeout=0.2)
            except Empty:
                continue
            else:
                queue.put(transformer(item))

    _output_load_thread = Thread(target=_output_load_func)
    _item_process_func = Thread(target=_item_process_func)

    _output_load_thread.start()
    _item_process_func.start()

    _output_load_thread.join()
    _item_process_func.join()


def measure_thread(start_time_ok: Event, start_time: Value, child_pid: int) \
        -> Tuple[Thread, EventClass, EventClass, EventClass, ValueProxy]:
    _process_result = ValueProxy()
    _process_complete = Event()
    _measure_initialized = Event()
    _measure_complete = Event()

    def _thread_func():
        _measure_initialized.set()
        _, status, resource_usage = os.wait4(child_pid, os.WSTOPPED)
        _process_complete.set()
        start_time_ok.wait()
        _process_result.value = ProcessResult(status, start_time.value, time.time(), resource_usage)
        _measure_complete.set()

    return Thread(target=_thread_func), _measure_initialized, _process_complete, _measure_complete, _process_result


def killer_thread(start_time_ok: Event, start_time: Value, child_pid: int,
                  real_time_limit: float, process_complete: Event) -> Tuple[Thread, EventClass]:
    _killer_initialized = Event()

    def _thread_func():
        _killer_initialized.set()
        if real_time_limit is not None:
            start_time_ok.wait()
            target_time = start_time.value + real_time_limit
            while time.time() < target_time and not process_complete.is_set():
                time.sleep(min(max(target_time - time.time(), 0.0), 0.2))
            if not process_complete.is_set():
                os.killpg(os.getpgid(child_pid), signal.SIGKILL)
                process_complete.wait()

    return Thread(target=_thread_func), _killer_initialized
