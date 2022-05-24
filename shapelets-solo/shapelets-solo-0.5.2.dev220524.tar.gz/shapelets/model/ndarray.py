# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
import numpy as np
import typing


class AttributeNames(Enum):
    DESCRIPTION = "description"
    DIMS = 'dims'
    DTYPE = "dtype"
    ND_ARRAY = "NDArray"
    ND_ARRAY_ID = "ndarray_id"
    ND_ARRAY_ID_2 = "ndArrayId"
    NAME = "name"


class NDArray:
    """
    This class is a data holder to represent Shapelets NDArrays.
    """

    def __init__(self,
                 nd_array_id: str,
                 name: str,
                 description: str,
                 dtype: np.dtype,
                 dims: typing.Tuple[int, ...]):
        self.nd_array_id = nd_array_id
        self.name = name
        self.description = description
        self.dtype = dtype
        self.dims = dims

    def __hash__(self):
        return hash((self.nd_array_id,
                     self.name,
                     self.description,
                     self.dtype,
                     self.dims))

    def __eq__(self, other):
        return (isinstance(other, NDArray) and
                self.nd_array_id == other.nd_array_id and
                self.name == other.name and
                self.description == other.description and
                self.dtype == other.dtype and
                self.dims == other.dims)

    def __repr__(self):
        nd_repr = f"{AttributeNames.ND_ARRAY.value}({AttributeNames.ND_ARRAY_ID.value}={self.nd_array_id}, "
        nd_repr += f"{AttributeNames.NAME.value}={self.name}, "
        nd_repr += f"{AttributeNames.DESCRIPTION.value}={self.description}, "
        nd_repr += f"{AttributeNames.DTYPE.value}={self.dtype}, "
        nd_repr += f"{AttributeNames.DIMS.value}={self.dims})"
        return nd_repr

    def to_dict(self):
        data = dict()
        data[AttributeNames.ND_ARRAY_ID_2.value] = self.nd_array_id
        if self.name:
            data[AttributeNames.NAME.value] = self.name
        if self.description:
            data[AttributeNames.DESCRIPTION.value] = self.description
        data[AttributeNames.DTYPE.value] = str(self.dtype)
        data[AttributeNames.DIMS.value] = self.dims
        return data

    @staticmethod
    def from_dict(dct):
        return NDArray(
            nd_array_id=dct[AttributeNames.ND_ARRAY_ID_2.value],
            name=dct[AttributeNames.NAME.value],
            description=dct[AttributeNames.DESCRIPTION.value],
            dtype=np.dtype(dct[AttributeNames.DTYPE.value]),
            dims=tuple(dct[AttributeNames.DIMS.value]))
