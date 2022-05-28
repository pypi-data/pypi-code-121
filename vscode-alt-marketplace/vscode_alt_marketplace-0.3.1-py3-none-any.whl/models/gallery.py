from enum import Enum, IntEnum, IntFlag
from typing import Optional, TypedDict
from typing_extensions import NotRequired

# https://github.com/microsoft/vscode/blob/main/src/vs/platform/extensionManagement/common/extensionManagement.ts
class SortBy(IntEnum):
    NoneOrRelevance = 0
    LastUpdatedDate = 1
    Title = 2
    PublisherName = 3
    InstallCount = 4
    PublishedDate = 10
    AverageRating = 6
    WeightedRating = 12


class SortOrder(IntEnum):
    Default = 0
    Ascending = 1
    Descending = 2


# https://github.com/microsoft/vscode/blob/main/src/vs/platform/extensionManagement/common/extensionGalleryService.ts


class GalleryExtensionFile(TypedDict):
    assetType: str
    source: str


class GalleryExtensionProperty(TypedDict):
    key: str
    value: str


class GalleryExtensionVersion(TypedDict):
    version: str
    lastUpdated: str
    assetUri: str
    fallbackAssetUri: str
    files: "list[GalleryExtensionFile]"
    properties: NotRequired["list[GalleryExtensionProperty]"]
    targetPlatform: NotRequired[str]
    flags: str


class GalleryExtensionStatistics(TypedDict):
    statisticName: str
    value: float


class GalleryExtensionPublisher(TypedDict):
    displayName: str
    publisherId: str
    publisherName: str
    domain: NotRequired[Optional[str]]
    isDomainVerified: NotRequired[bool]


class InstallationTarget(TypedDict):
    target: str
    targetVersion: str


class GalleryExtension(TypedDict):
    extensionId: str
    extensionName: str
    displayName: str
    shortDescription: str
    publisher: GalleryExtensionPublisher
    versions: "list[GalleryExtensionVersion]"
    statistics: "list[GalleryExtensionStatistics]"
    tags: Optional["list[str]"]
    releaseDate: str
    publishedDate: str
    lastUpdated: str
    categories: Optional["list[str]"]
    flags: str
    installationTargets: "list[InstallationTarget]"


class GalleryExtensionQueryResultMetadataItem(TypedDict):
    name: str
    count: float


# Inline in source code
class GalleryExtensionQueryResultMetadata(TypedDict):
    metadataType: str
    metadataItems: "list[GalleryExtensionQueryResultMetadataItem]"


# Inline in source code
class GalleryExtensionQueryResult(TypedDict):
    extensions: "list[GalleryExtension]"
    resultMetadata: "list[GalleryExtensionQueryResultMetadata]"


class GalleryQueryResult(TypedDict):
    results: "list[GalleryExtensionQueryResult]"


class GalleryFlags(IntFlag):
    # None is used to retrieve only the basic extension details.
    NONE = 0x0
    # IncludeVersions will return version information for extensions returned
    IncludeVersions = 0x1
    # IncludeFiles will return information about which files were found
    # within the extension that were stored independent of the manifest.
    # When asking for files, versions will be included as well since files
    # are returned as a property of the versions.
    # These files can be retrieved using the path to the file without
    # requiring the entire manifest be downloaded.
    IncludeFiles = 0x2
    # Include the Categories and Tags that were added to the extension definition.
    IncludeCategoryAndTags = 0x4
    # Include the details about which accounts the extension has been shared
    # with if the extension is a private extension.
    IncludeSharedAccounts = 0x8
    # Include properties associated with versions of the extension
    IncludeVersionProperties = 0x10
    # Excluding non-validated extensions will remove any extension versions that
    # either are in the process of being validated or have failed validation.
    ExcludeNonValidated = 0x20
    # Include the set of installation targets the extension has requested.
    IncludeInstallationTargets = 0x40
    # Include the base uri for assets of this extension
    IncludeAssetUri = 0x80
    # Include the statistics associated with this extension
    IncludeStatistics = 0x100
    # When retrieving versions from a query, only include the latest
    # version of the extensions that matched. This is useful when the
    # caller doesn't need all the published versions. It will save a
    # significant size in the returned payload.
    IncludeLatestVersionOnly = 0x200
    # This flag switches the asset uri to use GetAssetByName instead of CDN
    # When this is used, values of base asset uri and base asset uri fallback are switched
    # When this is used, source of asset files are pointed to Gallery service always even if CDN is available
    Unpublished = 0x1000
    # Include the details if an extension is in conflict list or not
    IncludeNameConflictInfo = 0x8000


class FilterType(IntEnum):
    Tag = 1
    ExtensionId = 4
    Category = 5
    ExtensionName = 7
    Target = 8
    Featured = 9
    SearchText = 10
    ExcludeWithFlags = 12


class AssetType(str, Enum):
    Icon = "Microsoft.VisualStudio.Services.Icons.Default"
    Details = "Microsoft.VisualStudio.Services.Content.Details"
    Changelog = "Microsoft.VisualStudio.Services.Content.Changelog"
    Manifest = "Microsoft.VisualStudio.Code.Manifest"
    VSIX = "Microsoft.VisualStudio.Services.VSIXPackage"
    License = "Microsoft.VisualStudio.Services.Content.License"
    Repository = "Microsoft.VisualStudio.Services.Links.Source"


class PropertyType(str, Enum):
    Dependency = "Microsoft.VisualStudio.Code.ExtensionDependencies"
    ExtensionPack = "Microsoft.VisualStudio.Code.ExtensionPack"
    Engine = "Microsoft.VisualStudio.Code.Engine"
    PreRelease = "Microsoft.VisualStudio.Code.PreRelease"
    LocalizedLanguages = "Microsoft.VisualStudio.Code.LocalizedLanguages"
    WebExtension = "Microsoft.VisualStudio.Code.WebExtension"


class GalleryCriterium(TypedDict):
    filterType: FilterType
    value: NotRequired[str]


VSCODE_INSTALLATION_TARGET = "Microsoft.VisualStudio.Code"
DefaultPageSize = 10

# From request
class GalleryExtensionQueryFilter(TypedDict):
    pageNumber: float
    pageSize: float
    pagingToken: None
    sortBy: SortBy
    sortOrder: SortOrder
    criteria: "list[GalleryCriterium]"


class GalleryExtensionQuery(TypedDict):
    assetTypes: "list[str]"
    filters: "list[GalleryExtensionQueryFilter]"
    flags: GalleryFlags
