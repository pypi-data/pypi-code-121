import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AccessKeyIdString = str
AuditContextString = str
BooleanNullable = bool
CatalogIdString = str
CredentialTimeoutDurationSecondInteger = int
DataLakePrincipalString = str
DescriptionString = str
ETagString = str
ErrorMessageString = str
GetQueryStateRequestQueryIdString = str
GetQueryStatisticsRequestQueryIdString = str
GetWorkUnitResultsRequestQueryIdString = str
GetWorkUnitsRequestQueryIdString = str
IAMRoleArn = str
Identifier = str
Integer = int
LFTagKey = str
LFTagValue = str
MessageString = str
NameString = str
NullableBoolean = bool
PageSize = int
PartitionValueString = str
PredicateString = str
QueryIdString = str
QueryPlanningContextDatabaseNameString = str
RAMResourceShareArn = str
ResourceArnString = str
Result = str
SecretAccessKeyString = str
SessionTokenString = str
StorageOptimizerConfigKey = str
StorageOptimizerConfigValue = str
String = str
StringValue = str
SyntheticGetWorkUnitResultsRequestWorkUnitTokenString = str
SyntheticStartQueryPlanningRequestQueryString = str
Token = str
TokenString = str
TransactionIdString = str
TrueFalseString = str
URI = str
ValueString = str
WorkUnitTokenString = str


class ComparisonOperator(str):
    EQ = "EQ"
    NE = "NE"
    LE = "LE"
    LT = "LT"
    GE = "GE"
    GT = "GT"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    BEGINS_WITH = "BEGINS_WITH"
    IN = "IN"
    BETWEEN = "BETWEEN"


class DataLakeResourceType(str):
    CATALOG = "CATALOG"
    DATABASE = "DATABASE"
    TABLE = "TABLE"
    DATA_LOCATION = "DATA_LOCATION"
    LF_TAG = "LF_TAG"
    LF_TAG_POLICY = "LF_TAG_POLICY"
    LF_TAG_POLICY_DATABASE = "LF_TAG_POLICY_DATABASE"
    LF_TAG_POLICY_TABLE = "LF_TAG_POLICY_TABLE"


class FieldNameString(str):
    RESOURCE_ARN = "RESOURCE_ARN"
    ROLE_ARN = "ROLE_ARN"
    LAST_MODIFIED = "LAST_MODIFIED"


class OptimizerType(str):
    COMPACTION = "COMPACTION"
    GARBAGE_COLLECTION = "GARBAGE_COLLECTION"
    ALL = "ALL"


class Permission(str):
    ALL = "ALL"
    SELECT = "SELECT"
    ALTER = "ALTER"
    DROP = "DROP"
    DELETE = "DELETE"
    INSERT = "INSERT"
    DESCRIBE = "DESCRIBE"
    CREATE_DATABASE = "CREATE_DATABASE"
    CREATE_TABLE = "CREATE_TABLE"
    DATA_LOCATION_ACCESS = "DATA_LOCATION_ACCESS"
    CREATE_TAG = "CREATE_TAG"
    ASSOCIATE = "ASSOCIATE"


class PermissionType(str):
    COLUMN_PERMISSION = "COLUMN_PERMISSION"
    CELL_FILTER_PERMISSION = "CELL_FILTER_PERMISSION"


class QueryStateString(str):
    PENDING = "PENDING"
    WORKUNITS_AVAILABLE = "WORKUNITS_AVAILABLE"
    ERROR = "ERROR"
    FINISHED = "FINISHED"
    EXPIRED = "EXPIRED"


class ResourceShareType(str):
    FOREIGN = "FOREIGN"
    ALL = "ALL"


class ResourceType(str):
    DATABASE = "DATABASE"
    TABLE = "TABLE"


class TransactionStatus(str):
    ACTIVE = "ACTIVE"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"
    COMMIT_IN_PROGRESS = "COMMIT_IN_PROGRESS"


class TransactionStatusFilter(str):
    ALL = "ALL"
    COMPLETED = "COMPLETED"
    ACTIVE = "ACTIVE"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"


class TransactionType(str):
    READ_AND_WRITE = "READ_AND_WRITE"
    READ_ONLY = "READ_ONLY"


class AccessDeniedException(ServiceException):
    """Access to a resource was denied."""

    Message: Optional[MessageString]


class AlreadyExistsException(ServiceException):
    """A resource to be created or added already exists."""

    Message: Optional[MessageString]


class ConcurrentModificationException(ServiceException):
    """Two processes are trying to modify a resource simultaneously."""

    Message: Optional[MessageString]


class EntityNotFoundException(ServiceException):
    """A specified entity does not exist"""

    Message: Optional[MessageString]


class ExpiredException(ServiceException):
    """Contains details about an error where the query request expired."""

    Message: Optional[MessageString]


class GlueEncryptionException(ServiceException):
    """An encryption operation failed."""

    Message: Optional[MessageString]


class InternalServiceException(ServiceException):
    """An internal service error occurred."""

    Message: Optional[MessageString]


class InvalidInputException(ServiceException):
    """The input provided was not valid."""

    Message: Optional[MessageString]


class OperationTimeoutException(ServiceException):
    """The operation timed out."""

    Message: Optional[MessageString]


class PermissionTypeMismatchException(ServiceException):
    """The engine does not support filtering data based on the enforced
    permissions. For example, if you call the
    ``GetTemporaryGlueTableCredentials`` operation with
    ``SupportedPermissionType`` equal to ``ColumnPermission``, but
    cell-level permissions exist on the table, this exception is thrown.
    """

    Message: Optional[MessageString]


class ResourceNotReadyException(ServiceException):
    """Contains details about an error related to a resource which is not ready
    for a transaction.
    """

    Message: Optional[MessageString]


class ResourceNumberLimitExceededException(ServiceException):
    """A resource numerical limit was exceeded."""

    Message: Optional[MessageString]


class StatisticsNotReadyYetException(ServiceException):
    """Contains details about an error related to statistics not being ready."""

    Message: Optional[MessageString]


class ThrottledException(ServiceException):
    """Contains details about an error where the query request was throttled."""

    Message: Optional[MessageString]


class TransactionCanceledException(ServiceException):
    """Contains details about an error related to a transaction that was
    cancelled.
    """

    Message: Optional[MessageString]


class TransactionCommitInProgressException(ServiceException):
    """Contains details about an error related to a transaction commit that was
    in progress.
    """

    Message: Optional[MessageString]


class TransactionCommittedException(ServiceException):
    """Contains details about an error where the specified transaction has
    already been committed and cannot be used for ``UpdateTableObjects``.
    """

    Message: Optional[MessageString]


class WorkUnitsNotReadyYetException(ServiceException):
    """Contains details about an error related to work units not being ready."""

    Message: Optional[MessageString]


TagValueList = List[LFTagValue]


class LFTagPair(TypedDict, total=False):
    """A structure containing an LF-tag key-value pair."""

    CatalogId: Optional[CatalogIdString]
    TagKey: LFTagKey
    TagValues: TagValueList


LFTagsList = List[LFTagPair]


class LFTag(TypedDict, total=False):
    """A structure that allows an admin to grant user permissions on certain
    conditions. For example, granting a role access to all columns that do
    not have the LF-tag 'PII' in tables that have the LF-tag 'Prod'.
    """

    TagKey: LFTagKey
    TagValues: TagValueList


Expression = List[LFTag]


class LFTagPolicyResource(TypedDict, total=False):
    """A structure containing a list of LF-tag conditions that apply to a
    resource's LF-tag policy.
    """

    CatalogId: Optional[CatalogIdString]
    ResourceType: ResourceType
    Expression: Expression


class LFTagKeyResource(TypedDict, total=False):
    """A structure containing an LF-tag key and values for a resource."""

    CatalogId: Optional[CatalogIdString]
    TagKey: NameString
    TagValues: TagValueList


class DataCellsFilterResource(TypedDict, total=False):
    """A structure for a data cells filter resource."""

    TableCatalogId: Optional[CatalogIdString]
    DatabaseName: Optional[NameString]
    TableName: Optional[NameString]
    Name: Optional[NameString]


