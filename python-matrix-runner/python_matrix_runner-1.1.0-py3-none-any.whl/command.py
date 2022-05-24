# -*- coding: utf-8 -*-

import logging
import shutil

from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from subprocess import Popen, PIPE, TimeoutExpired
from tempfile import gettempdir
from threading import Thread
from time import perf_counter, time, sleep
from typing import Callable, List, Union, AnyStr, Optional, IO, Iterable, Dict

import psutil

from filelock import FileLock
from psutil import AccessDenied, NoSuchProcess, TimeoutExpired as PSTimeoutExpired

from ._helper import partial_with_inspect
from .report import ReportFilter

CommandFunction = Callable[..., List]


class Result:
    """Execution result capsule."""

    def __init__(self, extra=None):
        self.exit_status = None
        self.success = False
        self.output = StringIO()
        self.test_report = None
        self.start_time = 0
        self.end_time = 0
        self.start_perf_counter = 0
        self.end_perf_counter = 0
        self._extra = extra

    @contextmanager
    def capture(self, proc: Popen):
        """Context manager for capturing process output."""
        output_handler = logging.StreamHandler(self.output)
        logger = logging.getLogger(f'{self.__class__.__name__}:{proc.pid}')
        logger.addHandler(output_handler)
        logger.setLevel(logging.INFO)

        def capture_output(stream: IO, loglevel: int):
            for line in stream:
                line = line.rstrip()
                if line:
                    logger.log(loglevel, line, extra=self._extra)

        thout = Thread(target=capture_output, args=(proc.stdout, logging.INFO), daemon=True)
        therr = Thread(target=capture_output, args=(proc.stderr, logging.ERROR), daemon=True)
        thout.start()
        therr.start()

        self.log_start()
        try:
            yield self
        finally:
            self.log_end()

            thout.join()
            therr.join()

    def log_start(self):
        """Record execution start time stamp."""
        self.start_time = time()
        self.start_perf_counter = perf_counter()

    def log_end(self):
        """Record execution end time stamp."""
        self.end_time = time()
        self.end_perf_counter = perf_counter()


