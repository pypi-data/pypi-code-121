from mopidy import backend, audio
from .utils import Utils
import logging
import requests
logger = logging.getLogger("mopidy")


class MopidyPlaybackProvider(backend.PlaybackProvider):
    def __init__(self, backend, audio, url):
        super().__init__(audio, backend)
        self._url = url

    def translate_uri(self, uri: str):
        logger.debug('translate '+uri)
        uri = Utils.uri_to_master(uri)
        return self._url+"track/"+uri;
