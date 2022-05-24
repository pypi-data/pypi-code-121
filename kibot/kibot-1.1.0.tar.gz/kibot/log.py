# -*- coding: utf-8 -*-
# Copyright (c) 2020-2022 Salvador E. Tropea
# Copyright (c) 2020-2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
# Adapted from: https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
"""
Log module

Handles logging initialization and formatting.
"""
import io
import os
import sys
import traceback
import logging
no_colorama = False
try:
    from colorama import init as colorama_init, Fore, Back, Style
except ImportError:
    no_colorama = True
# If colorama isn't installed use an ANSI basic replacement
if no_colorama:
    from .mcpyrate.ansi import Fore, Back, Style  # noqa: F811
else:
    colorama_init()
# Default domain, base name for the tool
domain = 'kilog'
filters = None
root_logger = None
visual_level = None


def get_logger(name=None):
    """Get a module for a submodule or the root logger if no name is
       provided"""
    # print('get_logger '+str(name))
    if name:
        if name.startswith(domain):
            return logging.getLogger(name)
        return logging.getLogger(domain+'.'+name)
    return logging.getLogger(domain)


def set_domain(name):
    """Set the base name for the tool"""
    global domain
    domain = name


def set_filters(f):
    """Set the list of warning filters"""
    global filters
    filters = f


class MyLogger(logging.Logger):
    warn_hash = {}
    warn_tcnt = warn_cnt = n_filtered = 0

    @staticmethod
    def reset_warn_hash():
        """ Clean the hash, used for testing """
        MyLogger.warn_hash = {}

    def warning(self, msg, *args, **kwargs):
        MyLogger.warn_tcnt += 1
        # Get the message applying optional C style expansions
        # No longer used:
        # if isinstance(msg, str) and len(args):
        #     buf = StringIO()
        #     buf.write(msg % args)
        #     buf = buf.getvalue()
        # else:
        buf = str(msg)
        # Avoid repeated warnings
        if buf in MyLogger.warn_hash:
            MyLogger.warn_hash[buf] += 1
            return
        # Apply the filters
        if filters and buf.startswith('(W'):
            pos_end = buf.find(')')
            if pos_end > 0:
                num_str = buf[2:pos_end]
                if num_str[0] == 'C':
                    number = int(buf[3:pos_end])+1000
                else:
                    number = int(num_str)
                for f in filters:
                    if f.number == number and f.regex.search(buf):
                        MyLogger.n_filtered += 1
                        return
        MyLogger.warn_cnt += 1
        MyLogger.warn_hash[buf] = 1
        if sys.version_info >= (3, 8):
            super().warning(buf, stacklevel=2, **kwargs)  # pragma: no cover (Py38)
        else:
            super().warning(buf, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        if level < self.getEffectiveLevel():
            return
        if isinstance(msg, tuple):
            msg = ' '.join(map(str, msg))
        if sys.version_info >= (3, 8):
            super(self.__class__, self).debug(msg, stacklevel=2, *args, **kwargs)  # pragma: no cover (Py38)
        else:
            super(self.__class__, self).debug(msg, *args, **kwargs)

    def log_totals(self):
        if MyLogger.warn_cnt:
            filt_msg = ''
            if MyLogger.n_filtered:
                filt_msg = ', {} filtered'.format(MyLogger.n_filtered)
            self.info('Found {} unique warning/s ({} total{})'.format(MyLogger.warn_cnt, MyLogger.warn_tcnt, filt_msg))

    def findCaller(self, stack_info=False, stacklevel=1):
        f = sys._getframe(1)
        # Skip frames from logging module
        while '/logging/' in os.path.normcase(f.f_code.co_filename):
            f = f.f_back
        # Apply the indicated stacklevel
        while stacklevel > 1:
            f = f.f_back
            stacklevel -= 1
        # Skip the __init__.py wrappers
        fname = os.path.normcase(f.f_code.co_filename)
        if fname.endswith('__init__.py') or fname.endswith('log__.py'):
            f = f.f_back
        # Create the stack info if needed
        sinfo = None
        if stack_info:
            out = io.StringIO()
            out.write(u"Stack (most recent call last):\n")
            traceback.print_stack(f, file=out)
            sinfo = out.getvalue().rstrip(u"\n")
        return os.path.normcase(f.f_code.co_filename), f.f_lineno, f.f_code.co_name, sinfo


def set_verbosity(logger, verbose, quiet):
    # Choose the log level
    log_level = logging.INFO
    if verbose:
        log_level = logging.DEBUG
    if quiet:
        log_level = logging.WARNING
    # We use debug level but we then filter according to the desired level (visual_level)
    # In this way we can log debug to files and only the user level to the console
    logger.setLevel(logging.DEBUG)
    global visual_level
    visual_level = log_level
    return log_level <= logging.DEBUG


class FilterOnlyInfo(object):
    def filter(self, record):
        if visual_level is not None and record.levelno < visual_level:
            return False
        return record.levelno == logging.INFO


class FilterNoInfo(object):
    def filter(self, record):
        if visual_level is not None and record.levelno < visual_level:
            return False
        return record.levelno != logging.INFO


def init():
    """Initialize the logging feature using a custom format"""
    # Use a class to count and filter warnings
    logging.setLoggerClass(MyLogger)
    logger = get_logger()
    # Handler for all but info.
    # Outputs to stderr
    ch = logging.StreamHandler()
    ch.addFilter(FilterNoInfo())
    ch.setFormatter(CustomFormatter(sys.stderr))
    logger.addHandler(ch)
    # Handler for info.
    # Outputs to stdout
    ch = logging.StreamHandler(sys.stdout)
    ch.addFilter(FilterOnlyInfo())
    ch.setFormatter(CustomFormatter(sys.stdout))
    logger.addHandler(ch)
    global root_logger
    root_logger = logger
    return logger


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    def __init__(self, stream=None):
        super(logging.Formatter, self).__init__()
        if stream is not None and stream.isatty():
            white = Fore.WHITE
            yellow = Fore.YELLOW + Style.BRIGHT
            red = Fore.RED + Style.BRIGHT
            red_alarm = Fore.RED + Back.WHITE + Style.BRIGHT
            cyan = Fore.CYAN + Style.BRIGHT
            reset = Style.RESET_ALL
        else:
            white = ""
            yellow = ""
            red = ""
            red_alarm = ""
            cyan = ""
            reset = ""
        # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
        #          "(%(filename)s:%(lineno)d)"
        format = "%(levelname)s:%(message)s (%(name)s - %(filename)s:%(lineno)d)"
        format_simple = "%(message)s"

        self.FORMATS = {
            logging.DEBUG: cyan + format + reset,
            logging.INFO: white + format_simple + reset,
            logging.WARNING: yellow + format + reset,
            logging.ERROR: red + format + reset,
            logging.CRITICAL: red_alarm + format + reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def set_file_log(fname):
    fh = logging.FileHandler(fname)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(CustomFormatter())
    root_logger.addHandler(fh)
    return fh


def remove_file_log(fh):
    root_logger.removeHandler(fh)
