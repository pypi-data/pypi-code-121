from __future__ import annotations

from abc import ABC
from typing import List, Optional, Union

import requests
from requests.auth import HTTPBasicAuth

from bigeye_sdk.client.enum import Method
from bigeye_sdk.client.generated_datawatch_client import GeneratedDatawatchClient
from bigeye_sdk.functions.delta_functions import infer_column_mappings
from bigeye_sdk.functions.metric_functions import set_default_model_type_for_threshold, is_freshness_metric
from bigeye_sdk.functions.table_functions import get_table_column_priority_first, table_has_metric_time

from bigeye_sdk.generated.com.torodata.models.generated import MetricCreationState, \
    MetricConfiguration, TimeInterval, Threshold, MetricType, MetricParameter, LookbackType, NotificationChannel, \
    CreateComparisonTableResponse, CreateComparisonTableRequest, \
    ComparisonTableConfiguration, IdAndDisplayName, ComparisonColumnMapping, \
    ColumnNamePair, Table

# create logger
from bigeye_sdk.log import get_logger
from bigeye_sdk.model.api_credentials import BasicAuthRequestLibApiConf
from bigeye_sdk.model.configuration_templates import SimpleUpsertMetricRequest

log = get_logger(__file__)


class DatawatchClient(GeneratedDatawatchClient, ABC):
    def set_table_metric_time(self,
                              column_id: int):
        """
        Sets metric time by column id for a particular table.
        :param column_id: column id
        :return:
        """
        url = f'/dataset/loadedDate/{column_id}'
        self._call_datawatch(method=Method.PUT, url=url, body=None)

    def unset_table_metric_time(self,
                                table: Table):
        """
        Sets metric time by column id for a particular table.
        :param table: Table object
        :return:
        """

        if table_has_metric_time(table):
            url = f'/dataset/loadedDate/{table.metric_time_column.id}'
            log.info(f'Removing metric time from table: {table.database_name}.{table.schema_name}.{table.name}')
            self._call_datawatch(method=Method.DELETE, url=url, body=None)
        else:
            log.info(f'Table has no metric time set: {table.database_name}.{table.schema_name}.{table.name}')

    def _set_table_metric_times(self,
                                column_names: List[str],
                                tables: List[Table],
                                replace: bool = False
                                ):
        """Sets metric times on tables if a column matches, by order priority, and column name in the list of column
        names.  If replace is true then it will reset metric time on tables then it will do a backfill of all metrics
        in that table."""
        for t in tables:
            has_metric_time = table_has_metric_time(t)
            if not has_metric_time or replace:
                c = get_table_column_priority_first(table=t, column_names=column_names)
                if c:
                    log.info(f'Setting column {c.name} in table {t.database_name}.{t.schema_name}.{t.name} '
                             f'as metric time.')
                    self.set_table_metric_time(c.id)

                    if has_metric_time and replace:
                        mcs = self.search_metric_configuration(table_ids=[t.id])
                        mids = [mc.id for mc in mcs]
                        log.info(f'Backfilling metrics after replace.  Metric IDs: {mids}')
                        self.backfill_metric(metric_ids=mids)
                else:
                    log.info(f'No column name provided can be identified in table '
                             f'{t.database_name}.{t.schema_name}.{t.name}')

    def set_table_metric_times(self,
                               column_names: List[str],
                               table_ids: List[int],
                               replace: bool = False):
        """
        Accepts a list of column_names that are acceptable metric time columns and applies for a list of tables.
        :param replace: replace metric time if exists.
        :param column_names: names of columns that would be acceptable metric time columns.
        :param table_ids: the tables to apply metric times on.
        :return:
        """
        tables = self.get_tables(ids=table_ids).tables
        self._set_table_metric_times(tables=tables, column_names=column_names, replace=replace)

    def set_source_metric_times(self,
                                column_names: List[str],
                                wid: int,
                                replace: bool = False):
        """
        Accepts a list of column_names that are acceptable metric time columns and applies for the whole source.
        :param replace: replace metric time if exists.
        :param column_names: names of columns that would be acceptable metric time columns.
        :param wid: the wid to apply metric times on.
        :return:
        """
        tables = self.get_tables(warehouse_id=[wid]).tables
        self._set_table_metric_times(tables=tables, column_names=column_names, replace=replace)

    def unset_table_metric_times(self,
                                 table_ids: List[int]):
        """
        Unsets metric time for specified table ids.
        :param table_ids: table ids.
        :return:
        """
        tables = self.get_tables(ids=table_ids).tables
        for t in tables:
            self.unset_table_metric_time(t)

    def unset_source_metric_times(self,
                                  wid: int):
        """
        Unsets metric time for all tables in warehouse.
        :param wid: warehouse id.
        :return:
        """
        tables = self.get_tables(warehouse_id=[wid]).tables
        for t in tables:
            self.unset_table_metric_time(t)

    def create_delta(
            self,
            name: str,
            source_table_id: int,
            target_table_id: int,
            column_mappings: List[ComparisonColumnMapping] = [],
            named_schedule: IdAndDisplayName = None,
            group_bys: List[ColumnNamePair] = [],
            source_filters: List[str] = [],
            target_filters: List[str] = [],
            comparison_table_configuration: Optional["ComparisonTableConfiguration"] = None,
    ) -> CreateComparisonTableResponse:
        """

        Args:
            name: Required.  Name of delta
            source_table_id:  Required.  table id for source table
            target_table_id: Required. Table id for target table
            column_mappings: Optional. If not exists then will infer from applicable table mappings based on column name.
            named_schedule: Optional.  No schedule if not exists
            group_bys: Optional.  No group bys if not exists
            source_filters: Optional.  No filters if not exists
            target_filters: Optional.  No filters if not exists
            comparison_table_configuration: Optional.

        Returns:  CreateComparisonTableResponse

        """

        if not column_mappings:
            source_metric_types = self.get_delta_applicable_metric_types(table_id=source_table_id).metric_types
            target_metric_types = self.get_delta_applicable_metric_types(table_id=target_table_id).metric_types
            column_mappings = infer_column_mappings(source_metric_types=source_metric_types,
                                                    target_metric_types=target_metric_types)

        url = '/api/v1/metrics/comparisons/tables'

        request = CreateComparisonTableRequest()
        if comparison_table_configuration is not None:
            request.comparison_table_configuration = comparison_table_configuration
        else:
            request.comparison_table_configuration.name = name
            request.comparison_table_configuration.source_table_id = source_table_id
            request.comparison_table_configuration.target_table_id = target_table_id
            request.comparison_table_configuration.column_mappings = column_mappings
            if named_schedule:
                request.comparison_table_configuration.named_schedule = named_schedule
            request.comparison_table_configuration.group_bys = group_bys
            request.comparison_table_configuration.source_filters = source_filters
            request.comparison_table_configuration.target_filters = target_filters
            request.comparison_table_configuration.target_table_id = target_table_id

        response = self._call_datawatch(Method.POST, url, request.to_json())

        return CreateComparisonTableResponse().from_dict(response)

    def upsert_metric(
            self,
            *,
            id: int = 0,
            schedule_frequency: Optional[TimeInterval] = None,
            filters: List[str] = [],
            group_bys: List[str] = [],
            thresholds: List[Threshold] = [],
            notification_channels: List[NotificationChannel] = [],
            warehouse_id: int = 0,
            dataset_id: int = 0,
            metric_type: Optional[MetricType] = None,
            parameters: List[MetricParameter] = [],
            lookback: Optional[TimeInterval] = None,
            lookback_type: LookbackType = 0,
            metric_creation_state: MetricCreationState = 0,
            grain_seconds: int = 0,
            muted_until_epoch_seconds: int = 0,
            name: str = "",
            description: str = "",
            metric_configuration: MetricConfiguration = None
    ) -> MetricConfiguration:
        """Create or update metric"""

        if metric_configuration:
            request = metric_configuration
        else:
            request = MetricConfiguration()
            request.id = id
            if schedule_frequency is not None:
                request.schedule_frequency = schedule_frequency
            request.filters = filters
            request.group_bys = group_bys
            if thresholds is not None:
                request.thresholds = set_default_model_type_for_threshold(thresholds)
            if notification_channels is not None:
                request.notification_channels = notification_channels
            request.warehouse_id = warehouse_id
            request.dataset_id = dataset_id
            if metric_type is not None:
                request.metric_type = metric_type
            if parameters is not None:
                request.parameters = parameters
            if lookback is not None:
                request.lookback = lookback
            request.lookback_type = lookback_type
            request.metric_creation_state = metric_creation_state
            request.grain_seconds = grain_seconds
            request.muted_until_epoch_seconds = muted_until_epoch_seconds
            request.name = name
            request.description = description

        set_default_model_type_for_threshold(request.thresholds)

        url = "/api/v1/metrics"

        response = self._call_datawatch(Method.POST, url=url, body=request.to_json())

        return MetricConfiguration().from_dict(response)

    def upsert_metric_from_simple_template(
            self,
            sumr: SimpleUpsertMetricRequest,
            target_warehouse_id: int = None,
            existing_metric_id: int = None
    ) -> int:
        """
        Takes a warehouse id and a SimpleUpsertMetricRequest, fills in reasonable defaults, and upserts a metric.
        :param target_warehouse_id: deploy to warehouse id.
        :param sumr: SimpleUpsertMetricRequest object
        :return: Id of the resulting metric.
        """
        # TODO Consider moving warehouse_id into sumr
        if sumr.metric_template.metric_name is None:
            raise Exception("Metric name must be present in configuration", sumr)

        tables = self.get_tables(warehouse_id=[target_warehouse_id], schema=[sumr.schema_name],
                                 table_name=[sumr.table_name]).tables

        if not tables:
            raise Exception(f"Could not find table: {sumr.schema_name}.{sumr.table_name}")
        elif len(tables) > 1:
            p = [f"Warehouse ID: {t.warehouse_id}.  FQ Table Name: " \
                 f"{t.database_name}.{t.schema_name}.{t.name}" for t in tables]
            raise Exception(f"Found multiple tables. {p}")
        else:
            table = tables[0]

        if existing_metric_id:
            existing_metric = self.get_metric_configuration(metric_id=existing_metric_id)
        else:
            existing_metric = self.get_existing_metric(
                warehouse_id=target_warehouse_id,
                table=table,
                column_name=sumr.column_name,
                user_defined_name=sumr.metric_template.user_defined_metric_name,
                metric_name=sumr.metric_template.metric_name,
                group_by=sumr.metric_template.group_by,
                filters=sumr.metric_template.filters)

        metric = sumr.build_upsert_request_object(target_table=table, existing_metric=existing_metric)

        should_backfill = False
        if metric.id is None and not is_freshness_metric(sumr.metric_template.metric_name):
            should_backfill = True

        result = self.upsert_metric(metric_configuration=metric)

        log.info("Create result: %s", result.to_json())
        if should_backfill and result.id is not None and table_has_metric_time(table):
            self.backfill_metric(metric_ids=[result.id])

        return result.id

    def regen_autometrics(self, table_id: int):
        url = f'/statistics/suggestions/{table_id}/queue'
        log.info(url)
        response = self._call_datawatch(Method.GET, url=url)

    def backfill_autothresholds(self,
                                metric_ids: List[int] = []):
        """
        Runs posthoc autothresholds for existing metric runs.  Does not run metrics for past data.  Not destructive.
        Will run sync.
        :param metric_ids: list of metric ids
        :return: none.
        """
        for metric_id in metric_ids:
            log.info(f"Backfilling autothreshold: {metric_id}")
            url = f"/statistics/backfillAutoThresholds/{metric_id}"
            response = self._call_datawatch(Method.GET, url=url)


