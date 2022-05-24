import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

ARN = str
AbortableOperationInProgress = bool
ApplicationArn = str
ApplicationName = str
ApplicationVersionArn = str
ApplicationVersionProccess = bool
AutoCreateApplication = bool
BoxedBoolean = bool
BoxedInt = int
BranchName = str
BranchOrder = int
Cause = str
CnameAvailability = bool
ConfigurationOptionDefaultValue = str
ConfigurationOptionName = str
ConfigurationOptionPossibleValue = str
ConfigurationOptionSeverity = str
ConfigurationOptionValue = str
ConfigurationTemplateName = str
DNSCname = str
DNSCnamePrefix = str
DeleteSourceBundle = bool
Description = str
Ec2InstanceId = str
EndpointURL = str
EnvironmentArn = str
EnvironmentId = str
EnvironmentName = str
EventMessage = str
ExceptionMessage = str
FileTypeExtension = str
ForceTerminate = bool
GroupName = str
ImageId = str
IncludeDeleted = bool
InstanceId = str
Integer = int
LoadAverageValue = float
Maintainer = str
ManagedActionHistoryMaxItems = int
MaxRecords = int
Message = str
NextToken = str
NonEmptyString = str
NullableDouble = float
NullableInteger = int
OperatingSystemName = str
OperatingSystemVersion = str
OperationsRole = str
OptionNamespace = str
OptionRestrictionMaxLength = int
OptionRestrictionMaxValue = int
OptionRestrictionMinValue = int
PlatformArn = str
PlatformBranchLifecycleState = str
PlatformBranchMaxRecords = int
PlatformCategory = str
PlatformFilterOperator = str
PlatformFilterType = str
PlatformFilterValue = str
PlatformLifecycleState = str
PlatformMaxRecords = int
PlatformName = str
PlatformOwner = str
PlatformVersion = str
RegexLabel = str
RegexPattern = str
RequestCount = int
RequestId = str
ResourceArn = str
ResourceId = str
ResourceName = str
S3Bucket = str
S3Key = str
SearchFilterAttribute = str
SearchFilterOperator = str
SearchFilterValue = str
SolutionStackName = str
SourceLocation = str
String = str
SupportedAddon = str
SupportedTier = str
TagKey = str
TagValue = str
TerminateEnvForce = bool
TerminateEnvironmentResources = bool
Token = str
UserDefinedOption = bool
ValidationMessageString = str
VersionLabel = str
VirtualizationType = str


class ActionHistoryStatus(str):
    Completed = "Completed"
    Failed = "Failed"
    Unknown = "Unknown"


class ActionStatus(str):
    Scheduled = "Scheduled"
    Pending = "Pending"
    Running = "Running"
    Unknown = "Unknown"


class ActionType(str):
    InstanceRefresh = "InstanceRefresh"
    PlatformUpdate = "PlatformUpdate"
    Unknown = "Unknown"


class ApplicationVersionStatus(str):
    Processed = "Processed"
    Unprocessed = "Unprocessed"
    Failed = "Failed"
    Processing = "Processing"
    Building = "Building"


class ComputeType(str):
    BUILD_GENERAL1_SMALL = "BUILD_GENERAL1_SMALL"
    BUILD_GENERAL1_MEDIUM = "BUILD_GENERAL1_MEDIUM"
    BUILD_GENERAL1_LARGE = "BUILD_GENERAL1_LARGE"


class ConfigurationDeploymentStatus(str):
    deployed = "deployed"
    pending = "pending"
    failed = "failed"


class ConfigurationOptionValueType(str):
    Scalar = "Scalar"
    List = "List"


class EnvironmentHealth(str):
    Green = "Green"
    Yellow = "Yellow"
    Red = "Red"
    Grey = "Grey"


class EnvironmentHealthAttribute(str):
    Status = "Status"
    Color = "Color"
    Causes = "Causes"
    ApplicationMetrics = "ApplicationMetrics"
    InstancesHealth = "InstancesHealth"
    All = "All"
    HealthStatus = "HealthStatus"
    RefreshedAt = "RefreshedAt"


class EnvironmentHealthStatus(str):
    NoData = "NoData"
    Unknown = "Unknown"
    Pending = "Pending"
    Ok = "Ok"
    Info = "Info"
    Warning = "Warning"
    Degraded = "Degraded"
    Severe = "Severe"
    Suspended = "Suspended"


class EnvironmentInfoType(str):
    tail = "tail"
    bundle = "bundle"


class EnvironmentStatus(str):
    Aborting = "Aborting"
    Launching = "Launching"
    Updating = "Updating"
    LinkingFrom = "LinkingFrom"
    LinkingTo = "LinkingTo"
    Ready = "Ready"
    Terminating = "Terminating"
    Terminated = "Terminated"


class EventSeverity(str):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class FailureType(str):
    UpdateCancelled = "UpdateCancelled"
    CancellationFailed = "CancellationFailed"
    RollbackFailed = "RollbackFailed"
    RollbackSuccessful = "RollbackSuccessful"
    InternalFailure = "InternalFailure"
    InvalidEnvironmentState = "InvalidEnvironmentState"
    PermissionsError = "PermissionsError"


class InstancesHealthAttribute(str):
    HealthStatus = "HealthStatus"
    Color = "Color"
    Causes = "Causes"
    ApplicationMetrics = "ApplicationMetrics"
    RefreshedAt = "RefreshedAt"
    LaunchedAt = "LaunchedAt"
    System = "System"
    Deployment = "Deployment"
    AvailabilityZone = "AvailabilityZone"
    InstanceType = "InstanceType"
    All = "All"


class PlatformStatus(str):
    Creating = "Creating"
    Failed = "Failed"
    Ready = "Ready"
    Deleting = "Deleting"
    Deleted = "Deleted"


class SourceRepository(str):
    CodeCommit = "CodeCommit"
    S3 = "S3"


class SourceType(str):
    Git = "Git"
    Zip = "Zip"


class ValidationSeverity(str):
    error = "error"
    warning = "warning"


class CodeBuildNotInServiceRegionException(ServiceException):
    """AWS CodeBuild is not available in the specified region."""


class ElasticBeanstalkServiceException(ServiceException):
    """A generic service exception has occurred."""

    message: Optional[ExceptionMessage]


class InsufficientPrivilegesException(ServiceException):
    """The specified account does not have sufficient privileges for one or
    more AWS services.
    """


class InvalidRequestException(ServiceException):
    """One or more input parameters is not valid. Please correct the input
    parameters and try the operation again.
    """


class ManagedActionInvalidStateException(ServiceException):
    """Cannot modify the managed action in its current state."""


class OperationInProgressException(ServiceException):
    """Unable to perform the specified operation because another operation that
    effects an element in this activity is already in progress.
    """


class PlatformVersionStillReferencedException(ServiceException):
    """You cannot delete the platform version because there are still
    environments running on it.
    """


class ResourceNotFoundException(ServiceException):
    """A resource doesn't exist for the specified Amazon Resource Name (ARN)."""


class ResourceTypeNotSupportedException(ServiceException):
    """The type of the specified Amazon Resource Name (ARN) isn't supported for
    this operation.
    """


class S3LocationNotInServiceRegionException(ServiceException):
    """The specified S3 bucket does not belong to the S3 region in which the
    service is running. The following regions are supported:

    -  IAD/us-east-1

    -  PDX/us-west-2

    -  DUB/eu-west-1
    """


class S3SubscriptionRequiredException(ServiceException):
    """The specified account does not have a subscription to Amazon S3."""


class SourceBundleDeletionException(ServiceException):
    """Unable to delete the Amazon S3 source bundle associated with the
    application version. The application version was deleted successfully.
    """


class TooManyApplicationVersionsException(ServiceException):
    """The specified account has reached its limit of application versions."""


class TooManyApplicationsException(ServiceException):
    """The specified account has reached its limit of applications."""


class TooManyBucketsException(ServiceException):
    """The specified account has reached its limit of Amazon S3 buckets."""


class TooManyConfigurationTemplatesException(ServiceException):
    """The specified account has reached its limit of configuration templates."""


class TooManyEnvironmentsException(ServiceException):
    """The specified account has reached its limit of environments."""


class TooManyPlatformsException(ServiceException):
    """You have exceeded the maximum number of allowed platforms associated
    with the account.
    """


class TooManyTagsException(ServiceException):
    """The number of tags in the resource would exceed the number of tags that
    each resource can have.

    To calculate this, the operation considers both the number of tags the
    resource already has and the tags this operation would add if it
    succeeded.
    """


class AbortEnvironmentUpdateMessage(ServiceRequest):
    EnvironmentId: Optional[EnvironmentId]
    EnvironmentName: Optional[EnvironmentName]


class MaxAgeRule(TypedDict, total=False):
    """A lifecycle rule that deletes application versions after the specified
    number of days.
    """

    Enabled: BoxedBoolean
    MaxAgeInDays: Optional[BoxedInt]
    DeleteSourceFromS3: Optional[BoxedBoolean]


class MaxCountRule(TypedDict, total=False):
    """A lifecycle rule that deletes the oldest application version when the
    maximum count is exceeded.
    """

    Enabled: BoxedBoolean
    MaxCount: Optional[BoxedInt]
    DeleteSourceFromS3: Optional[BoxedBoolean]


class ApplicationVersionLifecycleConfig(TypedDict, total=False):
    """The application version lifecycle settings for an application. Defines
    the rules that Elastic Beanstalk applies to an application's versions in
    order to avoid hitting the per-region limit for application versions.

    When Elastic Beanstalk deletes an application version from its database,
    you can no longer deploy that version to an environment. The source
    bundle remains in S3 unless you configure the rule to delete it.
    """

    MaxCountRule: Optional[MaxCountRule]
    MaxAgeRule: Optional[MaxAgeRule]


class ApplicationResourceLifecycleConfig(TypedDict, total=False):
    """The resource lifecycle configuration for an application. Defines
    lifecycle settings for resources that belong to the application, and the
    service role that AWS Elastic Beanstalk assumes in order to apply
    lifecycle settings. The version lifecycle configuration defines
    lifecycle settings for application versions.
    """

    ServiceRole: Optional[String]
    VersionLifecycleConfig: Optional[ApplicationVersionLifecycleConfig]


ConfigurationTemplateNamesList = List[ConfigurationTemplateName]
VersionLabelsList = List[VersionLabel]
UpdateDate = datetime
CreationDate = datetime


class ApplicationDescription(TypedDict, total=False):
    """Describes the properties of an application."""

    ApplicationArn: Optional[ApplicationArn]
    ApplicationName: Optional[ApplicationName]
    Description: Optional[Description]
    DateCreated: Optional[CreationDate]
    DateUpdated: Optional[UpdateDate]
    Versions: Optional[VersionLabelsList]
    ConfigurationTemplates: Optional[ConfigurationTemplateNamesList]
    ResourceLifecycleConfig: Optional[ApplicationResourceLifecycleConfig]


ApplicationDescriptionList = List[ApplicationDescription]


class ApplicationDescriptionMessage(TypedDict, total=False):
    """Result message containing a single description of an application."""

    Application: Optional[ApplicationDescription]


