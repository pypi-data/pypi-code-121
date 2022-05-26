import io, os
from typing import Optional, Union, List
from datetime import datetime

import numpy as np
from dataclasses import dataclass

from ..constants import AssetsConstants
from ..custom_exceptions import EmbeddingError
from ..models.annotation import Annotation
from ..tools.misc import get_md5_from_json_object, hash_string_into_positive_integer_reproducible, get_md5_from_string, get_guid
from ..tools.naming import get_similarity_index_name, standardize_name, assert_standardized, convert_booleans_to_string


@dataclass(frozen=False)
class UnstructuredInputAsset:
    id: Optional[str] = None
    path: Optional[str] = None
    url: Optional[str] = None
    uri: Optional[str] = None
    bytes: Optional[Union[io.BytesIO, bytes, str]] = None
    sensor: Optional[str] = None
    timestamp: Optional[Union[str, datetime]] = None
    session_uid: Optional[str] = None
    aux_metadata: Optional[dict] = None

    def __post_init__(self):
        # Validate inputs
        assert sum(x is not None for x in [self.path, self.url, self.uri, self.bytes]) == 1, \
            "One and only one of [path, url, uri, bytes] should be specified"

        if self.id is None:
            if self.bytes:
                self.id = get_guid()
            else:
                self.id = get_md5_from_string(self.path or self.url or self.uri)
        else:
            self.id = standardize_name(self.id)

        assert isinstance(self.id, str), "asset id should be a string"

        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

        if self.path:
            assert os.path.exists(self.path), f"path {self.path} does not exist"

        if self.aux_metadata:
            self.aux_metadata = convert_booleans_to_string(self.aux_metadata)

@dataclass
class Image(UnstructuredInputAsset):
    annotations: Optional[List[Annotation]] = None

    def __post_init__(self):
        super(Image, self).__post_init__()
        if self.annotations:
            for annotation in self.annotations:
                assert annotation.media_type == AssetsConstants.IMAGES_ASSET_ID

@dataclass
class Video(UnstructuredInputAsset):
    annotations: Optional[List[Annotation]] = None
    tags: Optional[List[str]] = None
    start_timestamp: Optional[Union[str, datetime]] = None

    def __post_init__(self):
        super(Video, self).__post_init__()
        if self.annotations:
            for annotation in self.annotations:
                assert annotation.media_type == AssetsConstants.VIDEOS_ASSET_ID
        if not self.start_timestamp:
            self.start_timestamp = self.timestamp

@dataclass
class Lidar(UnstructuredInputAsset):
    format: Optional[str] = None
    binary_format: Optional[str] = None
    related_images: Optional[List[str]] = None
    num_fields: Optional[int] = None

    def __post_init__(self):
        super(Lidar, self).__post_init__()

        if not self.format:
            self.format = "pcd"
        if self.format == "numpy":
            assert self.num_fields, "num_fields is needed for numpy data"
        elif self.format == "binary":
            assert self.binary_format, "binary_format is needed for binary data"
        else:
            assert self.format == "pcd", "format should be pcd, numpy, or binary"

        if self.related_images:
            self.related_images = [standardize_name(_) for _ in self.related_images]


class Embedding(object):
    def __init__(self,
                 data: Union[io.BytesIO, bytes, np.array, List[Union[float, int]]],
                 asset_id: str,
                 asset_type: str = AssetsConstants.IMAGES_ASSET_ID,
                 model: str = "default",
                 version: str = "v1",
                 timestamp: Optional[Union[str, datetime]] = None,
                 layer: Optional[Union[int, str]] = None,
                 dtype: Optional[Union[type(np.float32), type(np.float64), type(float)]] = np.float32,
                 ndim: Optional[int] = None,
                 session_uid: Optional[str] = None
                 ):
        """Create an Embedding.

            Parameters
            ----------
            data:
                Embeddings data.
            model:
                The name of the embeddings model.  Helps to differentiate from other models.
            version:
                The version of the embeddings model.  Helps to differentiate several versions of the same model.
            asset_id:
                The asset ID associated with the embedding passed in `data`. Must refer to an asset ID available on
                SceneBox.
            asset_type:
                The type of the asset referred to in `asset_id`.  Currently, only images and objects are supported.
            timestamp:
                timestamp of the embeddings. if not provided, ingestion timestamp is used.
            layer:
                Layer associated with the embedding.
            dtype:
                The datatype of the embedding.  Helps to cast data.  If not listed, assumed to be `np.float32`.
            ndim:
                Number of dimensions in `data`.  Helps to assert that the dimension calculated by
                the platform is correct.  Raises an error of the calculated dimensions does not match this field.
            session_uid:
                The unique identifier of the session that the asset with asset_id belongs to.
        """

        if isinstance(data, io.BytesIO) or isinstance(data, bytes):
            # Enforce a cast to float32
            embedding_array = np.float32(np.frombuffer(data, dtype=dtype))
        elif isinstance(data, np.ndarray):
            embedding_array = np.float32(data)
        elif isinstance(data, list) and all([isinstance(datum, float) or isinstance(datum, int)
                                                   for datum in data]):
            embedding_array = np.float32(np.array(data))
        else:
            raise NotImplementedError("Supported data types are io.BytesIO, bytes, np.array, List[float]")

        if embedding_array.size <= 0:
            raise EmbeddingError("no embedding bytes were detected")

        self.ndim = embedding_array.reshape(1, -1).shape[1]
        if self.ndim <= 0:
            raise EmbeddingError("dimension of the embedding = {}. Must be a positive integer".format(self.ndim))

        if not asset_id:
            raise ValueError("cannot create an embedding without an asset id")

        if ndim and self.ndim != ndim:
            raise EmbeddingError("ndim passed {} does not match the ndim in data {}".format(ndim, self.ndim))

        self.bytes = embedding_array.tobytes()
        self.timestamp = timestamp or datetime.utcnow()
        assert_standardized(asset_id)  # remove in the future
        self.asset_id = standardize_name(asset_id)
        self.asset_type = asset_type
        self.model = model
        self.version = version
        self.layer = layer

        json_object_for_embedding_id = {
            'model': self.model,
            'version': self.version,
            'asset_id': self.asset_id,
            'ndim': self.ndim,
            'layer': self.layer}

        embeddings_hash = get_md5_from_json_object(json_object=json_object_for_embedding_id)
        self.id = str(hash_string_into_positive_integer_reproducible(embeddings_hash))
        self.metadata = {
                'id': self.id,
                'timestamp': self.timestamp,
                'tags': [self.layer] if self.layer else [],
                'media_type': self.asset_type,
                'asset_id': self.asset_id,
                'model': self.model,
                'version': self.version,
                'ndim': self.ndim,
                'index_name': get_similarity_index_name(
                    media_type=self.asset_type,
                    model=self.model,
                    version=self.version)}
        if session_uid:
            self.metadata["session_uid"] = session_uid
