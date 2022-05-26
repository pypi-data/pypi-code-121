"""Customized log handler for CoSApp simulation."""
import io
import logging
import sys
from contextlib import contextmanager
from enum import Enum, IntEnum
from logging.handlers import RotatingFileHandler
from numbers import Number
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Iterable,
    List,
    Mapping,
    Optional,
    Type,
    Union,
)

from cosapp.utils.helpers import check_arg


root_logger = logging.getLogger()
logger = logging.getLogger(__name__)


DEFAULT_STREAM = object()


class LogFormat(Enum):
    """Expected format of the log message.
    
    RAW : Raw text
    """

    RAW = 0


class LogLevel(IntEnum):
    """CoSApp log level.
    
    FULL_DEBUG : Detailed debug log
    DEBUG : Debug log
    INFO : Information log
    WARNING : Warning log
    ERROR : Error log
    CRITICAL : Critical log
    """

    FULL_DEBUG = logging.DEBUG - 1
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


VERBOSE_LEVEL = LogLevel.DEBUG


class HandlerWithContextFilters:
    """Add method to handlers for CoSApp log message."""

    def __init__(self):
        self.contextual_filters: List[FilterWithContext] = list()

    def _set_contextual_filters(self, filters: Iterable[logging.Filter]) -> None:
        self.contextual_filters = list(
            filter(lambda f: isinstance(f, FilterWithContext), filters)
        )

    def log(
        self,
        level: LogLevel,
        msg: str,
        name: str = "",
        fn: str = "",
        lino: int = 0,
        args: tuple = (),
        exc_info=None,
        func: Optional[str] = None,
        extra: Optional[Mapping[str, Any]] = None,
        sinfo: Optional[str] = None,
    ) -> None:
        """Helper function to publish log message with this handler.

        Parameters
        ----------
        level : LogLevel
            The numeric level of the logging event (one of DEBUG, INFO etc.) Note that
            this is converted to two attributes of the LogRecord: levelno for the numeric
            value and levelname for the corresponding level name.
        msg : str
            The event description message, possibly a format string with placeholders
            for variable data.
        name : str, optional
            The name of the logger used to log the event represented by this LogRecord.
            Note that this name will always have this value, even though it may be
            emitted by a handler attached to a different (ancestor) logger.
        pathname : str, optional
            The full pathname of the source file where the logging call was made.
        lineno : int, optional
            The line number in the source file where the logging call was made.
        args : tuple
            Variable data to merge into the msg argument to obtain the event description.
        exc_info : optional
            An exception tuple with the current exception information, or None if no
            exception information is available.
        func : str, optional
            The name of the function or method from which the logging call was invoked.
        sinfo: str, optional
            A text string representing stack information from the base of the stack in
            the current thread, up to the logging call.
        """
        if isinstance(self, logging.Handler):
            if self.level <= level:
                record = logger.makeRecord(
                    name or logger.name,
                    level,
                    fn,
                    0,
                    msg,
                    args,
                    exc_info,
                    func,
                    extra,
                    sinfo,
                )
                self.handle(record)
        else:
            raise NotImplementedError(f"{self} cannot handle log messages.")

    def needs_handling(self, record: logging.LogRecord) -> bool:
        """Test the record to see if it needs to be processed or not.
        
        Parameters
        ----------
        record : logging.LogRecord
            Log record

        Returns
        -------
        bool
            Is the record to be processed?
        """
        context = getattr(record, "context", None)
        result = True
        if context is not None:
            activation = getattr(record, "activate", None)

            if activation == True:
                for f in self.contextual_filters:
                    f.current_context = context

            result = False
            if isinstance(context, LoggerContext):
                result = context.log_debug_message(self, record)

            if activation == False:
                for f in self.contextual_filters:
                    f.current_context = context

        return result


class LoggerContext:
    """Interface for context object to connect to the logging system."""

    __slots__ = ()

    CONTEXT_ENTER_MESSAGE: ClassVar[str] = "Entering"
    CONTEXT_EXIT_MESSAGE: ClassVar[str] = "Exiting"

    @contextmanager
    def log_context(self, suffix: str = "") -> None:
        """Set this object as the context for the logger.

        Parameters
        ----------
        suffix : str, optional
            Suffix text to append to the log message
        """
        try:
            msg = f"{LoggerContext.CONTEXT_ENTER_MESSAGE} {self!r}{suffix}"
            logger.log(VERBOSE_LEVEL, msg, extra={"activate": True, "context": self})
            yield
        finally:
            msg = f"{LoggerContext.CONTEXT_EXIT_MESSAGE} {self!r}{suffix}"
            logger.log(VERBOSE_LEVEL, msg, extra={"activate": False, "context": self})

    def log_debug_message(
        self,
        handler: HandlerWithContextFilters,
        record: logging.LogRecord,
        format: LogFormat = LogFormat.RAW,
    ) -> bool:
        """Callback method on the context object to log more detailed information.

        This method will be called by the log handler when :py:meth:`~cosapp.utils.logging.LoggerContext.log_context`
        is active if the logging level is lower or equals to VERBOSE_LEVEL. It allows
        the object to send additional log message to help debugging a simulation.

        Parameters
        ----------
        handler : HandlerWithContextFilters
            Log handler on which additional message should be published.
        record : logging.LogRecord
            Log record
        format : LogFormat
            Format of the message

        Returns
        -------
        bool
            Should the provided records be logged?
        """
        return True


