#!/usr/bin/env python
"""List the songs in the spotify queue."""

import os
import spotipy
import termcolor

# from rich import print

client_id = os.environ["SPOTIPY_CLIENT_ID"]
client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]


REDIRECT_URI = "http://localhost:8888/callback/"
SCOPE = "user-read-currently-playing"


auth_manager = spotipy.oauth2.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
)

print(f"token: {auth_manager.get_cached_token()}")

sp = spotipy.Spotify(auth_manager=auth_manager)
track: dict = sp.current_user_playing_track()


def get_playlist_ids(username: str, playlist_id: str):
    """Get tracks ids using the playlist id and username"""
    info: dict = sp.user_playlist_tracks(username, playlist_id)
    items = info["items"]
    while info["next"]:
        info = sp.next(info)
        items.extend(info["items"])
    return [item["track"]["id"] for item in items]


def tracks(user_id, playlist_id):
    """List all tracks"""
    track_ids = get_playlist_ids(user_id, playlist_id)
    for track_id in track_ids:
        track_item: dict = sp.track(track_id)
        track_fullname = track_item["name"] + "-" + track_item["artists"][0]["name"]
        if track_id == track["item"]["id"]:
            termcolor.cprint(track_fullname, attrs=["bold"])
        else:
            print(track_fullname)


my_id: str = sp.me()["id"]
my_playlist: str = track["context"]["uri"]
tracks(my_id, my_playlist)
