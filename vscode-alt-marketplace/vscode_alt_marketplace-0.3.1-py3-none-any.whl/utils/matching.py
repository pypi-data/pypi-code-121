import re
from typing import Callable, Optional

from ..models.gallery import (
    VSCODE_INSTALLATION_TARGET,
    FilterType,
    GalleryCriterium,
    GalleryExtension,
    GalleryExtensionQuery,
    GalleryFlags,
    SortBy,
    SortOrder,
)


def token_regex(token: str):
    return re.compile(
        r"\b" + token + r'("([^"]*)"|([^"]\S*))(\s+|\b|$)', flags=re.IGNORECASE
    )


def collect_filter_token(
    type: FilterType, token: re.Pattern, search: str, criteria: "list[GalleryCriterium]"
):
    def collect(match: re.Match):
        criteria.append({"filterType": type, "value": match[1]})
        return ""

    search = token.sub(collect, search)
    return search


CATEGORY_TOKEN = token_regex("category:")
TAG_TOKEN = token_regex("tag:")
TEXT_TOKEN = token_regex("")


class ExtensionFilter:
    type: FilterType
    value: Optional[str]
    matcher: Callable[[GalleryExtension], bool]

    def __init__(self, criterium: GalleryCriterium) -> None:
        type = self.type = FilterType(criterium["filterType"])
        self.value = criterium["value"]
        if type is FilterType.Tag:
            value = self.value.lower()

            def matcher(ext: GalleryExtension):
                return value in ext["tags"]

        elif type is FilterType.ExtensionId:
            value = self.value.lower()

            def matcher(ext: GalleryExtension):
                return value == ext["extensionId"]

        elif type is FilterType.Category:
            value = self.value

            def matcher(ext: GalleryExtension):
                return value in ext["categories"]

        elif type is FilterType.ExtensionName:
            value = self.value.lower()

            def matcher(ext: GalleryExtension):
                return value in [
                    ext["extensionName"],
                    ext["publisher"]["publisherName"] + "." + ext["extensionName"],
                ]

        elif type is FilterType.Target:
            value = self.value

            def matcher(ext: GalleryExtension):
                return value == VSCODE_INSTALLATION_TARGET

        elif type is FilterType.Featured:

            def matcher(ext: GalleryExtension):
                return True

        elif type is FilterType.SearchText:
            criteria: "list[GalleryCriterium]" = []
            value = collect_filter_token(
                FilterType.Category, CATEGORY_TOKEN, self.value, criteria
            )
            value = collect_filter_token(FilterType.Tag, TAG_TOKEN, value, criteria)

            criteria_matcher = CriteriaMatcher(criteria)

            search_texts = [
                re.compile(r".*\b" + re.escape(match[0]) + r".*", re.IGNORECASE)
                for match in TEXT_TOKEN.findall(value)
            ]

            def matcher(ext: GalleryExtension):

                if not (
                    criteria_matcher.and_filters or criteria_matcher.or_filters
                ) or criteria_matcher.is_match(ext):
                    tags = [t for t in ext.get("tags", []) if not t.startswith("__")]
                    locs = [
                        ext["extensionName"],
                        ext.get("shortDescription", ""),
                        ext["displayName"],
                        ext["publisher"]["displayName"],
                        *tags,
                    ]

                    for text in search_texts:
                        for loc in locs:
                            if text.match(loc):
                                return True

        elif type is FilterType.ExcludeWithFlags:
            flags = GalleryFlags(int(self.value))
            if GalleryFlags.Unpublished in flags:

                def matcher(ext: GalleryExtension):
                    return "unpublished" not in ext["flags"]

            else:

                def matcher(ext: GalleryExtension):
                    return True

        self.matcher = matcher


AND_FILTERS = [FilterType.Target, FilterType.Featured, FilterType.ExcludeWithFlags]


class CriteriaMatcher:
    def __init__(self, criteria: "list[GalleryCriterium]") -> None:
        filters = [ExtensionFilter(c) for c in criteria]
        self.and_filters = [f for f in filters if f.type in AND_FILTERS]
        self.or_filters = [f for f in filters if f.type not in AND_FILTERS]

    def is_match(self, ext: GalleryExtension) -> bool:
        for f in self.and_filters:
            if not f.matcher(ext):
                return False
        for f in self.or_filters:
            if f.matcher(ext):
                return True
        return not self.or_filters


def simple_query(
    search: "str | list[GalleryCriterium]",
    page: int = 1,
    pageSize: int = 50,
    sortBy: SortBy = SortBy.NoneOrRelevance,
    sortOrder: SortOrder = SortOrder.Default,
    flags: GalleryFlags = GalleryFlags.IncludeStatistics
    | GalleryFlags.IncludeAssetUri
    | GalleryFlags.ExcludeNonValidated
    | GalleryFlags.IncludeVersionProperties
    | GalleryFlags.IncludeCategoryAndTags
    | GalleryFlags.IncludeFiles
    | GalleryFlags.IncludeVersions,
) -> GalleryExtensionQuery:
    return {
        "filters": [
            {
                "criteria": [
                    {
                        "filterType": FilterType.Target,
                        "value": VSCODE_INSTALLATION_TARGET,
                    },
                    {"filterType": FilterType.SearchText, "value": search},
                    {
                        "filterType": FilterType.ExcludeWithFlags,
                        "value": GalleryFlags.Unpublished,
                    },
                ]
                if isinstance(search, str)
                else search,
                "pageNumber": page,
                "pageSize": pageSize,
                "sortBy": sortBy,
                "sortOrder": sortOrder,
            }
        ],
        "assetTypes": [],
        "flags": flags,
    }
