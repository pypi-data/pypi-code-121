import json
from typing import Dict, NoReturn, Any, Set, TypedDict

import requests
from requests.models import Response

from videoembed.exceptions import APIRequestFailed


class TOEmbedData(TypedDict):
    title: str
    author_name: str
    author_url: str
    type: str
    height: int
    width: int
    version: str
    provider_name: str
    provider_url: str
    thumbnail_height: int
    thumbnail_width: int
    thumbnail_url: str
    html: str


class TThumbnailData(TypedDict):
    title: str
    width: int
    height: int
    url: str


class TRequestParams(TypedDict):
    maxwidth: int
    maxheight: int
    autoplay: int
    url: str
    format: str


class BaseProvider(object):
    """ Base class for any provider classes """

    # default values
    width: int = 640
    height: int = 360
    autoplay: bool = False

    video_url: str
    api_url: str
    oembed_data: TOEmbedData

    def __init__(self, video_url: str, config: Dict[str, Any]) -> NoReturn:
        allowed_keys: Set[str] = {
            'width',
            'height',
            'autoplay'
        }
        self.__dict__.update((k, v) for k, v in config.items() if k in allowed_keys)

        self.video_url = video_url
        self.oembed_data = self.make_request()

    @property
    def embed_code(self) -> str:
        return self.oembed_data.get('html')

    @property
    def thumbnail(self) -> TThumbnailData:
        return {
            'title': self.oembed_data.get('title'),
            'width': self.oembed_data.get('thumbnail_width'),
            'height': self.oembed_data.get('thumbnail_height'),
            'url': self.oembed_data.get('thumbnail_url')
        }

    def make_request(self) -> TOEmbedData:
        response: Response = requests.get(
            url=self.api_url,
            params=self._build_request_params()
        )

        if response.status_code != 200:
            raise APIRequestFailed(response)

        return json.loads(response.text)

    def _build_request_params(self) -> TRequestParams:
        return {
            'maxwidth': self.width,
            'maxheight': self.height,
            'autoplay': int(self.autoplay),
            'url': self.video_url,
            'format': 'json'
        }
