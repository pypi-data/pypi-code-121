# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import sys
import asyncio

from ... import hagworm_slogan
from ... import __version__ as hagworm_version

from .base import install_uvloop, Utils

from ..error import catch_error
from ..process import fork_processes
from ..logging import DEFAULT_LOG_FILE_ROTATOR
from ..interface import FunctorInterface, RunnableInterface
from ..asyncio.zmq import Push, Pull


SIGNAL_PROTOCOL = r'tcp'
SIGNAL_PORT_1 = 83310
SIGNAL_PORT_2 = 10601


class Daemon(FunctorInterface):

    def __init__(self, child_num=2, keep_alive=False):

        if child_num < 2:
            raise ValueError(r'child_num cannot be less than 2')

        self._child_num = child_num
        self._keep_alive = keep_alive

        self._pids = set()

    def is_active(self):

        return self._child_num != 0 and len(self._pids) != 0

    def _fork_processes(self):

        while len(self._pids) < self._child_num:

            pid = fork_processes()

            if pid == 0:
                self._child_num = 0
                return False

            self._pids.add(pid)

        return True

    def _check_processes(self):

        for pid in self._pids.copy():

            if os.waitpid(pid, os.WNOHANG)[0] != pid:
                continue

            self._pids.remove(pid)

            if self._keep_alive:
                self._fork_processes()

    def _run(self):

        while True:

            self._check_processes()

            if not self.is_active():
                return

    def __call__(self):

        if self._fork_processes():
            self._run()
            sys.exit(0)


class MainProcessAbstract(Daemon):

    def __init__(self, child_num=2):

        Daemon.__init__(self, child_num, False)

        global SIGNAL_PROTOCOL, SIGNAL_PORT_1, SIGNAL_PORT_2

        self._push_server = Push(f'{SIGNAL_PROTOCOL}://*:{SIGNAL_PORT_1}', True)
        self._pull_server = Pull(f'{SIGNAL_PROTOCOL}://*:{SIGNAL_PORT_2}', True)

    async def _handle_message(self, message):
        raise NotImplementedError()

    async def _recv_message(self):

        while True:

            message = await self._pull_server.recv(True)

            if message is None:
                break
            else:
                await self._handle_message(message)

    async def _run(self):

        while True:

            self._check_processes()

            if self.is_active():
                await self._recv_message()
            else:
                break

    def __call__(self):

        if not self._fork_processes():
            return

        self._push_server.open()
        self._pull_server.open()

        with catch_error():
            Utils.run_until_complete(self._run())

        self._push_server.close()
        self._pull_server.close()

        sys.exit(0)


class ChildProcessAbstract(FunctorInterface):

    def __init__(self):

        global SIGNAL_PROTOCOL, SIGNAL_PORT_1, SIGNAL_PORT_2

        self._push_client = Push(f'{SIGNAL_PROTOCOL}://localhost:{SIGNAL_PORT_2}')
        self._pull_client = Pull(f'{SIGNAL_PROTOCOL}://localhost:{SIGNAL_PORT_1}')

        self._process_id = Utils.getpid()

    async def __call__(self):

        self._push_client.open()
        self._pull_client.open()

        with catch_error():
            await self._run()

        self._push_client.close()
        self._pull_client.close()

    async def _run(self):
        raise NotImplementedError()


class Launcher(RunnableInterface):
    """异步版本的启动器

    用于简化和统一程序的启动操作

    """

    def __init__(self,
                 log_file_path=None, log_level=r'INFO',
                 log_file_rotation=DEFAULT_LOG_FILE_ROTATOR, log_file_retention=0xff,
                 daemon=None, debug=False
                 ):

        if log_file_path:

            _log_file_path = Utils.path.join(
                log_file_path,
                r'runtime_{time}.log'
            )

            Utils.log.add(
                _log_file_path,
                level=log_level,
                enqueue=True,
                backtrace=debug,
                rotation=log_file_rotation,
                retention=log_file_retention
            )

        else:

            Utils.log.level(log_level)

        environment = Utils.environment()

        Utils.log.info(
            f'{hagworm_slogan}'
            f'hagworm {hagworm_version}\n'
            f'python {environment["python"]}\n'
            f'system {" ".join(environment["system"])}'
        )

        install_uvloop()

        if daemon:
            daemon()

        self._event_loop = asyncio.get_event_loop()
        self._event_loop.set_debug(debug)

    def run(self, func, *args, **kwargs):

        pid = Utils.getpid()

        Utils.log.success(f'Start process pid.{pid}')

        self._event_loop.run_until_complete(func(*args, **kwargs))

        Utils.log.success(f'Stop process pid.{pid}')
