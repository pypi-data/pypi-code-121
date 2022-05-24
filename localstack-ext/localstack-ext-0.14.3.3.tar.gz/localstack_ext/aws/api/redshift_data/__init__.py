import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Boolean = bool
BoxedBoolean = bool
BoxedDouble = float
Integer = int
ListStatementsLimit = int
Location = str
PageSize = int
ParameterName = str
ParameterValue = str
SecretArn = str
StatementId = str
StatementNameString = str
StatementString = str
String = str
bool = bool


class StatementStatusString(str):
    SUBMITTED = "SUBMITTED"
    PICKED = "PICKED"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"


class StatusString(str):
    SUBMITTED = "SUBMITTED"
    PICKED = "PICKED"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"
    ALL = "ALL"


class ActiveStatementsExceededException(ServiceException):
    """The number of active statements exceeds the limit."""

    Message: Optional[String]


class BatchExecuteStatementException(ServiceException):
    """An SQL statement encountered an environmental error while running."""

    Message: String
    StatementId: String


class DatabaseConnectionException(ServiceException):
    """Connection to a database failed."""

    Message: String


class ExecuteStatementException(ServiceException):
    """The SQL statement encountered an environmental error while running."""

    Message: String
    StatementId: String


class InternalServerException(ServiceException):
    """The Amazon Redshift Data API operation failed due to invalid input."""

    Message: String


class ResourceNotFoundException(ServiceException):
    """The Amazon Redshift Data API operation failed due to a missing resource."""

    Message: String
    ResourceId: String


class ValidationException(ServiceException):
    """The Amazon Redshift Data API operation failed due to invalid input."""

    Message: Optional[String]


SqlList = List[StatementString]


class BatchExecuteStatementInput(ServiceRequest):
    ClusterIdentifier: Optional[Location]
    Database: String
    DbUser: Optional[String]
    SecretArn: Optional[SecretArn]
    Sqls: SqlList
    StatementName: Optional[StatementNameString]
    WithEvent: Optional[Boolean]


Timestamp = datetime


class BatchExecuteStatementOutput(TypedDict, total=False):
    ClusterIdentifier: Optional[Location]
    CreatedAt: Optional[Timestamp]
    Database: Optional[String]
    DbUser: Optional[String]
    Id: Optional[StatementId]
    SecretArn: Optional[SecretArn]


Blob = bytes
BoxedLong = int


class CancelStatementRequest(ServiceRequest):
    Id: StatementId


class CancelStatementResponse(TypedDict, total=False):
    Status: Optional[Boolean]


class ColumnMetadata(TypedDict, total=False):
    """The properties (metadata) of a column."""

    columnDefault: Optional[String]
    isCaseSensitive: Optional[bool]
    isCurrency: Optional[bool]
    isSigned: Optional[bool]
    label: Optional[String]
    length: Optional[Integer]
    name: Optional[String]
    nullable: Optional[Integer]
    precision: Optional[Integer]
    scale: Optional[Integer]
    schemaName: Optional[String]
    tableName: Optional[String]
    typeName: Optional[String]


ColumnList = List[ColumnMetadata]
ColumnMetadataList = List[ColumnMetadata]
DatabaseList = List[String]


class DescribeStatementRequest(ServiceRequest):
    Id: StatementId


Long = int


class SubStatementData(TypedDict, total=False):
    """Information about an SQL statement."""

    CreatedAt: Optional[Timestamp]
    Duration: Optional[Long]
    Error: Optional[String]
    HasResultSet: Optional[Boolean]
    Id: StatementId
    QueryString: Optional[StatementString]
    RedshiftQueryId: Optional[Long]
    ResultRows: Optional[Long]
    ResultSize: Optional[Long]
    Status: Optional[StatementStatusString]
    UpdatedAt: Optional[Timestamp]


SubStatementList = List[SubStatementData]


class SqlParameter(TypedDict, total=False):
    """A parameter used in a SQL statement."""

    name: ParameterName
    value: ParameterValue


SqlParametersList = List[SqlParameter]


