import sys
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Arn = str
Boolean = bool
BoxedBoolean = bool
BoxedDouble = float
BoxedFloat = float
BoxedInteger = int
DbName = str
ErrorMessage = str
FormattedSqlRecords = str
Id = str
Integer = int
ParameterName = str
SqlStatement = str
String = str
TransactionStatus = str


class DecimalReturnType(str):
    STRING = "STRING"
    DOUBLE_OR_LONG = "DOUBLE_OR_LONG"


class LongReturnType(str):
    STRING = "STRING"
    LONG = "LONG"


class RecordsFormatType(str):
    NONE = "NONE"
    JSON = "JSON"


class TypeHint(str):
    JSON = "JSON"
    UUID = "UUID"
    TIMESTAMP = "TIMESTAMP"
    DATE = "DATE"
    TIME = "TIME"
    DECIMAL = "DECIMAL"


class AccessDeniedException(ServiceException):
    """You do not have sufficient access to perform this action."""

    message: Optional[ErrorMessage]


class BadRequestException(ServiceException):
    """There is an error in the call or in a SQL statement."""

    message: Optional[ErrorMessage]


class ForbiddenException(ServiceException):
    """There are insufficient privileges to make the call."""

    message: Optional[ErrorMessage]


class InternalServerErrorException(ServiceException):
    """An internal error occurred."""


class NotFoundException(ServiceException):
    """The ``resourceArn``, ``secretArn``, or ``transactionId`` value can't be
    found.
    """

    message: Optional[ErrorMessage]


class ServiceUnavailableError(ServiceException):
    """The service specified by the ``resourceArn`` parameter is not available."""


Long = int


class StatementTimeoutException(ServiceException):
    """The execution of the SQL statement timed out."""

    dbConnectionId: Optional[Long]
    message: Optional[ErrorMessage]


StringArray = List[String]
BoxedLong = int
LongArray = List[BoxedLong]
DoubleArray = List[BoxedDouble]
BooleanArray = List[BoxedBoolean]
ArrayOfArray = List["ArrayValue"]


class ArrayValue(TypedDict, total=False):
    """Contains an array."""

    arrayValues: Optional[ArrayOfArray]
    booleanValues: Optional[BooleanArray]
    doubleValues: Optional[DoubleArray]
    longValues: Optional[LongArray]
    stringValues: Optional[StringArray]


ArrayValueList = List["Value"]


class StructValue(TypedDict, total=False):
    """A structure value returned by a call.

    This data structure is only used with the deprecated ``ExecuteSql``
    operation. Use the ``BatchExecuteStatement`` or ``ExecuteStatement``
    operation instead.
    """

    attributes: Optional[ArrayValueList]


Blob = bytes


class Value(TypedDict, total=False):
    """Contains the value of a column.

    ::

        <important> <p>This data structure is only used with the deprecated <code>ExecuteSql</code> operation. Use the <code>BatchExecuteStatement</code> or <code>ExecuteStatement</code> operation instead.</p> </important>
    """

    arrayValues: Optional[ArrayValueList]
    bigIntValue: Optional[BoxedLong]
    bitValue: Optional[BoxedBoolean]
    blobValue: Optional[Blob]
    doubleValue: Optional[BoxedDouble]
    intValue: Optional[BoxedInteger]
    isNull: Optional[BoxedBoolean]
    realValue: Optional[BoxedFloat]
    stringValue: Optional[String]
    structValue: Optional[StructValue]


class Field(TypedDict, total=False):
    """Contains a value."""

    arrayValue: Optional[ArrayValue]
    blobValue: Optional[Blob]
    booleanValue: Optional[BoxedBoolean]
    doubleValue: Optional[BoxedDouble]
    isNull: Optional[BoxedBoolean]
    longValue: Optional[BoxedLong]
    stringValue: Optional[String]


class SqlParameter(TypedDict, total=False):
    """A parameter used in a SQL statement."""

    name: Optional[ParameterName]
    typeHint: Optional[TypeHint]
    value: Optional[Field]


SqlParametersList = List[SqlParameter]
SqlParameterSets = List[SqlParametersList]


