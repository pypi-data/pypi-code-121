from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import requests
from typing import List, Optional, NamedTuple, Union

from ..constants import AUXILIARY_KEY, EntityNames, EntityTypes, EntityInfluenceTypes, AssetsConstants
from ..custom_exceptions import InvalidArgumentsError
from ..models.assets import UnstructuredInputAsset, Lidar, Image, Video
from ..models.object_access import ObjectAccess
from ..tools.asset_utils import get_asset_attributes_filename
from ..tools.misc import chunk_list, run_threaded, get_guid
from ..tools.time_utils import datetime_or_str_to_iso_utc, str_or_datetime_to_datetime


class BulkAssetUploader(ABC):
    '''
    Preprocesses and indexes assets in bulk
    '''
    CHUNK_SIZE = 100

    def __init__(self, sec, asset_type: str, has_annotations: bool, index_annotations: bool):
        self.sec = sec
        self.asset_type = asset_type
        self.amc = self.sec.get_asset_manager(asset_type=self.asset_type)
        self.has_annotations = has_annotations
        self.index_annotations = index_annotations

    @abstractmethod
    def create_metadata(self, asset: UnstructuredInputAsset, asset_attributes: NamedTuple,
                        timestamp: Optional[Union[str, datetime]], sets: List[str]) -> dict:
        '''
        Creates asset metadata
        '''
        pass

    @abstractmethod
    def create_entity_dict(self, asset: UnstructuredInputAsset, enrichments: Optional[List[str]], asset_metadata: dict,
                           filename: Optional[str] = None) -> dict:
        '''
        Creates entity dictionary for session
        '''
        pass

    @abstractmethod
    def post_index_processing(self, ids: List[str]):
        '''
        Executes post-processing (if any) after indexing assets
        '''
        pass

    def get_content_type(self, asset_attributes: NamedTuple, asset: UnstructuredInputAsset):
        '''
        get asset content type based on attributes
        '''
        return None

    def preprocess_and_upload_bulk(self,
                                   assets: List[UnstructuredInputAsset],
                                   set_id: str,
                                   add_to_session: bool,
                                   enrichments: Optional[List[str]],
                                   **kwargs) -> List[str]:
        '''

        Args:
            assets: list of UnstructuredInputAsset (Image, Video or Lidar)
            set_id: The set (str) or sets (List[str]) to add the assets to.
            add_to_session: If True and session_uid is not None, add to the existing session with the passed session_uid.
            enrichments: The types of enrichments to add to the asset.
            **kwargs: any extra arguments

        Returns:
             List[str]
               List of ids of the added assets.
        '''

        assets_list_chunked = chunk_list(assets, chunk_size=self.CHUNK_SIZE)

        sets = []
        assert set_id, f"`set_id` is None. {self.asset_type} need to be associated with a set. Please specify `set_id`!"
        if isinstance(set_id, str):
            sets = [set_id]
        elif isinstance(set_id, list):
            sets = set_id

        # for assets_chunk in assets_list_chunked:
        chunk_id_added_asset_ids_map = {}

        def process_asset_chunk_add(iterable):

            assets_chunk, chunk_id = iterable
            chunk_length = len(assets_chunk)
            asset_ids = []
            uri_object_access_list = []

            # Process asset object information to lists
            asset_source_types = set()
            asset_sources = []
            for asset in assets_chunk:
                asset_ids.append(asset.id)
                if asset.path is not None:
                    asset_sources.append(asset.path)
                    source_type = "path"
                    asset_source_types.add(source_type)
                if asset.url is not None:
                    asset_sources.append(asset.url)
                    source_type = "url"
                    asset_source_types.add(source_type)
                if asset.uri is not None:
                    asset_sources.append(asset.uri)
                    source_type = "uri"
                    asset_source_types.add(source_type)
                    uri_object_access_list.append(ObjectAccess(uri=asset.uri).to_dic())
                if asset.bytes is not None:
                    asset_sources.append(asset.bytes)
                    source_type = "bytes"
                    asset_source_types.add(source_type)

            # Ensure all assets have only one of these available
            if len(asset_source_types) != 1 or len(asset_sources) != chunk_length:
                raise InvalidArgumentsError(
                    "Exactly one of path, url, uri, or bytes "
                    "should be specified for all assets")

            # for uris get object access in batch
            id_url_map = {}
            if uri_object_access_list:
                url = self.amc.get_assets_url("url_from_object_access_in_batch/")
                params = self.amc.add_asset_manager_params()
                resp = requests.post(url, params=params, json={"ids": asset_ids,
                                                               "object_accesses": uri_object_access_list})
                id_url_map = resp.json()

            asset_id_filenames_map = {}
            asset_id_metadata_map = {}
            asset_id_content_type_map = {}
            asset_id_entity_map = {}
            asset_id_annotations_map = {}

            def process_asset_metadata(iterable):
                asset, asset_source = iterable
                asset_attributes, filename = get_asset_attributes_filename(asset_type=self.asset_type,
                                                                           asset_source=asset_source,
                                                                           source_type=source_type,
                                                                           id=asset.id,
                                                                           url=id_url_map.get(
                                                                               asset.id))

                if asset.timestamp is None:
                    timestamp = datetime.utcnow()
                else:
                    timestamp = datetime_or_str_to_iso_utc(asset.timestamp)

                # build asset metadata and entity dict (if applicable) based on asset type
                asset_metadata = self.create_metadata(asset, asset_attributes, timestamp, sets)

                # If session_uid does not exist skip creating and pushing the entity
                if asset.session_uid and add_to_session:
                    entity_dict = self.create_entity_dict(asset, enrichments, asset_metadata, filename)
                    asset_id_entity_map[asset.id] = entity_dict

                if asset.session_uid is not None:
                    asset_metadata["session_uid"] = asset.session_uid

                if self.has_annotations and asset.annotations:
                    asset_metadata["annotations"] = [_.id for _ in asset.annotations]
                    asset_metadata["annotations_meta"] = [
                        {
                            "provider": _.provider,
                            "id": _.id,
                            "version": _.version,
                            "type": _.annotation_type
                        } for _ in asset.annotations]
                    labels = set()

                    for annotation in asset.annotations:
                        if self.index_annotations:
                            annotation.timestamp = timestamp
                            annotation.sensor = asset.sensor
                            annotation.session_uid = asset.session_uid

                        for ae in annotation.annotation_entities:
                            if kwargs.get("add_provider_to_labels"):
                                labels.add("{}_{}".format(ae.label, annotation.provider))
                            else:
                                labels.add(ae.label)

                    # Collect annotations
                    if self.index_annotations:
                        asset_id_annotations_map[asset.id] = asset.annotations

                    labels = list(labels)

                    if asset.aux_metadata:
                        asset.aux_metadata["labels"] = labels
                    else:
                        asset.aux_metadata = {"labels": labels}

                if asset.aux_metadata:
                    asset_metadata[AUXILIARY_KEY] = asset.aux_metadata

                content_type = self.get_content_type(asset_attributes, asset)
                if content_type:
                    asset_id_content_type_map[asset.id] = content_type

                asset_id_filenames_map[asset.id] = filename
                asset_id_metadata_map[asset.id] = asset_metadata

            run_threaded(func=process_asset_metadata,
                         iterable=zip(assets_chunk, asset_sources),
                         desc="processing asset attributes",
                         num_threads=10,
                         disable_threading=False,
                         disable_tqdm=True)

            asset_content_types_list = []
            asset_metadata_list = []
            asset_filenames_list = []

            for asset in assets_chunk:
                asset_filenames_list.append(asset_id_filenames_map[asset.id])
                asset_metadata_list.append(asset_id_metadata_map[asset.id])
                if asset_id_content_type_map:
                    asset_content_types_list.append(asset_id_content_type_map[asset.id])

            ids = self.amc.put_assets_batch(
                metadata=asset_metadata_list,
                filenames=asset_filenames_list,
                file_paths=asset_sources if source_type == "path" else None,
                urls=asset_sources if source_type == "url" else None,
                ids=asset_ids,
                uris=asset_sources if source_type == "uri" else None,
                geo_field=kwargs.get("geo_field"),
                shape_group_field=kwargs.get("shape_group_field"),
                wait_for_completion=True,
                content_type=asset_content_types_list or None,
                threading=True,
                disable_tqdm=True,
                add_to_redis_cache=kwargs.get("add_to_cache"))

            if add_to_session and asset_id_entity_map:
                self.sec.add_entities(entity_dicts=list(asset_id_entity_map.values()))

            self.post_index_processing(ids=ids)

            if self.index_annotations and asset_id_annotations_map:
                self.sec.add_annotations(
                    annotations=list(asset_id_annotations_map.values()),
                    update_asset=False,
                    threading=False,
                    disable_tqdm=True)

            chunk_id_added_asset_ids_map[chunk_id] = ids

        run_threaded(func=process_asset_chunk_add,
                     iterable=zip(assets_list_chunked, range(len(assets_list_chunked))),
                     desc="ingesting {} {} in {} chunks".format(len(assets), self.asset_type, len(assets_list_chunked)),
                     num_threads=self.sec.num_threads,
                     disable_threading=False,
                     disable_tqdm=False,
                     unit=f" {self.CHUNK_SIZE} {self.asset_type}"
                     )

        added_asset_ids = []
        for chunk_id in range(len(assets_list_chunked)):
            added_asset_ids.extend(chunk_id_added_asset_ids_map[chunk_id])

        return added_asset_ids


