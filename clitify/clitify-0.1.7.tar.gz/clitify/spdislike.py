#!/usr/bin/env python
import os
import spotipy
from rich import print

import termcolor

client_id = os.environ["SPOTIPY_CLIENT_ID"]
client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
cache_path = os.path.join(os.environ["XDG_RUNTIME_DIR"], ".spcache")

redirect_uri = "http://localhost:8888/callback/"
scope = "user-read-currently-playing user-library-modify"


auth_manager = spotipy.oauth2.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_path=cache_path,
)

sp = spotipy.Spotify(auth_manager=auth_manager)
track = sp.current_user_playing_track()
token = auth_manager.get_cached_token()
access_token = token["access_token"]

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}
BASE_URL = "https://api.spotify.com/v1/"


track = sp.currently_playing()["item"]

track_id = track["id"]
image = track["album"]["images"][0]["url"]
name = track["name"]
artists_names = ", ".join(map(lambda a: a["name"], track["artists"]))

sp.current_user_saved_tracks_delete(tracks=[track_id])

os.system(f"curl -so /tmp/spimage {image}")
message = f"♡ {artists_names} - {name}"
cmd = f'notify-send -i /tmp/spimage "{message}"'
print(message)
os.system(cmd)
