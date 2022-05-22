from typing import List
import re

from videoembed.providers.base import BaseProvider

URL_PATTERNS: List[str] = [
    'youtu.be',
    'youtube.com',
    'youtube-nocookie.com',
    'www.youtu.be',
    'www.youtube.com',
    'www.youtube-nocookie.com'
]


class YoutubeProvider(BaseProvider):

    api_url: str = 'https://www.youtube.com/oembed'

    @property
    def embed_code(self) -> str:
        html = self.oembed_data.get('html')
        if self.autoplay:
            html = re.sub(r's*(src=\".+?)(\?|\")', r'\1?autoplay=1"', html)
        return html
