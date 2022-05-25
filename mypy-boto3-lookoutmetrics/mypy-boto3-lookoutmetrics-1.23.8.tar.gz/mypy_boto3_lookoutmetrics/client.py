"""
Type annotations for lookoutmetrics service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_lookoutmetrics.client import LookoutMetricsClient

    session = Session()
    client: LookoutMetricsClient = session.client("lookoutmetrics")
    ```
"""
from typing import Any, Dict, Mapping, Sequence, Type

from botocore.client import BaseClient, ClientMeta

from .literals import FrequencyType, RelationshipTypeType
from .type_defs import (
    ActionTypeDef,
    AnomalyDetectorConfigTypeDef,
    AnomalyGroupTimeSeriesFeedbackTypeDef,
    AnomalyGroupTimeSeriesTypeDef,
    AutoDetectionMetricSourceTypeDef,
    CreateAlertResponseTypeDef,
    CreateAnomalyDetectorResponseTypeDef,
    CreateMetricSetResponseTypeDef,
    DescribeAlertResponseTypeDef,
    DescribeAnomalyDetectionExecutionsResponseTypeDef,
    DescribeAnomalyDetectorResponseTypeDef,
    DescribeMetricSetResponseTypeDef,
    DetectMetricSetConfigResponseTypeDef,
    GetAnomalyGroupResponseTypeDef,
    GetFeedbackResponseTypeDef,
    GetSampleDataResponseTypeDef,
    ListAlertsResponseTypeDef,
    ListAnomalyDetectorsResponseTypeDef,
    ListAnomalyGroupRelatedMetricsResponseTypeDef,
    ListAnomalyGroupSummariesResponseTypeDef,
    ListAnomalyGroupTimeSeriesResponseTypeDef,
    ListMetricSetsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    MetricSourceTypeDef,
    MetricTypeDef,
    SampleDataS3SourceConfigTypeDef,
    TimestampColumnTypeDef,
    UpdateAnomalyDetectorResponseTypeDef,
    UpdateMetricSetResponseTypeDef,
)

