# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

from enum import Enum
import typing
import numpy as np
import pandas as pd

from shapelets.model import (
    Collection,
    CollectionType,
    Sequence,
    Permission,
    Privilege,
    User,
    SequenceAxis,
    AxisTypeEnum
)
from shapelets.services.base_service import BaseService


def read_series_from_file(csv_file: str,
                          index_col: str,
                          sep: str = ",") -> typing.Tuple[typing.List[pd.DataFrame], int, int]:
    dataframe = pd.read_csv(filepath_or_buffer=csv_file, sep=sep, index_col=index_col, parse_dates=[index_col])
    dataframe = dataframe.loc[:, ~dataframe.columns.str.contains("^Unnamed")]
    dataframe.columns = [name.upper() for name in dataframe.columns]
    dataframe = dataframe.tz_localize(None)
    series_df = _fill_na(dataframe.loc[:, ~dataframe.columns.duplicated()])
    starts, every = extract_starts_and_every_from_index(series_df)
    series = [series_df[seq].to_frame() for seq in series_df]
    return series, starts, every


def extract_starts_and_every_from_index(dataframe: pd.DataFrame) -> typing.Tuple[int, int]:
    indices = dataframe.index.values
    # The timestamp is stored as nanoseconds from epoch. Get it as an int64 and convert it to ms
    starts = int(indices[0].astype('uint64') / 1e6)
    every = int((indices[1] - indices[0]).astype("timedelta64[ms]") / np.timedelta64(1, 'ms'))
    return starts, every


def create_axis(dataframe: pd.DataFrame,
                starts: np.datetime64 = None,
                every: int = None) -> SequenceAxis:
    index = dataframe.index
    if isinstance(index, pd.DatetimeIndex):
        starts, every = extract_starts_and_every_from_index(dataframe)
    else:
        if starts is None or every is None:
            raise Exception(
                "'starts' and 'every' are required when the " +
                "DataFrame's index is not a DatetimeIndex")
        starts = int(starts.astype('uint64'))
    return SequenceAxis(AxisTypeEnum.ORDINAL, starts, every)


class Endpoint(Enum):
    COLLECTIONS = "api/collections"
    CREATE_DEFAULT = f"{COLLECTIONS}/specificCollections"
    COLLECTION_TYPES = f"{COLLECTIONS}/types"
    COLLECTION_BY_ID = f"{COLLECTIONS}/###collection-id###"
    COLLECTION_METADATA = f"{COLLECTION_BY_ID}/metadataItems"
    COLLECTION_SEQUENCES = f"{COLLECTION_BY_ID}/sequences"
    COLLECTION_SEQUENCE_METADATA = f"{COLLECTION_SEQUENCES}/###sequence-id###/metadata"
    COLLECTION_PRIVILEGES = f"{COLLECTION_BY_ID}/privileges"
    COLLECTION_SHARING = f"{COLLECTION_BY_ID}/share"
    COLLECTION_SHARING_BY_ID = f"{COLLECTION_SHARING}/###subject-id###"
    COLLECTION_USER_SHARING = f"{COLLECTION_SHARING_BY_ID}/user"
    COLLECTION_GROUP_SHARING = f"{COLLECTION_SHARING_BY_ID}/group"

    def replace(self, collection_id: str, sequence_id: str = None) -> str:
        template = str(self.value)
        template = template.replace("###collection-id###", collection_id)
        if sequence_id is not None:
            template = template.replace("###sequence-id###", sequence_id)
        return template

    def replace_subject_id(self, collection_id: str, subject_id: str) -> str:
        return self.replace(collection_id).replace("###subject-id###", subject_id)


