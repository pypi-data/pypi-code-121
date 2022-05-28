from typing import Callable, Generator, Iterable
from pathlib import Path

from ..utils.misc import iter_bytes_read

from .common import IAssetSrc, IExtensionSrc

from ..utils.matching import CriteriaMatcher
from ..utils.extension import (
    get_asset_from_vsix,
    get_version,
    get_version_asset,
    get_vsix_manifest,
    sanitize_extension,
    sort_extensions,
)

from ..models import *

try:
    from .gallery import ExternalGallery

    class MirrorExtensionSrc(IExtensionSrc):
        def __init__(self, src: str = None) -> None:
            super().__init__()
            self._gallery = ExternalGallery(src)

        def _sanitize_extension(self, ext: GalleryExtension):
            return ext

        def generate_page(
            self,
            criteria: "list[GalleryCriterium]",
            flags: GalleryFlags,
            assetTypes: "list[str]",
            page: int = 1,
            pageSize: int = 10,
            sortBy: SortBy = SortBy.NoneOrRelevance,
            sortOrder: SortOrder = SortOrder.Default,
        ) -> Generator[
            GalleryExtension, None, "list[GalleryExtensionQueryResultMetadata]"
        ]:
            resp = self._gallery.extension_query(
                {
                    "filters": [
                        {
                            "criteria": criteria,
                            "pageNumber": page,
                            "pageSize": pageSize,
                            "sortBy": sortBy,
                            "sortOrder": sortOrder,
                        }
                    ],
                    "assetTypes": assetTypes,
                    "flags": flags,
                },
            )

            for ext in resp["results"][0]["extensions"]:
                yield self._sanitize_extension(ext)
            return resp["results"][0]["resultMetadata"]

except ModuleNotFoundError:
    pass


class IterExtensionSrc(IExtensionSrc):
    def __init__(self, exts: Iterable[GalleryExtension]) -> None:
        super().__init__()
        self._exts = exts

    def iter(self):
        return self._exts

    def _sanitize_extension(
        self, flags: GalleryFlags, assetTypes: "list[str]", ext: GalleryExtension
    ):
        return sanitize_extension(flags, assetTypes, ext)

    def generate_page(
        self,
        criteria: "list[GalleryCriterium]",
        flags: GalleryFlags,
        assetTypes: "list[str]",
        page: int = 1,
        pageSize: int = 10,
        sortBy: SortBy = SortBy.NoneOrRelevance,
        sortOrder: SortOrder = SortOrder.Default,
        *,
        short_on_qty: bool = False,
    ) -> Generator[GalleryExtension, None, "list[GalleryExtensionQueryResultMetadata]"]:
        matcher: CriteriaMatcher = CriteriaMatcher(criteria)
        matched = 0
        start = ((page or 1) - 1) * pageSize
        end = start + pageSize
        cats = {}

        for ext in sort_extensions(self.iter(), sortOrder, sortBy):
            if (
                GalleryFlags.ExcludeNonValidated in flags
                and "validated" not in ext["flags"]
            ):
                continue
            if matcher.is_match(ext):
                matched += 1
                for cat in ext.get("categories", []):
                    cats[cat] = cats.get(cat, 0) + 1
                if matched > start and matched <= end:
                    yield self._sanitize_extension(flags, assetTypes, ext)
                if matched >= end and short_on_qty:
                    break

        return [
            {
                "metadataType": "ResultCount",
                "metadataItems": [
                    {"name": "TotalCount", "count": matched},
                ],
            },
            {
                "metadataType": "Categories",
                "metadataItems": [
                    {"name": cat, "count": count} for cat, count in cats.items()
                ],
            },
        ]


class ProxyExtensionSrc(IExtensionSrc):
    def __init__(
        self,
        src: IExtensionSrc,
        proxy_url: Callable[[str, str, GalleryExtension, GalleryExtensionVersion], str],
    ) -> None:
        super().__init__()
        self.src = src
        self.proxy_url = proxy_url

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
        gen = self.src.generate_page(
            criteria, flags, assetTypes, page, pageSize, sortBy, sortOrder
        )
        while True:
            try:
                ext: GalleryExtension = next(gen)
                for ver in ext.get("versions", []):
                    for uri in ["assetUri", "fallbackAssetUri"]:
                        if uri in ver:
                            ver[uri] = self.proxy_url(ver[uri], uri, ext, ver)
                yield ext
            except StopIteration as ex:
                return ex.value


