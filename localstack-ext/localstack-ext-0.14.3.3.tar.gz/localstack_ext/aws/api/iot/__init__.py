import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AbortThresholdPercentage = float
AcmCertificateArn = str
AggregationField = str
AggregationTypeValue = str
AlarmName = str
AlertTargetArn = str
AllowAuthorizerOverride = bool
AllowAutoRegistration = bool
AscendingOrder = bool
AssetId = str
AssetPropertyAlias = str
AssetPropertyBooleanValue = str
AssetPropertyDoubleValue = str
AssetPropertyEntryId = str
AssetPropertyId = str
AssetPropertyIntegerValue = str
AssetPropertyOffsetInNanos = str
AssetPropertyQuality = str
AssetPropertyStringValue = str
AssetPropertyTimeInSeconds = str
AttributeKey = str
AttributeName = str
AttributeValue = str
AuditCheckName = str
AuditDescription = str
AuditTaskId = str
AuthorizerArn = str
AuthorizerFunctionArn = str
AuthorizerName = str
Average = float
AwsAccountId = str
AwsArn = str
AwsIotJobArn = str
AwsIotJobId = str
AwsIotSqlVersion = str
AwsJobAbortCriteriaAbortThresholdPercentage = float
AwsJobAbortCriteriaMinimumNumberOfExecutedThings = int
AwsJobRateIncreaseCriteriaNumberOfThings = int
AwsJobRolloutIncrementFactor = float
AwsJobRolloutRatePerMinute = int
BatchMode = bool
BehaviorMetric = str
BehaviorName = str
BillingGroupArn = str
BillingGroupDescription = str
BillingGroupId = str
BillingGroupName = str
Boolean = bool
BooleanKey = bool
BooleanWrapperObject = bool
BucketKeyValue = str
BucketName = str
CanceledChecksCount = int
CanceledThings = int
CertificateArn = str
CertificateId = str
CertificateName = str
CertificatePathOnDevice = str
CertificatePem = str
CertificateSigningRequest = str
ChannelName = str
CheckCompliant = bool
Cidr = str
ClientId = str
ClientRequestToken = str
Code = str
CognitoIdentityPoolId = str
Comment = str
CompliantChecksCount = int
ConfirmationToken = str
ConsecutiveDatapointsToAlarm = int
ConsecutiveDatapointsToClear = int
Count = int
CredentialDurationSeconds = int
CustomMetricArn = str
CustomMetricDisplayName = str
CustomerVersion = int
DataCollectionPercentage = float
DayOfMonth = str
DeleteAdditionalMetricsToRetain = bool
DeleteAlertTargets = bool
DeleteBehaviors = bool
DeleteScheduledAudits = bool
DeleteStream = bool
DeliveryStreamName = str
Description = str
DetailsKey = str
DetailsValue = str
DetectMitigationActionExecutionErrorCode = str
DeviceDefenderThingName = str
DimensionArn = str
DimensionName = str
DimensionStringValue = str
DisableAllLogs = bool
DisconnectReason = str
DomainConfigurationArn = str
DomainConfigurationName = str
DomainName = str
DurationSeconds = int
DynamoOperation = str
ElasticsearchEndpoint = str
ElasticsearchId = str
ElasticsearchIndex = str
ElasticsearchType = str
EnableCachingForHttp = bool
Enabled = bool
EndpointAddress = str
EndpointType = str
Environment = str
ErrorCode = str
ErrorMessage = str
EvaluationStatistic = str
Example = str
ExecutionNamePrefix = str
FailedChecksCount = int
FailedThings = int
FieldName = str
FileId = int
FileName = str
FileType = int
FindingId = str
FirehoseSeparator = str
Flag = bool
FleetMetricArn = str
FleetMetricDescription = str
FleetMetricName = str
FleetMetricPeriod = int
ForceDelete = bool
ForceDeleteAWSJob = bool
ForceFlag = bool
Forced = bool
FunctionArn = str
GenerationId = str
HashAlgorithm = str
HashKeyField = str
HashKeyValue = str
HeaderKey = str
HeaderValue = str
HttpHeaderName = str
HttpHeaderValue = str
HttpQueryString = str
InProgressChecksCount = int
InProgressThings = int
IncrementFactor = float
IndexName = str
IndexSchema = str
InlineDocument = str
InputName = str
IsAuthenticated = bool
IsDefaultVersion = bool
IsDisabled = bool
IsSuppressed = bool
JobArn = str
JobDescription = str
JobDocument = str
JobDocumentSource = str
JobId = str
JobTemplateArn = str
JobTemplateId = str
JsonDocument = str
Key = str
KeyName = str
KeyValue = str
LaserMaxResults = int
ListSuppressedAlerts = bool
ListSuppressedFindings = bool
LogGroupName = str
LogTargetName = str
ManagedJobTemplateName = str
ManagedTemplateVersion = str
Marker = str
MaxBuckets = int
MaxJobExecutionsPerMin = int
MaxResults = int
Maximum = float
MaximumPerMinute = int
Message = str
MessageId = str
MetricName = str
Minimum = float
MinimumNumberOfExecutedThings = int
MissingContextValue = str
MitigationActionArn = str
MitigationActionId = str
MitigationActionName = str
MitigationActionsTaskId = str
MqttClientId = str
MqttUsername = str
NamespaceId = str
NextToken = str
NonCompliantChecksCount = int
NullableBoolean = bool
Number = float
NumberOfRetries = int
NumberOfThings = int
OTAUpdateArn = str
OTAUpdateDescription = str
OTAUpdateErrorMessage = str
OTAUpdateFileVersion = str
OTAUpdateId = str
Optional_ = bool
OverrideDynamicGroups = bool
PageSize = int
Parameter = str
ParameterKey = str
ParameterValue = str
PartitionKey = str
PayloadField = str
PayloadVersion = str
Percent = float
PercentValue = float
Percentage = int
Platform = str
PolicyArn = str
PolicyDocument = str
PolicyName = str
PolicyTarget = str
PolicyVersionId = str
Port = int
Prefix = str
PrimitiveBoolean = bool
Principal = str
PrincipalArn = str
PrincipalId = str
PrivateKey = str
ProcessingTargetName = str
PublicKey = str
Qos = int
QueryMaxResults = int
QueryString = str
QueryVersion = str
QueueUrl = str
QueuedThings = int
RangeKeyField = str
RangeKeyValue = str
ReasonCode = str
ReasonForNonCompliance = str
ReasonForNonComplianceCode = str
Recursive = bool
RecursiveWithoutDefault = bool
Regex = str
RegistrationCode = str
RegistryMaxResults = int
RegistryS3BucketName = str
RegistryS3KeyName = str
RejectedThings = int
RemoveAuthorizerConfig = bool
RemoveAutoRegistration = bool
RemoveHook = bool
RemoveThingType = bool
RemovedThings = int
ReservedDomainConfigurationName = str
Resource = str
ResourceArn = str
ResourceLogicalId = str
RetryAttempt = int
RoleAlias = str
RoleAliasArn = str
RoleArn = str
RolloutRatePerMinute = int
RuleArn = str
RuleName = str
S3Bucket = str
S3FileUrl = str
S3Key = str
S3Version = str
SQL = str
SalesforceEndpoint = str
SalesforceToken = str
ScheduledAuditArn = str
ScheduledAuditName = str
Seconds = int
SecurityGroupId = str
SecurityProfileArn = str
SecurityProfileDescription = str
SecurityProfileName = str
SecurityProfileTargetArn = str
ServerCertificateStatusDetail = str
ServerName = str
ServiceName = str
SetAsActive = bool
SetAsActiveFlag = bool
SetAsDefault = bool
SignatureAlgorithm = str
SigningJobId = str
SigningProfileName = str
SigningRegion = str
SkyfallMaxResults = int
SnsTopicArn = str
StateMachineName = str
StateReason = str
StateValue = str
StdDeviation = float
StreamArn = str
StreamDescription = str
StreamId = str
StreamName = str
StreamVersion = int
String = str
SubnetId = str
SucceededThings = int
Sum = float
SumOfSquares = float
SuppressAlerts = bool
SuppressIndefinitely = bool
TableName = str
TagKey = str
TagValue = str
Target = str
TargetArn = str
TaskId = str
TemplateArn = str
TemplateBody = str
TemplateDescription = str
TemplateName = str
TemplateVersionId = int
ThingArn = str
ThingGroupArn = str
ThingGroupDescription = str
ThingGroupId = str
ThingGroupName = str
ThingId = str
ThingName = str
ThingTypeArn = str
ThingTypeDescription = str
ThingTypeId = str
ThingTypeName = str
TimedOutThings = int
TimestreamDatabaseName = str
TimestreamDimensionName = str
TimestreamDimensionValue = str
TimestreamTableName = str
TimestreamTimestampUnit = str
TimestreamTimestampValue = str
TinyMaxResults = int
Token = str
TokenKeyName = str
TokenSignature = str
Topic = str
TopicPattern = str
TopicRuleDestinationMaxResults = int
TopicRuleMaxResults = int
TotalChecksCount = int
UndoDeprecate = bool
Url = str
UseBase64 = bool
Valid = bool
Value = str
Variance = float
VerificationStateDescription = str
ViolationId = str
VpcId = str
WaitingForDataCollectionChecksCount = int
errorMessage = str
resourceArn = str
resourceId = str
stringValue = str
usePrefixAttributeValue = bool


class AbortAction(str):
    CANCEL = "CANCEL"


class ActionType(str):
    PUBLISH = "PUBLISH"
    SUBSCRIBE = "SUBSCRIBE"
    RECEIVE = "RECEIVE"
    CONNECT = "CONNECT"


class AggregationTypeName(str):
    Statistics = "Statistics"
    Percentiles = "Percentiles"
    Cardinality = "Cardinality"


class AlertTargetType(str):
    SNS = "SNS"


class AuditCheckRunStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_DATA_COLLECTION = "WAITING_FOR_DATA_COLLECTION"
    CANCELED = "CANCELED"
    COMPLETED_COMPLIANT = "COMPLETED_COMPLIANT"
    COMPLETED_NON_COMPLIANT = "COMPLETED_NON_COMPLIANT"
    FAILED = "FAILED"


class AuditFindingSeverity(str):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AuditFrequency(str):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"


class AuditMitigationActionsExecutionStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    SKIPPED = "SKIPPED"
    PENDING = "PENDING"


class AuditMitigationActionsTaskStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class AuditNotificationType(str):
    SNS = "SNS"


class AuditTaskStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class AuditTaskType(str):
    ON_DEMAND_AUDIT_TASK = "ON_DEMAND_AUDIT_TASK"
    SCHEDULED_AUDIT_TASK = "SCHEDULED_AUDIT_TASK"


class AuthDecision(str):
    ALLOWED = "ALLOWED"
    EXPLICIT_DENY = "EXPLICIT_DENY"
    IMPLICIT_DENY = "IMPLICIT_DENY"


class AuthorizerStatus(str):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class AutoRegistrationStatus(str):
    ENABLE = "ENABLE"
    DISABLE = "DISABLE"


class AwsJobAbortCriteriaAbortAction(str):
    CANCEL = "CANCEL"


class AwsJobAbortCriteriaFailureType(str):
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    TIMED_OUT = "TIMED_OUT"
    ALL = "ALL"


class BehaviorCriteriaType(str):
    STATIC = "STATIC"
    STATISTICAL = "STATISTICAL"
    MACHINE_LEARNING = "MACHINE_LEARNING"


class CACertificateStatus(str):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class CACertificateUpdateAction(str):
    DEACTIVATE = "DEACTIVATE"


class CannedAccessControlList(str):
    private = "private"
    public_read = "public-read"
    public_read_write = "public-read-write"
    aws_exec_read = "aws-exec-read"
    authenticated_read = "authenticated-read"
    bucket_owner_read = "bucket-owner-read"
    bucket_owner_full_control = "bucket-owner-full-control"
    log_delivery_write = "log-delivery-write"


class CertificateMode(str):
    DEFAULT = "DEFAULT"
    SNI_ONLY = "SNI_ONLY"


class CertificateStatus(str):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    REVOKED = "REVOKED"
    PENDING_TRANSFER = "PENDING_TRANSFER"
    REGISTER_INACTIVE = "REGISTER_INACTIVE"
    PENDING_ACTIVATION = "PENDING_ACTIVATION"


class ComparisonOperator(str):
    less_than = "less-than"
    less_than_equals = "less-than-equals"
    greater_than = "greater-than"
    greater_than_equals = "greater-than-equals"
    in_cidr_set = "in-cidr-set"
    not_in_cidr_set = "not-in-cidr-set"
    in_port_set = "in-port-set"
    not_in_port_set = "not-in-port-set"
    in_set = "in-set"
    not_in_set = "not-in-set"


class ConfidenceLevel(str):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CustomMetricType(str):
    string_list = "string-list"
    ip_address_list = "ip-address-list"
    number_list = "number-list"
    number = "number"


class DayOfWeek(str):
    SUN = "SUN"
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"


class DetectMitigationActionExecutionStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class DetectMitigationActionsTaskStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class DeviceCertificateUpdateAction(str):
    DEACTIVATE = "DEACTIVATE"


class DeviceDefenderIndexingMode(str):
    OFF = "OFF"
    VIOLATIONS = "VIOLATIONS"


class DimensionType(str):
    TOPIC_FILTER = "TOPIC_FILTER"


class DimensionValueOperator(str):
    IN = "IN"
    NOT_IN = "NOT_IN"


class DomainConfigurationStatus(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class DomainType(str):
    ENDPOINT = "ENDPOINT"
    AWS_MANAGED = "AWS_MANAGED"
    CUSTOMER_MANAGED = "CUSTOMER_MANAGED"


class DynamicGroupStatus(str):
    ACTIVE = "ACTIVE"
    BUILDING = "BUILDING"
    REBUILDING = "REBUILDING"


class DynamoKeyType(str):
    STRING = "STRING"
    NUMBER = "NUMBER"


class EventType(str):
    THING = "THING"
    THING_GROUP = "THING_GROUP"
    THING_TYPE = "THING_TYPE"
    THING_GROUP_MEMBERSHIP = "THING_GROUP_MEMBERSHIP"
    THING_GROUP_HIERARCHY = "THING_GROUP_HIERARCHY"
    THING_TYPE_ASSOCIATION = "THING_TYPE_ASSOCIATION"
    JOB = "JOB"
    JOB_EXECUTION = "JOB_EXECUTION"
    POLICY = "POLICY"
    CERTIFICATE = "CERTIFICATE"
    CA_CERTIFICATE = "CA_CERTIFICATE"


class FieldType(str):
    Number = "Number"
    String = "String"
    Boolean = "Boolean"


class FleetMetricUnit(str):
    Seconds = "Seconds"
    Microseconds = "Microseconds"
    Milliseconds = "Milliseconds"
    Bytes = "Bytes"
    Kilobytes = "Kilobytes"
    Megabytes = "Megabytes"
    Gigabytes = "Gigabytes"
    Terabytes = "Terabytes"
    Bits = "Bits"
    Kilobits = "Kilobits"
    Megabits = "Megabits"
    Gigabits = "Gigabits"
    Terabits = "Terabits"
    Percent = "Percent"
    Count = "Count"
    Bytes_Second = "Bytes/Second"
    Kilobytes_Second = "Kilobytes/Second"
    Megabytes_Second = "Megabytes/Second"
    Gigabytes_Second = "Gigabytes/Second"
    Terabytes_Second = "Terabytes/Second"
    Bits_Second = "Bits/Second"
    Kilobits_Second = "Kilobits/Second"
    Megabits_Second = "Megabits/Second"
    Gigabits_Second = "Gigabits/Second"
    Terabits_Second = "Terabits/Second"
    Count_Second = "Count/Second"
    None_ = "None"


class IndexStatus(str):
    ACTIVE = "ACTIVE"
    BUILDING = "BUILDING"
    REBUILDING = "REBUILDING"


class JobExecutionFailureType(str):
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    TIMED_OUT = "TIMED_OUT"
    ALL = "ALL"


class JobExecutionStatus(str):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    REJECTED = "REJECTED"
    REMOVED = "REMOVED"
    CANCELED = "CANCELED"


class JobStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
    DELETION_IN_PROGRESS = "DELETION_IN_PROGRESS"


class LogLevel(str):
    DEBUG = "DEBUG"
    INFO = "INFO"
    ERROR = "ERROR"
    WARN = "WARN"
    DISABLED = "DISABLED"


class LogTargetType(str):
    DEFAULT = "DEFAULT"
    THING_GROUP = "THING_GROUP"
    CLIENT_ID = "CLIENT_ID"
    SOURCE_IP = "SOURCE_IP"
    PRINCIPAL_ID = "PRINCIPAL_ID"


class MessageFormat(str):
    RAW = "RAW"
    JSON = "JSON"


class MitigationActionType(str):
    UPDATE_DEVICE_CERTIFICATE = "UPDATE_DEVICE_CERTIFICATE"
    UPDATE_CA_CERTIFICATE = "UPDATE_CA_CERTIFICATE"
    ADD_THINGS_TO_THING_GROUP = "ADD_THINGS_TO_THING_GROUP"
    REPLACE_DEFAULT_POLICY_VERSION = "REPLACE_DEFAULT_POLICY_VERSION"
    ENABLE_IOT_LOGGING = "ENABLE_IOT_LOGGING"
    PUBLISH_FINDING_TO_SNS = "PUBLISH_FINDING_TO_SNS"


class ModelStatus(str):
    PENDING_BUILD = "PENDING_BUILD"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"


class NamedShadowIndexingMode(str):
    OFF = "OFF"
    ON = "ON"


class OTAUpdateStatus(str):
    CREATE_PENDING = "CREATE_PENDING"
    CREATE_IN_PROGRESS = "CREATE_IN_PROGRESS"
    CREATE_COMPLETE = "CREATE_COMPLETE"
    CREATE_FAILED = "CREATE_FAILED"


class PolicyTemplateName(str):
    BLANK_POLICY = "BLANK_POLICY"


class Protocol(str):
    MQTT = "MQTT"
    HTTP = "HTTP"


class ReportType(str):
    ERRORS = "ERRORS"
    RESULTS = "RESULTS"


class ResourceType(str):
    DEVICE_CERTIFICATE = "DEVICE_CERTIFICATE"
    CA_CERTIFICATE = "CA_CERTIFICATE"
    IOT_POLICY = "IOT_POLICY"
    COGNITO_IDENTITY_POOL = "COGNITO_IDENTITY_POOL"
    CLIENT_ID = "CLIENT_ID"
    ACCOUNT_SETTINGS = "ACCOUNT_SETTINGS"
    ROLE_ALIAS = "ROLE_ALIAS"
    IAM_ROLE = "IAM_ROLE"


class RetryableFailureType(str):
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    ALL = "ALL"


class ServerCertificateStatus(str):
    INVALID = "INVALID"
    VALID = "VALID"


class ServiceType(str):
    DATA = "DATA"
    CREDENTIAL_PROVIDER = "CREDENTIAL_PROVIDER"
    JOBS = "JOBS"


class Status(str):
    InProgress = "InProgress"
    Completed = "Completed"
    Failed = "Failed"
    Cancelled = "Cancelled"
    Cancelling = "Cancelling"


class TargetSelection(str):
    CONTINUOUS = "CONTINUOUS"
    SNAPSHOT = "SNAPSHOT"


class ThingConnectivityIndexingMode(str):
    OFF = "OFF"
    STATUS = "STATUS"


class ThingGroupIndexingMode(str):
    OFF = "OFF"
    ON = "ON"


class ThingIndexingMode(str):
    OFF = "OFF"
    REGISTRY = "REGISTRY"
    REGISTRY_AND_SHADOW = "REGISTRY_AND_SHADOW"


class TopicRuleDestinationStatus(str):
    ENABLED = "ENABLED"
    IN_PROGRESS = "IN_PROGRESS"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    DELETING = "DELETING"


class VerificationState(str):
    FALSE_POSITIVE = "FALSE_POSITIVE"
    BENIGN_POSITIVE = "BENIGN_POSITIVE"
    TRUE_POSITIVE = "TRUE_POSITIVE"
    UNKNOWN = "UNKNOWN"


class ViolationEventType(str):
    in_alarm = "in-alarm"
    alarm_cleared = "alarm-cleared"
    alarm_invalidated = "alarm-invalidated"


class CertificateConflictException(ServiceException):
    """Unable to verify the CA certificate used to sign the device certificate
    you are attempting to register. This is happens when you have registered
    more than one CA certificate that has the same subject field and public
    key.
    """

    message: Optional[errorMessage]


class CertificateStateException(ServiceException):
    """The certificate operation is not allowed."""

    message: Optional[errorMessage]


class CertificateValidationException(ServiceException):
    """The certificate is invalid."""

    message: Optional[errorMessage]


class ConflictException(ServiceException):
    """A resource with the same name already exists."""

    message: Optional[errorMessage]


class ConflictingResourceUpdateException(ServiceException):
    """A conflicting resource update exception. This exception is thrown when
    two pending updates cause a conflict.
    """

    message: Optional[errorMessage]


class DeleteConflictException(ServiceException):
    """You can't delete the resource because it is attached to one or more
    resources.
    """

    message: Optional[errorMessage]


class IndexNotReadyException(ServiceException):
    """The index is not ready."""

    message: Optional[errorMessage]


class InternalException(ServiceException):
    """An unexpected error has occurred."""

    message: Optional[errorMessage]


class InternalFailureException(ServiceException):
    """An unexpected error has occurred."""

    message: Optional[errorMessage]


class InternalServerException(ServiceException):
    """Internal error from the service that indicates an unexpected error or
    that the service is unavailable.
    """

    message: Optional[errorMessage]


class InvalidAggregationException(ServiceException):
    """The aggregation is invalid."""

    message: Optional[errorMessage]


class InvalidQueryException(ServiceException):
    """The query is invalid."""

    message: Optional[errorMessage]


class InvalidRequestException(ServiceException):
    """The request is not valid."""

    message: Optional[errorMessage]


class InvalidResponseException(ServiceException):
    """The response is invalid."""

    message: Optional[errorMessage]


class InvalidStateTransitionException(ServiceException):
    """An attempt was made to change to an invalid state, for example by
    deleting a job or a job execution which is "IN_PROGRESS" without setting
    the ``force`` parameter.
    """

    message: Optional[errorMessage]


class LimitExceededException(ServiceException):
    """A limit has been exceeded."""

    message: Optional[errorMessage]


class MalformedPolicyException(ServiceException):
    """The policy documentation is not valid."""

    message: Optional[errorMessage]


class NotConfiguredException(ServiceException):
    """The resource is not configured."""

    message: Optional[errorMessage]


class RegistrationCodeValidationException(ServiceException):
    """The registration code is invalid."""

    message: Optional[errorMessage]


class ResourceAlreadyExistsException(ServiceException):
    """The resource already exists."""

    message: Optional[errorMessage]
    resourceId: Optional[resourceId]
    resourceArn: Optional[resourceArn]


class ResourceNotFoundException(ServiceException):
    """The specified resource does not exist."""

    message: Optional[errorMessage]


class ResourceRegistrationFailureException(ServiceException):
    """The resource registration failed."""

    message: Optional[errorMessage]


class ServiceUnavailableException(ServiceException):
    """The service is temporarily unavailable."""

    message: Optional[errorMessage]


class SqlParseException(ServiceException):
    """The Rule-SQL expression can't be parsed correctly."""

    message: Optional[errorMessage]


class TaskAlreadyExistsException(ServiceException):
    """This exception occurs if you attempt to start a task with the same
    task-id as an existing task but with a different clientRequestToken.
    """

    message: Optional[errorMessage]


class ThrottlingException(ServiceException):
    """The rate exceeds the limit."""

    message: Optional[errorMessage]


class TransferAlreadyCompletedException(ServiceException):
    """You can't revert the certificate transfer because the transfer is
    already complete.
    """

    message: Optional[errorMessage]


class TransferConflictException(ServiceException):
    """You can't transfer the certificate because authorization policies are
    still attached.
    """

    message: Optional[errorMessage]


class UnauthorizedException(ServiceException):
    """You are not authorized to perform this operation."""

    message: Optional[errorMessage]


class VersionConflictException(ServiceException):
    """An exception thrown when the version of an entity specified with the
    ``expectedVersion`` parameter does not match the latest version in the
    system.
    """

    message: Optional[errorMessage]


class VersionsLimitExceededException(ServiceException):
    """The number of policy versions exceeds the limit."""

    message: Optional[errorMessage]


class AbortCriteria(TypedDict, total=False):
    """The criteria that determine when and how a job abort takes place."""

    failureType: JobExecutionFailureType
    action: AbortAction
    thresholdPercentage: AbortThresholdPercentage
    minNumberOfExecutedThings: MinimumNumberOfExecutedThings


AbortCriteriaList = List[AbortCriteria]


class AbortConfig(TypedDict, total=False):
    """The criteria that determine when and how a job abort takes place."""

    criteriaList: AbortCriteriaList


class AcceptCertificateTransferRequest(ServiceRequest):
    """The input for the AcceptCertificateTransfer operation."""

    certificateId: CertificateId
    setAsActive: Optional[SetAsActive]


OpenSearchAction = TypedDict(
    "OpenSearchAction",
    {
        "roleArn": AwsArn,
        "endpoint": ElasticsearchEndpoint,
        "index": ElasticsearchIndex,
        "type": ElasticsearchType,
        "id": ElasticsearchId,
    },
    total=False,
)
ClientProperties = Dict[String, String]


class KafkaAction(TypedDict, total=False):
    """Send messages to an Amazon Managed Streaming for Apache Kafka (Amazon
    MSK) or self-managed Apache Kafka cluster.
    """

    destinationArn: AwsArn
    topic: String
    key: Optional[String]
    partition: Optional[String]
    clientProperties: ClientProperties


class SigV4Authorization(TypedDict, total=False):
    """For more information, see `Signature Version 4 signing
    process <https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html>`__.
    """

    signingRegion: SigningRegion
    serviceName: ServiceName
    roleArn: AwsArn


class HttpAuthorization(TypedDict, total=False):
    """The authorization method used to send messages."""

    sigv4: Optional[SigV4Authorization]


class HttpActionHeader(TypedDict, total=False):
    """The HTTP action header."""

    key: HeaderKey
    value: HeaderValue


HeaderList = List[HttpActionHeader]


class HttpAction(TypedDict, total=False):
    """Send data to an HTTPS endpoint."""

    url: Url
    confirmationUrl: Optional[Url]
    headers: Optional[HeaderList]
    auth: Optional[HttpAuthorization]


class TimestreamTimestamp(TypedDict, total=False):
    """Describes how to interpret an application-defined timestamp value from
    an MQTT message payload and the precision of that value.
    """

    value: TimestreamTimestampValue
    unit: TimestreamTimestampUnit


class TimestreamDimension(TypedDict, total=False):
    """Metadata attributes of the time series that are written in each measure
    record.
    """

    name: TimestreamDimensionName
    value: TimestreamDimensionValue


TimestreamDimensionList = List[TimestreamDimension]


class TimestreamAction(TypedDict, total=False):
    """The Timestream rule action writes attributes (measures) from an MQTT
    message into an Amazon Timestream table. For more information, see the
    `Timestream <https://docs.aws.amazon.com/iot/latest/developerguide/timestream-rule-action.html>`__
    topic rule action documentation.
    """

    roleArn: AwsArn
    databaseName: TimestreamDatabaseName
    tableName: TimestreamTableName
    dimensions: TimestreamDimensionList
    timestamp: Optional[TimestreamTimestamp]


class StepFunctionsAction(TypedDict, total=False):
    """Starts execution of a Step Functions state machine."""

    executionNamePrefix: Optional[ExecutionNamePrefix]
    stateMachineName: StateMachineName
    roleArn: AwsArn


class AssetPropertyTimestamp(TypedDict, total=False):
    """An asset property timestamp entry containing the following information."""

    timeInSeconds: AssetPropertyTimeInSeconds
    offsetInNanos: Optional[AssetPropertyOffsetInNanos]


class AssetPropertyVariant(TypedDict, total=False):
    """Contains an asset property value (of a single type)."""

    stringValue: Optional[AssetPropertyStringValue]
    integerValue: Optional[AssetPropertyIntegerValue]
    doubleValue: Optional[AssetPropertyDoubleValue]
    booleanValue: Optional[AssetPropertyBooleanValue]


class AssetPropertyValue(TypedDict, total=False):
    """An asset property value entry containing the following information."""

    value: AssetPropertyVariant
    timestamp: AssetPropertyTimestamp
    quality: Optional[AssetPropertyQuality]


AssetPropertyValueList = List[AssetPropertyValue]


class PutAssetPropertyValueEntry(TypedDict, total=False):
    """An asset property value entry containing the following information."""

    entryId: Optional[AssetPropertyEntryId]
    assetId: Optional[AssetId]
    propertyId: Optional[AssetPropertyId]
    propertyAlias: Optional[AssetPropertyAlias]
    propertyValues: AssetPropertyValueList


PutAssetPropertyValueEntryList = List[PutAssetPropertyValueEntry]


class IotSiteWiseAction(TypedDict, total=False):
    """Describes an action to send data from an MQTT message that triggered the
    rule to IoT SiteWise asset properties.
    """

    putAssetPropertyValueEntries: PutAssetPropertyValueEntryList
    roleArn: AwsArn


class IotEventsAction(TypedDict, total=False):
    """Sends an input to an IoT Events detector."""

    inputName: InputName
    messageId: Optional[MessageId]
    batchMode: Optional[BatchMode]
    roleArn: AwsArn


class IotAnalyticsAction(TypedDict, total=False):
    """Sends message data to an IoT Analytics channel."""

    channelArn: Optional[AwsArn]
    channelName: Optional[ChannelName]
    batchMode: Optional[BatchMode]
    roleArn: Optional[AwsArn]


class SalesforceAction(TypedDict, total=False):
    """Describes an action to write a message to a Salesforce IoT Cloud Input
    Stream.
    """

    token: SalesforceToken
    url: SalesforceEndpoint


ElasticsearchAction = TypedDict(
    "ElasticsearchAction",
    {
        "roleArn": AwsArn,
        "endpoint": ElasticsearchEndpoint,
        "index": ElasticsearchIndex,
        "type": ElasticsearchType,
        "id": ElasticsearchId,
    },
    total=False,
)


class CloudwatchLogsAction(TypedDict, total=False):
    """Describes an action that sends data to CloudWatch Logs."""

    roleArn: AwsArn
    logGroupName: LogGroupName


class CloudwatchAlarmAction(TypedDict, total=False):
    """Describes an action that updates a CloudWatch alarm."""

    roleArn: AwsArn
    alarmName: AlarmName
    stateReason: StateReason
    stateValue: StateValue


class CloudwatchMetricAction(TypedDict, total=False):
    """Describes an action that captures a CloudWatch metric."""

    roleArn: AwsArn
    metricNamespace: String
    metricName: String
    metricValue: String
    metricUnit: String
    metricTimestamp: Optional[String]


class FirehoseAction(TypedDict, total=False):
    """Describes an action that writes data to an Amazon Kinesis Firehose
    stream.
    """

    roleArn: AwsArn
    deliveryStreamName: DeliveryStreamName
    separator: Optional[FirehoseSeparator]
    batchMode: Optional[BatchMode]


class S3Action(TypedDict, total=False):
    """Describes an action to write data to an Amazon S3 bucket."""

    roleArn: AwsArn
    bucketName: BucketName
    key: Key
    cannedAcl: Optional[CannedAccessControlList]


class RepublishAction(TypedDict, total=False):
    """Describes an action to republish to another topic."""

    roleArn: AwsArn
    topic: TopicPattern
    qos: Optional[Qos]


class KinesisAction(TypedDict, total=False):
    """Describes an action to write data to an Amazon Kinesis stream."""

    roleArn: AwsArn
    streamName: StreamName
    partitionKey: Optional[PartitionKey]


class SqsAction(TypedDict, total=False):
    """Describes an action to publish data to an Amazon SQS queue."""

    roleArn: AwsArn
    queueUrl: QueueUrl
    useBase64: Optional[UseBase64]


class SnsAction(TypedDict, total=False):
    """Describes an action to publish to an Amazon SNS topic."""

    targetArn: AwsArn
    roleArn: AwsArn
    messageFormat: Optional[MessageFormat]


class LambdaAction(TypedDict, total=False):
    """Describes an action to invoke a Lambda function."""

    functionArn: FunctionArn


class PutItemInput(TypedDict, total=False):
    """The input for the DynamoActionVS action that specifies the DynamoDB
    table to which the message data will be written.
    """

    tableName: TableName


class DynamoDBv2Action(TypedDict, total=False):
    """Describes an action to write to a DynamoDB table.

    This DynamoDB action writes each attribute in the message payload into
    it's own column in the DynamoDB table.
    """

    roleArn: AwsArn
    putItem: PutItemInput


class DynamoDBAction(TypedDict, total=False):
    """Describes an action to write to a DynamoDB table.

    The ``tableName``, ``hashKeyField``, and ``rangeKeyField`` values must
    match the values used when you created the table.

    The ``hashKeyValue`` and ``rangeKeyvalue`` fields use a substitution
    template syntax. These templates provide data at runtime. The syntax is
    as follows: ${*sql-expression*}.

    You can specify any valid expression in a WHERE or SELECT clause,
    including JSON properties, comparisons, calculations, and functions. For
    example, the following field uses the third level of the topic:

    ``"hashKeyValue": "${topic(3)}"``

    The following field uses the timestamp:

    ``"rangeKeyValue": "${timestamp()}"``
    """

    tableName: TableName
    roleArn: AwsArn
    operation: Optional[DynamoOperation]
    hashKeyField: HashKeyField
    hashKeyValue: HashKeyValue
    hashKeyType: Optional[DynamoKeyType]
    rangeKeyField: Optional[RangeKeyField]
    rangeKeyValue: Optional[RangeKeyValue]
    rangeKeyType: Optional[DynamoKeyType]
    payloadField: Optional[PayloadField]


Action = TypedDict(
    "Action",
    {
        "dynamoDB": Optional[DynamoDBAction],
        "dynamoDBv2": Optional[DynamoDBv2Action],
        "lambda": Optional[LambdaAction],
        "sns": Optional[SnsAction],
        "sqs": Optional[SqsAction],
        "kinesis": Optional[KinesisAction],
        "republish": Optional[RepublishAction],
        "s3": Optional[S3Action],
        "firehose": Optional[FirehoseAction],
        "cloudwatchMetric": Optional[CloudwatchMetricAction],
        "cloudwatchAlarm": Optional[CloudwatchAlarmAction],
        "cloudwatchLogs": Optional[CloudwatchLogsAction],
        "elasticsearch": Optional[ElasticsearchAction],
        "salesforce": Optional[SalesforceAction],
        "iotAnalytics": Optional[IotAnalyticsAction],
        "iotEvents": Optional[IotEventsAction],
        "iotSiteWise": Optional[IotSiteWiseAction],
        "stepFunctions": Optional[StepFunctionsAction],
        "timestream": Optional[TimestreamAction],
        "http": Optional[HttpAction],
        "kafka": Optional[KafkaAction],
        "openSearch": Optional[OpenSearchAction],
    },
    total=False,
)
ActionList = List[Action]
Timestamp = datetime


class ViolationEventAdditionalInfo(TypedDict, total=False):
    """The details of a violation event."""

    confidenceLevel: Optional[ConfidenceLevel]


StringList = List[stringValue]
NumberList = List[Number]
Ports = List[Port]
Cidrs = List[Cidr]
UnsignedLong = int


class MetricValue(TypedDict, total=False):
    """The value to be compared with the ``metric``."""

    count: Optional[UnsignedLong]
    cidrs: Optional[Cidrs]
    ports: Optional[Ports]
    number: Optional[Number]
    numbers: Optional[NumberList]
    strings: Optional[StringList]


class MachineLearningDetectionConfig(TypedDict, total=False):
    """The configuration of an ML Detect Security Profile."""

    confidenceLevel: ConfidenceLevel


class StatisticalThreshold(TypedDict, total=False):
    """A statistical ranking (percentile) that indicates a threshold value by
    which a behavior is determined to be in compliance or in violation of
    the behavior.
    """

    statistic: Optional[EvaluationStatistic]


class BehaviorCriteria(TypedDict, total=False):
    """The criteria by which the behavior is determined to be normal."""

    comparisonOperator: Optional[ComparisonOperator]
    value: Optional[MetricValue]
    durationSeconds: Optional[DurationSeconds]
    consecutiveDatapointsToAlarm: Optional[ConsecutiveDatapointsToAlarm]
    consecutiveDatapointsToClear: Optional[ConsecutiveDatapointsToClear]
    statisticalThreshold: Optional[StatisticalThreshold]
    mlDetectionConfig: Optional[MachineLearningDetectionConfig]


class MetricDimension(TypedDict, total=False):
    """The dimension of a metric."""

    dimensionName: DimensionName
    operator: Optional[DimensionValueOperator]


class Behavior(TypedDict, total=False):
    """A Device Defender security profile behavior."""

    name: BehaviorName
    metric: Optional[BehaviorMetric]
    metricDimension: Optional[MetricDimension]
    criteria: Optional[BehaviorCriteria]
    suppressAlerts: Optional[SuppressAlerts]


class ActiveViolation(TypedDict, total=False):
    """Information about an active Device Defender security profile behavior
    violation.
    """

    violationId: Optional[ViolationId]
    thingName: Optional[DeviceDefenderThingName]
    securityProfileName: Optional[SecurityProfileName]
    behavior: Optional[Behavior]
    lastViolationValue: Optional[MetricValue]
    violationEventAdditionalInfo: Optional[ViolationEventAdditionalInfo]
    verificationState: Optional[VerificationState]
    verificationStateDescription: Optional[VerificationStateDescription]
    lastViolationTime: Optional[Timestamp]
    violationStartTime: Optional[Timestamp]


ActiveViolations = List[ActiveViolation]


class AddThingToBillingGroupRequest(ServiceRequest):
    billingGroupName: Optional[BillingGroupName]
    billingGroupArn: Optional[BillingGroupArn]
    thingName: Optional[ThingName]
    thingArn: Optional[ThingArn]


class AddThingToBillingGroupResponse(TypedDict, total=False):
    pass


class AddThingToThingGroupRequest(ServiceRequest):
    thingGroupName: Optional[ThingGroupName]
    thingGroupArn: Optional[ThingGroupArn]
    thingName: Optional[ThingName]
    thingArn: Optional[ThingArn]
    overrideDynamicGroups: Optional[OverrideDynamicGroups]


class AddThingToThingGroupResponse(TypedDict, total=False):
    pass


ThingGroupNames = List[ThingGroupName]


class AddThingsToThingGroupParams(TypedDict, total=False):
    """Parameters used when defining a mitigation action that move a set of
    things to a thing group.
    """

    thingGroupNames: ThingGroupNames
    overrideDynamicGroups: Optional[NullableBoolean]


AdditionalMetricsToRetainList = List[BehaviorMetric]


class MetricToRetain(TypedDict, total=False):
    """The metric you want to retain. Dimensions are optional."""

    metric: BehaviorMetric
    metricDimension: Optional[MetricDimension]


AdditionalMetricsToRetainV2List = List[MetricToRetain]
AdditionalParameterMap = Dict[AttributeKey, Value]
AggregationTypeValues = List[AggregationTypeValue]


class AggregationType(TypedDict, total=False):
    """The type of aggregation queries."""

    name: AggregationTypeName
    values: Optional[AggregationTypeValues]


class AlertTarget(TypedDict, total=False):
    """A structure containing the alert target ARN and the role ARN."""

    alertTargetArn: AlertTargetArn
    roleArn: RoleArn


AlertTargets = Dict[AlertTargetType, AlertTarget]


class Policy(TypedDict, total=False):
    """Describes an IoT policy."""

    policyName: Optional[PolicyName]
    policyArn: Optional[PolicyArn]


Policies = List[Policy]


class Allowed(TypedDict, total=False):
    """Contains information that allowed the authorization."""

    policies: Optional[Policies]


ApproximateSecondsBeforeTimedOut = int
JobTargets = List[TargetArn]


class AssociateTargetsWithJobRequest(ServiceRequest):
    targets: JobTargets
    jobId: JobId
    comment: Optional[Comment]
    namespaceId: Optional[NamespaceId]


class AssociateTargetsWithJobResponse(TypedDict, total=False):
    jobArn: Optional[JobArn]
    jobId: Optional[JobId]
    description: Optional[JobDescription]


class AttachPolicyRequest(ServiceRequest):
    policyName: PolicyName
    target: PolicyTarget


class AttachPrincipalPolicyRequest(ServiceRequest):
    """The input for the AttachPrincipalPolicy operation."""

    policyName: PolicyName
    principal: Principal


class AttachSecurityProfileRequest(ServiceRequest):
    securityProfileName: SecurityProfileName
    securityProfileTargetArn: SecurityProfileTargetArn


class AttachSecurityProfileResponse(TypedDict, total=False):
    pass


class AttachThingPrincipalRequest(ServiceRequest):
    """The input for the AttachThingPrincipal operation."""

    thingName: ThingName
    principal: Principal


class AttachThingPrincipalResponse(TypedDict, total=False):
    """The output from the AttachThingPrincipal operation."""


Attributes = Dict[AttributeName, AttributeValue]


class AttributePayload(TypedDict, total=False):
    """The attribute payload."""

    attributes: Optional[Attributes]
    merge: Optional[Flag]


AttributesMap = Dict[AttributeKey, Value]


class AuditCheckConfiguration(TypedDict, total=False):
    """Which audit checks are enabled and disabled for this account."""

    enabled: Optional[Enabled]


AuditCheckConfigurations = Dict[AuditCheckName, AuditCheckConfiguration]
SuppressedNonCompliantResourcesCount = int
NonCompliantResourcesCount = int
TotalResourcesCount = int


class AuditCheckDetails(TypedDict, total=False):
    """Information about the audit check."""

    checkRunStatus: Optional[AuditCheckRunStatus]
    checkCompliant: Optional[CheckCompliant]
    totalResourcesCount: Optional[TotalResourcesCount]
    nonCompliantResourcesCount: Optional[NonCompliantResourcesCount]
    suppressedNonCompliantResourcesCount: Optional[SuppressedNonCompliantResourcesCount]
    errorCode: Optional[ErrorCode]
    message: Optional[ErrorMessage]


MitigationActionNameList = List[MitigationActionName]
AuditCheckToActionsMapping = Dict[AuditCheckName, MitigationActionNameList]
ReasonForNonComplianceCodes = List[ReasonForNonComplianceCode]
AuditCheckToReasonCodeFilter = Dict[AuditCheckName, ReasonForNonComplianceCodes]
AuditDetails = Dict[AuditCheckName, AuditCheckDetails]
StringMap = Dict[String, String]


class PolicyVersionIdentifier(TypedDict, total=False):
    """Information about the version of the policy associated with the
    resource.
    """

    policyName: Optional[PolicyName]
    policyVersionId: Optional[PolicyVersionId]


class ResourceIdentifier(TypedDict, total=False):
    """Information that identifies the noncompliant resource."""

    deviceCertificateId: Optional[CertificateId]
    caCertificateId: Optional[CertificateId]
    cognitoIdentityPoolId: Optional[CognitoIdentityPoolId]
    clientId: Optional[ClientId]
    policyVersionIdentifier: Optional[PolicyVersionIdentifier]
    account: Optional[AwsAccountId]
    iamRoleArn: Optional[RoleArn]
    roleAliasArn: Optional[RoleAliasArn]


class RelatedResource(TypedDict, total=False):
    """Information about a related resource."""

    resourceType: Optional[ResourceType]
    resourceIdentifier: Optional[ResourceIdentifier]
    additionalInfo: Optional[StringMap]


RelatedResources = List[RelatedResource]


class NonCompliantResource(TypedDict, total=False):
    """Information about the resource that was noncompliant with the audit
    check.
    """

    resourceType: Optional[ResourceType]
    resourceIdentifier: Optional[ResourceIdentifier]
    additionalInfo: Optional[StringMap]


class AuditFinding(TypedDict, total=False):
    """The findings (results) of the audit."""

    findingId: Optional[FindingId]
    taskId: Optional[AuditTaskId]
    checkName: Optional[AuditCheckName]
    taskStartTime: Optional[Timestamp]
    findingTime: Optional[Timestamp]
    severity: Optional[AuditFindingSeverity]
    nonCompliantResource: Optional[NonCompliantResource]
    relatedResources: Optional[RelatedResources]
    reasonForNonCompliance: Optional[ReasonForNonCompliance]
    reasonForNonComplianceCode: Optional[ReasonForNonComplianceCode]
    isSuppressed: Optional[IsSuppressed]


AuditFindings = List[AuditFinding]


class AuditMitigationActionExecutionMetadata(TypedDict, total=False):
    """Returned by ListAuditMitigationActionsTask, this object contains
    information that describes a mitigation action that has been started.
    """

    taskId: Optional[MitigationActionsTaskId]
    findingId: Optional[FindingId]
    actionName: Optional[MitigationActionName]
    actionId: Optional[MitigationActionId]
    status: Optional[AuditMitigationActionsExecutionStatus]
    startTime: Optional[Timestamp]
    endTime: Optional[Timestamp]
    errorCode: Optional[ErrorCode]
    message: Optional[ErrorMessage]


AuditMitigationActionExecutionMetadataList = List[AuditMitigationActionExecutionMetadata]


class AuditMitigationActionsTaskMetadata(TypedDict, total=False):
    """Information about an audit mitigation actions task that is returned by
    ``ListAuditMitigationActionsTasks``.
    """

    taskId: Optional[MitigationActionsTaskId]
    startTime: Optional[Timestamp]
    taskStatus: Optional[AuditMitigationActionsTaskStatus]


AuditMitigationActionsTaskMetadataList = List[AuditMitigationActionsTaskMetadata]
CanceledFindingsCount = int
SkippedFindingsCount = int
SucceededFindingsCount = int
FailedFindingsCount = int
TotalFindingsCount = int


class TaskStatisticsForAuditCheck(TypedDict, total=False):
    """Provides summary counts of how many tasks for findings are in a
    particular state. This information is included in the response from
    DescribeAuditMitigationActionsTask.
    """

    totalFindingsCount: Optional[TotalFindingsCount]
    failedFindingsCount: Optional[FailedFindingsCount]
    succeededFindingsCount: Optional[SucceededFindingsCount]
    skippedFindingsCount: Optional[SkippedFindingsCount]
    canceledFindingsCount: Optional[CanceledFindingsCount]


AuditMitigationActionsTaskStatistics = Dict[AuditCheckName, TaskStatisticsForAuditCheck]
FindingIds = List[FindingId]


class AuditMitigationActionsTaskTarget(TypedDict, total=False):
    """Used in MitigationActionParams, this information identifies the target
    findings to which the mitigation actions are applied. Only one entry
    appears.
    """

    auditTaskId: Optional[AuditTaskId]
    findingIds: Optional[FindingIds]
    auditCheckToReasonCodeFilter: Optional[AuditCheckToReasonCodeFilter]


class AuditNotificationTarget(TypedDict, total=False):
    """Information about the targets to which audit notifications are sent."""

    targetArn: Optional[TargetArn]
    roleArn: Optional[RoleArn]
    enabled: Optional[Enabled]


AuditNotificationTargetConfigurations = Dict[AuditNotificationType, AuditNotificationTarget]


class AuditSuppression(TypedDict, total=False):
    """Filters out specific findings of a Device Defender audit."""

    checkName: AuditCheckName
    resourceIdentifier: ResourceIdentifier
    expirationDate: Optional[Timestamp]
    suppressIndefinitely: Optional[SuppressIndefinitely]
    description: Optional[AuditDescription]


AuditSuppressionList = List[AuditSuppression]


class AuditTaskMetadata(TypedDict, total=False):
    """The audits that were performed."""

    taskId: Optional[AuditTaskId]
    taskStatus: Optional[AuditTaskStatus]
    taskType: Optional[AuditTaskType]


AuditTaskMetadataList = List[AuditTaskMetadata]
Resources = List[Resource]


class AuthInfo(TypedDict, total=False):
    """A collection of authorization information."""

    actionType: Optional[ActionType]
    resources: Resources


AuthInfos = List[AuthInfo]
MissingContextValues = List[MissingContextValue]


class ExplicitDeny(TypedDict, total=False):
    """Information that explicitly denies authorization."""

    policies: Optional[Policies]


class ImplicitDeny(TypedDict, total=False):
    """Information that implicitly denies authorization. When policy doesn't
    explicitly deny or allow an action on a resource it is considered an
    implicit deny.
    """

    policies: Optional[Policies]


class Denied(TypedDict, total=False):
    """Contains information that denied the authorization."""

    implicitDeny: Optional[ImplicitDeny]
    explicitDeny: Optional[ExplicitDeny]


class AuthResult(TypedDict, total=False):
    """The authorizer result."""

    authInfo: Optional[AuthInfo]
    allowed: Optional[Allowed]
    denied: Optional[Denied]
    authDecision: Optional[AuthDecision]
    missingContextValues: Optional[MissingContextValues]


AuthResults = List[AuthResult]


class AuthorizerConfig(TypedDict, total=False):
    """An object that specifies the authorization service for a domain."""

    defaultAuthorizerName: Optional[AuthorizerName]
    allowAuthorizerOverride: Optional[AllowAuthorizerOverride]


DateType = datetime
PublicKeyMap = Dict[KeyName, KeyValue]


class AuthorizerDescription(TypedDict, total=False):
    """The authorizer description."""

    authorizerName: Optional[AuthorizerName]
    authorizerArn: Optional[AuthorizerArn]
    authorizerFunctionArn: Optional[AuthorizerFunctionArn]
    tokenKeyName: Optional[TokenKeyName]
    tokenSigningPublicKeys: Optional[PublicKeyMap]
    status: Optional[AuthorizerStatus]
    creationDate: Optional[DateType]
    lastModifiedDate: Optional[DateType]
    signingDisabled: Optional[BooleanKey]
    enableCachingForHttp: Optional[EnableCachingForHttp]


class AuthorizerSummary(TypedDict, total=False):
    """The authorizer summary."""

    authorizerName: Optional[AuthorizerName]
    authorizerArn: Optional[AuthorizerArn]


Authorizers = List[AuthorizerSummary]


class AwsJobAbortCriteria(TypedDict, total=False):
    """The criteria that determine when and how a job abort takes place."""

    failureType: AwsJobAbortCriteriaFailureType
    action: AwsJobAbortCriteriaAbortAction
    thresholdPercentage: AwsJobAbortCriteriaAbortThresholdPercentage
    minNumberOfExecutedThings: AwsJobAbortCriteriaMinimumNumberOfExecutedThings


AwsJobAbortCriteriaList = List[AwsJobAbortCriteria]


class AwsJobAbortConfig(TypedDict, total=False):
    """The criteria that determine when and how a job abort takes place."""

    abortCriteriaList: AwsJobAbortCriteriaList


class AwsJobRateIncreaseCriteria(TypedDict, total=False):
    """The criteria to initiate the increase in rate of rollout for a job."""

    numberOfNotifiedThings: Optional[AwsJobRateIncreaseCriteriaNumberOfThings]
    numberOfSucceededThings: Optional[AwsJobRateIncreaseCriteriaNumberOfThings]


class AwsJobExponentialRolloutRate(TypedDict, total=False):
    """The rate of increase for a job rollout. This parameter allows you to
    define an exponential rate increase for a job rollout.
    """

    baseRatePerMinute: AwsJobRolloutRatePerMinute
    incrementFactor: AwsJobRolloutIncrementFactor
    rateIncreaseCriteria: AwsJobRateIncreaseCriteria


class AwsJobExecutionsRolloutConfig(TypedDict, total=False):
    """Configuration for the rollout of OTA updates."""

    maximumPerMinute: Optional[MaximumPerMinute]
    exponentialRate: Optional[AwsJobExponentialRolloutRate]


ExpiresInSeconds = int


class AwsJobPresignedUrlConfig(TypedDict, total=False):
    """Configuration information for pre-signed URLs. Valid when ``protocols``
    contains HTTP.
    """

    expiresInSec: Optional[ExpiresInSeconds]


AwsJobTimeoutInProgressTimeoutInMinutes = int


class AwsJobTimeoutConfig(TypedDict, total=False):
    """Specifies the amount of time each device has to finish its execution of
    the job. A timer is started when the job execution status is set to
    ``IN_PROGRESS``. If the job execution status is not set to another
    terminal state before the timer expires, it will be automatically set to
    ``TIMED_OUT``.
    """

    inProgressTimeoutInMinutes: Optional[AwsJobTimeoutInProgressTimeoutInMinutes]


class BehaviorModelTrainingSummary(TypedDict, total=False):
    """The summary of an ML Detect behavior model."""

    securityProfileName: Optional[SecurityProfileName]
    behaviorName: Optional[BehaviorName]
    trainingDataCollectionStartDate: Optional[Timestamp]
    modelStatus: Optional[ModelStatus]
    datapointsCollectionPercentage: Optional[DataCollectionPercentage]
    lastModelRefreshDate: Optional[Timestamp]


BehaviorModelTrainingSummaries = List[BehaviorModelTrainingSummary]
Behaviors = List[Behavior]
CreationDate = datetime


class BillingGroupMetadata(TypedDict, total=False):
    """Additional information about the billing group."""

    creationDate: Optional[CreationDate]


class GroupNameAndArn(TypedDict, total=False):
    """The name and ARN of a group."""

    groupName: Optional[ThingGroupName]
    groupArn: Optional[ThingGroupArn]


BillingGroupNameAndArnList = List[GroupNameAndArn]


class BillingGroupProperties(TypedDict, total=False):
    """The properties of a billing group."""

    billingGroupDescription: Optional[BillingGroupDescription]


class Bucket(TypedDict, total=False):
    """A count of documents that meets a specific aggregation criteria."""

    keyValue: Optional[BucketKeyValue]
    count: Optional[Count]


Buckets = List[Bucket]


class TermsAggregation(TypedDict, total=False):
    """Performs an aggregation that will return a list of buckets. The list of
    buckets is a ranked list of the number of occurrences of an aggregation
    field value.
    """

    maxBuckets: Optional[MaxBuckets]


class BucketsAggregationType(TypedDict, total=False):
    """The type of bucketed aggregation performed."""

    termsAggregation: Optional[TermsAggregation]


class CACertificate(TypedDict, total=False):
    """A CA certificate."""

    certificateArn: Optional[CertificateArn]
    certificateId: Optional[CertificateId]
    status: Optional[CACertificateStatus]
    creationDate: Optional[DateType]


class CertificateValidity(TypedDict, total=False):
    """When the certificate is valid."""

    notBefore: Optional[DateType]
    notAfter: Optional[DateType]


class CACertificateDescription(TypedDict, total=False):
    """Describes a CA certificate."""

    certificateArn: Optional[CertificateArn]
    certificateId: Optional[CertificateId]
    status: Optional[CACertificateStatus]
    certificatePem: Optional[CertificatePem]
    ownedBy: Optional[AwsAccountId]
    creationDate: Optional[DateType]
    autoRegistrationStatus: Optional[AutoRegistrationStatus]
    lastModifiedDate: Optional[DateType]
    customerVersion: Optional[CustomerVersion]
    generationId: Optional[GenerationId]
    validity: Optional[CertificateValidity]


CACertificates = List[CACertificate]


class CancelAuditMitigationActionsTaskRequest(ServiceRequest):
    taskId: MitigationActionsTaskId


class CancelAuditMitigationActionsTaskResponse(TypedDict, total=False):
    pass


class CancelAuditTaskRequest(ServiceRequest):
    taskId: AuditTaskId


class CancelAuditTaskResponse(TypedDict, total=False):
    pass


class CancelCertificateTransferRequest(ServiceRequest):
    """The input for the CancelCertificateTransfer operation."""

    certificateId: CertificateId


class CancelDetectMitigationActionsTaskRequest(ServiceRequest):
    taskId: MitigationActionsTaskId


class CancelDetectMitigationActionsTaskResponse(TypedDict, total=False):
    pass


DetailsMap = Dict[DetailsKey, DetailsValue]
ExpectedVersion = int


class CancelJobExecutionRequest(ServiceRequest):
    jobId: JobId
    thingName: ThingName
    force: Optional[ForceFlag]
    expectedVersion: Optional[ExpectedVersion]
    statusDetails: Optional[DetailsMap]


class CancelJobRequest(ServiceRequest):
    jobId: JobId
    reasonCode: Optional[ReasonCode]
    comment: Optional[Comment]
    force: Optional[ForceFlag]


class CancelJobResponse(TypedDict, total=False):
    jobArn: Optional[JobArn]
    jobId: Optional[JobId]
    description: Optional[JobDescription]


class Certificate(TypedDict, total=False):
    """Information about a certificate."""

    certificateArn: Optional[CertificateArn]
    certificateId: Optional[CertificateId]
    status: Optional[CertificateStatus]
    certificateMode: Optional[CertificateMode]
    creationDate: Optional[DateType]


class TransferData(TypedDict, total=False):
    """Data used to transfer a certificate to an Amazon Web Services account."""

    transferMessage: Optional[Message]
    rejectReason: Optional[Message]
    transferDate: Optional[DateType]
    acceptDate: Optional[DateType]
    rejectDate: Optional[DateType]


class CertificateDescription(TypedDict, total=False):
    """Describes a certificate."""

    certificateArn: Optional[CertificateArn]
    certificateId: Optional[CertificateId]
    caCertificateId: Optional[CertificateId]
    status: Optional[CertificateStatus]
    certificatePem: Optional[CertificatePem]
    ownedBy: Optional[AwsAccountId]
    previousOwnedBy: Optional[AwsAccountId]
    creationDate: Optional[DateType]
    lastModifiedDate: Optional[DateType]
    customerVersion: Optional[CustomerVersion]
    transferData: Optional[TransferData]
    generationId: Optional[GenerationId]
    validity: Optional[CertificateValidity]
    certificateMode: Optional[CertificateMode]


Certificates = List[Certificate]


class ClearDefaultAuthorizerRequest(ServiceRequest):
    pass


class ClearDefaultAuthorizerResponse(TypedDict, total=False):
    pass


class CodeSigningCertificateChain(TypedDict, total=False):
    """Describes the certificate chain being used when code signing a file."""

    certificateName: Optional[CertificateName]
    inlineDocument: Optional[InlineDocument]


Signature = bytes


class CodeSigningSignature(TypedDict, total=False):
    """Describes the signature for a file."""

    inlineDocument: Optional[Signature]


class CustomCodeSigning(TypedDict, total=False):
    """Describes a custom method used to code sign a file."""

    signature: Optional[CodeSigningSignature]
    certificateChain: Optional[CodeSigningCertificateChain]
    hashAlgorithm: Optional[HashAlgorithm]
    signatureAlgorithm: Optional[SignatureAlgorithm]


class S3Destination(TypedDict, total=False):
    """Describes the location of updated firmware in S3."""

    bucket: Optional[S3Bucket]
    prefix: Optional[Prefix]


class Destination(TypedDict, total=False):
    """Describes the location of the updated firmware."""

    s3Destination: Optional[S3Destination]


class SigningProfileParameter(TypedDict, total=False):
    """Describes the code-signing profile."""

    certificateArn: Optional[CertificateArn]
    platform: Optional[Platform]
    certificatePathOnDevice: Optional[CertificatePathOnDevice]


class StartSigningJobParameter(TypedDict, total=False):
    """Information required to start a signing job."""

    signingProfileParameter: Optional[SigningProfileParameter]
    signingProfileName: Optional[SigningProfileName]
    destination: Optional[Destination]


class CodeSigning(TypedDict, total=False):
    """Describes the method to use when code signing a file."""

    awsSignerJobId: Optional[SigningJobId]
    startSigningJobParameter: Optional[StartSigningJobParameter]
    customCodeSigning: Optional[CustomCodeSigning]


class Configuration(TypedDict, total=False):
    """Configuration."""

    Enabled: Optional[Enabled]


class ConfirmTopicRuleDestinationRequest(ServiceRequest):
    confirmationToken: ConfirmationToken


class ConfirmTopicRuleDestinationResponse(TypedDict, total=False):
    pass


ConnectivityTimestamp = int


class CreateAuditSuppressionRequest(ServiceRequest):
    checkName: AuditCheckName
    resourceIdentifier: ResourceIdentifier
    expirationDate: Optional[Timestamp]
    suppressIndefinitely: Optional[SuppressIndefinitely]
    description: Optional[AuditDescription]
    clientRequestToken: ClientRequestToken


class CreateAuditSuppressionResponse(TypedDict, total=False):
    pass


class Tag(TypedDict, total=False):
    """A set of key/value pairs that are used to manage the resource."""

    Key: TagKey
    Value: Optional[TagValue]


TagList = List[Tag]


class CreateAuthorizerRequest(ServiceRequest):
    authorizerName: AuthorizerName
    authorizerFunctionArn: AuthorizerFunctionArn
    tokenKeyName: Optional[TokenKeyName]
    tokenSigningPublicKeys: Optional[PublicKeyMap]
    status: Optional[AuthorizerStatus]
    tags: Optional[TagList]
    signingDisabled: Optional[BooleanKey]
    enableCachingForHttp: Optional[EnableCachingForHttp]


class CreateAuthorizerResponse(TypedDict, total=False):
    authorizerName: Optional[AuthorizerName]
    authorizerArn: Optional[AuthorizerArn]


class CreateBillingGroupRequest(ServiceRequest):
    billingGroupName: BillingGroupName
    billingGroupProperties: Optional[BillingGroupProperties]
    tags: Optional[TagList]


class CreateBillingGroupResponse(TypedDict, total=False):
    billingGroupName: Optional[BillingGroupName]
    billingGroupArn: Optional[BillingGroupArn]
    billingGroupId: Optional[BillingGroupId]


class CreateCertificateFromCsrRequest(ServiceRequest):
    """The input for the CreateCertificateFromCsr operation."""

    certificateSigningRequest: CertificateSigningRequest
    setAsActive: Optional[SetAsActive]


class CreateCertificateFromCsrResponse(TypedDict, total=False):
    """The output from the CreateCertificateFromCsr operation."""

    certificateArn: Optional[CertificateArn]
    certificateId: Optional[CertificateId]
    certificatePem: Optional[CertificatePem]


class CreateCustomMetricRequest(ServiceRequest):
    metricName: MetricName
    displayName: Optional[CustomMetricDisplayName]
    metricType: CustomMetricType
    tags: Optional[TagList]
    clientRequestToken: ClientRequestToken


class CreateCustomMetricResponse(TypedDict, total=False):
    metricName: Optional[MetricName]
    metricArn: Optional[CustomMetricArn]


DimensionStringValues = List[DimensionStringValue]
CreateDimensionRequest = TypedDict(
    "CreateDimensionRequest",
    {
        "name": DimensionName,
        "type": DimensionType,
        "stringValues": DimensionStringValues,
        "tags": Optional[TagList],
        "clientRequestToken": ClientRequestToken,
    },
    total=False,
)


class CreateDimensionResponse(TypedDict, total=False):
    name: Optional[DimensionName]
    arn: Optional[DimensionArn]


ServerCertificateArns = List[AcmCertificateArn]


class CreateDomainConfigurationRequest(ServiceRequest):
    domainConfigurationName: DomainConfigurationName
    domainName: Optional[DomainName]
    serverCertificateArns: Optional[ServerCertificateArns]
    validationCertificateArn: Optional[AcmCertificateArn]
    authorizerConfig: Optional[AuthorizerConfig]
    serviceType: Optional[ServiceType]
    tags: Optional[TagList]


class CreateDomainConfigurationResponse(TypedDict, total=False):
    domainConfigurationName: Optional[DomainConfigurationName]
    domainConfigurationArn: Optional[DomainConfigurationArn]


class ThingGroupProperties(TypedDict, total=False):
    """Thing group properties."""

    thingGroupDescription: Optional[ThingGroupDescription]
    attributePayload: Optional[AttributePayload]


class CreateDynamicThingGroupRequest(ServiceRequest):
    thingGroupName: ThingGroupName
    thingGroupProperties: Optional[ThingGroupProperties]
    indexName: Optional[IndexName]
    queryString: QueryString
    queryVersion: Optional[QueryVersion]
    tags: Optional[TagList]


class CreateDynamicThingGroupResponse(TypedDict, total=False):
    thingGroupName: Optional[ThingGroupName]
    thingGroupArn: Optional[ThingGroupArn]
    thingGroupId: Optional[ThingGroupId]
    indexName: Optional[IndexName]
    queryString: Optional[QueryString]
    queryVersion: Optional[QueryVersion]


class CreateFleetMetricRequest(ServiceRequest):
    metricName: FleetMetricName
    queryString: QueryString
    aggregationType: AggregationType
    period: FleetMetricPeriod
    aggregationField: AggregationField
    description: Optional[FleetMetricDescription]
    queryVersion: Optional[QueryVersion]
    indexName: Optional[IndexName]
    unit: Optional[FleetMetricUnit]
    tags: Optional[TagList]


class CreateFleetMetricResponse(TypedDict, total=False):
    metricName: Optional[FleetMetricName]
    metricArn: Optional[FleetMetricArn]


ParameterMap = Dict[ParameterKey, ParameterValue]


class RetryCriteria(TypedDict, total=False):
    """The criteria that determines how many retries are allowed for each
    failure type for a job.
    """

    failureType: RetryableFailureType
    numberOfRetries: NumberOfRetries


RetryCriteriaList = List[RetryCriteria]


class JobExecutionsRetryConfig(TypedDict, total=False):
    """The configuration that determines how many retries are allowed for each
    failure type for a job.
    """

    criteriaList: RetryCriteriaList


InProgressTimeoutInMinutes = int


class TimeoutConfig(TypedDict, total=False):
    """Specifies the amount of time each device has to finish its execution of
    the job. A timer is started when the job execution status is set to
    ``IN_PROGRESS``. If the job execution status is not set to another
    terminal state before the timer expires, it will be automatically set to
    ``TIMED_OUT``.
    """

    inProgressTimeoutInMinutes: Optional[InProgressTimeoutInMinutes]


class RateIncreaseCriteria(TypedDict, total=False):
    """Allows you to define a criteria to initiate the increase in rate of
    rollout for a job.
    """

    numberOfNotifiedThings: Optional[NumberOfThings]
    numberOfSucceededThings: Optional[NumberOfThings]


class ExponentialRolloutRate(TypedDict, total=False):
    """Allows you to create an exponential rate of rollout for a job."""

    baseRatePerMinute: RolloutRatePerMinute
    incrementFactor: IncrementFactor
    rateIncreaseCriteria: RateIncreaseCriteria


class JobExecutionsRolloutConfig(TypedDict, total=False):
    """Allows you to create a staged rollout of a job."""

    maximumPerMinute: Optional[MaxJobExecutionsPerMin]
    exponentialRate: Optional[ExponentialRolloutRate]


ExpiresInSec = int


class PresignedUrlConfig(TypedDict, total=False):
    """Configuration for pre-signed S3 URLs."""

    roleArn: Optional[RoleArn]
    expiresInSec: Optional[ExpiresInSec]


class CreateJobRequest(ServiceRequest):
    jobId: JobId
    targets: JobTargets
    documentSource: Optional[JobDocumentSource]
    document: Optional[JobDocument]
    description: Optional[JobDescription]
    presignedUrlConfig: Optional[PresignedUrlConfig]
    targetSelection: Optional[TargetSelection]
    jobExecutionsRolloutConfig: Optional[JobExecutionsRolloutConfig]
    abortConfig: Optional[AbortConfig]
    timeoutConfig: Optional[TimeoutConfig]
    tags: Optional[TagList]
    namespaceId: Optional[NamespaceId]
    jobTemplateArn: Optional[JobTemplateArn]
    jobExecutionsRetryConfig: Optional[JobExecutionsRetryConfig]
    documentParameters: Optional[ParameterMap]


class CreateJobResponse(TypedDict, total=False):
    jobArn: Optional[JobArn]
    jobId: Optional[JobId]
    description: Optional[JobDescription]


class CreateJobTemplateRequest(ServiceRequest):
    jobTemplateId: JobTemplateId
    jobArn: Optional[JobArn]
    documentSource: Optional[JobDocumentSource]
    document: Optional[JobDocument]
    description: JobDescription
    presignedUrlConfig: Optional[PresignedUrlConfig]
    jobExecutionsRolloutConfig: Optional[JobExecutionsRolloutConfig]
    abortConfig: Optional[AbortConfig]
    timeoutConfig: Optional[TimeoutConfig]
    tags: Optional[TagList]
    jobExecutionsRetryConfig: Optional[JobExecutionsRetryConfig]


class CreateJobTemplateResponse(TypedDict, total=False):
    jobTemplateArn: Optional[JobTemplateArn]
    jobTemplateId: Optional[JobTemplateId]


class CreateKeysAndCertificateRequest(ServiceRequest):
    """The input for the CreateKeysAndCertificate operation.

    Requires permission to access the
    `CreateKeysAndCertificateRequest <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
    action.
    """

    setAsActive: Optional[SetAsActive]


class KeyPair(TypedDict, total=False):
    """Describes a key pair."""

    PublicKey: Optional[PublicKey]
    PrivateKey: Optional[PrivateKey]


class CreateKeysAndCertificateResponse(TypedDict, total=False):
    """The output of the CreateKeysAndCertificate operation."""

    certificateArn: Optional[CertificateArn]
    certificateId: Optional[CertificateId]
    certificatePem: Optional[CertificatePem]
    keyPair: Optional[KeyPair]


class PublishFindingToSnsParams(TypedDict, total=False):
    """Parameters to define a mitigation action that publishes findings to
    Amazon SNS. You can implement your own custom actions in response to the
    Amazon SNS messages.
    """

    topicArn: SnsTopicArn


class EnableIoTLoggingParams(TypedDict, total=False):
    """Parameters used when defining a mitigation action that enable Amazon Web
    Services IoT Core logging.
    """

    roleArnForLogging: RoleArn
    logLevel: LogLevel


class ReplaceDefaultPolicyVersionParams(TypedDict, total=False):
    """Parameters to define a mitigation action that adds a blank policy to
    restrict permissions.
    """

    templateName: PolicyTemplateName


class UpdateCACertificateParams(TypedDict, total=False):
    """Parameters to define a mitigation action that changes the state of the
    CA certificate to inactive.
    """

    action: CACertificateUpdateAction


class UpdateDeviceCertificateParams(TypedDict, total=False):
    """Parameters to define a mitigation action that changes the state of the
    device certificate to inactive.
    """

    action: DeviceCertificateUpdateAction


class MitigationActionParams(TypedDict, total=False):
    """The set of parameters for this mitigation action. You can specify only
    one type of parameter (in other words, you can apply only one action for
    each defined mitigation action).
    """

    updateDeviceCertificateParams: Optional[UpdateDeviceCertificateParams]
    updateCACertificateParams: Optional[UpdateCACertificateParams]
    addThingsToThingGroupParams: Optional[AddThingsToThingGroupParams]
    replaceDefaultPolicyVersionParams: Optional[ReplaceDefaultPolicyVersionParams]
    enableIoTLoggingParams: Optional[EnableIoTLoggingParams]
    publishFindingToSnsParams: Optional[PublishFindingToSnsParams]


class CreateMitigationActionRequest(ServiceRequest):
    actionName: MitigationActionName
    roleArn: RoleArn
    actionParams: MitigationActionParams
    tags: Optional[TagList]


class CreateMitigationActionResponse(TypedDict, total=False):
    actionArn: Optional[MitigationActionArn]
    actionId: Optional[MitigationActionId]


class S3Location(TypedDict, total=False):
    """The S3 location."""

    bucket: Optional[S3Bucket]
    key: Optional[S3Key]
    version: Optional[S3Version]


class Stream(TypedDict, total=False):
    """Describes a group of files that can be streamed."""

    streamId: Optional[StreamId]
    fileId: Optional[FileId]


class FileLocation(TypedDict, total=False):
    """The location of the OTA update."""

    stream: Optional[Stream]
    s3Location: Optional[S3Location]


class OTAUpdateFile(TypedDict, total=False):
    """Describes a file to be associated with an OTA update."""

    fileName: Optional[FileName]
    fileType: Optional[FileType]
    fileVersion: Optional[OTAUpdateFileVersion]
    fileLocation: Optional[FileLocation]
    codeSigning: Optional[CodeSigning]
    attributes: Optional[AttributesMap]


OTAUpdateFiles = List[OTAUpdateFile]
Protocols = List[Protocol]
Targets = List[Target]


class CreateOTAUpdateRequest(ServiceRequest):
    otaUpdateId: OTAUpdateId
    description: Optional[OTAUpdateDescription]
    targets: Targets
    protocols: Optional[Protocols]
    targetSelection: Optional[TargetSelection]
    awsJobExecutionsRolloutConfig: Optional[AwsJobExecutionsRolloutConfig]
    awsJobPresignedUrlConfig: Optional[AwsJobPresignedUrlConfig]
    awsJobAbortConfig: Optional[AwsJobAbortConfig]
    awsJobTimeoutConfig: Optional[AwsJobTimeoutConfig]
    files: OTAUpdateFiles
    roleArn: RoleArn
    additionalParameters: Optional[AdditionalParameterMap]
    tags: Optional[TagList]


class CreateOTAUpdateResponse(TypedDict, total=False):
    otaUpdateId: Optional[OTAUpdateId]
    awsIotJobId: Optional[AwsIotJobId]
    otaUpdateArn: Optional[OTAUpdateArn]
    awsIotJobArn: Optional[AwsIotJobArn]
    otaUpdateStatus: Optional[OTAUpdateStatus]


class CreatePolicyRequest(ServiceRequest):
    """The input for the CreatePolicy operation."""

    policyName: PolicyName
    policyDocument: PolicyDocument
    tags: Optional[TagList]


class CreatePolicyResponse(TypedDict, total=False):
    """The output from the CreatePolicy operation."""

    policyName: Optional[PolicyName]
    policyArn: Optional[PolicyArn]
    policyDocument: Optional[PolicyDocument]
    policyVersionId: Optional[PolicyVersionId]


class CreatePolicyVersionRequest(ServiceRequest):
    """The input for the CreatePolicyVersion operation."""

    policyName: PolicyName
    policyDocument: PolicyDocument
    setAsDefault: Optional[SetAsDefault]


class CreatePolicyVersionResponse(TypedDict, total=False):
    """The output of the CreatePolicyVersion operation."""

    policyArn: Optional[PolicyArn]
    policyDocument: Optional[PolicyDocument]
    policyVersionId: Optional[PolicyVersionId]
    isDefaultVersion: Optional[IsDefaultVersion]


class CreateProvisioningClaimRequest(ServiceRequest):
    templateName: TemplateName


class CreateProvisioningClaimResponse(TypedDict, total=False):
    certificateId: Optional[CertificateId]
    certificatePem: Optional[CertificatePem]
    keyPair: Optional[KeyPair]
    expiration: Optional[DateType]


class ProvisioningHook(TypedDict, total=False):
    """Structure that contains ``payloadVersion`` and ``targetArn``."""

    payloadVersion: Optional[PayloadVersion]
    targetArn: TargetArn


class CreateProvisioningTemplateRequest(ServiceRequest):
    templateName: TemplateName
    description: Optional[TemplateDescription]
    templateBody: TemplateBody
    enabled: Optional[Enabled]
    provisioningRoleArn: RoleArn
    preProvisioningHook: Optional[ProvisioningHook]
    tags: Optional[TagList]


class CreateProvisioningTemplateResponse(TypedDict, total=False):
    templateArn: Optional[TemplateArn]
    templateName: Optional[TemplateName]
    defaultVersionId: Optional[TemplateVersionId]


class CreateProvisioningTemplateVersionRequest(ServiceRequest):
    templateName: TemplateName
    templateBody: TemplateBody
    setAsDefault: Optional[SetAsDefault]


class CreateProvisioningTemplateVersionResponse(TypedDict, total=False):
    templateArn: Optional[TemplateArn]
    templateName: Optional[TemplateName]
    versionId: Optional[TemplateVersionId]
    isDefaultVersion: Optional[IsDefaultVersion]


class CreateRoleAliasRequest(ServiceRequest):
    roleAlias: RoleAlias
    roleArn: RoleArn
    credentialDurationSeconds: Optional[CredentialDurationSeconds]
    tags: Optional[TagList]


class CreateRoleAliasResponse(TypedDict, total=False):
    roleAlias: Optional[RoleAlias]
    roleAliasArn: Optional[RoleAliasArn]


TargetAuditCheckNames = List[AuditCheckName]


class CreateScheduledAuditRequest(ServiceRequest):
    frequency: AuditFrequency
    dayOfMonth: Optional[DayOfMonth]
    dayOfWeek: Optional[DayOfWeek]
    targetCheckNames: TargetAuditCheckNames
    scheduledAuditName: ScheduledAuditName
    tags: Optional[TagList]


class CreateScheduledAuditResponse(TypedDict, total=False):
    scheduledAuditArn: Optional[ScheduledAuditArn]


class CreateSecurityProfileRequest(ServiceRequest):
    securityProfileName: SecurityProfileName
    securityProfileDescription: Optional[SecurityProfileDescription]
    behaviors: Optional[Behaviors]
    alertTargets: Optional[AlertTargets]
    additionalMetricsToRetain: Optional[AdditionalMetricsToRetainList]
    additionalMetricsToRetainV2: Optional[AdditionalMetricsToRetainV2List]
    tags: Optional[TagList]


class CreateSecurityProfileResponse(TypedDict, total=False):
    securityProfileName: Optional[SecurityProfileName]
    securityProfileArn: Optional[SecurityProfileArn]


class StreamFile(TypedDict, total=False):
    """Represents a file to stream."""

    fileId: Optional[FileId]
    s3Location: Optional[S3Location]


StreamFiles = List[StreamFile]


class CreateStreamRequest(ServiceRequest):
    streamId: StreamId
    description: Optional[StreamDescription]
    files: StreamFiles
    roleArn: RoleArn
    tags: Optional[TagList]


class CreateStreamResponse(TypedDict, total=False):
    streamId: Optional[StreamId]
    streamArn: Optional[StreamArn]
    description: Optional[StreamDescription]
    streamVersion: Optional[StreamVersion]


class CreateThingGroupRequest(ServiceRequest):
    thingGroupName: ThingGroupName
    parentGroupName: Optional[ThingGroupName]
    thingGroupProperties: Optional[ThingGroupProperties]
    tags: Optional[TagList]


class CreateThingGroupResponse(TypedDict, total=False):
    thingGroupName: Optional[ThingGroupName]
    thingGroupArn: Optional[ThingGroupArn]
    thingGroupId: Optional[ThingGroupId]


class CreateThingRequest(ServiceRequest):
    """The input for the CreateThing operation."""

    thingName: ThingName
    thingTypeName: Optional[ThingTypeName]
    attributePayload: Optional[AttributePayload]
    billingGroupName: Optional[BillingGroupName]


class CreateThingResponse(TypedDict, total=False):
    """The output of the CreateThing operation."""

    thingName: Optional[ThingName]
    thingArn: Optional[ThingArn]
    thingId: Optional[ThingId]


SearchableAttributes = List[AttributeName]


class ThingTypeProperties(TypedDict, total=False):
    """The ThingTypeProperties contains information about the thing type
    including: a thing type description, and a list of searchable thing
    attribute names.
    """

    thingTypeDescription: Optional[ThingTypeDescription]
    searchableAttributes: Optional[SearchableAttributes]


class CreateThingTypeRequest(ServiceRequest):
    """The input for the CreateThingType operation."""

    thingTypeName: ThingTypeName
    thingTypeProperties: Optional[ThingTypeProperties]
    tags: Optional[TagList]


class CreateThingTypeResponse(TypedDict, total=False):
    """The output of the CreateThingType operation."""

    thingTypeName: Optional[ThingTypeName]
    thingTypeArn: Optional[ThingTypeArn]
    thingTypeId: Optional[ThingTypeId]


SecurityGroupList = List[SecurityGroupId]
SubnetIdList = List[SubnetId]


class VpcDestinationConfiguration(TypedDict, total=False):
    """The configuration information for a virtual private cloud (VPC)
    destination.
    """

    subnetIds: SubnetIdList
    securityGroups: Optional[SecurityGroupList]
    vpcId: VpcId
    roleArn: AwsArn


class HttpUrlDestinationConfiguration(TypedDict, total=False):
    """HTTP URL destination configuration used by the topic rule's HTTP action."""

    confirmationUrl: Url


class TopicRuleDestinationConfiguration(TypedDict, total=False):
    """Configuration of the topic rule destination."""

    httpUrlConfiguration: Optional[HttpUrlDestinationConfiguration]
    vpcConfiguration: Optional[VpcDestinationConfiguration]


class CreateTopicRuleDestinationRequest(ServiceRequest):
    destinationConfiguration: TopicRuleDestinationConfiguration


class VpcDestinationProperties(TypedDict, total=False):
    """The properties of a virtual private cloud (VPC) destination."""

    subnetIds: Optional[SubnetIdList]
    securityGroups: Optional[SecurityGroupList]
    vpcId: Optional[VpcId]
    roleArn: Optional[AwsArn]


class HttpUrlDestinationProperties(TypedDict, total=False):
    """HTTP URL destination properties."""

    confirmationUrl: Optional[Url]


LastUpdatedAtDate = datetime
CreatedAtDate = datetime


class TopicRuleDestination(TypedDict, total=False):
    """A topic rule destination."""

    arn: Optional[AwsArn]
    status: Optional[TopicRuleDestinationStatus]
    createdAt: Optional[CreatedAtDate]
    lastUpdatedAt: Optional[LastUpdatedAtDate]
    statusReason: Optional[String]
    httpUrlProperties: Optional[HttpUrlDestinationProperties]
    vpcProperties: Optional[VpcDestinationProperties]


class CreateTopicRuleDestinationResponse(TypedDict, total=False):
    topicRuleDestination: Optional[TopicRuleDestination]


class TopicRulePayload(TypedDict, total=False):
    """Describes a rule."""

    sql: SQL
    description: Optional[Description]
    actions: ActionList
    ruleDisabled: Optional[IsDisabled]
    awsIotSqlVersion: Optional[AwsIotSqlVersion]
    errorAction: Optional[Action]


class CreateTopicRuleRequest(ServiceRequest):
    """The input for the CreateTopicRule operation."""

    ruleName: RuleName
    topicRulePayload: TopicRulePayload
    tags: Optional[String]


class DeleteAccountAuditConfigurationRequest(ServiceRequest):
    deleteScheduledAudits: Optional[DeleteScheduledAudits]


class DeleteAccountAuditConfigurationResponse(TypedDict, total=False):
    pass


class DeleteAuditSuppressionRequest(ServiceRequest):
    checkName: AuditCheckName
    resourceIdentifier: ResourceIdentifier


class DeleteAuditSuppressionResponse(TypedDict, total=False):
    pass


class DeleteAuthorizerRequest(ServiceRequest):
    authorizerName: AuthorizerName


class DeleteAuthorizerResponse(TypedDict, total=False):
    pass


OptionalVersion = int


class DeleteBillingGroupRequest(ServiceRequest):
    billingGroupName: BillingGroupName
    expectedVersion: Optional[OptionalVersion]


class DeleteBillingGroupResponse(TypedDict, total=False):
    pass


class DeleteCACertificateRequest(ServiceRequest):
    """Input for the DeleteCACertificate operation."""

    certificateId: CertificateId


class DeleteCACertificateResponse(TypedDict, total=False):
    """The output for the DeleteCACertificate operation."""


class DeleteCertificateRequest(ServiceRequest):
    """The input for the DeleteCertificate operation."""

    certificateId: CertificateId
    forceDelete: Optional[ForceDelete]


class DeleteCustomMetricRequest(ServiceRequest):
    metricName: MetricName


class DeleteCustomMetricResponse(TypedDict, total=False):
    pass


class DeleteDimensionRequest(ServiceRequest):
    name: DimensionName


class DeleteDimensionResponse(TypedDict, total=False):
    pass


class DeleteDomainConfigurationRequest(ServiceRequest):
    domainConfigurationName: DomainConfigurationName


class DeleteDomainConfigurationResponse(TypedDict, total=False):
    pass


class DeleteDynamicThingGroupRequest(ServiceRequest):
    thingGroupName: ThingGroupName
    expectedVersion: Optional[OptionalVersion]


class DeleteDynamicThingGroupResponse(TypedDict, total=False):
    pass


class DeleteFleetMetricRequest(ServiceRequest):
    metricName: FleetMetricName
    expectedVersion: Optional[OptionalVersion]


ExecutionNumber = int


class DeleteJobExecutionRequest(ServiceRequest):
    jobId: JobId
    thingName: ThingName
    executionNumber: ExecutionNumber
    force: Optional[ForceFlag]
    namespaceId: Optional[NamespaceId]


class DeleteJobRequest(ServiceRequest):
    jobId: JobId
    force: Optional[ForceFlag]
    namespaceId: Optional[NamespaceId]


class DeleteJobTemplateRequest(ServiceRequest):
    jobTemplateId: JobTemplateId


class DeleteMitigationActionRequest(ServiceRequest):
    actionName: MitigationActionName


class DeleteMitigationActionResponse(TypedDict, total=False):
    pass


class DeleteOTAUpdateRequest(ServiceRequest):
    otaUpdateId: OTAUpdateId
    deleteStream: Optional[DeleteStream]
    forceDeleteAWSJob: Optional[ForceDeleteAWSJob]


class DeleteOTAUpdateResponse(TypedDict, total=False):
    pass


class DeletePolicyRequest(ServiceRequest):
    """The input for the DeletePolicy operation."""

    policyName: PolicyName


class DeletePolicyVersionRequest(ServiceRequest):
    """The input for the DeletePolicyVersion operation."""

    policyName: PolicyName
    policyVersionId: PolicyVersionId


class DeleteProvisioningTemplateRequest(ServiceRequest):
    templateName: TemplateName


class DeleteProvisioningTemplateResponse(TypedDict, total=False):
    pass


class DeleteProvisioningTemplateVersionRequest(ServiceRequest):
    templateName: TemplateName
    versionId: TemplateVersionId


class DeleteProvisioningTemplateVersionResponse(TypedDict, total=False):
    pass


class DeleteRegistrationCodeRequest(ServiceRequest):
    """The input for the DeleteRegistrationCode operation."""


class DeleteRegistrationCodeResponse(TypedDict, total=False):
    """The output for the DeleteRegistrationCode operation."""


class DeleteRoleAliasRequest(ServiceRequest):
    roleAlias: RoleAlias


class DeleteRoleAliasResponse(TypedDict, total=False):
    pass


class DeleteScheduledAuditRequest(ServiceRequest):
    scheduledAuditName: ScheduledAuditName


class DeleteScheduledAuditResponse(TypedDict, total=False):
    pass


class DeleteSecurityProfileRequest(ServiceRequest):
    securityProfileName: SecurityProfileName
    expectedVersion: Optional[OptionalVersion]


class DeleteSecurityProfileResponse(TypedDict, total=False):
    pass


class DeleteStreamRequest(ServiceRequest):
    streamId: StreamId


class DeleteStreamResponse(TypedDict, total=False):
    pass


class DeleteThingGroupRequest(ServiceRequest):
    thingGroupName: ThingGroupName
    expectedVersion: Optional[OptionalVersion]


class DeleteThingGroupResponse(TypedDict, total=False):
    pass


class DeleteThingRequest(ServiceRequest):
    """The input for the DeleteThing operation."""

    thingName: ThingName
    expectedVersion: Optional[OptionalVersion]


class DeleteThingResponse(TypedDict, total=False):
    """The output of the DeleteThing operation."""


class DeleteThingTypeRequest(ServiceRequest):
    """The input for the DeleteThingType operation."""

    thingTypeName: ThingTypeName


class DeleteThingTypeResponse(TypedDict, total=False):
    """The output for the DeleteThingType operation."""


class DeleteTopicRuleDestinationRequest(ServiceRequest):
    arn: AwsArn


class DeleteTopicRuleDestinationResponse(TypedDict, total=False):
    pass


class DeleteTopicRuleRequest(ServiceRequest):
    """The input for the DeleteTopicRule operation."""

    ruleName: RuleName


class DeleteV2LoggingLevelRequest(ServiceRequest):
    targetType: LogTargetType
    targetName: LogTargetName


class DeprecateThingTypeRequest(ServiceRequest):
    """The input for the DeprecateThingType operation."""

    thingTypeName: ThingTypeName
    undoDeprecate: Optional[UndoDeprecate]


class DeprecateThingTypeResponse(TypedDict, total=False):
    """The output for the DeprecateThingType operation."""


DeprecationDate = datetime


class DescribeAccountAuditConfigurationRequest(ServiceRequest):
    pass


class DescribeAccountAuditConfigurationResponse(TypedDict, total=False):
    roleArn: Optional[RoleArn]
    auditNotificationTargetConfigurations: Optional[AuditNotificationTargetConfigurations]
    auditCheckConfigurations: Optional[AuditCheckConfigurations]


class DescribeAuditFindingRequest(ServiceRequest):
    findingId: FindingId


class DescribeAuditFindingResponse(TypedDict, total=False):
    finding: Optional[AuditFinding]


class DescribeAuditMitigationActionsTaskRequest(ServiceRequest):
    taskId: MitigationActionsTaskId


class MitigationAction(TypedDict, total=False):
    """Describes which changes should be applied as part of a mitigation
    action.
    """

    name: Optional[MitigationActionName]
    id: Optional[MitigationActionId]
    roleArn: Optional[RoleArn]
    actionParams: Optional[MitigationActionParams]


MitigationActionList = List[MitigationAction]


class DescribeAuditMitigationActionsTaskResponse(TypedDict, total=False):
    taskStatus: Optional[AuditMitigationActionsTaskStatus]
    startTime: Optional[Timestamp]
    endTime: Optional[Timestamp]
    taskStatistics: Optional[AuditMitigationActionsTaskStatistics]
    target: Optional[AuditMitigationActionsTaskTarget]
    auditCheckToActionsMapping: Optional[AuditCheckToActionsMapping]
    actionsDefinition: Optional[MitigationActionList]


class DescribeAuditSuppressionRequest(ServiceRequest):
    checkName: AuditCheckName
    resourceIdentifier: ResourceIdentifier


class DescribeAuditSuppressionResponse(TypedDict, total=False):
    checkName: Optional[AuditCheckName]
    resourceIdentifier: Optional[ResourceIdentifier]
    expirationDate: Optional[Timestamp]
    suppressIndefinitely: Optional[SuppressIndefinitely]
    description: Optional[AuditDescription]


class DescribeAuditTaskRequest(ServiceRequest):
    taskId: AuditTaskId


class TaskStatistics(TypedDict, total=False):
    """Statistics for the checks performed during the audit."""

    totalChecks: Optional[TotalChecksCount]
    inProgressChecks: Optional[InProgressChecksCount]
    waitingForDataCollectionChecks: Optional[WaitingForDataCollectionChecksCount]
    compliantChecks: Optional[CompliantChecksCount]
    nonCompliantChecks: Optional[NonCompliantChecksCount]
    failedChecks: Optional[FailedChecksCount]
    canceledChecks: Optional[CanceledChecksCount]


class DescribeAuditTaskResponse(TypedDict, total=False):
    taskStatus: Optional[AuditTaskStatus]
    taskType: Optional[AuditTaskType]
    taskStartTime: Optional[Timestamp]
    taskStatistics: Optional[TaskStatistics]
    scheduledAuditName: Optional[ScheduledAuditName]
    auditDetails: Optional[AuditDetails]


class DescribeAuthorizerRequest(ServiceRequest):
    authorizerName: AuthorizerName


class DescribeAuthorizerResponse(TypedDict, total=False):
    authorizerDescription: Optional[AuthorizerDescription]


class DescribeBillingGroupRequest(ServiceRequest):
    billingGroupName: BillingGroupName


Version = int


class DescribeBillingGroupResponse(TypedDict, total=False):
    billingGroupName: Optional[BillingGroupName]
    billingGroupId: Optional[BillingGroupId]
    billingGroupArn: Optional[BillingGroupArn]
    version: Optional[Version]
    billingGroupProperties: Optional[BillingGroupProperties]
    billingGroupMetadata: Optional[BillingGroupMetadata]


class DescribeCACertificateRequest(ServiceRequest):
    """The input for the DescribeCACertificate operation."""

    certificateId: CertificateId


class RegistrationConfig(TypedDict, total=False):
    """The registration configuration."""

    templateBody: Optional[TemplateBody]
    roleArn: Optional[RoleArn]


class DescribeCACertificateResponse(TypedDict, total=False):
    """The output from the DescribeCACertificate operation."""

    certificateDescription: Optional[CACertificateDescription]
    registrationConfig: Optional[RegistrationConfig]


class DescribeCertificateRequest(ServiceRequest):
    """The input for the DescribeCertificate operation."""

    certificateId: CertificateId


class DescribeCertificateResponse(TypedDict, total=False):
    """The output of the DescribeCertificate operation."""

    certificateDescription: Optional[CertificateDescription]


class DescribeCustomMetricRequest(ServiceRequest):
    metricName: MetricName


class DescribeCustomMetricResponse(TypedDict, total=False):
    metricName: Optional[MetricName]
    metricArn: Optional[CustomMetricArn]
    metricType: Optional[CustomMetricType]
    displayName: Optional[CustomMetricDisplayName]
    creationDate: Optional[Timestamp]
    lastModifiedDate: Optional[Timestamp]


class DescribeDefaultAuthorizerRequest(ServiceRequest):
    pass


class DescribeDefaultAuthorizerResponse(TypedDict, total=False):
    authorizerDescription: Optional[AuthorizerDescription]


class DescribeDetectMitigationActionsTaskRequest(ServiceRequest):
    taskId: MitigationActionsTaskId


GenericLongValue = int


class DetectMitigationActionsTaskStatistics(TypedDict, total=False):
    """The statistics of a mitigation action task."""

    actionsExecuted: Optional[GenericLongValue]
    actionsSkipped: Optional[GenericLongValue]
    actionsFailed: Optional[GenericLongValue]


class ViolationEventOccurrenceRange(TypedDict, total=False):
    """Specifies the time period of which violation events occurred between."""

    startTime: Timestamp
    endTime: Timestamp


TargetViolationIdsForDetectMitigationActions = List[ViolationId]


class DetectMitigationActionsTaskTarget(TypedDict, total=False):
    """The target of a mitigation action task."""

    violationIds: Optional[TargetViolationIdsForDetectMitigationActions]
    securityProfileName: Optional[SecurityProfileName]
    behaviorName: Optional[BehaviorName]


class DetectMitigationActionsTaskSummary(TypedDict, total=False):
    """The summary of the mitigation action tasks."""

    taskId: Optional[MitigationActionsTaskId]
    taskStatus: Optional[DetectMitigationActionsTaskStatus]
    taskStartTime: Optional[Timestamp]
    taskEndTime: Optional[Timestamp]
    target: Optional[DetectMitigationActionsTaskTarget]
    violationEventOccurrenceRange: Optional[ViolationEventOccurrenceRange]
    onlyActiveViolationsIncluded: Optional[PrimitiveBoolean]
    suppressedAlertsIncluded: Optional[PrimitiveBoolean]
    actionsDefinition: Optional[MitigationActionList]
    taskStatistics: Optional[DetectMitigationActionsTaskStatistics]


class DescribeDetectMitigationActionsTaskResponse(TypedDict, total=False):
    taskSummary: Optional[DetectMitigationActionsTaskSummary]


class DescribeDimensionRequest(ServiceRequest):
    name: DimensionName


DescribeDimensionResponse = TypedDict(
    "DescribeDimensionResponse",
    {
        "name": Optional[DimensionName],
        "arn": Optional[DimensionArn],
        "type": Optional[DimensionType],
        "stringValues": Optional[DimensionStringValues],
        "creationDate": Optional[Timestamp],
        "lastModifiedDate": Optional[Timestamp],
    },
    total=False,
)


class DescribeDomainConfigurationRequest(ServiceRequest):
    domainConfigurationName: ReservedDomainConfigurationName


class ServerCertificateSummary(TypedDict, total=False):
    """An object that contains information about a server certificate."""

    serverCertificateArn: Optional[AcmCertificateArn]
    serverCertificateStatus: Optional[ServerCertificateStatus]
    serverCertificateStatusDetail: Optional[ServerCertificateStatusDetail]


ServerCertificates = List[ServerCertificateSummary]


class DescribeDomainConfigurationResponse(TypedDict, total=False):
    domainConfigurationName: Optional[ReservedDomainConfigurationName]
    domainConfigurationArn: Optional[DomainConfigurationArn]
    domainName: Optional[DomainName]
    serverCertificates: Optional[ServerCertificates]
    authorizerConfig: Optional[AuthorizerConfig]
    domainConfigurationStatus: Optional[DomainConfigurationStatus]
    serviceType: Optional[ServiceType]
    domainType: Optional[DomainType]
    lastStatusChangeDate: Optional[DateType]


class DescribeEndpointRequest(ServiceRequest):
    """The input for the DescribeEndpoint operation."""

    endpointType: Optional[EndpointType]


class DescribeEndpointResponse(TypedDict, total=False):
    """The output from the DescribeEndpoint operation."""

    endpointAddress: Optional[EndpointAddress]


class DescribeEventConfigurationsRequest(ServiceRequest):
    pass


LastModifiedDate = datetime
EventConfigurations = Dict[EventType, Configuration]


class DescribeEventConfigurationsResponse(TypedDict, total=False):
    eventConfigurations: Optional[EventConfigurations]
    creationDate: Optional[CreationDate]
    lastModifiedDate: Optional[LastModifiedDate]


class DescribeFleetMetricRequest(ServiceRequest):
    metricName: FleetMetricName


class DescribeFleetMetricResponse(TypedDict, total=False):
    metricName: Optional[FleetMetricName]
    queryString: Optional[QueryString]
    aggregationType: Optional[AggregationType]
    period: Optional[FleetMetricPeriod]
    aggregationField: Optional[AggregationField]
    description: Optional[FleetMetricDescription]
    queryVersion: Optional[QueryVersion]
    indexName: Optional[IndexName]
    creationDate: Optional[CreationDate]
    lastModifiedDate: Optional[LastModifiedDate]
    unit: Optional[FleetMetricUnit]
    version: Optional[Version]
    metricArn: Optional[FleetMetricArn]


class DescribeIndexRequest(ServiceRequest):
    indexName: IndexName


class DescribeIndexResponse(TypedDict, total=False):
    indexName: Optional[IndexName]
    indexStatus: Optional[IndexStatus]
    schema: Optional[IndexSchema]


class DescribeJobExecutionRequest(ServiceRequest):
    jobId: JobId
    thingName: ThingName
    executionNumber: Optional[ExecutionNumber]


VersionNumber = int


class JobExecutionStatusDetails(TypedDict, total=False):
    """Details of the job execution status."""

    detailsMap: Optional[DetailsMap]


class JobExecution(TypedDict, total=False):
    """The job execution object represents the execution of a job on a
    particular device.
    """

    jobId: Optional[JobId]
    status: Optional[JobExecutionStatus]
    forceCanceled: Optional[Forced]
    statusDetails: Optional[JobExecutionStatusDetails]
    thingArn: Optional[ThingArn]
    queuedAt: Optional[DateType]
    startedAt: Optional[DateType]
    lastUpdatedAt: Optional[DateType]
    executionNumber: Optional[ExecutionNumber]
    versionNumber: Optional[VersionNumber]
    approximateSecondsBeforeTimedOut: Optional[ApproximateSecondsBeforeTimedOut]


class DescribeJobExecutionResponse(TypedDict, total=False):
    execution: Optional[JobExecution]


class DescribeJobRequest(ServiceRequest):
    jobId: JobId


ProcessingTargetNameList = List[ProcessingTargetName]


class JobProcessDetails(TypedDict, total=False):
    """The job process details."""

    processingTargets: Optional[ProcessingTargetNameList]
    numberOfCanceledThings: Optional[CanceledThings]
    numberOfSucceededThings: Optional[SucceededThings]
    numberOfFailedThings: Optional[FailedThings]
    numberOfRejectedThings: Optional[RejectedThings]
    numberOfQueuedThings: Optional[QueuedThings]
    numberOfInProgressThings: Optional[InProgressThings]
    numberOfRemovedThings: Optional[RemovedThings]
    numberOfTimedOutThings: Optional[TimedOutThings]


class Job(TypedDict, total=False):
    """The ``Job`` object contains details about a job."""

    jobArn: Optional[JobArn]
    jobId: Optional[JobId]
    targetSelection: Optional[TargetSelection]
    status: Optional[JobStatus]
    forceCanceled: Optional[Forced]
    reasonCode: Optional[ReasonCode]
    comment: Optional[Comment]
    targets: Optional[JobTargets]
    description: Optional[JobDescription]
    presignedUrlConfig: Optional[PresignedUrlConfig]
    jobExecutionsRolloutConfig: Optional[JobExecutionsRolloutConfig]
    abortConfig: Optional[AbortConfig]
    createdAt: Optional[DateType]
    lastUpdatedAt: Optional[DateType]
    completedAt: Optional[DateType]
    jobProcessDetails: Optional[JobProcessDetails]
    timeoutConfig: Optional[TimeoutConfig]
    namespaceId: Optional[NamespaceId]
    jobTemplateArn: Optional[JobTemplateArn]
    jobExecutionsRetryConfig: Optional[JobExecutionsRetryConfig]
    documentParameters: Optional[ParameterMap]
    isConcurrent: Optional[BooleanWrapperObject]


class DescribeJobResponse(TypedDict, total=False):
    documentSource: Optional[JobDocumentSource]
    job: Optional[Job]


class DescribeJobTemplateRequest(ServiceRequest):
    jobTemplateId: JobTemplateId


class DescribeJobTemplateResponse(TypedDict, total=False):
    jobTemplateArn: Optional[JobTemplateArn]
    jobTemplateId: Optional[JobTemplateId]
    description: Optional[JobDescription]
    documentSource: Optional[JobDocumentSource]
    document: Optional[JobDocument]
    createdAt: Optional[DateType]
    presignedUrlConfig: Optional[PresignedUrlConfig]
    jobExecutionsRolloutConfig: Optional[JobExecutionsRolloutConfig]
    abortConfig: Optional[AbortConfig]
    timeoutConfig: Optional[TimeoutConfig]
    jobExecutionsRetryConfig: Optional[JobExecutionsRetryConfig]


class DescribeManagedJobTemplateRequest(ServiceRequest):
    templateName: ManagedJobTemplateName
    templateVersion: Optional[ManagedTemplateVersion]


class DocumentParameter(TypedDict, total=False):
    """A map of key-value pairs containing the patterns that need to be
    replaced in a managed template job document schema. You can use the
    description of each key as a guidance to specify the inputs during
    runtime when creating a job.
    """

    key: Optional[ParameterKey]
    description: Optional[JobDescription]
    regex: Optional[Regex]
    example: Optional[Example]
    optional: Optional[Optional_]


DocumentParameters = List[DocumentParameter]
Environments = List[Environment]


class DescribeManagedJobTemplateResponse(TypedDict, total=False):
    templateName: Optional[ManagedJobTemplateName]
    templateArn: Optional[JobTemplateArn]
    description: Optional[JobDescription]
    templateVersion: Optional[ManagedTemplateVersion]
    environments: Optional[Environments]
    documentParameters: Optional[DocumentParameters]
    document: Optional[JobDocument]


class DescribeMitigationActionRequest(ServiceRequest):
    actionName: MitigationActionName


class DescribeMitigationActionResponse(TypedDict, total=False):
    actionName: Optional[MitigationActionName]
    actionType: Optional[MitigationActionType]
    actionArn: Optional[MitigationActionArn]
    actionId: Optional[MitigationActionId]
    roleArn: Optional[RoleArn]
    actionParams: Optional[MitigationActionParams]
    creationDate: Optional[Timestamp]
    lastModifiedDate: Optional[Timestamp]


class DescribeProvisioningTemplateRequest(ServiceRequest):
    templateName: TemplateName


class DescribeProvisioningTemplateResponse(TypedDict, total=False):
    templateArn: Optional[TemplateArn]
    templateName: Optional[TemplateName]
    description: Optional[TemplateDescription]
    creationDate: Optional[DateType]
    lastModifiedDate: Optional[DateType]
    defaultVersionId: Optional[TemplateVersionId]
    templateBody: Optional[TemplateBody]
    enabled: Optional[Enabled]
    provisioningRoleArn: Optional[RoleArn]
    preProvisioningHook: Optional[ProvisioningHook]


class DescribeProvisioningTemplateVersionRequest(ServiceRequest):
    templateName: TemplateName
    versionId: TemplateVersionId


class DescribeProvisioningTemplateVersionResponse(TypedDict, total=False):
    versionId: Optional[TemplateVersionId]
    creationDate: Optional[DateType]
    templateBody: Optional[TemplateBody]
    isDefaultVersion: Optional[IsDefaultVersion]


class DescribeRoleAliasRequest(ServiceRequest):
    roleAlias: RoleAlias


class RoleAliasDescription(TypedDict, total=False):
    """Role alias description."""

    roleAlias: Optional[RoleAlias]
    roleAliasArn: Optional[RoleAliasArn]
    roleArn: Optional[RoleArn]
    owner: Optional[AwsAccountId]
    credentialDurationSeconds: Optional[CredentialDurationSeconds]
    creationDate: Optional[DateType]
    lastModifiedDate: Optional[DateType]


class DescribeRoleAliasResponse(TypedDict, total=False):
    roleAliasDescription: Optional[RoleAliasDescription]


class DescribeScheduledAuditRequest(ServiceRequest):
    scheduledAuditName: ScheduledAuditName


class DescribeScheduledAuditResponse(TypedDict, total=False):
    frequency: Optional[AuditFrequency]
    dayOfMonth: Optional[DayOfMonth]
    dayOfWeek: Optional[DayOfWeek]
    targetCheckNames: Optional[TargetAuditCheckNames]
    scheduledAuditName: Optional[ScheduledAuditName]
    scheduledAuditArn: Optional[ScheduledAuditArn]


class DescribeSecurityProfileRequest(ServiceRequest):
    securityProfileName: SecurityProfileName


class DescribeSecurityProfileResponse(TypedDict, total=False):
    securityProfileName: Optional[SecurityProfileName]
    securityProfileArn: Optional[SecurityProfileArn]
    securityProfileDescription: Optional[SecurityProfileDescription]
    behaviors: Optional[Behaviors]
    alertTargets: Optional[AlertTargets]
    additionalMetricsToRetain: Optional[AdditionalMetricsToRetainList]
    additionalMetricsToRetainV2: Optional[AdditionalMetricsToRetainV2List]
    version: Optional[Version]
    creationDate: Optional[Timestamp]
    lastModifiedDate: Optional[Timestamp]


class DescribeStreamRequest(ServiceRequest):
    streamId: StreamId


class StreamInfo(TypedDict, total=False):
    """Information about a stream."""

    streamId: Optional[StreamId]
    streamArn: Optional[StreamArn]
    streamVersion: Optional[StreamVersion]
    description: Optional[StreamDescription]
    files: Optional[StreamFiles]
    createdAt: Optional[DateType]
    lastUpdatedAt: Optional[DateType]
    roleArn: Optional[RoleArn]


class DescribeStreamResponse(TypedDict, total=False):
    streamInfo: Optional[StreamInfo]


class DescribeThingGroupRequest(ServiceRequest):
    thingGroupName: ThingGroupName


ThingGroupNameAndArnList = List[GroupNameAndArn]


class ThingGroupMetadata(TypedDict, total=False):
    """Thing group metadata."""

    parentGroupName: Optional[ThingGroupName]
    rootToParentThingGroups: Optional[ThingGroupNameAndArnList]
    creationDate: Optional[CreationDate]


class DescribeThingGroupResponse(TypedDict, total=False):
    thingGroupName: Optional[ThingGroupName]
    thingGroupId: Optional[ThingGroupId]
    thingGroupArn: Optional[ThingGroupArn]
    version: Optional[Version]
    thingGroupProperties: Optional[ThingGroupProperties]
    thingGroupMetadata: Optional[ThingGroupMetadata]
    indexName: Optional[IndexName]
    queryString: Optional[QueryString]
    queryVersion: Optional[QueryVersion]
    status: Optional[DynamicGroupStatus]


class DescribeThingRegistrationTaskRequest(ServiceRequest):
    taskId: TaskId


class DescribeThingRegistrationTaskResponse(TypedDict, total=False):
    taskId: Optional[TaskId]
    creationDate: Optional[CreationDate]
    lastModifiedDate: Optional[LastModifiedDate]
    templateBody: Optional[TemplateBody]
    inputFileBucket: Optional[RegistryS3BucketName]
    inputFileKey: Optional[RegistryS3KeyName]
    roleArn: Optional[RoleArn]
    status: Optional[Status]
    message: Optional[ErrorMessage]
    successCount: Optional[Count]
    failureCount: Optional[Count]
    percentageProgress: Optional[Percentage]


class DescribeThingRequest(ServiceRequest):
    """The input for the DescribeThing operation."""

    thingName: ThingName


class DescribeThingResponse(TypedDict, total=False):
    """The output from the DescribeThing operation."""

    defaultClientId: Optional[ClientId]
    thingName: Optional[ThingName]
    thingId: Optional[ThingId]
    thingArn: Optional[ThingArn]
    thingTypeName: Optional[ThingTypeName]
    attributes: Optional[Attributes]
    version: Optional[Version]
    billingGroupName: Optional[BillingGroupName]


class DescribeThingTypeRequest(ServiceRequest):
    """The input for the DescribeThingType operation."""

    thingTypeName: ThingTypeName


class ThingTypeMetadata(TypedDict, total=False):
    """The ThingTypeMetadata contains additional information about the thing
    type including: creation date and time, a value indicating whether the
    thing type is deprecated, and a date and time when time was deprecated.
    """

    deprecated: Optional[Boolean]
    deprecationDate: Optional[DeprecationDate]
    creationDate: Optional[CreationDate]


class DescribeThingTypeResponse(TypedDict, total=False):
    """The output for the DescribeThingType operation."""

    thingTypeName: Optional[ThingTypeName]
    thingTypeId: Optional[ThingTypeId]
    thingTypeArn: Optional[ThingTypeArn]
    thingTypeProperties: Optional[ThingTypeProperties]
    thingTypeMetadata: Optional[ThingTypeMetadata]


class DetachPolicyRequest(ServiceRequest):
    policyName: PolicyName
    target: PolicyTarget


class DetachPrincipalPolicyRequest(ServiceRequest):
    """The input for the DetachPrincipalPolicy operation."""

    policyName: PolicyName
    principal: Principal


class DetachSecurityProfileRequest(ServiceRequest):
    securityProfileName: SecurityProfileName
    securityProfileTargetArn: SecurityProfileTargetArn


class DetachSecurityProfileResponse(TypedDict, total=False):
    pass


class DetachThingPrincipalRequest(ServiceRequest):
    """The input for the DetachThingPrincipal operation."""

    thingName: ThingName
    principal: Principal


class DetachThingPrincipalResponse(TypedDict, total=False):
    """The output from the DetachThingPrincipal operation."""


class DetectMitigationActionExecution(TypedDict, total=False):
    """Describes which mitigation actions should be executed."""

    taskId: Optional[MitigationActionsTaskId]
    violationId: Optional[ViolationId]
    actionName: Optional[MitigationActionName]
    thingName: Optional[DeviceDefenderThingName]
    executionStartDate: Optional[Timestamp]
    executionEndDate: Optional[Timestamp]
    status: Optional[DetectMitigationActionExecutionStatus]
    errorCode: Optional[DetectMitigationActionExecutionErrorCode]
    message: Optional[ErrorMessage]


DetectMitigationActionExecutionList = List[DetectMitigationActionExecution]
DetectMitigationActionsTaskSummaryList = List[DetectMitigationActionsTaskSummary]
DetectMitigationActionsToExecuteList = List[MitigationActionName]
DimensionNames = List[DimensionName]


class DisableTopicRuleRequest(ServiceRequest):
    """The input for the DisableTopicRuleRequest operation."""

    ruleName: RuleName


class DomainConfigurationSummary(TypedDict, total=False):
    """The summary of a domain configuration. A domain configuration specifies
    custom IoT-specific information about a domain. A domain configuration
    can be associated with an Amazon Web Services-managed domain (for
    example, dbc123defghijk.iot.us-west-2.amazonaws.com), a customer managed
    domain, or a default endpoint.

    -  Data

    -  Jobs

    -  CredentialProvider
    """

    domainConfigurationName: Optional[ReservedDomainConfigurationName]
    domainConfigurationArn: Optional[DomainConfigurationArn]
    serviceType: Optional[ServiceType]


DomainConfigurations = List[DomainConfigurationSummary]


class EffectivePolicy(TypedDict, total=False):
    """The policy that has the effect on the authorization results."""

    policyName: Optional[PolicyName]
    policyArn: Optional[PolicyArn]
    policyDocument: Optional[PolicyDocument]


EffectivePolicies = List[EffectivePolicy]


class EnableTopicRuleRequest(ServiceRequest):
    """The input for the EnableTopicRuleRequest operation."""

    ruleName: RuleName


class ErrorInfo(TypedDict, total=False):
    """Error information."""

    code: Optional[Code]
    message: Optional[OTAUpdateErrorMessage]


Field = TypedDict(
    "Field",
    {
        "name": Optional[FieldName],
        "type": Optional[FieldType],
    },
    total=False,
)
Fields = List[Field]


class FleetMetricNameAndArn(TypedDict, total=False):
    """The name and ARN of a fleet metric."""

    metricName: Optional[FleetMetricName]
    metricArn: Optional[FleetMetricArn]


FleetMetricNameAndArnList = List[FleetMetricNameAndArn]


class GetBehaviorModelTrainingSummariesRequest(ServiceRequest):
    securityProfileName: Optional[SecurityProfileName]
    maxResults: Optional[TinyMaxResults]
    nextToken: Optional[NextToken]


class GetBehaviorModelTrainingSummariesResponse(TypedDict, total=False):
    summaries: Optional[BehaviorModelTrainingSummaries]
    nextToken: Optional[NextToken]


class GetBucketsAggregationRequest(ServiceRequest):
    indexName: Optional[IndexName]
    queryString: QueryString
    aggregationField: AggregationField
    queryVersion: Optional[QueryVersion]
    bucketsAggregationType: BucketsAggregationType


class GetBucketsAggregationResponse(TypedDict, total=False):
    totalCount: Optional[Count]
    buckets: Optional[Buckets]


class GetCardinalityRequest(ServiceRequest):
    indexName: Optional[IndexName]
    queryString: QueryString
    aggregationField: Optional[AggregationField]
    queryVersion: Optional[QueryVersion]


class GetCardinalityResponse(TypedDict, total=False):
    cardinality: Optional[Count]


class GetEffectivePoliciesRequest(ServiceRequest):
    principal: Optional[Principal]
    cognitoIdentityPoolId: Optional[CognitoIdentityPoolId]
    thingName: Optional[ThingName]


class GetEffectivePoliciesResponse(TypedDict, total=False):
    effectivePolicies: Optional[EffectivePolicies]


class GetIndexingConfigurationRequest(ServiceRequest):
    pass


class ThingGroupIndexingConfiguration(TypedDict, total=False):
    """Thing group indexing configuration."""

    thingGroupIndexingMode: ThingGroupIndexingMode
    managedFields: Optional[Fields]
    customFields: Optional[Fields]


class ThingIndexingConfiguration(TypedDict, total=False):
    """The thing indexing configuration. For more information, see `Managing
    Thing
    Indexing <https://docs.aws.amazon.com/iot/latest/developerguide/managing-index.html>`__.
    """

    thingIndexingMode: ThingIndexingMode
    thingConnectivityIndexingMode: Optional[ThingConnectivityIndexingMode]
    deviceDefenderIndexingMode: Optional[DeviceDefenderIndexingMode]
    namedShadowIndexingMode: Optional[NamedShadowIndexingMode]
    managedFields: Optional[Fields]
    customFields: Optional[Fields]


class GetIndexingConfigurationResponse(TypedDict, total=False):
    thingIndexingConfiguration: Optional[ThingIndexingConfiguration]
    thingGroupIndexingConfiguration: Optional[ThingGroupIndexingConfiguration]


class GetJobDocumentRequest(ServiceRequest):
    jobId: JobId


class GetJobDocumentResponse(TypedDict, total=False):
    document: Optional[JobDocument]


class GetLoggingOptionsRequest(ServiceRequest):
    """The input for the GetLoggingOptions operation."""


class GetLoggingOptionsResponse(TypedDict, total=False):
    """The output from the GetLoggingOptions operation."""

    roleArn: Optional[AwsArn]
    logLevel: Optional[LogLevel]


class GetOTAUpdateRequest(ServiceRequest):
    otaUpdateId: OTAUpdateId


class OTAUpdateInfo(TypedDict, total=False):
    """Information about an OTA update."""

    otaUpdateId: Optional[OTAUpdateId]
    otaUpdateArn: Optional[OTAUpdateArn]
    creationDate: Optional[DateType]
    lastModifiedDate: Optional[DateType]
    description: Optional[OTAUpdateDescription]
    targets: Optional[Targets]
    protocols: Optional[Protocols]
    awsJobExecutionsRolloutConfig: Optional[AwsJobExecutionsRolloutConfig]
    awsJobPresignedUrlConfig: Optional[AwsJobPresignedUrlConfig]
    targetSelection: Optional[TargetSelection]
    otaUpdateFiles: Optional[OTAUpdateFiles]
    otaUpdateStatus: Optional[OTAUpdateStatus]
    awsIotJobId: Optional[AwsIotJobId]
    awsIotJobArn: Optional[AwsIotJobArn]
    errorInfo: Optional[ErrorInfo]
    additionalParameters: Optional[AdditionalParameterMap]


class GetOTAUpdateResponse(TypedDict, total=False):
    otaUpdateInfo: Optional[OTAUpdateInfo]


PercentList = List[Percent]


class GetPercentilesRequest(ServiceRequest):
    indexName: Optional[IndexName]
    queryString: QueryString
    aggregationField: Optional[AggregationField]
    queryVersion: Optional[QueryVersion]
    percents: Optional[PercentList]


class PercentPair(TypedDict, total=False):
    """Describes the percentile and percentile value."""

    percent: Optional[Percent]
    value: Optional[PercentValue]


Percentiles = List[PercentPair]


class GetPercentilesResponse(TypedDict, total=False):
    percentiles: Optional[Percentiles]


class GetPolicyRequest(ServiceRequest):
    """The input for the GetPolicy operation."""

    policyName: PolicyName


class GetPolicyResponse(TypedDict, total=False):
    """The output from the GetPolicy operation."""

    policyName: Optional[PolicyName]
    policyArn: Optional[PolicyArn]
    policyDocument: Optional[PolicyDocument]
    defaultVersionId: Optional[PolicyVersionId]
    creationDate: Optional[DateType]
    lastModifiedDate: Optional[DateType]
    generationId: Optional[GenerationId]


class GetPolicyVersionRequest(ServiceRequest):
    """The input for the GetPolicyVersion operation."""

    policyName: PolicyName
    policyVersionId: PolicyVersionId


class GetPolicyVersionResponse(TypedDict, total=False):
    """The output from the GetPolicyVersion operation."""

    policyArn: Optional[PolicyArn]
    policyName: Optional[PolicyName]
    policyDocument: Optional[PolicyDocument]
    policyVersionId: Optional[PolicyVersionId]
    isDefaultVersion: Optional[IsDefaultVersion]
    creationDate: Optional[DateType]
    lastModifiedDate: Optional[DateType]
    generationId: Optional[GenerationId]


class GetRegistrationCodeRequest(ServiceRequest):
    """The input to the GetRegistrationCode operation."""


class GetRegistrationCodeResponse(TypedDict, total=False):
    """The output from the GetRegistrationCode operation."""

    registrationCode: Optional[RegistrationCode]


class GetStatisticsRequest(ServiceRequest):
    indexName: Optional[IndexName]
    queryString: QueryString
    aggregationField: Optional[AggregationField]
    queryVersion: Optional[QueryVersion]


class Statistics(TypedDict, total=False):
    """A map of key-value pairs for all supported statistics. For issues with
    missing or unexpected values for this API, consult `Fleet indexing
    troubleshooting
    guide <https://docs.aws.amazon.com/iot/latest/developerguide/fleet-indexing-troubleshooting.html>`__.
    """

    count: Optional[Count]
    average: Optional[Average]
    sum: Optional[Sum]
    minimum: Optional[Minimum]
    maximum: Optional[Maximum]
    sumOfSquares: Optional[SumOfSquares]
    variance: Optional[Variance]
    stdDeviation: Optional[StdDeviation]


class GetStatisticsResponse(TypedDict, total=False):
    statistics: Optional[Statistics]


class GetTopicRuleDestinationRequest(ServiceRequest):
    arn: AwsArn


class GetTopicRuleDestinationResponse(TypedDict, total=False):
    topicRuleDestination: Optional[TopicRuleDestination]


class GetTopicRuleRequest(ServiceRequest):
    """The input for the GetTopicRule operation."""

    ruleName: RuleName


class TopicRule(TypedDict, total=False):
    """Describes a rule."""

    ruleName: Optional[RuleName]
    sql: Optional[SQL]
    description: Optional[Description]
    createdAt: Optional[CreatedAtDate]
    actions: Optional[ActionList]
    ruleDisabled: Optional[IsDisabled]
    awsIotSqlVersion: Optional[AwsIotSqlVersion]
    errorAction: Optional[Action]


class GetTopicRuleResponse(TypedDict, total=False):
    """The output from the GetTopicRule operation."""

    ruleArn: Optional[RuleArn]
    rule: Optional[TopicRule]


class GetV2LoggingOptionsRequest(ServiceRequest):
    pass


class GetV2LoggingOptionsResponse(TypedDict, total=False):
    roleArn: Optional[AwsArn]
    defaultLogLevel: Optional[LogLevel]
    disableAllLogs: Optional[DisableAllLogs]


HttpHeaders = Dict[HttpHeaderName, HttpHeaderValue]


class HttpContext(TypedDict, total=False):
    """Specifies the HTTP context to use for the test authorizer request."""

    headers: Optional[HttpHeaders]
    queryString: Optional[HttpQueryString]


class HttpUrlDestinationSummary(TypedDict, total=False):
    """Information about an HTTP URL destination."""

    confirmationUrl: Optional[Url]


IndexNamesList = List[IndexName]


class JobExecutionSummary(TypedDict, total=False):
    """The job execution summary."""

    status: Optional[JobExecutionStatus]
    queuedAt: Optional[DateType]
    startedAt: Optional[DateType]
    lastUpdatedAt: Optional[DateType]
    executionNumber: Optional[ExecutionNumber]
    retryAttempt: Optional[RetryAttempt]


class JobExecutionSummaryForJob(TypedDict, total=False):
    """Contains a summary of information about job executions for a specific
    job.
    """

    thingArn: Optional[ThingArn]
    jobExecutionSummary: Optional[JobExecutionSummary]


JobExecutionSummaryForJobList = List[JobExecutionSummaryForJob]


class JobExecutionSummaryForThing(TypedDict, total=False):
    """The job execution summary for a thing."""

    jobId: Optional[JobId]
    jobExecutionSummary: Optional[JobExecutionSummary]


JobExecutionSummaryForThingList = List[JobExecutionSummaryForThing]


class JobSummary(TypedDict, total=False):
    """The job summary."""

    jobArn: Optional[JobArn]
    jobId: Optional[JobId]
    thingGroupId: Optional[ThingGroupId]
    targetSelection: Optional[TargetSelection]
    status: Optional[JobStatus]
    createdAt: Optional[DateType]
    lastUpdatedAt: Optional[DateType]
    completedAt: Optional[DateType]
    isConcurrent: Optional[BooleanWrapperObject]


JobSummaryList = List[JobSummary]


class JobTemplateSummary(TypedDict, total=False):
    """An object that contains information about the job template."""

    jobTemplateArn: Optional[JobTemplateArn]
    jobTemplateId: Optional[JobTemplateId]
    description: Optional[JobDescription]
    createdAt: Optional[DateType]


JobTemplateSummaryList = List[JobTemplateSummary]


class ListActiveViolationsRequest(ServiceRequest):
    thingName: Optional[DeviceDefenderThingName]
    securityProfileName: Optional[SecurityProfileName]
    behaviorCriteriaType: Optional[BehaviorCriteriaType]
    listSuppressedAlerts: Optional[ListSuppressedAlerts]
    verificationState: Optional[VerificationState]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListActiveViolationsResponse(TypedDict, total=False):
    activeViolations: Optional[ActiveViolations]
    nextToken: Optional[NextToken]


class ListAttachedPoliciesRequest(ServiceRequest):
    target: PolicyTarget
    recursive: Optional[Recursive]
    marker: Optional[Marker]
    pageSize: Optional[PageSize]


class ListAttachedPoliciesResponse(TypedDict, total=False):
    policies: Optional[Policies]
    nextMarker: Optional[Marker]


class ListAuditFindingsRequest(ServiceRequest):
    taskId: Optional[AuditTaskId]
    checkName: Optional[AuditCheckName]
    resourceIdentifier: Optional[ResourceIdentifier]
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]
    startTime: Optional[Timestamp]
    endTime: Optional[Timestamp]
    listSuppressedFindings: Optional[ListSuppressedFindings]


class ListAuditFindingsResponse(TypedDict, total=False):
    findings: Optional[AuditFindings]
    nextToken: Optional[NextToken]


class ListAuditMitigationActionsExecutionsRequest(ServiceRequest):
    taskId: MitigationActionsTaskId
    actionStatus: Optional[AuditMitigationActionsExecutionStatus]
    findingId: FindingId
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]


class ListAuditMitigationActionsExecutionsResponse(TypedDict, total=False):
    actionsExecutions: Optional[AuditMitigationActionExecutionMetadataList]
    nextToken: Optional[NextToken]


class ListAuditMitigationActionsTasksRequest(ServiceRequest):
    auditTaskId: Optional[AuditTaskId]
    findingId: Optional[FindingId]
    taskStatus: Optional[AuditMitigationActionsTaskStatus]
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]
    startTime: Timestamp
    endTime: Timestamp


class ListAuditMitigationActionsTasksResponse(TypedDict, total=False):
    tasks: Optional[AuditMitigationActionsTaskMetadataList]
    nextToken: Optional[NextToken]


class ListAuditSuppressionsRequest(ServiceRequest):
    checkName: Optional[AuditCheckName]
    resourceIdentifier: Optional[ResourceIdentifier]
    ascendingOrder: Optional[AscendingOrder]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListAuditSuppressionsResponse(TypedDict, total=False):
    suppressions: Optional[AuditSuppressionList]
    nextToken: Optional[NextToken]


class ListAuditTasksRequest(ServiceRequest):
    startTime: Timestamp
    endTime: Timestamp
    taskType: Optional[AuditTaskType]
    taskStatus: Optional[AuditTaskStatus]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListAuditTasksResponse(TypedDict, total=False):
    tasks: Optional[AuditTaskMetadataList]
    nextToken: Optional[NextToken]


class ListAuthorizersRequest(ServiceRequest):
    pageSize: Optional[PageSize]
    marker: Optional[Marker]
    ascendingOrder: Optional[AscendingOrder]
    status: Optional[AuthorizerStatus]


class ListAuthorizersResponse(TypedDict, total=False):
    authorizers: Optional[Authorizers]
    nextMarker: Optional[Marker]


class ListBillingGroupsRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]
    namePrefixFilter: Optional[BillingGroupName]


class ListBillingGroupsResponse(TypedDict, total=False):
    billingGroups: Optional[BillingGroupNameAndArnList]
    nextToken: Optional[NextToken]


class ListCACertificatesRequest(ServiceRequest):
    """Input for the ListCACertificates operation."""

    pageSize: Optional[PageSize]
    marker: Optional[Marker]
    ascendingOrder: Optional[AscendingOrder]


class ListCACertificatesResponse(TypedDict, total=False):
    """The output from the ListCACertificates operation."""

    certificates: Optional[CACertificates]
    nextMarker: Optional[Marker]


class ListCertificatesByCARequest(ServiceRequest):
    """The input to the ListCertificatesByCA operation."""

    caCertificateId: CertificateId
    pageSize: Optional[PageSize]
    marker: Optional[Marker]
    ascendingOrder: Optional[AscendingOrder]


class ListCertificatesByCAResponse(TypedDict, total=False):
    """The output of the ListCertificatesByCA operation."""

    certificates: Optional[Certificates]
    nextMarker: Optional[Marker]


class ListCertificatesRequest(ServiceRequest):
    """The input for the ListCertificates operation."""

    pageSize: Optional[PageSize]
    marker: Optional[Marker]
    ascendingOrder: Optional[AscendingOrder]


class ListCertificatesResponse(TypedDict, total=False):
    """The output of the ListCertificates operation."""

    certificates: Optional[Certificates]
    nextMarker: Optional[Marker]


class ListCustomMetricsRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


MetricNames = List[MetricName]


class ListCustomMetricsResponse(TypedDict, total=False):
    metricNames: Optional[MetricNames]
    nextToken: Optional[NextToken]


class ListDetectMitigationActionsExecutionsRequest(ServiceRequest):
    taskId: Optional[MitigationActionsTaskId]
    violationId: Optional[ViolationId]
    thingName: Optional[DeviceDefenderThingName]
    startTime: Optional[Timestamp]
    endTime: Optional[Timestamp]
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]


class ListDetectMitigationActionsExecutionsResponse(TypedDict, total=False):
    actionsExecutions: Optional[DetectMitigationActionExecutionList]
    nextToken: Optional[NextToken]


class ListDetectMitigationActionsTasksRequest(ServiceRequest):
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]
    startTime: Timestamp
    endTime: Timestamp


class ListDetectMitigationActionsTasksResponse(TypedDict, total=False):
    tasks: Optional[DetectMitigationActionsTaskSummaryList]
    nextToken: Optional[NextToken]


class ListDimensionsRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListDimensionsResponse(TypedDict, total=False):
    dimensionNames: Optional[DimensionNames]
    nextToken: Optional[NextToken]


class ListDomainConfigurationsRequest(ServiceRequest):
    marker: Optional[Marker]
    pageSize: Optional[PageSize]
    serviceType: Optional[ServiceType]


class ListDomainConfigurationsResponse(TypedDict, total=False):
    domainConfigurations: Optional[DomainConfigurations]
    nextMarker: Optional[Marker]


class ListFleetMetricsRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListFleetMetricsResponse(TypedDict, total=False):
    fleetMetrics: Optional[FleetMetricNameAndArnList]
    nextToken: Optional[NextToken]


class ListIndicesRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[QueryMaxResults]


class ListIndicesResponse(TypedDict, total=False):
    indexNames: Optional[IndexNamesList]
    nextToken: Optional[NextToken]


class ListJobExecutionsForJobRequest(ServiceRequest):
    jobId: JobId
    status: Optional[JobExecutionStatus]
    maxResults: Optional[LaserMaxResults]
    nextToken: Optional[NextToken]


class ListJobExecutionsForJobResponse(TypedDict, total=False):
    executionSummaries: Optional[JobExecutionSummaryForJobList]
    nextToken: Optional[NextToken]


class ListJobExecutionsForThingRequest(ServiceRequest):
    thingName: ThingName
    status: Optional[JobExecutionStatus]
    namespaceId: Optional[NamespaceId]
    maxResults: Optional[LaserMaxResults]
    nextToken: Optional[NextToken]
    jobId: Optional[JobId]


class ListJobExecutionsForThingResponse(TypedDict, total=False):
    executionSummaries: Optional[JobExecutionSummaryForThingList]
    nextToken: Optional[NextToken]


class ListJobTemplatesRequest(ServiceRequest):
    maxResults: Optional[LaserMaxResults]
    nextToken: Optional[NextToken]


class ListJobTemplatesResponse(TypedDict, total=False):
    jobTemplates: Optional[JobTemplateSummaryList]
    nextToken: Optional[NextToken]


class ListJobsRequest(ServiceRequest):
    status: Optional[JobStatus]
    targetSelection: Optional[TargetSelection]
    maxResults: Optional[LaserMaxResults]
    nextToken: Optional[NextToken]
    thingGroupName: Optional[ThingGroupName]
    thingGroupId: Optional[ThingGroupId]
    namespaceId: Optional[NamespaceId]


class ListJobsResponse(TypedDict, total=False):
    jobs: Optional[JobSummaryList]
    nextToken: Optional[NextToken]


class ListManagedJobTemplatesRequest(ServiceRequest):
    templateName: Optional[ManagedJobTemplateName]
    maxResults: Optional[LaserMaxResults]
    nextToken: Optional[NextToken]


class ManagedJobTemplateSummary(TypedDict, total=False):
    """An object that contains information about the managed template."""

    templateArn: Optional[JobTemplateArn]
    templateName: Optional[ManagedJobTemplateName]
    description: Optional[JobDescription]
    environments: Optional[Environments]
    templateVersion: Optional[ManagedTemplateVersion]


ManagedJobTemplatesSummaryList = List[ManagedJobTemplateSummary]


class ListManagedJobTemplatesResponse(TypedDict, total=False):
    managedJobTemplates: Optional[ManagedJobTemplatesSummaryList]
    nextToken: Optional[NextToken]


class ListMetricValuesRequest(ServiceRequest):
    thingName: DeviceDefenderThingName
    metricName: BehaviorMetric
    dimensionName: Optional[DimensionName]
    dimensionValueOperator: Optional[DimensionValueOperator]
    startTime: Timestamp
    endTime: Timestamp
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]


class MetricDatum(TypedDict, total=False):
    """A metric."""

    timestamp: Optional[Timestamp]
    value: Optional[MetricValue]


MetricDatumList = List[MetricDatum]


class ListMetricValuesResponse(TypedDict, total=False):
    metricDatumList: Optional[MetricDatumList]
    nextToken: Optional[NextToken]


class ListMitigationActionsRequest(ServiceRequest):
    actionType: Optional[MitigationActionType]
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]


class MitigationActionIdentifier(TypedDict, total=False):
    """Information that identifies a mitigation action. This information is
    returned by ListMitigationActions.
    """

    actionName: Optional[MitigationActionName]
    actionArn: Optional[MitigationActionArn]
    creationDate: Optional[Timestamp]


MitigationActionIdentifierList = List[MitigationActionIdentifier]


class ListMitigationActionsResponse(TypedDict, total=False):
    actionIdentifiers: Optional[MitigationActionIdentifierList]
    nextToken: Optional[NextToken]


class ListOTAUpdatesRequest(ServiceRequest):
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]
    otaUpdateStatus: Optional[OTAUpdateStatus]


class OTAUpdateSummary(TypedDict, total=False):
    """An OTA update summary."""

    otaUpdateId: Optional[OTAUpdateId]
    otaUpdateArn: Optional[OTAUpdateArn]
    creationDate: Optional[DateType]


OTAUpdatesSummary = List[OTAUpdateSummary]


class ListOTAUpdatesResponse(TypedDict, total=False):
    otaUpdates: Optional[OTAUpdatesSummary]
    nextToken: Optional[NextToken]


class ListOutgoingCertificatesRequest(ServiceRequest):
    """The input to the ListOutgoingCertificates operation."""

    pageSize: Optional[PageSize]
    marker: Optional[Marker]
    ascendingOrder: Optional[AscendingOrder]


class OutgoingCertificate(TypedDict, total=False):
    """A certificate that has been transferred but not yet accepted."""

    certificateArn: Optional[CertificateArn]
    certificateId: Optional[CertificateId]
    transferredTo: Optional[AwsAccountId]
    transferDate: Optional[DateType]
    transferMessage: Optional[Message]
    creationDate: Optional[DateType]


OutgoingCertificates = List[OutgoingCertificate]


class ListOutgoingCertificatesResponse(TypedDict, total=False):
    """The output from the ListOutgoingCertificates operation."""

    outgoingCertificates: Optional[OutgoingCertificates]
    nextMarker: Optional[Marker]


class ListPoliciesRequest(ServiceRequest):
    """The input for the ListPolicies operation."""

    marker: Optional[Marker]
    pageSize: Optional[PageSize]
    ascendingOrder: Optional[AscendingOrder]


class ListPoliciesResponse(TypedDict, total=False):
    """The output from the ListPolicies operation."""

    policies: Optional[Policies]
    nextMarker: Optional[Marker]


class ListPolicyPrincipalsRequest(ServiceRequest):
    """The input for the ListPolicyPrincipals operation."""

    policyName: PolicyName
    marker: Optional[Marker]
    pageSize: Optional[PageSize]
    ascendingOrder: Optional[AscendingOrder]


Principals = List[PrincipalArn]


class ListPolicyPrincipalsResponse(TypedDict, total=False):
    """The output from the ListPolicyPrincipals operation."""

    principals: Optional[Principals]
    nextMarker: Optional[Marker]


class ListPolicyVersionsRequest(ServiceRequest):
    """The input for the ListPolicyVersions operation."""

    policyName: PolicyName


class PolicyVersion(TypedDict, total=False):
    """Describes a policy version."""

    versionId: Optional[PolicyVersionId]
    isDefaultVersion: Optional[IsDefaultVersion]
    createDate: Optional[DateType]


PolicyVersions = List[PolicyVersion]


class ListPolicyVersionsResponse(TypedDict, total=False):
    """The output from the ListPolicyVersions operation."""

    policyVersions: Optional[PolicyVersions]


class ListPrincipalPoliciesRequest(ServiceRequest):
    """The input for the ListPrincipalPolicies operation."""

    principal: Principal
    marker: Optional[Marker]
    pageSize: Optional[PageSize]
    ascendingOrder: Optional[AscendingOrder]


class ListPrincipalPoliciesResponse(TypedDict, total=False):
    """The output from the ListPrincipalPolicies operation."""

    policies: Optional[Policies]
    nextMarker: Optional[Marker]


class ListPrincipalThingsRequest(ServiceRequest):
    """The input for the ListPrincipalThings operation."""

    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]
    principal: Principal


ThingNameList = List[ThingName]


class ListPrincipalThingsResponse(TypedDict, total=False):
    """The output from the ListPrincipalThings operation."""

    things: Optional[ThingNameList]
    nextToken: Optional[NextToken]


class ListProvisioningTemplateVersionsRequest(ServiceRequest):
    templateName: TemplateName
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]


class ProvisioningTemplateVersionSummary(TypedDict, total=False):
    """A summary of information about a fleet provision template version."""

    versionId: Optional[TemplateVersionId]
    creationDate: Optional[DateType]
    isDefaultVersion: Optional[IsDefaultVersion]


ProvisioningTemplateVersionListing = List[ProvisioningTemplateVersionSummary]


class ListProvisioningTemplateVersionsResponse(TypedDict, total=False):
    versions: Optional[ProvisioningTemplateVersionListing]
    nextToken: Optional[NextToken]


class ListProvisioningTemplatesRequest(ServiceRequest):
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]


class ProvisioningTemplateSummary(TypedDict, total=False):
    """A summary of information about a fleet provisioning template."""

    templateArn: Optional[TemplateArn]
    templateName: Optional[TemplateName]
    description: Optional[TemplateDescription]
    creationDate: Optional[DateType]
    lastModifiedDate: Optional[DateType]
    enabled: Optional[Enabled]


ProvisioningTemplateListing = List[ProvisioningTemplateSummary]


class ListProvisioningTemplatesResponse(TypedDict, total=False):
    templates: Optional[ProvisioningTemplateListing]
    nextToken: Optional[NextToken]


class ListRoleAliasesRequest(ServiceRequest):
    pageSize: Optional[PageSize]
    marker: Optional[Marker]
    ascendingOrder: Optional[AscendingOrder]


RoleAliases = List[RoleAlias]


class ListRoleAliasesResponse(TypedDict, total=False):
    roleAliases: Optional[RoleAliases]
    nextMarker: Optional[Marker]


class ListScheduledAuditsRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ScheduledAuditMetadata(TypedDict, total=False):
    """Information about the scheduled audit."""

    scheduledAuditName: Optional[ScheduledAuditName]
    scheduledAuditArn: Optional[ScheduledAuditArn]
    frequency: Optional[AuditFrequency]
    dayOfMonth: Optional[DayOfMonth]
    dayOfWeek: Optional[DayOfWeek]


ScheduledAuditMetadataList = List[ScheduledAuditMetadata]


class ListScheduledAuditsResponse(TypedDict, total=False):
    scheduledAudits: Optional[ScheduledAuditMetadataList]
    nextToken: Optional[NextToken]


class ListSecurityProfilesForTargetRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]
    recursive: Optional[Recursive]
    securityProfileTargetArn: SecurityProfileTargetArn


class SecurityProfileTarget(TypedDict, total=False):
    """A target to which an alert is sent when a security profile behavior is
    violated.
    """

    arn: SecurityProfileTargetArn


class SecurityProfileIdentifier(TypedDict, total=False):
    """Identifying information for a Device Defender security profile."""

    name: SecurityProfileName
    arn: SecurityProfileArn


class SecurityProfileTargetMapping(TypedDict, total=False):
    """Information about a security profile and the target associated with it."""

    securityProfileIdentifier: Optional[SecurityProfileIdentifier]
    target: Optional[SecurityProfileTarget]


SecurityProfileTargetMappings = List[SecurityProfileTargetMapping]


class ListSecurityProfilesForTargetResponse(TypedDict, total=False):
    securityProfileTargetMappings: Optional[SecurityProfileTargetMappings]
    nextToken: Optional[NextToken]


class ListSecurityProfilesRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]
    dimensionName: Optional[DimensionName]
    metricName: Optional[MetricName]


SecurityProfileIdentifiers = List[SecurityProfileIdentifier]


class ListSecurityProfilesResponse(TypedDict, total=False):
    securityProfileIdentifiers: Optional[SecurityProfileIdentifiers]
    nextToken: Optional[NextToken]


class ListStreamsRequest(ServiceRequest):
    maxResults: Optional[MaxResults]
    nextToken: Optional[NextToken]
    ascendingOrder: Optional[AscendingOrder]


class StreamSummary(TypedDict, total=False):
    """A summary of a stream."""

    streamId: Optional[StreamId]
    streamArn: Optional[StreamArn]
    streamVersion: Optional[StreamVersion]
    description: Optional[StreamDescription]


StreamsSummary = List[StreamSummary]


class ListStreamsResponse(TypedDict, total=False):
    streams: Optional[StreamsSummary]
    nextToken: Optional[NextToken]


class ListTagsForResourceRequest(ServiceRequest):
    resourceArn: ResourceArn
    nextToken: Optional[NextToken]


class ListTagsForResourceResponse(TypedDict, total=False):
    tags: Optional[TagList]
    nextToken: Optional[NextToken]


class ListTargetsForPolicyRequest(ServiceRequest):
    policyName: PolicyName
    marker: Optional[Marker]
    pageSize: Optional[PageSize]


PolicyTargets = List[PolicyTarget]


class ListTargetsForPolicyResponse(TypedDict, total=False):
    targets: Optional[PolicyTargets]
    nextMarker: Optional[Marker]


class ListTargetsForSecurityProfileRequest(ServiceRequest):
    securityProfileName: SecurityProfileName
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


SecurityProfileTargets = List[SecurityProfileTarget]


class ListTargetsForSecurityProfileResponse(TypedDict, total=False):
    securityProfileTargets: Optional[SecurityProfileTargets]
    nextToken: Optional[NextToken]


class ListThingGroupsForThingRequest(ServiceRequest):
    thingName: ThingName
    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]


class ListThingGroupsForThingResponse(TypedDict, total=False):
    thingGroups: Optional[ThingGroupNameAndArnList]
    nextToken: Optional[NextToken]


class ListThingGroupsRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]
    parentGroup: Optional[ThingGroupName]
    namePrefixFilter: Optional[ThingGroupName]
    recursive: Optional[RecursiveWithoutDefault]


class ListThingGroupsResponse(TypedDict, total=False):
    thingGroups: Optional[ThingGroupNameAndArnList]
    nextToken: Optional[NextToken]


class ListThingPrincipalsRequest(ServiceRequest):
    """The input for the ListThingPrincipal operation."""

    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]
    thingName: ThingName


class ListThingPrincipalsResponse(TypedDict, total=False):
    """The output from the ListThingPrincipals operation."""

    principals: Optional[Principals]
    nextToken: Optional[NextToken]


class ListThingRegistrationTaskReportsRequest(ServiceRequest):
    taskId: TaskId
    reportType: ReportType
    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]


S3FileUrlList = List[S3FileUrl]


class ListThingRegistrationTaskReportsResponse(TypedDict, total=False):
    resourceLinks: Optional[S3FileUrlList]
    reportType: Optional[ReportType]
    nextToken: Optional[NextToken]


class ListThingRegistrationTasksRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]
    status: Optional[Status]


TaskIdList = List[TaskId]


class ListThingRegistrationTasksResponse(TypedDict, total=False):
    taskIds: Optional[TaskIdList]
    nextToken: Optional[NextToken]


class ListThingTypesRequest(ServiceRequest):
    """The input for the ListThingTypes operation."""

    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]
    thingTypeName: Optional[ThingTypeName]


class ThingTypeDefinition(TypedDict, total=False):
    """The definition of the thing type, including thing type name and
    description.
    """

    thingTypeName: Optional[ThingTypeName]
    thingTypeArn: Optional[ThingTypeArn]
    thingTypeProperties: Optional[ThingTypeProperties]
    thingTypeMetadata: Optional[ThingTypeMetadata]


ThingTypeList = List[ThingTypeDefinition]


class ListThingTypesResponse(TypedDict, total=False):
    """The output for the ListThingTypes operation."""

    thingTypes: Optional[ThingTypeList]
    nextToken: Optional[NextToken]


class ListThingsInBillingGroupRequest(ServiceRequest):
    billingGroupName: BillingGroupName
    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]


class ListThingsInBillingGroupResponse(TypedDict, total=False):
    things: Optional[ThingNameList]
    nextToken: Optional[NextToken]


class ListThingsInThingGroupRequest(ServiceRequest):
    thingGroupName: ThingGroupName
    recursive: Optional[Recursive]
    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]


class ListThingsInThingGroupResponse(TypedDict, total=False):
    things: Optional[ThingNameList]
    nextToken: Optional[NextToken]


class ListThingsRequest(ServiceRequest):
    """The input for the ListThings operation."""

    nextToken: Optional[NextToken]
    maxResults: Optional[RegistryMaxResults]
    attributeName: Optional[AttributeName]
    attributeValue: Optional[AttributeValue]
    thingTypeName: Optional[ThingTypeName]
    usePrefixAttributeValue: Optional[usePrefixAttributeValue]


class ThingAttribute(TypedDict, total=False):
    """The properties of the thing, including thing name, thing type name, and
    a list of thing attributes.
    """

    thingName: Optional[ThingName]
    thingTypeName: Optional[ThingTypeName]
    thingArn: Optional[ThingArn]
    attributes: Optional[Attributes]
    version: Optional[Version]


ThingAttributeList = List[ThingAttribute]


class ListThingsResponse(TypedDict, total=False):
    """The output from the ListThings operation."""

    things: Optional[ThingAttributeList]
    nextToken: Optional[NextToken]


class ListTopicRuleDestinationsRequest(ServiceRequest):
    maxResults: Optional[TopicRuleDestinationMaxResults]
    nextToken: Optional[NextToken]


class VpcDestinationSummary(TypedDict, total=False):
    """The summary of a virtual private cloud (VPC) destination."""

    subnetIds: Optional[SubnetIdList]
    securityGroups: Optional[SecurityGroupList]
    vpcId: Optional[VpcId]
    roleArn: Optional[AwsArn]


class TopicRuleDestinationSummary(TypedDict, total=False):
    """Information about the topic rule destination."""

    arn: Optional[AwsArn]
    status: Optional[TopicRuleDestinationStatus]
    createdAt: Optional[CreatedAtDate]
    lastUpdatedAt: Optional[LastUpdatedAtDate]
    statusReason: Optional[String]
    httpUrlSummary: Optional[HttpUrlDestinationSummary]
    vpcDestinationSummary: Optional[VpcDestinationSummary]


TopicRuleDestinationSummaries = List[TopicRuleDestinationSummary]


class ListTopicRuleDestinationsResponse(TypedDict, total=False):
    destinationSummaries: Optional[TopicRuleDestinationSummaries]
    nextToken: Optional[NextToken]


class ListTopicRulesRequest(ServiceRequest):
    """The input for the ListTopicRules operation."""

    topic: Optional[Topic]
    maxResults: Optional[TopicRuleMaxResults]
    nextToken: Optional[NextToken]
    ruleDisabled: Optional[IsDisabled]


class TopicRuleListItem(TypedDict, total=False):
    """Describes a rule."""

    ruleArn: Optional[RuleArn]
    ruleName: Optional[RuleName]
    topicPattern: Optional[TopicPattern]
    createdAt: Optional[CreatedAtDate]
    ruleDisabled: Optional[IsDisabled]


TopicRuleList = List[TopicRuleListItem]


class ListTopicRulesResponse(TypedDict, total=False):
    """The output from the ListTopicRules operation."""

    rules: Optional[TopicRuleList]
    nextToken: Optional[NextToken]


class ListV2LoggingLevelsRequest(ServiceRequest):
    targetType: Optional[LogTargetType]
    nextToken: Optional[NextToken]
    maxResults: Optional[SkyfallMaxResults]


class LogTarget(TypedDict, total=False):
    """A log target."""

    targetType: LogTargetType
    targetName: Optional[LogTargetName]


class LogTargetConfiguration(TypedDict, total=False):
    """The target configuration."""

    logTarget: Optional[LogTarget]
    logLevel: Optional[LogLevel]


LogTargetConfigurations = List[LogTargetConfiguration]


class ListV2LoggingLevelsResponse(TypedDict, total=False):
    logTargetConfigurations: Optional[LogTargetConfigurations]
    nextToken: Optional[NextToken]


class ListViolationEventsRequest(ServiceRequest):
    startTime: Timestamp
    endTime: Timestamp
    thingName: Optional[DeviceDefenderThingName]
    securityProfileName: Optional[SecurityProfileName]
    behaviorCriteriaType: Optional[BehaviorCriteriaType]
    listSuppressedAlerts: Optional[ListSuppressedAlerts]
    verificationState: Optional[VerificationState]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ViolationEvent(TypedDict, total=False):
    """Information about a Device Defender security profile behavior violation."""

    violationId: Optional[ViolationId]
    thingName: Optional[DeviceDefenderThingName]
    securityProfileName: Optional[SecurityProfileName]
    behavior: Optional[Behavior]
    metricValue: Optional[MetricValue]
    violationEventAdditionalInfo: Optional[ViolationEventAdditionalInfo]
    violationEventType: Optional[ViolationEventType]
    verificationState: Optional[VerificationState]
    verificationStateDescription: Optional[VerificationStateDescription]
    violationEventTime: Optional[Timestamp]


ViolationEvents = List[ViolationEvent]


class ListViolationEventsResponse(TypedDict, total=False):
    violationEvents: Optional[ViolationEvents]
    nextToken: Optional[NextToken]


class LoggingOptionsPayload(TypedDict, total=False):
    """Describes the logging options payload."""

    roleArn: AwsArn
    logLevel: Optional[LogLevel]


MqttPassword = bytes


class MqttContext(TypedDict, total=False):
    """Specifies the MQTT context to use for the test authorizer request"""

    username: Optional[MqttUsername]
    password: Optional[MqttPassword]
    clientId: Optional[MqttClientId]


Parameters = Dict[Parameter, Value]
PolicyDocuments = List[PolicyDocument]
PolicyNames = List[PolicyName]


class PutVerificationStateOnViolationRequest(ServiceRequest):
    violationId: ViolationId
    verificationState: VerificationState
    verificationStateDescription: Optional[VerificationStateDescription]


class PutVerificationStateOnViolationResponse(TypedDict, total=False):
    pass


class RegisterCACertificateRequest(ServiceRequest):
    """The input to the RegisterCACertificate operation."""

    caCertificate: CertificatePem
    verificationCertificate: CertificatePem
    setAsActive: Optional[SetAsActive]
    allowAutoRegistration: Optional[AllowAutoRegistration]
    registrationConfig: Optional[RegistrationConfig]
    tags: Optional[TagList]


class RegisterCACertificateResponse(TypedDict, total=False):
    """The output from the RegisterCACertificateResponse operation."""

    certificateArn: Optional[CertificateArn]
    certificateId: Optional[CertificateId]


class RegisterCertificateRequest(ServiceRequest):
    """The input to the RegisterCertificate operation."""

    certificatePem: CertificatePem
    caCertificatePem: Optional[CertificatePem]
    setAsActive: Optional[SetAsActiveFlag]
    status: Optional[CertificateStatus]


class RegisterCertificateResponse(TypedDict, total=False):
    """The output from the RegisterCertificate operation."""

    certificateArn: Optional[CertificateArn]
    certificateId: Optional[CertificateId]


class RegisterCertificateWithoutCARequest(ServiceRequest):
    certificatePem: CertificatePem
    status: Optional[CertificateStatus]


class RegisterCertificateWithoutCAResponse(TypedDict, total=False):
    certificateArn: Optional[CertificateArn]
    certificateId: Optional[CertificateId]


class RegisterThingRequest(ServiceRequest):
    templateBody: TemplateBody
    parameters: Optional[Parameters]


ResourceArns = Dict[ResourceLogicalId, ResourceArn]


class RegisterThingResponse(TypedDict, total=False):
    certificatePem: Optional[CertificatePem]
    resourceArns: Optional[ResourceArns]


class RejectCertificateTransferRequest(ServiceRequest):
    """The input for the RejectCertificateTransfer operation."""

    certificateId: CertificateId
    rejectReason: Optional[Message]


class RemoveThingFromBillingGroupRequest(ServiceRequest):
    billingGroupName: Optional[BillingGroupName]
    billingGroupArn: Optional[BillingGroupArn]
    thingName: Optional[ThingName]
    thingArn: Optional[ThingArn]


class RemoveThingFromBillingGroupResponse(TypedDict, total=False):
    pass


class RemoveThingFromThingGroupRequest(ServiceRequest):
    thingGroupName: Optional[ThingGroupName]
    thingGroupArn: Optional[ThingGroupArn]
    thingName: Optional[ThingName]
    thingArn: Optional[ThingArn]


class RemoveThingFromThingGroupResponse(TypedDict, total=False):
    pass


class ReplaceTopicRuleRequest(ServiceRequest):
    """The input for the ReplaceTopicRule operation."""

    ruleName: RuleName
    topicRulePayload: TopicRulePayload


class SearchIndexRequest(ServiceRequest):
    indexName: Optional[IndexName]
    queryString: QueryString
    nextToken: Optional[NextToken]
    maxResults: Optional[QueryMaxResults]
    queryVersion: Optional[QueryVersion]


ThingGroupNameList = List[ThingGroupName]


class ThingGroupDocument(TypedDict, total=False):
    """The thing group search index document."""

    thingGroupName: Optional[ThingGroupName]
    thingGroupId: Optional[ThingGroupId]
    thingGroupDescription: Optional[ThingGroupDescription]
    attributes: Optional[Attributes]
    parentGroupNames: Optional[ThingGroupNameList]


ThingGroupDocumentList = List[ThingGroupDocument]


class ThingConnectivity(TypedDict, total=False):
    """The connectivity status of the thing."""

    connected: Optional[Boolean]
    timestamp: Optional[ConnectivityTimestamp]
    disconnectReason: Optional[DisconnectReason]


class ThingDocument(TypedDict, total=False):
    """The thing search index document."""

    thingName: Optional[ThingName]
    thingId: Optional[ThingId]
    thingTypeName: Optional[ThingTypeName]
    thingGroupNames: Optional[ThingGroupNameList]
    attributes: Optional[Attributes]
    shadow: Optional[JsonDocument]
    deviceDefender: Optional[JsonDocument]
    connectivity: Optional[ThingConnectivity]


ThingDocumentList = List[ThingDocument]


class SearchIndexResponse(TypedDict, total=False):
    nextToken: Optional[NextToken]
    things: Optional[ThingDocumentList]
    thingGroups: Optional[ThingGroupDocumentList]


class SetDefaultAuthorizerRequest(ServiceRequest):
    authorizerName: AuthorizerName


class SetDefaultAuthorizerResponse(TypedDict, total=False):
    authorizerName: Optional[AuthorizerName]
    authorizerArn: Optional[AuthorizerArn]


class SetDefaultPolicyVersionRequest(ServiceRequest):
    """The input for the SetDefaultPolicyVersion operation."""

    policyName: PolicyName
    policyVersionId: PolicyVersionId


class SetLoggingOptionsRequest(ServiceRequest):
    """The input for the SetLoggingOptions operation."""

    loggingOptionsPayload: LoggingOptionsPayload


class SetV2LoggingLevelRequest(ServiceRequest):
    logTarget: LogTarget
    logLevel: LogLevel


class SetV2LoggingOptionsRequest(ServiceRequest):
    roleArn: Optional[AwsArn]
    defaultLogLevel: Optional[LogLevel]
    disableAllLogs: Optional[DisableAllLogs]


class StartAuditMitigationActionsTaskRequest(ServiceRequest):
    taskId: MitigationActionsTaskId
    target: AuditMitigationActionsTaskTarget
    auditCheckToActionsMapping: AuditCheckToActionsMapping
    clientRequestToken: ClientRequestToken


class StartAuditMitigationActionsTaskResponse(TypedDict, total=False):
    taskId: Optional[MitigationActionsTaskId]


class StartDetectMitigationActionsTaskRequest(ServiceRequest):
    taskId: MitigationActionsTaskId
    target: DetectMitigationActionsTaskTarget
    actions: DetectMitigationActionsToExecuteList
    violationEventOccurrenceRange: Optional[ViolationEventOccurrenceRange]
    includeOnlyActiveViolations: Optional[NullableBoolean]
    includeSuppressedAlerts: Optional[NullableBoolean]
    clientRequestToken: ClientRequestToken


class StartDetectMitigationActionsTaskResponse(TypedDict, total=False):
    taskId: Optional[MitigationActionsTaskId]


class StartOnDemandAuditTaskRequest(ServiceRequest):
    targetCheckNames: TargetAuditCheckNames


class StartOnDemandAuditTaskResponse(TypedDict, total=False):
    taskId: Optional[AuditTaskId]


class StartThingRegistrationTaskRequest(ServiceRequest):
    templateBody: TemplateBody
    inputFileBucket: RegistryS3BucketName
    inputFileKey: RegistryS3KeyName
    roleArn: RoleArn


class StartThingRegistrationTaskResponse(TypedDict, total=False):
    taskId: Optional[TaskId]


class StopThingRegistrationTaskRequest(ServiceRequest):
    taskId: TaskId


class StopThingRegistrationTaskResponse(TypedDict, total=False):
    pass


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    resourceArn: ResourceArn
    tags: TagList


class TagResourceResponse(TypedDict, total=False):
    pass


class TestAuthorizationRequest(ServiceRequest):
    principal: Optional[Principal]
    cognitoIdentityPoolId: Optional[CognitoIdentityPoolId]
    authInfos: AuthInfos
    clientId: Optional[ClientId]
    policyNamesToAdd: Optional[PolicyNames]
    policyNamesToSkip: Optional[PolicyNames]


class TestAuthorizationResponse(TypedDict, total=False):
    authResults: Optional[AuthResults]


class TlsContext(TypedDict, total=False):
    """Specifies the TLS context to use for the test authorizer request."""

    serverName: Optional[ServerName]


class TestInvokeAuthorizerRequest(ServiceRequest):
    authorizerName: AuthorizerName
    token: Optional[Token]
    tokenSignature: Optional[TokenSignature]
    httpContext: Optional[HttpContext]
    mqttContext: Optional[MqttContext]
    tlsContext: Optional[TlsContext]


class TestInvokeAuthorizerResponse(TypedDict, total=False):
    isAuthenticated: Optional[IsAuthenticated]
    principalId: Optional[PrincipalId]
    policyDocuments: Optional[PolicyDocuments]
    refreshAfterInSeconds: Optional[Seconds]
    disconnectAfterInSeconds: Optional[Seconds]


ThingGroupList = List[ThingGroupName]


class TransferCertificateRequest(ServiceRequest):
    """The input for the TransferCertificate operation."""

    certificateId: CertificateId
    targetAwsAccount: AwsAccountId
    transferMessage: Optional[Message]


class TransferCertificateResponse(TypedDict, total=False):
    """The output from the TransferCertificate operation."""

    transferredCertificateArn: Optional[CertificateArn]


class UntagResourceRequest(ServiceRequest):
    resourceArn: ResourceArn
    tagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateAccountAuditConfigurationRequest(ServiceRequest):
    roleArn: Optional[RoleArn]
    auditNotificationTargetConfigurations: Optional[AuditNotificationTargetConfigurations]
    auditCheckConfigurations: Optional[AuditCheckConfigurations]


class UpdateAccountAuditConfigurationResponse(TypedDict, total=False):
    pass


class UpdateAuditSuppressionRequest(ServiceRequest):
    checkName: AuditCheckName
    resourceIdentifier: ResourceIdentifier
    expirationDate: Optional[Timestamp]
    suppressIndefinitely: Optional[SuppressIndefinitely]
    description: Optional[AuditDescription]


class UpdateAuditSuppressionResponse(TypedDict, total=False):
    pass


class UpdateAuthorizerRequest(ServiceRequest):
    authorizerName: AuthorizerName
    authorizerFunctionArn: Optional[AuthorizerFunctionArn]
    tokenKeyName: Optional[TokenKeyName]
    tokenSigningPublicKeys: Optional[PublicKeyMap]
    status: Optional[AuthorizerStatus]
    enableCachingForHttp: Optional[EnableCachingForHttp]


class UpdateAuthorizerResponse(TypedDict, total=False):
    authorizerName: Optional[AuthorizerName]
    authorizerArn: Optional[AuthorizerArn]


class UpdateBillingGroupRequest(ServiceRequest):
    billingGroupName: BillingGroupName
    billingGroupProperties: BillingGroupProperties
    expectedVersion: Optional[OptionalVersion]


class UpdateBillingGroupResponse(TypedDict, total=False):
    version: Optional[Version]


class UpdateCACertificateRequest(ServiceRequest):
    """The input to the UpdateCACertificate operation."""

    certificateId: CertificateId
    newStatus: Optional[CACertificateStatus]
    newAutoRegistrationStatus: Optional[AutoRegistrationStatus]
    registrationConfig: Optional[RegistrationConfig]
    removeAutoRegistration: Optional[RemoveAutoRegistration]


class UpdateCertificateRequest(ServiceRequest):
    """The input for the UpdateCertificate operation."""

    certificateId: CertificateId
    newStatus: CertificateStatus


class UpdateCustomMetricRequest(ServiceRequest):
    metricName: MetricName
    displayName: CustomMetricDisplayName


class UpdateCustomMetricResponse(TypedDict, total=False):
    metricName: Optional[MetricName]
    metricArn: Optional[CustomMetricArn]
    metricType: Optional[CustomMetricType]
    displayName: Optional[CustomMetricDisplayName]
    creationDate: Optional[Timestamp]
    lastModifiedDate: Optional[Timestamp]


class UpdateDimensionRequest(ServiceRequest):
    name: DimensionName
    stringValues: DimensionStringValues


UpdateDimensionResponse = TypedDict(
    "UpdateDimensionResponse",
    {
        "name": Optional[DimensionName],
        "arn": Optional[DimensionArn],
        "type": Optional[DimensionType],
        "stringValues": Optional[DimensionStringValues],
        "creationDate": Optional[Timestamp],
        "lastModifiedDate": Optional[Timestamp],
    },
    total=False,
)


class UpdateDomainConfigurationRequest(ServiceRequest):
    domainConfigurationName: ReservedDomainConfigurationName
    authorizerConfig: Optional[AuthorizerConfig]
    domainConfigurationStatus: Optional[DomainConfigurationStatus]
    removeAuthorizerConfig: Optional[RemoveAuthorizerConfig]


class UpdateDomainConfigurationResponse(TypedDict, total=False):
    domainConfigurationName: Optional[ReservedDomainConfigurationName]
    domainConfigurationArn: Optional[DomainConfigurationArn]


class UpdateDynamicThingGroupRequest(ServiceRequest):
    thingGroupName: ThingGroupName
    thingGroupProperties: ThingGroupProperties
    expectedVersion: Optional[OptionalVersion]
    indexName: Optional[IndexName]
    queryString: Optional[QueryString]
    queryVersion: Optional[QueryVersion]


class UpdateDynamicThingGroupResponse(TypedDict, total=False):
    version: Optional[Version]


class UpdateEventConfigurationsRequest(ServiceRequest):
    eventConfigurations: Optional[EventConfigurations]


class UpdateEventConfigurationsResponse(TypedDict, total=False):
    pass


class UpdateFleetMetricRequest(ServiceRequest):
    metricName: FleetMetricName
    queryString: Optional[QueryString]
    aggregationType: Optional[AggregationType]
    period: Optional[FleetMetricPeriod]
    aggregationField: Optional[AggregationField]
    description: Optional[FleetMetricDescription]
    queryVersion: Optional[QueryVersion]
    indexName: IndexName
    unit: Optional[FleetMetricUnit]
    expectedVersion: Optional[OptionalVersion]


class UpdateIndexingConfigurationRequest(ServiceRequest):
    thingIndexingConfiguration: Optional[ThingIndexingConfiguration]
    thingGroupIndexingConfiguration: Optional[ThingGroupIndexingConfiguration]


class UpdateIndexingConfigurationResponse(TypedDict, total=False):
    pass


class UpdateJobRequest(ServiceRequest):
    jobId: JobId
    description: Optional[JobDescription]
    presignedUrlConfig: Optional[PresignedUrlConfig]
    jobExecutionsRolloutConfig: Optional[JobExecutionsRolloutConfig]
    abortConfig: Optional[AbortConfig]
    timeoutConfig: Optional[TimeoutConfig]
    namespaceId: Optional[NamespaceId]
    jobExecutionsRetryConfig: Optional[JobExecutionsRetryConfig]


class UpdateMitigationActionRequest(ServiceRequest):
    actionName: MitigationActionName
    roleArn: Optional[RoleArn]
    actionParams: Optional[MitigationActionParams]


class UpdateMitigationActionResponse(TypedDict, total=False):
    actionArn: Optional[MitigationActionArn]
    actionId: Optional[MitigationActionId]


class UpdateProvisioningTemplateRequest(ServiceRequest):
    templateName: TemplateName
    description: Optional[TemplateDescription]
    enabled: Optional[Enabled]
    defaultVersionId: Optional[TemplateVersionId]
    provisioningRoleArn: Optional[RoleArn]
    preProvisioningHook: Optional[ProvisioningHook]
    removePreProvisioningHook: Optional[RemoveHook]


class UpdateProvisioningTemplateResponse(TypedDict, total=False):
    pass


class UpdateRoleAliasRequest(ServiceRequest):
    roleAlias: RoleAlias
    roleArn: Optional[RoleArn]
    credentialDurationSeconds: Optional[CredentialDurationSeconds]


class UpdateRoleAliasResponse(TypedDict, total=False):
    roleAlias: Optional[RoleAlias]
    roleAliasArn: Optional[RoleAliasArn]


class UpdateScheduledAuditRequest(ServiceRequest):
    frequency: Optional[AuditFrequency]
    dayOfMonth: Optional[DayOfMonth]
    dayOfWeek: Optional[DayOfWeek]
    targetCheckNames: Optional[TargetAuditCheckNames]
    scheduledAuditName: ScheduledAuditName


class UpdateScheduledAuditResponse(TypedDict, total=False):
    scheduledAuditArn: Optional[ScheduledAuditArn]


class UpdateSecurityProfileRequest(ServiceRequest):
    securityProfileName: SecurityProfileName
    securityProfileDescription: Optional[SecurityProfileDescription]
    behaviors: Optional[Behaviors]
    alertTargets: Optional[AlertTargets]
    additionalMetricsToRetain: Optional[AdditionalMetricsToRetainList]
    additionalMetricsToRetainV2: Optional[AdditionalMetricsToRetainV2List]
    deleteBehaviors: Optional[DeleteBehaviors]
    deleteAlertTargets: Optional[DeleteAlertTargets]
    deleteAdditionalMetricsToRetain: Optional[DeleteAdditionalMetricsToRetain]
    expectedVersion: Optional[OptionalVersion]


class UpdateSecurityProfileResponse(TypedDict, total=False):
    securityProfileName: Optional[SecurityProfileName]
    securityProfileArn: Optional[SecurityProfileArn]
    securityProfileDescription: Optional[SecurityProfileDescription]
    behaviors: Optional[Behaviors]
    alertTargets: Optional[AlertTargets]
    additionalMetricsToRetain: Optional[AdditionalMetricsToRetainList]
    additionalMetricsToRetainV2: Optional[AdditionalMetricsToRetainV2List]
    version: Optional[Version]
    creationDate: Optional[Timestamp]
    lastModifiedDate: Optional[Timestamp]


class UpdateStreamRequest(ServiceRequest):
    streamId: StreamId
    description: Optional[StreamDescription]
    files: Optional[StreamFiles]
    roleArn: Optional[RoleArn]


class UpdateStreamResponse(TypedDict, total=False):
    streamId: Optional[StreamId]
    streamArn: Optional[StreamArn]
    description: Optional[StreamDescription]
    streamVersion: Optional[StreamVersion]


class UpdateThingGroupRequest(ServiceRequest):
    thingGroupName: ThingGroupName
    thingGroupProperties: ThingGroupProperties
    expectedVersion: Optional[OptionalVersion]


class UpdateThingGroupResponse(TypedDict, total=False):
    version: Optional[Version]


class UpdateThingGroupsForThingRequest(ServiceRequest):
    thingName: Optional[ThingName]
    thingGroupsToAdd: Optional[ThingGroupList]
    thingGroupsToRemove: Optional[ThingGroupList]
    overrideDynamicGroups: Optional[OverrideDynamicGroups]


class UpdateThingGroupsForThingResponse(TypedDict, total=False):
    pass


class UpdateThingRequest(ServiceRequest):
    """The input for the UpdateThing operation."""

    thingName: ThingName
    thingTypeName: Optional[ThingTypeName]
    attributePayload: Optional[AttributePayload]
    expectedVersion: Optional[OptionalVersion]
    removeThingType: Optional[RemoveThingType]


class UpdateThingResponse(TypedDict, total=False):
    """The output from the UpdateThing operation."""


class UpdateTopicRuleDestinationRequest(ServiceRequest):
    arn: AwsArn
    status: TopicRuleDestinationStatus


class UpdateTopicRuleDestinationResponse(TypedDict, total=False):
    pass


class ValidateSecurityProfileBehaviorsRequest(ServiceRequest):
    behaviors: Behaviors


class ValidationError(TypedDict, total=False):
    """Information about an error found in a behavior specification."""

    errorMessage: Optional[ErrorMessage]


ValidationErrors = List[ValidationError]


class ValidateSecurityProfileBehaviorsResponse(TypedDict, total=False):
    valid: Optional[Valid]
    validationErrors: Optional[ValidationErrors]


class IotApi:

    service = "iot"
    version = "2015-05-28"

    @handler("AcceptCertificateTransfer")
    def accept_certificate_transfer(
        self,
        context: RequestContext,
        certificate_id: CertificateId,
        set_as_active: SetAsActive = None,
    ) -> None:
        """Accepts a pending certificate transfer. The default state of the
        certificate is INACTIVE.

        To check for pending certificate transfers, call ListCertificates to
        enumerate your certificates.

        Requires permission to access the
        `AcceptCertificateTransfer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param certificate_id: The ID of the certificate.
        :param set_as_active: Specifies whether the certificate is active.
        :raises ResourceNotFoundException:
        :raises TransferAlreadyCompletedException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("AddThingToBillingGroup")
    def add_thing_to_billing_group(
        self,
        context: RequestContext,
        billing_group_name: BillingGroupName = None,
        billing_group_arn: BillingGroupArn = None,
        thing_name: ThingName = None,
        thing_arn: ThingArn = None,
    ) -> AddThingToBillingGroupResponse:
        """Adds a thing to a billing group.

        Requires permission to access the
        `AddThingToBillingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param billing_group_name: The name of the billing group.
        :param billing_group_arn: The ARN of the billing group.
        :param thing_name: The name of the thing to be added to the billing group.
        :param thing_arn: The ARN of the thing to be added to the billing group.
        :returns: AddThingToBillingGroupResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("AddThingToThingGroup")
    def add_thing_to_thing_group(
        self,
        context: RequestContext,
        thing_group_name: ThingGroupName = None,
        thing_group_arn: ThingGroupArn = None,
        thing_name: ThingName = None,
        thing_arn: ThingArn = None,
        override_dynamic_groups: OverrideDynamicGroups = None,
    ) -> AddThingToThingGroupResponse:
        """Adds a thing to a thing group.

        Requires permission to access the
        `AddThingToThingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_group_name: The name of the group to which you are adding a thing.
        :param thing_group_arn: The ARN of the group to which you are adding a thing.
        :param thing_name: The name of the thing to add to a group.
        :param thing_arn: The ARN of the thing to add to a group.
        :param override_dynamic_groups: Override dynamic thing groups with static thing groups when 10-group
        limit is reached.
        :returns: AddThingToThingGroupResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("AssociateTargetsWithJob")
    def associate_targets_with_job(
        self,
        context: RequestContext,
        targets: JobTargets,
        job_id: JobId,
        comment: Comment = None,
        namespace_id: NamespaceId = None,
    ) -> AssociateTargetsWithJobResponse:
        """Associates a group with a continuous job. The following criteria must be
        met:

        -  The job must have been created with the ``targetSelection`` field set
           to "CONTINUOUS".

        -  The job status must currently be "IN_PROGRESS".

        -  The total number of targets associated with a job must not exceed
           100.

        Requires permission to access the
        `AssociateTargetsWithJob <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param targets: A list of thing group ARNs that define the targets of the job.
        :param job_id: The unique identifier you assigned to this job when it was created.
        :param comment: An optional comment string describing why the job was associated with
        the targets.
        :param namespace_id: The namespace used to indicate that a job is a customer-managed job.
        :returns: AssociateTargetsWithJobResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("AttachPolicy")
    def attach_policy(
        self, context: RequestContext, policy_name: PolicyName, target: PolicyTarget
    ) -> None:
        """Attaches the specified policy to the specified principal (certificate or
        other credential).

        Requires permission to access the
        `AttachPolicy <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The name of the policy to attach.
        :param target: The
        `identity <https://docs.
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("AttachPrincipalPolicy")
    def attach_principal_policy(
        self, context: RequestContext, policy_name: PolicyName, principal: Principal
    ) -> None:
        """Attaches the specified policy to the specified principal (certificate or
        other credential).

        **Note:** This action is deprecated. Please use AttachPolicy instead.

        Requires permission to access the
        `AttachPrincipalPolicy <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The policy name.
        :param principal: The principal, which can be a certificate ARN (as returned from the
        CreateCertificate operation) or an Amazon Cognito ID.
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("AttachSecurityProfile")
    def attach_security_profile(
        self,
        context: RequestContext,
        security_profile_name: SecurityProfileName,
        security_profile_target_arn: SecurityProfileTargetArn,
    ) -> AttachSecurityProfileResponse:
        """Associates a Device Defender security profile with a thing group or this
        account. Each thing group or account can have up to five security
        profiles associated with it.

        Requires permission to access the
        `AttachSecurityProfile <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param security_profile_name: The security profile that is attached.
        :param security_profile_target_arn: The ARN of the target (thing group) to which the security profile is
        attached.
        :returns: AttachSecurityProfileResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises LimitExceededException:
        :raises VersionConflictException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("AttachThingPrincipal")
    def attach_thing_principal(
        self, context: RequestContext, thing_name: ThingName, principal: Principal
    ) -> AttachThingPrincipalResponse:
        """Attaches the specified principal to the specified thing. A principal can
        be X.509 certificates, IAM users, groups, and roles, Amazon Cognito
        identities or federated identities.

        Requires permission to access the
        `AttachThingPrincipal <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The name of the thing.
        :param principal: The principal, which can be a certificate ARN (as returned from the
        CreateCertificate operation) or an Amazon Cognito ID.
        :returns: AttachThingPrincipalResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CancelAuditMitigationActionsTask")
    def cancel_audit_mitigation_actions_task(
        self, context: RequestContext, task_id: MitigationActionsTaskId
    ) -> CancelAuditMitigationActionsTaskResponse:
        """Cancels a mitigation action task that is in progress. If the task is not
        in progress, an InvalidRequestException occurs.

        Requires permission to access the
        `CancelAuditMitigationActionsTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: The unique identifier for the task that you want to cancel.
        :returns: CancelAuditMitigationActionsTaskResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CancelAuditTask")
    def cancel_audit_task(
        self, context: RequestContext, task_id: AuditTaskId
    ) -> CancelAuditTaskResponse:
        """Cancels an audit that is in progress. The audit can be either scheduled
        or on demand. If the audit isn't in progress, an
        "InvalidRequestException" occurs.

        Requires permission to access the
        `CancelAuditTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: The ID of the audit you want to cancel.
        :returns: CancelAuditTaskResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CancelCertificateTransfer")
    def cancel_certificate_transfer(
        self, context: RequestContext, certificate_id: CertificateId
    ) -> None:
        """Cancels a pending transfer for the specified certificate.

        **Note** Only the transfer source account can use this operation to
        cancel a transfer. (Transfer destinations can use
        RejectCertificateTransfer instead.) After transfer, IoT returns the
        certificate to the source account in the INACTIVE state. After the
        destination account has accepted the transfer, the transfer cannot be
        cancelled.

        After a certificate transfer is cancelled, the status of the certificate
        changes from PENDING_TRANSFER to INACTIVE.

        Requires permission to access the
        `CancelCertificateTransfer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param certificate_id: The ID of the certificate.
        :raises ResourceNotFoundException:
        :raises TransferAlreadyCompletedException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CancelDetectMitigationActionsTask")
    def cancel_detect_mitigation_actions_task(
        self, context: RequestContext, task_id: MitigationActionsTaskId
    ) -> CancelDetectMitigationActionsTaskResponse:
        """Cancels a Device Defender ML Detect mitigation action.

        Requires permission to access the
        `CancelDetectMitigationActionsTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: The unique identifier of the task.
        :returns: CancelDetectMitigationActionsTaskResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CancelJob")
    def cancel_job(
        self,
        context: RequestContext,
        job_id: JobId,
        reason_code: ReasonCode = None,
        comment: Comment = None,
        force: ForceFlag = None,
    ) -> CancelJobResponse:
        """Cancels a job.

        Requires permission to access the
        `CancelJob <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_id: The unique identifier you assigned to this job when it was created.
        :param reason_code: (Optional)A reason code string that explains why the job was canceled.
        :param comment: An optional comment string describing why the job was canceled.
        :param force: (Optional) If ``true`` job executions with status "IN_PROGRESS" and
        "QUEUED" are canceled, otherwise only job executions with status
        "QUEUED" are canceled.
        :returns: CancelJobResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CancelJobExecution")
    def cancel_job_execution(
        self,
        context: RequestContext,
        job_id: JobId,
        thing_name: ThingName,
        force: ForceFlag = None,
        expected_version: ExpectedVersion = None,
        status_details: DetailsMap = None,
    ) -> None:
        """Cancels the execution of a job for a given thing.

        Requires permission to access the
        `CancelJobExecution <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_id: The ID of the job to be canceled.
        :param thing_name: The name of the thing whose execution of the job will be canceled.
        :param force: (Optional) If ``true`` the job execution will be canceled if it has
        status IN_PROGRESS or QUEUED, otherwise the job execution will be
        canceled only if it has status QUEUED.
        :param expected_version: (Optional) The expected current version of the job execution.
        :param status_details: A collection of name/value pairs that describe the status of the job
        execution.
        :raises InvalidRequestException:
        :raises InvalidStateTransitionException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        :raises VersionConflictException:
        """
        raise NotImplementedError

    @handler("ClearDefaultAuthorizer")
    def clear_default_authorizer(
        self,
        context: RequestContext,
    ) -> ClearDefaultAuthorizerResponse:
        """Clears the default authorizer.

        Requires permission to access the
        `ClearDefaultAuthorizer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :returns: ClearDefaultAuthorizerResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ConfirmTopicRuleDestination")
    def confirm_topic_rule_destination(
        self, context: RequestContext, confirmation_token: ConfirmationToken
    ) -> ConfirmTopicRuleDestinationResponse:
        """Confirms a topic rule destination. When you create a rule requiring a
        destination, IoT sends a confirmation message to the endpoint or base
        address you specify. The message includes a token which you pass back
        when calling ``ConfirmTopicRuleDestination`` to confirm that you own or
        have access to the endpoint.

        Requires permission to access the
        `ConfirmTopicRuleDestination <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param confirmation_token: The token used to confirm ownership or access to the topic rule
        confirmation URL.
        :returns: ConfirmTopicRuleDestinationResponse
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises UnauthorizedException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("CreateAuditSuppression")
    def create_audit_suppression(
        self,
        context: RequestContext,
        check_name: AuditCheckName,
        resource_identifier: ResourceIdentifier,
        client_request_token: ClientRequestToken,
        expiration_date: Timestamp = None,
        suppress_indefinitely: SuppressIndefinitely = None,
        description: AuditDescription = None,
    ) -> CreateAuditSuppressionResponse:
        """Creates a Device Defender audit suppression.

        Requires permission to access the
        `CreateAuditSuppression <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param check_name: An audit check name.
        :param resource_identifier: Information that identifies the noncompliant resource.
        :param client_request_token: Each audit supression must have a unique client request token.
        :param expiration_date: The epoch timestamp in seconds at which this suppression expires.
        :param suppress_indefinitely: Indicates whether a suppression should exist indefinitely or not.
        :param description: The description of the audit suppression.
        :returns: CreateAuditSuppressionResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateAuthorizer")
    def create_authorizer(
        self,
        context: RequestContext,
        authorizer_name: AuthorizerName,
        authorizer_function_arn: AuthorizerFunctionArn,
        token_key_name: TokenKeyName = None,
        token_signing_public_keys: PublicKeyMap = None,
        status: AuthorizerStatus = None,
        tags: TagList = None,
        signing_disabled: BooleanKey = None,
        enable_caching_for_http: EnableCachingForHttp = None,
    ) -> CreateAuthorizerResponse:
        """Creates an authorizer.

        Requires permission to access the
        `CreateAuthorizer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param authorizer_name: The authorizer name.
        :param authorizer_function_arn: The ARN of the authorizer's Lambda function.
        :param token_key_name: The name of the token key used to extract the token from the HTTP
        headers.
        :param token_signing_public_keys: The public keys used to verify the digital signature returned by your
        custom authentication service.
        :param status: The status of the create authorizer request.
        :param tags: Metadata which can be used to manage the custom authorizer.
        :param signing_disabled: Specifies whether IoT validates the token signature in an authorization
        request.
        :param enable_caching_for_http: When ``true``, the result from the authorizer’s Lambda function is
        cached for clients that use persistent HTTP connections.
        :returns: CreateAuthorizerResponse
        :raises ResourceAlreadyExistsException:
        :raises InvalidRequestException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateBillingGroup")
    def create_billing_group(
        self,
        context: RequestContext,
        billing_group_name: BillingGroupName,
        billing_group_properties: BillingGroupProperties = None,
        tags: TagList = None,
    ) -> CreateBillingGroupResponse:
        """Creates a billing group.

        Requires permission to access the
        `CreateBillingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param billing_group_name: The name you wish to give to the billing group.
        :param billing_group_properties: The properties of the billing group.
        :param tags: Metadata which can be used to manage the billing group.
        :returns: CreateBillingGroupResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateCertificateFromCsr")
    def create_certificate_from_csr(
        self,
        context: RequestContext,
        certificate_signing_request: CertificateSigningRequest,
        set_as_active: SetAsActive = None,
    ) -> CreateCertificateFromCsrResponse:
        """Creates an X.509 certificate using the specified certificate signing
        request.

        **Note:** The CSR must include a public key that is either an RSA key
        with a length of at least 2048 bits or an ECC key from NIST P-256, NIST
        P-384, or NIST P-512 curves. For supported certificates, consult
        `Certificate signing algorithms supported by
        IoT <https://docs.aws.amazon.com/iot/latest/developerguide/x509-client-certs.html#x509-cert-algorithms>`__.

        **Note:** Reusing the same certificate signing request (CSR) results in
        a distinct certificate.

        Requires permission to access the
        `CreateCertificateFromCsr <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        You can create multiple certificates in a batch by creating a directory,
        copying multiple .csr files into that directory, and then specifying
        that directory on the command line. The following commands show how to
        create a batch of certificates given a batch of CSRs.

        Assuming a set of CSRs are located inside of the directory
        my-csr-directory:

        On Linux and OS X, the command is:

        $ ls my-csr-directory/ | xargs -I {} aws iot
        create-certificate-from-csr --certificate-signing-request
        file://my-csr-directory/{}

        This command lists all of the CSRs in my-csr-directory and pipes each
        CSR file name to the aws iot create-certificate-from-csr Amazon Web
        Services CLI command to create a certificate for the corresponding CSR.

        The aws iot create-certificate-from-csr part of the command can also be
        run in parallel to speed up the certificate creation process:

        $ ls my-csr-directory/ | xargs -P 10 -I {} aws iot
        create-certificate-from-csr --certificate-signing-request
        file://my-csr-directory/{}

        On Windows PowerShell, the command to create certificates for all CSRs
        in my-csr-directory is:

        > ls -Name my-csr-directory | %{aws iot create-certificate-from-csr
        --certificate-signing-request file://my-csr-directory/$_}

        On a Windows command prompt, the command to create certificates for all
        CSRs in my-csr-directory is:

        > forfiles /p my-csr-directory /c "cmd /c aws iot
        create-certificate-from-csr --certificate-signing-request file://@path"

        :param certificate_signing_request: The certificate signing request (CSR).
        :param set_as_active: Specifies whether the certificate is active.
        :returns: CreateCertificateFromCsrResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateCustomMetric")
    def create_custom_metric(
        self,
        context: RequestContext,
        metric_name: MetricName,
        metric_type: CustomMetricType,
        client_request_token: ClientRequestToken,
        display_name: CustomMetricDisplayName = None,
        tags: TagList = None,
    ) -> CreateCustomMetricResponse:
        """Use this API to define a Custom Metric published by your devices to
        Device Defender.

        Requires permission to access the
        `CreateCustomMetric <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param metric_name: The name of the custom metric.
        :param metric_type: The type of the custom metric.
        :param client_request_token: Each custom metric must have a unique client request token.
        :param display_name: The friendly name in the console for the custom metric.
        :param tags: Metadata that can be used to manage the custom metric.
        :returns: CreateCustomMetricResponse
        :raises InvalidRequestException:
        :raises LimitExceededException:
        :raises ResourceAlreadyExistsException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateDimension", expand=False)
    def create_dimension(
        self, context: RequestContext, request: CreateDimensionRequest
    ) -> CreateDimensionResponse:
        """Create a dimension that you can use to limit the scope of a metric used
        in a security profile for IoT Device Defender. For example, using a
        ``TOPIC_FILTER`` dimension, you can narrow down the scope of the metric
        only to MQTT topics whose name match the pattern specified in the
        dimension.

        Requires permission to access the
        `CreateDimension <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param name: A unique identifier for the dimension.
        :param type: Specifies the type of dimension.
        :param string_values: Specifies the value or list of values for the dimension.
        :param client_request_token: Each dimension must have a unique client request token.
        :param tags: Metadata that can be used to manage the dimension.
        :returns: CreateDimensionResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises LimitExceededException:
        :raises ResourceAlreadyExistsException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateDomainConfiguration")
    def create_domain_configuration(
        self,
        context: RequestContext,
        domain_configuration_name: DomainConfigurationName,
        domain_name: DomainName = None,
        server_certificate_arns: ServerCertificateArns = None,
        validation_certificate_arn: AcmCertificateArn = None,
        authorizer_config: AuthorizerConfig = None,
        service_type: ServiceType = None,
        tags: TagList = None,
    ) -> CreateDomainConfigurationResponse:
        """Creates a domain configuration.

        Requires permission to access the
        `CreateDomainConfiguration <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param domain_configuration_name: The name of the domain configuration.
        :param domain_name: The name of the domain.
        :param server_certificate_arns: The ARNs of the certificates that IoT passes to the device during the
        TLS handshake.
        :param validation_certificate_arn: The certificate used to validate the server certificate and prove domain
        name ownership.
        :param authorizer_config: An object that specifies the authorization service for a domain.
        :param service_type: The type of service delivered by the endpoint.
        :param tags: Metadata which can be used to manage the domain configuration.
        :returns: CreateDomainConfigurationResponse
        :raises LimitExceededException:
        :raises CertificateValidationException:
        :raises ResourceAlreadyExistsException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises UnauthorizedException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateDynamicThingGroup")
    def create_dynamic_thing_group(
        self,
        context: RequestContext,
        thing_group_name: ThingGroupName,
        query_string: QueryString,
        thing_group_properties: ThingGroupProperties = None,
        index_name: IndexName = None,
        query_version: QueryVersion = None,
        tags: TagList = None,
    ) -> CreateDynamicThingGroupResponse:
        """Creates a dynamic thing group.

        Requires permission to access the
        `CreateDynamicThingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_group_name: The dynamic thing group name to create.
        :param query_string: The dynamic thing group search query string.
        :param thing_group_properties: The dynamic thing group properties.
        :param index_name: The dynamic thing group index name.
        :param query_version: The dynamic thing group query version.
        :param tags: Metadata which can be used to manage the dynamic thing group.
        :returns: CreateDynamicThingGroupResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises InvalidQueryException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateFleetMetric")
    def create_fleet_metric(
        self,
        context: RequestContext,
        metric_name: FleetMetricName,
        query_string: QueryString,
        aggregation_type: AggregationType,
        period: FleetMetricPeriod,
        aggregation_field: AggregationField,
        description: FleetMetricDescription = None,
        query_version: QueryVersion = None,
        index_name: IndexName = None,
        unit: FleetMetricUnit = None,
        tags: TagList = None,
    ) -> CreateFleetMetricResponse:
        """Creates a fleet metric.

        Requires permission to access the
        `CreateFleetMetric <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param metric_name: The name of the fleet metric to create.
        :param query_string: The search query string.
        :param aggregation_type: The type of the aggregation query.
        :param period: The time in seconds between fleet metric emissions.
        :param aggregation_field: The field to aggregate.
        :param description: The fleet metric description.
        :param query_version: The query version.
        :param index_name: The name of the index to search.
        :param unit: Used to support unit transformation such as milliseconds to seconds.
        :param tags: Metadata, which can be used to manage the fleet metric.
        :returns: CreateFleetMetricResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        :raises ResourceAlreadyExistsException:
        :raises ResourceNotFoundException:
        :raises InvalidQueryException:
        :raises InvalidAggregationException:
        :raises IndexNotReadyException:
        """
        raise NotImplementedError

    @handler("CreateJob")
    def create_job(
        self,
        context: RequestContext,
        job_id: JobId,
        targets: JobTargets,
        document_source: JobDocumentSource = None,
        document: JobDocument = None,
        description: JobDescription = None,
        presigned_url_config: PresignedUrlConfig = None,
        target_selection: TargetSelection = None,
        job_executions_rollout_config: JobExecutionsRolloutConfig = None,
        abort_config: AbortConfig = None,
        timeout_config: TimeoutConfig = None,
        tags: TagList = None,
        namespace_id: NamespaceId = None,
        job_template_arn: JobTemplateArn = None,
        job_executions_retry_config: JobExecutionsRetryConfig = None,
        document_parameters: ParameterMap = None,
    ) -> CreateJobResponse:
        """Creates a job.

        Requires permission to access the
        `CreateJob <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_id: A job identifier which must be unique for your Amazon Web Services
        account.
        :param targets: A list of things and thing groups to which the job should be sent.
        :param document_source: An S3 link to the job document.
        :param document: The job document.
        :param description: A short text description of the job.
        :param presigned_url_config: Configuration information for pre-signed S3 URLs.
        :param target_selection: Specifies whether the job will continue to run (CONTINUOUS), or will be
        complete after all those things specified as targets have completed the
        job (SNAPSHOT).
        :param job_executions_rollout_config: Allows you to create a staged rollout of the job.
        :param abort_config: Allows you to create the criteria to abort a job.
        :param timeout_config: Specifies the amount of time each device has to finish its execution of
        the job.
        :param tags: Metadata which can be used to manage the job.
        :param namespace_id: The namespace used to indicate that a job is a customer-managed job.
        :param job_template_arn: The ARN of the job template used to create the job.
        :param job_executions_retry_config: Allows you to create the criteria to retry a job.
        :param document_parameters: Parameters of a managed template that you can specify to create the job
        document.
        :returns: CreateJobResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ResourceAlreadyExistsException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("CreateJobTemplate")
    def create_job_template(
        self,
        context: RequestContext,
        job_template_id: JobTemplateId,
        description: JobDescription,
        job_arn: JobArn = None,
        document_source: JobDocumentSource = None,
        document: JobDocument = None,
        presigned_url_config: PresignedUrlConfig = None,
        job_executions_rollout_config: JobExecutionsRolloutConfig = None,
        abort_config: AbortConfig = None,
        timeout_config: TimeoutConfig = None,
        tags: TagList = None,
        job_executions_retry_config: JobExecutionsRetryConfig = None,
    ) -> CreateJobTemplateResponse:
        """Creates a job template.

        Requires permission to access the
        `CreateJobTemplate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_template_id: A unique identifier for the job template.
        :param description: A description of the job document.
        :param job_arn: The ARN of the job to use as the basis for the job template.
        :param document_source: An S3 link to the job document to use in the template.
        :param document: The job document.
        :param presigned_url_config: Configuration for pre-signed S3 URLs.
        :param job_executions_rollout_config: Allows you to create a staged rollout of a job.
        :param abort_config: The criteria that determine when and how a job abort takes place.
        :param timeout_config: Specifies the amount of time each device has to finish its execution of
        the job.
        :param tags: Metadata that can be used to manage the job template.
        :param job_executions_retry_config: Allows you to create the criteria to retry a job.
        :returns: CreateJobTemplateResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ConflictException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateKeysAndCertificate")
    def create_keys_and_certificate(
        self, context: RequestContext, set_as_active: SetAsActive = None
    ) -> CreateKeysAndCertificateResponse:
        """Creates a 2048-bit RSA key pair and issues an X.509 certificate using
        the issued public key. You can also call ``CreateKeysAndCertificate``
        over MQTT from a device, for more information, see `Provisioning MQTT
        API <https://docs.aws.amazon.com/iot/latest/developerguide/provision-wo-cert.html#provision-mqtt-api>`__.

        **Note** This is the only time IoT issues the private key for this
        certificate, so it is important to keep it in a secure location.

        Requires permission to access the
        `CreateKeysAndCertificate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param set_as_active: Specifies whether the certificate is active.
        :returns: CreateKeysAndCertificateResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateMitigationAction")
    def create_mitigation_action(
        self,
        context: RequestContext,
        action_name: MitigationActionName,
        role_arn: RoleArn,
        action_params: MitigationActionParams,
        tags: TagList = None,
    ) -> CreateMitigationActionResponse:
        """Defines an action that can be applied to audit findings by using
        StartAuditMitigationActionsTask. Only certain types of mitigation
        actions can be applied to specific check names. For more information,
        see `Mitigation
        actions <https://docs.aws.amazon.com/iot/latest/developerguide/device-defender-mitigation-actions.html>`__.
        Each mitigation action can apply only one type of change.

        Requires permission to access the
        `CreateMitigationAction <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param action_name: A friendly name for the action.
        :param role_arn: The ARN of the IAM role that is used to apply the mitigation action.
        :param action_params: Defines the type of action and the parameters for that action.
        :param tags: Metadata that can be used to manage the mitigation action.
        :returns: CreateMitigationActionResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateOTAUpdate")
    def create_ota_update(
        self,
        context: RequestContext,
        ota_update_id: OTAUpdateId,
        targets: Targets,
        files: OTAUpdateFiles,
        role_arn: RoleArn,
        description: OTAUpdateDescription = None,
        protocols: Protocols = None,
        target_selection: TargetSelection = None,
        aws_job_executions_rollout_config: AwsJobExecutionsRolloutConfig = None,
        aws_job_presigned_url_config: AwsJobPresignedUrlConfig = None,
        aws_job_abort_config: AwsJobAbortConfig = None,
        aws_job_timeout_config: AwsJobTimeoutConfig = None,
        additional_parameters: AdditionalParameterMap = None,
        tags: TagList = None,
    ) -> CreateOTAUpdateResponse:
        """Creates an IoT OTA update on a target group of things or groups.

        Requires permission to access the
        `CreateOTAUpdate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param ota_update_id: The ID of the OTA update to be created.
        :param targets: The devices targeted to receive OTA updates.
        :param files: The files to be streamed by the OTA update.
        :param role_arn: The IAM role that grants Amazon Web Services IoT Core access to the
        Amazon S3, IoT jobs and Amazon Web Services Code Signing resources to
        create an OTA update job.
        :param description: The description of the OTA update.
        :param protocols: The protocol used to transfer the OTA update image.
        :param target_selection: Specifies whether the update will continue to run (CONTINUOUS), or will
        be complete after all the things specified as targets have completed the
        update (SNAPSHOT).
        :param aws_job_executions_rollout_config: Configuration for the rollout of OTA updates.
        :param aws_job_presigned_url_config: Configuration information for pre-signed URLs.
        :param aws_job_abort_config: The criteria that determine when and how a job abort takes place.
        :param aws_job_timeout_config: Specifies the amount of time each device has to finish its execution of
        the job.
        :param additional_parameters: A list of additional OTA update parameters which are name-value pairs.
        :param tags: Metadata which can be used to manage updates.
        :returns: CreateOTAUpdateResponse
        :raises InvalidRequestException:
        :raises LimitExceededException:
        :raises ResourceNotFoundException:
        :raises ResourceAlreadyExistsException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("CreatePolicy")
    def create_policy(
        self,
        context: RequestContext,
        policy_name: PolicyName,
        policy_document: PolicyDocument,
        tags: TagList = None,
    ) -> CreatePolicyResponse:
        """Creates an IoT policy.

        The created policy is the default version for the policy. This operation
        creates a policy version with a version identifier of **1** and sets
        **1** as the policy's default version.

        Requires permission to access the
        `CreatePolicy <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The policy name.
        :param policy_document: The JSON document that describes the policy.
        :param tags: Metadata which can be used to manage the policy.
        :returns: CreatePolicyResponse
        :raises ResourceAlreadyExistsException:
        :raises MalformedPolicyException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreatePolicyVersion")
    def create_policy_version(
        self,
        context: RequestContext,
        policy_name: PolicyName,
        policy_document: PolicyDocument,
        set_as_default: SetAsDefault = None,
    ) -> CreatePolicyVersionResponse:
        """Creates a new version of the specified IoT policy. To update a policy,
        create a new policy version. A managed policy can have up to five
        versions. If the policy has five versions, you must use
        DeletePolicyVersion to delete an existing version before you create a
        new one.

        Optionally, you can set the new version as the policy's default version.
        The default version is the operative version (that is, the version that
        is in effect for the certificates to which the policy is attached).

        Requires permission to access the
        `CreatePolicyVersion <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The policy name.
        :param policy_document: The JSON document that describes the policy.
        :param set_as_default: Specifies whether the policy version is set as the default.
        :returns: CreatePolicyVersionResponse
        :raises ResourceNotFoundException:
        :raises MalformedPolicyException:
        :raises VersionsLimitExceededException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateProvisioningClaim")
    def create_provisioning_claim(
        self, context: RequestContext, template_name: TemplateName
    ) -> CreateProvisioningClaimResponse:
        """Creates a provisioning claim.

        Requires permission to access the
        `CreateProvisioningClaim <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_name: The name of the provisioning template to use.
        :returns: CreateProvisioningClaimResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateProvisioningTemplate")
    def create_provisioning_template(
        self,
        context: RequestContext,
        template_name: TemplateName,
        template_body: TemplateBody,
        provisioning_role_arn: RoleArn,
        description: TemplateDescription = None,
        enabled: Enabled = None,
        pre_provisioning_hook: ProvisioningHook = None,
        tags: TagList = None,
    ) -> CreateProvisioningTemplateResponse:
        """Creates a fleet provisioning template.

        Requires permission to access the
        `CreateProvisioningTemplate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_name: The name of the fleet provisioning template.
        :param template_body: The JSON formatted contents of the fleet provisioning template.
        :param provisioning_role_arn: The role ARN for the role associated with the fleet provisioning
        template.
        :param description: The description of the fleet provisioning template.
        :param enabled: True to enable the fleet provisioning template, otherwise false.
        :param pre_provisioning_hook: Creates a pre-provisioning hook template.
        :param tags: Metadata which can be used to manage the fleet provisioning template.
        :returns: CreateProvisioningTemplateResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ResourceAlreadyExistsException:
        """
        raise NotImplementedError

    @handler("CreateProvisioningTemplateVersion")
    def create_provisioning_template_version(
        self,
        context: RequestContext,
        template_name: TemplateName,
        template_body: TemplateBody,
        set_as_default: SetAsDefault = None,
    ) -> CreateProvisioningTemplateVersionResponse:
        """Creates a new version of a fleet provisioning template.

        Requires permission to access the
        `CreateProvisioningTemplateVersion <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_name: The name of the fleet provisioning template.
        :param template_body: The JSON formatted contents of the fleet provisioning template.
        :param set_as_default: Sets a fleet provision template version as the default version.
        :returns: CreateProvisioningTemplateVersionResponse
        :raises VersionsLimitExceededException:
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        :raises UnauthorizedException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("CreateRoleAlias")
    def create_role_alias(
        self,
        context: RequestContext,
        role_alias: RoleAlias,
        role_arn: RoleArn,
        credential_duration_seconds: CredentialDurationSeconds = None,
        tags: TagList = None,
    ) -> CreateRoleAliasResponse:
        """Creates a role alias.

        Requires permission to access the
        `CreateRoleAlias <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param role_alias: The role alias that points to a role ARN.
        :param role_arn: The role ARN.
        :param credential_duration_seconds: How long (in seconds) the credentials will be valid.
        :param tags: Metadata which can be used to manage the role alias.
        :returns: CreateRoleAliasResponse
        :raises ResourceAlreadyExistsException:
        :raises InvalidRequestException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateScheduledAudit")
    def create_scheduled_audit(
        self,
        context: RequestContext,
        frequency: AuditFrequency,
        target_check_names: TargetAuditCheckNames,
        scheduled_audit_name: ScheduledAuditName,
        day_of_month: DayOfMonth = None,
        day_of_week: DayOfWeek = None,
        tags: TagList = None,
    ) -> CreateScheduledAuditResponse:
        """Creates a scheduled audit that is run at a specified time interval.

        Requires permission to access the
        `CreateScheduledAudit <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param frequency: How often the scheduled audit takes place, either ``DAILY``, ``WEEKLY``,
        ``BIWEEKLY`` or ``MONTHLY``.
        :param target_check_names: Which checks are performed during the scheduled audit.
        :param scheduled_audit_name: The name you want to give to the scheduled audit.
        :param day_of_month: The day of the month on which the scheduled audit takes place.
        :param day_of_week: The day of the week on which the scheduled audit takes place, either
        ``SUN``, ``MON``, ``TUE``, ``WED``, ``THU``, ``FRI``, or ``SAT``.
        :param tags: Metadata that can be used to manage the scheduled audit.
        :returns: CreateScheduledAuditResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateSecurityProfile")
    def create_security_profile(
        self,
        context: RequestContext,
        security_profile_name: SecurityProfileName,
        security_profile_description: SecurityProfileDescription = None,
        behaviors: Behaviors = None,
        alert_targets: AlertTargets = None,
        additional_metrics_to_retain: AdditionalMetricsToRetainList = None,
        additional_metrics_to_retain_v2: AdditionalMetricsToRetainV2List = None,
        tags: TagList = None,
    ) -> CreateSecurityProfileResponse:
        """Creates a Device Defender security profile.

        Requires permission to access the
        `CreateSecurityProfile <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param security_profile_name: The name you are giving to the security profile.
        :param security_profile_description: A description of the security profile.
        :param behaviors: Specifies the behaviors that, when violated by a device (thing), cause
        an alert.
        :param alert_targets: Specifies the destinations to which alerts are sent.
        :param additional_metrics_to_retain: *Please use CreateSecurityProfileRequest$additionalMetricsToRetainV2
        instead.
        :param additional_metrics_to_retain_v2: A list of metrics whose data is retained (stored).
        :param tags: Metadata that can be used to manage the security profile.
        :returns: CreateSecurityProfileResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateStream")
    def create_stream(
        self,
        context: RequestContext,
        stream_id: StreamId,
        files: StreamFiles,
        role_arn: RoleArn,
        description: StreamDescription = None,
        tags: TagList = None,
    ) -> CreateStreamResponse:
        """Creates a stream for delivering one or more large files in chunks over
        MQTT. A stream transports data bytes in chunks or blocks packaged as
        MQTT messages from a source like S3. You can have one or more files
        associated with a stream.

        Requires permission to access the
        `CreateStream <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param stream_id: The stream ID.
        :param files: The files to stream.
        :param role_arn: An IAM role that allows the IoT service principal to access your S3
        files.
        :param description: A description of the stream.
        :param tags: Metadata which can be used to manage streams.
        :returns: CreateStreamResponse
        :raises InvalidRequestException:
        :raises LimitExceededException:
        :raises ResourceNotFoundException:
        :raises ResourceAlreadyExistsException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateThing")
    def create_thing(
        self,
        context: RequestContext,
        thing_name: ThingName,
        thing_type_name: ThingTypeName = None,
        attribute_payload: AttributePayload = None,
        billing_group_name: BillingGroupName = None,
    ) -> CreateThingResponse:
        """Creates a thing record in the registry. If this call is made multiple
        times using the same thing name and configuration, the call will
        succeed. If this call is made with the same thing name but different
        configuration a ``ResourceAlreadyExistsException`` is thrown.

        This is a control plane operation. See
        `Authorization <https://docs.aws.amazon.com/iot/latest/developerguide/iot-authorization.html>`__
        for information about authorizing control plane actions.

        Requires permission to access the
        `CreateThing <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The name of the thing to create.
        :param thing_type_name: The name of the thing type associated with the new thing.
        :param attribute_payload: The attribute payload, which consists of up to three name/value pairs in
        a JSON document.
        :param billing_group_name: The name of the billing group the thing will be added to.
        :returns: CreateThingResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceAlreadyExistsException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("CreateThingGroup")
    def create_thing_group(
        self,
        context: RequestContext,
        thing_group_name: ThingGroupName,
        parent_group_name: ThingGroupName = None,
        thing_group_properties: ThingGroupProperties = None,
        tags: TagList = None,
    ) -> CreateThingGroupResponse:
        """Create a thing group.

        This is a control plane operation. See
        `Authorization <https://docs.aws.amazon.com/iot/latest/developerguide/iot-authorization.html>`__
        for information about authorizing control plane actions.

        Requires permission to access the
        `CreateThingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_group_name: The thing group name to create.
        :param parent_group_name: The name of the parent thing group.
        :param thing_group_properties: The thing group properties.
        :param tags: Metadata which can be used to manage the thing group.
        :returns: CreateThingGroupResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("CreateThingType")
    def create_thing_type(
        self,
        context: RequestContext,
        thing_type_name: ThingTypeName,
        thing_type_properties: ThingTypeProperties = None,
        tags: TagList = None,
    ) -> CreateThingTypeResponse:
        """Creates a new thing type.

        Requires permission to access the
        `CreateThingType <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_type_name: The name of the thing type.
        :param thing_type_properties: The ThingTypeProperties for the thing type to create.
        :param tags: Metadata which can be used to manage the thing type.
        :returns: CreateThingTypeResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceAlreadyExistsException:
        """
        raise NotImplementedError

    @handler("CreateTopicRule")
    def create_topic_rule(
        self,
        context: RequestContext,
        rule_name: RuleName,
        topic_rule_payload: TopicRulePayload,
        tags: String = None,
    ) -> None:
        """Creates a rule. Creating rules is an administrator-level action. Any
        user who has permission to create rules will be able to access data
        processed by the rule.

        Requires permission to access the
        `CreateTopicRule <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param rule_name: The name of the rule.
        :param topic_rule_payload: The rule payload.
        :param tags: Metadata which can be used to manage the topic rule.
        :raises SqlParseException:
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises ServiceUnavailableException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("CreateTopicRuleDestination")
    def create_topic_rule_destination(
        self, context: RequestContext, destination_configuration: TopicRuleDestinationConfiguration
    ) -> CreateTopicRuleDestinationResponse:
        """Creates a topic rule destination. The destination must be confirmed
        prior to use.

        Requires permission to access the
        `CreateTopicRuleDestination <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param destination_configuration: The topic rule destination configuration.
        :returns: CreateTopicRuleDestinationResponse
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises ServiceUnavailableException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("DeleteAccountAuditConfiguration")
    def delete_account_audit_configuration(
        self, context: RequestContext, delete_scheduled_audits: DeleteScheduledAudits = None
    ) -> DeleteAccountAuditConfigurationResponse:
        """Restores the default settings for Device Defender audits for this
        account. Any configuration data you entered is deleted and all audit
        checks are reset to disabled.

        Requires permission to access the
        `DeleteAccountAuditConfiguration <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param delete_scheduled_audits: If true, all scheduled audits are deleted.
        :returns: DeleteAccountAuditConfigurationResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteAuditSuppression")
    def delete_audit_suppression(
        self,
        context: RequestContext,
        check_name: AuditCheckName,
        resource_identifier: ResourceIdentifier,
    ) -> DeleteAuditSuppressionResponse:
        """Deletes a Device Defender audit suppression.

        Requires permission to access the
        `DeleteAuditSuppression <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param check_name: An audit check name.
        :param resource_identifier: Information that identifies the noncompliant resource.
        :returns: DeleteAuditSuppressionResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteAuthorizer")
    def delete_authorizer(
        self, context: RequestContext, authorizer_name: AuthorizerName
    ) -> DeleteAuthorizerResponse:
        """Deletes an authorizer.

        Requires permission to access the
        `DeleteAuthorizer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param authorizer_name: The name of the authorizer to delete.
        :returns: DeleteAuthorizerResponse
        :raises DeleteConflictException:
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteBillingGroup")
    def delete_billing_group(
        self,
        context: RequestContext,
        billing_group_name: BillingGroupName,
        expected_version: OptionalVersion = None,
    ) -> DeleteBillingGroupResponse:
        """Deletes the billing group.

        Requires permission to access the
        `DeleteBillingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param billing_group_name: The name of the billing group.
        :param expected_version: The expected version of the billing group.
        :returns: DeleteBillingGroupResponse
        :raises InvalidRequestException:
        :raises VersionConflictException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteCACertificate")
    def delete_ca_certificate(
        self, context: RequestContext, certificate_id: CertificateId
    ) -> DeleteCACertificateResponse:
        """Deletes a registered CA certificate.

        Requires permission to access the
        `DeleteCACertificate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param certificate_id: The ID of the certificate to delete.
        :returns: DeleteCACertificateResponse
        :raises InvalidRequestException:
        :raises CertificateStateException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteCertificate")
    def delete_certificate(
        self,
        context: RequestContext,
        certificate_id: CertificateId,
        force_delete: ForceDelete = None,
    ) -> None:
        """Deletes the specified certificate.

        A certificate cannot be deleted if it has a policy or IoT thing attached
        to it or if its status is set to ACTIVE. To delete a certificate, first
        use the DetachPolicy action to detach all policies. Next, use the
        UpdateCertificate action to set the certificate to the INACTIVE status.

        Requires permission to access the
        `DeleteCertificate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param certificate_id: The ID of the certificate.
        :param force_delete: Forces the deletion of a certificate if it is inactive and is not
        attached to an IoT thing.
        :raises CertificateStateException:
        :raises DeleteConflictException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteCustomMetric")
    def delete_custom_metric(
        self, context: RequestContext, metric_name: MetricName
    ) -> DeleteCustomMetricResponse:
        """Deletes a Device Defender detect custom metric.

        Requires permission to access the
        `DeleteCustomMetric <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        Before you can delete a custom metric, you must first remove the custom
        metric from all security profiles it's a part of. The security profile
        associated with the custom metric can be found using the
        `ListSecurityProfiles <https://docs.aws.amazon.com/iot/latest/apireference/API_ListSecurityProfiles.html>`__
        API with ``metricName`` set to your custom metric name.

        :param metric_name: The name of the custom metric.
        :returns: DeleteCustomMetricResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteDimension")
    def delete_dimension(
        self, context: RequestContext, name: DimensionName
    ) -> DeleteDimensionResponse:
        """Removes the specified dimension from your Amazon Web Services accounts.

        Requires permission to access the
        `DeleteDimension <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param name: The unique identifier for the dimension that you want to delete.
        :returns: DeleteDimensionResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteDomainConfiguration")
    def delete_domain_configuration(
        self, context: RequestContext, domain_configuration_name: DomainConfigurationName
    ) -> DeleteDomainConfigurationResponse:
        """Deletes the specified domain configuration.

        Requires permission to access the
        `DeleteDomainConfiguration <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param domain_configuration_name: The name of the domain configuration to be deleted.
        :returns: DeleteDomainConfigurationResponse
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DeleteDynamicThingGroup")
    def delete_dynamic_thing_group(
        self,
        context: RequestContext,
        thing_group_name: ThingGroupName,
        expected_version: OptionalVersion = None,
    ) -> DeleteDynamicThingGroupResponse:
        """Deletes a dynamic thing group.

        Requires permission to access the
        `DeleteDynamicThingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_group_name: The name of the dynamic thing group to delete.
        :param expected_version: The expected version of the dynamic thing group to delete.
        :returns: DeleteDynamicThingGroupResponse
        :raises InvalidRequestException:
        :raises VersionConflictException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteFleetMetric")
    def delete_fleet_metric(
        self,
        context: RequestContext,
        metric_name: FleetMetricName,
        expected_version: OptionalVersion = None,
    ) -> None:
        """Deletes the specified fleet metric. Returns successfully with no error
        if the deletion is successful or you specify a fleet metric that doesn't
        exist.

        Requires permission to access the
        `DeleteFleetMetric <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param metric_name: The name of the fleet metric to delete.
        :param expected_version: The expected version of the fleet metric to delete.
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises VersionConflictException:
        """
        raise NotImplementedError

    @handler("DeleteJob")
    def delete_job(
        self,
        context: RequestContext,
        job_id: JobId,
        force: ForceFlag = None,
        namespace_id: NamespaceId = None,
    ) -> None:
        """Deletes a job and its related job executions.

        Deleting a job may take time, depending on the number of job executions
        created for the job and various other factors. While the job is being
        deleted, the status of the job will be shown as "DELETION_IN_PROGRESS".
        Attempting to delete or cancel a job whose status is already
        "DELETION_IN_PROGRESS" will result in an error.

        Only 10 jobs may have status "DELETION_IN_PROGRESS" at the same time, or
        a LimitExceededException will occur.

        Requires permission to access the
        `DeleteJob <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_id: The ID of the job to be deleted.
        :param force: (Optional) When true, you can delete a job which is "IN_PROGRESS".
        :param namespace_id: The namespace used to indicate that a job is a customer-managed job.
        :raises InvalidRequestException:
        :raises InvalidStateTransitionException:
        :raises ResourceNotFoundException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteJobExecution")
    def delete_job_execution(
        self,
        context: RequestContext,
        job_id: JobId,
        thing_name: ThingName,
        execution_number: ExecutionNumber,
        force: ForceFlag = None,
        namespace_id: NamespaceId = None,
    ) -> None:
        """Deletes a job execution.

        Requires permission to access the
        `DeleteJobExecution <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_id: The ID of the job whose execution on a particular device will be
        deleted.
        :param thing_name: The name of the thing whose job execution will be deleted.
        :param execution_number: The ID of the job execution to be deleted.
        :param force: (Optional) When true, you can delete a job execution which is
        "IN_PROGRESS".
        :param namespace_id: The namespace used to indicate that a job is a customer-managed job.
        :raises InvalidRequestException:
        :raises InvalidStateTransitionException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteJobTemplate")
    def delete_job_template(self, context: RequestContext, job_template_id: JobTemplateId) -> None:
        """Deletes the specified job template.

        :param job_template_id: The unique identifier of the job template to delete.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteMitigationAction")
    def delete_mitigation_action(
        self, context: RequestContext, action_name: MitigationActionName
    ) -> DeleteMitigationActionResponse:
        """Deletes a defined mitigation action from your Amazon Web Services
        accounts.

        Requires permission to access the
        `DeleteMitigationAction <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param action_name: The name of the mitigation action that you want to delete.
        :returns: DeleteMitigationActionResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteOTAUpdate")
    def delete_ota_update(
        self,
        context: RequestContext,
        ota_update_id: OTAUpdateId,
        delete_stream: DeleteStream = None,
        force_delete_aws_job: ForceDeleteAWSJob = None,
    ) -> DeleteOTAUpdateResponse:
        """Delete an OTA update.

        Requires permission to access the
        `DeleteOTAUpdate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param ota_update_id: The ID of the OTA update to delete.
        :param delete_stream: When true, the stream created by the OTAUpdate process is deleted when
        the OTA update is deleted.
        :param force_delete_aws_job: When true, deletes the IoT job created by the OTAUpdate process even if
        it is "IN_PROGRESS".
        :returns: DeleteOTAUpdateResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises VersionConflictException:
        """
        raise NotImplementedError

    @handler("DeletePolicy")
    def delete_policy(self, context: RequestContext, policy_name: PolicyName) -> None:
        """Deletes the specified policy.

        A policy cannot be deleted if it has non-default versions or it is
        attached to any certificate.

        To delete a policy, use the DeletePolicyVersion action to delete all
        non-default versions of the policy; use the DetachPolicy action to
        detach the policy from any certificate; and then use the DeletePolicy
        action to delete the policy.

        When a policy is deleted using DeletePolicy, its default version is
        deleted with it.

        Because of the distributed nature of Amazon Web Services, it can take up
        to five minutes after a policy is detached before it's ready to be
        deleted.

        Requires permission to access the
        `DeletePolicy <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The name of the policy to delete.
        :raises DeleteConflictException:
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeletePolicyVersion")
    def delete_policy_version(
        self, context: RequestContext, policy_name: PolicyName, policy_version_id: PolicyVersionId
    ) -> None:
        """Deletes the specified version of the specified policy. You cannot delete
        the default version of a policy using this action. To delete the default
        version of a policy, use DeletePolicy. To find out which version of a
        policy is marked as the default version, use ListPolicyVersions.

        Requires permission to access the
        `DeletePolicyVersion <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The name of the policy.
        :param policy_version_id: The policy version ID.
        :raises DeleteConflictException:
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteProvisioningTemplate")
    def delete_provisioning_template(
        self, context: RequestContext, template_name: TemplateName
    ) -> DeleteProvisioningTemplateResponse:
        """Deletes a fleet provisioning template.

        Requires permission to access the
        `DeleteProvisioningTemplate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_name: The name of the fleet provision template to delete.
        :returns: DeleteProvisioningTemplateResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises DeleteConflictException:
        :raises ThrottlingException:
        :raises ConflictingResourceUpdateException:
        :raises UnauthorizedException:
        """
        raise NotImplementedError

    @handler("DeleteProvisioningTemplateVersion")
    def delete_provisioning_template_version(
        self, context: RequestContext, template_name: TemplateName, version_id: TemplateVersionId
    ) -> DeleteProvisioningTemplateVersionResponse:
        """Deletes a fleet provisioning template version.

        Requires permission to access the
        `DeleteProvisioningTemplateVersion <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_name: The name of the fleet provisioning template version to delete.
        :param version_id: The fleet provisioning template version ID to delete.
        :returns: DeleteProvisioningTemplateVersionResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        :raises UnauthorizedException:
        :raises ConflictingResourceUpdateException:
        :raises DeleteConflictException:
        """
        raise NotImplementedError

    @handler("DeleteRegistrationCode")
    def delete_registration_code(
        self,
        context: RequestContext,
    ) -> DeleteRegistrationCodeResponse:
        """Deletes a CA certificate registration code.

        Requires permission to access the
        `DeleteRegistrationCode <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :returns: DeleteRegistrationCodeResponse
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteRoleAlias")
    def delete_role_alias(
        self, context: RequestContext, role_alias: RoleAlias
    ) -> DeleteRoleAliasResponse:
        """Deletes a role alias

        Requires permission to access the
        `DeleteRoleAlias <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param role_alias: The role alias to delete.
        :returns: DeleteRoleAliasResponse
        :raises DeleteConflictException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteScheduledAudit")
    def delete_scheduled_audit(
        self, context: RequestContext, scheduled_audit_name: ScheduledAuditName
    ) -> DeleteScheduledAuditResponse:
        """Deletes a scheduled audit.

        Requires permission to access the
        `DeleteScheduledAudit <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param scheduled_audit_name: The name of the scheduled audit you want to delete.
        :returns: DeleteScheduledAuditResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteSecurityProfile")
    def delete_security_profile(
        self,
        context: RequestContext,
        security_profile_name: SecurityProfileName,
        expected_version: OptionalVersion = None,
    ) -> DeleteSecurityProfileResponse:
        """Deletes a Device Defender security profile.

        Requires permission to access the
        `DeleteSecurityProfile <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param security_profile_name: The name of the security profile to be deleted.
        :param expected_version: The expected version of the security profile.
        :returns: DeleteSecurityProfileResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises VersionConflictException:
        """
        raise NotImplementedError

    @handler("DeleteStream")
    def delete_stream(self, context: RequestContext, stream_id: StreamId) -> DeleteStreamResponse:
        """Deletes a stream.

        Requires permission to access the
        `DeleteStream <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param stream_id: The stream ID.
        :returns: DeleteStreamResponse
        :raises ResourceNotFoundException:
        :raises DeleteConflictException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteThing")
    def delete_thing(
        self,
        context: RequestContext,
        thing_name: ThingName,
        expected_version: OptionalVersion = None,
    ) -> DeleteThingResponse:
        """Deletes the specified thing. Returns successfully with no error if the
        deletion is successful or you specify a thing that doesn't exist.

        Requires permission to access the
        `DeleteThing <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The name of the thing to delete.
        :param expected_version: The expected version of the thing record in the registry.
        :returns: DeleteThingResponse
        :raises ResourceNotFoundException:
        :raises VersionConflictException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteThingGroup")
    def delete_thing_group(
        self,
        context: RequestContext,
        thing_group_name: ThingGroupName,
        expected_version: OptionalVersion = None,
    ) -> DeleteThingGroupResponse:
        """Deletes a thing group.

        Requires permission to access the
        `DeleteThingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_group_name: The name of the thing group to delete.
        :param expected_version: The expected version of the thing group to delete.
        :returns: DeleteThingGroupResponse
        :raises InvalidRequestException:
        :raises VersionConflictException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteThingType")
    def delete_thing_type(
        self, context: RequestContext, thing_type_name: ThingTypeName
    ) -> DeleteThingTypeResponse:
        """Deletes the specified thing type. You cannot delete a thing type if it
        has things associated with it. To delete a thing type, first mark it as
        deprecated by calling DeprecateThingType, then remove any associated
        things by calling UpdateThing to change the thing type on any associated
        thing, and finally use DeleteThingType to delete the thing type.

        Requires permission to access the
        `DeleteThingType <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_type_name: The name of the thing type.
        :returns: DeleteThingTypeResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DeleteTopicRule")
    def delete_topic_rule(self, context: RequestContext, rule_name: RuleName) -> None:
        """Deletes the rule.

        Requires permission to access the
        `DeleteTopicRule <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param rule_name: The name of the rule.
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises UnauthorizedException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("DeleteTopicRuleDestination")
    def delete_topic_rule_destination(
        self, context: RequestContext, arn: AwsArn
    ) -> DeleteTopicRuleDestinationResponse:
        """Deletes a topic rule destination.

        Requires permission to access the
        `DeleteTopicRuleDestination <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param arn: The ARN of the topic rule destination to delete.
        :returns: DeleteTopicRuleDestinationResponse
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises UnauthorizedException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("DeleteV2LoggingLevel")
    def delete_v2_logging_level(
        self, context: RequestContext, target_type: LogTargetType, target_name: LogTargetName
    ) -> None:
        """Deletes a logging level.

        Requires permission to access the
        `DeleteV2LoggingLevel <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param target_type: The type of resource for which you are configuring logging.
        :param target_name: The name of the resource for which you are configuring logging.
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeprecateThingType")
    def deprecate_thing_type(
        self,
        context: RequestContext,
        thing_type_name: ThingTypeName,
        undo_deprecate: UndoDeprecate = None,
    ) -> DeprecateThingTypeResponse:
        """Deprecates a thing type. You can not associate new things with
        deprecated thing type.

        Requires permission to access the
        `DeprecateThingType <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_type_name: The name of the thing type to deprecate.
        :param undo_deprecate: Whether to undeprecate a deprecated thing type.
        :returns: DeprecateThingTypeResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeAccountAuditConfiguration")
    def describe_account_audit_configuration(
        self,
        context: RequestContext,
    ) -> DescribeAccountAuditConfigurationResponse:
        """Gets information about the Device Defender audit settings for this
        account. Settings include how audit notifications are sent and which
        audit checks are enabled or disabled.

        Requires permission to access the
        `DescribeAccountAuditConfiguration <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :returns: DescribeAccountAuditConfigurationResponse
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeAuditFinding")
    def describe_audit_finding(
        self, context: RequestContext, finding_id: FindingId
    ) -> DescribeAuditFindingResponse:
        """Gets information about a single audit finding. Properties include the
        reason for noncompliance, the severity of the issue, and the start time
        when the audit that returned the finding.

        Requires permission to access the
        `DescribeAuditFinding <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param finding_id: A unique identifier for a single audit finding.
        :returns: DescribeAuditFindingResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeAuditMitigationActionsTask")
    def describe_audit_mitigation_actions_task(
        self, context: RequestContext, task_id: MitigationActionsTaskId
    ) -> DescribeAuditMitigationActionsTaskResponse:
        """Gets information about an audit mitigation task that is used to apply
        mitigation actions to a set of audit findings. Properties include the
        actions being applied, the audit checks to which they're being applied,
        the task status, and aggregated task statistics.

        :param task_id: The unique identifier for the audit mitigation task.
        :returns: DescribeAuditMitigationActionsTaskResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeAuditSuppression")
    def describe_audit_suppression(
        self,
        context: RequestContext,
        check_name: AuditCheckName,
        resource_identifier: ResourceIdentifier,
    ) -> DescribeAuditSuppressionResponse:
        """Gets information about a Device Defender audit suppression.

        :param check_name: An audit check name.
        :param resource_identifier: Information that identifies the noncompliant resource.
        :returns: DescribeAuditSuppressionResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeAuditTask")
    def describe_audit_task(
        self, context: RequestContext, task_id: AuditTaskId
    ) -> DescribeAuditTaskResponse:
        """Gets information about a Device Defender audit.

        Requires permission to access the
        `DescribeAuditTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: The ID of the audit whose information you want to get.
        :returns: DescribeAuditTaskResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeAuthorizer")
    def describe_authorizer(
        self, context: RequestContext, authorizer_name: AuthorizerName
    ) -> DescribeAuthorizerResponse:
        """Describes an authorizer.

        Requires permission to access the
        `DescribeAuthorizer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param authorizer_name: The name of the authorizer to describe.
        :returns: DescribeAuthorizerResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeBillingGroup")
    def describe_billing_group(
        self, context: RequestContext, billing_group_name: BillingGroupName
    ) -> DescribeBillingGroupResponse:
        """Returns information about a billing group.

        Requires permission to access the
        `DescribeBillingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param billing_group_name: The name of the billing group.
        :returns: DescribeBillingGroupResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeCACertificate")
    def describe_ca_certificate(
        self, context: RequestContext, certificate_id: CertificateId
    ) -> DescribeCACertificateResponse:
        """Describes a registered CA certificate.

        Requires permission to access the
        `DescribeCACertificate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param certificate_id: The CA certificate identifier.
        :returns: DescribeCACertificateResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeCertificate")
    def describe_certificate(
        self, context: RequestContext, certificate_id: CertificateId
    ) -> DescribeCertificateResponse:
        """Gets information about the specified certificate.

        Requires permission to access the
        `DescribeCertificate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param certificate_id: The ID of the certificate.
        :returns: DescribeCertificateResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeCustomMetric")
    def describe_custom_metric(
        self, context: RequestContext, metric_name: MetricName
    ) -> DescribeCustomMetricResponse:
        """Gets information about a Device Defender detect custom metric.

        Requires permission to access the
        `DescribeCustomMetric <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param metric_name: The name of the custom metric.
        :returns: DescribeCustomMetricResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeDefaultAuthorizer")
    def describe_default_authorizer(
        self,
        context: RequestContext,
    ) -> DescribeDefaultAuthorizerResponse:
        """Describes the default authorizer.

        Requires permission to access the
        `DescribeDefaultAuthorizer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :returns: DescribeDefaultAuthorizerResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeDetectMitigationActionsTask")
    def describe_detect_mitigation_actions_task(
        self, context: RequestContext, task_id: MitigationActionsTaskId
    ) -> DescribeDetectMitigationActionsTaskResponse:
        """Gets information about a Device Defender ML Detect mitigation action.

        Requires permission to access the
        `DescribeDetectMitigationActionsTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: The unique identifier of the task.
        :returns: DescribeDetectMitigationActionsTaskResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeDimension")
    def describe_dimension(
        self, context: RequestContext, name: DimensionName
    ) -> DescribeDimensionResponse:
        """Provides details about a dimension that is defined in your Amazon Web
        Services accounts.

        Requires permission to access the
        `DescribeDimension <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param name: The unique identifier for the dimension.
        :returns: DescribeDimensionResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DescribeDomainConfiguration")
    def describe_domain_configuration(
        self, context: RequestContext, domain_configuration_name: ReservedDomainConfigurationName
    ) -> DescribeDomainConfigurationResponse:
        """Gets summary information about a domain configuration.

        Requires permission to access the
        `DescribeDomainConfiguration <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param domain_configuration_name: The name of the domain configuration.
        :returns: DescribeDomainConfigurationResponse
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InvalidRequestException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeEndpoint")
    def describe_endpoint(
        self, context: RequestContext, endpoint_type: EndpointType = None
    ) -> DescribeEndpointResponse:
        """Returns a unique endpoint specific to the Amazon Web Services account
        making the call.

        Requires permission to access the
        `DescribeEndpoint <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param endpoint_type: The endpoint type.
        :returns: DescribeEndpointResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises UnauthorizedException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DescribeEventConfigurations")
    def describe_event_configurations(
        self,
        context: RequestContext,
    ) -> DescribeEventConfigurationsResponse:
        """Describes event configurations.

        Requires permission to access the
        `DescribeEventConfigurations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :returns: DescribeEventConfigurationsResponse
        :raises InternalFailureException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DescribeFleetMetric")
    def describe_fleet_metric(
        self, context: RequestContext, metric_name: FleetMetricName
    ) -> DescribeFleetMetricResponse:
        """Gets information about the specified fleet metric.

        Requires permission to access the
        `DescribeFleetMetric <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param metric_name: The name of the fleet metric to describe.
        :returns: DescribeFleetMetricResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeIndex")
    def describe_index(
        self, context: RequestContext, index_name: IndexName
    ) -> DescribeIndexResponse:
        """Describes a search index.

        Requires permission to access the
        `DescribeIndex <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param index_name: The index name.
        :returns: DescribeIndexResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeJob")
    def describe_job(self, context: RequestContext, job_id: JobId) -> DescribeJobResponse:
        """Describes a job.

        Requires permission to access the
        `DescribeJob <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_id: The unique identifier you assigned to this job when it was created.
        :returns: DescribeJobResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeJobExecution")
    def describe_job_execution(
        self,
        context: RequestContext,
        job_id: JobId,
        thing_name: ThingName,
        execution_number: ExecutionNumber = None,
    ) -> DescribeJobExecutionResponse:
        """Describes a job execution.

        Requires permission to access the
        `DescribeJobExecution <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_id: The unique identifier you assigned to this job when it was created.
        :param thing_name: The name of the thing on which the job execution is running.
        :param execution_number: A string (consisting of the digits "0" through "9" which is used to
        specify a particular job execution on a particular device.
        :returns: DescribeJobExecutionResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeJobTemplate")
    def describe_job_template(
        self, context: RequestContext, job_template_id: JobTemplateId
    ) -> DescribeJobTemplateResponse:
        """Returns information about a job template.

        :param job_template_id: The unique identifier of the job template.
        :returns: DescribeJobTemplateResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeManagedJobTemplate")
    def describe_managed_job_template(
        self,
        context: RequestContext,
        template_name: ManagedJobTemplateName,
        template_version: ManagedTemplateVersion = None,
    ) -> DescribeManagedJobTemplateResponse:
        """View details of a managed job template.

        :param template_name: The unique name of a managed job template, which is required.
        :param template_version: An optional parameter to specify version of a managed template.
        :returns: DescribeManagedJobTemplateResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("DescribeMitigationAction")
    def describe_mitigation_action(
        self, context: RequestContext, action_name: MitigationActionName
    ) -> DescribeMitigationActionResponse:
        """Gets information about a mitigation action.

        Requires permission to access the
        `DescribeMitigationAction <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param action_name: The friendly name that uniquely identifies the mitigation action.
        :returns: DescribeMitigationActionResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeProvisioningTemplate")
    def describe_provisioning_template(
        self, context: RequestContext, template_name: TemplateName
    ) -> DescribeProvisioningTemplateResponse:
        """Returns information about a fleet provisioning template.

        Requires permission to access the
        `DescribeProvisioningTemplate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_name: The name of the fleet provisioning template.
        :returns: DescribeProvisioningTemplateResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        """
        raise NotImplementedError

    @handler("DescribeProvisioningTemplateVersion")
    def describe_provisioning_template_version(
        self, context: RequestContext, template_name: TemplateName, version_id: TemplateVersionId
    ) -> DescribeProvisioningTemplateVersionResponse:
        """Returns information about a fleet provisioning template version.

        Requires permission to access the
        `DescribeProvisioningTemplateVersion <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_name: The template name.
        :param version_id: The fleet provisioning template version ID.
        :returns: DescribeProvisioningTemplateVersionResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        :raises UnauthorizedException:
        """
        raise NotImplementedError

    @handler("DescribeRoleAlias")
    def describe_role_alias(
        self, context: RequestContext, role_alias: RoleAlias
    ) -> DescribeRoleAliasResponse:
        """Describes a role alias.

        Requires permission to access the
        `DescribeRoleAlias <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param role_alias: The role alias to describe.
        :returns: DescribeRoleAliasResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeScheduledAudit")
    def describe_scheduled_audit(
        self, context: RequestContext, scheduled_audit_name: ScheduledAuditName
    ) -> DescribeScheduledAuditResponse:
        """Gets information about a scheduled audit.

        Requires permission to access the
        `DescribeScheduledAudit <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param scheduled_audit_name: The name of the scheduled audit whose information you want to get.
        :returns: DescribeScheduledAuditResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeSecurityProfile")
    def describe_security_profile(
        self, context: RequestContext, security_profile_name: SecurityProfileName
    ) -> DescribeSecurityProfileResponse:
        """Gets information about a Device Defender security profile.

        Requires permission to access the
        `DescribeSecurityProfile <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param security_profile_name: The name of the security profile whose information you want to get.
        :returns: DescribeSecurityProfileResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeStream")
    def describe_stream(
        self, context: RequestContext, stream_id: StreamId
    ) -> DescribeStreamResponse:
        """Gets information about a stream.

        Requires permission to access the
        `DescribeStream <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param stream_id: The stream ID.
        :returns: DescribeStreamResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeThing")
    def describe_thing(
        self, context: RequestContext, thing_name: ThingName
    ) -> DescribeThingResponse:
        """Gets information about the specified thing.

        Requires permission to access the
        `DescribeThing <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The name of the thing.
        :returns: DescribeThingResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DescribeThingGroup")
    def describe_thing_group(
        self, context: RequestContext, thing_group_name: ThingGroupName
    ) -> DescribeThingGroupResponse:
        """Describe a thing group.

        Requires permission to access the
        `DescribeThingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_group_name: The name of the thing group.
        :returns: DescribeThingGroupResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeThingRegistrationTask")
    def describe_thing_registration_task(
        self, context: RequestContext, task_id: TaskId
    ) -> DescribeThingRegistrationTaskResponse:
        """Describes a bulk thing provisioning task.

        Requires permission to access the
        `DescribeThingRegistrationTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: The task ID.
        :returns: DescribeThingRegistrationTaskResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeThingType")
    def describe_thing_type(
        self, context: RequestContext, thing_type_name: ThingTypeName
    ) -> DescribeThingTypeResponse:
        """Gets information about the specified thing type.

        Requires permission to access the
        `DescribeThingType <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_type_name: The name of the thing type.
        :returns: DescribeThingTypeResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DetachPolicy")
    def detach_policy(
        self, context: RequestContext, policy_name: PolicyName, target: PolicyTarget
    ) -> None:
        """Detaches a policy from the specified target.

        Because of the distributed nature of Amazon Web Services, it can take up
        to five minutes after a policy is detached before it's ready to be
        deleted.

        Requires permission to access the
        `DetachPolicy <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The policy to detach.
        :param target: The target from which the policy will be detached.
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("DetachPrincipalPolicy")
    def detach_principal_policy(
        self, context: RequestContext, policy_name: PolicyName, principal: Principal
    ) -> None:
        """Removes the specified policy from the specified certificate.

        This action is deprecated. Please use DetachPolicy instead.

        Requires permission to access the
        `DetachPrincipalPolicy <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The name of the policy to detach.
        :param principal: The principal.
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DetachSecurityProfile")
    def detach_security_profile(
        self,
        context: RequestContext,
        security_profile_name: SecurityProfileName,
        security_profile_target_arn: SecurityProfileTargetArn,
    ) -> DetachSecurityProfileResponse:
        """Disassociates a Device Defender security profile from a thing group or
        from this account.

        Requires permission to access the
        `DetachSecurityProfile <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param security_profile_name: The security profile that is detached.
        :param security_profile_target_arn: The ARN of the thing group from which the security profile is detached.
        :returns: DetachSecurityProfileResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DetachThingPrincipal")
    def detach_thing_principal(
        self, context: RequestContext, thing_name: ThingName, principal: Principal
    ) -> DetachThingPrincipalResponse:
        """Detaches the specified principal from the specified thing. A principal
        can be X.509 certificates, IAM users, groups, and roles, Amazon Cognito
        identities or federated identities.

        This call is asynchronous. It might take several seconds for the
        detachment to propagate.

        Requires permission to access the
        `DetachThingPrincipal <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The name of the thing.
        :param principal: If the principal is a certificate, this value must be ARN of the
        certificate.
        :returns: DetachThingPrincipalResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("DisableTopicRule")
    def disable_topic_rule(self, context: RequestContext, rule_name: RuleName) -> None:
        """Disables the rule.

        Requires permission to access the
        `DisableTopicRule <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param rule_name: The name of the rule to disable.
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises UnauthorizedException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("EnableTopicRule")
    def enable_topic_rule(self, context: RequestContext, rule_name: RuleName) -> None:
        """Enables the rule.

        Requires permission to access the
        `EnableTopicRule <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param rule_name: The name of the topic rule to enable.
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises UnauthorizedException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("GetBehaviorModelTrainingSummaries")
    def get_behavior_model_training_summaries(
        self,
        context: RequestContext,
        security_profile_name: SecurityProfileName = None,
        max_results: TinyMaxResults = None,
        next_token: NextToken = None,
    ) -> GetBehaviorModelTrainingSummariesResponse:
        """Returns a Device Defender's ML Detect Security Profile training model's
        status.

        Requires permission to access the
        `GetBehaviorModelTrainingSummaries <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param security_profile_name: The name of the security profile.
        :param max_results: The maximum number of results to return at one time.
        :param next_token: The token for the next set of results.
        :returns: GetBehaviorModelTrainingSummariesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("GetBucketsAggregation")
    def get_buckets_aggregation(
        self,
        context: RequestContext,
        query_string: QueryString,
        aggregation_field: AggregationField,
        buckets_aggregation_type: BucketsAggregationType,
        index_name: IndexName = None,
        query_version: QueryVersion = None,
    ) -> GetBucketsAggregationResponse:
        """Aggregates on indexed data with search queries pertaining to particular
        fields.

        Requires permission to access the
        `GetBucketsAggregation <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param query_string: The search query string.
        :param aggregation_field: The aggregation field.
        :param buckets_aggregation_type: The basic control of the response shape and the bucket aggregation type
        to perform.
        :param index_name: The name of the index to search.
        :param query_version: The version of the query.
        :returns: GetBucketsAggregationResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises InvalidQueryException:
        :raises InvalidAggregationException:
        :raises IndexNotReadyException:
        """
        raise NotImplementedError

    @handler("GetCardinality")
    def get_cardinality(
        self,
        context: RequestContext,
        query_string: QueryString,
        index_name: IndexName = None,
        aggregation_field: AggregationField = None,
        query_version: QueryVersion = None,
    ) -> GetCardinalityResponse:
        """Returns the approximate count of unique values that match the query.

        Requires permission to access the
        `GetCardinality <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param query_string: The search query string.
        :param index_name: The name of the index to search.
        :param aggregation_field: The field to aggregate.
        :param query_version: The query version.
        :returns: GetCardinalityResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises InvalidQueryException:
        :raises InvalidAggregationException:
        :raises IndexNotReadyException:
        """
        raise NotImplementedError

    @handler("GetEffectivePolicies")
    def get_effective_policies(
        self,
        context: RequestContext,
        principal: Principal = None,
        cognito_identity_pool_id: CognitoIdentityPoolId = None,
        thing_name: ThingName = None,
    ) -> GetEffectivePoliciesResponse:
        """Gets a list of the policies that have an effect on the authorization
        behavior of the specified device when it connects to the IoT device
        gateway.

        Requires permission to access the
        `GetEffectivePolicies <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param principal: The principal.
        :param cognito_identity_pool_id: The Cognito identity pool ID.
        :param thing_name: The thing name.
        :returns: GetEffectivePoliciesResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("GetIndexingConfiguration")
    def get_indexing_configuration(
        self,
        context: RequestContext,
    ) -> GetIndexingConfigurationResponse:
        """Gets the indexing configuration.

        Requires permission to access the
        `GetIndexingConfiguration <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :returns: GetIndexingConfigurationResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetJobDocument")
    def get_job_document(self, context: RequestContext, job_id: JobId) -> GetJobDocumentResponse:
        """Gets a job document.

        Requires permission to access the
        `GetJobDocument <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_id: The unique identifier you assigned to this job when it was created.
        :returns: GetJobDocumentResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetLoggingOptions")
    def get_logging_options(
        self,
        context: RequestContext,
    ) -> GetLoggingOptionsResponse:
        """Gets the logging options.

        NOTE: use of this command is not recommended. Use
        ``GetV2LoggingOptions`` instead.

        Requires permission to access the
        `GetLoggingOptions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :returns: GetLoggingOptionsResponse
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetOTAUpdate")
    def get_ota_update(
        self, context: RequestContext, ota_update_id: OTAUpdateId
    ) -> GetOTAUpdateResponse:
        """Gets an OTA update.

        Requires permission to access the
        `GetOTAUpdate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param ota_update_id: The OTA update ID.
        :returns: GetOTAUpdateResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("GetPercentiles")
    def get_percentiles(
        self,
        context: RequestContext,
        query_string: QueryString,
        index_name: IndexName = None,
        aggregation_field: AggregationField = None,
        query_version: QueryVersion = None,
        percents: PercentList = None,
    ) -> GetPercentilesResponse:
        """Groups the aggregated values that match the query into percentile
        groupings. The default percentile groupings are: 1,5,25,50,75,95,99,
        although you can specify your own when you call ``GetPercentiles``. This
        function returns a value for each percentile group specified (or the
        default percentile groupings). The percentile group "1" contains the
        aggregated field value that occurs in approximately one percent of the
        values that match the query. The percentile group "5" contains the
        aggregated field value that occurs in approximately five percent of the
        values that match the query, and so on. The result is an approximation,
        the more values that match the query, the more accurate the percentile
        values.

        Requires permission to access the
        `GetPercentiles <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param query_string: The search query string.
        :param index_name: The name of the index to search.
        :param aggregation_field: The field to aggregate.
        :param query_version: The query version.
        :param percents: The percentile groups returned.
        :returns: GetPercentilesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises InvalidQueryException:
        :raises InvalidAggregationException:
        :raises IndexNotReadyException:
        """
        raise NotImplementedError

    @handler("GetPolicy")
    def get_policy(self, context: RequestContext, policy_name: PolicyName) -> GetPolicyResponse:
        """Gets information about the specified policy with the policy document of
        the default version.

        Requires permission to access the
        `GetPolicy <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The name of the policy.
        :returns: GetPolicyResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetPolicyVersion")
    def get_policy_version(
        self, context: RequestContext, policy_name: PolicyName, policy_version_id: PolicyVersionId
    ) -> GetPolicyVersionResponse:
        """Gets information about the specified policy version.

        Requires permission to access the
        `GetPolicyVersion <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The name of the policy.
        :param policy_version_id: The policy version ID.
        :returns: GetPolicyVersionResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("GetRegistrationCode")
    def get_registration_code(
        self,
        context: RequestContext,
    ) -> GetRegistrationCodeResponse:
        """Gets a registration code used to register a CA certificate with IoT.

        Requires permission to access the
        `GetRegistrationCode <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :returns: GetRegistrationCodeResponse
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("GetStatistics")
    def get_statistics(
        self,
        context: RequestContext,
        query_string: QueryString,
        index_name: IndexName = None,
        aggregation_field: AggregationField = None,
        query_version: QueryVersion = None,
    ) -> GetStatisticsResponse:
        """Returns the count, average, sum, minimum, maximum, sum of squares,
        variance, and standard deviation for the specified aggregated field. If
        the aggregation field is of type ``String``, only the count statistic is
        returned.

        Requires permission to access the
        `GetStatistics <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param query_string: The query used to search.
        :param index_name: The name of the index to search.
        :param aggregation_field: The aggregation field name.
        :param query_version: The version of the query used to search.
        :returns: GetStatisticsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises InvalidQueryException:
        :raises InvalidAggregationException:
        :raises IndexNotReadyException:
        """
        raise NotImplementedError

    @handler("GetTopicRule")
    def get_topic_rule(self, context: RequestContext, rule_name: RuleName) -> GetTopicRuleResponse:
        """Gets information about the rule.

        Requires permission to access the
        `GetTopicRule <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param rule_name: The name of the rule.
        :returns: GetTopicRuleResponse
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises UnauthorizedException:
        """
        raise NotImplementedError

    @handler("GetTopicRuleDestination")
    def get_topic_rule_destination(
        self, context: RequestContext, arn: AwsArn
    ) -> GetTopicRuleDestinationResponse:
        """Gets information about a topic rule destination.

        Requires permission to access the
        `GetTopicRuleDestination <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param arn: The ARN of the topic rule destination.
        :returns: GetTopicRuleDestinationResponse
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises UnauthorizedException:
        """
        raise NotImplementedError

    @handler("GetV2LoggingOptions")
    def get_v2_logging_options(
        self,
        context: RequestContext,
    ) -> GetV2LoggingOptionsResponse:
        """Gets the fine grained logging options.

        Requires permission to access the
        `GetV2LoggingOptions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :returns: GetV2LoggingOptionsResponse
        :raises InternalException:
        :raises NotConfiguredException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListActiveViolations")
    def list_active_violations(
        self,
        context: RequestContext,
        thing_name: DeviceDefenderThingName = None,
        security_profile_name: SecurityProfileName = None,
        behavior_criteria_type: BehaviorCriteriaType = None,
        list_suppressed_alerts: ListSuppressedAlerts = None,
        verification_state: VerificationState = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListActiveViolationsResponse:
        """Lists the active violations for a given Device Defender security
        profile.

        Requires permission to access the
        `ListActiveViolations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The name of the thing whose active violations are listed.
        :param security_profile_name: The name of the Device Defender security profile for which violations
        are listed.
        :param behavior_criteria_type: The criteria for a behavior.
        :param list_suppressed_alerts: A list of all suppressed alerts.
        :param verification_state: The verification state of the violation (detect alarm).
        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListActiveViolationsResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListAttachedPolicies")
    def list_attached_policies(
        self,
        context: RequestContext,
        target: PolicyTarget,
        recursive: Recursive = None,
        marker: Marker = None,
        page_size: PageSize = None,
    ) -> ListAttachedPoliciesResponse:
        """Lists the policies attached to the specified thing group.

        Requires permission to access the
        `ListAttachedPolicies <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param target: The group or principal for which the policies will be listed.
        :param recursive: When true, recursively list attached policies.
        :param marker: The token to retrieve the next set of results.
        :param page_size: The maximum number of results to be returned per request.
        :returns: ListAttachedPoliciesResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("ListAuditFindings")
    def list_audit_findings(
        self,
        context: RequestContext,
        task_id: AuditTaskId = None,
        check_name: AuditCheckName = None,
        resource_identifier: ResourceIdentifier = None,
        max_results: MaxResults = None,
        next_token: NextToken = None,
        start_time: Timestamp = None,
        end_time: Timestamp = None,
        list_suppressed_findings: ListSuppressedFindings = None,
    ) -> ListAuditFindingsResponse:
        """Lists the findings (results) of a Device Defender audit or of the audits
        performed during a specified time period. (Findings are retained for 90
        days.)

        Requires permission to access the
        `ListAuditFindings <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: A filter to limit results to the audit with the specified ID.
        :param check_name: A filter to limit results to the findings for the specified audit check.
        :param resource_identifier: Information identifying the noncompliant resource.
        :param max_results: The maximum number of results to return at one time.
        :param next_token: The token for the next set of results.
        :param start_time: A filter to limit results to those found after the specified time.
        :param end_time: A filter to limit results to those found before the specified time.
        :param list_suppressed_findings: Boolean flag indicating whether only the suppressed findings or the
        unsuppressed findings should be listed.
        :returns: ListAuditFindingsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListAuditMitigationActionsExecutions")
    def list_audit_mitigation_actions_executions(
        self,
        context: RequestContext,
        task_id: MitigationActionsTaskId,
        finding_id: FindingId,
        action_status: AuditMitigationActionsExecutionStatus = None,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListAuditMitigationActionsExecutionsResponse:
        """Gets the status of audit mitigation action tasks that were executed.

        Requires permission to access the
        `ListAuditMitigationActionsExecutions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: Specify this filter to limit results to actions for a specific audit
        mitigation actions task.
        :param finding_id: Specify this filter to limit results to those that were applied to a
        specific audit finding.
        :param action_status: Specify this filter to limit results to those with a specific status.
        :param max_results: The maximum number of results to return at one time.
        :param next_token: The token for the next set of results.
        :returns: ListAuditMitigationActionsExecutionsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListAuditMitigationActionsTasks")
    def list_audit_mitigation_actions_tasks(
        self,
        context: RequestContext,
        start_time: Timestamp,
        end_time: Timestamp,
        audit_task_id: AuditTaskId = None,
        finding_id: FindingId = None,
        task_status: AuditMitigationActionsTaskStatus = None,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListAuditMitigationActionsTasksResponse:
        """Gets a list of audit mitigation action tasks that match the specified
        filters.

        Requires permission to access the
        `ListAuditMitigationActionsTasks <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param start_time: Specify this filter to limit results to tasks that began on or after a
        specific date and time.
        :param end_time: Specify this filter to limit results to tasks that were completed or
        canceled on or before a specific date and time.
        :param audit_task_id: Specify this filter to limit results to tasks that were applied to
        results for a specific audit.
        :param finding_id: Specify this filter to limit results to tasks that were applied to a
        specific audit finding.
        :param task_status: Specify this filter to limit results to tasks that are in a specific
        state.
        :param max_results: The maximum number of results to return at one time.
        :param next_token: The token for the next set of results.
        :returns: ListAuditMitigationActionsTasksResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListAuditSuppressions")
    def list_audit_suppressions(
        self,
        context: RequestContext,
        check_name: AuditCheckName = None,
        resource_identifier: ResourceIdentifier = None,
        ascending_order: AscendingOrder = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListAuditSuppressionsResponse:
        """Lists your Device Defender audit listings.

        Requires permission to access the
        `ListAuditSuppressions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param check_name: An audit check name.
        :param resource_identifier: Information that identifies the noncompliant resource.
        :param ascending_order: Determines whether suppressions are listed in ascending order by
        expiration date or not.
        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListAuditSuppressionsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListAuditTasks")
    def list_audit_tasks(
        self,
        context: RequestContext,
        start_time: Timestamp,
        end_time: Timestamp,
        task_type: AuditTaskType = None,
        task_status: AuditTaskStatus = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListAuditTasksResponse:
        """Lists the Device Defender audits that have been performed during a given
        time period.

        Requires permission to access the
        `ListAuditTasks <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param start_time: The beginning of the time period.
        :param end_time: The end of the time period.
        :param task_type: A filter to limit the output to the specified type of audit: can be one
        of "ON_DEMAND_AUDIT_TASK" or "SCHEDULED__AUDIT_TASK".
        :param task_status: A filter to limit the output to audits with the specified completion
        status: can be one of "IN_PROGRESS", "COMPLETED", "FAILED", or
        "CANCELED".
        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListAuditTasksResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListAuthorizers")
    def list_authorizers(
        self,
        context: RequestContext,
        page_size: PageSize = None,
        marker: Marker = None,
        ascending_order: AscendingOrder = None,
        status: AuthorizerStatus = None,
    ) -> ListAuthorizersResponse:
        """Lists the authorizers registered in your account.

        Requires permission to access the
        `ListAuthorizers <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param page_size: The maximum number of results to return at one time.
        :param marker: A marker used to get the next set of results.
        :param ascending_order: Return the list of authorizers in ascending alphabetical order.
        :param status: The status of the list authorizers request.
        :returns: ListAuthorizersResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListBillingGroups")
    def list_billing_groups(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
        name_prefix_filter: BillingGroupName = None,
    ) -> ListBillingGroupsResponse:
        """Lists the billing groups you have created.

        Requires permission to access the
        `ListBillingGroups <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return per request.
        :param name_prefix_filter: Limit the results to billing groups whose names have the given prefix.
        :returns: ListBillingGroupsResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListCACertificates")
    def list_ca_certificates(
        self,
        context: RequestContext,
        page_size: PageSize = None,
        marker: Marker = None,
        ascending_order: AscendingOrder = None,
    ) -> ListCACertificatesResponse:
        """Lists the CA certificates registered for your Amazon Web Services
        account.

        The results are paginated with a default page size of 25. You can use
        the returned marker to retrieve additional results.

        Requires permission to access the
        `ListCACertificates <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param page_size: The result page size.
        :param marker: The marker for the next set of results.
        :param ascending_order: Determines the order of the results.
        :returns: ListCACertificatesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListCertificates")
    def list_certificates(
        self,
        context: RequestContext,
        page_size: PageSize = None,
        marker: Marker = None,
        ascending_order: AscendingOrder = None,
    ) -> ListCertificatesResponse:
        """Lists the certificates registered in your Amazon Web Services account.

        The results are paginated with a default page size of 25. You can use
        the returned marker to retrieve additional results.

        Requires permission to access the
        `ListCertificates <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param page_size: The result page size.
        :param marker: The marker for the next set of results.
        :param ascending_order: Specifies the order for results.
        :returns: ListCertificatesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListCertificatesByCA")
    def list_certificates_by_ca(
        self,
        context: RequestContext,
        ca_certificate_id: CertificateId,
        page_size: PageSize = None,
        marker: Marker = None,
        ascending_order: AscendingOrder = None,
    ) -> ListCertificatesByCAResponse:
        """List the device certificates signed by the specified CA certificate.

        Requires permission to access the
        `ListCertificatesByCA <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param ca_certificate_id: The ID of the CA certificate.
        :param page_size: The result page size.
        :param marker: The marker for the next set of results.
        :param ascending_order: Specifies the order for results.
        :returns: ListCertificatesByCAResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListCustomMetrics")
    def list_custom_metrics(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListCustomMetricsResponse:
        """Lists your Device Defender detect custom metrics.

        Requires permission to access the
        `ListCustomMetrics <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListCustomMetricsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListDetectMitigationActionsExecutions")
    def list_detect_mitigation_actions_executions(
        self,
        context: RequestContext,
        task_id: MitigationActionsTaskId = None,
        violation_id: ViolationId = None,
        thing_name: DeviceDefenderThingName = None,
        start_time: Timestamp = None,
        end_time: Timestamp = None,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListDetectMitigationActionsExecutionsResponse:
        """Lists mitigation actions executions for a Device Defender ML Detect
        Security Profile.

        Requires permission to access the
        `ListDetectMitigationActionsExecutions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: The unique identifier of the task.
        :param violation_id: The unique identifier of the violation.
        :param thing_name: The name of the thing whose mitigation actions are listed.
        :param start_time: A filter to limit results to those found after the specified time.
        :param end_time: The end of the time period for which ML Detect mitigation actions
        executions are returned.
        :param max_results: The maximum number of results to return at one time.
        :param next_token: The token for the next set of results.
        :returns: ListDetectMitigationActionsExecutionsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListDetectMitigationActionsTasks")
    def list_detect_mitigation_actions_tasks(
        self,
        context: RequestContext,
        start_time: Timestamp,
        end_time: Timestamp,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListDetectMitigationActionsTasksResponse:
        """List of Device Defender ML Detect mitigation actions tasks.

        Requires permission to access the
        `ListDetectMitigationActionsTasks <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param start_time: A filter to limit results to those found after the specified time.
        :param end_time: The end of the time period for which ML Detect mitigation actions tasks
        are returned.
        :param max_results: The maximum number of results to return at one time.
        :param next_token: The token for the next set of results.
        :returns: ListDetectMitigationActionsTasksResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListDimensions")
    def list_dimensions(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListDimensionsResponse:
        """List the set of dimensions that are defined for your Amazon Web Services
        accounts.

        Requires permission to access the
        `ListDimensions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to retrieve at one time.
        :returns: ListDimensionsResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListDomainConfigurations")
    def list_domain_configurations(
        self,
        context: RequestContext,
        marker: Marker = None,
        page_size: PageSize = None,
        service_type: ServiceType = None,
    ) -> ListDomainConfigurationsResponse:
        """Gets a list of domain configurations for the user. This list is sorted
        alphabetically by domain configuration name.

        Requires permission to access the
        `ListDomainConfigurations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param marker: The marker for the next set of results.
        :param page_size: The result page size.
        :param service_type: The type of service delivered by the endpoint.
        :returns: ListDomainConfigurationsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListFleetMetrics")
    def list_fleet_metrics(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListFleetMetricsResponse:
        """Lists all your fleet metrics.

        Requires permission to access the
        `ListFleetMetrics <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise ``null`` to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :returns: ListFleetMetricsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListIndices")
    def list_indices(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        max_results: QueryMaxResults = None,
    ) -> ListIndicesResponse:
        """Lists the search indices.

        Requires permission to access the
        `ListIndices <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param next_token: The token used to get the next set of results, or ``null`` if there are
        no additional results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListIndicesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListJobExecutionsForJob")
    def list_job_executions_for_job(
        self,
        context: RequestContext,
        job_id: JobId,
        status: JobExecutionStatus = None,
        max_results: LaserMaxResults = None,
        next_token: NextToken = None,
    ) -> ListJobExecutionsForJobResponse:
        """Lists the job executions for a job.

        Requires permission to access the
        `ListJobExecutionsForJob <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_id: The unique identifier you assigned to this job when it was created.
        :param status: The status of the job.
        :param max_results: The maximum number of results to be returned per request.
        :param next_token: The token to retrieve the next set of results.
        :returns: ListJobExecutionsForJobResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListJobExecutionsForThing")
    def list_job_executions_for_thing(
        self,
        context: RequestContext,
        thing_name: ThingName,
        status: JobExecutionStatus = None,
        namespace_id: NamespaceId = None,
        max_results: LaserMaxResults = None,
        next_token: NextToken = None,
        job_id: JobId = None,
    ) -> ListJobExecutionsForThingResponse:
        """Lists the job executions for the specified thing.

        Requires permission to access the
        `ListJobExecutionsForThing <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The thing name.
        :param status: An optional filter that lets you search for jobs that have the specified
        status.
        :param namespace_id: The namespace used to indicate that a job is a customer-managed job.
        :param max_results: The maximum number of results to be returned per request.
        :param next_token: The token to retrieve the next set of results.
        :param job_id: The unique identifier you assigned to this job when it was created.
        :returns: ListJobExecutionsForThingResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListJobTemplates")
    def list_job_templates(
        self,
        context: RequestContext,
        max_results: LaserMaxResults = None,
        next_token: NextToken = None,
    ) -> ListJobTemplatesResponse:
        """Returns a list of job templates.

        Requires permission to access the
        `ListJobTemplates <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param max_results: The maximum number of results to return in the list.
        :param next_token: The token to use to return the next set of results in the list.
        :returns: ListJobTemplatesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListJobs")
    def list_jobs(
        self,
        context: RequestContext,
        status: JobStatus = None,
        target_selection: TargetSelection = None,
        max_results: LaserMaxResults = None,
        next_token: NextToken = None,
        thing_group_name: ThingGroupName = None,
        thing_group_id: ThingGroupId = None,
        namespace_id: NamespaceId = None,
    ) -> ListJobsResponse:
        """Lists jobs.

        Requires permission to access the
        `ListJobs <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param status: An optional filter that lets you search for jobs that have the specified
        status.
        :param target_selection: Specifies whether the job will continue to run (CONTINUOUS), or will be
        complete after all those things specified as targets have completed the
        job (SNAPSHOT).
        :param max_results: The maximum number of results to return per request.
        :param next_token: The token to retrieve the next set of results.
        :param thing_group_name: A filter that limits the returned jobs to those for the specified group.
        :param thing_group_id: A filter that limits the returned jobs to those for the specified group.
        :param namespace_id: The namespace used to indicate that a job is a customer-managed job.
        :returns: ListJobsResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListManagedJobTemplates")
    def list_managed_job_templates(
        self,
        context: RequestContext,
        template_name: ManagedJobTemplateName = None,
        max_results: LaserMaxResults = None,
        next_token: NextToken = None,
    ) -> ListManagedJobTemplatesResponse:
        """Returns a list of managed job templates.

        :param template_name: An optional parameter for template name.
        :param max_results: Maximum number of entries that can be returned.
        :param next_token: The token to retrieve the next set of results.
        :returns: ListManagedJobTemplatesResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalServerException:
        """
        raise NotImplementedError

    @handler("ListMetricValues")
    def list_metric_values(
        self,
        context: RequestContext,
        thing_name: DeviceDefenderThingName,
        metric_name: BehaviorMetric,
        start_time: Timestamp,
        end_time: Timestamp,
        dimension_name: DimensionName = None,
        dimension_value_operator: DimensionValueOperator = None,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListMetricValuesResponse:
        """Lists the values reported for an IoT Device Defender metric (device-side
        metric, cloud-side metric, or custom metric) by the given thing during
        the specified time period.

        :param thing_name: The name of the thing for which security profile metric values are
        returned.
        :param metric_name: The name of the security profile metric for which values are returned.
        :param start_time: The start of the time period for which metric values are returned.
        :param end_time: The end of the time period for which metric values are returned.
        :param dimension_name: The dimension name.
        :param dimension_value_operator: The dimension value operator.
        :param max_results: The maximum number of results to return at one time.
        :param next_token: The token for the next set of results.
        :returns: ListMetricValuesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListMitigationActions")
    def list_mitigation_actions(
        self,
        context: RequestContext,
        action_type: MitigationActionType = None,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListMitigationActionsResponse:
        """Gets a list of all mitigation actions that match the specified filter
        criteria.

        Requires permission to access the
        `ListMitigationActions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param action_type: Specify a value to limit the result to mitigation actions with a
        specific action type.
        :param max_results: The maximum number of results to return at one time.
        :param next_token: The token for the next set of results.
        :returns: ListMitigationActionsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListOTAUpdates")
    def list_ota_updates(
        self,
        context: RequestContext,
        max_results: MaxResults = None,
        next_token: NextToken = None,
        ota_update_status: OTAUpdateStatus = None,
    ) -> ListOTAUpdatesResponse:
        """Lists OTA updates.

        Requires permission to access the
        `ListOTAUpdates <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param max_results: The maximum number of results to return at one time.
        :param next_token: A token used to retrieve the next set of results.
        :param ota_update_status: The OTA update job status.
        :returns: ListOTAUpdatesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListOutgoingCertificates")
    def list_outgoing_certificates(
        self,
        context: RequestContext,
        page_size: PageSize = None,
        marker: Marker = None,
        ascending_order: AscendingOrder = None,
    ) -> ListOutgoingCertificatesResponse:
        """Lists certificates that are being transferred but not yet accepted.

        Requires permission to access the
        `ListOutgoingCertificates <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param page_size: The result page size.
        :param marker: The marker for the next set of results.
        :param ascending_order: Specifies the order for results.
        :returns: ListOutgoingCertificatesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListPolicies")
    def list_policies(
        self,
        context: RequestContext,
        marker: Marker = None,
        page_size: PageSize = None,
        ascending_order: AscendingOrder = None,
    ) -> ListPoliciesResponse:
        """Lists your policies.

        Requires permission to access the
        `ListPolicies <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param marker: The marker for the next set of results.
        :param page_size: The result page size.
        :param ascending_order: Specifies the order for results.
        :returns: ListPoliciesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListPolicyPrincipals")
    def list_policy_principals(
        self,
        context: RequestContext,
        policy_name: PolicyName,
        marker: Marker = None,
        page_size: PageSize = None,
        ascending_order: AscendingOrder = None,
    ) -> ListPolicyPrincipalsResponse:
        """Lists the principals associated with the specified policy.

        **Note:** This action is deprecated. Please use ListTargetsForPolicy
        instead.

        Requires permission to access the
        `ListPolicyPrincipals <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The policy name.
        :param marker: The marker for the next set of results.
        :param page_size: The result page size.
        :param ascending_order: Specifies the order for results.
        :returns: ListPolicyPrincipalsResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListPolicyVersions")
    def list_policy_versions(
        self, context: RequestContext, policy_name: PolicyName
    ) -> ListPolicyVersionsResponse:
        """Lists the versions of the specified policy and identifies the default
        version.

        Requires permission to access the
        `ListPolicyVersions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The policy name.
        :returns: ListPolicyVersionsResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListPrincipalPolicies")
    def list_principal_policies(
        self,
        context: RequestContext,
        principal: Principal,
        marker: Marker = None,
        page_size: PageSize = None,
        ascending_order: AscendingOrder = None,
    ) -> ListPrincipalPoliciesResponse:
        """Lists the policies attached to the specified principal. If you use an
        Cognito identity, the ID must be in `AmazonCognito Identity
        format <https://docs.aws.amazon.com/cognitoidentity/latest/APIReference/API_GetCredentialsForIdentity.html#API_GetCredentialsForIdentity_RequestSyntax>`__.

        **Note:** This action is deprecated. Please use ListAttachedPolicies
        instead.

        Requires permission to access the
        `ListPrincipalPolicies <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param principal: The principal.
        :param marker: The marker for the next set of results.
        :param page_size: The result page size.
        :param ascending_order: Specifies the order for results.
        :returns: ListPrincipalPoliciesResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListPrincipalThings")
    def list_principal_things(
        self,
        context: RequestContext,
        principal: Principal,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
    ) -> ListPrincipalThingsResponse:
        """Lists the things associated with the specified principal. A principal
        can be X.509 certificates, IAM users, groups, and roles, Amazon Cognito
        identities or federated identities.

        Requires permission to access the
        `ListPrincipalThings <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param principal: The principal.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :returns: ListPrincipalThingsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListProvisioningTemplateVersions")
    def list_provisioning_template_versions(
        self,
        context: RequestContext,
        template_name: TemplateName,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListProvisioningTemplateVersionsResponse:
        """A list of fleet provisioning template versions.

        Requires permission to access the
        `ListProvisioningTemplateVersions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_name: The name of the fleet provisioning template.
        :param max_results: The maximum number of results to return at one time.
        :param next_token: A token to retrieve the next set of results.
        :returns: ListProvisioningTemplateVersionsResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        :raises UnauthorizedException:
        """
        raise NotImplementedError

    @handler("ListProvisioningTemplates")
    def list_provisioning_templates(
        self, context: RequestContext, max_results: MaxResults = None, next_token: NextToken = None
    ) -> ListProvisioningTemplatesResponse:
        """Lists the fleet provisioning templates in your Amazon Web Services
        account.

        Requires permission to access the
        `ListProvisioningTemplates <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param max_results: The maximum number of results to return at one time.
        :param next_token: A token to retrieve the next set of results.
        :returns: ListProvisioningTemplatesResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        """
        raise NotImplementedError

    @handler("ListRoleAliases")
    def list_role_aliases(
        self,
        context: RequestContext,
        page_size: PageSize = None,
        marker: Marker = None,
        ascending_order: AscendingOrder = None,
    ) -> ListRoleAliasesResponse:
        """Lists the role aliases registered in your account.

        Requires permission to access the
        `ListRoleAliases <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param page_size: The maximum number of results to return at one time.
        :param marker: A marker used to get the next set of results.
        :param ascending_order: Return the list of role aliases in ascending alphabetical order.
        :returns: ListRoleAliasesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListScheduledAudits")
    def list_scheduled_audits(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListScheduledAuditsResponse:
        """Lists all of your scheduled audits.

        Requires permission to access the
        `ListScheduledAudits <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListScheduledAuditsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListSecurityProfiles")
    def list_security_profiles(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        max_results: MaxResults = None,
        dimension_name: DimensionName = None,
        metric_name: MetricName = None,
    ) -> ListSecurityProfilesResponse:
        """Lists the Device Defender security profiles you've created. You can
        filter security profiles by dimension or custom metric.

        Requires permission to access the
        `ListSecurityProfiles <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        ``dimensionName`` and ``metricName`` cannot be used in the same request.

        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return at one time.
        :param dimension_name: A filter to limit results to the security profiles that use the defined
        dimension.
        :param metric_name: The name of the custom metric.
        :returns: ListSecurityProfilesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListSecurityProfilesForTarget")
    def list_security_profiles_for_target(
        self,
        context: RequestContext,
        security_profile_target_arn: SecurityProfileTargetArn,
        next_token: NextToken = None,
        max_results: MaxResults = None,
        recursive: Recursive = None,
    ) -> ListSecurityProfilesForTargetResponse:
        """Lists the Device Defender security profiles attached to a target (thing
        group).

        Requires permission to access the
        `ListSecurityProfilesForTarget <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param security_profile_target_arn: The ARN of the target (thing group) whose attached security profiles you
        want to get.
        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return at one time.
        :param recursive: If true, return child groups too.
        :returns: ListSecurityProfilesForTargetResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListStreams")
    def list_streams(
        self,
        context: RequestContext,
        max_results: MaxResults = None,
        next_token: NextToken = None,
        ascending_order: AscendingOrder = None,
    ) -> ListStreamsResponse:
        """Lists all of the streams in your Amazon Web Services account.

        Requires permission to access the
        `ListStreams <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param max_results: The maximum number of results to return at a time.
        :param next_token: A token used to get the next set of results.
        :param ascending_order: Set to true to return the list of streams in ascending order.
        :returns: ListStreamsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: ResourceArn, next_token: NextToken = None
    ) -> ListTagsForResourceResponse:
        """Lists the tags (metadata) you have assigned to the resource.

        Requires permission to access the
        `ListTagsForResource <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param resource_arn: The ARN of the resource.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :returns: ListTagsForResourceResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListTargetsForPolicy")
    def list_targets_for_policy(
        self,
        context: RequestContext,
        policy_name: PolicyName,
        marker: Marker = None,
        page_size: PageSize = None,
    ) -> ListTargetsForPolicyResponse:
        """List targets for the specified policy.

        Requires permission to access the
        `ListTargetsForPolicy <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The policy name.
        :param marker: A marker used to get the next set of results.
        :param page_size: The maximum number of results to return at one time.
        :returns: ListTargetsForPolicyResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("ListTargetsForSecurityProfile")
    def list_targets_for_security_profile(
        self,
        context: RequestContext,
        security_profile_name: SecurityProfileName,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListTargetsForSecurityProfileResponse:
        """Lists the targets (thing groups) associated with a given Device Defender
        security profile.

        Requires permission to access the
        `ListTargetsForSecurityProfile <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param security_profile_name: The security profile.
        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListTargetsForSecurityProfileResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListThingGroups")
    def list_thing_groups(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
        parent_group: ThingGroupName = None,
        name_prefix_filter: ThingGroupName = None,
        recursive: RecursiveWithoutDefault = None,
    ) -> ListThingGroupsResponse:
        """List the thing groups in your account.

        Requires permission to access the
        `ListThingGroups <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return at one time.
        :param parent_group: A filter that limits the results to those with the specified parent
        group.
        :param name_prefix_filter: A filter that limits the results to those with the specified name
        prefix.
        :param recursive: If true, return child groups as well.
        :returns: ListThingGroupsResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListThingGroupsForThing")
    def list_thing_groups_for_thing(
        self,
        context: RequestContext,
        thing_name: ThingName,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
    ) -> ListThingGroupsForThingResponse:
        """List the thing groups to which the specified thing belongs.

        Requires permission to access the
        `ListThingGroupsForThing <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The thing name.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListThingGroupsForThingResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListThingPrincipals")
    def list_thing_principals(
        self,
        context: RequestContext,
        thing_name: ThingName,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
    ) -> ListThingPrincipalsResponse:
        """Lists the principals associated with the specified thing. A principal
        can be X.509 certificates, IAM users, groups, and roles, Amazon Cognito
        identities or federated identities.

        Requires permission to access the
        `ListThingPrincipals <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The name of the thing.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :returns: ListThingPrincipalsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListThingRegistrationTaskReports")
    def list_thing_registration_task_reports(
        self,
        context: RequestContext,
        task_id: TaskId,
        report_type: ReportType,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
    ) -> ListThingRegistrationTaskReportsResponse:
        """Information about the thing registration tasks.

        :param task_id: The id of the task.
        :param report_type: The type of task report.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return per request.
        :returns: ListThingRegistrationTaskReportsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListThingRegistrationTasks")
    def list_thing_registration_tasks(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
        status: Status = None,
    ) -> ListThingRegistrationTasksResponse:
        """List bulk thing provisioning tasks.

        Requires permission to access the
        `ListThingRegistrationTasks <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return at one time.
        :param status: The status of the bulk thing provisioning task.
        :returns: ListThingRegistrationTasksResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListThingTypes")
    def list_thing_types(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
        thing_type_name: ThingTypeName = None,
    ) -> ListThingTypesResponse:
        """Lists the existing thing types.

        Requires permission to access the
        `ListThingTypes <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :param thing_type_name: The name of the thing type.
        :returns: ListThingTypesResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListThings")
    def list_things(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
        attribute_name: AttributeName = None,
        attribute_value: AttributeValue = None,
        thing_type_name: ThingTypeName = None,
        use_prefix_attribute_value: usePrefixAttributeValue = None,
    ) -> ListThingsResponse:
        """Lists your things. Use the **attributeName** and **attributeValue**
        parameters to filter your things. For example, calling ``ListThings``
        with attributeName=Color and attributeValue=Red retrieves all things in
        the registry that contain an attribute **Color** with the value **Red**.

        Requires permission to access the
        `ListThings <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        You will not be charged for calling this API if an ``Access denied``
        error is returned. You will also not be charged if no attributes or
        pagination token was provided in request and no pagination token and no
        results were returned.

        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return in this operation.
        :param attribute_name: The attribute name used to search for things.
        :param attribute_value: The attribute value used to search for things.
        :param thing_type_name: The name of the thing type used to search for things.
        :param use_prefix_attribute_value: When ``true``, the action returns the thing resources with attribute
        values that start with the ``attributeValue`` provided.
        :returns: ListThingsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("ListThingsInBillingGroup")
    def list_things_in_billing_group(
        self,
        context: RequestContext,
        billing_group_name: BillingGroupName,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
    ) -> ListThingsInBillingGroupResponse:
        """Lists the things you have added to the given billing group.

        Requires permission to access the
        `ListThingsInBillingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param billing_group_name: The name of the billing group.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return per request.
        :returns: ListThingsInBillingGroupResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListThingsInThingGroup")
    def list_things_in_thing_group(
        self,
        context: RequestContext,
        thing_group_name: ThingGroupName,
        recursive: Recursive = None,
        next_token: NextToken = None,
        max_results: RegistryMaxResults = None,
    ) -> ListThingsInThingGroupResponse:
        """Lists the things in the specified group.

        Requires permission to access the
        `ListThingsInThingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_group_name: The thing group name.
        :param recursive: When true, list things in this thing group and in all child groups as
        well.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListThingsInThingGroupResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListTopicRuleDestinations")
    def list_topic_rule_destinations(
        self,
        context: RequestContext,
        max_results: TopicRuleDestinationMaxResults = None,
        next_token: NextToken = None,
    ) -> ListTopicRuleDestinationsResponse:
        """Lists all the topic rule destinations in your Amazon Web Services
        account.

        Requires permission to access the
        `ListTopicRuleDestinations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param max_results: The maximum number of results to return at one time.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :returns: ListTopicRuleDestinationsResponse
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises UnauthorizedException:
        """
        raise NotImplementedError

    @handler("ListTopicRules")
    def list_topic_rules(
        self,
        context: RequestContext,
        topic: Topic = None,
        max_results: TopicRuleMaxResults = None,
        next_token: NextToken = None,
        rule_disabled: IsDisabled = None,
    ) -> ListTopicRulesResponse:
        """Lists the rules for the specific topic.

        Requires permission to access the
        `ListTopicRules <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param topic: The topic.
        :param max_results: The maximum number of results to return.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param rule_disabled: Specifies whether the rule is disabled.
        :returns: ListTopicRulesResponse
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListV2LoggingLevels")
    def list_v2_logging_levels(
        self,
        context: RequestContext,
        target_type: LogTargetType = None,
        next_token: NextToken = None,
        max_results: SkyfallMaxResults = None,
    ) -> ListV2LoggingLevelsResponse:
        """Lists logging levels.

        Requires permission to access the
        `ListV2LoggingLevels <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param target_type: The type of resource for which you are configuring logging.
        :param next_token: To retrieve the next set of results, the ``nextToken`` value from a
        previous response; otherwise **null** to receive the first set of
        results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListV2LoggingLevelsResponse
        :raises InternalException:
        :raises NotConfiguredException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListViolationEvents")
    def list_violation_events(
        self,
        context: RequestContext,
        start_time: Timestamp,
        end_time: Timestamp,
        thing_name: DeviceDefenderThingName = None,
        security_profile_name: SecurityProfileName = None,
        behavior_criteria_type: BehaviorCriteriaType = None,
        list_suppressed_alerts: ListSuppressedAlerts = None,
        verification_state: VerificationState = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListViolationEventsResponse:
        """Lists the Device Defender security profile violations discovered during
        the given time period. You can use filters to limit the results to those
        alerts issued for a particular security profile, behavior, or thing
        (device).

        Requires permission to access the
        `ListViolationEvents <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param start_time: The start time for the alerts to be listed.
        :param end_time: The end time for the alerts to be listed.
        :param thing_name: A filter to limit results to those alerts caused by the specified thing.
        :param security_profile_name: A filter to limit results to those alerts generated by the specified
        security profile.
        :param behavior_criteria_type: The criteria for a behavior.
        :param list_suppressed_alerts: A list of all suppressed alerts.
        :param verification_state: The verification state of the violation (detect alarm).
        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return at one time.
        :returns: ListViolationEventsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("PutVerificationStateOnViolation")
    def put_verification_state_on_violation(
        self,
        context: RequestContext,
        violation_id: ViolationId,
        verification_state: VerificationState,
        verification_state_description: VerificationStateDescription = None,
    ) -> PutVerificationStateOnViolationResponse:
        """Set a verification state and provide a description of that verification
        state on a violation (detect alarm).

        :param violation_id: The violation ID.
        :param verification_state: The verification state of the violation.
        :param verification_state_description: The description of the verification state of the violation (detect
        alarm).
        :returns: PutVerificationStateOnViolationResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("RegisterCACertificate")
    def register_ca_certificate(
        self,
        context: RequestContext,
        ca_certificate: CertificatePem,
        verification_certificate: CertificatePem,
        set_as_active: SetAsActive = None,
        allow_auto_registration: AllowAutoRegistration = None,
        registration_config: RegistrationConfig = None,
        tags: TagList = None,
    ) -> RegisterCACertificateResponse:
        """Registers a CA certificate with IoT. This CA certificate can then be
        used to sign device certificates, which can be then registered with IoT.
        You can register up to 10 CA certificates per Amazon Web Services
        account that have the same subject field. This enables you to have up to
        10 certificate authorities sign your device certificates. If you have
        more than one CA certificate registered, make sure you pass the CA
        certificate when you register your device certificates with the
        RegisterCertificate action.

        Requires permission to access the
        `RegisterCACertificate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param ca_certificate: The CA certificate.
        :param verification_certificate: The private key verification certificate.
        :param set_as_active: A boolean value that specifies if the CA certificate is set to active.
        :param allow_auto_registration: Allows this CA certificate to be used for auto registration of device
        certificates.
        :param registration_config: Information about the registration configuration.
        :param tags: Metadata which can be used to manage the CA certificate.
        :returns: RegisterCACertificateResponse
        :raises ResourceAlreadyExistsException:
        :raises RegistrationCodeValidationException:
        :raises InvalidRequestException:
        :raises CertificateValidationException:
        :raises ThrottlingException:
        :raises LimitExceededException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("RegisterCertificate")
    def register_certificate(
        self,
        context: RequestContext,
        certificate_pem: CertificatePem,
        ca_certificate_pem: CertificatePem = None,
        set_as_active: SetAsActiveFlag = None,
        status: CertificateStatus = None,
    ) -> RegisterCertificateResponse:
        """Registers a device certificate with IoT. If you have more than one CA
        certificate that has the same subject field, you must specify the CA
        certificate that was used to sign the device certificate being
        registered.

        Requires permission to access the
        `RegisterCertificate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param certificate_pem: The certificate data, in PEM format.
        :param ca_certificate_pem: The CA certificate used to sign the device certificate being registered.
        :param set_as_active: A boolean value that specifies if the certificate is set to active.
        :param status: The status of the register certificate request.
        :returns: RegisterCertificateResponse
        :raises ResourceAlreadyExistsException:
        :raises InvalidRequestException:
        :raises CertificateValidationException:
        :raises CertificateStateException:
        :raises CertificateConflictException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("RegisterCertificateWithoutCA")
    def register_certificate_without_ca(
        self,
        context: RequestContext,
        certificate_pem: CertificatePem,
        status: CertificateStatus = None,
    ) -> RegisterCertificateWithoutCAResponse:
        """Register a certificate that does not have a certificate authority (CA).
        For supported certificates, consult `Certificate signing algorithms
        supported by
        IoT <https://docs.aws.amazon.com/iot/latest/developerguide/x509-client-certs.html#x509-cert-algorithms>`__.

        :param certificate_pem: The certificate data, in PEM format.
        :param status: The status of the register certificate request.
        :returns: RegisterCertificateWithoutCAResponse
        :raises ResourceAlreadyExistsException:
        :raises InvalidRequestException:
        :raises CertificateStateException:
        :raises CertificateValidationException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("RegisterThing")
    def register_thing(
        self, context: RequestContext, template_body: TemplateBody, parameters: Parameters = None
    ) -> RegisterThingResponse:
        """Provisions a thing in the device registry. RegisterThing calls other IoT
        control plane APIs. These calls might exceed your account level `IoT
        Throttling
        Limits <https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html#limits_iot>`__
        and cause throttle errors. Please contact `Amazon Web Services Customer
        Support <https://console.aws.amazon.com/support/home>`__ to raise your
        throttling limits if necessary.

        Requires permission to access the
        `RegisterThing <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_body: The provisioning template.
        :param parameters: The parameters for provisioning a thing.
        :returns: RegisterThingResponse
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises InvalidRequestException:
        :raises UnauthorizedException:
        :raises ThrottlingException:
        :raises ConflictingResourceUpdateException:
        :raises ResourceRegistrationFailureException:
        """
        raise NotImplementedError

    @handler("RejectCertificateTransfer")
    def reject_certificate_transfer(
        self, context: RequestContext, certificate_id: CertificateId, reject_reason: Message = None
    ) -> None:
        """Rejects a pending certificate transfer. After IoT rejects a certificate
        transfer, the certificate status changes from **PENDING_TRANSFER** to
        **INACTIVE**.

        To check for pending certificate transfers, call ListCertificates to
        enumerate your certificates.

        This operation can only be called by the transfer destination. After it
        is called, the certificate will be returned to the source's account in
        the INACTIVE state.

        Requires permission to access the
        `RejectCertificateTransfer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param certificate_id: The ID of the certificate.
        :param reject_reason: The reason the certificate transfer was rejected.
        :raises ResourceNotFoundException:
        :raises TransferAlreadyCompletedException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("RemoveThingFromBillingGroup")
    def remove_thing_from_billing_group(
        self,
        context: RequestContext,
        billing_group_name: BillingGroupName = None,
        billing_group_arn: BillingGroupArn = None,
        thing_name: ThingName = None,
        thing_arn: ThingArn = None,
    ) -> RemoveThingFromBillingGroupResponse:
        """Removes the given thing from the billing group.

        Requires permission to access the
        `RemoveThingFromBillingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        This call is asynchronous. It might take several seconds for the
        detachment to propagate.

        :param billing_group_name: The name of the billing group.
        :param billing_group_arn: The ARN of the billing group.
        :param thing_name: The name of the thing to be removed from the billing group.
        :param thing_arn: The ARN of the thing to be removed from the billing group.
        :returns: RemoveThingFromBillingGroupResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("RemoveThingFromThingGroup")
    def remove_thing_from_thing_group(
        self,
        context: RequestContext,
        thing_group_name: ThingGroupName = None,
        thing_group_arn: ThingGroupArn = None,
        thing_name: ThingName = None,
        thing_arn: ThingArn = None,
    ) -> RemoveThingFromThingGroupResponse:
        """Remove the specified thing from the specified group.

        You must specify either a ``thingGroupArn`` or a ``thingGroupName`` to
        identify the thing group and either a ``thingArn`` or a ``thingName`` to
        identify the thing to remove from the thing group.

        Requires permission to access the
        `RemoveThingFromThingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_group_name: The group name.
        :param thing_group_arn: The group ARN.
        :param thing_name: The name of the thing to remove from the group.
        :param thing_arn: The ARN of the thing to remove from the group.
        :returns: RemoveThingFromThingGroupResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ReplaceTopicRule")
    def replace_topic_rule(
        self, context: RequestContext, rule_name: RuleName, topic_rule_payload: TopicRulePayload
    ) -> None:
        """Replaces the rule. You must specify all parameters for the new rule.
        Creating rules is an administrator-level action. Any user who has
        permission to create rules will be able to access data processed by the
        rule.

        Requires permission to access the
        `ReplaceTopicRule <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param rule_name: The name of the rule.
        :param topic_rule_payload: The rule payload.
        :raises SqlParseException:
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises UnauthorizedException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("SearchIndex")
    def search_index(
        self,
        context: RequestContext,
        query_string: QueryString,
        index_name: IndexName = None,
        next_token: NextToken = None,
        max_results: QueryMaxResults = None,
        query_version: QueryVersion = None,
    ) -> SearchIndexResponse:
        """The query search index.

        Requires permission to access the
        `SearchIndex <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param query_string: The search query string.
        :param index_name: The search index name.
        :param next_token: The token used to get the next set of results, or ``null`` if there are
        no additional results.
        :param max_results: The maximum number of results to return at one time.
        :param query_version: The query version.
        :returns: SearchIndexResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises InvalidQueryException:
        :raises IndexNotReadyException:
        """
        raise NotImplementedError

    @handler("SetDefaultAuthorizer")
    def set_default_authorizer(
        self, context: RequestContext, authorizer_name: AuthorizerName
    ) -> SetDefaultAuthorizerResponse:
        """Sets the default authorizer. This will be used if a websocket connection
        is made without specifying an authorizer.

        Requires permission to access the
        `SetDefaultAuthorizer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param authorizer_name: The authorizer name.
        :returns: SetDefaultAuthorizerResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceAlreadyExistsException:
        """
        raise NotImplementedError

    @handler("SetDefaultPolicyVersion")
    def set_default_policy_version(
        self, context: RequestContext, policy_name: PolicyName, policy_version_id: PolicyVersionId
    ) -> None:
        """Sets the specified version of the specified policy as the policy's
        default (operative) version. This action affects all certificates to
        which the policy is attached. To list the principals the policy is
        attached to, use the ListPrincipalPolicies action.

        Requires permission to access the
        `SetDefaultPolicyVersion <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param policy_name: The policy name.
        :param policy_version_id: The policy version ID.
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("SetLoggingOptions")
    def set_logging_options(
        self, context: RequestContext, logging_options_payload: LoggingOptionsPayload
    ) -> None:
        """Sets the logging options.

        NOTE: use of this command is not recommended. Use
        ``SetV2LoggingOptions`` instead.

        Requires permission to access the
        `SetLoggingOptions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param logging_options_payload: The logging options payload.
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("SetV2LoggingLevel")
    def set_v2_logging_level(
        self, context: RequestContext, log_target: LogTarget, log_level: LogLevel
    ) -> None:
        """Sets the logging level.

        Requires permission to access the
        `SetV2LoggingLevel <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param log_target: The log target.
        :param log_level: The log level.
        :raises InternalException:
        :raises NotConfiguredException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("SetV2LoggingOptions")
    def set_v2_logging_options(
        self,
        context: RequestContext,
        role_arn: AwsArn = None,
        default_log_level: LogLevel = None,
        disable_all_logs: DisableAllLogs = None,
    ) -> None:
        """Sets the logging options for the V2 logging service.

        Requires permission to access the
        `SetV2LoggingOptions <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param role_arn: The ARN of the role that allows IoT to write to Cloudwatch logs.
        :param default_log_level: The default logging level.
        :param disable_all_logs: If true all logs are disabled.
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("StartAuditMitigationActionsTask")
    def start_audit_mitigation_actions_task(
        self,
        context: RequestContext,
        task_id: MitigationActionsTaskId,
        target: AuditMitigationActionsTaskTarget,
        audit_check_to_actions_mapping: AuditCheckToActionsMapping,
        client_request_token: ClientRequestToken,
    ) -> StartAuditMitigationActionsTaskResponse:
        """Starts a task that applies a set of mitigation actions to the specified
        target.

        Requires permission to access the
        `StartAuditMitigationActionsTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: A unique identifier for the task.
        :param target: Specifies the audit findings to which the mitigation actions are
        applied.
        :param audit_check_to_actions_mapping: For an audit check, specifies which mitigation actions to apply.
        :param client_request_token: Each audit mitigation task must have a unique client request token.
        :returns: StartAuditMitigationActionsTaskResponse
        :raises InvalidRequestException:
        :raises TaskAlreadyExistsException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("StartDetectMitigationActionsTask")
    def start_detect_mitigation_actions_task(
        self,
        context: RequestContext,
        task_id: MitigationActionsTaskId,
        target: DetectMitigationActionsTaskTarget,
        actions: DetectMitigationActionsToExecuteList,
        client_request_token: ClientRequestToken,
        violation_event_occurrence_range: ViolationEventOccurrenceRange = None,
        include_only_active_violations: NullableBoolean = None,
        include_suppressed_alerts: NullableBoolean = None,
    ) -> StartDetectMitigationActionsTaskResponse:
        """Starts a Device Defender ML Detect mitigation actions task.

        Requires permission to access the
        `StartDetectMitigationActionsTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: The unique identifier of the task.
        :param target: Specifies the ML Detect findings to which the mitigation actions are
        applied.
        :param actions: The actions to be performed when a device has unexpected behavior.
        :param client_request_token: Each mitigation action task must have a unique client request token.
        :param violation_event_occurrence_range: Specifies the time period of which violation events occurred between.
        :param include_only_active_violations: Specifies to list only active violations.
        :param include_suppressed_alerts: Specifies to include suppressed alerts.
        :returns: StartDetectMitigationActionsTaskResponse
        :raises InvalidRequestException:
        :raises TaskAlreadyExistsException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("StartOnDemandAuditTask")
    def start_on_demand_audit_task(
        self, context: RequestContext, target_check_names: TargetAuditCheckNames
    ) -> StartOnDemandAuditTaskResponse:
        """Starts an on-demand Device Defender audit.

        Requires permission to access the
        `StartOnDemandAuditTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param target_check_names: Which checks are performed during the audit.
        :returns: StartOnDemandAuditTaskResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("StartThingRegistrationTask")
    def start_thing_registration_task(
        self,
        context: RequestContext,
        template_body: TemplateBody,
        input_file_bucket: RegistryS3BucketName,
        input_file_key: RegistryS3KeyName,
        role_arn: RoleArn,
    ) -> StartThingRegistrationTaskResponse:
        """Creates a bulk thing provisioning task.

        Requires permission to access the
        `StartThingRegistrationTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_body: The provisioning template.
        :param input_file_bucket: The S3 bucket that contains the input file.
        :param input_file_key: The name of input file within the S3 bucket.
        :param role_arn: The IAM role ARN that grants permission the input file.
        :returns: StartThingRegistrationTaskResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("StopThingRegistrationTask")
    def stop_thing_registration_task(
        self, context: RequestContext, task_id: TaskId
    ) -> StopThingRegistrationTaskResponse:
        """Cancels a bulk thing provisioning task.

        Requires permission to access the
        `StopThingRegistrationTask <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param task_id: The bulk thing provisioning task ID.
        :returns: StopThingRegistrationTaskResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: ResourceArn, tags: TagList
    ) -> TagResourceResponse:
        """Adds to or modifies the tags of the given resource. Tags are metadata
        which can be used to manage a resource.

        Requires permission to access the
        `TagResource <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param resource_arn: The ARN of the resource.
        :param tags: The new or modified tags for the resource.
        :returns: TagResourceResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("TestAuthorization")
    def test_authorization(
        self,
        context: RequestContext,
        auth_infos: AuthInfos,
        principal: Principal = None,
        cognito_identity_pool_id: CognitoIdentityPoolId = None,
        client_id: ClientId = None,
        policy_names_to_add: PolicyNames = None,
        policy_names_to_skip: PolicyNames = None,
    ) -> TestAuthorizationResponse:
        """Tests if a specified principal is authorized to perform an IoT action on
        a specified resource. Use this to test and debug the authorization
        behavior of devices that connect to the IoT device gateway.

        Requires permission to access the
        `TestAuthorization <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param auth_infos: A list of authorization info objects.
        :param principal: The principal.
        :param cognito_identity_pool_id: The Cognito identity pool ID.
        :param client_id: The MQTT client ID.
        :param policy_names_to_add: When testing custom authorization, the policies specified here are
        treated as if they are attached to the principal being authorized.
        :param policy_names_to_skip: When testing custom authorization, the policies specified here are
        treated as if they are not attached to the principal being authorized.
        :returns: TestAuthorizationResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("TestInvokeAuthorizer")
    def test_invoke_authorizer(
        self,
        context: RequestContext,
        authorizer_name: AuthorizerName,
        token: Token = None,
        token_signature: TokenSignature = None,
        http_context: HttpContext = None,
        mqtt_context: MqttContext = None,
        tls_context: TlsContext = None,
    ) -> TestInvokeAuthorizerResponse:
        """Tests a custom authorization behavior by invoking a specified custom
        authorizer. Use this to test and debug the custom authorization behavior
        of devices that connect to the IoT device gateway.

        Requires permission to access the
        `TestInvokeAuthorizer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param authorizer_name: The custom authorizer name.
        :param token: The token returned by your custom authentication service.
        :param token_signature: The signature made with the token and your custom authentication
        service's private key.
        :param http_context: Specifies a test HTTP authorization request.
        :param mqtt_context: Specifies a test MQTT authorization request.
        :param tls_context: Specifies a test TLS authorization request.
        :returns: TestInvokeAuthorizerResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises InvalidResponseException:
        """
        raise NotImplementedError

    @handler("TransferCertificate")
    def transfer_certificate(
        self,
        context: RequestContext,
        certificate_id: CertificateId,
        target_aws_account: AwsAccountId,
        transfer_message: Message = None,
    ) -> TransferCertificateResponse:
        """Transfers the specified certificate to the specified Amazon Web Services
        account.

        Requires permission to access the
        `TransferCertificate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        You can cancel the transfer until it is acknowledged by the recipient.

        No notification is sent to the transfer destination's account. It is up
        to the caller to notify the transfer target.

        The certificate being transferred must not be in the ACTIVE state. You
        can use the UpdateCertificate action to deactivate it.

        The certificate must not have any policies attached to it. You can use
        the DetachPolicy action to detach them.

        :param certificate_id: The ID of the certificate.
        :param target_aws_account: The Amazon Web Services account.
        :param transfer_message: The transfer message.
        :returns: TransferCertificateResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises CertificateStateException:
        :raises TransferConflictException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: ResourceArn, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Removes the given tags (metadata) from the resource.

        Requires permission to access the
        `UntagResource <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param resource_arn: The ARN of the resource.
        :param tag_keys: A list of the keys of the tags to be removed from the resource.
        :returns: UntagResourceResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateAccountAuditConfiguration")
    def update_account_audit_configuration(
        self,
        context: RequestContext,
        role_arn: RoleArn = None,
        audit_notification_target_configurations: AuditNotificationTargetConfigurations = None,
        audit_check_configurations: AuditCheckConfigurations = None,
    ) -> UpdateAccountAuditConfigurationResponse:
        """Configures or reconfigures the Device Defender audit settings for this
        account. Settings include how audit notifications are sent and which
        audit checks are enabled or disabled.

        Requires permission to access the
        `UpdateAccountAuditConfiguration <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param role_arn: The Amazon Resource Name (ARN) of the role that grants permission to IoT
        to access information about your devices, policies, certificates, and
        other items as required when performing an audit.
        :param audit_notification_target_configurations: Information about the targets to which audit notifications are sent.
        :param audit_check_configurations: Specifies which audit checks are enabled and disabled for this account.
        :returns: UpdateAccountAuditConfigurationResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateAuditSuppression")
    def update_audit_suppression(
        self,
        context: RequestContext,
        check_name: AuditCheckName,
        resource_identifier: ResourceIdentifier,
        expiration_date: Timestamp = None,
        suppress_indefinitely: SuppressIndefinitely = None,
        description: AuditDescription = None,
    ) -> UpdateAuditSuppressionResponse:
        """Updates a Device Defender audit suppression.

        :param check_name: An audit check name.
        :param resource_identifier: Information that identifies the noncompliant resource.
        :param expiration_date: The expiration date (epoch timestamp in seconds) that you want the
        suppression to adhere to.
        :param suppress_indefinitely: Indicates whether a suppression should exist indefinitely or not.
        :param description: The description of the audit suppression.
        :returns: UpdateAuditSuppressionResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateAuthorizer")
    def update_authorizer(
        self,
        context: RequestContext,
        authorizer_name: AuthorizerName,
        authorizer_function_arn: AuthorizerFunctionArn = None,
        token_key_name: TokenKeyName = None,
        token_signing_public_keys: PublicKeyMap = None,
        status: AuthorizerStatus = None,
        enable_caching_for_http: EnableCachingForHttp = None,
    ) -> UpdateAuthorizerResponse:
        """Updates an authorizer.

        Requires permission to access the
        `UpdateAuthorizer <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param authorizer_name: The authorizer name.
        :param authorizer_function_arn: The ARN of the authorizer's Lambda function.
        :param token_key_name: The key used to extract the token from the HTTP headers.
        :param token_signing_public_keys: The public keys used to verify the token signature.
        :param status: The status of the update authorizer request.
        :param enable_caching_for_http: When ``true``, the result from the authorizer’s Lambda function is
        cached for the time specified in ``refreshAfterInSeconds``.
        :returns: UpdateAuthorizerResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises LimitExceededException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateBillingGroup")
    def update_billing_group(
        self,
        context: RequestContext,
        billing_group_name: BillingGroupName,
        billing_group_properties: BillingGroupProperties,
        expected_version: OptionalVersion = None,
    ) -> UpdateBillingGroupResponse:
        """Updates information about the billing group.

        Requires permission to access the
        `UpdateBillingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param billing_group_name: The name of the billing group.
        :param billing_group_properties: The properties of the billing group.
        :param expected_version: The expected version of the billing group.
        :returns: UpdateBillingGroupResponse
        :raises InvalidRequestException:
        :raises VersionConflictException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateCACertificate")
    def update_ca_certificate(
        self,
        context: RequestContext,
        certificate_id: CertificateId,
        new_status: CACertificateStatus = None,
        new_auto_registration_status: AutoRegistrationStatus = None,
        registration_config: RegistrationConfig = None,
        remove_auto_registration: RemoveAutoRegistration = None,
    ) -> None:
        """Updates a registered CA certificate.

        Requires permission to access the
        `UpdateCACertificate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param certificate_id: The CA certificate identifier.
        :param new_status: The updated status of the CA certificate.
        :param new_auto_registration_status: The new value for the auto registration status.
        :param registration_config: Information about the registration configuration.
        :param remove_auto_registration: If true, removes auto registration.
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateCertificate")
    def update_certificate(
        self, context: RequestContext, certificate_id: CertificateId, new_status: CertificateStatus
    ) -> None:
        """Updates the status of the specified certificate. This operation is
        idempotent.

        Requires permission to access the
        `UpdateCertificate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        Certificates must be in the ACTIVE state to authenticate devices that
        use a certificate to connect to IoT.

        Within a few minutes of updating a certificate from the ACTIVE state to
        any other state, IoT disconnects all devices that used that certificate
        to connect. Devices cannot use a certificate that is not in the ACTIVE
        state to reconnect.

        :param certificate_id: The ID of the certificate.
        :param new_status: The new status.
        :raises ResourceNotFoundException:
        :raises CertificateStateException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateCustomMetric")
    def update_custom_metric(
        self,
        context: RequestContext,
        metric_name: MetricName,
        display_name: CustomMetricDisplayName,
    ) -> UpdateCustomMetricResponse:
        """Updates a Device Defender detect custom metric.

        Requires permission to access the
        `UpdateCustomMetric <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param metric_name: The name of the custom metric.
        :param display_name: Field represents a friendly name in the console for the custom metric,
        it doesn't have to be unique.
        :returns: UpdateCustomMetricResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateDimension")
    def update_dimension(
        self, context: RequestContext, name: DimensionName, string_values: DimensionStringValues
    ) -> UpdateDimensionResponse:
        """Updates the definition for a dimension. You cannot change the type of a
        dimension after it is created (you can delete it and recreate it).

        Requires permission to access the
        `UpdateDimension <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param name: A unique identifier for the dimension.
        :param string_values: Specifies the value or list of values for the dimension.
        :returns: UpdateDimensionResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateDomainConfiguration")
    def update_domain_configuration(
        self,
        context: RequestContext,
        domain_configuration_name: ReservedDomainConfigurationName,
        authorizer_config: AuthorizerConfig = None,
        domain_configuration_status: DomainConfigurationStatus = None,
        remove_authorizer_config: RemoveAuthorizerConfig = None,
    ) -> UpdateDomainConfigurationResponse:
        """Updates values stored in the domain configuration. Domain configurations
        for default endpoints can't be updated.

        Requires permission to access the
        `UpdateDomainConfiguration <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param domain_configuration_name: The name of the domain configuration to be updated.
        :param authorizer_config: An object that specifies the authorization service for a domain.
        :param domain_configuration_status: The status to which the domain configuration should be updated.
        :param remove_authorizer_config: Removes the authorization configuration from a domain.
        :returns: UpdateDomainConfigurationResponse
        :raises ResourceNotFoundException:
        :raises CertificateValidationException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateDynamicThingGroup")
    def update_dynamic_thing_group(
        self,
        context: RequestContext,
        thing_group_name: ThingGroupName,
        thing_group_properties: ThingGroupProperties,
        expected_version: OptionalVersion = None,
        index_name: IndexName = None,
        query_string: QueryString = None,
        query_version: QueryVersion = None,
    ) -> UpdateDynamicThingGroupResponse:
        """Updates a dynamic thing group.

        Requires permission to access the
        `UpdateDynamicThingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_group_name: The name of the dynamic thing group to update.
        :param thing_group_properties: The dynamic thing group properties to update.
        :param expected_version: The expected version of the dynamic thing group to update.
        :param index_name: The dynamic thing group index to update.
        :param query_string: The dynamic thing group search query string to update.
        :param query_version: The dynamic thing group query version to update.
        :returns: UpdateDynamicThingGroupResponse
        :raises InvalidRequestException:
        :raises VersionConflictException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises InvalidQueryException:
        """
        raise NotImplementedError

    @handler("UpdateEventConfigurations")
    def update_event_configurations(
        self, context: RequestContext, event_configurations: EventConfigurations = None
    ) -> UpdateEventConfigurationsResponse:
        """Updates the event configurations.

        Requires permission to access the
        `UpdateEventConfigurations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param event_configurations: The new event configuration values.
        :returns: UpdateEventConfigurationsResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateFleetMetric")
    def update_fleet_metric(
        self,
        context: RequestContext,
        metric_name: FleetMetricName,
        index_name: IndexName,
        query_string: QueryString = None,
        aggregation_type: AggregationType = None,
        period: FleetMetricPeriod = None,
        aggregation_field: AggregationField = None,
        description: FleetMetricDescription = None,
        query_version: QueryVersion = None,
        unit: FleetMetricUnit = None,
        expected_version: OptionalVersion = None,
    ) -> None:
        """Updates the data for a fleet metric.

        Requires permission to access the
        `UpdateFleetMetric <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param metric_name: The name of the fleet metric to update.
        :param index_name: The name of the index to search.
        :param query_string: The search query string.
        :param aggregation_type: The type of the aggregation query.
        :param period: The time in seconds between fleet metric emissions.
        :param aggregation_field: The field to aggregate.
        :param description: The description of the fleet metric.
        :param query_version: The version of the query.
        :param unit: Used to support unit transformation such as milliseconds to seconds.
        :param expected_version: The expected version of the fleet metric record in the registry.
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        :raises InvalidQueryException:
        :raises InvalidAggregationException:
        :raises VersionConflictException:
        :raises IndexNotReadyException:
        """
        raise NotImplementedError

    @handler("UpdateIndexingConfiguration")
    def update_indexing_configuration(
        self,
        context: RequestContext,
        thing_indexing_configuration: ThingIndexingConfiguration = None,
        thing_group_indexing_configuration: ThingGroupIndexingConfiguration = None,
    ) -> UpdateIndexingConfigurationResponse:
        """Updates the search configuration.

        Requires permission to access the
        `UpdateIndexingConfiguration <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_indexing_configuration: Thing indexing configuration.
        :param thing_group_indexing_configuration: Thing group indexing configuration.
        :returns: UpdateIndexingConfigurationResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateJob")
    def update_job(
        self,
        context: RequestContext,
        job_id: JobId,
        description: JobDescription = None,
        presigned_url_config: PresignedUrlConfig = None,
        job_executions_rollout_config: JobExecutionsRolloutConfig = None,
        abort_config: AbortConfig = None,
        timeout_config: TimeoutConfig = None,
        namespace_id: NamespaceId = None,
        job_executions_retry_config: JobExecutionsRetryConfig = None,
    ) -> None:
        """Updates supported fields of the specified job.

        Requires permission to access the
        `UpdateJob <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param job_id: The ID of the job to be updated.
        :param description: A short text description of the job.
        :param presigned_url_config: Configuration information for pre-signed S3 URLs.
        :param job_executions_rollout_config: Allows you to create a staged rollout of the job.
        :param abort_config: Allows you to create criteria to abort a job.
        :param timeout_config: Specifies the amount of time each device has to finish its execution of
        the job.
        :param namespace_id: The namespace used to indicate that a job is a customer-managed job.
        :param job_executions_retry_config: Allows you to create the criteria to retry a job.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("UpdateMitigationAction")
    def update_mitigation_action(
        self,
        context: RequestContext,
        action_name: MitigationActionName,
        role_arn: RoleArn = None,
        action_params: MitigationActionParams = None,
    ) -> UpdateMitigationActionResponse:
        """Updates the definition for the specified mitigation action.

        Requires permission to access the
        `UpdateMitigationAction <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param action_name: The friendly name for the mitigation action.
        :param role_arn: The ARN of the IAM role that is used to apply the mitigation action.
        :param action_params: Defines the type of action and the parameters for that action.
        :returns: UpdateMitigationActionResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateProvisioningTemplate")
    def update_provisioning_template(
        self,
        context: RequestContext,
        template_name: TemplateName,
        description: TemplateDescription = None,
        enabled: Enabled = None,
        default_version_id: TemplateVersionId = None,
        provisioning_role_arn: RoleArn = None,
        pre_provisioning_hook: ProvisioningHook = None,
        remove_pre_provisioning_hook: RemoveHook = None,
    ) -> UpdateProvisioningTemplateResponse:
        """Updates a fleet provisioning template.

        Requires permission to access the
        `UpdateProvisioningTemplate <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param template_name: The name of the fleet provisioning template.
        :param description: The description of the fleet provisioning template.
        :param enabled: True to enable the fleet provisioning template, otherwise false.
        :param default_version_id: The ID of the default provisioning template version.
        :param provisioning_role_arn: The ARN of the role associated with the provisioning template.
        :param pre_provisioning_hook: Updates the pre-provisioning hook template.
        :param remove_pre_provisioning_hook: Removes pre-provisioning hook template.
        :returns: UpdateProvisioningTemplateResponse
        :raises InternalFailureException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises UnauthorizedException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("UpdateRoleAlias")
    def update_role_alias(
        self,
        context: RequestContext,
        role_alias: RoleAlias,
        role_arn: RoleArn = None,
        credential_duration_seconds: CredentialDurationSeconds = None,
    ) -> UpdateRoleAliasResponse:
        """Updates a role alias.

        Requires permission to access the
        `UpdateRoleAlias <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param role_alias: The role alias to update.
        :param role_arn: The role ARN.
        :param credential_duration_seconds: The number of seconds the credential will be valid.
        :returns: UpdateRoleAliasResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateScheduledAudit")
    def update_scheduled_audit(
        self,
        context: RequestContext,
        scheduled_audit_name: ScheduledAuditName,
        frequency: AuditFrequency = None,
        day_of_month: DayOfMonth = None,
        day_of_week: DayOfWeek = None,
        target_check_names: TargetAuditCheckNames = None,
    ) -> UpdateScheduledAuditResponse:
        """Updates a scheduled audit, including which checks are performed and how
        often the audit takes place.

        Requires permission to access the
        `UpdateScheduledAudit <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param scheduled_audit_name: The name of the scheduled audit.
        :param frequency: How often the scheduled audit takes place, either ``DAILY``, ``WEEKLY``,
        ``BIWEEKLY``, or ``MONTHLY``.
        :param day_of_month: The day of the month on which the scheduled audit takes place.
        :param day_of_week: The day of the week on which the scheduled audit takes place.
        :param target_check_names: Which checks are performed during the scheduled audit.
        :returns: UpdateScheduledAuditResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateSecurityProfile")
    def update_security_profile(
        self,
        context: RequestContext,
        security_profile_name: SecurityProfileName,
        security_profile_description: SecurityProfileDescription = None,
        behaviors: Behaviors = None,
        alert_targets: AlertTargets = None,
        additional_metrics_to_retain: AdditionalMetricsToRetainList = None,
        additional_metrics_to_retain_v2: AdditionalMetricsToRetainV2List = None,
        delete_behaviors: DeleteBehaviors = None,
        delete_alert_targets: DeleteAlertTargets = None,
        delete_additional_metrics_to_retain: DeleteAdditionalMetricsToRetain = None,
        expected_version: OptionalVersion = None,
    ) -> UpdateSecurityProfileResponse:
        """Updates a Device Defender security profile.

        Requires permission to access the
        `UpdateSecurityProfile <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param security_profile_name: The name of the security profile you want to update.
        :param security_profile_description: A description of the security profile.
        :param behaviors: Specifies the behaviors that, when violated by a device (thing), cause
        an alert.
        :param alert_targets: Where the alerts are sent.
        :param additional_metrics_to_retain: *Please use UpdateSecurityProfileRequest$additionalMetricsToRetainV2
        instead.
        :param additional_metrics_to_retain_v2: A list of metrics whose data is retained (stored).
        :param delete_behaviors: If true, delete all ``behaviors`` defined for this security profile.
        :param delete_alert_targets: If true, delete all ``alertTargets`` defined for this security profile.
        :param delete_additional_metrics_to_retain: If true, delete all ``additionalMetricsToRetain`` defined for this
        security profile.
        :param expected_version: The expected version of the security profile.
        :returns: UpdateSecurityProfileResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises VersionConflictException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateStream")
    def update_stream(
        self,
        context: RequestContext,
        stream_id: StreamId,
        description: StreamDescription = None,
        files: StreamFiles = None,
        role_arn: RoleArn = None,
    ) -> UpdateStreamResponse:
        """Updates an existing stream. The stream version will be incremented by
        one.

        Requires permission to access the
        `UpdateStream <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param stream_id: The stream ID.
        :param description: The description of the stream.
        :param files: The files associated with the stream.
        :param role_arn: An IAM role that allows the IoT service principal assumes to access your
        S3 files.
        :returns: UpdateStreamResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        """
        raise NotImplementedError

    @handler("UpdateThing")
    def update_thing(
        self,
        context: RequestContext,
        thing_name: ThingName,
        thing_type_name: ThingTypeName = None,
        attribute_payload: AttributePayload = None,
        expected_version: OptionalVersion = None,
        remove_thing_type: RemoveThingType = None,
    ) -> UpdateThingResponse:
        """Updates the data for a thing.

        Requires permission to access the
        `UpdateThing <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The name of the thing to update.
        :param thing_type_name: The name of the thing type.
        :param attribute_payload: A list of thing attributes, a JSON string containing name-value pairs.
        :param expected_version: The expected version of the thing record in the registry.
        :param remove_thing_type: Remove a thing type association.
        :returns: UpdateThingResponse
        :raises InvalidRequestException:
        :raises VersionConflictException:
        :raises ThrottlingException:
        :raises UnauthorizedException:
        :raises ServiceUnavailableException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateThingGroup")
    def update_thing_group(
        self,
        context: RequestContext,
        thing_group_name: ThingGroupName,
        thing_group_properties: ThingGroupProperties,
        expected_version: OptionalVersion = None,
    ) -> UpdateThingGroupResponse:
        """Update a thing group.

        Requires permission to access the
        `UpdateThingGroup <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_group_name: The thing group to update.
        :param thing_group_properties: The thing group properties.
        :param expected_version: The expected version of the thing group.
        :returns: UpdateThingGroupResponse
        :raises InvalidRequestException:
        :raises VersionConflictException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateThingGroupsForThing")
    def update_thing_groups_for_thing(
        self,
        context: RequestContext,
        thing_name: ThingName = None,
        thing_groups_to_add: ThingGroupList = None,
        thing_groups_to_remove: ThingGroupList = None,
        override_dynamic_groups: OverrideDynamicGroups = None,
    ) -> UpdateThingGroupsForThingResponse:
        """Updates the groups to which the thing belongs.

        Requires permission to access the
        `UpdateThingGroupsForThing <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param thing_name: The thing whose group memberships will be updated.
        :param thing_groups_to_add: The groups to which the thing will be added.
        :param thing_groups_to_remove: The groups from which the thing will be removed.
        :param override_dynamic_groups: Override dynamic thing groups with static thing groups when 10-group
        limit is reached.
        :returns: UpdateThingGroupsForThingResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateTopicRuleDestination")
    def update_topic_rule_destination(
        self, context: RequestContext, arn: AwsArn, status: TopicRuleDestinationStatus
    ) -> UpdateTopicRuleDestinationResponse:
        """Updates a topic rule destination. You use this to change the status,
        endpoint URL, or confirmation URL of the destination.

        Requires permission to access the
        `UpdateTopicRuleDestination <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param arn: The ARN of the topic rule destination.
        :param status: The status of the topic rule destination.
        :returns: UpdateTopicRuleDestinationResponse
        :raises InternalException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises UnauthorizedException:
        :raises ConflictingResourceUpdateException:
        """
        raise NotImplementedError

    @handler("ValidateSecurityProfileBehaviors")
    def validate_security_profile_behaviors(
        self, context: RequestContext, behaviors: Behaviors
    ) -> ValidateSecurityProfileBehaviorsResponse:
        """Validates a Device Defender security profile behaviors specification.

        Requires permission to access the
        `ValidateSecurityProfileBehaviors <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiot.html#awsiot-actions-as-permissions>`__
        action.

        :param behaviors: Specifies the behaviors that, when violated by a device (thing), cause
        an alert.
        :returns: ValidateSecurityProfileBehaviorsResponse
        :raises InvalidRequestException:
        :raises ThrottlingException:
        :raises InternalFailureException:
        """
        raise NotImplementedError
