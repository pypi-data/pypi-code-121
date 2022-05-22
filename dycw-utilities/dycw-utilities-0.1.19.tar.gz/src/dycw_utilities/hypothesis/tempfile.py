from pathlib import Path
from uuid import UUID

from hypothesis.strategies import SearchStrategy
from hypothesis.strategies import uuids

from dycw_utilities.hypothesis import draw_and_map
from dycw_utilities.tempfile import TemporaryDirectory
from dycw_utilities.tempfile import gettempdir


def temp_dirs() -> SearchStrategy[TemporaryDirectory]:
    dir = gettempdir().joinpath("hypothesis")
    dir.mkdir(exist_ok=True)
    return draw_and_map(_draw_temp_dirs, uuids(), dir)


def _draw_temp_dirs(uuid: UUID, dir: Path, /) -> TemporaryDirectory:
    return TemporaryDirectory(prefix=f"{uuid}__", dir=dir.as_posix())