class CachedGallerySrc(IterExtensionSrc, IAssetSrc):
    _exts: "dict[str, GalleryExtension]"
    _uid_map: "dict[str, str]"

    def __init__(self, asset_target: "str|Callable[[], str]" = None) -> None:
        self._uid_map = {}
        asset_target = asset_target or None
        self._asset_target = (
            (lambda: asset_target) if isinstance(asset_target, str) else asset_target
        )

    def _get_uid(self, id: "str|GalleryExtension"):
        if isinstance(id, str):
            if "." in id:
                return id
            else:
                return self._uid_map.get(id.lower())
        else:
            return f'{id["publisher"]["publisherName"]}.{id["extensionName"]}'

    def _load(self) -> Iterable[GalleryExtension]:
        return []

    def _sanitize_extension(
        self, flags: GalleryFlags, assetTypes: "list[str]", ext: GalleryExtension
    ):
        ext = super()._sanitize_extension(flags, assetTypes, ext)
        asset_target = self._asset_target() if self._asset_target else "/"
        if not asset_target.endswith("/"):
            asset_target += "/"
        for ver in ext.get("versions", []):
            ver["assetUri"] = ver["fallbackAssetUri"] = asset_target + self.asset_path(
                ext["extensionId"], ver["version"]
            )
        return ext

    def iter(self):
        return self._exts.values()

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
        extuid = self._get_uid(extensionId)
        ext = self._exts.get(extuid, None)
        if ext:
            return self._sanitize_extension(flags, assetTypes, ext)

    def asset_path(self, extensionId: str, version: str) -> "str|None":
        uid = self._get_uid(extensionId)
        if uid:
            return f"{uid}/{version}"

    def get_extension_asset(self, extensionId: str, version: "str | None", asset: str):
        path = self.asset_path(extensionId, version)
        if path:
            return self.get_asset(path, asset)
        return None, None

    def get_asset(self, src: str, asset: AssetType):
        return None, None

    def reload(self):
        import semver

        self._exts: "dict[str, GalleryExtension]" = {}
        for ext in self._load():
            uid = self._get_uid(ext)
            _ext = self._exts.get(uid, None)

            if _ext:
                for ver in ext["versions"]:
                    dup = False
                    v = ver["version"]
                    for _ver in _ext["versions"]:
                        _v = _ver["version"]
                        if _v == v:
                            dup = True
                    if not dup:
                        _ext["versions"].append(ver)
            else:
                self._exts[uid] = ext
                self._uid_map[ext["extensionId"]] = uid

        for ext in self._exts.values():
            ext["versions"].sort(
                key=lambda v: semver.Version.parse(v["version"]), reverse=True
            )


class LocalGallerySrc(CachedGallerySrc):
    def __init__(self, path: str, id_cache: str = None, asset_target=None) -> None:
        self._path = Path(path)
        self._path.mkdir(exist_ok=True, parents=True)
        self._ids_cache = Path(id_cache) if id_cache else self._path / "ids.json"
        super().__init__(asset_target)
        self.reload()

    def get_asset(self, path: str, asset: "str|AssetType"):
        assets = self.assets.get(path, None)
        if assets:
            vsix = self._path / assets[AssetType.VSIX]
            if asset == AssetType.VSIX:
                return iter_bytes_read(vsix), vsix
            else:
                return get_asset_from_vsix(vsix, asset, assets_map=assets)

        return None, None

    def _load(self):
        import json, uuid
        from ..utils.extension import gallery_ext_from_manifest

        self.assets: "dict[str, dict[AssetType, str]]" = {}
        ids = (
            json.loads(self._ids_cache.read_text()) if self._ids_cache.exists() else {}
        )

        for file in self._path.iterdir():
            if file.suffix == ".vsix":
                manifest = get_vsix_manifest(file)
                ext = gallery_ext_from_manifest(manifest)
                uid = self._get_uid(ext)
                ext["extensionId"] = ids.setdefault(uid, str(uuid.uuid4()))
                ext["publisher"]["publisherId"] = ids.setdefault(
                    ext["publisher"]["publisherName"], str(uuid.uuid4())
                )
                ext["versions"][0]["assetUri"] = str(file.name)
                ext["versions"][0]["fallbackAssetUri"] = str(file.name)
                ext["versions"][0]["flags"] += " validated"
                ext["flags"] += " validated"
                ext["versions"][0]["files"].append(
                    {"source": file.name, "assetType": AssetType.VSIX.value}
                )
                self.assets[self.asset_path(uid, ext["versions"][0]["version"])] = {
                    f["assetType"]: f["source"] for f in ext["versions"][0]["files"]
                }
                yield ext

        self._ids_cache.write_text(json.dumps(ids))
