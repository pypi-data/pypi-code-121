import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AccountId = str
AttemptCount = int
AuditContextString = str
BatchSize = int
BatchWindow = int
BlueprintParameterSpec = str
BlueprintParameters = str
Boolean = bool
BooleanNullable = bool
BooleanValue = bool
CatalogGetterPageSize = int
CatalogIdString = str
Classification = str
CodeGenArgName = str
CodeGenArgValue = str
CodeGenIdentifier = str
CodeGenNodeType = str
ColumnNameString = str
ColumnTypeString = str
ColumnValuesString = str
CommentString = str
ConnectionName = str
CrawlerConfiguration = str
CrawlerSecurityConfiguration = str
CreatedTimestamp = str
CronExpression = str
CsvColumnDelimiter = str
CsvQuoteSymbol = str
CustomPatterns = str
DataLakePrincipalString = str
DatabaseName = str
DescriptionString = str
DescriptionStringRemovable = str
Double = float
DoubleValue = float
ErrorCodeString = str
ErrorMessageString = str
ErrorString = str
EventQueueArn = str
ExecutionTime = int
FieldType = str
FilterString = str
FormatString = str
Generic512CharString = str
GenericBoundedDouble = float
GenericString = str
GlueResourceArn = str
GlueVersionString = str
GrokPattern = str
HashString = str
IdString = str
Integer = int
IntegerFlag = int
IntegerValue = int
IsVersionValid = bool
JobName = str
JsonPath = str
JsonValue = str
KeyString = str
KmsKeyArn = str
LabelCount = int
LatestSchemaVersionBoolean = bool
LocationString = str
LogGroup = str
LogStream = str
MaxConcurrentRuns = int
MaxResultsNumber = int
MaxRetries = int
MessagePrefix = str
MessageString = str
MetadataKeyString = str
MetadataValueString = str
NameString = str
NonNegativeDouble = float
NonNegativeInteger = int
NotifyDelayAfter = int
NullableBoolean = bool
NullableDouble = float
NullableInteger = int
OrchestrationArgumentsValue = str
OrchestrationIAMRoleArn = str
OrchestrationNameString = str
OrchestrationRoleArn = str
OrchestrationS3Location = str
OrchestrationStatementCodeString = str
OrchestrationToken = str
PageSize = int
PaginationToken = str
ParametersMapValue = str
Path = str
PolicyJsonString = str
PredicateString = str
PythonScript = str
PythonVersionString = str
QuerySchemaVersionMetadataMaxResults = int
ReplaceBoolean = bool
Role = str
RoleArn = str
RoleString = str
RowTag = str
RunId = str
ScalaCode = str
SchemaDefinitionDiff = str
SchemaDefinitionString = str
SchemaPathString = str
SchemaRegistryNameString = str
SchemaRegistryTokenString = str
SchemaValidationError = str
SchemaVersionIdString = str
ScriptLocationString = str
TableName = str
TablePrefix = str
TableTypeString = str
TagKey = str
TagValue = str
Timeout = int
Token = str
TotalSegmentsInteger = int
TransactionIdString = str
TypeString = str
URI = str
UpdatedTimestamp = str
UriString = str
ValueString = str
VersionString = str
VersionsString = str
ViewTextString = str


class BackfillErrorCode(str):
    ENCRYPTED_PARTITION_ERROR = "ENCRYPTED_PARTITION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_PARTITION_TYPE_DATA_ERROR = "INVALID_PARTITION_TYPE_DATA_ERROR"
    MISSING_PARTITION_VALUE_ERROR = "MISSING_PARTITION_VALUE_ERROR"
    UNSUPPORTED_PARTITION_CHARACTER_ERROR = "UNSUPPORTED_PARTITION_CHARACTER_ERROR"


class BlueprintRunState(str):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    ROLLING_BACK = "ROLLING_BACK"


class BlueprintStatus(str):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    UPDATING = "UPDATING"
    FAILED = "FAILED"


class CatalogEncryptionMode(str):
    DISABLED = "DISABLED"
    SSE_KMS = "SSE-KMS"


class CloudWatchEncryptionMode(str):
    DISABLED = "DISABLED"
    SSE_KMS = "SSE-KMS"


class ColumnStatisticsType(str):
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    DECIMAL = "DECIMAL"
    DOUBLE = "DOUBLE"
    LONG = "LONG"
    STRING = "STRING"
    BINARY = "BINARY"


class Comparator(str):
    EQUALS = "EQUALS"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN_EQUALS = "GREATER_THAN_EQUALS"
    LESS_THAN_EQUALS = "LESS_THAN_EQUALS"


class Compatibility(str):
    NONE = "NONE"
    DISABLED = "DISABLED"
    BACKWARD = "BACKWARD"
    BACKWARD_ALL = "BACKWARD_ALL"
    FORWARD = "FORWARD"
    FORWARD_ALL = "FORWARD_ALL"
    FULL = "FULL"
    FULL_ALL = "FULL_ALL"


class ConnectionPropertyKey(str):
    HOST = "HOST"
    PORT = "PORT"
    USERNAME = "USERNAME"
    PASSWORD = "PASSWORD"
    ENCRYPTED_PASSWORD = "ENCRYPTED_PASSWORD"
    JDBC_DRIVER_JAR_URI = "JDBC_DRIVER_JAR_URI"
    JDBC_DRIVER_CLASS_NAME = "JDBC_DRIVER_CLASS_NAME"
    JDBC_ENGINE = "JDBC_ENGINE"
    JDBC_ENGINE_VERSION = "JDBC_ENGINE_VERSION"
    CONFIG_FILES = "CONFIG_FILES"
    INSTANCE_ID = "INSTANCE_ID"
    JDBC_CONNECTION_URL = "JDBC_CONNECTION_URL"
    JDBC_ENFORCE_SSL = "JDBC_ENFORCE_SSL"
    CUSTOM_JDBC_CERT = "CUSTOM_JDBC_CERT"
    SKIP_CUSTOM_JDBC_CERT_VALIDATION = "SKIP_CUSTOM_JDBC_CERT_VALIDATION"
    CUSTOM_JDBC_CERT_STRING = "CUSTOM_JDBC_CERT_STRING"
    CONNECTION_URL = "CONNECTION_URL"
    KAFKA_BOOTSTRAP_SERVERS = "KAFKA_BOOTSTRAP_SERVERS"
    KAFKA_SSL_ENABLED = "KAFKA_SSL_ENABLED"
    KAFKA_CUSTOM_CERT = "KAFKA_CUSTOM_CERT"
    KAFKA_SKIP_CUSTOM_CERT_VALIDATION = "KAFKA_SKIP_CUSTOM_CERT_VALIDATION"
    KAFKA_CLIENT_KEYSTORE = "KAFKA_CLIENT_KEYSTORE"
    KAFKA_CLIENT_KEYSTORE_PASSWORD = "KAFKA_CLIENT_KEYSTORE_PASSWORD"
    KAFKA_CLIENT_KEY_PASSWORD = "KAFKA_CLIENT_KEY_PASSWORD"
    ENCRYPTED_KAFKA_CLIENT_KEYSTORE_PASSWORD = "ENCRYPTED_KAFKA_CLIENT_KEYSTORE_PASSWORD"
    ENCRYPTED_KAFKA_CLIENT_KEY_PASSWORD = "ENCRYPTED_KAFKA_CLIENT_KEY_PASSWORD"
    SECRET_ID = "SECRET_ID"
    CONNECTOR_URL = "CONNECTOR_URL"
    CONNECTOR_TYPE = "CONNECTOR_TYPE"
    CONNECTOR_CLASS_NAME = "CONNECTOR_CLASS_NAME"


class ConnectionType(str):
    JDBC = "JDBC"
    SFTP = "SFTP"
    MONGODB = "MONGODB"
    KAFKA = "KAFKA"
    NETWORK = "NETWORK"
    MARKETPLACE = "MARKETPLACE"
    CUSTOM = "CUSTOM"


class CrawlState(str):
    RUNNING = "RUNNING"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class CrawlerLineageSettings(str):
    ENABLE = "ENABLE"
    DISABLE = "DISABLE"


class CrawlerState(str):
    READY = "READY"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"


class CsvHeaderOption(str):
    UNKNOWN = "UNKNOWN"
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"


class DataFormat(str):
    AVRO = "AVRO"
    JSON = "JSON"
    PROTOBUF = "PROTOBUF"


class DeleteBehavior(str):
    LOG = "LOG"
    DELETE_FROM_DATABASE = "DELETE_FROM_DATABASE"
    DEPRECATE_IN_DATABASE = "DEPRECATE_IN_DATABASE"


class EnableHybridValues(str):
    TRUE = "TRUE"
    FALSE = "FALSE"


class ExistCondition(str):
    MUST_EXIST = "MUST_EXIST"
    NOT_EXIST = "NOT_EXIST"
    NONE = "NONE"


class JobBookmarksEncryptionMode(str):
    DISABLED = "DISABLED"
    CSE_KMS = "CSE-KMS"


class JobRunState(str):
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class Language(str):
    PYTHON = "PYTHON"
    SCALA = "SCALA"


class LastCrawlStatus(str):
    SUCCEEDED = "SUCCEEDED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class Logical(str):
    AND = "AND"
    ANY = "ANY"


class LogicalOperator(str):
    EQUALS = "EQUALS"


class MLUserDataEncryptionModeString(str):
    DISABLED = "DISABLED"
    SSE_KMS = "SSE-KMS"


class NodeType(str):
    CRAWLER = "CRAWLER"
    JOB = "JOB"
    TRIGGER = "TRIGGER"


class PartitionIndexStatus(str):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"
    FAILED = "FAILED"


class Permission(str):
    ALL = "ALL"
    SELECT = "SELECT"
    ALTER = "ALTER"
    DROP = "DROP"
    DELETE = "DELETE"
    INSERT = "INSERT"
    CREATE_DATABASE = "CREATE_DATABASE"
    CREATE_TABLE = "CREATE_TABLE"
    DATA_LOCATION_ACCESS = "DATA_LOCATION_ACCESS"


class PermissionType(str):
    COLUMN_PERMISSION = "COLUMN_PERMISSION"
    CELL_FILTER_PERMISSION = "CELL_FILTER_PERMISSION"


class PrincipalType(str):
    USER = "USER"
    ROLE = "ROLE"
    GROUP = "GROUP"


class RecrawlBehavior(str):
    CRAWL_EVERYTHING = "CRAWL_EVERYTHING"
    CRAWL_NEW_FOLDERS_ONLY = "CRAWL_NEW_FOLDERS_ONLY"
    CRAWL_EVENT_MODE = "CRAWL_EVENT_MODE"


class RegistryStatus(str):
    AVAILABLE = "AVAILABLE"
    DELETING = "DELETING"


class ResourceShareType(str):
    FOREIGN = "FOREIGN"
    ALL = "ALL"


class ResourceType(str):
    JAR = "JAR"
    FILE = "FILE"
    ARCHIVE = "ARCHIVE"


class S3EncryptionMode(str):
    DISABLED = "DISABLED"
    SSE_KMS = "SSE-KMS"
    SSE_S3 = "SSE-S3"


class ScheduleState(str):
    SCHEDULED = "SCHEDULED"
    NOT_SCHEDULED = "NOT_SCHEDULED"
    TRANSITIONING = "TRANSITIONING"


class SchemaDiffType(str):
    SYNTAX_DIFF = "SYNTAX_DIFF"


class SchemaStatus(str):
    AVAILABLE = "AVAILABLE"
    PENDING = "PENDING"
    DELETING = "DELETING"


class SchemaVersionStatus(str):
    AVAILABLE = "AVAILABLE"
    PENDING = "PENDING"
    FAILURE = "FAILURE"
    DELETING = "DELETING"


class SessionStatus(str):
    PROVISIONING = "PROVISIONING"
    READY = "READY"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"


class Sort(str):
    ASC = "ASC"
    DESC = "DESC"


class SortDirectionType(str):
    DESCENDING = "DESCENDING"
    ASCENDING = "ASCENDING"


class StatementState(str):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    AVAILABLE = "AVAILABLE"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"


class TaskRunSortColumnType(str):
    TASK_RUN_TYPE = "TASK_RUN_TYPE"
    STATUS = "STATUS"
    STARTED = "STARTED"


class TaskStatusType(str):
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class TaskType(str):
    EVALUATION = "EVALUATION"
    LABELING_SET_GENERATION = "LABELING_SET_GENERATION"
    IMPORT_LABELS = "IMPORT_LABELS"
    EXPORT_LABELS = "EXPORT_LABELS"
    FIND_MATCHES = "FIND_MATCHES"


class TransformSortColumnType(str):
    NAME = "NAME"
    TRANSFORM_TYPE = "TRANSFORM_TYPE"
    STATUS = "STATUS"
    CREATED = "CREATED"
    LAST_MODIFIED = "LAST_MODIFIED"


class TransformStatusType(str):
    NOT_READY = "NOT_READY"
    READY = "READY"
    DELETING = "DELETING"


class TransformType(str):
    FIND_MATCHES = "FIND_MATCHES"


class TriggerState(str):
    CREATING = "CREATING"
    CREATED = "CREATED"
    ACTIVATING = "ACTIVATING"
    ACTIVATED = "ACTIVATED"
    DEACTIVATING = "DEACTIVATING"
    DEACTIVATED = "DEACTIVATED"
    DELETING = "DELETING"
    UPDATING = "UPDATING"


class TriggerType(str):
    SCHEDULED = "SCHEDULED"
    CONDITIONAL = "CONDITIONAL"
    ON_DEMAND = "ON_DEMAND"
    EVENT = "EVENT"


class UpdateBehavior(str):
    LOG = "LOG"
    UPDATE_IN_DATABASE = "UPDATE_IN_DATABASE"


class WorkerType(str):
    Standard = "Standard"
    G_1X = "G.1X"
    G_2X = "G.2X"


class WorkflowRunStatus(str):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class AccessDeniedException(ServiceException):
    """Access to a resource was denied."""

    Message: Optional[MessageString]


class AlreadyExistsException(ServiceException):
    """A resource to be created or added already exists."""

    Message: Optional[MessageString]


class ConcurrentModificationException(ServiceException):
    """Two processes are trying to modify a resource simultaneously."""

    Message: Optional[MessageString]


class ConcurrentRunsExceededException(ServiceException):
    """Too many jobs are being run concurrently."""

    Message: Optional[MessageString]


class ConditionCheckFailureException(ServiceException):
    """A specified condition was not satisfied."""

    Message: Optional[MessageString]


class ConflictException(ServiceException):
    """The ``CreatePartitions`` API was called on a table that has indexes
    enabled.
    """

    Message: Optional[MessageString]


class CrawlerNotRunningException(ServiceException):
    """The specified crawler is not running."""

    Message: Optional[MessageString]


class CrawlerRunningException(ServiceException):
    """The operation cannot be performed because the crawler is already
    running.
    """

    Message: Optional[MessageString]


class CrawlerStoppingException(ServiceException):
    """The specified crawler is stopping."""

    Message: Optional[MessageString]


class EntityNotFoundException(ServiceException):
    """A specified entity does not exist"""

    Message: Optional[MessageString]


class GlueEncryptionException(ServiceException):
    """An encryption operation failed."""

    Message: Optional[MessageString]


class IdempotentParameterMismatchException(ServiceException):
    """The same unique identifier was associated with two different records."""

    Message: Optional[MessageString]


class IllegalBlueprintStateException(ServiceException):
    Message: Optional[MessageString]


class IllegalSessionStateException(ServiceException):
    """The session is in an invalid state to perform a requested operation."""

    Message: Optional[MessageString]


class IllegalWorkflowStateException(ServiceException):
    """The workflow is in an invalid state to perform a requested operation."""

    Message: Optional[MessageString]


class InternalServiceException(ServiceException):
    """An internal service error occurred."""

    Message: Optional[MessageString]


class InvalidInputException(ServiceException):
    """The input provided was not valid."""

    Message: Optional[MessageString]


class InvalidStateException(ServiceException):
    """An error that indicates your data is in an invalid state."""

    Message: Optional[MessageString]


class MLTransformNotReadyException(ServiceException):
    """The machine learning transform is not ready to run."""

    Message: Optional[MessageString]


class NoScheduleException(ServiceException):
    """There is no applicable schedule."""

    Message: Optional[MessageString]


class OperationTimeoutException(ServiceException):
    """The operation timed out."""

    Message: Optional[MessageString]


class PermissionTypeMismatchException(ServiceException):
    Message: Optional[MessageString]


class ResourceNotReadyException(ServiceException):
    """A resource was not ready for a transaction."""

    Message: Optional[MessageString]


class ResourceNumberLimitExceededException(ServiceException):
    """A resource numerical limit was exceeded."""

    Message: Optional[MessageString]


class SchedulerNotRunningException(ServiceException):
    """The specified scheduler is not running."""

    Message: Optional[MessageString]


class SchedulerRunningException(ServiceException):
    """The specified scheduler is already running."""

    Message: Optional[MessageString]


class SchedulerTransitioningException(ServiceException):
    """The specified scheduler is transitioning."""

    Message: Optional[MessageString]


class ValidationException(ServiceException):
    """A value could not be validated."""

    Message: Optional[MessageString]


class VersionMismatchException(ServiceException):
    """There was a version conflict."""

    Message: Optional[MessageString]


class NotificationProperty(TypedDict, total=False):
    """Specifies configuration properties of a notification."""

    NotifyDelayAfter: Optional[NotifyDelayAfter]


GenericMap = Dict[GenericString, GenericString]


class Action(TypedDict, total=False):
    """Defines an action to be initiated by a trigger."""

    JobName: Optional[NameString]
    Arguments: Optional[GenericMap]
    Timeout: Optional[Timeout]
    SecurityConfiguration: Optional[NameString]
    NotificationProperty: Optional[NotificationProperty]
    CrawlerName: Optional[NameString]


ActionList = List[Action]
AdditionalPlanOptionsMap = Dict[GenericString, GenericString]
AuditColumnNamesList = List[ColumnNameString]


class AuditContext(TypedDict, total=False):
    """A structure containing information for audit."""

    AdditionalAuditContext: Optional[AuditContextString]
    RequestedColumns: Optional[AuditColumnNamesList]
    AllColumnsRequested: Optional[NullableBoolean]


ValueStringList = List[ValueString]


class PartitionValueList(TypedDict, total=False):
    """Contains a list of values defining partitions."""

    Values: ValueStringList


BackfillErroredPartitionsList = List[PartitionValueList]


class BackfillError(TypedDict, total=False):
    """A list of errors that can occur when registering partition indexes for
    an existing table.

    These errors give the details about why an index registration failed and
    provide a limited number of partitions in the response, so that you can
    fix the partitions at fault and try registering the index again. The
    most common set of errors that can occur are categorized as follows:

    -  EncryptedPartitionError: The partitions are encrypted.

    -  InvalidPartitionTypeDataError: The partition value doesn't match the
       data type for that partition column.

    -  MissingPartitionValueError: The partitions are encrypted.

    -  UnsupportedPartitionCharacterError: Characters inside the partition
       value are not supported. For example: U+0000 , U+0001, U+0002.

    -  InternalError: Any error which does not belong to other error codes.
    """

    Code: Optional[BackfillErrorCode]
    Partitions: Optional[BackfillErroredPartitionsList]


BackfillErrors = List[BackfillError]
Timestamp = datetime
ParametersMap = Dict[KeyString, ParametersMapValue]
VersionLongNumber = int


class SchemaId(TypedDict, total=False):
    """The unique ID of the schema in the Glue schema registry."""

    SchemaArn: Optional[GlueResourceArn]
    SchemaName: Optional[SchemaRegistryNameString]
    RegistryName: Optional[SchemaRegistryNameString]


class SchemaReference(TypedDict, total=False):
    """An object that references a schema stored in the Glue Schema Registry."""

    SchemaId: Optional[SchemaId]
    SchemaVersionId: Optional[SchemaVersionIdString]
    SchemaVersionNumber: Optional[VersionLongNumber]


LocationMap = Dict[ColumnValuesString, ColumnValuesString]
ColumnValueStringList = List[ColumnValuesString]
NameStringList = List[NameString]


class SkewedInfo(TypedDict, total=False):
    """Specifies skewed values in a table. Skewed values are those that occur
    with very high frequency.
    """

    SkewedColumnNames: Optional[NameStringList]
    SkewedColumnValues: Optional[ColumnValueStringList]
    SkewedColumnValueLocationMaps: Optional[LocationMap]


class Order(TypedDict, total=False):
    """Specifies the sort order of a sorted column."""

    Column: NameString
    SortOrder: IntegerFlag


OrderList = List[Order]


class SerDeInfo(TypedDict, total=False):
    """Information about a serialization/deserialization program (SerDe) that
    serves as an extractor and loader.
    """

    Name: Optional[NameString]
    SerializationLibrary: Optional[NameString]
    Parameters: Optional[ParametersMap]


LocationStringList = List[LocationString]


class Column(TypedDict, total=False):
    """A column in a ``Table``."""

    Name: NameString
    Type: Optional[ColumnTypeString]
    Comment: Optional[CommentString]
    Parameters: Optional[ParametersMap]


ColumnList = List[Column]


class StorageDescriptor(TypedDict, total=False):
    """Describes the physical storage of table data."""

    Columns: Optional[ColumnList]
    Location: Optional[LocationString]
    AdditionalLocations: Optional[LocationStringList]
    InputFormat: Optional[FormatString]
    OutputFormat: Optional[FormatString]
    Compressed: Optional[Boolean]
    NumberOfBuckets: Optional[Integer]
    SerdeInfo: Optional[SerDeInfo]
    BucketColumns: Optional[NameStringList]
    SortColumns: Optional[OrderList]
    Parameters: Optional[ParametersMap]
    SkewedInfo: Optional[SkewedInfo]
    StoredAsSubDirectories: Optional[Boolean]
    SchemaReference: Optional[SchemaReference]


class PartitionInput(TypedDict, total=False):
    """The structure used to create and update a partition."""

    Values: Optional[ValueStringList]
    LastAccessTime: Optional[Timestamp]
    StorageDescriptor: Optional[StorageDescriptor]
    Parameters: Optional[ParametersMap]
    LastAnalyzedTime: Optional[Timestamp]


PartitionInputList = List[PartitionInput]


class BatchCreatePartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionInputList: PartitionInputList


class ErrorDetail(TypedDict, total=False):
    """Contains details about an error."""

    ErrorCode: Optional[NameString]
    ErrorMessage: Optional[DescriptionString]


class PartitionError(TypedDict, total=False):
    """Contains information about a partition error."""

    PartitionValues: Optional[ValueStringList]
    ErrorDetail: Optional[ErrorDetail]


PartitionErrors = List[PartitionError]


class BatchCreatePartitionResponse(TypedDict, total=False):
    Errors: Optional[PartitionErrors]


DeleteConnectionNameList = List[NameString]


class BatchDeleteConnectionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    ConnectionNameList: DeleteConnectionNameList


ErrorByName = Dict[NameString, ErrorDetail]


class BatchDeleteConnectionResponse(TypedDict, total=False):
    Succeeded: Optional[NameStringList]
    Errors: Optional[ErrorByName]


BatchDeletePartitionValueList = List[PartitionValueList]


class BatchDeletePartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionsToDelete: BatchDeletePartitionValueList


class BatchDeletePartitionResponse(TypedDict, total=False):
    Errors: Optional[PartitionErrors]


BatchDeleteTableNameList = List[NameString]


class BatchDeleteTableRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TablesToDelete: BatchDeleteTableNameList
    TransactionId: Optional[TransactionIdString]


class TableError(TypedDict, total=False):
    """An error record for table operations."""

    TableName: Optional[NameString]
    ErrorDetail: Optional[ErrorDetail]


TableErrors = List[TableError]


class BatchDeleteTableResponse(TypedDict, total=False):
    Errors: Optional[TableErrors]


BatchDeleteTableVersionList = List[VersionString]


class BatchDeleteTableVersionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    VersionIds: BatchDeleteTableVersionList


class TableVersionError(TypedDict, total=False):
    """An error record for table-version operations."""

    TableName: Optional[NameString]
    VersionId: Optional[VersionString]
    ErrorDetail: Optional[ErrorDetail]


TableVersionErrors = List[TableVersionError]


class BatchDeleteTableVersionResponse(TypedDict, total=False):
    Errors: Optional[TableVersionErrors]


BatchGetBlueprintNames = List[OrchestrationNameString]


class BatchGetBlueprintsRequest(ServiceRequest):
    Names: BatchGetBlueprintNames
    IncludeBlueprint: Optional[NullableBoolean]
    IncludeParameterSpec: Optional[NullableBoolean]


BlueprintNames = List[OrchestrationNameString]
TimestampValue = datetime


class LastActiveDefinition(TypedDict, total=False):
    """When there are multiple versions of a blueprint and the latest version
    has some errors, this attribute indicates the last successful blueprint
    definition that is available with the service.
    """

    Description: Optional[Generic512CharString]
    LastModifiedOn: Optional[TimestampValue]
    ParameterSpec: Optional[BlueprintParameterSpec]
    BlueprintLocation: Optional[GenericString]
    BlueprintServiceLocation: Optional[GenericString]


class Blueprint(TypedDict, total=False):
    """The details of a blueprint."""

    Name: Optional[OrchestrationNameString]
    Description: Optional[Generic512CharString]
    CreatedOn: Optional[TimestampValue]
    LastModifiedOn: Optional[TimestampValue]
    ParameterSpec: Optional[BlueprintParameterSpec]
    BlueprintLocation: Optional[GenericString]
    BlueprintServiceLocation: Optional[GenericString]
    Status: Optional[BlueprintStatus]
    ErrorMessage: Optional[ErrorString]
    LastActiveDefinition: Optional[LastActiveDefinition]


Blueprints = List[Blueprint]


class BatchGetBlueprintsResponse(TypedDict, total=False):
    Blueprints: Optional[Blueprints]
    MissingBlueprints: Optional[BlueprintNames]


CrawlerNameList = List[NameString]


class BatchGetCrawlersRequest(ServiceRequest):
    CrawlerNames: CrawlerNameList


class LakeFormationConfiguration(TypedDict, total=False):
    """Specifies AWS Lake Formation configuration settings for the crawler."""

    UseLakeFormationCredentials: Optional[NullableBoolean]
    AccountId: Optional[AccountId]


VersionId = int


class LastCrawlInfo(TypedDict, total=False):
    """Status and error information about the most recent crawl."""

    Status: Optional[LastCrawlStatus]
    ErrorMessage: Optional[DescriptionString]
    LogGroup: Optional[LogGroup]
    LogStream: Optional[LogStream]
    MessagePrefix: Optional[MessagePrefix]
    StartTime: Optional[Timestamp]


MillisecondsCount = int


class Schedule(TypedDict, total=False):
    """A scheduling object using a ``cron`` statement to schedule an event."""

    ScheduleExpression: Optional[CronExpression]
    State: Optional[ScheduleState]


class LineageConfiguration(TypedDict, total=False):
    """Specifies data lineage configuration settings for the crawler."""

    CrawlerLineageSettings: Optional[CrawlerLineageSettings]


class SchemaChangePolicy(TypedDict, total=False):
    """A policy that specifies update and deletion behaviors for the crawler."""

    UpdateBehavior: Optional[UpdateBehavior]
    DeleteBehavior: Optional[DeleteBehavior]


class RecrawlPolicy(TypedDict, total=False):
    """When crawling an Amazon S3 data source after the first crawl is
    complete, specifies whether to crawl the entire dataset again or to
    crawl only folders that were added since the last crawler run. For more
    information, see `Incremental Crawls in
    Glue <https://docs.aws.amazon.com/glue/latest/dg/incremental-crawls.html>`__
    in the developer guide.
    """

    RecrawlBehavior: Optional[RecrawlBehavior]


ClassifierNameList = List[NameString]
PathList = List[Path]


class DeltaTarget(TypedDict, total=False):
    """Specifies a Delta data store to crawl one or more Delta tables."""

    DeltaTables: Optional[PathList]
    ConnectionName: Optional[ConnectionName]
    WriteManifest: Optional[NullableBoolean]


DeltaTargetList = List[DeltaTarget]
CatalogTablesList = List[NameString]


class CatalogTarget(TypedDict, total=False):
    """Specifies an Glue Data Catalog target."""

    DatabaseName: NameString
    Tables: CatalogTablesList
    ConnectionName: Optional[ConnectionName]


CatalogTargetList = List[CatalogTarget]


class DynamoDBTarget(TypedDict, total=False):
    """Specifies an Amazon DynamoDB table to crawl."""

    Path: Optional[Path]
    scanAll: Optional[NullableBoolean]
    scanRate: Optional[NullableDouble]


DynamoDBTargetList = List[DynamoDBTarget]


class MongoDBTarget(TypedDict, total=False):
    """Specifies an Amazon DocumentDB or MongoDB data store to crawl."""

    ConnectionName: Optional[ConnectionName]
    Path: Optional[Path]
    ScanAll: Optional[NullableBoolean]


MongoDBTargetList = List[MongoDBTarget]


class JdbcTarget(TypedDict, total=False):
    """Specifies a JDBC data store to crawl."""

    ConnectionName: Optional[ConnectionName]
    Path: Optional[Path]
    Exclusions: Optional[PathList]


JdbcTargetList = List[JdbcTarget]


class S3Target(TypedDict, total=False):
    """Specifies a data store in Amazon Simple Storage Service (Amazon S3)."""

    Path: Optional[Path]
    Exclusions: Optional[PathList]
    ConnectionName: Optional[ConnectionName]
    SampleSize: Optional[NullableInteger]
    EventQueueArn: Optional[EventQueueArn]
    DlqEventQueueArn: Optional[EventQueueArn]


S3TargetList = List[S3Target]


class CrawlerTargets(TypedDict, total=False):
    """Specifies data stores to crawl."""

    S3Targets: Optional[S3TargetList]
    JdbcTargets: Optional[JdbcTargetList]
    MongoDBTargets: Optional[MongoDBTargetList]
    DynamoDBTargets: Optional[DynamoDBTargetList]
    CatalogTargets: Optional[CatalogTargetList]
    DeltaTargets: Optional[DeltaTargetList]


class Crawler(TypedDict, total=False):
    """Specifies a crawler program that examines a data source and uses
    classifiers to try to determine its schema. If successful, the crawler
    records metadata concerning the data source in the Glue Data Catalog.
    """

    Name: Optional[NameString]
    Role: Optional[Role]
    Targets: Optional[CrawlerTargets]
    DatabaseName: Optional[DatabaseName]
    Description: Optional[DescriptionString]
    Classifiers: Optional[ClassifierNameList]
    RecrawlPolicy: Optional[RecrawlPolicy]
    SchemaChangePolicy: Optional[SchemaChangePolicy]
    LineageConfiguration: Optional[LineageConfiguration]
    State: Optional[CrawlerState]
    TablePrefix: Optional[TablePrefix]
    Schedule: Optional[Schedule]
    CrawlElapsedTime: Optional[MillisecondsCount]
    CreationTime: Optional[Timestamp]
    LastUpdated: Optional[Timestamp]
    LastCrawl: Optional[LastCrawlInfo]
    Version: Optional[VersionId]
    Configuration: Optional[CrawlerConfiguration]
    CrawlerSecurityConfiguration: Optional[CrawlerSecurityConfiguration]
    LakeFormationConfiguration: Optional[LakeFormationConfiguration]


CrawlerList = List[Crawler]


class BatchGetCrawlersResponse(TypedDict, total=False):
    Crawlers: Optional[CrawlerList]
    CrawlersNotFound: Optional[CrawlerNameList]


CustomEntityTypeNames = List[NameString]


class BatchGetCustomEntityTypesRequest(ServiceRequest):
    Names: CustomEntityTypeNames


ContextWords = List[NameString]


class CustomEntityType(TypedDict, total=False):
    """An object representing a custom pattern for detecting sensitive data
    across the columns and rows of your structured data.
    """

    Name: NameString
    RegexString: NameString
    ContextWords: Optional[ContextWords]


CustomEntityTypes = List[CustomEntityType]


class BatchGetCustomEntityTypesResponse(TypedDict, total=False):
    CustomEntityTypes: Optional[CustomEntityTypes]
    CustomEntityTypesNotFound: Optional[CustomEntityTypeNames]


DevEndpointNames = List[GenericString]


class BatchGetDevEndpointsRequest(ServiceRequest):
    DevEndpointNames: DevEndpointNames


MapValue = Dict[GenericString, GenericString]
PublicKeysList = List[GenericString]
StringList = List[GenericString]