class ApplicationDescriptionsMessage(TypedDict, total=False):
    """Result message containing a list of application descriptions."""

    Applications: Optional[ApplicationDescriptionList]


class Latency(TypedDict, total=False):
    """Represents the average latency for the slowest X percent of requests
    over the last 10 seconds.
    """

    P999: Optional[NullableDouble]
    P99: Optional[NullableDouble]
    P95: Optional[NullableDouble]
    P90: Optional[NullableDouble]
    P85: Optional[NullableDouble]
    P75: Optional[NullableDouble]
    P50: Optional[NullableDouble]
    P10: Optional[NullableDouble]


class StatusCodes(TypedDict, total=False):
    """Represents the percentage of requests over the last 10 seconds that
    resulted in each type of status code response. For more information, see
    `Status Code
    Definitions <http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html>`__.
    """

    Status2xx: Optional[NullableInteger]
    Status3xx: Optional[NullableInteger]
    Status4xx: Optional[NullableInteger]
    Status5xx: Optional[NullableInteger]


class ApplicationMetrics(TypedDict, total=False):
    """Application request metrics for an AWS Elastic Beanstalk environment."""

    Duration: Optional[NullableInteger]
    RequestCount: Optional[RequestCount]
    StatusCodes: Optional[StatusCodes]
    Latency: Optional[Latency]


ApplicationNamesList = List[ApplicationName]


class ApplicationResourceLifecycleDescriptionMessage(TypedDict, total=False):
    ApplicationName: Optional[ApplicationName]
    ResourceLifecycleConfig: Optional[ApplicationResourceLifecycleConfig]


class S3Location(TypedDict, total=False):
    """The bucket and key of an item stored in Amazon S3."""

    S3Bucket: Optional[S3Bucket]
    S3Key: Optional[S3Key]


class SourceBuildInformation(TypedDict, total=False):
    """Location of the source code for an application version."""

    SourceType: SourceType
    SourceRepository: SourceRepository
    SourceLocation: SourceLocation


class ApplicationVersionDescription(TypedDict, total=False):
    """Describes the properties of an application version."""

    ApplicationVersionArn: Optional[ApplicationVersionArn]
    ApplicationName: Optional[ApplicationName]
    Description: Optional[Description]
    VersionLabel: Optional[VersionLabel]
    SourceBuildInformation: Optional[SourceBuildInformation]
    BuildArn: Optional[String]
    SourceBundle: Optional[S3Location]
    DateCreated: Optional[CreationDate]
    DateUpdated: Optional[UpdateDate]
    Status: Optional[ApplicationVersionStatus]


ApplicationVersionDescriptionList = List[ApplicationVersionDescription]


class ApplicationVersionDescriptionMessage(TypedDict, total=False):
    """Result message wrapping a single description of an application version."""

    ApplicationVersion: Optional[ApplicationVersionDescription]


class ApplicationVersionDescriptionsMessage(TypedDict, total=False):
    """Result message wrapping a list of application version descriptions."""

    ApplicationVersions: Optional[ApplicationVersionDescriptionList]
    NextToken: Optional[Token]


class ApplyEnvironmentManagedActionRequest(ServiceRequest):
    """Request to execute a scheduled managed action immediately."""

    EnvironmentName: Optional[String]
    EnvironmentId: Optional[String]
    ActionId: String


class ApplyEnvironmentManagedActionResult(TypedDict, total=False):
    """The result message containing information about the managed action."""

    ActionId: Optional[String]
    ActionDescription: Optional[String]
    ActionType: Optional[ActionType]
    Status: Optional[String]


class AssociateEnvironmentOperationsRoleMessage(ServiceRequest):
    """Request to add or change the operations role used by an environment."""

    EnvironmentName: EnvironmentName
    OperationsRole: OperationsRole


class AutoScalingGroup(TypedDict, total=False):
    """Describes an Auto Scaling launch configuration."""

    Name: Optional[ResourceId]


AutoScalingGroupList = List[AutoScalingGroup]
SolutionStackFileTypeList = List[FileTypeExtension]


class SolutionStackDescription(TypedDict, total=False):
    """Describes the solution stack."""

    SolutionStackName: Optional[SolutionStackName]
    PermittedFileTypes: Optional[SolutionStackFileTypeList]


AvailableSolutionStackDetailsList = List[SolutionStackDescription]
AvailableSolutionStackNamesList = List[SolutionStackName]


class BuildConfiguration(TypedDict, total=False):
    """Settings for an AWS CodeBuild build."""

    ArtifactName: Optional[String]
    CodeBuildServiceRole: NonEmptyString
    ComputeType: Optional[ComputeType]
    Image: NonEmptyString
    TimeoutInMinutes: Optional[BoxedInt]


class Builder(TypedDict, total=False):
    """The builder used to build the custom platform."""

    ARN: Optional[ARN]


class CPUUtilization(TypedDict, total=False):
    """CPU utilization metrics for an instance."""

    User: Optional[NullableDouble]
    Nice: Optional[NullableDouble]
    System: Optional[NullableDouble]
    Idle: Optional[NullableDouble]
    IOWait: Optional[NullableDouble]
    IRQ: Optional[NullableDouble]
    SoftIRQ: Optional[NullableDouble]
    Privileged: Optional[NullableDouble]


Causes = List[Cause]


class CheckDNSAvailabilityMessage(ServiceRequest):
    """Results message indicating whether a CNAME is available."""

    CNAMEPrefix: DNSCnamePrefix


class CheckDNSAvailabilityResultMessage(TypedDict, total=False):
    """Indicates if the specified CNAME is available."""

    Available: Optional[CnameAvailability]
    FullyQualifiedCNAME: Optional[DNSCname]


VersionLabels = List[VersionLabel]


class ComposeEnvironmentsMessage(ServiceRequest):
    """Request to create or update a group of environments."""

    ApplicationName: Optional[ApplicationName]
    GroupName: Optional[GroupName]
    VersionLabels: Optional[VersionLabels]


class OptionRestrictionRegex(TypedDict, total=False):
    """A regular expression representing a restriction on a string
    configuration option value.
    """

    Pattern: Optional[RegexPattern]
    Label: Optional[RegexLabel]


ConfigurationOptionPossibleValues = List[ConfigurationOptionPossibleValue]


class ConfigurationOptionDescription(TypedDict, total=False):
    """Describes the possible values for a configuration option."""

    Namespace: Optional[OptionNamespace]
    Name: Optional[ConfigurationOptionName]
    DefaultValue: Optional[ConfigurationOptionDefaultValue]
    ChangeSeverity: Optional[ConfigurationOptionSeverity]
    UserDefined: Optional[UserDefinedOption]
    ValueType: Optional[ConfigurationOptionValueType]
    ValueOptions: Optional[ConfigurationOptionPossibleValues]
    MinValue: Optional[OptionRestrictionMinValue]
    MaxValue: Optional[OptionRestrictionMaxValue]
    MaxLength: Optional[OptionRestrictionMaxLength]
    Regex: Optional[OptionRestrictionRegex]


ConfigurationOptionDescriptionsList = List[ConfigurationOptionDescription]


class ConfigurationOptionSetting(TypedDict, total=False):
    """A specification identifying an individual configuration option along
    with its current value. For a list of possible namespaces and option
    values, see `Option
    Values <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/command-options.html>`__
    in the *AWS Elastic Beanstalk Developer Guide*.
    """

    ResourceName: Optional[ResourceName]
    Namespace: Optional[OptionNamespace]
    OptionName: Optional[ConfigurationOptionName]
    Value: Optional[ConfigurationOptionValue]


ConfigurationOptionSettingsList = List[ConfigurationOptionSetting]


class ConfigurationOptionsDescription(TypedDict, total=False):
    """Describes the settings for a specified configuration set."""

    SolutionStackName: Optional[SolutionStackName]
    PlatformArn: Optional[PlatformArn]
    Options: Optional[ConfigurationOptionDescriptionsList]


class ConfigurationSettingsDescription(TypedDict, total=False):
    """Describes the settings for a configuration set."""

    SolutionStackName: Optional[SolutionStackName]
    PlatformArn: Optional[PlatformArn]
    ApplicationName: Optional[ApplicationName]
    TemplateName: Optional[ConfigurationTemplateName]
    Description: Optional[Description]
    EnvironmentName: Optional[EnvironmentName]
    DeploymentStatus: Optional[ConfigurationDeploymentStatus]
    DateCreated: Optional[CreationDate]
    DateUpdated: Optional[UpdateDate]
    OptionSettings: Optional[ConfigurationOptionSettingsList]


ConfigurationSettingsDescriptionList = List[ConfigurationSettingsDescription]


class ConfigurationSettingsDescriptions(TypedDict, total=False):
    """The results from a request to change the configuration settings of an
    environment.
    """

    ConfigurationSettings: Optional[ConfigurationSettingsDescriptionList]


class ValidationMessage(TypedDict, total=False):
    """An error or warning for a desired configuration option value."""

    Message: Optional[ValidationMessageString]
    Severity: Optional[ValidationSeverity]
    Namespace: Optional[OptionNamespace]
    OptionName: Optional[ConfigurationOptionName]


ValidationMessagesList = List[ValidationMessage]


class ConfigurationSettingsValidationMessages(TypedDict, total=False):
    """Provides a list of validation messages."""

    Messages: Optional[ValidationMessagesList]


class Tag(TypedDict, total=False):
    """Describes a tag applied to a resource in an environment."""

    Key: Optional[TagKey]
    Value: Optional[TagValue]


Tags = List[Tag]


class CreateApplicationMessage(ServiceRequest):
    """Request to create an application."""

    ApplicationName: ApplicationName
    Description: Optional[Description]
    ResourceLifecycleConfig: Optional[ApplicationResourceLifecycleConfig]
    Tags: Optional[Tags]


class CreateApplicationVersionMessage(ServiceRequest):
    ApplicationName: ApplicationName
    VersionLabel: VersionLabel
    Description: Optional[Description]
    SourceBuildInformation: Optional[SourceBuildInformation]
    SourceBundle: Optional[S3Location]
    BuildConfiguration: Optional[BuildConfiguration]
    AutoCreateApplication: Optional[AutoCreateApplication]
    Process: Optional[ApplicationVersionProccess]
    Tags: Optional[Tags]


class SourceConfiguration(TypedDict, total=False):
    """A specification for an environment configuration."""

    ApplicationName: Optional[ApplicationName]
    TemplateName: Optional[ConfigurationTemplateName]


class CreateConfigurationTemplateMessage(ServiceRequest):
    """Request to create a configuration template."""

    ApplicationName: ApplicationName
    TemplateName: ConfigurationTemplateName
    SolutionStackName: Optional[SolutionStackName]
    PlatformArn: Optional[PlatformArn]
    SourceConfiguration: Optional[SourceConfiguration]
    EnvironmentId: Optional[EnvironmentId]
    Description: Optional[Description]
    OptionSettings: Optional[ConfigurationOptionSettingsList]
    Tags: Optional[Tags]


class OptionSpecification(TypedDict, total=False):
    """A specification identifying an individual configuration option."""

    ResourceName: Optional[ResourceName]
    Namespace: Optional[OptionNamespace]
    OptionName: Optional[ConfigurationOptionName]