class DataLocationResource(TypedDict, total=False):
    """A structure for a data location object where permissions are granted or
    revoked.
    """

    CatalogId: Optional[CatalogIdString]
    ResourceArn: ResourceArnString


ColumnNames = List[NameString]


class ColumnWildcard(TypedDict, total=False):
    """A wildcard object, consisting of an optional list of excluded column
    names or indexes.
    """

    ExcludedColumnNames: Optional[ColumnNames]


class TableWithColumnsResource(TypedDict, total=False):
    """A structure for a table with columns object. This object is only used
    when granting a SELECT permission.

    This object must take a value for at least one of ``ColumnsNames``,
    ``ColumnsIndexes``, or ``ColumnsWildcard``.
    """

    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    Name: NameString
    ColumnNames: Optional[ColumnNames]
    ColumnWildcard: Optional[ColumnWildcard]


class TableWildcard(TypedDict, total=False):
    """A wildcard object representing every table under a database."""


class TableResource(TypedDict, total=False):
    """A structure for the table object. A table is a metadata definition that
    represents your data. You can Grant and Revoke table privileges to a
    principal.
    """

    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    Name: Optional[NameString]
    TableWildcard: Optional[TableWildcard]


class DatabaseResource(TypedDict, total=False):
    """A structure for the database object."""

    CatalogId: Optional[CatalogIdString]
    Name: NameString


class CatalogResource(TypedDict, total=False):
    """A structure for the catalog object."""


class Resource(TypedDict, total=False):
    """A structure for the resource."""

    Catalog: Optional[CatalogResource]
    Database: Optional[DatabaseResource]
    Table: Optional[TableResource]
    TableWithColumns: Optional[TableWithColumnsResource]
    DataLocation: Optional[DataLocationResource]
    DataCellsFilter: Optional[DataCellsFilterResource]
    LFTag: Optional[LFTagKeyResource]
    LFTagPolicy: Optional[LFTagPolicyResource]


class AddLFTagsToResourceRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Resource: Resource
    LFTags: LFTagsList


class ErrorDetail(TypedDict, total=False):
    """Contains details about an error."""

    ErrorCode: Optional[NameString]
    ErrorMessage: Optional[DescriptionString]


class LFTagError(TypedDict, total=False):
    """A structure containing an error related to a ``TagResource`` or
    ``UnTagResource`` operation.
    """

    LFTag: Optional[LFTagPair]
    Error: Optional[ErrorDetail]


LFTagErrors = List[LFTagError]


class AddLFTagsToResourceResponse(TypedDict, total=False):
    Failures: Optional[LFTagErrors]


PartitionValuesList = List[PartitionValueString]
ObjectSize = int


class AddObjectInput(TypedDict, total=False):
    """A new object to add to the governed table."""

    Uri: URI
    ETag: ETagString
    Size: ObjectSize
    PartitionValues: Optional[PartitionValuesList]


class AllRowsWildcard(TypedDict, total=False):
    """A structure that you pass to indicate you want all rows in a filter."""


class AuditContext(TypedDict, total=False):
    """A structure used to include auditing information on the privileged API."""

    AdditionalAuditContext: Optional[AuditContextString]


AuthorizedSessionTagValueList = List[NameString]
PermissionList = List[Permission]


class DataLakePrincipal(TypedDict, total=False):
    """The Lake Formation principal. Supported principals are IAM users or IAM
    roles.
    """

    DataLakePrincipalIdentifier: Optional[DataLakePrincipalString]


class BatchPermissionsRequestEntry(TypedDict, total=False):
    """A permission to a resource granted by batch operation to the principal."""

    Id: Identifier
    Principal: Optional[DataLakePrincipal]
    Resource: Optional[Resource]
    Permissions: Optional[PermissionList]
    PermissionsWithGrantOption: Optional[PermissionList]


BatchPermissionsRequestEntryList = List[BatchPermissionsRequestEntry]


class BatchGrantPermissionsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Entries: BatchPermissionsRequestEntryList


class BatchPermissionsFailureEntry(TypedDict, total=False):
    """A list of failures when performing a batch grant or batch revoke
    operation.
    """

    RequestEntry: Optional[BatchPermissionsRequestEntry]
    Error: Optional[ErrorDetail]


BatchPermissionsFailureList = List[BatchPermissionsFailureEntry]


class BatchGrantPermissionsResponse(TypedDict, total=False):
    Failures: Optional[BatchPermissionsFailureList]


class BatchRevokePermissionsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Entries: BatchPermissionsRequestEntryList


class BatchRevokePermissionsResponse(TypedDict, total=False):
    Failures: Optional[BatchPermissionsFailureList]


class CancelTransactionRequest(ServiceRequest):
    TransactionId: TransactionIdString


class CancelTransactionResponse(TypedDict, total=False):
    pass


class ColumnLFTag(TypedDict, total=False):
    """A structure containing the name of a column resource and the LF-tags
    attached to it.
    """

    Name: Optional[NameString]
    LFTags: Optional[LFTagsList]


ColumnLFTagsList = List[ColumnLFTag]


class CommitTransactionRequest(ServiceRequest):
    TransactionId: TransactionIdString


class CommitTransactionResponse(TypedDict, total=False):
    TransactionStatus: Optional[TransactionStatus]


class RowFilter(TypedDict, total=False):
    """A PartiQL predicate."""

    FilterExpression: Optional[PredicateString]
    AllRowsWildcard: Optional[AllRowsWildcard]


class DataCellsFilter(TypedDict, total=False):
    """A structure that describes certain columns on certain rows."""

    TableCatalogId: CatalogIdString
    DatabaseName: NameString
    TableName: NameString
    Name: NameString
    RowFilter: Optional[RowFilter]
    ColumnNames: Optional[ColumnNames]
    ColumnWildcard: Optional[ColumnWildcard]


class CreateDataCellsFilterRequest(ServiceRequest):
    TableData: DataCellsFilter


class CreateDataCellsFilterResponse(TypedDict, total=False):
    pass


class CreateLFTagRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    TagKey: LFTagKey
    TagValues: TagValueList


class CreateLFTagResponse(TypedDict, total=False):
    pass


DataCellsFilterList = List[DataCellsFilter]
DataLakePrincipalList = List[DataLakePrincipal]
TrustedResourceOwners = List[CatalogIdString]


class PrincipalPermissions(TypedDict, total=False):
    """Permissions granted to a principal."""

    Principal: Optional[DataLakePrincipal]
    Permissions: Optional[PermissionList]


PrincipalPermissionsList = List[PrincipalPermissions]


class DataLakeSettings(TypedDict, total=False):
    """A structure representing a list of Lake Formation principals designated
    as data lake administrators and lists of principal permission entries
    for default create database and default create table permissions.
    """

    DataLakeAdmins: Optional[DataLakePrincipalList]
    CreateDatabaseDefaultPermissions: Optional[PrincipalPermissionsList]
    CreateTableDefaultPermissions: Optional[PrincipalPermissionsList]
    TrustedResourceOwners: Optional[TrustedResourceOwners]
    AllowExternalDataFiltering: Optional[NullableBoolean]
    ExternalDataFilteringAllowList: Optional[DataLakePrincipalList]
    AuthorizedSessionTagValueList: Optional[AuthorizedSessionTagValueList]


class TaggedDatabase(TypedDict, total=False):
    """A structure describing a database resource with LF-tags."""

    Database: Optional[DatabaseResource]
    LFTags: Optional[LFTagsList]


DatabaseLFTagsList = List[TaggedDatabase]
DateTime = datetime


class DeleteDataCellsFilterRequest(ServiceRequest):
    TableCatalogId: Optional[CatalogIdString]
    DatabaseName: Optional[NameString]
    TableName: Optional[NameString]
    Name: Optional[NameString]


class DeleteDataCellsFilterResponse(TypedDict, total=False):
    pass


class DeleteLFTagRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    TagKey: LFTagKey


class DeleteLFTagResponse(TypedDict, total=False):
    pass


class DeleteObjectInput(TypedDict, total=False):
    """An object to delete from the governed table."""

    Uri: URI
    ETag: Optional[ETagString]
    PartitionValues: Optional[PartitionValuesList]


