import logging
from pathlib import Path
from typing import Union

import certifi
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import connectionDone
from twisted.internet.ssl import Certificate
from twisted.internet.ssl import trustRootFromCertificates
from twisted.python import failure
from twisted.web._newclient import ResponseDone
from twisted.web._newclient import ResponseFailed
from twisted.web.client import Agent
from twisted.web.client import BrowserLikePolicyForHTTPS
from twisted.web.http_headers import Headers

logger = logging.getLogger(__name__)


class LargeFileHttpDownloader:
    def __init__(self, url: Union[str, bytes], path: Path):
        self._path = path
        self._url = url.encode() if isinstance(url, str) else url

    @inlineCallbacks
    def download(self) -> Deferred:
        with open(certifi.where(), "r") as f:
            rawPemData = f.read()
        trustRoot = trustRootFromCertificates(
            [
                Certificate.loadPEM(rawCertificate)
                for rawCertificate in rawPemData.split("\n\n")
            ]
        )

        agent = Agent(
            reactor,
            BrowserLikePolicyForHTTPS(trustRoot=trustRoot),
        )
        logger.debug(self._url)

        url = self._url
        while True:
            try:
                response = yield agent.request(
                    b"GET",
                    url,
                    Headers({b"User-Agent": [b"Attune File Downloader"]}),
                    None,
                )

                if response.code == 302:
                    url = response.headers.getRawHeaders("location")[0].encode()
                    continue

                if response.code == 200:
                    downloader = _FileDownloader(self._path)
                else:
                    downloader = _BodyError(
                        response.code, response.request.absoluteURI
                    )
                response.deliverBody(downloader)
                return (yield downloader.deferred)
            except ResponseFailed as e:
                logger.debug(e.reasons[0].getTraceback())
                raise Exception(str(e))


class _FileDownloader(Protocol):
    def __init__(self, path: Path):
        self._finishedDeferred = Deferred()
        self._file = open(path, "wb")
        self._writeSize = 0

    @property
    def deferred(self) -> Deferred:
        return self._finishedDeferred

    def dataReceived(self, data: bytes):
        self._file.write(data)
        self._writeSize += len(data)

    def connectionLost(self, reason: failure.Failure = connectionDone):
        self._file.close()

        if isinstance(reason.value, ResponseDone):
            self._finishedDeferred.callback(self._file)
            return

        self._finishedDeferred.errback(reason)


class _BodyError(Protocol):
    def __init__(self, responseCode, responseUri):
        self._finishedDeferred = Deferred()
        self._responseCode = responseCode
        self._responseUri = responseUri
        self._msg = ""

    @property
    def deferred(self) -> Deferred:
        return self._finishedDeferred

    def dataReceived(self, data: bytes):
        self._msg += bytes

    def connectionLost(self, reason: failure.Failure = connectionDone):
        self._finishedDeferred.errback(
            Exception(
                f"Server returned {self._responseCode} for "
                f"{self._responseUri}\n"
                f"{reason}\n{self._msg}"
            )
        )
