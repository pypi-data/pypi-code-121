import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

ARN = str
AccountId = str
BackupOptionKey = str
BackupOptionValue = str
BackupPlanName = str
BackupRuleName = str
BackupSelectionName = str
BackupVaultName = str
Boolean = bool
ConditionKey = str
ConditionValue = str
ControlName = str
CronExpression = str
FrameworkDescription = str
FrameworkName = str
GlobalSettingsName = str
GlobalSettingsValue = str
IAMPolicy = str
IAMRoleArn = str
IsEnabled = bool
MaxFrameworkInputs = int
MaxResults = int
MetadataKey = str
MetadataValue = str
ParameterName = str
ParameterValue = str
ReportJobId = str
ReportPlanDescription = str
ReportPlanName = str
ResourceType = str
RestoreJobId = str
TagKey = str
TagValue = str
boolean = bool
integer = int
string = str


class BackupJobState(str):
    CREATED = "CREATED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    ABORTING = "ABORTING"
    ABORTED = "ABORTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class BackupVaultEvent(str):
    BACKUP_JOB_STARTED = "BACKUP_JOB_STARTED"
    BACKUP_JOB_COMPLETED = "BACKUP_JOB_COMPLETED"
    BACKUP_JOB_SUCCESSFUL = "BACKUP_JOB_SUCCESSFUL"
    BACKUP_JOB_FAILED = "BACKUP_JOB_FAILED"
    BACKUP_JOB_EXPIRED = "BACKUP_JOB_EXPIRED"
    RESTORE_JOB_STARTED = "RESTORE_JOB_STARTED"
    RESTORE_JOB_COMPLETED = "RESTORE_JOB_COMPLETED"
    RESTORE_JOB_SUCCESSFUL = "RESTORE_JOB_SUCCESSFUL"
    RESTORE_JOB_FAILED = "RESTORE_JOB_FAILED"
    COPY_JOB_STARTED = "COPY_JOB_STARTED"
    COPY_JOB_SUCCESSFUL = "COPY_JOB_SUCCESSFUL"
    COPY_JOB_FAILED = "COPY_JOB_FAILED"
    RECOVERY_POINT_MODIFIED = "RECOVERY_POINT_MODIFIED"
    BACKUP_PLAN_CREATED = "BACKUP_PLAN_CREATED"
    BACKUP_PLAN_MODIFIED = "BACKUP_PLAN_MODIFIED"
    S3_BACKUP_OBJECT_FAILED = "S3_BACKUP_OBJECT_FAILED"
    S3_RESTORE_OBJECT_FAILED = "S3_RESTORE_OBJECT_FAILED"


class ConditionType(str):
    STRINGEQUALS = "STRINGEQUALS"


class CopyJobState(str):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RecoveryPointStatus(str):
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    DELETING = "DELETING"
    EXPIRED = "EXPIRED"


class RestoreJobStatus(str):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"


class StorageClass(str):
    WARM = "WARM"
    COLD = "COLD"
    DELETED = "DELETED"


class AlreadyExistsException(ServiceException):
    """The required resource already exists."""

    Code: Optional[string]
    Message: Optional[string]
    CreatorRequestId: Optional[string]
    Arn: Optional[string]
    Type: Optional[string]
    Context: Optional[string]


class ConflictException(ServiceException):
    """Backup can't perform the action that you requested until it finishes
    performing a previous action. Try again later.
    """

    Code: Optional[string]
    Message: Optional[string]
    Type: Optional[string]
    Context: Optional[string]


class DependencyFailureException(ServiceException):
    """A dependent Amazon Web Services service or resource returned an error to
    the Backup service, and the action cannot be completed.
    """

    Code: Optional[string]
    Message: Optional[string]
    Type: Optional[string]
    Context: Optional[string]


class InvalidParameterValueException(ServiceException):
    """Indicates that something is wrong with a parameter's value. For example,
    the value is out of range.
    """

    Code: Optional[string]
    Message: Optional[string]
    Type: Optional[string]
    Context: Optional[string]


class InvalidRequestException(ServiceException):
    """Indicates that something is wrong with the input to the request. For
    example, a parameter is of the wrong type.
    """

    Code: Optional[string]
    Message: Optional[string]
    Type: Optional[string]
    Context: Optional[string]


class InvalidResourceStateException(ServiceException):
    """Backup is already performing an action on this recovery point. It can't
    perform the action you requested until the first action finishes. Try
    again later.
    """

    Code: Optional[string]
    Message: Optional[string]
    Type: Optional[string]
    Context: Optional[string]


class LimitExceededException(ServiceException):
    """A limit in the request has been exceeded; for example, a maximum number
    of items allowed in a request.
    """

    Code: Optional[string]
    Message: Optional[string]
    Type: Optional[string]
    Context: Optional[string]


class MissingParameterValueException(ServiceException):
    """Indicates that a required parameter is missing."""

    Code: Optional[string]
    Message: Optional[string]
    Type: Optional[string]
    Context: Optional[string]


class ResourceNotFoundException(ServiceException):
    """A resource that is required for the action doesn't exist."""

    Code: Optional[string]
    Message: Optional[string]
    Type: Optional[string]
    Context: Optional[string]


class ServiceUnavailableException(ServiceException):
    """The request failed due to a temporary failure of the server."""

    Code: Optional[string]
    Message: Optional[string]
    Type: Optional[string]
    Context: Optional[string]


BackupOptions = Dict[BackupOptionKey, BackupOptionValue]


class AdvancedBackupSetting(TypedDict, total=False):
    """A list of backup options for each resource type."""

    ResourceType: Optional[ResourceType]
    BackupOptions: Optional[BackupOptions]


AdvancedBackupSettings = List[AdvancedBackupSetting]
Long = int
timestamp = datetime


class RecoveryPointCreator(TypedDict, total=False):
    """Contains information about the backup plan and rule that Backup used to
    initiate the recovery point backup.
    """

    BackupPlanId: Optional[string]
    BackupPlanArn: Optional[ARN]
    BackupPlanVersion: Optional[string]
    BackupRuleId: Optional[string]


class BackupJob(TypedDict, total=False):
    """Contains detailed information about a backup job."""

    AccountId: Optional[AccountId]
    BackupJobId: Optional[string]
    BackupVaultName: Optional[BackupVaultName]
    BackupVaultArn: Optional[ARN]
    RecoveryPointArn: Optional[ARN]
    ResourceArn: Optional[ARN]
    CreationDate: Optional[timestamp]
    CompletionDate: Optional[timestamp]
    State: Optional[BackupJobState]
    StatusMessage: Optional[string]
    PercentDone: Optional[string]
    BackupSizeInBytes: Optional[Long]
    IamRoleArn: Optional[IAMRoleArn]
    CreatedBy: Optional[RecoveryPointCreator]
    ExpectedCompletionDate: Optional[timestamp]
    StartBy: Optional[timestamp]
    ResourceType: Optional[ResourceType]
    BytesTransferred: Optional[Long]
    BackupOptions: Optional[BackupOptions]
    BackupType: Optional[string]


BackupJobsList = List[BackupJob]


class Lifecycle(TypedDict, total=False):
    """Contains an array of ``Transition`` objects specifying how long in days
    before a recovery point transitions to cold storage or is deleted.

    Backups transitioned to cold storage must be stored in cold storage for
    a minimum of 90 days. Therefore, on the console, the “retention” setting
    must be 90 days greater than the “transition to cold after days”
    setting. The “transition to cold after days” setting cannot be changed
    after a backup has been transitioned to cold.

    Only resource types that support full Backup management can transition
    their backups to cold storage. Those resource types are listed in the
    "Full Backup management" section of the `Feature availability by
    resource <https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html#features-by-resource>`__
    table. Backup ignores this expression for other resource types.
    """

    MoveToColdStorageAfterDays: Optional[Long]
    DeleteAfterDays: Optional[Long]


class CopyAction(TypedDict, total=False):
    """The details of the copy operation."""

    Lifecycle: Optional[Lifecycle]
    DestinationBackupVaultArn: ARN


CopyActions = List[CopyAction]
Tags = Dict[TagKey, TagValue]
WindowMinutes = int


class BackupRule(TypedDict, total=False):
    """Specifies a scheduled task used to back up a selection of resources."""

    RuleName: BackupRuleName
    TargetBackupVaultName: BackupVaultName
    ScheduleExpression: Optional[CronExpression]
    StartWindowMinutes: Optional[WindowMinutes]
    CompletionWindowMinutes: Optional[WindowMinutes]
    Lifecycle: Optional[Lifecycle]
    RecoveryPointTags: Optional[Tags]
    RuleId: Optional[string]
    CopyActions: Optional[CopyActions]
    EnableContinuousBackup: Optional[Boolean]


BackupRules = List[BackupRule]


class BackupPlan(TypedDict, total=False):
    """Contains an optional backup plan display name and an array of
    ``BackupRule`` objects, each of which specifies a backup rule. Each rule
    in a backup plan is a separate scheduled task and can back up a
    different selection of Amazon Web Services resources.
    """

    BackupPlanName: BackupPlanName
    Rules: BackupRules
    AdvancedBackupSettings: Optional[AdvancedBackupSettings]


class BackupRuleInput(TypedDict, total=False):
    """Specifies a scheduled task used to back up a selection of resources."""

    RuleName: BackupRuleName
    TargetBackupVaultName: BackupVaultName
    ScheduleExpression: Optional[CronExpression]
    StartWindowMinutes: Optional[WindowMinutes]
    CompletionWindowMinutes: Optional[WindowMinutes]
    Lifecycle: Optional[Lifecycle]
    RecoveryPointTags: Optional[Tags]
    CopyActions: Optional[CopyActions]
    EnableContinuousBackup: Optional[Boolean]


BackupRulesInput = List[BackupRuleInput]


class BackupPlanInput(TypedDict, total=False):
    """Contains an optional backup plan display name and an array of
    ``BackupRule`` objects, each of which specifies a backup rule. Each rule
    in a backup plan is a separate scheduled task.
    """

    BackupPlanName: BackupPlanName
    Rules: BackupRulesInput
    AdvancedBackupSettings: Optional[AdvancedBackupSettings]


class BackupPlanTemplatesListMember(TypedDict, total=False):
    """An object specifying metadata associated with a backup plan template."""

    BackupPlanTemplateId: Optional[string]
    BackupPlanTemplateName: Optional[string]


BackupPlanTemplatesList = List[BackupPlanTemplatesListMember]


class BackupPlansListMember(TypedDict, total=False):
    """Contains metadata about a backup plan."""

    BackupPlanArn: Optional[ARN]
    BackupPlanId: Optional[string]
    CreationDate: Optional[timestamp]
    DeletionDate: Optional[timestamp]
    VersionId: Optional[string]
    BackupPlanName: Optional[BackupPlanName]
    CreatorRequestId: Optional[string]
    LastExecutionDate: Optional[timestamp]
    AdvancedBackupSettings: Optional[AdvancedBackupSettings]


