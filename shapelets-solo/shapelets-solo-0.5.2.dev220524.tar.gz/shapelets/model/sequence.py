# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum

from shapelets.model.sequence_axis import SequenceAxis


class SequenceColumnDataTypeEnum(Enum):
    NUMERICAL = "NUMERICAL"
    NUMERICAL_FROM_STRING = "NUMERICAL_FROM_STRING"
    INTEGER = "INTEGER"
    ORDINAL = "ORDINAL"
    TIMESTAMP = "TIMESTAMP"
    TIMESTAMP_SECONDS_FROM_STRING = "TIMESTAMP_SECONDS_FROM_STRING"
    TIMESTAMP_MILLIS_FROM_STRING = "TIMESTAMP_MILLIS_FROM_STRING"
    SYMBOLIC = "SYMBOLIC"
    UNCERTAIN = "UNCERTAIN"


class SequenceColumnInfoEnum(Enum):
    UNIDIMENSIONAL = "UNIDIMENSIONAL"
    MULTIDIMENSIONAL = "MULTIDIMENSIONAL"
    UNCERTAIN = "UNCERTAIN"


class SequenceDensityEnum(Enum):
    DENSE = "DENSE"
    SPARSE = "SPARSE"


SequenceDensityEnumMapping = {
    "Dense.Regular": SequenceDensityEnum.DENSE,
    "Dense.Irregular": SequenceDensityEnum.DENSE,
    "DENSE": SequenceDensityEnum.DENSE,
    "Sparse": SequenceDensityEnum.SPARSE,
    "SPARSE": SequenceDensityEnum.SPARSE
}


class SequenceRegularityEnum(Enum):
    REGULAR = "REGULAR"
    IRREGULAR = "IRREGULAR"


class SequenceBaseTypeEnum(Enum):
    INTEGER = "INTEGER"
    ORDINAL = "ORDINAL"
    NUMERICAL = "NUMERICAL"
    SYMBOLIC = "SYMBOLICAL"
    UNCERTAIN = "UNCERTAIN"
    COMPLEXNUMBER = "COMPLEX_NUMBER"
    GEO2D = "GEO2D"
    GEO3D = "GEO3D"
    ISAXREPRESENTATION = "ISAX_REPRESENTATION"
    MATRIXPROFILE = "MATRIX_PROFILE"


class AttributeNames(Enum):
    AXIS = "axis"
    AXIS_INFO = "axisInfo"
    BASE_TYPE = "baseType"
    DENSITY = "density"
    ID = "id"
    LENGTH = "length"
    OFFSET = "offset"
    NAME = "name"
    SEQUENCE = "Sequence"
    SEQUENCE_ID = "sequence_id"
    UNITS = "units"


class Sequence:
    """
    This class is a data holder to represent Shapelets Sequences.
    """

    def __init__(self,
                 sequence_id: str,
                 name: str,
                 axis: SequenceAxis,
                 length: int,
                 offset: int,
                 units: str,
                 density: SequenceDensityEnum,
                 base_type: SequenceBaseTypeEnum):
        self.sequence_id = sequence_id
        self.name = name
        self.axis = axis
        self.offset = offset
        self.length = length
        self.units = units
        if isinstance(density, SequenceDensityEnum):
            self.density = density
        elif isinstance(density, str):
            self.density = SequenceDensityEnumMapping[density]
        else:
            raise ValueError(f"unexpected type for density: {density}")
        if isinstance(base_type, SequenceBaseTypeEnum):
            self.base_type = base_type
        elif isinstance(base_type, str):
            self.base_type = SequenceBaseTypeEnum[base_type.upper()]
        else:
            raise ValueError(f"unexpected type for base_type: {base_type}")

    def __hash__(self):
        return hash((self.sequence_id,
                     self.name,
                     self.offset,
                     self.length,
                     self.density,
                     self.axis,
                     self.units,
                     self.base_type))

    def __eq__(self, other):
        return (isinstance(other, Sequence) and
                self.sequence_id == other.sequence_id and
                self.offset == other.offset and
                self.length == other.length and
                self.density == other.density and
                self.axis == other.axis and
                self.units == other.units and
                self.base_type == other.base_type)

    def __repr__(self):
        s_repr = f"{AttributeNames.SEQUENCE.value}({AttributeNames.SEQUENCE_ID.value}={self.sequence_id}, "
        s_repr += f"{AttributeNames.NAME.value}={self.name}, "
        s_repr += f"{AttributeNames.OFFSET.value}={self.offset}, "
        s_repr += f"{AttributeNames.LENGTH.value}={self.length}, "
        s_repr += f"{AttributeNames.UNITS.value}={self.units}, "
        s_repr += f"{AttributeNames.DENSITY.value}={self.density}, "
        s_repr += f"{AttributeNames.BASE_TYPE.value}={self.base_type}, "
        s_repr += f"{AttributeNames.AXIS.value}={self.axis})"
        return s_repr

    def to_dict(self):
        data = {}
        if self.sequence_id:
            data[AttributeNames.ID.value] = self.sequence_id
        if self.name:
            data[AttributeNames.NAME.value] = self.name
        data[AttributeNames.OFFSET.value] = self.offset
        data[AttributeNames.LENGTH.value] = self.length
        if self.units:
            data[AttributeNames.UNITS.value] = self.units
        if self.density:
            data[AttributeNames.DENSITY.value] = self.density.value
        data[AttributeNames.BASE_TYPE.value] = self.base_type.value
        if self.axis:
            data[AttributeNames.AXIS_INFO.value] = self.axis.to_dict()
        return data

    @staticmethod
    def from_dict(dct):
        return Sequence(
            sequence_id=dct[AttributeNames.ID.value],
            name=dct[AttributeNames.NAME.value],
            axis=SequenceAxis.from_dict(dct[AttributeNames.AXIS_INFO.value]),
            length=dct[AttributeNames.LENGTH.value],
            offset=dct[AttributeNames.OFFSET.value],
            units=dct[AttributeNames.UNITS.value],
            density=dct[AttributeNames.DENSITY.value],
            base_type=dct[AttributeNames.BASE_TYPE.value])
