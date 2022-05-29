import os
import datetime
import sys
from typing import List, Union, Any

from loguru import logger
from loguru._logger import Logger


class MyLogger:

    def __init__(
            self,
            logger: 'logger',
            parent_dir: str = '',
            logs_dir: str = 'logs',
            date_dir: bool = True,
            default_log_level: int = int(os.getenv("LOGGING_LEVEL", 1))
    ):
        self.LOGGING_DIRECTORY: str = os.path.join(parent_dir, logs_dir)
        if date_dir:
            current_date: str = datetime.datetime.today().strftime("%Y-%m-%d")
            self.LOGGING_DIRECTORY: str = os.path.join(self.LOGGING_DIRECTORY, current_date)
        self.LOGGING_LEVEL: int = default_log_level
        self.levels: List[dict] = []
        self._logger: logger = logger
        self._logger.remove()

    def add_level(self, name: str, color: str = "<white>", no: int = 0, log_filename: str = ''):
        """Add new logging level to loguru.logger config
        :param name - logging level name
        :param color  - color for logging level
        :param no - minimal logging level
        :param log_filename - filename for current level
        """

        if not self.levels:
            self.levels = []
        if not log_filename:
            log_filename = f'{name.lower()}.log'
        level_data: dict = {
            "config": {"name": name, "color": color},
            "path": os.path.join(self.LOGGING_DIRECTORY, log_filename)
        }
        if no:
            level_data["config"].update(no=no)
        self.levels.append(level_data)
        if self._is_level_exists(name):
            return
        self._logger.configure(levels=[level_data["config"]])

    def _is_level_exists(self, name: str) -> bool:
        level_names = tuple(level.get("config", {}).get("name") for level in self.levels)
        return name in level_names

    def add_logger(self, **kwargs):
        """Add new logging settings to loguru.logger
        :param level int | str - logging level (level=5 or level="DEBUG")
        :param sink - interace for logging out (filepath, stdout, etc),
            default: 'parent_dir/logs/date_dir/"level_name".log
        :param: More read loguru docs
        """
        level: Union[int, str] = kwargs.get("level", self.LOGGING_LEVEL)
        if self._is_level_exists(level):
            return
        sink: Any = kwargs.get("sink")
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


def get_logger() -> 'Logger':
    return MyLogger(logger).get_default().get_new_logger()