OptionsSpecifierList = List[OptionSpecification]


class EnvironmentTier(TypedDict, total=False):
    """Describes the properties of an environment tier"""

    Name: Optional[String]
    Type: Optional[String]
    Version: Optional[String]


class CreateEnvironmentMessage(ServiceRequest):
    ApplicationName: ApplicationName
    EnvironmentName: Optional[EnvironmentName]
    GroupName: Optional[GroupName]
    Description: Optional[Description]
    CNAMEPrefix: Optional[DNSCnamePrefix]
    Tier: Optional[EnvironmentTier]
    Tags: Optional[Tags]
    VersionLabel: Optional[VersionLabel]
    TemplateName: Optional[ConfigurationTemplateName]
    SolutionStackName: Optional[SolutionStackName]
    PlatformArn: Optional[PlatformArn]
    OptionSettings: Optional[ConfigurationOptionSettingsList]
    OptionsToRemove: Optional[OptionsSpecifierList]
    OperationsRole: Optional[OperationsRole]


class CreatePlatformVersionRequest(ServiceRequest):
    """Request to create a new platform version."""

    PlatformName: PlatformName
    PlatformVersion: PlatformVersion
    PlatformDefinitionBundle: S3Location
    EnvironmentName: Optional[EnvironmentName]
    OptionSettings: Optional[ConfigurationOptionSettingsList]
    Tags: Optional[Tags]


SupportedAddonList = List[SupportedAddon]
SupportedTierList = List[SupportedTier]


class PlatformSummary(TypedDict, total=False):
    """Summary information about a platform version."""

    PlatformArn: Optional[PlatformArn]
    PlatformOwner: Optional[PlatformOwner]
    PlatformStatus: Optional[PlatformStatus]
    PlatformCategory: Optional[PlatformCategory]
    OperatingSystemName: Optional[OperatingSystemName]
    OperatingSystemVersion: Optional[OperatingSystemVersion]
    SupportedTierList: Optional[SupportedTierList]
    SupportedAddonList: Optional[SupportedAddonList]
    PlatformLifecycleState: Optional[PlatformLifecycleState]
    PlatformVersion: Optional[PlatformVersion]
    PlatformBranchName: Optional[BranchName]
    PlatformBranchLifecycleState: Optional[PlatformBranchLifecycleState]


class CreatePlatformVersionResult(TypedDict, total=False):
    PlatformSummary: Optional[PlatformSummary]
    Builder: Optional[Builder]


class CreateStorageLocationResultMessage(TypedDict, total=False):
    """Results of a CreateStorageLocationResult call."""

    S3Bucket: Optional[S3Bucket]


class CustomAmi(TypedDict, total=False):
    """A custom AMI available to platforms."""

    VirtualizationType: Optional[VirtualizationType]
    ImageId: Optional[ImageId]


CustomAmiList = List[CustomAmi]


class DeleteApplicationMessage(ServiceRequest):
    """Request to delete an application."""

    ApplicationName: ApplicationName
    TerminateEnvByForce: Optional[TerminateEnvForce]


class DeleteApplicationVersionMessage(ServiceRequest):
    """Request to delete an application version."""

    ApplicationName: ApplicationName
    VersionLabel: VersionLabel
    DeleteSourceBundle: Optional[DeleteSourceBundle]


class DeleteConfigurationTemplateMessage(ServiceRequest):
    """Request to delete a configuration template."""

    ApplicationName: ApplicationName
    TemplateName: ConfigurationTemplateName


class DeleteEnvironmentConfigurationMessage(ServiceRequest):
    """Request to delete a draft environment configuration."""

    ApplicationName: ApplicationName
    EnvironmentName: EnvironmentName


class DeletePlatformVersionRequest(ServiceRequest):
    PlatformArn: Optional[PlatformArn]


class DeletePlatformVersionResult(TypedDict, total=False):
    PlatformSummary: Optional[PlatformSummary]


DeploymentTimestamp = datetime
NullableLong = int


class Deployment(TypedDict, total=False):
    """Information about an application version deployment."""

    VersionLabel: Optional[String]
    DeploymentId: Optional[NullableLong]
    Status: Optional[String]
    DeploymentTime: Optional[DeploymentTimestamp]


class ResourceQuota(TypedDict, total=False):
    """The AWS Elastic Beanstalk quota information for a single resource type
    in an AWS account. It reflects the resource's limits for this account.
    """

    Maximum: Optional[BoxedInt]


class ResourceQuotas(TypedDict, total=False):
    """A set of per-resource AWS Elastic Beanstalk quotas associated with an
    AWS account. They reflect Elastic Beanstalk resource limits for this
    account.
    """

    ApplicationQuota: Optional[ResourceQuota]
    ApplicationVersionQuota: Optional[ResourceQuota]
    EnvironmentQuota: Optional[ResourceQuota]
    ConfigurationTemplateQuota: Optional[ResourceQuota]
    CustomPlatformQuota: Optional[ResourceQuota]


class DescribeAccountAttributesResult(TypedDict, total=False):
    ResourceQuotas: Optional[ResourceQuotas]


class DescribeApplicationVersionsMessage(ServiceRequest):
    """Request to describe application versions."""

    ApplicationName: Optional[ApplicationName]
    VersionLabels: Optional[VersionLabelsList]
    MaxRecords: Optional[MaxRecords]
    NextToken: Optional[Token]


class DescribeApplicationsMessage(ServiceRequest):
    """Request to describe one or more applications."""

    ApplicationNames: Optional[ApplicationNamesList]


class DescribeConfigurationOptionsMessage(ServiceRequest):
    """Result message containing a list of application version descriptions."""

    ApplicationName: Optional[ApplicationName]
    TemplateName: Optional[ConfigurationTemplateName]
    EnvironmentName: Optional[EnvironmentName]
    SolutionStackName: Optional[SolutionStackName]
    PlatformArn: Optional[PlatformArn]
    Options: Optional[OptionsSpecifierList]


class DescribeConfigurationSettingsMessage(ServiceRequest):
    """Result message containing all of the configuration settings for a
    specified solution stack or configuration template.
    """

    ApplicationName: ApplicationName
    TemplateName: Optional[ConfigurationTemplateName]
    EnvironmentName: Optional[EnvironmentName]


EnvironmentHealthAttributes = List[EnvironmentHealthAttribute]


class DescribeEnvironmentHealthRequest(ServiceRequest):
    """See the example below to learn how to create a request body."""

    EnvironmentName: Optional[EnvironmentName]
    EnvironmentId: Optional[EnvironmentId]
    AttributeNames: Optional[EnvironmentHealthAttributes]


RefreshedAt = datetime


class InstanceHealthSummary(TypedDict, total=False):
    """Represents summary information about the health of an instance. For more
    information, see `Health Colors and
    Statuses <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/health-enhanced-status.html>`__.
    """

    NoData: Optional[NullableInteger]
    Unknown: Optional[NullableInteger]
    Pending: Optional[NullableInteger]
    Ok: Optional[NullableInteger]
    Info: Optional[NullableInteger]
    Warning: Optional[NullableInteger]
    Degraded: Optional[NullableInteger]
    Severe: Optional[NullableInteger]


class DescribeEnvironmentHealthResult(TypedDict, total=False):
    """Health details for an AWS Elastic Beanstalk environment."""

    EnvironmentName: Optional[EnvironmentName]
    HealthStatus: Optional[String]
    Status: Optional[EnvironmentHealth]
    Color: Optional[String]
    Causes: Optional[Causes]
    ApplicationMetrics: Optional[ApplicationMetrics]
    InstancesHealth: Optional[InstanceHealthSummary]
    RefreshedAt: Optional[RefreshedAt]


class DescribeEnvironmentManagedActionHistoryRequest(ServiceRequest):
    """Request to list completed and failed managed actions."""

    EnvironmentId: Optional[EnvironmentId]
    EnvironmentName: Optional[EnvironmentName]
    NextToken: Optional[String]
    MaxItems: Optional[ManagedActionHistoryMaxItems]


Timestamp = datetime


class ManagedActionHistoryItem(TypedDict, total=False):
    """The record of a completed or failed managed action."""

    ActionId: Optional[String]
    ActionType: Optional[ActionType]
    ActionDescription: Optional[String]
    FailureType: Optional[FailureType]
    Status: Optional[ActionHistoryStatus]
    FailureDescription: Optional[String]
    ExecutedTime: Optional[Timestamp]
    FinishedTime: Optional[Timestamp]


ManagedActionHistoryItems = List[ManagedActionHistoryItem]


class DescribeEnvironmentManagedActionHistoryResult(TypedDict, total=False):
    """A result message containing a list of completed and failed managed
    actions.
    """

    ManagedActionHistoryItems: Optional[ManagedActionHistoryItems]
    NextToken: Optional[String]


class DescribeEnvironmentManagedActionsRequest(ServiceRequest):
    """Request to list an environment's upcoming and in-progress managed
    actions.
    """

    EnvironmentName: Optional[String]
    EnvironmentId: Optional[String]
    Status: Optional[ActionStatus]


class ManagedAction(TypedDict, total=False):
    """The record of an upcoming or in-progress managed action."""

    ActionId: Optional[String]
    ActionDescription: Optional[String]
    ActionType: Optional[ActionType]
    Status: Optional[ActionStatus]
    WindowStartTime: Optional[Timestamp]


ManagedActions = List[ManagedAction]


class DescribeEnvironmentManagedActionsResult(TypedDict, total=False):
    """The result message containing a list of managed actions."""

    ManagedActions: Optional[ManagedActions]


class DescribeEnvironmentResourcesMessage(ServiceRequest):
    """Request to describe the resources in an environment."""

    EnvironmentId: Optional[EnvironmentId]
    EnvironmentName: Optional[EnvironmentName]


IncludeDeletedBackTo = datetime
EnvironmentNamesList = List[EnvironmentName]
EnvironmentIdList = List[EnvironmentId]


class DescribeEnvironmentsMessage(ServiceRequest):
    """Request to describe one or more environments."""

    ApplicationName: Optional[ApplicationName]
    VersionLabel: Optional[VersionLabel]
    EnvironmentIds: Optional[EnvironmentIdList]
    EnvironmentNames: Optional[EnvironmentNamesList]
    IncludeDeleted: Optional[IncludeDeleted]
    IncludedDeletedBackTo: Optional[IncludeDeletedBackTo]
    MaxRecords: Optional[MaxRecords]
    NextToken: Optional[Token]


TimeFilterEnd = datetime
TimeFilterStart = datetime


class DescribeEventsMessage(ServiceRequest):
    """Request to retrieve a list of events for an environment."""

    ApplicationName: Optional[ApplicationName]
    VersionLabel: Optional[VersionLabel]
    TemplateName: Optional[ConfigurationTemplateName]
    EnvironmentId: Optional[EnvironmentId]
    EnvironmentName: Optional[EnvironmentName]
    PlatformArn: Optional[PlatformArn]
    RequestId: Optional[RequestId]
    Severity: Optional[EventSeverity]
    StartTime: Optional[TimeFilterStart]
    EndTime: Optional[TimeFilterEnd]
    MaxRecords: Optional[MaxRecords]
    NextToken: Optional[Token]