class DevEndpoint(TypedDict, total=False):
    """A development endpoint where a developer can remotely debug extract,
    transform, and load (ETL) scripts.
    """

    EndpointName: Optional[GenericString]
    RoleArn: Optional[RoleArn]
    SecurityGroupIds: Optional[StringList]
    SubnetId: Optional[GenericString]
    YarnEndpointAddress: Optional[GenericString]
    PrivateAddress: Optional[GenericString]
    ZeppelinRemoteSparkInterpreterPort: Optional[IntegerValue]
    PublicAddress: Optional[GenericString]
    Status: Optional[GenericString]
    WorkerType: Optional[WorkerType]
    GlueVersion: Optional[GlueVersionString]
    NumberOfWorkers: Optional[NullableInteger]
    NumberOfNodes: Optional[IntegerValue]
    AvailabilityZone: Optional[GenericString]
    VpcId: Optional[GenericString]
    ExtraPythonLibsS3Path: Optional[GenericString]
    ExtraJarsS3Path: Optional[GenericString]
    FailureReason: Optional[GenericString]
    LastUpdateStatus: Optional[GenericString]
    CreatedTimestamp: Optional[TimestampValue]
    LastModifiedTimestamp: Optional[TimestampValue]
    PublicKey: Optional[GenericString]
    PublicKeys: Optional[PublicKeysList]
    SecurityConfiguration: Optional[NameString]
    Arguments: Optional[MapValue]


DevEndpointList = List[DevEndpoint]


class BatchGetDevEndpointsResponse(TypedDict, total=False):
    DevEndpoints: Optional[DevEndpointList]
    DevEndpointsNotFound: Optional[DevEndpointNames]


JobNameList = List[NameString]


class BatchGetJobsRequest(ServiceRequest):
    JobNames: JobNameList


OrchestrationStringList = List[GenericString]


class ConnectionsList(TypedDict, total=False):
    """Specifies the connections used by a job."""

    Connections: Optional[OrchestrationStringList]


class JobCommand(TypedDict, total=False):
    """Specifies code that runs when a job is run."""

    Name: Optional[GenericString]
    ScriptLocation: Optional[ScriptLocationString]
    PythonVersion: Optional[PythonVersionString]


class ExecutionProperty(TypedDict, total=False):
    """An execution property of a job."""

    MaxConcurrentRuns: Optional[MaxConcurrentRuns]


class Job(TypedDict, total=False):
    """Specifies a job definition."""

    Name: Optional[NameString]
    Description: Optional[DescriptionString]
    LogUri: Optional[UriString]
    Role: Optional[RoleString]
    CreatedOn: Optional[TimestampValue]
    LastModifiedOn: Optional[TimestampValue]
    ExecutionProperty: Optional[ExecutionProperty]
    Command: Optional[JobCommand]
    DefaultArguments: Optional[GenericMap]
    NonOverridableArguments: Optional[GenericMap]
    Connections: Optional[ConnectionsList]
    MaxRetries: Optional[MaxRetries]
    AllocatedCapacity: Optional[IntegerValue]
    Timeout: Optional[Timeout]
    MaxCapacity: Optional[NullableDouble]
    WorkerType: Optional[WorkerType]
    NumberOfWorkers: Optional[NullableInteger]
    SecurityConfiguration: Optional[NameString]
    NotificationProperty: Optional[NotificationProperty]
    GlueVersion: Optional[GlueVersionString]


JobList = List[Job]


class BatchGetJobsResponse(TypedDict, total=False):
    Jobs: Optional[JobList]
    JobsNotFound: Optional[JobNameList]


BatchGetPartitionValueList = List[PartitionValueList]


class BatchGetPartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionsToGet: BatchGetPartitionValueList


class Partition(TypedDict, total=False):
    """Represents a slice of table data."""

    Values: Optional[ValueStringList]
    DatabaseName: Optional[NameString]
    TableName: Optional[NameString]
    CreationTime: Optional[Timestamp]
    LastAccessTime: Optional[Timestamp]
    StorageDescriptor: Optional[StorageDescriptor]
    Parameters: Optional[ParametersMap]
    LastAnalyzedTime: Optional[Timestamp]
    CatalogId: Optional[CatalogIdString]


PartitionList = List[Partition]


class BatchGetPartitionResponse(TypedDict, total=False):
    Partitions: Optional[PartitionList]
    UnprocessedKeys: Optional[BatchGetPartitionValueList]


TriggerNameList = List[NameString]


class BatchGetTriggersRequest(ServiceRequest):
    TriggerNames: TriggerNameList


class EventBatchingCondition(TypedDict, total=False):
    """Batch condition that must be met (specified number of events received or
    batch time window expired) before EventBridge event trigger fires.
    """

    BatchSize: BatchSize
    BatchWindow: Optional[BatchWindow]


class Condition(TypedDict, total=False):
    """Defines a condition under which a trigger fires."""

    LogicalOperator: Optional[LogicalOperator]
    JobName: Optional[NameString]
    State: Optional[JobRunState]
    CrawlerName: Optional[NameString]
    CrawlState: Optional[CrawlState]


ConditionList = List[Condition]


class Predicate(TypedDict, total=False):
    """Defines the predicate of the trigger, which determines when it fires."""

    Logical: Optional[Logical]
    Conditions: Optional[ConditionList]


class Trigger(TypedDict, total=False):
    """Information about a specific trigger."""

    Name: Optional[NameString]
    WorkflowName: Optional[NameString]
    Id: Optional[IdString]
    Type: Optional[TriggerType]
    State: Optional[TriggerState]
    Description: Optional[DescriptionString]
    Schedule: Optional[GenericString]
    Actions: Optional[ActionList]
    Predicate: Optional[Predicate]
    EventBatchingCondition: Optional[EventBatchingCondition]


TriggerList = List[Trigger]


class BatchGetTriggersResponse(TypedDict, total=False):
    Triggers: Optional[TriggerList]
    TriggersNotFound: Optional[TriggerNameList]


WorkflowNames = List[NameString]


class BatchGetWorkflowsRequest(ServiceRequest):
    Names: WorkflowNames
    IncludeGraph: Optional[NullableBoolean]


class BlueprintDetails(TypedDict, total=False):
    """The details of a blueprint."""

    BlueprintName: Optional[OrchestrationNameString]
    RunId: Optional[IdString]


class Edge(TypedDict, total=False):
    """An edge represents a directed connection between two components on a
    workflow graph.
    """

    SourceId: Optional[NameString]
    DestinationId: Optional[NameString]


EdgeList = List[Edge]


class Crawl(TypedDict, total=False):
    """The details of a crawl in the workflow."""

    State: Optional[CrawlState]
    StartedOn: Optional[TimestampValue]
    CompletedOn: Optional[TimestampValue]
    ErrorMessage: Optional[DescriptionString]
    LogGroup: Optional[LogGroup]
    LogStream: Optional[LogStream]


CrawlList = List[Crawl]


class CrawlerNodeDetails(TypedDict, total=False):
    """The details of a Crawler node present in the workflow."""

    Crawls: Optional[CrawlList]


class Predecessor(TypedDict, total=False):
    """A job run that was used in the predicate of a conditional trigger that
    triggered this job run.
    """

    JobName: Optional[NameString]
    RunId: Optional[IdString]


PredecessorList = List[Predecessor]


class JobRun(TypedDict, total=False):
    """Contains information about a job run."""

    Id: Optional[IdString]
    Attempt: Optional[AttemptCount]
    PreviousRunId: Optional[IdString]
    TriggerName: Optional[NameString]
    JobName: Optional[NameString]
    StartedOn: Optional[TimestampValue]
    LastModifiedOn: Optional[TimestampValue]
    CompletedOn: Optional[TimestampValue]
    JobRunState: Optional[JobRunState]
    Arguments: Optional[GenericMap]
    ErrorMessage: Optional[ErrorString]
    PredecessorRuns: Optional[PredecessorList]
    AllocatedCapacity: Optional[IntegerValue]
    ExecutionTime: Optional[ExecutionTime]
    Timeout: Optional[Timeout]
    MaxCapacity: Optional[NullableDouble]
    WorkerType: Optional[WorkerType]
    NumberOfWorkers: Optional[NullableInteger]
    SecurityConfiguration: Optional[NameString]
    LogGroupName: Optional[GenericString]
    NotificationProperty: Optional[NotificationProperty]
    GlueVersion: Optional[GlueVersionString]
    DPUSeconds: Optional[NullableDouble]


JobRunList = List[JobRun]


class JobNodeDetails(TypedDict, total=False):
    """The details of a Job node present in the workflow."""

    JobRuns: Optional[JobRunList]


class TriggerNodeDetails(TypedDict, total=False):
    """The details of a Trigger node present in the workflow."""

    Trigger: Optional[Trigger]


class Node(TypedDict, total=False):
    """A node represents an Glue component (trigger, crawler, or job) on a
    workflow graph.
    """

    Type: Optional[NodeType]
    Name: Optional[NameString]
    UniqueId: Optional[NameString]
    TriggerDetails: Optional[TriggerNodeDetails]
    JobDetails: Optional[JobNodeDetails]
    CrawlerDetails: Optional[CrawlerNodeDetails]


NodeList = List[Node]


class WorkflowGraph(TypedDict, total=False):
    """A workflow graph represents the complete workflow containing all the
    Glue components present in the workflow and all the directed connections
    between them.
    """

    Nodes: Optional[NodeList]
    Edges: Optional[EdgeList]


class StartingEventBatchCondition(TypedDict, total=False):
    """The batch condition that started the workflow run. Either the number of
    events in the batch size arrived, in which case the BatchSize member is
    non-zero, or the batch window expired, in which case the BatchWindow
    member is non-zero.
    """

    BatchSize: Optional[NullableInteger]
    BatchWindow: Optional[NullableInteger]


class WorkflowRunStatistics(TypedDict, total=False):
    """Workflow run statistics provides statistics about the workflow run."""

    TotalActions: Optional[IntegerValue]
    TimeoutActions: Optional[IntegerValue]
    FailedActions: Optional[IntegerValue]
    StoppedActions: Optional[IntegerValue]
    SucceededActions: Optional[IntegerValue]
    RunningActions: Optional[IntegerValue]


WorkflowRunProperties = Dict[IdString, GenericString]


class WorkflowRun(TypedDict, total=False):
    """A workflow run is an execution of a workflow providing all the runtime
    information.
    """

    Name: Optional[NameString]
    WorkflowRunId: Optional[IdString]
    PreviousRunId: Optional[IdString]
    WorkflowRunProperties: Optional[WorkflowRunProperties]
    StartedOn: Optional[TimestampValue]
    CompletedOn: Optional[TimestampValue]
    Status: Optional[WorkflowRunStatus]
    ErrorMessage: Optional[ErrorString]
    Statistics: Optional[WorkflowRunStatistics]
    Graph: Optional[WorkflowGraph]
    StartingEventBatchCondition: Optional[StartingEventBatchCondition]


class Workflow(TypedDict, total=False):
    """A workflow is a collection of multiple dependent Glue jobs and crawlers
    that are run to complete a complex ETL task. A workflow manages the
    execution and monitoring of all its jobs and crawlers.
    """

    Name: Optional[NameString]
    Description: Optional[GenericString]
    DefaultRunProperties: Optional[WorkflowRunProperties]
    CreatedOn: Optional[TimestampValue]
    LastModifiedOn: Optional[TimestampValue]
    LastRun: Optional[WorkflowRun]
    Graph: Optional[WorkflowGraph]
    MaxConcurrentRuns: Optional[NullableInteger]
    BlueprintDetails: Optional[BlueprintDetails]


Workflows = List[Workflow]


class BatchGetWorkflowsResponse(TypedDict, total=False):
    Workflows: Optional[Workflows]
    MissingWorkflows: Optional[WorkflowNames]


class BatchStopJobRunError(TypedDict, total=False):
    """Records an error that occurred when attempting to stop a specified job
    run.
    """

    JobName: Optional[NameString]
    JobRunId: Optional[IdString]
    ErrorDetail: Optional[ErrorDetail]


BatchStopJobRunErrorList = List[BatchStopJobRunError]
BatchStopJobRunJobRunIdList = List[IdString]


class BatchStopJobRunRequest(ServiceRequest):
    JobName: NameString
    JobRunIds: BatchStopJobRunJobRunIdList


class BatchStopJobRunSuccessfulSubmission(TypedDict, total=False):
    """Records a successful request to stop a specified ``JobRun``."""

    JobName: Optional[NameString]
    JobRunId: Optional[IdString]


BatchStopJobRunSuccessfulSubmissionList = List[BatchStopJobRunSuccessfulSubmission]


class BatchStopJobRunResponse(TypedDict, total=False):
    SuccessfulSubmissions: Optional[BatchStopJobRunSuccessfulSubmissionList]
    Errors: Optional[BatchStopJobRunErrorList]


BoundedPartitionValueList = List[ValueString]


class BatchUpdatePartitionFailureEntry(TypedDict, total=False):
    """Contains information about a batch update partition error."""

    PartitionValueList: Optional[BoundedPartitionValueList]
    ErrorDetail: Optional[ErrorDetail]


BatchUpdatePartitionFailureList = List[BatchUpdatePartitionFailureEntry]


class BatchUpdatePartitionRequestEntry(TypedDict, total=False):
    """A structure that contains the values and structure used to update a
    partition.
    """

    PartitionValueList: BoundedPartitionValueList
    PartitionInput: PartitionInput


BatchUpdatePartitionRequestEntryList = List[BatchUpdatePartitionRequestEntry]


class BatchUpdatePartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    Entries: BatchUpdatePartitionRequestEntryList


class BatchUpdatePartitionResponse(TypedDict, total=False):
    Errors: Optional[BatchUpdatePartitionFailureList]


NonNegativeLong = int


class BinaryColumnStatisticsData(TypedDict, total=False):
    """Defines column statistics supported for bit sequence data values."""

    MaximumLength: NonNegativeLong
    AverageLength: NonNegativeDouble
    NumberOfNulls: NonNegativeLong


Blob = bytes


class BlueprintRun(TypedDict, total=False):
    """The details of a blueprint run."""

    BlueprintName: Optional[OrchestrationNameString]
    RunId: Optional[IdString]
    WorkflowName: Optional[NameString]
    State: Optional[BlueprintRunState]
    StartedOn: Optional[TimestampValue]
    CompletedOn: Optional[TimestampValue]
    ErrorMessage: Optional[MessageString]
    RollbackErrorMessage: Optional[MessageString]
    Parameters: Optional[BlueprintParameters]
    RoleArn: Optional[OrchestrationIAMRoleArn]


BlueprintRuns = List[BlueprintRun]


class BooleanColumnStatisticsData(TypedDict, total=False):
    """Defines column statistics supported for Boolean data columns."""

    NumberOfTrues: NonNegativeLong
    NumberOfFalses: NonNegativeLong
    NumberOfNulls: NonNegativeLong


class CancelMLTaskRunRequest(ServiceRequest):
    TransformId: HashString
    TaskRunId: HashString


class CancelMLTaskRunResponse(TypedDict, total=False):
    TransformId: Optional[HashString]
    TaskRunId: Optional[HashString]
    Status: Optional[TaskStatusType]


class CancelStatementRequest(ServiceRequest):
    SessionId: NameString
    Id: IntegerValue
    RequestOrigin: Optional[OrchestrationNameString]


class CancelStatementResponse(TypedDict, total=False):
    pass


class CatalogEntry(TypedDict, total=False):
    """Specifies a table definition in the Glue Data Catalog."""

    DatabaseName: NameString
    TableName: NameString


CatalogEntries = List[CatalogEntry]


class CatalogImportStatus(TypedDict, total=False):
    """A structure containing migration status information."""

    ImportCompleted: Optional[Boolean]
    ImportTime: Optional[Timestamp]
    ImportedBy: Optional[NameString]


class CheckSchemaVersionValidityInput(ServiceRequest):
    DataFormat: DataFormat
    SchemaDefinition: SchemaDefinitionString


class CheckSchemaVersionValidityResponse(TypedDict, total=False):
    Valid: Optional[IsVersionValid]
    Error: Optional[SchemaValidationError]


CsvHeader = List[NameString]


class CsvClassifier(TypedDict, total=False):
    """A classifier for custom ``CSV`` content."""

    Name: NameString
    CreationTime: Optional[Timestamp]
    LastUpdated: Optional[Timestamp]
    Version: Optional[VersionId]
    Delimiter: Optional[CsvColumnDelimiter]
    QuoteSymbol: Optional[CsvQuoteSymbol]
    ContainsHeader: Optional[CsvHeaderOption]
    Header: Optional[CsvHeader]
    DisableValueTrimming: Optional[NullableBoolean]
    AllowSingleColumn: Optional[NullableBoolean]


class JsonClassifier(TypedDict, total=False):
    """A classifier for ``JSON`` content."""

    Name: NameString
    CreationTime: Optional[Timestamp]
    LastUpdated: Optional[Timestamp]
    Version: Optional[VersionId]
    JsonPath: JsonPath


class XMLClassifier(TypedDict, total=False):
    """A classifier for ``XML`` content."""

    Name: NameString
    Classification: Classification
    CreationTime: Optional[Timestamp]
    LastUpdated: Optional[Timestamp]
    Version: Optional[VersionId]
    RowTag: Optional[RowTag]


class GrokClassifier(TypedDict, total=False):
    """A classifier that uses ``grok`` patterns."""

    Name: NameString
    Classification: Classification
    CreationTime: Optional[Timestamp]
    LastUpdated: Optional[Timestamp]
    Version: Optional[VersionId]
    GrokPattern: GrokPattern
    CustomPatterns: Optional[CustomPatterns]


class Classifier(TypedDict, total=False):
    """Classifiers are triggered during a crawl task. A classifier checks
    whether a given file is in a format it can handle. If it is, the
    classifier creates a schema in the form of a ``StructType`` object that
    matches that data format.

    You can use the standard classifiers that Glue provides, or you can
    write your own classifiers to best categorize your data sources and
    specify the appropriate schemas to use for them. A classifier can be a
    ``grok`` classifier, an ``XML`` classifier, a ``JSON`` classifier, or a
    custom ``CSV`` classifier, as specified in one of the fields in the
    ``Classifier`` object.
    """

    GrokClassifier: Optional[GrokClassifier]
    XMLClassifier: Optional[XMLClassifier]
    JsonClassifier: Optional[JsonClassifier]
    CsvClassifier: Optional[CsvClassifier]


ClassifierList = List[Classifier]


class CloudWatchEncryption(TypedDict, total=False):
    """Specifies how Amazon CloudWatch data should be encrypted."""

    CloudWatchEncryptionMode: Optional[CloudWatchEncryptionMode]
    KmsKeyArn: Optional[KmsKeyArn]


class CodeGenEdge(TypedDict, total=False):
    """Represents a directional edge in a directed acyclic graph (DAG)."""

    Source: CodeGenIdentifier
    Target: CodeGenIdentifier
    TargetParameter: Optional[CodeGenArgName]


class CodeGenNodeArg(TypedDict, total=False):
    """An argument or property of a node."""

    Name: CodeGenArgName
    Value: CodeGenArgValue
    Param: Optional[Boolean]


CodeGenNodeArgs = List[CodeGenNodeArg]


class CodeGenNode(TypedDict, total=False):
    """Represents a node in a directed acyclic graph (DAG)"""

    Id: CodeGenIdentifier
    NodeType: CodeGenNodeType
    Args: CodeGenNodeArgs
    LineNumber: Optional[Integer]


class ColumnError(TypedDict, total=False):
    """Encapsulates a column name that failed and the reason for failure."""

    ColumnName: Optional[NameString]
    Error: Optional[ErrorDetail]


ColumnErrors = List[ColumnError]


class ColumnImportance(TypedDict, total=False):
    """A structure containing the column name and column importance score for a
    column.

    Column importance helps you understand how columns contribute to your
    model, by identifying which columns in your records are more important
    than others.
    """

    ColumnName: Optional[NameString]
    Importance: Optional[GenericBoundedDouble]


ColumnImportanceList = List[ColumnImportance]


class ColumnRowFilter(TypedDict, total=False):
    ColumnName: Optional[NameString]
    RowFilterExpression: Optional[PredicateString]


ColumnRowFilterList = List[ColumnRowFilter]


class StringColumnStatisticsData(TypedDict, total=False):
    """Defines column statistics supported for character sequence data values."""

    MaximumLength: NonNegativeLong
    AverageLength: NonNegativeDouble
    NumberOfNulls: NonNegativeLong
    NumberOfDistinctValues: NonNegativeLong


Long = int


class LongColumnStatisticsData(TypedDict, total=False):
    """Defines column statistics supported for integer data columns."""

    MinimumValue: Optional[Long]
    MaximumValue: Optional[Long]
    NumberOfNulls: NonNegativeLong
    NumberOfDistinctValues: NonNegativeLong


class DoubleColumnStatisticsData(TypedDict, total=False):
    """Defines column statistics supported for floating-point number data
    columns.
    """

    MinimumValue: Optional[Double]
    MaximumValue: Optional[Double]
    NumberOfNulls: NonNegativeLong
    NumberOfDistinctValues: NonNegativeLong


class DecimalNumber(TypedDict, total=False):
    """Contains a numeric value in decimal format."""

    UnscaledValue: Blob
    Scale: Integer


class DecimalColumnStatisticsData(TypedDict, total=False):
    """Defines column statistics supported for fixed-point number data columns."""

    MinimumValue: Optional[DecimalNumber]
    MaximumValue: Optional[DecimalNumber]
    NumberOfNulls: NonNegativeLong
    NumberOfDistinctValues: NonNegativeLong


class DateColumnStatisticsData(TypedDict, total=False):
    """Defines column statistics supported for timestamp data columns."""

    MinimumValue: Optional[Timestamp]
    MaximumValue: Optional[Timestamp]
    NumberOfNulls: NonNegativeLong
    NumberOfDistinctValues: NonNegativeLong


class ColumnStatisticsData(TypedDict, total=False):
    """Contains the individual types of column statistics data. Only one data
    object should be set and indicated by the ``Type`` attribute.
    """

    Type: ColumnStatisticsType
    BooleanColumnStatisticsData: Optional[BooleanColumnStatisticsData]
    DateColumnStatisticsData: Optional[DateColumnStatisticsData]
    DecimalColumnStatisticsData: Optional[DecimalColumnStatisticsData]
    DoubleColumnStatisticsData: Optional[DoubleColumnStatisticsData]
    LongColumnStatisticsData: Optional[LongColumnStatisticsData]
    StringColumnStatisticsData: Optional[StringColumnStatisticsData]
    BinaryColumnStatisticsData: Optional[BinaryColumnStatisticsData]


class ColumnStatistics(TypedDict, total=False):
    """Represents the generated column-level statistics for a table or
    partition.
    """

    ColumnName: NameString
    ColumnType: TypeString
    AnalyzedTime: Timestamp
    StatisticsData: ColumnStatisticsData


class ColumnStatisticsError(TypedDict, total=False):
    """Encapsulates a ``ColumnStatistics`` object that failed and the reason
    for failure.
    """

    ColumnStatistics: Optional[ColumnStatistics]
    Error: Optional[ErrorDetail]


ColumnStatisticsErrors = List[ColumnStatisticsError]
ColumnStatisticsList = List[ColumnStatistics]
RecordsCount = int


class ConfusionMatrix(TypedDict, total=False):
    """The confusion matrix shows you what your transform is predicting
    accurately and what types of errors it is making.

    For more information, see `Confusion
    matrix <https://en.wikipedia.org/wiki/Confusion_matrix>`__ in Wikipedia.
    """

    NumTruePositives: Optional[RecordsCount]
    NumFalsePositives: Optional[RecordsCount]
    NumTrueNegatives: Optional[RecordsCount]
    NumFalseNegatives: Optional[RecordsCount]


SecurityGroupIdList = List[NameString]


class PhysicalConnectionRequirements(TypedDict, total=False):
    """Specifies the physical requirements for a connection."""

    SubnetId: Optional[NameString]
    SecurityGroupIdList: Optional[SecurityGroupIdList]
    AvailabilityZone: Optional[NameString]


ConnectionProperties = Dict[ConnectionPropertyKey, ValueString]
MatchCriteria = List[NameString]


class Connection(TypedDict, total=False):
    """Defines a connection to a data source."""

    Name: Optional[NameString]
    Description: Optional[DescriptionString]
    ConnectionType: Optional[ConnectionType]
    MatchCriteria: Optional[MatchCriteria]
    ConnectionProperties: Optional[ConnectionProperties]
    PhysicalConnectionRequirements: Optional[PhysicalConnectionRequirements]
    CreationTime: Optional[Timestamp]
    LastUpdatedTime: Optional[Timestamp]
    LastUpdatedBy: Optional[NameString]


class ConnectionInput(TypedDict, total=False):
    """A structure that is used to specify a connection to create or update."""

    Name: NameString
    Description: Optional[DescriptionString]
    ConnectionType: ConnectionType
    MatchCriteria: Optional[MatchCriteria]
    ConnectionProperties: ConnectionProperties
    PhysicalConnectionRequirements: Optional[PhysicalConnectionRequirements]


ConnectionList = List[Connection]


class ConnectionPasswordEncryption(TypedDict, total=False):
    """The data structure used by the Data Catalog to encrypt the password as
    part of ``CreateConnection`` or ``UpdateConnection`` and store it in the
    ``ENCRYPTED_PASSWORD`` field in the connection properties. You can
    enable catalog encryption or only password encryption.

    When a ``CreationConnection`` request arrives containing a password, the
    Data Catalog first encrypts the password using your KMS key. It then
    encrypts the whole connection object again if catalog encryption is also
    enabled.

    This encryption requires that you set KMS key permissions to enable or
    restrict access on the password key according to your security
    requirements. For example, you might want only administrators to have
    decrypt permission on the password key.
    """

    ReturnConnectionPasswordEncrypted: Boolean
    AwsKmsKeyId: Optional[NameString]


class CrawlerMetrics(TypedDict, total=False):
    """Metrics for a specified crawler."""

    CrawlerName: Optional[NameString]
    TimeLeftSeconds: Optional[NonNegativeDouble]
    StillEstimating: Optional[Boolean]
    LastRuntimeSeconds: Optional[NonNegativeDouble]
    MedianRuntimeSeconds: Optional[NonNegativeDouble]
    TablesCreated: Optional[NonNegativeInteger]
    TablesUpdated: Optional[NonNegativeInteger]
    TablesDeleted: Optional[NonNegativeInteger]


CrawlerMetricsList = List[CrawlerMetrics]
TagsMap = Dict[TagKey, TagValue]


class CreateBlueprintRequest(ServiceRequest):
    Name: OrchestrationNameString
    Description: Optional[Generic512CharString]
    BlueprintLocation: OrchestrationS3Location
    Tags: Optional[TagsMap]


class CreateBlueprintResponse(TypedDict, total=False):
    Name: Optional[NameString]


class CreateCsvClassifierRequest(TypedDict, total=False):
    """Specifies a custom CSV classifier for ``CreateClassifier`` to create."""

    Name: NameString
    Delimiter: Optional[CsvColumnDelimiter]
    QuoteSymbol: Optional[CsvQuoteSymbol]
    ContainsHeader: Optional[CsvHeaderOption]
    Header: Optional[CsvHeader]
    DisableValueTrimming: Optional[NullableBoolean]
    AllowSingleColumn: Optional[NullableBoolean]


class CreateJsonClassifierRequest(TypedDict, total=False):
    """Specifies a JSON classifier for ``CreateClassifier`` to create."""

    Name: NameString
    JsonPath: JsonPath


class CreateXMLClassifierRequest(TypedDict, total=False):
    """Specifies an XML classifier for ``CreateClassifier`` to create."""

    Classification: Classification
    Name: NameString
    RowTag: Optional[RowTag]


class CreateGrokClassifierRequest(TypedDict, total=False):
    """Specifies a ``grok`` classifier for ``CreateClassifier`` to create."""

    Classification: Classification
    Name: NameString
    GrokPattern: GrokPattern
    CustomPatterns: Optional[CustomPatterns]


class CreateClassifierRequest(ServiceRequest):
    GrokClassifier: Optional[CreateGrokClassifierRequest]
    XMLClassifier: Optional[CreateXMLClassifierRequest]
    JsonClassifier: Optional[CreateJsonClassifierRequest]
    CsvClassifier: Optional[CreateCsvClassifierRequest]


class CreateClassifierResponse(TypedDict, total=False):
    pass


class CreateConnectionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    ConnectionInput: ConnectionInput
    Tags: Optional[TagsMap]


class CreateConnectionResponse(TypedDict, total=False):
    pass


class CreateCrawlerRequest(ServiceRequest):
    Name: NameString
    Role: Role
    DatabaseName: Optional[DatabaseName]
    Description: Optional[DescriptionString]
    Targets: CrawlerTargets
    Schedule: Optional[CronExpression]
    Classifiers: Optional[ClassifierNameList]
    TablePrefix: Optional[TablePrefix]
    SchemaChangePolicy: Optional[SchemaChangePolicy]
    RecrawlPolicy: Optional[RecrawlPolicy]
    LineageConfiguration: Optional[LineageConfiguration]
    LakeFormationConfiguration: Optional[LakeFormationConfiguration]
    Configuration: Optional[CrawlerConfiguration]
    CrawlerSecurityConfiguration: Optional[CrawlerSecurityConfiguration]
    Tags: Optional[TagsMap]


class CreateCrawlerResponse(TypedDict, total=False):
    pass


class CreateCustomEntityTypeRequest(ServiceRequest):
    Name: NameString
    RegexString: NameString
    ContextWords: Optional[ContextWords]


class CreateCustomEntityTypeResponse(TypedDict, total=False):
    Name: Optional[NameString]


class DatabaseIdentifier(TypedDict, total=False):
    """A structure that describes a target database for resource linking."""

    CatalogId: Optional[CatalogIdString]
    DatabaseName: Optional[NameString]


PermissionList = List[Permission]


class DataLakePrincipal(TypedDict, total=False):
    """The Lake Formation principal."""

    DataLakePrincipalIdentifier: Optional[DataLakePrincipalString]


class PrincipalPermissions(TypedDict, total=False):
    """Permissions granted to a principal."""

    Principal: Optional[DataLakePrincipal]
    Permissions: Optional[PermissionList]


PrincipalPermissionsList = List[PrincipalPermissions]


class DatabaseInput(TypedDict, total=False):
    """The structure used to create or update a database."""

    Name: NameString
    Description: Optional[DescriptionString]
    LocationUri: Optional[URI]
    Parameters: Optional[ParametersMap]
    CreateTableDefaultPermissions: Optional[PrincipalPermissionsList]
    TargetDatabase: Optional[DatabaseIdentifier]


class CreateDatabaseRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseInput: DatabaseInput


class CreateDatabaseResponse(TypedDict, total=False):
    pass


class CreateDevEndpointRequest(ServiceRequest):
    EndpointName: GenericString
    RoleArn: RoleArn
    SecurityGroupIds: Optional[StringList]
    SubnetId: Optional[GenericString]
    PublicKey: Optional[GenericString]
    PublicKeys: Optional[PublicKeysList]
    NumberOfNodes: Optional[IntegerValue]
    WorkerType: Optional[WorkerType]
    GlueVersion: Optional[GlueVersionString]
    NumberOfWorkers: Optional[NullableInteger]
    ExtraPythonLibsS3Path: Optional[GenericString]
    ExtraJarsS3Path: Optional[GenericString]
    SecurityConfiguration: Optional[NameString]
    Tags: Optional[TagsMap]
    Arguments: Optional[MapValue]


class CreateDevEndpointResponse(TypedDict, total=False):
    EndpointName: Optional[GenericString]
    Status: Optional[GenericString]
    SecurityGroupIds: Optional[StringList]
    SubnetId: Optional[GenericString]
    RoleArn: Optional[RoleArn]
    YarnEndpointAddress: Optional[GenericString]
    ZeppelinRemoteSparkInterpreterPort: Optional[IntegerValue]
    NumberOfNodes: Optional[IntegerValue]
    WorkerType: Optional[WorkerType]
    GlueVersion: Optional[GlueVersionString]
    NumberOfWorkers: Optional[NullableInteger]
    AvailabilityZone: Optional[GenericString]
    VpcId: Optional[GenericString]
    ExtraPythonLibsS3Path: Optional[GenericString]
    ExtraJarsS3Path: Optional[GenericString]
    FailureReason: Optional[GenericString]
    SecurityConfiguration: Optional[NameString]
    CreatedTimestamp: Optional[TimestampValue]
    Arguments: Optional[MapValue]


