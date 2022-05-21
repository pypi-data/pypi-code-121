# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(r'../'))

from hagworm.extend.asyncio.base import Utils, AsyncCirculatorForSecond
from hagworm.extend.asyncio.command import Launcher, MainProcessAbstract, ChildProcessAbstract


class MainProcess(MainProcessAbstract):

    async def _handle_message(self, message):

        await self._push_server.send(message)


class ChildProcess(ChildProcessAbstract):

    async def _run(self):

        async for idx in AsyncCirculatorForSecond(max_times=5):

            await self._push_client.send(f'{self._process_id}_{idx}')

            message = await self._pull_client.recv()

            Utils.log.info(message)


if __name__ == r'__main__':

    Launcher(daemon=MainProcess(2)).run(ChildProcess())
