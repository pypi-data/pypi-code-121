"""
Type annotations for personalize service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_personalize/type_defs/)

Usage::

    ```python
    from mypy_boto3_personalize.type_defs import AlgorithmImageTypeDef

    data: AlgorithmImageTypeDef = {...}
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import DomainType, IngestionModeType, ObjectiveSensitivityType, TrainingModeType

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AlgorithmImageTypeDef",
    "AutoMLConfigTypeDef",
    "AutoMLResultTypeDef",
    "BatchInferenceJobConfigTypeDef",
    "S3DataConfigTypeDef",
    "BatchInferenceJobSummaryTypeDef",
    "BatchSegmentJobSummaryTypeDef",
    "CampaignConfigTypeDef",
    "CampaignSummaryTypeDef",
    "CategoricalHyperParameterRangeTypeDef",
    "ContinuousHyperParameterRangeTypeDef",
    "TagTypeDef",
    "ResponseMetadataTypeDef",
    "DataSourceTypeDef",
    "RecommenderConfigTypeDef",
    "CreateSchemaRequestRequestTypeDef",
    "DatasetExportJobSummaryTypeDef",
    "DatasetGroupSummaryTypeDef",
    "DatasetGroupTypeDef",
    "DatasetImportJobSummaryTypeDef",
    "DatasetSchemaSummaryTypeDef",
    "DatasetSchemaTypeDef",
    "DatasetSummaryTypeDef",
    "DatasetTypeDef",
    "DefaultCategoricalHyperParameterRangeTypeDef",
    "DefaultContinuousHyperParameterRangeTypeDef",
    "DefaultIntegerHyperParameterRangeTypeDef",
    "DeleteCampaignRequestRequestTypeDef",
    "DeleteDatasetGroupRequestRequestTypeDef",
    "DeleteDatasetRequestRequestTypeDef",
    "DeleteEventTrackerRequestRequestTypeDef",
    "DeleteFilterRequestRequestTypeDef",
    "DeleteRecommenderRequestRequestTypeDef",
    "DeleteSchemaRequestRequestTypeDef",
    "DeleteSolutionRequestRequestTypeDef",
    "DescribeAlgorithmRequestRequestTypeDef",
    "DescribeBatchInferenceJobRequestRequestTypeDef",
    "DescribeBatchSegmentJobRequestRequestTypeDef",
    "DescribeCampaignRequestRequestTypeDef",
    "DescribeDatasetExportJobRequestRequestTypeDef",
    "DescribeDatasetGroupRequestRequestTypeDef",
    "DescribeDatasetImportJobRequestRequestTypeDef",
    "DescribeDatasetRequestRequestTypeDef",
    "DescribeEventTrackerRequestRequestTypeDef",
    "EventTrackerTypeDef",
    "DescribeFeatureTransformationRequestRequestTypeDef",
    "FeatureTransformationTypeDef",
    "DescribeFilterRequestRequestTypeDef",
    "FilterTypeDef",
    "DescribeRecipeRequestRequestTypeDef",
    "RecipeTypeDef",
    "DescribeRecommenderRequestRequestTypeDef",
    "DescribeSchemaRequestRequestTypeDef",
    "DescribeSolutionRequestRequestTypeDef",
    "DescribeSolutionVersionRequestRequestTypeDef",
    "EventTrackerSummaryTypeDef",
    "FilterSummaryTypeDef",
    "GetSolutionMetricsRequestRequestTypeDef",
    "HPOObjectiveTypeDef",
    "HPOResourceConfigTypeDef",
    "IntegerHyperParameterRangeTypeDef",
    "PaginatorConfigTypeDef",
    "ListBatchInferenceJobsRequestRequestTypeDef",
    "ListBatchSegmentJobsRequestRequestTypeDef",
    "ListCampaignsRequestRequestTypeDef",
    "ListDatasetExportJobsRequestRequestTypeDef",
    "ListDatasetGroupsRequestRequestTypeDef",
    "ListDatasetImportJobsRequestRequestTypeDef",
    "ListDatasetsRequestRequestTypeDef",
    "ListEventTrackersRequestRequestTypeDef",
    "ListFiltersRequestRequestTypeDef",
    "ListRecipesRequestRequestTypeDef",
    "RecipeSummaryTypeDef",
    "ListRecommendersRequestRequestTypeDef",
    "ListSchemasRequestRequestTypeDef",
    "ListSolutionVersionsRequestRequestTypeDef",
    "SolutionVersionSummaryTypeDef",
    "ListSolutionsRequestRequestTypeDef",
    "SolutionSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "OptimizationObjectiveTypeDef",
    "TunedHPOParamsTypeDef",
    "StartRecommenderRequestRequestTypeDef",
    "StopRecommenderRequestRequestTypeDef",
    "StopSolutionVersionCreationRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "BatchInferenceJobInputTypeDef",
    "BatchInferenceJobOutputTypeDef",
    "BatchSegmentJobInputTypeDef",
    "BatchSegmentJobOutputTypeDef",
    "DatasetExportJobOutputTypeDef",
    "CampaignUpdateSummaryTypeDef",
    "UpdateCampaignRequestRequestTypeDef",
    "CreateCampaignRequestRequestTypeDef",
    "CreateDatasetGroupRequestRequestTypeDef",
    "CreateDatasetRequestRequestTypeDef",
    "CreateEventTrackerRequestRequestTypeDef",
    "CreateFilterRequestRequestTypeDef",
    "CreateSolutionVersionRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateBatchInferenceJobResponseTypeDef",
    "CreateBatchSegmentJobResponseTypeDef",
    "CreateCampaignResponseTypeDef",
    "CreateDatasetExportJobResponseTypeDef",
    "CreateDatasetGroupResponseTypeDef",
    "CreateDatasetImportJobResponseTypeDef",
    "CreateDatasetResponseTypeDef",
    "CreateEventTrackerResponseTypeDef",
    "CreateFilterResponseTypeDef",
    "CreateRecommenderResponseTypeDef",
    "CreateSchemaResponseTypeDef",
    "CreateSolutionResponseTypeDef",
    "CreateSolutionVersionResponseTypeDef",
    "GetSolutionMetricsResponseTypeDef",
    "ListBatchInferenceJobsResponseTypeDef",
    "ListBatchSegmentJobsResponseTypeDef",
    "ListCampaignsResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "StartRecommenderResponseTypeDef",
    "StopRecommenderResponseTypeDef",
    "UpdateCampaignResponseTypeDef",
    "UpdateRecommenderResponseTypeDef",
    "CreateDatasetImportJobRequestRequestTypeDef",
    "DatasetImportJobTypeDef",
    "CreateRecommenderRequestRequestTypeDef",
    "RecommenderSummaryTypeDef",
    "RecommenderUpdateSummaryTypeDef",
    "UpdateRecommenderRequestRequestTypeDef",
    "ListDatasetExportJobsResponseTypeDef",
    "ListDatasetGroupsResponseTypeDef",
    "DescribeDatasetGroupResponseTypeDef",
    "ListDatasetImportJobsResponseTypeDef",
    "ListSchemasResponseTypeDef",
    "DescribeSchemaResponseTypeDef",
    "ListDatasetsResponseTypeDef",
    "DescribeDatasetResponseTypeDef",
    "DefaultHyperParameterRangesTypeDef",
    "DescribeEventTrackerResponseTypeDef",
    "DescribeFeatureTransformationResponseTypeDef",
    "DescribeFilterResponseTypeDef",
    "DescribeRecipeResponseTypeDef",
    "ListEventTrackersResponseTypeDef",
    "ListFiltersResponseTypeDef",
    "HyperParameterRangesTypeDef",
    "ListBatchInferenceJobsRequestListBatchInferenceJobsPaginateTypeDef",
    "ListBatchSegmentJobsRequestListBatchSegmentJobsPaginateTypeDef",
    "ListCampaignsRequestListCampaignsPaginateTypeDef",
    "ListDatasetExportJobsRequestListDatasetExportJobsPaginateTypeDef",
    "ListDatasetGroupsRequestListDatasetGroupsPaginateTypeDef",
    "ListDatasetImportJobsRequestListDatasetImportJobsPaginateTypeDef",
    "ListDatasetsRequestListDatasetsPaginateTypeDef",
    "ListEventTrackersRequestListEventTrackersPaginateTypeDef",
    "ListFiltersRequestListFiltersPaginateTypeDef",
    "ListRecipesRequestListRecipesPaginateTypeDef",
    "ListRecommendersRequestListRecommendersPaginateTypeDef",
    "ListSchemasRequestListSchemasPaginateTypeDef",
    "ListSolutionVersionsRequestListSolutionVersionsPaginateTypeDef",
    "ListSolutionsRequestListSolutionsPaginateTypeDef",
    "ListRecipesResponseTypeDef",
    "ListSolutionVersionsResponseTypeDef",
    "ListSolutionsResponseTypeDef",
    "BatchInferenceJobTypeDef",
    "CreateBatchInferenceJobRequestRequestTypeDef",
    "BatchSegmentJobTypeDef",
    "CreateBatchSegmentJobRequestRequestTypeDef",
    "CreateDatasetExportJobRequestRequestTypeDef",
    "DatasetExportJobTypeDef",
    "CampaignTypeDef",
    "DescribeDatasetImportJobResponseTypeDef",
    "ListRecommendersResponseTypeDef",
    "RecommenderTypeDef",
    "AlgorithmTypeDef",
    "HPOConfigTypeDef",
    "DescribeBatchInferenceJobResponseTypeDef",
    "DescribeBatchSegmentJobResponseTypeDef",
    "DescribeDatasetExportJobResponseTypeDef",
    "DescribeCampaignResponseTypeDef",
    "DescribeRecommenderResponseTypeDef",
    "DescribeAlgorithmResponseTypeDef",
    "SolutionConfigTypeDef",
    "CreateSolutionRequestRequestTypeDef",
    "SolutionTypeDef",
    "SolutionVersionTypeDef",
    "DescribeSolutionResponseTypeDef",
    "DescribeSolutionVersionResponseTypeDef",
)

_RequiredAlgorithmImageTypeDef = TypedDict(
    "_RequiredAlgorithmImageTypeDef",
    {
        "dockerURI": str,
    },
)
_OptionalAlgorithmImageTypeDef = TypedDict(
    "_OptionalAlgorithmImageTypeDef",
    {
        "name": str,
    },
    total=False,
)


class AlgorithmImageTypeDef(_RequiredAlgorithmImageTypeDef, _OptionalAlgorithmImageTypeDef):
    pass


AutoMLConfigTypeDef = TypedDict(
    "AutoMLConfigTypeDef",
    {
        "metricName": str,
        "recipeList": Sequence[str],
    },
    total=False,
)

AutoMLResultTypeDef = TypedDict(
    "AutoMLResultTypeDef",
    {
        "bestRecipeArn": str,
    },
    total=False,
)

BatchInferenceJobConfigTypeDef = TypedDict(
    "BatchInferenceJobConfigTypeDef",
    {
        "itemExplorationConfig": Mapping[str, str],
    },
    total=False,
)

_RequiredS3DataConfigTypeDef = TypedDict(
    "_RequiredS3DataConfigTypeDef",
    {
        "path": str,
    },
)
_OptionalS3DataConfigTypeDef = TypedDict(
    "_OptionalS3DataConfigTypeDef",
    {
        "kmsKeyArn": str,
    },
    total=False,
)


class S3DataConfigTypeDef(_RequiredS3DataConfigTypeDef, _OptionalS3DataConfigTypeDef):
    pass


BatchInferenceJobSummaryTypeDef = TypedDict(
    "BatchInferenceJobSummaryTypeDef",
    {
        "batchInferenceJobArn": str,
        "jobName": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "failureReason": str,
        "solutionVersionArn": str,
    },
    total=False,
)

BatchSegmentJobSummaryTypeDef = TypedDict(
    "BatchSegmentJobSummaryTypeDef",
    {
        "batchSegmentJobArn": str,
        "jobName": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "failureReason": str,
        "solutionVersionArn": str,
    },
    total=False,
)

CampaignConfigTypeDef = TypedDict(
    "CampaignConfigTypeDef",
    {
        "itemExplorationConfig": Mapping[str, str],
    },
    total=False,
)

CampaignSummaryTypeDef = TypedDict(
    "CampaignSummaryTypeDef",
    {
        "name": str,
        "campaignArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "failureReason": str,
    },
    total=False,
)

CategoricalHyperParameterRangeTypeDef = TypedDict(
    "CategoricalHyperParameterRangeTypeDef",
    {
        "name": str,
        "values": Sequence[str],
    },
    total=False,
)

ContinuousHyperParameterRangeTypeDef = TypedDict(
    "ContinuousHyperParameterRangeTypeDef",
    {
        "name": str,
        "minValue": float,
        "maxValue": float,
    },
    total=False,
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "tagKey": str,
        "tagValue": str,
    },
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

DataSourceTypeDef = TypedDict(
    "DataSourceTypeDef",
    {
        "dataLocation": str,
    },
    total=False,
)

RecommenderConfigTypeDef = TypedDict(
    "RecommenderConfigTypeDef",
    {
        "itemExplorationConfig": Mapping[str, str],
        "minRecommendationRequestsPerSecond": int,
    },
    total=False,
)

_RequiredCreateSchemaRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSchemaRequestRequestTypeDef",
    {
        "name": str,
        "schema": str,
    },
)
_OptionalCreateSchemaRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSchemaRequestRequestTypeDef",
    {
        "domain": DomainType,
    },
    total=False,
)


class CreateSchemaRequestRequestTypeDef(
    _RequiredCreateSchemaRequestRequestTypeDef, _OptionalCreateSchemaRequestRequestTypeDef
):
    pass


DatasetExportJobSummaryTypeDef = TypedDict(
    "DatasetExportJobSummaryTypeDef",
    {
        "datasetExportJobArn": str,
        "jobName": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "failureReason": str,
    },
    total=False,
)

DatasetGroupSummaryTypeDef = TypedDict(
    "DatasetGroupSummaryTypeDef",
    {
        "name": str,
        "datasetGroupArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "failureReason": str,
        "domain": DomainType,
    },
    total=False,
)

DatasetGroupTypeDef = TypedDict(
    "DatasetGroupTypeDef",
    {
        "name": str,
        "datasetGroupArn": str,
        "status": str,
        "roleArn": str,
        "kmsKeyArn": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "failureReason": str,
        "domain": DomainType,
    },
    total=False,
)

DatasetImportJobSummaryTypeDef = TypedDict(
    "DatasetImportJobSummaryTypeDef",
    {
        "datasetImportJobArn": str,
        "jobName": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "failureReason": str,
    },
    total=False,
)

DatasetSchemaSummaryTypeDef = TypedDict(
    "DatasetSchemaSummaryTypeDef",
    {
        "name": str,
        "schemaArn": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "domain": DomainType,
    },
    total=False,
)

DatasetSchemaTypeDef = TypedDict(
    "DatasetSchemaTypeDef",
    {
        "name": str,
        "schemaArn": str,
        "schema": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "domain": DomainType,
    },
    total=False,
)

DatasetSummaryTypeDef = TypedDict(
    "DatasetSummaryTypeDef",
    {
        "name": str,
        "datasetArn": str,
        "datasetType": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

DatasetTypeDef = TypedDict(
    "DatasetTypeDef",
    {
        "name": str,
        "datasetArn": str,
        "datasetGroupArn": str,
        "datasetType": str,
        "schemaArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

DefaultCategoricalHyperParameterRangeTypeDef = TypedDict(
    "DefaultCategoricalHyperParameterRangeTypeDef",
    {
        "name": str,
        "values": List[str],
        "isTunable": bool,
    },
    total=False,
)

DefaultContinuousHyperParameterRangeTypeDef = TypedDict(
    "DefaultContinuousHyperParameterRangeTypeDef",
    {
        "name": str,
        "minValue": float,
        "maxValue": float,
        "isTunable": bool,
    },
    total=False,
)

DefaultIntegerHyperParameterRangeTypeDef = TypedDict(
    "DefaultIntegerHyperParameterRangeTypeDef",
    {
        "name": str,
        "minValue": int,
        "maxValue": int,
        "isTunable": bool,
    },
    total=False,
)

DeleteCampaignRequestRequestTypeDef = TypedDict(
    "DeleteCampaignRequestRequestTypeDef",
    {
        "campaignArn": str,
    },
)

DeleteDatasetGroupRequestRequestTypeDef = TypedDict(
    "DeleteDatasetGroupRequestRequestTypeDef",
    {
        "datasetGroupArn": str,
    },
)

DeleteDatasetRequestRequestTypeDef = TypedDict(
    "DeleteDatasetRequestRequestTypeDef",
    {
        "datasetArn": str,
    },
)

DeleteEventTrackerRequestRequestTypeDef = TypedDict(
    "DeleteEventTrackerRequestRequestTypeDef",
    {
        "eventTrackerArn": str,
    },
)

DeleteFilterRequestRequestTypeDef = TypedDict(
    "DeleteFilterRequestRequestTypeDef",
    {
        "filterArn": str,
    },
)

DeleteRecommenderRequestRequestTypeDef = TypedDict(
    "DeleteRecommenderRequestRequestTypeDef",
    {
        "recommenderArn": str,
    },
)

DeleteSchemaRequestRequestTypeDef = TypedDict(
    "DeleteSchemaRequestRequestTypeDef",
    {
        "schemaArn": str,
    },
)

DeleteSolutionRequestRequestTypeDef = TypedDict(
    "DeleteSolutionRequestRequestTypeDef",
    {
        "solutionArn": str,
    },
)

DescribeAlgorithmRequestRequestTypeDef = TypedDict(
    "DescribeAlgorithmRequestRequestTypeDef",
    {
        "algorithmArn": str,
    },
)

DescribeBatchInferenceJobRequestRequestTypeDef = TypedDict(
    "DescribeBatchInferenceJobRequestRequestTypeDef",
    {
        "batchInferenceJobArn": str,
    },
)

DescribeBatchSegmentJobRequestRequestTypeDef = TypedDict(
    "DescribeBatchSegmentJobRequestRequestTypeDef",
    {
        "batchSegmentJobArn": str,
    },
)

DescribeCampaignRequestRequestTypeDef = TypedDict(
    "DescribeCampaignRequestRequestTypeDef",
    {
        "campaignArn": str,
    },
)

DescribeDatasetExportJobRequestRequestTypeDef = TypedDict(
    "DescribeDatasetExportJobRequestRequestTypeDef",
    {
        "datasetExportJobArn": str,
    },
)

DescribeDatasetGroupRequestRequestTypeDef = TypedDict(
    "DescribeDatasetGroupRequestRequestTypeDef",
    {
        "datasetGroupArn": str,
    },
)

DescribeDatasetImportJobRequestRequestTypeDef = TypedDict(
    "DescribeDatasetImportJobRequestRequestTypeDef",
    {
        "datasetImportJobArn": str,
    },
)

DescribeDatasetRequestRequestTypeDef = TypedDict(
    "DescribeDatasetRequestRequestTypeDef",
    {
        "datasetArn": str,
    },
)

DescribeEventTrackerRequestRequestTypeDef = TypedDict(
    "DescribeEventTrackerRequestRequestTypeDef",
    {
        "eventTrackerArn": str,
    },
)

EventTrackerTypeDef = TypedDict(
    "EventTrackerTypeDef",
    {
        "name": str,
        "eventTrackerArn": str,
        "accountId": str,
        "trackingId": str,
        "datasetGroupArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

DescribeFeatureTransformationRequestRequestTypeDef = TypedDict(
    "DescribeFeatureTransformationRequestRequestTypeDef",
    {
        "featureTransformationArn": str,
    },
)

FeatureTransformationTypeDef = TypedDict(
    "FeatureTransformationTypeDef",
    {
        "name": str,
        "featureTransformationArn": str,
        "defaultParameters": Dict[str, str],
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "status": str,
    },
    total=False,
)

DescribeFilterRequestRequestTypeDef = TypedDict(
    "DescribeFilterRequestRequestTypeDef",
    {
        "filterArn": str,
    },
)

FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "name": str,
        "filterArn": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "datasetGroupArn": str,
        "failureReason": str,
        "filterExpression": str,
        "status": str,
    },
    total=False,
)

DescribeRecipeRequestRequestTypeDef = TypedDict(
    "DescribeRecipeRequestRequestTypeDef",
    {
        "recipeArn": str,
    },
)

RecipeTypeDef = TypedDict(
    "RecipeTypeDef",
    {
        "name": str,
        "recipeArn": str,
        "algorithmArn": str,
        "featureTransformationArn": str,
        "status": str,
        "description": str,
        "creationDateTime": datetime,
        "recipeType": str,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

DescribeRecommenderRequestRequestTypeDef = TypedDict(
    "DescribeRecommenderRequestRequestTypeDef",
    {
        "recommenderArn": str,
    },
)

DescribeSchemaRequestRequestTypeDef = TypedDict(
    "DescribeSchemaRequestRequestTypeDef",
    {
        "schemaArn": str,
    },
)

DescribeSolutionRequestRequestTypeDef = TypedDict(
    "DescribeSolutionRequestRequestTypeDef",
    {
        "solutionArn": str,
    },
)

DescribeSolutionVersionRequestRequestTypeDef = TypedDict(
    "DescribeSolutionVersionRequestRequestTypeDef",
    {
        "solutionVersionArn": str,
    },
)

EventTrackerSummaryTypeDef = TypedDict(
    "EventTrackerSummaryTypeDef",
    {
        "name": str,
        "eventTrackerArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

FilterSummaryTypeDef = TypedDict(
    "FilterSummaryTypeDef",
    {
        "name": str,
        "filterArn": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "datasetGroupArn": str,
        "failureReason": str,
        "status": str,
    },
    total=False,
)

GetSolutionMetricsRequestRequestTypeDef = TypedDict(
    "GetSolutionMetricsRequestRequestTypeDef",
    {
        "solutionVersionArn": str,
    },
)

HPOObjectiveTypeDef = TypedDict(
    "HPOObjectiveTypeDef",
    {
        "type": str,
        "metricName": str,
        "metricRegex": str,
    },
    total=False,
)

HPOResourceConfigTypeDef = TypedDict(
    "HPOResourceConfigTypeDef",
    {
        "maxNumberOfTrainingJobs": str,
        "maxParallelTrainingJobs": str,
    },
    total=False,
)

IntegerHyperParameterRangeTypeDef = TypedDict(
    "IntegerHyperParameterRangeTypeDef",
    {
        "name": str,
        "minValue": int,
        "maxValue": int,
    },
    total=False,
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": int,
        "PageSize": int,
        "StartingToken": str,
    },
    total=False,
)

ListBatchInferenceJobsRequestRequestTypeDef = TypedDict(
    "ListBatchInferenceJobsRequestRequestTypeDef",
    {
        "solutionVersionArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListBatchSegmentJobsRequestRequestTypeDef = TypedDict(
    "ListBatchSegmentJobsRequestRequestTypeDef",
    {
        "solutionVersionArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListCampaignsRequestRequestTypeDef = TypedDict(
    "ListCampaignsRequestRequestTypeDef",
    {
        "solutionArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListDatasetExportJobsRequestRequestTypeDef = TypedDict(
    "ListDatasetExportJobsRequestRequestTypeDef",
    {
        "datasetArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListDatasetGroupsRequestRequestTypeDef = TypedDict(
    "ListDatasetGroupsRequestRequestTypeDef",
    {
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListDatasetImportJobsRequestRequestTypeDef = TypedDict(
    "ListDatasetImportJobsRequestRequestTypeDef",
    {
        "datasetArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListDatasetsRequestRequestTypeDef = TypedDict(
    "ListDatasetsRequestRequestTypeDef",
    {
        "datasetGroupArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListEventTrackersRequestRequestTypeDef = TypedDict(
    "ListEventTrackersRequestRequestTypeDef",
    {
        "datasetGroupArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListFiltersRequestRequestTypeDef = TypedDict(
    "ListFiltersRequestRequestTypeDef",
    {
        "datasetGroupArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListRecipesRequestRequestTypeDef = TypedDict(
    "ListRecipesRequestRequestTypeDef",
    {
        "recipeProvider": Literal["SERVICE"],
        "nextToken": str,
        "maxResults": int,
        "domain": DomainType,
    },
    total=False,
)

RecipeSummaryTypeDef = TypedDict(
    "RecipeSummaryTypeDef",
    {
        "name": str,
        "recipeArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "domain": DomainType,
    },
    total=False,
)

ListRecommendersRequestRequestTypeDef = TypedDict(
    "ListRecommendersRequestRequestTypeDef",
    {
        "datasetGroupArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListSchemasRequestRequestTypeDef = TypedDict(
    "ListSchemasRequestRequestTypeDef",
    {
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

ListSolutionVersionsRequestRequestTypeDef = TypedDict(
    "ListSolutionVersionsRequestRequestTypeDef",
    {
        "solutionArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

SolutionVersionSummaryTypeDef = TypedDict(
    "SolutionVersionSummaryTypeDef",
    {
        "solutionVersionArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "failureReason": str,
    },
    total=False,
)

ListSolutionsRequestRequestTypeDef = TypedDict(
    "ListSolutionsRequestRequestTypeDef",
    {
        "datasetGroupArn": str,
        "nextToken": str,
        "maxResults": int,
    },
    total=False,
)

SolutionSummaryTypeDef = TypedDict(
    "SolutionSummaryTypeDef",
    {
        "name": str,
        "solutionArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)

OptimizationObjectiveTypeDef = TypedDict(
    "OptimizationObjectiveTypeDef",
    {
        "itemAttribute": str,
        "objectiveSensitivity": ObjectiveSensitivityType,
    },
    total=False,
)

TunedHPOParamsTypeDef = TypedDict(
    "TunedHPOParamsTypeDef",
    {
        "algorithmHyperParameters": Dict[str, str],
    },
    total=False,
)

StartRecommenderRequestRequestTypeDef = TypedDict(
    "StartRecommenderRequestRequestTypeDef",
    {
        "recommenderArn": str,
    },
)

StopRecommenderRequestRequestTypeDef = TypedDict(
    "StopRecommenderRequestRequestTypeDef",
    {
        "recommenderArn": str,
    },
)

StopSolutionVersionCreationRequestRequestTypeDef = TypedDict(
    "StopSolutionVersionCreationRequestRequestTypeDef",
    {
        "solutionVersionArn": str,
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

BatchInferenceJobInputTypeDef = TypedDict(
    "BatchInferenceJobInputTypeDef",
    {
        "s3DataSource": S3DataConfigTypeDef,
    },
)

BatchInferenceJobOutputTypeDef = TypedDict(
    "BatchInferenceJobOutputTypeDef",
    {
        "s3DataDestination": S3DataConfigTypeDef,
    },
)

BatchSegmentJobInputTypeDef = TypedDict(
    "BatchSegmentJobInputTypeDef",
    {
        "s3DataSource": S3DataConfigTypeDef,
    },
)

BatchSegmentJobOutputTypeDef = TypedDict(
    "BatchSegmentJobOutputTypeDef",
    {
        "s3DataDestination": S3DataConfigTypeDef,
    },
)

DatasetExportJobOutputTypeDef = TypedDict(
    "DatasetExportJobOutputTypeDef",
    {
        "s3DataDestination": S3DataConfigTypeDef,
    },
)

CampaignUpdateSummaryTypeDef = TypedDict(
    "CampaignUpdateSummaryTypeDef",
    {
        "solutionVersionArn": str,
        "minProvisionedTPS": int,
        "campaignConfig": CampaignConfigTypeDef,
        "status": str,
        "failureReason": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

_RequiredUpdateCampaignRequestRequestTypeDef = TypedDict(
    "_RequiredUpdateCampaignRequestRequestTypeDef",
    {
        "campaignArn": str,
    },
)
_OptionalUpdateCampaignRequestRequestTypeDef = TypedDict(
    "_OptionalUpdateCampaignRequestRequestTypeDef",
    {
        "solutionVersionArn": str,
        "minProvisionedTPS": int,
        "campaignConfig": CampaignConfigTypeDef,
    },
    total=False,
)


class UpdateCampaignRequestRequestTypeDef(
    _RequiredUpdateCampaignRequestRequestTypeDef, _OptionalUpdateCampaignRequestRequestTypeDef
):
    pass


_RequiredCreateCampaignRequestRequestTypeDef = TypedDict(
    "_RequiredCreateCampaignRequestRequestTypeDef",
    {
        "name": str,
        "solutionVersionArn": str,
    },
)
_OptionalCreateCampaignRequestRequestTypeDef = TypedDict(
    "_OptionalCreateCampaignRequestRequestTypeDef",
    {
        "minProvisionedTPS": int,
        "campaignConfig": CampaignConfigTypeDef,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateCampaignRequestRequestTypeDef(
    _RequiredCreateCampaignRequestRequestTypeDef, _OptionalCreateCampaignRequestRequestTypeDef
):
    pass


_RequiredCreateDatasetGroupRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDatasetGroupRequestRequestTypeDef",
    {
        "name": str,
    },
)
_OptionalCreateDatasetGroupRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDatasetGroupRequestRequestTypeDef",
    {
        "roleArn": str,
        "kmsKeyArn": str,
        "domain": DomainType,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateDatasetGroupRequestRequestTypeDef(
    _RequiredCreateDatasetGroupRequestRequestTypeDef,
    _OptionalCreateDatasetGroupRequestRequestTypeDef,
):
    pass


_RequiredCreateDatasetRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDatasetRequestRequestTypeDef",
    {
        "name": str,
        "schemaArn": str,
        "datasetGroupArn": str,
        "datasetType": str,
    },
)
_OptionalCreateDatasetRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDatasetRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateDatasetRequestRequestTypeDef(
    _RequiredCreateDatasetRequestRequestTypeDef, _OptionalCreateDatasetRequestRequestTypeDef
):
    pass


_RequiredCreateEventTrackerRequestRequestTypeDef = TypedDict(
    "_RequiredCreateEventTrackerRequestRequestTypeDef",
    {
        "name": str,
        "datasetGroupArn": str,
    },
)
_OptionalCreateEventTrackerRequestRequestTypeDef = TypedDict(
    "_OptionalCreateEventTrackerRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateEventTrackerRequestRequestTypeDef(
    _RequiredCreateEventTrackerRequestRequestTypeDef,
    _OptionalCreateEventTrackerRequestRequestTypeDef,
):
    pass


_RequiredCreateFilterRequestRequestTypeDef = TypedDict(
    "_RequiredCreateFilterRequestRequestTypeDef",
    {
        "name": str,
        "datasetGroupArn": str,
        "filterExpression": str,
    },
)
_OptionalCreateFilterRequestRequestTypeDef = TypedDict(
    "_OptionalCreateFilterRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateFilterRequestRequestTypeDef(
    _RequiredCreateFilterRequestRequestTypeDef, _OptionalCreateFilterRequestRequestTypeDef
):
    pass


_RequiredCreateSolutionVersionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSolutionVersionRequestRequestTypeDef",
    {
        "solutionArn": str,
    },
)
_OptionalCreateSolutionVersionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSolutionVersionRequestRequestTypeDef",
    {
        "trainingMode": TrainingModeType,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateSolutionVersionRequestRequestTypeDef(
    _RequiredCreateSolutionVersionRequestRequestTypeDef,
    _OptionalCreateSolutionVersionRequestRequestTypeDef,
):
    pass


TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Sequence[TagTypeDef],
    },
)

CreateBatchInferenceJobResponseTypeDef = TypedDict(
    "CreateBatchInferenceJobResponseTypeDef",
    {
        "batchInferenceJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateBatchSegmentJobResponseTypeDef = TypedDict(
    "CreateBatchSegmentJobResponseTypeDef",
    {
        "batchSegmentJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCampaignResponseTypeDef = TypedDict(
    "CreateCampaignResponseTypeDef",
    {
        "campaignArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDatasetExportJobResponseTypeDef = TypedDict(
    "CreateDatasetExportJobResponseTypeDef",
    {
        "datasetExportJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDatasetGroupResponseTypeDef = TypedDict(
    "CreateDatasetGroupResponseTypeDef",
    {
        "datasetGroupArn": str,
        "domain": DomainType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDatasetImportJobResponseTypeDef = TypedDict(
    "CreateDatasetImportJobResponseTypeDef",
    {
        "datasetImportJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDatasetResponseTypeDef = TypedDict(
    "CreateDatasetResponseTypeDef",
    {
        "datasetArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEventTrackerResponseTypeDef = TypedDict(
    "CreateEventTrackerResponseTypeDef",
    {
        "eventTrackerArn": str,
        "trackingId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateFilterResponseTypeDef = TypedDict(
    "CreateFilterResponseTypeDef",
    {
        "filterArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRecommenderResponseTypeDef = TypedDict(
    "CreateRecommenderResponseTypeDef",
    {
        "recommenderArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSchemaResponseTypeDef = TypedDict(
    "CreateSchemaResponseTypeDef",
    {
        "schemaArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSolutionResponseTypeDef = TypedDict(
    "CreateSolutionResponseTypeDef",
    {
        "solutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSolutionVersionResponseTypeDef = TypedDict(
    "CreateSolutionVersionResponseTypeDef",
    {
        "solutionVersionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetSolutionMetricsResponseTypeDef = TypedDict(
    "GetSolutionMetricsResponseTypeDef",
    {
        "solutionVersionArn": str,
        "metrics": Dict[str, float],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListBatchInferenceJobsResponseTypeDef = TypedDict(
    "ListBatchInferenceJobsResponseTypeDef",
    {
        "batchInferenceJobs": List[BatchInferenceJobSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListBatchSegmentJobsResponseTypeDef = TypedDict(
    "ListBatchSegmentJobsResponseTypeDef",
    {
        "batchSegmentJobs": List[BatchSegmentJobSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListCampaignsResponseTypeDef = TypedDict(
    "ListCampaignsResponseTypeDef",
    {
        "campaigns": List[CampaignSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartRecommenderResponseTypeDef = TypedDict(
    "StartRecommenderResponseTypeDef",
    {
        "recommenderArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopRecommenderResponseTypeDef = TypedDict(
    "StopRecommenderResponseTypeDef",
    {
        "recommenderArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateCampaignResponseTypeDef = TypedDict(
    "UpdateCampaignResponseTypeDef",
    {
        "campaignArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateRecommenderResponseTypeDef = TypedDict(
    "UpdateRecommenderResponseTypeDef",
    {
        "recommenderArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredCreateDatasetImportJobRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDatasetImportJobRequestRequestTypeDef",
    {
        "jobName": str,
        "datasetArn": str,
        "dataSource": DataSourceTypeDef,
        "roleArn": str,
    },
)
_OptionalCreateDatasetImportJobRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDatasetImportJobRequestRequestTypeDef",
    {
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateDatasetImportJobRequestRequestTypeDef(
    _RequiredCreateDatasetImportJobRequestRequestTypeDef,
    _OptionalCreateDatasetImportJobRequestRequestTypeDef,
):
    pass


DatasetImportJobTypeDef = TypedDict(
    "DatasetImportJobTypeDef",
    {
        "jobName": str,
        "datasetImportJobArn": str,
        "datasetArn": str,
        "dataSource": DataSourceTypeDef,
        "roleArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "failureReason": str,
    },
    total=False,
)

_RequiredCreateRecommenderRequestRequestTypeDef = TypedDict(
    "_RequiredCreateRecommenderRequestRequestTypeDef",
    {
        "name": str,
        "datasetGroupArn": str,
        "recipeArn": str,
    },
)
_OptionalCreateRecommenderRequestRequestTypeDef = TypedDict(
    "_OptionalCreateRecommenderRequestRequestTypeDef",
    {
        "recommenderConfig": RecommenderConfigTypeDef,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateRecommenderRequestRequestTypeDef(
    _RequiredCreateRecommenderRequestRequestTypeDef, _OptionalCreateRecommenderRequestRequestTypeDef
):
    pass


RecommenderSummaryTypeDef = TypedDict(
    "RecommenderSummaryTypeDef",
    {
        "name": str,
        "recommenderArn": str,
        "datasetGroupArn": str,
        "recipeArn": str,
        "recommenderConfig": RecommenderConfigTypeDef,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

RecommenderUpdateSummaryTypeDef = TypedDict(
    "RecommenderUpdateSummaryTypeDef",
    {
        "recommenderConfig": RecommenderConfigTypeDef,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "status": str,
        "failureReason": str,
    },
    total=False,
)

UpdateRecommenderRequestRequestTypeDef = TypedDict(
    "UpdateRecommenderRequestRequestTypeDef",
    {
        "recommenderArn": str,
        "recommenderConfig": RecommenderConfigTypeDef,
    },
)

ListDatasetExportJobsResponseTypeDef = TypedDict(
    "ListDatasetExportJobsResponseTypeDef",
    {
        "datasetExportJobs": List[DatasetExportJobSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDatasetGroupsResponseTypeDef = TypedDict(
    "ListDatasetGroupsResponseTypeDef",
    {
        "datasetGroups": List[DatasetGroupSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDatasetGroupResponseTypeDef = TypedDict(
    "DescribeDatasetGroupResponseTypeDef",
    {
        "datasetGroup": DatasetGroupTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDatasetImportJobsResponseTypeDef = TypedDict(
    "ListDatasetImportJobsResponseTypeDef",
    {
        "datasetImportJobs": List[DatasetImportJobSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSchemasResponseTypeDef = TypedDict(
    "ListSchemasResponseTypeDef",
    {
        "schemas": List[DatasetSchemaSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSchemaResponseTypeDef = TypedDict(
    "DescribeSchemaResponseTypeDef",
    {
        "schema": DatasetSchemaTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDatasetsResponseTypeDef = TypedDict(
    "ListDatasetsResponseTypeDef",
    {
        "datasets": List[DatasetSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDatasetResponseTypeDef = TypedDict(
    "DescribeDatasetResponseTypeDef",
    {
        "dataset": DatasetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DefaultHyperParameterRangesTypeDef = TypedDict(
    "DefaultHyperParameterRangesTypeDef",
    {
        "integerHyperParameterRanges": List[DefaultIntegerHyperParameterRangeTypeDef],
        "continuousHyperParameterRanges": List[DefaultContinuousHyperParameterRangeTypeDef],
        "categoricalHyperParameterRanges": List[DefaultCategoricalHyperParameterRangeTypeDef],
    },
    total=False,
)

DescribeEventTrackerResponseTypeDef = TypedDict(
    "DescribeEventTrackerResponseTypeDef",
    {
        "eventTracker": EventTrackerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFeatureTransformationResponseTypeDef = TypedDict(
    "DescribeFeatureTransformationResponseTypeDef",
    {
        "featureTransformation": FeatureTransformationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeFilterResponseTypeDef = TypedDict(
    "DescribeFilterResponseTypeDef",
    {
        "filter": FilterTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeRecipeResponseTypeDef = TypedDict(
    "DescribeRecipeResponseTypeDef",
    {
        "recipe": RecipeTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEventTrackersResponseTypeDef = TypedDict(
    "ListEventTrackersResponseTypeDef",
    {
        "eventTrackers": List[EventTrackerSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListFiltersResponseTypeDef = TypedDict(
    "ListFiltersResponseTypeDef",
    {
        "Filters": List[FilterSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

HyperParameterRangesTypeDef = TypedDict(
    "HyperParameterRangesTypeDef",
    {
        "integerHyperParameterRanges": Sequence[IntegerHyperParameterRangeTypeDef],
        "continuousHyperParameterRanges": Sequence[ContinuousHyperParameterRangeTypeDef],
        "categoricalHyperParameterRanges": Sequence[CategoricalHyperParameterRangeTypeDef],
    },
    total=False,
)

ListBatchInferenceJobsRequestListBatchInferenceJobsPaginateTypeDef = TypedDict(
    "ListBatchInferenceJobsRequestListBatchInferenceJobsPaginateTypeDef",
    {
        "solutionVersionArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListBatchSegmentJobsRequestListBatchSegmentJobsPaginateTypeDef = TypedDict(
    "ListBatchSegmentJobsRequestListBatchSegmentJobsPaginateTypeDef",
    {
        "solutionVersionArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListCampaignsRequestListCampaignsPaginateTypeDef = TypedDict(
    "ListCampaignsRequestListCampaignsPaginateTypeDef",
    {
        "solutionArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListDatasetExportJobsRequestListDatasetExportJobsPaginateTypeDef = TypedDict(
    "ListDatasetExportJobsRequestListDatasetExportJobsPaginateTypeDef",
    {
        "datasetArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListDatasetGroupsRequestListDatasetGroupsPaginateTypeDef = TypedDict(
    "ListDatasetGroupsRequestListDatasetGroupsPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListDatasetImportJobsRequestListDatasetImportJobsPaginateTypeDef = TypedDict(
    "ListDatasetImportJobsRequestListDatasetImportJobsPaginateTypeDef",
    {
        "datasetArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListDatasetsRequestListDatasetsPaginateTypeDef = TypedDict(
    "ListDatasetsRequestListDatasetsPaginateTypeDef",
    {
        "datasetGroupArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListEventTrackersRequestListEventTrackersPaginateTypeDef = TypedDict(
    "ListEventTrackersRequestListEventTrackersPaginateTypeDef",
    {
        "datasetGroupArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListFiltersRequestListFiltersPaginateTypeDef = TypedDict(
    "ListFiltersRequestListFiltersPaginateTypeDef",
    {
        "datasetGroupArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListRecipesRequestListRecipesPaginateTypeDef = TypedDict(
    "ListRecipesRequestListRecipesPaginateTypeDef",
    {
        "recipeProvider": Literal["SERVICE"],
        "domain": DomainType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListRecommendersRequestListRecommendersPaginateTypeDef = TypedDict(
    "ListRecommendersRequestListRecommendersPaginateTypeDef",
    {
        "datasetGroupArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListSchemasRequestListSchemasPaginateTypeDef = TypedDict(
    "ListSchemasRequestListSchemasPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListSolutionVersionsRequestListSolutionVersionsPaginateTypeDef = TypedDict(
    "ListSolutionVersionsRequestListSolutionVersionsPaginateTypeDef",
    {
        "solutionArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListSolutionsRequestListSolutionsPaginateTypeDef = TypedDict(
    "ListSolutionsRequestListSolutionsPaginateTypeDef",
    {
        "datasetGroupArn": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

ListRecipesResponseTypeDef = TypedDict(
    "ListRecipesResponseTypeDef",
    {
        "recipes": List[RecipeSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSolutionVersionsResponseTypeDef = TypedDict(
    "ListSolutionVersionsResponseTypeDef",
    {
        "solutionVersions": List[SolutionVersionSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSolutionsResponseTypeDef = TypedDict(
    "ListSolutionsResponseTypeDef",
    {
        "solutions": List[SolutionSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

BatchInferenceJobTypeDef = TypedDict(
    "BatchInferenceJobTypeDef",
    {
        "jobName": str,
        "batchInferenceJobArn": str,
        "filterArn": str,
        "failureReason": str,
        "solutionVersionArn": str,
        "numResults": int,
        "jobInput": BatchInferenceJobInputTypeDef,
        "jobOutput": BatchInferenceJobOutputTypeDef,
        "batchInferenceJobConfig": BatchInferenceJobConfigTypeDef,
        "roleArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

_RequiredCreateBatchInferenceJobRequestRequestTypeDef = TypedDict(
    "_RequiredCreateBatchInferenceJobRequestRequestTypeDef",
    {
        "jobName": str,
        "solutionVersionArn": str,
        "jobInput": BatchInferenceJobInputTypeDef,
        "jobOutput": BatchInferenceJobOutputTypeDef,
        "roleArn": str,
    },
)
_OptionalCreateBatchInferenceJobRequestRequestTypeDef = TypedDict(
    "_OptionalCreateBatchInferenceJobRequestRequestTypeDef",
    {
        "filterArn": str,
        "numResults": int,
        "batchInferenceJobConfig": BatchInferenceJobConfigTypeDef,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateBatchInferenceJobRequestRequestTypeDef(
    _RequiredCreateBatchInferenceJobRequestRequestTypeDef,
    _OptionalCreateBatchInferenceJobRequestRequestTypeDef,
):
    pass


BatchSegmentJobTypeDef = TypedDict(
    "BatchSegmentJobTypeDef",
    {
        "jobName": str,
        "batchSegmentJobArn": str,
        "filterArn": str,
        "failureReason": str,
        "solutionVersionArn": str,
        "numResults": int,
        "jobInput": BatchSegmentJobInputTypeDef,
        "jobOutput": BatchSegmentJobOutputTypeDef,
        "roleArn": str,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

_RequiredCreateBatchSegmentJobRequestRequestTypeDef = TypedDict(
    "_RequiredCreateBatchSegmentJobRequestRequestTypeDef",
    {
        "jobName": str,
        "solutionVersionArn": str,
        "jobInput": BatchSegmentJobInputTypeDef,
        "jobOutput": BatchSegmentJobOutputTypeDef,
        "roleArn": str,
    },
)
_OptionalCreateBatchSegmentJobRequestRequestTypeDef = TypedDict(
    "_OptionalCreateBatchSegmentJobRequestRequestTypeDef",
    {
        "filterArn": str,
        "numResults": int,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateBatchSegmentJobRequestRequestTypeDef(
    _RequiredCreateBatchSegmentJobRequestRequestTypeDef,
    _OptionalCreateBatchSegmentJobRequestRequestTypeDef,
):
    pass


_RequiredCreateDatasetExportJobRequestRequestTypeDef = TypedDict(
    "_RequiredCreateDatasetExportJobRequestRequestTypeDef",
    {
        "jobName": str,
        "datasetArn": str,
        "roleArn": str,
        "jobOutput": DatasetExportJobOutputTypeDef,
    },
)
_OptionalCreateDatasetExportJobRequestRequestTypeDef = TypedDict(
    "_OptionalCreateDatasetExportJobRequestRequestTypeDef",
    {
        "ingestionMode": IngestionModeType,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateDatasetExportJobRequestRequestTypeDef(
    _RequiredCreateDatasetExportJobRequestRequestTypeDef,
    _OptionalCreateDatasetExportJobRequestRequestTypeDef,
):
    pass


DatasetExportJobTypeDef = TypedDict(
    "DatasetExportJobTypeDef",
    {
        "jobName": str,
        "datasetExportJobArn": str,
        "datasetArn": str,
        "ingestionMode": IngestionModeType,
        "roleArn": str,
        "status": str,
        "jobOutput": DatasetExportJobOutputTypeDef,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "failureReason": str,
    },
    total=False,
)

CampaignTypeDef = TypedDict(
    "CampaignTypeDef",
    {
        "name": str,
        "campaignArn": str,
        "solutionVersionArn": str,
        "minProvisionedTPS": int,
        "campaignConfig": CampaignConfigTypeDef,
        "status": str,
        "failureReason": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "latestCampaignUpdate": CampaignUpdateSummaryTypeDef,
    },
    total=False,
)

DescribeDatasetImportJobResponseTypeDef = TypedDict(
    "DescribeDatasetImportJobResponseTypeDef",
    {
        "datasetImportJob": DatasetImportJobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListRecommendersResponseTypeDef = TypedDict(
    "ListRecommendersResponseTypeDef",
    {
        "recommenders": List[RecommenderSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RecommenderTypeDef = TypedDict(
    "RecommenderTypeDef",
    {
        "recommenderArn": str,
        "datasetGroupArn": str,
        "name": str,
        "recipeArn": str,
        "recommenderConfig": RecommenderConfigTypeDef,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "status": str,
        "failureReason": str,
        "latestRecommenderUpdate": RecommenderUpdateSummaryTypeDef,
        "modelMetrics": Dict[str, float],
    },
    total=False,
)

AlgorithmTypeDef = TypedDict(
    "AlgorithmTypeDef",
    {
        "name": str,
        "algorithmArn": str,
        "algorithmImage": AlgorithmImageTypeDef,
        "defaultHyperParameters": Dict[str, str],
        "defaultHyperParameterRanges": DefaultHyperParameterRangesTypeDef,
        "defaultResourceConfig": Dict[str, str],
        "trainingInputMode": str,
        "roleArn": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

HPOConfigTypeDef = TypedDict(
    "HPOConfigTypeDef",
    {
        "hpoObjective": HPOObjectiveTypeDef,
        "hpoResourceConfig": HPOResourceConfigTypeDef,
        "algorithmHyperParameterRanges": HyperParameterRangesTypeDef,
    },
    total=False,
)

DescribeBatchInferenceJobResponseTypeDef = TypedDict(
    "DescribeBatchInferenceJobResponseTypeDef",
    {
        "batchInferenceJob": BatchInferenceJobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeBatchSegmentJobResponseTypeDef = TypedDict(
    "DescribeBatchSegmentJobResponseTypeDef",
    {
        "batchSegmentJob": BatchSegmentJobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDatasetExportJobResponseTypeDef = TypedDict(
    "DescribeDatasetExportJobResponseTypeDef",
    {
        "datasetExportJob": DatasetExportJobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeCampaignResponseTypeDef = TypedDict(
    "DescribeCampaignResponseTypeDef",
    {
        "campaign": CampaignTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeRecommenderResponseTypeDef = TypedDict(
    "DescribeRecommenderResponseTypeDef",
    {
        "recommender": RecommenderTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeAlgorithmResponseTypeDef = TypedDict(
    "DescribeAlgorithmResponseTypeDef",
    {
        "algorithm": AlgorithmTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SolutionConfigTypeDef = TypedDict(
    "SolutionConfigTypeDef",
    {
        "eventValueThreshold": str,
        "hpoConfig": HPOConfigTypeDef,
        "algorithmHyperParameters": Mapping[str, str],
        "featureTransformationParameters": Mapping[str, str],
        "autoMLConfig": AutoMLConfigTypeDef,
        "optimizationObjective": OptimizationObjectiveTypeDef,
    },
    total=False,
)

_RequiredCreateSolutionRequestRequestTypeDef = TypedDict(
    "_RequiredCreateSolutionRequestRequestTypeDef",
    {
        "name": str,
        "datasetGroupArn": str,
    },
)
_OptionalCreateSolutionRequestRequestTypeDef = TypedDict(
    "_OptionalCreateSolutionRequestRequestTypeDef",
    {
        "performHPO": bool,
        "performAutoML": bool,
        "recipeArn": str,
        "eventType": str,
        "solutionConfig": SolutionConfigTypeDef,
        "tags": Sequence[TagTypeDef],
    },
    total=False,
)


class CreateSolutionRequestRequestTypeDef(
    _RequiredCreateSolutionRequestRequestTypeDef, _OptionalCreateSolutionRequestRequestTypeDef
):
    pass


SolutionTypeDef = TypedDict(
    "SolutionTypeDef",
    {
        "name": str,
        "solutionArn": str,
        "performHPO": bool,
        "performAutoML": bool,
        "recipeArn": str,
        "datasetGroupArn": str,
        "eventType": str,
        "solutionConfig": SolutionConfigTypeDef,
        "autoMLResult": AutoMLResultTypeDef,
        "status": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "latestSolutionVersion": SolutionVersionSummaryTypeDef,
    },
    total=False,
)

SolutionVersionTypeDef = TypedDict(
    "SolutionVersionTypeDef",
    {
        "solutionVersionArn": str,
        "solutionArn": str,
        "performHPO": bool,
        "performAutoML": bool,
        "recipeArn": str,
        "eventType": str,
        "datasetGroupArn": str,
        "solutionConfig": SolutionConfigTypeDef,
        "trainingHours": float,
        "trainingMode": TrainingModeType,
        "tunedHPOParams": TunedHPOParamsTypeDef,
        "status": str,
        "failureReason": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
    },
    total=False,
)

DescribeSolutionResponseTypeDef = TypedDict(
    "DescribeSolutionResponseTypeDef",
    {
        "solution": SolutionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSolutionVersionResponseTypeDef = TypedDict(
    "DescribeSolutionVersionResponseTypeDef",
    {
        "solutionVersion": SolutionVersionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
