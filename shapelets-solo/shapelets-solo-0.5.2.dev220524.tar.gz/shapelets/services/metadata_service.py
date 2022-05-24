# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import numpy as np
import pandas as pd
import typing

from shapelets.model import (
    Collection,
    Sequence,
    SequenceMetadata,
    MetadataCoordinates,
    MetadataItem,
    MetadataType,
)
from shapelets.services.base_service import BaseService
from shapelets.services.collections_service import Endpoint as CollectionsEndpoint


class MetadataService(BaseService):

    def get_metadata(self, collection: Collection) -> pd.DataFrame:
        response = self.request_get(
            CollectionsEndpoint.COLLECTION_METADATA.replace(collection.collection_id))
        metadata = _build_metadata_from_response(response)
        return _build_dataframe(metadata)

    def add_metadata(self,
                     collection: Collection,
                     sequence: Sequence,
                     metadata: SequenceMetadata) -> None:
        self.request_post(
            CollectionsEndpoint.COLLECTION_SEQUENCE_METADATA.replace(
                collection.collection_id, sequence.sequence_id),
            metadata.to_dict())

    def add_metadata_from_pandas(self,
                                 collection: Collection,
                                 sequences: typing.List[Sequence],
                                 data_frame: pd.DataFrame) -> None:
        data_frame = _remove_duplicates(data_frame)
        types = _infer_types(data_frame)
        metadata = _metadata_items_by_sequence(data_frame, types)
        for sequence_name, sequence_metadata in metadata.items():
            try:
                sequence = next(x for x in sequences if x.name == sequence_name)
            except StopIteration:
                print(
                    f"Sequence name {sequence_name} was not found on index column")
                continue
            self.add_metadata(collection, sequence, sequence_metadata)


def _get_metadata_type_from_object(value):
    metadata_type = None
    if isinstance(value, str):
        metadata_type = MetadataType.STRING
    elif isinstance(value, MetadataCoordinates):
        metadata_type = MetadataType.GEOHASH
    return metadata_type


def _get_metadata_type(typ, value):
    metadata_type = None
    if typ == float:
        metadata_type = MetadataType.DOUBLE
    elif np.issubdtype(typ, np.datetime64):
        metadata_type = MetadataType.TIMESTAMP
    elif typ == object:
        metadata_type = _get_metadata_type_from_object(value)
    return metadata_type


def _infer_types(data_frame: pd.DataFrame):
    df_types = dict(data_frame.dtypes)
    output = {}
    for name, typ in df_types.items():
        value = data_frame.iloc[0, data_frame.columns.get_loc(name)]
        metadata_type = _get_metadata_type(typ, value)
        if metadata_type is None:
            raise Exception(f"Non valid MetadataType in column '{name}'")
        output[name] = metadata_type
    return output


def _get_sequence_metadata_from_row(items: pd.Series,
                                    types: typing.Dict[str, MetadataType]) -> SequenceMetadata:
    return SequenceMetadata([
        MetadataItem(types[i_name], i_name, i_value) for i_name, i_value in items.iteritems()
    ])


def _metadata_items_by_sequence(data_frame: pd.DataFrame,
                                types: typing.Dict[str, MetadataType]) -> typing.Dict[str, SequenceMetadata]:
    rows = data_frame.iterrows()
    return {
        str(index): _get_sequence_metadata_from_row(row, types) for index, row in rows
    }


def _remove_duplicates(data_frame: pd.DataFrame) -> pd.DataFrame:
    return data_frame.loc[~data_frame.index.duplicated(keep='first')]


def _build_metadata_from_response(response: typing.Dict) -> typing.Dict[str, SequenceMetadata]:
    metadata_items = response['sequencesMetadata'].items()
    return {
        key: SequenceMetadata.from_dict(value) for key, value in metadata_items
    }


def _get_values(sequence_metadata: SequenceMetadata) -> typing.List:
    return [field.value for field in sequence_metadata.items]


def _build_dataframe(metadata_dict: typing.Dict[str, SequenceMetadata]) -> pd.DataFrame:
    # Empty dataframe if there is no sequence or there is no metadata field.
    if not metadata_dict or not next(metadata_dict.values().__iter__()).items:
        return pd.DataFrame()
    field_names = [value.name for value in next(metadata_dict.values().__iter__()).items]
    rows = {
        sequence: _get_values(s_metadata) for sequence, s_metadata in metadata_dict.items()
    }
    return pd.DataFrame.from_dict(rows, orient='index', columns=field_names)
