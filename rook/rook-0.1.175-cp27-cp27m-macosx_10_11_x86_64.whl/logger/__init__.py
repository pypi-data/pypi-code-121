import six
import traceback
import sys
import datetime
import time
import threading
import os
import inspect

from ..processor.namespaces.python_object_namespace import PythonObjectNamespace

from rook.config import LoggingConfiguration
from rook.serverless import on_lambda
from rook.config import LoggingConfiguration, ShutdownConfig

LOG_LEVELS = ["trace", "debug", "info", "warning", "error", "fatal"]

TRACEBACK_LIMIT = 25

STDERR_WRITABLE = True


class _LogRecord(object):

    def __init__(self, level, level_no, text, formatted_message, args):
        self.level = level
        self.level_no = level_no
        self.datetime = datetime.datetime.now()
        self.time = time.time()
        self.filename, self.lineno, self.function = self._get_caller()
        self.text = text
        self.formatted_message = formatted_message
        self.args = args
        self.process = os.getpid()
        self.thread = threading.current_thread().ident
        self.thread_name = threading.current_thread().name

    def format(self):
        return r'%s %d:%s- %s:%s@%d - %s - %s' % (
            str(self.datetime),
            self.process,
            self.thread_name,
            os.path.splitext(self.filename)[0],
            self.function,
            self.lineno,
            self.level,
            self.formatted_message)

    # Based off Python built-in logging library

    # _srcfile is used when walking the stack to check when we've got the first
    # caller stack frame.
    #
    _srcfile = os.path.normcase(sys._getframe(1).f_code.co_filename)

    @staticmethod
    def _get_caller():
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = inspect.currentframe()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _LogRecord._srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv


class Logger(object):

    def __init__(self):
        if sys.argv and ('unittest' in sys.argv[0] or 'pytest' in sys.argv[0]) and ("PythonRook" in os.getcwd()):
            LoggingConfiguration.LOG_TO_STDERR = True
            LoggingConfiguration.LOG_LEVEL = "debug"

        self.output = None

        try:
            self.verbosity = LOG_LEVELS.index(LoggingConfiguration.LOG_LEVEL.lower())
        except ValueError:
            self.verbosity = LOG_LEVELS.index("info")

        self.handlers = self._build_handlers()

    def register_output(self, output):
        self.output = output

    def remove_output(self, output):
        self.output = None

    def debug(self, message, *args, **kwargs):
        self._log("debug", message, args, exc_info=kwargs.get('exc_info', False))

    def info(self, message, *args, **kwargs):
        self._log("info", message, args, exc_info=kwargs.get('exc_info', False))

    def warn(self, message, *args, **kwargs):
        self._log("warning", message, args, exc_info=kwargs.get('exc_info', False))

    def warning(self, message, *args, **kwargs):
        self._log("warning", message, args, exc_info=kwargs.get('exc_info', False))

    def error(self, message, *args, **kwargs):
        self._log("error", message, args, exc_info=kwargs.get('exc_info', False))

    def exception(self, message, *args):
        self._log("error", message, args, exc_info=1)

    def _log(self, level, message, args, **kwargs):
        try:
            if ShutdownConfig.IS_SHUTTING_DOWN:
                return

            level_no = len(LOG_LEVELS)
            try:
                level_no = LOG_LEVELS.index(level)
            except ValueError: # Use default value (error)
                pass

            if level_no < self.verbosity:
                return

            formatted_message = message
            try:
                formatted_message = message % args

                if kwargs.get("exc_info", False):
                    formatted_message += traceback.format_exc(TRACEBACK_LIMIT)
            except Exception:  # Use original message on error
                pass

            record = _LogRecord(level, level_no, message, formatted_message, args)
            for handler in self.handlers:
                handler(record)

        except Exception:
            six.print_("[Rookout] Unexpected error when writing to log: " + traceback.format_exc())

    def _build_handlers(self):
        handlers = []

        if LoggingConfiguration.LOG_TO_STDERR:
            handlers.append(self._get_stderr_handler())

            if not on_lambda():
                file_handler = self._get_file_handler(LoggingConfiguration.FILE_NAME)
                if file_handler:
                    handlers.append(file_handler)

        handlers.append(self._remote_handler)

        return handlers

    @staticmethod
    def _get_file_handler(file_name):
        if not file_name:
            return None

        # Calculate file path
        abs_file_path = None
        if os.path.isabs(file_name):
            abs_file_path = file_name
        else:
            if "darwin" in sys.platform:
                abs_file_path = os.path.join(os.getenv("HOME", "."), file_name)
            elif sys.platform == "win32":
                abs_file_path = os.path.join(os.getenv("USERPROFILE", "."), file_name)
            else:
                abs_file_path = os.path.join("/var/log", file_name)

        try:
            # Create directory if does not exist
            dirname = os.path.dirname(abs_file_path)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            # file handler
            f = open(abs_file_path, "wt")
            return lambda record: f.write(record.format() + "\n")
        except Exception:
            if LoggingConfiguration.DEBUG:
                six.print_("[Rookout] Failed to open log file: %s".format(abs_file_path))
                traceback.print_exc()

            return None

    @staticmethod
    def _get_stderr_handler():
        if six.PY3:
            # In some versions of Python3, trying to write to STDERR in a
            # daemon thread after the main thread has ended might
            # lead to crashes.
            import atexit

            def disable_writing():
                global STDERR_WRITABLE
                STDERR_WRITABLE = False

            atexit.register(disable_writing)

        def _stderr_handler(record):
            if sys and sys.stderr and STDERR_WRITABLE:
                sys.stderr.write(record.format() + "\n")

        return _stderr_handler

    def _remote_handler(self, record):
        if not self.output:
            return

        try:
            arguments = {}

            if record.args:
                arguments['args'] = PythonObjectNamespace(record.args)

            self.output.send_log_message(
                record.level_no,
                record.time,
                record.filename,
                record.lineno,
                record.text,
                record.formatted_message,
                arguments)
        except Exception: # We are potentially deep in error handling code - just ignore
            pass


logger = Logger()
