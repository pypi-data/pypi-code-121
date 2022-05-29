"""Utils for reading remote files."""
import json
import logging
import ssl
import time

import requests
from bs4 import BeautifulSoup

from utils import filex, timex, tsv
from utils.browserx import Browser
from utils.cache import cache

USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) '
    + 'Gecko/20100101 Firefox/65.0'
)
ENCODING = 'utf-8'
SELENIUM_SCROLL_REPEATS = 3
SELENIUM_SCROLL_WAIT_TIME = 0.5

# pylint: disable=W0212
ssl._create_default_https_context = ssl._create_unverified_context


def _read_helper(url, cached=True):
    if cached:
        return _read_helper_cached(url)
    return _read_helper_nocached(url)


@cache('utils.www', timex.SECONDS_IN.HOUR)
def _read_helper_cached(url):
    return _read_helper_nocached(url)


def _read_helper_nocached(url):
    try:
        resp = requests.get(url, headers={'user-agent': USER_AGENT})
        if resp.status_code != 200:
            return None
        return resp.content
    except requests.exceptions.ConnectionError:
        return None


def _read_helper_selenium(url, cached=True):
    if cached:
        return _read_helper_selenium_cached(url)
    return _read_helper_selenium_noncached(url)


@cache('utils.www', timex.SECONDS_IN.HOUR)
def _read_helper_selenium_cached(url):
    return _read_helper_selenium_noncached(url)


def _read_helper_selenium_noncached(url):
    browser = Browser(url)
    for _ in range(0, SELENIUM_SCROLL_REPEATS):
        browser.scroll_to_bottom()
        time.sleep(SELENIUM_SCROLL_WAIT_TIME)
    content = browser.get_source()
    browser.quit()
    return content


def read(url, cached=True, use_selenium=False):
    """Read url."""
    if use_selenium:
        return _read_helper_selenium(url, cached)
    content = _read_helper(url, cached)
    return content.decode(ENCODING) if content else None


def read_json(url, cached=True):
    """Read JSON content from url."""
    content = read(url, cached)
    return json.loads(content) if content else None


def read_tsv(url, cached=True):
    """Read TSV content from url."""
    csv_lines = read(url, cached).split('\n')
    return tsv._read_helper(csv_lines)


def download_binary(url, file_name, cached=True):
    """Download binary."""
    content = _read_helper(url, cached)
    filex.write(file_name, content, 'wb')
    logging.debug('Wrote %dB from %s to %s', len(content), url, file_name)


def exists(url, timeout=1):
    """Check if URL exists."""
    try:
        response = requests.head(url, timeout=timeout)
        # pylint: disable=E1101
        return response.status_code == requests.codes.ok
    except requests.exceptions.ConnectTimeout:
        return False


def get_all_urls(root_url, cached=True):
    """Get all URLs linked to a webpage."""
    soup = BeautifulSoup(read(root_url, cached), 'html.parser')
    urls = list(
        map(
            lambda a_link: a_link['href'],
            soup.find_all('a', href=True),
        )
    )
    logging.debug('Found %d links on %s', len(urls), root_url)
    return urls