class BulkImageUploader(BulkAssetUploader):

    def __init__(self, sec, preprocesses: Optional[List[str]] = None,
                 thumbnailize_at_ingest: bool = False):
        super().__init__(sec=sec, asset_type=AssetsConstants.IMAGES_ASSET_ID, has_annotations=True, index_annotations=True)
        self.preprocesses = preprocesses
        self.thumbnailize_at_ingest = thumbnailize_at_ingest

    def create_metadata(self, asset: Image, asset_attributes: NamedTuple,
                        timestamp: Optional[Union[str, datetime]], sets: List[str]) -> dict:
        return {
            "width": asset_attributes.width,
            "height": asset_attributes.height,
            "format": asset_attributes.format,
            "sensor": asset.sensor,
            "timestamp": timestamp,
            "sets": sets,
            "preprocesses": self.preprocesses or [],
        }

    def create_entity_dict(self, asset: Image, enrichments: Optional[List[str]], asset_metadata: dict,
                           filename: Optional[str] = None) -> dict:
        return {
            "session": asset.session_uid,
            "timestamp": asset_metadata["timestamp"],
            "enrichments": enrichments or [],
            "entity_name": EntityNames.IMAGE,
            "media_asset_id": asset.id,
            "entity_value": asset.id,
            "entity_id": get_guid(),
            "entity_type": EntityTypes.MEDIA,
            "influence": EntityInfluenceTypes.INTERVAL
        }

    def get_content_type(self, asset_attributes: NamedTuple, asset: UnstructuredInputAsset):
        content_type = None
        if asset.bytes:
            if "png" in asset_attributes.format.lower():
                content_type = "image/png"
            elif "jpg" in asset_attributes.format.lower() or "jpeg" in asset_attributes.format.lower():
                content_type = "image/jpeg"
            else:
                content_type = None
        return content_type

    def post_index_processing(self, ids: List[str]):
        if self.thumbnailize_at_ingest:
            for preset in ["small", "tiny", "full_size_png"]:
                self.sec.compress_images(ids=ids, use_preset=preset)


