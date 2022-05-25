from typing import Union

from .image_utils import get_image_attributes
from .misc import parse_file_path
from .naming import UriParser
from .video_utils import get_video_attributes
from ..constants import AssetsConstants


def get_asset_attributes_filename(asset_type:str,asset_source: Union[str, bytes], source_type: str, **kwargs):
    def get_attributes(s, t):
        if asset_type == AssetsConstants.IMAGES_ASSET_ID:
            return get_image_attributes(s, t)
        if asset_type == AssetsConstants.VIDEOS_ASSET_ID:
            return get_video_attributes(s)
        return None

    if source_type == "url":
        return get_attributes(asset_source, source_type), asset_source.split("/")[-1]

    if source_type == "path":
        filename, _, _, image_format = parse_file_path(asset_source)
        return get_attributes(asset_source, source_type), filename

    if source_type == "bytes":
        return get_attributes(asset_source, source_type), kwargs["id"]

    if source_type == "uri":
        return get_attributes(kwargs["url"], "url"), UriParser(uri=asset_source).key.split("/")[-1]

    else:
        raise NotImplementedError(
            "Either image url, uri, path or bytes must be provided")