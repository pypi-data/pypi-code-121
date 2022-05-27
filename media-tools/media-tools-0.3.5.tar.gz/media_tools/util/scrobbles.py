__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import logging
from calendar import timegm
from datetime import datetime
from time import sleep
from typing import Any, Callable, Dict, List, Optional, Union

from pylast import PyLastError

from media_tools.util.dump_data import dump_data
from media_tools.util.lastfm_user import LastFMUser


class Scrobbles:

    def __init__(
            self, user: LastFMUser, year: Optional[int], limit: Optional[int], max_retry_wait: int
    ):
        self.user = user.user
        self.year = year
        self.limit = limit
        self.max_retry_wait = max_retry_wait

    def get_and_dump(self, filename: Optional[str] = None):
        scrobble_data = self.get_data()
        backup_filename = get_output_filename(self.year, filename)
        dump_data(scrobble_data, backup_filename)

    def get_data(
            self, wait_time: int = 0, tracks: Optional[List[str]] = None,
            loved: Optional[List[str]] = None, top_tracks: Optional[List[str]] = None
    ) -> Dict:
        logging.info(
            "get_data(user=%s, year=%s, limit=%s, wait=%s)",
            self.user.name, self.year, self.limit, wait_time
        )
        year_dates = year_range(self.year)
        try:
            play_count = self.user.get_playcount()
            tracks = self.get_and_wait(tracks, self.user.get_recent_tracks, wait_time, **year_dates)
            loved = self.get_and_wait(loved, self.user.get_loved_tracks, wait_time)
            top_tracks = self.get_and_wait(top_tracks, self.user.get_top_tracks, wait_time)
            top_artists = self.get_and_wait(None, self.user.get_top_artists, wait_time)
            top_albums = self.get_and_wait(None, self.user.get_top_albums, wait_time)
            top_tags = self.user.get_top_tags(limit=self.limit)
            return dict(
                time=datetime.now(),
                play_count=play_count,
                tracks=tracks,
                loved=loved,
                top_tracks=top_tracks,
                top_artists=top_artists,
                top_albums=top_albums,
                top_tags=top_tags,
            )
        # pylast has a feature to deal with rate limiting, but it doesn't seem to work reliably
        except PyLastError as error:
            logging.info("%s: %s", type(error).__name__, str(error))
            next_wait_time = 1 if wait_time == 0 else 2 * wait_time
            if next_wait_time <= self.max_retry_wait:
                logging.warning(
                    "%s, retrying with %ss wait time", type(error).__name__, next_wait_time
                )
                return self.get_data(
                    next_wait_time, tracks=tracks, loved=loved, top_tracks=top_tracks
                )
            logging.error('Rate limiting still active after %ss - giving up', self.max_retry_wait)
            raise

    def get_and_wait(
            self, values: Optional[List], function: Callable, wait_time: int, **kwargs
    ) -> Union[List[Any], Any]:
        if values is None:
            values = function(limit=self.limit, **kwargs)
            logging.info('waiting %ss', str(wait_time))
            sleep(wait_time)
        return values


def get_output_filename(year: Optional[int], filename: Optional[str]) -> str:
    if filename is None:
        year_string = "all" if year is None else str(year)
        filename = f'backup_lastfm_{year_string}.pickle.bz2'
    return filename


def from_datetime(convert_datetime: datetime) -> int:
    return timegm(convert_datetime.utctimetuple())


def year_range(year: Optional[int]) -> Dict[str, int]:
    start = None if year is None else from_datetime(datetime(year, 1, 1, 0, 0, 0))
    end = None if year is None else from_datetime(datetime(year, 12, 31, 23, 59, 59, 999999))
    return dict(time_from=start, time_to=end)