class VirtualObject(TypedDict, total=False):
    """An object that defines an Amazon S3 object to be deleted if a
    transaction cancels, provided that ``VirtualPut`` was called before
    writing the object.
    """

    Uri: URI
    ETag: Optional[ETagString]


VirtualObjectList = List[VirtualObject]


class DeleteObjectsOnCancelRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    TransactionId: TransactionIdString
    Objects: VirtualObjectList


class DeleteObjectsOnCancelResponse(TypedDict, total=False):
    pass


class DeregisterResourceRequest(ServiceRequest):
    ResourceArn: ResourceArnString


class DeregisterResourceResponse(TypedDict, total=False):
    pass


class DescribeResourceRequest(ServiceRequest):
    ResourceArn: ResourceArnString


LastModifiedTimestamp = datetime


class ResourceInfo(TypedDict, total=False):
    """A structure containing information about an Lake Formation resource."""

    ResourceArn: Optional[ResourceArnString]
    RoleArn: Optional[IAMRoleArn]
    LastModified: Optional[LastModifiedTimestamp]


class DescribeResourceResponse(TypedDict, total=False):
    ResourceInfo: Optional[ResourceInfo]


class DescribeTransactionRequest(ServiceRequest):
    TransactionId: TransactionIdString


Timestamp = datetime


class TransactionDescription(TypedDict, total=False):
    """A structure that contains information about a transaction."""

    TransactionId: Optional[TransactionIdString]
    TransactionStatus: Optional[TransactionStatus]
    TransactionStartTime: Optional[Timestamp]
    TransactionEndTime: Optional[Timestamp]


class DescribeTransactionResponse(TypedDict, total=False):
    TransactionDescription: Optional[TransactionDescription]


ResourceShareList = List[RAMResourceShareArn]


class DetailsMap(TypedDict, total=False):
    """A structure containing the additional details to be returned in the
    ``AdditionalDetails`` attribute of ``PrincipalResourcePermissions``.

    If a catalog resource is shared through Resource Access Manager (RAM),
    then there will exist a corresponding RAM resource share ARN.
    """

    ResourceShare: Optional[ResourceShareList]


NumberOfItems = int
NumberOfBytes = int
NumberOfMilliseconds = int


class ExecutionStatistics(TypedDict, total=False):
    """Statistics related to the processing of a query statement."""

    AverageExecutionTimeMillis: Optional[NumberOfMilliseconds]
    DataScannedBytes: Optional[NumberOfBytes]
    WorkUnitsExecutedCount: Optional[NumberOfItems]


ExpirationTimestamp = datetime


class ExtendTransactionRequest(ServiceRequest):
    TransactionId: Optional[TransactionIdString]


class ExtendTransactionResponse(TypedDict, total=False):
    pass


StringValueList = List[StringValue]


class FilterCondition(TypedDict, total=False):
    """This structure describes the filtering of columns in a table based on a
    filter condition.
    """

    Field: Optional[FieldNameString]
    ComparisonOperator: Optional[ComparisonOperator]
    StringValueList: Optional[StringValueList]


FilterConditionList = List[FilterCondition]


class GetDataLakeSettingsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]


class GetDataLakeSettingsResponse(TypedDict, total=False):
    DataLakeSettings: Optional[DataLakeSettings]


class GetEffectivePermissionsForPathRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    ResourceArn: ResourceArnString
    NextToken: Optional[Token]
    MaxResults: Optional[PageSize]


class PrincipalResourcePermissions(TypedDict, total=False):
    """The permissions granted or revoked on a resource."""

    Principal: Optional[DataLakePrincipal]
    Resource: Optional[Resource]
    Permissions: Optional[PermissionList]
    PermissionsWithGrantOption: Optional[PermissionList]
    AdditionalDetails: Optional[DetailsMap]


PrincipalResourcePermissionsList = List[PrincipalResourcePermissions]


class GetEffectivePermissionsForPathResponse(TypedDict, total=False):
    Permissions: Optional[PrincipalResourcePermissionsList]
    NextToken: Optional[Token]


class GetLFTagRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    TagKey: LFTagKey


class GetLFTagResponse(TypedDict, total=False):
    CatalogId: Optional[CatalogIdString]
    TagKey: Optional[LFTagKey]
    TagValues: Optional[TagValueList]


class GetQueryStateRequest(ServiceRequest):
    QueryId: GetQueryStateRequestQueryIdString


class GetQueryStateResponse(TypedDict, total=False):
    """A structure for the output."""

    Error: Optional[ErrorMessageString]
    State: QueryStateString


class GetQueryStatisticsRequest(ServiceRequest):
    QueryId: GetQueryStatisticsRequestQueryIdString


class PlanningStatistics(TypedDict, total=False):
    """Statistics related to the processing of a query statement."""

    EstimatedDataToScanBytes: Optional[NumberOfBytes]
    PlanningTimeMillis: Optional[NumberOfMilliseconds]
    QueueTimeMillis: Optional[NumberOfMilliseconds]
    WorkUnitsGeneratedCount: Optional[NumberOfItems]


class GetQueryStatisticsResponse(TypedDict, total=False):
    ExecutionStatistics: Optional[ExecutionStatistics]
    PlanningStatistics: Optional[PlanningStatistics]
    QuerySubmissionTime: Optional[DateTime]


class GetResourceLFTagsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Resource: Resource
    ShowAssignedLFTags: Optional[BooleanNullable]


class GetResourceLFTagsResponse(TypedDict, total=False):
    LFTagOnDatabase: Optional[LFTagsList]
    LFTagsOnTable: Optional[LFTagsList]
    LFTagsOnColumns: Optional[ColumnLFTagsList]


class GetTableObjectsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    TransactionId: Optional[TransactionIdString]
    QueryAsOfTime: Optional[Timestamp]
    PartitionPredicate: Optional[PredicateString]
    MaxResults: Optional[PageSize]
    NextToken: Optional[TokenString]


class TableObject(TypedDict, total=False):
    """Specifies the details of a governed table."""

    Uri: Optional[URI]
    ETag: Optional[ETagString]
    Size: Optional[ObjectSize]


TableObjectList = List[TableObject]


class PartitionObjects(TypedDict, total=False):
    """A structure containing a list of partition values and table objects."""

    PartitionValues: Optional[PartitionValuesList]
    Objects: Optional[TableObjectList]


PartitionedTableObjectsList = List[PartitionObjects]


class GetTableObjectsResponse(TypedDict, total=False):
    Objects: Optional[PartitionedTableObjectsList]
    NextToken: Optional[TokenString]


PermissionTypeList = List[PermissionType]
ValueStringList = List[ValueString]


class PartitionValueList(TypedDict, total=False):
    """Contains a list of values defining partitions."""

    Values: ValueStringList


class GetTemporaryGluePartitionCredentialsRequest(ServiceRequest):
    TableArn: ResourceArnString
    Partition: PartitionValueList
    Permissions: Optional[PermissionList]
    DurationSeconds: Optional[CredentialTimeoutDurationSecondInteger]
    AuditContext: Optional[AuditContext]
    SupportedPermissionTypes: PermissionTypeList


class GetTemporaryGluePartitionCredentialsResponse(TypedDict, total=False):
    AccessKeyId: Optional[AccessKeyIdString]
    SecretAccessKey: Optional[SecretAccessKeyString]
    SessionToken: Optional[SessionTokenString]
    Expiration: Optional[ExpirationTimestamp]


class GetTemporaryGlueTableCredentialsRequest(ServiceRequest):
    TableArn: ResourceArnString
    Permissions: Optional[PermissionList]
    DurationSeconds: Optional[CredentialTimeoutDurationSecondInteger]
    AuditContext: Optional[AuditContext]
    SupportedPermissionTypes: PermissionTypeList


class GetTemporaryGlueTableCredentialsResponse(TypedDict, total=False):
    AccessKeyId: Optional[AccessKeyIdString]
    SecretAccessKey: Optional[SecretAccessKeyString]
    SessionToken: Optional[SessionTokenString]
    Expiration: Optional[ExpirationTimestamp]


