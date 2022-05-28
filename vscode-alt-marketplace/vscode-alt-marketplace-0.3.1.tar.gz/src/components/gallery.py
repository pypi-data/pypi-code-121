from typing import Callable

from ..constants import GALLERY_API_ENDPOINT, MARKETPLACE_FQDN
from ..models import *
from .common import IAssetSrc, IGallery, IExtensionSrc
from ..utils import collect_from_generator


class Gallery(IGallery):
    def __init__(self, exts_src: IExtensionSrc, asset_src: IAssetSrc = None) -> None:
        self.exts_src = exts_src
        self.asset_src = asset_src
        if self.asset_src is None:
            self.asset_src = exts_src if isinstance(exts_src, IAssetSrc) else super()

    def extension_query(self, query: GalleryExtensionQuery) -> GalleryQueryResult:

        flags = GalleryFlags(query["flags"])
        assetTypes = query["assetTypes"]

        result: GalleryQueryResult = {"results": []}

        for filter in query["filters"]:
            exts, meta = collect_from_generator(
                self.exts_src.generate_page(
                    filter["criteria"],
                    flags,
                    assetTypes,
                    filter["pageNumber"],
                    filter["pageSize"],
                    SortBy(filter["sortBy"]),
                    SortOrder(filter["sortOrder"]),
                )
            )
            result["results"].append({"extensions": exts, "resultMetadata": meta})
        return result

    def get_extension_asset(
        self, extensionId: str, version: "str | None", asset: "AssetType|str"
    ):
        return self.asset_src.get_extension_asset(extensionId, version, asset)

    def get_publisher_vspackage(self, publisher: str, extension: str, version: str):
        return self.get_extension_asset(
            f"{publisher}.{extension}", version=version, asset=AssetType.VSIX
        )


try:
    from requests import Session
    import requests

    class ExternalGallery(IGallery):
        def __init__(
            self, src: str = None, get_session: Callable[[], Session] = None
        ) -> None:
            self._src = src or f"https://{MARKETPLACE_FQDN}{GALLERY_API_ENDPOINT}"
            self._session = get_session or (lambda: requests)

        def extension_query(
            self, query: GalleryExtensionQuery, *, session: requests.Session = None
        ) -> GalleryQueryResult:
            session: requests.Session
            return (
                (session or self._session())
                .post(
                    self._src + "extensionquery",
                    headers={"Accept": "application/json;api-version=3.0-preview.1"},
                    json=query,
                )
                .json()
            )

        def get_extension_asset(
            self,
            extensionId: str,
            version: str,
            asset: "AssetType|str",
            *,
            session: requests.Session = None,
        ):
            return (
                (session or self._session())
                .get(
                    f"{self._src}/extensions/{extensionId}/{version}/assets/{asset}",
                    headers={"Accept": "application/json;api-version=3.0-preview.1"},
                )
                .content
            )

        def get_publisher_vspackage(
            self,
            publisher: str,
            extension: str,
            version: str,
            *,
            session: requests.Session = None,
        ):
            return (
                (session or self._session())
                .get(
                    f"{self._src}/publishers/{publisher}/vsextensions/{extension}/{version}/vspackage",
                    headers={"Accept": "application/json;api-version=3.0-preview.1"},
                )
                .content
            )

except ModuleNotFoundError:
    pass