class CoreDatawatchClient(DatawatchClient):
    """TODO: Rename to BasicAuthDatawatchClient"""

    def __init__(self, api_conf: BasicAuthRequestLibApiConf):
        self._base_url = api_conf.base_url
        self._auth = HTTPBasicAuth(api_conf.user, api_conf.password)
        pass

    def _call_datawatch_impl(self, method: Method, url, body: str = None):
        try:
            fq_url = f'{self._base_url}{url}'
            log.info(f'Request Type: {method.name}; URL: {fq_url}; Body: {body}')
            if method == Method.GET:
                response = requests.get(
                    fq_url,
                    auth=self._auth
                )
            elif method == Method.POST:
                response = requests.post(
                    fq_url,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    data=body,
                    auth=self._auth
                )
            elif method == Method.PUT:
                response = requests.put(
                    fq_url,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    data=body,
                    auth=self._auth
                )
            elif method == Method.DELETE:
                response = requests.delete(f'{self._base_url}{url}',
                                           headers={"Content-Type": "application/json", "Accept": "application/json"},
                                           data=body,
                                           auth=self._auth)
            else:
                raise Exception(f'Unsupported http method {method}')
        except Exception as e:
            log.error(f'Exception calling datawatch: {str(e)}')
            raise e
        else:
            log.info(f'Return Code: {response.status_code}')
            if response.status_code < 200 or response.status_code >= 300:
                log.error(f'Error code returned from datawatch: {str(response)}')
                raise Exception(response.text)
            else:
                # Not empty response
                if response.status_code != 204:
                    return response.json()