InstancesHealthAttributes = List[InstancesHealthAttribute]


class DescribeInstancesHealthRequest(ServiceRequest):
    """Parameters for a call to ``DescribeInstancesHealth``."""

    EnvironmentName: Optional[EnvironmentName]
    EnvironmentId: Optional[EnvironmentId]
    AttributeNames: Optional[InstancesHealthAttributes]
    NextToken: Optional[NextToken]


LoadAverage = List[LoadAverageValue]


class SystemStatus(TypedDict, total=False):
    """CPU utilization and load average metrics for an Amazon EC2 instance."""

    CPUUtilization: Optional[CPUUtilization]
    LoadAverage: Optional[LoadAverage]


LaunchedAt = datetime


class SingleInstanceHealth(TypedDict, total=False):
    """Detailed health information about an Amazon EC2 instance in your Elastic
    Beanstalk environment.
    """

    InstanceId: Optional[InstanceId]
    HealthStatus: Optional[String]
    Color: Optional[String]
    Causes: Optional[Causes]
    LaunchedAt: Optional[LaunchedAt]
    ApplicationMetrics: Optional[ApplicationMetrics]
    System: Optional[SystemStatus]
    Deployment: Optional[Deployment]
    AvailabilityZone: Optional[String]
    InstanceType: Optional[String]


InstanceHealthList = List[SingleInstanceHealth]


class DescribeInstancesHealthResult(TypedDict, total=False):
    """Detailed health information about the Amazon EC2 instances in an AWS
    Elastic Beanstalk environment.
    """

    InstanceHealthList: Optional[InstanceHealthList]
    RefreshedAt: Optional[RefreshedAt]
    NextToken: Optional[NextToken]


class DescribePlatformVersionRequest(ServiceRequest):
    PlatformArn: Optional[PlatformArn]


class PlatformFramework(TypedDict, total=False):
    """A framework supported by the platform."""

    Name: Optional[String]
    Version: Optional[String]


PlatformFrameworks = List[PlatformFramework]


class PlatformProgrammingLanguage(TypedDict, total=False):
    """A programming language supported by the platform."""

    Name: Optional[String]
    Version: Optional[String]


PlatformProgrammingLanguages = List[PlatformProgrammingLanguage]


class PlatformDescription(TypedDict, total=False):
    """Detailed information about a platform version."""

    PlatformArn: Optional[PlatformArn]
    PlatformOwner: Optional[PlatformOwner]
    PlatformName: Optional[PlatformName]
    PlatformVersion: Optional[PlatformVersion]
    SolutionStackName: Optional[SolutionStackName]
    PlatformStatus: Optional[PlatformStatus]
    DateCreated: Optional[CreationDate]
    DateUpdated: Optional[UpdateDate]
    PlatformCategory: Optional[PlatformCategory]
    Description: Optional[Description]
    Maintainer: Optional[Maintainer]
    OperatingSystemName: Optional[OperatingSystemName]
    OperatingSystemVersion: Optional[OperatingSystemVersion]
    ProgrammingLanguages: Optional[PlatformProgrammingLanguages]
    Frameworks: Optional[PlatformFrameworks]
    CustomAmiList: Optional[CustomAmiList]
    SupportedTierList: Optional[SupportedTierList]
    SupportedAddonList: Optional[SupportedAddonList]
    PlatformLifecycleState: Optional[PlatformLifecycleState]
    PlatformBranchName: Optional[BranchName]
    PlatformBranchLifecycleState: Optional[PlatformBranchLifecycleState]


class DescribePlatformVersionResult(TypedDict, total=False):
    PlatformDescription: Optional[PlatformDescription]


class DisassociateEnvironmentOperationsRoleMessage(ServiceRequest):
    """Request to disassociate the operations role from an environment."""

    EnvironmentName: EnvironmentName


class EnvironmentLink(TypedDict, total=False):
    """A link to another environment, defined in the environment's manifest.
    Links provide connection information in system properties that can be
    used to connect to another environment in the same group. See
    `Environment Manifest
    (env.yaml) <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/environment-cfg-manifest.html>`__
    for details.
    """

    LinkName: Optional[String]
    EnvironmentName: Optional[String]


EnvironmentLinks = List[EnvironmentLink]


class Listener(TypedDict, total=False):
    """Describes the properties of a Listener for the LoadBalancer."""

    Protocol: Optional[String]
    Port: Optional[Integer]


LoadBalancerListenersDescription = List[Listener]


class LoadBalancerDescription(TypedDict, total=False):
    """Describes the details of a LoadBalancer."""

    LoadBalancerName: Optional[String]
    Domain: Optional[String]
    Listeners: Optional[LoadBalancerListenersDescription]


class EnvironmentResourcesDescription(TypedDict, total=False):
    """Describes the AWS resources in use by this environment. This data is not
    live data.
    """

    LoadBalancer: Optional[LoadBalancerDescription]


class EnvironmentDescription(TypedDict, total=False):
    """Describes the properties of an environment."""

    EnvironmentName: Optional[EnvironmentName]
    EnvironmentId: Optional[EnvironmentId]
    ApplicationName: Optional[ApplicationName]
    VersionLabel: Optional[VersionLabel]
    SolutionStackName: Optional[SolutionStackName]
    PlatformArn: Optional[PlatformArn]
    TemplateName: Optional[ConfigurationTemplateName]
    Description: Optional[Description]
    EndpointURL: Optional[EndpointURL]
    CNAME: Optional[DNSCname]
    DateCreated: Optional[CreationDate]
    DateUpdated: Optional[UpdateDate]
    Status: Optional[EnvironmentStatus]
    AbortableOperationInProgress: Optional[AbortableOperationInProgress]
    Health: Optional[EnvironmentHealth]
    HealthStatus: Optional[EnvironmentHealthStatus]
    Resources: Optional[EnvironmentResourcesDescription]
    Tier: Optional[EnvironmentTier]
    EnvironmentLinks: Optional[EnvironmentLinks]
    EnvironmentArn: Optional[EnvironmentArn]
    OperationsRole: Optional[OperationsRole]


EnvironmentDescriptionsList = List[EnvironmentDescription]


class EnvironmentDescriptionsMessage(TypedDict, total=False):
    """Result message containing a list of environment descriptions."""

    Environments: Optional[EnvironmentDescriptionsList]
    NextToken: Optional[Token]


SampleTimestamp = datetime


class EnvironmentInfoDescription(TypedDict, total=False):
    """The information retrieved from the Amazon EC2 instances."""

    InfoType: Optional[EnvironmentInfoType]
    Ec2InstanceId: Optional[Ec2InstanceId]
    SampleTimestamp: Optional[SampleTimestamp]
    Message: Optional[Message]


EnvironmentInfoDescriptionList = List[EnvironmentInfoDescription]


class Queue(TypedDict, total=False):
    """Describes a queue."""

    Name: Optional[String]
    URL: Optional[String]


QueueList = List[Queue]


class Trigger(TypedDict, total=False):
    """Describes a trigger."""

    Name: Optional[ResourceId]


TriggerList = List[Trigger]


class LoadBalancer(TypedDict, total=False):
    """Describes a LoadBalancer."""

    Name: Optional[ResourceId]


LoadBalancerList = List[LoadBalancer]


class LaunchTemplate(TypedDict, total=False):
    """Describes an Amazon EC2 launch template."""

    Id: Optional[ResourceId]


LaunchTemplateList = List[LaunchTemplate]


class LaunchConfiguration(TypedDict, total=False):
    """Describes an Auto Scaling launch configuration."""

    Name: Optional[ResourceId]


LaunchConfigurationList = List[LaunchConfiguration]


class Instance(TypedDict, total=False):
    """The description of an Amazon EC2 instance."""

    Id: Optional[ResourceId]


InstanceList = List[Instance]


class EnvironmentResourceDescription(TypedDict, total=False):
    """Describes the AWS resources in use by this environment. This data is
    live.
    """

    EnvironmentName: Optional[EnvironmentName]
    AutoScalingGroups: Optional[AutoScalingGroupList]
    Instances: Optional[InstanceList]
    LaunchConfigurations: Optional[LaunchConfigurationList]
    LaunchTemplates: Optional[LaunchTemplateList]
    LoadBalancers: Optional[LoadBalancerList]
    Triggers: Optional[TriggerList]
    Queues: Optional[QueueList]


class EnvironmentResourceDescriptionsMessage(TypedDict, total=False):
    """Result message containing a list of environment resource descriptions."""

    EnvironmentResources: Optional[EnvironmentResourceDescription]


EventDate = datetime


class EventDescription(TypedDict, total=False):
    """Describes an event."""

    EventDate: Optional[EventDate]
    Message: Optional[EventMessage]
    ApplicationName: Optional[ApplicationName]
    VersionLabel: Optional[VersionLabel]
    TemplateName: Optional[ConfigurationTemplateName]
    EnvironmentName: Optional[EnvironmentName]
    PlatformArn: Optional[PlatformArn]
    RequestId: Optional[RequestId]
    Severity: Optional[EventSeverity]


EventDescriptionList = List[EventDescription]


class EventDescriptionsMessage(TypedDict, total=False):
    """Result message wrapping a list of event descriptions."""

    Events: Optional[EventDescriptionList]
    NextToken: Optional[Token]


class ListAvailableSolutionStacksResultMessage(TypedDict, total=False):
    """A list of available AWS Elastic Beanstalk solution stacks."""

    SolutionStacks: Optional[AvailableSolutionStackNamesList]
    SolutionStackDetails: Optional[AvailableSolutionStackDetailsList]


SearchFilterValues = List[SearchFilterValue]


class SearchFilter(TypedDict, total=False):
    """Describes criteria to restrict a list of results.

    For operators that apply a single value to the attribute, the filter is
    evaluated as follows: ``Attribute Operator Values[1]``

    Some operators, e.g. ``in``, can apply multiple values. In this case,
    the filter is evaluated as a logical union (OR) of applications of the
    operator to the attribute with each one of the values:
    ``(Attribute Operator Values[1]) OR (Attribute Operator Values[2]) OR ...``

    The valid values for attributes of ``SearchFilter`` depend on the API
    action. For valid values, see the reference page for the API action
    you're calling that takes a ``SearchFilter`` parameter.
    """

    Attribute: Optional[SearchFilterAttribute]
    Operator: Optional[SearchFilterOperator]
    Values: Optional[SearchFilterValues]


SearchFilters = List[SearchFilter]


class ListPlatformBranchesRequest(ServiceRequest):
    Filters: Optional[SearchFilters]
    MaxRecords: Optional[PlatformBranchMaxRecords]
    NextToken: Optional[Token]


class PlatformBranchSummary(TypedDict, total=False):
    """Summary information about a platform branch."""

    PlatformName: Optional[PlatformName]
    BranchName: Optional[BranchName]
    LifecycleState: Optional[PlatformBranchLifecycleState]
    BranchOrder: Optional[BranchOrder]
    SupportedTierList: Optional[SupportedTierList]


PlatformBranchSummaryList = List[PlatformBranchSummary]


class ListPlatformBranchesResult(TypedDict, total=False):
    PlatformBranchSummaryList: Optional[PlatformBranchSummaryList]
    NextToken: Optional[Token]


PlatformFilterValueList = List[PlatformFilterValue]


class PlatformFilter(TypedDict, total=False):
    """Describes criteria to restrict the results when listing platform
    versions.

    The filter is evaluated as follows: ``Type Operator Values[1]``
    """

    Type: Optional[PlatformFilterType]
    Operator: Optional[PlatformFilterOperator]
    Values: Optional[PlatformFilterValueList]


PlatformFilters = List[PlatformFilter]


class ListPlatformVersionsRequest(ServiceRequest):
    Filters: Optional[PlatformFilters]
    MaxRecords: Optional[PlatformMaxRecords]
    NextToken: Optional[Token]


PlatformSummaryList = List[PlatformSummary]


class ListPlatformVersionsResult(TypedDict, total=False):
    PlatformSummaryList: Optional[PlatformSummaryList]
    NextToken: Optional[Token]


class ListTagsForResourceMessage(ServiceRequest):
    ResourceArn: ResourceArn


class RebuildEnvironmentMessage(ServiceRequest):
    EnvironmentId: Optional[EnvironmentId]
    EnvironmentName: Optional[EnvironmentName]


class RequestEnvironmentInfoMessage(ServiceRequest):
    """Request to retrieve logs from an environment and store them in your
    Elastic Beanstalk storage bucket.
    """

    EnvironmentId: Optional[EnvironmentId]
    EnvironmentName: Optional[EnvironmentName]
    InfoType: EnvironmentInfoType


TagList = List[Tag]


class ResourceTagsDescriptionMessage(TypedDict, total=False):
    ResourceArn: Optional[ResourceArn]
    ResourceTags: Optional[TagList]


class RestartAppServerMessage(ServiceRequest):
    EnvironmentId: Optional[EnvironmentId]
    EnvironmentName: Optional[EnvironmentName]


class RetrieveEnvironmentInfoMessage(ServiceRequest):
    """Request to download logs retrieved with RequestEnvironmentInfo."""

    EnvironmentId: Optional[EnvironmentId]
    EnvironmentName: Optional[EnvironmentName]
    InfoType: EnvironmentInfoType


class RetrieveEnvironmentInfoResultMessage(TypedDict, total=False):
    """Result message containing a description of the requested environment
    info.
    """

    EnvironmentInfo: Optional[EnvironmentInfoDescriptionList]


class SwapEnvironmentCNAMEsMessage(ServiceRequest):
    """Swaps the CNAMEs of two environments."""

    SourceEnvironmentId: Optional[EnvironmentId]
    SourceEnvironmentName: Optional[EnvironmentName]
    DestinationEnvironmentId: Optional[EnvironmentId]
    DestinationEnvironmentName: Optional[EnvironmentName]


TagKeyList = List[TagKey]


class TerminateEnvironmentMessage(ServiceRequest):
    """Request to terminate an environment."""

    EnvironmentId: Optional[EnvironmentId]
    EnvironmentName: Optional[EnvironmentName]
    TerminateResources: Optional[TerminateEnvironmentResources]
    ForceTerminate: Optional[ForceTerminate]


class UpdateApplicationMessage(ServiceRequest):
    """Request to update an application."""

    ApplicationName: ApplicationName
    Description: Optional[Description]


class UpdateApplicationResourceLifecycleMessage(ServiceRequest):
    ApplicationName: ApplicationName
    ResourceLifecycleConfig: ApplicationResourceLifecycleConfig


class UpdateApplicationVersionMessage(ServiceRequest):
    ApplicationName: ApplicationName
    VersionLabel: VersionLabel
    Description: Optional[Description]


class UpdateConfigurationTemplateMessage(ServiceRequest):
    """The result message containing the options for the specified solution
    stack.
    """

    ApplicationName: ApplicationName
    TemplateName: ConfigurationTemplateName
    Description: Optional[Description]
    OptionSettings: Optional[ConfigurationOptionSettingsList]
    OptionsToRemove: Optional[OptionsSpecifierList]


class UpdateEnvironmentMessage(ServiceRequest):
    """Request to update an environment."""

    ApplicationName: Optional[ApplicationName]
    EnvironmentId: Optional[EnvironmentId]
    EnvironmentName: Optional[EnvironmentName]
    GroupName: Optional[GroupName]
    Description: Optional[Description]
    Tier: Optional[EnvironmentTier]
    VersionLabel: Optional[VersionLabel]
    TemplateName: Optional[ConfigurationTemplateName]
    SolutionStackName: Optional[SolutionStackName]
    PlatformArn: Optional[PlatformArn]
    OptionSettings: Optional[ConfigurationOptionSettingsList]
    OptionsToRemove: Optional[OptionsSpecifierList]


class UpdateTagsForResourceMessage(ServiceRequest):
    ResourceArn: ResourceArn
    TagsToAdd: Optional[TagList]
    TagsToRemove: Optional[TagKeyList]


class ValidateConfigurationSettingsMessage(ServiceRequest):
    """A list of validation messages for a specified configuration template."""

    ApplicationName: ApplicationName
    TemplateName: Optional[ConfigurationTemplateName]
    EnvironmentName: Optional[EnvironmentName]
    OptionSettings: ConfigurationOptionSettingsList


class ElasticbeanstalkApi:

    service = "elasticbeanstalk"
    version = "2010-12-01"

    @handler("AbortEnvironmentUpdate")
    def abort_environment_update(
        self,
        context: RequestContext,
        environment_id: EnvironmentId = None,
        environment_name: EnvironmentName = None,
    ) -> None:
        """Cancels in-progress environment configuration update or application
        version deployment.

        :param environment_id: This specifies the ID of the environment with the in-progress update
        that you want to cancel.
        :param environment_name: This specifies the name of the environment with the in-progress update
        that you want to cancel.
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("ApplyEnvironmentManagedAction")
    def apply_environment_managed_action(
        self,
        context: RequestContext,
        action_id: String,
        environment_name: String = None,
        environment_id: String = None,
    ) -> ApplyEnvironmentManagedActionResult:
        """Applies a scheduled managed action immediately. A managed action can be
        applied only if its status is ``Scheduled``. Get the status and action
        ID of a managed action with DescribeEnvironmentManagedActions.

        :param action_id: The action ID of the scheduled managed action to execute.
        :param environment_name: The name of the target environment.
        :param environment_id: The environment ID of the target environment.
        :returns: ApplyEnvironmentManagedActionResult
        :raises ElasticBeanstalkServiceException:
        :raises ManagedActionInvalidStateException:
        """
        raise NotImplementedError

    @handler("AssociateEnvironmentOperationsRole")
    def associate_environment_operations_role(
        self,
        context: RequestContext,
        environment_name: EnvironmentName,
        operations_role: OperationsRole,
    ) -> None:
        """Add or change the operations role used by an environment. After this
        call is made, Elastic Beanstalk uses the associated operations role for
        permissions to downstream services during subsequent calls acting on
        this environment. For more information, see `Operations
        roles <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/iam-operationsrole.html>`__
        in the *AWS Elastic Beanstalk Developer Guide*.

        :param environment_name: The name of the environment to which to set the operations role.
        :param operations_role: The Amazon Resource Name (ARN) of an existing IAM role to be used as the
        environment's operations role.
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("CheckDNSAvailability")
    def check_dns_availability(
        self, context: RequestContext, cname_prefix: DNSCnamePrefix
    ) -> CheckDNSAvailabilityResultMessage:
        """Checks if the specified CNAME is available.

        :param cname_prefix: The prefix used when this CNAME is reserved.
        :returns: CheckDNSAvailabilityResultMessage
        """
        raise NotImplementedError

    @handler("ComposeEnvironments")
    def compose_environments(
        self,
        context: RequestContext,
        application_name: ApplicationName = None,
        group_name: GroupName = None,
        version_labels: VersionLabels = None,
    ) -> EnvironmentDescriptionsMessage:
        """Create or update a group of environments that each run a separate
        component of a single application. Takes a list of version labels that
        specify application source bundles for each of the environments to
        create or update. The name of each environment and other required
        information must be included in the source bundles in an environment
        manifest named ``env.yaml``. See `Compose
        Environments <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/environment-mgmt-compose.html>`__
        for details.

        :param application_name: The name of the application to which the specified source bundles
        belong.
        :param group_name: The name of the group to which the target environments belong.
        :param version_labels: A list of version labels, specifying one or more application source
        bundles that belong to the target application.
        :returns: EnvironmentDescriptionsMessage
        :raises TooManyEnvironmentsException:
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("CreateApplication")
    def create_application(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        description: Description = None,
        resource_lifecycle_config: ApplicationResourceLifecycleConfig = None,
        tags: Tags = None,
    ) -> ApplicationDescriptionMessage:
        """Creates an application that has one configuration template named
        ``default`` and no application versions.

        :param application_name: The name of the application.
        :param description: Your description of the application.
        :param resource_lifecycle_config: Specifies an application resource lifecycle configuration to prevent
        your application from accumulating too many versions.
        :param tags: Specifies the tags applied to the application.
        :returns: ApplicationDescriptionMessage
        :raises TooManyApplicationsException:
        """
        raise NotImplementedError

    @handler("CreateApplicationVersion")
    def create_application_version(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        version_label: VersionLabel,
        description: Description = None,
        source_build_information: SourceBuildInformation = None,
        source_bundle: S3Location = None,
        build_configuration: BuildConfiguration = None,
        auto_create_application: AutoCreateApplication = None,
        process: ApplicationVersionProccess = None,
        tags: Tags = None,
    ) -> ApplicationVersionDescriptionMessage:
        """Creates an application version for the specified application. You can
        create an application version from a source bundle in Amazon S3, a
        commit in AWS CodeCommit, or the output of an AWS CodeBuild build as
        follows:

        Specify a commit in an AWS CodeCommit repository with
        ``SourceBuildInformation``.

        Specify a build in an AWS CodeBuild with ``SourceBuildInformation`` and
        ``BuildConfiguration``.

        Specify a source bundle in S3 with ``SourceBundle``

        Omit both ``SourceBuildInformation`` and ``SourceBundle`` to use the
        default sample application.

        After you create an application version with a specified Amazon S3
        bucket and key location, you can't change that Amazon S3 location. If
        you change the Amazon S3 location, you receive an exception when you
        attempt to launch an environment from the application version.

        :param application_name: The name of the application.
        :param version_label: A label identifying this version.
        :param description: A description of this application version.
        :param source_build_information: Specify a commit in an AWS CodeCommit Git repository to use as the
        source code for the application version.
        :param source_bundle: The Amazon S3 bucket and key that identify the location of the source
        bundle for this version.
        :param build_configuration: Settings for an AWS CodeBuild build.
        :param auto_create_application: Set to ``true`` to create an application with the specified name if it
        doesn't already exist.
        :param process: Pre-processes and validates the environment manifest (``env.
        :param tags: Specifies the tags applied to the application version.
        :returns: ApplicationVersionDescriptionMessage
        :raises TooManyApplicationsException:
        :raises TooManyApplicationVersionsException:
        :raises InsufficientPrivilegesException:
        :raises S3LocationNotInServiceRegionException:
        :raises CodeBuildNotInServiceRegionException:
        """
        raise NotImplementedError

    @handler("CreateConfigurationTemplate")
    def create_configuration_template(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        template_name: ConfigurationTemplateName,
        solution_stack_name: SolutionStackName = None,
        platform_arn: PlatformArn = None,
        source_configuration: SourceConfiguration = None,
        environment_id: EnvironmentId = None,
        description: Description = None,
        option_settings: ConfigurationOptionSettingsList = None,
        tags: Tags = None,
    ) -> ConfigurationSettingsDescription:
        """Creates an AWS Elastic Beanstalk configuration template, associated with
        a specific Elastic Beanstalk application. You define application
        configuration settings in a configuration template. You can then use the
        configuration template to deploy different versions of the application
        with the same configuration settings.

        Templates aren't associated with any environment. The
        ``EnvironmentName`` response element is always ``null``.

        Related Topics

        -  DescribeConfigurationOptions

        -  DescribeConfigurationSettings

        -  ListAvailableSolutionStacks

        :param application_name: The name of the Elastic Beanstalk application to associate with this
        configuration template.
        :param template_name: The name of the configuration template.
        :param solution_stack_name: The name of an Elastic Beanstalk solution stack (platform version) that
        this configuration uses.
        :param platform_arn: The Amazon Resource Name (ARN) of the custom platform.
        :param source_configuration: An Elastic Beanstalk configuration template to base this one on.
        :param environment_id: The ID of an environment whose settings you want to use to create the
        configuration template.
        :param description: An optional description for this configuration.
        :param option_settings: Option values for the Elastic Beanstalk configuration, such as the
        instance type.
        :param tags: Specifies the tags applied to the configuration template.
        :returns: ConfigurationSettingsDescription
        :raises InsufficientPrivilegesException:
        :raises TooManyBucketsException:
        :raises TooManyConfigurationTemplatesException:
        """
        raise NotImplementedError

    @handler("CreateEnvironment")
    def create_environment(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        environment_name: EnvironmentName = None,
        group_name: GroupName = None,
        description: Description = None,
        cname_prefix: DNSCnamePrefix = None,
        tier: EnvironmentTier = None,
        tags: Tags = None,
        version_label: VersionLabel = None,
        template_name: ConfigurationTemplateName = None,
        solution_stack_name: SolutionStackName = None,
        platform_arn: PlatformArn = None,
        option_settings: ConfigurationOptionSettingsList = None,
        options_to_remove: OptionsSpecifierList = None,
        operations_role: OperationsRole = None,
    ) -> EnvironmentDescription:
        """Launches an AWS Elastic Beanstalk environment for the specified
        application using the specified configuration.

        :param application_name: The name of the application that is associated with this environment.
        :param environment_name: A unique name for the environment.
        :param group_name: The name of the group to which the target environment belongs.
        :param description: Your description for this environment.
        :param cname_prefix: If specified, the environment attempts to use this value as the prefix
        for the CNAME in your Elastic Beanstalk environment URL.
        :param tier: Specifies the tier to use in creating this environment.
        :param tags: Specifies the tags applied to resources in the environment.
        :param version_label: The name of the application version to deploy.
        :param template_name: The name of the Elastic Beanstalk configuration template to use with the
        environment.
        :param solution_stack_name: The name of an Elastic Beanstalk solution stack (platform version) to
        use with the environment.
        :param platform_arn: The Amazon Resource Name (ARN) of the custom platform to use with the
        environment.
        :param option_settings: If specified, AWS Elastic Beanstalk sets the specified configuration
        options to the requested value in the configuration set for the new
        environment.
        :param options_to_remove: A list of custom user-defined configuration options to remove from the
        configuration set for this new environment.
        :param operations_role: The Amazon Resource Name (ARN) of an existing IAM role to be used as the
        environment's operations role.
        :returns: EnvironmentDescription
        :raises TooManyEnvironmentsException:
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("CreatePlatformVersion")
    def create_platform_version(
        self,
        context: RequestContext,
        platform_name: PlatformName,
        platform_version: PlatformVersion,
        platform_definition_bundle: S3Location,
        environment_name: EnvironmentName = None,
        option_settings: ConfigurationOptionSettingsList = None,
        tags: Tags = None,
    ) -> CreatePlatformVersionResult:
        """Create a new version of your custom platform.

        :param platform_name: The name of your custom platform.
        :param platform_version: The number, such as 1.
        :param platform_definition_bundle: The location of the platform definition archive in Amazon S3.
        :param environment_name: The name of the builder environment.
        :param option_settings: The configuration option settings to apply to the builder environment.
        :param tags: Specifies the tags applied to the new platform version.
        :returns: CreatePlatformVersionResult
        :raises InsufficientPrivilegesException:
        :raises ElasticBeanstalkServiceException:
        :raises TooManyPlatformsException:
        """
        raise NotImplementedError

    @handler("CreateStorageLocation")
    def create_storage_location(
        self,
        context: RequestContext,
    ) -> CreateStorageLocationResultMessage:
        """Creates a bucket in Amazon S3 to store application versions, logs, and
        other files used by Elastic Beanstalk environments. The Elastic
        Beanstalk console and EB CLI call this API the first time you create an
        environment in a region. If the storage location already exists,
        ``CreateStorageLocation`` still returns the bucket name but does not
        create a new bucket.

        :returns: CreateStorageLocationResultMessage
        :raises TooManyBucketsException:
        :raises S3SubscriptionRequiredException:
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("DeleteApplication")
    def delete_application(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        terminate_env_by_force: TerminateEnvForce = None,
    ) -> None:
        """Deletes the specified application along with all associated versions and
        configurations. The application versions will not be deleted from your
        Amazon S3 bucket.

        You cannot delete an application that has a running environment.

        :param application_name: The name of the application to delete.
        :param terminate_env_by_force: When set to true, running environments will be terminated before
        deleting the application.
        :raises OperationInProgressException:
        """
        raise NotImplementedError

    @handler("DeleteApplicationVersion")
    def delete_application_version(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        version_label: VersionLabel,
        delete_source_bundle: DeleteSourceBundle = None,
    ) -> None:
        """Deletes the specified version from the specified application.

        You cannot delete an application version that is associated with a
        running environment.

        :param application_name: The name of the application to which the version belongs.
        :param version_label: The label of the version to delete.
        :param delete_source_bundle: Set to ``true`` to delete the source bundle from your storage bucket.
        :raises SourceBundleDeletionException:
        :raises InsufficientPrivilegesException:
        :raises OperationInProgressException:
        :raises S3LocationNotInServiceRegionException:
        """
        raise NotImplementedError

    @handler("DeleteConfigurationTemplate")
    def delete_configuration_template(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        template_name: ConfigurationTemplateName,
    ) -> None:
        """Deletes the specified configuration template.

        When you launch an environment using a configuration template, the
        environment gets a copy of the template. You can delete or modify the
        environment's copy of the template without affecting the running
        environment.

        :param application_name: The name of the application to delete the configuration template from.
        :param template_name: The name of the configuration template to delete.
        :raises OperationInProgressException:
        """
        raise NotImplementedError

    @handler("DeleteEnvironmentConfiguration")
    def delete_environment_configuration(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        environment_name: EnvironmentName,
    ) -> None:
        """Deletes the draft configuration associated with the running environment.

        Updating a running environment with any configuration changes creates a
        draft configuration set. You can get the draft configuration using
        DescribeConfigurationSettings while the update is in progress or if the
        update fails. The ``DeploymentStatus`` for the draft configuration
        indicates whether the deployment is in process or has failed. The draft
        configuration remains in existence until it is deleted with this action.

        :param application_name: The name of the application the environment is associated with.
        :param environment_name: The name of the environment to delete the draft configuration from.
        """
        raise NotImplementedError

    @handler("DeletePlatformVersion")
    def delete_platform_version(
        self, context: RequestContext, platform_arn: PlatformArn = None
    ) -> DeletePlatformVersionResult:
        """Deletes the specified version of a custom platform.

        :param platform_arn: The ARN of the version of the custom platform.
        :returns: DeletePlatformVersionResult
        :raises OperationInProgressException:
        :raises InsufficientPrivilegesException:
        :raises ElasticBeanstalkServiceException:
        :raises PlatformVersionStillReferencedException:
        """
        raise NotImplementedError

    @handler("DescribeAccountAttributes")
    def describe_account_attributes(
        self,
        context: RequestContext,
    ) -> DescribeAccountAttributesResult:
        """Returns attributes related to AWS Elastic Beanstalk that are associated
        with the calling AWS account.

        The result currently has one set of attributes—resource quotas.

        :returns: DescribeAccountAttributesResult
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("DescribeApplicationVersions")
    def describe_application_versions(
        self,
        context: RequestContext,
        application_name: ApplicationName = None,
        version_labels: VersionLabelsList = None,
        max_records: MaxRecords = None,
        next_token: Token = None,
    ) -> ApplicationVersionDescriptionsMessage:
        """Retrieve a list of application versions.

        :param application_name: Specify an application name to show only application versions for that
        application.
        :param version_labels: Specify a version label to show a specific application version.
        :param max_records: For a paginated request.
        :param next_token: For a paginated request.
        :returns: ApplicationVersionDescriptionsMessage
        """
        raise NotImplementedError

    @handler("DescribeApplications")
    def describe_applications(
        self, context: RequestContext, application_names: ApplicationNamesList = None
    ) -> ApplicationDescriptionsMessage:
        """Returns the descriptions of existing applications.

        :param application_names: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to only include those with the specified names.
        :returns: ApplicationDescriptionsMessage
        """
        raise NotImplementedError

    @handler("DescribeConfigurationOptions")
    def describe_configuration_options(
        self,
        context: RequestContext,
        application_name: ApplicationName = None,
        template_name: ConfigurationTemplateName = None,
        environment_name: EnvironmentName = None,
        solution_stack_name: SolutionStackName = None,
        platform_arn: PlatformArn = None,
        options: OptionsSpecifierList = None,
    ) -> ConfigurationOptionsDescription:
        """Describes the configuration options that are used in a particular
        configuration template or environment, or that a specified solution
        stack defines. The description includes the values the options, their
        default values, and an indication of the required action on a running
        environment if an option value is changed.

        :param application_name: The name of the application associated with the configuration template
        or environment.
        :param template_name: The name of the configuration template whose configuration options you
        want to describe.
        :param environment_name: The name of the environment whose configuration options you want to
        describe.
        :param solution_stack_name: The name of the solution stack whose configuration options you want to
        describe.
        :param platform_arn: The ARN of the custom platform.
        :param options: If specified, restricts the descriptions to only the specified options.
        :returns: ConfigurationOptionsDescription
        :raises TooManyBucketsException:
        """
        raise NotImplementedError

    @handler("DescribeConfigurationSettings")
    def describe_configuration_settings(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        template_name: ConfigurationTemplateName = None,
        environment_name: EnvironmentName = None,
    ) -> ConfigurationSettingsDescriptions:
        """Returns a description of the settings for the specified configuration
        set, that is, either a configuration template or the configuration set
        associated with a running environment.

        When describing the settings for the configuration set associated with a
        running environment, it is possible to receive two sets of setting
        descriptions. One is the deployed configuration set, and the other is a
        draft configuration of an environment that is either in the process of
        deployment or that failed to deploy.

        Related Topics

        -  DeleteEnvironmentConfiguration

        :param application_name: The application for the environment or configuration template.
        :param template_name: The name of the configuration template to describe.
        :param environment_name: The name of the environment to describe.
        :returns: ConfigurationSettingsDescriptions
        :raises TooManyBucketsException:
        """
        raise NotImplementedError

    @handler("DescribeEnvironmentHealth")
    def describe_environment_health(
        self,
        context: RequestContext,
        environment_name: EnvironmentName = None,
        environment_id: EnvironmentId = None,
        attribute_names: EnvironmentHealthAttributes = None,
    ) -> DescribeEnvironmentHealthResult:
        """Returns information about the overall health of the specified
        environment. The **DescribeEnvironmentHealth** operation is only
        available with AWS Elastic Beanstalk Enhanced Health.

        :param environment_name: Specify the environment by name.
        :param environment_id: Specify the environment by ID.
        :param attribute_names: Specify the response elements to return.
        :returns: DescribeEnvironmentHealthResult
        :raises InvalidRequestException:
        :raises ElasticBeanstalkServiceException:
        """
        raise NotImplementedError

    @handler("DescribeEnvironmentManagedActionHistory")
    def describe_environment_managed_action_history(
        self,
        context: RequestContext,
        environment_id: EnvironmentId = None,
        environment_name: EnvironmentName = None,
        next_token: String = None,
        max_items: ManagedActionHistoryMaxItems = None,
    ) -> DescribeEnvironmentManagedActionHistoryResult:
        """Lists an environment's completed and failed managed actions.

        :param environment_id: The environment ID of the target environment.
        :param environment_name: The name of the target environment.
        :param next_token: The pagination token returned by a previous request.
        :param max_items: The maximum number of items to return for a single request.
        :returns: DescribeEnvironmentManagedActionHistoryResult
        :raises ElasticBeanstalkServiceException:
        """
        raise NotImplementedError

    @handler("DescribeEnvironmentManagedActions")
    def describe_environment_managed_actions(
        self,
        context: RequestContext,
        environment_name: String = None,
        environment_id: String = None,
        status: ActionStatus = None,
    ) -> DescribeEnvironmentManagedActionsResult:
        """Lists an environment's upcoming and in-progress managed actions.

        :param environment_name: The name of the target environment.
        :param environment_id: The environment ID of the target environment.
        :param status: To show only actions with a particular status, specify a status.
        :returns: DescribeEnvironmentManagedActionsResult
        :raises ElasticBeanstalkServiceException:
        """
        raise NotImplementedError

    @handler("DescribeEnvironmentResources")
    def describe_environment_resources(
        self,
        context: RequestContext,
        environment_id: EnvironmentId = None,
        environment_name: EnvironmentName = None,
    ) -> EnvironmentResourceDescriptionsMessage:
        """Returns AWS resources for this environment.

        :param environment_id: The ID of the environment to retrieve AWS resource usage data.
        :param environment_name: The name of the environment to retrieve AWS resource usage data.
        :returns: EnvironmentResourceDescriptionsMessage
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("DescribeEnvironments")
    def describe_environments(
        self,
        context: RequestContext,
        application_name: ApplicationName = None,
        version_label: VersionLabel = None,
        environment_ids: EnvironmentIdList = None,
        environment_names: EnvironmentNamesList = None,
        include_deleted: IncludeDeleted = None,
        included_deleted_back_to: IncludeDeletedBackTo = None,
        max_records: MaxRecords = None,
        next_token: Token = None,
    ) -> EnvironmentDescriptionsMessage:
        """Returns descriptions for existing environments.

        :param application_name: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to include only those that are associated with this application.
        :param version_label: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to include only those that are associated with this application version.
        :param environment_ids: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to include only those that have the specified IDs.
        :param environment_names: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to include only those that have the specified names.
        :param include_deleted: Indicates whether to include deleted environments:

        ``true``: Environments that have been deleted after
        ``IncludedDeletedBackTo`` are displayed.
        :param included_deleted_back_to: If specified when ``IncludeDeleted`` is set to ``true``, then
        environments deleted after this date are displayed.
        :param max_records: For a paginated request.
        :param next_token: For a paginated request.
        :returns: EnvironmentDescriptionsMessage
        """
        raise NotImplementedError

    @handler("DescribeEvents")
    def describe_events(
        self,
        context: RequestContext,
        application_name: ApplicationName = None,
        version_label: VersionLabel = None,
        template_name: ConfigurationTemplateName = None,
        environment_id: EnvironmentId = None,
        environment_name: EnvironmentName = None,
        platform_arn: PlatformArn = None,
        request_id: RequestId = None,
        severity: EventSeverity = None,
        start_time: TimeFilterStart = None,
        end_time: TimeFilterEnd = None,
        max_records: MaxRecords = None,
        next_token: Token = None,
    ) -> EventDescriptionsMessage:
        """Returns list of event descriptions matching criteria up to the last 6
        weeks.

        This action returns the most recent 1,000 events from the specified
        ``NextToken``.

        :param application_name: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to include only those associated with this application.
        :param version_label: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to those associated with this application version.
        :param template_name: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to those that are associated with this environment configuration.
        :param environment_id: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to those associated with this environment.
        :param environment_name: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to those associated with this environment.
        :param platform_arn: The ARN of a custom platform version.
        :param request_id: If specified, AWS Elastic Beanstalk restricts the described events to
        include only those associated with this request ID.
        :param severity: If specified, limits the events returned from this call to include only
        those with the specified severity or higher.
        :param start_time: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to those that occur on or after this time.
        :param end_time: If specified, AWS Elastic Beanstalk restricts the returned descriptions
        to those that occur up to, but not including, the ``EndTime``.
        :param max_records: Specifies the maximum number of events that can be returned, beginning
        with the most recent event.
        :param next_token: Pagination token.
        :returns: EventDescriptionsMessage
        """
        raise NotImplementedError

    @handler("DescribeInstancesHealth")
    def describe_instances_health(
        self,
        context: RequestContext,
        environment_name: EnvironmentName = None,
        environment_id: EnvironmentId = None,
        attribute_names: InstancesHealthAttributes = None,
        next_token: NextToken = None,
    ) -> DescribeInstancesHealthResult:
        """Retrieves detailed information about the health of instances in your AWS
        Elastic Beanstalk. This operation requires `enhanced health
        reporting <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/health-enhanced.html>`__.

        :param environment_name: Specify the AWS Elastic Beanstalk environment by name.
        :param environment_id: Specify the AWS Elastic Beanstalk environment by ID.
        :param attribute_names: Specifies the response elements you wish to receive.
        :param next_token: Specify the pagination token returned by a previous call.
        :returns: DescribeInstancesHealthResult
        :raises InvalidRequestException:
        :raises ElasticBeanstalkServiceException:
        """
        raise NotImplementedError

    @handler("DescribePlatformVersion")
    def describe_platform_version(
        self, context: RequestContext, platform_arn: PlatformArn = None
    ) -> DescribePlatformVersionResult:
        """Describes a platform version. Provides full details. Compare to
        ListPlatformVersions, which provides summary information about a list of
        platform versions.

        For definitions of platform version and other platform-related terms,
        see `AWS Elastic Beanstalk Platforms
        Glossary <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/platforms-glossary.html>`__.

        :param platform_arn: The ARN of the platform version.
        :returns: DescribePlatformVersionResult
        :raises InsufficientPrivilegesException:
        :raises ElasticBeanstalkServiceException:
        """
        raise NotImplementedError

    @handler("DisassociateEnvironmentOperationsRole")
    def disassociate_environment_operations_role(
        self, context: RequestContext, environment_name: EnvironmentName
    ) -> None:
        """Disassociate the operations role from an environment. After this call is
        made, Elastic Beanstalk uses the caller's permissions for permissions to
        downstream services during subsequent calls acting on this environment.
        For more information, see `Operations
        roles <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/iam-operationsrole.html>`__
        in the *AWS Elastic Beanstalk Developer Guide*.

        :param environment_name: The name of the environment from which to disassociate the operations
        role.
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("ListAvailableSolutionStacks")
    def list_available_solution_stacks(
        self,
        context: RequestContext,
    ) -> ListAvailableSolutionStacksResultMessage:
        """Returns a list of the available solution stack names, with the public
        version first and then in reverse chronological order.

        :returns: ListAvailableSolutionStacksResultMessage
        """
        raise NotImplementedError

    @handler("ListPlatformBranches")
    def list_platform_branches(
        self,
        context: RequestContext,
        filters: SearchFilters = None,
        max_records: PlatformBranchMaxRecords = None,
        next_token: Token = None,
    ) -> ListPlatformBranchesResult:
        """Lists the platform branches available for your account in an AWS Region.
        Provides summary information about each platform branch.

        For definitions of platform branch and other platform-related terms, see
        `AWS Elastic Beanstalk Platforms
        Glossary <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/platforms-glossary.html>`__.

        :param filters: Criteria for restricting the resulting list of platform branches.
        :param max_records: The maximum number of platform branch values returned in one call.
        :param next_token: For a paginated request.
        :returns: ListPlatformBranchesResult
        """
        raise NotImplementedError

    @handler("ListPlatformVersions")
    def list_platform_versions(
        self,
        context: RequestContext,
        filters: PlatformFilters = None,
        max_records: PlatformMaxRecords = None,
        next_token: Token = None,
    ) -> ListPlatformVersionsResult:
        """Lists the platform versions available for your account in an AWS Region.
        Provides summary information about each platform version. Compare to
        DescribePlatformVersion, which provides full details about a single
        platform version.

        For definitions of platform version and other platform-related terms,
        see `AWS Elastic Beanstalk Platforms
        Glossary <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/platforms-glossary.html>`__.

        :param filters: Criteria for restricting the resulting list of platform versions.
        :param max_records: The maximum number of platform version values returned in one call.
        :param next_token: For a paginated request.
        :returns: ListPlatformVersionsResult
        :raises InsufficientPrivilegesException:
        :raises ElasticBeanstalkServiceException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: ResourceArn
    ) -> ResourceTagsDescriptionMessage:
        """Return the tags applied to an AWS Elastic Beanstalk resource. The
        response contains a list of tag key-value pairs.

        Elastic Beanstalk supports tagging of all of its resources. For details
        about resource tagging, see `Tagging Application
        Resources <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/applications-tagging-resources.html>`__.

        :param resource_arn: The Amazon Resource Name (ARN) of the resouce for which a tag list is
        requested.
        :returns: ResourceTagsDescriptionMessage
        :raises InsufficientPrivilegesException:
        :raises ResourceNotFoundException:
        :raises ResourceTypeNotSupportedException:
        """
        raise NotImplementedError

    @handler("RebuildEnvironment")
    def rebuild_environment(
        self,
        context: RequestContext,
        environment_id: EnvironmentId = None,
        environment_name: EnvironmentName = None,
    ) -> None:
        """Deletes and recreates all of the AWS resources (for example: the Auto
        Scaling group, load balancer, etc.) for a specified environment and
        forces a restart.

        :param environment_id: The ID of the environment to rebuild.
        :param environment_name: The name of the environment to rebuild.
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("RequestEnvironmentInfo")
    def request_environment_info(
        self,
        context: RequestContext,
        info_type: EnvironmentInfoType,
        environment_id: EnvironmentId = None,
        environment_name: EnvironmentName = None,
    ) -> None:
        """Initiates a request to compile the specified type of information of the
        deployed environment.

        Setting the ``InfoType`` to ``tail`` compiles the last lines from the
        application server log files of every Amazon EC2 instance in your
        environment.

        Setting the ``InfoType`` to ``bundle`` compresses the application server
        log files for every Amazon EC2 instance into a ``.zip`` file. Legacy and
        .NET containers do not support bundle logs.

        Use RetrieveEnvironmentInfo to obtain the set of logs.

        Related Topics

        -  RetrieveEnvironmentInfo

        :param info_type: The type of information to request.
        :param environment_id: The ID of the environment of the requested data.
        :param environment_name: The name of the environment of the requested data.
        """
        raise NotImplementedError

    @handler("RestartAppServer")
    def restart_app_server(
        self,
        context: RequestContext,
        environment_id: EnvironmentId = None,
        environment_name: EnvironmentName = None,
    ) -> None:
        """Causes the environment to restart the application container server
        running on each Amazon EC2 instance.

        :param environment_id: The ID of the environment to restart the server for.
        :param environment_name: The name of the environment to restart the server for.
        """
        raise NotImplementedError

    @handler("RetrieveEnvironmentInfo")
    def retrieve_environment_info(
        self,
        context: RequestContext,
        info_type: EnvironmentInfoType,
        environment_id: EnvironmentId = None,
        environment_name: EnvironmentName = None,
    ) -> RetrieveEnvironmentInfoResultMessage:
        """Retrieves the compiled information from a RequestEnvironmentInfo
        request.

        Related Topics

        -  RequestEnvironmentInfo

        :param info_type: The type of information to retrieve.
        :param environment_id: The ID of the data's environment.
        :param environment_name: The name of the data's environment.
        :returns: RetrieveEnvironmentInfoResultMessage
        """
        raise NotImplementedError

    @handler("SwapEnvironmentCNAMEs")
    def swap_environment_cnam_es(
        self,
        context: RequestContext,
        source_environment_id: EnvironmentId = None,
        source_environment_name: EnvironmentName = None,
        destination_environment_id: EnvironmentId = None,
        destination_environment_name: EnvironmentName = None,
    ) -> None:
        """Swaps the CNAMEs of two environments.

        :param source_environment_id: The ID of the source environment.
        :param source_environment_name: The name of the source environment.
        :param destination_environment_id: The ID of the destination environment.
        :param destination_environment_name: The name of the destination environment.
        """
        raise NotImplementedError

    @handler("TerminateEnvironment")
    def terminate_environment(
        self,
        context: RequestContext,
        environment_id: EnvironmentId = None,
        environment_name: EnvironmentName = None,
        terminate_resources: TerminateEnvironmentResources = None,
        force_terminate: ForceTerminate = None,
    ) -> EnvironmentDescription:
        """Terminates the specified environment.

        :param environment_id: The ID of the environment to terminate.
        :param environment_name: The name of the environment to terminate.
        :param terminate_resources: Indicates whether the associated AWS resources should shut down when the
        environment is terminated:

        -  ``true``: The specified environment as well as the associated AWS
           resources, such as Auto Scaling group and LoadBalancer, are
           terminated.
        :param force_terminate: Terminates the target environment even if another environment in the
        same group is dependent on it.
        :returns: EnvironmentDescription
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("UpdateApplication")
    def update_application(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        description: Description = None,
    ) -> ApplicationDescriptionMessage:
        """Updates the specified application to have the specified properties.

        If a property (for example, ``description``) is not provided, the value
        remains unchanged. To clear these properties, specify an empty string.

        :param application_name: The name of the application to update.
        :param description: A new description for the application.
        :returns: ApplicationDescriptionMessage
        """
        raise NotImplementedError

    @handler("UpdateApplicationResourceLifecycle")
    def update_application_resource_lifecycle(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        resource_lifecycle_config: ApplicationResourceLifecycleConfig,
    ) -> ApplicationResourceLifecycleDescriptionMessage:
        """Modifies lifecycle settings for an application.

        :param application_name: The name of the application.
        :param resource_lifecycle_config: The lifecycle configuration.
        :returns: ApplicationResourceLifecycleDescriptionMessage
        :raises InsufficientPrivilegesException:
        """
        raise NotImplementedError

    @handler("UpdateApplicationVersion")
    def update_application_version(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        version_label: VersionLabel,
        description: Description = None,
    ) -> ApplicationVersionDescriptionMessage:
        """Updates the specified application version to have the specified
        properties.

        If a property (for example, ``description``) is not provided, the value
        remains unchanged. To clear properties, specify an empty string.

        :param application_name: The name of the application associated with this version.
        :param version_label: The name of the version to update.
        :param description: A new description for this version.
        :returns: ApplicationVersionDescriptionMessage
        """
        raise NotImplementedError

    @handler("UpdateConfigurationTemplate")
    def update_configuration_template(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        template_name: ConfigurationTemplateName,
        description: Description = None,
        option_settings: ConfigurationOptionSettingsList = None,
        options_to_remove: OptionsSpecifierList = None,
    ) -> ConfigurationSettingsDescription:
        """Updates the specified configuration template to have the specified
        properties or configuration option values.

        If a property (for example, ``ApplicationName``) is not provided, its
        value remains unchanged. To clear such properties, specify an empty
        string.

        Related Topics

        -  DescribeConfigurationOptions

        :param application_name: The name of the application associated with the configuration template
        to update.
        :param template_name: The name of the configuration template to update.
        :param description: A new description for the configuration.
        :param option_settings: A list of configuration option settings to update with the new specified
        option value.
        :param options_to_remove: A list of configuration options to remove from the configuration set.
        :returns: ConfigurationSettingsDescription
        :raises InsufficientPrivilegesException:
        :raises TooManyBucketsException:
        """
        raise NotImplementedError

    @handler("UpdateEnvironment")
    def update_environment(
        self,
        context: RequestContext,
        application_name: ApplicationName = None,
        environment_id: EnvironmentId = None,
        environment_name: EnvironmentName = None,
        group_name: GroupName = None,
        description: Description = None,
        tier: EnvironmentTier = None,
        version_label: VersionLabel = None,
        template_name: ConfigurationTemplateName = None,
        solution_stack_name: SolutionStackName = None,
        platform_arn: PlatformArn = None,
        option_settings: ConfigurationOptionSettingsList = None,
        options_to_remove: OptionsSpecifierList = None,
    ) -> EnvironmentDescription:
        """Updates the environment description, deploys a new application version,
        updates the configuration settings to an entirely new configuration
        template, or updates select configuration option values in the running
        environment.

        Attempting to update both the release and configuration is not allowed
        and AWS Elastic Beanstalk returns an ``InvalidParameterCombination``
        error.

        When updating the configuration settings to a new template or individual
        settings, a draft configuration is created and
        DescribeConfigurationSettings for this environment returns two setting
        descriptions with different ``DeploymentStatus`` values.

        :param application_name: The name of the application with which the environment is associated.
        :param environment_id: The ID of the environment to update.
        :param environment_name: The name of the environment to update.
        :param group_name: The name of the group to which the target environment belongs.
        :param description: If this parameter is specified, AWS Elastic Beanstalk updates the
        description of this environment.
        :param tier: This specifies the tier to use to update the environment.
        :param version_label: If this parameter is specified, AWS Elastic Beanstalk deploys the named
        application version to the environment.
        :param template_name: If this parameter is specified, AWS Elastic Beanstalk deploys this
        configuration template to the environment.
        :param solution_stack_name: This specifies the platform version that the environment will run after
        the environment is updated.
        :param platform_arn: The ARN of the platform, if used.
        :param option_settings: If specified, AWS Elastic Beanstalk updates the configuration set
        associated with the running environment and sets the specified
        configuration options to the requested value.
        :param options_to_remove: A list of custom user-defined configuration options to remove from the
        configuration set for this environment.
        :returns: EnvironmentDescription
        :raises InsufficientPrivilegesException:
        :raises TooManyBucketsException:
        """
        raise NotImplementedError

    @handler("UpdateTagsForResource")
    def update_tags_for_resource(
        self,
        context: RequestContext,
        resource_arn: ResourceArn,
        tags_to_add: TagList = None,
        tags_to_remove: TagKeyList = None,
    ) -> None:
        """Update the list of tags applied to an AWS Elastic Beanstalk resource.
        Two lists can be passed: ``TagsToAdd`` for tags to add or update, and
        ``TagsToRemove``.

        Elastic Beanstalk supports tagging of all of its resources. For details
        about resource tagging, see `Tagging Application
        Resources <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/applications-tagging-resources.html>`__.

        If you create a custom IAM user policy to control permission to this
        operation, specify one of the following two virtual actions (or both)
        instead of the API operation name:

        elasticbeanstalk:AddTags
           Controls permission to call ``UpdateTagsForResource`` and pass a list
           of tags to add in the ``TagsToAdd`` parameter.

        elasticbeanstalk:RemoveTags
           Controls permission to call ``UpdateTagsForResource`` and pass a list
           of tag keys to remove in the ``TagsToRemove`` parameter.

        For details about creating a custom user policy, see `Creating a Custom
        User
        Policy <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.iam.managed-policies.html#AWSHowTo.iam.policies>`__.

        :param resource_arn: The Amazon Resource Name (ARN) of the resouce to be updated.
        :param tags_to_add: A list of tags to add or update.
        :param tags_to_remove: A list of tag keys to remove.
        :raises InsufficientPrivilegesException:
        :raises OperationInProgressException:
        :raises TooManyTagsException:
        :raises ResourceNotFoundException:
        :raises ResourceTypeNotSupportedException:
        """
        raise NotImplementedError

    @handler("ValidateConfigurationSettings")
    def validate_configuration_settings(
        self,
        context: RequestContext,
        application_name: ApplicationName,
        option_settings: ConfigurationOptionSettingsList,
        template_name: ConfigurationTemplateName = None,
        environment_name: EnvironmentName = None,
    ) -> ConfigurationSettingsValidationMessages:
        """Takes a set of configuration settings and either a configuration
        template or environment, and determines whether those values are valid.

        This action returns a list of messages indicating any errors or warnings
        associated with the selection of option values.

        :param application_name: The name of the application that the configuration template or
        environment belongs to.
        :param option_settings: A list of the options and desired values to evaluate.
        :param template_name: The name of the configuration template to validate the settings against.
        :param environment_name: The name of the environment to validate the settings against.
        :returns: ConfigurationSettingsValidationMessages
        :raises InsufficientPrivilegesException:
        :raises TooManyBucketsException:
        """
        raise NotImplementedError
