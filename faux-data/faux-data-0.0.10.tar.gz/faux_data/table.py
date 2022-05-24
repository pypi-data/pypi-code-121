import logging
from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd
import yaml

from .column import Column
from .factory import ColumnFactory, TargetFactory
from .target import Target

pd.set_option("max_colwidth", 180)

log = logging.getLogger(__name__)


@dataclass(kw_only=True)
class Table:
    name: str
    rows: int
    columns: List[Column]
    targets: List[Target] = field(default_factory=list, repr=False)
    output_columns: List[str] = field(default_factory=list)
    df: pd.DataFrame = None
    complete: bool = False
    error: Exception = None

    @classmethod
    def parse_from_yaml(cls, yaml_str):
        conf = yaml.safe_load(yaml_str)
        return cls(**conf)

    def __init__(self,
                 name: str,
                 rows: int | str,
                 columns: list,
                 output_columns: list = None,
                 targets: list = None):
        try:
            self.name = name
            self.rows = rows
            self.columns = self.parse_cols(columns)
            self.targets = self.parse_targets(targets)
            self.output_columns = output_columns if output_columns else None

        except Exception as e:
            self.complete = False
            log.error(e)
            raise TableParsingException(f"Error on table [{self.name}]. {e}")

    def parse_cols(self, columns) -> list:
        cols = []
        for column in columns:
            cols.append(ColumnFactory.parse(column))

        return cols

    def parse_targets(self, targets) -> list:
        targs = []

        if not targets:
            return targs

        for target in targets:
            try:
                targs.append(TargetFactory.parse(target))
            except Exception as e:
                log.warning(f"unable to parse target - {e}")
                pass

        return targs

    def create_df(self) -> pd.DataFrame:
        if isinstance(self.rows, int):
            return pd.DataFrame({"rowId": np.arange(self.rows)})
        else:
            df = pd.read_csv(self.rows)
            df['rowId'] = df.index
            return df

    def generate(self) -> None:
        """Generates the table data"""
        try:
            self.df = self.create_df()
            for column in self.columns:
                column.maybe_add_column(self.df)

        except Exception as e:
            self.complete = False
            self.error = TableGenerationException(
                f"Error on table [{self.name}]. {e}")

            raise self.error

        else:
            self.df.drop(columns="rowId", inplace=True)

            if self.output_columns:
                self.df = self.df[self.output_columns]

            self.complete = True

    def load(self):
        """Loads `self.df` to the specified targets"""
        if not self.targets:
            print("No targets!")

        try:
            for target in self.targets:
                target.save(self)

        except Exception as e:
            self.complete = False
            self.error = TableLoadingException(
                f"Error on table [{self.name}]. {e}")

            raise self.error

    def run(self):
        self.generate()
        self.load()

    def result(self):
        return "yope"


class TableParsingException(Exception):
    pass


class TableGenerationException(Exception):
    pass


class TableLoadingException(Exception):
    pass