class CreateJobRequest(ServiceRequest):
    Name: NameString
    Description: Optional[DescriptionString]
    LogUri: Optional[UriString]
    Role: RoleString
    ExecutionProperty: Optional[ExecutionProperty]
    Command: JobCommand
    DefaultArguments: Optional[GenericMap]
    NonOverridableArguments: Optional[GenericMap]
    Connections: Optional[ConnectionsList]
    MaxRetries: Optional[MaxRetries]
    AllocatedCapacity: Optional[IntegerValue]
    Timeout: Optional[Timeout]
    MaxCapacity: Optional[NullableDouble]
    SecurityConfiguration: Optional[NameString]
    Tags: Optional[TagsMap]
    NotificationProperty: Optional[NotificationProperty]
    GlueVersion: Optional[GlueVersionString]
    NumberOfWorkers: Optional[NullableInteger]
    WorkerType: Optional[WorkerType]


class CreateJobResponse(TypedDict, total=False):
    Name: Optional[NameString]


class MLUserDataEncryption(TypedDict, total=False):
    """The encryption-at-rest settings of the transform that apply to accessing
    user data.
    """

    MlUserDataEncryptionMode: MLUserDataEncryptionModeString
    KmsKeyId: Optional[NameString]


class TransformEncryption(TypedDict, total=False):
    """The encryption-at-rest settings of the transform that apply to accessing
    user data. Machine learning transforms can access user data encrypted in
    Amazon S3 using KMS.

    Additionally, imported labels and trained transforms can now be
    encrypted using a customer provided KMS key.
    """

    MlUserDataEncryption: Optional[MLUserDataEncryption]
    TaskRunSecurityConfigurationName: Optional[NameString]


class FindMatchesParameters(TypedDict, total=False):
    """The parameters to configure the find matches transform."""

    PrimaryKeyColumnName: Optional[ColumnNameString]
    PrecisionRecallTradeoff: Optional[GenericBoundedDouble]
    AccuracyCostTradeoff: Optional[GenericBoundedDouble]
    EnforceProvidedLabels: Optional[NullableBoolean]


class TransformParameters(TypedDict, total=False):
    """The algorithm-specific parameters that are associated with the machine
    learning transform.
    """

    TransformType: TransformType
    FindMatchesParameters: Optional[FindMatchesParameters]


class GlueTable(TypedDict, total=False):
    """The database and table in the Glue Data Catalog that is used for input
    or output data.
    """

    DatabaseName: NameString
    TableName: NameString
    CatalogId: Optional[NameString]
    ConnectionName: Optional[NameString]


GlueTables = List[GlueTable]


class CreateMLTransformRequest(ServiceRequest):
    Name: NameString
    Description: Optional[DescriptionString]
    InputRecordTables: GlueTables
    Parameters: TransformParameters
    Role: RoleString
    GlueVersion: Optional[GlueVersionString]
    MaxCapacity: Optional[NullableDouble]
    WorkerType: Optional[WorkerType]
    NumberOfWorkers: Optional[NullableInteger]
    Timeout: Optional[Timeout]
    MaxRetries: Optional[NullableInteger]
    Tags: Optional[TagsMap]
    TransformEncryption: Optional[TransformEncryption]


class CreateMLTransformResponse(TypedDict, total=False):
    TransformId: Optional[HashString]


KeyList = List[NameString]


class PartitionIndex(TypedDict, total=False):
    """A structure for a partition index."""

    Keys: KeyList
    IndexName: NameString


class CreatePartitionIndexRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionIndex: PartitionIndex


class CreatePartitionIndexResponse(TypedDict, total=False):
    pass


class CreatePartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionInput: PartitionInput


class CreatePartitionResponse(TypedDict, total=False):
    pass


class CreateRegistryInput(ServiceRequest):
    RegistryName: SchemaRegistryNameString
    Description: Optional[DescriptionString]
    Tags: Optional[TagsMap]


class CreateRegistryResponse(TypedDict, total=False):
    RegistryArn: Optional[GlueResourceArn]
    RegistryName: Optional[SchemaRegistryNameString]
    Description: Optional[DescriptionString]
    Tags: Optional[TagsMap]


class RegistryId(TypedDict, total=False):
    """A wrapper structure that may contain the registry name and Amazon
    Resource Name (ARN).
    """

    RegistryName: Optional[SchemaRegistryNameString]
    RegistryArn: Optional[GlueResourceArn]


class CreateSchemaInput(ServiceRequest):
    RegistryId: Optional[RegistryId]
    SchemaName: SchemaRegistryNameString
    DataFormat: DataFormat
    Compatibility: Optional[Compatibility]
    Description: Optional[DescriptionString]
    Tags: Optional[TagsMap]
    SchemaDefinition: Optional[SchemaDefinitionString]


SchemaCheckpointNumber = int


class CreateSchemaResponse(TypedDict, total=False):
    RegistryName: Optional[SchemaRegistryNameString]
    RegistryArn: Optional[GlueResourceArn]
    SchemaName: Optional[SchemaRegistryNameString]
    SchemaArn: Optional[GlueResourceArn]
    Description: Optional[DescriptionString]
    DataFormat: Optional[DataFormat]
    Compatibility: Optional[Compatibility]
    SchemaCheckpoint: Optional[SchemaCheckpointNumber]
    LatestSchemaVersion: Optional[VersionLongNumber]
    NextSchemaVersion: Optional[VersionLongNumber]
    SchemaStatus: Optional[SchemaStatus]
    Tags: Optional[TagsMap]
    SchemaVersionId: Optional[SchemaVersionIdString]
    SchemaVersionStatus: Optional[SchemaVersionStatus]


DagEdges = List[CodeGenEdge]
DagNodes = List[CodeGenNode]


class CreateScriptRequest(ServiceRequest):
    DagNodes: Optional[DagNodes]
    DagEdges: Optional[DagEdges]
    Language: Optional[Language]


class CreateScriptResponse(TypedDict, total=False):
    PythonScript: Optional[PythonScript]
    ScalaCode: Optional[ScalaCode]


class JobBookmarksEncryption(TypedDict, total=False):
    """Specifies how job bookmark data should be encrypted."""

    JobBookmarksEncryptionMode: Optional[JobBookmarksEncryptionMode]
    KmsKeyArn: Optional[KmsKeyArn]


class S3Encryption(TypedDict, total=False):
    """Specifies how Amazon Simple Storage Service (Amazon S3) data should be
    encrypted.
    """

    S3EncryptionMode: Optional[S3EncryptionMode]
    KmsKeyArn: Optional[KmsKeyArn]


S3EncryptionList = List[S3Encryption]


class EncryptionConfiguration(TypedDict, total=False):
    """Specifies an encryption configuration."""

    S3Encryption: Optional[S3EncryptionList]
    CloudWatchEncryption: Optional[CloudWatchEncryption]
    JobBookmarksEncryption: Optional[JobBookmarksEncryption]


class CreateSecurityConfigurationRequest(ServiceRequest):
    Name: NameString
    EncryptionConfiguration: EncryptionConfiguration


class CreateSecurityConfigurationResponse(TypedDict, total=False):
    Name: Optional[NameString]
    CreatedTimestamp: Optional[TimestampValue]


OrchestrationArgumentsMap = Dict[OrchestrationNameString, OrchestrationArgumentsValue]


class SessionCommand(TypedDict, total=False):
    """The ``SessionCommand`` that runs the job."""

    Name: Optional[NameString]
    PythonVersion: Optional[PythonVersionString]


class CreateSessionRequest(ServiceRequest):
    """Request to create a new session."""

    Id: NameString
    Description: Optional[DescriptionString]
    Role: OrchestrationRoleArn
    Command: SessionCommand
    Timeout: Optional[Timeout]
    IdleTimeout: Optional[Timeout]
    DefaultArguments: Optional[OrchestrationArgumentsMap]
    Connections: Optional[ConnectionsList]
    MaxCapacity: Optional[NullableDouble]
    NumberOfWorkers: Optional[NullableInteger]
    WorkerType: Optional[WorkerType]
    SecurityConfiguration: Optional[NameString]
    GlueVersion: Optional[GlueVersionString]
    Tags: Optional[TagsMap]
    RequestOrigin: Optional[OrchestrationNameString]


class Session(TypedDict, total=False):
    """The period in which a remote Spark runtime environment is running."""

    Id: Optional[NameString]
    CreatedOn: Optional[TimestampValue]
    Status: Optional[SessionStatus]
    ErrorMessage: Optional[DescriptionString]
    Description: Optional[DescriptionString]
    Role: Optional[OrchestrationRoleArn]
    Command: Optional[SessionCommand]
    DefaultArguments: Optional[OrchestrationArgumentsMap]
    Connections: Optional[ConnectionsList]
    Progress: Optional[DoubleValue]
    MaxCapacity: Optional[NullableDouble]
    SecurityConfiguration: Optional[NameString]
    GlueVersion: Optional[GlueVersionString]


class CreateSessionResponse(TypedDict, total=False):
    Session: Optional[Session]


PartitionIndexList = List[PartitionIndex]


class TableIdentifier(TypedDict, total=False):
    """A structure that describes a target table for resource linking."""

    CatalogId: Optional[CatalogIdString]
    DatabaseName: Optional[NameString]
    Name: Optional[NameString]


class TableInput(TypedDict, total=False):
    """A structure used to define a table."""

    Name: NameString
    Description: Optional[DescriptionString]
    Owner: Optional[NameString]
    LastAccessTime: Optional[Timestamp]
    LastAnalyzedTime: Optional[Timestamp]
    Retention: Optional[NonNegativeInteger]
    StorageDescriptor: Optional[StorageDescriptor]
    PartitionKeys: Optional[ColumnList]
    ViewOriginalText: Optional[ViewTextString]
    ViewExpandedText: Optional[ViewTextString]
    TableType: Optional[TableTypeString]
    Parameters: Optional[ParametersMap]
    TargetTable: Optional[TableIdentifier]


class CreateTableRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableInput: TableInput
    PartitionIndexes: Optional[PartitionIndexList]
    TransactionId: Optional[TransactionIdString]


class CreateTableResponse(TypedDict, total=False):
    pass


class CreateTriggerRequest(ServiceRequest):
    Name: NameString
    WorkflowName: Optional[NameString]
    Type: TriggerType
    Schedule: Optional[GenericString]
    Predicate: Optional[Predicate]
    Actions: ActionList
    Description: Optional[DescriptionString]
    StartOnCreation: Optional[BooleanValue]
    Tags: Optional[TagsMap]
    EventBatchingCondition: Optional[EventBatchingCondition]


class CreateTriggerResponse(TypedDict, total=False):
    Name: Optional[NameString]


class ResourceUri(TypedDict, total=False):
    """The URIs for function resources."""

    ResourceType: Optional[ResourceType]
    Uri: Optional[URI]


ResourceUriList = List[ResourceUri]


class UserDefinedFunctionInput(TypedDict, total=False):
    """A structure used to create or update a user-defined function."""

    FunctionName: Optional[NameString]
    ClassName: Optional[NameString]
    OwnerName: Optional[NameString]
    OwnerType: Optional[PrincipalType]
    ResourceUris: Optional[ResourceUriList]


class CreateUserDefinedFunctionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    FunctionInput: UserDefinedFunctionInput


class CreateUserDefinedFunctionResponse(TypedDict, total=False):
    pass


class CreateWorkflowRequest(ServiceRequest):
    Name: NameString
    Description: Optional[GenericString]
    DefaultRunProperties: Optional[WorkflowRunProperties]
    Tags: Optional[TagsMap]
    MaxConcurrentRuns: Optional[NullableInteger]


class CreateWorkflowResponse(TypedDict, total=False):
    Name: Optional[NameString]


class EncryptionAtRest(TypedDict, total=False):
    """Specifies the encryption-at-rest configuration for the Data Catalog."""

    CatalogEncryptionMode: CatalogEncryptionMode
    SseAwsKmsKeyId: Optional[NameString]


class DataCatalogEncryptionSettings(TypedDict, total=False):
    """Contains configuration information for maintaining Data Catalog
    security.
    """

    EncryptionAtRest: Optional[EncryptionAtRest]
    ConnectionPasswordEncryption: Optional[ConnectionPasswordEncryption]


class Database(TypedDict, total=False):
    """The ``Database`` object represents a logical grouping of tables that
    might reside in a Hive metastore or an RDBMS.
    """

    Name: NameString
    Description: Optional[DescriptionString]
    LocationUri: Optional[URI]
    Parameters: Optional[ParametersMap]
    CreateTime: Optional[Timestamp]
    CreateTableDefaultPermissions: Optional[PrincipalPermissionsList]
    TargetDatabase: Optional[DatabaseIdentifier]
    CatalogId: Optional[CatalogIdString]


DatabaseList = List[Database]


class DeleteBlueprintRequest(ServiceRequest):
    Name: NameString


class DeleteBlueprintResponse(TypedDict, total=False):
    Name: Optional[NameString]


class DeleteClassifierRequest(ServiceRequest):
    Name: NameString


class DeleteClassifierResponse(TypedDict, total=False):
    pass


class DeleteColumnStatisticsForPartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionValues: ValueStringList
    ColumnName: NameString


class DeleteColumnStatisticsForPartitionResponse(TypedDict, total=False):
    pass


class DeleteColumnStatisticsForTableRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    ColumnName: NameString


class DeleteColumnStatisticsForTableResponse(TypedDict, total=False):
    pass


class DeleteConnectionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    ConnectionName: NameString


class DeleteConnectionResponse(TypedDict, total=False):
    pass


class DeleteCrawlerRequest(ServiceRequest):
    Name: NameString


class DeleteCrawlerResponse(TypedDict, total=False):
    pass


class DeleteCustomEntityTypeRequest(ServiceRequest):
    Name: NameString


class DeleteCustomEntityTypeResponse(TypedDict, total=False):
    Name: Optional[NameString]


class DeleteDatabaseRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Name: NameString


class DeleteDatabaseResponse(TypedDict, total=False):
    pass


class DeleteDevEndpointRequest(ServiceRequest):
    EndpointName: GenericString


class DeleteDevEndpointResponse(TypedDict, total=False):
    pass


class DeleteJobRequest(ServiceRequest):
    JobName: NameString


class DeleteJobResponse(TypedDict, total=False):
    JobName: Optional[NameString]


class DeleteMLTransformRequest(ServiceRequest):
    TransformId: HashString


class DeleteMLTransformResponse(TypedDict, total=False):
    TransformId: Optional[HashString]


class DeletePartitionIndexRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    IndexName: NameString


class DeletePartitionIndexResponse(TypedDict, total=False):
    pass


class DeletePartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionValues: ValueStringList


class DeletePartitionResponse(TypedDict, total=False):
    pass


class DeleteRegistryInput(ServiceRequest):
    RegistryId: RegistryId


class DeleteRegistryResponse(TypedDict, total=False):
    RegistryName: Optional[SchemaRegistryNameString]
    RegistryArn: Optional[GlueResourceArn]
    Status: Optional[RegistryStatus]


class DeleteResourcePolicyRequest(ServiceRequest):
    PolicyHashCondition: Optional[HashString]
    ResourceArn: Optional[GlueResourceArn]


class DeleteResourcePolicyResponse(TypedDict, total=False):
    pass


class DeleteSchemaInput(ServiceRequest):
    SchemaId: SchemaId


class DeleteSchemaResponse(TypedDict, total=False):
    SchemaArn: Optional[GlueResourceArn]
    SchemaName: Optional[SchemaRegistryNameString]
    Status: Optional[SchemaStatus]


class DeleteSchemaVersionsInput(ServiceRequest):
    SchemaId: SchemaId
    Versions: VersionsString


class ErrorDetails(TypedDict, total=False):
    """An object containing error details."""

    ErrorCode: Optional[ErrorCodeString]
    ErrorMessage: Optional[ErrorMessageString]


class SchemaVersionErrorItem(TypedDict, total=False):
    """An object that contains the error details for an operation on a schema
    version.
    """

    VersionNumber: Optional[VersionLongNumber]
    ErrorDetails: Optional[ErrorDetails]


SchemaVersionErrorList = List[SchemaVersionErrorItem]


class DeleteSchemaVersionsResponse(TypedDict, total=False):
    SchemaVersionErrors: Optional[SchemaVersionErrorList]


class DeleteSecurityConfigurationRequest(ServiceRequest):
    Name: NameString


class DeleteSecurityConfigurationResponse(TypedDict, total=False):
    pass


class DeleteSessionRequest(ServiceRequest):
    Id: NameString
    RequestOrigin: Optional[OrchestrationNameString]


class DeleteSessionResponse(TypedDict, total=False):
    Id: Optional[NameString]


class DeleteTableRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    Name: NameString
    TransactionId: Optional[TransactionIdString]


class DeleteTableResponse(TypedDict, total=False):
    pass


class DeleteTableVersionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    VersionId: VersionString


class DeleteTableVersionResponse(TypedDict, total=False):
    pass


class DeleteTriggerRequest(ServiceRequest):
    Name: NameString


class DeleteTriggerResponse(TypedDict, total=False):
    Name: Optional[NameString]


class DeleteUserDefinedFunctionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    FunctionName: NameString


class DeleteUserDefinedFunctionResponse(TypedDict, total=False):
    pass


class DeleteWorkflowRequest(ServiceRequest):
    Name: NameString


class DeleteWorkflowResponse(TypedDict, total=False):
    Name: Optional[NameString]


class DevEndpointCustomLibraries(TypedDict, total=False):
    """Custom libraries to be loaded into a development endpoint."""

    ExtraPythonLibsS3Path: Optional[GenericString]
    ExtraJarsS3Path: Optional[GenericString]


DevEndpointNameList = List[NameString]


class FindMatchesMetrics(TypedDict, total=False):
    """The evaluation metrics for the find matches algorithm. The quality of
    your machine learning transform is measured by getting your transform to
    predict some matches and comparing the results to known matches from the
    same dataset. The quality metrics are based on a subset of your data, so
    they are not precise.
    """

    AreaUnderPRCurve: Optional[GenericBoundedDouble]
    Precision: Optional[GenericBoundedDouble]
    Recall: Optional[GenericBoundedDouble]
    F1: Optional[GenericBoundedDouble]
    ConfusionMatrix: Optional[ConfusionMatrix]
    ColumnImportances: Optional[ColumnImportanceList]


class EvaluationMetrics(TypedDict, total=False):
    """Evaluation metrics provide an estimate of the quality of your machine
    learning transform.
    """

    TransformType: TransformType
    FindMatchesMetrics: Optional[FindMatchesMetrics]


class ExportLabelsTaskRunProperties(TypedDict, total=False):
    """Specifies configuration properties for an exporting labels task run."""

    OutputS3Path: Optional[UriString]


class FindMatchesTaskRunProperties(TypedDict, total=False):
    """Specifies configuration properties for a Find Matches task run."""

    JobId: Optional[HashString]
    JobName: Optional[NameString]
    JobRunId: Optional[HashString]


class GetBlueprintRequest(ServiceRequest):
    Name: NameString
    IncludeBlueprint: Optional[NullableBoolean]
    IncludeParameterSpec: Optional[NullableBoolean]


class GetBlueprintResponse(TypedDict, total=False):
    Blueprint: Optional[Blueprint]


class GetBlueprintRunRequest(ServiceRequest):
    BlueprintName: OrchestrationNameString
    RunId: IdString


class GetBlueprintRunResponse(TypedDict, total=False):
    BlueprintRun: Optional[BlueprintRun]


class GetBlueprintRunsRequest(ServiceRequest):
    BlueprintName: NameString
    NextToken: Optional[GenericString]
    MaxResults: Optional[PageSize]


class GetBlueprintRunsResponse(TypedDict, total=False):
    BlueprintRuns: Optional[BlueprintRuns]
    NextToken: Optional[GenericString]


class GetCatalogImportStatusRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]


class GetCatalogImportStatusResponse(TypedDict, total=False):
    ImportStatus: Optional[CatalogImportStatus]


class GetClassifierRequest(ServiceRequest):
    Name: NameString


class GetClassifierResponse(TypedDict, total=False):
    Classifier: Optional[Classifier]


class GetClassifiersRequest(ServiceRequest):
    MaxResults: Optional[PageSize]
    NextToken: Optional[Token]


class GetClassifiersResponse(TypedDict, total=False):
    Classifiers: Optional[ClassifierList]
    NextToken: Optional[Token]


GetColumnNamesList = List[NameString]


class GetColumnStatisticsForPartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionValues: ValueStringList
    ColumnNames: GetColumnNamesList


class GetColumnStatisticsForPartitionResponse(TypedDict, total=False):
    ColumnStatisticsList: Optional[ColumnStatisticsList]
    Errors: Optional[ColumnErrors]


class GetColumnStatisticsForTableRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    ColumnNames: GetColumnNamesList


class GetColumnStatisticsForTableResponse(TypedDict, total=False):
    ColumnStatisticsList: Optional[ColumnStatisticsList]
    Errors: Optional[ColumnErrors]


class GetConnectionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Name: NameString
    HidePassword: Optional[Boolean]


class GetConnectionResponse(TypedDict, total=False):
    Connection: Optional[Connection]


class GetConnectionsFilter(TypedDict, total=False):
    """Filters the connection definitions that are returned by the
    ``GetConnections`` API operation.
    """

    MatchCriteria: Optional[MatchCriteria]
    ConnectionType: Optional[ConnectionType]


class GetConnectionsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Filter: Optional[GetConnectionsFilter]
    HidePassword: Optional[Boolean]
    NextToken: Optional[Token]
    MaxResults: Optional[PageSize]


class GetConnectionsResponse(TypedDict, total=False):
    ConnectionList: Optional[ConnectionList]
    NextToken: Optional[Token]


class GetCrawlerMetricsRequest(ServiceRequest):
    CrawlerNameList: Optional[CrawlerNameList]
    MaxResults: Optional[PageSize]
    NextToken: Optional[Token]


class GetCrawlerMetricsResponse(TypedDict, total=False):
    CrawlerMetricsList: Optional[CrawlerMetricsList]
    NextToken: Optional[Token]


class GetCrawlerRequest(ServiceRequest):
    Name: NameString


class GetCrawlerResponse(TypedDict, total=False):
    Crawler: Optional[Crawler]


class GetCrawlersRequest(ServiceRequest):
    MaxResults: Optional[PageSize]
    NextToken: Optional[Token]


class GetCrawlersResponse(TypedDict, total=False):
    Crawlers: Optional[CrawlerList]
    NextToken: Optional[Token]


class GetCustomEntityTypeRequest(ServiceRequest):
    Name: NameString


class GetCustomEntityTypeResponse(TypedDict, total=False):
    Name: Optional[NameString]
    RegexString: Optional[NameString]
    ContextWords: Optional[ContextWords]


class GetDataCatalogEncryptionSettingsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]


class GetDataCatalogEncryptionSettingsResponse(TypedDict, total=False):
    DataCatalogEncryptionSettings: Optional[DataCatalogEncryptionSettings]


class GetDatabaseRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Name: NameString


class GetDatabaseResponse(TypedDict, total=False):
    Database: Optional[Database]


class GetDatabasesRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    NextToken: Optional[Token]
    MaxResults: Optional[CatalogGetterPageSize]
    ResourceShareType: Optional[ResourceShareType]


class GetDatabasesResponse(TypedDict, total=False):
    DatabaseList: DatabaseList
    NextToken: Optional[Token]


class GetDataflowGraphRequest(ServiceRequest):
    PythonScript: Optional[PythonScript]


class GetDataflowGraphResponse(TypedDict, total=False):
    DagNodes: Optional[DagNodes]
    DagEdges: Optional[DagEdges]


class GetDevEndpointRequest(ServiceRequest):
    EndpointName: GenericString


class GetDevEndpointResponse(TypedDict, total=False):
    DevEndpoint: Optional[DevEndpoint]


class GetDevEndpointsRequest(ServiceRequest):
    MaxResults: Optional[PageSize]
    NextToken: Optional[GenericString]


class GetDevEndpointsResponse(TypedDict, total=False):
    DevEndpoints: Optional[DevEndpointList]
    NextToken: Optional[GenericString]


class GetJobBookmarkRequest(ServiceRequest):
    JobName: JobName
    RunId: Optional[RunId]


class JobBookmarkEntry(TypedDict, total=False):
    """Defines a point that a job can resume processing."""

    JobName: Optional[JobName]
    Version: Optional[IntegerValue]
    Run: Optional[IntegerValue]
    Attempt: Optional[IntegerValue]
    PreviousRunId: Optional[RunId]
    RunId: Optional[RunId]
    JobBookmark: Optional[JsonValue]


class GetJobBookmarkResponse(TypedDict, total=False):
    JobBookmarkEntry: Optional[JobBookmarkEntry]


class GetJobRequest(ServiceRequest):
    JobName: NameString


class GetJobResponse(TypedDict, total=False):
    Job: Optional[Job]


class GetJobRunRequest(ServiceRequest):
    JobName: NameString
    RunId: IdString
    PredecessorsIncluded: Optional[BooleanValue]


class GetJobRunResponse(TypedDict, total=False):
    JobRun: Optional[JobRun]


class GetJobRunsRequest(ServiceRequest):
    JobName: NameString
    NextToken: Optional[GenericString]
    MaxResults: Optional[PageSize]


class GetJobRunsResponse(TypedDict, total=False):
    JobRuns: Optional[JobRunList]
    NextToken: Optional[GenericString]


class GetJobsRequest(ServiceRequest):
    NextToken: Optional[GenericString]
    MaxResults: Optional[PageSize]


class GetJobsResponse(TypedDict, total=False):
    Jobs: Optional[JobList]
    NextToken: Optional[GenericString]


class GetMLTaskRunRequest(ServiceRequest):
    TransformId: HashString
    TaskRunId: HashString


class LabelingSetGenerationTaskRunProperties(TypedDict, total=False):
    """Specifies configuration properties for a labeling set generation task
    run.
    """

    OutputS3Path: Optional[UriString]


class ImportLabelsTaskRunProperties(TypedDict, total=False):
    """Specifies configuration properties for an importing labels task run."""

    InputS3Path: Optional[UriString]
    Replace: Optional[ReplaceBoolean]


class TaskRunProperties(TypedDict, total=False):
    """The configuration properties for the task run."""

    TaskType: Optional[TaskType]
    ImportLabelsTaskRunProperties: Optional[ImportLabelsTaskRunProperties]
    ExportLabelsTaskRunProperties: Optional[ExportLabelsTaskRunProperties]
    LabelingSetGenerationTaskRunProperties: Optional[LabelingSetGenerationTaskRunProperties]
    FindMatchesTaskRunProperties: Optional[FindMatchesTaskRunProperties]


class GetMLTaskRunResponse(TypedDict, total=False):
    TransformId: Optional[HashString]
    TaskRunId: Optional[HashString]
    Status: Optional[TaskStatusType]
    LogGroupName: Optional[GenericString]
    Properties: Optional[TaskRunProperties]
    ErrorString: Optional[GenericString]
    StartedOn: Optional[Timestamp]
    LastModifiedOn: Optional[Timestamp]
    CompletedOn: Optional[Timestamp]
    ExecutionTime: Optional[ExecutionTime]


class TaskRunSortCriteria(TypedDict, total=False):
    """The sorting criteria that are used to sort the list of task runs for the
    machine learning transform.
    """

    Column: TaskRunSortColumnType
    SortDirection: SortDirectionType


class TaskRunFilterCriteria(TypedDict, total=False):
    """The criteria that are used to filter the task runs for the machine
    learning transform.
    """

    TaskRunType: Optional[TaskType]
    Status: Optional[TaskStatusType]
    StartedBefore: Optional[Timestamp]
    StartedAfter: Optional[Timestamp]


class GetMLTaskRunsRequest(ServiceRequest):
    TransformId: HashString
    NextToken: Optional[PaginationToken]
    MaxResults: Optional[PageSize]
    Filter: Optional[TaskRunFilterCriteria]
    Sort: Optional[TaskRunSortCriteria]


class TaskRun(TypedDict, total=False):
    """The sampling parameters that are associated with the machine learning
    transform.
    """

    TransformId: Optional[HashString]
    TaskRunId: Optional[HashString]
    Status: Optional[TaskStatusType]
    LogGroupName: Optional[GenericString]
    Properties: Optional[TaskRunProperties]
    ErrorString: Optional[GenericString]
    StartedOn: Optional[Timestamp]
    LastModifiedOn: Optional[Timestamp]
    CompletedOn: Optional[Timestamp]
    ExecutionTime: Optional[ExecutionTime]


TaskRunList = List[TaskRun]


class GetMLTaskRunsResponse(TypedDict, total=False):
    TaskRuns: Optional[TaskRunList]
    NextToken: Optional[PaginationToken]


class GetMLTransformRequest(ServiceRequest):
    TransformId: HashString


class SchemaColumn(TypedDict, total=False):
    """A key-value pair representing a column and data type that this transform
    can run against. The ``Schema`` parameter of the ``MLTransform`` may
    contain up to 100 of these structures.
    """

    Name: Optional[ColumnNameString]
    DataType: Optional[ColumnTypeString]


TransformSchema = List[SchemaColumn]


class GetMLTransformResponse(TypedDict, total=False):
    TransformId: Optional[HashString]
    Name: Optional[NameString]
    Description: Optional[DescriptionString]
    Status: Optional[TransformStatusType]
    CreatedOn: Optional[Timestamp]
    LastModifiedOn: Optional[Timestamp]
    InputRecordTables: Optional[GlueTables]
    Parameters: Optional[TransformParameters]
    EvaluationMetrics: Optional[EvaluationMetrics]
    LabelCount: Optional[LabelCount]
    Schema: Optional[TransformSchema]
    Role: Optional[RoleString]
    GlueVersion: Optional[GlueVersionString]
    MaxCapacity: Optional[NullableDouble]
    WorkerType: Optional[WorkerType]
    NumberOfWorkers: Optional[NullableInteger]
    Timeout: Optional[Timeout]
    MaxRetries: Optional[NullableInteger]
    TransformEncryption: Optional[TransformEncryption]


class TransformSortCriteria(TypedDict, total=False):
    """The sorting criteria that are associated with the machine learning
    transform.
    """

    Column: TransformSortColumnType
    SortDirection: SortDirectionType


class TransformFilterCriteria(TypedDict, total=False):
    """The criteria used to filter the machine learning transforms."""

    Name: Optional[NameString]
    TransformType: Optional[TransformType]
    Status: Optional[TransformStatusType]
    GlueVersion: Optional[GlueVersionString]
    CreatedBefore: Optional[Timestamp]
    CreatedAfter: Optional[Timestamp]
    LastModifiedBefore: Optional[Timestamp]
    LastModifiedAfter: Optional[Timestamp]
    Schema: Optional[TransformSchema]


class GetMLTransformsRequest(ServiceRequest):
    NextToken: Optional[PaginationToken]
    MaxResults: Optional[PageSize]
    Filter: Optional[TransformFilterCriteria]
    Sort: Optional[TransformSortCriteria]


class MLTransform(TypedDict, total=False):
    """A structure for a machine learning transform."""

    TransformId: Optional[HashString]
    Name: Optional[NameString]
    Description: Optional[DescriptionString]
    Status: Optional[TransformStatusType]
    CreatedOn: Optional[Timestamp]
    LastModifiedOn: Optional[Timestamp]
    InputRecordTables: Optional[GlueTables]
    Parameters: Optional[TransformParameters]
    EvaluationMetrics: Optional[EvaluationMetrics]
    LabelCount: Optional[LabelCount]
    Schema: Optional[TransformSchema]
    Role: Optional[RoleString]
    GlueVersion: Optional[GlueVersionString]
    MaxCapacity: Optional[NullableDouble]
    WorkerType: Optional[WorkerType]
    NumberOfWorkers: Optional[NullableInteger]
    Timeout: Optional[Timeout]
    MaxRetries: Optional[NullableInteger]
    TransformEncryption: Optional[TransformEncryption]


TransformList = List[MLTransform]


class GetMLTransformsResponse(TypedDict, total=False):
    Transforms: TransformList
    NextToken: Optional[PaginationToken]


class Location(TypedDict, total=False):
    """The location of resources."""

    Jdbc: Optional[CodeGenNodeArgs]
    S3: Optional[CodeGenNodeArgs]
    DynamoDB: Optional[CodeGenNodeArgs]


