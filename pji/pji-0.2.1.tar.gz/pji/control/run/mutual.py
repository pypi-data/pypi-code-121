import importlib
import io
import os
import sys
import time
from multiprocessing import Process, Event
from threading import Thread
from typing import Callable

from .encoding import _auto_encode, _try_write
from ..model import TimingContent, RunResult
from ..process import interactive_process
from ...utils import eclosing


class MutualStdout(TimingContent):
    pass


class MutualStderr(TimingContent):
    pass


_INTERACT_FUNC = Callable[[], None]


def _load_func_from_str(source: str) -> _INTERACT_FUNC:
    _split = source.split(':')
    if len(_split) == 2:
        _module_name, _func_name = _split
        _module = importlib.import_module(_module_name)
        _func = getattr(_module, _func_name)
        if hasattr(_func, '__call__'):
            return _func
        else:
            raise TypeError('Callable expected but {actual} found.'.format(actual=repr(type(_func).__name__)))
    else:
        raise ValueError('Invalid mutual function - {func}.'.format(func=repr(source)))


def _load_func(func) -> _INTERACT_FUNC:
    if func is None:
        return lambda: None
    elif hasattr(func, '__call__'):
        return func
    elif isinstance(func, str):
        return _load_func_from_str(func)
    else:
        raise TypeError('Callable or str source expected but {actual} found.'.format(actual=repr(type(func).__name__)))


def mutual_run(args, shell: bool = False, stdin=None, stdout=None, stderr=None,
               environ=None, cwd=None, resources=None, identification=None) -> RunResult:
    """
    Create an mutual process with stream
    :param args: arguments for execution
    :param shell: use shell to execute args
    :param stdin: stdin interaction function (none means nothing)
    :param stdout: stdout stream (none means nothing)
    :param stderr: stderr stream (none means nothing)
    :param environ: environment variables
    :param cwd: new work dir
    :param resources: resource limit
    :param identification: user and group for execution
    :return: run result of this time
    """
    stdin = _load_func(stdin)

    stdout_need_close = not stdout
    stdout = stdout or io.BytesIO()

    stderr_need_close = not stderr
    stderr = stderr or io.BytesIO()

    with eclosing(stdout, stdout_need_close) as stdout, \
            eclosing(stderr, stderr_need_close) as stderr:
        mutual_stdout_get, mutual_stdout_put = os.pipe()
        mutual_stdin_get, mutual_stdin_put = os.pipe()
        mutual_stderr_get, mutual_stderr_put = os.pipe()

        _mutual_initialize_ok = Event()
        _prepare_ok = Event()

        # noinspection DuplicatedCode
        def _launch_mutual():
            os.close(mutual_stdin_put)
            # sys.stdin = sys.__stdin__  # this stdin is closed, ValueError: I/O operation on closed file
            os.dup2(mutual_stdin_get, sys.stdin.fileno())

            os.close(mutual_stdout_get)
            sys.stdout = sys.__stdout__
            os.dup2(mutual_stdout_put, sys.stdout.fileno())

            os.close(mutual_stderr_get)
            sys.stderr = sys.__stderr__
            os.dup2(mutual_stderr_put, sys.stderr.fileno())

            _mutual_initialize_ok.set()
            _prepare_ok.wait()
            stdin()

        _mutual_process = Process(target=_launch_mutual)

        with interactive_process(
                args=args, shell=shell,
                environ=environ, cwd=cwd,
                resources=resources, identification=identification,
        ) as ip:
            _mutual_process.start()
            os.close(mutual_stdin_get)
            os.close(mutual_stdout_put)
            os.close(mutual_stderr_put)
            _mutual_initialize_ok.wait()

            _stdout_list = []
            _stderr_list = []

            with os.fdopen(mutual_stdin_put, 'wb', 0) as f_mutual_stdin, \
                    os.fdopen(mutual_stdout_get, 'rb', 0) as f_mutual_stdout, \
                    os.fdopen(mutual_stderr_get, 'rb', 0) as f_mutual_stderr:
                def _load_output_from_ip():
                    _mutual_close_stdin = False
                    for _time, _tag, _line in ip.output_yield:
                        if _tag == 'stdout':
                            if not _mutual_close_stdin:
                                _mutual_initialize_ok.wait()
                                try:
                                    f_mutual_stdin.write(_line + _auto_encode(os.linesep))
                                    f_mutual_stdin.flush()
                                except BrokenPipeError:
                                    _mutual_close_stdin = True
                        elif _tag == 'stderr':
                            _stderr_list.append((time.time() - ip.start_time, _line))

                    f_mutual_stdin.close()

                def _load_stdout_from_mutual():
                    _mutual_initialize_ok.wait()
                    for _line in f_mutual_stdout:
                        try:
                            ip.print_stdin(_line.rstrip(b'\r\n'))
                        except BrokenPipeError:
                            break
                    ip.close_stdin()

                def _load_stderr_from_mutual():
                    _mutual_initialize_ok.wait()
                    for _line in f_mutual_stderr:
                        _stdout_list.append((time.time() - ip.start_time, _line.rstrip(b'\r\n')))

                _threads = [Thread(target=_func) for _func in
                            [_load_output_from_ip, _load_stdout_from_mutual, _load_stderr_from_mutual]]
                for _item in _threads:
                    _item.start()
                _prepare_ok.set()

                for _item in _threads:
                    _item.join()

            _try_write(stdout, MutualStdout(_stdout_list).dumps())
            _try_write(stderr, MutualStderr(_stderr_list).dumps())

            return ip.result
