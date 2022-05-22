from typing import List

from videoembed.providers.base import BaseProvider, TOEmbedData

URL_PATTERNS: List[str] = [
    'vimeo.com',
    'www.vimeo.com'
]


class TOembedVimeoData(TOEmbedData):
    duration: int
    description: str
    thumbnail_url_with_play_button: str
    upload_date: str
    video_id: int
    uri: str
    is_plus: str
    account_type: str


class VimeoProvider(BaseProvider):

    api_url: str = 'https://vimeo.com/api/oembed.json'
    oembed_data: TOembedVimeoData