class FilterWithContext(logging.Filter):
    """Interface to add a context on an object."""

    def __init__(self):
        super().__init__()
        self.__context = None

    @property
    def current_context(self) -> LoggerContext:
        """LoggerContext : Current context"""
        return self.__context

    @current_context.setter
    def current_context(self, context: LoggerContext) -> None:
        self.__context = context
        self._set_context()

    def _set_context(self) -> None:
        """Hook method called by current_context setter."""
        pass


class TimeFilter(FilterWithContext):
    """Log record filter depending on the current time of a context.
    
    Parameters
    ----------
    start_time : Number
        Time from which debug log will be recorded; default all time steps
    """

    def __init__(self, start_time: Number):
        super().__init__()
        self.__start_time = start_time
        self.__current_time = start_time

    def _set_context(self) -> None:
        """Update current time with the one of the context."""
        self.__current_time = getattr(self.current_context, "time", self.__current_time)

    def filter(self, record: logging.LogRecord) -> int:
        """Is the specified record to be logged? Returns zero for no, nonzero for yes.
        If deemed appropriate, the record may be modified in-place by this method.
        
        Parameters
        ----------
        record : logging.LogRecord
            Log record to test
        
        Returns
        -------
        int
            Non-zero if the record is to be logged.
        """
        return int(
            record.levelno > VERBOSE_LEVEL or self.__current_time >= self.__start_time
        )


class ContextFilter(FilterWithContext):
    def __init__(self, context: Optional[str] = None):
        super().__init__()

        self.__filter_context: Optional[str] = context  # Filter context
        self.__active: bool = False
        self.__context_type: Optional[Type] = None

        # Set context filter logic
        if self.__filter_context is None:
            self._context_filter = lambda record: 1
        else:
            self._context_filter = lambda record: int(
                record.levelno > VERBOSE_LEVEL or self.__active
            )

    def filter(self, record: logging.LogRecord) -> int:
        """Is the specified record to be logged? Returns zero for no, nonzero for yes.
        If deemed appropriate, the record may be modified in-place by this method.
        
        Parameters
        ----------
        record : logging.LogRecord
            Log record to test
        
        Returns
        -------
        int
            Non-zero if the record is to be logged.
        """
        return self._context_filter(record)

    def _set_context(self) -> None:
        context = self.current_context
        context_name = getattr(context, "name", None)

        if self.__context_type is not None:
            if context_name == self.__filter_context:
                self.__context_type = None
                self.__active = False
            else:
                self.__active = isinstance(context, self.__context_type)

        elif context_name == self.__filter_context:
            from cosapp.drivers import Driver
            from cosapp.systems import System

            if isinstance(context, System):
                self.__context_type = System
            elif isinstance(context, Driver):
                self.__context_type = Driver
            else:
                self.__context_type = type(context)
            self.__active = True


class FileLogHandler(RotatingFileHandler, HandlerWithContextFilters):
    """Special RotatingFileHandler for CoSApp log message.

    Parameters
    ----------
    filename : str or Path, optional
        Log filename; default "cosapp_trace.log"
    backupCount : int, optional
        Number of backup log files; default 5
    encoding : str, optional
        File encoding to be enforced
    """

    def __init__(
        self,
        filename: Union[str, Path] = "cosapp_trace.log",
        backupCount: int = 5,
        encoding: Optional[str] = None,
    ) -> None:
        RotatingFileHandler.__init__(
            self, filename, backupCount=backupCount, encoding=encoding, delay=True
        )
        HandlerWithContextFilters.__init__(self)

    def addFilter(self, filter):
        """Adds the specified filter filter to this handler."""
        super().addFilter(filter)
        self._set_contextual_filters(self.filters)

    def removeFilter(self, filter):
        """Removes the specified filter filter from this handler."""
        super().removeFilter(filter)
        self._set_contextual_filters(self.filters)

    def handle(self, record: logging.LogRecord) -> bool:
        """Conditionally emits the specified logging record, depending on filters which
        may have been added to the handler. Wraps the actual emission of the record
        with acquisition/release of the I/O thread lock.
        
        Parameters
        ----------
        record : logging.LogRecord
            Log record

        Returns
        -------
        bool
            Is the record processed?
        """
        return self.needs_handling(record) and super().handle(record)


