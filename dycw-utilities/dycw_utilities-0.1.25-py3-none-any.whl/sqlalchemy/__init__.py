from collections.abc import Callable
from functools import reduce
from operator import ge
from operator import le
from re import search
from typing import Any
from typing import Optional

from sqlalchemy import Table
from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import create_engine as _create_engine
from sqlalchemy.engine import URL
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DatabaseError
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool
from sqlalchemy.pool import Pool


def columnwise_max(*columns: Any) -> Any:
    """Compute the columnwise max of a number of columns."""

    return _columnwise_minmax(*columns, op=ge)


def columnwise_min(*columns: Any) -> Any:
    """Compute the columnwise min of a number of columns."""

    return _columnwise_minmax(*columns, op=le)


def _columnwise_minmax(*columns: Any, op: Callable[[Any, Any], Any]) -> Any:
    """Compute the columnwise min of a number of columns."""

    def func(x: Any, y: Any, /) -> Any:
        x_none = x.is_(None)
        y_none = y.is_(None)
        col = case(
            (and_(x_none, y_none), None),
            (and_(~x_none, y_none), x),
            (and_(x_none, ~y_none), y),
            (op(x, y), x),
            else_=y,
        )
        # try auto-label
        names = {
            value
            for col in [x, y]
            if (value := getattr(col, "name", None)) is not None
        }
        try:
            (name,) = names
        except ValueError:
            return col
        else:
            return col.label(name)

    return reduce(func, columns)


def create_engine(
    drivername: str,
    /,
    *,
    username: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
    poolclass: Optional[type[Pool]] = NullPool,
) -> Engine:
    """Create a SQLAlchemy engine."""

    url = URL.create(
        drivername,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )
    return _create_engine(url, future=True, poolclass=poolclass)


def ensure_table_created(table_or_model: Any, engine: Engine, /) -> None:
    """Ensure a table is created."""

    table = get_table(table_or_model)
    try:
        with engine.begin() as conn:
            table.create(conn)
    # note that OperationalError < DatabaseError
    except OperationalError as error:
        # sqlite
        (msg,) = error.args
        if not search("table .* already exists", msg):  # pragma: no cover
            raise
    except DatabaseError as error:  # pragma: no cover
        # oracle
        (msg,) = error.args
        if not search(
            "ORA-00955: name is already used by an existing object", msg
        ):
            raise


def ensure_table_dropped(table_or_model: Any, engine: Engine, /) -> None:
    """Ensure a table is dropped."""

    table = get_table(table_or_model)
    try:
        with engine.begin() as conn:
            table.drop(conn)
    # note that OperationalError < DatabaseError
    except OperationalError as error:
        # sqlite
        (msg,) = error.args
        if not search("no such table", msg):  # pragma: no cover
            raise
    except DatabaseError as error:  # pragma: no cover
        # oracle
        (msg,) = error.args
        if not search("ORA-00942: table or view does not exist", msg):
            raise


def get_column_names(table_or_model: Any, /) -> list[str]:
    """Get the column names from a table or model."""

    return [col.name for col in get_columns(table_or_model)]


def get_columns(table_or_model: Any, /) -> list[Any]:
    """Get the columns from a table or model."""

    return list(get_table(table_or_model).columns)


def get_table(table_or_model: Any, /) -> Table:
    """Get the table from a ORM model."""

    if isinstance(table_or_model, Table):
        return table_or_model
    else:
        return table_or_model.__table__
