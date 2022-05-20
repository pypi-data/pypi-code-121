"""
Copyright 2021 Daniel Afriyie

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import logging
import pathlib
import os
import asyncio
import threading
import typing

from colorama import Fore

from ru.utils import abstractmethod


def logger(name: str = None, fmt: str = None, filename: str = None):
    lg = Logger(name, fmt, filename)
    return lg()


class Logger:
    __loggers = {}

    def __init__(self, name: str = None, fmt: str = None, filename: str = None):
        self._name = name if name else __name__
        self._fmt = fmt if fmt else '%(asctime)s:%(levelname)s:%(message)s'
        self._filename = filename
        self._root_path = pathlib.Path('.').absolute()

    def _get_log_file(self):
        fn = self._filename if self._filename else 'log'
        log_path = os.path.join(self._root_path, 'logs')
        log_file = os.path.join(log_path, f'{fn}.log')
        if not os.path.exists(log_path):
            os.mkdir(os.path.join(log_path))
        return log_file

    def _create_logger(self):
        _logger = logging.getLogger(self._name)
        _logger.setLevel(level=logging.DEBUG)

        formatter = logging.Formatter(self._fmt)
        file_handler = logging.FileHandler(self._get_log_file(), encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)

        _logger.addHandler(file_handler)
        _logger.addHandler(stream_handler)

        return _logger

    @abstractmethod
    def _log_file_manager(self):
        """
        check if the log file size is more than 10mb then deletes it
        """

    def __call__(self):
        if self._name in self.__loggers:
            return self.__loggers.get(self._name)
        else:
            _logger = self._create_logger()
            self.__loggers[self._name] = _logger
            return _logger


class BaseColorPrint:
    mutex: typing.Union[asyncio.Lock, threading.Lock, threading.RLock] = None

    def _print(self, text, color):
        with self.mutex:
            print(color + text)

    def info(self, text, color=Fore.MAGENTA):
        self._print(text, color)

    def warning(self, text, color=Fore.YELLOW):
        self._print(text, color)

    def success(self, text, color=Fore.GREEN):
        self._print(text, color)

    def error(self, text, color=Fore.RED):
        self._print(text, color)


class ColorPrint(BaseColorPrint):
    mutex = threading.Lock()


class AsyncColorPrint(BaseColorPrint):
    mutex = asyncio.Lock()

    async def _print(self, text, color):
        async with self.mutex:
            print(color + text)

    async def info(self, text, color=Fore.MAGENTA):
        await self._print(text, color)

    async def warning(self, text, color=Fore.YELLOW):
        await self._print(text, color)

    async def success(self, text, color=Fore.GREEN):
        await self._print(text, color)

    async def error(self, text, color=Fore.RED):
        await self._print(text, color)
