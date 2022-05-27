__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

import os
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from media_tools.util.scrobbles import LastFMUser, Scrobbles
from media_tools.util.logging import setup_logging

MAX_RETRY_WAIT = 1024


def parse(args: List[str]) -> Namespace:

    def env_or_required(key):
        return {'default': os.environ[key]} if key in os.environ else {'required': True}

    parser = ArgumentParser(
        description="Creates a pickle or JSON file from a last.fm user's scrobbles"
    )
    parser.add_argument(
        '-l', '--limit', type=int, default=None,
        help='Max. number of entries to request'
    )
    parser.add_argument(
        '-y', '--year', type=int, default=None,
        help='Year the data is requested for (empty for entire period)'
    )
    parser.add_argument(
        '-o', '--output', type=str, default=None,
        help='output file name'
    )
    parser.add_argument(
        '--lastfm-user', type=str,
        help='Last.FM user', **env_or_required('PYLAST_USERNAME')
    )
    parser.add_argument(
        '--lastfm-api-key', type=str,
        help='Last.FM API key', **env_or_required('PYLAST_API_KEY')
    )
    parser.add_argument(
        '--lastfm-api-secret', type=str,
        help='Last.FM API secret', **env_or_required('PYLAST_API_SECRET')
    )
    parser.add_argument(
        '-m', '--max-retry-wait', type=int, default=MAX_RETRY_WAIT,
        help='Max. seconds to wait between requests to avoid rate limiting'
    )
    return parser.parse_args(args)


def main(args: List[str]) -> None:
    options = parse(args)
    setup_logging(options)

    user = LastFMUser.from_options(options)

    for year in user.get_year_list(options.year):
        scrobble_data = Scrobbles(user, year, options.limit, options.max_retry_wait)
        scrobble_data.get_and_dump(options.output)


def entry() -> None:
    main(sys.argv[1:])


if __name__ == '__main__':
    entry()