class BatchExecuteStatementRequest(ServiceRequest):
    """The request parameters represent the input of a SQL statement over an
    array of data.
    """

    database: Optional[DbName]
    parameterSets: Optional[SqlParameterSets]
    resourceArn: Arn
    schema: Optional[DbName]
    secretArn: Arn
    sql: SqlStatement
    transactionId: Optional[Id]


FieldList = List[Field]


class UpdateResult(TypedDict, total=False):
    """The response elements represent the results of an update."""

    generatedFields: Optional[FieldList]


UpdateResults = List[UpdateResult]


class BatchExecuteStatementResponse(TypedDict, total=False):
    """The response elements represent the output of a SQL statement over an
    array of data.
    """

    updateResults: Optional[UpdateResults]


class BeginTransactionRequest(ServiceRequest):
    """The request parameters represent the input of a request to start a SQL
    transaction.
    """

    database: Optional[DbName]
    resourceArn: Arn
    schema: Optional[DbName]
    secretArn: Arn


class BeginTransactionResponse(TypedDict, total=False):
    """The response elements represent the output of a request to start a SQL
    transaction.
    """

    transactionId: Optional[Id]


ColumnMetadata = TypedDict(
    "ColumnMetadata",
    {
        "arrayBaseColumnType": Optional[Integer],
        "isAutoIncrement": Optional[Boolean],
        "isCaseSensitive": Optional[Boolean],
        "isCurrency": Optional[Boolean],
        "isSigned": Optional[Boolean],
        "label": Optional[String],
        "name": Optional[String],
        "nullable": Optional[Integer],
        "precision": Optional[Integer],
        "scale": Optional[Integer],
        "schemaName": Optional[String],
        "tableName": Optional[String],
        "type": Optional[Integer],
        "typeName": Optional[String],
    },
    total=False,
)


class CommitTransactionRequest(ServiceRequest):
    """The request parameters represent the input of a commit transaction
    request.
    """

    resourceArn: Arn
    secretArn: Arn
    transactionId: Id


class CommitTransactionResponse(TypedDict, total=False):
    """The response elements represent the output of a commit transaction
    request.
    """

    transactionStatus: Optional[TransactionStatus]


class ExecuteSqlRequest(ServiceRequest):
    """The request parameters represent the input of a request to run one or
    more SQL statements.
    """

    awsSecretStoreArn: Arn
    database: Optional[DbName]
    dbClusterOrInstanceArn: Arn
    schema: Optional[DbName]
    sqlStatements: SqlStatement


Metadata = List[ColumnMetadata]


class ResultSetMetadata(TypedDict, total=False):
    """The metadata of the result set returned by a SQL statement."""

    columnCount: Optional[Long]
    columnMetadata: Optional[Metadata]


Row = List[Value]


class Record(TypedDict, total=False):
    """A record returned by a call.

    This data structure is only used with the deprecated ``ExecuteSql``
    operation. Use the ``BatchExecuteStatement`` or ``ExecuteStatement``
    operation instead.
    """

    values: Optional[Row]


Records = List[Record]


class ResultFrame(TypedDict, total=False):
    """The result set returned by a SQL statement.

    This data structure is only used with the deprecated ``ExecuteSql``
    operation. Use the ``BatchExecuteStatement`` or ``ExecuteStatement``
    operation instead.
    """

    records: Optional[Records]
    resultSetMetadata: Optional[ResultSetMetadata]


RecordsUpdated = int


class SqlStatementResult(TypedDict, total=False):
    """The result of a SQL statement.

    ::

        <important> <p>This data structure is only used with the deprecated <code>ExecuteSql</code> operation. Use the <code>BatchExecuteStatement</code> or <code>ExecuteStatement</code> operation instead.</p> </important>
    """

    numberOfRecordsUpdated: Optional[RecordsUpdated]
    resultFrame: Optional[ResultFrame]


SqlStatementResults = List[SqlStatementResult]


class ExecuteSqlResponse(TypedDict, total=False):
    """The response elements represent the output of a request to run one or
    more SQL statements.
    """

    sqlStatementResults: Optional[SqlStatementResults]


