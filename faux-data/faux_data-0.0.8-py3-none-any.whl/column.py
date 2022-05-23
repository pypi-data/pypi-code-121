import abc
import logging
import random
import string
from dataclasses import dataclass, field
from decimal import Decimal
from itertools import chain, zip_longest
from typing import List, Optional

import numpy as np
import pandas as pd

pandas_type_mapping = {
    "Int": "Int64",
    "String": "string",
    "Float": "float64",
    "Decimal": "float",
    "Timestamp": "datetime64[ns]",
    "TimestampAsInt": "Int64",
    "Bool": "bool",
    "Date": "object",
}


@dataclass(kw_only=True)
class Column(abc.ABC):
    id: str = ""
    name: str
    column_type: str
    data_type: str = None
    output_type: Optional[str] = None
    null_percentage: int = 0
    decimal_places: int = 4
    date_format: str = "%Y-%m-%d %H:%M:%S"

    def maybe_add_column(self, df: pd.DataFrame) -> None:
        try:
            self.add_column(df)
            self.post_process(df)
        except Exception as e:
            raise ColumnGenerationException(
                f"Error on column [{self.name}]. Caused by: {e}.")

    def add_column(self, df: pd.DataFrame) -> None:
        df[self.name] = self.generate(len(df))

    def post_process(self, df: pd.DataFrame) -> None:
        match self.data_type:
            case None:
                pass
            case 'Decimal':
                df[self.name] = df[self.name][df[self.name].notnull()] \
                                    .round(decimals=self.decimal_places) \
                                    .astype("string") \
                                    .apply(lambda v: Decimal(v)) \
                                    .astype("object")
            case _:
                pandas_type = self.pandas_type()
                if pandas_type is None:
                    logging.warning(f"column: [{self.name}] -> data_type [{self.data_type}] not recognised, ignoring.")
                else:
                    df[self.name] = df[self.name].astype(self.pandas_type())

        match self.output_type:
            case None:
                pass
            case 'String':
                if df[self.name].dtype == 'datetime64[ns]':
                    df[self.name] = df[self.name].dt.strftime(self.date_format).astype('string')
                else:
                    df[self.name] = df[self.name].astype(pandas_type_mapping[self.output_type])
            case _:
                raise Exception(f"output_type: [{self.output_type}] not recognised")

    def generate(self, rows: int) -> pd.Series:
        raise NotImplementedError("Subclasses of Column should implement either `generate` or `add_column`")

    def pandas_type(self) -> str | None:
        if self.data_type:
            return pandas_type_mapping.get(self.data_type)
        return None


@dataclass(kw_only=True)
class Fixed(Column):
    """
    A column with a single fixed `value:`.

    """

    value: any

    def generate(self, rows: int) -> pd.Series:
        match self.data_type:
            case 'Int':
                return pd.Series(np.full(rows, self.value)).astype('float64').astype(self.pandas_type())
            case 'Bool':
                return pd.Series(np.full(rows, bool(self.value)), dtype=self.pandas_type())
            case _:
                return pd.Series(np.full(rows, self.value), dtype=self.pandas_type())


@dataclass(kw_only=True)
class Empty(Column):
    """
    An empty column.

    """
    def add_column(self, df: pd.DataFrame):
        df[self.name] = pd.Series(np.full(len(df), np.nan), dtype=self.pandas_type())


@dataclass(kw_only=True)
class MapValues(Column):
    """
    A map column.

    """
    source_column: str
    values: dict
    default: any = np.nan

    def add_column(self, df: pd.DataFrame):
        df[self.name] = df[self.source_column].map(self.values).fillna(self.default)



unit_factor = {
    's' :1E9,
    'ms':1E6,
    'us':1E3,
    'ns':1
}

