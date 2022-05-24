from mopidy.models import Playlist, Track, Ref, fields, Artist, Album
import logging
logger = logging.getLogger("mopidy_mopidy")

class ARef(Ref):
  artwork = fields.String()
  @staticmethod
  def from_ref(ref):
    if 'artwork' in ref:
      artwork = ref['artwork']
    else:
      artwork = ''
    if 'type' in ref:
      type = ref['type']
    else:
      type = 'playlist'
    return ARef(uri="mopidymopidy:directory:"+ref['uri'],type=type,name=ref['name'],artwork=artwork)

class AAlbum(Album):
  artwork = fields.String()
  @staticmethod
  def from_album(album):
     if 'uri' in album:
       uri = album['uri']
     else:
       uri = album['name']
     if 'artwork' in album:
       artwork = album['artwork']
     else:
       artwork = ''
     artists = []
     if 'artists' in album:
       for artist in album['artists']:
          artists.append(AArtist.from_artist(artist))

     return AAlbum(uri="mopidymopidy:album:"+uri, name=album['name'], artists=artists,artwork=artwork)

class AArtist(Artist):
  artwork = fields.String()
  @staticmethod
  def from_artist(artist):
    if 'uri' in artist:
      artisturi = artist['uri']
    else:
      artisturi = artist['name']

    if 'artwork' in artist:
      artwork = artist['artwork']
    else:
      artwork = ''
    return AArtist(uri="mopidymopidy:artist:"+artisturi, name=artist['name'], artwork=artwork)

class ATrack(Track):
  artwork = fields.String()
  like = fields.Boolean()

  @staticmethod
  def from_track(track):
      artists = []
      for artist in track['artists']:
        artists.append(AArtist.from_artist(artist))
      if 'album' in track:
        album = AAlbum.from_album(track['album'])
      else:
        album = None
      if 'like' in track:
        like = track['like']
      else:
        like = False
      if 'length' in track:
        length = track['length']
      else:
        length = 0
      if 'artwork' in track:
        artwork = track['artwork']
      else:
        artwork = ''
      return ATrack(uri="mopidymopidy:track:"+track['uri'],name=track['name'],
            length=length, artwork=artwork, artists=artists, album=album, like=like)

class APlaylist(Playlist):
  artwork = fields.String()
