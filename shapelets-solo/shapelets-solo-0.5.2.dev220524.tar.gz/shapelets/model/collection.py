# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum


class CollectionType(Enum):
    GENERAL = 1
    ENERGY = 2
    HEALTH = 3
    FINANCE = 4

    @staticmethod
    def to_string(collection_type):
        if collection_type == CollectionType.GENERAL:
            return "GENERAL"
        if collection_type == CollectionType.ENERGY:
            return "ENERGY"
        if collection_type == CollectionType.HEALTH:
            return "HEALTH"
        if collection_type == CollectionType.FINANCE:
            return "FINANCE"
        raise ValueError(f"unrecognized type: {collection_type}")

    @staticmethod
    def from_string(collection_type):
        if collection_type == "GENERAL":
            return CollectionType.GENERAL
        if collection_type == "ENERGY":
            return CollectionType.ENERGY
        if collection_type == "HEALTH":
            return CollectionType.HEALTH
        if collection_type == "FINANCE":
            return CollectionType.FINANCE
        raise ValueError(f"unrecognized type: {collection_type}")


class AttributeNames(Enum):
    COLLECTION = "Collection"
    COLLECTION_ID = "collection_id"
    COLLECTION_TYPE = "collection_type"
    DESCRIPTION = "description"
    FAVORITE = "favorite"
    ID = "id"
    NAME = "name"
    NUM_SEQUENCES = "num_sequences"
    SEQUENCES = "sequences"
    TAGS = "tags"
    TYPE = "type"


class Collection:
    """
    This class is a data holder to represent Shapelets Collections.
    """

    def __init__(self,
                 collection_id,
                 name=None,
                 favorite=None,
                 description=None,
                 tags=None,
                 num_sequences=None,
                 collection_type=CollectionType.GENERAL):
        self.collection_id = collection_id
        self.name = name
        self.favorite = favorite
        self.description = description
        self.tags = tags
        self.num_sequences = num_sequences
        self.collection_type = collection_type

    def __repr__(self):
        s_repr = f"{AttributeNames.COLLECTION.value}({AttributeNames.COLLECTION_ID.value}={self.collection_id}, "
        s_repr += f"{AttributeNames.NAME.value}={self.name}, "
        s_repr += f"{AttributeNames.FAVORITE.value}={self.favorite}, "
        s_repr += f"{AttributeNames.DESCRIPTION.value}={self.description}, "
        s_repr += f"{AttributeNames.TAGS.value}={self.tags}, "
        s_repr += f"{AttributeNames.NUM_SEQUENCES.value}={self.num_sequences}, "
        s_repr += f"{AttributeNames.COLLECTION_TYPE.value}={self.collection_type})"
        return s_repr

    def to_dict(self):
        data = {}
        if self.collection_id is not None:
            data[AttributeNames.ID.value] = self.collection_id
        if self.name is not None:
            data[AttributeNames.NAME.value] = self.name
        if self.favorite is not None:
            data[AttributeNames.FAVORITE.value] = self.favorite
        if self.description is not None:
            data[AttributeNames.DESCRIPTION.value] = self.description
        if self.tags is not None:
            data[AttributeNames.TAGS.value] = self.tags
        if self.num_sequences is not None:
            data[AttributeNames.SEQUENCES.value] = self.num_sequences
        if self.collection_type is not None:
            data[AttributeNames.TYPE.value] = CollectionType.to_string(self.collection_type)
        return data

    @staticmethod
    def from_dict(dct):
        col_type = CollectionType.GENERAL
        if AttributeNames.TYPE.value in dct:
            col_type = CollectionType.from_string(dct[AttributeNames.TYPE.value])
        return Collection(
            dct[AttributeNames.ID.value] if AttributeNames.ID.value in dct else None,
            name=dct[AttributeNames.NAME.value] if AttributeNames.NAME.value in dct else None,
            favorite=dct[AttributeNames.FAVORITE.value] if AttributeNames.FAVORITE.value in dct else None,
            description=dct[AttributeNames.DESCRIPTION.value] if AttributeNames.DESCRIPTION.value in dct else None,
            tags=dct[AttributeNames.TAGS.value] if AttributeNames.TAGS.value in dct else None,
            num_sequences=dct[AttributeNames.SEQUENCES.value] if AttributeNames.SEQUENCES.value in dct else None,
            collection_type=col_type)
