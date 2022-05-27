"""
main.py
========
This is the main file for tinyplaylists.
"""

from pathlib import Path
from typing import Dict
import os

from tinyplaylists.playlist import Playlist
from tinyplaylists.track import Track


class TinyPlaylists:
    """
    The entry point for the library.
    """

    root: Path
    playlists: Dict[str, Playlist]

    def __init__(self, root: Path):
        self.root = root
        self.load_playlists()

    def load_playlists(self):
        self.playlists = {}
        for dir in self.root.iterdir():
            if dir.is_dir():
                self.playlists[dir.name] = Playlist(dir)

    def get_playlist(self, name: str) -> Playlist:
        return self.playlists[name]

    def import_track(self, file: Path, playlist_name: str, metadata: dict) -> Track:
        pl = self.get_playlist(playlist_name)
        return pl.import_track(file, metadata)

    def create_playlist(self, name: str) -> Playlist:
        dir = self.root / name
        os.mkdir(dir)
        pl = Playlist(dir)
        self.playlists[name] = pl
        return pl

    def find_playlist_with_track(self, track_id: str) -> Playlist:
        """
        Find the playlist that contains the track with the given id.
        Raises ValueError if no playlist contains the track.
        """
        for pl in self.playlists.values():
            if track_id in pl.tracks:
                return pl
        raise ValueError(f"No playlist contains track with id {track_id}")

    def get_track(self, id: str) -> Track:
        """
        Find the track with the given id.
        Returns None if no playlist contains the track.
        """
        pl = self.find_playlist_with_track(id)
        return pl.tracks[id]

    def remove_track(self, id: str):
        """
        Remove the track with the given id from the playlist.
        """

        pl = self.find_playlist_with_track(id)
        pl.remove_track(id)

    def playlist_tracks(self, playlist_name: str) -> Dict[str, Track]:
        """
        Return a dictionary of the tracks in the given playlist. The keys are the track ids.
        """
        pl = self.get_playlist(playlist_name)
        return pl.tracks
