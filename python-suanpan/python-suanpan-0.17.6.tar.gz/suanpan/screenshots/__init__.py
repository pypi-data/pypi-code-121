# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import g
from suanpan.proxy import Proxy

TYPE = g.screenshotsType
PATTERN = g.screenshotsPattern
STORAGE_KEY = g.screenshotsStorageKey
THUMBNAIL_STORAGE_KEY = g.screenshotsThumbnailStorageKey


class Screenshots(Proxy):
    MAPPING = {
        "index": "suanpan.screenshots.base.ScreenshotsIndexSaver",
        "time": "suanpan.screenshots.base.ScreenshotsTimeSaver",
    }
    DEFAULT_PATTERN_MAPPING = {"index": "{index}.png", "time": "{time}.png"}

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(self.TYPE_KEY, TYPE)
        kwargs.setdefault("name", STORAGE_KEY)
        kwargs.setdefault("thumbnail", THUMBNAIL_STORAGE_KEY)
        kwargs.setdefault(
            "pattern", PATTERN or self.DEFAULT_PATTERN_MAPPING.get(kwargs["type"])
        )
        super().__init__(*args, **kwargs)


screenshots = Screenshots()
