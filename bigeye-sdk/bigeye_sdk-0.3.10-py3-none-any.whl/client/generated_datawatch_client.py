from __future__ import annotations

import abc
import json
from typing import List, Optional, Union

from bigeye_sdk.client.enum import Method
from bigeye_sdk.functions.metric_functions import is_same_metric, is_same_column_metric
from bigeye_sdk.functions.urlfuncts import encode_url_params

from bigeye_sdk.generated.com.torodata.models.generated import TableList, ColumnMetricProfileList, \
    AutometricAcceptRequest, \
    AutometricAcceptResponse, GetMetricInfoListRequest, MetricInfoList, SearchMetricConfigurationRequest, \
    BatchGetMetricResponse, MetricCreationState, ThreeLeggedBoolean, MetricSortField, SortDirection, \
    MetricConfiguration, \
    MetricBackfillResponse, MetricBackfillRequest, GetCollectionsResponse, GetCollectionResponse, Collection, \
    EditCollectionResponse, EditCollectionRequest, \
    GetDeltaApplicableMetricTypesResponse, BatchRunMetricsRequest, BatchRunMetricsResponse, \
    GetSourceListResponse, Empty, Source, CreateSourceRequest, BatchMetricConfigRequest, \
    BatchMetricConfigResponse, Table, ComparisonTableInfo, GetComparisonTableInfosResponse, RunComparisonTableResponse, \
    GetComparisonTableInfosRequest, GetIssuesRequest, Issue, GetIssuesResponse, UpdateIssueRequest, \
    IssueStatusUpdate, IssueStatus, MetricRunLabel, User, UpdateIssueResponse, \
    GetTableComparisonMetricGroupInfoRequest, GetTableComparisonMetricGroupInfoResponse, ComparisonMetricGroup, \
    SinglePathParamMetricIdRequest

# create logger
from bigeye_sdk.log import get_logger

log = get_logger(__file__)


