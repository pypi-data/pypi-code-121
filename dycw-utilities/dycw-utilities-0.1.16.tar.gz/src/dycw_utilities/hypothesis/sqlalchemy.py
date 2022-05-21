import datetime as dt
from collections.abc import Callable
from os import getpid
from pathlib import Path
from typing import Optional
from typing import Union

from hypothesis.strategies import SearchStrategy
from sqlalchemy.engine import Engine

from dycw_utilities.hypothesis import draw_and_map
from dycw_utilities.hypothesis.tempfile import temp_dirs
from dycw_utilities.hypothesis.typing import MaybeSearchStrategy
from dycw_utilities.sqlalchemy import create_engine
from dycw_utilities.tempfile import TemporaryDirectory


def sqlite_engines(
    *,
    dir: MaybeSearchStrategy[Union[Path, TemporaryDirectory]] = temp_dirs(),
    post_init: Optional[Callable[[Engine], None]] = None,
) -> SearchStrategy[Engine]:
    """Strategy for generating SQLite engines."""

    return draw_and_map(_draw_sqlite_engines, dir, post_init=post_init)


def _draw_sqlite_engines(
    dir: Union[Path, TemporaryDirectory],
    /,
    *,
    post_init: Optional[Callable[[Engine], None]] = None,
) -> Engine:
    dir_use = dir if isinstance(dir, Path) else dir.name
    now = dt.datetime.now().strftime("%4Y%m%dT%H%M%S.%f")
    pid = getpid()
    path = dir_use.joinpath(f"db__{now}__{pid}.sqlite")
    engine = create_engine("sqlite", database=path.as_posix())
    if post_init is not None:
        post_init(engine)
    return engine
