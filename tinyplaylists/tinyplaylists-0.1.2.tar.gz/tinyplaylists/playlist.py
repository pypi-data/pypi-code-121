import os
from pathlib import Path
from typing import Dict

from tinyplaylists.track import Track


class Playlist:
    name: str
    dir: Path
    tracks: Dict[str, Track]

    def __init__(self, dir: Path):
        self.dir = dir
        self.name = dir.name
        self.load_tracks()

    def load_tracks(self):
        self.tracks = {}
        for file in self.dir.iterdir():
            if file.is_file():
                t = Track.from_file(file)
                self.tracks[t.id] = t

    def import_track(self, file: Path, metadata: dict) -> Track:
        """
        Copy the file to the playlist directory and add a Track to the playlist.
        """
        target = self.dir / file.name
        os.link(file, target)
        t = Track.from_file(target)
        self.tracks[t.id] = t
        t.update_metadata(metadata)
        return t

    def remove_track(self, id: str):
        """
        Remove the track with the given id from the playlist.
        """
        t = self.tracks.pop(id)
        t.path.unlink()
