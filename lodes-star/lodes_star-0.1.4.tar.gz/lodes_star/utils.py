import requests
import io
import os
import glob
import shutil
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse


###
def fetch_bytes(file_url, suffix="", cache=True):
    if isinstance(cache, str):
        file_path = os.path.join(cache, urlparse(file_url).path.lstrip('/'))
    else:
        file_path = os.path.join('./cache', urlparse(file_url).path.lstrip('/'))

    print(file_path)
    file_name = os.path.basename(file_url)

    if not os.path.exists(file_path.replace(file_name, '')):
        os.makedirs(file_path.replace(file_name, ''))

    # Check if already cached
    if not os.path.exists(file_path):
        s = requests.Session()
        response = requests_retry_session(session=s).get(file_url, stream=True, timeout=5)

        # file obj as real file or nulls
        obj = open(file_path, 'wb') if cache else open(os.devnull, 'wb')

        bytes_data = b''
        with tqdm.wrapattr(obj, "write",
                           desc=' '.join(['Fetching', file_name, suffix]),
                           total=int(response.headers.get("Content-Length", 0))
                           ) as out:

            # save the output to a file
            for buf in response.iter_content(io.DEFAULT_BUFFER_SIZE):
                out.write(buf)
                bytes_data += buf

        return bytes_data

    else:
        print(' '.join(['Loading cached', file_name, suffix]))
        return open(file_path, 'rb').read()


def get_cache_list(cache_dir=os.getcwd(), full_path=True):
    if full_path:
        return [f for f in glob.glob(os.path.join(cache_dir, '**/*.csv.gz'), recursive=True)]
    else:
        return [os.path.basename(f) for f in glob.glob(os.path.join(cache_dir, '**/*.csv.gz'), recursive=True)]


def get_file_list(base_url, state, zone_types, job_cat, year):
    file_list = {}

    for zone in zone_types:
        # Get list of relevant files
        url = '/'.join([base_url, state.lower(), zone.lower()])

        # HTTPS session
        s = requests.Session()
        response = requests_retry_session(session=s).get(url, stream=True, timeout=5)

        # Parse the hrefs from page
        hrefs = [x.get('href') for x in BeautifulSoup(response.text, 'html.parser').find_all('a')]

        for node in hrefs:
            if node.endswith('.csv.gz') and year in node and any([True for x in job_cat if x in node]):
                file_list[node] = os.path.join(url, node)

    return file_list


def get_latest_year(base_url, state):
    common_years = None
    for zone in ['od', 'rac', 'wac']:
        url = '/'.join([base_url, state.lower(), zone.lower()])

        s = requests.Session()
        response = requests_retry_session(session=s).get(url, timeout=5)

        hrefs = [x.get('href') for x in BeautifulSoup(response.text, 'html.parser').find_all('a')]
        years = [node.replace('.csv.gz', '')[-4:] for node in hrefs if node.endswith('.csv.gz')]

        if not common_years:
            common_years = set(years)
        else:
            common_years = common_years.intersection(years)

    return max(common_years)


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def iterable_to_stream(iterable, buffer_size=io.DEFAULT_BUFFER_SIZE):
    """
    Lets you use an iterable (e.g. a generator) that yields bytestrings as a read-only
    input stream.

    The stream implements Python 3's newer I/O API (available in Python 2's io module).
    For efficiency, the stream is buffered.
    """
    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None

        def readable(self):
            return True

        def readinto(self, b):
            try:
                l = len(b)  # We're supposed to return at most this much
                chunk = self.leftover or next(iterable)
                output, self.leftover = chunk[:l], chunk[l:]
                b[:len(output)] = output
                return len(output)
            except StopIteration:
                return 0    # indicate EOF
    return io.BufferedReader(IterStream(), buffer_size=buffer_size)


def stream_to_file(response, file_path, desc_lab=""):
    # check header to get content length, in bytes
    total_length = int(response.headers.get("Content-Length"))
    # implement progress bar via tqdm
    with tqdm.wrapattr(response.raw, "read", total=total_length, desc=desc_lab) as raw:
        # save the output to a file
        with open(file_path, 'wb') as output:
            shutil.copyfileobj(raw, output)
