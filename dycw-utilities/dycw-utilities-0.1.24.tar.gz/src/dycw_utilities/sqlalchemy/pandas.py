import datetime as dt
from collections.abc import Iterator
from decimal import Decimal
from typing import Any

from pandas import DataFrame
from pandas import NaT
from pandas import Series
from sqlalchemy.engine import Engine

from dycw_utilities.numpy import datetime64ns
from dycw_utilities.numpy import has_dtype
from dycw_utilities.pandas import Int64
from dycw_utilities.pandas import boolean
from dycw_utilities.pandas import string
from dycw_utilities.pandas import timestamp_to_date
from dycw_utilities.pandas import timestamp_to_datetime
from dycw_utilities.sqlalchemy import get_column_names
from dycw_utilities.sqlalchemy import get_columns
from dycw_utilities.sqlalchemy import get_table


def insert_dataframe(
    df: DataFrame, table_or_model: Any, engine: Engine, /
) -> None:
    """Insert a DataFrame into a database."""

    names = get_column_names(table_or_model)
    columns = get_columns(table_or_model)
    all_names_to_columns = dict(zip(names, columns))
    names_to_columns = {
        name: col
        for name, col in all_names_to_columns.items()
        if (df.columns == name).any()
    }
    nativized = (
        _nativize_column(df[name], column)
        for name, column in names_to_columns.items()
    )
    rows = zip(*nativized)
    dicts = [dict(zip(names_to_columns, row)) for row in rows]
    if len(dicts) >= 1:
        table = get_table(table_or_model)
        with engine.begin() as conn:
            _ = conn.execute(table.insert(), list(dicts))


def _nativize_column(series: Series, column: Any, /) -> Iterator[Any]:
    """Check the columns of the DataFrame form a subset of the columns of the
    table.
    """

    py_type = column.type.python_type
    as_list = series.tolist()
    if (
        (has_dtype(series, (bool, boolean)) and (py_type in {bool, int}))
        or (has_dtype(series, float) and (py_type is float))
        or (has_dtype(series, (int, Int64)) and (py_type is int))
        or (has_dtype(series, string) and (py_type is str))
    ):
        values = as_list
    elif has_dtype(series, datetime64ns) and (py_type is dt.date):
        values = [None if t is NaT else timestamp_to_date(t) for t in as_list]
    elif has_dtype(series, datetime64ns) and (py_type is dt.datetime):
        values = [
            None if t is NaT else timestamp_to_datetime(t) for t in as_list
        ]
    else:
        raise TypeError(f"Invalid types: {series}, {py_type}")
    for is_null, native in zip(series.isna(), values):
        yield None if is_null else native


def read_dataframe(sel: Any, engine: Engine, /) -> DataFrame:
    """Read a table from a database into a DataFrame."""

    with engine.begin() as conn:
        rows = conn.execute(sel).all()
    sel = {col.name: _get_dtype(col) for col in sel.selected_columns}
    return DataFrame(rows, columns=list(sel)).astype(sel)


def _get_dtype(column: Any, /) -> Any:
    """Get the mapping of names to dtypes."""

    py_type = column.type.python_type
    if py_type is bool:
        return boolean
    elif (py_type is float) or (py_type is Decimal):
        return float
    elif py_type is int:
        return Int64
    elif py_type is str:
        return string
    elif issubclass(py_type, dt.date):
        return datetime64ns
    else:
        raise TypeError(f"Invalid type: {py_type}")  # pragma: no cover
