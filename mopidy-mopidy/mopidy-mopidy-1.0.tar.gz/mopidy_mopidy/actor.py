
from mopidy.audio import PlaybackState
import pykka
import os
from mopidy import exceptions, listener, zeroconf
from mopidy.core import CoreListener
import requests
import logging
import asyncio
from threading import Thread
import multiprocessing
import concurrent.futures
from tornado import websocket, ioloop
import json
import signal
import time

logger = logging.getLogger(__name__)

class MasterFrontend(pykka.ThreadingActor, CoreListener):
    def __init__(self, config, core):
        super(MasterFrontend, self).__init__()
        self.core = core
        mst_config = config['mopidy_mopidy']
        self._name = mst_config['name']
        self._ip = mst_config["ip"]
        self._frontend = mst_config["frontend"]
        self._master_url = "http://{}:6680/master/".format(mst_config['master'])
        self._master_ws = "ws://{}:6680/master/socketapi/ws".format(mst_config['master'])
        self._master_mopidy_ws = "ws://{}:6680/mopidy/ws".format(mst_config['master'])
        self._is_active = False
        self._ws_opened = False
        self._stop = False
        self._mopidy_ws_opened = False
        self.loop = asyncio.new_event_loop()
        self.loop.set_exception_handler(self.handle_exception)
        self.master_task = asyncio.run_coroutine_threadsafe(self.client_connect(),self.loop)
        asyncio.run_coroutine_threadsafe(self.mopidy_connect(),self.loop)
        self.background_thread = Thread(target=self.start_background_loop, args=(self.loop,), daemon=True)
        self.background_thread.start()

        signal.signal(signal.SIGTERM, self.stop)

    def handle_exception(self, loop, context):
      # context["message"] will always be there; but context["exception"] may not
      logger.error(f"LOOP EXCEPTION")

      msg = context.get("exception", context["message"])
      logger.error(f"Caught exception: {msg}")

    def stop(self, p1, p2):
        logger.debug("mopidy stop")
        self._stop = True
        self.mopidy_ws.close()
        self.ws.close()
        time.sleep(1)
        self.loop.call_soon_threadsafe(self.cancel_tasks)
        time.sleep(5)
        os.kill(os.getpid(),signal.SIGKILL)

    def cancel_tasks(self):
        logger.debug("get tasks")
        for task in asyncio.all_tasks():
           logger.debug(task)
        self.loop.stop()


    def start_background_loop(self, loop: asyncio.AbstractEventLoop) -> None:
       logger.debug('starting background thread')
       asyncio.set_event_loop(loop)
       loop.run_forever()

    @asyncio.coroutine
    def websocket_connect(self):
        yield from self.client_connect()
        yield from self.mopidy_connect()

    @asyncio.coroutine
    def client_connect(self):
      while not self._stop:
        self._registered = False
        self._is_active = False
        if self._stop:
           return
        logger.debug("start of master sync")
        try:
          self.ws = yield from websocket.websocket_connect(self._master_ws)
          logger.debug("connected to master")
        except:
          logger.error("cannot connect to master")
          if not self._stop:
            yield from asyncio.sleep(10)
        else:
          yield from self.run()


    @asyncio.coroutine
    def run(self):
      self._ws_opened = True
      self.register()
      self.ws.write_message(json.dumps({"message":"list"}))
      while self._ws_opened and not self._stop:
          logger.debug('master message waiting')
          msg = yield from self.ws.read_message()
          if msg is None:
             if self._ws_opened and not self._stop:
               self._ws_opened = False
               logger.error('master connection closed')
               return
          else:
            data = json.loads(msg)
            if data['msg'] == 'devices':
              for device in data['devices']:
                 if data['devices'][device]['name'] == self._name:
                    self.change_active(data['devices'][device]['active'], data['track_position'])


    @asyncio.coroutine
    def mopidy_connect(self):
      while not self._stop:
        logger.debug("start mopidy connect")
        try:
          self.mopidy_ws = yield from websocket.websocket_connect(self._master_mopidy_ws)
          logger.debug("connected to mopidy at master")
        except:
          logger.error("cannot connect to mopidy at master")
          if not self._stop:
            yield from asyncio.sleep(10)
        else:
          yield from self.mopidy_run()

    @asyncio.coroutine
    def mopidy_run(self):
      self._mopidy_ws_opened = True
      self.get_master_tracklist()
      while self._mopidy_ws_opened and not self._stop:
          msg = yield from self.mopidy_ws.read_message()

          if msg is None:
             if self._mopidy_ws_opened:
               self._mopidy_ws_opened = False
               logger.error('connection closed to mopidy')
               return
          else:
            if self._is_active:
               logger.debug('Skip because active')
               continue
            data = json.loads(msg)
            if 'event' in data:
              if data['event'] == 'tracklist_changed':
                self.get_master_tracklist()
              elif data['event'] == 'track_playback_started':
                track_uri = 'mopidymopidy:track:'+data['tl_track']['track']['uri']
                self.set_current_track(track_uri)
              elif data['event'] == 'playback_state_changed':
                self.core.playback.set_state(data['new_state'])
            else:
              logger.debug(data['id'])
              if data['id'] == 101: #tracklist
                self.core.tracklist.clear()
                track_uris = []
                for track in data['result']:
                  track_uris.append('mopidymopidy:track:'+track['track']['uri'])
                self.core.tracklist.add(uris=track_uris)
                self.get_current_track()
              elif data['id'] == 102: #currenttrack
                if data['result'] != None:
                  track_uri = 'mopidymopidy:track:'+data['result']['track']['uri']
                  self.set_current_track(track_uri)
                  self.get_playback_state()
              elif data['id'] == 103: #playbackstate
                if data['result'] != None:
                  self.core.playback.set_state(data['result'])

    def set_current_track(self, uri):
      tl_tracks = self.core.tracklist.filter({"uri": [uri]}).get()
      if len(tl_tracks) > 0:
        #We need to call private method to set current track to replaced one
        self.core._actor.playback._set_current_tl_track(tl_tracks[0])

    def get_master_tracklist(self):
      payload = {
         "method": "core.tracklist.get_tl_tracks",
         "jsonrpc": "2.0",
         "id": 101
      }
      self.mopidy_ws.write_message(json.dumps(payload))

    def get_current_track(self):
      payload = {
         "method": "core.playback.get_current_tl_track",
         "jsonrpc": "2.0",
         "params":{},
         "id": 102
      }
      self.mopidy_ws.write_message(json.dumps(payload))

    def get_playback_state(self):
      payload = {
         "method": "core.playback.get_state",
         "jsonrpc": "2.0",
         "params":{},
         "id": 103
      }
      self.mopidy_ws.write_message(json.dumps(payload))

    def change_active(self, active, track_position):
      if self._is_active != active:
        self._is_active = active
        if not active:
          #replicate tracks from master
          self.core.playback.stop()
          self.get_master_tracklist()
        else:
          logger.debug('starting playback')
          tl_track = self.core.playback.get_current_tl_track().get()
          logger.error(tl_track)
          logger.error(track_position)
          self.core.playback.seek(track_position)
          self.core.playback.play(tl_track)
          self.core.playback.set_state(PlaybackState.PLAYING)
          logger.debug("Playback switched")

    def set_active(self):
        payload = {
          "message":"activate",
          "name": self._name
        }
        self.ws.write_message(json.dumps(payload))

    def on_event(self, event, **kwargs):
         if event == 'track_playback_started':
           self.loop.call_soon_threadsafe(self.set_active)
         logger.debug(event)

    def register(self):
        payload = {
          "message":"register",
          "name": self._name,
          "url": f"http://{self._ip}:6680/{self._frontend}",
          "ws": f"ws://{self._ip}:6680/mopidy/ws",
        }
        self.ws.write_message(json.dumps(payload))
        self._registered = True