class GetMappingRequest(ServiceRequest):
    Source: CatalogEntry
    Sinks: Optional[CatalogEntries]
    Location: Optional[Location]


class MappingEntry(TypedDict, total=False):
    """Defines a mapping."""

    SourceTable: Optional[TableName]
    SourcePath: Optional[SchemaPathString]
    SourceType: Optional[FieldType]
    TargetTable: Optional[TableName]
    TargetPath: Optional[SchemaPathString]
    TargetType: Optional[FieldType]


MappingList = List[MappingEntry]


class GetMappingResponse(TypedDict, total=False):
    Mapping: MappingList


class GetPartitionIndexesRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    NextToken: Optional[Token]


class KeySchemaElement(TypedDict, total=False):
    """A partition key pair consisting of a name and a type."""

    Name: NameString
    Type: ColumnTypeString


KeySchemaElementList = List[KeySchemaElement]


class PartitionIndexDescriptor(TypedDict, total=False):
    """A descriptor for a partition index in a table."""

    IndexName: NameString
    Keys: KeySchemaElementList
    IndexStatus: PartitionIndexStatus
    BackfillErrors: Optional[BackfillErrors]


PartitionIndexDescriptorList = List[PartitionIndexDescriptor]


class GetPartitionIndexesResponse(TypedDict, total=False):
    PartitionIndexDescriptorList: Optional[PartitionIndexDescriptorList]
    NextToken: Optional[Token]


class GetPartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionValues: ValueStringList


class GetPartitionResponse(TypedDict, total=False):
    Partition: Optional[Partition]


class Segment(TypedDict, total=False):
    """Defines a non-overlapping region of a table's partitions, allowing
    multiple requests to be run in parallel.
    """

    SegmentNumber: NonNegativeInteger
    TotalSegments: TotalSegmentsInteger


class GetPartitionsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    Expression: Optional[PredicateString]
    NextToken: Optional[Token]
    Segment: Optional[Segment]
    MaxResults: Optional[PageSize]
    ExcludeColumnSchema: Optional[BooleanNullable]
    TransactionId: Optional[TransactionIdString]
    QueryAsOfTime: Optional[Timestamp]


class GetPartitionsResponse(TypedDict, total=False):
    Partitions: Optional[PartitionList]
    NextToken: Optional[Token]


class GetPlanRequest(ServiceRequest):
    Mapping: MappingList
    Source: CatalogEntry
    Sinks: Optional[CatalogEntries]
    Location: Optional[Location]
    Language: Optional[Language]
    AdditionalPlanOptionsMap: Optional[AdditionalPlanOptionsMap]


class GetPlanResponse(TypedDict, total=False):
    PythonScript: Optional[PythonScript]
    ScalaCode: Optional[ScalaCode]


class GetRegistryInput(ServiceRequest):
    RegistryId: RegistryId


class GetRegistryResponse(TypedDict, total=False):
    RegistryName: Optional[SchemaRegistryNameString]
    RegistryArn: Optional[GlueResourceArn]
    Description: Optional[DescriptionString]
    Status: Optional[RegistryStatus]
    CreatedTime: Optional[CreatedTimestamp]
    UpdatedTime: Optional[UpdatedTimestamp]


class GetResourcePoliciesRequest(ServiceRequest):
    NextToken: Optional[Token]
    MaxResults: Optional[PageSize]


class GluePolicy(TypedDict, total=False):
    """A structure for returning a resource policy."""

    PolicyInJson: Optional[PolicyJsonString]
    PolicyHash: Optional[HashString]
    CreateTime: Optional[Timestamp]
    UpdateTime: Optional[Timestamp]


GetResourcePoliciesResponseList = List[GluePolicy]


class GetResourcePoliciesResponse(TypedDict, total=False):
    GetResourcePoliciesResponseList: Optional[GetResourcePoliciesResponseList]
    NextToken: Optional[Token]


class GetResourcePolicyRequest(ServiceRequest):
    ResourceArn: Optional[GlueResourceArn]


class GetResourcePolicyResponse(TypedDict, total=False):
    PolicyInJson: Optional[PolicyJsonString]
    PolicyHash: Optional[HashString]
    CreateTime: Optional[Timestamp]
    UpdateTime: Optional[Timestamp]


class GetSchemaByDefinitionInput(ServiceRequest):
    SchemaId: SchemaId
    SchemaDefinition: SchemaDefinitionString


class GetSchemaByDefinitionResponse(TypedDict, total=False):
    SchemaVersionId: Optional[SchemaVersionIdString]
    SchemaArn: Optional[GlueResourceArn]
    DataFormat: Optional[DataFormat]
    Status: Optional[SchemaVersionStatus]
    CreatedTime: Optional[CreatedTimestamp]


class GetSchemaInput(ServiceRequest):
    SchemaId: SchemaId


class GetSchemaResponse(TypedDict, total=False):
    RegistryName: Optional[SchemaRegistryNameString]
    RegistryArn: Optional[GlueResourceArn]
    SchemaName: Optional[SchemaRegistryNameString]
    SchemaArn: Optional[GlueResourceArn]
    Description: Optional[DescriptionString]
    DataFormat: Optional[DataFormat]
    Compatibility: Optional[Compatibility]
    SchemaCheckpoint: Optional[SchemaCheckpointNumber]
    LatestSchemaVersion: Optional[VersionLongNumber]
    NextSchemaVersion: Optional[VersionLongNumber]
    SchemaStatus: Optional[SchemaStatus]
    CreatedTime: Optional[CreatedTimestamp]
    UpdatedTime: Optional[UpdatedTimestamp]


class SchemaVersionNumber(TypedDict, total=False):
    """A structure containing the schema version information."""

    LatestVersion: Optional[LatestSchemaVersionBoolean]
    VersionNumber: Optional[VersionLongNumber]


class GetSchemaVersionInput(ServiceRequest):
    SchemaId: Optional[SchemaId]
    SchemaVersionId: Optional[SchemaVersionIdString]
    SchemaVersionNumber: Optional[SchemaVersionNumber]


class GetSchemaVersionResponse(TypedDict, total=False):
    SchemaVersionId: Optional[SchemaVersionIdString]
    SchemaDefinition: Optional[SchemaDefinitionString]
    DataFormat: Optional[DataFormat]
    SchemaArn: Optional[GlueResourceArn]
    VersionNumber: Optional[VersionLongNumber]
    Status: Optional[SchemaVersionStatus]
    CreatedTime: Optional[CreatedTimestamp]


class GetSchemaVersionsDiffInput(ServiceRequest):
    SchemaId: SchemaId
    FirstSchemaVersionNumber: SchemaVersionNumber
    SecondSchemaVersionNumber: SchemaVersionNumber
    SchemaDiffType: SchemaDiffType


class GetSchemaVersionsDiffResponse(TypedDict, total=False):
    Diff: Optional[SchemaDefinitionDiff]


class GetSecurityConfigurationRequest(ServiceRequest):
    Name: NameString


class SecurityConfiguration(TypedDict, total=False):
    """Specifies a security configuration."""

    Name: Optional[NameString]
    CreatedTimeStamp: Optional[TimestampValue]
    EncryptionConfiguration: Optional[EncryptionConfiguration]


class GetSecurityConfigurationResponse(TypedDict, total=False):
    SecurityConfiguration: Optional[SecurityConfiguration]


class GetSecurityConfigurationsRequest(ServiceRequest):
    MaxResults: Optional[PageSize]
    NextToken: Optional[GenericString]


SecurityConfigurationList = List[SecurityConfiguration]


class GetSecurityConfigurationsResponse(TypedDict, total=False):
    SecurityConfigurations: Optional[SecurityConfigurationList]
    NextToken: Optional[GenericString]


class GetSessionRequest(ServiceRequest):
    Id: NameString
    RequestOrigin: Optional[OrchestrationNameString]


class GetSessionResponse(TypedDict, total=False):
    Session: Optional[Session]


class GetStatementRequest(ServiceRequest):
    SessionId: NameString
    Id: IntegerValue
    RequestOrigin: Optional[OrchestrationNameString]


LongValue = int


class StatementOutputData(TypedDict, total=False):
    """The code execution output in JSON format."""

    TextPlain: Optional[GenericString]


class StatementOutput(TypedDict, total=False):
    """The code execution output in JSON format."""

    Data: Optional[StatementOutputData]
    ExecutionCount: Optional[IntegerValue]
    Status: Optional[StatementState]
    ErrorName: Optional[GenericString]
    ErrorValue: Optional[GenericString]
    Traceback: Optional[OrchestrationStringList]


class Statement(TypedDict, total=False):
    """The statement or request for a particular action to occur in a session."""

    Id: Optional[IntegerValue]
    Code: Optional[GenericString]
    State: Optional[StatementState]
    Output: Optional[StatementOutput]
    Progress: Optional[DoubleValue]
    StartedOn: Optional[LongValue]
    CompletedOn: Optional[LongValue]


class GetStatementResponse(TypedDict, total=False):
    Statement: Optional[Statement]


class GetTableRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    Name: NameString
    TransactionId: Optional[TransactionIdString]
    QueryAsOfTime: Optional[Timestamp]


class Table(TypedDict, total=False):
    """Represents a collection of related data organized in columns and rows."""

    Name: NameString
    DatabaseName: Optional[NameString]
    Description: Optional[DescriptionString]
    Owner: Optional[NameString]
    CreateTime: Optional[Timestamp]
    UpdateTime: Optional[Timestamp]
    LastAccessTime: Optional[Timestamp]
    LastAnalyzedTime: Optional[Timestamp]
    Retention: Optional[NonNegativeInteger]
    StorageDescriptor: Optional[StorageDescriptor]
    PartitionKeys: Optional[ColumnList]
    ViewOriginalText: Optional[ViewTextString]
    ViewExpandedText: Optional[ViewTextString]
    TableType: Optional[TableTypeString]
    Parameters: Optional[ParametersMap]
    CreatedBy: Optional[NameString]
    IsRegisteredWithLakeFormation: Optional[Boolean]
    TargetTable: Optional[TableIdentifier]
    CatalogId: Optional[CatalogIdString]
    VersionId: Optional[VersionString]


class GetTableResponse(TypedDict, total=False):
    Table: Optional[Table]


class GetTableVersionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    VersionId: Optional[VersionString]


class TableVersion(TypedDict, total=False):
    """Specifies a version of a table."""

    Table: Optional[Table]
    VersionId: Optional[VersionString]


class GetTableVersionResponse(TypedDict, total=False):
    TableVersion: Optional[TableVersion]


GetTableVersionsList = List[TableVersion]


class GetTableVersionsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    NextToken: Optional[Token]
    MaxResults: Optional[CatalogGetterPageSize]


class GetTableVersionsResponse(TypedDict, total=False):
    TableVersions: Optional[GetTableVersionsList]
    NextToken: Optional[Token]


class GetTablesRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    Expression: Optional[FilterString]
    NextToken: Optional[Token]
    MaxResults: Optional[CatalogGetterPageSize]
    TransactionId: Optional[TransactionIdString]
    QueryAsOfTime: Optional[Timestamp]


TableList = List[Table]


class GetTablesResponse(TypedDict, total=False):
    TableList: Optional[TableList]
    NextToken: Optional[Token]


class GetTagsRequest(ServiceRequest):
    ResourceArn: GlueResourceArn


class GetTagsResponse(TypedDict, total=False):
    Tags: Optional[TagsMap]


class GetTriggerRequest(ServiceRequest):
    Name: NameString


class GetTriggerResponse(TypedDict, total=False):
    Trigger: Optional[Trigger]


class GetTriggersRequest(ServiceRequest):
    NextToken: Optional[GenericString]
    DependentJobName: Optional[NameString]
    MaxResults: Optional[PageSize]


class GetTriggersResponse(TypedDict, total=False):
    Triggers: Optional[TriggerList]
    NextToken: Optional[GenericString]


PermissionTypeList = List[PermissionType]


class GetUnfilteredPartitionMetadataRequest(ServiceRequest):
    CatalogId: CatalogIdString
    DatabaseName: NameString
    TableName: NameString
    PartitionValues: ValueStringList
    AuditContext: Optional[AuditContext]
    SupportedPermissionTypes: PermissionTypeList


class GetUnfilteredPartitionMetadataResponse(TypedDict, total=False):
    Partition: Optional[Partition]
    AuthorizedColumns: Optional[NameStringList]
    IsRegisteredWithLakeFormation: Optional[Boolean]


class GetUnfilteredPartitionsMetadataRequest(ServiceRequest):
    CatalogId: CatalogIdString
    DatabaseName: NameString
    TableName: NameString
    Expression: Optional[PredicateString]
    AuditContext: Optional[AuditContext]
    SupportedPermissionTypes: PermissionTypeList
    NextToken: Optional[Token]
    Segment: Optional[Segment]
    MaxResults: Optional[PageSize]


class UnfilteredPartition(TypedDict, total=False):
    Partition: Optional[Partition]
    AuthorizedColumns: Optional[NameStringList]
    IsRegisteredWithLakeFormation: Optional[Boolean]


UnfilteredPartitionList = List[UnfilteredPartition]


class GetUnfilteredPartitionsMetadataResponse(TypedDict, total=False):
    UnfilteredPartitions: Optional[UnfilteredPartitionList]
    NextToken: Optional[Token]


class GetUnfilteredTableMetadataRequest(ServiceRequest):
    CatalogId: CatalogIdString
    DatabaseName: NameString
    Name: NameString
    AuditContext: Optional[AuditContext]
    SupportedPermissionTypes: PermissionTypeList


class GetUnfilteredTableMetadataResponse(TypedDict, total=False):
    Table: Optional[Table]
    AuthorizedColumns: Optional[NameStringList]
    IsRegisteredWithLakeFormation: Optional[Boolean]
    CellFilters: Optional[ColumnRowFilterList]


class GetUserDefinedFunctionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    FunctionName: NameString


class UserDefinedFunction(TypedDict, total=False):
    """Represents the equivalent of a Hive user-defined function (``UDF``)
    definition.
    """

    FunctionName: Optional[NameString]
    DatabaseName: Optional[NameString]
    ClassName: Optional[NameString]
    OwnerName: Optional[NameString]
    OwnerType: Optional[PrincipalType]
    CreateTime: Optional[Timestamp]
    ResourceUris: Optional[ResourceUriList]
    CatalogId: Optional[CatalogIdString]


class GetUserDefinedFunctionResponse(TypedDict, total=False):
    UserDefinedFunction: Optional[UserDefinedFunction]


class GetUserDefinedFunctionsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: Optional[NameString]
    Pattern: NameString
    NextToken: Optional[Token]
    MaxResults: Optional[CatalogGetterPageSize]


UserDefinedFunctionList = List[UserDefinedFunction]


class GetUserDefinedFunctionsResponse(TypedDict, total=False):
    UserDefinedFunctions: Optional[UserDefinedFunctionList]
    NextToken: Optional[Token]


class GetWorkflowRequest(ServiceRequest):
    Name: NameString
    IncludeGraph: Optional[NullableBoolean]


class GetWorkflowResponse(TypedDict, total=False):
    Workflow: Optional[Workflow]


class GetWorkflowRunPropertiesRequest(ServiceRequest):
    Name: NameString
    RunId: IdString


class GetWorkflowRunPropertiesResponse(TypedDict, total=False):
    RunProperties: Optional[WorkflowRunProperties]


class GetWorkflowRunRequest(ServiceRequest):
    Name: NameString
    RunId: IdString
    IncludeGraph: Optional[NullableBoolean]


class GetWorkflowRunResponse(TypedDict, total=False):
    Run: Optional[WorkflowRun]


class GetWorkflowRunsRequest(ServiceRequest):
    Name: NameString
    IncludeGraph: Optional[NullableBoolean]
    NextToken: Optional[GenericString]
    MaxResults: Optional[PageSize]


WorkflowRuns = List[WorkflowRun]


class GetWorkflowRunsResponse(TypedDict, total=False):
    Runs: Optional[WorkflowRuns]
    NextToken: Optional[GenericString]


class ImportCatalogToGlueRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]


class ImportCatalogToGlueResponse(TypedDict, total=False):
    pass


class JobUpdate(TypedDict, total=False):
    """Specifies information used to update an existing job definition. The
    previous job definition is completely overwritten by this information.
    """

    Description: Optional[DescriptionString]
    LogUri: Optional[UriString]
    Role: Optional[RoleString]
    ExecutionProperty: Optional[ExecutionProperty]
    Command: Optional[JobCommand]
    DefaultArguments: Optional[GenericMap]
    NonOverridableArguments: Optional[GenericMap]
    Connections: Optional[ConnectionsList]
    MaxRetries: Optional[MaxRetries]
    AllocatedCapacity: Optional[IntegerValue]
    Timeout: Optional[Timeout]
    MaxCapacity: Optional[NullableDouble]
    WorkerType: Optional[WorkerType]
    NumberOfWorkers: Optional[NullableInteger]
    SecurityConfiguration: Optional[NameString]
    NotificationProperty: Optional[NotificationProperty]
    GlueVersion: Optional[GlueVersionString]


class ListBlueprintsRequest(ServiceRequest):
    NextToken: Optional[GenericString]
    MaxResults: Optional[PageSize]
    Tags: Optional[TagsMap]


class ListBlueprintsResponse(TypedDict, total=False):
    Blueprints: Optional[BlueprintNames]
    NextToken: Optional[GenericString]


class ListCrawlersRequest(ServiceRequest):
    MaxResults: Optional[PageSize]
    NextToken: Optional[Token]
    Tags: Optional[TagsMap]


class ListCrawlersResponse(TypedDict, total=False):
    CrawlerNames: Optional[CrawlerNameList]
    NextToken: Optional[Token]


class ListCustomEntityTypesRequest(ServiceRequest):
    NextToken: Optional[PaginationToken]
    MaxResults: Optional[PageSize]


class ListCustomEntityTypesResponse(TypedDict, total=False):
    CustomEntityTypes: Optional[CustomEntityTypes]
    NextToken: Optional[PaginationToken]


class ListDevEndpointsRequest(ServiceRequest):
    NextToken: Optional[GenericString]
    MaxResults: Optional[PageSize]
    Tags: Optional[TagsMap]


class ListDevEndpointsResponse(TypedDict, total=False):
    DevEndpointNames: Optional[DevEndpointNameList]
    NextToken: Optional[GenericString]


class ListJobsRequest(ServiceRequest):
    NextToken: Optional[GenericString]
    MaxResults: Optional[PageSize]
    Tags: Optional[TagsMap]


class ListJobsResponse(TypedDict, total=False):
    JobNames: Optional[JobNameList]
    NextToken: Optional[GenericString]


class ListMLTransformsRequest(ServiceRequest):
    NextToken: Optional[PaginationToken]
    MaxResults: Optional[PageSize]
    Filter: Optional[TransformFilterCriteria]
    Sort: Optional[TransformSortCriteria]
    Tags: Optional[TagsMap]


TransformIdList = List[HashString]


class ListMLTransformsResponse(TypedDict, total=False):
    TransformIds: TransformIdList
    NextToken: Optional[PaginationToken]


class ListRegistriesInput(ServiceRequest):
    MaxResults: Optional[MaxResultsNumber]
    NextToken: Optional[SchemaRegistryTokenString]


class RegistryListItem(TypedDict, total=False):
    """A structure containing the details for a registry."""

    RegistryName: Optional[SchemaRegistryNameString]
    RegistryArn: Optional[GlueResourceArn]
    Description: Optional[DescriptionString]
    Status: Optional[RegistryStatus]
    CreatedTime: Optional[CreatedTimestamp]
    UpdatedTime: Optional[UpdatedTimestamp]


RegistryListDefinition = List[RegistryListItem]


class ListRegistriesResponse(TypedDict, total=False):
    Registries: Optional[RegistryListDefinition]
    NextToken: Optional[SchemaRegistryTokenString]


class ListSchemaVersionsInput(ServiceRequest):
    SchemaId: SchemaId
    MaxResults: Optional[MaxResultsNumber]
    NextToken: Optional[SchemaRegistryTokenString]


class SchemaVersionListItem(TypedDict, total=False):
    """An object containing the details about a schema version."""

    SchemaArn: Optional[GlueResourceArn]
    SchemaVersionId: Optional[SchemaVersionIdString]
    VersionNumber: Optional[VersionLongNumber]
    Status: Optional[SchemaVersionStatus]
    CreatedTime: Optional[CreatedTimestamp]


SchemaVersionList = List[SchemaVersionListItem]


class ListSchemaVersionsResponse(TypedDict, total=False):
    Schemas: Optional[SchemaVersionList]
    NextToken: Optional[SchemaRegistryTokenString]


class ListSchemasInput(ServiceRequest):
    RegistryId: Optional[RegistryId]
    MaxResults: Optional[MaxResultsNumber]
    NextToken: Optional[SchemaRegistryTokenString]


class SchemaListItem(TypedDict, total=False):
    """An object that contains minimal details for a schema."""

    RegistryName: Optional[SchemaRegistryNameString]
    SchemaName: Optional[SchemaRegistryNameString]
    SchemaArn: Optional[GlueResourceArn]
    Description: Optional[DescriptionString]
    SchemaStatus: Optional[SchemaStatus]
    CreatedTime: Optional[CreatedTimestamp]
    UpdatedTime: Optional[UpdatedTimestamp]


SchemaListDefinition = List[SchemaListItem]


class ListSchemasResponse(TypedDict, total=False):
    Schemas: Optional[SchemaListDefinition]
    NextToken: Optional[SchemaRegistryTokenString]


class ListSessionsRequest(ServiceRequest):
    NextToken: Optional[OrchestrationToken]
    MaxResults: Optional[PageSize]
    Tags: Optional[TagsMap]
    RequestOrigin: Optional[OrchestrationNameString]


SessionList = List[Session]
SessionIdList = List[NameString]


class ListSessionsResponse(TypedDict, total=False):
    Ids: Optional[SessionIdList]
    Sessions: Optional[SessionList]
    NextToken: Optional[OrchestrationToken]


class ListStatementsRequest(ServiceRequest):
    SessionId: NameString
    RequestOrigin: Optional[OrchestrationNameString]
    NextToken: Optional[OrchestrationToken]


StatementList = List[Statement]


class ListStatementsResponse(TypedDict, total=False):
    Statements: Optional[StatementList]
    NextToken: Optional[OrchestrationToken]


class ListTriggersRequest(ServiceRequest):
    NextToken: Optional[GenericString]
    DependentJobName: Optional[NameString]
    MaxResults: Optional[PageSize]
    Tags: Optional[TagsMap]


class ListTriggersResponse(TypedDict, total=False):
    TriggerNames: Optional[TriggerNameList]
    NextToken: Optional[GenericString]


class ListWorkflowsRequest(ServiceRequest):
    NextToken: Optional[GenericString]
    MaxResults: Optional[PageSize]


class ListWorkflowsResponse(TypedDict, total=False):
    Workflows: Optional[WorkflowNames]
    NextToken: Optional[GenericString]


class OtherMetadataValueListItem(TypedDict, total=False):
    """A structure containing other metadata for a schema version belonging to
    the same metadata key.
    """

    MetadataValue: Optional[MetadataValueString]
    CreatedTime: Optional[CreatedTimestamp]


OtherMetadataValueList = List[OtherMetadataValueListItem]


class MetadataInfo(TypedDict, total=False):
    """A structure containing metadata information for a schema version."""

    MetadataValue: Optional[MetadataValueString]
    CreatedTime: Optional[CreatedTimestamp]
    OtherMetadataValueList: Optional[OtherMetadataValueList]


MetadataInfoMap = Dict[MetadataKeyString, MetadataInfo]


class MetadataKeyValuePair(TypedDict, total=False):
    """A structure containing a key value pair for metadata."""

    MetadataKey: Optional[MetadataKeyString]
    MetadataValue: Optional[MetadataValueString]


MetadataList = List[MetadataKeyValuePair]
NodeIdList = List[NameString]


class PropertyPredicate(TypedDict, total=False):
    """Defines a property predicate."""

    Key: Optional[ValueString]
    Value: Optional[ValueString]
    Comparator: Optional[Comparator]


class PutDataCatalogEncryptionSettingsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DataCatalogEncryptionSettings: DataCatalogEncryptionSettings


class PutDataCatalogEncryptionSettingsResponse(TypedDict, total=False):
    pass


class PutResourcePolicyRequest(ServiceRequest):
    PolicyInJson: PolicyJsonString
    ResourceArn: Optional[GlueResourceArn]
    PolicyHashCondition: Optional[HashString]
    PolicyExistsCondition: Optional[ExistCondition]
    EnableHybrid: Optional[EnableHybridValues]


class PutResourcePolicyResponse(TypedDict, total=False):
    PolicyHash: Optional[HashString]


class PutSchemaVersionMetadataInput(ServiceRequest):
    SchemaId: Optional[SchemaId]
    SchemaVersionNumber: Optional[SchemaVersionNumber]
    SchemaVersionId: Optional[SchemaVersionIdString]
    MetadataKeyValue: MetadataKeyValuePair


class PutSchemaVersionMetadataResponse(TypedDict, total=False):
    SchemaArn: Optional[GlueResourceArn]
    SchemaName: Optional[SchemaRegistryNameString]
    RegistryName: Optional[SchemaRegistryNameString]
    LatestVersion: Optional[LatestSchemaVersionBoolean]
    VersionNumber: Optional[VersionLongNumber]
    SchemaVersionId: Optional[SchemaVersionIdString]
    MetadataKey: Optional[MetadataKeyString]
    MetadataValue: Optional[MetadataValueString]


class PutWorkflowRunPropertiesRequest(ServiceRequest):
    Name: NameString
    RunId: IdString
    RunProperties: WorkflowRunProperties


class PutWorkflowRunPropertiesResponse(TypedDict, total=False):
    pass


class QuerySchemaVersionMetadataInput(ServiceRequest):
    SchemaId: Optional[SchemaId]
    SchemaVersionNumber: Optional[SchemaVersionNumber]
    SchemaVersionId: Optional[SchemaVersionIdString]
    MetadataList: Optional[MetadataList]
    MaxResults: Optional[QuerySchemaVersionMetadataMaxResults]
    NextToken: Optional[SchemaRegistryTokenString]


class QuerySchemaVersionMetadataResponse(TypedDict, total=False):
    MetadataInfoMap: Optional[MetadataInfoMap]
    SchemaVersionId: Optional[SchemaVersionIdString]
    NextToken: Optional[SchemaRegistryTokenString]


class RegisterSchemaVersionInput(ServiceRequest):
    SchemaId: SchemaId
    SchemaDefinition: SchemaDefinitionString


class RegisterSchemaVersionResponse(TypedDict, total=False):
    SchemaVersionId: Optional[SchemaVersionIdString]
    VersionNumber: Optional[VersionLongNumber]
    Status: Optional[SchemaVersionStatus]


class RemoveSchemaVersionMetadataInput(ServiceRequest):
    SchemaId: Optional[SchemaId]
    SchemaVersionNumber: Optional[SchemaVersionNumber]
    SchemaVersionId: Optional[SchemaVersionIdString]
    MetadataKeyValue: MetadataKeyValuePair


class RemoveSchemaVersionMetadataResponse(TypedDict, total=False):
    SchemaArn: Optional[GlueResourceArn]
    SchemaName: Optional[SchemaRegistryNameString]
    RegistryName: Optional[SchemaRegistryNameString]
    LatestVersion: Optional[LatestSchemaVersionBoolean]
    VersionNumber: Optional[VersionLongNumber]
    SchemaVersionId: Optional[SchemaVersionIdString]
    MetadataKey: Optional[MetadataKeyString]
    MetadataValue: Optional[MetadataValueString]


class ResetJobBookmarkRequest(ServiceRequest):
    JobName: JobName
    RunId: Optional[RunId]


class ResetJobBookmarkResponse(TypedDict, total=False):
    JobBookmarkEntry: Optional[JobBookmarkEntry]


class ResumeWorkflowRunRequest(ServiceRequest):
    Name: NameString
    RunId: IdString
    NodeIds: NodeIdList


class ResumeWorkflowRunResponse(TypedDict, total=False):
    RunId: Optional[IdString]
    NodeIds: Optional[NodeIdList]


class RunStatementRequest(ServiceRequest):
    SessionId: NameString
    Code: OrchestrationStatementCodeString
    RequestOrigin: Optional[OrchestrationNameString]


class RunStatementResponse(TypedDict, total=False):
    Id: Optional[IntegerValue]


SearchPropertyPredicates = List[PropertyPredicate]


class SortCriterion(TypedDict, total=False):
    """Specifies a field to sort by and a sort order."""

    FieldName: Optional[ValueString]
    Sort: Optional[Sort]


SortCriteria = List[SortCriterion]


class SearchTablesRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    NextToken: Optional[Token]
    Filters: Optional[SearchPropertyPredicates]
    SearchText: Optional[ValueString]
    SortCriteria: Optional[SortCriteria]
    MaxResults: Optional[PageSize]
    ResourceShareType: Optional[ResourceShareType]


class SearchTablesResponse(TypedDict, total=False):
    NextToken: Optional[Token]
    TableList: Optional[TableList]


class StartBlueprintRunRequest(ServiceRequest):
    BlueprintName: OrchestrationNameString
    Parameters: Optional[BlueprintParameters]
    RoleArn: OrchestrationIAMRoleArn


class StartBlueprintRunResponse(TypedDict, total=False):
    RunId: Optional[IdString]


class StartCrawlerRequest(ServiceRequest):
    Name: NameString


class StartCrawlerResponse(TypedDict, total=False):
    pass


class StartCrawlerScheduleRequest(ServiceRequest):
    CrawlerName: NameString


class StartCrawlerScheduleResponse(TypedDict, total=False):
    pass


class StartExportLabelsTaskRunRequest(ServiceRequest):
    TransformId: HashString
    OutputS3Path: UriString


class StartExportLabelsTaskRunResponse(TypedDict, total=False):
    TaskRunId: Optional[HashString]


class StartImportLabelsTaskRunRequest(ServiceRequest):
    TransformId: HashString
    InputS3Path: UriString
    ReplaceAllLabels: Optional[ReplaceBoolean]


class StartImportLabelsTaskRunResponse(TypedDict, total=False):
    TaskRunId: Optional[HashString]


class StartJobRunRequest(ServiceRequest):
    JobName: NameString
    JobRunId: Optional[IdString]
    Arguments: Optional[GenericMap]
    AllocatedCapacity: Optional[IntegerValue]
    Timeout: Optional[Timeout]
    MaxCapacity: Optional[NullableDouble]
    SecurityConfiguration: Optional[NameString]
    NotificationProperty: Optional[NotificationProperty]
    WorkerType: Optional[WorkerType]
    NumberOfWorkers: Optional[NullableInteger]


class StartJobRunResponse(TypedDict, total=False):
    JobRunId: Optional[IdString]


class StartMLEvaluationTaskRunRequest(ServiceRequest):
    TransformId: HashString


class StartMLEvaluationTaskRunResponse(TypedDict, total=False):
    TaskRunId: Optional[HashString]


class StartMLLabelingSetGenerationTaskRunRequest(ServiceRequest):
    TransformId: HashString
    OutputS3Path: UriString


class StartMLLabelingSetGenerationTaskRunResponse(TypedDict, total=False):
    TaskRunId: Optional[HashString]


class StartTriggerRequest(ServiceRequest):
    Name: NameString


class StartTriggerResponse(TypedDict, total=False):
    Name: Optional[NameString]


class StartWorkflowRunRequest(ServiceRequest):
    Name: NameString
    RunProperties: Optional[WorkflowRunProperties]


class StartWorkflowRunResponse(TypedDict, total=False):
    RunId: Optional[IdString]


class StopCrawlerRequest(ServiceRequest):
    Name: NameString


class StopCrawlerResponse(TypedDict, total=False):
    pass


class StopCrawlerScheduleRequest(ServiceRequest):
    CrawlerName: NameString


class StopCrawlerScheduleResponse(TypedDict, total=False):
    pass


class StopSessionRequest(ServiceRequest):
    Id: NameString
    RequestOrigin: Optional[OrchestrationNameString]


class StopSessionResponse(TypedDict, total=False):
    Id: Optional[NameString]


class StopTriggerRequest(ServiceRequest):
    Name: NameString


class StopTriggerResponse(TypedDict, total=False):
    Name: Optional[NameString]


class StopWorkflowRunRequest(ServiceRequest):
    Name: NameString
    RunId: IdString


class StopWorkflowRunResponse(TypedDict, total=False):
    pass


TagKeysList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    ResourceArn: GlueResourceArn
    TagsToAdd: TagsMap


