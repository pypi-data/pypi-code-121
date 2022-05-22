from typing import TypedDict, List

from videoembed.providers import vimeo, youtube
from videoembed.providers.vimeo import VimeoProvider
from videoembed.providers.youtube import YoutubeProvider


class TProviders(TypedDict):
    VimeoProvider: List[str]
    YoutubeProvider: List[str]


PROVIDERS: TProviders = {
    VimeoProvider: vimeo.URL_PATTERNS,
    YoutubeProvider: youtube.URL_PATTERNS
}

