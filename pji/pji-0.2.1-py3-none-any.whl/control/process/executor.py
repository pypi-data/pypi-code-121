import os
import pickle
import sys
import time
from multiprocessing import Value
from multiprocessing.synchronize import Event as EventClass
from typing import Mapping

import where

from ...utils import args_split


class ExecutorException(Exception):
    def __init__(self, exception):
        self.__exception = exception
        Exception.__init__(self, repr(exception))

    @property
    def exception(self):
        return self.__exception


def get_child_executor_func(args, environ: Mapping[str, str], preexec_fn,
                            executor_prepare_ok: EventClass, exception_pipes,
                            parent_initialized: EventClass,
                            start_time_ok: EventClass, start_time: Value,
                            stdin_pipes, stdout_pipes, stderr_pipes):
    args = args_split(args)
    arg_file = where.first(args[0])

    if not arg_file:
        raise EnvironmentError('Executable {exec} not found.'.format(exec=args[0]))

    stdin_read, stdin_write = stdin_pipes
    stdout_read, stdout_write = stdout_pipes
    stderr_read, stderr_write = stderr_pipes
    exception_read, exception_write = exception_pipes

    # noinspection DuplicatedCode
    def _execute_child():
        os.setsid()  # become the group leader

        os.close(stdin_write)
        sys.stdin = sys.__stdin__
        os.dup2(stdin_read, sys.stdin.fileno())

        os.close(stdout_read)
        sys.stdout = sys.__stdout__
        os.dup2(stdout_write, sys.stdout.fileno())

        os.close(stderr_read)
        sys.stderr = sys.__stderr__
        os.dup2(stderr_write, sys.stderr.fileno())

        _exception = None
        try:
            if preexec_fn is not None:
                preexec_fn()
        except Exception as err:
            _exception = err

        os.close(exception_read)
        with os.fdopen(exception_write, 'wb', 0) as ef:
            if _exception is not None:
                pickle.dump(ExecutorException(_exception), ef)
            else:
                pickle.dump(None, ef)
        executor_prepare_ok.set()

        if _exception is None:
            parent_initialized.wait()
            start_time.value = time.time()
            start_time_ok.set()

            os.execvpe(arg_file, args, environ)

    return _execute_child
