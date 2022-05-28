import enum
import typing

import pandas as pd
from pydantic import BaseModel
from whylogs import DatasetProfile

from mlfoundry.dataset.whylogs_types import DataFrameSummary
from mlfoundry.log_types import DatasetSchemaRunLog, DatasetStatsRunLog, StatsSource


class FieldType(enum.Enum):
    NUMERICAL = "NUMERICAL"
    CATEGORICAL = "CATEGORICAL"
    EMPTY = "EMPTY"


class InferredFieldType(BaseModel):
    field_type: typing.Optional[FieldType]
    pandas_inferred_dtype: str


class Profiles(BaseModel):
    features: DatasetProfile
    actuals: typing.Optional[DatasetProfile] = None
    predictions: typing.Optional[DatasetProfile] = None

    class Config:
        arbitrary_types_allowed = True


class DataSet(BaseModel):
    dataset_name: str

    features: pd.DataFrame
    actuals: typing.Optional[pd.Series] = None
    predictions: typing.Optional[pd.Series] = None

    class Config:
        arbitrary_types_allowed = True
        allow_mutation = False


class DatasetStats(BaseModel):
    features: DataFrameSummary
    actuals: typing.Optional[DataFrameSummary] = None
    predictions: typing.Optional[DataFrameSummary] = None

    def to_log(self) -> DatasetStatsRunLog:
        return DatasetStatsRunLog(value=self.dict(), stats_source=StatsSource.WHYLOGS)


class DatasetSchema(BaseModel):
    features: typing.Dict[str, InferredFieldType]

    # only supports scalar output at this point
    # we do not support multi-label
    actuals: typing.Optional[InferredFieldType] = None
    predictions: typing.Optional[InferredFieldType] = None

    def to_log(self) -> DatasetSchemaRunLog:
        return DatasetSchemaRunLog(value=self.dict())
