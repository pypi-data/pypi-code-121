# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2020 Mark Crewson <mark@crewson.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Standard python logging extensions and configuration classes.
"""

__all__ = ['configure', 'getlog', 'log_subprocess']

import errno
import logging
import os
import subprocess
import sys
import time
import types
import traceback

from .baseobject import BaseObject
from .config import Config
from .string_conversion import convert_to_bool

try:
    import codecs
except ImportError:
    codecs = None

##############################################################################

# Logging extensions

TRACE = int((logging.NOTSET + logging.DEBUG) / 2)
MOREINFO = int((logging.DEBUG + logging.INFO) / 2)

# Logger class methods to be injected


def trace_method(self, msg='trace', *args, **kwargs):
    if self.isEnabledFor(TRACE):
        stack = traceback.extract_stack()[-2]
        msg = '[%s:%i] %s: %s' % (os.path.basename(stack[0]),  # FILENAME
                                  stack[1],                    # LINENO
                                  stack[2] + '()',             # FUNCNAME
                                  msg)
        self._log(TRACE, msg, args, **kwargs)


def moreinfo_method(self, msg, *args, **kwargs):
    if self.isEnabledFor(MOREINFO):
        self._log(MOREINFO, msg, args, **kwargs)


def repr_method(self):
    return '<logging.Logger instance at 0x%x (name = "%s")>' % (id(self), self.name)

##############################################################################

# Logging configuration class


class LoggingFactory (BaseObject):

    DEFAULT_LEVEL = 'INFO'
    DEFAULT_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
    DEFAULT_DATEFMT = '%Y-%m-%d %H:%M:%S'

    DEFAULT_CONSOLE_LEVEL = 'WARNING'
    DEFAULT_CONSOLE_FORMAT = '%(message)s'
    DEFAULT_CONSOLE_DATEFMT = ''

    options = {'file':            None,
               'level':           DEFAULT_LEVEL,
               'format':          DEFAULT_FORMAT,
               'datefmt':         DEFAULT_DATEFMT,
               'console':         (True, convert_to_bool),
               'console_level':   DEFAULT_CONSOLE_LEVEL,
               'console_format':  DEFAULT_CONSOLE_FORMAT,
               'console_datefmt': DEFAULT_CONSOLE_DATEFMT,
               'enabled':         (True, convert_to_bool),
               }

    def __init__(self, **kw):
        super(LoggingFactory, self).__init__()
        self._parse_options(LoggingFactory.options, kw)
        self.is_setup = False
        self.setup()
        self.loggers = dict()

    def setup(self):
        logging.getLogger('').handlers = []

        logging.addLevelName(TRACE, 'TRACE')
        logging.addLevelName(MOREINFO, 'MOREINFO')

        if logging.getLevelName(self.console_level) < logging.getLevelName(self.level):
            self.level = self.console_level

        if self.enabled is True:

            # setup root logger
            self.root_logger = logging.getLogger('')
            if self.file is not None:
                formatter = logging.Formatter(self.format, self.datefmt)
                handler = MyFileHandler(self.file, 'a')
                handler.setFormatter(formatter)
                self.root_logger.addHandler(handler)
            else:
                self.root_logger.addHandler(DevnullHandler())
            self.root_logger.setLevel(logging.getLevelName(self.level))

            self.root_logger.trace = types.MethodType(trace_method, self.root_logger)
            self.root_logger.moreinfo = types.MethodType(moreinfo_method, self.root_logger)
            self.root_logger.__repr__ = types.MethodType(repr_method, self.root_logger)

            # setup a console logger, if enabled
            if self.console is True:
                console_fmtr = logging.Formatter(self.console_format, self.console_datefmt)
                console_hdlr = logging.StreamHandler(sys.stderr)
                console_hdlr.setFormatter(console_fmtr)
                console_hdlr.setLevel(logging.getLevelName(self.console_level))
                self.root_logger.addHandler(console_hdlr)

        self.is_setup = True

    def get_logger(self, name=None, config=None):
        if self.enabled is False:
            logger = self.devnull_logger()
        elif name is None:
            logger = self.root_logger
        elif name in self.loggers:
            logger = self.loggers[name]
        else:
            logger = self.make_logger(name, config)
            self.loggers[name] = logger

        return logger

    def make_logger(self, name, config):
        logger = logging.getLogger(name)
        if name is not None:
            logfile = config.get('file', None)
            if logfile is not None:
                handler = MyFileHandler(logfile, 'a')
                format = config.get('format', self.root_format)
                datefmt = config.get('datefmt', self.root_datefmt)
                formatter = logging.Formatter(format, datefmt)
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            level = config.get('level', None)
            if level is not None:
                logger.setLevel(logging.getLevelName(level))

        if not hasattr(logger, 'trace'):
            logger.trace = types.MethodType(trace_method, logger)
        if not hasattr(logger, 'moreinfo'):
            logger.moreinfo = types.MethodType(moreinfo_method, logger)
        if not hasattr(logger, '__repr__'):
            logger.__repr__ = types.MethodType(repr_method, logger)

        return logger

    def devnull_logger(self):
        try:
            return self._devnull_logger
        except AttributeError:
            self._devnull_logger = logging.getLogger("devnull")
            self._devnull_logger.addHandler(DevnullHandler())
            self._devnull_logger.propagate = False
            return self._devnull_logger

##############################################################################

# Logging write handlers


class DevnullHandler (logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def handle(self, record):
        pass


class MyFileHandler (logging.StreamHandler):

    checkperiod = 10  # seconds

    def __init__(self, filename, mode='a', encoding=None):
        if codecs is None:
            encoding = None
        self.baseFilename = os.path.abspath(filename)
        self.mode = mode
        self.encoding = encoding
        logging.StreamHandler.__init__(self, self._open())

    def close(self):
        if self.stream:
            try:
                self.flush()
            except ValueError:
                pass
            if hasattr(self.stream, 'close'):
                self.stream.close()
            logging.StreamHandler.close(self)
            self.stream = None

    def _open(self):
        if self.encoding is None:
            stream = open(self.baseFilename, self.mode)
        else:
            stream = codecs.open(self.baseFilename, self.mode, self.encoding)
        self.inode = os.stat(self.baseFilename).st_ino
        self.lastcheck = time.time()
        return stream

    def _check(self):
        now = time.time()
        if self.lastcheck + self.checkperiod >= now:
            return

        try:
            inode = os.stat(self.baseFilename).st_ino
        except OSError as err:
            if err.errno != errno.ENOENT:
                raise
            # File was probably deleted.
            inode = None

        if inode != self.inode:
            self.close()
            self.stream = self._open()
        self.lastcheck = now

    def emit(self, record):
        self._check()
        try:
            msg = self.format(record)
            if msg.endswith('\n'):
                fs = '%s'
            else:
                fs = '%s\n'
            if not hasattr(types, "UnicodeType"):
                self.stream.write(fs % msg)
            else:
                try:
                    self.stream.write(fs % msg)
                except UnicodeError:
                    self.stream.write(fs % msg.encode("UTF-8"))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except: # noqa
            self.handleError(record)


##############################################################################

__logging_factory = None


def configure(config, cmdline_arguments):
    global __logging_factory
    if isinstance(config, Config) and 'logging' in config.get_sections():
        logconfig = config.section('logging')
    else:
        logconfig = {}

    if cmdline_arguments.logfile:
        logconfig['file'] = cmdline_arguments.logfile

    console_level = {0: 'WARNING',
                     1: 'INFO',
                     2: 'MOREINFO',
                     3: 'DEBUG',
                     4: 'TRACE',
                     }.get(cmdline_arguments.verbose_level, 'TRACE')
    logconfig['console_level'] = console_level

    __logging_factory = LoggingFactory(**logconfig)


def getlog(name=None, config=None):
    global __logging_factory
    if __logging_factory is None:
        class MockCmdline (object):
            logfile = None
            verbose_level = 1
        configure(None, MockCmdline())
    return __logging_factory.get_logger(name, config)


##############################################################################

def log_subprocess(logger, subargs, **kwargs):
    process = subprocess.Popen(subargs, **kwargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def check_output():
        while True:
            out = process.stdout.readline().strip().decode()
            if out:
                logger(out)
            else:
                break

    returncode = process.poll()
    while returncode is None:
        check_output()
        returncode = process.poll()
    return returncode

##############################################################################
# THE END