BackupPlanVersionsList = List[BackupPlansListMember]
BackupPlansList = List[BackupPlansListMember]


class ConditionParameter(TypedDict, total=False):
    """Includes information about tags you define to assign tagged resources to
    a backup plan.
    """

    ConditionKey: Optional[ConditionKey]
    ConditionValue: Optional[ConditionValue]


ConditionParameters = List[ConditionParameter]


class Conditions(TypedDict, total=False):
    """Contains information about which resources to include or exclude from a
    backup plan using their tags. Conditions are case sensitive.
    """

    StringEquals: Optional[ConditionParameters]
    StringNotEquals: Optional[ConditionParameters]
    StringLike: Optional[ConditionParameters]
    StringNotLike: Optional[ConditionParameters]


ResourceArns = List[ARN]


class Condition(TypedDict, total=False):
    """Contains an array of triplets made up of a condition type (such as
    ``StringEquals``), a key, and a value. Used to filter resources using
    their tags and assign them to a backup plan. Case sensitive.
    """

    ConditionType: ConditionType
    ConditionKey: ConditionKey
    ConditionValue: ConditionValue


ListOfTags = List[Condition]


class BackupSelection(TypedDict, total=False):
    """Used to specify a set of resources to a backup plan."""

    SelectionName: BackupSelectionName
    IamRoleArn: IAMRoleArn
    Resources: Optional[ResourceArns]
    ListOfTags: Optional[ListOfTags]
    NotResources: Optional[ResourceArns]
    Conditions: Optional[Conditions]


class BackupSelectionsListMember(TypedDict, total=False):
    """Contains metadata about a ``BackupSelection`` object."""

    SelectionId: Optional[string]
    SelectionName: Optional[BackupSelectionName]
    BackupPlanId: Optional[string]
    CreationDate: Optional[timestamp]
    CreatorRequestId: Optional[string]
    IamRoleArn: Optional[IAMRoleArn]


BackupSelectionsList = List[BackupSelectionsListMember]
BackupVaultEvents = List[BackupVaultEvent]
long = int


class BackupVaultListMember(TypedDict, total=False):
    """Contains metadata about a backup vault."""

    BackupVaultName: Optional[BackupVaultName]
    BackupVaultArn: Optional[ARN]
    CreationDate: Optional[timestamp]
    EncryptionKeyArn: Optional[ARN]
    CreatorRequestId: Optional[string]
    NumberOfRecoveryPoints: Optional[long]
    Locked: Optional[Boolean]
    MinRetentionDays: Optional[Long]
    MaxRetentionDays: Optional[Long]
    LockDate: Optional[timestamp]


BackupVaultList = List[BackupVaultListMember]


class CalculatedLifecycle(TypedDict, total=False):
    """Contains ``DeleteAt`` and ``MoveToColdStorageAt`` timestamps, which are
    used to specify a lifecycle for a recovery point.

    The lifecycle defines when a protected resource is transitioned to cold
    storage and when it expires. Backup transitions and expires backups
    automatically according to the lifecycle that you define.

    Backups transitioned to cold storage must be stored in cold storage for
    a minimum of 90 days. Therefore, the “retention” setting must be 90 days
    greater than the “transition to cold after days” setting. The
    “transition to cold after days” setting cannot be changed after a backup
    has been transitioned to cold.

    Only resource types that support full Backup management can transition
    their backups to cold storage. Those resource types are listed in the
    "Full Backup management" section of the `Feature availability by
    resource <https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html#features-by-resource>`__
    table. Backup ignores this expression for other resource types.
    """

    MoveToColdStorageAt: Optional[timestamp]
    DeleteAt: Optional[timestamp]


ComplianceResourceIdList = List[string]


class ControlInputParameter(TypedDict, total=False):
    """A list of parameters for a control. A control can have zero, one, or
    more than one parameter. An example of a control with two parameters is:
    "backup plan frequency is at least ``daily`` and the retention period is
    at least ``1 year``". The first parameter is ``daily``. The second
    parameter is ``1 year``.
    """

    ParameterName: Optional[ParameterName]
    ParameterValue: Optional[ParameterValue]


ControlInputParameters = List[ControlInputParameter]
stringMap = Dict[string, string]
ResourceTypeList = List[ARN]


class ControlScope(TypedDict, total=False):
    """A framework consists of one or more controls. Each control has its own
    control scope. The control scope can include one or more resource types,
    a combination of a tag key and value, or a combination of one resource
    type and one resource ID. If no scope is specified, evaluations for the
    rule are triggered when any resource in your recording group changes in
    configuration.

    To set a control scope that includes all of a particular resource, leave
    the ``ControlScope`` empty or do not pass it when calling
    ``CreateFramework``.
    """

    ComplianceResourceIds: Optional[ComplianceResourceIdList]
    ComplianceResourceTypes: Optional[ResourceTypeList]
    Tags: Optional[stringMap]


class CopyJob(TypedDict, total=False):
    """Contains detailed information about a copy job."""

    AccountId: Optional[AccountId]
    CopyJobId: Optional[string]
    SourceBackupVaultArn: Optional[ARN]
    SourceRecoveryPointArn: Optional[ARN]
    DestinationBackupVaultArn: Optional[ARN]
    DestinationRecoveryPointArn: Optional[ARN]
    ResourceArn: Optional[ARN]
    CreationDate: Optional[timestamp]
    CompletionDate: Optional[timestamp]
    State: Optional[CopyJobState]
    StatusMessage: Optional[string]
    BackupSizeInBytes: Optional[Long]
    IamRoleArn: Optional[IAMRoleArn]
    CreatedBy: Optional[RecoveryPointCreator]
    ResourceType: Optional[ResourceType]


CopyJobsList = List[CopyJob]


class CreateBackupPlanInput(ServiceRequest):
    BackupPlan: BackupPlanInput
    BackupPlanTags: Optional[Tags]
    CreatorRequestId: Optional[string]


class CreateBackupPlanOutput(TypedDict, total=False):
    BackupPlanId: Optional[string]
    BackupPlanArn: Optional[ARN]
    CreationDate: Optional[timestamp]
    VersionId: Optional[string]
    AdvancedBackupSettings: Optional[AdvancedBackupSettings]


class CreateBackupSelectionInput(ServiceRequest):
    BackupPlanId: string
    BackupSelection: BackupSelection
    CreatorRequestId: Optional[string]


class CreateBackupSelectionOutput(TypedDict, total=False):
    SelectionId: Optional[string]
    BackupPlanId: Optional[string]
    CreationDate: Optional[timestamp]


class CreateBackupVaultInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    BackupVaultTags: Optional[Tags]
    EncryptionKeyArn: Optional[ARN]
    CreatorRequestId: Optional[string]


class CreateBackupVaultOutput(TypedDict, total=False):
    BackupVaultName: Optional[BackupVaultName]
    BackupVaultArn: Optional[ARN]
    CreationDate: Optional[timestamp]


class FrameworkControl(TypedDict, total=False):
    """Contains detailed information about all of the controls of a framework.
    Each framework must contain at least one control.
    """

    ControlName: ControlName
    ControlInputParameters: Optional[ControlInputParameters]
    ControlScope: Optional[ControlScope]


FrameworkControls = List[FrameworkControl]


class CreateFrameworkInput(ServiceRequest):
    FrameworkName: FrameworkName
    FrameworkDescription: Optional[FrameworkDescription]
    FrameworkControls: FrameworkControls
    IdempotencyToken: Optional[string]
    FrameworkTags: Optional[stringMap]


class CreateFrameworkOutput(TypedDict, total=False):
    FrameworkName: Optional[FrameworkName]
    FrameworkArn: Optional[ARN]


stringList = List[string]


class ReportSetting(TypedDict, total=False):
    """Contains detailed information about a report setting."""

    ReportTemplate: string
    FrameworkArns: Optional[stringList]
    NumberOfFrameworks: Optional[integer]


FormatList = List[string]


class ReportDeliveryChannel(TypedDict, total=False):
    """Contains information from your report plan about where to deliver your
    reports, specifically your Amazon S3 bucket name, S3 key prefix, and the
    formats of your reports.
    """

    S3BucketName: string
    S3KeyPrefix: Optional[string]
    Formats: Optional[FormatList]


class CreateReportPlanInput(ServiceRequest):
    ReportPlanName: ReportPlanName
    ReportPlanDescription: Optional[ReportPlanDescription]
    ReportDeliveryChannel: ReportDeliveryChannel
    ReportSetting: ReportSetting
    ReportPlanTags: Optional[stringMap]
    IdempotencyToken: Optional[string]


class CreateReportPlanOutput(TypedDict, total=False):
    ReportPlanName: Optional[ReportPlanName]
    ReportPlanArn: Optional[ARN]
    CreationTime: Optional[timestamp]


class DeleteBackupPlanInput(ServiceRequest):
    BackupPlanId: string


class DeleteBackupPlanOutput(TypedDict, total=False):
    BackupPlanId: Optional[string]
    BackupPlanArn: Optional[ARN]
    DeletionDate: Optional[timestamp]
    VersionId: Optional[string]


class DeleteBackupSelectionInput(ServiceRequest):
    BackupPlanId: string
    SelectionId: string


class DeleteBackupVaultAccessPolicyInput(ServiceRequest):
    BackupVaultName: BackupVaultName


class DeleteBackupVaultInput(ServiceRequest):
    BackupVaultName: string


class DeleteBackupVaultLockConfigurationInput(ServiceRequest):
    BackupVaultName: BackupVaultName


class DeleteBackupVaultNotificationsInput(ServiceRequest):
    BackupVaultName: BackupVaultName


class DeleteFrameworkInput(ServiceRequest):
    FrameworkName: FrameworkName


class DeleteRecoveryPointInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    RecoveryPointArn: ARN


class DeleteReportPlanInput(ServiceRequest):
    ReportPlanName: ReportPlanName


class DescribeBackupJobInput(ServiceRequest):
    BackupJobId: string


class DescribeBackupJobOutput(TypedDict, total=False):
    AccountId: Optional[AccountId]
    BackupJobId: Optional[string]
    BackupVaultName: Optional[BackupVaultName]
    BackupVaultArn: Optional[ARN]
    RecoveryPointArn: Optional[ARN]
    ResourceArn: Optional[ARN]
    CreationDate: Optional[timestamp]
    CompletionDate: Optional[timestamp]
    State: Optional[BackupJobState]
    StatusMessage: Optional[string]
    PercentDone: Optional[string]
    BackupSizeInBytes: Optional[Long]
    IamRoleArn: Optional[IAMRoleArn]
    CreatedBy: Optional[RecoveryPointCreator]
    ResourceType: Optional[ResourceType]
    BytesTransferred: Optional[Long]
    ExpectedCompletionDate: Optional[timestamp]
    StartBy: Optional[timestamp]
    BackupOptions: Optional[BackupOptions]
    BackupType: Optional[string]


class DescribeBackupVaultInput(ServiceRequest):
    BackupVaultName: string


class DescribeBackupVaultOutput(TypedDict, total=False):
    BackupVaultName: Optional[string]
    BackupVaultArn: Optional[ARN]
    EncryptionKeyArn: Optional[ARN]
    CreationDate: Optional[timestamp]
    CreatorRequestId: Optional[string]
    NumberOfRecoveryPoints: Optional[long]
    Locked: Optional[Boolean]
    MinRetentionDays: Optional[Long]
    MaxRetentionDays: Optional[Long]
    LockDate: Optional[timestamp]


class DescribeCopyJobInput(ServiceRequest):
    CopyJobId: string


class DescribeCopyJobOutput(TypedDict, total=False):
    CopyJob: Optional[CopyJob]


class DescribeFrameworkInput(ServiceRequest):
    FrameworkName: FrameworkName


class DescribeFrameworkOutput(TypedDict, total=False):
    FrameworkName: Optional[FrameworkName]
    FrameworkArn: Optional[ARN]
    FrameworkDescription: Optional[FrameworkDescription]
    FrameworkControls: Optional[FrameworkControls]
    CreationTime: Optional[timestamp]
    DeploymentStatus: Optional[string]
    FrameworkStatus: Optional[string]
    IdempotencyToken: Optional[string]


class DescribeGlobalSettingsInput(ServiceRequest):
    pass


GlobalSettings = Dict[GlobalSettingsName, GlobalSettingsValue]


class DescribeGlobalSettingsOutput(TypedDict, total=False):
    GlobalSettings: Optional[GlobalSettings]
    LastUpdateTime: Optional[timestamp]


class DescribeProtectedResourceInput(ServiceRequest):
    ResourceArn: ARN


class DescribeProtectedResourceOutput(TypedDict, total=False):
    ResourceArn: Optional[ARN]
    ResourceType: Optional[ResourceType]
    LastBackupTime: Optional[timestamp]


class DescribeRecoveryPointInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    RecoveryPointArn: ARN


class DescribeRecoveryPointOutput(TypedDict, total=False):
    RecoveryPointArn: Optional[ARN]
    BackupVaultName: Optional[BackupVaultName]
    BackupVaultArn: Optional[ARN]
    SourceBackupVaultArn: Optional[ARN]
    ResourceArn: Optional[ARN]
    ResourceType: Optional[ResourceType]
    CreatedBy: Optional[RecoveryPointCreator]
    IamRoleArn: Optional[IAMRoleArn]
    Status: Optional[RecoveryPointStatus]
    StatusMessage: Optional[string]
    CreationDate: Optional[timestamp]
    CompletionDate: Optional[timestamp]
    BackupSizeInBytes: Optional[Long]
    CalculatedLifecycle: Optional[CalculatedLifecycle]
    Lifecycle: Optional[Lifecycle]
    EncryptionKeyArn: Optional[ARN]
    IsEncrypted: Optional[boolean]
    StorageClass: Optional[StorageClass]
    LastRestoreTime: Optional[timestamp]


class DescribeRegionSettingsInput(ServiceRequest):
    pass


ResourceTypeManagementPreference = Dict[ResourceType, IsEnabled]
ResourceTypeOptInPreference = Dict[ResourceType, IsEnabled]


class DescribeRegionSettingsOutput(TypedDict, total=False):
    ResourceTypeOptInPreference: Optional[ResourceTypeOptInPreference]
    ResourceTypeManagementPreference: Optional[ResourceTypeManagementPreference]


class DescribeReportJobInput(ServiceRequest):
    ReportJobId: ReportJobId


class ReportDestination(TypedDict, total=False):
    """Contains information from your report job about your report destination."""

    S3BucketName: Optional[string]
    S3Keys: Optional[stringList]


class ReportJob(TypedDict, total=False):
    """Contains detailed information about a report job. A report job compiles
    a report based on a report plan and publishes it to Amazon S3.
    """

    ReportJobId: Optional[ReportJobId]
    ReportPlanArn: Optional[ARN]
    ReportTemplate: Optional[string]
    CreationTime: Optional[timestamp]
    CompletionTime: Optional[timestamp]
    Status: Optional[string]
    StatusMessage: Optional[string]
    ReportDestination: Optional[ReportDestination]


class DescribeReportJobOutput(TypedDict, total=False):
    ReportJob: Optional[ReportJob]


class DescribeReportPlanInput(ServiceRequest):
    ReportPlanName: ReportPlanName


class ReportPlan(TypedDict, total=False):
    """Contains detailed information about a report plan."""

    ReportPlanArn: Optional[ARN]
    ReportPlanName: Optional[ReportPlanName]
    ReportPlanDescription: Optional[ReportPlanDescription]
    ReportSetting: Optional[ReportSetting]
    ReportDeliveryChannel: Optional[ReportDeliveryChannel]
    DeploymentStatus: Optional[string]
    CreationTime: Optional[timestamp]
    LastAttemptedExecutionTime: Optional[timestamp]
    LastSuccessfulExecutionTime: Optional[timestamp]


class DescribeReportPlanOutput(TypedDict, total=False):
    ReportPlan: Optional[ReportPlan]


class DescribeRestoreJobInput(ServiceRequest):
    RestoreJobId: RestoreJobId


class DescribeRestoreJobOutput(TypedDict, total=False):
    AccountId: Optional[AccountId]
    RestoreJobId: Optional[string]
    RecoveryPointArn: Optional[ARN]
    CreationDate: Optional[timestamp]
    CompletionDate: Optional[timestamp]
    Status: Optional[RestoreJobStatus]
    StatusMessage: Optional[string]
    PercentDone: Optional[string]
    BackupSizeInBytes: Optional[Long]
    IamRoleArn: Optional[IAMRoleArn]
    ExpectedCompletionTimeMinutes: Optional[Long]
    CreatedResourceArn: Optional[ARN]
    ResourceType: Optional[ResourceType]


class DisassociateRecoveryPointInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    RecoveryPointArn: ARN


class ExportBackupPlanTemplateInput(ServiceRequest):
    BackupPlanId: string


class ExportBackupPlanTemplateOutput(TypedDict, total=False):
    BackupPlanTemplateJson: Optional[string]


class Framework(TypedDict, total=False):
    """Contains detailed information about a framework. Frameworks contain
    controls, which evaluate and report on your backup events and resources.
    Frameworks generate daily compliance results.
    """

    FrameworkName: Optional[FrameworkName]
    FrameworkArn: Optional[ARN]
    FrameworkDescription: Optional[FrameworkDescription]
    NumberOfControls: Optional[integer]
    CreationTime: Optional[timestamp]
    DeploymentStatus: Optional[string]


FrameworkList = List[Framework]


class GetBackupPlanFromJSONInput(ServiceRequest):
    BackupPlanTemplateJson: string


class GetBackupPlanFromJSONOutput(TypedDict, total=False):
    BackupPlan: Optional[BackupPlan]


class GetBackupPlanFromTemplateInput(ServiceRequest):
    BackupPlanTemplateId: string


class GetBackupPlanFromTemplateOutput(TypedDict, total=False):
    BackupPlanDocument: Optional[BackupPlan]


class GetBackupPlanInput(ServiceRequest):
    BackupPlanId: string
    VersionId: Optional[string]


class GetBackupPlanOutput(TypedDict, total=False):
    BackupPlan: Optional[BackupPlan]
    BackupPlanId: Optional[string]
    BackupPlanArn: Optional[ARN]
    VersionId: Optional[string]
    CreatorRequestId: Optional[string]
    CreationDate: Optional[timestamp]
    DeletionDate: Optional[timestamp]
    LastExecutionDate: Optional[timestamp]
    AdvancedBackupSettings: Optional[AdvancedBackupSettings]


class GetBackupSelectionInput(ServiceRequest):
    BackupPlanId: string
    SelectionId: string


class GetBackupSelectionOutput(TypedDict, total=False):
    BackupSelection: Optional[BackupSelection]
    SelectionId: Optional[string]
    BackupPlanId: Optional[string]
    CreationDate: Optional[timestamp]
    CreatorRequestId: Optional[string]


class GetBackupVaultAccessPolicyInput(ServiceRequest):
    BackupVaultName: BackupVaultName


class GetBackupVaultAccessPolicyOutput(TypedDict, total=False):
    BackupVaultName: Optional[BackupVaultName]
    BackupVaultArn: Optional[ARN]
    Policy: Optional[IAMPolicy]


class GetBackupVaultNotificationsInput(ServiceRequest):
    BackupVaultName: BackupVaultName


class GetBackupVaultNotificationsOutput(TypedDict, total=False):
    BackupVaultName: Optional[BackupVaultName]
    BackupVaultArn: Optional[ARN]
    SNSTopicArn: Optional[ARN]
    BackupVaultEvents: Optional[BackupVaultEvents]


class GetRecoveryPointRestoreMetadataInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    RecoveryPointArn: ARN


Metadata = Dict[MetadataKey, MetadataValue]


class GetRecoveryPointRestoreMetadataOutput(TypedDict, total=False):
    BackupVaultArn: Optional[ARN]
    RecoveryPointArn: Optional[ARN]
    RestoreMetadata: Optional[Metadata]


ResourceTypes = List[ResourceType]


class GetSupportedResourceTypesOutput(TypedDict, total=False):
    ResourceTypes: Optional[ResourceTypes]


class ListBackupJobsInput(ServiceRequest):
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]
    ByResourceArn: Optional[ARN]
    ByState: Optional[BackupJobState]
    ByBackupVaultName: Optional[BackupVaultName]
    ByCreatedBefore: Optional[timestamp]
    ByCreatedAfter: Optional[timestamp]
    ByResourceType: Optional[ResourceType]
    ByAccountId: Optional[AccountId]
    ByCompleteAfter: Optional[timestamp]
    ByCompleteBefore: Optional[timestamp]


class ListBackupJobsOutput(TypedDict, total=False):
    BackupJobs: Optional[BackupJobsList]
    NextToken: Optional[string]


class ListBackupPlanTemplatesInput(ServiceRequest):
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]


class ListBackupPlanTemplatesOutput(TypedDict, total=False):
    NextToken: Optional[string]
    BackupPlanTemplatesList: Optional[BackupPlanTemplatesList]


class ListBackupPlanVersionsInput(ServiceRequest):
    BackupPlanId: string
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]


class ListBackupPlanVersionsOutput(TypedDict, total=False):
    NextToken: Optional[string]
    BackupPlanVersionsList: Optional[BackupPlanVersionsList]


class ListBackupPlansInput(ServiceRequest):
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]
    IncludeDeleted: Optional[Boolean]


class ListBackupPlansOutput(TypedDict, total=False):
    NextToken: Optional[string]
    BackupPlansList: Optional[BackupPlansList]


class ListBackupSelectionsInput(ServiceRequest):
    BackupPlanId: string
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]


class ListBackupSelectionsOutput(TypedDict, total=False):
    NextToken: Optional[string]
    BackupSelectionsList: Optional[BackupSelectionsList]


class ListBackupVaultsInput(ServiceRequest):
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]


class ListBackupVaultsOutput(TypedDict, total=False):
    BackupVaultList: Optional[BackupVaultList]
    NextToken: Optional[string]


class ListCopyJobsInput(ServiceRequest):
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]
    ByResourceArn: Optional[ARN]
    ByState: Optional[CopyJobState]
    ByCreatedBefore: Optional[timestamp]
    ByCreatedAfter: Optional[timestamp]
    ByResourceType: Optional[ResourceType]
    ByDestinationVaultArn: Optional[string]
    ByAccountId: Optional[AccountId]
    ByCompleteBefore: Optional[timestamp]
    ByCompleteAfter: Optional[timestamp]


class ListCopyJobsOutput(TypedDict, total=False):
    CopyJobs: Optional[CopyJobsList]
    NextToken: Optional[string]


class ListFrameworksInput(ServiceRequest):
    MaxResults: Optional[MaxFrameworkInputs]
    NextToken: Optional[string]


class ListFrameworksOutput(TypedDict, total=False):
    Frameworks: Optional[FrameworkList]
    NextToken: Optional[string]


class ListProtectedResourcesInput(ServiceRequest):
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]


class ProtectedResource(TypedDict, total=False):
    """A structure that contains information about a backed-up resource."""

    ResourceArn: Optional[ARN]
    ResourceType: Optional[ResourceType]
    LastBackupTime: Optional[timestamp]


ProtectedResourcesList = List[ProtectedResource]


class ListProtectedResourcesOutput(TypedDict, total=False):
    Results: Optional[ProtectedResourcesList]
    NextToken: Optional[string]


class ListRecoveryPointsByBackupVaultInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]
    ByResourceArn: Optional[ARN]
    ByResourceType: Optional[ResourceType]
    ByBackupPlanId: Optional[string]
    ByCreatedBefore: Optional[timestamp]
    ByCreatedAfter: Optional[timestamp]


class RecoveryPointByBackupVault(TypedDict, total=False):
    """Contains detailed information about the recovery points stored in a
    backup vault.
    """

    RecoveryPointArn: Optional[ARN]
    BackupVaultName: Optional[BackupVaultName]
    BackupVaultArn: Optional[ARN]
    SourceBackupVaultArn: Optional[ARN]
    ResourceArn: Optional[ARN]
    ResourceType: Optional[ResourceType]
    CreatedBy: Optional[RecoveryPointCreator]
    IamRoleArn: Optional[IAMRoleArn]
    Status: Optional[RecoveryPointStatus]
    StatusMessage: Optional[string]
    CreationDate: Optional[timestamp]
    CompletionDate: Optional[timestamp]
    BackupSizeInBytes: Optional[Long]
    CalculatedLifecycle: Optional[CalculatedLifecycle]
    Lifecycle: Optional[Lifecycle]
    EncryptionKeyArn: Optional[ARN]
    IsEncrypted: Optional[boolean]
    LastRestoreTime: Optional[timestamp]


RecoveryPointByBackupVaultList = List[RecoveryPointByBackupVault]


class ListRecoveryPointsByBackupVaultOutput(TypedDict, total=False):
    NextToken: Optional[string]
    RecoveryPoints: Optional[RecoveryPointByBackupVaultList]


class ListRecoveryPointsByResourceInput(ServiceRequest):
    ResourceArn: ARN
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]


class RecoveryPointByResource(TypedDict, total=False):
    """Contains detailed information about a saved recovery point."""

    RecoveryPointArn: Optional[ARN]
    CreationDate: Optional[timestamp]
    Status: Optional[RecoveryPointStatus]
    StatusMessage: Optional[string]
    EncryptionKeyArn: Optional[ARN]
    BackupSizeBytes: Optional[Long]
    BackupVaultName: Optional[BackupVaultName]


RecoveryPointByResourceList = List[RecoveryPointByResource]


class ListRecoveryPointsByResourceOutput(TypedDict, total=False):
    NextToken: Optional[string]
    RecoveryPoints: Optional[RecoveryPointByResourceList]


class ListReportJobsInput(ServiceRequest):
    ByReportPlanName: Optional[ReportPlanName]
    ByCreationBefore: Optional[timestamp]
    ByCreationAfter: Optional[timestamp]
    ByStatus: Optional[string]
    MaxResults: Optional[MaxResults]
    NextToken: Optional[string]


ReportJobList = List[ReportJob]


class ListReportJobsOutput(TypedDict, total=False):
    ReportJobs: Optional[ReportJobList]
    NextToken: Optional[string]


class ListReportPlansInput(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[string]


ReportPlanList = List[ReportPlan]


class ListReportPlansOutput(TypedDict, total=False):
    ReportPlans: Optional[ReportPlanList]
    NextToken: Optional[string]


class ListRestoreJobsInput(ServiceRequest):
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]
    ByAccountId: Optional[AccountId]
    ByCreatedBefore: Optional[timestamp]
    ByCreatedAfter: Optional[timestamp]
    ByStatus: Optional[RestoreJobStatus]
    ByCompleteBefore: Optional[timestamp]
    ByCompleteAfter: Optional[timestamp]


class RestoreJobsListMember(TypedDict, total=False):
    """Contains metadata about a restore job."""

    AccountId: Optional[AccountId]
    RestoreJobId: Optional[string]
    RecoveryPointArn: Optional[ARN]
    CreationDate: Optional[timestamp]
    CompletionDate: Optional[timestamp]
    Status: Optional[RestoreJobStatus]
    StatusMessage: Optional[string]
    PercentDone: Optional[string]
    BackupSizeInBytes: Optional[Long]
    IamRoleArn: Optional[IAMRoleArn]
    ExpectedCompletionTimeMinutes: Optional[Long]
    CreatedResourceArn: Optional[ARN]
    ResourceType: Optional[ResourceType]


RestoreJobsList = List[RestoreJobsListMember]


class ListRestoreJobsOutput(TypedDict, total=False):
    RestoreJobs: Optional[RestoreJobsList]
    NextToken: Optional[string]


class ListTagsInput(ServiceRequest):
    ResourceArn: ARN
    NextToken: Optional[string]
    MaxResults: Optional[MaxResults]


class ListTagsOutput(TypedDict, total=False):
    NextToken: Optional[string]
    Tags: Optional[Tags]


class PutBackupVaultAccessPolicyInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    Policy: Optional[IAMPolicy]


class PutBackupVaultLockConfigurationInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    MinRetentionDays: Optional[Long]
    MaxRetentionDays: Optional[Long]
    ChangeableForDays: Optional[Long]


class PutBackupVaultNotificationsInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    SNSTopicArn: ARN
    BackupVaultEvents: BackupVaultEvents


class StartBackupJobInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    ResourceArn: ARN
    IamRoleArn: IAMRoleArn
    IdempotencyToken: Optional[string]
    StartWindowMinutes: Optional[WindowMinutes]
    CompleteWindowMinutes: Optional[WindowMinutes]
    Lifecycle: Optional[Lifecycle]
    RecoveryPointTags: Optional[Tags]
    BackupOptions: Optional[BackupOptions]


class StartBackupJobOutput(TypedDict, total=False):
    BackupJobId: Optional[string]
    RecoveryPointArn: Optional[ARN]
    CreationDate: Optional[timestamp]


class StartCopyJobInput(ServiceRequest):
    RecoveryPointArn: ARN
    SourceBackupVaultName: BackupVaultName
    DestinationBackupVaultArn: ARN
    IamRoleArn: IAMRoleArn
    IdempotencyToken: Optional[string]
    Lifecycle: Optional[Lifecycle]


class StartCopyJobOutput(TypedDict, total=False):
    CopyJobId: Optional[string]
    CreationDate: Optional[timestamp]


class StartReportJobInput(ServiceRequest):
    ReportPlanName: ReportPlanName
    IdempotencyToken: Optional[string]


class StartReportJobOutput(TypedDict, total=False):
    ReportJobId: Optional[ReportJobId]


class StartRestoreJobInput(ServiceRequest):
    RecoveryPointArn: ARN
    Metadata: Metadata
    IamRoleArn: IAMRoleArn
    IdempotencyToken: Optional[string]
    ResourceType: Optional[ResourceType]


class StartRestoreJobOutput(TypedDict, total=False):
    RestoreJobId: Optional[RestoreJobId]


class StopBackupJobInput(ServiceRequest):
    BackupJobId: string


TagKeyList = List[string]


class TagResourceInput(ServiceRequest):
    ResourceArn: ARN
    Tags: Tags


class UntagResourceInput(ServiceRequest):
    ResourceArn: ARN
    TagKeyList: TagKeyList


class UpdateBackupPlanInput(ServiceRequest):
    BackupPlanId: string
    BackupPlan: BackupPlanInput


class UpdateBackupPlanOutput(TypedDict, total=False):
    BackupPlanId: Optional[string]
    BackupPlanArn: Optional[ARN]
    CreationDate: Optional[timestamp]
    VersionId: Optional[string]
    AdvancedBackupSettings: Optional[AdvancedBackupSettings]


class UpdateFrameworkInput(ServiceRequest):
    FrameworkName: FrameworkName
    FrameworkDescription: Optional[FrameworkDescription]
    FrameworkControls: Optional[FrameworkControls]
    IdempotencyToken: Optional[string]


class UpdateFrameworkOutput(TypedDict, total=False):
    FrameworkName: Optional[FrameworkName]
    FrameworkArn: Optional[ARN]
    CreationTime: Optional[timestamp]


class UpdateGlobalSettingsInput(ServiceRequest):
    GlobalSettings: Optional[GlobalSettings]


class UpdateRecoveryPointLifecycleInput(ServiceRequest):
    BackupVaultName: BackupVaultName
    RecoveryPointArn: ARN
    Lifecycle: Optional[Lifecycle]


class UpdateRecoveryPointLifecycleOutput(TypedDict, total=False):
    BackupVaultArn: Optional[ARN]
    RecoveryPointArn: Optional[ARN]
    Lifecycle: Optional[Lifecycle]
    CalculatedLifecycle: Optional[CalculatedLifecycle]


class UpdateRegionSettingsInput(ServiceRequest):
    ResourceTypeOptInPreference: Optional[ResourceTypeOptInPreference]
    ResourceTypeManagementPreference: Optional[ResourceTypeManagementPreference]


class UpdateReportPlanInput(ServiceRequest):
    ReportPlanName: ReportPlanName
    ReportPlanDescription: Optional[ReportPlanDescription]
    ReportDeliveryChannel: Optional[ReportDeliveryChannel]
    ReportSetting: Optional[ReportSetting]
    IdempotencyToken: Optional[string]


class UpdateReportPlanOutput(TypedDict, total=False):
    ReportPlanName: Optional[ReportPlanName]
    ReportPlanArn: Optional[ARN]
    CreationTime: Optional[timestamp]


class BackupApi:

    service = "backup"
    version = "2018-11-15"

    @handler("CreateBackupPlan")
    def create_backup_plan(
        self,
        context: RequestContext,
        backup_plan: BackupPlanInput,
        backup_plan_tags: Tags = None,
        creator_request_id: string = None,
    ) -> CreateBackupPlanOutput:
        """Creates a backup plan using a backup plan name and backup rules. A
        backup plan is a document that contains information that Backup uses to
        schedule tasks that create recovery points for resources.

        If you call ``CreateBackupPlan`` with a plan that already exists, you
        receive an ``AlreadyExistsException`` exception.

        :param backup_plan: Specifies the body of a backup plan.
        :param backup_plan_tags: To help organize your resources, you can assign your own metadata to the
        resources that you create.
        :param creator_request_id: Identifies the request and allows failed requests to be retried without
        the risk of running the operation twice.
        :returns: CreateBackupPlanOutput
        :raises LimitExceededException:
        :raises AlreadyExistsException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("CreateBackupSelection")
    def create_backup_selection(
        self,
        context: RequestContext,
        backup_plan_id: string,
        backup_selection: BackupSelection,
        creator_request_id: string = None,
    ) -> CreateBackupSelectionOutput:
        """Creates a JSON document that specifies a set of resources to assign to a
        backup plan. For examples, see `Assigning resources
        programmatically <https://docs.aws.amazon.com/aws-backup/latest/devguide/assigning-resources.html#assigning-resources-json>`__.

        :param backup_plan_id: Uniquely identifies the backup plan to be associated with the selection
        of resources.
        :param backup_selection: Specifies the body of a request to assign a set of resources to a backup
        plan.
        :param creator_request_id: A unique string that identifies the request and allows failed requests
        to be retried without the risk of running the operation twice.
        :returns: CreateBackupSelectionOutput
        :raises LimitExceededException:
        :raises AlreadyExistsException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("CreateBackupVault")
    def create_backup_vault(
        self,
        context: RequestContext,
        backup_vault_name: BackupVaultName,
        backup_vault_tags: Tags = None,
        encryption_key_arn: ARN = None,
        creator_request_id: string = None,
    ) -> CreateBackupVaultOutput:
        """Creates a logical container where backups are stored. A
        ``CreateBackupVault`` request includes a name, optionally one or more
        resource tags, an encryption key, and a request ID.

        Do not include sensitive data, such as passport numbers, in the name of
        a backup vault.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :param backup_vault_tags: Metadata that you can assign to help organize the resources that you
        create.
        :param encryption_key_arn: The server-side encryption key that is used to protect your backups; for
        example,
        ``arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab``.
        :param creator_request_id: A unique string that identifies the request and allows failed requests
        to be retried without the risk of running the operation twice.
        :returns: CreateBackupVaultOutput
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises LimitExceededException:
        :raises AlreadyExistsException:
        """
        raise NotImplementedError

    @handler("CreateFramework")
    def create_framework(
        self,
        context: RequestContext,
        framework_name: FrameworkName,
        framework_controls: FrameworkControls,
        framework_description: FrameworkDescription = None,
        idempotency_token: string = None,
        framework_tags: stringMap = None,
    ) -> CreateFrameworkOutput:
        """Creates a framework with one or more controls. A framework is a
        collection of controls that you can use to evaluate your backup
        practices. By using pre-built customizable controls to define your
        policies, you can evaluate whether your backup practices comply with
        your policies and which resources are not yet in compliance.

        :param framework_name: The unique name of the framework.
        :param framework_controls: A list of the controls that make up the framework.
        :param framework_description: An optional description of the framework with a maximum of 1,024
        characters.
        :param idempotency_token: A customer-chosen string that you can use to distinguish between
        otherwise identical calls to ``CreateFrameworkInput``.
        :param framework_tags: Metadata that you can assign to help organize the frameworks that you
        create.
        :returns: CreateFrameworkOutput
        :raises AlreadyExistsException:
        :raises LimitExceededException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("CreateReportPlan")
    def create_report_plan(
        self,
        context: RequestContext,
        report_plan_name: ReportPlanName,
        report_delivery_channel: ReportDeliveryChannel,
        report_setting: ReportSetting,
        report_plan_description: ReportPlanDescription = None,
        report_plan_tags: stringMap = None,
        idempotency_token: string = None,
    ) -> CreateReportPlanOutput:
        """Creates a report plan. A report plan is a document that contains
        information about the contents of the report and where Backup will
        deliver it.

        If you call ``CreateReportPlan`` with a plan that already exists, you
        receive an ``AlreadyExistsException`` exception.

        :param report_plan_name: The unique name of the report plan.
        :param report_delivery_channel: A structure that contains information about where and how to deliver
        your reports, specifically your Amazon S3 bucket name, S3 key prefix,
        and the formats of your reports.
        :param report_setting: Identifies the report template for the report.
        :param report_plan_description: An optional description of the report plan with a maximum of 1,024
        characters.
        :param report_plan_tags: Metadata that you can assign to help organize the report plans that you
        create.
        :param idempotency_token: A customer-chosen string that you can use to distinguish between
        otherwise identical calls to ``CreateReportPlanInput``.
        :returns: CreateReportPlanOutput
        :raises AlreadyExistsException:
        :raises LimitExceededException:
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        :raises MissingParameterValueException:
        """
        raise NotImplementedError

    @handler("DeleteBackupPlan")
    def delete_backup_plan(
        self, context: RequestContext, backup_plan_id: string
    ) -> DeleteBackupPlanOutput:
        """Deletes a backup plan. A backup plan can only be deleted after all
        associated selections of resources have been deleted. Deleting a backup
        plan deletes the current version of a backup plan. Previous versions, if
        any, will still exist.

        :param backup_plan_id: Uniquely identifies a backup plan.
        :returns: DeleteBackupPlanOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DeleteBackupSelection")
    def delete_backup_selection(
        self, context: RequestContext, backup_plan_id: string, selection_id: string
    ) -> None:
        """Deletes the resource selection associated with a backup plan that is
        specified by the ``SelectionId``.

        :param backup_plan_id: Uniquely identifies a backup plan.
        :param selection_id: Uniquely identifies the body of a request to assign a set of resources
        to a backup plan.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteBackupVault")
    def delete_backup_vault(self, context: RequestContext, backup_vault_name: string) -> None:
        """Deletes the backup vault identified by its name. A vault can be deleted
        only if it is empty.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DeleteBackupVaultAccessPolicy")
    def delete_backup_vault_access_policy(
        self, context: RequestContext, backup_vault_name: BackupVaultName
    ) -> None:
        """Deletes the policy document that manages permissions on a backup vault.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteBackupVaultLockConfiguration")
    def delete_backup_vault_lock_configuration(
        self, context: RequestContext, backup_vault_name: BackupVaultName
    ) -> None:
        """Deletes Backup Vault Lock from a backup vault specified by a backup
        vault name.

        If the Vault Lock configuration is immutable, then you cannot delete
        Vault Lock using API operations, and you will receive an
        ``InvalidRequestException`` if you attempt to do so. For more
        information, see `Vault
        Lock <https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html>`__
        in the *Backup Developer Guide*.

        :param backup_vault_name: The name of the backup vault from which to delete Backup Vault Lock.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteBackupVaultNotifications")
    def delete_backup_vault_notifications(
        self, context: RequestContext, backup_vault_name: BackupVaultName
    ) -> None:
        """Deletes event notifications for the specified backup vault.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteFramework")
    def delete_framework(self, context: RequestContext, framework_name: FrameworkName) -> None:
        """Deletes the framework specified by a framework name.

        :param framework_name: The unique name of a framework.
        :raises MissingParameterValueException:
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        :raises ConflictException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteRecoveryPoint")
    def delete_recovery_point(
        self, context: RequestContext, backup_vault_name: BackupVaultName, recovery_point_arn: ARN
    ) -> None:
        """Deletes the recovery point specified by a recovery point ID.

        If the recovery point ID belongs to a continuous backup, calling this
        endpoint deletes the existing continuous backup and stops future
        continuous backup.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :param recovery_point_arn: An Amazon Resource Name (ARN) that uniquely identifies a recovery point;
        for example,
        ``arn:aws:backup:us-east-1:123456789012:recovery-point:1EB3B5E7-9EB0-435A-A80B-108B488B0D45``.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises InvalidResourceStateException:
        :raises ServiceUnavailableException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DeleteReportPlan")
    def delete_report_plan(self, context: RequestContext, report_plan_name: ReportPlanName) -> None:
        """Deletes the report plan specified by a report plan name.

        :param report_plan_name: The unique name of a report plan.
        :raises MissingParameterValueException:
        :raises InvalidParameterValueException:
        :raises ConflictException:
        :raises ServiceUnavailableException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeBackupJob")
    def describe_backup_job(
        self, context: RequestContext, backup_job_id: string
    ) -> DescribeBackupJobOutput:
        """Returns backup job details for the specified ``BackupJobId``.

        :param backup_job_id: Uniquely identifies a request to Backup to back up a resource.
        :returns: DescribeBackupJobOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises DependencyFailureException:
        """
        raise NotImplementedError

    @handler("DescribeBackupVault")
    def describe_backup_vault(
        self, context: RequestContext, backup_vault_name: string
    ) -> DescribeBackupVaultOutput:
        """Returns metadata about a backup vault specified by its name.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :returns: DescribeBackupVaultOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeCopyJob")
    def describe_copy_job(
        self, context: RequestContext, copy_job_id: string
    ) -> DescribeCopyJobOutput:
        """Returns metadata associated with creating a copy of a resource.

        :param copy_job_id: Uniquely identifies a copy job.
        :returns: DescribeCopyJobOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeFramework")
    def describe_framework(
        self, context: RequestContext, framework_name: FrameworkName
    ) -> DescribeFrameworkOutput:
        """Returns the framework details for the specified ``FrameworkName``.

        :param framework_name: The unique name of a framework.
        :returns: DescribeFrameworkOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeGlobalSettings")
    def describe_global_settings(
        self,
        context: RequestContext,
    ) -> DescribeGlobalSettingsOutput:
        """Describes whether the Amazon Web Services account is opted in to
        cross-account backup. Returns an error if the account is not a member of
        an Organizations organization. Example:
        ``describe-global-settings --region us-west-2``

        :returns: DescribeGlobalSettingsOutput
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeProtectedResource")
    def describe_protected_resource(
        self, context: RequestContext, resource_arn: ARN
    ) -> DescribeProtectedResourceOutput:
        """Returns information about a saved resource, including the last time it
        was backed up, its Amazon Resource Name (ARN), and the Amazon Web
        Services service type of the saved resource.

        :param resource_arn: An Amazon Resource Name (ARN) that uniquely identifies a resource.
        :returns: DescribeProtectedResourceOutput
        :raises MissingParameterValueException:
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeRecoveryPoint")
    def describe_recovery_point(
        self, context: RequestContext, backup_vault_name: BackupVaultName, recovery_point_arn: ARN
    ) -> DescribeRecoveryPointOutput:
        """Returns metadata associated with a recovery point, including ID, status,
        encryption, and lifecycle.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :param recovery_point_arn: An Amazon Resource Name (ARN) that uniquely identifies a recovery point;
        for example,
        ``arn:aws:backup:us-east-1:123456789012:recovery-point:1EB3B5E7-9EB0-435A-A80B-108B488B0D45``.
        :returns: DescribeRecoveryPointOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeRegionSettings")
    def describe_region_settings(
        self,
        context: RequestContext,
    ) -> DescribeRegionSettingsOutput:
        """Returns the current service opt-in settings for the Region. If service
        opt-in is enabled for a service, Backup tries to protect that service's
        resources in this Region, when the resource is included in an on-demand
        backup or scheduled backup plan. Otherwise, Backup does not try to
        protect that service's resources in this Region.

        :returns: DescribeRegionSettingsOutput
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeReportJob")
    def describe_report_job(
        self, context: RequestContext, report_job_id: ReportJobId
    ) -> DescribeReportJobOutput:
        """Returns the details associated with creating a report as specified by
        its ``ReportJobId``.

        :param report_job_id: The identifier of the report job.
        :returns: DescribeReportJobOutput
        :raises ServiceUnavailableException:
        :raises MissingParameterValueException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeReportPlan")
    def describe_report_plan(
        self, context: RequestContext, report_plan_name: ReportPlanName
    ) -> DescribeReportPlanOutput:
        """Returns a list of all report plans for an Amazon Web Services account
        and Amazon Web Services Region.

        :param report_plan_name: The unique name of a report plan.
        :returns: DescribeReportPlanOutput
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ResourceNotFoundException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeRestoreJob")
    def describe_restore_job(
        self, context: RequestContext, restore_job_id: RestoreJobId
    ) -> DescribeRestoreJobOutput:
        """Returns metadata associated with a restore job that is specified by a
        job ID.

        :param restore_job_id: Uniquely identifies the job that restores a recovery point.
        :returns: DescribeRestoreJobOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises DependencyFailureException:
        """
        raise NotImplementedError

    @handler("DisassociateRecoveryPoint")
    def disassociate_recovery_point(
        self, context: RequestContext, backup_vault_name: BackupVaultName, recovery_point_arn: ARN
    ) -> None:
        """Deletes the specified continuous backup recovery point from Backup and
        releases control of that continuous backup to the source service, such
        as Amazon RDS. The source service will continue to create and retain
        continuous backups using the lifecycle that you specified in your
        original backup plan.

        Does not support snapshot backup recovery points.

        :param backup_vault_name: The unique name of an Backup vault.
        :param recovery_point_arn: An Amazon Resource Name (ARN) that uniquely identifies an Backup
        recovery point.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises InvalidResourceStateException:
        :raises ServiceUnavailableException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ExportBackupPlanTemplate")
    def export_backup_plan_template(
        self, context: RequestContext, backup_plan_id: string
    ) -> ExportBackupPlanTemplateOutput:
        """Returns the backup plan that is specified by the plan ID as a backup
        template.

        :param backup_plan_id: Uniquely identifies a backup plan.
        :returns: ExportBackupPlanTemplateOutput
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("GetBackupPlan")
    def get_backup_plan(
        self, context: RequestContext, backup_plan_id: string, version_id: string = None
    ) -> GetBackupPlanOutput:
        """Returns ``BackupPlan`` details for the specified ``BackupPlanId``. The
        details are the body of a backup plan in JSON format, in addition to
        plan metadata.

        :param backup_plan_id: Uniquely identifies a backup plan.
        :param version_id: Unique, randomly generated, Unicode, UTF-8 encoded strings that are at
        most 1,024 bytes long.
        :returns: GetBackupPlanOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetBackupPlanFromJSON")
    def get_backup_plan_from_json(
        self, context: RequestContext, backup_plan_template_json: string
    ) -> GetBackupPlanFromJSONOutput:
        """Returns a valid JSON document specifying a backup plan or an error.

        :param backup_plan_template_json: A customer-supplied backup plan document in JSON format.
        :returns: GetBackupPlanFromJSONOutput
        :raises LimitExceededException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("GetBackupPlanFromTemplate")
    def get_backup_plan_from_template(
        self, context: RequestContext, backup_plan_template_id: string
    ) -> GetBackupPlanFromTemplateOutput:
        """Returns the template specified by its ``templateId`` as a backup plan.

        :param backup_plan_template_id: Uniquely identifies a stored backup plan template.
        :returns: GetBackupPlanFromTemplateOutput
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("GetBackupSelection")
    def get_backup_selection(
        self, context: RequestContext, backup_plan_id: string, selection_id: string
    ) -> GetBackupSelectionOutput:
        """Returns selection metadata and a document in JSON format that specifies
        a list of resources that are associated with a backup plan.

        :param backup_plan_id: Uniquely identifies a backup plan.
        :param selection_id: Uniquely identifies the body of a request to assign a set of resources
        to a backup plan.
        :returns: GetBackupSelectionOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetBackupVaultAccessPolicy")
    def get_backup_vault_access_policy(
        self, context: RequestContext, backup_vault_name: BackupVaultName
    ) -> GetBackupVaultAccessPolicyOutput:
        """Returns the access policy document that is associated with the named
        backup vault.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :returns: GetBackupVaultAccessPolicyOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetBackupVaultNotifications")
    def get_backup_vault_notifications(
        self, context: RequestContext, backup_vault_name: BackupVaultName
    ) -> GetBackupVaultNotificationsOutput:
        """Returns event notifications for the specified backup vault.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :returns: GetBackupVaultNotificationsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetRecoveryPointRestoreMetadata")
    def get_recovery_point_restore_metadata(
        self, context: RequestContext, backup_vault_name: BackupVaultName, recovery_point_arn: ARN
    ) -> GetRecoveryPointRestoreMetadataOutput:
        """Returns a set of metadata key-value pairs that were used to create the
        backup.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :param recovery_point_arn: An Amazon Resource Name (ARN) that uniquely identifies a recovery point;
        for example,
        ``arn:aws:backup:us-east-1:123456789012:recovery-point:1EB3B5E7-9EB0-435A-A80B-108B488B0D45``.
        :returns: GetRecoveryPointRestoreMetadataOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetSupportedResourceTypes")
    def get_supported_resource_types(
        self,
        context: RequestContext,
    ) -> GetSupportedResourceTypesOutput:
        """Returns the Amazon Web Services resource types supported by Backup.

        :returns: GetSupportedResourceTypesOutput
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListBackupJobs")
    def list_backup_jobs(
        self,
        context: RequestContext,
        next_token: string = None,
        max_results: MaxResults = None,
        by_resource_arn: ARN = None,
        by_state: BackupJobState = None,
        by_backup_vault_name: BackupVaultName = None,
        by_created_before: timestamp = None,
        by_created_after: timestamp = None,
        by_resource_type: ResourceType = None,
        by_account_id: AccountId = None,
        by_complete_after: timestamp = None,
        by_complete_before: timestamp = None,
    ) -> ListBackupJobsOutput:
        """Returns a list of existing backup jobs for an authenticated account for
        the last 30 days. For a longer period of time, consider using these
        `monitoring
        tools <https://docs.aws.amazon.com/aws-backup/latest/devguide/monitoring.html>`__.

        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :param by_resource_arn: Returns only backup jobs that match the specified resource Amazon
        Resource Name (ARN).
        :param by_state: Returns only backup jobs that are in the specified state.
        :param by_backup_vault_name: Returns only backup jobs that will be stored in the specified backup
        vault.
        :param by_created_before: Returns only backup jobs that were created before the specified date.
        :param by_created_after: Returns only backup jobs that were created after the specified date.
        :param by_resource_type: Returns only backup jobs for the specified resources:

        -  ``Aurora`` for Amazon Aurora

        -  ``DocumentDB`` for Amazon DocumentDB (with MongoDB compatibility)

        -  ``DynamoDB`` for Amazon DynamoDB

        -  ``EBS`` for Amazon Elastic Block Store

        -  ``EC2`` for Amazon Elastic Compute Cloud

        -  ``EFS`` for Amazon Elastic File System

        -  ``FSx`` for Amazon FSx

        -  ``Neptune`` for Amazon Neptune

        -  ``RDS`` for Amazon Relational Database Service

        -  ``Storage Gateway`` for Storage Gateway

        -  ``S3`` for Amazon S3

        -  ``VirtualMachine`` for virtual machines.
        :param by_account_id: The account ID to list the jobs from.
        :param by_complete_after: Returns only backup jobs completed after a date expressed in Unix format
        and Coordinated Universal Time (UTC).
        :param by_complete_before: Returns only backup jobs completed before a date expressed in Unix
        format and Coordinated Universal Time (UTC).
        :returns: ListBackupJobsOutput
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListBackupPlanTemplates")
    def list_backup_plan_templates(
        self, context: RequestContext, next_token: string = None, max_results: MaxResults = None
    ) -> ListBackupPlanTemplatesOutput:
        """Returns metadata of your saved backup plan templates, including the
        template ID, name, and the creation and deletion dates.

        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :returns: ListBackupPlanTemplatesOutput
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListBackupPlanVersions")
    def list_backup_plan_versions(
        self,
        context: RequestContext,
        backup_plan_id: string,
        next_token: string = None,
        max_results: MaxResults = None,
    ) -> ListBackupPlanVersionsOutput:
        """Returns version metadata of your backup plans, including Amazon Resource
        Names (ARNs), backup plan IDs, creation and deletion dates, plan names,
        and version IDs.

        :param backup_plan_id: Uniquely identifies a backup plan.
        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :returns: ListBackupPlanVersionsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListBackupPlans")
    def list_backup_plans(
        self,
        context: RequestContext,
        next_token: string = None,
        max_results: MaxResults = None,
        include_deleted: Boolean = None,
    ) -> ListBackupPlansOutput:
        """Returns a list of all active backup plans for an authenticated account.
        The list contains information such as Amazon Resource Names (ARNs), plan
        IDs, creation and deletion dates, version IDs, plan names, and creator
        request IDs.

        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :param include_deleted: A Boolean value with a default value of ``FALSE`` that returns deleted
        backup plans when set to ``TRUE``.
        :returns: ListBackupPlansOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListBackupSelections")
    def list_backup_selections(
        self,
        context: RequestContext,
        backup_plan_id: string,
        next_token: string = None,
        max_results: MaxResults = None,
    ) -> ListBackupSelectionsOutput:
        """Returns an array containing metadata of the resources associated with
        the target backup plan.

        :param backup_plan_id: Uniquely identifies a backup plan.
        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :returns: ListBackupSelectionsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListBackupVaults")
    def list_backup_vaults(
        self, context: RequestContext, next_token: string = None, max_results: MaxResults = None
    ) -> ListBackupVaultsOutput:
        """Returns a list of recovery point storage containers along with
        information about them.

        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :returns: ListBackupVaultsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListCopyJobs")
    def list_copy_jobs(
        self,
        context: RequestContext,
        next_token: string = None,
        max_results: MaxResults = None,
        by_resource_arn: ARN = None,
        by_state: CopyJobState = None,
        by_created_before: timestamp = None,
        by_created_after: timestamp = None,
        by_resource_type: ResourceType = None,
        by_destination_vault_arn: string = None,
        by_account_id: AccountId = None,
        by_complete_before: timestamp = None,
        by_complete_after: timestamp = None,
    ) -> ListCopyJobsOutput:
        """Returns metadata about your copy jobs.

        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :param by_resource_arn: Returns only copy jobs that match the specified resource Amazon Resource
        Name (ARN).
        :param by_state: Returns only copy jobs that are in the specified state.
        :param by_created_before: Returns only copy jobs that were created before the specified date.
        :param by_created_after: Returns only copy jobs that were created after the specified date.
        :param by_resource_type: Returns only backup jobs for the specified resources:

        -  ``Aurora`` for Amazon Aurora

        -  ``DocumentDB`` for Amazon DocumentDB (with MongoDB compatibility)

        -  ``DynamoDB`` for Amazon DynamoDB

        -  ``EBS`` for Amazon Elastic Block Store

        -  ``EC2`` for Amazon Elastic Compute Cloud

        -  ``EFS`` for Amazon Elastic File System

        -  ``FSx`` for Amazon FSx

        -  ``Neptune`` for Amazon Neptune

        -  ``RDS`` for Amazon Relational Database Service

        -  ``Storage Gateway`` for Storage Gateway

        -  ``S3`` for Amazon S3

        -  ``VirtualMachine`` for virtual machines.
        :param by_destination_vault_arn: An Amazon Resource Name (ARN) that uniquely identifies a source backup
        vault to copy from; for example,
        ``arn:aws:backup:us-east-1:123456789012:vault:aBackupVault``.
        :param by_account_id: The account ID to list the jobs from.
        :param by_complete_before: Returns only copy jobs completed before a date expressed in Unix format
        and Coordinated Universal Time (UTC).
        :param by_complete_after: Returns only copy jobs completed after a date expressed in Unix format
        and Coordinated Universal Time (UTC).
        :returns: ListCopyJobsOutput
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListFrameworks")
    def list_frameworks(
        self,
        context: RequestContext,
        max_results: MaxFrameworkInputs = None,
        next_token: string = None,
    ) -> ListFrameworksOutput:
        """Returns a list of all frameworks for an Amazon Web Services account and
        Amazon Web Services Region.

        :param max_results: The number of desired results from 1 to 1000.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which can be used to return the next set of items in the
        list.
        :returns: ListFrameworksOutput
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListProtectedResources")
    def list_protected_resources(
        self, context: RequestContext, next_token: string = None, max_results: MaxResults = None
    ) -> ListProtectedResourcesOutput:
        """Returns an array of resources successfully backed up by Backup,
        including the time the resource was saved, an Amazon Resource Name (ARN)
        of the resource, and a resource type.

        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :returns: ListProtectedResourcesOutput
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListRecoveryPointsByBackupVault")
    def list_recovery_points_by_backup_vault(
        self,
        context: RequestContext,
        backup_vault_name: BackupVaultName,
        next_token: string = None,
        max_results: MaxResults = None,
        by_resource_arn: ARN = None,
        by_resource_type: ResourceType = None,
        by_backup_plan_id: string = None,
        by_created_before: timestamp = None,
        by_created_after: timestamp = None,
    ) -> ListRecoveryPointsByBackupVaultOutput:
        """Returns detailed information about the recovery points stored in a
        backup vault.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :param by_resource_arn: Returns only recovery points that match the specified resource Amazon
        Resource Name (ARN).
        :param by_resource_type: Returns only recovery points that match the specified resource type.
        :param by_backup_plan_id: Returns only recovery points that match the specified backup plan ID.
        :param by_created_before: Returns only recovery points that were created before the specified
        timestamp.
        :param by_created_after: Returns only recovery points that were created after the specified
        timestamp.
        :returns: ListRecoveryPointsByBackupVaultOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListRecoveryPointsByResource")
    def list_recovery_points_by_resource(
        self,
        context: RequestContext,
        resource_arn: ARN,
        next_token: string = None,
        max_results: MaxResults = None,
    ) -> ListRecoveryPointsByResourceOutput:
        """Returns detailed information about all the recovery points of the type
        specified by a resource Amazon Resource Name (ARN).

        For Amazon EFS and Amazon EC2, this action only lists recovery points
        created by Backup.

        :param resource_arn: An ARN that uniquely identifies a resource.
        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :returns: ListRecoveryPointsByResourceOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListReportJobs")
    def list_report_jobs(
        self,
        context: RequestContext,
        by_report_plan_name: ReportPlanName = None,
        by_creation_before: timestamp = None,
        by_creation_after: timestamp = None,
        by_status: string = None,
        max_results: MaxResults = None,
        next_token: string = None,
    ) -> ListReportJobsOutput:
        """Returns details about your report jobs.

        :param by_report_plan_name: Returns only report jobs with the specified report plan name.
        :param by_creation_before: Returns only report jobs that were created before the date and time
        specified in Unix format and Coordinated Universal Time (UTC).
        :param by_creation_after: Returns only report jobs that were created after the date and time
        specified in Unix format and Coordinated Universal Time (UTC).
        :param by_status: Returns only report jobs that are in the specified status.
        :param max_results: The number of desired results from 1 to 1000.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which can be used to return the next set of items in the
        list.
        :returns: ListReportJobsOutput
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListReportPlans")
    def list_report_plans(
        self, context: RequestContext, max_results: MaxResults = None, next_token: string = None
    ) -> ListReportPlansOutput:
        """Returns a list of your report plans. For detailed information about a
        single report plan, use ``DescribeReportPlan``.

        :param max_results: The number of desired results from 1 to 1000.
        :param next_token: An identifier that was returned from the previous call to this
        operation, which can be used to return the next set of items in the
        list.
        :returns: ListReportPlansOutput
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListRestoreJobs")
    def list_restore_jobs(
        self,
        context: RequestContext,
        next_token: string = None,
        max_results: MaxResults = None,
        by_account_id: AccountId = None,
        by_created_before: timestamp = None,
        by_created_after: timestamp = None,
        by_status: RestoreJobStatus = None,
        by_complete_before: timestamp = None,
        by_complete_after: timestamp = None,
    ) -> ListRestoreJobsOutput:
        """Returns a list of jobs that Backup initiated to restore a saved
        resource, including details about the recovery process.

        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :param by_account_id: The account ID to list the jobs from.
        :param by_created_before: Returns only restore jobs that were created before the specified date.
        :param by_created_after: Returns only restore jobs that were created after the specified date.
        :param by_status: Returns only restore jobs associated with the specified job status.
        :param by_complete_before: Returns only copy jobs completed before a date expressed in Unix format
        and Coordinated Universal Time (UTC).
        :param by_complete_after: Returns only copy jobs completed after a date expressed in Unix format
        and Coordinated Universal Time (UTC).
        :returns: ListRestoreJobsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListTags")
    def list_tags(
        self,
        context: RequestContext,
        resource_arn: ARN,
        next_token: string = None,
        max_results: MaxResults = None,
    ) -> ListTagsOutput:
        """Returns a list of key-value pairs assigned to a target recovery point,
        backup plan, or backup vault.

        ``ListTags`` only works for resource types that support full Backup
        management of their backups. Those resource types are listed in the
        "Full Backup management" section of the `Feature availability by
        resource <https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html#features-by-resource>`__
        table.

        :param resource_arn: An Amazon Resource Name (ARN) that uniquely identifies a resource.
        :param next_token: The next item following a partial list of returned items.
        :param max_results: The maximum number of items to be returned.
        :returns: ListTagsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("PutBackupVaultAccessPolicy")
    def put_backup_vault_access_policy(
        self, context: RequestContext, backup_vault_name: BackupVaultName, policy: IAMPolicy = None
    ) -> None:
        """Sets a resource-based policy that is used to manage access permissions
        on the target backup vault. Requires a backup vault name and an access
        policy document in JSON format.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :param policy: The backup vault access policy document in JSON format.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("PutBackupVaultLockConfiguration")
    def put_backup_vault_lock_configuration(
        self,
        context: RequestContext,
        backup_vault_name: BackupVaultName,
        min_retention_days: Long = None,
        max_retention_days: Long = None,
        changeable_for_days: Long = None,
    ) -> None:
        """Applies Backup Vault Lock to a backup vault, preventing attempts to
        delete any recovery point stored in or created in a backup vault. Vault
        Lock also prevents attempts to update the lifecycle policy that controls
        the retention period of any recovery point currently stored in a backup
        vault. If specified, Vault Lock enforces a minimum and maximum retention
        period for future backup and copy jobs that target a backup vault.

        Backup Vault Lock has yet to receive a third-party assessment for SEC
        17a-4(f) and CFTC.

        :param backup_vault_name: The Backup Vault Lock configuration that specifies the name of the
        backup vault it protects.
        :param min_retention_days: The Backup Vault Lock configuration that specifies the minimum retention
        period that the vault retains its recovery points.
        :param max_retention_days: The Backup Vault Lock configuration that specifies the maximum retention
        period that the vault retains its recovery points.
        :param changeable_for_days: The Backup Vault Lock configuration that specifies the number of days
        before the lock date.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("PutBackupVaultNotifications")
    def put_backup_vault_notifications(
        self,
        context: RequestContext,
        backup_vault_name: BackupVaultName,
        sns_topic_arn: ARN,
        backup_vault_events: BackupVaultEvents,
    ) -> None:
        """Turns on notifications on a backup vault for the specified topic and
        events.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :param sns_topic_arn: The Amazon Resource Name (ARN) that specifies the topic for a backup
        vault’s events; for example,
        ``arn:aws:sns:us-west-2:111122223333:MyVaultTopic``.
        :param backup_vault_events: An array of events that indicate the status of jobs to back up resources
        to the backup vault.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("StartBackupJob")
    def start_backup_job(
        self,
        context: RequestContext,
        backup_vault_name: BackupVaultName,
        resource_arn: ARN,
        iam_role_arn: IAMRoleArn,
        idempotency_token: string = None,
        start_window_minutes: WindowMinutes = None,
        complete_window_minutes: WindowMinutes = None,
        lifecycle: Lifecycle = None,
        recovery_point_tags: Tags = None,
        backup_options: BackupOptions = None,
    ) -> StartBackupJobOutput:
        """Starts an on-demand backup job for the specified resource.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :param resource_arn: An Amazon Resource Name (ARN) that uniquely identifies a resource.
        :param iam_role_arn: Specifies the IAM role ARN used to create the target recovery point; for
        example, ``arn:aws:iam::123456789012:role/S3Access``.
        :param idempotency_token: A customer-chosen string that you can use to distinguish between
        otherwise identical calls to ``StartBackupJob``.
        :param start_window_minutes: A value in minutes after a backup is scheduled before a job will be
        canceled if it doesn't start successfully.
        :param complete_window_minutes: A value in minutes during which a successfully started backup must
        complete, or else Backup will cancel the job.
        :param lifecycle: The lifecycle defines when a protected resource is transitioned to cold
        storage and when it expires.
        :param recovery_point_tags: To help organize your resources, you can assign your own metadata to the
        resources that you create.
        :param backup_options: Specifies the backup option for a selected resource.
        :returns: StartBackupJobOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("StartCopyJob")
    def start_copy_job(
        self,
        context: RequestContext,
        recovery_point_arn: ARN,
        source_backup_vault_name: BackupVaultName,
        destination_backup_vault_arn: ARN,
        iam_role_arn: IAMRoleArn,
        idempotency_token: string = None,
        lifecycle: Lifecycle = None,
    ) -> StartCopyJobOutput:
        """Starts a job to create a one-time copy of the specified resource.

        Does not support continuous backups.

        :param recovery_point_arn: An ARN that uniquely identifies a recovery point to use for the copy
        job; for example,
        arn:aws:backup:us-east-1:123456789012:recovery-point:1EB3B5E7-9EB0-435A-A80B-108B488B0D45.
        :param source_backup_vault_name: The name of a logical source container where backups are stored.
        :param destination_backup_vault_arn: An Amazon Resource Name (ARN) that uniquely identifies a destination
        backup vault to copy to; for example,
        ``arn:aws:backup:us-east-1:123456789012:vault:aBackupVault``.
        :param iam_role_arn: Specifies the IAM role ARN used to copy the target recovery point; for
        example, ``arn:aws:iam::123456789012:role/S3Access``.
        :param idempotency_token: A customer-chosen string that you can use to distinguish between
        otherwise identical calls to ``StartCopyJob``.
        :param lifecycle: Contains an array of ``Transition`` objects specifying how long in days
        before a recovery point transitions to cold storage or is deleted.
        :returns: StartCopyJobOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises LimitExceededException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("StartReportJob")
    def start_report_job(
        self,
        context: RequestContext,
        report_plan_name: ReportPlanName,
        idempotency_token: string = None,
    ) -> StartReportJobOutput:
        """Starts an on-demand report job for the specified report plan.

        :param report_plan_name: The unique name of a report plan.
        :param idempotency_token: A customer-chosen string that you can use to distinguish between
        otherwise identical calls to ``StartReportJobInput``.
        :returns: StartReportJobOutput
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        :raises MissingParameterValueException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("StartRestoreJob")
    def start_restore_job(
        self,
        context: RequestContext,
        recovery_point_arn: ARN,
        metadata: Metadata,
        iam_role_arn: IAMRoleArn,
        idempotency_token: string = None,
        resource_type: ResourceType = None,
    ) -> StartRestoreJobOutput:
        """Recovers the saved resource identified by an Amazon Resource Name (ARN).

        :param recovery_point_arn: An ARN that uniquely identifies a recovery point; for example,
        ``arn:aws:backup:us-east-1:123456789012:recovery-point:1EB3B5E7-9EB0-435A-A80B-108B488B0D45``.
        :param metadata: A set of metadata key-value pairs.
        :param iam_role_arn: The Amazon Resource Name (ARN) of the IAM role that Backup uses to
        create the target recovery point; for example,
        ``arn:aws:iam::123456789012:role/S3Access``.
        :param idempotency_token: A customer-chosen string that you can use to distinguish between
        otherwise identical calls to ``StartRestoreJob``.
        :param resource_type: Starts a job to restore a recovery point for one of the following
        resources:

        -  ``Aurora`` for Amazon Aurora

        -  ``DocumentDB`` for Amazon DocumentDB (with MongoDB compatibility)

        -  ``DynamoDB`` for Amazon DynamoDB

        -  ``EBS`` for Amazon Elastic Block Store

        -  ``EC2`` for Amazon Elastic Compute Cloud

        -  ``EFS`` for Amazon Elastic File System

        -  ``FSx`` for Amazon FSx

        -  ``Neptune`` for Amazon Neptune

        -  ``RDS`` for Amazon Relational Database Service

        -  ``Storage Gateway`` for Storage Gateway

        -  ``S3`` for Amazon S3

        -  ``VirtualMachine`` for virtual machines.
        :returns: StartRestoreJobOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("StopBackupJob")
    def stop_backup_job(self, context: RequestContext, backup_job_id: string) -> None:
        """Attempts to cancel a job to create a one-time backup of a resource.

        :param backup_job_id: Uniquely identifies a request to Backup to back up a resource.
        :raises MissingParameterValueException:
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises InvalidRequestException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(self, context: RequestContext, resource_arn: ARN, tags: Tags) -> None:
        """Assigns a set of key-value pairs to a recovery point, backup plan, or
        backup vault identified by an Amazon Resource Name (ARN).

        :param resource_arn: An ARN that uniquely identifies a resource.
        :param tags: Key-value pairs that are used to help organize your resources.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: ARN, tag_key_list: TagKeyList
    ) -> None:
        """Removes a set of key-value pairs from a recovery point, backup plan, or
        backup vault identified by an Amazon Resource Name (ARN)

        :param resource_arn: An ARN that uniquely identifies a resource.
        :param tag_key_list: A list of keys to identify which key-value tags to remove from a
        resource.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("UpdateBackupPlan")
    def update_backup_plan(
        self, context: RequestContext, backup_plan_id: string, backup_plan: BackupPlanInput
    ) -> UpdateBackupPlanOutput:
        """Updates an existing backup plan identified by its ``backupPlanId`` with
        the input document in JSON format. The new version is uniquely
        identified by a ``VersionId``.

        :param backup_plan_id: Uniquely identifies a backup plan.
        :param backup_plan: Specifies the body of a backup plan.
        :returns: UpdateBackupPlanOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("UpdateFramework")
    def update_framework(
        self,
        context: RequestContext,
        framework_name: FrameworkName,
        framework_description: FrameworkDescription = None,
        framework_controls: FrameworkControls = None,
        idempotency_token: string = None,
    ) -> UpdateFrameworkOutput:
        """Updates an existing framework identified by its ``FrameworkName`` with
        the input document in JSON format.

        :param framework_name: The unique name of a framework.
        :param framework_description: An optional description of the framework with a maximum 1,024
        characters.
        :param framework_controls: A list of the controls that make up the framework.
        :param idempotency_token: A customer-chosen string that you can use to distinguish between
        otherwise identical calls to ``UpdateFrameworkInput``.
        :returns: UpdateFrameworkOutput
        :raises AlreadyExistsException:
        :raises ResourceNotFoundException:
        :raises LimitExceededException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ConflictException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("UpdateGlobalSettings")
    def update_global_settings(
        self, context: RequestContext, global_settings: GlobalSettings = None
    ) -> None:
        """Updates whether the Amazon Web Services account is opted in to
        cross-account backup. Returns an error if the account is not an
        Organizations management account. Use the ``DescribeGlobalSettings`` API
        to determine the current settings.

        :param global_settings: A value for ``isCrossAccountBackupEnabled`` and a Region.
        :raises ServiceUnavailableException:
        :raises MissingParameterValueException:
        :raises InvalidParameterValueException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("UpdateRecoveryPointLifecycle")
    def update_recovery_point_lifecycle(
        self,
        context: RequestContext,
        backup_vault_name: BackupVaultName,
        recovery_point_arn: ARN,
        lifecycle: Lifecycle = None,
    ) -> UpdateRecoveryPointLifecycleOutput:
        """Sets the transition lifecycle of a recovery point.

        The lifecycle defines when a protected resource is transitioned to cold
        storage and when it expires. Backup transitions and expires backups
        automatically according to the lifecycle that you define.

        Backups transitioned to cold storage must be stored in cold storage for
        a minimum of 90 days. Therefore, the “retention” setting must be 90 days
        greater than the “transition to cold after days” setting. The
        “transition to cold after days” setting cannot be changed after a backup
        has been transitioned to cold.

        Only resource types that support full Backup management can transition
        their backups to cold storage. Those resource types are listed in the
        "Full Backup management" section of the `Feature availability by
        resource <https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html#features-by-resource>`__
        table. Backup ignores this expression for other resource types.

        This operation does not support continuous backups.

        :param backup_vault_name: The name of a logical container where backups are stored.
        :param recovery_point_arn: An Amazon Resource Name (ARN) that uniquely identifies a recovery point;
        for example,
        ``arn:aws:backup:us-east-1:123456789012:recovery-point:1EB3B5E7-9EB0-435A-A80B-108B488B0D45``.
        :param lifecycle: The lifecycle defines when a protected resource is transitioned to cold
        storage and when it expires.
        :returns: UpdateRecoveryPointLifecycleOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises InvalidRequestException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("UpdateRegionSettings")
    def update_region_settings(
        self,
        context: RequestContext,
        resource_type_opt_in_preference: ResourceTypeOptInPreference = None,
        resource_type_management_preference: ResourceTypeManagementPreference = None,
    ) -> None:
        """Updates the current service opt-in settings for the Region. If
        service-opt-in is enabled for a service, Backup tries to protect that
        service's resources in this Region, when the resource is included in an
        on-demand backup or scheduled backup plan. Otherwise, Backup does not
        try to protect that service's resources in this Region. Use the
        ``DescribeRegionSettings`` API to determine the resource types that are
        supported.

        :param resource_type_opt_in_preference: Updates the list of services along with the opt-in preferences for the
        Region.
        :param resource_type_management_preference: Enables or disables full Backup management of backups for a resource
        type.
        :raises ServiceUnavailableException:
        :raises MissingParameterValueException:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("UpdateReportPlan")
    def update_report_plan(
        self,
        context: RequestContext,
        report_plan_name: ReportPlanName,
        report_plan_description: ReportPlanDescription = None,
        report_delivery_channel: ReportDeliveryChannel = None,
        report_setting: ReportSetting = None,
        idempotency_token: string = None,
    ) -> UpdateReportPlanOutput:
        """Updates an existing report plan identified by its ``ReportPlanName``
        with the input document in JSON format.

        :param report_plan_name: The unique name of the report plan.
        :param report_plan_description: An optional description of the report plan with a maximum 1,024
        characters.
        :param report_delivery_channel: A structure that contains information about where to deliver your
        reports, specifically your Amazon S3 bucket name, S3 key prefix, and the
        formats of your reports.
        :param report_setting: Identifies the report template for the report.
        :param idempotency_token: A customer-chosen string that you can use to distinguish between
        otherwise identical calls to ``UpdateReportPlanInput``.
        :returns: UpdateReportPlanOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises ServiceUnavailableException:
        :raises MissingParameterValueException:
        :raises ConflictException:
        """
        raise NotImplementedError