class ResultSetOptions(TypedDict, total=False):
    """Options that control how the result set is returned."""

    decimalReturnType: Optional[DecimalReturnType]
    longReturnType: Optional[LongReturnType]


class ExecuteStatementRequest(ServiceRequest):
    """The request parameters represent the input of a request to run a SQL
    statement against a database.
    """

    continueAfterTimeout: Optional[Boolean]
    database: Optional[DbName]
    formatRecordsAs: Optional[RecordsFormatType]
    includeResultMetadata: Optional[Boolean]
    parameters: Optional[SqlParametersList]
    resourceArn: Arn
    resultSetOptions: Optional[ResultSetOptions]
    schema: Optional[DbName]
    secretArn: Arn
    sql: SqlStatement
    transactionId: Optional[Id]


SqlRecords = List[FieldList]


class ExecuteStatementResponse(TypedDict, total=False):
    """The response elements represent the output of a request to run a SQL
    statement against a database.
    """

    columnMetadata: Optional[Metadata]
    formattedRecords: Optional[FormattedSqlRecords]
    generatedFields: Optional[FieldList]
    numberOfRecordsUpdated: Optional[RecordsUpdated]
    records: Optional[SqlRecords]


class RollbackTransactionRequest(ServiceRequest):
    """The request parameters represent the input of a request to perform a
    rollback of a transaction.
    """

    resourceArn: Arn
    secretArn: Arn
    transactionId: Id


class RollbackTransactionResponse(TypedDict, total=False):
    """The response elements represent the output of a request to perform a
    rollback of a transaction.
    """

    transactionStatus: Optional[TransactionStatus]