class GeneratedDatawatchClient(abc.ABC):
    """TODO: Should only contain methods generated from protobuf."""

    def _call_datawatch(self, method: Method, url, body: str = None):
        url = url.replace('//', '/')
        return self._call_datawatch_impl(method=method, url=url, body=body)

    @abc.abstractmethod
    def _call_datawatch_impl(self, method: Method, url, body: str = None):
        """Each implementation must override this."""
        pass

    def get_dataset(self, warehouse_id: int, schema_name: str) -> List[dict]:
        """
        Provides advanced dataset details for a schema but returns a list of dictionaries instead of an list of Table
        objects.

        Args:
            warehouse_id:
            schema_name:

        Returns: list of dictionaries containing advanced details about all datasets in a schema.

        """
        url = f"/dataset/tables/{warehouse_id}/{schema_name}"

        return self._call_datawatch(Method.GET, url)

    def get_tables(self,
                   *,
                   warehouse_id: List[int] = [],
                   schema: List[str] = [],
                   table_name: List[str] = [],
                   ids: List[int] = [],
                   schema_id: List[int] = []) -> TableList:
        url = f"/api/v1/tables?{encode_url_params(locals(), remove_keys=['api_conf'])}"
        log.info('Getting warehouse tables.')
        log.info(url)
        response = self._call_datawatch(Method.GET, url)
        tables = TableList().from_dict(response)
        return tables

    def get_table_ids(self,
                      warehouse_id: List[int] = [],
                      schemas: List[str] = [],
                      table_name: List[str] = [],
                      ids: List[int] = [],
                      schema_id: List[int] = []) -> List[int]:
        return [t.id for t in self.get_tables(warehouse_id=warehouse_id, schema=schemas, table_name=table_name,
                                              ids=ids, schema_id=schema_id).tables]

    def rebuild(self, warehouse_id: int, schema_name: str = None):
        """
        TODO: switch to returning an object from the protobuf.

        Args:
            warehouse_id:
            schema_name:

        Returns: list of metrics.

        """
        url = f'/dataset/rebuild/{warehouse_id}'

        if schema_name is not None:
            url = url + f'/{schema_name}'

        return self._call_datawatch(Method.GET, url)

    def get_table_profile(self, table_id: int) -> ColumnMetricProfileList:
        url = f'/api/v1/tables/profile/{table_id}'
        return ColumnMetricProfileList().from_dict(self._call_datawatch(Method.GET, url))

    def batch_delete_metrics(self, metric_ids: List[int]):
        body = json.dumps({"metricIds": metric_ids})
        log.info(f'Deleting metrics: {metric_ids}')
        url = f'/statistics'
        return self._call_datawatch(Method.DELETE, url, body)

    def accept_autometrics(
            self, *, metric_ids: List[int] = [], lookback_days: int = 7
    ) -> AutometricAcceptResponse:
        """Batch accept autometrics"""

        request = AutometricAcceptRequest()
        request.metric_ids = metric_ids
        request.lookback_days = lookback_days

        url = f'/api/v1/metrics/autometrics/accept'
        body = request.to_json()
        log.info(f'Deploying autometrics: {url} -- {body}')
        r = self._call_datawatch(Method.POST, url, body)
        return AutometricAcceptResponse().from_dict(r)

    def get_metric_configuration(
        self, *, metric_id: int = 0
    ) -> MetricConfiguration:
        """Get metric configuration"""

        url = f'/api/v1/metrics/{metric_id}'

        r = self._call_datawatch(Method.GET, url)
        return MetricConfiguration().from_dict(r)

    def search_metric_configuration(
            self,
            *,
            ids: List[int] = [],
            warehouse_ids: List[int] = [],
            table_ids: List[int] = [],
            table_name: str = "",
            status: str = "",
            muted: bool = False,
    ) -> List[MetricConfiguration]:
        """Search metric configurations"""

        request = SearchMetricConfigurationRequest()
        request.ids = ids
        request.warehouse_ids = warehouse_ids
        request.table_ids = table_ids
        request.table_name = table_name
        request.status = status
        request.muted = muted

        url = f'/api/v1/metrics?{encode_url_params(d=request.to_dict())}'

        response = self._call_datawatch(Method.GET, url=url)

        return [MetricConfiguration().from_dict(m) for m in BatchGetMetricResponse(metrics=response).metrics]

    def get_metric_info_batch_post(
            self,
            *,
            metric_ids: List[int] = [],
            warehouse_ids: List[int] = [],
            table_ids: List[int] = [],
            table_name: str = "",
            status: str = "",
            metric_creation_states: List[MetricCreationState] = [],
            muted: ThreeLeggedBoolean = 0,
            page_size: int = 0,
            page_cursor: str = "",
            sort_field: MetricSortField = 0,
            schema_name: str = "",
            column_ids: List[int] = [],
            search: str = "",
            sort_direction: SortDirection = 0,
    ) -> MetricInfoList:
        """Get batch metric information"""

        request = GetMetricInfoListRequest()
        request.metric_ids = metric_ids
        request.warehouse_ids = warehouse_ids
        request.table_ids = table_ids
        request.table_name = table_name
        request.status = status
        request.metric_creation_states = metric_creation_states
        request.muted = muted
        request.page_size = page_size
        request.page_cursor = page_cursor
        request.sort_field = sort_field
        request.schema_name = schema_name
        request.column_ids = column_ids
        request.search = search
        request.sort_direction = sort_direction

        url = '/api/v1/metrics/info'

        response = self._call_datawatch(Method.POST, url=url, body=request.to_json())

        mil_current = MetricInfoList().from_dict(response)
        mil_return = MetricInfoList()

        while mil_current.pagination_info.next_cursor:
            mil_return.metrics.extend(mil_current.metrics)
            request.page_cursor = mil_current.pagination_info.next_cursor
            response = self._call_datawatch(Method.POST, url=url, body=request.to_json())
            mil_current = MetricInfoList().from_dict(response)

        return MetricInfoList().from_dict(response)

    def get_existing_metric(self,
                            warehouse_id: int, table: Table, column_name: str, user_defined_name: str,
                            metric_name: str, group_by: List[str], filters: List[str]):
        """
        Get an existing metric by name and group_by.
        """
        metrics: List[MetricConfiguration] = self.search_metric_configuration(warehouse_ids=[warehouse_id],
                                                                              table_ids=[table.id])

        for m in metrics:
            if is_same_metric(m, metric_name, user_defined_name, group_by, filters) \
                    and is_same_column_metric(m, column_name):
                return m
        return None

    def backfill_metric(
            self,
            *,
            metric_ids: List[int] = [],
            backfill_range: Optional["TimeRange"] = None,
    ) -> MetricBackfillResponse:
        """
        Runs metrics for past data and returns the API response.  Destructive.
        :param metric_ids: list of metric ids to run.
        :param backfill_range: time range for metrics to be run.
        :return: MetricBackfillResponse object.
        """

        request = MetricBackfillRequest()
        request.metric_ids = metric_ids
        if backfill_range is not None:
            request.backfill_range = backfill_range

        url = "/api/v1/metrics/backfill"

        response = self._call_datawatch(Method.POST, url=url, body=request.to_json())

        return MetricBackfillResponse().from_dict(response)

    def get_collections(self) -> GetCollectionsResponse:
        url = "/api/v1/collections/"
        log.info(url)
        response = self._call_datawatch(Method.GET, url=url)
        return GetCollectionsResponse().from_dict(response)

    def get_collection(self, collection_id: int) -> GetCollectionResponse:
        url = f"/api/v1/collections/{collection_id}"
        log.info(url)
        response = self._call_datawatch(Method.GET, url=url)
        return GetCollectionResponse().from_dict(response)

    def create_collection(self, collection: Collection) -> EditCollectionResponse:
        url = f"/api/v1/collections"

        request: EditCollectionRequest = EditCollectionRequest()
        request.collection_name = collection.name
        request.description = collection.description
        request.metric_ids = collection.metric_ids
        request.notification_channels = collection.notification_channels
        request.muted_until_timestamp = collection.muted_until_timestamp

        log.info(f'Query: {url}; Body: {request.to_json()}')

        response = self._call_datawatch(Method.POST, url=url, body=request.to_json())

        return EditCollectionResponse().from_dict(response)

    def update_collection(self, collection: Collection) -> EditCollectionResponse:
        url = f"/api/v1/collections"

        request: EditCollectionRequest = EditCollectionRequest()
        request.collection_name = collection.name
        request.description = collection.description
        request.metric_ids = collection.metric_ids
        request.notification_channels = collection.notification_channels
        request.muted_until_timestamp = collection.muted_until_timestamp

        log.info(f'Query: {url}; Body: {request.to_json()}')

        response = self._call_datawatch(Method.PUT, url=url, body=request.to_json())

        return EditCollectionResponse().from_dict(response)

    def upsert_metric_to_collection(self, collection_id: int,
                                    add_metric_ids: Union[int, List[int]]) -> EditCollectionResponse:

        if type(add_metric_ids) == int:
            mids = list(add_metric_ids)
        else:
            mids = add_metric_ids

        collection: Collection = self.get_collection(collection_id=collection_id).collection

        for mid in mids:
            collection.metric_ids.append(mid)

        return self.update_collection(collection=collection)

    def get_delta_applicable_metric_types(
            self, *, table_id: int = 0
    ) -> GetDeltaApplicableMetricTypesResponse:
        """
        Get list of metrics applicable for deltas
        Args:
            table_id: source table id

        Returns: list of metrics applicable for deltas.

        """

        url = f"/api/v1/tables/{table_id}/delta-applicable-metric-types"

        response = self._call_datawatch(Method.GET, url)

        return GetDeltaApplicableMetricTypesResponse().from_dict(response)

    def run_a_delta(self, *, delta_id: int) -> ComparisonTableInfo:
        """

        Args:
            delta_id: Required.  The ID of the delta to run

        Returns:  ComparisonTableInfo

        """

        url = f"/api/v1/metrics/comparisons/tables/run/{delta_id}"
        response = self._call_datawatch(Method.GET, url)

        return RunComparisonTableResponse().from_dict(response).comparison_table_info

    def get_delta_information(self, *, delta_ids: List[int],
                              exclude_comparison_metrics: bool = False) -> List[ComparisonTableInfo]:
        """

            Args:
                delta_ids: Required.  The delta ID or IDs.
                exclude_comparison_metrics: Optional. Whether to include the list of ComparisonMetricInfos

            Returns:  List[ComparisonTableInfo]

        """

        url = "/api/v1/metrics/comparisons/tables/info"
        request = GetComparisonTableInfosRequest(delta_ids, exclude_comparison_metrics)
        response = self._call_datawatch(Method.POST, url, request.to_json())

        return GetComparisonTableInfosResponse().from_dict(response).comparison_table_infos

    def get_delta_groups_information(self, *, comparison_metric_id: int) -> List[ComparisonMetricGroup]:
        """

            Args:
                comparison_metric_id: Required.  The ID for a delta with grouped by columns.

            Returns:  List[ComparisonMetricGroup]

        """

        url = f"/api/v1/metrics/comparisons/metrics/{comparison_metric_id}/groups/info"
        request = GetTableComparisonMetricGroupInfoRequest(comparison_metric_id)
        response = self._call_datawatch(Method.GET, url, request.to_json())

        return GetTableComparisonMetricGroupInfoResponse().from_dict(response).group_state

    def run_metric_batch(
            self, *, metric_ids: List[int] = []
    ) -> BatchRunMetricsResponse:
        """Batch run metrics"""

        request = BatchRunMetricsRequest()
        request.metric_ids = metric_ids

        url = '/api/v1/metrics/run/batch'

        response = self._call_datawatch(Method.POST, url, request.to_json())

        return BatchRunMetricsResponse().from_dict(response)

    def get_sources(self) -> GetSourceListResponse:
        """Get sources"""
        url = "/api/v1/sources/fetch"
        request = Empty()

        response = self._call_datawatch(Method.POST, url, request.to_json())

        return GetSourceListResponse().from_dict(response)

    def edit_metric(self, metric_configuration: MetricConfiguration = None) -> BatchMetricConfigResponse:
        """
        TODO: Only supporting 1 metric because of weird defaults and required fields.
        Args:
            metric_configuration:

        Returns:

        """
        url = "/api/v1/metrics/batch"

        request = BatchMetricConfigRequest()
        request.metric_ids = [metric_configuration.id]

        request.metric_configuration = metric_configuration
        request_json = request.to_json()

        response = self._call_datawatch(Method.PUT, url, request_json)

        return BatchMetricConfigResponse().from_dict(response)

    def create_source(self, request: CreateSourceRequest) -> Source:

        url = 'api/v1/sources'

        response = self._call_datawatch(Method.POST, url, request.to_json())
        source = Source().from_dict(value=response.json()['source'])
        log.info(f'Source {source.name} created with warehouse ID: {source.id}')
        return source

    def delete_metric(self, *, metric_id: int):
        """Delete metric"""

        url = f'/api/v1/metrics/{metric_id}'

        self._call_datawatch(Method.DELETE, url)

    def delete_source(self, warehouse_id: int):

        url = f'/api/v1/sources/{warehouse_id}'

        self._call_datawatch(Method.DELETE, url)
        log.info(f'Begin delete for warehouse ID: {warehouse_id}')

    def get_issues(
            self,
            *,
            warehouse_ids: List[int] = [],
            schemas: List[str] = [],
            metric_ids: List[int] = [],
            sla_ids: List[int] = [],
            issue_ids: List[int] = []) -> List[Issue]:

        url = '/api/v1/issues/fetch'

        request = GetIssuesRequest()
        request.warehouse_ids = warehouse_ids
        request.schema_names = schemas
        request.metric_ids = metric_ids
        request.sla_ids = sla_ids
        request.issue_ids = issue_ids

        response = self._call_datawatch(Method.POST, url, request.to_json())
        return GetIssuesResponse().from_dict(response).issue

    def get_issue(self, issue_id: int) -> Issue:
        return self.get_issues(issue_ids=[issue_id])[0]

    def update_issue(self,
                     *,
                     issue_id: int,
                     issue_status: str,
                     updated_by: str,
                     update_message: str,
                     closing_label: Optional[str]) -> Issue:

        url = f'/api/v1/issues/{issue_id}'

        status = IssueStatus.from_string(f'ISSUE_STATUS_{issue_status.upper()}')
        isu = IssueStatusUpdate()
        isu.updated_by = User(name=updated_by)
        isu.message = update_message
        isu.new_status = status

        if status == IssueStatus.ISSUE_STATUS_CLOSED:
            label = MetricRunLabel.from_string(f'METRIC_RUN_LABEL_{closing_label.upper()}')
            isu.closing_label = label

        request = UpdateIssueRequest(status_update=isu)

        response = self._call_datawatch(Method.PUT, url, request.to_json())
        return UpdateIssueResponse().from_dict(response).issue
