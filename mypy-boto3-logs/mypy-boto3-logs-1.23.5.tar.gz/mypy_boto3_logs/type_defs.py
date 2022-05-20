"""
Type annotations for logs service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/type_defs/)

Usage::

    ```python
    from mypy_boto3_logs.type_defs import AssociateKmsKeyRequestRequestTypeDef

    data: AssociateKmsKeyRequestRequestTypeDef = {...}
    ```
"""
import sys
from typing import Dict, List, Mapping, Sequence

from .literals import (
    DistributionType,
    ExportTaskStatusCodeType,
    OrderByType,
    QueryStatusType,
    StandardUnitType,
)

if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "AssociateKmsKeyRequestRequestTypeDef",
    "CancelExportTaskRequestRequestTypeDef",
    "CreateExportTaskRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "CreateLogGroupRequestRequestTypeDef",
    "CreateLogStreamRequestRequestTypeDef",
    "DeleteDestinationRequestRequestTypeDef",
    "DeleteLogGroupRequestRequestTypeDef",
    "DeleteLogStreamRequestRequestTypeDef",
    "DeleteMetricFilterRequestRequestTypeDef",
    "DeleteQueryDefinitionRequestRequestTypeDef",
    "DeleteResourcePolicyRequestRequestTypeDef",
    "DeleteRetentionPolicyRequestRequestTypeDef",
    "DeleteSubscriptionFilterRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeDestinationsRequestRequestTypeDef",
    "DestinationTypeDef",
    "DescribeExportTasksRequestRequestTypeDef",
    "DescribeLogGroupsRequestRequestTypeDef",
    "LogGroupTypeDef",
    "DescribeLogStreamsRequestRequestTypeDef",
    "LogStreamTypeDef",
    "DescribeMetricFiltersRequestRequestTypeDef",
    "DescribeQueriesRequestRequestTypeDef",
    "QueryInfoTypeDef",
    "DescribeQueryDefinitionsRequestRequestTypeDef",
    "QueryDefinitionTypeDef",
    "DescribeResourcePoliciesRequestRequestTypeDef",
    "ResourcePolicyTypeDef",
    "DescribeSubscriptionFiltersRequestRequestTypeDef",
    "SubscriptionFilterTypeDef",
    "DisassociateKmsKeyRequestRequestTypeDef",
    "ExportTaskExecutionInfoTypeDef",
    "ExportTaskStatusTypeDef",
    "FilterLogEventsRequestRequestTypeDef",
    "FilteredLogEventTypeDef",
    "SearchedLogStreamTypeDef",
    "GetLogEventsRequestRequestTypeDef",
    "OutputLogEventTypeDef",
    "GetLogGroupFieldsRequestRequestTypeDef",
    "LogGroupFieldTypeDef",
    "GetLogRecordRequestRequestTypeDef",
    "GetQueryResultsRequestRequestTypeDef",
    "QueryStatisticsTypeDef",
    "ResultFieldTypeDef",
    "InputLogEventTypeDef",
    "ListTagsLogGroupRequestRequestTypeDef",
    "MetricFilterMatchRecordTypeDef",
    "MetricTransformationTypeDef",
    "PutDestinationPolicyRequestRequestTypeDef",
    "PutDestinationRequestRequestTypeDef",
    "RejectedLogEventsInfoTypeDef",
    "PutQueryDefinitionRequestRequestTypeDef",
    "PutResourcePolicyRequestRequestTypeDef",
    "PutRetentionPolicyRequestRequestTypeDef",
    "PutSubscriptionFilterRequestRequestTypeDef",
    "StartQueryRequestRequestTypeDef",
    "StopQueryRequestRequestTypeDef",
    "TagLogGroupRequestRequestTypeDef",
    "TestMetricFilterRequestRequestTypeDef",
    "UntagLogGroupRequestRequestTypeDef",
    "CreateExportTaskResponseTypeDef",
    "DeleteQueryDefinitionResponseTypeDef",
    "GetLogRecordResponseTypeDef",
    "ListTagsLogGroupResponseTypeDef",
    "PutQueryDefinitionResponseTypeDef",
    "StartQueryResponseTypeDef",
    "StopQueryResponseTypeDef",
    "DescribeDestinationsRequestDescribeDestinationsPaginateTypeDef",
    "DescribeExportTasksRequestDescribeExportTasksPaginateTypeDef",
    "DescribeLogGroupsRequestDescribeLogGroupsPaginateTypeDef",
    "DescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef",
    "DescribeMetricFiltersRequestDescribeMetricFiltersPaginateTypeDef",
    "DescribeQueriesRequestDescribeQueriesPaginateTypeDef",
    "DescribeResourcePoliciesRequestDescribeResourcePoliciesPaginateTypeDef",
    "DescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef",
    "FilterLogEventsRequestFilterLogEventsPaginateTypeDef",
    "DescribeDestinationsResponseTypeDef",
    "PutDestinationResponseTypeDef",
    "DescribeLogGroupsResponseTypeDef",
    "DescribeLogStreamsResponseTypeDef",
    "DescribeQueriesResponseTypeDef",
    "DescribeQueryDefinitionsResponseTypeDef",
    "DescribeResourcePoliciesResponseTypeDef",
    "PutResourcePolicyResponseTypeDef",
    "DescribeSubscriptionFiltersResponseTypeDef",
    "ExportTaskTypeDef",
    "FilterLogEventsResponseTypeDef",
    "GetLogEventsResponseTypeDef",
    "GetLogGroupFieldsResponseTypeDef",
    "GetQueryResultsResponseTypeDef",
    "PutLogEventsRequestRequestTypeDef",
    "TestMetricFilterResponseTypeDef",
    "MetricFilterTypeDef",
    "PutMetricFilterRequestRequestTypeDef",
    "PutLogEventsResponseTypeDef",
    "DescribeExportTasksResponseTypeDef",
    "DescribeMetricFiltersResponseTypeDef",
)