class Command:
    """Command wrapper"""
    _exit_code: Union[int, Callable[[int], bool]]

    def __init__(self, fn: Callable[[], List], exit_code: Union[int, Iterable[int], Callable[[int], bool]] = 0,
                 needs_shell: bool = False, encoding: str = 'utf-8', exclusive: bool = False,
                 timeout: Optional[float] = None, retry: Optional[int] = 1, rest_period: Optional[float] = None,
                 test_report: Optional[ReportFilter] = None):  # pylint: disable=too-many-arguments
        self._fn = fn
        self._exit_code = exit_code
        self._needs_shell = needs_shell
        self._encoding = encoding
        self._exclusive = exclusive
        self._timeout = timeout
        self._retry = max(retry, 1)
        self._rest_period = rest_period
        self._test_report = test_report
        self.extra = {'cmd':  f":{fn.__name__}"}

    def __call__(self):
        cmdline = self._fn()
        result = CommandResult(self, cmdline)
        self._execute(cmdline, result)
        return result

    def __getattr__(self, item):
        if isinstance(self._fn, partial_with_inspect):
            return self._fn.__getattr__(item)
        raise AttributeError(f"'Command' object has no attribute '{item}'")

    @staticmethod
    def _resolve_cmdlineel(elem) -> str:
        """Resolve command line element."""
        if isinstance(elem, str):
            return elem
        if isinstance(elem, Path):
            return str(elem.resolve())
        return str(elem)

    def _resolve_cmdline(self, cmdline: List) -> List[str]:
        """Resolve command line."""
        cmdline = [Command._resolve_cmdlineel(el) for el in cmdline]
        cmd = shutil.which(cmdline[0])
        if cmd:
            cmdline[0] = cmd
        else:
            logging.error("Command '%s' not found in current environment.", cmdline[0], extra=self.extra)
        return cmdline

    # pylint: disable=too-many-arguments,too-many-statements
    @staticmethod
    def _popen(cmdline: List[str], result: Result, needs_shell: bool = False, encoding: str = 'utf8',
               timeout: Optional[float] = None, extra: Optional[Dict[str, str]] = None) -> int:

        @contextmanager
        def observe(process):
            parent = psutil.Process(process.pid)
            children = {parent}

            def observer():
                try:
                    logging.debug("Observing process %s [pid %d]", parent.name(), parent.pid, extra=extra)
                    while parent.is_running():
                        sleep(1)
                        try:
                            new = set(parent.children(recursive=True)) - children
                            children.update(new)
                            for child in new:
                                logging.debug("Detected new subprocess %s [pid %d]",
                                              child.name(), child.pid, extra=extra)
                        except NoSuchProcess:
                            pass
                except NoSuchProcess:
                    pass

            worker = Thread(target=observer, daemon=True)
            worker.start()

            try:
                yield
            finally:
                if parent.is_running():
                    try:
                        logging.error("Process %s [pid %d] did not terminate!", parent.name(), parent.pid, extra=extra)
                        parent.kill()
                        parent.wait(timeout=10)
                    except NoSuchProcess:
                        pass
                    except PSTimeoutExpired:
                        logging.critical("Unable to kill process %s [pid %d]!", parent.name(), parent.pid, extra=extra)
                    # Workaround for zombie processes
                    # Zombie processes are assumed as still running,
                    # hence the worker (observer) doesn't terminate.
                    parent._gone = True  # pylint: disable=protected-access
                worker.join()

                logging.debug("Waiting for all subprocesses to terminate...", extra=extra)
                try:
                    _, alive = psutil.wait_procs(children, timeout=1)
                    for pid in alive:
                        logging.error("Subprocess %s [pid %d] did not terminate!", pid.name(), pid.pid, extra=extra)
                        try:
                            pid.kill()
                            pid.wait(timeout=10)
                        except NoSuchProcess:
                            pass
                        except PSTimeoutExpired:
                            logging.critical("Unable to kill subprocess %s [pid %d]!", pid.name(), pid.pid, extra=extra)
                except NoSuchProcess:
                    pass
                except AccessDenied as exc_info:
                    logging.warning("Waiting for subprocesses failed!", extra=extra)
                    logging.debug("Exception Info", exc_info=exc_info, extra=extra)

        if needs_shell:
            for idx, cmd in enumerate(cmdline):
                if " " in cmd:
                    cmdline[idx] = '"'+cmd.replace('"', '\\"')+'"'
            cmdline = " ".join(cmdline)

        with Popen(cmdline, stdout=PIPE, stderr=PIPE, shell=needs_shell, encoding=encoding) as proc, \
                result.capture(proc), observe(proc):
            try:
                result.exit_status = proc.wait(timeout)
            except TimeoutExpired as e:
                logging.debug("Command timeout expired, terminating...")
                proc.terminate()
                result.exit_status = TimeoutError(e)
                raise TimeoutError() from e

        return result.exit_status

    def _is_success(self, rc: int) -> bool:
        if isinstance(self._exit_code, Callable):
            return self._exit_code(rc)
        if isinstance(self._exit_code, Iterable):
            return rc in self._exit_code
        return rc == self._exit_code

    def _execute_with_timeout(self, cmdline: List[AnyStr], result: Result) -> bool:
        try:
            if self._timeout:
                logging.info("... with timeout of %d seconds", self._timeout, extra=self.extra)

            rc = Command._popen(cmdline, result, needs_shell=self._needs_shell, encoding=self._encoding,
                                timeout=self._timeout, extra=self.extra)
            result.success = self._is_success(rc)

            if result.success:
                logging.warning("%s succeeded with exit code %d", cmdline[0], rc, extra=self.extra)
            else:
                logging.error("%s failed with exit code %d", cmdline[0], rc, extra=self.extra)

        except TimeoutError:
            logging.error("Execution timed out!", extra=self.extra)

        return result.success

    def _execute_with_rest(self, cmdline: List[AnyStr], result: Result) -> bool:
        if self._rest_period:
            logging.info("... resting for %d seconds", self._rest_period, extra=self.extra)
            sleep(self._rest_period)

        return self._execute_with_timeout(cmdline, result)

    def _execute_with_retry(self, cmdline: List[AnyStr], result: Result) -> bool:
        tries = self._retry
        for i in range(0, tries):
            logging.log(logging.DEBUG if not i else logging.WARN, "... with retry %d/%d", i+1, tries, extra=self.extra)
            success = self._execute_with_rest(cmdline, result)
            if success:
                break
        return success

    def _execute_with_lock(self, cmdline: List[AnyStr], result: Result) -> bool:
        @contextmanager
        def lock(cmd):
            _lock = None

            if self._exclusive:
                lock_path = Path(gettempdir(), f"{Path(cmd).name}.lock")
                # https://github.com/tox-dev/py-filelock/issues/102
                # pylint: disable=abstract-class-instantiated
                _lock = FileLock(lock_path)
                _lock.acquire(poll_intervall=10.0)

            try:
                yield _lock
            finally:
                if self._exclusive:
                    _lock.release()

        with lock(cmdline[0]):
            return self._execute_with_retry(cmdline, result)

    def _execute(self, cmdline: List[AnyStr], result: Result) -> bool:
        cmdline = self._resolve_cmdline(cmdline)
        logging.warning(" ".join(cmdline), extra=self.extra)

        success = self._execute_with_lock(cmdline, result)

        if self._test_report:
            if isinstance(self._test_report, Callable):
                self._test_report = self._test_report(result)
            result.test_report = self._test_report.apply(result)

        return success


class CommandResult(Result):
    """Full command result capsule."""
    def __init__(self, command: Command, cmdline: List):
        super().__init__(extra=command.extra)
        self.command = command
        self.cmdline = cmdline