@dataclass(kw_only=True)
class Random(Column):
    """
    A random value.

    """

    data_type: str = "Int"
    min: any = 0
    max: any = 1
    str_max_chars: int = 5000
    time_unit: str = 'ms'

    def generate(self, rows: int) -> pd.Series:
        match self.data_type:
            case 'Int' | 'Bool':
                return pd.Series(np.random.randint(int(self.min), int(self.max)+1, rows), dtype=self.pandas_type())

            case 'Float' | 'Decimal':
                return pd.Series(np.random.uniform(float(self.min), float(self.max)+1, rows)
                                          .round(decimals=self.decimal_places),
                                 dtype=self.pandas_type())

            case 'String':
                # limit how long strings can be
                self.min = min(int(self.min), self.str_max_chars)
                self.max = min(int(self.max), self.str_max_chars)
                return pd.Series(list(''.join(random.choices(string.ascii_letters, k=random.randint(self.min, self.max))) for _ in range(rows)), dtype=self.pandas_type())

            case 'Timestamp':
                date_ints_series = self.random_date_ints(self.min, self.max, rows, self.time_unit)
                return pd.to_datetime(date_ints_series, unit=self.time_unit)

            case 'TimestampAsInt':
                date_ints_series = self.random_date_ints(self.min, self.max, rows, self.time_unit)
                return date_ints_series

            case _:
                raise ColumnGenerationException(f"Data type [{self.data_type}] not recognised")


    def random_date_ints(self, start, end, rows, unit='ms'):
        start, end = pd.Timestamp(start), pd.Timestamp(end)
        return pd.Series(np.random.uniform(start.value // unit_factor[unit], end.value // unit_factor[unit], rows)).astype(int)


@dataclass(kw_only=True)
class Selection(Column):
    """
    A random selection from some preset values

    """

    values: List[any] = field(default_factory=list)
    #source_columns: List[any] = field(default_factory=list)
    weights: List[int] = field(default_factory=list)

    def __post_init__(self):
        if self.data_type == 'Bool' and not self.values:
            self.values = [True, False]
        elif not self.values:
            raise Exception("no `values:` were provided ")

        if self.weights:
            value_weight_pairs = list(zip_longest(self.values, self.weights[0:len(self.values)], fillvalue=1))
            self.values = list(chain(*[list([k] * v) for k, v in value_weight_pairs]))


    def generate(self, rows: int) -> pd.Series:
        return pd.Series(np.random.choice(self.values, rows, replace=True), dtype=self.pandas_type())


@dataclass(kw_only=True)
class Sequential(Column):
    """

    See https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases for `step:` values for Timestamps
    """
    start: any = 0
    step: any = 1

    def add_column(self, df: pd.DataFrame) -> None:
        if self.data_type in ['Int', 'Decimal', 'Float', None]:
            df[self.name] = (df['rowId'] * float(self.step) + float(self.start)).round(decimals=self.decimal_places)

        elif self.data_type == 'Timestamp':
            df[self.name] = pd.date_range(start=self.start, periods=len(df), freq=self.step)

        else:
            raise ColumnGenerationException(f"Data type [{self.data_type}] not recognised")


@dataclass(kw_only=True)
class Map(Column):
    """
    Creates a dict of columns based on the source cols

    """

    source_columns: List[str] = field(default_factory=list)
    columns: List = field(default_factory=list)
    drop: bool = False
    select_one: bool = False
    json: bool = False

    def add_column(self, df: pd.DataFrame) -> None:
        if self.columns:
            self.drop = True
            for sub_col in self.columns:
                self.source_columns.append(sub_col.name)
                sub_col.maybe_add_column(df)


        if self.select_one:
            # randomly select one source_column per row and blank all other columns on that row
            chosen_cols = df[self.source_columns].columns.to_series().sample(len(df), replace=True, ignore_index=True)
            for col in self.source_columns:
                df.loc[chosen_cols != col, col] = np.nan

        if self.json:
            df[self.name] = pd.Series(df[self.source_columns].to_json(orient='records', lines=True).splitlines()).astype("string")
        else:
            df[self.name] = df[self.source_columns].to_dict(orient='records')

        if self.drop:
            df.drop(columns=self.source_columns, inplace=True)


@dataclass(kw_only=True)
class Array(Column):
    """
    Creates an array column based on a list of `source_columns:`.

    """

    source_columns: List[str] = field(default_factory=list)

    def add_column(self, df: pd.DataFrame) -> None:
        df[self.name] = list(df[self.source_columns].values)


@dataclass(kw_only=True)
class Series(Column):
    """
    Repeats a series of values

    """

    values: List[str] = field(default_factory=list)

    def generate(self, rows: int) -> pd.Series:
        repeats = rows // len(self.values) + 1
        return pd.Series(np.tile(self.values, repeats)[0:rows])


@dataclass(kw_only=True)
class ExtractDate(Column):
    """
    Extracts dates from a `source_columnn:`.

    """

    source_column: str

    def add_column(self, df: pd.DataFrame) -> None:
        match self.data_type:
            case 'String' | 'Int':
                df[self.name] = df[self.source_column].dt.strftime(self.date_format)
            case 'Date':
                df[self.name] = df[self.source_column].dt.date
            case _:
                raise NotImplementedError(f"data_type: [{self.data_type}] is not implemented for the ExtractDate column_type")


@dataclass(kw_only=True)
class Eval(Column):
    """
    An eval column

    """

    expression: str

    def add_column(self, df: pd.DataFrame) -> None:
        df[self.name] = df.eval(self.expression)


@dataclass(kw_only=True)
class TimestampOffset(Column):
    """
    Create a new column by adding or removing random time deltas from another timestamp column.

    """
    min: str
    max: str
    source_column: str
    time_unit: str = "s"

    def add_column(self, df: pd.DataFrame) -> None:
        low = pd.Timedelta(self.min).total_seconds()
        high = pd.Timedelta(self.max).total_seconds()

        df[self.name] = df[self.source_column] + pd.to_timedelta(np.random.uniform(low, high, size=len(df)), 's').round(self.time_unit)


class ColumnGenerationException(Exception):
    pass