class StreamLogHandler(logging.StreamHandler, HandlerWithContextFilters):
    """Special StreamHandler for CoSApp log message."""

    def __init__(self, stream: io.TextIOBase = DEFAULT_STREAM) -> None:
        if stream is DEFAULT_STREAM:
            stream = sys.stdout
        logging.StreamHandler.__init__(self, stream=stream)
        HandlerWithContextFilters.__init__(self)

    def addFilter(self, filter):
        """Adds the specified filter filter to this handler."""
        super().addFilter(filter)
        self._set_contextual_filters(self.filters)

    def removeFilter(self, filter):
        """Removes the specified filter filter from this handler."""
        super().removeFilter(filter)
        self._set_contextual_filters(self.filters)

    def handle(self, record: logging.LogRecord) -> bool:
        """Conditionally emits the specified logging record, depending on filters which
        may have been added to the handler. Wraps the actual emission of the record
        with acquisition/release of the I/O thread lock.
        
        Parameters
        ----------
        record : logging.LogRecord
            Log record

        Returns
        -------
        bool
            Is the record processed?
        """
        return self.needs_handling(record) and super().handle(record)


def rollover_logfile() -> None:
    """Rollover logfile of CoSApp LogHandler."""
    root_logger = logging.getLogger()

    for handler in root_logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.doRollover()


def set_log(
    filename: Union[str, Path, None] = "cosapp_trace.log",
    stream: Optional[io.TextIOBase] = DEFAULT_STREAM,
    level: int = LogLevel.INFO,
    context: Optional[str] = None,
    start_time: Optional[Number] = None,
    format: str = "%(message)s",
    encoding: Optional[str] = None,
    backupCount: int = 5,
) -> None:
    """Set the CoSApp simulation log behavior.

    If `backupCount` is nonzero, at most `backupCount` files will be kept, and if more
    would be created when rollover occurs, the oldest one is deleted.

    The system will save old log files by appending extensions to the filename. The
    extensions are date-and-time based, using the strftime format `%Y-%m-%d_%H-%M-%S`.

    By default the log messages are written to a file (specified by its `filename`) and
    to a stream. Set either `filename` or `stream` to deactivate the corresponding log
    handler.

    Parameters
    ----------
    filename : str or Path or None, optional
        Log filename; default "cosapp_trace.log"
    stream : io.TextIOBase or None, optional
        Log stream; default ``sys.stdout``
    level : int or LogLevel, optional
        Log level; default LogLevel.INFO
    context : str or None, optional
        Context on which to focus the log message; default None
    start_time : Number or None, optional
        Time from which debug log will be recorded; default all time steps
    format : str, optional
        Log record format; default "%(message)s" - for the available attributes (see https://docs.python.org/3/library/logging.html#logrecord-attributes)
    encoding : str, optional
        File encoding to be enforced
    backupCount : int, optional
        Number of backup log files; default 5
    """
    nonetype = type(None)
    check_arg(filename, "filename", (str, Path, nonetype))
    if stream is not DEFAULT_STREAM:
        check_arg(stream, "stream", (io.TextIOBase, nonetype))
    check_arg(level, "level", (int, LogLevel))
    check_arg(context, "context", (str, nonetype))
    check_arg(start_time, "start_time", (Number, nonetype))
    check_arg(format, "format", str)
    check_arg(encoding, "encoding", (str, nonetype))
    check_arg(backupCount, "backupCount", int, lambda v: v >= 0)

    root_logger.setLevel(level)

    for handler in root_logger.handlers[:]:
        if isinstance(handler, HandlerWithContextFilters):
            handler.close()  # Be sure to close the file descriptor
            root_logger.removeHandler(handler)

    def add_handler(h):
        fmt = logging.Formatter(format)
        h.setFormatter(fmt)
        h.setLevel(level)
        if context is not None:
            h.addFilter(ContextFilter(context))
        if start_time is not None:
            h.addFilter(TimeFilter(start_time))
        root_logger.addHandler(h)

    handlers = list()
    if filename is not None:
        handlers.append(
            FileLogHandler(filename, backupCount=backupCount, encoding=encoding)
        )

    if stream is not None:
        handlers.append(StreamLogHandler(stream))

    for handler in handlers:
        add_handler(handler)

    if len(handlers) == 0:
        logger.warning("No CoSApp log handlers added.")
