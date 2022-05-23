from enum import Enum


class FileArchiveTupleTypeEnum(Enum):
    VERSIONED = "com.servertribe.attune.tuples.FileArchiveVersionedTuple"
    LARGE = "com.servertribe.attune.tuples.FileArchiveLargeTuple"


ARCHIVE_FORMAT_KEY_ZIP: str = "zip"
ARCHIVE_FORMAT_KEY_7Z: str = "7z"
ARCHIVE_FORMAT_KEY_TAR: str = "tar"
ARCHIVE_FORMAT_KEY_TAR_GZ: str = "tar.gz"
ARCHIVE_FORMAT_KEY_TAR_BZ2: str = "tar.bz2"
ARCHIVE_FORMAT_KEY_TAR_XZ: str = "tar.xz"
ARCHIVE_FORMAT_KEY_UNKNOWN: str = "unknown"
