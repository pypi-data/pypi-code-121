from dataclasses import dataclass
from enum import Enum
from typing import List, Union
from typing_extensions import TypedDict


class StrEnum(str, Enum):
    def __repr__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)


class ColumnType(StrEnum):
    Numerical = 'Numerical'
    Categorical = 'Categorical'
    Textual = 'Textual'
    TimeStamp = 'TimeStamp'
    Auto = 'Auto'
    Empty = 'Empty'


@dataclass
class Column:
    name: str
    type: ColumnType


class ColumnDict(TypedDict):
    name: str
    type: ColumnType


class DataConfigurationType(StrEnum):
    Data = 'Data'
    Column = 'Column'
    Columns = 'Columns'


# class DefinedConstraint(StrEnum):
#     ColumnNumberConstraint = 'ColumnNumberConstraint'
#     ColumnRequiredConstraint = 'ColumnRequiredConstraint'
#     RecordNumberConstraint = 'RecordNumberConstraint'
#
#
# @dataclass
# class Constraint:
#     dataKey: str
#     key: str
#     type: DataConfigurationType
#     constraint: DefinedConstraint
#     value: int


@dataclass
class DataConfiguration:
    display_name: str
    key: str
    type: DataConfigurationType
    value: Union[Column, List[Column]]
    required: bool
    # constraints: List[Constraint]
    description: str

    def __post_init__(self):
        if self.value is None:
            if self.type == DataConfigurationType.Column:
                self.value = Column(name='', type=ColumnType.Empty)
            elif self.type == DataConfigurationType.Columns:
                self.value = []


@dataclass
class DataConfig:
    display_name: str
    key: str
    description: str
    configurations: List[DataConfiguration]
    # constraints: List


@dataclass
class PredefinedAIDataConfig:
    key: str
    description: str
    data_configs: List[DataConfig]

