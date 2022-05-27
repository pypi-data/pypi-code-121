# pylint: disable=unsupported-membership-test,not-an-iterable
__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import webbrowser
from typing import Dict, Optional, Tuple
from urllib.parse import quote_plus

from media_tools.util.buying.trackdb import TrackDB


class Track:

    distributors: Tuple = None
    track_db: TrackDB = None

    @classmethod
    def setup(cls, distributors: Tuple, track_db: Optional[TrackDB]) -> None:
        cls.distributors = distributors
        cls.track_db = track_db

    @classmethod
    def from_dict(cls, data: Dict) -> 'Track':
        try:
            return Track(
                data['artist'].get('name', data['artist'].get('#text')),
                data['name'], int(data.get('playcount', 1))
            )
        except KeyError:
            print("Couldn't create Track from", data)
            raise

    def __init__(self, artist: str, title: str, play_count: int = 1) -> None:
        if self.distributors is None:
            raise ValueError('Call Track.setup() before trying to create a Track!')
        self._artist: str = artist
        self._title: str = title
        self.play_count: int = play_count
        self._buy_url: Optional[str] = None

    def __repr__(self) -> str:
        return f'{self._artist} / {self._title} ({self.play_count} plays)'

    def __eq__(self, other: object) -> bool:
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash(self._artist + self._title)

    @property
    def title(self) -> str:
        return quote_plus(self._title)

    @property
    def artist(self) -> str:
        return quote_plus(self._artist)

    def buy_url(self) -> str:
        if self._buy_url is not None:
            return self._buy_url

        self._buy_url = ''
        for distributor in self.distributors:
            if distributor.is_present(self):
                self._buy_url = distributor.search_url(self)
                break
        return self._buy_url

    def buy(self) -> None:
        if self.buy_url() and Track.track_db is not None and self not in Track.track_db:
            webbrowser.open(self.buy_url())
            Track.track_db.add(self)
