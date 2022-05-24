import datetime
import logging
import logging.config
import os


class Logger(object):

    def __init__(self, filename: str = None, path: str = None,
                 level: int = None):
        """Creates a basic logger for console/terminal and optional file output.

        Args:
            filename: Name of the file the output should be logged to, file format can be ommited.
            Current timestamp and file format is automatically appened to the given filename.
            If no, filename is given, the output is written to console/terminal only.
            path: Optional path to the logging file. If omitted, file is created at the current working directory.
            level: Specifies which information should be logged as specified by the python logging module.
            If not set, default console level is INFO and default file level is DEBUG.
        """
        if filename is not None:
            self._filename = filename.split("\\")[-1] if len(
                filename.split("\\")) > 1 else filename.split("/")[-1]
        else:
            self._filename = filename
        self._path = path if path is not None else ''
        self.root_logger = logging.getLogger(None)
        self.root_logger.setLevel(logging.DEBUG)

        self.root_formatter = logging.Formatter(
            '### %(levelname)-8s %(asctime)s  %(name)-40s ###\n%(message)s\n')

        # initialize FileHandler
        if self._filename is not None:
            self.file_handler = logging.handlers.RotatingFileHandler(
                os.path.join(self._path, "{}_{}.txt".format(filename,
                                                            datetime.datetime.now().isoformat()).replace(
                    ':', '-')), maxBytes=20 * 1024 ** 2,
                backupCount=3)
            self.file_handler.doRollover()
            if level is None:
                self.file_handler.setLevel(logging.DEBUG)
            else:
                self.file_handler.setLevel(level)
            self.file_handler.setFormatter(self.root_formatter)
            self.root_logger.addHandler(self.file_handler)

        # initialize StreamHandler (Console Output)
        self.console_handler = logging.StreamHandler()
        if level is None:
            self.console_handler.setLevel(logging.INFO)
        else:
            self.console_handler.setLevel(level)
        self.console_handler.setFormatter(self.root_formatter)
        self.root_logger.addHandler(self.console_handler)

    def get(self, name: str = None) -> logging.Logger:
        """Returns the basic python logging utility.

        Args:
            name: Name to identify the logger. If no name is given, the RootLogger is returned.

        Returns: A basic python logger with the given name.

        """
        return logging.getLogger(name)

    def set_logging_level(self, level: int, target: str = '') -> None:
        """Sets the logging level.

        Args:
            level: Specifies which information should be logged as specified by the python logging module.
            target: If specified as "FileHandler" the minimum file output is set to the given level.
             If specified as "StreamHandler" the minimum console/terminal output is set to the given level.
             If omitted, the level is set for both handlers.

        """
        if target == 'FileHandler':
            if self._filename is not None:
                self.file_handler.setLevel(level)
        elif target == 'StreamHandler':
            self.console_handler.setLevel(level)
        else:
            self.console_handler.setLevel(level)
            if self._filename is not None:
                self.file_handler.setLevel(level)
