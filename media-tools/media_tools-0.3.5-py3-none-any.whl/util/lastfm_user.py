__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

from argparse import Namespace
from datetime import date, datetime
from typing import Optional, Sequence

from pylast import LastFMNetwork, User


class LastFMUser:

    @staticmethod
    def from_options(options: Namespace) -> 'LastFMUser':
        network = LastFMNetwork(
            api_key=options.lastfm_api_key, api_secret=options.lastfm_api_secret
        )
        return LastFMUser(network.get_user(options.lastfm_user))

    def __init__(self, user: User) -> None:
        self.user = user

    def start_year(self) -> int:
        return date.fromtimestamp(self.user.get_unixtime_registered()).year

    def get_year_list(self, year: Optional[int]) -> Sequence[int]:
        return [year] if year or year is None else range(self.start_year(), datetime.now().year)
