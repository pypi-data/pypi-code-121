# -*- coding: UTF-8 -*-

from configparser import ConfigParser
from os.path import isfile
from sys import argv
from typing import Sequence

from .argsparser import ArgsParser
from ..handles import FileHandle
from ..utils import ensure_folder


class CfgParser(ConfigParser):
    """Configuration handle."""

    def __init__(self, *args, **kwargs):
        super(CfgParser, self).__init__(*args, **kwargs)
        self._parser = ArgsParser()

    def parse(self, args: Sequence[str] = None):
        """Parse command-line arguments and update the configuration."""
        if args is None:
            args = argv[1:]

        if len(args) > 0:
            parameters = self._parser.parse(args)
            self.read_dict(dictionary=parameters, source="<cmd-line>")

    def set_defaults(self, **kwargs):
        """Update `DEFAULT` section using the `kwargs`."""
        if len(kwargs) > 0:
            self._read_defaults(kwargs)

    def open(self, file_path: str, encoding: str = "UTF-8", fallback: dict = None):
        """
        Read from configuration `file_path`.
        If `file_path` does not exist and `fallback` is provided
        the latter will be used and a new configuration file will be written.
        """

        if isfile(file_path) is True:
            with FileHandle(file_path, "r", encoding=encoding) as file_handle:
                self.read_file(file_handle, source="<main>")

        elif fallback is not None:
            self.read_dict(dictionary=fallback, source="<backup>")
            self.save(file_path, encoding)

    def save(self, file_path: str, encoding: str):
        """Save the configuration to `file_path`."""
        ensure_folder(file_path)
        with FileHandle(file_path, "w", encoding=encoding) as file_handle:
            self.write(file_handle)
