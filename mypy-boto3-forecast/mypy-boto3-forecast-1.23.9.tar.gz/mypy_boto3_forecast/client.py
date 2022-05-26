"""
Type annotations for forecast service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_forecast.client import ForecastServiceClient

    session = Session()
    client: ForecastServiceClient = session.client("forecast")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .literals import (
    AutoMLOverrideStrategyType,
    DatasetTypeType,
    DomainType,
    OptimizationMetricType,
)
from .paginator import (
    ListDatasetGroupsPaginator,
    ListDatasetImportJobsPaginator,
    ListDatasetsPaginator,
    ListExplainabilitiesPaginator,
    ListExplainabilityExportsPaginator,
    ListForecastExportJobsPaginator,
    ListForecastsPaginator,
    ListMonitorEvaluationsPaginator,
    ListMonitorsPaginator,
    ListPredictorBacktestExportJobsPaginator,
    ListPredictorsPaginator,
)
from .type_defs import (
    CreateAutoPredictorResponseTypeDef,
    CreateDatasetGroupResponseTypeDef,
    CreateDatasetImportJobResponseTypeDef,
    CreateDatasetResponseTypeDef,
    CreateExplainabilityExportResponseTypeDef,
    CreateExplainabilityResponseTypeDef,
    CreateForecastExportJobResponseTypeDef,
    CreateForecastResponseTypeDef,
    CreateMonitorResponseTypeDef,
    CreatePredictorBacktestExportJobResponseTypeDef,
    CreatePredictorResponseTypeDef,
    DataConfigTypeDef,
    DataDestinationTypeDef,
    DataSourceTypeDef,
    DescribeAutoPredictorResponseTypeDef,
    DescribeDatasetGroupResponseTypeDef,
    DescribeDatasetImportJobResponseTypeDef,
    DescribeDatasetResponseTypeDef,
    DescribeExplainabilityExportResponseTypeDef,
    DescribeExplainabilityResponseTypeDef,
    DescribeForecastExportJobResponseTypeDef,
    DescribeForecastResponseTypeDef,
    DescribeMonitorResponseTypeDef,
    DescribePredictorBacktestExportJobResponseTypeDef,
    DescribePredictorResponseTypeDef,
    EncryptionConfigTypeDef,
    EvaluationParametersTypeDef,
    ExplainabilityConfigTypeDef,
    FeaturizationConfigTypeDef,
    FilterTypeDef,
    GetAccuracyMetricsResponseTypeDef,
    HyperParameterTuningJobConfigTypeDef,
    InputDataConfigTypeDef,
    ListDatasetGroupsResponseTypeDef,
    ListDatasetImportJobsResponseTypeDef,
    ListDatasetsResponseTypeDef,
    ListExplainabilitiesResponseTypeDef,
    ListExplainabilityExportsResponseTypeDef,
    ListForecastExportJobsResponseTypeDef,
    ListForecastsResponseTypeDef,
    ListMonitorEvaluationsResponseTypeDef,
    ListMonitorsResponseTypeDef,
    ListPredictorBacktestExportJobsResponseTypeDef,
    ListPredictorsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    MonitorConfigTypeDef,
    SchemaTypeDef,
    TagTypeDef,
    TimeAlignmentBoundaryTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("ForecastServiceClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    ClientError: Type[BotocoreClientError]
    InvalidInputException: Type[BotocoreClientError]
    InvalidNextTokenException: Type[BotocoreClientError]
    LimitExceededException: Type[BotocoreClientError]
    ResourceAlreadyExistsException: Type[BotocoreClientError]
    ResourceInUseException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]


class ForecastServiceClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        ForecastServiceClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#can_paginate)
        """

    def create_auto_predictor(
        self,
        *,
        PredictorName: str,
        ForecastHorizon: int = ...,
        ForecastTypes: Sequence[str] = ...,
        ForecastDimensions: Sequence[str] = ...,
        ForecastFrequency: str = ...,
        DataConfig: DataConfigTypeDef = ...,
        EncryptionConfig: EncryptionConfigTypeDef = ...,
        ReferencePredictorArn: str = ...,
        OptimizationMetric: OptimizationMetricType = ...,
        ExplainPredictor: bool = ...,
        Tags: Sequence[TagTypeDef] = ...,
        MonitorConfig: MonitorConfigTypeDef = ...,
        TimeAlignmentBoundary: TimeAlignmentBoundaryTypeDef = ...
    ) -> CreateAutoPredictorResponseTypeDef:
        """
        Creates an Amazon Forecast predictor.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_auto_predictor)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_auto_predictor)
        """

    def create_dataset(
        self,
        *,
        DatasetName: str,
        Domain: DomainType,
        DatasetType: DatasetTypeType,
        Schema: SchemaTypeDef,
        DataFrequency: str = ...,
        EncryptionConfig: EncryptionConfigTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateDatasetResponseTypeDef:
        """
        Creates an Amazon Forecast dataset.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_dataset)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_dataset)
        """

    def create_dataset_group(
        self,
        *,
        DatasetGroupName: str,
        Domain: DomainType,
        DatasetArns: Sequence[str] = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateDatasetGroupResponseTypeDef:
        """
        Creates a dataset group, which holds a collection of related datasets.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_dataset_group)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_dataset_group)
        """

    def create_dataset_import_job(
        self,
        *,
        DatasetImportJobName: str,
        DatasetArn: str,
        DataSource: DataSourceTypeDef,
        TimestampFormat: str = ...,
        TimeZone: str = ...,
        UseGeolocationForTimeZone: bool = ...,
        GeolocationFormat: str = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateDatasetImportJobResponseTypeDef:
        """
        Imports your training data to an Amazon Forecast dataset.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_dataset_import_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_dataset_import_job)
        """

    def create_explainability(
        self,
        *,
        ExplainabilityName: str,
        ResourceArn: str,
        ExplainabilityConfig: ExplainabilityConfigTypeDef,
        DataSource: DataSourceTypeDef = ...,
        Schema: SchemaTypeDef = ...,
        EnableVisualization: bool = ...,
        StartDateTime: str = ...,
        EndDateTime: str = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateExplainabilityResponseTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_explainability)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_explainability)
        """

    def create_explainability_export(
        self,
        *,
        ExplainabilityExportName: str,
        ExplainabilityArn: str,
        Destination: DataDestinationTypeDef,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateExplainabilityExportResponseTypeDef:
        """
        Exports an Explainability resource created by the  CreateExplainability
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_explainability_export)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_explainability_export)
        """

    def create_forecast(
        self,
        *,
        ForecastName: str,
        PredictorArn: str,
        ForecastTypes: Sequence[str] = ...,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateForecastResponseTypeDef:
        """
        Creates a forecast for each item in the `TARGET_TIME_SERIES` dataset that was
        used to train the predictor.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_forecast)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_forecast)
        """

    def create_forecast_export_job(
        self,
        *,
        ForecastExportJobName: str,
        ForecastArn: str,
        Destination: DataDestinationTypeDef,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreateForecastExportJobResponseTypeDef:
        """
        Exports a forecast created by the  CreateForecast operation to your Amazon
        Simple Storage Service (Amazon S3) bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_forecast_export_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_forecast_export_job)
        """

    def create_monitor(
        self, *, MonitorName: str, ResourceArn: str, Tags: Sequence[TagTypeDef] = ...
    ) -> CreateMonitorResponseTypeDef:
        """
        Creates a predictor monitor resource for an existing auto predictor.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_monitor)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_monitor)
        """

    def create_predictor(
        self,
        *,
        PredictorName: str,
        ForecastHorizon: int,
        InputDataConfig: InputDataConfigTypeDef,
        FeaturizationConfig: FeaturizationConfigTypeDef,
        AlgorithmArn: str = ...,
        ForecastTypes: Sequence[str] = ...,
        PerformAutoML: bool = ...,
        AutoMLOverrideStrategy: AutoMLOverrideStrategyType = ...,
        PerformHPO: bool = ...,
        TrainingParameters: Mapping[str, str] = ...,
        EvaluationParameters: EvaluationParametersTypeDef = ...,
        HPOConfig: HyperParameterTuningJobConfigTypeDef = ...,
        EncryptionConfig: EncryptionConfigTypeDef = ...,
        Tags: Sequence[TagTypeDef] = ...,
        OptimizationMetric: OptimizationMetricType = ...
    ) -> CreatePredictorResponseTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_predictor)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_predictor)
        """

    def create_predictor_backtest_export_job(
        self,
        *,
        PredictorBacktestExportJobName: str,
        PredictorArn: str,
        Destination: DataDestinationTypeDef,
        Tags: Sequence[TagTypeDef] = ...
    ) -> CreatePredictorBacktestExportJobResponseTypeDef:
        """
        Exports backtest forecasts and accuracy metrics generated by the
        CreateAutoPredictor or  CreatePredictor operations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.create_predictor_backtest_export_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#create_predictor_backtest_export_job)
        """

    def delete_dataset(self, *, DatasetArn: str) -> None:
        """
        Deletes an Amazon Forecast dataset that was created using the
        [CreateDataset](https://docs.aws.amazon.com/forecast/latest/dg/API_CreateDataset.html)_
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_dataset)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_dataset)
        """

    def delete_dataset_group(self, *, DatasetGroupArn: str) -> None:
        """
        Deletes a dataset group created using the
        [CreateDatasetGroup](https://docs.aws.amazon.com/forecast/latest/dg/API_CreateDatasetGroup.html)_
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_dataset_group)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_dataset_group)
        """

    def delete_dataset_import_job(self, *, DatasetImportJobArn: str) -> None:
        """
        Deletes a dataset import job created using the
        [CreateDatasetImportJob](https://docs.aws.amazon.com/forecast/latest/dg/API_CreateDatasetImportJob.html)_
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_dataset_import_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_dataset_import_job)
        """

    def delete_explainability(self, *, ExplainabilityArn: str) -> None:
        """
        Deletes an Explainability resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_explainability)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_explainability)
        """

    def delete_explainability_export(self, *, ExplainabilityExportArn: str) -> None:
        """
        Deletes an Explainability export.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_explainability_export)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_explainability_export)
        """

    def delete_forecast(self, *, ForecastArn: str) -> None:
        """
        Deletes a forecast created using the  CreateForecast operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_forecast)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_forecast)
        """

    def delete_forecast_export_job(self, *, ForecastExportJobArn: str) -> None:
        """
        Deletes a forecast export job created using the  CreateForecastExportJob
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_forecast_export_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_forecast_export_job)
        """

    def delete_monitor(self, *, MonitorArn: str) -> None:
        """
        Deletes a monitor resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_monitor)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_monitor)
        """

    def delete_predictor(self, *, PredictorArn: str) -> None:
        """
        Deletes a predictor created using the  DescribePredictor or  CreatePredictor
        operations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_predictor)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_predictor)
        """

    def delete_predictor_backtest_export_job(self, *, PredictorBacktestExportJobArn: str) -> None:
        """
        Deletes a predictor backtest export job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_predictor_backtest_export_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_predictor_backtest_export_job)
        """

    def delete_resource_tree(self, *, ResourceArn: str) -> None:
        """
        Deletes an entire resource tree.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.delete_resource_tree)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#delete_resource_tree)
        """

    def describe_auto_predictor(self, *, PredictorArn: str) -> DescribeAutoPredictorResponseTypeDef:
        """
        Describes a predictor created using the CreateAutoPredictor operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_auto_predictor)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_auto_predictor)
        """

    def describe_dataset(self, *, DatasetArn: str) -> DescribeDatasetResponseTypeDef:
        """
        Describes an Amazon Forecast dataset created using the
        [CreateDataset](https://docs.aws.amazon.com/forecast/latest/dg/API_CreateDataset.html)_
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_dataset)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_dataset)
        """

    def describe_dataset_group(
        self, *, DatasetGroupArn: str
    ) -> DescribeDatasetGroupResponseTypeDef:
        """
        Describes a dataset group created using the
        [CreateDatasetGroup](https://docs.aws.amazon.com/forecast/latest/dg/API_CreateDatasetGroup.html)_
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_dataset_group)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_dataset_group)
        """

    def describe_dataset_import_job(
        self, *, DatasetImportJobArn: str
    ) -> DescribeDatasetImportJobResponseTypeDef:
        """
        Describes a dataset import job created using the
        [CreateDatasetImportJob](https://docs.aws.amazon.com/forecast/latest/dg/API_CreateDatasetImportJob.html)_
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_dataset_import_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_dataset_import_job)
        """

    def describe_explainability(
        self, *, ExplainabilityArn: str
    ) -> DescribeExplainabilityResponseTypeDef:
        """
        Describes an Explainability resource created using the  CreateExplainability
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_explainability)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_explainability)
        """

    def describe_explainability_export(
        self, *, ExplainabilityExportArn: str
    ) -> DescribeExplainabilityExportResponseTypeDef:
        """
        Describes an Explainability export created using the  CreateExplainabilityExport
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_explainability_export)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_explainability_export)
        """

    def describe_forecast(self, *, ForecastArn: str) -> DescribeForecastResponseTypeDef:
        """
        Describes a forecast created using the  CreateForecast operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_forecast)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_forecast)
        """

    def describe_forecast_export_job(
        self, *, ForecastExportJobArn: str
    ) -> DescribeForecastExportJobResponseTypeDef:
        """
        Describes a forecast export job created using the  CreateForecastExportJob
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_forecast_export_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_forecast_export_job)
        """

    def describe_monitor(self, *, MonitorArn: str) -> DescribeMonitorResponseTypeDef:
        """
        Describes a monitor resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_monitor)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_monitor)
        """

    def describe_predictor(self, *, PredictorArn: str) -> DescribePredictorResponseTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_predictor)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_predictor)
        """

    def describe_predictor_backtest_export_job(
        self, *, PredictorBacktestExportJobArn: str
    ) -> DescribePredictorBacktestExportJobResponseTypeDef:
        """
        Describes a predictor backtest export job created using the
        CreatePredictorBacktestExportJob operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.describe_predictor_backtest_export_job)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#describe_predictor_backtest_export_job)
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

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#generate_presigned_url)
        """

    def get_accuracy_metrics(self, *, PredictorArn: str) -> GetAccuracyMetricsResponseTypeDef:
        """
        Provides metrics on the accuracy of the models that were trained by the
        CreatePredictor operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_accuracy_metrics)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_accuracy_metrics)
        """

    def list_dataset_groups(
        self, *, NextToken: str = ..., MaxResults: int = ...
    ) -> ListDatasetGroupsResponseTypeDef:
        """
        Returns a list of dataset groups created using the
        [CreateDatasetGroup](https://docs.aws.amazon.com/forecast/latest/dg/API_CreateDatasetGroup.html)_
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_dataset_groups)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_dataset_groups)
        """

    def list_dataset_import_jobs(
        self, *, NextToken: str = ..., MaxResults: int = ..., Filters: Sequence[FilterTypeDef] = ...
    ) -> ListDatasetImportJobsResponseTypeDef:
        """
        Returns a list of dataset import jobs created using the
        [CreateDatasetImportJob](https://docs.aws.amazon.com/forecast/latest/dg/API_CreateDatasetImportJob.html)_
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_dataset_import_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_dataset_import_jobs)
        """

    def list_datasets(
        self, *, NextToken: str = ..., MaxResults: int = ...
    ) -> ListDatasetsResponseTypeDef:
        """
        Returns a list of datasets created using the
        [CreateDataset](https://docs.aws.amazon.com/forecast/latest/dg/API_CreateDataset.html)_
        operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_datasets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_datasets)
        """

    def list_explainabilities(
        self, *, NextToken: str = ..., MaxResults: int = ..., Filters: Sequence[FilterTypeDef] = ...
    ) -> ListExplainabilitiesResponseTypeDef:
        """
        Returns a list of Explainability resources created using the
        CreateExplainability operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_explainabilities)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_explainabilities)
        """

    def list_explainability_exports(
        self, *, NextToken: str = ..., MaxResults: int = ..., Filters: Sequence[FilterTypeDef] = ...
    ) -> ListExplainabilityExportsResponseTypeDef:
        """
        Returns a list of Explainability exports created using the
        CreateExplainabilityExport operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_explainability_exports)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_explainability_exports)
        """

    def list_forecast_export_jobs(
        self, *, NextToken: str = ..., MaxResults: int = ..., Filters: Sequence[FilterTypeDef] = ...
    ) -> ListForecastExportJobsResponseTypeDef:
        """
        Returns a list of forecast export jobs created using the
        CreateForecastExportJob operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_forecast_export_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_forecast_export_jobs)
        """

    def list_forecasts(
        self, *, NextToken: str = ..., MaxResults: int = ..., Filters: Sequence[FilterTypeDef] = ...
    ) -> ListForecastsResponseTypeDef:
        """
        Returns a list of forecasts created using the  CreateForecast operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_forecasts)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_forecasts)
        """

    def list_monitor_evaluations(
        self,
        *,
        MonitorArn: str,
        NextToken: str = ...,
        MaxResults: int = ...,
        Filters: Sequence[FilterTypeDef] = ...
    ) -> ListMonitorEvaluationsResponseTypeDef:
        """
        Returns a list of the monitoring evaluation results and predictor events
        collected by the monitor resource during different windows of time.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_monitor_evaluations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_monitor_evaluations)
        """

    def list_monitors(
        self, *, NextToken: str = ..., MaxResults: int = ..., Filters: Sequence[FilterTypeDef] = ...
    ) -> ListMonitorsResponseTypeDef:
        """
        Returns a list of monitors created with the  CreateMonitor operation and
        CreateAutoPredictor operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_monitors)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_monitors)
        """

    def list_predictor_backtest_export_jobs(
        self, *, NextToken: str = ..., MaxResults: int = ..., Filters: Sequence[FilterTypeDef] = ...
    ) -> ListPredictorBacktestExportJobsResponseTypeDef:
        """
        Returns a list of predictor backtest export jobs created using the
        CreatePredictorBacktestExportJob operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_predictor_backtest_export_jobs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_predictor_backtest_export_jobs)
        """

    def list_predictors(
        self, *, NextToken: str = ..., MaxResults: int = ..., Filters: Sequence[FilterTypeDef] = ...
    ) -> ListPredictorsResponseTypeDef:
        """
        Returns a list of predictors created using the  CreateAutoPredictor or
        CreatePredictor operations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_predictors)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_predictors)
        """

    def list_tags_for_resource(self, *, ResourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Lists the tags for an Amazon Forecast resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#list_tags_for_resource)
        """

    def resume_resource(self, *, ResourceArn: str) -> None:
        """
        Resumes a stopped monitor resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.resume_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#resume_resource)
        """

    def stop_resource(self, *, ResourceArn: str) -> None:
        """
        Stops a resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.stop_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#stop_resource)
        """

    def tag_resource(self, *, ResourceArn: str, Tags: Sequence[TagTypeDef]) -> Dict[str, Any]:
        """
        Associates the specified tags to a resource with the specified `resourceArn`.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#tag_resource)
        """

    def untag_resource(self, *, ResourceArn: str, TagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Deletes the specified tags from a resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#untag_resource)
        """

    def update_dataset_group(
        self, *, DatasetGroupArn: str, DatasetArns: Sequence[str]
    ) -> Dict[str, Any]:
        """
        Replaces the datasets in a dataset group with the specified datasets.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.update_dataset_group)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#update_dataset_group)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_dataset_groups"]
    ) -> ListDatasetGroupsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_dataset_import_jobs"]
    ) -> ListDatasetImportJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_datasets"]) -> ListDatasetsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_explainabilities"]
    ) -> ListExplainabilitiesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_explainability_exports"]
    ) -> ListExplainabilityExportsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_forecast_export_jobs"]
    ) -> ListForecastExportJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_forecasts"]) -> ListForecastsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_monitor_evaluations"]
    ) -> ListMonitorEvaluationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_monitors"]) -> ListMonitorsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_predictor_backtest_export_jobs"]
    ) -> ListPredictorBacktestExportJobsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_predictors"]) -> ListPredictorsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html#ForecastService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_forecast/client/#get_paginator)
        """
