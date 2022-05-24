# from __future__ import annotations
# Above is temporarily commented to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
# import inspect
import logging as lg
import os
from typing import Optional, Any
from pythagoras.utils import *

# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
class LoggableObject:
    pass

class LoggableObject:
    """ Base class for types that are able to log events/messages.

    A wrapper for standard Python logging functionality
    that offers object-level logging granularity.
    """

    root_logger_name: str
    reveal_identity: bool
    reveal_calling_method: bool
    selflog_prefix: str = "SELF_LOG: "
    logging_level: Optional[int] = None

    def __init__(self
             , *
             , root_logger_name: str = "pythagoras"
             , reveal_logger_identity: bool = True
             , reveal_calling_method: bool = False
             , logging_level: int = lg.WARNING
             , logging_handler: lg.Handler = None
             , logging_formatter: lg.Formatter =  None
             ) -> None:
        super().__init__()
        assert len(root_logger_name), "root_logger_name can not be empty"

        if logging_handler is None:
            logging_handler = lg.StreamHandler()

        if  logging_formatter is None:
            logging_formatter = lg.Formatter(
                '%(asctime)s %(name)s %(levelname)s: %(message)s',
                datefmt="%I:%M:%S")

        self.root_logger_name = root_logger_name
        self.reveal_identity = reveal_logger_identity
        self.reveal_calling_method = reveal_calling_method
        self.logging_level = logging_level
        self.update_logger(
            logging_level, logging_handler, logging_formatter)

    def logger(self
               , suffix:str = ""
               , extend_logger_name:bool = True):
        logger_name = self.root_logger_name
        if self.reveal_identity:
            logger_name += "." + type(self).__qualname__
            logger_name += "." + str(id(self))
            if extend_logger_name:
                self_names = NeatStr.object_names(self)
                if len(self_names):
                    logger_name += "." + self_names
        if len(suffix):
            logger_name += "." + suffix
        resulting_logger = lg.getLogger(logger_name)
        return resulting_logger

    def __str__(self) -> str:
        description = f"{self.logger()}"
        description = description[1:-1]
        return description

    def update_logger(self
            , new_logging_level: int
            , new_logging_handler: lg.Handler = None
            , new_logging_formatter: lg.Formatter = None
            ) -> LoggableObject:
        current_logger = self.logger(extend_logger_name = False)

        if new_logging_level is not None:
            current_logger.setLevel(new_logging_level)

        if new_logging_handler is not None:
            if new_logging_level is not None:
                new_logging_handler.setLevel(new_logging_level)
            if new_logging_formatter is not None:
                new_logging_handler.setFormatter(new_logging_formatter)

            for h in current_logger.handlers:
                if str(h) == str(new_logging_handler):
                    current_logger.removeHandler(h)
                    current_logger.addHandler(new_logging_handler)
                    break
            else:
                current_logger.addHandler(new_logging_handler)

        return self

    def debug(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log a DEBUG message msg via self.logger"""
        self._log_impl(level=lg.DEBUG, msg=msg, *args, **kwargs)

    def info(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log an INFO message msg via self.logger"""
        self._log_impl(level=lg.INFO, msg=msg, *args, **kwargs)

    def warning(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log a WARNING message msg via self.logger"""
        self._log_impl(level=lg.WARNING, msg=msg, *args, **kwargs)

    def error(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log an ERROR message msg via self.logger"""
        self._log_impl(level=lg.ERROR, msg=msg, *args, **kwargs)

    def critical(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log a CRITICAL message msg via self.logger"""
        self._log_impl(level=lg.CRITICAL, msg=msg, *args, **kwargs)

    def fatal(self, msg: Optional[Any] = None, *args, **kwargs):
        """Log a FATAL message msg via self.logger"""
        self._log_impl(level=lg.FATAL, msg=msg, *args, **kwargs)

    def log(self
            , level: Optional[int] = None
            , msg: Optional[Any] = None
            , *args
            , **kwargs):
        """Log a message msg with specific level via self.logger"""
        self._log_impl(level=level, msg=msg, *args, **kwargs)

    def _log_impl(self
            , level: Optional[int] = None
            , msg: Optional[Any] = None
            , *args
            , **kwargs):
        """Log a message msg via self.logger

        If msg is a string, it will be logged.
        If msg is None, str() representation of self will be logged.
        If msg has some other type, a string with object info for msg
        will be composed (including names of other variables
        holding the same object, object's type and str() representation),
        and this string will be used as a message to log.
        """

        if level is None:
            level = self.logging_level

        if msg is None:
            msg_to_log = self.selflog_prefix + str(self)
        elif isinstance(msg, str):
            msg_to_log = msg
        else:
            msg_to_log = NeatStr.object_info(
                msg, div_ch=" / ", stacks_to_skip = 2)

        suffix = ""
        if self.reveal_identity and self.reveal_calling_method:
            frame2 = inspect.stack()[2]
            calling_method_name = frame2.function
            if hasattr(self,calling_method_name):
                try:
                    if frame2[0].f_locals["self"] is self:
                        suffix = calling_method_name + "()"
                except:
                    suffix = ""
        if self.reveal_identity:
            suffix += f"  [pid:{os.getpid()}] "
        self.logger(suffix).log(level, msg_to_log, *args, **kwargs)