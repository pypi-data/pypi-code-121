# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Using logger.info/debug/someOtherLevel() is not supported in this module. In order to get the correct
frame info, we must skip over functions called in this module and in externed structlog. If logging is attempted,
incorrect frame info will be displayed on the log message if used in this file.

Use print(...) instead
"""
import asyncio
import sys
import logging
from os import getpid
from os.path import basename
import threading

import contrast
from contrast.extern.structlog._frames import _find_first_app_frame_and_name
from contrast.extern import structlog
from contrast.utils.configuration_utils import get_hostname

from contrast.utils.loggers import TRACE_LEVEL

LOGGING_TO_BUNYAN_LOG_LEVEL_CONVERSION = {
    "critical": 60,
    "error": 50,
    "warning": 40,
    "info": 30,
    "debug": 20,
    "trace": TRACE_LEVEL,
}


def add_hostname(logger, method_name, event_dict):
    event_dict["hostname"] = get_hostname()

    return event_dict


def add_pid(logger, method_name, event_dict):
    event_dict["pid"] = getpid()

    return event_dict


def add_thread_id(logger, method_name, event_dict):
    event_dict["thread_id"] = threading.current_thread().ident

    return event_dict


def add_request_id(logger, method_name, event_dict):
    context = contrast.CS__CONTEXT_TRACKER.current()
    obj_id = -1

    if context:
        obj_id = id(context)

    event_dict["request_id"] = obj_id

    return event_dict


def rename_key(old_name, new_name):
    def event_key_to_msg(logger, method_name, event_dict):
        """
        msg is a required key for bunyan parsing. The event key is renamed to msg
        """

        value = event_dict.get(old_name)
        if value and not event_dict.get(new_name):
            event_dict[new_name] = value
            del event_dict[old_name]

        return event_dict

    return event_key_to_msg


def add_bunyan_log_level(logger, log_level, event_dict):
    """
    This Processor must be installed AFTER structlog.stdlib.add_log_level.
    structlog.stdlib.add_log_level adds level: "info/debug/...". This function
    converts that string to the bunyan integer value equivalent (whenever possible).
    """
    if log_level == "warn":
        # The stdlib has an alias
        log_level = "warning"

    new_value = LOGGING_TO_BUNYAN_LOG_LEVEL_CONVERSION.get(log_level, None)

    if new_value:
        event_dict["level"] = new_value

    return event_dict


def add_v(logger, method_name, event_dict):
    """
    Required key for bunyan log parsing
    """
    event_dict["v"] = 0

    return event_dict


def add_frame_info(logger, method_name, event_dict):
    """
    Adds filename, function name and line number based on where the logger is called
    """
    ignore_frames = [
        "contrast.extern.structlog",
        "contrast.utils.loggers.structlog",
        "logging",
    ]

    frame_info = _find_first_app_frame_and_name(ignore_frames)

    if frame_info and frame_info[0]:
        frame = frame_info[0]

        event_dict[
            "frame_info"
        ] = f"{basename(frame.f_code.co_filename)}:{frame.f_code.co_name}:{frame.f_lineno}"

    return event_dict


def add_progname(logger, method_name, event_dict):
    """
    progname is the name of the process the agents uses in logs.
    The default value is Contrast Agent. progname will be used
    as the name of the logger as seen in the logs.
    """
    field = "name"
    current_handler = logger.handlers[0]

    if hasattr(current_handler.filters[0], field):
        progname = current_handler.filters[0].progname

        if progname:
            event_dict[field] = progname

    return event_dict


def add_asyncio_info(logger, method_name, event_dict):
    try:
        current_task = asyncio.current_task()

        if sys.version_info[:2] > (3, 7):
            # get_name and get_coro are only supported on 3.8+

            # If no name has been explicitly assigned to the Task, the default asyncio Task implementation
            # generates a default name during instantiation.
            event_dict["asyncio_task_name"] = current_task.get_name()

            current_coro = current_task.get_coro()
            if hasattr(current_coro, "__name__"):
                event_dict["asyncio_coro_name"] = current_coro.__name__

        event_dict["asyncio_task_id"] = id(current_task)
    except Exception:
        # This can happen when there is no running event loop
        pass

    return event_dict


def register_log_level(level_value, level_name):
    """
    Register and add new custom log level with structlog and Python logging module.

    This is a modified version of code in this PR
    https://github.com/hynek/structlog/pull/279
    """
    level_name_lower = level_name.lower()
    level_name_upper = level_name.upper()

    # If anything else has already registered this level, we won't do so.
    if (
        hasattr(logging, level_name_upper)
        or hasattr(logging.Logger, level_name_lower)
        or not logging.getLevelName(level_value).startswith("Level ")
    ):
        print("Contrast Agent will not register log level", level_name)
        return

    # Register constants with structlog
    setattr(structlog.stdlib, level_name_upper, level_value)
    structlog.stdlib._NAME_TO_LEVEL[level_name_lower] = level_value
    structlog.stdlib._LEVEL_TO_NAME[level_value] = level_name_lower

    # For convenience, add new log.<level name> method
    def make_logger_function(name):
        def log_method(self, msg, *args, **kwargs):
            return self.log(level_value, msg, *args, **kwargs)

        log_method.__name__ = name
        return log_method

    log_method = make_logger_function(level_name_lower)

    # Register new level with structlog
    setattr(structlog.stdlib._FixedFindCallerLogger, level_name_lower, log_method)
    setattr(structlog.stdlib.BoundLogger, level_name_lower, log_method)

    # Register new level with stdlib logging module
    setattr(logging.Logger, level_name_lower, log_method)
    setattr(logging, level_name_upper, level_value)
    logging.addLevelName(level_value, level_name_upper)


def init_structlog():
    """
    Configures structlog -- must be called AFTER logging module is configured
    """
    # TRACE is not currently a supported level so we add it ourselves.
    register_log_level(TRACE_LEVEL, "TRACE")

    structlog.configure(
        # Each processor is called from the top down and can modify the event_dict passed to it
        processors=[
            add_bunyan_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            # rename_key must be called after timestamp is added by TimeStamper
            rename_key("timestamp", "time"),
            rename_key("event", "msg"),
            add_v,
            add_hostname,
            add_pid,
            add_thread_id,
            add_request_id,
            add_frame_info,
            add_progname,
            add_asyncio_info,
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
