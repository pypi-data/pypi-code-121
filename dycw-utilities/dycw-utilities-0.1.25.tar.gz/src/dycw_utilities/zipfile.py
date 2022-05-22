from collections.abc import Iterator
from pathlib import Path
from zipfile import ZipFile

from dycw_utilities.contextlib import contextmanager
from dycw_utilities.pathlib import PathLike
from dycw_utilities.tempfile import TemporaryDirectory


@contextmanager
def yield_zip_file_contents(path: PathLike, /) -> Iterator[list[Path]]:
    """Yield the contents of a zipfile in a temporary directory."""

    with ZipFile(path) as zf, TemporaryDirectory() as temp:
        zf.extractall(path=temp)
        yield list(temp.iterdir())
    _ = zf  # this ensures that `zf` is considered returned; for coverage
