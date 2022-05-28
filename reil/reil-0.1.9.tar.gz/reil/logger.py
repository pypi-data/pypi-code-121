import logging
from typing import Any, Dict, Optional

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

DEFAULT_FORMAT = ' %(name)s :: %(levelname)-8s :: %(message)s'


class Logger:
    def __init__(
            self, logger_name: str, logger_level: Optional[int] = None,
            logger_filename: Optional[str] = None,
            fmt: Optional[str] = None) -> None:
        self._name = logger_name
        self._level = logger_level or logging.WARNING
        self._filename = logger_filename
        self._fmt = fmt or DEFAULT_FORMAT

        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(self._level)
        if not self._logger.hasHandlers():
            if self._filename is None:
                handler = logging.StreamHandler()
            else:
                handler = logging.FileHandler(self._filename)

            handler.setFormatter(logging.Formatter(fmt=self._fmt))
            self._logger.addHandler(handler)
        else:
            self._logger.debug(
                f'logger {self._name} already has a handler.')

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls(**config)

    def get_config(self) -> Dict[str, Any]:
        return self.__getstate__()

    def debug(self, msg: str):
        self._logger.debug(msg)

    def info(self, msg: str):
        self._logger.info(msg)

    def warning(self, msg: str):
        self._logger.warning(msg)

    def error(self, msg: str):
        self._logger.error(msg)

    def exception(self, msg: str):
        self._logger.exception(msg)

    def critical(self, msg: str):
        self._logger.critical(msg)

    def __getstate__(self):
        state = dict(
            name=self._name,
            level=self._level,
            filename=self._filename)

        if self._fmt != DEFAULT_FORMAT:
            state.update({'fmt': self._fmt})

        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        try:
            self.__init__(
                logger_name=state['name'], logger_level=state.get('level'),
                logger_filename=state.get('filename'), fmt=state.get('fmt'))
        except KeyError:
            try:
                self.__init__(
                    logger_name=state['_name'],
                    logger_level=state.get('_level'),
                    logger_filename=state.get('_filename'),
                    fmt=state.get('_fmt'))
            except KeyError:
                self.__init__(
                    logger_name=state['logger_name'],
                    logger_level=state.get('logger_level'),
                    logger_filename=state.get('logger_filename'),
                    fmt=state.get('_fmt'))