GetWorkUnitResultsRequestWorkUnitIdLong = int


class GetWorkUnitResultsRequest(ServiceRequest):
    QueryId: GetWorkUnitResultsRequestQueryIdString
    WorkUnitId: GetWorkUnitResultsRequestWorkUnitIdLong
    WorkUnitToken: SyntheticGetWorkUnitResultsRequestWorkUnitTokenString


ResultStream = bytes


class GetWorkUnitResultsResponse(TypedDict, total=False):
    """A structure for the output."""

    ResultStream: Optional[ResultStream]


class GetWorkUnitsRequest(ServiceRequest):
    NextToken: Optional[Token]
    PageSize: Optional[Integer]
    QueryId: GetWorkUnitsRequestQueryIdString


WorkUnitIdLong = int


class WorkUnitRange(TypedDict, total=False):
    """Defines the valid range of work unit IDs for querying the execution
    service.
    """

    WorkUnitIdMax: WorkUnitIdLong
    WorkUnitIdMin: WorkUnitIdLong
    WorkUnitToken: WorkUnitTokenString


WorkUnitRangeList = List[WorkUnitRange]


class GetWorkUnitsResponse(TypedDict, total=False):
    """A structure for the output."""

    NextToken: Optional[Token]
    QueryId: QueryIdString
    WorkUnitRanges: WorkUnitRangeList


class GrantPermissionsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Principal: DataLakePrincipal
    Resource: Resource
    Permissions: PermissionList
    PermissionsWithGrantOption: Optional[PermissionList]


class GrantPermissionsResponse(TypedDict, total=False):
    pass


class ListDataCellsFilterRequest(ServiceRequest):
    Table: Optional[TableResource]
    NextToken: Optional[Token]
    MaxResults: Optional[PageSize]


class ListDataCellsFilterResponse(TypedDict, total=False):
    DataCellsFilters: Optional[DataCellsFilterList]
    NextToken: Optional[Token]


class ListLFTagsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    ResourceShareType: Optional[ResourceShareType]
    MaxResults: Optional[PageSize]
    NextToken: Optional[Token]


class ListLFTagsResponse(TypedDict, total=False):
    LFTags: Optional[LFTagsList]
    NextToken: Optional[Token]


class ListPermissionsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Principal: Optional[DataLakePrincipal]
    ResourceType: Optional[DataLakeResourceType]
    Resource: Optional[Resource]
    NextToken: Optional[Token]
    MaxResults: Optional[PageSize]
    IncludeRelated: Optional[TrueFalseString]


class ListPermissionsResponse(TypedDict, total=False):
    PrincipalResourcePermissions: Optional[PrincipalResourcePermissionsList]
    NextToken: Optional[Token]


class ListResourcesRequest(ServiceRequest):
    FilterConditionList: Optional[FilterConditionList]
    MaxResults: Optional[PageSize]
    NextToken: Optional[Token]


ResourceInfoList = List[ResourceInfo]


class ListResourcesResponse(TypedDict, total=False):
    ResourceInfoList: Optional[ResourceInfoList]
    NextToken: Optional[Token]


class ListTableStorageOptimizersRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    StorageOptimizerType: Optional[OptimizerType]
    MaxResults: Optional[PageSize]
    NextToken: Optional[Token]


StorageOptimizerConfig = Dict[StorageOptimizerConfigKey, StorageOptimizerConfigValue]


class StorageOptimizer(TypedDict, total=False):
    """A structure describing the configuration and details of a storage
    optimizer.
    """

    StorageOptimizerType: Optional[OptimizerType]
    Config: Optional[StorageOptimizerConfig]
    ErrorMessage: Optional[MessageString]
    Warnings: Optional[MessageString]
    LastRunDetails: Optional[MessageString]


StorageOptimizerList = List[StorageOptimizer]


class ListTableStorageOptimizersResponse(TypedDict, total=False):
    StorageOptimizerList: Optional[StorageOptimizerList]
    NextToken: Optional[Token]


class ListTransactionsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    StatusFilter: Optional[TransactionStatusFilter]
    MaxResults: Optional[PageSize]
    NextToken: Optional[TokenString]


TransactionDescriptionList = List[TransactionDescription]


class ListTransactionsResponse(TypedDict, total=False):
    Transactions: Optional[TransactionDescriptionList]
    NextToken: Optional[TokenString]


class PutDataLakeSettingsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DataLakeSettings: DataLakeSettings


class PutDataLakeSettingsResponse(TypedDict, total=False):
    pass


QueryParameterMap = Dict[String, String]


class QueryPlanningContext(TypedDict, total=False):
    """A structure containing information about the query plan."""

    CatalogId: Optional[CatalogIdString]
    DatabaseName: QueryPlanningContextDatabaseNameString
    QueryAsOfTime: Optional[Timestamp]
    QueryParameters: Optional[QueryParameterMap]
    TransactionId: Optional[TransactionIdString]


class RegisterResourceRequest(ServiceRequest):
    ResourceArn: ResourceArnString
    UseServiceLinkedRole: Optional[NullableBoolean]
    RoleArn: Optional[IAMRoleArn]


class RegisterResourceResponse(TypedDict, total=False):
    pass


class RemoveLFTagsFromResourceRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Resource: Resource
    LFTags: LFTagsList


class RemoveLFTagsFromResourceResponse(TypedDict, total=False):
    Failures: Optional[LFTagErrors]


class RevokePermissionsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    Principal: DataLakePrincipal
    Resource: Resource
    Permissions: PermissionList
    PermissionsWithGrantOption: Optional[PermissionList]


class RevokePermissionsResponse(TypedDict, total=False):
    pass


class SearchDatabasesByLFTagsRequest(ServiceRequest):
    NextToken: Optional[Token]
    MaxResults: Optional[PageSize]
    CatalogId: Optional[CatalogIdString]
    Expression: Expression


class SearchDatabasesByLFTagsResponse(TypedDict, total=False):
    NextToken: Optional[Token]
    DatabaseList: Optional[DatabaseLFTagsList]


class SearchTablesByLFTagsRequest(ServiceRequest):
    NextToken: Optional[Token]
    MaxResults: Optional[PageSize]
    CatalogId: Optional[CatalogIdString]
    Expression: Expression


class TaggedTable(TypedDict, total=False):
    """A structure describing a table resource with LF-tags."""

    Table: Optional[TableResource]
    LFTagOnDatabase: Optional[LFTagsList]
    LFTagsOnTable: Optional[LFTagsList]
    LFTagsOnColumns: Optional[ColumnLFTagsList]


TableLFTagsList = List[TaggedTable]


class SearchTablesByLFTagsResponse(TypedDict, total=False):
    NextToken: Optional[Token]
    TableList: Optional[TableLFTagsList]


class StartQueryPlanningRequest(ServiceRequest):
    QueryPlanningContext: QueryPlanningContext
    QueryString: SyntheticStartQueryPlanningRequestQueryString


class StartQueryPlanningResponse(TypedDict, total=False):
    """A structure for the output."""

    QueryId: QueryIdString


class StartTransactionRequest(ServiceRequest):
    TransactionType: Optional[TransactionType]


class StartTransactionResponse(TypedDict, total=False):
    TransactionId: Optional[TransactionIdString]


StorageOptimizerConfigMap = Dict[OptimizerType, StorageOptimizerConfig]


class UpdateLFTagRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    TagKey: LFTagKey
    TagValuesToDelete: Optional[TagValueList]
    TagValuesToAdd: Optional[TagValueList]


class UpdateLFTagResponse(TypedDict, total=False):
    pass


class UpdateResourceRequest(ServiceRequest):
    RoleArn: IAMRoleArn
    ResourceArn: ResourceArnString


class UpdateResourceResponse(TypedDict, total=False):
    pass


class WriteOperation(TypedDict, total=False):
    """Defines an object to add to or delete from a governed table."""

    AddObject: Optional[AddObjectInput]
    DeleteObject: Optional[DeleteObjectInput]


WriteOperationList = List[WriteOperation]


class UpdateTableObjectsRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    TransactionId: Optional[TransactionIdString]
    WriteOperations: WriteOperationList


class UpdateTableObjectsResponse(TypedDict, total=False):
    pass