AssociateKmsKeyRequestRequestTypeDef = TypedDict(
    "AssociateKmsKeyRequestRequestTypeDef",
    {
        "logGroupName": str,
        "kmsKeyId": str,
    },
)

CancelExportTaskRequestRequestTypeDef = TypedDict(
    "CancelExportTaskRequestRequestTypeDef",
    {
        "taskId": str,
    },
)

_RequiredCreateExportTaskRequestRequestTypeDef = TypedDict(
    "_RequiredCreateExportTaskRequestRequestTypeDef",
    {
        "logGroupName": str,
        "fromTime": int,
        "to": int,
        "destination": str,
    },
)
_OptionalCreateExportTaskRequestRequestTypeDef = TypedDict(
    "_OptionalCreateExportTaskRequestRequestTypeDef",
    {
        "taskName": str,
        "logStreamNamePrefix": str,
        "destinationPrefix": str,
    },
    total=False,
)


class CreateExportTaskRequestRequestTypeDef(
    _RequiredCreateExportTaskRequestRequestTypeDef, _OptionalCreateExportTaskRequestRequestTypeDef
):
    pass


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

_RequiredCreateLogGroupRequestRequestTypeDef = TypedDict(
    "_RequiredCreateLogGroupRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)
_OptionalCreateLogGroupRequestRequestTypeDef = TypedDict(
    "_OptionalCreateLogGroupRequestRequestTypeDef",
    {
        "kmsKeyId": str,
        "tags": Mapping[str, str],
    },
    total=False,
)


class CreateLogGroupRequestRequestTypeDef(
    _RequiredCreateLogGroupRequestRequestTypeDef, _OptionalCreateLogGroupRequestRequestTypeDef
):
    pass


CreateLogStreamRequestRequestTypeDef = TypedDict(
    "CreateLogStreamRequestRequestTypeDef",
    {
        "logGroupName": str,
        "logStreamName": str,
    },
)

DeleteDestinationRequestRequestTypeDef = TypedDict(
    "DeleteDestinationRequestRequestTypeDef",
    {
        "destinationName": str,
    },
)

DeleteLogGroupRequestRequestTypeDef = TypedDict(
    "DeleteLogGroupRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)

DeleteLogStreamRequestRequestTypeDef = TypedDict(
    "DeleteLogStreamRequestRequestTypeDef",
    {
        "logGroupName": str,
        "logStreamName": str,
    },
)

DeleteMetricFilterRequestRequestTypeDef = TypedDict(
    "DeleteMetricFilterRequestRequestTypeDef",
    {
        "logGroupName": str,
        "filterName": str,
    },
)

DeleteQueryDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteQueryDefinitionRequestRequestTypeDef",
    {
        "queryDefinitionId": str,
    },
)

DeleteResourcePolicyRequestRequestTypeDef = TypedDict(
    "DeleteResourcePolicyRequestRequestTypeDef",
    {
        "policyName": str,
    },
    total=False,
)

DeleteRetentionPolicyRequestRequestTypeDef = TypedDict(
    "DeleteRetentionPolicyRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)

DeleteSubscriptionFilterRequestRequestTypeDef = TypedDict(
    "DeleteSubscriptionFilterRequestRequestTypeDef",
    {
        "logGroupName": str,
        "filterName": str,
    },
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

DescribeDestinationsRequestRequestTypeDef = TypedDict(
    "DescribeDestinationsRequestRequestTypeDef",
    {
        "DestinationNamePrefix": str,
        "nextToken": str,
        "limit": int,
    },
    total=False,
)

DestinationTypeDef = TypedDict(
    "DestinationTypeDef",
    {
        "destinationName": str,
        "targetArn": str,
        "roleArn": str,
        "accessPolicy": str,
        "arn": str,
        "creationTime": int,
    },
    total=False,
)

DescribeExportTasksRequestRequestTypeDef = TypedDict(
    "DescribeExportTasksRequestRequestTypeDef",
    {
        "taskId": str,
        "statusCode": ExportTaskStatusCodeType,
        "nextToken": str,
        "limit": int,
    },
    total=False,
)

DescribeLogGroupsRequestRequestTypeDef = TypedDict(
    "DescribeLogGroupsRequestRequestTypeDef",
    {
        "logGroupNamePrefix": str,
        "nextToken": str,
        "limit": int,
    },
    total=False,
)

LogGroupTypeDef = TypedDict(
    "LogGroupTypeDef",
    {
        "logGroupName": str,
        "creationTime": int,
        "retentionInDays": int,
        "metricFilterCount": int,
        "arn": str,
        "storedBytes": int,
        "kmsKeyId": str,
    },
    total=False,
)

_RequiredDescribeLogStreamsRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeLogStreamsRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)
_OptionalDescribeLogStreamsRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeLogStreamsRequestRequestTypeDef",
    {
        "logStreamNamePrefix": str,
        "orderBy": OrderByType,
        "descending": bool,
        "nextToken": str,
        "limit": int,
    },
    total=False,
)


class DescribeLogStreamsRequestRequestTypeDef(
    _RequiredDescribeLogStreamsRequestRequestTypeDef,
    _OptionalDescribeLogStreamsRequestRequestTypeDef,
):
    pass


LogStreamTypeDef = TypedDict(
    "LogStreamTypeDef",
    {
        "logStreamName": str,
        "creationTime": int,
        "firstEventTimestamp": int,
        "lastEventTimestamp": int,
        "lastIngestionTime": int,
        "uploadSequenceToken": str,
        "arn": str,
        "storedBytes": int,
    },
    total=False,
)

DescribeMetricFiltersRequestRequestTypeDef = TypedDict(
    "DescribeMetricFiltersRequestRequestTypeDef",
    {
        "logGroupName": str,
        "filterNamePrefix": str,
        "nextToken": str,
        "limit": int,
        "metricName": str,
        "metricNamespace": str,
    },
    total=False,
)

DescribeQueriesRequestRequestTypeDef = TypedDict(
    "DescribeQueriesRequestRequestTypeDef",
    {
        "logGroupName": str,
        "status": QueryStatusType,
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

QueryInfoTypeDef = TypedDict(
    "QueryInfoTypeDef",
    {
        "queryId": str,
        "queryString": str,
        "status": QueryStatusType,
        "createTime": int,
        "logGroupName": str,
    },
    total=False,
)

DescribeQueryDefinitionsRequestRequestTypeDef = TypedDict(
    "DescribeQueryDefinitionsRequestRequestTypeDef",
    {
        "queryDefinitionNamePrefix": str,
        "maxResults": int,
        "nextToken": str,
    },
    total=False,
)

QueryDefinitionTypeDef = TypedDict(
    "QueryDefinitionTypeDef",
    {
        "queryDefinitionId": str,
        "name": str,
        "queryString": str,
        "lastModified": int,
        "logGroupNames": List[str],
    },
    total=False,
)

DescribeResourcePoliciesRequestRequestTypeDef = TypedDict(
    "DescribeResourcePoliciesRequestRequestTypeDef",
    {
        "nextToken": str,
        "limit": int,
    },
    total=False,
)

ResourcePolicyTypeDef = TypedDict(
    "ResourcePolicyTypeDef",
    {
        "policyName": str,
        "policyDocument": str,
        "lastUpdatedTime": int,
    },
    total=False,
)

_RequiredDescribeSubscriptionFiltersRequestRequestTypeDef = TypedDict(
    "_RequiredDescribeSubscriptionFiltersRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)
_OptionalDescribeSubscriptionFiltersRequestRequestTypeDef = TypedDict(
    "_OptionalDescribeSubscriptionFiltersRequestRequestTypeDef",
    {
        "filterNamePrefix": str,
        "nextToken": str,
        "limit": int,
    },
    total=False,
)


class DescribeSubscriptionFiltersRequestRequestTypeDef(
    _RequiredDescribeSubscriptionFiltersRequestRequestTypeDef,
    _OptionalDescribeSubscriptionFiltersRequestRequestTypeDef,
):
    pass


SubscriptionFilterTypeDef = TypedDict(
    "SubscriptionFilterTypeDef",
    {
        "filterName": str,
        "logGroupName": str,
        "filterPattern": str,
        "destinationArn": str,
        "roleArn": str,
        "distribution": DistributionType,
        "creationTime": int,
    },
    total=False,
)

DisassociateKmsKeyRequestRequestTypeDef = TypedDict(
    "DisassociateKmsKeyRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)

ExportTaskExecutionInfoTypeDef = TypedDict(
    "ExportTaskExecutionInfoTypeDef",
    {
        "creationTime": int,
        "completionTime": int,
    },
    total=False,
)

ExportTaskStatusTypeDef = TypedDict(
    "ExportTaskStatusTypeDef",
    {
        "code": ExportTaskStatusCodeType,
        "message": str,
    },
    total=False,
)

_RequiredFilterLogEventsRequestRequestTypeDef = TypedDict(
    "_RequiredFilterLogEventsRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)
_OptionalFilterLogEventsRequestRequestTypeDef = TypedDict(
    "_OptionalFilterLogEventsRequestRequestTypeDef",
    {
        "logStreamNames": Sequence[str],
        "logStreamNamePrefix": str,
        "startTime": int,
        "endTime": int,
        "filterPattern": str,
        "nextToken": str,
        "limit": int,
        "interleaved": bool,
    },
    total=False,
)


class FilterLogEventsRequestRequestTypeDef(
    _RequiredFilterLogEventsRequestRequestTypeDef, _OptionalFilterLogEventsRequestRequestTypeDef
):
    pass


FilteredLogEventTypeDef = TypedDict(
    "FilteredLogEventTypeDef",
    {
        "logStreamName": str,
        "timestamp": int,
        "message": str,
        "ingestionTime": int,
        "eventId": str,
    },
    total=False,
)

SearchedLogStreamTypeDef = TypedDict(
    "SearchedLogStreamTypeDef",
    {
        "logStreamName": str,
        "searchedCompletely": bool,
    },
    total=False,
)

_RequiredGetLogEventsRequestRequestTypeDef = TypedDict(
    "_RequiredGetLogEventsRequestRequestTypeDef",
    {
        "logGroupName": str,
        "logStreamName": str,
    },
)
_OptionalGetLogEventsRequestRequestTypeDef = TypedDict(
    "_OptionalGetLogEventsRequestRequestTypeDef",
    {
        "startTime": int,
        "endTime": int,
        "nextToken": str,
        "limit": int,
        "startFromHead": bool,
    },
    total=False,
)


class GetLogEventsRequestRequestTypeDef(
    _RequiredGetLogEventsRequestRequestTypeDef, _OptionalGetLogEventsRequestRequestTypeDef
):
    pass


OutputLogEventTypeDef = TypedDict(
    "OutputLogEventTypeDef",
    {
        "timestamp": int,
        "message": str,
        "ingestionTime": int,
    },
    total=False,
)

_RequiredGetLogGroupFieldsRequestRequestTypeDef = TypedDict(
    "_RequiredGetLogGroupFieldsRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)
_OptionalGetLogGroupFieldsRequestRequestTypeDef = TypedDict(
    "_OptionalGetLogGroupFieldsRequestRequestTypeDef",
    {
        "time": int,
    },
    total=False,
)


class GetLogGroupFieldsRequestRequestTypeDef(
    _RequiredGetLogGroupFieldsRequestRequestTypeDef, _OptionalGetLogGroupFieldsRequestRequestTypeDef
):
    pass


LogGroupFieldTypeDef = TypedDict(
    "LogGroupFieldTypeDef",
    {
        "name": str,
        "percent": int,
    },
    total=False,
)

GetLogRecordRequestRequestTypeDef = TypedDict(
    "GetLogRecordRequestRequestTypeDef",
    {
        "logRecordPointer": str,
    },
)

GetQueryResultsRequestRequestTypeDef = TypedDict(
    "GetQueryResultsRequestRequestTypeDef",
    {
        "queryId": str,
    },
)

QueryStatisticsTypeDef = TypedDict(
    "QueryStatisticsTypeDef",
    {
        "recordsMatched": float,
        "recordsScanned": float,
        "bytesScanned": float,
    },
    total=False,
)

ResultFieldTypeDef = TypedDict(
    "ResultFieldTypeDef",
    {
        "field": str,
        "value": str,
    },
    total=False,
)

InputLogEventTypeDef = TypedDict(
    "InputLogEventTypeDef",
    {
        "timestamp": int,
        "message": str,
    },
)

ListTagsLogGroupRequestRequestTypeDef = TypedDict(
    "ListTagsLogGroupRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)

MetricFilterMatchRecordTypeDef = TypedDict(
    "MetricFilterMatchRecordTypeDef",
    {
        "eventNumber": int,
        "eventMessage": str,
        "extractedValues": Dict[str, str],
    },
    total=False,
)

_RequiredMetricTransformationTypeDef = TypedDict(
    "_RequiredMetricTransformationTypeDef",
    {
        "metricName": str,
        "metricNamespace": str,
        "metricValue": str,
    },
)
_OptionalMetricTransformationTypeDef = TypedDict(
    "_OptionalMetricTransformationTypeDef",
    {
        "defaultValue": float,
        "dimensions": Dict[str, str],
        "unit": StandardUnitType,
    },
    total=False,
)


class MetricTransformationTypeDef(
    _RequiredMetricTransformationTypeDef, _OptionalMetricTransformationTypeDef
):
    pass


_RequiredPutDestinationPolicyRequestRequestTypeDef = TypedDict(
    "_RequiredPutDestinationPolicyRequestRequestTypeDef",
    {
        "destinationName": str,
        "accessPolicy": str,
    },
)
_OptionalPutDestinationPolicyRequestRequestTypeDef = TypedDict(
    "_OptionalPutDestinationPolicyRequestRequestTypeDef",
    {
        "forceUpdate": bool,
    },
    total=False,
)


class PutDestinationPolicyRequestRequestTypeDef(
    _RequiredPutDestinationPolicyRequestRequestTypeDef,
    _OptionalPutDestinationPolicyRequestRequestTypeDef,
):
    pass


PutDestinationRequestRequestTypeDef = TypedDict(
    "PutDestinationRequestRequestTypeDef",
    {
        "destinationName": str,
        "targetArn": str,
        "roleArn": str,
    },
)

RejectedLogEventsInfoTypeDef = TypedDict(
    "RejectedLogEventsInfoTypeDef",
    {
        "tooNewLogEventStartIndex": int,
        "tooOldLogEventEndIndex": int,
        "expiredLogEventEndIndex": int,
    },
    total=False,
)

_RequiredPutQueryDefinitionRequestRequestTypeDef = TypedDict(
    "_RequiredPutQueryDefinitionRequestRequestTypeDef",
    {
        "name": str,
        "queryString": str,
    },
)
_OptionalPutQueryDefinitionRequestRequestTypeDef = TypedDict(
    "_OptionalPutQueryDefinitionRequestRequestTypeDef",
    {
        "queryDefinitionId": str,
        "logGroupNames": Sequence[str],
    },
    total=False,
)


class PutQueryDefinitionRequestRequestTypeDef(
    _RequiredPutQueryDefinitionRequestRequestTypeDef,
    _OptionalPutQueryDefinitionRequestRequestTypeDef,
):
    pass


PutResourcePolicyRequestRequestTypeDef = TypedDict(
    "PutResourcePolicyRequestRequestTypeDef",
    {
        "policyName": str,
        "policyDocument": str,
    },
    total=False,
)

PutRetentionPolicyRequestRequestTypeDef = TypedDict(
    "PutRetentionPolicyRequestRequestTypeDef",
    {
        "logGroupName": str,
        "retentionInDays": int,
    },
)

_RequiredPutSubscriptionFilterRequestRequestTypeDef = TypedDict(
    "_RequiredPutSubscriptionFilterRequestRequestTypeDef",
    {
        "logGroupName": str,
        "filterName": str,
        "filterPattern": str,
        "destinationArn": str,
    },
)
_OptionalPutSubscriptionFilterRequestRequestTypeDef = TypedDict(
    "_OptionalPutSubscriptionFilterRequestRequestTypeDef",
    {
        "roleArn": str,
        "distribution": DistributionType,
    },
    total=False,
)


class PutSubscriptionFilterRequestRequestTypeDef(
    _RequiredPutSubscriptionFilterRequestRequestTypeDef,
    _OptionalPutSubscriptionFilterRequestRequestTypeDef,
):
    pass


_RequiredStartQueryRequestRequestTypeDef = TypedDict(
    "_RequiredStartQueryRequestRequestTypeDef",
    {
        "startTime": int,
        "endTime": int,
        "queryString": str,
    },
)
_OptionalStartQueryRequestRequestTypeDef = TypedDict(
    "_OptionalStartQueryRequestRequestTypeDef",
    {
        "logGroupName": str,
        "logGroupNames": Sequence[str],
        "limit": int,
    },
    total=False,
)


class StartQueryRequestRequestTypeDef(
    _RequiredStartQueryRequestRequestTypeDef, _OptionalStartQueryRequestRequestTypeDef
):
    pass


StopQueryRequestRequestTypeDef = TypedDict(
    "StopQueryRequestRequestTypeDef",
    {
        "queryId": str,
    },
)

TagLogGroupRequestRequestTypeDef = TypedDict(
    "TagLogGroupRequestRequestTypeDef",
    {
        "logGroupName": str,
        "tags": Mapping[str, str],
    },
)

TestMetricFilterRequestRequestTypeDef = TypedDict(
    "TestMetricFilterRequestRequestTypeDef",
    {
        "filterPattern": str,
        "logEventMessages": Sequence[str],
    },
)

UntagLogGroupRequestRequestTypeDef = TypedDict(
    "UntagLogGroupRequestRequestTypeDef",
    {
        "logGroupName": str,
        "tags": Sequence[str],
    },
)

CreateExportTaskResponseTypeDef = TypedDict(
    "CreateExportTaskResponseTypeDef",
    {
        "taskId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteQueryDefinitionResponseTypeDef = TypedDict(
    "DeleteQueryDefinitionResponseTypeDef",
    {
        "success": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetLogRecordResponseTypeDef = TypedDict(
    "GetLogRecordResponseTypeDef",
    {
        "logRecord": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsLogGroupResponseTypeDef = TypedDict(
    "ListTagsLogGroupResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutQueryDefinitionResponseTypeDef = TypedDict(
    "PutQueryDefinitionResponseTypeDef",
    {
        "queryDefinitionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartQueryResponseTypeDef = TypedDict(
    "StartQueryResponseTypeDef",
    {
        "queryId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopQueryResponseTypeDef = TypedDict(
    "StopQueryResponseTypeDef",
    {
        "success": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDestinationsRequestDescribeDestinationsPaginateTypeDef = TypedDict(
    "DescribeDestinationsRequestDescribeDestinationsPaginateTypeDef",
    {
        "DestinationNamePrefix": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeExportTasksRequestDescribeExportTasksPaginateTypeDef = TypedDict(
    "DescribeExportTasksRequestDescribeExportTasksPaginateTypeDef",
    {
        "taskId": str,
        "statusCode": ExportTaskStatusCodeType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeLogGroupsRequestDescribeLogGroupsPaginateTypeDef = TypedDict(
    "DescribeLogGroupsRequestDescribeLogGroupsPaginateTypeDef",
    {
        "logGroupNamePrefix": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredDescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef = TypedDict(
    "_RequiredDescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef",
    {
        "logGroupName": str,
    },
)
_OptionalDescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef = TypedDict(
    "_OptionalDescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef",
    {
        "logStreamNamePrefix": str,
        "orderBy": OrderByType,
        "descending": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef(
    _RequiredDescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef,
    _OptionalDescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef,
):
    pass


DescribeMetricFiltersRequestDescribeMetricFiltersPaginateTypeDef = TypedDict(
    "DescribeMetricFiltersRequestDescribeMetricFiltersPaginateTypeDef",
    {
        "logGroupName": str,
        "filterNamePrefix": str,
        "metricName": str,
        "metricNamespace": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeQueriesRequestDescribeQueriesPaginateTypeDef = TypedDict(
    "DescribeQueriesRequestDescribeQueriesPaginateTypeDef",
    {
        "logGroupName": str,
        "status": QueryStatusType,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

DescribeResourcePoliciesRequestDescribeResourcePoliciesPaginateTypeDef = TypedDict(
    "DescribeResourcePoliciesRequestDescribeResourcePoliciesPaginateTypeDef",
    {
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)

_RequiredDescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef = TypedDict(
    "_RequiredDescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef",
    {
        "logGroupName": str,
    },
)
_OptionalDescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef = TypedDict(
    "_OptionalDescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef",
    {
        "filterNamePrefix": str,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class DescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef(
    _RequiredDescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef,
    _OptionalDescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef,
):
    pass


_RequiredFilterLogEventsRequestFilterLogEventsPaginateTypeDef = TypedDict(
    "_RequiredFilterLogEventsRequestFilterLogEventsPaginateTypeDef",
    {
        "logGroupName": str,
    },
)
_OptionalFilterLogEventsRequestFilterLogEventsPaginateTypeDef = TypedDict(
    "_OptionalFilterLogEventsRequestFilterLogEventsPaginateTypeDef",
    {
        "logStreamNames": Sequence[str],
        "logStreamNamePrefix": str,
        "startTime": int,
        "endTime": int,
        "filterPattern": str,
        "interleaved": bool,
        "PaginationConfig": PaginatorConfigTypeDef,
    },
    total=False,
)


class FilterLogEventsRequestFilterLogEventsPaginateTypeDef(
    _RequiredFilterLogEventsRequestFilterLogEventsPaginateTypeDef,
    _OptionalFilterLogEventsRequestFilterLogEventsPaginateTypeDef,
):
    pass


DescribeDestinationsResponseTypeDef = TypedDict(
    "DescribeDestinationsResponseTypeDef",
    {
        "destinations": List[DestinationTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutDestinationResponseTypeDef = TypedDict(
    "PutDestinationResponseTypeDef",
    {
        "destination": DestinationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLogGroupsResponseTypeDef = TypedDict(
    "DescribeLogGroupsResponseTypeDef",
    {
        "logGroups": List[LogGroupTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLogStreamsResponseTypeDef = TypedDict(
    "DescribeLogStreamsResponseTypeDef",
    {
        "logStreams": List[LogStreamTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeQueriesResponseTypeDef = TypedDict(
    "DescribeQueriesResponseTypeDef",
    {
        "queries": List[QueryInfoTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeQueryDefinitionsResponseTypeDef = TypedDict(
    "DescribeQueryDefinitionsResponseTypeDef",
    {
        "queryDefinitions": List[QueryDefinitionTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeResourcePoliciesResponseTypeDef = TypedDict(
    "DescribeResourcePoliciesResponseTypeDef",
    {
        "resourcePolicies": List[ResourcePolicyTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutResourcePolicyResponseTypeDef = TypedDict(
    "PutResourcePolicyResponseTypeDef",
    {
        "resourcePolicy": ResourcePolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSubscriptionFiltersResponseTypeDef = TypedDict(
    "DescribeSubscriptionFiltersResponseTypeDef",
    {
        "subscriptionFilters": List[SubscriptionFilterTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExportTaskTypeDef = TypedDict(
    "ExportTaskTypeDef",
    {
        "taskId": str,
        "taskName": str,
        "logGroupName": str,
        "from": int,
        "to": int,
        "destination": str,
        "destinationPrefix": str,
        "status": ExportTaskStatusTypeDef,
        "executionInfo": ExportTaskExecutionInfoTypeDef,
    },
    total=False,
)

FilterLogEventsResponseTypeDef = TypedDict(
    "FilterLogEventsResponseTypeDef",
    {
        "events": List[FilteredLogEventTypeDef],
        "searchedLogStreams": List[SearchedLogStreamTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetLogEventsResponseTypeDef = TypedDict(
    "GetLogEventsResponseTypeDef",
    {
        "events": List[OutputLogEventTypeDef],
        "nextForwardToken": str,
        "nextBackwardToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetLogGroupFieldsResponseTypeDef = TypedDict(
    "GetLogGroupFieldsResponseTypeDef",
    {
        "logGroupFields": List[LogGroupFieldTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetQueryResultsResponseTypeDef = TypedDict(
    "GetQueryResultsResponseTypeDef",
    {
        "results": List[List[ResultFieldTypeDef]],
        "statistics": QueryStatisticsTypeDef,
        "status": QueryStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

_RequiredPutLogEventsRequestRequestTypeDef = TypedDict(
    "_RequiredPutLogEventsRequestRequestTypeDef",
    {
        "logGroupName": str,
        "logStreamName": str,
        "logEvents": Sequence[InputLogEventTypeDef],
    },
)
_OptionalPutLogEventsRequestRequestTypeDef = TypedDict(
    "_OptionalPutLogEventsRequestRequestTypeDef",
    {
        "sequenceToken": str,
    },
    total=False,
)


class PutLogEventsRequestRequestTypeDef(
    _RequiredPutLogEventsRequestRequestTypeDef, _OptionalPutLogEventsRequestRequestTypeDef
):
    pass


TestMetricFilterResponseTypeDef = TypedDict(
    "TestMetricFilterResponseTypeDef",
    {
        "matches": List[MetricFilterMatchRecordTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MetricFilterTypeDef = TypedDict(
    "MetricFilterTypeDef",
    {
        "filterName": str,
        "filterPattern": str,
        "metricTransformations": List[MetricTransformationTypeDef],
        "creationTime": int,
        "logGroupName": str,
    },
    total=False,
)

PutMetricFilterRequestRequestTypeDef = TypedDict(
    "PutMetricFilterRequestRequestTypeDef",
    {
        "logGroupName": str,
        "filterName": str,
        "filterPattern": str,
        "metricTransformations": Sequence[MetricTransformationTypeDef],
    },
)

PutLogEventsResponseTypeDef = TypedDict(
    "PutLogEventsResponseTypeDef",
    {
        "nextSequenceToken": str,
        "rejectedLogEventsInfo": RejectedLogEventsInfoTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeExportTasksResponseTypeDef = TypedDict(
    "DescribeExportTasksResponseTypeDef",
    {
        "exportTasks": List[ExportTaskTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeMetricFiltersResponseTypeDef = TypedDict(
    "DescribeMetricFiltersResponseTypeDef",
    {
        "metricFilters": List[MetricFilterTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