class DescribeStatementResponse(TypedDict, total=False):
    ClusterIdentifier: Optional[String]
    CreatedAt: Optional[Timestamp]
    Database: Optional[String]
    DbUser: Optional[String]
    Duration: Optional[Long]
    Error: Optional[String]
    HasResultSet: Optional[Boolean]
    Id: StatementId
    QueryParameters: Optional[SqlParametersList]
    QueryString: Optional[StatementString]
    RedshiftPid: Optional[Long]
    RedshiftQueryId: Optional[Long]
    ResultRows: Optional[Long]
    ResultSize: Optional[Long]
    SecretArn: Optional[SecretArn]
    Status: Optional[StatusString]
    SubStatements: Optional[SubStatementList]
    UpdatedAt: Optional[Timestamp]


class DescribeTableRequest(ServiceRequest):
    ClusterIdentifier: Optional[Location]
    ConnectedDatabase: Optional[String]
    Database: String
    DbUser: Optional[String]
    MaxResults: Optional[PageSize]
    NextToken: Optional[String]
    Schema: Optional[String]
    SecretArn: Optional[SecretArn]
    Table: Optional[String]


class DescribeTableResponse(TypedDict, total=False):
    ColumnList: Optional[ColumnList]
    NextToken: Optional[String]
    TableName: Optional[String]


class ExecuteStatementInput(ServiceRequest):
    ClusterIdentifier: Optional[Location]
    Database: String
    DbUser: Optional[String]
    Parameters: Optional[SqlParametersList]
    SecretArn: Optional[SecretArn]
    Sql: StatementString
    StatementName: Optional[StatementNameString]
    WithEvent: Optional[Boolean]


class ExecuteStatementOutput(TypedDict, total=False):
    ClusterIdentifier: Optional[Location]
    CreatedAt: Optional[Timestamp]
    Database: Optional[String]
    DbUser: Optional[String]
    Id: Optional[StatementId]
    SecretArn: Optional[SecretArn]


class Field(TypedDict, total=False):
    """A data value in a column."""

    blobValue: Optional[Blob]
    booleanValue: Optional[BoxedBoolean]
    doubleValue: Optional[BoxedDouble]
    isNull: Optional[BoxedBoolean]
    longValue: Optional[BoxedLong]
    stringValue: Optional[String]


FieldList = List[Field]


class GetStatementResultRequest(ServiceRequest):
    Id: StatementId
    NextToken: Optional[String]


SqlRecords = List[FieldList]


class GetStatementResultResponse(TypedDict, total=False):
    ColumnMetadata: Optional[ColumnMetadataList]
    NextToken: Optional[String]
    Records: SqlRecords
    TotalNumRows: Optional[Long]


class ListDatabasesRequest(ServiceRequest):
    ClusterIdentifier: Optional[Location]
    Database: String
    DbUser: Optional[String]
    MaxResults: Optional[PageSize]
    NextToken: Optional[String]
    SecretArn: Optional[SecretArn]


class ListDatabasesResponse(TypedDict, total=False):
    Databases: Optional[DatabaseList]
    NextToken: Optional[String]


class ListSchemasRequest(ServiceRequest):
    ClusterIdentifier: Optional[Location]
    ConnectedDatabase: Optional[String]
    Database: String
    DbUser: Optional[String]
    MaxResults: Optional[PageSize]
    NextToken: Optional[String]
    SchemaPattern: Optional[String]
    SecretArn: Optional[SecretArn]


SchemaList = List[String]


class ListSchemasResponse(TypedDict, total=False):
    NextToken: Optional[String]
    Schemas: Optional[SchemaList]


class ListStatementsRequest(ServiceRequest):
    MaxResults: Optional[ListStatementsLimit]
    NextToken: Optional[String]
    RoleLevel: Optional[Boolean]
    StatementName: Optional[StatementNameString]
    Status: Optional[StatusString]


StatementStringList = List[StatementString]


class StatementData(TypedDict, total=False):
    """The SQL statement to run."""

    CreatedAt: Optional[Timestamp]
    Id: StatementId
    IsBatchStatement: Optional[Boolean]
    QueryParameters: Optional[SqlParametersList]
    QueryString: Optional[StatementString]
    QueryStrings: Optional[StatementStringList]
    SecretArn: Optional[SecretArn]
    StatementName: Optional[StatementNameString]
    Status: Optional[StatusString]
    UpdatedAt: Optional[Timestamp]


StatementList = List[StatementData]


class ListStatementsResponse(TypedDict, total=False):
    NextToken: Optional[String]
    Statements: StatementList


