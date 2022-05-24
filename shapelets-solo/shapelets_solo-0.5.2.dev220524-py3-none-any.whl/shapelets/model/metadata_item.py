# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
import numpy as np
import pandas as pd
import pygeohash as pgh
import typing


class MetadataType(Enum):
    STRING = "STRING"
    DOUBLE = "DOUBLE"
    TIMESTAMP = "TIMESTAMP"
    BOOLEAN = "BOOLEAN"
    GEOHASH = "COORDINATES"


class AttributeNames(Enum):
    BOOLEAN = 'boolean'
    GEOHASH = 'coordinates'
    DOUBLE = 'double'
    EXCEPTION = "Metadata type not supported"
    ITEMS = "items"
    LAT = "Lat"
    LONG = "Long"
    METADATA_ITEM = 'MetadataItem'
    NAME = "name"
    STRING = 'string'
    TIMESTAMP = 'timestamp'
    TYPE = "type"
    VALUE = 'value'


class MetadataCoordinates:
    def __init__(self, latitude: float, longitude: float):
        self.lat = latitude
        self.lon = longitude

    def __repr__(self):
        return f"{AttributeNames.LAT.value}:{self.lat}; {AttributeNames.LONG.value}:{self.lon}"

    def __hash__(self):
        return hash((self.lat, self.lon))

    def __eq__(self, other):
        return (isinstance(other, MetadataCoordinates) and
                self.lat == other.lat and
                self.lon == other.lon)


ValueOutTypeVar = typing.TypeVar(
    'T', str, float, bool, np.datetime64, MetadataCoordinates)


class MetadataItem:
    def __init__(self, metadata_type: MetadataType, name: str, value: ValueOutTypeVar):
        self.metadata_type = metadata_type
        self.name = name
        self.value = value

    def __repr__(self):
        s_repr = f"{AttributeNames.METADATA_ITEM.value}{{{AttributeNames.TYPE.value}:{self.metadata_type.value}, "
        s_repr += f"{AttributeNames.NAME.value}:'{self.name}', "
        s_repr += f"{AttributeNames.VALUE.value}:'{self.value}'}}"
        return s_repr

    def to_dict(self) -> dict:
        return {
            AttributeNames.NAME.value: self.name,
            AttributeNames.VALUE.value: MetadataItem.adapt_value_out(self.metadata_type, self.value)
        }

    @staticmethod
    def from_dict(dct):
        metadata_name = dct[AttributeNames.NAME.value]
        metadata_type = MetadataType(dct[AttributeNames.VALUE.value][AttributeNames.TYPE.value])
        return MetadataItem(
            metadata_type=metadata_type,
            name=metadata_name,
            value=MetadataItem.adapt_value_in(metadata_type, dct[AttributeNames.VALUE.value])
        )

    @staticmethod
    def adapt_value_out(metadata_type: MetadataType, value: ValueOutTypeVar) -> dict:
        ret = {
            AttributeNames.TYPE.value: metadata_type.value
        }
        if metadata_type == MetadataType.GEOHASH:
            ret[AttributeNames.GEOHASH.value] = pgh.encode(value.lat, value.lon)
        elif metadata_type == MetadataType.TIMESTAMP:
            if value is pd.NaT:
                timestamp_value = 0
            elif isinstance(value, pd.Timestamp):
                timestamp_value = int(value.timestamp() * 1e3)
            else:
                timestamp_value = int(value.astype("datetime64[ms]").astype("uint64"))
            ret[AttributeNames.TIMESTAMP.value] = timestamp_value
        elif metadata_type == MetadataType.BOOLEAN:
            ret[AttributeNames.BOOLEAN.value] = value
        elif metadata_type == MetadataType.DOUBLE:
            ret[AttributeNames.DOUBLE.value] = value
        elif metadata_type == MetadataType.STRING:
            ret[AttributeNames.STRING.value] = value
        else:
            raise ValueError(AttributeNames.EXCEPTION.value)
        return ret

    @staticmethod
    def adapt_value_in(metadata_type: MetadataType,
                       value: typing.TypeVar('T_out', str, int)) -> ValueOutTypeVar:
        if metadata_type == MetadataType.GEOHASH:
            coords = pgh.decode(value[AttributeNames.GEOHASH.value])
            return MetadataCoordinates(coords[0], coords[1])
        if metadata_type == MetadataType.TIMESTAMP:
            return np.datetime64(value["timestamp"], "ms")
        if metadata_type == MetadataType.STRING:
            return value[AttributeNames.STRING.value]
        if metadata_type == MetadataType.DOUBLE:
            return value[AttributeNames.DOUBLE.value]
        if metadata_type == MetadataType.BOOLEAN:
            return value[AttributeNames.BOOLEAN.value]
        raise ValueError(AttributeNames.EXCEPTION.value)


class SequenceMetadata:
    def __init__(self, items: typing.Optional[typing.List[MetadataItem]] = None):
        if items is None:
            items = []
        self.items = items

    def to_dict(self) -> dict:
        return {AttributeNames.ITEMS.value: [item.to_dict() for item in self.items]}

    @staticmethod
    def from_dict(dct):
        items_dict = dct[AttributeNames.ITEMS.value]
        items = [MetadataItem.from_dict(item_dict) for item_dict in items_dict]
        return SequenceMetadata(items=items)
