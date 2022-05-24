from mopidy import backend, models, config
from .classes import ATrack, AArtist, AAlbum, ARef, APlaylist
from .utils import Utils
import logging
import requests
logger = logging.getLogger("mopidy_mopidy")

class MopidyLibraryProvider(backend.LibraryProvider):
    def __init__(self, url):
        self._url = url
        uri = "mopidymopidy:directory:root"
        name = "Mopidy Master"
        artwork = "user-images.githubusercontent.com/38141262/39072403-9afaaf90-4514-11e8-9518-14e978e54e3f.png"
        self.root_directory = ARef(type=ARef.PLAYLIST, uri=uri, name=name, artwork=artwork)



    def browse(self, uri):
        uri = Utils.uri_to_master(uri)
        if uri == "root":
          uri = None
        payload = {
          "method": "core.library.browse",
          "jsonrpc": "2.0",
          "params": {"uri":uri},
          "id": 0,
        }
        response = requests.post(self._url, json=payload).json()
        refs = []
        for res in response['result']:
          refs.append(ARef.from_ref(res))
        return refs

    def search(self, query, uris = None, exact = False):
        payload = {
          "method": "core.library.search",
          "jsonrpc": "2.0",
          "params": {"query":query,"uris":uris},
          "id": 0,
        }
        response = requests.post(self._url, json=payload).json()
        res_tracks = []
        res_albums = []
        res_artists = []
        for res in response['result']:
          if 'tracks' in res:
            for track in res['tracks']:
              res_tracks.append(ATrack.from_track(track))
          if 'albums' in res:
            for album in res['albums']:
              res_albums.append(AAlbum.from_album(album))
          if 'artists' in res:
            for artist in res['artists']:
              res_artists.append(AArtist.from_artist(artist))
        sresult = models.SearchResult(uri='', tracks=res_tracks, artists=res_artists, albums=res_albums)
        return sresult


    def lookup(self, uri: str):
        uri = Utils.uri_to_master(uri)
        payload = {
          "method": "core.library.lookup",
          "jsonrpc": "2.0",
          "params": {"uris":[uri]},
          "id": 0,
        }
        response = requests.post(self._url, json=payload).json()
        tracks = []
        for res in response['result']:
          for track in response['result'][res]:
            if 'uri' not in track:
              track['uri'] = res
            tracks.append( ATrack.from_track(track))

        return tracks

    def get_images(self, uris):
        master_uris = []
        for uri in uris:
          master_uris.append(Utils.uri_to_master(uri))

        payload = {
          "method": "core.library.get_images",
          "jsonrpc": "2.0",
          "params": {"uris":master_uris},
          "id": 0,
        }
        result = dict()
        response = requests.post(self._url, json=payload).json()
        for res_uri in response['result']:
          for image in response['result'][res_uri]:
            for uri in uris:
              if res_uri in uri:
                result[uri] = [models.Image(uri=image['uri'])]
                break
        return result
