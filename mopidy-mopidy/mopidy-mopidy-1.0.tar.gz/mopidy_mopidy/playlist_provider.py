from mopidy import backend
from .classes import ARef, APlaylist, ATrack, AArtist, AAlbum
from .utils import Utils
from typing import List
import logging
import time
import json
import random
import requests
logger = logging.getLogger("mopidy_mopidy")


class MopidyPlaylistProvider(backend.PlaylistsProvider):

    def __init__(self, backend, url):
        super().__init__(backend)
        self._url = url;
        logger.debug("mopidy backend started")

    def as_list(self) -> List[ARef]:

        payload = {
          "method": "core.playlists.as_list",
          "jsonrpc": "2.0",
          "id": 0,
        }
        response = requests.post(self._url, json=payload).json()
        playlists = []
        for res in response['result']:
          if 'artwork' in res:
            artwork = res['artwork']
          else:
            artwork = ''
          playlists.append(ARef(type=ARef.PLAYLIST,uri="mopidymopidy:playlist:"+res['uri'],name=res['name'],artwork=artwork))
        return playlists


    def lookup(self, uri: str) -> APlaylist:
        uri = Utils.uri_to_master(uri)
        payload = {
          "method": "core.playlists.lookup",
          "jsonrpc": "2.0",
          "params": { "uri":uri },
          "id": 0,
        }
        response = requests.post(self._url, json=payload).json()
        tracks = []
        for track in response['result']['tracks']:
           tracks.append(ATrack.from_track(track))
        return APlaylist(uri=uri, name=response['result']['name'], tracks=tracks)

    def create(self, name):
        logger.error("create playlist")
        logger.error(name)
        return None

    def delete(self, uri):
        logger.error("delete playlist")
        logger.error(name)
        return None

    def refresh(self):
        logger.debug("refresh")
        pass

    def save(self, playlist):
        logger.error("save playlist")
        logger.error(playlist)
        return None

