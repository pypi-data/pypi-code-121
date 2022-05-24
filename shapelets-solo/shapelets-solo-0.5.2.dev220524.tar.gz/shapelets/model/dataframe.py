# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
from typing import Tuple, List


class AttributeNames(Enum):
    COL_NAMES = "colNames"
    COL_TYPES = "colTypes"
    DATAFRAME = "Dataframe"
    DATAFRAME_ID = "dataframe_id"
    DATAFRAME_ID_2 = "dataframeId"
    DESCRIPTION = "description"
    HAS_INDEX = "hasIndex"
    INDEX_TYPE = "indexType"
    NAME = "name"
    N_COLS = "nCols"
    N_ROWS = "nRows"


class Dataframe:
    """
    This class is a data holder to represent Shapelets Dataframe.
    """

    def __init__(self,
                 dataframe_id: str,
                 n_cols: int,
                 n_rows: int,
                 col_names: List[str],
                 col_types: List[str],
                 has_index: bool,
                 index_type: str,
                 name: str = None,
                 description: str = None):
        self.dataframe_id = dataframe_id
        self.name = name
        self.description = description
        self.n_cols = n_cols
        self.n_rows = n_rows
        self.col_names = col_names
        self.col_types = col_types
        self.has_index = has_index
        self.index_type = index_type

    def __hash__(self):
        return hash((self.dataframe_id,
                     self.name,
                     self.description,
                     self.n_cols,
                     self.n_rows,
                     tuple(self.col_names),
                     tuple(self.col_types),
                     self.has_index,
                     self.index_type))

    def __eq__(self, other):
        return (isinstance(other, Dataframe) and
                self.dataframe_id == other.dataframe_id and
                self.name == other.name and
                self.description == other.description and
                self.n_cols == other.n_cols and
                self.n_rows == other.n_rows and
                self.col_names == other.col_names and
                self.col_types == other.col_types and
                self.has_index == other.has_index and
                self.index_type == other.index_type)

    def __repr__(self):
        dataframe_repr = f"{AttributeNames.DATAFRAME.value}({AttributeNames.DATAFRAME_ID.value}={self.dataframe_id}, "
        dataframe_repr += f"{AttributeNames.NAME.value}={self.name}, "
        dataframe_repr += f"{AttributeNames.DESCRIPTION.value}={self.description}, "
        dataframe_repr += f"{AttributeNames.N_COLS.value}={self.n_cols}, "
        dataframe_repr += f"{AttributeNames.N_ROWS.value}={self.n_rows},)"
        dataframe_repr += f"{AttributeNames.COL_NAMES.value}={self.col_names},)"
        dataframe_repr += f"{AttributeNames.COL_TYPES.value}={self.col_types},)"
        dataframe_repr += f"{AttributeNames.HAS_INDEX.value}={self.has_index},)"
        dataframe_repr += f"{AttributeNames.INDEX_TYPE.value}={self.index_type})"
        return dataframe_repr

    def to_dict(self):
        data = dict()
        data[AttributeNames.DATAFRAME_ID_2.value] = {"id": self.dataframe_id}
        data[AttributeNames.NAME.value] = self.name
        data[AttributeNames.DESCRIPTION.value] = self.description
        data[AttributeNames.N_COLS.value] = self.n_cols
        data[AttributeNames.N_ROWS.value] = self.n_rows
        data[AttributeNames.COL_NAMES.value] = self.col_names
        data[AttributeNames.COL_TYPES.value] = self.col_types
        data[AttributeNames.HAS_INDEX.value] = self.has_index
        data[AttributeNames.INDEX_TYPE.value] = self.index_type
        return data

    @staticmethod
    def from_dict(dct):
        return Dataframe(
            dataframe_id=dct[AttributeNames.DATAFRAME_ID_2.value],
            name=dct[AttributeNames.NAME.value],
            description=dct[AttributeNames.DESCRIPTION.value],
            n_cols=dct[AttributeNames.N_COLS.value],
            n_rows=dct[AttributeNames.N_ROWS.value],
            col_names=list(dct[AttributeNames.COL_NAMES.value]),
            col_types=list(dct[AttributeNames.COL_TYPES.value]),
            has_index=dct[AttributeNames.HAS_INDEX.value],
            index_type=dct[AttributeNames.INDEX_TYPE.value])
