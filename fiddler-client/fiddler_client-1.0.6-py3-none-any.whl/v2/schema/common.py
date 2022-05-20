import enum
from typing import Any, List, Optional

from pydantic import Field

from fiddler.v2.schema.base import BaseDataSchema


@enum.unique
class DataType(str, enum.Enum):
    """Supported datatypes for the Fiddler engine."""

    FLOAT = 'float'
    INTEGER = 'int'
    BOOLEAN = 'bool'
    STRING = 'str'
    CATEGORY = 'category'

    def is_numeric(self):
        return self.value in (DataType.INTEGER.value, DataType.FLOAT.value)

    def is_bool_or_cat(self):
        return self.value in (DataType.BOOLEAN.value, DataType.CATEGORY.value)

    def is_valid_target(self):
        return self.value != DataType.STRING.value


class Column(BaseDataSchema):
    """Represents a single column of a dataset or model input/output.

    :param name: The name of the column (corresponds to the header row of a
        CSV file)
    :param data_type: The best encoding type for this column's data.
    :param possible_values: If data_type is CATEGORY, then an exhaustive list
        of possible values for this category must be provided. Otherwise
        this field has no effect and is optional.
    :param is_nullable: Optional metadata. Tracks whether or not this column is
        expected to contain some null values.
    :param value_range_x: Optional metadata. If data_type is FLOAT or INTEGER,
        then these values specify a range this column's values are expected to
        stay within. Has no effect for non-numerical data_types.
    """

    name: str = Field(alias='column-name')
    data_type: DataType = Field(alias='data-type')
    possible_values: Optional[List[Any]] = Field(None, alias='possible-values')
    is_nullable: Optional[bool] = Field(None, alias='is-nullable')
    value_range_min: Optional[float] = Field(None, alias='value-range-min')
    value_range_max: Optional[float] = Field(None, alias='value-range-max')

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True

    # # @TODO: Use pydantic validator
    # inappropriate_value_range = not self.data_type.is_numeric() and not (
    #     self.value_range_min is None and self.value_range_max is None
    # )
    # if inappropriate_value_range:
    #     raise ValueError(
    #         f'Do not pass `value_range` for '
    #         f'non-numerical {self.data_type} data type.'
    #     )

    @classmethod
    def from_dict(cls, desrialized_json: dict):
        return cls.parse_obj(desrialized_json)


class DatasetInfo(BaseDataSchema):
    columns: List[Column]
