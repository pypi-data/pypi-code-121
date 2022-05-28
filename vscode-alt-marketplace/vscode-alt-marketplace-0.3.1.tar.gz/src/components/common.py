from typing import Iterable, Generator

from ..utils.extension import get_version, get_version_asset

from ..models import *


class IUpdateServer:
    def get_vscode_update(
        platform: str, channel: str, commit: str
    ) -> "tuple[bytes|Iterable[bytes]|None, str|None]":
        raise NotImplementedError()

    def get_remote_ssh_server(
        commit: str, platform: str, channel: str
    ) -> "tuple[bytes|Iterable[bytes]|None, str|None]":
        raise NotImplementedError()


class IAssetSrc:
    def asset_path(self, extension:str, version:str):
        raise NotImplementedError()

    def get_asset(
        self, path: str, asset: "str|AssetType"
    ) -> "tuple[bytes|Iterable[bytes]|None, str|None]":
        raise NotImplementedError()

    def get_extension_asset(
        self, extensionId: str, version: "str | None", asset: str
    ) -> "tuple[bytes|Iterable[bytes]|None, str|None]":
        raise NotImplementedError()


class IExtensionSrc:
    def generate_page(
        self,
        criteria: "list[GalleryCriterium]",
        flags: GalleryFlags,
        assetTypes: "list[str]",
        page: int = 1,
        pageSize: int = 10,
        sortBy: SortBy = SortBy.NoneOrRelevance,
        sortOrder: SortOrder = SortOrder.Default,
    ) -> Generator[GalleryExtension, None, "list[GalleryExtensionQueryResultMetadata]"]:
        raise NotImplementedError()

    def get_extension(
        self,
        extensionId: str,
        flags: GalleryFlags = GalleryFlags.IncludeAssetUri
        | GalleryFlags.IncludeCategoryAndTags
        | GalleryFlags.IncludeFiles
        | GalleryFlags.IncludeInstallationTargets
        | GalleryFlags.IncludeStatistics
        | GalleryFlags.IncludeVersionProperties
        | GalleryFlags.IncludeVersions,
        assetTypes: "list[str]" = [],
    ):
        return next(
            self.generate_page(
                [
                    {
                        "filterType": FilterType.ExtensionName
                        if "." in extensionId
                        else FilterType.ExtensionName,
                        "value": extensionId,
                    }
                ],
                page=1,
                pageSize=1,
                flags=flags,
                assetTypes=assetTypes,
            ),
            None,
        )


class IGallery:
    def extension_query(self, query: GalleryExtensionQuery) -> GalleryQueryResult:
        raise NotImplementedError()

    def get_extension_asset(
        self, extensionId: str, version: str, asset: "AssetType|str"
    ) -> "tuple[bytes|Iterable[bytes]|None, str|None]":
        ext = next(
            self.extension_query(
                {
                    "filters": [
                        {
                            "criteria": [
                                {
                                    "filterType": FilterType.ExtensionName
                                    if "." in extensionId
                                    else FilterType.ExtensionName,
                                    "value": extensionId,
                                }
                            ],
                            "pageNumber": 1,
                            "pageSize": 1,
                            "sortBy": SortBy.NoneOrRelevance,
                            "sortOrder": SortOrder.Default,
                        }
                    ],
                    "assetTypes": [],
                    "flags": GalleryFlags.IncludeAssetUri
                    | GalleryFlags.IncludeFiles
                    | GalleryFlags.IncludeVersions,
                }
            ),
            None,
        )
        if ext:
            ver = get_version(ext, version)
            if ver:
                if get_version_asset(ver, asset):
                    import requests

                    return requests.get(f'{ver["assetUri"]}/{asset}').content

    def get_publisher_vspackage(self, publisher: str, extension: str, version: str):
        return self.get_extension_asset(
            f"{publisher}.{extension}", version=version, asset=AssetType.VSIX
        )
