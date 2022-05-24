from mopidy import backend, audio
import pykka
from .playlist_provider import MopidyPlaylistProvider
from .playback_provider import MopidyPlaybackProvider
from .library_provider import MopidyLibraryProvider
import socket
import logging
import requests
logger = logging.getLogger("mopidy_mopidy")

class MopidyMusicBackend(pykka.ThreadingActor, backend.Backend):


    def __init__(self, config: dict, audio: audio):
        super(MopidyMusicBackend, self).__init__()

        ym_config :dict = config["mopidy_mopidy"]

        host = ym_config["master"]
        url = "http://{}:6680/mopidy/rpc".format(host)
        master_url = "http://{}:6680/master/".format(host)
        self._config = config
        self._audio = audio
        self.playlists = MopidyPlaylistProvider(self, url)
        self.playback = MopidyPlaybackProvider(self, audio, master_url)
        self.library = MopidyLibraryProvider(url)
        self.uri_schemes = ["mopidymopidy"]

