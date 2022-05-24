import os
import tempfile
import zipfile
from urllib.error import (
    HTTPError,
)
from urllib.request import (
    urlretrieve,
)
from uuid import (
    uuid4,
)

from progress.bar import (
    Bar,
)

from m3_gar.importer.signals import (
    post_download,
    pre_download,
)
from m3_gar.importer.source.exceptions import (
    BadArchiveError,
    EmptyArchiveError,
    RetrieveError,
)
from m3_gar.importer.source.tablelist import (
    TableList,
)
from m3_gar.importer.source.wrapper import (
    LocalArchiveWrapper,
)


class ZipFile(zipfile.ZipFile):

    @classmethod
    def open_file(cls, source):
        try:
            return cls(source)
        except zipfile.BadZipfile:
            raise BadArchiveError(source)


class LocalArchiveTableList(TableList):
    wrapper_class = LocalArchiveWrapper

    def get_archive(self, source):
        if zipfile.is_zipfile(source):
            archive_class = ZipFile
        else:
            raise BadArchiveError(source)

        return archive_class.open_file(source)

    def load_data(self, source):
        archive = self.get_archive(source)

        if not archive.namelist():
            raise EmptyArchiveError(source)

        return self.wrapper_class(source=archive)


class DlProgressBar(Bar):
    message = 'Downloading: '
    suffix = '%(index)d/%(max)d. ETA: %(elapsed)s'
    hide_cursor = False


class RemoteArchiveTableList(LocalArchiveTableList):
    download_progress_class = DlProgressBar

    def load_data(self, source):
        progress = self.download_progress_class()

        def update_progress(count, block_size, total_size):
            progress.goto(int(count * block_size * 100 / total_size))

        if self.tempdir:
            tmp_file = os.path.join(self.tempdir, str(uuid4()))
        else:
            tmp_file = None

        pre_download.send(sender=self.__class__, url=source)
        try:
            path = urlretrieve(source, reporthook=update_progress, filename=tmp_file)[0]
        except HTTPError as e:
            raise RetrieveError(
                f'Can not download data archive at url `{source}`. '
                f'Error occurred: "{e}"'
            )
        progress.finish()
        post_download.send(sender=self.__class__, url=source, path=path)

        return super().load_data(source=path)
