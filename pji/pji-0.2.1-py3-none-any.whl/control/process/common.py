import os
import pickle
from multiprocessing import Event, Value, Lock
from multiprocessing.synchronize import Event as EventClass
from threading import Thread
from typing import Optional, Tuple, Mapping

from .base import measure_thread, killer_thread, read_all_from_bytes_stream, GeneralProcess
from .decorator import process_setter
from .executor import get_child_executor_func
from ..model import ResourceLimit
from ...utils import ValueProxy


class CommonProcess(GeneralProcess):
    def __init__(self, start_time: float,
                 communicate_event: EventClass, communicate_complete: EventClass,
                 communicate_stdin: ValueProxy, communicate_stdout: ValueProxy, communicate_stderr: ValueProxy,
                 resources: ResourceLimit, process_result_func, lifetime_event: EventClass):
        self.__lock = Lock()
        GeneralProcess.__init__(self, start_time, resources, process_result_func, lifetime_event, self.__lock)

        self.__communicate_event = communicate_event
        self.__communicate_complete = communicate_complete
        self.__communicate_stdin = communicate_stdin
        self.__communicate_stdout = communicate_stdout
        self.__communicate_stderr = communicate_stderr
        self.__communicated = False

    def __communicate(self, stdin: Optional[bytes] = None, wait: bool = True) -> Optional[Tuple[bytes, bytes]]:
        if not self.__communicated:
            self.__communicate_stdin.value = stdin or b''
            self.__communicate_event.set()
            self.__communicated = True

            if wait:
                self.__communicate_complete.wait()
                return self.__communicate_stdout.value, self.__communicate_stderr.value
            else:
                return None
        else:
            raise RuntimeError('Already communicated.')

    def __exit(self):
        if not self.__communicated:
            self.__communicate()
        self._wait_for_end()

    def communicate(self, stdin: Optional[bytes] = None, wait: bool = True) -> Optional[Tuple[bytes, bytes]]:
        with self.__lock:
            return self.__communicate(stdin, wait)

    @property
    def stdin(self) -> Optional[bytes]:
        with self.__lock:
            return self.__communicate_stdin.value

    @property
    def stdout(self) -> Optional[bytes]:
        with self.__lock:
            return self.__communicate_stdout.value

    @property
    def stderr(self) -> Optional[bytes]:
        with self.__lock:
            return self.__communicate_stderr.value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.__lock:
            self.__exit()


# Attention: only real_time_limit will be processed in this function, other limits will be processed in decorator
# noinspection DuplicatedCode,PyIncorrectDocstring,PyUnresolvedReferences
@process_setter
def common_process(args, preexec_fn=None, resources=None,
                   environ: Optional[Mapping[str, str]] = None) -> CommonProcess:
    """
    Create an common process
    :param args: arguments for execution
    :param shell: use shell to execute args
    :param preexec_fn: pre execute function to attach before that
    :param resources: resource limit
    :param environ: environment variables
    :param cwd: new work dir
    :param identification: user and group for execution
    :return: CommonProcess object to do run
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
    def _execute_parent() -> CommonProcess:
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

        # communication thread
        _communicate_initialized, _communicate_event, _communicate_complete = Event(), Event(), Event()
        _communicate_stdin, _communicate_stdout, _communicate_stderr = ValueProxy(), ValueProxy(), ValueProxy()

        def _communicate_func():
            with os.fdopen(stdin_write, 'wb', 0) as fstdin, \
                    os.fdopen(stdout_read, 'rb', 0) as fstdout, \
                    os.fdopen(stderr_read, 'rb', 0) as fstderr:
                _communicate_initialized.set()
                _communicate_event.wait()

                _stdout, _stderr = None, None

                def _read_stdout():
                    nonlocal _stdout
                    _stdout = read_all_from_bytes_stream(fstdout)

                def _read_stderr():
                    nonlocal _stderr
                    _stderr = read_all_from_bytes_stream(fstderr)

                def _write_stdin():
                    try:
                        fstdin.write(_communicate_stdin.value)
                        fstdin.flush()
                    except BrokenPipeError:
                        pass
                    finally:
                        fstdin.close()

                _stdin_thread = Thread(target=_write_stdin)
                _stdout_thread = Thread(target=_read_stdout)
                _stderr_thread = Thread(target=_read_stderr)

                # write stdin into stream
                _stdin_thread.start()
                _stdout_thread.start()
                _stderr_thread.start()

                # waiting for receiving of stdout and stderr
                _stdin_thread.join()
                _stdout_thread.join()
                _stderr_thread.join()

                # set stderr
                _communicate_stdout.value = _stdout
                _communicate_stderr.value = _stderr
                _communicate_complete.set()

                # ending of all the process
                _process_complete.wait()
                _measure_complete.wait()
                _full_lifetime_complete.set()

        _communicate_thread = Thread(target=_communicate_func)

        # waiting for prepare ok
        _executor_prepare_ok.wait()
        with os.fdopen(_exception_get, 'rb', 0) as ef:
            _exception = pickle.load(ef)
            if _exception:
                raise _exception

        # start all the threads and services
        _measure_thread.start()
        _killer_thread.start()
        _communicate_thread.start()

        # wait for all the thread initialized
        _measure_initialized.wait()
        _killer_initialized.wait()
        _communicate_initialized.wait()
        _parent_initialized.set()

        _start_time_ok.wait()
        return CommonProcess(
            start_time=_start_time.value,
            communicate_event=_communicate_event,
            communicate_complete=_communicate_complete,
            communicate_stdin=_communicate_stdin,
            communicate_stdout=_communicate_stdout,
            communicate_stderr=_communicate_stderr,
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
