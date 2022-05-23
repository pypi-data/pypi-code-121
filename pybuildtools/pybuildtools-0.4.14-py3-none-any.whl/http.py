'''
HTTP stuff.

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import logging
from pathlib import Path
from typing import Union

import requests
from tqdm import tqdm

from buildtools.bt_logging import IndentLogger

HTTP_METHOD_GET = 'GET'
HTTP_METHOD_POST = 'POST'

log = IndentLogger(logging.getLogger(__name__))


def DownloadFile(url: str, filename: Union[str, Path], log_after: bool = True, print_status: bool = True, log_before: bool = True, **kwargs) -> bool:
    '''
    Download a file from url to filename.

    :param url:
        HTTP URL to download. (SSL/TLS will also work, assuming the cert isn't broken.)
    :param filename:
        Path of the file to download to.
    :param log_after:
        Produce a log statement after the download completes (includes URL).
    :param log_before:
        Produce a log statement before the download starts.
    :param print_status:
        Prints live-updated status of the download progress. (May not work very well for piped or redirected output.)
    :param session:
        Requests session.
    '''
    output = Path(filename)
    #kwargs['headers'] = dict(DEFAULT_HEADERS, **kwargs.get('headers', {}))
    r = None
    session = kwargs.pop('session', requests)
    try:
        r = session.get(url, stream=True, **kwargs)
    except requests.exceptions.ConnectionError as e:
        logging.warning(e)
        return False
    except UnicodeEncodeError as e:
        logging.warning(e)
        return False

    if (r.status_code == 404):
        logging.warn('404 - Not Found: %s', url)
        return False
    elif(r.status_code != 200):
        logging.warn("Error code: {0}".format(r.status_code))
        return False
    with open(output, 'wb') as f:
        fsz_str: str = 'UNKNOWN'
        try:
            file_size = int(r.headers.get('Content-Length', '-1'))
            if file_size < 0:
                log.warn(f'Content-Length header was not received, expect progress bar weirdness.')
            fsz_str = str(file_size)
        except ValueError:
            file_size_value = r.headers['Content-Length']
            log.warn(f'Content-Length header has invalid value: {file_size_value!r}')
        if log_before:
            log.info(f'Downloading: {output}, Bytes: {fsz_str}B')

        file_size_dl = 0
        block_sz = 8192

        progress = tqdm(total=file_size, unit_scale=True, unit_divisor=1024, unit='B', leave=False) if print_status else None
        for buf in r.iter_content(block_sz):
            if not buf or file_size == file_size_dl:
                break

            buf_len = len(buf)
            file_size_dl += buf_len
            f.write(buf)
            if print_status:
                #status = r"%10d/%10d  [%3.2f%%]" % (file_size_dl, file_size, file_size_dl * 100. / file_size)
                progress.update(buf_len)
                #status = status + chr(8) * (len(status) + 1)  - pre-2.6 method
                #print(status, end='\r')
        if progress is not None:
            progress.close()
    if log_after:
        log.info(f'Downloaded {url} to {output} ({file_size_dl}B)')