class UpdateTableStorageOptimizerRequest(ServiceRequest):
    CatalogId: Optional[CatalogIdString]
    DatabaseName: NameString
    TableName: NameString
    StorageOptimizerConfig: StorageOptimizerConfigMap


class UpdateTableStorageOptimizerResponse(TypedDict, total=False):
    Result: Optional[Result]


class LakeformationApi:

    service = "lakeformation"
    version = "2017-03-31"

    @handler("AddLFTagsToResource")
    def add_lf_tags_to_resource(
        self,
        context: RequestContext,
        resource: Resource,
        lf_tags: LFTagsList,
        catalog_id: CatalogIdString = None,
    ) -> AddLFTagsToResourceResponse:
        """Attaches one or more LF-tags to an existing resource.

        :param resource: The database, table, or column resource to which to attach an LF-tag.
        :param lf_tags: The LF-tags to attach to the resource.
        :param catalog_id: The identifier for the Data Catalog.
        :returns: AddLFTagsToResourceResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("BatchGrantPermissions")
    def batch_grant_permissions(
        self,
        context: RequestContext,
        entries: BatchPermissionsRequestEntryList,
        catalog_id: CatalogIdString = None,
    ) -> BatchGrantPermissionsResponse:
        """Batch operation to grant permissions to the principal.

        :param entries: A list of up to 20 entries for resource permissions to be granted by
        batch operation to the principal.
        :param catalog_id: The identifier for the Data Catalog.
        :returns: BatchGrantPermissionsResponse
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("BatchRevokePermissions")
    def batch_revoke_permissions(
        self,
        context: RequestContext,
        entries: BatchPermissionsRequestEntryList,
        catalog_id: CatalogIdString = None,
    ) -> BatchRevokePermissionsResponse:
        """Batch operation to revoke permissions from the principal.

        :param entries: A list of up to 20 entries for resource permissions to be revoked by
        batch operation to the principal.
        :param catalog_id: The identifier for the Data Catalog.
        :returns: BatchRevokePermissionsResponse
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("CancelTransaction")
    def cancel_transaction(
        self, context: RequestContext, transaction_id: TransactionIdString
    ) -> CancelTransactionResponse:
        """Attempts to cancel the specified transaction. Returns an exception if
        the transaction was previously committed.

        :param transaction_id: The transaction to cancel.
        :returns: CancelTransactionResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises TransactionCommittedException:
        :raises TransactionCommitInProgressException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("CommitTransaction")
    def commit_transaction(
        self, context: RequestContext, transaction_id: TransactionIdString
    ) -> CommitTransactionResponse:
        """Attempts to commit the specified transaction. Returns an exception if
        the transaction was previously aborted. This API action is idempotent if
        called multiple times for the same transaction.

        :param transaction_id: The transaction to commit.
        :returns: CommitTransactionResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises TransactionCanceledException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("CreateDataCellsFilter")
    def create_data_cells_filter(
        self, context: RequestContext, table_data: DataCellsFilter
    ) -> CreateDataCellsFilterResponse:
        """Creates a data cell filter to allow one to grant access to certain
        columns on certain rows.

        :param table_data: A ``DataCellsFilter`` structure containing information about the data
        cells filter.
        :returns: CreateDataCellsFilterResponse
        :raises AlreadyExistsException:
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises ResourceNumberLimitExceededException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("CreateLFTag")
    def create_lf_tag(
        self,
        context: RequestContext,
        tag_key: LFTagKey,
        tag_values: TagValueList,
        catalog_id: CatalogIdString = None,
    ) -> CreateLFTagResponse:
        """Creates an LF-tag with the specified name and values.

        :param tag_key: The key-name for the LF-tag.
        :param tag_values: A list of possible values an attribute can take.
        :param catalog_id: The identifier for the Data Catalog.
        :returns: CreateLFTagResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises ResourceNumberLimitExceededException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("DeleteDataCellsFilter")
    def delete_data_cells_filter(
        self,
        context: RequestContext,
        table_catalog_id: CatalogIdString = None,
        database_name: NameString = None,
        table_name: NameString = None,
        name: NameString = None,
    ) -> DeleteDataCellsFilterResponse:
        """Deletes a data cell filter.

        :param table_catalog_id: The ID of the catalog to which the table belongs.
        :param database_name: A database in the Glue Data Catalog.
        :param table_name: A table in the database.
        :param name: The name given by the user to the data filter cell.
        :returns: DeleteDataCellsFilterResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("DeleteLFTag")
    def delete_lf_tag(
        self, context: RequestContext, tag_key: LFTagKey, catalog_id: CatalogIdString = None
    ) -> DeleteLFTagResponse:
        """Deletes the specified LF-tag key name. If the attribute key does not
        exist or the LF-tag does not exist, then the operation will not do
        anything. If the attribute key exists, then the operation checks if any
        resources are tagged with this attribute key, if yes, the API throws a
        400 Exception with the message "Delete not allowed" as the LF-tag key is
        still attached with resources. You can consider untagging resources with
        this LF-tag key.

        :param tag_key: The key-name for the LF-tag to delete.
        :param catalog_id: The identifier for the Data Catalog.
        :returns: DeleteLFTagResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("DeleteObjectsOnCancel")
    def delete_objects_on_cancel(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        transaction_id: TransactionIdString,
        objects: VirtualObjectList,
        catalog_id: CatalogIdString = None,
    ) -> DeleteObjectsOnCancelResponse:
        """For a specific governed table, provides a list of Amazon S3 objects that
        will be written during the current transaction and that can be
        automatically deleted if the transaction is canceled. Without this call,
        no Amazon S3 objects are automatically deleted when a transaction
        cancels.

        The Glue ETL library function ``write_dynamic_frame.from_catalog()``
        includes an option to automatically call ``DeleteObjectsOnCancel``
        before writes. For more information, see `Rolling Back Amazon S3
        Writes <https://docs.aws.amazon.com/lake-formation/latest/dg/transactions-data-operations.html#rolling-back-writes>`__.

        :param database_name: The database that contains the governed table.
        :param table_name: The name of the governed table.
        :param transaction_id: ID of the transaction that the writes occur in.
        :param objects: A list of VirtualObject structures, which indicates the Amazon S3
        objects to be deleted if the transaction cancels.
        :param catalog_id: The Glue data catalog that contains the governed table.
        :returns: DeleteObjectsOnCancelResponse
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        :raises TransactionCommittedException:
        :raises TransactionCanceledException:
        :raises ResourceNotReadyException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("DeregisterResource")
    def deregister_resource(
        self, context: RequestContext, resource_arn: ResourceArnString
    ) -> DeregisterResourceResponse:
        """Deregisters the resource as managed by the Data Catalog.

        When you deregister a path, Lake Formation removes the path from the
        inline policy attached to your service-linked role.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource that you want to
        deregister.
        :returns: DeregisterResourceResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeResource")
    def describe_resource(
        self, context: RequestContext, resource_arn: ResourceArnString
    ) -> DescribeResourceResponse:
        """Retrieves the current data access role for the given resource registered
        in Lake Formation.

        :param resource_arn: The resource ARN.
        :returns: DescribeResourceResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeTransaction")
    def describe_transaction(
        self, context: RequestContext, transaction_id: TransactionIdString
    ) -> DescribeTransactionResponse:
        """Returns the details of a single transaction.

        :param transaction_id: The transaction for which to return status.
        :returns: DescribeTransactionResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ExtendTransaction")
    def extend_transaction(
        self, context: RequestContext, transaction_id: TransactionIdString = None
    ) -> ExtendTransactionResponse:
        """Indicates to the service that the specified transaction is still active
        and should not be treated as idle and aborted.

        Write transactions that remain idle for a long period are automatically
        aborted unless explicitly extended.

        :param transaction_id: The transaction to extend.
        :returns: ExtendTransactionResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises TransactionCommittedException:
        :raises TransactionCanceledException:
        :raises TransactionCommitInProgressException:
        """
        raise NotImplementedError

    @handler("GetDataLakeSettings")
    def get_data_lake_settings(
        self, context: RequestContext, catalog_id: CatalogIdString = None
    ) -> GetDataLakeSettingsResponse:
        """Retrieves the list of the data lake administrators of a Lake
        Formation-managed data lake.

        :param catalog_id: The identifier for the Data Catalog.
        :returns: GetDataLakeSettingsResponse
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        """
        raise NotImplementedError

    @handler("GetEffectivePermissionsForPath")
    def get_effective_permissions_for_path(
        self,
        context: RequestContext,
        resource_arn: ResourceArnString,
        catalog_id: CatalogIdString = None,
        next_token: Token = None,
        max_results: PageSize = None,
    ) -> GetEffectivePermissionsForPathResponse:
        """Returns the Lake Formation permissions for a specified table or database
        resource located at a path in Amazon S3.
        ``GetEffectivePermissionsForPath`` will not return databases and tables
        if the catalog is encrypted.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource for which you want to get
        permissions.
        :param catalog_id: The identifier for the Data Catalog.
        :param next_token: A continuation token, if this is not the first call to retrieve this
        list.
        :param max_results: The maximum number of results to return.
        :returns: GetEffectivePermissionsForPathResponse
        :raises InvalidInputException:
        :raises EntityNotFoundException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("GetLFTag")
    def get_lf_tag(
        self, context: RequestContext, tag_key: LFTagKey, catalog_id: CatalogIdString = None
    ) -> GetLFTagResponse:
        """Returns an LF-tag definition.

        :param tag_key: The key-name for the LF-tag.
        :param catalog_id: The identifier for the Data Catalog.
        :returns: GetLFTagResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("GetQueryState")
    def get_query_state(
        self, context: RequestContext, query_id: GetQueryStateRequestQueryIdString
    ) -> GetQueryStateResponse:
        """Returns the state of a query previously submitted. Clients are expected
        to poll ``GetQueryState`` to monitor the current state of the planning
        before retrieving the work units. A query state is only visible to the
        principal that made the initial call to ``StartQueryPlanning``.

        :param query_id: The ID of the plan query operation.
        :returns: GetQueryStateResponse
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("GetQueryStatistics")
    def get_query_statistics(
        self, context: RequestContext, query_id: GetQueryStatisticsRequestQueryIdString
    ) -> GetQueryStatisticsResponse:
        """Retrieves statistics on the planning and execution of a query.

        :param query_id: The ID of the plan query operation.
        :returns: GetQueryStatisticsResponse
        :raises StatisticsNotReadyYetException:
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises ExpiredException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetResourceLFTags")
    def get_resource_lf_tags(
        self,
        context: RequestContext,
        resource: Resource,
        catalog_id: CatalogIdString = None,
        show_assigned_lf_tags: BooleanNullable = None,
    ) -> GetResourceLFTagsResponse:
        """Returns the LF-tags applied to a resource.

        :param resource: The database, table, or column resource for which you want to return
        LF-tags.
        :param catalog_id: The identifier for the Data Catalog.
        :param show_assigned_lf_tags: Indicates whether to show the assigned LF-tags.
        :returns: GetResourceLFTagsResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("GetTableObjects")
    def get_table_objects(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        catalog_id: CatalogIdString = None,
        transaction_id: TransactionIdString = None,
        query_as_of_time: Timestamp = None,
        partition_predicate: PredicateString = None,
        max_results: PageSize = None,
        next_token: TokenString = None,
    ) -> GetTableObjectsResponse:
        """Returns the set of Amazon S3 objects that make up the specified governed
        table. A transaction ID or timestamp can be specified for time-travel
        queries.

        :param database_name: The database containing the governed table.
        :param table_name: The governed table for which to retrieve objects.
        :param catalog_id: The catalog containing the governed table.
        :param transaction_id: The transaction ID at which to read the governed table contents.
        :param query_as_of_time: The time as of when to read the governed table contents.
        :param partition_predicate: A predicate to filter the objects returned based on the partition keys
        defined in the governed table.
        :param max_results: Specifies how many values to return in a page.
        :param next_token: A continuation token if this is not the first call to retrieve these
        objects.
        :returns: GetTableObjectsResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises TransactionCommittedException:
        :raises TransactionCanceledException:
        :raises ResourceNotReadyException:
        """
        raise NotImplementedError

    @handler("GetTemporaryGluePartitionCredentials")
    def get_temporary_glue_partition_credentials(
        self,
        context: RequestContext,
        table_arn: ResourceArnString,
        partition: PartitionValueList,
        supported_permission_types: PermissionTypeList,
        permissions: PermissionList = None,
        duration_seconds: CredentialTimeoutDurationSecondInteger = None,
        audit_context: AuditContext = None,
    ) -> GetTemporaryGluePartitionCredentialsResponse:
        """This API is identical to ``GetTemporaryTableCredentials`` except that
        this is used when the target Data Catalog resource is of type Partition.
        Lake Formation restricts the permission of the vended credentials with
        the same scope down policy which restricts access to a single Amazon S3
        prefix.

        :param table_arn: The ARN of the partitions' table.
        :param partition: A list of partition values identifying a single partition.
        :param supported_permission_types: A list of supported permission types for the partition.
        :param permissions: Filters the request based on the user having been granted a list of
        specified permissions on the requested resource(s).
        :param duration_seconds: The time period, between 900 and 21,600 seconds, for the timeout of the
        temporary credentials.
        :param audit_context: A structure representing context to access a resource (column names,
        query ID, etc).
        :returns: GetTemporaryGluePartitionCredentialsResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        :raises AccessDeniedException:
        :raises PermissionTypeMismatchException:
        """
        raise NotImplementedError

    @handler("GetTemporaryGlueTableCredentials")
    def get_temporary_glue_table_credentials(
        self,
        context: RequestContext,
        table_arn: ResourceArnString,
        supported_permission_types: PermissionTypeList,
        permissions: PermissionList = None,
        duration_seconds: CredentialTimeoutDurationSecondInteger = None,
        audit_context: AuditContext = None,
    ) -> GetTemporaryGlueTableCredentialsResponse:
        """Allows a caller in a secure environment to assume a role with permission
        to access Amazon S3. In order to vend such credentials, Lake Formation
        assumes the role associated with a registered location, for example an
        Amazon S3 bucket, with a scope down policy which restricts the access to
        a single prefix.

        :param table_arn: The ARN identifying a table in the Data Catalog for the temporary
        credentials request.
        :param supported_permission_types: A list of supported permission types for the table.
        :param permissions: Filters the request based on the user having been granted a list of
        specified permissions on the requested resource(s).
        :param duration_seconds: The time period, between 900 and 21,600 seconds, for the timeout of the
        temporary credentials.
        :param audit_context: A structure representing context to access a resource (column names,
        query ID, etc).
        :returns: GetTemporaryGlueTableCredentialsResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        :raises AccessDeniedException:
        :raises PermissionTypeMismatchException:
        """
        raise NotImplementedError

    @handler("GetWorkUnitResults")
    def get_work_unit_results(
        self,
        context: RequestContext,
        query_id: GetWorkUnitResultsRequestQueryIdString,
        work_unit_id: GetWorkUnitResultsRequestWorkUnitIdLong,
        work_unit_token: SyntheticGetWorkUnitResultsRequestWorkUnitTokenString,
    ) -> GetWorkUnitResultsResponse:
        """Returns the work units resulting from the query. Work units can be
        executed in any order and in parallel.

        :param query_id: The ID of the plan query operation for which to get results.
        :param work_unit_id: The work unit ID for which to get results.
        :param work_unit_token: A work token used to query the execution service.
        :returns: GetWorkUnitResultsResponse
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises ExpiredException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetWorkUnits")
    def get_work_units(
        self,
        context: RequestContext,
        query_id: GetWorkUnitsRequestQueryIdString,
        next_token: Token = None,
        page_size: Integer = None,
    ) -> GetWorkUnitsResponse:
        """Retrieves the work units generated by the ``StartQueryPlanning``
        operation.

        :param query_id: The ID of the plan query operation.
        :param next_token: A continuation token, if this is a continuation call.
        :param page_size: The size of each page to get in the Amazon Web Services service call.
        :returns: GetWorkUnitsResponse
        :raises WorkUnitsNotReadyYetException:
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises ExpiredException:
        """
        raise NotImplementedError

    @handler("GrantPermissions")
    def grant_permissions(
        self,
        context: RequestContext,
        principal: DataLakePrincipal,
        resource: Resource,
        permissions: PermissionList,
        catalog_id: CatalogIdString = None,
        permissions_with_grant_option: PermissionList = None,
    ) -> GrantPermissionsResponse:
        """Grants permissions to the principal to access metadata in the Data
        Catalog and data organized in underlying data storage such as Amazon S3.

        For information about permissions, see `Security and Access Control to
        Metadata and
        Data <https://docs-aws.amazon.com/lake-formation/latest/dg/security-data-access.html>`__.

        :param principal: The principal to be granted the permissions on the resource.
        :param resource: The resource to which permissions are to be granted.
        :param permissions: The permissions granted to the principal on the resource.
        :param catalog_id: The identifier for the Data Catalog.
        :param permissions_with_grant_option: Indicates a list of the granted permissions that the principal may pass
        to other users.
        :returns: GrantPermissionsResponse
        :raises ConcurrentModificationException:
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("ListDataCellsFilter")
    def list_data_cells_filter(
        self,
        context: RequestContext,
        table: TableResource = None,
        next_token: Token = None,
        max_results: PageSize = None,
    ) -> ListDataCellsFilterResponse:
        """Lists all the data cell filters on a table.

        :param table: A table in the Glue Data Catalog.
        :param next_token: A continuation token, if this is a continuation call.
        :param max_results: The maximum size of the response.
        :returns: ListDataCellsFilterResponse
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("ListLFTags")
    def list_lf_tags(
        self,
        context: RequestContext,
        catalog_id: CatalogIdString = None,
        resource_share_type: ResourceShareType = None,
        max_results: PageSize = None,
        next_token: Token = None,
    ) -> ListLFTagsResponse:
        """Lists LF-tags that the requester has permission to view.

        :param catalog_id: The identifier for the Data Catalog.
        :param resource_share_type: If resource share type is ``ALL``, returns both in-account LF-tags and
        shared LF-tags that the requester has permission to view.
        :param max_results: The maximum number of results to return.
        :param next_token: A continuation token, if this is not the first call to retrieve this
        list.
        :returns: ListLFTagsResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("ListPermissions")
    def list_permissions(
        self,
        context: RequestContext,
        catalog_id: CatalogIdString = None,
        principal: DataLakePrincipal = None,
        resource_type: DataLakeResourceType = None,
        resource: Resource = None,
        next_token: Token = None,
        max_results: PageSize = None,
        include_related: TrueFalseString = None,
    ) -> ListPermissionsResponse:
        """Returns a list of the principal permissions on the resource, filtered by
        the permissions of the caller. For example, if you are granted an ALTER
        permission, you are able to see only the principal permissions for
        ALTER.

        This operation returns only those permissions that have been explicitly
        granted.

        For information about permissions, see `Security and Access Control to
        Metadata and
        Data <https://docs-aws.amazon.com/lake-formation/latest/dg/security-data-access.html>`__.

        :param catalog_id: The identifier for the Data Catalog.
        :param principal: Specifies a principal to filter the permissions returned.
        :param resource_type: Specifies a resource type to filter the permissions returned.
        :param resource: A resource where you will get a list of the principal permissions.
        :param next_token: A continuation token, if this is not the first call to retrieve this
        list.
        :param max_results: The maximum number of results to return.
        :param include_related: Indicates that related permissions should be included in the results.
        :returns: ListPermissionsResponse
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("ListResources")
    def list_resources(
        self,
        context: RequestContext,
        filter_condition_list: FilterConditionList = None,
        max_results: PageSize = None,
        next_token: Token = None,
    ) -> ListResourcesResponse:
        """Lists the resources registered to be managed by the Data Catalog.

        :param filter_condition_list: Any applicable row-level and/or column-level filtering conditions for
        the resources.
        :param max_results: The maximum number of resource results.
        :param next_token: A continuation token, if this is not the first call to retrieve these
        resources.
        :returns: ListResourcesResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("ListTableStorageOptimizers")
    def list_table_storage_optimizers(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        catalog_id: CatalogIdString = None,
        storage_optimizer_type: OptimizerType = None,
        max_results: PageSize = None,
        next_token: Token = None,
    ) -> ListTableStorageOptimizersResponse:
        """Returns the configuration of all storage optimizers associated with a
        specified table.

        :param database_name: Name of the database where the table is present.
        :param table_name: Name of the table.
        :param catalog_id: The Catalog ID of the table.
        :param storage_optimizer_type: The specific type of storage optimizers to list.
        :param max_results: The number of storage optimizers to return on each call.
        :param next_token: A continuation token, if this is a continuation call.
        :returns: ListTableStorageOptimizersResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("ListTransactions")
    def list_transactions(
        self,
        context: RequestContext,
        catalog_id: CatalogIdString = None,
        status_filter: TransactionStatusFilter = None,
        max_results: PageSize = None,
        next_token: TokenString = None,
    ) -> ListTransactionsResponse:
        """Returns metadata about transactions and their status. To prevent the
        response from growing indefinitely, only uncommitted transactions and
        those available for time-travel queries are returned.

        This operation can help you identify uncommitted transactions or to get
        information about transactions.

        :param catalog_id: The catalog for which to list transactions.
        :param status_filter: A filter indicating the status of transactions to return.
        :param max_results: The maximum number of transactions to return in a single call.
        :param next_token: A continuation token if this is not the first call to retrieve
        transactions.
        :returns: ListTransactionsResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("PutDataLakeSettings")
    def put_data_lake_settings(
        self,
        context: RequestContext,
        data_lake_settings: DataLakeSettings,
        catalog_id: CatalogIdString = None,
    ) -> PutDataLakeSettingsResponse:
        """Sets the list of data lake administrators who have admin privileges on
        all resources managed by Lake Formation. For more information on admin
        privileges, see `Granting Lake Formation
        Permissions <https://docs.aws.amazon.com/lake-formation/latest/dg/lake-formation-permissions.html>`__.

        This API replaces the current list of data lake admins with the new list
        being passed. To add an admin, fetch the current list and add the new
        admin to that list and pass that list in this API.

        :param data_lake_settings: A structure representing a list of Lake Formation principals designated
        as data lake administrators.
        :param catalog_id: The identifier for the Data Catalog.
        :returns: PutDataLakeSettingsResponse
        :raises InternalServiceException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("RegisterResource")
    def register_resource(
        self,
        context: RequestContext,
        resource_arn: ResourceArnString,
        use_service_linked_role: NullableBoolean = None,
        role_arn: IAMRoleArn = None,
    ) -> RegisterResourceResponse:
        """Registers the resource as managed by the Data Catalog.

        To add or update data, Lake Formation needs read/write access to the
        chosen Amazon S3 path. Choose a role that you know has permission to do
        this, or choose the AWSServiceRoleForLakeFormationDataAccess
        service-linked role. When you register the first Amazon S3 path, the
        service-linked role and a new inline policy are created on your behalf.
        Lake Formation adds the first path to the inline policy and attaches it
        to the service-linked role. When you register subsequent paths, Lake
        Formation adds the path to the existing policy.

        The following request registers a new location and gives Lake Formation
        permission to use the service-linked role to access that location.

        ``ResourceArn = arn:aws:s3:::my-bucket UseServiceLinkedRole = true``

        If ``UseServiceLinkedRole`` is not set to true, you must provide or set
        the ``RoleArn``:

        ``arn:aws:iam::12345:role/my-data-access-role``

        :param resource_arn: The Amazon Resource Name (ARN) of the resource that you want to
        register.
        :param use_service_linked_role: Designates an Identity and Access Management (IAM) service-linked role
        by registering this role with the Data Catalog.
        :param role_arn: The identifier for the role that registers the resource.
        :returns: RegisterResourceResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises AlreadyExistsException:
        :raises EntityNotFoundException:
        :raises ResourceNumberLimitExceededException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("RemoveLFTagsFromResource")
    def remove_lf_tags_from_resource(
        self,
        context: RequestContext,
        resource: Resource,
        lf_tags: LFTagsList,
        catalog_id: CatalogIdString = None,
    ) -> RemoveLFTagsFromResourceResponse:
        """Removes an LF-tag from the resource. Only database, table, or
        tableWithColumns resource are allowed. To tag columns, use the column
        inclusion list in ``tableWithColumns`` to specify column input.

        :param resource: The database, table, or column resource where you want to remove an
        LF-tag.
        :param lf_tags: The LF-tags to be removed from the resource.
        :param catalog_id: The identifier for the Data Catalog.
        :returns: RemoveLFTagsFromResourceResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises AccessDeniedException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("RevokePermissions")
    def revoke_permissions(
        self,
        context: RequestContext,
        principal: DataLakePrincipal,
        resource: Resource,
        permissions: PermissionList,
        catalog_id: CatalogIdString = None,
        permissions_with_grant_option: PermissionList = None,
    ) -> RevokePermissionsResponse:
        """Revokes permissions to the principal to access metadata in the Data
        Catalog and data organized in underlying data storage such as Amazon S3.

        :param principal: The principal to be revoked permissions on the resource.
        :param resource: The resource to which permissions are to be revoked.
        :param permissions: The permissions revoked to the principal on the resource.
        :param catalog_id: The identifier for the Data Catalog.
        :param permissions_with_grant_option: Indicates a list of permissions for which to revoke the grant option
        allowing the principal to pass permissions to other principals.
        :returns: RevokePermissionsResponse
        :raises ConcurrentModificationException:
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        """
        raise NotImplementedError

    @handler("SearchDatabasesByLFTags")
    def search_databases_by_lf_tags(
        self,
        context: RequestContext,
        expression: Expression,
        next_token: Token = None,
        max_results: PageSize = None,
        catalog_id: CatalogIdString = None,
    ) -> SearchDatabasesByLFTagsResponse:
        """This operation allows a search on ``DATABASE`` resources by
        ``TagCondition``. This operation is used by admins who want to grant
        user permissions on certain ``TagConditions``. Before making a grant,
        the admin can use ``SearchDatabasesByTags`` to find all resources where
        the given ``TagConditions`` are valid to verify whether the returned
        resources can be shared.

        :param expression: A list of conditions (``LFTag`` structures) to search for in database
        resources.
        :param next_token: A continuation token, if this is not the first call to retrieve this
        list.
        :param max_results: The maximum number of results to return.
        :param catalog_id: The identifier for the Data Catalog.
        :returns: SearchDatabasesByLFTagsResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("SearchTablesByLFTags")
    def search_tables_by_lf_tags(
        self,
        context: RequestContext,
        expression: Expression,
        next_token: Token = None,
        max_results: PageSize = None,
        catalog_id: CatalogIdString = None,
    ) -> SearchTablesByLFTagsResponse:
        """This operation allows a search on ``TABLE`` resources by ``LFTag`` s.
        This will be used by admins who want to grant user permissions on
        certain LF-tags. Before making a grant, the admin can use
        ``SearchTablesByLFTags`` to find all resources where the given
        ``LFTag`` s are valid to verify whether the returned resources can be
        shared.

        :param expression: A list of conditions (``LFTag`` structures) to search for in table
        resources.
        :param next_token: A continuation token, if this is not the first call to retrieve this
        list.
        :param max_results: The maximum number of results to return.
        :param catalog_id: The identifier for the Data Catalog.
        :returns: SearchTablesByLFTagsResponse
        :raises EntityNotFoundException:
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises GlueEncryptionException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("StartQueryPlanning")
    def start_query_planning(
        self,
        context: RequestContext,
        query_planning_context: QueryPlanningContext,
        query_string: SyntheticStartQueryPlanningRequestQueryString,
    ) -> StartQueryPlanningResponse:
        """Submits a request to process a query statement.

        This operation generates work units that can be retrieved with the
        ``GetWorkUnits`` operation as soon as the query state is
        WORKUNITS_AVAILABLE or FINISHED.

        :param query_planning_context: A structure containing information about the query plan.
        :param query_string: A PartiQL query statement used as an input to the planner service.
        :returns: StartQueryPlanningResponse
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("StartTransaction")
    def start_transaction(
        self, context: RequestContext, transaction_type: TransactionType = None
    ) -> StartTransactionResponse:
        """Starts a new transaction and returns its transaction ID. Transaction IDs
        are opaque objects that you can use to identify a transaction.

        :param transaction_type: Indicates whether this transaction should be read only or read and
        write.
        :returns: StartTransactionResponse
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        """
        raise NotImplementedError

    @handler("UpdateLFTag")
    def update_lf_tag(
        self,
        context: RequestContext,
        tag_key: LFTagKey,
        catalog_id: CatalogIdString = None,
        tag_values_to_delete: TagValueList = None,
        tag_values_to_add: TagValueList = None,
    ) -> UpdateLFTagResponse:
        """Updates the list of possible values for the specified LF-tag key. If the
        LF-tag does not exist, the operation throws an EntityNotFoundException.
        The values in the delete key values will be deleted from list of
        possible values. If any value in the delete key values is attached to a
        resource, then API errors out with a 400 Exception - "Update not
        allowed". Untag the attribute before deleting the LF-tag key's value.

        :param tag_key: The key-name for the LF-tag for which to add or delete values.
        :param catalog_id: The identifier for the Data Catalog.
        :param tag_values_to_delete: A list of LF-tag values to delete from the LF-tag.
        :param tag_values_to_add: A list of LF-tag values to add from the LF-tag.
        :returns: UpdateLFTagResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises ConcurrentModificationException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("UpdateResource")
    def update_resource(
        self, context: RequestContext, role_arn: IAMRoleArn, resource_arn: ResourceArnString
    ) -> UpdateResourceResponse:
        """Updates the data access role used for vending access to the given
        (registered) resource in Lake Formation.

        :param role_arn: The new role to use for the given resource registered in Lake Formation.
        :param resource_arn: The resource ARN.
        :returns: UpdateResourceResponse
        :raises InvalidInputException:
        :raises InternalServiceException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateTableObjects")
    def update_table_objects(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        write_operations: WriteOperationList,
        catalog_id: CatalogIdString = None,
        transaction_id: TransactionIdString = None,
    ) -> UpdateTableObjectsResponse:
        """Updates the manifest of Amazon S3 objects that make up the specified
        governed table.

        :param database_name: The database containing the governed table to update.
        :param table_name: The governed table to update.
        :param write_operations: A list of ``WriteOperation`` objects that define an object to add to or
        delete from the manifest for a governed table.
        :param catalog_id: The catalog containing the governed table to update.
        :param transaction_id: The transaction at which to do the write.
        :returns: UpdateTableObjectsResponse
        :raises InternalServiceException:
        :raises InvalidInputException:
        :raises OperationTimeoutException:
        :raises EntityNotFoundException:
        :raises TransactionCommittedException:
        :raises TransactionCanceledException:
        :raises TransactionCommitInProgressException:
        :raises ResourceNotReadyException:
        :raises ConcurrentModificationException:
        """
        raise NotImplementedError

    @handler("UpdateTableStorageOptimizer")
    def update_table_storage_optimizer(
        self,
        context: RequestContext,
        database_name: NameString,
        table_name: NameString,
        storage_optimizer_config: StorageOptimizerConfigMap,
        catalog_id: CatalogIdString = None,
    ) -> UpdateTableStorageOptimizerResponse:
        """Updates the configuration of the storage optimizers for a table.

        :param database_name: Name of the database where the table is present.
        :param table_name: Name of the table for which to enable the storage optimizer.
        :param storage_optimizer_config: Name of the table for which to enable the storage optimizer.
        :param catalog_id: The Catalog ID of the table.
        :returns: UpdateTableStorageOptimizerResponse
        :raises EntityNotFoundException:
        :raises InvalidInputException:
        :raises AccessDeniedException:
        :raises InternalServiceException:
        """
        raise NotImplementedError
