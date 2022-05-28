from typing import Callable, TypeVar
from ..models.gallery import (
    GalleryExtensionQueryResult,
    GalleryExtensionQueryResultMetadata,
)
from pathlib import Path


def reduceResultMeta(meta: "list[GalleryExtensionQueryResultMetadata]"):
    result = {}
    for group in meta:
        i = result[group["metadataType"]] = {}
        for item in group["metadataItems"]:
            i[item["name"]] = item["count"]
    return result


T = TypeVar("T")


def diff(a: "list[T]", b: "list[T]", key: "str|Callable[[T],object]" = None):
    bmissing = []
    if key is None:
        key = lambda e: e
    elif isinstance(key, str):
        _key = key
        key = lambda e: e[_key]

    for item in a:
        id = key(item)
        if (
            next(
                (e for e in b if key(e) == id),
                False,
            )
            == False
        ):
            bmissing.append(item)
    return bmissing


def diff_query_results(a: GalleryExtensionQueryResult, b: GalleryExtensionQueryResult):
    key = lambda e: e["extensionId"]
    missingb = diff(a["extensions"], b["extensions"], key)
    missinga = diff(b["extensions"], a["extensions"], key)
    return missinga, missingb


def iter_bytes_read(path: str, chunk_size: int = 1024):
    with Path(path).open("rb") as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            yield data
