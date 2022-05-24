import logging
import os
import pathlib
import pykka
from mopidy import core
from tornado import gen, web, websocket, httpclient
logger = logging.getLogger(__name__)
import json
import requests
import asyncio
import time

class MasterApiHandler(web.RequestHandler):

    def initialize(self, master, name):
        self._master = master
        self.devices = dict()
        self._name = name

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self, *args):
        # no body
        # `*args` is for route with `path arguments` supports
        self.set_status(204)
        self.finish()

    def get(self, path):
      if path == 'list':
        device_list = requests.get(f"http://{self._master}:6680/master/masterapi/list").json()
        for device in device_list:
          if device == self._name:
             device_list[device]['me'] = True
        self.write(json.dumps(device_list))
      else:
        self.set_status('404')
        self.write('Not found')


class MasterApiWebSocketHandler(websocket.WebSocketHandler):

    def initialize(self, master, name):
        self._master = master
        self.devices = dict()
        self._name = name

    @classmethod
    def urls(cls):
        return [
            (r'/ws/', cls, {}),  # Route/Handler/kwargs
        ]

    def open(self, channel):
        """
        Client opens a websocket
        """
        self.channel = channel
        loop = asyncio.get_event_loop()
        self.future = self.client_connect()
        asyncio.ensure_future(self.future,loop=loop)


    @asyncio.coroutine
    def client_connect(self):
        try:
          self.ws = yield from websocket.websocket_connect(f"ws://{self._master}:6680/master/socketapi/ws")
          logger.error("connected to master")
          self.future_run = self.run()
          loop = asyncio.get_event_loop()
          asyncio.ensure_future(self.future_run,loop=loop)
        except:
          logger.error("cannot connect to master")

    async def run(self):
      self.opened = True
      while self.opened:
          msg = await self.ws.read_message()
          logger.error("get message")
          logger.error(msg)
          if msg is None:
             self.opened = False
             logger.error('connection closed')
          else:
            self.write_message(msg)


    async def on_message(self, message):
        """
        Message received on channel
        """
        if not hasattr(self,'ws'):
           loop = asyncio.get_event_loop()
           await asyncio.wait([self.future],loop=loop)
           logger.error(self.future)

        logger.error(message)
        try:
          data = json.loads(message)
        except:
          logger.error('bad command received')
          return
        if data['message'] == 'list':
          self.ws.write_message(message)
        if 'activate' in data['message']:
          self.ws.write_message(message)

    def on_close(self):
        self.opened = False
