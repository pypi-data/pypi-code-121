import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AmazonResourceName = str
Boolean = bool
BoxedBoolean = bool
CatalogNameString = str
CommentString = str
DatabaseString = str
DescriptionString = str
ErrorCategory = int
ErrorCode = str
ErrorMessage = str
ErrorType = int
ExpressionString = str
IdempotencyToken = str
Integer = int
KeyString = str
MaxDataCatalogsCount = int
MaxDatabasesCount = int
MaxEngineVersionsCount = int
MaxNamedQueriesCount = int
MaxPreparedStatementsCount = int
MaxQueryExecutionsCount = int
MaxQueryResults = int
MaxTableMetadataCount = int
MaxTagsCount = int
MaxWorkGroupsCount = int
NameString = str
NamedQueryDescriptionString = str
NamedQueryId = str
ParametersMapValue = str
QueryExecutionId = str
QueryString = str
StatementName = str
String = str
TableTypeString = str
TagKey = str
TagValue = str
Token = str
TypeString = str
WorkGroupDescriptionString = str
WorkGroupName = str
datumString = str


class ColumnNullable(str):
    NOT_NULL = "NOT_NULL"
    NULLABLE = "NULLABLE"
    UNKNOWN = "UNKNOWN"


class DataCatalogType(str):
    LAMBDA = "LAMBDA"
    GLUE = "GLUE"
    HIVE = "HIVE"


class EncryptionOption(str):
    SSE_S3 = "SSE_S3"
    SSE_KMS = "SSE_KMS"
    CSE_KMS = "CSE_KMS"


class QueryExecutionState(str):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class S3AclOption(str):
    BUCKET_OWNER_FULL_CONTROL = "BUCKET_OWNER_FULL_CONTROL"


class StatementType(str):
    DDL = "DDL"
    DML = "DML"
    UTILITY = "UTILITY"


class ThrottleReason(str):
    CONCURRENT_QUERY_LIMIT_EXCEEDED = "CONCURRENT_QUERY_LIMIT_EXCEEDED"