__all__ = ("LookoutMetricsClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    TooManyRequestsException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class LookoutMetricsClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        LookoutMetricsClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#exceptions)
        """

    def activate_anomaly_detector(self, *, AnomalyDetectorArn: str) -> Dict[str, Any]:
        """
        Activates an anomaly detector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.activate_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#activate_anomaly_detector)
        """

    def back_test_anomaly_detector(self, *, AnomalyDetectorArn: str) -> Dict[str, Any]:
        """
        Runs a backtest for anomaly detection for the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.back_test_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#back_test_anomaly_detector)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#can_paginate)
        """

    def create_alert(
        self,
        *,
        AlertName: str,
        AlertSensitivityThreshold: int,
        AnomalyDetectorArn: str,
        Action: ActionTypeDef,
        AlertDescription: str = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateAlertResponseTypeDef:
        """
        Creates an alert for an anomaly detector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.create_alert)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#create_alert)
        """

    def create_anomaly_detector(
        self,
        *,
        AnomalyDetectorName: str,
        AnomalyDetectorConfig: AnomalyDetectorConfigTypeDef,
        AnomalyDetectorDescription: str = ...,
        KmsKeyArn: str = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateAnomalyDetectorResponseTypeDef:
        """
        Creates an anomaly detector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.create_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#create_anomaly_detector)
        """

    def create_metric_set(
        self,
        *,
        AnomalyDetectorArn: str,
        MetricSetName: str,
        MetricList: Sequence[MetricTypeDef],
        MetricSource: MetricSourceTypeDef,
        MetricSetDescription: str = ...,
        Offset: int = ...,
        TimestampColumn: TimestampColumnTypeDef = ...,
        DimensionList: Sequence[str] = ...,
        MetricSetFrequency: FrequencyType = ...,
        Timezone: str = ...,
        Tags: Mapping[str, str] = ...
    ) -> CreateMetricSetResponseTypeDef:
        """
        Creates a dataset.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.create_metric_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#create_metric_set)
        """

    def deactivate_anomaly_detector(self, *, AnomalyDetectorArn: str) -> Dict[str, Any]:
        """
        Deactivates an anomaly detector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.deactivate_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#deactivate_anomaly_detector)
        """

    def delete_alert(self, *, AlertArn: str) -> Dict[str, Any]:
        """
        Deletes an alert.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.delete_alert)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#delete_alert)
        """

    def delete_anomaly_detector(self, *, AnomalyDetectorArn: str) -> Dict[str, Any]:
        """
        Deletes a detector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.delete_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#delete_anomaly_detector)
        """

    def describe_alert(self, *, AlertArn: str) -> DescribeAlertResponseTypeDef:
        """
        Describes an alert.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.describe_alert)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#describe_alert)
        """

    def describe_anomaly_detection_executions(
        self,
        *,
        AnomalyDetectorArn: str,
        Timestamp: str = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> DescribeAnomalyDetectionExecutionsResponseTypeDef:
        """
        Returns information about the status of the specified anomaly detection jobs.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.describe_anomaly_detection_executions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#describe_anomaly_detection_executions)
        """

    def describe_anomaly_detector(
        self, *, AnomalyDetectorArn: str
    ) -> DescribeAnomalyDetectorResponseTypeDef:
        """
        Describes a detector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.describe_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#describe_anomaly_detector)
        """

    def describe_metric_set(self, *, MetricSetArn: str) -> DescribeMetricSetResponseTypeDef:
        """
        Describes a dataset.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.describe_metric_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#describe_metric_set)
        """

    def detect_metric_set_config(
        self,
        *,
        AnomalyDetectorArn: str,
        AutoDetectionMetricSource: AutoDetectionMetricSourceTypeDef
    ) -> DetectMetricSetConfigResponseTypeDef:
        """
        Detects an Amazon S3 dataset's file format, interval, and offset.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.detect_metric_set_config)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#detect_metric_set_config)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#generate_presigned_url)
        """

    def get_anomaly_group(
        self, *, AnomalyGroupId: str, AnomalyDetectorArn: str
    ) -> GetAnomalyGroupResponseTypeDef:
        """
        Returns details about a group of anomalous metrics.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.get_anomaly_group)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#get_anomaly_group)
        """

    def get_feedback(
        self,
        *,
        AnomalyDetectorArn: str,
        AnomalyGroupTimeSeriesFeedback: AnomalyGroupTimeSeriesTypeDef,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> GetFeedbackResponseTypeDef:
        """
        Get feedback for an anomaly group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.get_feedback)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#get_feedback)
        """

    def get_sample_data(
        self, *, S3SourceConfig: SampleDataS3SourceConfigTypeDef = ...
    ) -> GetSampleDataResponseTypeDef:
        """
        Returns a selection of sample records from an Amazon S3 datasource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.get_sample_data)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#get_sample_data)
        """

    def list_alerts(
        self, *, AnomalyDetectorArn: str = ..., NextToken: str = ..., MaxResults: int = ...
    ) -> ListAlertsResponseTypeDef:
        """
        Lists the alerts attached to a detector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.list_alerts)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#list_alerts)
        """

    def list_anomaly_detectors(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListAnomalyDetectorsResponseTypeDef:
        """
        Lists the detectors in the current AWS Region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.list_anomaly_detectors)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#list_anomaly_detectors)
        """

    def list_anomaly_group_related_metrics(
        self,
        *,
        AnomalyDetectorArn: str,
        AnomalyGroupId: str,
        RelationshipTypeFilter: RelationshipTypeType = ...,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListAnomalyGroupRelatedMetricsResponseTypeDef:
        """
        Returns a list of measures that are potential causes or effects of an anomaly
        group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.list_anomaly_group_related_metrics)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#list_anomaly_group_related_metrics)
        """

    def list_anomaly_group_summaries(
        self,
        *,
        AnomalyDetectorArn: str,
        SensitivityThreshold: int,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListAnomalyGroupSummariesResponseTypeDef:
        """
        Returns a list of anomaly groups.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.list_anomaly_group_summaries)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#list_anomaly_group_summaries)
        """

    def list_anomaly_group_time_series(
        self,
        *,
        AnomalyDetectorArn: str,
        AnomalyGroupId: str,
        MetricName: str,
        MaxResults: int = ...,
        NextToken: str = ...
    ) -> ListAnomalyGroupTimeSeriesResponseTypeDef:
        """
        Gets a list of anomalous metrics for a measure in an anomaly group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.list_anomaly_group_time_series)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#list_anomaly_group_time_series)
        """

    def list_metric_sets(
        self, *, AnomalyDetectorArn: str = ..., MaxResults: int = ..., NextToken: str = ...
    ) -> ListMetricSetsResponseTypeDef:
        """
        Lists the datasets in the current AWS Region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.list_metric_sets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#list_metric_sets)
        """

    def list_tags_for_resource(self, *, ResourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Gets a list of
        [tags](https://docs.aws.amazon.com/lookoutmetrics/latest/dev/detectors-
        tags.html)_ for a detector, dataset, or alert.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#list_tags_for_resource)
        """

    def put_feedback(
        self,
        *,
        AnomalyDetectorArn: str,
        AnomalyGroupTimeSeriesFeedback: AnomalyGroupTimeSeriesFeedbackTypeDef
    ) -> Dict[str, Any]:
        """
        Add feedback for an anomalous metric.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.put_feedback)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#put_feedback)
        """

    def tag_resource(self, *, ResourceArn: str, Tags: Mapping[str, str]) -> Dict[str, Any]:
        """
        Adds [tags](https://docs.aws.amazon.com/lookoutmetrics/latest/dev/detectors-
        tags.html)_ to a detector, dataset, or alert.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#tag_resource)
        """

    def untag_resource(self, *, ResourceArn: str, TagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes [tags](https://docs.aws.amazon.com/lookoutmetrics/latest/dev/detectors-
        tags.html)_ from a detector, dataset, or alert.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#untag_resource)
        """

    def update_anomaly_detector(
        self,
        *,
        AnomalyDetectorArn: str,
        KmsKeyArn: str = ...,
        AnomalyDetectorDescription: str = ...,
        AnomalyDetectorConfig: AnomalyDetectorConfigTypeDef = ...
    ) -> UpdateAnomalyDetectorResponseTypeDef:
        """
        Updates a detector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.update_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#update_anomaly_detector)
        """

    def update_metric_set(
        self,
        *,
        MetricSetArn: str,
        MetricSetDescription: str = ...,
        MetricList: Sequence[MetricTypeDef] = ...,
        Offset: int = ...,
        TimestampColumn: TimestampColumnTypeDef = ...,
        DimensionList: Sequence[str] = ...,
        MetricSetFrequency: FrequencyType = ...,
        MetricSource: MetricSourceTypeDef = ...
    ) -> UpdateMetricSetResponseTypeDef:
        """
        Updates a dataset.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lookoutmetrics.html#LookoutMetrics.Client.update_metric_set)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutmetrics/client/#update_metric_set)
        """
