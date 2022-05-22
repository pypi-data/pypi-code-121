from enum import Enum


class DownloadMode(Enum):
    ALL_POSTS = "ALL_POSTS"
    ALL_POSTS_WITH_IMAGES = "ALL_POSTS_WITH_IMAGES"
    FIRST_POST_ONLY = "FIRST_POST_ONLY"
