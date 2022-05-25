from typing import Iterable, List, Optional

import benchling_api_client
from benchling_api_client.api.apps import (
    archive_benchling_apps,
    create_benchling_app,
    get_benchling_app_by_id,
    list_benchling_apps,
    patch_benchling_app,
    unarchive_benchling_apps,
)
from benchling_api_client.types import Response
from benchling_api_client.v2.alpha.api.apps import (
    get_benchling_app_configuration,
    get_benchling_app_manifest,
    list_app_configurations,
    put_benchling_app_manifest,
    update_benchling_app_configuration,
)
from benchling_api_client.v2.alpha.models.benchling_app_configuration import BenchlingAppConfiguration
from benchling_api_client.v2.alpha.models.benchling_app_configuration_paginated_list import (
    BenchlingAppConfigurationPaginatedList,
)
from benchling_api_client.v2.alpha.models.benchling_app_configuration_update import (
    BenchlingAppConfigurationUpdate,
)
from benchling_api_client.v2.alpha.models.benchling_app_manifest import BenchlingAppManifest
from benchling_api_client.v2.beta.api.apps import get_app_configuration_by_app_id

from benchling_sdk.helpers.client_helpers import v2_alpha_client, v2_beta_client
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import (
    BenchlingApp,
    BenchlingAppCreate,
    BenchlingAppsArchivalChange,
    BenchlingAppsArchive,
    BenchlingAppsArchiveReason,
    BenchlingAppsPaginatedList,
    BenchlingAppsUnarchive,
    BenchlingAppUpdate,
    ListBenchlingAppsSort,
)
from benchling_sdk.services.base_service import BaseService


