from collections import namedtuple
from pathlib import Path

from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    ARCHIVE_FORMAT_KEY_7Z,
)
from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    ARCHIVE_FORMAT_KEY_TAR,
)
from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    ARCHIVE_FORMAT_KEY_TAR_BZ2,
)
from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    ARCHIVE_FORMAT_KEY_TAR_GZ,
)
from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    ARCHIVE_FORMAT_KEY_TAR_XZ,
)
from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    ARCHIVE_FORMAT_KEY_UNKNOWN,
)
from attune_project_api.items.file_archive_tuples.file_tuple_constants import (
    ARCHIVE_FORMAT_KEY_ZIP,
)


ArchiveFormat = namedtuple("ArchiveFormat", ["key", "name", "extensions"])
UnknownFormat = ArchiveFormat(ARCHIVE_FORMAT_KEY_UNKNOWN, "Unknown Format", [])
archiveFormatByKey = {ARCHIVE_FORMAT_KEY_UNKNOWN: UnknownFormat}

__ARCHIVE_TRYER_FORMAT = []


def isTarFile(archiveFormatKey: str) -> bool:
    return archiveFormatKey in (
        ARCHIVE_FORMAT_KEY_TAR,
        ARCHIVE_FORMAT_KEY_TAR_GZ,
        ARCHIVE_FORMAT_KEY_TAR_BZ2,
        ARCHIVE_FORMAT_KEY_TAR_XZ,
    )


def is7zFile(archiveFormatKey: str) -> bool:
    return archiveFormatKey in (ARCHIVE_FORMAT_KEY_7Z,)


def __registerArchiveFormat(key: str, name: str, extensions: list[str]):
    def wrapper(tryerMethod):
        format = ArchiveFormat(key, name, extensions)
        archiveFormatByKey[format.key] = format
        __ARCHIVE_TRYER_FORMAT.append((format, tryerMethod))
        return tryerMethod

    return wrapper


class InvalidArchiveFormatException(Exception):
    pass


def guessArchiveFormat(path: Path) -> ArchiveFormat:
    # Try tar first
    if _tryTar(path):
        return archiveFormatByKey[ARCHIVE_FORMAT_KEY_TAR]

    for format, tryer in __ARCHIVE_TRYER_FORMAT:
        if tryer(path):
            return format
    return UnknownFormat


@__registerArchiveFormat(ARCHIVE_FORMAT_KEY_TAR, "tar", ["tar"])
def _tryTar(path: Path) -> bool:
    return _tryTarWithFlag(path, "r:")


@__registerArchiveFormat(ARCHIVE_FORMAT_KEY_TAR_GZ, "tar.gz", ["tar.gz", "tgz"])
def _tryTarGz(path: Path) -> bool:
    return _tryTarWithFlag(path, "r:gz")


@__registerArchiveFormat(ARCHIVE_FORMAT_KEY_TAR_BZ2, "tar.bz2", ["tar.bz2"])
def _tryTarBz2(path: Path) -> bool:
    return _tryTarWithFlag(path, "r:bz2")


@__registerArchiveFormat(
    ARCHIVE_FORMAT_KEY_TAR_XZ, "tar.xz", ["tar.lzma", "tar.xz"]
)
def _tryTarLzma(path: Path) -> bool:
    return _tryTarWithFlag(path, "r:xz")


def _tryTarWithFlag(path: Path, mode: str) -> bool:
    from tarfile import TarFile, TarError

    try:
        with TarFile.open(path, mode):
            pass
        return True
    except TarError:
        return False


@__registerArchiveFormat(ARCHIVE_FORMAT_KEY_7Z, "7z", ["7z"])
def _try7z(path: Path) -> bool:
    from py7zr import is_7zfile

    return is_7zfile(path)


@__registerArchiveFormat(ARCHIVE_FORMAT_KEY_ZIP, "zip", ["zip"])
def _tryZip(path: Path) -> bool:

    import zipfile

    return zipfile.is_zipfile(path)
