import sys
import logging
import six
import os
import threading

from rook.processor.namespaces.container_namespace import ContainerNamespace
from rook.augs.processor_extensions.namespaces.log_record_namespace import LogRecordNamespace

# For traceback analysis
currentframe = lambda: sys._getframe(3)
_srcfile = os.path.normcase(currentframe.__code__.co_filename)
_logging_srcfile = logging._srcfile

# Copied from logging
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_levelNames = {
    CRITICAL : 'CRITICAL',
    ERROR : 'ERROR',
    WARNING : 'WARNING',
    INFO : 'INFO',
    DEBUG : 'DEBUG',
    NOTSET : 'NOTSET',
    'CRITICAL' : CRITICAL,
    'ERROR' : ERROR,
    'WARN' : WARNING,
    'WARNING' : WARNING,
    'INFO' : INFO,
    'DEBUG' : DEBUG,
    'NOTSET' : NOTSET,
}

class LoggingLocationService(object):
    NAME = "logging"

    METHODS_TO_HOOK = ["critical", "error", "warning", "info", "debug"]

    def __init__(self):
        self._lock = threading.RLock()

        self._hooked = False
        self._originalMethods = dict()
        self._originalHandle = None

        self._augs = dict()

    def add_logging_aug(self, aug):
        with self._lock:
            self._installHooks()

            self._augs[aug.aug_id] = aug
            aug.set_active()

    def remove_aug(self, aug_id):
        with self._lock:
            try:
                del self._augs[aug_id]
            except KeyError:
                pass

            if not self._augs:
                self._removeHooks()

    def clear_augs(self):
        with self._lock:
            for aug_id in list(self._augs.keys()):
                self.remove_aug(aug_id)

            self._augs = dict()
            self._removeHooks()

    def close(self):
        self.clear_augs()
        self._removeHooks()

    def pre_fork(self):
        if self._lock:
            self._lock.acquire()

    def post_fork(self):
        if self._lock:
            self._lock.release()

        self._removeHooks()

    def _installHooks(self):
        with self._lock:
            if self._hooked:
                return

            # TODO - hook log
            # TODO - properly set exc_info=1 on exception
            for name in self.METHODS_TO_HOOK:
                self._wrap_logging_method(name)

            self._hooked = True

    # based off https://github.com/getsentry/raven-python/blob/master/raven/breadcrumbs.py
    def _wrap_logging_method(self, name):

        func = logging.Logger.__dict__[name]
        code = func.__code__

        def _callback(logger, level, msg, *args, **kwargs):
            try:
                self._run_augs(self._create_record(logger, level, msg, args, **kwargs))
            # Don't have unit tests
            except AssertionError:
                raise
            except:  # lgtm[py/catch-base-exception]
                pass

        # This requires a bit of explanation why we're doing this.  Due to how
        # logging itself works we need to pretend that the method actually was
        # created within the logging module.  There are a few ways to detect
        # this and we fake all of them: we use the same function globals (the
        # one from the logging module), we create it entirely there which
        # means that also the filename is set correctly.  This fools the
        # detection code in logging and it makes logging itself skip past our
        # code when determining the code location.
        #
        # Because we point the globals to the logging module we now need to
        # refer to our own functions (original and the crumb recording
        # function) through a closure instead of the global scope.
        #
        # We also add a lot of newlines in front of the code so that the
        # code location lines up again in case someone runs inspect.getsource
        # on the function.
        ns = {}
        eval(compile('''%(offset)sif 1:	
        def factory(original, callback):	
            def %(name)s(self, *args, **kwargs):
                callback(self, %(level)d, *args, **kwargs)
                return original(self, *args, **kwargs)
            return %(name)s	
        \n''' % {
            'offset': '\n' * (code.co_firstlineno - 3),
            'name': name,
            'level': _levelNames[name.upper()]
        }, _logging_srcfile, 'exec'), logging.__dict__, ns)

        new_func = ns['factory'](func, _callback)
        new_func.__doc__ = func.__doc__

        # In theory this should already be set correctly, but in some cases
        # it is not.  So override it.
        new_func.__module__ = func.__module__
        new_func.__name__ = func.__name__

        self._originalMethods[name] = getattr(logging.Logger, name)
        setattr(logging.Logger, name, new_func)

    def _removeHooks(self):
        with self._lock:
            if not self._hooked:
                return

            for name in self.METHODS_TO_HOOK:
                setattr(logging.Logger, name, self._originalMethods[name])
                self._originalMethods[name] = None

            self._hooked = False

    # TODO - This is method is quite expensive and builds the full LogRecordNamespace object for every log call
    # TODO - Change into a lazy namespace to only calculate whatever is needed to evaluate the logging criteria
    def _create_record(self, logger, level, msg, args, exc_info=None, extra=None):
        if _srcfile:
            # IronPython doesn't track Python frames, so findCaller raises an
            # exception on some versions of IronPython. We trap it here so that
            # IronPython can use logging.
            try:
                fn, lno, func = self.findCaller()
            except ValueError:
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = logger.makeRecord(logger.name, level, fn, lno, msg, args, exc_info, func, extra)
        return record

    def findCaller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = currentframe()
        #On some versions of IronPython, currentframe() returns None if
        #IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile or filename == _logging_srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv

    def _run_augs(self, record):
        extracted = ContainerNamespace({'log_record': LogRecordNamespace(record)})

        with self._lock:
            for aug in six.itervalues(self._augs):
                aug.execute(None, extracted)