class AppService(BaseService):
    """
    Apps.

    Create and manage Apps on your tenant.

    See https://benchling.com/api/reference#/Apps
    """

    @api_method
    def _apps_page(
        self,
        *,
        page_size: Optional[int] = 50,
        next_token: Optional[str] = None,
        sort: Optional[ListBenchlingAppsSort] = None,
        ids: Optional[Iterable[str]] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        namesany_of: Optional[Iterable[str]] = None,
        namesany_ofcase_sensitive: Optional[Iterable[str]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        member_of: Optional[Iterable[str]] = None,
        admin_of: Optional[Iterable[str]] = None,
    ) -> Response[BenchlingAppsPaginatedList]:
        return list_benchling_apps.sync_detailed(  # type: ignore
            client=self.client,
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
            sort=none_as_unset(sort),
            ids=none_as_unset(optional_array_query_param(ids)),
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            namesany_of=none_as_unset(optional_array_query_param(namesany_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(namesany_ofcase_sensitive)),
            creator_ids=none_as_unset(optional_array_query_param(creator_ids)),
            member_of=none_as_unset(optional_array_query_param(member_of)),
            admin_of=none_as_unset(optional_array_query_param(admin_of)),
        )

    def list_apps(
        self,
        *,
        page_size: Optional[int] = 50,
        sort: Optional[ListBenchlingAppsSort] = None,
        ids: Optional[Iterable[str]] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        namesany_of: Optional[Iterable[str]] = None,
        namesany_ofcase_sensitive: Optional[Iterable[str]] = None,
        creator_ids: Optional[str] = None,
        member_of: Optional[str] = None,
        admin_of: Optional[str] = None,
    ) -> PageIterator[BenchlingApp]:
        """
        List Apps.

        See https://benchling.com/api/reference#/Apps/listBenchlingApps
        """

        def api_call(next_token: NextToken) -> Response[BenchlingAppsPaginatedList]:
            return self._apps_page(
                page_size=page_size,
                sort=sort,
                ids=ids,
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                namesany_of=namesany_of,
                namesany_ofcase_sensitive=namesany_ofcase_sensitive,
                creator_ids=creator_ids,
                member_of=member_of,
                admin_of=admin_of,
                next_token=next_token,
            )

        def results_extractor(body: BenchlingAppsPaginatedList) -> Optional[List[BenchlingApp]]:
            return body.apps

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_by_id(self, app_id: str) -> BenchlingApp:
        """
        Get an App by ID.

        See https://benchling.com/api/reference#/Apps/getBenchlingAppByID
        """
        response = get_benchling_app_by_id.sync_detailed(client=self.client, app_id=app_id)
        return model_from_detailed(response)

    @api_method
    def create(self, app: BenchlingAppCreate) -> BenchlingApp:
        """
        Create an App.

        See https://benchling.com/api/reference#/Apps/createBenchlingApp
        """
        response = create_benchling_app.sync_detailed(client=self.client, json_body=app)
        return model_from_detailed(response)

    @api_method
    def update(self, app_id: str, app: BenchlingAppUpdate) -> BenchlingApp:
        """
        Update an App's metadata.

        See https://benchling.com/api/reference#/Apps/patchBenchlingApp
        """
        response = patch_benchling_app.sync_detailed(client=self.client, app_id=app_id, json_body=app)
        return model_from_detailed(response)

    @api_method
    def archive(
        self, app_ids: Iterable[str], reason: BenchlingAppsArchiveReason
    ) -> BenchlingAppsArchivalChange:
        """
        Archive Apps.

        See https://benchling.com/api/reference#/Apps/archiveBenchlingApps
        """
        archive_request = BenchlingAppsArchive(app_ids=list(app_ids), reason=reason)
        response = archive_benchling_apps.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, app_ids: Iterable[str]) -> BenchlingAppsArchivalChange:
        """
        Unarchive Apps.

        See https://benchling.com/api/reference#/Apps/unarchiveBenchlingApps
        """
        unarchive_request = BenchlingAppsUnarchive(app_ids=list(app_ids))
        response = unarchive_benchling_apps.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    # V2-alpha methods

    @api_method
    def _configurations_page(
        self,
        *,
        app_id: Optional[str] = None,
        page_size: Optional[int] = 50,
        next_token: Optional[str] = None,
        modified_at: Optional[str] = None,
    ) -> Response[BenchlingAppConfigurationPaginatedList]:
        alpha_client = v2_alpha_client(self.client)
        return list_app_configurations.sync_detailed(  # type: ignore
            client=alpha_client,
            app_id=none_as_unset(app_id),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
            modified_at=none_as_unset(modified_at),
        )

    def list_configurations(
        self,
        *,
        app_id: Optional[str] = None,
        page_size: Optional[int] = 50,
        modified_at: Optional[str] = None,
    ) -> PageIterator[BenchlingAppConfiguration]:
        """
        Get app configurations.

        See https://benchling.com/api/v2-alpha/reference?stability=la#/Apps/listAppConfigurations
        """

        def api_call(next_token: NextToken) -> Response[BenchlingAppConfigurationPaginatedList]:
            return self._configurations_page(
                app_id=app_id,
                page_size=page_size,
                modified_at=modified_at,
                next_token=next_token,
            )

        def results_extractor(
            body: BenchlingAppConfigurationPaginatedList,
        ) -> Optional[List[BenchlingAppConfiguration]]:
            return body.app_configurations

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_configuration_by_id(self, configuration_id: str) -> BenchlingAppConfiguration:
        """
        Get app configuration.

        See https://benchling.com/api/v2-alpha/reference?stability=la#/Apps/getBenchlingAppConfiguration
        """
        alpha_client = v2_alpha_client(self.client)
        response = get_benchling_app_configuration.sync_detailed(
            client=alpha_client, configuration_id=configuration_id
        )
        return model_from_detailed(response)

    @api_method
    def update_configuration(
        self, configuration_id: str, configuration: BenchlingAppConfigurationUpdate
    ) -> BenchlingAppConfiguration:
        """
        Update app configuration.

        See https://benchling.com/api/v2-alpha/reference?stability=la#/Apps/updateBenchlingAppConfiguration
        """
        alpha_client = v2_alpha_client(self.client)
        response = update_benchling_app_configuration.sync_detailed(
            client=alpha_client, configuration_id=configuration_id, json_body=configuration
        )
        return model_from_detailed(response)

    @api_method
    def get_configuration_by_app_id(
        self, app_id: str
    ) -> benchling_api_client.v2.beta.models.benchling_app_configuration.BenchlingAppConfiguration:
        """
        Get an app's configuration by app id.

        See https://benchling.com/api/v2-alpha/reference?stability=la#/Apps/getAppConfigurationByAppID
        """
        beta_client = v2_beta_client(self.client)
        response = get_app_configuration_by_app_id.sync_detailed(client=beta_client, app_id=app_id)
        return model_from_detailed(response)

    @api_method
    def get_manifest(self, app_id: str) -> BenchlingAppManifest:
        """
        Get app manifest.

        See https://benchling.com/api/v2-alpha/reference?stability=la/Apps/getBenchlingAppManifest
        """
        alpha_client = v2_alpha_client(self.client)
        response = get_benchling_app_manifest.sync_detailed(client=alpha_client, app_id=app_id)
        return model_from_detailed(response)

    @api_method
    def update_manifest(self, app_id: str, manifest: BenchlingAppManifest) -> BenchlingAppManifest:
        """
        Update an app manifest.

        See https://benchling.com/api/v2-alpha/reference?stability=la#/Apps/putBenchlingAppManifest
        """
        alpha_client = v2_alpha_client(self.client)
        response = put_benchling_app_manifest.sync_detailed(
            client=alpha_client, app_id=app_id, yaml_body=manifest
        )
        return model_from_detailed(response)
