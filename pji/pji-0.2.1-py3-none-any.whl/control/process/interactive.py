import os
import pickle
from multiprocessing import Event, Value, Lock
from multiprocessing.synchronize import Event as EventClass
from queue import Queue, Empty
from threading import Thread
from typing import Optional, Mapping

from .base import BYTES_LINESEQ, measure_thread, killer_thread, load_lines_from_bytes_stream, GeneralProcess
from .decorator import process_setter
from .executor import get_child_executor_func
from ..model import ResourceLimit
from ...utils import gen_lock


class InteractiveProcess(GeneralProcess):
    def __init__(self, start_time: float, stdin_stream, output_iter,
                 resources: ResourceLimit, process_result_func, lifetime_event: EventClass):
        self.__lock = Lock()
        GeneralProcess.__init__(self, start_time, resources, process_result_func, lifetime_event, self.__lock)

        self.__stdin_stream = stdin_stream
        self.__output_iter = output_iter
        self.__stdin_closed = False

    def __write_stdin(self, data: bytes):
        try:
            self.__stdin_stream.write(data)
        except BrokenPipeError as err:
            self.__stdin_closed = True
            raise err

    def __flush_stdin(self):
        try:
            self.__stdin_stream.flush()
        except BrokenPipeError as err:
            self.__stdin_closed = True
            raise err

    def __close_stdin(self):
        try:
            self.__stdin_stream.close()
            self.__stdin_closed = True
        except BrokenPipeError as err:
            self.__stdin_closed = True
            raise err

    def __load_all_output(self):
        _ = list(self.__output_iter)

    def __exit(self):
        if not self.__stdin_closed:
            self.__close_stdin()
        self.__load_all_output()
        self._wait_for_end()

    @property
    def output_yield(self):
        with self.__lock:
            return self.__output_iter

    def print_stdin(self, line: bytes, flush: bool = True, end: bytes = BYTES_LINESEQ):
        with self.__lock:
            self.__write_stdin(line + end)
            if flush:
                self.__flush_stdin()

    def close_stdin(self):
        with self.__lock:
            self.__close_stdin()

    def __enter__(self):
        with self.__lock:
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.__lock:
            self.__exit()


def _read_pipe(pipe_entry, start_time_ok: EventClass, start_time: Value,
               tag: str, loader_initialized: EventClass, queue: Queue):
    def _transform_func(item):
        _time, _line = item
        start_time_ok.wait()
        return _time - start_time.value, tag, _line.rstrip(b'\r\n')

    with os.fdopen(pipe_entry, 'rb', 0) as stream:
        return load_lines_from_bytes_stream(stream, loader_initialized, queue, _transform_func)


# Attention: only real_time_limit will be processed in this function, other limits will be processed in decorator
# noinspection DuplicatedCode, PyIncorrectDocstring,PyUnresolvedReferences,SpellCheckingInspection
@process_setter
def interactive_process(args, preexec_fn=None, resources=None,
                        environ: Optional[Mapping[str, str]] = None) -> InteractiveProcess:
    """
    Create an interactive process
    :param args: arguments for execution
    :param shell: use shell to execute args
    :param preexec_fn: pre execute function to attach before that
    :param resources: resource limit
    :param environ: environment variables
    :param cwd: new work dir
    :param identification: user and group for execution
    :return: InteractiveProcess object to do run
    """
    resources = ResourceLimit.loads(resources)
    _full_lifetime_complete = Event()
    environ = dict(environ or {})

    _executor_prepare_ok = Event()
    _exception_get, _exception_put = os.pipe()

    _parent_initialized = Event()
    _start_time = Value('d', 0.0)
    _start_time_ok = Event()

    # noinspection DuplicatedCode
    def _execute_parent() -> InteractiveProcess:
        os.close(stdin_read)
        os.close(stdout_write)
        os.close(stderr_write)

        # measure thread
        _measure_thread, _measure_initialized, _process_complete, _measure_complete, _result_proxy = measure_thread(
            start_time_ok=_start_time_ok,
            start_time=_start_time,
            child_pid=child_pid,
        )

        # killer thread
        _killer_thread, _killer_initialized = killer_thread(
            start_time_ok=_start_time_ok,
            start_time=_start_time,
            child_pid=child_pid,
            real_time_limit=resources.max_real_time,
            process_complete=_process_complete,
        )

        # lines output
        _output_queue = Queue()
        _output_start, _output_complete = Event(), Event()
        _stdout_initialized, _stderr_initialized = Event(), Event()
        _stdout_thread = Thread(
            target=lambda: _read_pipe(
                pipe_entry=stdout_read,
                start_time_ok=_start_time_ok,
                start_time=_start_time,
                tag='stdout',
                loader_initialized=_stdout_initialized,
                queue=_output_queue,
            ))
        _stderr_thread = Thread(
            target=lambda: _read_pipe(
                pipe_entry=stderr_read,
                start_time_ok=_start_time_ok,
                start_time=_start_time,
                tag='stderr',
                loader_initialized=_stderr_initialized,
                queue=_output_queue,
            ))

        def _output_queue_func():
            _stdout_thread.start()
            _stderr_thread.start()
            _stdout_initialized.wait()
            _stderr_initialized.wait()
            _output_start.set()

            _stdout_thread.join()
            _stderr_thread.join()
            _output_complete.set()

        _queue_thread = Thread(target=_output_queue_func)

        def _output_yield():
            _output_start.wait()
            while not _output_complete.is_set() or not _output_queue.empty():
                try:
                    _time, _tag, _line = _output_queue.get(timeout=0.2)
                except Empty:
                    pass
                else:
                    yield _time, _tag, _line

            _measure_thread.join()
            _killer_thread.join()
            _queue_thread.join()
            _full_lifetime_complete.set()

        # waiting for prepare ok
        _executor_prepare_ok.wait()
        with os.fdopen(_exception_get, 'rb', 0) as ef:
            _exception = pickle.load(ef)
            if _exception:
                raise _exception

        # start all the threads and services
        _measure_thread.start()
        _killer_thread.start()
        _queue_thread.start()
        _stdin_stream = os.fdopen(stdin_write, 'wb', 0)
        _output_iter = gen_lock(_output_yield())

        # wait for all the thread initialized
        _measure_initialized.wait()
        _killer_initialized.wait()
        _output_start.wait()
        _parent_initialized.set()

        _start_time_ok.wait()
        return InteractiveProcess(
            start_time=_start_time.value,
            stdin_stream=_stdin_stream,
            output_iter=_output_iter,
            resources=resources,
            process_result_func=lambda: _result_proxy.value,
            lifetime_event=_full_lifetime_complete,
        )

    stdin_read, stdin_write = os.pipe()
    stdout_read, stdout_write = os.pipe()
    stderr_read, stderr_write = os.pipe()

    _execute_child = get_child_executor_func(
        args, dict(environ or {}), preexec_fn,
        _executor_prepare_ok, (_exception_get, _exception_put),
        _parent_initialized,
        _start_time_ok, _start_time,
        (stdin_read, stdin_write),
        (stdout_read, stdout_write),
        (stderr_read, stderr_write),
    )

    child_pid = os.fork()

    if not child_pid:
        _execute_child()
    else:
        return _execute_parent()
