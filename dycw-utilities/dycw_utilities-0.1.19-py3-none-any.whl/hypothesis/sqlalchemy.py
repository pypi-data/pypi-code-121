from typing import Any
from typing import Optional

from hypothesis.strategies import SearchStrategy
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine

from dycw_utilities.hypothesis import draw_and_map
from dycw_utilities.hypothesis.tempfile import temp_dirs
from dycw_utilities.sqlalchemy import create_engine
from dycw_utilities.tempfile import TemporaryDirectory


def sqlite_engines(
    *, metadata: Optional[MetaData] = None, base: Any = None
) -> SearchStrategy[Engine]:
    """Strategy for generating SQLite engines."""

    return draw_and_map(
        _draw_sqlite_engines, temp_dirs(), metadata=metadata, base=base
    )


def _draw_sqlite_engines(
    temp_dir: TemporaryDirectory,
    /,
    *,
    metadata: Optional[MetaData] = None,
    base: Any = None,
) -> Engine:
    path = temp_dir.name.joinpath("db.sqlite")
    engine = create_engine("sqlite", database=path.as_posix())
    if metadata is not None:
        metadata.create_all(engine)
    if base is not None:
        base.metadata.create_all(engine)

    # attach temp_dir to the engine, so as to keep it alive
    engine.temp_dir = temp_dir  # type: ignore

    return engine
