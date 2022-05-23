import logging
import re
from pathlib import Path
from typing import Any, TextIO

from colorama import Fore

import beni
import beni.color as bprint

_loggerName = 'beni'

_countWarning: int = 0
_countError: int = 0
_countCritical: int = 0


def init(loggerName: str = '', loggerLevel: int = logging.INFO, logFile: Path | None = None):
    LOGGER_FORMAT = '%(asctime)s %(levelname)-1s %(message)s', '%Y-%m-%d %H:%M:%S'
    LOGGER_LEVEL_NAME = {
        logging.DEBUG: 'D',
        logging.INFO: '',
        logging.WARNING: 'W',
        logging.ERROR: 'E',
        logging.CRITICAL: 'C',
    }

    if loggerName:
        global _loggerName
        _loggerName = loggerName

    logger = logging.getLogger(_loggerName)
    logger.setLevel(loggerLevel)
    for loggingLevel, value in LOGGER_LEVEL_NAME.items():
        logging.addLevelName(loggingLevel, value)

    loggerFormatter = logging.Formatter(*LOGGER_FORMAT)

    class CustomStreamHandler(logging.StreamHandler):

        stream: TextIO

        def emit(self, record: logging.LogRecord):
            try:
                msg = self.format(record) + self.terminator
                # issue 35046: merged two stream.writes into one.
                func = self.stream.write
                if record.levelno == logging.WARNING:
                    global _countWarning
                    _countWarning += 1
                    bprint.set(Fore.YELLOW)

                elif record.levelno == logging.ERROR:
                    global _countError
                    _countError += 1
                    bprint.set(Fore.LIGHTRED_EX)
                elif record.levelno == logging.CRITICAL:
                    global _countCritical
                    _countCritical += 1
                    bprint.set(Fore.LIGHTMAGENTA_EX)
                func(msg)
                bprint.clear()
                self.flush()
            except RecursionError:  # See issue 36272
                raise
            except Exception:
                self.handleError(record)

    loggerHandler = CustomStreamHandler()
    loggerHandler.setFormatter(loggerFormatter)
    loggerHandler.setLevel(loggerLevel)
    logger.addHandler(loggerHandler)

    if logFile:

        class CustomFileHandler(logging.FileHandler):

            _write_func: Any
            _xx = re.compile(r'\x1b\[\d+m')

            def _open(self):
                result = super()._open()
                self._write_func = result.write
                setattr(result, 'write', self._write)
                return result

            def _write(self, msg: str):
                msg = self._xx.sub('', msg)
                self._write_func(msg)

        beni.makeDir(logFile.parent)
        fileLoggerHandler = CustomFileHandler(logFile, delay=True)
        fileLoggerHandler.setFormatter(loggerFormatter)
        fileLoggerHandler.setLevel(loggerLevel)
        logger.addHandler(fileLoggerHandler)


def debug(msg: Any, wrap: bool = False, *args: Any, **kwargs: Any):
    logging.getLogger(_loggerName).debug(_format(msg, wrap), *args, **kwargs)


def info(msg: Any, wrap: bool = False, *args: Any, **kwargs: Any):
    logging.getLogger(_loggerName).info(_format(msg, wrap), *args, **kwargs)


def warning(msg: Any, wrap: bool = False, *args: Any, **kwargs: Any):
    logging.getLogger(_loggerName).warning(_format(msg, wrap), *args, **kwargs)


def error(msg: Any, wrap: bool = False, *args: Any, **kwargs: Any):
    logging.getLogger(_loggerName).error(_format(msg, wrap), *args, **kwargs)


def critical(msg: Any, wrap: bool = False, *args: Any, **kwargs: Any):
    logging.getLogger(_loggerName).critical(_format(msg, wrap), *args, **kwargs)


def _format(msg: Any, wrap: bool):
    if wrap:
        return '\n\n' + msg + '\n'
    else:
        return msg


def getCountWarning():
    return _countWarning


def setCountWarning(value: int):
    global _countWarning
    _countWarning = value


def getCountError():
    return _countError


def setCountError(value: int):
    global _countError
    _countError = value


def getCountCritical():
    return _countCritical


def setCountCritical(value: int):
    global _countCritical
    _countCritical = value