class RdsDataApi:

    service = "rds-data"
    version = "2018-08-01"

    @handler("BatchExecuteStatement")
    def batch_execute_statement(
        self,
        context: RequestContext,
        resource_arn: Arn,
        secret_arn: Arn,
        sql: SqlStatement,
        database: DbName = None,
        parameter_sets: SqlParameterSets = None,
        schema: DbName = None,
        transaction_id: Id = None,
    ) -> BatchExecuteStatementResponse:
        """Runs a batch SQL statement over an array of data.

        You can run bulk update and insert operations for multiple records using
        a DML statement with different parameter sets. Bulk operations can
        provide a significant performance improvement over individual insert and
        update operations.

        If a call isn't part of a transaction because it doesn't include the
        ``transactionID`` parameter, changes that result from the call are
        committed automatically.

        :param resource_arn: The Amazon Resource Name (ARN) of the Aurora Serverless DB cluster.
        :param secret_arn: The name or ARN of the secret that enables access to the DB cluster.
        :param sql: The SQL statement to run.
        :param database: The name of the database.
        :param parameter_sets: The parameter set for the batch operation.
        :param schema: The name of the database schema.
        :param transaction_id: The identifier of a transaction that was started by using the
        ``BeginTransaction`` operation.
        :returns: BatchExecuteStatementResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises StatementTimeoutException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        :raises ServiceUnavailableError:
        """
        raise NotImplementedError

    @handler("BeginTransaction")
    def begin_transaction(
        self,
        context: RequestContext,
        resource_arn: Arn,
        secret_arn: Arn,
        database: DbName = None,
        schema: DbName = None,
    ) -> BeginTransactionResponse:
        """Starts a SQL transaction.

        ::

            <important> <p>A transaction can run for a maximum of 24 hours. A transaction is terminated and rolled back automatically after 24 hours.</p> <p>A transaction times out if no calls use its transaction ID in three minutes. If a transaction times out before it's committed, it's rolled back automatically.</p> <p>DDL statements inside a transaction cause an implicit commit. We recommend that you run each DDL statement in a separate <code>ExecuteStatement</code> call with <code>continueAfterTimeout</code> enabled.</p> </important>

        :param resource_arn: The Amazon Resource Name (ARN) of the Aurora Serverless DB cluster.
        :param secret_arn: The name or ARN of the secret that enables access to the DB cluster.
        :param database: The name of the database.
        :param schema: The name of the database schema.
        :returns: BeginTransactionResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises StatementTimeoutException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        :raises ServiceUnavailableError:
        """
        raise NotImplementedError

    @handler("CommitTransaction")
    def commit_transaction(
        self, context: RequestContext, resource_arn: Arn, secret_arn: Arn, transaction_id: Id
    ) -> CommitTransactionResponse:
        """Ends a SQL transaction started with the ``BeginTransaction`` operation
        and commits the changes.

        :param resource_arn: The Amazon Resource Name (ARN) of the Aurora Serverless DB cluster.
        :param secret_arn: The name or ARN of the secret that enables access to the DB cluster.
        :param transaction_id: The identifier of the transaction to end and commit.
        :returns: CommitTransactionResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises StatementTimeoutException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        :raises ServiceUnavailableError:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("ExecuteSql")
    def execute_sql(
        self,
        context: RequestContext,
        aws_secret_store_arn: Arn,
        db_cluster_or_instance_arn: Arn,
        sql_statements: SqlStatement,
        database: DbName = None,
        schema: DbName = None,
    ) -> ExecuteSqlResponse:
        """Runs one or more SQL statements.

        This operation is deprecated. Use the ``BatchExecuteStatement`` or
        ``ExecuteStatement`` operation.

        :param aws_secret_store_arn: The Amazon Resource Name (ARN) of the secret that enables access to the
        DB cluster.
        :param db_cluster_or_instance_arn: The ARN of the Aurora Serverless DB cluster.
        :param sql_statements: One or more SQL statements to run on the DB cluster.
        :param database: The name of the database.
        :param schema: The name of the database schema.
        :returns: ExecuteSqlResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        :raises ServiceUnavailableError:
        """
        raise NotImplementedError

    @handler("ExecuteStatement")
    def execute_statement(
        self,
        context: RequestContext,
        resource_arn: Arn,
        secret_arn: Arn,
        sql: SqlStatement,
        continue_after_timeout: Boolean = None,
        database: DbName = None,
        format_records_as: RecordsFormatType = None,
        include_result_metadata: Boolean = None,
        parameters: SqlParametersList = None,
        result_set_options: ResultSetOptions = None,
        schema: DbName = None,
        transaction_id: Id = None,
    ) -> ExecuteStatementResponse:
        """Runs a SQL statement against a database.

        If a call isn't part of a transaction because it doesn't include the
        ``transactionID`` parameter, changes that result from the call are
        committed automatically.

        If the binary response data from the database is more than 1 MB, the
        call is terminated.

        :param resource_arn: The Amazon Resource Name (ARN) of the Aurora Serverless DB cluster.
        :param secret_arn: The name or ARN of the secret that enables access to the DB cluster.
        :param sql: The SQL statement to run.
        :param continue_after_timeout: A value that indicates whether to continue running the statement after
        the call times out.
        :param database: The name of the database.
        :param format_records_as: A value that indicates whether to format the result set as a single JSON
        string.
        :param include_result_metadata: A value that indicates whether to include metadata in the results.
        :param parameters: The parameters for the SQL statement.
        :param result_set_options: Options that control how the result set is returned.
        :param schema: The name of the database schema.
        :param transaction_id: The identifier of a transaction that was started by using the
        ``BeginTransaction`` operation.
        :returns: ExecuteStatementResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises StatementTimeoutException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        :raises ServiceUnavailableError:
        """
        raise NotImplementedError

    @handler("RollbackTransaction")
    def rollback_transaction(
        self, context: RequestContext, resource_arn: Arn, secret_arn: Arn, transaction_id: Id
    ) -> RollbackTransactionResponse:
        """Performs a rollback of a transaction. Rolling back a transaction cancels
        its changes.

        :param resource_arn: The Amazon Resource Name (ARN) of the Aurora Serverless DB cluster.
        :param secret_arn: The name or ARN of the secret that enables access to the DB cluster.
        :param transaction_id: The identifier of the transaction to roll back.
        :returns: RollbackTransactionResponse
        :raises AccessDeniedException:
        :raises BadRequestException:
        :raises StatementTimeoutException:
        :raises InternalServerErrorException:
        :raises ForbiddenException:
        :raises ServiceUnavailableError:
        :raises NotFoundException:
        """
        raise NotImplementedError
