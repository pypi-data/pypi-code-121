# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod
from atexit import register
from configparser import NoSectionError, NoOptionError
from glob import glob
from os import walk
from os.path import join, exists, splitext
from shutil import rmtree
from sys import stdout
from typing import Union

from .callstack import get_traceback, get_caller, get_level
from ..config import cfg
from ..constants import RECURSIVE_THREAD_LOCK, TRACEBACK, FRAME, ROW
from ..handles import FileHandle
from ..utils import timestamp, today, make_dirs, archive


@register
def _cleanup():
    try:
        target = cfg.get("FOLDERS", "logger")
    except (NoSectionError, NoOptionError):
        pass
    else:
        folders = _scan(target)
        for folder, files in folders:
            archive(f"{folder}.zip", files)
            rmtree(folder)


def _scan(target: str):
    current_month = today().strftime("%B").lower()
    for root, folders, files in walk(target):
        if (root == target) or (len(folders) == 0):
            continue
        for folder in folders:
            if folder == current_month:
                continue
            folder = join(root, folder)
            files = join(folder, "*.log")
            yield folder, (file for file in glob(files))


class AbstractHandler(ABC):
    """Base handle for all logging classes."""

    @abstractmethod
    def emit(self, *args, **kwargs):
        raise NotImplementedError


class RowFactory(object):
    """`ROW` builder."""

    @staticmethod
    def info(exception: Union[BaseException, tuple, bool]) -> Union[TRACEBACK, FRAME]:
        """
        Get information about the most recent exception caught by an except clause
        in the current stack frame or in an older stack frame.
        """
        if exception is not None:
            try:
                return get_traceback(exception)
            except AttributeError:
                pass

        return get_caller(5)

    @staticmethod
    def join(message: str, frame: Union[TRACEBACK, FRAME]) -> str:
        """Attach traceback info to `message` if `frame` is an exception."""
        if isinstance(frame, TRACEBACK) is True:
            message = f"{message} Traceback: {frame.message}"
        return message

    def build(self, message: str, exception: Union[BaseException, tuple, bool]) -> ROW:
        """Construct and return a new ROW object."""
        frame = self.info(exception)
        return ROW(
            time=timestamp(),
            level=get_level(3),
            file=frame.file,
            line=frame.line,
            code=frame.code,
            message=self.join(message, frame)
        )


class FormatFactory(object):
    """`ROW` formatter."""

    @staticmethod
    def _format(row: ROW) -> str:
        """Construct and return a string from the `row` object."""
        return f"[{row.time}] - {row.level} - <{row.file}, {row.line}, {row.code}>: {row.message}"

    def build(self, row: ROW) -> str:
        """Construct and return a new ROW object."""
        return self._format(row)


class AbstractStream(AbstractHandler):
    """Logging stream handler with thread lock management."""

    def emit(self, record: str):
        """Acquire a thread lock and write the log record."""
        with RECURSIVE_THREAD_LOCK:
            self.write(record)

    @abstractmethod
    def write(self, *args, **kwargs):
        raise NotImplementedError


class StdHandler(AbstractStream):
    """Simple `stdout` handler."""

    @staticmethod
    def write(record: str):
        """Write the log record to console and flush the handle."""
        stdout.write(f"{record}\n")
        stdout.flush()


class FileHandler(AbstractStream):
    """File handler that writes log messages to disk."""

    @staticmethod
    def _make_folder_path():
        dt = today()
        path = join(
            cfg.get("FOLDERS", "logger"),
            str(dt.year),
            dt.strftime("%B").lower(),
        )
        make_dirs(path)
        return path

    def __init__(self):
        self._file_path = None
        self._folder_path = None
        self._name = None
        self._ext = None
        self._idx = None
        self._size = 0

    def write(self, record: str):
        file_path = self.get_path()
        with FileHandle(file_path, "a", encoding="UTF-8") as file_handle:
            file_handle.write(f"{record}\n")
            self._size = file_handle.tell()

    def get_path(self):
        if self._file_path is None:
            self._file_path = self.make_file_path()
        elif self._size >= ((1024 * 1024) - 1024):
            self._file_path = self.make_file_path()
        return self._file_path

    def get_folder(self):
        if self._folder_path is None:
            self._folder_path = self._make_folder_path()
        return self._folder_path

    def get_name(self):
        if (self._name is None) and (self._ext is None):
            self._name, self._ext = splitext(cfg.get("LOGGER", "name"))
        return f"{today()}_{self._name}.{self.get_idx()}.{self._ext.strip('.')}"

    def get_idx(self):
        if self._idx is None:
            self._idx = 0
        else:
            self._idx += 1
        return self._idx

    def make_file_path(self):
        file_path = join(self.get_folder(), self.get_name())
        if exists(file_path) is True:
            return self.make_file_path()
        return file_path


class StreamHandler(AbstractHandler):

    @staticmethod
    def _handlers(target: str) -> AbstractStream:
        handlers = {
            "file": FileHandler,
            "console": StdHandler,
        }
        handler = handlers.get(target)
        return handler()

    def __init__(self):
        self._handler = None

    @property
    def handler(self) -> AbstractStream:
        if self._handler is None:
            self._handler = self._handlers(cfg.get("LOGGER", "handler"))
        return self._handler

    def emit(self, message: str):
        self.handler.emit(message)


class AbstractLogger(AbstractHandler):
    """Base logging handle."""

    def __init__(self):
        self._factory = RowFactory()
        self._format = FormatFactory()
        self._stream = StreamHandler()

    def emit(self, message: str, exception: Union[BaseException, tuple, bool]):
        """Construct and stream the log message."""
        with RECURSIVE_THREAD_LOCK:
            row = self._factory.build(message, exception)
            message = self._format.build(row)
            self._stream.emit(message)


class Logger(AbstractLogger):
    """Logging class with thread and file lock ability."""

    def debug(self, message: str, exception: Union[BaseException, tuple, bool] = None):
        """
        Log a message with level `DEBUG`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        if cfg.getboolean("LOGGER", "debug") is True:
            self.emit(message=message, exception=exception)

    def info(self, message: str, exception: Union[BaseException, tuple, bool] = None):
        """
        Log a message with level `INFO`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        self.emit(message=message, exception=exception)

    def warning(self, message: str, exception: Union[BaseException, tuple, bool] = None):
        """
        Log a message with level `WARNING`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        self.emit(message=message, exception=exception)

    def error(self, message: str, exception: Union[BaseException, tuple, bool] = None):
        """
        Log a message with level `ERROR`.

        :param message: The message to be logged.
        :param exception: Add exception info to the log message.
        """
        self.emit(message=message, exception=exception)
