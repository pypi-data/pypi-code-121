# coding:utf-8
__author__ = 'rk.feng'

import asyncio
import logging  # noqa
import os  # noqa
import random
import time
import typing
import unittest
from asyncio import futures
from collections import OrderedDict
from pprint import pprint
from urllib.parse import quote

import tornado.websocket
from tornado.websocket import WebSocketClientConnection, WebSocketClosedError

from pyxtools.basic_tools.md5_tools import create_guid, get_md5

REQUIRE_TEXT = """
pip install tornado>=5.1
"""


def build_device_id(route_key: str, device_hash: str = None) -> str:
    device_hash = device_hash or create_guid()
    return get_md5(route_key + "." + route_key[:-1])[:10] + get_md5(device_hash)[:5]


def check_device_id(route_key: str, device_id: str) -> bool:
    if len(route_key) < 3:
        return False
    if len(device_id) != 15:
        return False
    if get_md5(route_key + "." + route_key[:-1])[:10] != device_id[:10]:
        return False
    return True


class _RecvObj:
    __slots__ = ("fut", "waited")

    def __init__(self, fut: asyncio.Future, waited: float = 0, ):
        self.waited = waited  # waited的时间戳, <= 0 表示 还没被占用
        self.fut = fut

    @property
    def weight(self):
        had_data = bool(self.fut.cancelled() or self.fut.done())

        return 1 if had_data else 0, self.waited if self.waited > 0 else 0


class WsP2PClient:
    def __init__(self, route_key: str, ws_url: str, logger: logging.Logger, device_hash: str = None):
        self.logger = logger

        self._ws_server_conn: WebSocketClientConnection = None
        self.device_id: str = build_device_id(route_key, device_hash)
        self.route_key: str = route_key
        self._send_cache: typing.OrderedDict[str, asyncio.Future] = OrderedDict()
        self._recv_cache: typing.List[_RecvObj] = []
        self.ws_url = ws_url + f"?device_id={quote(self.device_id)}&route_key={quote(self.route_key)}"

        self._lock = asyncio.Lock()

    @classmethod
    def _create_frame_id(cls) -> str:
        return get_md5(create_guid())[:10]

    async def _open(self):
        """ """
        if self._ws_server_conn is not None:
            return

        async with self._lock:
            if self._ws_server_conn is not None:
                return

            self.logger.info(f"route_key : {self.route_key}, device_id {self.device_id}")
            self._ws_server_conn = await tornado.websocket.websocket_connect(
                self.ws_url,
                connect_timeout=60,
                ping_interval=10,
                on_message_callback=self._on_message_callback,
            )

    def _on_message_callback(self, message: str):
        async def on_message_async(msg: str):
            if not msg or len(msg) < 10:
                return
            frame_id, msg = msg[:10], msg[10:]
            if frame_id in self._send_cache:
                # response
                if not self._send_cache[frame_id].cancelled() and not self._send_cache[frame_id].done():
                    self._send_cache[frame_id].set_result(msg)
            else:
                # request
                fut: asyncio.Future = None
                recv_obj_list = sorted(
                    [recv_obj for recv_obj in self._recv_cache if not recv_obj.fut.done() or not recv_obj.fut.cancelled()],
                    key=lambda x: x.weight, reverse=True
                )
                if recv_obj_list:
                    recv_obj = recv_obj_list[0]
                    fut = recv_obj.fut
                else:
                    recv_obj = _RecvObj(fut=asyncio.Future())
                    fut = recv_obj.fut
                    self._recv_cache.append(recv_obj)

                fut.set_result((frame_id, msg))

        self.logger.info(f"on_message {message}")
        asyncio.ensure_future(on_message_async(message))

    async def send(self, msg: str, timeout: int = 0) -> str:
        await self._open()
        frame_id = self._create_frame_id()
        self._send_cache[frame_id] = asyncio.Future()
        # self.logger.info("[send][device_id {}][frame_id {}][msg {}]".format(self.device_id, frame_id, msg))
        if self._ws_server_conn is None:
            raise ValueError("websocket closed!")

        try:
            await self._ws_server_conn.write_message(message=frame_id + msg)
        except WebSocketClosedError:
            self._ws_server_conn = None
            raise ValueError("websocket closed!")

        # self.logger.info("[send][device_id {}][frame_id {}][msg {}]".format(self.device_id, frame_id, msg))
        if timeout and timeout > 0:
            try:
                res = await asyncio.wait_for(self._send_cache[frame_id], timeout=timeout)
            except futures.TimeoutError as e:
                if not self._send_cache[frame_id].cancelled() or not self._send_cache[frame_id].done():
                    self._send_cache[frame_id].set_exception(e)
                raise
        else:
            res = await self._send_cache[frame_id]
            del self._send_cache[frame_id]

        return res

    async def receive(self, handle_msg: typing.Callable[[str, str], typing.Awaitable[str]]):
        await self._open()

        # get req
        fut: asyncio.Future = None
        recv_obj_list = sorted(
            [recv_obj for recv_obj in self._recv_cache if recv_obj.waited <= 0], key=lambda x: x.weight, reverse=True
        )
        if recv_obj_list:
            recv_obj = recv_obj_list[0]
            recv_obj.waited = time.time()
            fut = recv_obj.fut
        else:
            recv_obj = _RecvObj(fut=asyncio.Future(), waited=time.time())
            self._recv_cache.append(recv_obj)
            fut = recv_obj.fut

        frame_id, msg = await fut
        _remove_index = None
        for recv_i, recv_obj in enumerate(self._recv_cache):
            if id(recv_obj.fut) == id(fut):
                _remove_index = recv_i
                break
        if _remove_index is not None:
            self._recv_cache.pop(_remove_index)

        # handle req
        if handle_msg:
            resp = await handle_msg(frame_id, msg)
        else:
            resp = ""

        # send resp
        if self._ws_server_conn is None:
            raise ValueError("websocket closed!")

        try:
            await self._ws_server_conn.write_message(message=frame_id + resp)
        except WebSocketClosedError:
            self._ws_server_conn = None
            raise ValueError("websocket closed!")


class T(unittest.TestCase):
    def setUp(self) -> None:
        logger = logging.getLogger()

        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        self.logger = logger
        self.route_key = 'aaaxbbb2'
        self.ws_url = "wss://www.example.com/ws/p2p"

    def testServer(self):
        async def consume(frame_id, msg: str) -> str:
            self.logger.info(f"[on_receive_msg][frame_id {frame_id}][msg {msg}]")
            await asyncio.sleep(random.randint(1, 3))
            return frame_id + "done" + msg

        async def s():
            x = WsP2PClient(route_key=self.route_key, ws_url=self.ws_url, logger=self.logger)
            while True:
                await x.receive(handle_msg=consume)

        asyncio.get_event_loop().run_until_complete(s())

    def testClient(self):
        async def c():
            x = WsP2PClient(route_key=self.route_key, ws_url=self.ws_url, logger=self.logger)
            i = 0
            while True:
                v_list = await asyncio.gather(*[
                    x.send(f"msg{i + 1}", timeout=2),
                    x.send(f"{i + 1}{i + 2}"),
                ])
                for v in v_list:
                    pprint(v)
                i += 2

        asyncio.get_event_loop().run_until_complete(c())