class WorkGroupState(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class InternalServerException(ServiceException):
    """Indicates a platform issue, which may be due to a transient condition or
    outage.
    """

    Message: Optional[ErrorMessage]


class InvalidRequestException(ServiceException):
    """Indicates that something is wrong with the input to the request. For
    example, a required parameter may be missing or out of range.
    """

    AthenaErrorCode: Optional[ErrorCode]
    Message: Optional[ErrorMessage]


class MetadataException(ServiceException):
    """An exception that Athena received when it called a custom metastore.
    Occurs if the error is not caused by user input
    (``InvalidRequestException``) or from the Athena platform
    (``InternalServerException``). For example, if a user-created Lambda
    function is missing permissions, the Lambda ``4XX`` exception is
    returned in a ``MetadataException``.
    """

    Message: Optional[ErrorMessage]


class ResourceNotFoundException(ServiceException):
    """A resource, such as a workgroup, was not found."""

    Message: Optional[ErrorMessage]
    ResourceName: Optional[AmazonResourceName]


class TooManyRequestsException(ServiceException):
    """Indicates that the request was throttled."""

    Message: Optional[ErrorMessage]
    Reason: Optional[ThrottleReason]


class AclConfiguration(TypedDict, total=False):
    """Indicates that an Amazon S3 canned ACL should be set to control
    ownership of stored query results. When Athena stores query results in
    Amazon S3, the canned ACL is set with the ``x-amz-acl`` request header.
    For more information about S3 Object Ownership, see `Object Ownership
    settings <https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html#object-ownership-overview>`__
    in the *Amazon S3 User Guide*.
    """

    S3AclOption: S3AclOption


class AthenaError(TypedDict, total=False):
    """Provides information about an Athena query error. The ``AthenaError``
    feature provides standardized error information to help you understand
    failed queries and take steps after a query failure occurs.
    ``AthenaError`` includes an ``ErrorCategory`` field that specifies
    whether the cause of the failed query is due to system error, user
    error, or other error.
    """

    ErrorCategory: Optional[ErrorCategory]
    ErrorType: Optional[ErrorType]
    Retryable: Optional[Boolean]
    ErrorMessage: Optional[String]


NamedQueryIdList = List[NamedQueryId]


class BatchGetNamedQueryInput(ServiceRequest):
    NamedQueryIds: NamedQueryIdList


class UnprocessedNamedQueryId(TypedDict, total=False):
    """Information about a named query ID that could not be processed."""

    NamedQueryId: Optional[NamedQueryId]
    ErrorCode: Optional[ErrorCode]
    ErrorMessage: Optional[ErrorMessage]


UnprocessedNamedQueryIdList = List[UnprocessedNamedQueryId]


class NamedQuery(TypedDict, total=False):
    """A query, where ``QueryString`` contains the SQL statements that make up
    the query.
    """

    Name: NameString
    Description: Optional[DescriptionString]
    Database: DatabaseString
    QueryString: QueryString
    NamedQueryId: Optional[NamedQueryId]
    WorkGroup: Optional[WorkGroupName]


NamedQueryList = List[NamedQuery]


class BatchGetNamedQueryOutput(TypedDict, total=False):
    NamedQueries: Optional[NamedQueryList]
    UnprocessedNamedQueryIds: Optional[UnprocessedNamedQueryIdList]


QueryExecutionIdList = List[QueryExecutionId]


class BatchGetQueryExecutionInput(ServiceRequest):
    QueryExecutionIds: QueryExecutionIdList


class UnprocessedQueryExecutionId(TypedDict, total=False):
    """Describes a query execution that failed to process."""

    QueryExecutionId: Optional[QueryExecutionId]
    ErrorCode: Optional[ErrorCode]
    ErrorMessage: Optional[ErrorMessage]


UnprocessedQueryExecutionIdList = List[UnprocessedQueryExecutionId]


class EngineVersion(TypedDict, total=False):
    """The Athena engine version for running queries."""

    SelectedEngineVersion: Optional[NameString]
    EffectiveEngineVersion: Optional[NameString]


Long = int


class QueryExecutionStatistics(TypedDict, total=False):
    """The amount of data scanned during the query execution and the amount of
    time that it took to execute, and the type of statement that was run.
    """

    EngineExecutionTimeInMillis: Optional[Long]
    DataScannedInBytes: Optional[Long]
    DataManifestLocation: Optional[String]
    TotalExecutionTimeInMillis: Optional[Long]
    QueryQueueTimeInMillis: Optional[Long]
    QueryPlanningTimeInMillis: Optional[Long]
    ServiceProcessingTimeInMillis: Optional[Long]


Date = datetime


class QueryExecutionStatus(TypedDict, total=False):
    """The completion date, current state, submission time, and state change
    reason (if applicable) for the query execution.
    """

    State: Optional[QueryExecutionState]
    StateChangeReason: Optional[String]
    SubmissionDateTime: Optional[Date]
    CompletionDateTime: Optional[Date]
    AthenaError: Optional[AthenaError]


class QueryExecutionContext(TypedDict, total=False):
    """The database and data catalog context in which the query execution
    occurs.
    """

    Database: Optional[DatabaseString]
    Catalog: Optional[CatalogNameString]


class EncryptionConfiguration(TypedDict, total=False):
    """If query results are encrypted in Amazon S3, indicates the encryption
    option used (for example, ``SSE_KMS`` or ``CSE_KMS``) and key
    information.
    """

    EncryptionOption: EncryptionOption
    KmsKey: Optional[String]


class ResultConfiguration(TypedDict, total=False):
    """The location in Amazon S3 where query results are stored and the
    encryption option, if any, used for query results. These are known as
    "client-side settings". If workgroup settings override client-side
    settings, then the query uses the workgroup settings.
    """

    OutputLocation: Optional[String]
    EncryptionConfiguration: Optional[EncryptionConfiguration]
    ExpectedBucketOwner: Optional[String]
    AclConfiguration: Optional[AclConfiguration]


class QueryExecution(TypedDict, total=False):
    """Information about a single instance of a query execution."""

    QueryExecutionId: Optional[QueryExecutionId]
    Query: Optional[QueryString]
    StatementType: Optional[StatementType]
    ResultConfiguration: Optional[ResultConfiguration]
    QueryExecutionContext: Optional[QueryExecutionContext]
    Status: Optional[QueryExecutionStatus]
    Statistics: Optional[QueryExecutionStatistics]
    WorkGroup: Optional[WorkGroupName]
    EngineVersion: Optional[EngineVersion]


QueryExecutionList = List[QueryExecution]


class BatchGetQueryExecutionOutput(TypedDict, total=False):
    QueryExecutions: Optional[QueryExecutionList]
    UnprocessedQueryExecutionIds: Optional[UnprocessedQueryExecutionIdList]


BytesScannedCutoffValue = int


class Column(TypedDict, total=False):
    """Contains metadata for a column in a table."""

    Name: NameString
    Type: Optional[TypeString]
    Comment: Optional[CommentString]


class ColumnInfo(TypedDict, total=False):
    """Information about the columns in a query execution result."""

    CatalogName: Optional[String]
    SchemaName: Optional[String]
    TableName: Optional[String]
    Name: String
    Label: Optional[String]
    Type: String
    Precision: Optional[Integer]
    Scale: Optional[Integer]
    Nullable: Optional[ColumnNullable]
    CaseSensitive: Optional[Boolean]


ColumnInfoList = List[ColumnInfo]
ColumnList = List[Column]


class Tag(TypedDict, total=False):
    """A label that you assign to a resource. In Athena, a resource can be a
    workgroup or data catalog. Each tag consists of a key and an optional
    value, both of which you define. For example, you can use tags to
    categorize Athena workgroups or data catalogs by purpose, owner, or
    environment. Use a consistent set of tag keys to make it easier to
    search and filter workgroups or data catalogs in your account. For best
    practices, see `Tagging Best
    Practices <https://aws.amazon.com/answers/account-management/aws-tagging-strategies/>`__.
    Tag keys can be from 1 to 128 UTF-8 Unicode characters, and tag values
    can be from 0 to 256 UTF-8 Unicode characters. Tags can use letters and
    numbers representable in UTF-8, and the following characters: + - = . _
    : / @. Tag keys and values are case-sensitive. Tag keys must be unique
    per resource. If you specify more than one tag, separate them by commas.
    """

    Key: Optional[TagKey]
    Value: Optional[TagValue]


TagList = List[Tag]
ParametersMap = Dict[KeyString, ParametersMapValue]


class CreateDataCatalogInput(ServiceRequest):
    Name: CatalogNameString
    Type: DataCatalogType
    Description: Optional[DescriptionString]
    Parameters: Optional[ParametersMap]
    Tags: Optional[TagList]


class CreateDataCatalogOutput(TypedDict, total=False):
    pass


class CreateNamedQueryInput(ServiceRequest):
    Name: NameString
    Description: Optional[DescriptionString]
    Database: DatabaseString
    QueryString: QueryString
    ClientRequestToken: Optional[IdempotencyToken]
    WorkGroup: Optional[WorkGroupName]


class CreateNamedQueryOutput(TypedDict, total=False):
    NamedQueryId: Optional[NamedQueryId]


class CreatePreparedStatementInput(ServiceRequest):
    StatementName: StatementName
    WorkGroup: WorkGroupName
    QueryStatement: QueryString
    Description: Optional[DescriptionString]


class CreatePreparedStatementOutput(TypedDict, total=False):
    pass


class WorkGroupConfiguration(TypedDict, total=False):
    """The configuration of the workgroup, which includes the location in
    Amazon S3 where query results are stored, the encryption option, if any,
    used for query results, whether the Amazon CloudWatch Metrics are
    enabled for the workgroup and whether workgroup settings override query
    settings, and the data usage limits for the amount of data scanned per
    query or per workgroup. The workgroup settings override is specified in
    ``EnforceWorkGroupConfiguration`` (true/false) in the
    ``WorkGroupConfiguration``. See
    WorkGroupConfiguration$EnforceWorkGroupConfiguration.
    """

    ResultConfiguration: Optional[ResultConfiguration]
    EnforceWorkGroupConfiguration: Optional[BoxedBoolean]
    PublishCloudWatchMetricsEnabled: Optional[BoxedBoolean]
    BytesScannedCutoffPerQuery: Optional[BytesScannedCutoffValue]
    RequesterPaysEnabled: Optional[BoxedBoolean]
    EngineVersion: Optional[EngineVersion]


class CreateWorkGroupInput(ServiceRequest):
    Name: WorkGroupName
    Configuration: Optional[WorkGroupConfiguration]
    Description: Optional[WorkGroupDescriptionString]
    Tags: Optional[TagList]


class CreateWorkGroupOutput(TypedDict, total=False):
    pass


class DataCatalog(TypedDict, total=False):
    """Contains information about a data catalog in an Amazon Web Services
    account.
    """

    Name: CatalogNameString
    Description: Optional[DescriptionString]
    Type: DataCatalogType
    Parameters: Optional[ParametersMap]


class DataCatalogSummary(TypedDict, total=False):
    """The summary information for the data catalog, which includes its name
    and type.
    """

    CatalogName: Optional[CatalogNameString]
    Type: Optional[DataCatalogType]


DataCatalogSummaryList = List[DataCatalogSummary]


class Database(TypedDict, total=False):
    """Contains metadata information for a database in a data catalog."""

    Name: NameString
    Description: Optional[DescriptionString]
    Parameters: Optional[ParametersMap]


DatabaseList = List[Database]


class Datum(TypedDict, total=False):
    """A piece of data (a field in the table)."""

    VarCharValue: Optional[datumString]


class DeleteDataCatalogInput(ServiceRequest):
    Name: CatalogNameString


class DeleteDataCatalogOutput(TypedDict, total=False):
    pass


class DeleteNamedQueryInput(ServiceRequest):
    NamedQueryId: NamedQueryId


class DeleteNamedQueryOutput(TypedDict, total=False):
    pass


class DeletePreparedStatementInput(ServiceRequest):
    StatementName: StatementName
    WorkGroup: WorkGroupName


class DeletePreparedStatementOutput(TypedDict, total=False):
    pass


class DeleteWorkGroupInput(ServiceRequest):
    WorkGroup: WorkGroupName
    RecursiveDeleteOption: Optional[BoxedBoolean]


class DeleteWorkGroupOutput(TypedDict, total=False):
    pass


EngineVersionsList = List[EngineVersion]


class GetDataCatalogInput(ServiceRequest):
    Name: CatalogNameString


class GetDataCatalogOutput(TypedDict, total=False):
    DataCatalog: Optional[DataCatalog]


class GetDatabaseInput(ServiceRequest):
    CatalogName: CatalogNameString
    DatabaseName: NameString


class GetDatabaseOutput(TypedDict, total=False):
    Database: Optional[Database]


class GetNamedQueryInput(ServiceRequest):
    NamedQueryId: NamedQueryId


class GetNamedQueryOutput(TypedDict, total=False):
    NamedQuery: Optional[NamedQuery]


class GetPreparedStatementInput(ServiceRequest):
    StatementName: StatementName
    WorkGroup: WorkGroupName


class PreparedStatement(TypedDict, total=False):
    """A prepared SQL statement for use with Athena."""

    StatementName: Optional[StatementName]
    QueryStatement: Optional[QueryString]
    WorkGroupName: Optional[WorkGroupName]
    Description: Optional[DescriptionString]
    LastModifiedTime: Optional[Date]


class GetPreparedStatementOutput(TypedDict, total=False):
    PreparedStatement: Optional[PreparedStatement]


class GetQueryExecutionInput(ServiceRequest):
    QueryExecutionId: QueryExecutionId


class GetQueryExecutionOutput(TypedDict, total=False):
    QueryExecution: Optional[QueryExecution]


class GetQueryResultsInput(ServiceRequest):
    QueryExecutionId: QueryExecutionId
    NextToken: Optional[Token]
    MaxResults: Optional[MaxQueryResults]


class ResultSetMetadata(TypedDict, total=False):
    """The metadata that describes the column structure and data types of a
    table of query results. To return a ``ResultSetMetadata`` object, use
    GetQueryResults.
    """

    ColumnInfo: Optional[ColumnInfoList]


datumList = List[Datum]


class Row(TypedDict, total=False):
    """The rows that make up a query result table."""

    Data: Optional[datumList]


RowList = List[Row]


class ResultSet(TypedDict, total=False):
    """The metadata and rows that make up a query result set. The metadata
    describes the column structure and data types. To return a ``ResultSet``
    object, use GetQueryResults.
    """

    Rows: Optional[RowList]
    ResultSetMetadata: Optional[ResultSetMetadata]


class GetQueryResultsOutput(TypedDict, total=False):
    UpdateCount: Optional[Long]
    ResultSet: Optional[ResultSet]
    NextToken: Optional[Token]


class GetTableMetadataInput(ServiceRequest):
    CatalogName: CatalogNameString
    DatabaseName: NameString
    TableName: NameString


Timestamp = datetime


class TableMetadata(TypedDict, total=False):
    """Contains metadata for a table."""

    Name: NameString
    CreateTime: Optional[Timestamp]
    LastAccessTime: Optional[Timestamp]
    TableType: Optional[TableTypeString]
    Columns: Optional[ColumnList]
    PartitionKeys: Optional[ColumnList]
    Parameters: Optional[ParametersMap]


class GetTableMetadataOutput(TypedDict, total=False):
    TableMetadata: Optional[TableMetadata]


class GetWorkGroupInput(ServiceRequest):
    WorkGroup: WorkGroupName


class WorkGroup(TypedDict, total=False):
    """A workgroup, which contains a name, description, creation time, state,
    and other configuration, listed under WorkGroup$Configuration. Each
    workgroup enables you to isolate queries for you or your group of users
    from other queries in the same account, to configure the query results
    location and the encryption configuration (known as workgroup settings),
    to enable sending query metrics to Amazon CloudWatch, and to establish
    per-query data usage control limits for all queries in a workgroup. The
    workgroup settings override is specified in
    ``EnforceWorkGroupConfiguration`` (true/false) in the
    ``WorkGroupConfiguration``. See
    WorkGroupConfiguration$EnforceWorkGroupConfiguration.
    """

    Name: WorkGroupName
    State: Optional[WorkGroupState]
    Configuration: Optional[WorkGroupConfiguration]
    Description: Optional[WorkGroupDescriptionString]
    CreationTime: Optional[Date]


class GetWorkGroupOutput(TypedDict, total=False):
    WorkGroup: Optional[WorkGroup]


class ListDataCatalogsInput(ServiceRequest):
    NextToken: Optional[Token]
    MaxResults: Optional[MaxDataCatalogsCount]


class ListDataCatalogsOutput(TypedDict, total=False):
    DataCatalogsSummary: Optional[DataCatalogSummaryList]
    NextToken: Optional[Token]


class ListDatabasesInput(ServiceRequest):
    CatalogName: CatalogNameString
    NextToken: Optional[Token]
    MaxResults: Optional[MaxDatabasesCount]


class ListDatabasesOutput(TypedDict, total=False):
    DatabaseList: Optional[DatabaseList]
    NextToken: Optional[Token]


class ListEngineVersionsInput(ServiceRequest):
    NextToken: Optional[Token]
    MaxResults: Optional[MaxEngineVersionsCount]


class ListEngineVersionsOutput(TypedDict, total=False):
    EngineVersions: Optional[EngineVersionsList]
    NextToken: Optional[Token]


class ListNamedQueriesInput(ServiceRequest):
    NextToken: Optional[Token]
    MaxResults: Optional[MaxNamedQueriesCount]
    WorkGroup: Optional[WorkGroupName]


class ListNamedQueriesOutput(TypedDict, total=False):
    NamedQueryIds: Optional[NamedQueryIdList]
    NextToken: Optional[Token]


class ListPreparedStatementsInput(ServiceRequest):
    WorkGroup: WorkGroupName
    NextToken: Optional[Token]
    MaxResults: Optional[MaxPreparedStatementsCount]


class PreparedStatementSummary(TypedDict, total=False):
    """The name and last modified time of the prepared statement."""

    StatementName: Optional[StatementName]
    LastModifiedTime: Optional[Date]


PreparedStatementsList = List[PreparedStatementSummary]


class ListPreparedStatementsOutput(TypedDict, total=False):
    PreparedStatements: Optional[PreparedStatementsList]
    NextToken: Optional[Token]


class ListQueryExecutionsInput(ServiceRequest):
    NextToken: Optional[Token]
    MaxResults: Optional[MaxQueryExecutionsCount]
    WorkGroup: Optional[WorkGroupName]


class ListQueryExecutionsOutput(TypedDict, total=False):
    QueryExecutionIds: Optional[QueryExecutionIdList]
    NextToken: Optional[Token]


class ListTableMetadataInput(ServiceRequest):
    CatalogName: CatalogNameString
    DatabaseName: NameString
    Expression: Optional[ExpressionString]
    NextToken: Optional[Token]
    MaxResults: Optional[MaxTableMetadataCount]


TableMetadataList = List[TableMetadata]


class ListTableMetadataOutput(TypedDict, total=False):
    TableMetadataList: Optional[TableMetadataList]
    NextToken: Optional[Token]


class ListTagsForResourceInput(ServiceRequest):
    ResourceARN: AmazonResourceName
    NextToken: Optional[Token]
    MaxResults: Optional[MaxTagsCount]


class ListTagsForResourceOutput(TypedDict, total=False):
    Tags: Optional[TagList]
    NextToken: Optional[Token]


class ListWorkGroupsInput(ServiceRequest):
    NextToken: Optional[Token]
    MaxResults: Optional[MaxWorkGroupsCount]


class WorkGroupSummary(TypedDict, total=False):
    """The summary information for the workgroup, which includes its name,
    state, description, and the date and time it was created.
    """

    Name: Optional[WorkGroupName]
    State: Optional[WorkGroupState]
    Description: Optional[WorkGroupDescriptionString]
    CreationTime: Optional[Date]
    EngineVersion: Optional[EngineVersion]


WorkGroupsList = List[WorkGroupSummary]


class ListWorkGroupsOutput(TypedDict, total=False):
    WorkGroups: Optional[WorkGroupsList]
    NextToken: Optional[Token]


class ResultConfigurationUpdates(TypedDict, total=False):
    """The information about the updates in the query results, such as output
    location and encryption configuration for the query results.
    """

    OutputLocation: Optional[String]
    RemoveOutputLocation: Optional[BoxedBoolean]
    EncryptionConfiguration: Optional[EncryptionConfiguration]
    RemoveEncryptionConfiguration: Optional[BoxedBoolean]
    ExpectedBucketOwner: Optional[String]
    RemoveExpectedBucketOwner: Optional[BoxedBoolean]
    AclConfiguration: Optional[AclConfiguration]
    RemoveAclConfiguration: Optional[BoxedBoolean]


class StartQueryExecutionInput(ServiceRequest):
    QueryString: QueryString
    ClientRequestToken: Optional[IdempotencyToken]
    QueryExecutionContext: Optional[QueryExecutionContext]
    ResultConfiguration: Optional[ResultConfiguration]
    WorkGroup: Optional[WorkGroupName]


class StartQueryExecutionOutput(TypedDict, total=False):
    QueryExecutionId: Optional[QueryExecutionId]


class StopQueryExecutionInput(ServiceRequest):
    QueryExecutionId: QueryExecutionId


class StopQueryExecutionOutput(TypedDict, total=False):
    pass


TagKeyList = List[TagKey]


class TagResourceInput(ServiceRequest):
    ResourceARN: AmazonResourceName
    Tags: TagList


class TagResourceOutput(TypedDict, total=False):
    pass


class UntagResourceInput(ServiceRequest):
    ResourceARN: AmazonResourceName
    TagKeys: TagKeyList


class UntagResourceOutput(TypedDict, total=False):
    pass


class UpdateDataCatalogInput(ServiceRequest):
    Name: CatalogNameString
    Type: DataCatalogType
    Description: Optional[DescriptionString]
    Parameters: Optional[ParametersMap]


class UpdateDataCatalogOutput(TypedDict, total=False):
    pass


class UpdateNamedQueryInput(ServiceRequest):
    NamedQueryId: NamedQueryId
    Name: NameString
    Description: Optional[NamedQueryDescriptionString]
    QueryString: QueryString


class UpdateNamedQueryOutput(TypedDict, total=False):
    pass


class UpdatePreparedStatementInput(ServiceRequest):
    StatementName: StatementName
    WorkGroup: WorkGroupName
    QueryStatement: QueryString
    Description: Optional[DescriptionString]


class UpdatePreparedStatementOutput(TypedDict, total=False):
    pass


class WorkGroupConfigurationUpdates(TypedDict, total=False):
    """The configuration information that will be updated for this workgroup,
    which includes the location in Amazon S3 where query results are stored,
    the encryption option, if any, used for query results, whether the
    Amazon CloudWatch Metrics are enabled for the workgroup, whether the
    workgroup settings override the client-side settings, and the data usage
    limit for the amount of bytes scanned per query, if it is specified.
    """

    EnforceWorkGroupConfiguration: Optional[BoxedBoolean]
    ResultConfigurationUpdates: Optional[ResultConfigurationUpdates]
    PublishCloudWatchMetricsEnabled: Optional[BoxedBoolean]
    BytesScannedCutoffPerQuery: Optional[BytesScannedCutoffValue]
    RemoveBytesScannedCutoffPerQuery: Optional[BoxedBoolean]
    RequesterPaysEnabled: Optional[BoxedBoolean]
    EngineVersion: Optional[EngineVersion]


class UpdateWorkGroupInput(ServiceRequest):
    WorkGroup: WorkGroupName
    Description: Optional[WorkGroupDescriptionString]
    ConfigurationUpdates: Optional[WorkGroupConfigurationUpdates]
    State: Optional[WorkGroupState]


class UpdateWorkGroupOutput(TypedDict, total=False):
    pass


class AthenaApi:

    service = "athena"
    version = "2017-05-18"

    @handler("BatchGetNamedQuery")
    def batch_get_named_query(
        self, context: RequestContext, named_query_ids: NamedQueryIdList
    ) -> BatchGetNamedQueryOutput:
        """Returns the details of a single named query or a list of up to 50
        queries, which you provide as an array of query ID strings. Requires you
        to have access to the workgroup in which the queries were saved. Use
        ListNamedQueriesInput to get the list of named query IDs in the
        specified workgroup. If information could not be retrieved for a
        submitted query ID, information about the query ID submitted is listed
        under UnprocessedNamedQueryId. Named queries differ from executed
        queries. Use BatchGetQueryExecutionInput to get details about each
        unique query execution, and ListQueryExecutionsInput to get a list of
        query execution IDs.

        :param named_query_ids: An array of query IDs.
        :returns: BatchGetNamedQueryOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("BatchGetQueryExecution")
    def batch_get_query_execution(
        self, context: RequestContext, query_execution_ids: QueryExecutionIdList
    ) -> BatchGetQueryExecutionOutput:
        """Returns the details of a single query execution or a list of up to 50
        query executions, which you provide as an array of query execution ID
        strings. Requires you to have access to the workgroup in which the
        queries ran. To get a list of query execution IDs, use
        ListQueryExecutionsInput$WorkGroup. Query executions differ from named
        (saved) queries. Use BatchGetNamedQueryInput to get details about named
        queries.

        :param query_execution_ids: An array of query execution IDs.
        :returns: BatchGetQueryExecutionOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("CreateDataCatalog", expand=False)
    def create_data_catalog(
        self, context: RequestContext, request: CreateDataCatalogInput
    ) -> CreateDataCatalogOutput:
        """Creates (registers) a data catalog with the specified name and
        properties. Catalogs created are visible to all users of the same Amazon
        Web Services account.

        :param name: The name of the data catalog to create.
        :param type: The type of data catalog to create: ``LAMBDA`` for a federated catalog,
        ``HIVE`` for an external hive metastore, or ``GLUE`` for an Glue Data
        Catalog.
        :param description: A description of the data catalog to be created.
        :param parameters: Specifies the Lambda function or functions to use for creating the data
        catalog.
        :param tags: A list of comma separated tags to add to the data catalog that is
        created.
        :returns: CreateDataCatalogOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("CreateNamedQuery")
    def create_named_query(
        self,
        context: RequestContext,
        name: NameString,
        database: DatabaseString,
        query_string: QueryString,
        description: DescriptionString = None,
        client_request_token: IdempotencyToken = None,
        work_group: WorkGroupName = None,
    ) -> CreateNamedQueryOutput:
        """Creates a named query in the specified workgroup. Requires that you have
        access to the workgroup.

        For code samples using the Amazon Web Services SDK for Java, see
        `Examples and Code
        Samples <http://docs.aws.amazon.com/athena/latest/ug/code-samples.html>`__
        in the *Amazon Athena User Guide*.

        :param name: The query name.
        :param database: The database to which the query belongs.
        :param query_string: The contents of the query with all query statements.
        :param description: The query description.
        :param client_request_token: A unique case-sensitive string used to ensure the request to create the
        query is idempotent (executes only once).
        :param work_group: The name of the workgroup in which the named query is being created.
        :returns: CreateNamedQueryOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("CreatePreparedStatement")
    def create_prepared_statement(
        self,
        context: RequestContext,
        statement_name: StatementName,
        work_group: WorkGroupName,
        query_statement: QueryString,
        description: DescriptionString = None,
    ) -> CreatePreparedStatementOutput:
        """Creates a prepared statement for use with SQL queries in Athena.

        :param statement_name: The name of the prepared statement.
        :param work_group: The name of the workgroup to which the prepared statement belongs.
        :param query_statement: The query string for the prepared statement.
        :param description: The description of the prepared statement.
        :returns: CreatePreparedStatementOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("CreateWorkGroup")
    def create_work_group(
        self,
        context: RequestContext,
        name: WorkGroupName,
        configuration: WorkGroupConfiguration = None,
        description: WorkGroupDescriptionString = None,
        tags: TagList = None,
    ) -> CreateWorkGroupOutput:
        """Creates a workgroup with the specified name.

        :param name: The workgroup name.
        :param configuration: The configuration for the workgroup, which includes the location in
        Amazon S3 where query results are stored, the encryption configuration,
        if any, used for encrypting query results, whether the Amazon CloudWatch
        Metrics are enabled for the workgroup, the limit for the amount of bytes
        scanned (cutoff) per query, if it is specified, and whether workgroup's
        settings (specified with ``EnforceWorkGroupConfiguration``) in the
        ``WorkGroupConfiguration`` override client-side settings.
        :param description: The workgroup description.
        :param tags: A list of comma separated tags to add to the workgroup that is created.
        :returns: CreateWorkGroupOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DeleteDataCatalog")
    def delete_data_catalog(
        self, context: RequestContext, name: CatalogNameString
    ) -> DeleteDataCatalogOutput:
        """Deletes a data catalog.

        :param name: The name of the data catalog to delete.
        :returns: DeleteDataCatalogOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DeleteNamedQuery")
    def delete_named_query(
        self, context: RequestContext, named_query_id: NamedQueryId
    ) -> DeleteNamedQueryOutput:
        """Deletes the named query if you have access to the workgroup in which the
        query was saved.

        For code samples using the Amazon Web Services SDK for Java, see
        `Examples and Code
        Samples <http://docs.aws.amazon.com/athena/latest/ug/code-samples.html>`__
        in the *Amazon Athena User Guide*.

        :param named_query_id: The unique ID of the query to delete.
        :returns: DeleteNamedQueryOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DeletePreparedStatement")
    def delete_prepared_statement(
        self, context: RequestContext, statement_name: StatementName, work_group: WorkGroupName
    ) -> DeletePreparedStatementOutput:
        """Deletes the prepared statement with the specified name from the
        specified workgroup.

        :param statement_name: The name of the prepared statement to delete.
        :param work_group: The workgroup to which the statement to be deleted belongs.
        :returns: DeletePreparedStatementOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteWorkGroup")
    def delete_work_group(
        self,
        context: RequestContext,
        work_group: WorkGroupName,
        recursive_delete_option: BoxedBoolean = None,
    ) -> DeleteWorkGroupOutput:
        """Deletes the workgroup with the specified name. The primary workgroup
        cannot be deleted.

        :param work_group: The unique name of the workgroup to delete.
        :param recursive_delete_option: The option to delete the workgroup and its contents even if the
        workgroup contains any named queries or query executions.
        :returns: DeleteWorkGroupOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("GetDataCatalog")
    def get_data_catalog(
        self, context: RequestContext, name: CatalogNameString
    ) -> GetDataCatalogOutput:
        """Returns the specified data catalog.

        :param name: The name of the data catalog to return.
        :returns: GetDataCatalogOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("GetDatabase")
    def get_database(
        self, context: RequestContext, catalog_name: CatalogNameString, database_name: NameString
    ) -> GetDatabaseOutput:
        """Returns a database object for the specified database and data catalog.

        :param catalog_name: The name of the data catalog that contains the database to return.
        :param database_name: The name of the database to return.
        :returns: GetDatabaseOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises MetadataException:
        """
        raise NotImplementedError

    @handler("GetNamedQuery")
    def get_named_query(
        self, context: RequestContext, named_query_id: NamedQueryId
    ) -> GetNamedQueryOutput:
        """Returns information about a single query. Requires that you have access
        to the workgroup in which the query was saved.

        :param named_query_id: The unique ID of the query.
        :returns: GetNamedQueryOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("GetPreparedStatement")
    def get_prepared_statement(
        self, context: RequestContext, statement_name: StatementName, work_group: WorkGroupName
    ) -> GetPreparedStatementOutput:
        """Retrieves the prepared statement with the specified name from the
        specified workgroup.

        :param statement_name: The name of the prepared statement to retrieve.
        :param work_group: The workgroup to which the statement to be retrieved belongs.
        :returns: GetPreparedStatementOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("GetQueryExecution")
    def get_query_execution(
        self, context: RequestContext, query_execution_id: QueryExecutionId
    ) -> GetQueryExecutionOutput:
        """Returns information about a single execution of a query if you have
        access to the workgroup in which the query ran. Each time a query
        executes, information about the query execution is saved with a unique
        ID.

        :param query_execution_id: The unique ID of the query execution.
        :returns: GetQueryExecutionOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("GetQueryResults")
    def get_query_results(
        self,
        context: RequestContext,
        query_execution_id: QueryExecutionId,
        next_token: Token = None,
        max_results: MaxQueryResults = None,
    ) -> GetQueryResultsOutput:
        """Streams the results of a single query execution specified by
        ``QueryExecutionId`` from the Athena query results location in Amazon
        S3. For more information, see `Query
        Results <https://docs.aws.amazon.com/athena/latest/ug/querying.html>`__
        in the *Amazon Athena User Guide*. This request does not execute the
        query but returns results. Use StartQueryExecution to run a query.

        To stream query results successfully, the IAM principal with permission
        to call ``GetQueryResults`` also must have permissions to the Amazon S3
        ``GetObject`` action for the Athena query results location.

        IAM principals with permission to the Amazon S3 ``GetObject`` action for
        the query results location are able to retrieve query results from
        Amazon S3 even if permission to the ``GetQueryResults`` action is
        denied. To restrict user or role access, ensure that Amazon S3
        permissions to the Athena query location are denied.

        :param query_execution_id: The unique ID of the query execution.
        :param next_token: A token generated by the Athena service that specifies where to continue
        pagination if a previous request was truncated.
        :param max_results: The maximum number of results (rows) to return in this request.
        :returns: GetQueryResultsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("GetTableMetadata")
    def get_table_metadata(
        self,
        context: RequestContext,
        catalog_name: CatalogNameString,
        database_name: NameString,
        table_name: NameString,
    ) -> GetTableMetadataOutput:
        """Returns table metadata for the specified catalog, database, and table.

        :param catalog_name: The name of the data catalog that contains the database and table
        metadata to return.
        :param database_name: The name of the database that contains the table metadata to return.
        :param table_name: The name of the table for which metadata is returned.
        :returns: GetTableMetadataOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises MetadataException:
        """
        raise NotImplementedError

    @handler("GetWorkGroup")
    def get_work_group(
        self, context: RequestContext, work_group: WorkGroupName
    ) -> GetWorkGroupOutput:
        """Returns information about the workgroup with the specified name.

        :param work_group: The name of the workgroup.
        :returns: GetWorkGroupOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListDataCatalogs")
    def list_data_catalogs(
        self,
        context: RequestContext,
        next_token: Token = None,
        max_results: MaxDataCatalogsCount = None,
    ) -> ListDataCatalogsOutput:
        """Lists the data catalogs in the current Amazon Web Services account.

        :param next_token: A token generated by the Athena service that specifies where to continue
        pagination if a previous request was truncated.
        :param max_results: Specifies the maximum number of data catalogs to return.
        :returns: ListDataCatalogsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListDatabases")
    def list_databases(
        self,
        context: RequestContext,
        catalog_name: CatalogNameString,
        next_token: Token = None,
        max_results: MaxDatabasesCount = None,
    ) -> ListDatabasesOutput:
        """Lists the databases in the specified data catalog.

        :param catalog_name: The name of the data catalog that contains the databases to return.
        :param next_token: A token generated by the Athena service that specifies where to continue
        pagination if a previous request was truncated.
        :param max_results: Specifies the maximum number of results to return.
        :returns: ListDatabasesOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises MetadataException:
        """
        raise NotImplementedError

    @handler("ListEngineVersions")
    def list_engine_versions(
        self,
        context: RequestContext,
        next_token: Token = None,
        max_results: MaxEngineVersionsCount = None,
    ) -> ListEngineVersionsOutput:
        """Returns a list of engine versions that are available to choose from,
        including the Auto option.

        :param next_token: A token generated by the Athena service that specifies where to continue
        pagination if a previous request was truncated.
        :param max_results: The maximum number of engine versions to return in this request.
        :returns: ListEngineVersionsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListNamedQueries")
    def list_named_queries(
        self,
        context: RequestContext,
        next_token: Token = None,
        max_results: MaxNamedQueriesCount = None,
        work_group: WorkGroupName = None,
    ) -> ListNamedQueriesOutput:
        """Provides a list of available query IDs only for queries saved in the
        specified workgroup. Requires that you have access to the specified
        workgroup. If a workgroup is not specified, lists the saved queries for
        the primary workgroup.

        For code samples using the Amazon Web Services SDK for Java, see
        `Examples and Code
        Samples <http://docs.aws.amazon.com/athena/latest/ug/code-samples.html>`__
        in the *Amazon Athena User Guide*.

        :param next_token: A token generated by the Athena service that specifies where to continue
        pagination if a previous request was truncated.
        :param max_results: The maximum number of queries to return in this request.
        :param work_group: The name of the workgroup from which the named queries are being
        returned.
        :returns: ListNamedQueriesOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListPreparedStatements")
    def list_prepared_statements(
        self,
        context: RequestContext,
        work_group: WorkGroupName,
        next_token: Token = None,
        max_results: MaxPreparedStatementsCount = None,
    ) -> ListPreparedStatementsOutput:
        """Lists the prepared statements in the specfied workgroup.

        :param work_group: The workgroup to list the prepared statements for.
        :param next_token: A token generated by the Athena service that specifies where to continue
        pagination if a previous request was truncated.
        :param max_results: The maximum number of results to return in this request.
        :returns: ListPreparedStatementsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListQueryExecutions")
    def list_query_executions(
        self,
        context: RequestContext,
        next_token: Token = None,
        max_results: MaxQueryExecutionsCount = None,
        work_group: WorkGroupName = None,
    ) -> ListQueryExecutionsOutput:
        """Provides a list of available query execution IDs for the queries in the
        specified workgroup. If a workgroup is not specified, returns a list of
        query execution IDs for the primary workgroup. Requires you to have
        access to the workgroup in which the queries ran.

        For code samples using the Amazon Web Services SDK for Java, see
        `Examples and Code
        Samples <http://docs.aws.amazon.com/athena/latest/ug/code-samples.html>`__
        in the *Amazon Athena User Guide*.

        :param next_token: A token generated by the Athena service that specifies where to continue
        pagination if a previous request was truncated.
        :param max_results: The maximum number of query executions to return in this request.
        :param work_group: The name of the workgroup from which queries are being returned.
        :returns: ListQueryExecutionsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListTableMetadata")
    def list_table_metadata(
        self,
        context: RequestContext,
        catalog_name: CatalogNameString,
        database_name: NameString,
        expression: ExpressionString = None,
        next_token: Token = None,
        max_results: MaxTableMetadataCount = None,
    ) -> ListTableMetadataOutput:
        """Lists the metadata for the tables in the specified data catalog
        database.

        :param catalog_name: The name of the data catalog for which table metadata should be
        returned.
        :param database_name: The name of the database for which table metadata should be returned.
        :param expression: A regex filter that pattern-matches table names.
        :param next_token: A token generated by the Athena service that specifies where to continue
        pagination if a previous request was truncated.
        :param max_results: Specifies the maximum number of results to return.
        :returns: ListTableMetadataOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises MetadataException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self,
        context: RequestContext,
        resource_arn: AmazonResourceName,
        next_token: Token = None,
        max_results: MaxTagsCount = None,
    ) -> ListTagsForResourceOutput:
        """Lists the tags associated with an Athena workgroup or data catalog
        resource.

        :param resource_arn: Lists the tags for the resource with the specified ARN.
        :param next_token: The token for the next set of results, or null if there are no
        additional results for this request, where the request lists the tags
        for the resource with the specified ARN.
        :param max_results: The maximum number of results to be returned per request that lists the
        tags for the resource.
        :returns: ListTagsForResourceOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListWorkGroups")
    def list_work_groups(
        self,
        context: RequestContext,
        next_token: Token = None,
        max_results: MaxWorkGroupsCount = None,
    ) -> ListWorkGroupsOutput:
        """Lists available workgroups for the account.

        :param next_token: A token generated by the Athena service that specifies where to continue
        pagination if a previous request was truncated.
        :param max_results: The maximum number of workgroups to return in this request.
        :returns: ListWorkGroupsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("StartQueryExecution")
    def start_query_execution(
        self,
        context: RequestContext,
        query_string: QueryString,
        client_request_token: IdempotencyToken = None,
        query_execution_context: QueryExecutionContext = None,
        result_configuration: ResultConfiguration = None,
        work_group: WorkGroupName = None,
    ) -> StartQueryExecutionOutput:
        """Runs the SQL query statements contained in the ``Query``. Requires you
        to have access to the workgroup in which the query ran. Running queries
        against an external catalog requires GetDataCatalog permission to the
        catalog. For code samples using the Amazon Web Services SDK for Java,
        see `Examples and Code
        Samples <http://docs.aws.amazon.com/athena/latest/ug/code-samples.html>`__
        in the *Amazon Athena User Guide*.

        :param query_string: The SQL query statements to be executed.
        :param client_request_token: A unique case-sensitive string used to ensure the request to create the
        query is idempotent (executes only once).
        :param query_execution_context: The database within which the query executes.
        :param result_configuration: Specifies information about where and how to save the results of the
        query execution.
        :param work_group: The name of the workgroup in which the query is being started.
        :returns: StartQueryExecutionOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises TooManyRequestsException:
        """
        raise NotImplementedError

    @handler("StopQueryExecution")
    def stop_query_execution(
        self, context: RequestContext, query_execution_id: QueryExecutionId
    ) -> StopQueryExecutionOutput:
        """Stops a query execution. Requires you to have access to the workgroup in
        which the query ran.

        For code samples using the Amazon Web Services SDK for Java, see
        `Examples and Code
        Samples <http://docs.aws.amazon.com/athena/latest/ug/code-samples.html>`__
        in the *Amazon Athena User Guide*.

        :param query_execution_id: The unique ID of the query execution to stop.
        :returns: StopQueryExecutionOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tags: TagList
    ) -> TagResourceOutput:
        """Adds one or more tags to an Athena resource. A tag is a label that you
        assign to a resource. In Athena, a resource can be a workgroup or data
        catalog. Each tag consists of a key and an optional value, both of which
        you define. For example, you can use tags to categorize Athena
        workgroups or data catalogs by purpose, owner, or environment. Use a
        consistent set of tag keys to make it easier to search and filter
        workgroups or data catalogs in your account. For best practices, see
        `Tagging Best
        Practices <https://aws.amazon.com/answers/account-management/aws-tagging-strategies/>`__.
        Tag keys can be from 1 to 128 UTF-8 Unicode characters, and tag values
        can be from 0 to 256 UTF-8 Unicode characters. Tags can use letters and
        numbers representable in UTF-8, and the following characters: + - = . _
        : / @. Tag keys and values are case-sensitive. Tag keys must be unique
        per resource. If you specify more than one tag, separate them by commas.

        :param resource_arn: Specifies the ARN of the Athena resource (workgroup or data catalog) to
        which tags are to be added.
        :param tags: A collection of one or more tags, separated by commas, to be added to an
        Athena workgroup or data catalog resource.
        :returns: TagResourceOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tag_keys: TagKeyList
    ) -> UntagResourceOutput:
        """Removes one or more tags from a data catalog or workgroup resource.

        :param resource_arn: Specifies the ARN of the resource from which tags are to be removed.
        :param tag_keys: A comma-separated list of one or more tag keys whose tags are to be
        removed from the specified resource.
        :returns: UntagResourceOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateDataCatalog", expand=False)
    def update_data_catalog(
        self, context: RequestContext, request: UpdateDataCatalogInput
    ) -> UpdateDataCatalogOutput:
        """Updates the data catalog that has the specified name.

        :param name: The name of the data catalog to update.
        :param type: Specifies the type of data catalog to update.
        :param description: New or modified text that describes the data catalog.
        :param parameters: Specifies the Lambda function or functions to use for updating the data
        catalog.
        :returns: UpdateDataCatalogOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("UpdateNamedQuery")
    def update_named_query(
        self,
        context: RequestContext,
        named_query_id: NamedQueryId,
        name: NameString,
        query_string: QueryString,
        description: NamedQueryDescriptionString = None,
    ) -> UpdateNamedQueryOutput:
        """Updates a NamedQuery object. The database or workgroup cannot be
        updated.

        :param named_query_id: The unique identifier (UUID) of the query.
        :param name: The name of the query.
        :param query_string: The contents of the query with all query statements.
        :param description: The query description.
        :returns: UpdateNamedQueryOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("UpdatePreparedStatement")
    def update_prepared_statement(
        self,
        context: RequestContext,
        statement_name: StatementName,
        work_group: WorkGroupName,
        query_statement: QueryString,
        description: DescriptionString = None,
    ) -> UpdatePreparedStatementOutput:
        """Updates a prepared statement.

        :param statement_name: The name of the prepared statement.
        :param work_group: The workgroup for the prepared statement.
        :param query_statement: The query string for the prepared statement.
        :param description: The description of the prepared statement.
        :returns: UpdatePreparedStatementOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateWorkGroup")
    def update_work_group(
        self,
        context: RequestContext,
        work_group: WorkGroupName,
        description: WorkGroupDescriptionString = None,
        configuration_updates: WorkGroupConfigurationUpdates = None,
        state: WorkGroupState = None,
    ) -> UpdateWorkGroupOutput:
        """Updates the workgroup with the specified name. The workgroup's name
        cannot be changed.

        :param work_group: The specified workgroup that will be updated.
        :param description: The workgroup description.
        :param configuration_updates: The workgroup configuration that will be updated for the given
        workgroup.
        :param state: The workgroup state that will be updated for the given workgroup.
        :returns: UpdateWorkGroupOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError
