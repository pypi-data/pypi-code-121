from pytmpdir.directory_ import Directory
from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest

from attune_project_api._private.large_file_http_downloader import (
    LargeFileHttpDownloader,
)


class HttpLargeFileDownloaderTest(unittest.TestCase):
    @inlineCallbacks
    def testDownload7zip(self):
        _7zurl = "https://www.7-zip.org/a/7z2107-x64.msi"
        dir = Directory()
        file_ = dir.createFile(name="test")
        downloader = LargeFileHttpDownloader(_7zurl, file_.realPath)

        yield downloader.download()

        # TODO, Add md5sum support fot pytmpdir
        # compare md5 with assert equal
