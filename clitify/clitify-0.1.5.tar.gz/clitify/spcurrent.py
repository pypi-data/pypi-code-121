#!/usr/bin/env python
import os
import spotipy
from rich import print

import requests
import termcolor

client_id = os.environ["SPOTIPY_CLIENT_ID"]
client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]


redirect_uri = "http://localhost:8888/callback/"
scope = "user-read-currently-playing"


auth_manager = spotipy.oauth2.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
)

sp = spotipy.Spotify(auth_manager=auth_manager)

track = sp.current_user_playing_track()

token = auth_manager.get_cached_token()
access_token = token["access_token"]
# print(track)
# print(track["context"]["uri"])


# print(sp.track(track_id=track["id"]))
print(sp.me())