class BulkVideoUploader(BulkAssetUploader):

    def __init__(self, sec, compress_videos: bool = False):
        super().__init__(sec=sec, asset_type=AssetsConstants.VIDEOS_ASSET_ID, has_annotations=True, index_annotations=False)
        self.compress_videos = compress_videos

    def create_metadata(self, asset: Video, asset_attributes: NamedTuple,
                        timestamp: Optional[Union[str, datetime]], sets: List[str]) -> dict:
        return {
            "timestamp": timestamp,
            "width": asset_attributes.width,
            "height": asset_attributes.height,
            "sensor": asset.sensor,
            "duration": float(asset_attributes.duration),
            "fps": asset_attributes.fps,
            "sets": sets,
            "start_time": timestamp,
            "end_time": datetime_or_str_to_iso_utc(
                str_or_datetime_to_datetime(timestamp)
                + timedelta(
                    seconds=float(asset_attributes.duration))),
            "tags": asset.tags or []
        }

    def create_entity_dict(self, asset: Video, enrichments: Optional[List[str]], asset_metadata: dict,
                           filename: Optional[str] = None) -> dict:
        return {
            "session": asset.session_uid,
            "start_time": asset_metadata["start_time"],
            "end_time": asset_metadata["end_time"],
            "timestamp": asset_metadata["timestamp"],
            "enrichments": enrichments or [],
            "entity_name": EntityNames.VIDEO,
            "entity_id": filename,
            "entity_type": EntityTypes.MEDIA,
            "entity_value": id,
            "media_asset_id": id,
            "influence": EntityInfluenceTypes.AFFECT_FORWARD,
            "extend_session": True
        }

    def post_index_processing(self, ids: List[str]):
        if self.compress_videos:
            for preset in ['small', 'tiny']:
                self.sec.compress_videos(
                    ids=ids,
                    use_preset=preset)


class BulkLidarUploader(BulkAssetUploader):
    def __init__(self, sec, compress_lidars: bool = False):
        super().__init__(sec=sec, asset_type=AssetsConstants.LIDARS_ASSET_ID, has_annotations=False, index_annotations=False)
        self.compress_lidars = compress_lidars

    def create_metadata(self, asset: Lidar, asset_attributes: NamedTuple,
                        timestamp: Optional[Union[str, datetime]], sets: List[str]) -> dict:
        metadata = {"format": asset.format,
                    "binary_format": asset.binary_format,
                    "sensor": asset.sensor,
                    "timestamp": timestamp,
                    "sets": sets}
        if asset.num_fields:
            metadata["num_fields"] = asset.num_fields

        if asset.related_images:
            images_amc = self.sec.get_asset_manager(asset_type=AssetsConstants.IMAGES_ASSET_ID)
            assert all(images_amc.exists_multiple(asset.related_images)), "some of the related images do not exist"
            metadata["related_images"] = asset.related_images

        return metadata

    def create_entity_dict(self, asset: Lidar, enrichments: Optional[List[str]], asset_metadata: dict,
                           filename: Optional[str] = None) -> dict:
        return {
            "session": asset.session_uid,
            "timestamp": asset_metadata["timestamp"],
            "enrichments": enrichments or [],
            "entity_name": EntityNames.LIDAR,
            "media_asset_id": id,
            "entity_id": get_guid(),
            "entity_value": id,
            "entity_type": EntityTypes.MEDIA,
            "influence": EntityInfluenceTypes.INTERVAL
        }

    def post_index_processing(self, ids: List[str]):
        if self.compress_lidars:
            self.sec.compress_lidars(
                ids=ids,
                skip_factors=[1, 10, 100]
            )
