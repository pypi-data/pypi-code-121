__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import logging
from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path
from sys import argv
from typing import List

from media_tools.util.buying.track import Track, TrackDB
from media_tools.util.buying.distributor import Beatport, Amazon
from media_tools.util.buying.last_fm import LastFM

DEFAULT_TRACK_DB = 'bought.pickle'


def read_datetime(args: str) -> datetime:
    try:
        return datetime.strptime(args, '%Y-%m-%d')
    except ValueError:
        logging.warning('Accepted date format: YYYY-MM-DD')
        raise


def parse_commandline(args: List[str]) -> Namespace:
    parser = ArgumentParser(
        description="..."
    )
    parser.add_argument(
        '-u', '--user', required=True, help='Last.FM username'
    )
    parser.add_argument(
        '-k', '--api-key', required=True, help='Last.FM API key'
    )
    parser.add_argument(
        '-l', '--limit', type=int, default=10, help='Maximum number of tracks to display'
    )
    parser.add_argument(
        '-m', '--min-plays', type=int, default=1, help='Minimum number of plays per track'
    )
    parser.add_argument(
        '--buy-up-to', type=int, default=None,
        help='When specified, repeat until this may tracks have been bought'
    )
    period_group = parser.add_mutually_exclusive_group()
    period_group.add_argument(
        '-p', '--period', choices=('overall', '7day', '1month', '3month', '6month', '12month'),
        default='overall', help='Period from which to choose favorite tracks'
    )
    period_group.add_argument(
        '-f', '--from-date', type=read_datetime,
        help='...'
    )
    parser.add_argument(
        '-t', '--to-date', type=read_datetime, default=datetime.now(),
        help='...'
    )
    parser.add_argument(
        '-d', '--track-db', type=str, default=DEFAULT_TRACK_DB,
        help='Name of the file storing already bought tracks'
    )

    return parser.parse_args(args)


def main() -> None:
    opts = parse_commandline(argv[1:])
    api = LastFM(opts.user, opts.api_key)

    with TrackDB(Path(opts.track_db)) as trackdb:
        Track.setup((Beatport(), Amazon()), trackdb)
        bought = buy_exactly(api, opts)
    logging.info('%s bought', bought)


def buy_exactly(api: LastFM, opts: Namespace) -> int:
    bought = 0
    while bought < (opts.buy_up_to or 1):
        bought = buy_more(api, opts, bought)
    return bought


def buy_more(api: LastFM, opts: Namespace, already_bought: int) -> int:
    for track in get_tracks_chunk(api, opts):
        logging.debug("%s: %s", track, track.buy_url())
        track.buy()
        already_bought += int(bool(track.buy_url()))
        if opts.buy_up_to and already_bought >= opts.buy_up_to:
            return already_bought
    return already_bought


def get_tracks_chunk(api: LastFM, opts: Namespace, page: int = 1) -> List[Track]:
    paging = LastFM.Paging(limit=opts.limit, page=page, min_plays=opts.min_plays)
    return api.get_tracks_by_period(
        from_date=opts.from_date, to_date=opts.to_date, paging=paging
    ) if opts.from_date else api.get_top_tracks(period=opts.period, paging=paging)


if __name__ == '__main__':
    main()