class TagResourceResponse(TypedDict, total=False):
    pass


class TriggerUpdate(TypedDict, total=False):
    """A structure used to provide information used to update a trigger. This
    object updates the previous trigger definition by overwriting it
    completely.
    """

    Name: Optional[NameString]
    Description: Optional[DescriptionString]
    Schedule: Optional[GenericString]
    Actions: Optional[ActionList]
    Predicate: Optional[Predicate]
    EventBatchingCondition: Optional[EventBatchingCondition]


class UntagResourceRequest(ServiceRequest):
    ResourceArn: GlueResourceArn
    TagsToRemove: TagKeysList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateBlueprintRequest(ServiceRequest):
    Name: OrchestrationNameString
    Description: Optional[Generic512CharString]
    BlueprintLocation: OrchestrationS3Location


class UpdateBlueprintResponse(TypedDict, total=False):
    Name: Optional[NameString]


class UpdateCsvClassifierRequest(TypedDict, total=False):
    """Specifies a custom CSV classifier to be updated."""

    Name: NameString
    Delimiter: Optional[CsvColumnDelimiter]
    QuoteSymbol: Optional[CsvQuoteSymbol]
    ContainsHeader: Optional[CsvHeaderOption]
    Header: Optional[CsvHeader]
    DisableValueTrimming: Optional[NullableBoolean]
    AllowSingleColumn: Optional[NullableBoolean]


class UpdateJsonClassifierRequest(TypedDict, total=False):
    """Specifies a JSON classifier to be updated."""

    Name: NameString
    JsonPath: Optional[JsonPath]


class UpdateXMLClassifierRequest(TypedDict, total=False):
    """Specifies an XML classifier to be updated."""

    Name: NameString
    Classification: Optional[Classification]
    RowTag: Optional[RowTag]


class UpdateGrokClassifierRequest(TypedDict, total=False):
    """Specifies a grok classifier to update when passed to
    ``UpdateClassifier``.
    """

    Name: NameString
    Classification: Optional[Classification]
    GrokPattern: Optional[GrokPattern]
    CustomPatterns: Optional[CustomPatterns]


class UpdateClassifierRequest(ServiceRequest):
    GrokClassifier: Optional[UpdateGrokClassifierRequest]
    XMLClassifier: Optional[UpdateXMLClassifierRequest]
    JsonClassifier: Optional[UpdateJsonClassifierRequest]
    CsvClassifier: Optional[UpdateCsvClassifierRequest]


class UpdateClassifierResponse(TypedDict, total=False):
    pass


UpdateColumnStatisticsList = List[ColumnStatistics]


class UpdateColumnStatisticsForPartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionValues: ValueStringList
    ColumnStatisticsList: UpdateColumnStatisticsList


class UpdateColumnStatisticsForPartitionResponse(TypedDict, total=False):
    Errors: Optional[ColumnStatisticsErrors]


class UpdateColumnStatisticsForTableRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    ColumnStatisticsList: UpdateColumnStatisticsList


class UpdateColumnStatisticsForTableResponse(TypedDict, total=False):
    Errors: Optional[ColumnStatisticsErrors]


class UpdateConnectionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Name: NameString
    ConnectionInput: ConnectionInput


class UpdateConnectionResponse(TypedDict, total=False):
    pass


class UpdateCrawlerRequest(ServiceRequest):
    Name: NameString
    Role: Optional[Role]
    DatabaseName: Optional[DatabaseName]
    Description: Optional[DescriptionStringRemovable]
    Targets: Optional[CrawlerTargets]
    Schedule: Optional[CronExpression]
    Classifiers: Optional[ClassifierNameList]
    TablePrefix: Optional[TablePrefix]
    SchemaChangePolicy: Optional[SchemaChangePolicy]
    RecrawlPolicy: Optional[RecrawlPolicy]
    LineageConfiguration: Optional[LineageConfiguration]
    LakeFormationConfiguration: Optional[LakeFormationConfiguration]
    Configuration: Optional[CrawlerConfiguration]
    CrawlerSecurityConfiguration: Optional[CrawlerSecurityConfiguration]


class UpdateCrawlerResponse(TypedDict, total=False):
    pass


class UpdateCrawlerScheduleRequest(ServiceRequest):
    CrawlerName: NameString
    Schedule: Optional[CronExpression]


class UpdateCrawlerScheduleResponse(TypedDict, total=False):
    pass


class UpdateDatabaseRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Name: NameString
    DatabaseInput: DatabaseInput


class UpdateDatabaseResponse(TypedDict, total=False):
    pass


class UpdateDevEndpointRequest(ServiceRequest):
    EndpointName: GenericString
    PublicKey: Optional[GenericString]
    AddPublicKeys: Optional[PublicKeysList]
    DeletePublicKeys: Optional[PublicKeysList]
    CustomLibraries: Optional[DevEndpointCustomLibraries]
    UpdateEtlLibraries: Optional[BooleanValue]
    DeleteArguments: Optional[StringList]
    AddArguments: Optional[MapValue]


class UpdateDevEndpointResponse(TypedDict, total=False):
    pass


class UpdateJobRequest(ServiceRequest):
    JobName: NameString
    JobUpdate: JobUpdate


class UpdateJobResponse(TypedDict, total=False):
    JobName: Optional[NameString]


class UpdateMLTransformRequest(ServiceRequest):
    TransformId: HashString
    Name: Optional[NameString]
    Description: Optional[DescriptionString]
    Parameters: Optional[TransformParameters]
    Role: Optional[RoleString]
    GlueVersion: Optional[GlueVersionString]
    MaxCapacity: Optional[NullableDouble]
    WorkerType: Optional[WorkerType]
    NumberOfWorkers: Optional[NullableInteger]
    Timeout: Optional[Timeout]
    MaxRetries: Optional[NullableInteger]


class UpdateMLTransformResponse(TypedDict, total=False):
    TransformId: Optional[HashString]


class UpdatePartitionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    PartitionValueList: BoundedPartitionValueList
    PartitionInput: PartitionInput


class UpdatePartitionResponse(TypedDict, total=False):
    pass


class UpdateRegistryInput(ServiceRequest):
    RegistryId: RegistryId
    Description: DescriptionString


class UpdateRegistryResponse(TypedDict, total=False):
    RegistryName: Optional[SchemaRegistryNameString]
    RegistryArn: Optional[GlueResourceArn]


class UpdateSchemaInput(ServiceRequest):
    SchemaId: SchemaId
    SchemaVersionNumber: Optional[SchemaVersionNumber]
    Compatibility: Optional[Compatibility]
    Description: Optional[DescriptionString]


class UpdateSchemaResponse(TypedDict, total=False):
    SchemaArn: Optional[GlueResourceArn]
    SchemaName: Optional[SchemaRegistryNameString]
    RegistryName: Optional[SchemaRegistryNameString]


class UpdateTableRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableInput: TableInput
    SkipArchive: Optional[BooleanNullable]
    TransactionId: Optional[TransactionIdString]
    VersionId: Optional[VersionString]


class UpdateTableResponse(TypedDict, total=False):
    pass


class UpdateTriggerRequest(ServiceRequest):
    Name: NameString
    TriggerUpdate: TriggerUpdate


class UpdateTriggerResponse(TypedDict, total=False):
    Trigger: Optional[Trigger]


class UpdateUserDefinedFunctionRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    FunctionName: NameString
    FunctionInput: UserDefinedFunctionInput


class UpdateUserDefinedFunctionResponse(TypedDict, total=False):
    pass


class UpdateWorkflowRequest(ServiceRequest):
    Name: NameString
    Description: Optional[GenericString]
    DefaultRunProperties: Optional[WorkflowRunProperties]
    MaxConcurrentRuns: Optional[NullableInteger]


class UpdateWorkflowResponse(TypedDict, total=False):
    Name: Optional[NameString]


