#!/usr/bin/env python
import os
import spotipy
from rich import print

import requests
import termcolor

client_id = os.environ["SPOTIPY_CLIENT_ID"]
client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]


redirect_uri = "http://localhost:8888/callback/"
# scope = "user-library-read"
# scope = "user-read-currently-playing"
# scope = "user-modify-playback-state"
scope = "user-read-currently-playing user-modify-playback-state"


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
# print(sp.me())


def get_playlist_ids(username, playlist_id):
    r = sp.user_playlist_tracks(username, playlist_id)
    t = r["items"]
    ids = []
    while r["next"]:
        r = sp.next(r)
        t.extend(r["items"])
    for s in t:
        ids.append(s["track"]["id"])
    return ids


def tracks():
    track_ids = get_playlist_ids(sp.me()["id"], track["context"]["uri"])
    for track_id in track_ids:
        track = sp.track(track_id)
        print(track["name"], "-", track["artists"][0]["name"])


headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}
BASE_URL = "https://api.spotify.com/v1/"


def post(path: str, json: dict = {}) -> requests.Response:
    url = os.path.join(BASE_URL, path)
    return requests.post(url=url, headers=headers, json=json)


def put(path: str, json: dict = {}) -> requests.Response:
    url = os.path.join(BASE_URL, path)
    return requests.put(url=url, headers=headers, json=json)


def next_track():
    response = post("me/player/next")
    print(response.text)


def playpause_song():
    response = put("me/player/pause")
    print(response.reason)
    print(response.text)


def play_song():
    response = put("me/player/play")
    print(response.reason)
    print(response.text)


# current_user_saved_tracks_add(tracks=None)

# playpause_song()
play_song()

# playlists = sp.user_playlists("spotify")
# while playlists:
#     for i, playlist in enumerate(playlists["items"]):
#         print(
#             "%4d %s %s"
#             % (i + 1 + playlists["offset"], playlist["uri"], playlist["name"])
#         )
#     if playlists["next"]:
#         playlists = sp.next(playlists)
#     else:
#         playlists = None

# results = sp.current_user_saved_tracks()
# for idx, item in enumerate(results["items"]):
#     track = item["track"]
#     print(idx, track["artists"][0]["name"], " – ", track["name"])
