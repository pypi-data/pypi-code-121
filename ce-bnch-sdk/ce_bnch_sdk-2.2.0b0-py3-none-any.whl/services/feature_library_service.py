from typing import Iterable, List, Optional

from benchling_api_client.api.feature_libraries import (
    bulk_create_features,
    create_feature,
    create_feature_library,
    get_feature,
    get_feature_library,
    list_feature_libraries,
    list_features,
    update_feature,
    update_feature_library,
)
from benchling_api_client.types import Response

from benchling_sdk.errors import raise_for_status
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import (
    AsyncTaskLink,
    Feature,
    FeatureBulkCreate,
    FeatureCreate,
    FeatureLibrariesPaginatedList,
    FeatureLibrary,
    FeatureLibraryCreate,
    FeatureLibraryUpdate,
    FeaturesBulkCreateRequest,
    FeaturesPaginatedList,
    FeatureUpdate,
    ListFeatureLibrariesSort,
    ListFeaturesMatchType,
)
from benchling_sdk.services.base_service import BaseService


class FeatureLibraryService(BaseService):
    """
    Feature Libraries.

    Feature Libraries are collections of shared canonical patterns that can be used to generate annotations
    on matching regions of DNA Sequences or AA Sequences.
    See https://benchling.com/api/reference#/Feature%20Libraries
    """

    @api_method
    def get_by_id(self, feature_library_id: str) -> FeatureLibrary:
        """
        Get a feature library by id.

        See https://benchling.com/api/reference#/Feature%20Libraries/getFeatureLibrary
        """
        response = get_feature_library.sync_detailed(
            client=self.client, feature_library_id=feature_library_id
        )
        return model_from_detailed(response)

    @api_method
    def _feature_libraries_page(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        sort: Optional[ListFeatureLibrariesSort] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[FeatureLibrariesPaginatedList]:
        response = list_feature_libraries.sync_detailed(
            client=self.client,
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            ids=none_as_unset(optional_array_query_param(ids)),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            sort=none_as_unset(sort),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
        )
        raise_for_status(response)
        return response  # type: ignore

    def list(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        sort: Optional[ListFeatureLibrariesSort] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[FeatureLibrary]:
        """
        List Feature Libraries.

        See https://benchling.com/api/reference#/Feature%20Libraries/listFeatureLibraries
        """

        def api_call(next_token: NextToken) -> Response[FeatureLibrariesPaginatedList]:
            return self._feature_libraries_page(
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                ids=ids,
                names_any_of=names_any_of,
                sort=sort,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: FeatureLibrariesPaginatedList) -> Optional[List[FeatureLibrary]]:
            return body.feature_libraries

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, feature_library: FeatureLibraryCreate) -> FeatureLibrary:
        """
        Create a new feature library.

        See https://benchling.com/api/reference#/Feature%20Libraries/createFeatureLibrary
        """
        response = create_feature_library.sync_detailed(client=self.client, json_body=feature_library)
        return model_from_detailed(response)

    @api_method
    def update(self, feature_library_id: str, feature_library: FeatureLibraryUpdate) -> FeatureLibrary:
        """
        Update a feature library.

        See https://benchling.com/api/reference#/Feature%20Libraries/updateFeatureLibrary
        """
        response = update_feature_library.sync_detailed(
            client=self.client, feature_library_id=feature_library_id, json_body=feature_library
        )
        return model_from_detailed(response)

    # The below methods deal with features instead of feature libraries.

    @api_method
    def get_feature_by_id(self, feature_id: str) -> Feature:
        """
        Get a feature by id.

        See https://benchling.com/api/reference#/Feature%20Libraries/getFeature
        """
        response = get_feature.sync_detailed(client=self.client, feature_id=feature_id)
        return model_from_detailed(response)

    @api_method
    def _features_page(
        self,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
        name: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        namesany_ofcase_sensitive: Optional[Iterable[str]] = None,
        feature_library_id: Optional[str] = None,
        feature_type: Optional[str] = None,
        match_type: Optional[ListFeaturesMatchType] = None,
    ) -> Response[FeaturesPaginatedList]:

        response = list_features.sync_detailed(  # type: ignore
            client=self.client,
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
            name=none_as_unset(name),
            ids=none_as_unset(optional_array_query_param(ids)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(namesany_ofcase_sensitive)),
            feature_library_id=none_as_unset(feature_library_id),
            feature_type=none_as_unset(feature_type),
            match_type=none_as_unset(match_type),
        )
        raise_for_status(response)
        return response  # type: ignore

    def list_features(
        self,
        page_size: Optional[int] = None,
        name: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        namesany_ofcase_sensitive: Optional[Iterable[str]] = None,
        feature_library_id: Optional[str] = None,
        feature_type: Optional[str] = None,
        match_type: Optional[ListFeaturesMatchType] = None,
    ) -> PageIterator[Feature]:
        """
        List Features.

        See https://benchling.com/api/reference#/Feature%20Libraries/listFeatures
        """

        def api_call(next_token: NextToken) -> Response[FeaturesPaginatedList]:
            return self._features_page(
                page_size=page_size,
                next_token=next_token,
                name=name,
                ids=ids,
                namesany_ofcase_sensitive=namesany_ofcase_sensitive,
                feature_library_id=feature_library_id,
                feature_type=feature_type,
                match_type=match_type,
            )

        def results_extractor(body: FeaturesPaginatedList) -> Optional[List[Feature]]:
            return body.features

        return PageIterator(api_call, results_extractor)

    @api_method
    def create_feature(self, feature: FeatureCreate) -> Feature:
        """
        Create a feature.

        See https://benchling.com/api/reference#/Feature%20Libraries/createFeature
        """
        response = create_feature.sync_detailed(client=self.client, json_body=feature)
        return model_from_detailed(response)

    @api_method
    def update_feature(self, feature_id: str, feature: FeatureUpdate) -> Feature:
        """
        Update a feature.

        See https://benchling.com/api/reference#/Feature%20Libraries/updateFeature
        """
        response = update_feature.sync_detailed(client=self.client, feature_id=feature_id, json_body=feature)
        return model_from_detailed(response)

    @api_method
    def bulk_create_features(self, features: Iterable[FeatureBulkCreate]) -> AsyncTaskLink:
        """
        Bulk create features.

        See https://benchling.com/api/reference#/Feature%20Libraries/bulkCreateFeatures
        """
        body = FeaturesBulkCreateRequest(list(features))
        response = bulk_create_features.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)
