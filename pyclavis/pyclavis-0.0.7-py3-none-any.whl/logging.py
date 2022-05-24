import sys
import os
import logging
import logging.handlers
import tempfile

_level = logging.INFO

_datefmt = "%Y.%m.%d %H:%M:%S"

_format = "%(levelname)-8s %(message)s"
_fileformat = "%(asctime)-8s %(levelname)s\t%(message)s"

_logger = None
_filehandler = None


#
# https://docs.python.org/3/howto/logging-cookbook.html
#


def setlevel(level=None, logtofile=False, opts=None):

    global _level, _logger

    if level:
        _level = level

    if _logger == None:
        # create root logger
        _logger = logging.getLogger()

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(_level)

        # create formatter
        formatter = logging.Formatter(_format, datefmt=_datefmt)

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        _logger.addHandler(ch)

    for h in [_logger, *_logger.handlers]:
        if h:
            h.setLevel(_level)

    if logtofile:
        setlogfile(opts=opts)


def setdebug():
    setlevel(logging.DEBUG)


def setlogfile(pnam=None, path=None, opts=None):

    global _filehandler
    if _filehandler:
        return

    if opts == None:
        opts = {"maxBytes": 1024 * 1024, "backupCount": 7}

    setlevel()

    if pnam == None:
        pnam = sys.argv[0]
    if path == None:
        path = tempfile.gettempdir()

    pnam, _ = os.path.splitext(os.path.basename(pnam))

    fnam = os.path.join(path, pnam, pnam + ".log")

    os.makedirs(os.path.dirname(fnam), exist_ok=True)

    _filehandler = logging.handlers.RotatingFileHandler(fnam, **opts)
    _filehandler.setLevel(_level)

    formatter = logging.Formatter(_fileformat, datefmt=_datefmt)
    _filehandler.setFormatter(formatter)
    _logger.addHandler(_filehandler)

    return fnam


def _flat(args):
    fs = map(lambda x: str(x), args)
    return " ".join(fs)


def _log(level, args):
    if _logger.isEnabledFor(level):
        _logger.log(level, _flat(args))


def log(*args):
    _log(logging.INFO, args)


def print_t(*args):
    _log(logging.DEBUG, args)


def print_w(*args):
    _log(logging.WARNING, args)


def print_e(*args):
    _log(logging.CRITICAL, args)


# create logger

setlevel()