class ListTablesRequest(ServiceRequest):
    ClusterIdentifier: Optional[Location]
    ConnectedDatabase: Optional[String]
    Database: String
    DbUser: Optional[String]
    MaxResults: Optional[PageSize]
    NextToken: Optional[String]
    SchemaPattern: Optional[String]
    SecretArn: Optional[SecretArn]
    TablePattern: Optional[String]


TableMember = TypedDict(
    "TableMember",
    {
        "name": Optional[String],
        "schema": Optional[String],
        "type": Optional[String],
    },
    total=False,
)
TableList = List[TableMember]


class ListTablesResponse(TypedDict, total=False):
    NextToken: Optional[String]
    Tables: Optional[TableList]


class RedshiftDataApi:

    service = "redshift-data"
    version = "2019-12-20"

    @handler("BatchExecuteStatement")
    def batch_execute_statement(
        self,
        context: RequestContext,
        database: String,
        sqls: SqlList,
        cluster_identifier: Location = None,
        db_user: String = None,
        secret_arn: SecretArn = None,
        statement_name: StatementNameString = None,
        with_event: Boolean = None,
    ) -> BatchExecuteStatementOutput:
        """Runs one or more SQL statements, which can be data manipulation language
        (DML) or data definition language (DDL). Depending on the authorization
        method, use one of the following combinations of request parameters:

        -  Secrets Manager - when connecting to a cluster, specify the Amazon
           Resource Name (ARN) of the secret, the database name, and the cluster
           identifier that matches the cluster in the secret. When connecting to
           a serverless endpoint, specify the Amazon Resource Name (ARN) of the
           secret and the database name.

        -  Temporary credentials - when connecting to a cluster, specify the
           cluster identifier, the database name, and the database user name.
           Also, permission to call the ``redshift:GetClusterCredentials``
           operation is required. When connecting to a serverless endpoint,
           specify the database name.

        :param database: The name of the database.
        :param sqls: One or more SQL statements to run.
        :param cluster_identifier: The cluster identifier.
        :param db_user: The database user name.
        :param secret_arn: The name or ARN of the secret that enables access to the database.
        :param statement_name: The name of the SQL statements.
        :param with_event: A value that indicates whether to send an event to the Amazon
        EventBridge event bus after the SQL statements run.
        :returns: BatchExecuteStatementOutput
        :raises ValidationException:
        :raises ActiveStatementsExceededException:
        :raises BatchExecuteStatementException:
        """
        raise NotImplementedError

    @handler("CancelStatement")
    def cancel_statement(self, context: RequestContext, id: StatementId) -> CancelStatementResponse:
        """Cancels a running query. To be canceled, a query must be running.

        :param id: The identifier of the SQL statement to cancel.
        :returns: CancelStatementResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        :raises DatabaseConnectionException:
        """
        raise NotImplementedError

    @handler("DescribeStatement")
    def describe_statement(
        self, context: RequestContext, id: StatementId
    ) -> DescribeStatementResponse:
        """Describes the details about a specific instance when a query was run by
        the Amazon Redshift Data API. The information includes when the query
        started, when it finished, the query status, the number of rows
        returned, and the SQL statement.

        :param id: The identifier of the SQL statement to describe.
        :returns: DescribeStatementResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("DescribeTable")
    def describe_table(
        self,
        context: RequestContext,
        database: String,
        cluster_identifier: Location = None,
        connected_database: String = None,
        db_user: String = None,
        max_results: PageSize = None,
        next_token: String = None,
        schema: String = None,
        secret_arn: SecretArn = None,
        table: String = None,
    ) -> DescribeTableResponse:
        """Describes the detailed information about a table from metadata in the
        cluster. The information includes its columns. A token is returned to
        page through the column list. Depending on the authorization method, use
        one of the following combinations of request parameters:

        -  Secrets Manager - when connecting to a cluster, specify the Amazon
           Resource Name (ARN) of the secret, the database name, and the cluster
           identifier that matches the cluster in the secret. When connecting to
           a serverless endpoint, specify the Amazon Resource Name (ARN) of the
           secret and the database name.

        -  Temporary credentials - when connecting to a cluster, specify the
           cluster identifier, the database name, and the database user name.
           Also, permission to call the ``redshift:GetClusterCredentials``
           operation is required. When connecting to a serverless endpoint,
           specify the database name.

        :param database: The name of the database that contains the tables to be described.
        :param cluster_identifier: The cluster identifier.
        :param connected_database: A database name.
        :param db_user: The database user name.
        :param max_results: The maximum number of tables to return in the response.
        :param next_token: A value that indicates the starting point for the next set of response
        records in a subsequent request.
        :param schema: The schema that contains the table.
        :param secret_arn: The name or ARN of the secret that enables access to the database.
        :param table: The table name.
        :returns: DescribeTableResponse
        :raises ValidationException:
        :raises InternalServerException:
        :raises DatabaseConnectionException:
        """
        raise NotImplementedError

    @handler("ExecuteStatement")
    def execute_statement(
        self,
        context: RequestContext,
        database: String,
        sql: StatementString,
        cluster_identifier: Location = None,
        db_user: String = None,
        parameters: SqlParametersList = None,
        secret_arn: SecretArn = None,
        statement_name: StatementNameString = None,
        with_event: Boolean = None,
    ) -> ExecuteStatementOutput:
        """Runs an SQL statement, which can be data manipulation language (DML) or
        data definition language (DDL). This statement must be a single SQL
        statement. Depending on the authorization method, use one of the
        following combinations of request parameters:

        -  Secrets Manager - when connecting to a cluster, specify the Amazon
           Resource Name (ARN) of the secret, the database name, and the cluster
           identifier that matches the cluster in the secret. When connecting to
           a serverless endpoint, specify the Amazon Resource Name (ARN) of the
           secret and the database name.

        -  Temporary credentials - when connecting to a cluster, specify the
           cluster identifier, the database name, and the database user name.
           Also, permission to call the ``redshift:GetClusterCredentials``
           operation is required. When connecting to a serverless endpoint,
           specify the database name.

        :param database: The name of the database.
        :param sql: The SQL statement text to run.
        :param cluster_identifier: The cluster identifier.
        :param db_user: The database user name.
        :param parameters: The parameters for the SQL statement.
        :param secret_arn: The name or ARN of the secret that enables access to the database.
        :param statement_name: The name of the SQL statement.
        :param with_event: A value that indicates whether to send an event to the Amazon
        EventBridge event bus after the SQL statement runs.
        :returns: ExecuteStatementOutput
        :raises ValidationException:
        :raises ExecuteStatementException:
        :raises ActiveStatementsExceededException:
        """
        raise NotImplementedError

    @handler("GetStatementResult")
    def get_statement_result(
        self, context: RequestContext, id: StatementId, next_token: String = None
    ) -> GetStatementResultResponse:
        """Fetches the temporarily cached result of an SQL statement. A token is
        returned to page through the statement results.

        :param id: The identifier of the SQL statement whose results are to be fetched.
        :param next_token: A value that indicates the starting point for the next set of response
        records in a subsequent request.
        :returns: GetStatementResultResponse
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("ListDatabases")
    def list_databases(
        self,
        context: RequestContext,
        database: String,
        cluster_identifier: Location = None,
        db_user: String = None,
        max_results: PageSize = None,
        next_token: String = None,
        secret_arn: SecretArn = None,
    ) -> ListDatabasesResponse:
        """List the databases in a cluster. A token is returned to page through the
        database list. Depending on the authorization method, use one of the
        following combinations of request parameters:

        -  Secrets Manager - when connecting to a cluster, specify the Amazon
           Resource Name (ARN) of the secret, the database name, and the cluster
           identifier that matches the cluster in the secret. When connecting to
           a serverless endpoint, specify the Amazon Resource Name (ARN) of the
           secret and the database name.

        -  Temporary credentials - when connecting to a cluster, specify the
           cluster identifier, the database name, and the database user name.
           Also, permission to call the ``redshift:GetClusterCredentials``
           operation is required. When connecting to a serverless endpoint,
           specify the database name.

        :param database: The name of the database.
        :param cluster_identifier: The cluster identifier.
        :param db_user: The database user name.
        :param max_results: The maximum number of databases to return in the response.
        :param next_token: A value that indicates the starting point for the next set of response
        records in a subsequent request.
        :param secret_arn: The name or ARN of the secret that enables access to the database.
        :returns: ListDatabasesResponse
        :raises ValidationException:
        :raises InternalServerException:
        :raises DatabaseConnectionException:
        """
        raise NotImplementedError

    @handler("ListSchemas")
    def list_schemas(
        self,
        context: RequestContext,
        database: String,
        cluster_identifier: Location = None,
        connected_database: String = None,
        db_user: String = None,
        max_results: PageSize = None,
        next_token: String = None,
        schema_pattern: String = None,
        secret_arn: SecretArn = None,
    ) -> ListSchemasResponse:
        """Lists the schemas in a database. A token is returned to page through the
        schema list. Depending on the authorization method, use one of the
        following combinations of request parameters:

        -  Secrets Manager - when connecting to a cluster, specify the Amazon
           Resource Name (ARN) of the secret, the database name, and the cluster
           identifier that matches the cluster in the secret. When connecting to
           a serverless endpoint, specify the Amazon Resource Name (ARN) of the
           secret and the database name.

        -  Temporary credentials - when connecting to a cluster, specify the
           cluster identifier, the database name, and the database user name.
           Also, permission to call the ``redshift:GetClusterCredentials``
           operation is required. When connecting to a serverless endpoint,
           specify the database name.

        :param database: The name of the database that contains the schemas to list.
        :param cluster_identifier: The cluster identifier.
        :param connected_database: A database name.
        :param db_user: The database user name.
        :param max_results: The maximum number of schemas to return in the response.
        :param next_token: A value that indicates the starting point for the next set of response
        records in a subsequent request.
        :param schema_pattern: A pattern to filter results by schema name.
        :param secret_arn: The name or ARN of the secret that enables access to the database.
        :returns: ListSchemasResponse
        :raises ValidationException:
        :raises InternalServerException:
        :raises DatabaseConnectionException:
        """
        raise NotImplementedError

    @handler("ListStatements")
    def list_statements(
        self,
        context: RequestContext,
        max_results: ListStatementsLimit = None,
        next_token: String = None,
        role_level: Boolean = None,
        statement_name: StatementNameString = None,
        status: StatusString = None,
    ) -> ListStatementsResponse:
        """List of SQL statements. By default, only finished statements are shown.
        A token is returned to page through the statement list.

        :param max_results: The maximum number of SQL statements to return in the response.
        :param next_token: A value that indicates the starting point for the next set of response
        records in a subsequent request.
        :param role_level: A value that filters which statements to return in the response.
        :param statement_name: The name of the SQL statement specified as input to
        ``BatchExecuteStatement`` or ``ExecuteStatement`` to identify the query.
        :param status: The status of the SQL statement to list.
        :returns: ListStatementsResponse
        :raises ValidationException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("ListTables")
    def list_tables(
        self,
        context: RequestContext,
        database: String,
        cluster_identifier: Location = None,
        connected_database: String = None,
        db_user: String = None,
        max_results: PageSize = None,
        next_token: String = None,
        schema_pattern: String = None,
        secret_arn: SecretArn = None,
        table_pattern: String = None,
    ) -> ListTablesResponse:
        """List the tables in a database. If neither ``SchemaPattern`` nor
        ``TablePattern`` are specified, then all tables in the database are
        returned. A token is returned to page through the table list. Depending
        on the authorization method, use one of the following combinations of
        request parameters:

        -  Secrets Manager - when connecting to a cluster, specify the Amazon
           Resource Name (ARN) of the secret, the database name, and the cluster
           identifier that matches the cluster in the secret. When connecting to
           a serverless endpoint, specify the Amazon Resource Name (ARN) of the
           secret and the database name.

        -  Temporary credentials - when connecting to a cluster, specify the
           cluster identifier, the database name, and the database user name.
           Also, permission to call the ``redshift:GetClusterCredentials``
           operation is required. When connecting to a serverless endpoint,
           specify the database name.

        :param database: The name of the database that contains the tables to list.
        :param cluster_identifier: The cluster identifier.
        :param connected_database: A database name.
        :param db_user: The database user name.
        :param max_results: The maximum number of tables to return in the response.
        :param next_token: A value that indicates the starting point for the next set of response
        records in a subsequent request.
        :param schema_pattern: A pattern to filter results by schema name.
        :param secret_arn: The name or ARN of the secret that enables access to the database.
        :param table_pattern: A pattern to filter results by table name.
        :returns: ListTablesResponse
        :raises ValidationException:
        :raises InternalServerException:
        :raises DatabaseConnectionException:
        """
        raise NotImplementedError
