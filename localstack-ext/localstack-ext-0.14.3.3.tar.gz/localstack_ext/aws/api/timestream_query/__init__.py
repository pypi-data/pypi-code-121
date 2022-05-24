import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AmazonResourceName = str
ClientRequestToken = str
ClientToken = str
Double = float
ErrorMessage = str
MaxQueryResults = int
MaxScheduledQueriesResults = int
MaxTagsForResourceResult = int
NextScheduledQueriesResultsToken = str
NextTagsForResourceResultsToken = str
NullableBoolean = bool
PaginationToken = str
QueryId = str
QueryString = str
ResourceName = str
S3BucketName = str
S3ObjectKey = str
S3ObjectKeyPrefix = str
ScalarValue = str
ScheduleExpression = str
ScheduledQueryName = str
SchemaName = str
ServiceErrorMessage = str
String = str
StringValue2048 = str
TagKey = str
TagValue = str
Timestamp = str


class DimensionValueType(str):
    VARCHAR = "VARCHAR"


class MeasureValueType(str):
    BIGINT = "BIGINT"
    BOOLEAN = "BOOLEAN"
    DOUBLE = "DOUBLE"
    VARCHAR = "VARCHAR"
    MULTI = "MULTI"


class S3EncryptionOption(str):
    SSE_S3 = "SSE_S3"
    SSE_KMS = "SSE_KMS"


class ScalarMeasureValueType(str):
    BIGINT = "BIGINT"
    BOOLEAN = "BOOLEAN"
    DOUBLE = "DOUBLE"
    VARCHAR = "VARCHAR"
    TIMESTAMP = "TIMESTAMP"


class ScalarType(str):
    VARCHAR = "VARCHAR"
    BOOLEAN = "BOOLEAN"
    BIGINT = "BIGINT"
    DOUBLE = "DOUBLE"
    TIMESTAMP = "TIMESTAMP"
    DATE = "DATE"
    TIME = "TIME"
    INTERVAL_DAY_TO_SECOND = "INTERVAL_DAY_TO_SECOND"
    INTERVAL_YEAR_TO_MONTH = "INTERVAL_YEAR_TO_MONTH"
    UNKNOWN = "UNKNOWN"
    INTEGER = "INTEGER"


class ScheduledQueryRunStatus(str):
    AUTO_TRIGGER_SUCCESS = "AUTO_TRIGGER_SUCCESS"
    AUTO_TRIGGER_FAILURE = "AUTO_TRIGGER_FAILURE"
    MANUAL_TRIGGER_SUCCESS = "MANUAL_TRIGGER_SUCCESS"
    MANUAL_TRIGGER_FAILURE = "MANUAL_TRIGGER_FAILURE"