class CollectionsService(BaseService):

    def create_collection(self,
                          name: str,
                          description: str = None,
                          tags: typing.List[str] = None,
                          collection_type: CollectionType = CollectionType.GENERAL) -> Collection:
        return Collection.from_dict(
            self.request_post(
                Endpoint.COLLECTIONS.value,
                {
                    "name": name,
                    "description": description if description else "",
                    "tags": tags if tags else [],
                    "type": CollectionType.to_string(collection_type),
                    "picture": ""
                }
            ))

    def create_default_collections(self, collection_name: str) -> None:
        self.request_post(Endpoint.CREATE_DEFAULT.value, {"type": collection_name})

    def get_collections(self) -> typing.List[Collection]:
        collections_json = self.request_get(Endpoint.COLLECTIONS.value)
        collections = []
        for collection in collections_json:
            collections.append(Collection.from_dict(collection))
        return collections

    def get_collection(self, collection_id: str) -> Collection:
        collection_json = self.request_get(Endpoint.COLLECTION_BY_ID.replace(collection_id))
        return Collection.from_dict(collection_json)

    def update_collection(self,
                          collection: Collection,
                          name: str = None,
                          favorite: bool = None,
                          description: str = None,
                          tags: str = None,
                          collection_type: CollectionType = None) -> Collection:
        # Only include non None fields.
        data = {}
        if name is not None:
            data["name"] = name
        if favorite is not None:
            data["favorite"] = favorite
        if description is not None:
            data["description"] = description
        if tags is not None:
            data["tags"] = tags
        if collection_type is not None:
            data["type"] = collection_type
        return Collection.from_dict(
            self.request_put(
                Endpoint.COLLECTION_BY_ID.replace(collection.collection_id),
                data))

    def delete_collection(self, collection: Collection) -> bool:
        return self.request_delete(Endpoint.COLLECTION_BY_ID.replace(collection.collection_id))

    def get_collection_sequences(self, collection: Collection) -> typing.List[Sequence]:
        collection_id = collection.collection_id
        sequences_json = self.request_get(Endpoint.COLLECTION_SEQUENCES.replace(collection_id))
        sequences = []
        for sequence in sequences_json:
            sequences.append(Sequence.from_dict(sequence))
        return sequences

    def get_collection_types(self):
        return self.request_get(Endpoint.COLLECTION_TYPES.value)["types"]

    def share_collection(self,
                         collection: Collection,
                         subject: typing.Any,
                         grant: Permission) -> None:
        collection_id = collection.collection_id
        subject_id = subject.uid
        self.request_post(
            Endpoint.COLLECTION_SHARING_BY_ID.replace_subject_id(collection_id, subject_id),
            {
                "isUser": isinstance(subject, User),
                "privilege": Permission.to_string(grant)
            })

    def unshare_collection(self, collection: Collection, subject: typing.Any) -> None:
        if isinstance(subject, User):
            endpoint = Endpoint.COLLECTION_USER_SHARING
        else:
            endpoint = Endpoint.COLLECTION_GROUP_SHARING
        collection_id = collection.collection_id
        subject_id = subject.uid
        self.request_delete(endpoint.replace_subject_id(collection_id, subject_id))

    def get_collection_sharing(self, collection: Collection) -> typing.List[Privilege]:
        collection_id = collection.collection_id
        privileges_json = self.request_get(Endpoint.COLLECTION_SHARING.replace(collection_id))
        privileges = []
        for privilege in privileges_json:
            privileges.append(Privilege.from_dict(privilege))
        return privileges

    def get_collection_privileges(self, collection: Collection) -> typing.List[Privilege]:
        collection_id = collection.collection_id
        privileges_json = self.request_get(Endpoint.COLLECTION_PRIVILEGES.replace(collection_id))
        privileges = []
        for privilege in privileges_json:
            privileges.append(Privilege.from_dict(privilege))
        return privileges


def _fill_na(dataframe: pd.DataFrame) -> pd.DataFrame:
    fwd_fill = dataframe.fillna(method="ffill")
    bck_fill = fwd_fill.fillna(method="bfill")
    return bck_fill.fillna(0)
