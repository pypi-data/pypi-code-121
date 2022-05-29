import os
import datetime
import sys
from pathlib import Path
from typing import List

from loguru import logger
from loguru._logger import Logger


class MyLogger:
    PATH = Path(__file__).resolve().parent
    TODAY = datetime.datetime.today().strftime("%Y-%m-%d")
    LOGGING_DIRECTORY = os.path.join(PATH, '../logs', TODAY)
    LOGGING_LEVEL = int(os.getenv("LOGGING_LEVEL", 1))
    levels: List[dict] = None

    def __init__(self, logger: 'logger'):
        self._logger: logger = logger
        self._logger.remove()
        self.get_default()

    def add_level(self, name: str, color: str = "<white>", no: int = 0, log_filename: str = ''):
        """Add new logging level to loguru.logger config"""

        if self.levels is None:
            self.levels = []
        if not log_filename:
            log_filename = f'{name.lower()}.log'
        level_data: dict = {
            "config": {"name": name, "color": color},
            "path": os.path.join(self.LOGGING_DIRECTORY, log_filename)
        }
        if no:
            level_data["config"].update(no=no)
        self._logger.configure(levels=[level_data["config"]])
        self.levels.append(level_data)

    def add_logger(self, **kwargs):
        """Add new logging settings to loguru.logger"""

        level = kwargs.get("level", self.LOGGING_LEVEL)
        sink = kwargs.get("sink")
        if not sink:
            sink: str = [elem for elem in self.levels if elem["config"]["name"] == level][0]["path"]
            kwargs.update(sink=sink)
        self._logger.add(**kwargs)

    def catch(self, *args, **kwargs):
        return self._logger.catch(*args, **kwargs)

    def info(self, text, *args, **kwargs):
        return self._logger.info(text, *args, **kwargs)

    def debug(self, text, *args, **kwargs):
        return self._logger.debug(text, *args, **kwargs)

    def error(self, text, *args, **kwargs):
        return self._logger.error(text, *args, **kwargs)

    def warning(self, text, *args, **kwargs):
        return self._logger.warning(text, *args, **kwargs)

    def success(self, text, *args, **kwargs):
        return self._logger.success(text, *args, **kwargs)

    def get_new_logger(self) -> 'Logger':
        """Returns updated loguru.logger instance"""

        return self._logger

    def get_default(self) -> 'MyLogger':
        """Returns self instance with default settings"""

        self.add_level("DEBUG", "<white>")
        self.add_level("INFO", "<fg #afffff>")
        self.add_level("WARNING", "<light-yellow>")
        self.add_level("ERROR", "<red>")
        self.add_logger(enqueue=True, level='ERROR', rotation="50 MB")
        self.add_logger(sink=sys.stdout)

        return self


logger: 'Logger' = MyLogger(logger).get_new_logger()