class ScheduledQueryState(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class AccessDeniedException(ServiceException):
    """You are not authorized to perform this action."""

    Message: Optional[ServiceErrorMessage]


class ConflictException(ServiceException):
    """Unable to poll results for a cancelled query."""

    Message: Optional[ErrorMessage]


class InternalServerException(ServiceException):
    """Timestream was unable to fully process this request because of an
    internal server error.
    """

    Message: Optional[ErrorMessage]


class InvalidEndpointException(ServiceException):
    """The requested endpoint was not valid."""

    Message: Optional[ErrorMessage]


class QueryExecutionException(ServiceException):
    """Timestream was unable to run the query successfully."""

    Message: Optional[ErrorMessage]


class ResourceNotFoundException(ServiceException):
    """The requested resource could not be found."""

    Message: Optional[ErrorMessage]
    ScheduledQueryArn: Optional[AmazonResourceName]


class ServiceQuotaExceededException(ServiceException):
    """You have exceeded the service quota."""

    Message: Optional[ErrorMessage]


class ThrottlingException(ServiceException):
    """The request was denied due to request throttling."""

    Message: Optional[ErrorMessage]


class ValidationException(ServiceException):
    """Invalid or malformed request."""

    Message: Optional[ErrorMessage]


class CancelQueryRequest(ServiceRequest):
    QueryId: QueryId


class CancelQueryResponse(TypedDict, total=False):
    CancellationMessage: Optional[String]


class ColumnInfo(TypedDict, total=False):
    """Contains the metadata for query results such as the column names, data
    types, and other attributes.
    """

    Name: Optional["String"]
    Type: "Type"


ColumnInfoList = List[ColumnInfo]


class Type(TypedDict, total=False):
    """Contains the data type of a column in a query result set. The data type
    can be scalar or complex. The supported scalar data types are integers,
    Boolean, string, double, timestamp, date, time, and intervals. The
    supported complex data types are arrays, rows, and timeseries.
    """

    ScalarType: Optional[ScalarType]
    ArrayColumnInfo: Optional[ColumnInfo]
    TimeSeriesMeasureValueColumnInfo: Optional[ColumnInfo]
    RowColumnInfo: Optional[ColumnInfoList]


class S3Configuration(TypedDict, total=False):
    """Details on S3 location for error reports that result from running a
    query.
    """

    BucketName: S3BucketName
    ObjectKeyPrefix: Optional[S3ObjectKeyPrefix]
    EncryptionOption: Optional[S3EncryptionOption]


class ErrorReportConfiguration(TypedDict, total=False):
    """Configuration required for error reporting."""

    S3Configuration: S3Configuration


class Tag(TypedDict, total=False):
    """A tag is a label that you assign to a Timestream database and/or table.
    Each tag consists of a key and an optional value, both of which you
    define. Tags enable you to categorize databases and/or tables, for
    example, by purpose, owner, or environment.
    """

    Key: TagKey
    Value: TagValue


TagList = List[Tag]


class MultiMeasureAttributeMapping(TypedDict, total=False):
    """Attribute mapping for MULTI value measures."""

    SourceColumn: SchemaName
    TargetMultiMeasureAttributeName: Optional[SchemaName]
    MeasureValueType: ScalarMeasureValueType


MultiMeasureAttributeMappingList = List[MultiMeasureAttributeMapping]


class MixedMeasureMapping(TypedDict, total=False):
    """MixedMeasureMappings are mappings that can be used to ingest data into a
    mixture of narrow and multi measures in the derived table.
    """

    MeasureName: Optional[SchemaName]
    SourceColumn: Optional[SchemaName]
    TargetMeasureName: Optional[SchemaName]
    MeasureValueType: MeasureValueType
    MultiMeasureAttributeMappings: Optional[MultiMeasureAttributeMappingList]


MixedMeasureMappingList = List[MixedMeasureMapping]


class MultiMeasureMappings(TypedDict, total=False):
    """Only one of MixedMeasureMappings or MultiMeasureMappings is to be
    provided. MultiMeasureMappings can be used to ingest data as multi
    measures in the derived table.
    """

    TargetMultiMeasureName: Optional[SchemaName]
    MultiMeasureAttributeMappings: MultiMeasureAttributeMappingList


class DimensionMapping(TypedDict, total=False):
    """This type is used to map column(s) from the query result to a dimension
    in the destination table.
    """

    Name: SchemaName
    DimensionValueType: DimensionValueType


DimensionMappingList = List[DimensionMapping]


class TimestreamConfiguration(TypedDict, total=False):
    """Configuration to write data into Timestream database and table. This
    configuration allows the user to map the query result select columns
    into the destination table columns.
    """

    DatabaseName: ResourceName
    TableName: ResourceName
    TimeColumn: SchemaName
    DimensionMappings: DimensionMappingList
    MultiMeasureMappings: Optional[MultiMeasureMappings]
    MixedMeasureMappings: Optional[MixedMeasureMappingList]
    MeasureNameColumn: Optional[SchemaName]


class TargetConfiguration(TypedDict, total=False):
    """Configuration used for writing the output of a query."""

    TimestreamConfiguration: TimestreamConfiguration


class SnsConfiguration(TypedDict, total=False):
    """Details on SNS that are required to send the notification."""

    TopicArn: AmazonResourceName


class NotificationConfiguration(TypedDict, total=False):
    """Notification configuration for a scheduled query. A notification is sent
    by Timestream when a scheduled query is created, its state is updated or
    when it is deleted.
    """

    SnsConfiguration: SnsConfiguration


class ScheduleConfiguration(TypedDict, total=False):
    """Configuration of the schedule of the query."""

    ScheduleExpression: ScheduleExpression


class CreateScheduledQueryRequest(ServiceRequest):
    Name: ScheduledQueryName
    QueryString: QueryString
    ScheduleConfiguration: ScheduleConfiguration
    NotificationConfiguration: NotificationConfiguration
    TargetConfiguration: Optional[TargetConfiguration]
    ClientToken: Optional[ClientToken]
    ScheduledQueryExecutionRoleArn: AmazonResourceName
    Tags: Optional[TagList]
    KmsKeyId: Optional[StringValue2048]
    ErrorReportConfiguration: ErrorReportConfiguration


class CreateScheduledQueryResponse(TypedDict, total=False):
    Arn: AmazonResourceName


class Datum(TypedDict, total=False):
    """Datum represents a single data point in a query result."""

    ScalarValue: Optional["ScalarValue"]
    TimeSeriesValue: Optional["TimeSeriesDataPointList"]
    ArrayValue: Optional["DatumList"]
    RowValue: Optional["Row"]
    NullValue: Optional["NullableBoolean"]


DatumList = List[Datum]


class Row(TypedDict, total=False):
    """Represents a single row in the query results."""

    Data: DatumList


class TimeSeriesDataPoint(TypedDict, total=False):
    """The timeseries data type represents the values of a measure over time. A
    time series is an array of rows of timestamps and measure values, with
    rows sorted in ascending order of time. A TimeSeriesDataPoint is a
    single data point in the time series. It represents a tuple of (time,
    measure value) in a time series.
    """

    Time: Timestamp
    Value: Datum


TimeSeriesDataPointList = List[TimeSeriesDataPoint]


class DeleteScheduledQueryRequest(ServiceRequest):
    ScheduledQueryArn: AmazonResourceName


class DescribeEndpointsRequest(ServiceRequest):
    pass


Long = int


class Endpoint(TypedDict, total=False):
    """Represents an available endpoint against which to make API calls
    against, as well as the TTL for that endpoint.
    """

    Address: String
    CachePeriodInMinutes: Long


Endpoints = List[Endpoint]


class DescribeEndpointsResponse(TypedDict, total=False):
    Endpoints: Endpoints


class DescribeScheduledQueryRequest(ServiceRequest):
    ScheduledQueryArn: AmazonResourceName


class S3ReportLocation(TypedDict, total=False):
    """S3 report location for the scheduled query run."""

    BucketName: Optional[S3BucketName]
    ObjectKey: Optional[S3ObjectKey]


class ErrorReportLocation(TypedDict, total=False):
    """This contains the location of the error report for a single scheduled
    query call.
    """

    S3ReportLocation: Optional[S3ReportLocation]


class ExecutionStats(TypedDict, total=False):
    """Statistics for a single scheduled query run."""

    ExecutionTimeInMillis: Optional[Long]
    DataWrites: Optional[Long]
    BytesMetered: Optional[Long]
    RecordsIngested: Optional[Long]
    QueryResultRows: Optional[Long]


Time = datetime


class ScheduledQueryRunSummary(TypedDict, total=False):
    """Run summary for the scheduled query"""

    InvocationTime: Optional[Time]
    TriggerTime: Optional[Time]
    RunStatus: Optional[ScheduledQueryRunStatus]
    ExecutionStats: Optional[ExecutionStats]
    ErrorReportLocation: Optional[ErrorReportLocation]
    FailureReason: Optional[ErrorMessage]


ScheduledQueryRunSummaryList = List[ScheduledQueryRunSummary]


class ScheduledQueryDescription(TypedDict, total=False):
    """Structure that describes scheduled query."""

    Arn: AmazonResourceName
    Name: ScheduledQueryName
    QueryString: QueryString
    CreationTime: Optional[Time]
    State: ScheduledQueryState
    PreviousInvocationTime: Optional[Time]
    NextInvocationTime: Optional[Time]
    ScheduleConfiguration: ScheduleConfiguration
    NotificationConfiguration: NotificationConfiguration
    TargetConfiguration: Optional[TargetConfiguration]
    ScheduledQueryExecutionRoleArn: Optional[AmazonResourceName]
    KmsKeyId: Optional[StringValue2048]
    ErrorReportConfiguration: Optional[ErrorReportConfiguration]
    LastRunSummary: Optional[ScheduledQueryRunSummary]
    RecentlyFailedRuns: Optional[ScheduledQueryRunSummaryList]


class DescribeScheduledQueryResponse(TypedDict, total=False):
    ScheduledQuery: ScheduledQueryDescription


class ExecuteScheduledQueryRequest(ServiceRequest):
    ScheduledQueryArn: AmazonResourceName
    InvocationTime: Time
    ClientToken: Optional[ClientToken]


class ListScheduledQueriesRequest(ServiceRequest):
    MaxResults: Optional[MaxScheduledQueriesResults]
    NextToken: Optional[NextScheduledQueriesResultsToken]


class TimestreamDestination(TypedDict, total=False):
    """Destination for scheduled query."""

    DatabaseName: Optional[ResourceName]
    TableName: Optional[ResourceName]


class TargetDestination(TypedDict, total=False):
    """Destination details to write data for a target data source. Current
    supported data source is Timestream.
    """

    TimestreamDestination: Optional[TimestreamDestination]


class ScheduledQuery(TypedDict, total=False):
    """Scheduled Query"""

    Arn: AmazonResourceName
    Name: ScheduledQueryName
    CreationTime: Optional[Time]
    State: ScheduledQueryState
    PreviousInvocationTime: Optional[Time]
    NextInvocationTime: Optional[Time]
    ErrorReportConfiguration: Optional[ErrorReportConfiguration]
    TargetDestination: Optional[TargetDestination]
    LastRunStatus: Optional[ScheduledQueryRunStatus]


ScheduledQueryList = List[ScheduledQuery]


class ListScheduledQueriesResponse(TypedDict, total=False):
    ScheduledQueries: ScheduledQueryList
    NextToken: Optional[NextScheduledQueriesResultsToken]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceARN: AmazonResourceName
    MaxResults: Optional[MaxTagsForResourceResult]
    NextToken: Optional[NextTagsForResourceResultsToken]


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: TagList
    NextToken: Optional[NextTagsForResourceResultsToken]


class ParameterMapping(TypedDict, total=False):
    """Mapping for named parameters."""

    Name: String
    Type: Type


ParameterMappingList = List[ParameterMapping]


class PrepareQueryRequest(ServiceRequest):
    QueryString: QueryString
    ValidateOnly: Optional[NullableBoolean]


class SelectColumn(TypedDict, total=False):
    """Details of the column that is returned by the query."""

    Name: Optional[String]
    Type: Optional[Type]
    DatabaseName: Optional[ResourceName]
    TableName: Optional[ResourceName]
    Aliased: Optional[NullableBoolean]


SelectColumnList = List[SelectColumn]


class PrepareQueryResponse(TypedDict, total=False):
    QueryString: QueryString
    Columns: SelectColumnList
    Parameters: ParameterMappingList


class QueryRequest(ServiceRequest):
    QueryString: QueryString
    ClientToken: Optional[ClientRequestToken]
    NextToken: Optional[PaginationToken]
    MaxRows: Optional[MaxQueryResults]


class QueryStatus(TypedDict, total=False):
    """Information about the status of the query, including progress and bytes
    scanned.
    """

    ProgressPercentage: Optional[Double]
    CumulativeBytesScanned: Optional[Long]
    CumulativeBytesMetered: Optional[Long]


RowList = List[Row]


class QueryResponse(TypedDict, total=False):
    QueryId: QueryId
    NextToken: Optional[PaginationToken]
    Rows: RowList
    ColumnInfo: ColumnInfoList
    QueryStatus: Optional[QueryStatus]


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    ResourceARN: AmazonResourceName
    Tags: TagList


class TagResourceResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    ResourceARN: AmazonResourceName
    TagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateScheduledQueryRequest(ServiceRequest):
    ScheduledQueryArn: AmazonResourceName
    State: ScheduledQueryState


class TimestreamQueryApi:

    service = "timestream-query"
    version = "2018-11-01"

    @handler("CancelQuery")
    def cancel_query(self, context: RequestContext, query_id: QueryId) -> CancelQueryResponse:
        """Cancels a query that has been issued. Cancellation is provided only if
        the query has not completed running before the cancellation request was
        issued. Because cancellation is an idempotent operation, subsequent
        cancellation requests will return a ``CancellationMessage``, indicating
        that the query has already been canceled. See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.cancel-query.html>`__
        for details.

        :param query_id: The ID of the query that needs to be cancelled.
        :returns: CancelQueryResponse
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("CreateScheduledQuery")
    def create_scheduled_query(
        self,
        context: RequestContext,
        name: ScheduledQueryName,
        query_string: QueryString,
        schedule_configuration: ScheduleConfiguration,
        notification_configuration: NotificationConfiguration,
        scheduled_query_execution_role_arn: AmazonResourceName,
        error_report_configuration: ErrorReportConfiguration,
        target_configuration: TargetConfiguration = None,
        client_token: ClientToken = None,
        tags: TagList = None,
        kms_key_id: StringValue2048 = None,
    ) -> CreateScheduledQueryResponse:
        """Create a scheduled query that will be run on your behalf at the
        configured schedule. Timestream assumes the execution role provided as
        part of the ``ScheduledQueryExecutionRoleArn`` parameter to run the
        query. You can use the ``NotificationConfiguration`` parameter to
        configure notification for your scheduled query operations.

        :param name: Name of the scheduled query.
        :param query_string: The query string to run.
        :param schedule_configuration: The schedule configuration for the query.
        :param notification_configuration: Notification configuration for the scheduled query.
        :param scheduled_query_execution_role_arn: The ARN for the IAM role that Timestream will assume when running the
        scheduled query.
        :param error_report_configuration: Configuration for error reporting.
        :param target_configuration: Configuration used for writing the result of a query.
        :param client_token: Using a ClientToken makes the call to CreateScheduledQuery idempotent,
        in other words, making the same request repeatedly will produce the same
        result.
        :param tags: A list of key-value pairs to label the scheduled query.
        :param kms_key_id: The Amazon KMS key used to encrypt the scheduled query resource,
        at-rest.
        :returns: CreateScheduledQueryResponse
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises ServiceQuotaExceededException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("DeleteScheduledQuery")
    def delete_scheduled_query(
        self, context: RequestContext, scheduled_query_arn: AmazonResourceName
    ) -> None:
        """Deletes a given scheduled query. This is an irreversible operation.

        :param scheduled_query_arn: The ARN of the scheduled query.
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("DescribeEndpoints")
    def describe_endpoints(
        self,
        context: RequestContext,
    ) -> DescribeEndpointsResponse:
        """DescribeEndpoints returns a list of available endpoints to make
        Timestream API calls against. This API is available through both Write
        and Query.

        Because the Timestream SDKs are designed to transparently work with the
        service’s architecture, including the management and mapping of the
        service endpoints, *it is not recommended that you use this API unless*:

        -  You are using `VPC endpoints (Amazon Web Services PrivateLink) with
           Timestream <https://docs.aws.amazon.com/timestream/latest/developerguide/VPCEndpoints>`__

        -  Your application uses a programming language that does not yet have
           SDK support

        -  You require better control over the client-side implementation

        For detailed information on how and when to use and implement
        DescribeEndpoints, see `The Endpoint Discovery
        Pattern <https://docs.aws.amazon.com/timestream/latest/developerguide/Using.API.html#Using-API.endpoint-discovery>`__.

        :returns: DescribeEndpointsResponse
        :raises InternalServerException:
        :raises ValidationException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DescribeScheduledQuery")
    def describe_scheduled_query(
        self, context: RequestContext, scheduled_query_arn: AmazonResourceName
    ) -> DescribeScheduledQueryResponse:
        """Provides detailed information about a scheduled query.

        :param scheduled_query_arn: The ARN of the scheduled query.
        :returns: DescribeScheduledQueryResponse
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("ExecuteScheduledQuery")
    def execute_scheduled_query(
        self,
        context: RequestContext,
        scheduled_query_arn: AmazonResourceName,
        invocation_time: Time,
        client_token: ClientToken = None,
    ) -> None:
        """You can use this API to run a scheduled query manually.

        :param scheduled_query_arn: ARN of the scheduled query.
        :param invocation_time: The timestamp in UTC.
        :param client_token: Not used.
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("ListScheduledQueries")
    def list_scheduled_queries(
        self,
        context: RequestContext,
        max_results: MaxScheduledQueriesResults = None,
        next_token: NextScheduledQueriesResultsToken = None,
    ) -> ListScheduledQueriesResponse:
        """Gets a list of all scheduled queries in the caller's Amazon account and
        Region. ``ListScheduledQueries`` is eventually consistent.

        :param max_results: The maximum number of items to return in the output.
        :param next_token: A pagination token to resume pagination.
        :returns: ListScheduledQueriesResponse
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self,
        context: RequestContext,
        resource_arn: AmazonResourceName,
        max_results: MaxTagsForResourceResult = None,
        next_token: NextTagsForResourceResultsToken = None,
    ) -> ListTagsForResourceResponse:
        """List all tags on a Timestream query resource.

        :param resource_arn: The Timestream resource with tags to be listed.
        :param max_results: The maximum number of tags to return.
        :param next_token: A pagination token to resume pagination.
        :returns: ListTagsForResourceResponse
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("PrepareQuery")
    def prepare_query(
        self,
        context: RequestContext,
        query_string: QueryString,
        validate_only: NullableBoolean = None,
    ) -> PrepareQueryResponse:
        """A synchronous operation that allows you to submit a query with
        parameters to be stored by Timestream for later running. Timestream only
        supports using this operation with the
        ``PrepareQueryRequest$ValidateOnly`` set to ``true``.

        :param query_string: The Timestream query string that you want to use as a prepared
        statement.
        :param validate_only: By setting this value to ``true``, Timestream will only validate that
        the query string is a valid Timestream query, and not store the prepared
        query for later use.
        :returns: PrepareQueryResponse
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("Query")
    def query(
        self,
        context: RequestContext,
        query_string: QueryString,
        client_token: ClientRequestToken = None,
        next_token: PaginationToken = None,
        max_rows: MaxQueryResults = None,
    ) -> QueryResponse:
        """``Query`` is a synchronous operation that enables you to run a query
        against your Amazon Timestream data. ``Query`` will time out after 60
        seconds. You must update the default timeout in the SDK to support a
        timeout of 60 seconds. See the `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.run-query.html>`__
        for details.

        Your query request will fail in the following cases:

        -  If you submit a ``Query`` request with the same client token outside
           of the 5-minute idempotency window.

        -  If you submit a ``Query`` request with the same client token, but
           change other parameters, within the 5-minute idempotency window.

        -  If the size of the row (including the query metadata) exceeds 1 MB,
           then the query will fail with the following error message:

           ``Query aborted as max page response size has been exceeded by the output result row``

        -  If the IAM principal of the query initiator and the result reader are
           not the same and/or the query initiator and the result reader do not
           have the same query string in the query requests, the query will fail
           with an ``Invalid pagination token`` error.

        :param query_string: The query to be run by Timestream.
        :param client_token: Unique, case-sensitive string of up to 64 ASCII characters specified
        when a ``Query`` request is made.
        :param next_token: A pagination token used to return a set of results.
        :param max_rows: The total number of rows to be returned in the ``Query`` output.
        :returns: QueryResponse
        :raises AccessDeniedException:
        :raises ConflictException:
        :raises InternalServerException:
        :raises QueryExecutionException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tags: TagList
    ) -> TagResourceResponse:
        """Associate a set of tags with a Timestream resource. You can then
        activate these user-defined tags so that they appear on the Billing and
        Cost Management console for cost allocation tracking.

        :param resource_arn: Identifies the Timestream resource to which tags should be added.
        :param tags: The tags to be assigned to the Timestream resource.
        :returns: TagResourceResponse
        :raises ResourceNotFoundException:
        :raises ServiceQuotaExceededException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Removes the association of tags from a Timestream query resource.

        :param resource_arn: The Timestream resource that the tags will be removed from.
        :param tag_keys: A list of tags keys.
        :returns: UntagResourceResponse
        :raises ValidationException:
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("UpdateScheduledQuery")
    def update_scheduled_query(
        self,
        context: RequestContext,
        scheduled_query_arn: AmazonResourceName,
        state: ScheduledQueryState,
    ) -> None:
        """Update a scheduled query.

        :param scheduled_query_arn: ARN of the scheuled query.
        :param state: State of the scheduled query.
        :raises AccessDeniedException:
        :raises InternalServerException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError
