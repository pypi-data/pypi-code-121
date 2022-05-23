"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2017 Laurent Labatut / Laurent Champagnac
#
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ===============================================================================
"""
import ast
import logging
import os
import platform
import sys
import time
import traceback
from logging.config import dictConfig
from logging.handlers import WatchedFileHandler, TimedRotatingFileHandler, SysLogHandler
from threading import Lock

import gevent
import pytz
from datetime import datetime

from gevent import monkey, config
from yaml import load, SafeLoader

from pysolbase.ContextFilter import ContextFilter

logger = logging.getLogger(__name__)
lifecyclelogger = logging.getLogger("lifecycle")


class SolBase(object):
    """
    Base utilities & helpers.
    """

    # ===============================
    # STATIC STUFF
    # ===============================

    # Component name (mainly for rsyslog)
    _compo_name = "CompoNotSet"

    # Global init stuff
    _voodoo_initialized = False
    _voodoo_lock = Lock()

    # Logging stuff
    _logging_initialized = False
    _logging_lock = Lock()

    # Fork stuff
    _master_process = True

    # ===============================
    # DATE & MS
    # ===============================

    @classmethod
    def mscurrent(cls):
        """
        Return current millis since epoch
        :return float
        :rtype float
        """
        return time.time() * 1000.0

    @classmethod
    def securrent(cls):
        """
        Return current seconds since epoch
        :return float
        :rtype float
        """
        return time.time()

    @classmethod
    def msdiff(cls, ms_start, ms_end=None):
        """
        Get difference in millis between current millis and provided millis.
        :param ms_start: Start millis
        :type ms_start: float
        :param ms_end: End millis (will use current if not provided)
        :type ms_end: float
        :return float
        :rtype float
        """

        if not ms_end:
            ms_end = cls.mscurrent()

        return ms_end - ms_start

    @classmethod
    def datecurrent(cls, erase_mode=0):
        """
        Return current date (UTC)
        :param erase_mode: Erase mode (0=nothing, 1=remove microseconds but keep millis, 2=remove millis completely)
        :return datetime.datetime
        :rtype datetime.datetime
        """

        if erase_mode == 0:
            return datetime.utcnow()
        elif erase_mode == 1:
            # Force precision loss (keep millis, kick micro)
            dt = datetime.utcnow()
            return dt.replace(microsecond=int((dt.microsecond * 0.001) * 1000))
        elif erase_mode == 2:
            return datetime.utcnow().replace(microsecond=0)

    @classmethod
    def datediff(cls, dt_start, dt_end=None):
        """
        Get difference in millis between two datetime
        :param dt_start: Start datetime
        :type dt_start: datetime.datetime
        :param dt_end: End datetime (will use current utc if not provided)
        :type dt_end: datetime.datetime
        :return float
        :rtype float
        """

        # Fix
        if not dt_end:
            dt_end = cls.datecurrent()

        # Get delta
        delta = dt_end - dt_start
        return ((delta.days * 86400 + delta.seconds) * 1000) + (delta.microseconds * 0.001)

    # ==========================================
    # EPOCH / DT
    # ==========================================

    DT_EPOCH = datetime.utcfromtimestamp(0)

    @classmethod
    def dt_to_epoch(cls, dt):
        """
        Convert a datetime (UTC required) to a unix time since epoch, as seconds, as integer.
        Note that millis precision is lost.
        :param dt: datetime
        :type dt: datetime
        :return int
        :rtype int
        """

        return int((dt - cls.DT_EPOCH).total_seconds())

    @classmethod
    def epoch_to_dt(cls, epoch):
        """
        Convert an epoch float or int to datetime (UTC)
        :param epoch: float,int
        :type epoch: float,int
        :return datetime
        :rtype datetime
        """

        return datetime.utcfromtimestamp(epoch)

    @classmethod
    def dt_is_naive(cls, dt):
        """
        Return true if dt is naive
        :param dt: datetime.datetime
        :type dt: datetime.datetime
        :return bool
        :rtype bool
        """

        # Naive : no tzinfo
        if not dt.tzinfo:
            return True

        # Aware
        return False

    @classmethod
    def dt_ensure_utc_aware(cls, dt):
        """
        Switch dt to utc time zone. If dt is naive, assume utc, otherwise, convert it to utc timezone.
        Return an AWARE timezone (utc switched) datetime,
        :param dt: datetime.datetime
        :type dt:datetime.datetime
        :return datetime.datetime
        :rtype datetime.datetime
        """

        # If naive, add utc
        if cls.dt_is_naive(dt):
            return dt.replace(tzinfo=pytz.utc)
        else:
            # Not naive, go utc, keep aware
            return dt.astimezone(pytz.utc)

    @classmethod
    def dt_ensure_utc_naive(cls, dt):
        """
        Ensure dt is naive. Return dt, switched to UTC (if applicable), and naive.
        :param dt: datetime.datetime
        :type dt:datetime.datetime
        :return datetime.datetime
        :rtype datetime.datetime
        """

        dt = cls.dt_ensure_utc_aware(dt)
        return dt.replace(tzinfo=None)

    # ===============================
    # COMPO NAME (FOR RSYSLOG)
    # ===============================

    @classmethod
    def set_compo_name(cls, compo_name):
        """
        Set the component name. Useful for rsyslog.
        :param compo_name: The component name or None. If None, method do nothing.
        :type compo_name: str,None
        """

        if compo_name:
            cls._compo_name = compo_name
            lifecyclelogger.debug("compo_name now set to=%s", cls._compo_name)

    @classmethod
    def get_compo_name(cls):
        """
        Get current component name.
        :return str
        :rtype str
        """

        return cls._compo_name

    @classmethod
    def get_machine_name(cls):
        """
        Get machine name
        :return: Machine name
        :rtype: str
        """

        return platform.uname()[1]

    # ===============================
    # MISC
    # ===============================

    @classmethod
    def sleep(cls, sleep_ms):
        """
        Sleep for specified ms.
        Also used as gevent context switch in code, since it rely on gevent.sleep.
        :param sleep_ms: Millis to sleep.
        :type sleep_ms: int
        :return Nothing.
        """
        ms = sleep_ms * 0.001

        # gevent 1.3 : ms is not fully respected (100 can be 80-100)
        gevent.sleep(ms)

    # ===============================
    # EXCEPTION HELPER
    # ===============================

    @classmethod
    def extostr(cls, e, max_level=30, max_path_level=5):
        """
        Format an exception.
        :param e: Any exception instance.
        :type e: Exception
        :param max_level: Maximum call stack level (default 30)
        :type max_level: int
        :param max_path_level: Maximum path level (default 5)
        :type max_path_level: int
        :return The exception readable string
        :rtype str
        """

        # Go
        list_frame = None
        try:
            out_buffer = ""

            # Class type
            out_buffer += "e.cls:[{0}]".format(e.__class__.__name__)

            # To string
            try:
                ex_buf = str(e)
            except UnicodeEncodeError:
                ex_buf = repr(str(e))
            except Exception as e:
                logger.warning("Exception, e=%s", e)
                raise
            out_buffer += ", e.bytes:[{0}]".format(ex_buf)

            # Traceback
            si = sys.exc_info()

            # Raw frame
            # tuple : (file, lineno, method, code)
            raw_frame = traceback.extract_tb(si[2])
            raw_frame.reverse()

            # Go to last tb_next
            last_tb_next = None
            cur_tb = si[2]
            while cur_tb:
                last_tb_next = cur_tb
                cur_tb = cur_tb.tb_next

            # Skip frame up to current raw frame count
            list_frame = list()
            cur_count = -1
            skip_count = len(raw_frame)
            if last_tb_next:
                cur_frame = last_tb_next.tb_frame
            else:
                cur_frame = None
            while cur_frame:
                cur_count += 1
                if cur_count < skip_count:
                    cur_frame = cur_frame.f_back
                else:
                    # Need : tuple : (file, lineno, method, code)
                    raw_frame.append((cur_frame.f_code.co_filename, cur_frame.f_lineno, cur_frame.f_code.co_name, ""))
                    cur_frame = cur_frame.f_back

            # Build it
            cur_idx = 0
            out_buffer += ", e.cs=["
            for tu in raw_frame:
                line = tu[1]
                cur_file = tu[0]
                method = tu[2]

                # Handle max path level
                ar_token = cur_file.rsplit(os.sep, max_path_level)
                if len(ar_token) > max_path_level:
                    # Remove head
                    ar_token.pop(0)
                    # Join
                    cur_file = "..." + os.sep.join(ar_token)

                # Format
                out_buffer += "in:{0}#{1}@{2} ".format(method, cur_file, line)

                # Loop
                cur_idx += 1
                if cur_idx >= max_level:
                    out_buffer += "..."
                    break

            # Close
            out_buffer += "]"

            # Ok
            return out_buffer
        finally:
            if list_frame:
                del list_frame

    # ===============================
    # VOODOO INIT
    # ===============================

    @classmethod
    def _reset(cls):
        """
        For unittest only
        """

        cls._logging_initialized = False
        cls._voodoo_initialized = False

    @classmethod
    def voodoo_init(cls, aggressive=True, init_logging=True):
        """
        Global initialization, to call asap.
        Apply gevent stuff & default logging configuration.
        :param aggressive: bool
        :type aggressive: bool
        :param init_logging: If True, logging_init is called.
        :type init_logging: bool
        :return Nothing.
        """

        try:
            # Check
            if cls._voodoo_initialized:
                return

            # Lock
            with cls._voodoo_lock:
                # Re-check
                if cls._voodoo_initialized:
                    return

                # Fire the voodoo magic :)
                lifecyclelogger.debug("Voodoo : gevent : entering, aggressive=%s", aggressive)
                monkey.patch_all(aggressive=aggressive)
                lifecyclelogger.debug("Voodoo : gevent : entering")

                # Gevent 1.3 : by default, gevent keep tracks of spawn call stack
                # This may lead to memory leak, if a method spawn itself in loop (timer mode)
                # We disable this
                config.track_greenlet_tree = False

                # Initialize log level to INFO
                if init_logging:
                    lifecyclelogger.debug("Voodoo : logging : entering")
                    cls.logging_init()
                    lifecyclelogger.debug("Voodoo : logging : done")

                # Done
                cls._voodoo_initialized = True
        finally:
            # If whenever init_logging if set AND it is NOT initialized => we must init it
            # => we may have been called previously with init_logging=false, but monkey patch is SET and logging not initialized
            # => so it must be init now
            if init_logging and not cls._logging_initialized:
                lifecyclelogger.debug("Voodoo : logging : not yet init : entering")
                cls.logging_init()
                lifecyclelogger.debug("Voodoo : logging : not yet init : done")

    # ===============================
    # LOGGING
    # ===============================

    @classmethod
    def logging_init(cls, log_level="INFO", force_reset=False, log_callback=None,
                     log_to_file=None,
                     log_to_syslog=True,
                     log_to_syslog_facility=SysLogHandler.LOG_LOCAL0,
                     log_to_console=True,
                     log_to_file_mode="watched_file",
                     context_filter=None):
        """
        Initialize logging sub system with default settings (console, pre-formatted output)
        :param log_to_console: if True to console
        :type log_to_console: bool
        :param log_level: The log level to set. Any value in "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"
        :type log_level: str
        :param force_reset: If true, logging system is reset.
        :type force_reset: bool
        :param log_to_file: If specified, log to file
        :type log_to_file: str,None
        :param log_to_syslog: If specified, log to syslog
        :type log_to_syslog: bool
        :param log_to_syslog_facility: Syslog facility.
        :type log_to_syslog_facility: int
        :param log_to_file_mode: str "watched_file" for WatchedFileHandler, "time_file" for TimedRotatingFileHandler (or time_file_seconds for unittest)
        :type log_to_file_mode: str
        :param log_callback: Callback for unittest
        :param context_filter: Context filter. If None, pysolbase.ContextFilter.ContextFilter is used. If used instance has an attr "filter", it is added to all handlers and "%(kfilter)s" will be populated by all thread context key/values, using filter method call. Refer to our ContextFilter default implementation for details.
        :type context_filter: None,object
        :return Nothing.
        """

        if cls._logging_initialized and not force_reset:
            return

        with cls._logging_lock:
            if cls._logging_initialized and not force_reset:
                return

            # Reset
            cls._reset_logging()

            # Default
            logging.basicConfig(level=log_level)

            # Filter
            if context_filter:
                c_filter = context_filter
            else:
                c_filter = ContextFilter()

            # Format begin
            s_f = "%(asctime)s | %(levelname)s | %(module)s@%(funcName)s@%(lineno)d | %(message)s "

            # Browse
            if hasattr(c_filter, "filter"):
                # Push generic field
                # We expect it to be formatted like our pysolbase.ContextFilter.ContextFilter#filter method.
                s_f += "|%(kfilter)s"

            # Format end
            s_f += "| %(thread)d:%(threadName)s | %(process)d:%(processName)s"

            # Formatter
            f = logging.Formatter(s_f)

            # Console handler
            c = None
            if log_to_console:
                # This can be overriden by unittest, we use __stdout__
                c = logging.StreamHandler(sys.__stdout__)
                c.setLevel(logging.getLevelName(log_level))
                c.setFormatter(f)

            # File handler to /tmp
            cf = None
            if log_to_file:
                if log_to_file_mode == "watched_file":
                    cf = WatchedFileHandler(log_to_file, encoding="utf-8")
                    cf.setLevel(logging.getLevelName(log_level))
                    cf.setFormatter(f)
                elif log_to_file_mode == "time_file":
                    cf = TimedRotatingFileHandler(log_to_file, encoding="utf-8", utc=True, when="D", interval=1, backupCount=7)
                    cf.setLevel(logging.getLevelName(log_level))
                    cf.setFormatter(f)
                elif log_to_file_mode == "time_file_seconds":
                    # For unittest only
                    cf = TimedRotatingFileHandler(log_to_file, encoding="utf-8", utc=True, when="S", interval=1, backupCount=7)
                    cf.setLevel(logging.getLevelName(log_level))
                    cf.setFormatter(f)
                else:
                    logger.warning("Invalid log_to_file_mode=%s", log_to_file_mode)

            # Syslog handler
            syslog = None
            if log_to_syslog:
                try:
                    from pysolbase.SysLogger import SysLogger

                    syslog = SysLogger(log_callback=log_callback, facility=log_to_syslog_facility)
                    syslog.setLevel(logging.getLevelName(log_level))
                    syslog.setFormatter(f)
                except Exception as e:
                    # This will fail on WINDOWS (no attr AF_UNIX)
                    logger.debug("Unable to import SysLogger, e=%s", SolBase.extostr(e))
                    syslog = False

            # Initialize
            root = logging.getLogger()
            root.setLevel(logging.getLevelName(log_level))
            root.handlers = []
            if log_to_console:
                c.addFilter(c_filter)
                root.addHandler(c)
            if log_to_file and cf:
                cf.addFilter(c_filter)
                root.addHandler(cf)
            if log_to_syslog and syslog:
                syslog.addFilter(c_filter)
                root.addHandler(syslog)

            # Done
            cls._logging_initialized = True
            if force_reset:
                lifecyclelogger.info("Logging : initialized from memory, log_level=%s, force_reset=%s", log_level, force_reset)
            else:
                lifecyclelogger.debug("Logging : initialized from memory, log_level=%s, force_reset=%s", log_level, force_reset)

    @classmethod
    def _register_filter(cls, c_filter):
        """
        Register filter across the whole logging (root and all loggers)
        Notice : addFilter is protected against duplicates add
        :param c_filter: pysolbase.ContextFilter.ContextFilter
        :type c_filter: pysolbase.ContextFilter.ContextFilter
        """

        # Initialize
        root = logging.getLogger()
        for h in list(root.handlers):
            h.addFilter(c_filter)

        # Browse all loggers and set
        for name in logging.root.manager.loggerDict:
            cur_logger = logging.getLogger(name)
            for h in list(cur_logger.handlers):
                h.addFilter(c_filter)

    @classmethod
    def _reset_logging(cls):
        """
        Reset
        """

        # Found no way to fully reset the logging stuff while running
        # We reset root and all loggers to INFO, and kick handlers

        # Initialize
        root = logging.getLogger()
        root.setLevel(logging.getLevelName("INFO"))
        root.handlers = []

        # Browse all loggers and set
        for name in logging.root.manager.loggerDict:
            cur_logger = logging.getLogger(name)
            cur_logger.setLevel(logging.getLevelName("INFO"))
            cur_logger.handlers = []

    @classmethod
    def logging_initfromfile(cls, config_file_name, force_reset=False, context_filter=None):
        """
        Initialize logging system from a configuration file, with optional reset.
        :param config_file_name: Configuration file name
        :type config_file_name: str
        :param force_reset: If true, logging system is reset.
        :type force_reset: bool
        :param context_filter: Context filter. If None, pysolbase.ContextFilter.ContextFilter is used. If used instance has an attr "filter", it is added to all handlers and "%(kfilter)s" will be populated by all thread context key/values, using filter method call. Refer to our ContextFilter default implementation for details.
        :type context_filter: None,object
        :return Nothing.
        """

        if cls._logging_initialized and not force_reset:
            return

        with cls._logging_lock:
            if cls._logging_initialized and not force_reset:
                return

            try:
                # Filter
                if context_filter:
                    c_filter = context_filter
                else:
                    c_filter = ContextFilter()

                # Reset
                cls._reset_logging()

                # Load
                logger.debug("Logging : yaml config_file_name=%s", config_file_name)
                with open(config_file_name, 'r') as f:
                    d = load(f, Loader=SafeLoader)
                    dictConfig(d)

                # Register filter
                if c_filter:
                    cls._register_filter(c_filter)

                if force_reset:
                    lifecyclelogger.info("Logging : initialized from yaml file, config_file_name=%s", config_file_name)
                else:
                    lifecyclelogger.debug("Logging : initialized from yaml file, config_file_name=%s", config_file_name)
            except Exception:
                raise

    @classmethod
    def context_set(cls, k, v):
        """
        Set thread/greenlet context value

        This is a wrapper to pysolbase.ContextFilter.ContextFilter#set_value
        and will work only if ContextFilter is defined (which is by default)
        :param k: key name
        :type k: basestring
        :param v: value
        :type v: object
        """

        ContextFilter.set_value(k, v)

    # ===============================
    # FORK STUFF
    # ===============================

    @classmethod
    def get_master_process(cls):
        """
        Return True if we are the master process, False otherwise.
        :return bool
        :rtype bool
        """
        return cls._master_process

    @classmethod
    def set_master_process(cls, b):
        """
        Set is we are a fork master or not
        :param b: True if we are master process, False if we are a child process.
        :type b: bool
        :return Nothing
        """

        logger.debug("Switching _masterProcess to %s", b)
        cls._master_process = b

    # ===============================
    # BINARY STUFF
    # ===============================

    @classmethod
    def binary_to_unicode(cls, bin_buf, encoding="utf-8"):
        """
        Binary buffer to str, using the specified encoding
        :param bin_buf: Binary buffer
        :type bin_buf: bytes
        :param encoding: Encoding to use
        :type encoding: str
        :return str
        :rtype str
        """

        return bin_buf.decode(encoding)

    @classmethod
    def unicode_to_binary(cls, unicode_buf, encoding="utf-8"):
        """
        Unicode to binary buffer, using the specified encoding
        :param unicode_buf: String to convert.
        :type unicode_buf: str
        :param encoding: Encoding to use.
        :type encoding: str
        :return bytes
        :rtype bytes
        """

        return unicode_buf.encode(encoding)

    @classmethod
    def fix_paths_for_popen(cls):
        """
        Fix path and env for popen calls toward current project
        Mainly used for unittests, which requires current env to be propagated while testing command line invocation within same project
        """

        # Merge all
        ar_p_path = sys.path
        if os.environ.get("PYTHONPATH"):
            ar_p_path.extend(os.environ.get("PYTHONPATH").split(":"))
        if os.environ.get("PATH"):
            ar_p_path.extend(os.environ.get("PATH").split(":"))

        # Join
        new_path = ":".join(ar_p_path)

        # Re-Assign
        os.environ["PATH"] = new_path
        os.environ["PYTHONPATH"] = new_path

    # ===============================
    # CONVERSIONS
    # ===============================

    @classmethod
    def to_int(cls, v):
        """
        Convert to int
        :param v: int,str
        :type v: int,str
        :return: int
        :rtype int
        """

        if isinstance(v, int):
            return v
        else:
            return int(v)

    @classmethod
    def to_bool(cls, v):
        """
        Convert to bool
        :param v: bool,str
        :type v: bool,str
        :return: bool
        :rtype bool
        """

        if isinstance(v, bool):
            return v
        else:
            return ast.literal_eval(v)

    @classmethod
    def get_classname(cls, my_instance):
        """
        Return the class name of my_instance, or "Instance.None".
        :param cls: Our class.
        :param my_instance: Instance to use.
        :return: Return the class name of my_instance, or "Instance.None" in case of error/None value.
        """
        if my_instance is None:
            return "Instance.None"
        else:
            return my_instance.__class__.__name__

    @classmethod
    def get_pathseparator(cls):
        """
        Return the path separator.
        https://docs.python.org/library/os.html#os.sep
        :param cls: Our class
        :return: The path separator (string)
        """
        return os.sep

    @classmethod
    def is_bool(cls, my_bool):
        """
        Return true if the provided my_bool is a boolean.
        :param cls: Our class.
        :param my_bool: A boolean..
        :return: Return true if the provided my_bool is a boolean. False otherwise.
        """
        if my_bool is None:
            return False
        else:
            return isinstance(my_bool, bool)

    @classmethod
    def is_int(cls, my_int):
        """
        Return true if the provided my_int is a integer.
        :param cls: Our class.
        :param my_int: An integer..
        :return: Return true if the provided my_int is a integer. False otherwise.
        """
        if my_int is None:
            return False
        # Caution, boolean is an integer...
        elif SolBase.is_bool(my_int):
            return False
        else:
            return isinstance(my_int, int)

    @classmethod
    def get_current_pid_as_string(cls):
        """
        Return the current pids as string.
        :param cls: Our class.
        :return: A String
        """
        try:
            return "pid={0}, ppid={1}".format(os.getpid(), os.getppid())
        except AttributeError:
            return "pid={0}".format(os.getpid())

    # =====================================================
    # HELPER FOR SOCKET CLOSING
    # =====================================================

    @classmethod
    def safe_close_socket(cls, soc_to_close):
        """
        Safe close a socket
        :param soc_to_close: socket
        :type soc_to_close: socket.socket
        """

        if soc_to_close is None:
            return

        try:
            soc_to_close.shutdown(2)
        except Exception as e:
            logger.debug("Socket shutdown ex=%s", SolBase.extostr(e))

        try:
            soc_to_close.close()
        except Exception as e:
            logger.debug("Socket close ex=%s", SolBase.extostr(e))

        try:
            del soc_to_close
        except Exception as e:
            logger.debug("Socket del ex=%s", SolBase.extostr(e))
