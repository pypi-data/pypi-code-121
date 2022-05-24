# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
import typing


class AttributeNames(Enum):
    DATA = "data"
    DESCRIPTION = "description"
    DIMS = 'dims'
    ID = "id"
    METADATA = "metadata"
    MODEL = "model"
    MODEL_ID = "model_id"
    MODEL_ID_2 = "modelId"
    NAME = "name"


class Model:
    """
    This class is a data holder to represent Models.
    """

    def __init__(self,
                 model_id: str,
                 name: str,
                 description: str,
                 data: str,
                 metadata: typing.Dict[str, str]):
        self.model_id = model_id
        self.name = name
        self.description = description
        self.data = data
        self.metadata = metadata

    def add_data(self, data: str):
        self.data = data

    def __hash__(self):
        return hash((self.model_id,
                     self.name,
                     self.description,
                     self.data,
                     str(self.metadata)))

    def __eq__(self, other):
        return (isinstance(other, Model) and
                self.model_id == other.model_id and
                self.name == other.name and
                self.description == other.description and
                self.data == other.data and
                self.metadata == other.metadata)

    def __repr__(self):
        model_repr = f"{AttributeNames.MODEL.value}({AttributeNames.MODEL_ID.value}={self.model_id}, "
        model_repr += f"{AttributeNames.NAME.value}={self.name}, "
        model_repr += f"{AttributeNames.DESCRIPTION.value}={self.description}, "
        model_repr += f"{AttributeNames.DATA.value}={self.data}, "
        model_repr += f"{AttributeNames.METADATA.value}={self.metadata} "
        return model_repr

    def to_dict(self):
        data = dict()
        data[AttributeNames.MODEL_ID_2.value] = {"id": self.model_id}
        if self.name:
            data[AttributeNames.NAME.value] = self.name
        if self.description:
            data[AttributeNames.DESCRIPTION.value] = self.description
        data[AttributeNames.DATA.value] = self.data
        if self.metadata:
            data[AttributeNames.METADATA.value] = self.metadata
        return data

    @staticmethod
    def from_dict(dct):
        return Model(
            model_id=dct[AttributeNames.MODEL_ID_2.value]["id"],
            name=dct[AttributeNames.NAME.value],
            description=dct[AttributeNames.DESCRIPTION.value],
            data=dct[AttributeNames.DATA.value],
            metadata=dct[AttributeNames.METADATA.value])
