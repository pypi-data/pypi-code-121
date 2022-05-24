# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum


class AxisTypeEnum(Enum):
    ORDINAL = "ORDINAL"
    TIME = "TIME"
    NUMERICAL = "NUMERICAL"
    IRREGULAR = "IRREGULAR"


FROM_BACKEND_MAPPING = {
    "io.shapelets.model.density.RegularOrdinalAxis": AxisTypeEnum.ORDINAL,
    "io.shapelets.model.density.RegularTimeAxis": AxisTypeEnum.TIME,
    "io.shapelets.model.density.RegularNumericalAxis": AxisTypeEnum.NUMERICAL,
    "io.shapelets.model.density.IrregularNumericalAxis": AxisTypeEnum.IRREGULAR
}


class AttributeNames(Enum):
    EVERY = "every"
    SEQUENCE_AXIS = "SequeceAxis"
    STARTS = "starts"
    TYPE = "type"


class SequenceAxis:
    def __init__(self, axis_type: AxisTypeEnum, starts: int, every: int):
        self.type = axis_type
        self.starts = starts
        self.every = every

    def __hash__(self):
        return hash((self.type, self.starts, self.every))

    def __eq__(self, other):
        return (isinstance(other, SequenceAxis) and
                self.type == other.type and
                self.starts == other.starts and
                self.every == other.every)

    def to_dict(self):
        return {
            AttributeNames.TYPE.value: self.type.value,
            AttributeNames.STARTS.value: self.starts,
            AttributeNames.EVERY.value: self.every
        }

    @staticmethod
    def from_dict(dct):
        a_type = AxisTypeEnum.NUMERICAL
        if dct.get(AttributeNames.TYPE.value):
            t_from_dict = dct[AttributeNames.TYPE.value]
            a_type = FROM_BACKEND_MAPPING.get(t_from_dict)
            if t_from_dict and not a_type:
                a_type = AxisTypeEnum[t_from_dict]
        return SequenceAxis(
            axis_type=a_type,
            starts=dct[AttributeNames.STARTS.value],
            every=dct[AttributeNames.EVERY.value])

    def __repr__(self):
        s_repr = f"{AttributeNames.SEQUENCE_AXIS.value}{{{AttributeNames.TYPE.value}:{self.type}, "
        s_repr += f"{AttributeNames.STARTS.value}:{self.starts}, "
        s_repr += f"{AttributeNames.EVERY.value}:{self.every}}}"
        return s_repr
