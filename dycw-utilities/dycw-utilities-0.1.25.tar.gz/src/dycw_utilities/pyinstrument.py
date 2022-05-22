import datetime as dt
from pathlib import Path
from typing import Iterator

from pyinstrument import Profiler

from dycw_utilities.contextlib import contextmanager
from dycw_utilities.pathlib import PathLike


@contextmanager
def profile(*, path: PathLike = Path.cwd()) -> Iterator[None]:
    """Profile the contents of a block."""

    with Profiler() as profiler:
        yield
    now = dt.datetime.now()
    filename = Path(path, f"profile__{now:%Y%m%dT%H%M%S}.html")
    with open(filename, mode="w") as fh:
        _ = fh.write(profiler.output_html())
