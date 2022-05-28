# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2020 Mark Crewson <mark@crewson.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import aiohttp
import asyncio
import os
import urllib.parse

from typing import Any, Generator

from .framew.application import ApplicationError, OperationError
from .framew.log import getlog


##############################################################################

class DownloadError(OperationError):
    """Raised when a downloader fails to download a file"""
    def __init__(self, status):
        self.status = status


##############################################################################

class RetryableHttpClient(object):

    start_timeout = 0.1
    max_timeout = 30.0
    factor = 2.0

    def __init__(self, attempts=3, statuses=[413, 429, 500, 502, 504], exceptions=[], *args, **kwargs):
        self.attempts = attempts
        self.statuses = statuses
        self.exceptions = exceptions
        self.client = aiohttp.ClientSession(*args, **kwargs)
        self.closed = False

    def __del__(self):
        if not self.closed:
            print("!! RetryableHttpClient was not closed !!")

    def get(self, url, **kwargs):
        return self._request(self.client.get, url, **kwargs)

    def head(self, url, **kwargs):
        return self._request(self.client.head, url, **kwargs)

    def _request(self, request, url, **kwargs):
        return RetryableRequestContext(request,
                                       url,
                                       self.attempts,
                                       self.statuses,
                                       self.exceptions,
                                       self.retry_timeout,
                                       **kwargs)

    def retry_timeout(self, attempt):
        timeout = self.start_timeout * (self.factor ** attempt)
        return min(timeout, self.max_timeout)

    async def close(self):
        await self.client.close()
        self.closed = True

    async def __aenter__(self) -> 'RetryableHttpClient':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


class RetryableRequestContext(object):

    def __init__(self, request, url, attempts, retry_statuses, retry_exceptions, retry_timeout, **kwargs):
        self.request = request
        self.url = url
        self.attempts = attempts
        self.retry_statuses = retry_statuses
        self.retry_exceptions = retry_exceptions
        self.retry_timeout = retry_timeout
        self.kwargs = kwargs

        self.current_attempt = 0
        self.response = None

    async def do_request(self):
        try:
            self.current_attempt += 1
            response = await self.request(self.url, **self.kwargs)
            code = response.status
            if self.current_attempt < self.attempts and code in self.retry_statuses:
                retry_wait = self.retry_timeout(self.current_attempt)
                await asyncio.sleep(retry_wait)
                return await self.do_request()
            self.response = response
            return response
        except Exception as e:
            retry_wait = self.retry_timeout(self.current_attempt)
            if self.current_attempt < self.attempts:
                for exc in self.retry_exceptions:
                    if isinstance(e, exc):
                        await asyncio.sleep(retry_wait)
                        return await self.do_request()
            raise e

    def __await__(self) -> Generator[Any, None, aiohttp.ClientResponse]:
        return self.__aenter__().__await()

    async def __aenter__(self) -> aiohttp.ClientResponse:
        return await self.do_request()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.response is not None:
            if not self.response.closed:
                self.response.close()

##############################################################################


class HttpDownloader (object):

    MAX_CONCURRENT_DOWNLOADS = 5

    def __init__(self, download_dir):
        super(HttpDownloader, self).__init__()
        self.download_dir = download_dir
        self.log = getlog()
        self.download_list = []

    ##########################################################################

    def subdownloader(self, download_dir):
        return HttpDownloader(os.path.join(self.download_dir, download_dir))

    ##########################################################################

    def add_download(self, url, filename=None):
        """
        Add a url to download by this Downloader. The url can be either a plain
        string, an iterable of strings, or a callable that returns an iterable
        of strings.  If its an iterable, the downloader will try each one until
        one of the urls download successfully.

        Optionally specify the filename to write the downloaded url to.
        """
        if filename is None:
            filename = os.path.basename(urllib.parse.urlparse(url).path)
        localfile = os.path.join(self.download_dir, filename)
        self.download_list.append((url, localfile))
        return localfile

    ##########################################################################

    def run(self, post=None):
        asyncio.run(self.do_downloads(post))
        self.download_list = []

    ##########################################################################

    def download_immediate(self, url, filename=None, post=None):
        localfile = self.add_download(url, filename)
        self.run(post)
        return localfile

    ##########################################################################

    async def do_downloads(self, post):
        tasks = []
        sem = asyncio.Semaphore(self.MAX_CONCURRENT_DOWNLOADS)

        async with RetryableHttpClient() as client:
            for url, localfile in self.download_list:
                if not os.path.exists(localfile):
                    tasks.append(self.do_download_one(url, localfile, post, client, sem))
                else:
                    self.log.moreinfo('  [cached]    : {}'.format(url))
                    if post is not None:
                        post(url, localfile)

            return await asyncio.gather(*tasks)

    ##########################################################################

    async def do_download_one(self, url, dest, post, client, sem):
        async with sem:

            destdir = os.path.dirname(dest)
            if not os.path.exists(destdir):
                os.makedirs(destdir)
            tempfile = os.path.join(destdir, '.downloading_{}'.format(os.path.basename(dest)))
            if os.path.exists(tempfile):
                os.remove(tempfile)

            # convert the supplied url to an iterable of urls to try
            # the url could be:
            # - a iterable: nothing to do here
            # - a string:  "http://google.com" -> ["http://google.com"]
            # - a callable: [ u for u in url() ]
            if type(url) is str:
                urls = [url, ]
            elif callable(url):
                urls = [u for u in url()]
            else:
                try:
                    urls = iter(url)
                except TypeError:
                    raise ApplicationError("Invalid type passed as url: {}".format(url))

            try:
                for one_url in urls:
                    self.log.moreinfo('  downloading : {}'.format(one_url))
                    async with client.get(one_url) as resp:
                        content = await resp.read()
                    if resp.status == 200:
                        with open(tempfile, 'wb') as f:
                            f.write(content)
                        os.rename(tempfile, dest)
                        if post is not None:
                            post(one_url, dest)
                        break
                else:
                    raise DownloadError(status=resp.status)
            finally:
                try:
                    os.remove(tempfile)
                except FileNotFoundError:
                    pass

##############################################################################
# THE END