class GlueApi:

    service = "glue"
    version = "2017-03-31"

    @handler("BatchCreatePartition")
    def batch_create_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partition_input_list: PartitionInputList,
        catalog_id: CatalogIdString = None,
    ) -> BatchCreatePartitionResponse:
        """Creates one or more partitions in a batch operation.

        :param database_name: The name of the metadata database in which the partition is to be
        created.
        :param table_name: The name of the metadata table in which the partition is to be created.
        :param partition_input_list: A list of ``PartitionInput`` structures that define the partitions to be
        created.
        :param catalog_id: The ID of the catalog in which the partition is to be created.
        :returns: BatchCreatePartitionResponse
        :raises InvalidInputException:
        :raises AlreadyExistsException:
        :raises ResourceNumberLimitExceededException:
        :raises InternalServiceException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("BatchDeleteConnection")
    def batch_delete_connection(
        self,
        context: RequestContext,
        connection_name_list: DeleteConnectionNameList,
        catalog_id: CatalogIdString = None,
    ) -> BatchDeleteConnectionResponse:
        """Deletes a list of connection definitions from the Data Catalog.

        :param connection_name_list: A list of names of the connections to delete.
        :param catalog_id: The ID of the Data Catalog in which the connections reside.
        :returns: BatchDeleteConnectionResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("BatchDeletePartition")
    def batch_delete_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partitions_to_delete: BatchDeletePartitionValueList,
        catalog_id: CatalogIdString = None,
    ) -> BatchDeletePartitionResponse:
        """Deletes one or more partitions in a batch operation.

        :param database_name: The name of the catalog database in which the table in question resides.
        :param table_name: The name of the table that contains the partitions to be deleted.
        :param partitions_to_delete: A list of ``PartitionInput`` structures that define the partitions to be
        deleted.
        :param catalog_id: The ID of the Data Catalog where the partition to be deleted resides.
        :returns: BatchDeletePartitionResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("BatchDeleteTable")
    def batch_delete_table(
        self,
        context: RequestContext,
        database_name: NameString,
        tables_to_delete: BatchDeleteTableNameList,
        catalog_id: CatalogIdString = None,
        transaction_id: TransactionIdString = None,
    ) -> BatchDeleteTableResponse:
        """Deletes multiple tables at once.

        After completing this operation, you no longer have access to the table
        versions and partitions that belong to the deleted table. Glue deletes
        these "orphaned" resources asynchronously in a timely manner, at the
        discretion of the service.

        To ensure the immediate deletion of all related resources, before
        calling ``BatchDeleteTable``, use ``DeleteTableVersion`` or
        ``BatchDeleteTableVersion``, and ``DeletePartition`` or
        ``BatchDeletePartition``, to delete any resources that belong to the
        table.

        :param database_name: The name of the catalog database in which the tables to delete reside.
        :param tables_to_delete: A list of the table to delete.
        :param catalog_id: The ID of the Data Catalog where the table resides.
        :param transaction_id: The transaction ID at which to delete the table contents.
        :returns: BatchDeleteTableResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises ResourceNotReadyException:
        """
        raise NotImplementedError

    @handler("BatchDeleteTableVersion")
    def batch_delete_table_version(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        version_ids: BatchDeleteTableVersionList,
        catalog_id: CatalogIdString = None,
    ) -> BatchDeleteTableVersionResponse:
        """Deletes a specified batch of versions of a table.

        :param database_name: The database in the catalog in which the table resides.
        :param table_name: The name of the table.
        :param version_ids: A list of the IDs of versions to be deleted.
        :param catalog_id: The ID of the Data Catalog where the tables reside.
        :returns: BatchDeleteTableVersionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("BatchGetBlueprints")
    def batch_get_blueprints(
        self,
        context: RequestContext,
        names: BatchGetBlueprintNames,
        include_blueprint: NullableBoolean = None,
        include_parameter_spec: NullableBoolean = None,
    ) -> BatchGetBlueprintsResponse:
        """Retrieves information about a list of blueprints.

        :param names: A list of blueprint names.
        :param include_blueprint: Specifies whether or not to include the blueprint in the response.
        :param include_parameter_spec: Specifies whether or not to include the parameters, as a JSON string,
        for the blueprint in the response.
        :returns: BatchGetBlueprintsResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("BatchGetCrawlers")
    def batch_get_crawlers(
        self, context: RequestContext, crawler_names: CrawlerNameList
    ) -> BatchGetCrawlersResponse:
        """Returns a list of resource metadata for a given list of crawler names.
        After calling the ``ListCrawlers`` operation, you can call this
        operation to access the data to which you have been granted permissions.
        This operation supports all IAM permissions, including permission
        conditions that uses tags.

        :param crawler_names: A list of crawler names, which might be the names returned from the
        ``ListCrawlers`` operation.
        :returns: BatchGetCrawlersResponse
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("BatchGetCustomEntityTypes")
    def batch_get_custom_entity_types(
        self, context: RequestContext, names: CustomEntityTypeNames
    ) -> BatchGetCustomEntityTypesResponse:
        """Retrieves the details for the custom patterns specified by a list of
        names.

        :param names: A list of names of the custom patterns that you want to retrieve.
        :returns: BatchGetCustomEntityTypesResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("BatchGetDevEndpoints")
    def batch_get_dev_endpoints(
        self, context: RequestContext, dev_endpoint_names: DevEndpointNames
    ) -> BatchGetDevEndpointsResponse:
        """Returns a list of resource metadata for a given list of development
        endpoint names. After calling the ``ListDevEndpoints`` operation, you
        can call this operation to access the data to which you have been
        granted permissions. This operation supports all IAM permissions,
        including permission conditions that uses tags.

        :param dev_endpoint_names: The list of ``DevEndpoint`` names, which might be the names returned
        from the ``ListDevEndpoint`` operation.
        :returns: BatchGetDevEndpointsResponse
        :raises AccessDeniedException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("BatchGetJobs")
    def batch_get_jobs(
        self, context: RequestContext, job_names: JobNameList
    ) -> BatchGetJobsResponse:
        """Returns a list of resource metadata for a given list of job names. After
        calling the ``ListJobs`` operation, you can call this operation to
        access the data to which you have been granted permissions. This
        operation supports all IAM permissions, including permission conditions
        that uses tags.

        :param job_names: A list of job names, which might be the names returned from the
        ``ListJobs`` operation.
        :returns: BatchGetJobsResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("BatchGetPartition")
    def batch_get_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partitions_to_get: BatchGetPartitionValueList,
        catalog_id: CatalogIdString = None,
    ) -> BatchGetPartitionResponse:
        """Retrieves partitions in a batch request.

        :param database_name: The name of the catalog database where the partitions reside.
        :param table_name: The name of the partitions' table.
        :param partitions_to_get: A list of partition values identifying the partitions to retrieve.
        :param catalog_id: The ID of the Data Catalog where the partitions in question reside.
        :returns: BatchGetPartitionResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises GlueEncryptionException:
        :raises InvalidStateException:
        """
        raise NotImplementedError

    @handler("BatchGetTriggers")
    def batch_get_triggers(
        self, context: RequestContext, trigger_names: TriggerNameList
    ) -> BatchGetTriggersResponse:
        """Returns a list of resource metadata for a given list of trigger names.
        After calling the ``ListTriggers`` operation, you can call this
        operation to access the data to which you have been granted permissions.
        This operation supports all IAM permissions, including permission
        conditions that uses tags.

        :param trigger_names: A list of trigger names, which may be the names returned from the
        ``ListTriggers`` operation.
        :returns: BatchGetTriggersResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("BatchGetWorkflows")
    def batch_get_workflows(
        self, context: RequestContext, names: WorkflowNames, include_graph: NullableBoolean = None
    ) -> BatchGetWorkflowsResponse:
        """Returns a list of resource metadata for a given list of workflow names.
        After calling the ``ListWorkflows`` operation, you can call this
        operation to access the data to which you have been granted permissions.
        This operation supports all IAM permissions, including permission
        conditions that uses tags.

        :param names: A list of workflow names, which may be the names returned from the
        ``ListWorkflows`` operation.
        :param include_graph: Specifies whether to include a graph when returning the workflow
        resource metadata.
        :returns: BatchGetWorkflowsResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("BatchStopJobRun")
    def batch_stop_job_run(
        self,
        context: RequestContext,
        job_name: NameString,
        job_run_ids: BatchStopJobRunJobRunIdList,
    ) -> BatchStopJobRunResponse:
        """Stops one or more job runs for a specified job definition.

        :param job_name: The name of the job definition for which to stop job runs.
        :param job_run_ids: A list of the ``JobRunIds`` that should be stopped for that job
        definition.
        :returns: BatchStopJobRunResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("BatchUpdatePartition")
    def batch_update_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        entries: BatchUpdatePartitionRequestEntryList,
        catalog_id: CatalogIdString = None,
    ) -> BatchUpdatePartitionResponse:
        """Updates one or more partitions in a batch operation.

        :param database_name: The name of the metadata database in which the partition is to be
        updated.
        :param table_name: The name of the metadata table in which the partition is to be updated.
        :param entries: A list of up to 100 ``BatchUpdatePartitionRequestEntry`` objects to
        update.
        :param catalog_id: The ID of the catalog in which the partition is to be updated.
        :returns: BatchUpdatePartitionResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("CancelMLTaskRun")
    def cancel_ml_task_run(
        self, context: RequestContext, transform_id: HashString, task_run_id: HashString
    ) -> CancelMLTaskRunResponse:
        """Cancels (stops) a task run. Machine learning task runs are asynchronous
        tasks that Glue runs on your behalf as part of various machine learning
        workflows. You can cancel a machine learning task run at any time by
        calling ``CancelMLTaskRun`` with a task run's parent transform's
        ``TransformID`` and the task run's ``TaskRunId``.

        :param transform_id: The unique identifier of the machine learning transform.
        :param task_run_id: A unique identifier for the task run.
        :returns: CancelMLTaskRunResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("CancelStatement")
    def cancel_statement(
        self,
        context: RequestContext,
        session_id: NameString,
        id: IntegerValue,
        request_origin: OrchestrationNameString = None,
    ) -> CancelStatementResponse:
        """Cancels the statement..

        :param session_id: The Session ID of the statement to be cancelled.
        :param id: The ID of the statement to be cancelled.
        :param request_origin: The origin of the request to cancel the statement.
        :returns: CancelStatementResponse
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises IllegalSessionStateException:
        """
        raise NotImplementedError

    @handler("CheckSchemaVersionValidity")
    def check_schema_version_validity(
        self,
        context: RequestContext,
        data_format: DataFormat,
        schema_definition: SchemaDefinitionString,
    ) -> CheckSchemaVersionValidityResponse:
        """Validates the supplied schema. This call has no side effects, it simply
        validates using the supplied schema using ``DataFormat`` as the format.
        Since it does not take a schema set name, no compatibility checks are
        performed.

        :param data_format: The data format of the schema definition.
        :param schema_definition: The definition of the schema that has to be validated.
        :returns: CheckSchemaVersionValidityResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("CreateBlueprint")
    def create_blueprint(
        self,
        context: RequestContext,
        name: OrchestrationNameString,
        blueprint_location: OrchestrationS3Location,
        description: Generic512CharString = None,
        tags: TagsMap = None,
    ) -> CreateBlueprintResponse:
        """Registers a blueprint with Glue.

        :param name: The name of the blueprint.
        :param blueprint_location: Specifies a path in Amazon S3 where the blueprint is published.
        :param description: A description of the blueprint.
        :param tags: The tags to be applied to this blueprint.
        :returns: CreateBlueprintResponse
        :raises AlreadyExistsException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises ResourceNumberLimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateClassifier")
    def create_classifier(
        self,
        context: RequestContext,
        grok_classifier: CreateGrokClassifierRequest = None,
        xml_classifier: CreateXMLClassifierRequest = None,
        json_classifier: CreateJsonClassifierRequest = None,
        csv_classifier: CreateCsvClassifierRequest = None,
    ) -> CreateClassifierResponse:
        """Creates a classifier in the user's account. This can be a
        ``GrokClassifier``, an ``XMLClassifier``, a ``JsonClassifier``, or a
        ``CsvClassifier``, depending on which field of the request is present.

        :param grok_classifier: A ``GrokClassifier`` object specifying the classifier to create.
        :param xml_classifier: An ``XMLClassifier`` object specifying the classifier to create.
        :param json_classifier: A ``JsonClassifier`` object specifying the classifier to create.
        :param csv_classifier: A ``CsvClassifier`` object specifying the classifier to create.
        :returns: CreateClassifierResponse
        :raises AlreadyExistsException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("CreateConnection")
    def create_connection(
        self,
        context: RequestContext,
        connection_input: ConnectionInput,
        catalog_id: CatalogIdString = None,
        tags: TagsMap = None,
    ) -> CreateConnectionResponse:
        """Creates a connection definition in the Data Catalog.

        :param connection_input: A ``ConnectionInput`` object defining the connection to create.
        :param catalog_id: The ID of the Data Catalog in which to create the connection.
        :param tags: The tags you assign to the connection.
        :returns: CreateConnectionResponse
        :raises AlreadyExistsException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("CreateCrawler")
    def create_crawler(
        self,
        context: RequestContext,
        name: NameString,
        role: Role,
        targets: CrawlerTargets,
        database_name: DatabaseName = None,
        description: DescriptionString = None,
        schedule: CronExpression = None,
        classifiers: ClassifierNameList = None,
        table_prefix: TablePrefix = None,
        schema_change_policy: SchemaChangePolicy = None,
        recrawl_policy: RecrawlPolicy = None,
        lineage_configuration: LineageConfiguration = None,
        lake_formation_configuration: LakeFormationConfiguration = None,
        configuration: CrawlerConfiguration = None,
        crawler_security_configuration: CrawlerSecurityConfiguration = None,
        tags: TagsMap = None,
    ) -> CreateCrawlerResponse:
        """Creates a new crawler with specified targets, role, configuration, and
        optional schedule. At least one crawl target must be specified, in the
        ``s3Targets`` field, the ``jdbcTargets`` field, or the
        ``DynamoDBTargets`` field.

        :param name: Name of the new crawler.
        :param role: The IAM role or Amazon Resource Name (ARN) of an IAM role used by the
        new crawler to access customer resources.
        :param targets: A list of collection of targets to crawl.
        :param database_name: The Glue database where results are written, such as:
        ``arn:aws:daylight:us-east-1::database/sometable/*``.
        :param description: A description of the new crawler.
        :param schedule: A ``cron`` expression used to specify the schedule (see `Time-Based
        Schedules for Jobs and
        Crawlers <https://docs.
        :param classifiers: A list of custom classifiers that the user has registered.
        :param table_prefix: The table prefix used for catalog tables that are created.
        :param schema_change_policy: The policy for the crawler's update and deletion behavior.
        :param recrawl_policy: A policy that specifies whether to crawl the entire dataset again, or to
        crawl only folders that were added since the last crawler run.
        :param lineage_configuration: Specifies data lineage configuration settings for the crawler.
        :param lake_formation_configuration: Specifies AWS Lake Formation configuration settings for the crawler.
        :param configuration: Crawler configuration information.
        :param crawler_security_configuration: The name of the ``SecurityConfiguration`` structure to be used by this
        crawler.
        :param tags: The tags to use with this crawler request.
        :returns: CreateCrawlerResponse
        :raises InvalidInputException:
        :raises AlreadyExistsException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateCustomEntityType")
    def create_custom_entity_type(
        self,
        context: RequestContext,
        name: NameString,
        regex_string: NameString,
        context_words: ContextWords = None,
    ) -> CreateCustomEntityTypeResponse:
        """Creates a custom pattern that is used to detect sensitive data across
        the columns and rows of your structured data.

        Each custom pattern you create specifies a regular expression and an
        optional list of context words. If no context words are passed only a
        regular expression is checked.

        :param name: A name for the custom pattern that allows it to be retrieved or deleted
        later.
        :param regex_string: A regular expression string that is used for detecting sensitive data in
        a custom pattern.
        :param context_words: A list of context words.
        :returns: CreateCustomEntityTypeResponse
        :raises AccessDeniedException:
        :raises AlreadyExistsException:
        :raises IdempotentParameterMismatchException:
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateDatabase")
    def create_database(
        self,
        context: RequestContext,
        database_input: DatabaseInput,
        catalog_id: CatalogIdString = None,
    ) -> CreateDatabaseResponse:
        """Creates a new database in a Data Catalog.

        :param database_input: The metadata for the database.
        :param catalog_id: The ID of the Data Catalog in which to create the database.
        :returns: CreateDatabaseResponse
        :raises InvalidInputException:
        :raises AlreadyExistsException:
        :raises ResourceNumberLimitExceededException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("CreateDevEndpoint")
    def create_dev_endpoint(
        self,
        context: RequestContext,
        endpoint_name: GenericString,
        role_arn: RoleArn,
        security_group_ids: StringList = None,
        subnet_id: GenericString = None,
        public_key: GenericString = None,
        public_keys: PublicKeysList = None,
        number_of_nodes: IntegerValue = None,
        worker_type: WorkerType = None,
        glue_version: GlueVersionString = None,
        number_of_workers: NullableInteger = None,
        extra_python_libs_s3_path: GenericString = None,
        extra_jars_s3_path: GenericString = None,
        security_configuration: NameString = None,
        tags: TagsMap = None,
        arguments: MapValue = None,
    ) -> CreateDevEndpointResponse:
        """Creates a new development endpoint.

        :param endpoint_name: The name to be assigned to the new ``DevEndpoint``.
        :param role_arn: The IAM role for the ``DevEndpoint``.
        :param security_group_ids: Security group IDs for the security groups to be used by the new
        ``DevEndpoint``.
        :param subnet_id: The subnet ID for the new ``DevEndpoint`` to use.
        :param public_key: The public key to be used by this ``DevEndpoint`` for authentication.
        :param public_keys: A list of public keys to be used by the development endpoints for
        authentication.
        :param number_of_nodes: The number of Glue Data Processing Units (DPUs) to allocate to this
        ``DevEndpoint``.
        :param worker_type: The type of predefined worker that is allocated to the development
        endpoint.
        :param glue_version: Glue version determines the versions of Apache Spark and Python that
        Glue supports.
        :param number_of_workers: The number of workers of a defined ``workerType`` that are allocated to
        the development endpoint.
        :param extra_python_libs_s3_path: The paths to one or more Python libraries in an Amazon S3 bucket that
        should be loaded in your ``DevEndpoint``.
        :param extra_jars_s3_path: The path to one or more Java ``.
        :param security_configuration: The name of the ``SecurityConfiguration`` structure to be used with this
        ``DevEndpoint``.
        :param tags: The tags to use with this DevEndpoint.
        :param arguments: A map of arguments used to configure the ``DevEndpoint``.
        :returns: CreateDevEndpointResponse
        :raises AccessDeniedException:
        :raises AlreadyExistsException:
        :raises IdempotentParameterMismatchException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises ValidationException:
        :raises ResourceNumberLimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateJob")
    def create_job(
        self,
        context: RequestContext,
        name: NameString,
        role: RoleString,
        command: JobCommand,
        description: DescriptionString = None,
        log_uri: UriString = None,
        execution_property: ExecutionProperty = None,
        default_arguments: GenericMap = None,
        non_overridable_arguments: GenericMap = None,
        connections: ConnectionsList = None,
        max_retries: MaxRetries = None,
        allocated_capacity: IntegerValue = None,
        timeout: Timeout = None,
        max_capacity: NullableDouble = None,
        security_configuration: NameString = None,
        tags: TagsMap = None,
        notification_property: NotificationProperty = None,
        glue_version: GlueVersionString = None,
        number_of_workers: NullableInteger = None,
        worker_type: WorkerType = None,
    ) -> CreateJobResponse:
        """Creates a new job definition.

        :param name: The name you assign to this job definition.
        :param role: The name or Amazon Resource Name (ARN) of the IAM role associated with
        this job.
        :param command: The ``JobCommand`` that runs this job.
        :param description: Description of the job being defined.
        :param log_uri: This field is reserved for future use.
        :param execution_property: An ``ExecutionProperty`` specifying the maximum number of concurrent
        runs allowed for this job.
        :param default_arguments: The default arguments for this job.
        :param non_overridable_arguments: Non-overridable arguments for this job, specified as name-value pairs.
        :param connections: The connections used for this job.
        :param max_retries: The maximum number of times to retry this job if it fails.
        :param allocated_capacity: This parameter is deprecated.
        :param timeout: The job timeout in minutes.
        :param max_capacity: For Glue version 1.
        :param security_configuration: The name of the ``SecurityConfiguration`` structure to be used with this
        job.
        :param tags: The tags to use with this job.
        :param notification_property: Specifies configuration properties of a job notification.
        :param glue_version: Glue version determines the versions of Apache Spark and Python that
        Glue supports.
        :param number_of_workers: The number of workers of a defined ``workerType`` that are allocated
        when a job runs.
        :param worker_type: The type of predefined worker that is allocated when a job runs.
        :returns: CreateJobResponse
        :raises InvalidInputException:
        :raises IdempotentParameterMismatchException:
        :raises AlreadyExistsException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("CreateMLTransform")
    def create_ml_transform(
        self,
        context: RequestContext,
        name: NameString,
        input_record_tables: GlueTables,
        parameters: TransformParameters,
        role: RoleString,
        description: DescriptionString = None,
        glue_version: GlueVersionString = None,
        max_capacity: NullableDouble = None,
        worker_type: WorkerType = None,
        number_of_workers: NullableInteger = None,
        timeout: Timeout = None,
        max_retries: NullableInteger = None,
        tags: TagsMap = None,
        transform_encryption: TransformEncryption = None,
    ) -> CreateMLTransformResponse:
        """Creates an Glue machine learning transform. This operation creates the
        transform and all the necessary parameters to train it.

        Call this operation as the first step in the process of using a machine
        learning transform (such as the ``FindMatches`` transform) for
        deduplicating data. You can provide an optional ``Description``, in
        addition to the parameters that you want to use for your algorithm.

        You must also specify certain parameters for the tasks that Glue runs on
        your behalf as part of learning from your data and creating a
        high-quality machine learning transform. These parameters include
        ``Role``, and optionally, ``AllocatedCapacity``, ``Timeout``, and
        ``MaxRetries``. For more information, see
        `Jobs <https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-jobs-job.html>`__.

        :param name: The unique name that you give the transform when you create it.
        :param input_record_tables: A list of Glue table definitions used by the transform.
        :param parameters: The algorithmic parameters that are specific to the transform type used.
        :param role: The name or Amazon Resource Name (ARN) of the IAM role with the required
        permissions.
        :param description: A description of the machine learning transform that is being defined.
        :param glue_version: This value determines which version of Glue this machine learning
        transform is compatible with.
        :param max_capacity: The number of Glue data processing units (DPUs) that are allocated to
        task runs for this transform.
        :param worker_type: The type of predefined worker that is allocated when this task runs.
        :param number_of_workers: The number of workers of a defined ``workerType`` that are allocated
        when this task runs.
        :param timeout: The timeout of the task run for this transform in minutes.
        :param max_retries: The maximum number of times to retry a task for this transform after a
        task run fails.
        :param tags: The tags to use with this machine learning transform.
        :param transform_encryption: The encryption-at-rest settings of the transform that apply to accessing
        user data.
        :returns: CreateMLTransformResponse
        :raises AlreadyExistsException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises AccessDeniedException:
        :raises ResourceNumberLimitExceededException:
        :raises IdempotentParameterMismatchException:
        """
        raise NotImplementedError

    @handler("CreatePartition")
    def create_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partition_input: PartitionInput,
        catalog_id: CatalogIdString = None,
    ) -> CreatePartitionResponse:
        """Creates a new partition.

        :param database_name: The name of the metadata database in which the partition is to be
        created.
        :param table_name: The name of the metadata table in which the partition is to be created.
        :param partition_input: A ``PartitionInput`` structure defining the partition to be created.
        :param catalog_id: The Amazon Web Services account ID of the catalog in which the partition
        is to be created.
        :returns: CreatePartitionResponse
        :raises InvalidInputException:
        :raises AlreadyExistsException:
        :raises ResourceNumberLimitExceededException:
        :raises InternalServiceException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("CreatePartitionIndex")
    def create_partition_index(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partition_index: PartitionIndex,
        catalog_id: CatalogIdString = None,
    ) -> CreatePartitionIndexResponse:
        """Creates a specified partition index in an existing table.

        :param database_name: Specifies the name of a database in which you want to create a partition
        index.
        :param table_name: Specifies the name of a table in which you want to create a partition
        index.
        :param partition_index: Specifies a ``PartitionIndex`` structure to create a partition index in
        an existing table.
        :param catalog_id: The catalog ID where the table resides.
        :returns: CreatePartitionIndexResponse
        :raises AlreadyExistsException:
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises ResourceNumberLimitExceededException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("CreateRegistry")
    def create_registry(
        self,
        context: RequestContext,
        registry_name: SchemaRegistryNameString,
        description: DescriptionString = None,
        tags: TagsMap = None,
    ) -> CreateRegistryResponse:
        """Creates a new registry which may be used to hold a collection of
        schemas.

        :param registry_name: Name of the registry to be created of max length of 255, and may only
        contain letters, numbers, hyphen, underscore, dollar sign, or hash mark.
        :param description: A description of the registry.
        :param tags: Amazon Web Services tags that contain a key value pair and may be
        searched by console, command line, or API.
        :returns: CreateRegistryResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises AlreadyExistsException:
        :raises ResourceNumberLimitExceededException:
        :raises ConcurrentModificationException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("CreateSchema")
    def create_schema(
        self,
        context: RequestContext,
        schema_name: SchemaRegistryNameString,
        data_format: DataFormat,
        registry_id: RegistryId = None,
        compatibility: Compatibility = None,
        description: DescriptionString = None,
        tags: TagsMap = None,
        schema_definition: SchemaDefinitionString = None,
    ) -> CreateSchemaResponse:
        """Creates a new schema set and registers the schema definition. Returns an
        error if the schema set already exists without actually registering the
        version.

        When the schema set is created, a version checkpoint will be set to the
        first version. Compatibility mode "DISABLED" restricts any additional
        schema versions from being added after the first schema version. For all
        other compatibility modes, validation of compatibility settings will be
        applied only from the second version onwards when the
        ``RegisterSchemaVersion`` API is used.

        When this API is called without a ``RegistryId``, this will create an
        entry for a "default-registry" in the registry database tables, if it is
        not already present.

        :param schema_name: Name of the schema to be created of max length of 255, and may only
        contain letters, numbers, hyphen, underscore, dollar sign, or hash mark.
        :param data_format: The data format of the schema definition.
        :param registry_id: This is a wrapper shape to contain the registry identity fields.
        :param compatibility: The compatibility mode of the schema.
        :param description: An optional description of the schema.
        :param tags: Amazon Web Services tags that contain a key value pair and may be
        searched by console, command line, or API.
        :param schema_definition: The schema definition using the ``DataFormat`` setting for
        ``SchemaName``.
        :returns: CreateSchemaResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises AlreadyExistsException:
        :raises ResourceNumberLimitExceededException:
        :raises ConcurrentModificationException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("CreateScript")
    def create_script(
        self,
        context: RequestContext,
        dag_nodes: DagNodes = None,
        dag_edges: DagEdges = None,
        language: Language = None,
    ) -> CreateScriptResponse:
        """Transforms a directed acyclic graph (DAG) into code.

        :param dag_nodes: A list of the nodes in the DAG.
        :param dag_edges: A list of the edges in the DAG.
        :param language: The programming language of the resulting code from the DAG.
        :returns: CreateScriptResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("CreateSecurityConfiguration")
    def create_security_configuration(
        self,
        context: RequestContext,
        name: NameString,
        encryption_configuration: EncryptionConfiguration,
    ) -> CreateSecurityConfigurationResponse:
        """Creates a new security configuration. A security configuration is a set
        of security properties that can be used by Glue. You can use a security
        configuration to encrypt data at rest. For information about using
        security configurations in Glue, see `Encrypting Data Written by
        Crawlers, Jobs, and Development
        Endpoints <https://docs.aws.amazon.com/glue/latest/dg/encryption-security-configuration.html>`__.

        :param name: The name for the new security configuration.
        :param encryption_configuration: The encryption configuration for the new security configuration.
        :returns: CreateSecurityConfigurationResponse
        :raises AlreadyExistsException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateSession")
    def create_session(
        self,
        context: RequestContext,
        id: NameString,
        role: OrchestrationRoleArn,
        command: SessionCommand,
        description: DescriptionString = None,
        timeout: Timeout = None,
        idle_timeout: Timeout = None,
        default_arguments: OrchestrationArgumentsMap = None,
        connections: ConnectionsList = None,
        max_capacity: NullableDouble = None,
        number_of_workers: NullableInteger = None,
        worker_type: WorkerType = None,
        security_configuration: NameString = None,
        glue_version: GlueVersionString = None,
        tags: TagsMap = None,
        request_origin: OrchestrationNameString = None,
    ) -> CreateSessionResponse:
        """Creates a new session.

        :param id: The ID of the session request.
        :param role: The IAM Role ARN.
        :param command: The ``SessionCommand`` that runs the job.
        :param description: The description of the session.
        :param timeout: The number of seconds before request times out.
        :param idle_timeout: The number of seconds when idle before request times out.
        :param default_arguments: A map array of key-value pairs.
        :param connections: The number of connections to use for the session.
        :param max_capacity: The number of AWS Glue data processing units (DPUs) that can be
        allocated when the job runs.
        :param number_of_workers: The number of workers to use for the session.
        :param worker_type: The Worker Type.
        :param security_configuration: The name of the SecurityConfiguration structure to be used with the
        session.
        :param glue_version: The Glue version determines the versions of Apache Spark and Python that
        AWS Glue supports.
        :param tags: The map of key value pairs (tags) belonging to the session.
        :param request_origin: The origin of the request.
        :returns: CreateSessionResponse
        :raises AccessDeniedException:
        :raises IdempotentParameterMismatchException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises ValidationException:
        :raises AlreadyExistsException:
        :raises ResourceNumberLimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateTable")
    def create_table(
        self,
        context: RequestContext,
        database_name: NameString,
        table_input: TableInput,
        catalog_id: CatalogIdString = None,
        partition_indexes: PartitionIndexList = None,
        transaction_id: TransactionIdString = None,
    ) -> CreateTableResponse:
        """Creates a new table definition in the Data Catalog.

        :param database_name: The catalog database in which to create the new table.
        :param table_input: The ``TableInput`` object that defines the metadata table to create in
        the catalog.
        :param catalog_id: The ID of the Data Catalog in which to create the ``Table``.
        :param partition_indexes: A list of partition indexes, ``PartitionIndex`` structures, to create in
        the table.
        :param transaction_id: The ID of the transaction.
        :returns: CreateTableResponse
        :raises AlreadyExistsException:
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises ResourceNumberLimitExceededException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises ConcurrentModificationException:
        :raises ResourceNotReadyException:
        """
        raise NotImplementedError

    @handler("CreateTrigger", expand=False)
    def create_trigger(
        self, context: RequestContext, request: CreateTriggerRequest
    ) -> CreateTriggerResponse:
        """Creates a new trigger.

        :param name: The name of the trigger.
        :param type: The type of the new trigger.
        :param actions: The actions initiated by this trigger when it fires.
        :param workflow_name: The name of the workflow associated with the trigger.
        :param schedule: A ``cron`` expression used to specify the schedule (see `Time-Based
        Schedules for Jobs and
        Crawlers <https://docs.
        :param predicate: A predicate to specify when the new trigger should fire.
        :param description: A description of the new trigger.
        :param start_on_creation: Set to ``true`` to start ``SCHEDULED`` and ``CONDITIONAL`` triggers when
        created.
        :param tags: The tags to use with this trigger.
        :param event_batching_condition: Batch condition that must be met (specified number of events received or
        batch time window expired) before EventBridge event trigger fires.
        :returns: CreateTriggerResponse
        :raises AlreadyExistsException:
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises IdempotentParameterMismatchException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("CreateUserDefinedFunction")
    def create_user_defined_function(
        self,
        context: RequestContext,
        database_name: NameString,
        function_input: UserDefinedFunctionInput,
        catalog_id: CatalogIdString = None,
    ) -> CreateUserDefinedFunctionResponse:
        """Creates a new function definition in the Data Catalog.

        :param database_name: The name of the catalog database in which to create the function.
        :param function_input: A ``FunctionInput`` object that defines the function to create in the
        Data Catalog.
        :param catalog_id: The ID of the Data Catalog in which to create the function.
        :returns: CreateUserDefinedFunctionResponse
        :raises AlreadyExistsException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("CreateWorkflow")
    def create_workflow(
        self,
        context: RequestContext,
        name: NameString,
        description: GenericString = None,
        default_run_properties: WorkflowRunProperties = None,
        tags: TagsMap = None,
        max_concurrent_runs: NullableInteger = None,
    ) -> CreateWorkflowResponse:
        """Creates a new workflow.

        :param name: The name to be assigned to the workflow.
        :param description: A description of the workflow.
        :param default_run_properties: A collection of properties to be used as part of each execution of the
        workflow.
        :param tags: The tags to be used with this workflow.
        :param max_concurrent_runs: You can use this parameter to prevent unwanted multiple updates to data,
        to control costs, or in some cases, to prevent exceeding the maximum
        number of concurrent runs of any of the component jobs.
        :returns: CreateWorkflowResponse
        :raises AlreadyExistsException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteBlueprint")
    def delete_blueprint(
        self, context: RequestContext, name: NameString
    ) -> DeleteBlueprintResponse:
        """Deletes an existing blueprint.

        :param name: The name of the blueprint to delete.
        :returns: DeleteBlueprintResponse
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("DeleteClassifier")
    def delete_classifier(
        self, context: RequestContext, name: NameString
    ) -> DeleteClassifierResponse:
        """Removes a classifier from the Data Catalog.

        :param name: Name of the classifier to remove.
        :returns: DeleteClassifierResponse
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("DeleteColumnStatisticsForPartition")
    def delete_column_statistics_for_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partition_values: ValueStringList,
        column_name: NameString,
        catalog_id: CatalogIdString = None,
    ) -> DeleteColumnStatisticsForPartitionResponse:
        """Delete the partition column statistics of a column.

        The Identity and Access Management (IAM) permission required for this
        operation is ``DeletePartition``.

        :param database_name: The name of the catalog database where the partitions reside.
        :param table_name: The name of the partitions' table.
        :param partition_values: A list of partition values identifying the partition.
        :param column_name: Name of the column.
        :param catalog_id: The ID of the Data Catalog where the partitions in question reside.
        :returns: DeleteColumnStatisticsForPartitionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("DeleteColumnStatisticsForTable")
    def delete_column_statistics_for_table(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        column_name: NameString,
        catalog_id: CatalogIdString = None,
    ) -> DeleteColumnStatisticsForTableResponse:
        """Retrieves table statistics of columns.

        The Identity and Access Management (IAM) permission required for this
        operation is ``DeleteTable``.

        :param database_name: The name of the catalog database where the partitions reside.
        :param table_name: The name of the partitions' table.
        :param column_name: The name of the column.
        :param catalog_id: The ID of the Data Catalog where the partitions in question reside.
        :returns: DeleteColumnStatisticsForTableResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("DeleteConnection")
    def delete_connection(
        self,
        context: RequestContext,
        connection_name: NameString,
        catalog_id: CatalogIdString = None,
    ) -> DeleteConnectionResponse:
        """Deletes a connection from the Data Catalog.

        :param connection_name: The name of the connection to delete.
        :param catalog_id: The ID of the Data Catalog in which the connection resides.
        :returns: DeleteConnectionResponse
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("DeleteCrawler")
    def delete_crawler(self, context: RequestContext, name: NameString) -> DeleteCrawlerResponse:
        """Removes a specified crawler from the Glue Data Catalog, unless the
        crawler state is ``RUNNING``.

        :param name: The name of the crawler to remove.
        :returns: DeleteCrawlerResponse
        :raises EntityNotFoundException:
        :raises CrawlerRunningException:
        :raises SchedulerTransitioningException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("DeleteCustomEntityType")
    def delete_custom_entity_type(
        self, context: RequestContext, name: NameString
    ) -> DeleteCustomEntityTypeResponse:
        """Deletes a custom pattern by specifying its name.

        :param name: The name of the custom pattern that you want to delete.
        :returns: DeleteCustomEntityTypeResponse
        :raises EntityNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("DeleteDatabase")
    def delete_database(
        self, context: RequestContext, name: NameString, catalog_id: CatalogIdString = None
    ) -> DeleteDatabaseResponse:
        """Removes a specified database from a Data Catalog.

        After completing this operation, you no longer have access to the tables
        (and all table versions and partitions that might belong to the tables)
        and the user-defined functions in the deleted database. Glue deletes
        these "orphaned" resources asynchronously in a timely manner, at the
        discretion of the service.

        To ensure the immediate deletion of all related resources, before
        calling ``DeleteDatabase``, use ``DeleteTableVersion`` or
        ``BatchDeleteTableVersion``, ``DeletePartition`` or
        ``BatchDeletePartition``, ``DeleteUserDefinedFunction``, and
        ``DeleteTable`` or ``BatchDeleteTable``, to delete any resources that
        belong to the database.

        :param name: The name of the database to delete.
        :param catalog_id: The ID of the Data Catalog in which the database resides.
        :returns: DeleteDatabaseResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteDevEndpoint")
    def delete_dev_endpoint(
        self, context: RequestContext, endpoint_name: GenericString
    ) -> DeleteDevEndpointResponse:
        """Deletes a specified development endpoint.

        :param endpoint_name: The name of the ``DevEndpoint``.
        :returns: DeleteDevEndpointResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("DeleteJob")
    def delete_job(self, context: RequestContext, job_name: NameString) -> DeleteJobResponse:
        """Deletes a specified job definition. If the job definition is not found,
        no exception is thrown.

        :param job_name: The name of the job definition to delete.
        :returns: DeleteJobResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("DeleteMLTransform")
    def delete_ml_transform(
        self, context: RequestContext, transform_id: HashString
    ) -> DeleteMLTransformResponse:
        """Deletes an Glue machine learning transform. Machine learning transforms
        are a special type of transform that use machine learning to learn the
        details of the transformation to be performed by learning from examples
        provided by humans. These transformations are then saved by Glue. If you
        no longer need a transform, you can delete it by calling
        ``DeleteMLTransforms``. However, any Glue jobs that still reference the
        deleted transform will no longer succeed.

        :param transform_id: The unique identifier of the transform to delete.
        :returns: DeleteMLTransformResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("DeletePartition")
    def delete_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partition_values: ValueStringList,
        catalog_id: CatalogIdString = None,
    ) -> DeletePartitionResponse:
        """Deletes a specified partition.

        :param database_name: The name of the catalog database in which the table in question resides.
        :param table_name: The name of the table that contains the partition to be deleted.
        :param partition_values: The values that define the partition.
        :param catalog_id: The ID of the Data Catalog where the partition to be deleted resides.
        :returns: DeletePartitionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("DeletePartitionIndex")
    def delete_partition_index(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        index_name: NameString,
        catalog_id: CatalogIdString = None,
    ) -> DeletePartitionIndexResponse:
        """Deletes a specified partition index from an existing table.

        :param database_name: Specifies the name of a database from which you want to delete a
        partition index.
        :param table_name: Specifies the name of a table from which you want to delete a partition
        index.
        :param index_name: The name of the partition index to be deleted.
        :param catalog_id: The catalog ID where the table resides.
        :returns: DeletePartitionIndexResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises ConflictException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("DeleteRegistry")
    def delete_registry(
        self, context: RequestContext, registry_id: RegistryId
    ) -> DeleteRegistryResponse:
        """Delete the entire registry including schema and all of its versions. To
        get the status of the delete operation, you can call the ``GetRegistry``
        API after the asynchronous call. Deleting a registry will deactivate all
        online operations for the registry such as the ``UpdateRegistry``,
        ``CreateSchema``, ``UpdateSchema``, and ``RegisterSchemaVersion`` APIs.

        :param registry_id: This is a wrapper structure that may contain the registry name and
        Amazon Resource Name (ARN).
        :returns: DeleteRegistryResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteResourcePolicy")
    def delete_resource_policy(
        self,
        context: RequestContext,
        policy_hash_condition: HashString = None,
        resource_arn: GlueResourceArn = None,
    ) -> DeleteResourcePolicyResponse:
        """Deletes a specified policy.

        :param policy_hash_condition: The hash value returned when this policy was set.
        :param resource_arn: The ARN of the Glue resource for the resource policy to be deleted.
        :returns: DeleteResourcePolicyResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises ConditionCheckFailureException:
        """
        raise NotImplementedError

    @handler("DeleteSchema")
    def delete_schema(self, context: RequestContext, schema_id: SchemaId) -> DeleteSchemaResponse:
        """Deletes the entire schema set, including the schema set and all of its
        versions. To get the status of the delete operation, you can call
        ``GetSchema`` API after the asynchronous call. Deleting a registry will
        deactivate all online operations for the schema, such as the
        ``GetSchemaByDefinition``, and ``RegisterSchemaVersion`` APIs.

        :param schema_id: This is a wrapper structure that may contain the schema name and Amazon
        Resource Name (ARN).
        :returns: DeleteSchemaResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteSchemaVersions")
    def delete_schema_versions(
        self, context: RequestContext, schema_id: SchemaId, versions: VersionsString
    ) -> DeleteSchemaVersionsResponse:
        """Remove versions from the specified schema. A version number or range may
        be supplied. If the compatibility mode forbids deleting of a version
        that is necessary, such as BACKWARDS_FULL, an error is returned. Calling
        the ``GetSchemaVersions`` API after this call will list the status of
        the deleted versions.

        When the range of version numbers contain check pointed version, the API
        will return a 409 conflict and will not proceed with the deletion. You
        have to remove the checkpoint first using the ``DeleteSchemaCheckpoint``
        API before using this API.

        You cannot use the ``DeleteSchemaVersions`` API to delete the first
        schema version in the schema set. The first schema version can only be
        deleted by the ``DeleteSchema`` API. This operation will also delete the
        attached ``SchemaVersionMetadata`` under the schema versions. Hard
        deletes will be enforced on the database.

        If the compatibility mode forbids deleting of a version that is
        necessary, such as BACKWARDS_FULL, an error is returned.

        :param schema_id: This is a wrapper structure that may contain the schema name and Amazon
        Resource Name (ARN).
        :param versions: A version range may be supplied which may be of the format:

        -  a single version number, 5

        -  a range, 5-8 : deletes versions 5, 6, 7, 8.
        :returns: DeleteSchemaVersionsResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteSecurityConfiguration")
    def delete_security_configuration(
        self, context: RequestContext, name: NameString
    ) -> DeleteSecurityConfigurationResponse:
        """Deletes a specified security configuration.

        :param name: The name of the security configuration to delete.
        :returns: DeleteSecurityConfigurationResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("DeleteSession")
    def delete_session(
        self,
        context: RequestContext,
        id: NameString,
        request_origin: OrchestrationNameString = None,
    ) -> DeleteSessionResponse:
        """Deletes the session.

        :param id: The ID of the session to be deleted.
        :param request_origin: The name of the origin of the delete session request.
        :returns: DeleteSessionResponse
        :raises AccessDeniedException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises IllegalSessionStateException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteTable")
    def delete_table(
        self,
        context: RequestContext,
        database_name: NameString,
        name: NameString,
        catalog_id: CatalogIdString = None,
        transaction_id: TransactionIdString = None,
    ) -> DeleteTableResponse:
        """Removes a table definition from the Data Catalog.

        After completing this operation, you no longer have access to the table
        versions and partitions that belong to the deleted table. Glue deletes
        these "orphaned" resources asynchronously in a timely manner, at the
        discretion of the service.

        To ensure the immediate deletion of all related resources, before
        calling ``DeleteTable``, use ``DeleteTableVersion`` or
        ``BatchDeleteTableVersion``, and ``DeletePartition`` or
        ``BatchDeletePartition``, to delete any resources that belong to the
        table.

        :param database_name: The name of the catalog database in which the table resides.
        :param name: The name of the table to be deleted.
        :param catalog_id: The ID of the Data Catalog where the table resides.
        :param transaction_id: The transaction ID at which to delete the table contents.
        :returns: DeleteTableResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ConcurrentModificationException:
        :raises ResourceNotReadyException:
        """
        raise NotImplementedError

    @handler("DeleteTableVersion")
    def delete_table_version(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        version_id: VersionString,
        catalog_id: CatalogIdString = None,
    ) -> DeleteTableVersionResponse:
        """Deletes a specified version of a table.

        :param database_name: The database in the catalog in which the table resides.
        :param table_name: The name of the table.
        :param version_id: The ID of the table version to be deleted.
        :param catalog_id: The ID of the Data Catalog where the tables reside.
        :returns: DeleteTableVersionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("DeleteTrigger")
    def delete_trigger(self, context: RequestContext, name: NameString) -> DeleteTriggerResponse:
        """Deletes a specified trigger. If the trigger is not found, no exception
        is thrown.

        :param name: The name of the trigger to delete.
        :returns: DeleteTriggerResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeleteUserDefinedFunction")
    def delete_user_defined_function(
        self,
        context: RequestContext,
        database_name: NameString,
        function_name: NameString,
        catalog_id: CatalogIdString = None,
    ) -> DeleteUserDefinedFunctionResponse:
        """Deletes an existing function definition from the Data Catalog.

        :param database_name: The name of the catalog database where the function is located.
        :param function_name: The name of the function definition to be deleted.
        :param catalog_id: The ID of the Data Catalog where the function to be deleted is located.
        :returns: DeleteUserDefinedFunctionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("DeleteWorkflow")
    def delete_workflow(self, context: RequestContext, name: NameString) -> DeleteWorkflowResponse:
        """Deletes a workflow.

        :param name: Name of the workflow to be deleted.
        :returns: DeleteWorkflowResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("GetBlueprint")
    def get_blueprint(
        self,
        context: RequestContext,
        name: NameString,
        include_blueprint: NullableBoolean = None,
        include_parameter_spec: NullableBoolean = None,
    ) -> GetBlueprintResponse:
        """Retrieves the details of a blueprint.

        :param name: The name of the blueprint.
        :param include_blueprint: Specifies whether or not to include the blueprint in the response.
        :param include_parameter_spec: Specifies whether or not to include the parameter specification.
        :returns: GetBlueprintResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetBlueprintRun")
    def get_blueprint_run(
        self, context: RequestContext, blueprint_name: OrchestrationNameString, run_id: IdString
    ) -> GetBlueprintRunResponse:
        """Retrieves the details of a blueprint run.

        :param blueprint_name: The name of the blueprint.
        :param run_id: The run ID for the blueprint run you want to retrieve.
        :returns: GetBlueprintRunResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetBlueprintRuns")
    def get_blueprint_runs(
        self,
        context: RequestContext,
        blueprint_name: NameString,
        next_token: GenericString = None,
        max_results: PageSize = None,
    ) -> GetBlueprintRunsResponse:
        """Retrieves the details of blueprint runs for a specified blueprint.

        :param blueprint_name: The name of the blueprint.
        :param next_token: A continuation token, if this is a continuation request.
        :param max_results: The maximum size of a list to return.
        :returns: GetBlueprintRunsResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("GetCatalogImportStatus")
    def get_catalog_import_status(
        self, context: RequestContext, catalog_id: CatalogIdString = None
    ) -> GetCatalogImportStatusResponse:
        """Retrieves the status of a migration operation.

        :param catalog_id: The ID of the catalog to migrate.
        :returns: GetCatalogImportStatusResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetClassifier")
    def get_classifier(self, context: RequestContext, name: NameString) -> GetClassifierResponse:
        """Retrieve a classifier by name.

        :param name: Name of the classifier to retrieve.
        :returns: GetClassifierResponse
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetClassifiers")
    def get_classifiers(
        self, context: RequestContext, max_results: PageSize = None, next_token: Token = None
    ) -> GetClassifiersResponse:
        """Lists all classifier objects in the Data Catalog.

        :param max_results: The size of the list to return (optional).
        :param next_token: An optional continuation token.
        :returns: GetClassifiersResponse
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetColumnStatisticsForPartition")
    def get_column_statistics_for_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partition_values: ValueStringList,
        column_names: GetColumnNamesList,
        catalog_id: CatalogIdString = None,
    ) -> GetColumnStatisticsForPartitionResponse:
        """Retrieves partition statistics of columns.

        The Identity and Access Management (IAM) permission required for this
        operation is ``GetPartition``.

        :param database_name: The name of the catalog database where the partitions reside.
        :param table_name: The name of the partitions' table.
        :param partition_values: A list of partition values identifying the partition.
        :param column_names: A list of the column names.
        :param catalog_id: The ID of the Data Catalog where the partitions in question reside.
        :returns: GetColumnStatisticsForPartitionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetColumnStatisticsForTable")
    def get_column_statistics_for_table(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        column_names: GetColumnNamesList,
        catalog_id: CatalogIdString = None,
    ) -> GetColumnStatisticsForTableResponse:
        """Retrieves table statistics of columns.

        The Identity and Access Management (IAM) permission required for this
        operation is ``GetTable``.

        :param database_name: The name of the catalog database where the partitions reside.
        :param table_name: The name of the partitions' table.
        :param column_names: A list of the column names.
        :param catalog_id: The ID of the Data Catalog where the partitions in question reside.
        :returns: GetColumnStatisticsForTableResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetConnection")
    def get_connection(
        self,
        context: RequestContext,
        name: NameString,
        catalog_id: CatalogIdString = None,
        hide_password: Boolean = None,
    ) -> GetConnectionResponse:
        """Retrieves a connection definition from the Data Catalog.

        :param name: The name of the connection definition to retrieve.
        :param catalog_id: The ID of the Data Catalog in which the connection resides.
        :param hide_password: Allows you to retrieve the connection metadata without returning the
        password.
        :returns: GetConnectionResponse
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetConnections")
    def get_connections(
        self,
        context: RequestContext,
        catalog_id: CatalogIdString = None,
        filter: GetConnectionsFilter = None,
        hide_password: Boolean = None,
        next_token: Token = None,
        max_results: PageSize = None,
    ) -> GetConnectionsResponse:
        """Retrieves a list of connection definitions from the Data Catalog.

        :param catalog_id: The ID of the Data Catalog in which the connections reside.
        :param filter: A filter that controls which connections are returned.
        :param hide_password: Allows you to retrieve the connection metadata without returning the
        password.
        :param next_token: A continuation token, if this is a continuation call.
        :param max_results: The maximum number of connections to return in one response.
        :returns: GetConnectionsResponse
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetCrawler")
    def get_crawler(self, context: RequestContext, name: NameString) -> GetCrawlerResponse:
        """Retrieves metadata for a specified crawler.

        :param name: The name of the crawler to retrieve metadata for.
        :returns: GetCrawlerResponse
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetCrawlerMetrics")
    def get_crawler_metrics(
        self,
        context: RequestContext,
        crawler_name_list: CrawlerNameList = None,
        max_results: PageSize = None,
        next_token: Token = None,
    ) -> GetCrawlerMetricsResponse:
        """Retrieves metrics about specified crawlers.

        :param crawler_name_list: A list of the names of crawlers about which to retrieve metrics.
        :param max_results: The maximum size of a list to return.
        :param next_token: A continuation token, if this is a continuation call.
        :returns: GetCrawlerMetricsResponse
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetCrawlers")
    def get_crawlers(
        self, context: RequestContext, max_results: PageSize = None, next_token: Token = None
    ) -> GetCrawlersResponse:
        """Retrieves metadata for all crawlers defined in the customer account.

        :param max_results: The number of crawlers to return on each call.
        :param next_token: A continuation token, if this is a continuation request.
        :returns: GetCrawlersResponse
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetCustomEntityType")
    def get_custom_entity_type(
        self, context: RequestContext, name: NameString
    ) -> GetCustomEntityTypeResponse:
        """Retrieves the details of a custom pattern by specifying its name.

        :param name: The name of the custom pattern that you want to retrieve.
        :returns: GetCustomEntityTypeResponse
        :raises EntityNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetDataCatalogEncryptionSettings")
    def get_data_catalog_encryption_settings(
        self, context: RequestContext, catalog_id: CatalogIdString = None
    ) -> GetDataCatalogEncryptionSettingsResponse:
        """Retrieves the security configuration for a specified catalog.

        :param catalog_id: The ID of the Data Catalog to retrieve the security configuration for.
        :returns: GetDataCatalogEncryptionSettingsResponse
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetDatabase")
    def get_database(
        self, context: RequestContext, name: NameString, catalog_id: CatalogIdString = None
    ) -> GetDatabaseResponse:
        """Retrieves the definition of a specified database.

        :param name: The name of the database to retrieve.
        :param catalog_id: The ID of the Data Catalog in which the database resides.
        :returns: GetDatabaseResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetDatabases")
    def get_databases(
        self,
        context: RequestContext,
        catalog_id: CatalogIdString = None,
        next_token: Token = None,
        max_results: CatalogGetterPageSize = None,
        resource_share_type: ResourceShareType = None,
    ) -> GetDatabasesResponse:
        """Retrieves all databases defined in a given Data Catalog.

        :param catalog_id: The ID of the Data Catalog from which to retrieve ``Databases``.
        :param next_token: A continuation token, if this is a continuation call.
        :param max_results: The maximum number of databases to return in one response.
        :param resource_share_type: Allows you to specify that you want to list the databases shared with
        your account.
        :returns: GetDatabasesResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetDataflowGraph")
    def get_dataflow_graph(
        self, context: RequestContext, python_script: PythonScript = None
    ) -> GetDataflowGraphResponse:
        """Transforms a Python script into a directed acyclic graph (DAG).

        :param python_script: The Python script to transform.
        :returns: GetDataflowGraphResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetDevEndpoint")
    def get_dev_endpoint(
        self, context: RequestContext, endpoint_name: GenericString
    ) -> GetDevEndpointResponse:
        """Retrieves information about a specified development endpoint.

        When you create a development endpoint in a virtual private cloud (VPC),
        Glue returns only a private IP address, and the public IP address field
        is not populated. When you create a non-VPC development endpoint, Glue
        returns only a public IP address.

        :param endpoint_name: Name of the ``DevEndpoint`` to retrieve information for.
        :returns: GetDevEndpointResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("GetDevEndpoints")
    def get_dev_endpoints(
        self,
        context: RequestContext,
        max_results: PageSize = None,
        next_token: GenericString = None,
    ) -> GetDevEndpointsResponse:
        """Retrieves all the development endpoints in this AWS account.

        When you create a development endpoint in a virtual private cloud (VPC),
        Glue returns only a private IP address and the public IP address field
        is not populated. When you create a non-VPC development endpoint, Glue
        returns only a public IP address.

        :param max_results: The maximum size of information to return.
        :param next_token: A continuation token, if this is a continuation call.
        :returns: GetDevEndpointsResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("GetJob")
    def get_job(self, context: RequestContext, job_name: NameString) -> GetJobResponse:
        """Retrieves an existing job definition.

        :param job_name: The name of the job definition to retrieve.
        :returns: GetJobResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetJobBookmark")
    def get_job_bookmark(
        self, context: RequestContext, job_name: JobName, run_id: RunId = None
    ) -> GetJobBookmarkResponse:
        """Returns information on a job bookmark entry.

        :param job_name: The name of the job in question.
        :param run_id: The unique run identifier associated with this job run.
        :returns: GetJobBookmarkResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("GetJobRun")
    def get_job_run(
        self,
        context: RequestContext,
        job_name: NameString,
        run_id: IdString,
        predecessors_included: BooleanValue = None,
    ) -> GetJobRunResponse:
        """Retrieves the metadata for a given job run.

        :param job_name: Name of the job definition being run.
        :param run_id: The ID of the job run.
        :param predecessors_included: True if a list of predecessor runs should be returned.
        :returns: GetJobRunResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetJobRuns")
    def get_job_runs(
        self,
        context: RequestContext,
        job_name: NameString,
        next_token: GenericString = None,
        max_results: PageSize = None,
    ) -> GetJobRunsResponse:
        """Retrieves metadata for all runs of a given job definition.

        :param job_name: The name of the job definition for which to retrieve all job runs.
        :param next_token: A continuation token, if this is a continuation call.
        :param max_results: The maximum size of the response.
        :returns: GetJobRunsResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetJobs")
    def get_jobs(
        self,
        context: RequestContext,
        next_token: GenericString = None,
        max_results: PageSize = None,
    ) -> GetJobsResponse:
        """Retrieves all current job definitions.

        :param next_token: A continuation token, if this is a continuation call.
        :param max_results: The maximum size of the response.
        :returns: GetJobsResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetMLTaskRun")
    def get_ml_task_run(
        self, context: RequestContext, transform_id: HashString, task_run_id: HashString
    ) -> GetMLTaskRunResponse:
        """Gets details for a specific task run on a machine learning transform.
        Machine learning task runs are asynchronous tasks that Glue runs on your
        behalf as part of various machine learning workflows. You can check the
        stats of any task run by calling ``GetMLTaskRun`` with the ``TaskRunID``
        and its parent transform's ``TransformID``.

        :param transform_id: The unique identifier of the machine learning transform.
        :param task_run_id: The unique identifier of the task run.
        :returns: GetMLTaskRunResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetMLTaskRuns")
    def get_ml_task_runs(
        self,
        context: RequestContext,
        transform_id: HashString,
        next_token: PaginationToken = None,
        max_results: PageSize = None,
        filter: TaskRunFilterCriteria = None,
        sort: TaskRunSortCriteria = None,
    ) -> GetMLTaskRunsResponse:
        """Gets a list of runs for a machine learning transform. Machine learning
        task runs are asynchronous tasks that Glue runs on your behalf as part
        of various machine learning workflows. You can get a sortable,
        filterable list of machine learning task runs by calling
        ``GetMLTaskRuns`` with their parent transform's ``TransformID`` and
        other optional parameters as documented in this section.

        This operation returns a list of historic runs and must be paginated.

        :param transform_id: The unique identifier of the machine learning transform.
        :param next_token: A token for pagination of the results.
        :param max_results: The maximum number of results to return.
        :param filter: The filter criteria, in the ``TaskRunFilterCriteria`` structure, for the
        task run.
        :param sort: The sorting criteria, in the ``TaskRunSortCriteria`` structure, for the
        task run.
        :returns: GetMLTaskRunsResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetMLTransform")
    def get_ml_transform(
        self, context: RequestContext, transform_id: HashString
    ) -> GetMLTransformResponse:
        """Gets an Glue machine learning transform artifact and all its
        corresponding metadata. Machine learning transforms are a special type
        of transform that use machine learning to learn the details of the
        transformation to be performed by learning from examples provided by
        humans. These transformations are then saved by Glue. You can retrieve
        their metadata by calling ``GetMLTransform``.

        :param transform_id: The unique identifier of the transform, generated at the time that the
        transform was created.
        :returns: GetMLTransformResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetMLTransforms")
    def get_ml_transforms(
        self,
        context: RequestContext,
        next_token: PaginationToken = None,
        max_results: PageSize = None,
        filter: TransformFilterCriteria = None,
        sort: TransformSortCriteria = None,
    ) -> GetMLTransformsResponse:
        """Gets a sortable, filterable list of existing Glue machine learning
        transforms. Machine learning transforms are a special type of transform
        that use machine learning to learn the details of the transformation to
        be performed by learning from examples provided by humans. These
        transformations are then saved by Glue, and you can retrieve their
        metadata by calling ``GetMLTransforms``.

        :param next_token: A paginated token to offset the results.
        :param max_results: The maximum number of results to return.
        :param filter: The filter transformation criteria.
        :param sort: The sorting criteria.
        :returns: GetMLTransformsResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetMapping")
    def get_mapping(
        self,
        context: RequestContext,
        source: CatalogEntry,
        sinks: CatalogEntries = None,
        location: Location = None,
    ) -> GetMappingResponse:
        """Creates mappings.

        :param source: Specifies the source table.
        :param sinks: A list of target tables.
        :param location: Parameters for the mapping.
        :returns: GetMappingResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        """
        raise NotImplementedError

    @handler("GetPartition")
    def get_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partition_values: ValueStringList,
        catalog_id: CatalogIdString = None,
    ) -> GetPartitionResponse:
        """Retrieves information about a specified partition.

        :param database_name: The name of the catalog database where the partition resides.
        :param table_name: The name of the partition's table.
        :param partition_values: The values that define the partition.
        :param catalog_id: The ID of the Data Catalog where the partition in question resides.
        :returns: GetPartitionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetPartitionIndexes")
    def get_partition_indexes(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        catalog_id: CatalogIdString = None,
        next_token: Token = None,
    ) -> GetPartitionIndexesResponse:
        """Retrieves the partition indexes associated with a table.

        :param database_name: Specifies the name of a database from which you want to retrieve
        partition indexes.
        :param table_name: Specifies the name of a table for which you want to retrieve the
        partition indexes.
        :param catalog_id: The catalog ID where the table resides.
        :param next_token: A continuation token, included if this is a continuation call.
        :returns: GetPartitionIndexesResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("GetPartitions")
    def get_partitions(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        catalog_id: CatalogIdString = None,
        expression: PredicateString = None,
        next_token: Token = None,
        segment: Segment = None,
        max_results: PageSize = None,
        exclude_column_schema: BooleanNullable = None,
        transaction_id: TransactionIdString = None,
        query_as_of_time: Timestamp = None,
    ) -> GetPartitionsResponse:
        """Retrieves information about the partitions in a table.

        :param database_name: The name of the catalog database where the partitions reside.
        :param table_name: The name of the partitions' table.
        :param catalog_id: The ID of the Data Catalog where the partitions in question reside.
        :param expression: An expression that filters the partitions to be returned.
        :param next_token: A continuation token, if this is not the first call to retrieve these
        partitions.
        :param segment: The segment of the table's partitions to scan in this request.
        :param max_results: The maximum number of partitions to return in a single response.
        :param exclude_column_schema: When true, specifies not returning the partition column schema.
        :param transaction_id: The transaction ID at which to read the partition contents.
        :param query_as_of_time: The time as of when to read the partition contents.
        :returns: GetPartitionsResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises GlueEncryptionException:
        :raises InvalidStateException:
        :raises ResourceNotReadyException:
        """
        raise NotImplementedError

    @handler("GetPlan")
    def get_plan(
        self,
        context: RequestContext,
        mapping: MappingList,
        source: CatalogEntry,
        sinks: CatalogEntries = None,
        location: Location = None,
        language: Language = None,
        additional_plan_options_map: AdditionalPlanOptionsMap = None,
    ) -> GetPlanResponse:
        """Gets code to perform a specified mapping.

        :param mapping: The list of mappings from a source table to target tables.
        :param source: The source table.
        :param sinks: The target tables.
        :param location: The parameters for the mapping.
        :param language: The programming language of the code to perform the mapping.
        :param additional_plan_options_map: A map to hold additional optional key-value parameters.
        :returns: GetPlanResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetRegistry")
    def get_registry(self, context: RequestContext, registry_id: RegistryId) -> GetRegistryResponse:
        """Describes the specified registry in detail.

        :param registry_id: This is a wrapper structure that may contain the registry name and
        Amazon Resource Name (ARN).
        :returns: GetRegistryResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetResourcePolicies")
    def get_resource_policies(
        self, context: RequestContext, next_token: Token = None, max_results: PageSize = None
    ) -> GetResourcePoliciesResponse:
        """Retrieves the resource policies set on individual resources by Resource
        Access Manager during cross-account permission grants. Also retrieves
        the Data Catalog resource policy.

        If you enabled metadata encryption in Data Catalog settings, and you do
        not have permission on the KMS key, the operation can't return the Data
        Catalog resource policy.

        :param next_token: A continuation token, if this is a continuation request.
        :param max_results: The maximum size of a list to return.
        :returns: GetResourcePoliciesResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetResourcePolicy")
    def get_resource_policy(
        self, context: RequestContext, resource_arn: GlueResourceArn = None
    ) -> GetResourcePolicyResponse:
        """Retrieves a specified resource policy.

        :param resource_arn: The ARN of the Glue resource for which to retrieve the resource policy.
        :returns: GetResourcePolicyResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("GetSchema")
    def get_schema(self, context: RequestContext, schema_id: SchemaId) -> GetSchemaResponse:
        """Describes the specified schema in detail.

        :param schema_id: This is a wrapper structure to contain schema identity fields.
        :returns: GetSchemaResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetSchemaByDefinition")
    def get_schema_by_definition(
        self,
        context: RequestContext,
        schema_id: SchemaId,
        schema_definition: SchemaDefinitionString,
    ) -> GetSchemaByDefinitionResponse:
        """Retrieves a schema by the ``SchemaDefinition``. The schema definition is
        sent to the Schema Registry, canonicalized, and hashed. If the hash is
        matched within the scope of the ``SchemaName`` or ARN (or the default
        registry, if none is supplied), that schema’s metadata is returned.
        Otherwise, a 404 or NotFound error is returned. Schema versions in
        ``Deleted`` statuses will not be included in the results.

        :param schema_id: This is a wrapper structure to contain schema identity fields.
        :param schema_definition: The definition of the schema for which schema details are required.
        :returns: GetSchemaByDefinitionResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetSchemaVersion")
    def get_schema_version(
        self,
        context: RequestContext,
        schema_id: SchemaId = None,
        schema_version_id: SchemaVersionIdString = None,
        schema_version_number: SchemaVersionNumber = None,
    ) -> GetSchemaVersionResponse:
        """Get the specified schema by its unique ID assigned when a version of the
        schema is created or registered. Schema versions in Deleted status will
        not be included in the results.

        :param schema_id: This is a wrapper structure to contain schema identity fields.
        :param schema_version_id: The ``SchemaVersionId`` of the schema version.
        :param schema_version_number: The version number of the schema.
        :returns: GetSchemaVersionResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetSchemaVersionsDiff")
    def get_schema_versions_diff(
        self,
        context: RequestContext,
        schema_id: SchemaId,
        first_schema_version_number: SchemaVersionNumber,
        second_schema_version_number: SchemaVersionNumber,
        schema_diff_type: SchemaDiffType,
    ) -> GetSchemaVersionsDiffResponse:
        """Fetches the schema version difference in the specified difference type
        between two stored schema versions in the Schema Registry.

        This API allows you to compare two schema versions between two schema
        definitions under the same schema.

        :param schema_id: This is a wrapper structure to contain schema identity fields.
        :param first_schema_version_number: The first of the two schema versions to be compared.
        :param second_schema_version_number: The second of the two schema versions to be compared.
        :param schema_diff_type: Refers to ``SYNTAX_DIFF``, which is the currently supported diff type.
        :returns: GetSchemaVersionsDiffResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetSecurityConfiguration")
    def get_security_configuration(
        self, context: RequestContext, name: NameString
    ) -> GetSecurityConfigurationResponse:
        """Retrieves a specified security configuration.

        :param name: The name of the security configuration to retrieve.
        :returns: GetSecurityConfigurationResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetSecurityConfigurations")
    def get_security_configurations(
        self,
        context: RequestContext,
        max_results: PageSize = None,
        next_token: GenericString = None,
    ) -> GetSecurityConfigurationsResponse:
        """Retrieves a list of all security configurations.

        :param max_results: The maximum number of results to return.
        :param next_token: A continuation token, if this is a continuation call.
        :returns: GetSecurityConfigurationsResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetSession")
    def get_session(
        self,
        context: RequestContext,
        id: NameString,
        request_origin: OrchestrationNameString = None,
    ) -> GetSessionResponse:
        """Retrieves the session.

        :param id: The ID of the session.
        :param request_origin: The origin of the request.
        :returns: GetSessionResponse
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("GetStatement")
    def get_statement(
        self,
        context: RequestContext,
        session_id: NameString,
        id: IntegerValue,
        request_origin: OrchestrationNameString = None,
    ) -> GetStatementResponse:
        """Retrieves the statement.

        :param session_id: The Session ID of the statement.
        :param id: The Id of the statement.
        :param request_origin: The origin of the request.
        :returns: GetStatementResponse
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises IllegalSessionStateException:
        """
        raise NotImplementedError

    @handler("GetTable")
    def get_table(
        self,
        context: RequestContext,
        database_name: NameString,
        name: NameString,
        catalog_id: CatalogIdString = None,
        transaction_id: TransactionIdString = None,
        query_as_of_time: Timestamp = None,
    ) -> GetTableResponse:
        """Retrieves the ``Table`` definition in a Data Catalog for a specified
        table.

        :param database_name: The name of the database in the catalog in which the table resides.
        :param name: The name of the table for which to retrieve the definition.
        :param catalog_id: The ID of the Data Catalog where the table resides.
        :param transaction_id: The transaction ID at which to read the table contents.
        :param query_as_of_time: The time as of when to read the table contents.
        :returns: GetTableResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises ResourceNotReadyException:
        """
        raise NotImplementedError

    @handler("GetTableVersion")
    def get_table_version(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        catalog_id: CatalogIdString = None,
        version_id: VersionString = None,
    ) -> GetTableVersionResponse:
        """Retrieves a specified version of a table.

        :param database_name: The database in the catalog in which the table resides.
        :param table_name: The name of the table.
        :param catalog_id: The ID of the Data Catalog where the tables reside.
        :param version_id: The ID value of the table version to be retrieved.
        :returns: GetTableVersionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetTableVersions")
    def get_table_versions(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        catalog_id: CatalogIdString = None,
        next_token: Token = None,
        max_results: CatalogGetterPageSize = None,
    ) -> GetTableVersionsResponse:
        """Retrieves a list of strings that identify available versions of a
        specified table.

        :param database_name: The database in the catalog in which the table resides.
        :param table_name: The name of the table.
        :param catalog_id: The ID of the Data Catalog where the tables reside.
        :param next_token: A continuation token, if this is not the first call.
        :param max_results: The maximum number of table versions to return in one response.
        :returns: GetTableVersionsResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetTables")
    def get_tables(
        self,
        context: RequestContext,
        database_name: NameString,
        catalog_id: CatalogIdString = None,
        expression: FilterString = None,
        next_token: Token = None,
        max_results: CatalogGetterPageSize = None,
        transaction_id: TransactionIdString = None,
        query_as_of_time: Timestamp = None,
    ) -> GetTablesResponse:
        """Retrieves the definitions of some or all of the tables in a given
        ``Database``.

        :param database_name: The database in the catalog whose tables to list.
        :param catalog_id: The ID of the Data Catalog where the tables reside.
        :param expression: A regular expression pattern.
        :param next_token: A continuation token, included if this is a continuation call.
        :param max_results: The maximum number of tables to return in a single response.
        :param transaction_id: The transaction ID at which to read the table contents.
        :param query_as_of_time: The time as of when to read the table contents.
        :returns: GetTablesResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetTags")
    def get_tags(self, context: RequestContext, resource_arn: GlueResourceArn) -> GetTagsResponse:
        """Retrieves a list of tags associated with a resource.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource for which to retrieve
        tags.
        :returns: GetTagsResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        """
        raise NotImplementedError

    @handler("GetTrigger")
    def get_trigger(self, context: RequestContext, name: NameString) -> GetTriggerResponse:
        """Retrieves the definition of a trigger.

        :param name: The name of the trigger to retrieve.
        :returns: GetTriggerResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetTriggers")
    def get_triggers(
        self,
        context: RequestContext,
        next_token: GenericString = None,
        dependent_job_name: NameString = None,
        max_results: PageSize = None,
    ) -> GetTriggersResponse:
        """Gets all the triggers associated with a job.

        :param next_token: A continuation token, if this is a continuation call.
        :param dependent_job_name: The name of the job to retrieve triggers for.
        :param max_results: The maximum size of the response.
        :returns: GetTriggersResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetUnfilteredPartitionMetadata")
    def get_unfiltered_partition_metadata(
        self,
        context: RequestContext,
        catalog_id: CatalogIdString,
        database_name: NameString,
        table_name: NameString,
        partition_values: ValueStringList,
        supported_permission_types: PermissionTypeList,
        audit_context: AuditContext = None,
    ) -> GetUnfilteredPartitionMetadataResponse:
        """

        :param catalog_id: .
        :param database_name: .
        :param table_name: .
        :param partition_values: .
        :param supported_permission_types: .
        :param audit_context: A structure containing information for audit.
        :returns: GetUnfilteredPartitionMetadataResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises PermissionTypeMismatchException:
        """
        raise NotImplementedError

    @handler("GetUnfilteredPartitionsMetadata")
    def get_unfiltered_partitions_metadata(
        self,
        context: RequestContext,
        catalog_id: CatalogIdString,
        database_name: NameString,
        table_name: NameString,
        supported_permission_types: PermissionTypeList,
        expression: PredicateString = None,
        audit_context: AuditContext = None,
        next_token: Token = None,
        segment: Segment = None,
        max_results: PageSize = None,
    ) -> GetUnfilteredPartitionsMetadataResponse:
        """

        :param catalog_id: .
        :param database_name: .
        :param table_name: .
        :param supported_permission_types: .
        :param expression: .
        :param audit_context: A structure containing information for audit.
        :param next_token: .
        :param segment: Defines a non-overlapping region of a table's partitions, allowing
        multiple requests to be run in parallel.
        :param max_results: .
        :returns: GetUnfilteredPartitionsMetadataResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises PermissionTypeMismatchException:
        """
        raise NotImplementedError

    @handler("GetUnfilteredTableMetadata")
    def get_unfiltered_table_metadata(
        self,
        context: RequestContext,
        catalog_id: CatalogIdString,
        database_name: NameString,
        name: NameString,
        supported_permission_types: PermissionTypeList,
        audit_context: AuditContext = None,
    ) -> GetUnfilteredTableMetadataResponse:
        """

        :param catalog_id: .
        :param database_name: .
        :param name: .
        :param supported_permission_types: .
        :param audit_context: A structure containing information for audit.
        :returns: GetUnfilteredTableMetadataResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises PermissionTypeMismatchException:
        """
        raise NotImplementedError

    @handler("GetUserDefinedFunction")
    def get_user_defined_function(
        self,
        context: RequestContext,
        database_name: NameString,
        function_name: NameString,
        catalog_id: CatalogIdString = None,
    ) -> GetUserDefinedFunctionResponse:
        """Retrieves a specified function definition from the Data Catalog.

        :param database_name: The name of the catalog database where the function is located.
        :param function_name: The name of the function.
        :param catalog_id: The ID of the Data Catalog where the function to be retrieved is
        located.
        :returns: GetUserDefinedFunctionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetUserDefinedFunctions")
    def get_user_defined_functions(
        self,
        context: RequestContext,
        pattern: NameString,
        catalog_id: CatalogIdString = None,
        database_name: NameString = None,
        next_token: Token = None,
        max_results: CatalogGetterPageSize = None,
    ) -> GetUserDefinedFunctionsResponse:
        """Retrieves multiple function definitions from the Data Catalog.

        :param pattern: An optional function-name pattern string that filters the function
        definitions returned.
        :param catalog_id: The ID of the Data Catalog where the functions to be retrieved are
        located.
        :param database_name: The name of the catalog database where the functions are located.
        :param next_token: A continuation token, if this is a continuation call.
        :param max_results: The maximum number of functions to return in one response.
        :returns: GetUserDefinedFunctionsResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("GetWorkflow")
    def get_workflow(
        self, context: RequestContext, name: NameString, include_graph: NullableBoolean = None
    ) -> GetWorkflowResponse:
        """Retrieves resource metadata for a workflow.

        :param name: The name of the workflow to retrieve.
        :param include_graph: Specifies whether to include a graph when returning the workflow
        resource metadata.
        :returns: GetWorkflowResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetWorkflowRun")
    def get_workflow_run(
        self,
        context: RequestContext,
        name: NameString,
        run_id: IdString,
        include_graph: NullableBoolean = None,
    ) -> GetWorkflowRunResponse:
        """Retrieves the metadata for a given workflow run.

        :param name: Name of the workflow being run.
        :param run_id: The ID of the workflow run.
        :param include_graph: Specifies whether to include the workflow graph in response or not.
        :returns: GetWorkflowRunResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetWorkflowRunProperties")
    def get_workflow_run_properties(
        self, context: RequestContext, name: NameString, run_id: IdString
    ) -> GetWorkflowRunPropertiesResponse:
        """Retrieves the workflow run properties which were set during the run.

        :param name: Name of the workflow which was run.
        :param run_id: The ID of the workflow run whose run properties should be returned.
        :returns: GetWorkflowRunPropertiesResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("GetWorkflowRuns")
    def get_workflow_runs(
        self,
        context: RequestContext,
        name: NameString,
        include_graph: NullableBoolean = None,
        next_token: GenericString = None,
        max_results: PageSize = None,
    ) -> GetWorkflowRunsResponse:
        """Retrieves metadata for all runs of a given workflow.

        :param name: Name of the workflow whose metadata of runs should be returned.
        :param include_graph: Specifies whether to include the workflow graph in response or not.
        :param next_token: The maximum size of the response.
        :param max_results: The maximum number of workflow runs to be included in the response.
        :returns: GetWorkflowRunsResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ImportCatalogToGlue")
    def import_catalog_to_glue(
        self, context: RequestContext, catalog_id: CatalogIdString = None
    ) -> ImportCatalogToGlueResponse:
        """Imports an existing Amazon Athena Data Catalog to Glue.

        :param catalog_id: The ID of the catalog to import.
        :returns: ImportCatalogToGlueResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ListBlueprints")
    def list_blueprints(
        self,
        context: RequestContext,
        next_token: GenericString = None,
        max_results: PageSize = None,
        tags: TagsMap = None,
    ) -> ListBlueprintsResponse:
        """Lists all the blueprint names in an account.

        :param next_token: A continuation token, if this is a continuation request.
        :param max_results: The maximum size of a list to return.
        :param tags: Filters the list by an Amazon Web Services resource tag.
        :returns: ListBlueprintsResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ListCrawlers")
    def list_crawlers(
        self,
        context: RequestContext,
        max_results: PageSize = None,
        next_token: Token = None,
        tags: TagsMap = None,
    ) -> ListCrawlersResponse:
        """Retrieves the names of all crawler resources in this Amazon Web Services
        account, or the resources with the specified tag. This operation allows
        you to see which resources are available in your account, and their
        names.

        This operation takes the optional ``Tags`` field, which you can use as a
        filter on the response so that tagged resources can be retrieved as a
        group. If you choose to use tags filtering, only resources with the tag
        are retrieved.

        :param max_results: The maximum size of a list to return.
        :param next_token: A continuation token, if this is a continuation request.
        :param tags: Specifies to return only these tagged resources.
        :returns: ListCrawlersResponse
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ListCustomEntityTypes")
    def list_custom_entity_types(
        self,
        context: RequestContext,
        next_token: PaginationToken = None,
        max_results: PageSize = None,
    ) -> ListCustomEntityTypesResponse:
        """Lists all the custom patterns that have been created.

        :param next_token: A paginated token to offset the results.
        :param max_results: The maximum number of results to return.
        :returns: ListCustomEntityTypesResponse
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("ListDevEndpoints")
    def list_dev_endpoints(
        self,
        context: RequestContext,
        next_token: GenericString = None,
        max_results: PageSize = None,
        tags: TagsMap = None,
    ) -> ListDevEndpointsResponse:
        """Retrieves the names of all ``DevEndpoint`` resources in this Amazon Web
        Services account, or the resources with the specified tag. This
        operation allows you to see which resources are available in your
        account, and their names.

        This operation takes the optional ``Tags`` field, which you can use as a
        filter on the response so that tagged resources can be retrieved as a
        group. If you choose to use tags filtering, only resources with the tag
        are retrieved.

        :param next_token: A continuation token, if this is a continuation request.
        :param max_results: The maximum size of a list to return.
        :param tags: Specifies to return only these tagged resources.
        :returns: ListDevEndpointsResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ListJobs")
    def list_jobs(
        self,
        context: RequestContext,
        next_token: GenericString = None,
        max_results: PageSize = None,
        tags: TagsMap = None,
    ) -> ListJobsResponse:
        """Retrieves the names of all job resources in this Amazon Web Services
        account, or the resources with the specified tag. This operation allows
        you to see which resources are available in your account, and their
        names.

        This operation takes the optional ``Tags`` field, which you can use as a
        filter on the response so that tagged resources can be retrieved as a
        group. If you choose to use tags filtering, only resources with the tag
        are retrieved.

        :param next_token: A continuation token, if this is a continuation request.
        :param max_results: The maximum size of a list to return.
        :param tags: Specifies to return only these tagged resources.
        :returns: ListJobsResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ListMLTransforms")
    def list_ml_transforms(
        self,
        context: RequestContext,
        next_token: PaginationToken = None,
        max_results: PageSize = None,
        filter: TransformFilterCriteria = None,
        sort: TransformSortCriteria = None,
        tags: TagsMap = None,
    ) -> ListMLTransformsResponse:
        """Retrieves a sortable, filterable list of existing Glue machine learning
        transforms in this Amazon Web Services account, or the resources with
        the specified tag. This operation takes the optional ``Tags`` field,
        which you can use as a filter of the responses so that tagged resources
        can be retrieved as a group. If you choose to use tag filtering, only
        resources with the tags are retrieved.

        :param next_token: A continuation token, if this is a continuation request.
        :param max_results: The maximum size of a list to return.
        :param filter: A ``TransformFilterCriteria`` used to filter the machine learning
        transforms.
        :param sort: A ``TransformSortCriteria`` used to sort the machine learning
        transforms.
        :param tags: Specifies to return only these tagged resources.
        :returns: ListMLTransformsResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("ListRegistries")
    def list_registries(
        self,
        context: RequestContext,
        max_results: MaxResultsNumber = None,
        next_token: SchemaRegistryTokenString = None,
    ) -> ListRegistriesResponse:
        """Returns a list of registries that you have created, with minimal
        registry information. Registries in the ``Deleting`` status will not be
        included in the results. Empty results will be returned if there are no
        registries available.

        :param max_results: Maximum number of results required per page.
        :param next_token: A continuation token, if this is a continuation call.
        :returns: ListRegistriesResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("ListSchemaVersions")
    def list_schema_versions(
        self,
        context: RequestContext,
        schema_id: SchemaId,
        max_results: MaxResultsNumber = None,
        next_token: SchemaRegistryTokenString = None,
    ) -> ListSchemaVersionsResponse:
        """Returns a list of schema versions that you have created, with minimal
        information. Schema versions in Deleted status will not be included in
        the results. Empty results will be returned if there are no schema
        versions available.

        :param schema_id: This is a wrapper structure to contain schema identity fields.
        :param max_results: Maximum number of results required per page.
        :param next_token: A continuation token, if this is a continuation call.
        :returns: ListSchemaVersionsResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("ListSchemas")
    def list_schemas(
        self,
        context: RequestContext,
        registry_id: RegistryId = None,
        max_results: MaxResultsNumber = None,
        next_token: SchemaRegistryTokenString = None,
    ) -> ListSchemasResponse:
        """Returns a list of schemas with minimal details. Schemas in Deleting
        status will not be included in the results. Empty results will be
        returned if there are no schemas available.

        When the ``RegistryId`` is not provided, all the schemas across
        registries will be part of the API response.

        :param registry_id: A wrapper structure that may contain the registry name and Amazon
        Resource Name (ARN).
        :param max_results: Maximum number of results required per page.
        :param next_token: A continuation token, if this is a continuation call.
        :returns: ListSchemasResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("ListSessions")
    def list_sessions(
        self,
        context: RequestContext,
        next_token: OrchestrationToken = None,
        max_results: PageSize = None,
        tags: TagsMap = None,
        request_origin: OrchestrationNameString = None,
    ) -> ListSessionsResponse:
        """Retrieve a session..

        :param next_token: The token for the next set of results, or null if there are no more
        result.
        :param max_results: The maximum number of results.
        :param tags: Tags belonging to the session.
        :param request_origin: The origin of the request.
        :returns: ListSessionsResponse
        :raises AccessDeniedException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ListStatements")
    def list_statements(
        self,
        context: RequestContext,
        session_id: NameString,
        request_origin: OrchestrationNameString = None,
        next_token: OrchestrationToken = None,
    ) -> ListStatementsResponse:
        """Lists statements for the session.

        :param session_id: The Session ID of the statements.
        :param request_origin: The origin of the request to list statements.
        :param next_token: .
        :returns: ListStatementsResponse
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises IllegalSessionStateException:
        """
        raise NotImplementedError

    @handler("ListTriggers")
    def list_triggers(
        self,
        context: RequestContext,
        next_token: GenericString = None,
        dependent_job_name: NameString = None,
        max_results: PageSize = None,
        tags: TagsMap = None,
    ) -> ListTriggersResponse:
        """Retrieves the names of all trigger resources in this Amazon Web Services
        account, or the resources with the specified tag. This operation allows
        you to see which resources are available in your account, and their
        names.

        This operation takes the optional ``Tags`` field, which you can use as a
        filter on the response so that tagged resources can be retrieved as a
        group. If you choose to use tags filtering, only resources with the tag
        are retrieved.

        :param next_token: A continuation token, if this is a continuation request.
        :param dependent_job_name: The name of the job for which to retrieve triggers.
        :param max_results: The maximum size of a list to return.
        :param tags: Specifies to return only these tagged resources.
        :returns: ListTriggersResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ListWorkflows")
    def list_workflows(
        self,
        context: RequestContext,
        next_token: GenericString = None,
        max_results: PageSize = None,
    ) -> ListWorkflowsResponse:
        """Lists names of workflows created in the account.

        :param next_token: A continuation token, if this is a continuation request.
        :param max_results: The maximum size of a list to return.
        :returns: ListWorkflowsResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("PutDataCatalogEncryptionSettings")
    def put_data_catalog_encryption_settings(
        self,
        context: RequestContext,
        data_catalog_encryption_settings: DataCatalogEncryptionSettings,
        catalog_id: CatalogIdString = None,
    ) -> PutDataCatalogEncryptionSettingsResponse:
        """Sets the security configuration for a specified catalog. After the
        configuration has been set, the specified encryption is applied to every
        catalog write thereafter.

        :param data_catalog_encryption_settings: The security configuration to set.
        :param catalog_id: The ID of the Data Catalog to set the security configuration for.
        :returns: PutDataCatalogEncryptionSettingsResponse
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("PutResourcePolicy")
    def put_resource_policy(
        self,
        context: RequestContext,
        policy_in_json: PolicyJsonString,
        resource_arn: GlueResourceArn = None,
        policy_hash_condition: HashString = None,
        policy_exists_condition: ExistCondition = None,
        enable_hybrid: EnableHybridValues = None,
    ) -> PutResourcePolicyResponse:
        """Sets the Data Catalog resource policy for access control.

        :param policy_in_json: Contains the policy document to set, in JSON format.
        :param resource_arn: Do not use.
        :param policy_hash_condition: The hash value returned when the previous policy was set using
        ``PutResourcePolicy``.
        :param policy_exists_condition: A value of ``MUST_EXIST`` is used to update a policy.
        :param enable_hybrid: If ``'TRUE'``, indicates that you are using both methods to grant
        cross-account access to Data Catalog resources:

        -  By directly updating the resource policy with ``PutResourePolicy``

        -  By using the **Grant permissions** command on the Amazon Web Services
           Management Console.
        :returns: PutResourcePolicyResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises ConditionCheckFailureException:
        """
        raise NotImplementedError

    @handler("PutSchemaVersionMetadata")
    def put_schema_version_metadata(
        self,
        context: RequestContext,
        metadata_key_value: MetadataKeyValuePair,
        schema_id: SchemaId = None,
        schema_version_number: SchemaVersionNumber = None,
        schema_version_id: SchemaVersionIdString = None,
    ) -> PutSchemaVersionMetadataResponse:
        """Puts the metadata key value pair for a specified schema version ID. A
        maximum of 10 key value pairs will be allowed per schema version. They
        can be added over one or more calls.

        :param metadata_key_value: The metadata key's corresponding value.
        :param schema_id: The unique ID for the schema.
        :param schema_version_number: The version number of the schema.
        :param schema_version_id: The unique version ID of the schema version.
        :returns: PutSchemaVersionMetadataResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises AlreadyExistsException:
        :raises EntityNotFoundException:
        :raises ResourceNumberLimitExceededException:
        """
        raise NotImplementedError

    @handler("PutWorkflowRunProperties")
    def put_workflow_run_properties(
        self,
        context: RequestContext,
        name: NameString,
        run_id: IdString,
        run_properties: WorkflowRunProperties,
    ) -> PutWorkflowRunPropertiesResponse:
        """Puts the specified workflow run properties for the given workflow run.
        If a property already exists for the specified run, then it overrides
        the value otherwise adds the property to existing properties.

        :param name: Name of the workflow which was run.
        :param run_id: The ID of the workflow run for which the run properties should be
        updated.
        :param run_properties: The properties to put for the specified run.
        :returns: PutWorkflowRunPropertiesResponse
        :raises AlreadyExistsException:
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("QuerySchemaVersionMetadata")
    def query_schema_version_metadata(
        self,
        context: RequestContext,
        schema_id: SchemaId = None,
        schema_version_number: SchemaVersionNumber = None,
        schema_version_id: SchemaVersionIdString = None,
        metadata_list: MetadataList = None,
        max_results: QuerySchemaVersionMetadataMaxResults = None,
        next_token: SchemaRegistryTokenString = None,
    ) -> QuerySchemaVersionMetadataResponse:
        """Queries for the schema version metadata information.

        :param schema_id: A wrapper structure that may contain the schema name and Amazon Resource
        Name (ARN).
        :param schema_version_number: The version number of the schema.
        :param schema_version_id: The unique version ID of the schema version.
        :param metadata_list: Search key-value pairs for metadata, if they are not provided all the
        metadata information will be fetched.
        :param max_results: Maximum number of results required per page.
        :param next_token: A continuation token, if this is a continuation call.
        :returns: QuerySchemaVersionMetadataResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        """
        raise NotImplementedError

    @handler("RegisterSchemaVersion")
    def register_schema_version(
        self,
        context: RequestContext,
        schema_id: SchemaId,
        schema_definition: SchemaDefinitionString,
    ) -> RegisterSchemaVersionResponse:
        """Adds a new version to the existing schema. Returns an error if new
        version of schema does not meet the compatibility requirements of the
        schema set. This API will not create a new schema set and will return a
        404 error if the schema set is not already present in the Schema
        Registry.

        If this is the first schema definition to be registered in the Schema
        Registry, this API will store the schema version and return immediately.
        Otherwise, this call has the potential to run longer than other
        operations due to compatibility modes. You can call the
        ``GetSchemaVersion`` API with the ``SchemaVersionId`` to check
        compatibility modes.

        If the same schema definition is already stored in Schema Registry as a
        version, the schema ID of the existing schema is returned to the caller.

        :param schema_id: This is a wrapper structure to contain schema identity fields.
        :param schema_definition: The schema definition using the ``DataFormat`` setting for the
        ``SchemaName``.
        :returns: RegisterSchemaVersionResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises ResourceNumberLimitExceededException:
        :raises ConcurrentModificationException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("RemoveSchemaVersionMetadata")
    def remove_schema_version_metadata(
        self,
        context: RequestContext,
        metadata_key_value: MetadataKeyValuePair,
        schema_id: SchemaId = None,
        schema_version_number: SchemaVersionNumber = None,
        schema_version_id: SchemaVersionIdString = None,
    ) -> RemoveSchemaVersionMetadataResponse:
        """Removes a key value pair from the schema version metadata for the
        specified schema version ID.

        :param metadata_key_value: The value of the metadata key.
        :param schema_id: A wrapper structure that may contain the schema name and Amazon Resource
        Name (ARN).
        :param schema_version_number: The version number of the schema.
        :param schema_version_id: The unique version ID of the schema version.
        :returns: RemoveSchemaVersionMetadataResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        """
        raise NotImplementedError

    @handler("ResetJobBookmark")
    def reset_job_bookmark(
        self, context: RequestContext, job_name: JobName, run_id: RunId = None
    ) -> ResetJobBookmarkResponse:
        """Resets a bookmark entry.

        :param job_name: The name of the job in question.
        :param run_id: The unique run identifier associated with this job run.
        :returns: ResetJobBookmarkResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ResumeWorkflowRun")
    def resume_workflow_run(
        self, context: RequestContext, name: NameString, run_id: IdString, node_ids: NodeIdList
    ) -> ResumeWorkflowRunResponse:
        """Restarts selected nodes of a previous partially completed workflow run
        and resumes the workflow run. The selected nodes and all nodes that are
        downstream from the selected nodes are run.

        :param name: The name of the workflow to resume.
        :param run_id: The ID of the workflow run to resume.
        :param node_ids: A list of the node IDs for the nodes you want to restart.
        :returns: ResumeWorkflowRunResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ConcurrentRunsExceededException:
        :raises IllegalWorkflowStateException:
        """
        raise NotImplementedError

    @handler("RunStatement")
    def run_statement(
        self,
        context: RequestContext,
        session_id: NameString,
        code: OrchestrationStatementCodeString,
        request_origin: OrchestrationNameString = None,
    ) -> RunStatementResponse:
        """Executes the statement.

        :param session_id: The Session Id of the statement to be run.
        :param code: The statement code to be run.
        :param request_origin: The origin of the request.
        :returns: RunStatementResponse
        :raises EntityNotFoundException:
        :raises AccessDeniedException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises ValidationException:
        :raises ResourceNumberLimitExceededException:
        :raises IllegalSessionStateException:
        """
        raise NotImplementedError

    @handler("SearchTables")
    def search_tables(
        self,
        context: RequestContext,
        catalog_id: CatalogIdString = None,
        next_token: Token = None,
        filters: SearchPropertyPredicates = None,
        search_text: ValueString = None,
        sort_criteria: SortCriteria = None,
        max_results: PageSize = None,
        resource_share_type: ResourceShareType = None,
    ) -> SearchTablesResponse:
        """Searches a set of tables based on properties in the table metadata as
        well as on the parent database. You can search against text or filter
        conditions.

        You can only get tables that you have access to based on the security
        policies defined in Lake Formation. You need at least a read-only access
        to the table for it to be returned. If you do not have access to all the
        columns in the table, these columns will not be searched against when
        returning the list of tables back to you. If you have access to the
        columns but not the data in the columns, those columns and the
        associated metadata for those columns will be included in the search.

        :param catalog_id: A unique identifier, consisting of ``account_id``.
        :param next_token: A continuation token, included if this is a continuation call.
        :param filters: A list of key-value pairs, and a comparator used to filter the search
        results.
        :param search_text: A string used for a text search.
        :param sort_criteria: A list of criteria for sorting the results by a field name, in an
        ascending or descending order.
        :param max_results: The maximum number of tables to return in a single response.
        :param resource_share_type: Allows you to specify that you want to search the tables shared with
        your account.
        :returns: SearchTablesResponse
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("StartBlueprintRun")
    def start_blueprint_run(
        self,
        context: RequestContext,
        blueprint_name: OrchestrationNameString,
        role_arn: OrchestrationIAMRoleArn,
        parameters: BlueprintParameters = None,
    ) -> StartBlueprintRunResponse:
        """Starts a new run of the specified blueprint.

        :param blueprint_name: The name of the blueprint.
        :param role_arn: Specifies the IAM role used to create the workflow.
        :param parameters: Specifies the parameters as a ``BlueprintParameters`` object.
        :returns: StartBlueprintRunResponse
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises ResourceNumberLimitExceededException:
        :raises EntityNotFoundException:
        :raises IllegalBlueprintStateException:
        """
        raise NotImplementedError

    @handler("StartCrawler")
    def start_crawler(self, context: RequestContext, name: NameString) -> StartCrawlerResponse:
        """Starts a crawl using the specified crawler, regardless of what is
        scheduled. If the crawler is already running, returns a
        `CrawlerRunningException <https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-exceptions.html#aws-glue-api-exceptions-CrawlerRunningException>`__.

        :param name: Name of the crawler to start.
        :returns: StartCrawlerResponse
        :raises EntityNotFoundException:
        :raises CrawlerRunningException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("StartCrawlerSchedule")
    def start_crawler_schedule(
        self, context: RequestContext, crawler_name: NameString
    ) -> StartCrawlerScheduleResponse:
        """Changes the schedule state of the specified crawler to ``SCHEDULED``,
        unless the crawler is already running or the schedule state is already
        ``SCHEDULED``.

        :param crawler_name: Name of the crawler to schedule.
        :returns: StartCrawlerScheduleResponse
        :raises EntityNotFoundException:
        :raises SchedulerRunningException:
        :raises SchedulerTransitioningException:
        :raises NoScheduleException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("StartExportLabelsTaskRun")
    def start_export_labels_task_run(
        self, context: RequestContext, transform_id: HashString, output_s3_path: UriString
    ) -> StartExportLabelsTaskRunResponse:
        """Begins an asynchronous task to export all labeled data for a particular
        transform. This task is the only label-related API call that is not part
        of the typical active learning workflow. You typically use
        ``StartExportLabelsTaskRun`` when you want to work with all of your
        existing labels at the same time, such as when you want to remove or
        change labels that were previously submitted as truth. This API
        operation accepts the ``TransformId`` whose labels you want to export
        and an Amazon Simple Storage Service (Amazon S3) path to export the
        labels to. The operation returns a ``TaskRunId``. You can check on the
        status of your task run by calling the ``GetMLTaskRun`` API.

        :param transform_id: The unique identifier of the machine learning transform.
        :param output_s3_path: The Amazon S3 path where you export the labels.
        :returns: StartExportLabelsTaskRunResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("StartImportLabelsTaskRun")
    def start_import_labels_task_run(
        self,
        context: RequestContext,
        transform_id: HashString,
        input_s3_path: UriString,
        replace_all_labels: ReplaceBoolean = None,
    ) -> StartImportLabelsTaskRunResponse:
        """Enables you to provide additional labels (examples of truth) to be used
        to teach the machine learning transform and improve its quality. This
        API operation is generally used as part of the active learning workflow
        that starts with the ``StartMLLabelingSetGenerationTaskRun`` call and
        that ultimately results in improving the quality of your machine
        learning transform.

        After the ``StartMLLabelingSetGenerationTaskRun`` finishes, Glue machine
        learning will have generated a series of questions for humans to answer.
        (Answering these questions is often called 'labeling' in the machine
        learning workflows). In the case of the ``FindMatches`` transform, these
        questions are of the form, “What is the correct way to group these rows
        together into groups composed entirely of matching records?” After the
        labeling process is finished, users upload their answers/labels with a
        call to ``StartImportLabelsTaskRun``. After ``StartImportLabelsTaskRun``
        finishes, all future runs of the machine learning transform use the new
        and improved labels and perform a higher-quality transformation.

        By default, ``StartMLLabelingSetGenerationTaskRun`` continually learns
        from and combines all labels that you upload unless you set ``Replace``
        to true. If you set ``Replace`` to true, ``StartImportLabelsTaskRun``
        deletes and forgets all previously uploaded labels and learns only from
        the exact set that you upload. Replacing labels can be helpful if you
        realize that you previously uploaded incorrect labels, and you believe
        that they are having a negative effect on your transform quality.

        You can check on the status of your task run by calling the
        ``GetMLTaskRun`` operation.

        :param transform_id: The unique identifier of the machine learning transform.
        :param input_s3_path: The Amazon Simple Storage Service (Amazon S3) path from where you import
        the labels.
        :param replace_all_labels: Indicates whether to overwrite your existing labels.
        :returns: StartImportLabelsTaskRunResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("StartJobRun")
    def start_job_run(
        self,
        context: RequestContext,
        job_name: NameString,
        job_run_id: IdString = None,
        arguments: GenericMap = None,
        allocated_capacity: IntegerValue = None,
        timeout: Timeout = None,
        max_capacity: NullableDouble = None,
        security_configuration: NameString = None,
        notification_property: NotificationProperty = None,
        worker_type: WorkerType = None,
        number_of_workers: NullableInteger = None,
    ) -> StartJobRunResponse:
        """Starts a job run using a job definition.

        :param job_name: The name of the job definition to use.
        :param job_run_id: The ID of a previous ``JobRun`` to retry.
        :param arguments: The job arguments specifically for this run.
        :param allocated_capacity: This field is deprecated.
        :param timeout: The ``JobRun`` timeout in minutes.
        :param max_capacity: The number of Glue data processing units (DPUs) that can be allocated
        when this job runs.
        :param security_configuration: The name of the ``SecurityConfiguration`` structure to be used with this
        job run.
        :param notification_property: Specifies configuration properties of a job run notification.
        :param worker_type: The type of predefined worker that is allocated when a job runs.
        :param number_of_workers: The number of workers of a defined ``workerType`` that are allocated
        when a job runs.
        :returns: StartJobRunResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        :raises ConcurrentRunsExceededException:
        """
        raise NotImplementedError

    @handler("StartMLEvaluationTaskRun")
    def start_ml_evaluation_task_run(
        self, context: RequestContext, transform_id: HashString
    ) -> StartMLEvaluationTaskRunResponse:
        """Starts a task to estimate the quality of the transform.

        When you provide label sets as examples of truth, Glue machine learning
        uses some of those examples to learn from them. The rest of the labels
        are used as a test to estimate quality.

        Returns a unique identifier for the run. You can call ``GetMLTaskRun``
        to get more information about the stats of the ``EvaluationTaskRun``.

        :param transform_id: The unique identifier of the machine learning transform.
        :returns: StartMLEvaluationTaskRunResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises ConcurrentRunsExceededException:
        :raises MLTransformNotReadyException:
        """
        raise NotImplementedError

    @handler("StartMLLabelingSetGenerationTaskRun")
    def start_ml_labeling_set_generation_task_run(
        self, context: RequestContext, transform_id: HashString, output_s3_path: UriString
    ) -> StartMLLabelingSetGenerationTaskRunResponse:
        """Starts the active learning workflow for your machine learning transform
        to improve the transform's quality by generating label sets and adding
        labels.

        When the ``StartMLLabelingSetGenerationTaskRun`` finishes, Glue will
        have generated a "labeling set" or a set of questions for humans to
        answer.

        In the case of the ``FindMatches`` transform, these questions are of the
        form, “What is the correct way to group these rows together into groups
        composed entirely of matching records?”

        After the labeling process is finished, you can upload your labels with
        a call to ``StartImportLabelsTaskRun``. After
        ``StartImportLabelsTaskRun`` finishes, all future runs of the machine
        learning transform will use the new and improved labels and perform a
        higher-quality transformation.

        :param transform_id: The unique identifier of the machine learning transform.
        :param output_s3_path: The Amazon Simple Storage Service (Amazon S3) path where you generate
        the labeling set.
        :returns: StartMLLabelingSetGenerationTaskRunResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises ConcurrentRunsExceededException:
        """
        raise NotImplementedError

    @handler("StartTrigger")
    def start_trigger(self, context: RequestContext, name: NameString) -> StartTriggerResponse:
        """Starts an existing trigger. See `Triggering
        Jobs <https://docs.aws.amazon.com/glue/latest/dg/trigger-job.html>`__
        for information about how different types of trigger are started.

        :param name: The name of the trigger to start.
        :returns: StartTriggerResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        :raises ConcurrentRunsExceededException:
        """
        raise NotImplementedError

    @handler("StartWorkflowRun")
    def start_workflow_run(
        self,
        context: RequestContext,
        name: NameString,
        run_properties: WorkflowRunProperties = None,
    ) -> StartWorkflowRunResponse:
        """Starts a new run of the specified workflow.

        :param name: The name of the workflow to start.
        :param run_properties: The workflow run properties for the new workflow run.
        :returns: StartWorkflowRunResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ResourceNumberLimitExceededException:
        :raises ConcurrentRunsExceededException:
        """
        raise NotImplementedError

    @handler("StopCrawler")
    def stop_crawler(self, context: RequestContext, name: NameString) -> StopCrawlerResponse:
        """If the specified crawler is running, stops the crawl.

        :param name: Name of the crawler to stop.
        :returns: StopCrawlerResponse
        :raises EntityNotFoundException:
        :raises CrawlerNotRunningException:
        :raises CrawlerStoppingException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("StopCrawlerSchedule")
    def stop_crawler_schedule(
        self, context: RequestContext, crawler_name: NameString
    ) -> StopCrawlerScheduleResponse:
        """Sets the schedule state of the specified crawler to ``NOT_SCHEDULED``,
        but does not stop the crawler if it is already running.

        :param crawler_name: Name of the crawler whose schedule state to set.
        :returns: StopCrawlerScheduleResponse
        :raises EntityNotFoundException:
        :raises SchedulerNotRunningException:
        :raises SchedulerTransitioningException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("StopSession")
    def stop_session(
        self,
        context: RequestContext,
        id: NameString,
        request_origin: OrchestrationNameString = None,
    ) -> StopSessionResponse:
        """Stops the session.

        :param id: The ID of the session to be stopped.
        :param request_origin: The origin of the request.
        :returns: StopSessionResponse
        :raises AccessDeniedException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises IllegalSessionStateException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("StopTrigger")
    def stop_trigger(self, context: RequestContext, name: NameString) -> StopTriggerResponse:
        """Stops a specified trigger.

        :param name: The name of the trigger to stop.
        :returns: StopTriggerResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("StopWorkflowRun")
    def stop_workflow_run(
        self, context: RequestContext, name: NameString, run_id: IdString
    ) -> StopWorkflowRunResponse:
        """Stops the execution of the specified workflow run.

        :param name: The name of the workflow to stop.
        :param run_id: The ID of the workflow run to stop.
        :returns: StopWorkflowRunResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises IllegalWorkflowStateException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: GlueResourceArn, tags_to_add: TagsMap
    ) -> TagResourceResponse:
        """Adds tags to a resource. A tag is a label you can assign to an Amazon
        Web Services resource. In Glue, you can tag only certain resources. For
        information about what resources you can tag, see `Amazon Web Services
        Tags in
        Glue <https://docs.aws.amazon.com/glue/latest/dg/monitor-tags.html>`__.

        :param resource_arn: The ARN of the Glue resource to which to add the tags.
        :param tags_to_add: Tags to add to this resource.
        :returns: TagResourceResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: GlueResourceArn, tags_to_remove: TagKeysList
    ) -> UntagResourceResponse:
        """Removes tags from a resource.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource from which to remove the
        tags.
        :param tags_to_remove: Tags to remove from this resource.
        :returns: UntagResourceResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateBlueprint")
    def update_blueprint(
        self,
        context: RequestContext,
        name: OrchestrationNameString,
        blueprint_location: OrchestrationS3Location,
        description: Generic512CharString = None,
    ) -> UpdateBlueprintResponse:
        """Updates a registered blueprint.

        :param name: The name of the blueprint.
        :param blueprint_location: Specifies a path in Amazon S3 where the blueprint is published.
        :param description: A description of the blueprint.
        :returns: UpdateBlueprintResponse
        :raises EntityNotFoundException:
        :raises ConcurrentModificationException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises IllegalBlueprintStateException:
        """
        raise NotImplementedError

    @handler("UpdateClassifier")
    def update_classifier(
        self,
        context: RequestContext,
        grok_classifier: UpdateGrokClassifierRequest = None,
        xml_classifier: UpdateXMLClassifierRequest = None,
        json_classifier: UpdateJsonClassifierRequest = None,
        csv_classifier: UpdateCsvClassifierRequest = None,
    ) -> UpdateClassifierResponse:
        """Modifies an existing classifier (a ``GrokClassifier``, an
        ``XMLClassifier``, a ``JsonClassifier``, or a ``CsvClassifier``,
        depending on which field is present).

        :param grok_classifier: A ``GrokClassifier`` object with updated fields.
        :param xml_classifier: An ``XMLClassifier`` object with updated fields.
        :param json_classifier: A ``JsonClassifier`` object with updated fields.
        :param csv_classifier: A ``CsvClassifier`` object with updated fields.
        :returns: UpdateClassifierResponse
        :raises InvalidInputException:
        :raises VersionMismatchException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("UpdateColumnStatisticsForPartition")
    def update_column_statistics_for_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partition_values: ValueStringList,
        column_statistics_list: UpdateColumnStatisticsList,
        catalog_id: CatalogIdString = None,
    ) -> UpdateColumnStatisticsForPartitionResponse:
        """Creates or updates partition statistics of columns.

        The Identity and Access Management (IAM) permission required for this
        operation is ``UpdatePartition``.

        :param database_name: The name of the catalog database where the partitions reside.
        :param table_name: The name of the partitions' table.
        :param partition_values: A list of partition values identifying the partition.
        :param column_statistics_list: A list of the column statistics.
        :param catalog_id: The ID of the Data Catalog where the partitions in question reside.
        :returns: UpdateColumnStatisticsForPartitionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("UpdateColumnStatisticsForTable")
    def update_column_statistics_for_table(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        column_statistics_list: UpdateColumnStatisticsList,
        catalog_id: CatalogIdString = None,
    ) -> UpdateColumnStatisticsForTableResponse:
        """Creates or updates table statistics of columns.

        The Identity and Access Management (IAM) permission required for this
        operation is ``UpdateTable``.

        :param database_name: The name of the catalog database where the partitions reside.
        :param table_name: The name of the partitions' table.
        :param column_statistics_list: A list of the column statistics.
        :param catalog_id: The ID of the Data Catalog where the partitions in question reside.
        :returns: UpdateColumnStatisticsForTableResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("UpdateConnection")
    def update_connection(
        self,
        context: RequestContext,
        name: NameString,
        connection_input: ConnectionInput,
        catalog_id: CatalogIdString = None,
    ) -> UpdateConnectionResponse:
        """Updates a connection definition in the Data Catalog.

        :param name: The name of the connection definition to update.
        :param connection_input: A ``ConnectionInput`` object that redefines the connection in question.
        :param catalog_id: The ID of the Data Catalog in which the connection resides.
        :returns: UpdateConnectionResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("UpdateCrawler")
    def update_crawler(
        self,
        context: RequestContext,
        name: NameString,
        role: Role = None,
        database_name: DatabaseName = None,
        description: DescriptionStringRemovable = None,
        targets: CrawlerTargets = None,
        schedule: CronExpression = None,
        classifiers: ClassifierNameList = None,
        table_prefix: TablePrefix = None,
        schema_change_policy: SchemaChangePolicy = None,
        recrawl_policy: RecrawlPolicy = None,
        lineage_configuration: LineageConfiguration = None,
        lake_formation_configuration: LakeFormationConfiguration = None,
        configuration: CrawlerConfiguration = None,
        crawler_security_configuration: CrawlerSecurityConfiguration = None,
    ) -> UpdateCrawlerResponse:
        """Updates a crawler. If a crawler is running, you must stop it using
        ``StopCrawler`` before updating it.

        :param name: Name of the new crawler.
        :param role: The IAM role or Amazon Resource Name (ARN) of an IAM role that is used
        by the new crawler to access customer resources.
        :param database_name: The Glue database where results are stored, such as:
        ``arn:aws:daylight:us-east-1::database/sometable/*``.
        :param description: A description of the new crawler.
        :param targets: A list of targets to crawl.
        :param schedule: A ``cron`` expression used to specify the schedule (see `Time-Based
        Schedules for Jobs and
        Crawlers <https://docs.
        :param classifiers: A list of custom classifiers that the user has registered.
        :param table_prefix: The table prefix used for catalog tables that are created.
        :param schema_change_policy: The policy for the crawler's update and deletion behavior.
        :param recrawl_policy: A policy that specifies whether to crawl the entire dataset again, or to
        crawl only folders that were added since the last crawler run.
        :param lineage_configuration: Specifies data lineage configuration settings for the crawler.
        :param lake_formation_configuration: Specifies AWS Lake Formation configuration settings for the crawler.
        :param configuration: Crawler configuration information.
        :param crawler_security_configuration: The name of the ``SecurityConfiguration`` structure to be used by this
        crawler.
        :returns: UpdateCrawlerResponse
        :raises InvalidInputException:
        :raises VersionMismatchException:
        :raises EntityNotFoundException:
        :raises CrawlerRunningException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("UpdateCrawlerSchedule")
    def update_crawler_schedule(
        self, context: RequestContext, crawler_name: NameString, schedule: CronExpression = None
    ) -> UpdateCrawlerScheduleResponse:
        """Updates the schedule of a crawler using a ``cron`` expression.

        :param crawler_name: The name of the crawler whose schedule to update.
        :param schedule: The updated ``cron`` expression used to specify the schedule (see
        `Time-Based Schedules for Jobs and
        Crawlers <https://docs.
        :returns: UpdateCrawlerScheduleResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises VersionMismatchException:
        :raises SchedulerTransitioningException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("UpdateDatabase")
    def update_database(
        self,
        context: RequestContext,
        name: NameString,
        database_input: DatabaseInput,
        catalog_id: CatalogIdString = None,
    ) -> UpdateDatabaseResponse:
        """Updates an existing database definition in a Data Catalog.

        :param name: The name of the database to update in the catalog.
        :param database_input: A ``DatabaseInput`` object specifying the new definition of the metadata
        database in the catalog.
        :param catalog_id: The ID of the Data Catalog in which the metadata database resides.
        :returns: UpdateDatabaseResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("UpdateDevEndpoint")
    def update_dev_endpoint(
        self,
        context: RequestContext,
        endpoint_name: GenericString,
        public_key: GenericString = None,
        add_public_keys: PublicKeysList = None,
        delete_public_keys: PublicKeysList = None,
        custom_libraries: DevEndpointCustomLibraries = None,
        update_etl_libraries: BooleanValue = None,
        delete_arguments: StringList = None,
        add_arguments: MapValue = None,
    ) -> UpdateDevEndpointResponse:
        """Updates a specified development endpoint.

        :param endpoint_name: The name of the ``DevEndpoint`` to be updated.
        :param public_key: The public key for the ``DevEndpoint`` to use.
        :param add_public_keys: The list of public keys for the ``DevEndpoint`` to use.
        :param delete_public_keys: The list of public keys to be deleted from the ``DevEndpoint``.
        :param custom_libraries: Custom Python or Java libraries to be loaded in the ``DevEndpoint``.
        :param update_etl_libraries: ``True`` if the list of custom libraries to be loaded in the development
        endpoint needs to be updated, or ``False`` if otherwise.
        :param delete_arguments: The list of argument keys to be deleted from the map of arguments used
        to configure the ``DevEndpoint``.
        :param add_arguments: The map of arguments to add the map of arguments used to configure the
        ``DevEndpoint``.
        :returns: UpdateDevEndpointResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises InvalidInputException:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("UpdateJob")
    def update_job(
        self, context: RequestContext, job_name: NameString, job_update: JobUpdate
    ) -> UpdateJobResponse:
        """Updates an existing job definition.

        :param job_name: The name of the job definition to update.
        :param job_update: Specifies the values with which to update the job definition.
        :returns: UpdateJobResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("UpdateMLTransform")
    def update_ml_transform(
        self,
        context: RequestContext,
        transform_id: HashString,
        name: NameString = None,
        description: DescriptionString = None,
        parameters: TransformParameters = None,
        role: RoleString = None,
        glue_version: GlueVersionString = None,
        max_capacity: NullableDouble = None,
        worker_type: WorkerType = None,
        number_of_workers: NullableInteger = None,
        timeout: Timeout = None,
        max_retries: NullableInteger = None,
    ) -> UpdateMLTransformResponse:
        """Updates an existing machine learning transform. Call this operation to
        tune the algorithm parameters to achieve better results.

        After calling this operation, you can call the
        ``StartMLEvaluationTaskRun`` operation to assess how well your new
        parameters achieved your goals (such as improving the quality of your
        machine learning transform, or making it more cost-effective).

        :param transform_id: A unique identifier that was generated when the transform was created.
        :param name: The unique name that you gave the transform when you created it.
        :param description: A description of the transform.
        :param parameters: The configuration parameters that are specific to the transform type
        (algorithm) used.
        :param role: The name or Amazon Resource Name (ARN) of the IAM role with the required
        permissions.
        :param glue_version: This value determines which version of Glue this machine learning
        transform is compatible with.
        :param max_capacity: The number of Glue data processing units (DPUs) that are allocated to
        task runs for this transform.
        :param worker_type: The type of predefined worker that is allocated when this task runs.
        :param number_of_workers: The number of workers of a defined ``workerType`` that are allocated
        when this task runs.
        :param timeout: The timeout for a task run for this transform in minutes.
        :param max_retries: The maximum number of times to retry a task for this transform after a
        task run fails.
        :returns: UpdateMLTransformResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("UpdatePartition")
    def update_partition(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        partition_value_list: BoundedPartitionValueList,
        partition_input: PartitionInput,
        catalog_id: CatalogIdString = None,
    ) -> UpdatePartitionResponse:
        """Updates a partition.

        :param database_name: The name of the catalog database in which the table in question resides.
        :param table_name: The name of the table in which the partition to be updated is located.
        :param partition_value_list: List of partition key values that define the partition to update.
        :param partition_input: The new partition object to update the partition to.
        :param catalog_id: The ID of the Data Catalog where the partition to be updated resides.
        :returns: UpdatePartitionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("UpdateRegistry")
    def update_registry(
        self, context: RequestContext, registry_id: RegistryId, description: DescriptionString
    ) -> UpdateRegistryResponse:
        """Updates an existing registry which is used to hold a collection of
        schemas. The updated properties relate to the registry, and do not
        modify any of the schemas within the registry.

        :param registry_id: This is a wrapper structure that may contain the registry name and
        Amazon Resource Name (ARN).
        :param description: A description of the registry.
        :returns: UpdateRegistryResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises ConcurrentModificationException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("UpdateSchema")
    def update_schema(
        self,
        context: RequestContext,
        schema_id: SchemaId,
        schema_version_number: SchemaVersionNumber = None,
        compatibility: Compatibility = None,
        description: DescriptionString = None,
    ) -> UpdateSchemaResponse:
        """Updates the description, compatibility setting, or version checkpoint
        for a schema set.

        For updating the compatibility setting, the call will not validate
        compatibility for the entire set of schema versions with the new
        compatibility setting. If the value for ``Compatibility`` is provided,
        the ``VersionNumber`` (a checkpoint) is also required. The API will
        validate the checkpoint version number for consistency.

        If the value for the ``VersionNumber`` (checkpoint) is provided,
        ``Compatibility`` is optional and this can be used to set/reset a
        checkpoint for the schema.

        This update will happen only if the schema is in the AVAILABLE state.

        :param schema_id: This is a wrapper structure to contain schema identity fields.
        :param schema_version_number: Version number required for check pointing.
        :param compatibility: The new compatibility setting for the schema.
        :param description: The new description for the schema.
        :returns: UpdateSchemaResponse
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises EntityNotFoundException:
        :raises ConcurrentModificationException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("UpdateTable")
    def update_table(
        self,
        context: RequestContext,
        database_name: NameString,
        table_input: TableInput,
        catalog_id: CatalogIdString = None,
        skip_archive: BooleanNullable = None,
        transaction_id: TransactionIdString = None,
        version_id: VersionString = None,
    ) -> UpdateTableResponse:
        """Updates a metadata table in the Data Catalog.

        :param database_name: The name of the catalog database in which the table resides.
        :param table_input: An updated ``TableInput`` object to define the metadata table in the
        catalog.
        :param catalog_id: The ID of the Data Catalog where the table resides.
        :param skip_archive: By default, ``UpdateTable`` always creates an archived version of the
        table before updating it.
        :param transaction_id: The transaction ID at which to update the table contents.
        :param version_id: .
        :returns: UpdateTableResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ConcurrentModificationException:
        :raises ResourceNumberLimitExceededException:
        :raises GlueEncryptionException:
        :raises ResourceNotReadyException:
        """
        raise NotImplementedError

    @handler("UpdateTrigger")
    def update_trigger(
        self, context: RequestContext, name: NameString, trigger_update: TriggerUpdate
    ) -> UpdateTriggerResponse:
        """Updates a trigger definition.

        :param name: The name of the trigger to update.
        :param trigger_update: The new values with which to update the trigger.
        :returns: UpdateTriggerResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("UpdateUserDefinedFunction")
    def update_user_defined_function(
        self,
        context: RequestContext,
        database_name: NameString,
        function_name: NameString,
        function_input: UserDefinedFunctionInput,
        catalog_id: CatalogIdString = None,
    ) -> UpdateUserDefinedFunctionResponse:
        """Updates an existing function definition in the Data Catalog.

        :param database_name: The name of the catalog database where the function to be updated is
        located.
        :param function_name: The name of the function.
        :param function_input: A ``FunctionInput`` object that redefines the function in the Data
        Catalog.
        :param catalog_id: The ID of the Data Catalog where the function to be updated is located.
        :returns: UpdateUserDefinedFunctionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        """
        raise NotImplementedError

    @handler("UpdateWorkflow")
    def update_workflow(
        self,
        context: RequestContext,
        name: NameString,
        description: GenericString = None,
        default_run_properties: WorkflowRunProperties = None,
        max_concurrent_runs: NullableInteger = None,
    ) -> UpdateWorkflowResponse:
        """Updates an existing workflow.

        :param name: Name of the workflow to be updated.
        :param description: The description of the workflow.
        :param default_run_properties: A collection of properties to be used as part of each execution of the
        workflow.
        :param max_concurrent_runs: You can use this parameter to prevent unwanted multiple updates to data,
        to control costs, or in some cases, to prevent exceeding the maximum
        number of concurrent runs of any of the component jobs.
        :returns: UpdateWorkflowResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError
