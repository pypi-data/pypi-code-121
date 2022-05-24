import errno
import os
import pathlib
import re
from timeit import default_timer
from urllib.parse import uses_relative, uses_netloc, uses_params

import requests
from six.moves.urllib_parse import urlparse
from urllib3.util import parse_url

from rebotics_sdk.advanced import remote_loaders

_VALID_URLS = set(uses_relative + uses_netloc + uses_params)
_VALID_URLS.discard("")


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def is_url(url) -> bool:
    """
    Check to see if a URL has a valid protocol.

    Parameters
    ----------
    url : str or unicode

    Returns
    -------
    isurl : bool
        If `url` has a valid protocol return True otherwise False.
    """
    if not isinstance(url, str):
        return False
    return parse_url(url).scheme in _VALID_URLS


def get_filename_from_url(url):
    return urlparse(url).path.split('/')[-1]


def download_file(url, filepath=None, **params):
    response = requests.get(
        url,
        stream=True,
        params=params,
        timeout=remote_loaders.HTTP_TIMEOUTS,
    )
    response.raise_for_status()

    if filepath is None:
        # TODO: decode url, get filename
        filepath = get_filename_from_url(url)

    with open(filepath, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)
    return filepath


class Timer(object):
    def __init__(self):
        self.timer = default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        end = self.timer()
        self.elapsed_secs = end - self.start
        self.elapsed = self.elapsed_secs * 1000  # millisecs


def parse_id_range_string(id_string):
    id_list = []
    range_pattern = re.compile(r'^(?P<from>\d+)-(?P<to>\d+)$')
    single_pattern = re.compile(r'^\d+$')

    left_out_parts = []

    for part in id_string.split(','):
        part = part.strip()
        range_match = range_pattern.match(part)

        if range_match:
            range_from = int(range_match.group('from'))
            range_to = int(range_match.group('to'))
            if range_from > range_to:
                left_out_parts.append(part)
                continue
            id_list.extend(range(range_from, range_to + 1))
        elif single_pattern.match(part):
            id_list.append(int(part))
        else:
            left_out_parts.append(part)

    if left_out_parts:
        raise ValueError('Please review the string as input: {}.\n Wrong parts are: {}'.format(
            id_string, left_out_parts
        ))
    if not id_list:
        raise ValueError('You need to supply a string with at least one ID. Given {}'.format(id_string))
    return sorted(list(set(id_list)))


def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except Exception:
        return False


def download_and_return_id(row, output: pathlib.Path):
    url = row['url']
    label = row['label']
    uuid = row['uuid']

    label_folder = output / label
    label_folder.mkdir(exist_ok=True, parents=True)

    filename = pathlib.Path(urlparse(url).path).name
    destination = label_folder / filename

    retries = 4
    while retries != 0:
        try:
            remote_loaders.download(url, destination)
            return uuid, destination
        except Exception:
            retries -= 1

    return uuid, None
