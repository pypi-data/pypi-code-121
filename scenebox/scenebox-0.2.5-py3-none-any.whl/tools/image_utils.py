#  Copyright (c) 2021 Caliber Data Labs.
#  All rights reserved.
#
from typing import NamedTuple, Union
import requests
from PIL import Image, ImageFile
from ..custom_exceptions import ResponseError

from .logger import get_logger

logger = get_logger(__name__)


class ImageProperties(NamedTuple):
    width: int
    height: int
    format: str


def __get_img_attr_by_url(url: str) -> ImageProperties:
    resp = requests.get(url, stream=True)
    if not resp.ok:
        raise ResponseError(
            "Could not find an image in {}".format(url))
    else:
        p = ImageFile.Parser()
        for data in resp.iter_content(chunk_size=1024):
            p.feed(data)
            if p.image:
                return ImageProperties(
                    width=p.image.width,
                    height=p.image.height,
                    format=p.image.format
                )


def __get_img_attr_by_path(path: str) -> ImageProperties:
    with Image.open(path) as image_file:
        width, height = image_file.size
        format = image_file.format
        return ImageProperties(
            width=width,
            height=height,
            format=format)


def __get_img_attr_by_bytes(img_bytes: bytes) -> ImageProperties:
    image = Image.open(img_bytes)
    width, height = image.size
    format = image.format
    return ImageProperties(
        width=width,
        height=height,
        format=format)


__img_attr_func_map = {"url": __get_img_attr_by_url, "path": __get_img_attr_by_path, "bytes": __get_img_attr_by_bytes}


def get_image_attributes(image_source: Union[str, bytes], source_type: str):
    # get file size *and* image size (None if not known)
    if source_type in __img_attr_func_map:
        return __img_attr_func_map[source_type](image_source)

    else:
        raise NotImplementedError(
            "Either image url, path or bytes must be provided")

class ImageSequence(object):
    def __init__(self,
                 sensor: str,
                 width: int,
                 height: int,
                 image_format: str,
                 encoding: str = "rgb"):
        """
        :param sensor: The sesnor that image sequence belongs to
        :param width: The width of images in the sequence, assumption is that all have the same width
        :param height: The height of images in the sequence, assumption is that all have the same height
        :param image_format: The format of images in the sequence, assumption is that all have the same format
        :param encoding: The encoding of images in the sequence, assumption is that all have the same encoding
        """
        self.sensor = sensor
        self.width = width
        self.height = height
        self.encoding = encoding
        self.image_format = image_format
        self.timestamps = []
        self.image_uris = []
        self.image_ids = []

    @property
    def end_time(self):
        if self.timestamps:
            return max(self.timestamps)
        else:
            return None

    @property
    def start_time(self):
        if self.timestamps:
            return min(self.timestamps)
        else:
            return None

    @property
    def fps_mean(self):
        if self.end_time and self.start_time and self.start_time != self.end_time:
            return (len(self.image_uris) - 1) / (self.end_time - self.start_time)
        else:
            return None

    @property
    def fps_max(self):
        if self.timestamps and self.start_time != self.end_time:
            return 1.0 / min([j-i for i, j in zip(self.timestamps[:-1], self.timestamps[1:])])
        else:
            return None

    def add_image(self, image_uri: str, timestamp: float, image_id: str):
        self.image_uris.append(image_uri)
        self.image_ids.append(image_id)
        self.timestamps.append(timestamp)
