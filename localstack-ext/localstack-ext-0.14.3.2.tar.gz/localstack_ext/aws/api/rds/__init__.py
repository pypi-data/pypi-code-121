import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AwsBackupRecoveryPointArn = str
Boolean = bool
BooleanOptional = bool
BucketName = str
CustomDBEngineVersionManifest = str
CustomEngineName = str
CustomEngineVersion = str
DBClusterIdentifier = str
DBProxyEndpointName = str
DBProxyName = str
Description = str
Double = float
DoubleOptional = float
GlobalClusterIdentifier = str
Integer = int
IntegerOptional = int
KmsKeyIdOrArn = str
MaxRecords = int
String = str
String255 = str


class ActivityStreamMode(str):
    sync = "sync"
    async_ = "async"


class ActivityStreamStatus(str):
    stopped = "stopped"
    starting = "starting"
    started = "started"
    stopping = "stopping"


class ApplyMethod(str):
    immediate = "immediate"
    pending_reboot = "pending-reboot"


class AuthScheme(str):
    SECRETS = "SECRETS"


class AutomationMode(str):
    full = "full"
    all_paused = "all-paused"


class CustomEngineVersionStatus(str):
    available = "available"
    inactive = "inactive"
    inactive_except_restore = "inactive-except-restore"


class DBProxyEndpointStatus(str):
    available = "available"
    modifying = "modifying"
    incompatible_network = "incompatible-network"
    insufficient_resource_limits = "insufficient-resource-limits"
    creating = "creating"
    deleting = "deleting"


class DBProxyEndpointTargetRole(str):
    READ_WRITE = "READ_WRITE"
    READ_ONLY = "READ_ONLY"


class DBProxyStatus(str):
    available = "available"
    modifying = "modifying"
    incompatible_network = "incompatible-network"
    insufficient_resource_limits = "insufficient-resource-limits"
    creating = "creating"
    deleting = "deleting"
    suspended = "suspended"
    suspending = "suspending"
    reactivating = "reactivating"


class EngineFamily(str):
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"


class FailoverStatus(str):
    pending = "pending"
    failing_over = "failing-over"
    cancelling = "cancelling"


class IAMAuthMode(str):
    DISABLED = "DISABLED"
    REQUIRED = "REQUIRED"


class ReplicaMode(str):
    open_read_only = "open-read-only"
    mounted = "mounted"


class SourceType(str):
    db_instance = "db-instance"
    db_parameter_group = "db-parameter-group"
    db_security_group = "db-security-group"
    db_snapshot = "db-snapshot"
    db_cluster = "db-cluster"
    db_cluster_snapshot = "db-cluster-snapshot"
    custom_engine_version = "custom-engine-version"
    db_proxy = "db-proxy"


class TargetHealthReason(str):
    UNREACHABLE = "UNREACHABLE"
    CONNECTION_FAILED = "CONNECTION_FAILED"
    AUTH_FAILURE = "AUTH_FAILURE"
    PENDING_PROXY_CAPACITY = "PENDING_PROXY_CAPACITY"
    INVALID_REPLICATION_STATE = "INVALID_REPLICATION_STATE"


class TargetRole(str):
    READ_WRITE = "READ_WRITE"
    READ_ONLY = "READ_ONLY"
    UNKNOWN = "UNKNOWN"


class TargetState(str):
    REGISTERING = "REGISTERING"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class TargetType(str):
    RDS_INSTANCE = "RDS_INSTANCE"
    RDS_SERVERLESS_ENDPOINT = "RDS_SERVERLESS_ENDPOINT"
    TRACKED_CLUSTER = "TRACKED_CLUSTER"


class WriteForwardingStatus(str):
    enabled = "enabled"
    disabled = "disabled"
    enabling = "enabling"
    disabling = "disabling"
    unknown = "unknown"


class AuthorizationAlreadyExistsFault(ServiceException):
    """The specified CIDR IP range or Amazon EC2 security group is already
    authorized for the specified DB security group.
    """


class AuthorizationNotFoundFault(ServiceException):
    """The specified CIDR IP range or Amazon EC2 security group might not be
    authorized for the specified DB security group.

    Or, RDS might not be authorized to perform necessary actions using IAM
    on your behalf.
    """


class AuthorizationQuotaExceededFault(ServiceException):
    """The DB security group authorization quota has been reached."""


class BackupPolicyNotFoundFault(ServiceException):
    pass


class CertificateNotFoundFault(ServiceException):
    """``CertificateIdentifier`` doesn't refer to an existing certificate."""


class CustomAvailabilityZoneNotFoundFault(ServiceException):
    """``CustomAvailabilityZoneId`` doesn't refer to an existing custom
    Availability Zone identifier.
    """


class CustomDBEngineVersionAlreadyExistsFault(ServiceException):
    """A CEV with the specified name already exists."""


class CustomDBEngineVersionNotFoundFault(ServiceException):
    """The specified CEV was not found."""


class CustomDBEngineVersionQuotaExceededFault(ServiceException):
    """You have exceeded your CEV quota."""


class DBClusterAlreadyExistsFault(ServiceException):
    """The user already has a DB cluster with the given identifier."""


class DBClusterBacktrackNotFoundFault(ServiceException):
    """``BacktrackIdentifier`` doesn't refer to an existing backtrack."""


class DBClusterEndpointAlreadyExistsFault(ServiceException):
    """The specified custom endpoint can't be created because it already
    exists.
    """


class DBClusterEndpointNotFoundFault(ServiceException):
    """The specified custom endpoint doesn't exist."""


class DBClusterEndpointQuotaExceededFault(ServiceException):
    """The cluster already has the maximum number of custom endpoints."""


class DBClusterNotFoundFault(ServiceException):
    """``DBClusterIdentifier`` doesn't refer to an existing DB cluster."""


class DBClusterParameterGroupNotFoundFault(ServiceException):
    """``DBClusterParameterGroupName`` doesn't refer to an existing DB cluster
    parameter group.
    """


class DBClusterQuotaExceededFault(ServiceException):
    """The user attempted to create a new DB cluster and the user has already
    reached the maximum allowed DB cluster quota.
    """


class DBClusterRoleAlreadyExistsFault(ServiceException):
    """The specified IAM role Amazon Resource Name (ARN) is already associated
    with the specified DB cluster.
    """


class DBClusterRoleNotFoundFault(ServiceException):
    """The specified IAM role Amazon Resource Name (ARN) isn't associated with
    the specified DB cluster.
    """


class DBClusterRoleQuotaExceededFault(ServiceException):
    """You have exceeded the maximum number of IAM roles that can be associated
    with the specified DB cluster.
    """


class DBClusterSnapshotAlreadyExistsFault(ServiceException):
    """The user already has a DB cluster snapshot with the given identifier."""


class DBClusterSnapshotNotFoundFault(ServiceException):
    """``DBClusterSnapshotIdentifier`` doesn't refer to an existing DB cluster
    snapshot.
    """


class DBInstanceAlreadyExistsFault(ServiceException):
    """The user already has a DB instance with the given identifier."""


class DBInstanceAutomatedBackupNotFoundFault(ServiceException):
    """No automated backup for this DB instance was found."""


class DBInstanceAutomatedBackupQuotaExceededFault(ServiceException):
    """The quota for retained automated backups was exceeded. This prevents you
    from retaining any additional automated backups. The retained automated
    backups quota is the same as your DB Instance quota.
    """


class DBInstanceNotFoundFault(ServiceException):
    """``DBInstanceIdentifier`` doesn't refer to an existing DB instance."""


class DBInstanceRoleAlreadyExistsFault(ServiceException):
    """The specified ``RoleArn`` or ``FeatureName`` value is already associated
    with the DB instance.
    """


class DBInstanceRoleNotFoundFault(ServiceException):
    """The specified ``RoleArn`` value doesn't match the specified feature for
    the DB instance.
    """


class DBInstanceRoleQuotaExceededFault(ServiceException):
    """You can't associate any more Amazon Web Services Identity and Access
    Management (IAM) roles with the DB instance because the quota has been
    reached.
    """


class DBLogFileNotFoundFault(ServiceException):
    """``LogFileName`` doesn't refer to an existing DB log file."""


class DBParameterGroupAlreadyExistsFault(ServiceException):
    """A DB parameter group with the same name exists."""


class DBParameterGroupNotFoundFault(ServiceException):
    """``DBParameterGroupName`` doesn't refer to an existing DB parameter
    group.
    """


class DBParameterGroupQuotaExceededFault(ServiceException):
    """The request would result in the user exceeding the allowed number of DB
    parameter groups.
    """


class DBProxyAlreadyExistsFault(ServiceException):
    """The specified proxy name must be unique for all proxies owned by your
    Amazon Web Services account in the specified Amazon Web Services Region.
    """


class DBProxyEndpointAlreadyExistsFault(ServiceException):
    """The specified DB proxy endpoint name must be unique for all DB proxy
    endpoints owned by your Amazon Web Services account in the specified
    Amazon Web Services Region.
    """


class DBProxyEndpointNotFoundFault(ServiceException):
    """The DB proxy endpoint doesn't exist."""


class DBProxyEndpointQuotaExceededFault(ServiceException):
    """The DB proxy already has the maximum number of endpoints."""


class DBProxyNotFoundFault(ServiceException):
    """The specified proxy name doesn't correspond to a proxy owned by your
    Amazon Web Services account in the specified Amazon Web Services Region.
    """


class DBProxyQuotaExceededFault(ServiceException):
    """Your Amazon Web Services account already has the maximum number of
    proxies in the specified Amazon Web Services Region.
    """


class DBProxyTargetAlreadyRegisteredFault(ServiceException):
    """The proxy is already associated with the specified RDS DB instance or
    Aurora DB cluster.
    """


class DBProxyTargetGroupNotFoundFault(ServiceException):
    """The specified target group isn't available for a proxy owned by your
    Amazon Web Services account in the specified Amazon Web Services Region.
    """


class DBProxyTargetNotFoundFault(ServiceException):
    """The specified RDS DB instance or Aurora DB cluster isn't available for a
    proxy owned by your Amazon Web Services account in the specified Amazon
    Web Services Region.
    """


class DBSecurityGroupAlreadyExistsFault(ServiceException):
    """A DB security group with the name specified in ``DBSecurityGroupName``
    already exists.
    """


class DBSecurityGroupNotFoundFault(ServiceException):
    """``DBSecurityGroupName`` doesn't refer to an existing DB security group."""


class DBSecurityGroupNotSupportedFault(ServiceException):
    """A DB security group isn't allowed for this action."""


class DBSecurityGroupQuotaExceededFault(ServiceException):
    """The request would result in the user exceeding the allowed number of DB
    security groups.
    """


class DBSnapshotAlreadyExistsFault(ServiceException):
    """``DBSnapshotIdentifier`` is already used by an existing snapshot."""


class DBSnapshotNotFoundFault(ServiceException):
    """``DBSnapshotIdentifier`` doesn't refer to an existing DB snapshot."""


class DBSubnetGroupAlreadyExistsFault(ServiceException):
    """``DBSubnetGroupName`` is already used by an existing DB subnet group."""


class DBSubnetGroupDoesNotCoverEnoughAZs(ServiceException):
    """Subnets in the DB subnet group should cover at least two Availability
    Zones unless there is only one Availability Zone.
    """


class DBSubnetGroupNotAllowedFault(ServiceException):
    """The DBSubnetGroup shouldn't be specified while creating read replicas
    that lie in the same region as the source instance.
    """


class DBSubnetGroupNotFoundFault(ServiceException):
    """``DBSubnetGroupName`` doesn't refer to an existing DB subnet group."""


class DBSubnetGroupQuotaExceededFault(ServiceException):
    """The request would result in the user exceeding the allowed number of DB
    subnet groups.
    """


class DBSubnetQuotaExceededFault(ServiceException):
    """The request would result in the user exceeding the allowed number of
    subnets in a DB subnet groups.
    """


class DBUpgradeDependencyFailureFault(ServiceException):
    """The DB upgrade failed because a resource the DB depends on can't be
    modified.
    """


class DomainNotFoundFault(ServiceException):
    """``Domain`` doesn't refer to an existing Active Directory domain."""


class EventSubscriptionQuotaExceededFault(ServiceException):
    """You have reached the maximum number of event subscriptions."""


class ExportTaskAlreadyExistsFault(ServiceException):
    """You can't start an export task that's already running."""


class ExportTaskNotFoundFault(ServiceException):
    """The export task doesn't exist."""


class GlobalClusterAlreadyExistsFault(ServiceException):
    """The ``GlobalClusterIdentifier`` already exists. Choose a new global
    database identifier (unique name) to create a new global database
    cluster.
    """


class GlobalClusterNotFoundFault(ServiceException):
    """The ``GlobalClusterIdentifier`` doesn't refer to an existing global
    database cluster.
    """


class GlobalClusterQuotaExceededFault(ServiceException):
    """The number of global database clusters for this account is already at
    the maximum allowed.
    """


class IamRoleMissingPermissionsFault(ServiceException):
    """The IAM role requires additional permissions to export to an Amazon S3
    bucket.
    """


class IamRoleNotFoundFault(ServiceException):
    """The IAM role is missing for exporting to an Amazon S3 bucket."""


class InstanceQuotaExceededFault(ServiceException):
    """The request would result in the user exceeding the allowed number of DB
    instances.
    """


class InsufficientAvailableIPsInSubnetFault(ServiceException):
    """The requested operation can't be performed because there aren't enough
    available IP addresses in the proxy's subnets. Add more CIDR blocks to
    the VPC or remove IP address that aren't required from the subnets.
    """


class InsufficientDBClusterCapacityFault(ServiceException):
    """The DB cluster doesn't have enough capacity for the current operation."""


class InsufficientDBInstanceCapacityFault(ServiceException):
    """The specified DB instance class isn't available in the specified
    Availability Zone.
    """


class InsufficientStorageClusterCapacityFault(ServiceException):
    """There is insufficient storage available for the current action. You
    might be able to resolve this error by updating your subnet group to use
    different Availability Zones that have more storage available.
    """


class InvalidCustomDBEngineVersionStateFault(ServiceException):
    """You can't delete the CEV."""


class InvalidDBClusterCapacityFault(ServiceException):
    """``Capacity`` isn't a valid Aurora Serverless DB cluster capacity. Valid
    capacity values are ``2``, ``4``, ``8``, ``16``, ``32``, ``64``,
    ``128``, and ``256``.
    """


class InvalidDBClusterEndpointStateFault(ServiceException):
    """The requested operation can't be performed on the endpoint while the
    endpoint is in this state.
    """


class InvalidDBClusterSnapshotStateFault(ServiceException):
    """The supplied value isn't a valid DB cluster snapshot state."""


class InvalidDBClusterStateFault(ServiceException):
    """The requested operation can't be performed while the cluster is in this
    state.
    """


class InvalidDBInstanceAutomatedBackupStateFault(ServiceException):
    """The automated backup is in an invalid state. For example, this automated
    backup is associated with an active instance.
    """


class InvalidDBInstanceStateFault(ServiceException):
    """The DB instance isn't in a valid state."""


class InvalidDBParameterGroupStateFault(ServiceException):
    """The DB parameter group is in use or is in an invalid state. If you are
    attempting to delete the parameter group, you can't delete it when the
    parameter group is in this state.
    """


class InvalidDBProxyEndpointStateFault(ServiceException):
    """You can't perform this operation while the DB proxy endpoint is in a
    particular state.
    """


class InvalidDBProxyStateFault(ServiceException):
    """The requested operation can't be performed while the proxy is in this
    state.
    """


class InvalidDBSecurityGroupStateFault(ServiceException):
    """The state of the DB security group doesn't allow deletion."""


class InvalidDBSnapshotStateFault(ServiceException):
    """The state of the DB snapshot doesn't allow deletion."""


class InvalidDBSubnetGroupFault(ServiceException):
    """The DBSubnetGroup doesn't belong to the same VPC as that of an existing
    cross-region read replica of the same source instance.
    """


class InvalidDBSubnetGroupStateFault(ServiceException):
    """The DB subnet group cannot be deleted because it's in use."""


class InvalidDBSubnetStateFault(ServiceException):
    """The DB subnet isn't in the *available* state."""


class InvalidEventSubscriptionStateFault(ServiceException):
    """This error can occur if someone else is modifying a subscription. You
    should retry the action.
    """


class InvalidExportOnlyFault(ServiceException):
    """The export is invalid for exporting to an Amazon S3 bucket."""


class InvalidExportSourceStateFault(ServiceException):
    """The state of the export snapshot is invalid for exporting to an Amazon
    S3 bucket.
    """


class InvalidExportTaskStateFault(ServiceException):
    """You can't cancel an export task that has completed."""


class InvalidGlobalClusterStateFault(ServiceException):
    """The global cluster is in an invalid state and can't perform the
    requested operation.
    """


class InvalidOptionGroupStateFault(ServiceException):
    """The option group isn't in the *available* state."""


class InvalidRestoreFault(ServiceException):
    """Cannot restore from VPC backup to non-VPC DB instance."""


class InvalidS3BucketFault(ServiceException):
    """The specified Amazon S3 bucket name can't be found or Amazon RDS isn't
    authorized to access the specified Amazon S3 bucket. Verify the
    **SourceS3BucketName** and **S3IngestionRoleArn** values and try again.
    """


class InvalidSubnet(ServiceException):
    """The requested subnet is invalid, or multiple subnets were requested that
    are not all in a common VPC.
    """


class InvalidVPCNetworkStateFault(ServiceException):
    """The DB subnet group doesn't cover all Availability Zones after it's
    created because of users' change.
    """


class KMSKeyNotAccessibleFault(ServiceException):
    """An error occurred accessing an Amazon Web Services KMS key."""


class NetworkTypeNotSupported(ServiceException):
    """The network type is invalid for the DB instance. Valid nework type
    values are ``IPV4`` and ``DUAL``.
    """


class OptionGroupAlreadyExistsFault(ServiceException):
    """The option group you are trying to create already exists."""


class OptionGroupNotFoundFault(ServiceException):
    """The specified option group could not be found."""


class OptionGroupQuotaExceededFault(ServiceException):
    """The quota of 20 option groups was exceeded for this Amazon Web Services
    account.
    """


class PointInTimeRestoreNotEnabledFault(ServiceException):
    """``SourceDBInstanceIdentifier`` refers to a DB instance with
    ``BackupRetentionPeriod`` equal to 0.
    """


class ProvisionedIopsNotAvailableInAZFault(ServiceException):
    """Provisioned IOPS not available in the specified Availability Zone."""


class ReservedDBInstanceAlreadyExistsFault(ServiceException):
    """User already has a reservation with the given identifier."""


class ReservedDBInstanceNotFoundFault(ServiceException):
    """The specified reserved DB Instance not found."""


class ReservedDBInstanceQuotaExceededFault(ServiceException):
    """Request would exceed the user's DB Instance quota."""


class ReservedDBInstancesOfferingNotFoundFault(ServiceException):
    """Specified offering does not exist."""


class ResourceNotFoundFault(ServiceException):
    """The specified resource ID was not found."""


class SNSInvalidTopicFault(ServiceException):
    """SNS has responded that there is a problem with the SNS topic specified."""


class SNSNoAuthorizationFault(ServiceException):
    """You do not have permission to publish to the SNS topic ARN."""


class SNSTopicArnNotFoundFault(ServiceException):
    """The SNS topic ARN does not exist."""


class SharedSnapshotQuotaExceededFault(ServiceException):
    """You have exceeded the maximum number of accounts that you can share a
    manual DB snapshot with.
    """


class SnapshotQuotaExceededFault(ServiceException):
    """The request would result in the user exceeding the allowed number of DB
    snapshots.
    """


class SourceNotFoundFault(ServiceException):
    """The requested source could not be found."""


class StorageQuotaExceededFault(ServiceException):
    """The request would result in the user exceeding the allowed amount of
    storage available across all DB instances.
    """


class StorageTypeNotSupportedFault(ServiceException):
    """Storage of the ``StorageType`` specified can't be associated with the DB
    instance.
    """


class SubnetAlreadyInUse(ServiceException):
    """The DB subnet is already in use in the Availability Zone."""


class SubscriptionAlreadyExistFault(ServiceException):
    """The supplied subscription name already exists."""


class SubscriptionCategoryNotFoundFault(ServiceException):
    """The supplied category does not exist."""


class SubscriptionNotFoundFault(ServiceException):
    """The subscription name does not exist."""


Long = int


class AccountQuota(TypedDict, total=False):
    """Describes a quota for an Amazon Web Services account.

    The following are account quotas:

    -  ``AllocatedStorage`` - The total allocated storage per account, in
       GiB. The used value is the total allocated storage in the account, in
       GiB.

    -  ``AuthorizationsPerDBSecurityGroup`` - The number of ingress rules
       per DB security group. The used value is the highest number of
       ingress rules in a DB security group in the account. Other DB
       security groups in the account might have a lower number of ingress
       rules.

    -  ``CustomEndpointsPerDBCluster`` - The number of custom endpoints per
       DB cluster. The used value is the highest number of custom endpoints
       in a DB clusters in the account. Other DB clusters in the account
       might have a lower number of custom endpoints.

    -  ``DBClusterParameterGroups`` - The number of DB cluster parameter
       groups per account, excluding default parameter groups. The used
       value is the count of nondefault DB cluster parameter groups in the
       account.

    -  ``DBClusterRoles`` - The number of associated Amazon Web Services
       Identity and Access Management (IAM) roles per DB cluster. The used
       value is the highest number of associated IAM roles for a DB cluster
       in the account. Other DB clusters in the account might have a lower
       number of associated IAM roles.

    -  ``DBClusters`` - The number of DB clusters per account. The used
       value is the count of DB clusters in the account.

    -  ``DBInstanceRoles`` - The number of associated IAM roles per DB
       instance. The used value is the highest number of associated IAM
       roles for a DB instance in the account. Other DB instances in the
       account might have a lower number of associated IAM roles.

    -  ``DBInstances`` - The number of DB instances per account. The used
       value is the count of the DB instances in the account.

       Amazon RDS DB instances, Amazon Aurora DB instances, Amazon Neptune
       instances, and Amazon DocumentDB instances apply to this quota.

    -  ``DBParameterGroups`` - The number of DB parameter groups per
       account, excluding default parameter groups. The used value is the
       count of nondefault DB parameter groups in the account.

    -  ``DBSecurityGroups`` - The number of DB security groups (not VPC
       security groups) per account, excluding the default security group.
       The used value is the count of nondefault DB security groups in the
       account.

    -  ``DBSubnetGroups`` - The number of DB subnet groups per account. The
       used value is the count of the DB subnet groups in the account.

    -  ``EventSubscriptions`` - The number of event subscriptions per
       account. The used value is the count of the event subscriptions in
       the account.

    -  ``ManualClusterSnapshots`` - The number of manual DB cluster
       snapshots per account. The used value is the count of the manual DB
       cluster snapshots in the account.

    -  ``ManualSnapshots`` - The number of manual DB instance snapshots per
       account. The used value is the count of the manual DB instance
       snapshots in the account.

    -  ``OptionGroups`` - The number of DB option groups per account,
       excluding default option groups. The used value is the count of
       nondefault DB option groups in the account.

    -  ``ReadReplicasPerMaster`` - The number of read replicas per DB
       instance. The used value is the highest number of read replicas for a
       DB instance in the account. Other DB instances in the account might
       have a lower number of read replicas.

    -  ``ReservedDBInstances`` - The number of reserved DB instances per
       account. The used value is the count of the active reserved DB
       instances in the account.

    -  ``SubnetsPerDBSubnetGroup`` - The number of subnets per DB subnet
       group. The used value is highest number of subnets for a DB subnet
       group in the account. Other DB subnet groups in the account might
       have a lower number of subnets.

    For more information, see `Quotas for Amazon
    RDS <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html>`__
    in the *Amazon RDS User Guide* and `Quotas for Amazon
    Aurora <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_Limits.html>`__
    in the *Amazon Aurora User Guide*.
    """

    AccountQuotaName: Optional[String]
    Used: Optional[Long]
    Max: Optional[Long]


AccountQuotaList = List[AccountQuota]


class AccountAttributesMessage(TypedDict, total=False):
    """Data returned by the **DescribeAccountAttributes** action."""

    AccountQuotas: Optional[AccountQuotaList]


ActivityStreamModeList = List[String]


class AddRoleToDBClusterMessage(ServiceRequest):
    DBClusterIdentifier: String
    RoleArn: String
    FeatureName: Optional[String]


class AddRoleToDBInstanceMessage(ServiceRequest):
    DBInstanceIdentifier: String
    RoleArn: String
    FeatureName: String


class AddSourceIdentifierToSubscriptionMessage(ServiceRequest):
    SubscriptionName: String
    SourceIdentifier: String


EventCategoriesList = List[String]
SourceIdsList = List[String]


class EventSubscription(TypedDict, total=False):
    """Contains the results of a successful invocation of the
    ``DescribeEventSubscriptions`` action.
    """

    CustomerAwsId: Optional[String]
    CustSubscriptionId: Optional[String]
    SnsTopicArn: Optional[String]
    Status: Optional[String]
    SubscriptionCreationTime: Optional[String]
    SourceType: Optional[String]
    SourceIdsList: Optional[SourceIdsList]
    EventCategoriesList: Optional[EventCategoriesList]
    Enabled: Optional[Boolean]
    EventSubscriptionArn: Optional[String]


class AddSourceIdentifierToSubscriptionResult(TypedDict, total=False):
    EventSubscription: Optional[EventSubscription]


class Tag(TypedDict, total=False):
    """Metadata assigned to an Amazon RDS resource consisting of a key-value
    pair.
    """

    Key: Optional[String]
    Value: Optional[String]


TagList = List[Tag]


class AddTagsToResourceMessage(ServiceRequest):
    ResourceName: String
    Tags: TagList


class ApplyPendingMaintenanceActionMessage(ServiceRequest):
    ResourceIdentifier: String
    ApplyAction: String
    OptInType: String


TStamp = datetime


class PendingMaintenanceAction(TypedDict, total=False):
    """Provides information about a pending maintenance action for a resource."""

    Action: Optional[String]
    AutoAppliedAfterDate: Optional[TStamp]
    ForcedApplyDate: Optional[TStamp]
    OptInStatus: Optional[String]
    CurrentApplyDate: Optional[TStamp]
    Description: Optional[String]


PendingMaintenanceActionDetails = List[PendingMaintenanceAction]


class ResourcePendingMaintenanceActions(TypedDict, total=False):
    """Describes the pending maintenance actions for a resource."""

    ResourceIdentifier: Optional[String]
    PendingMaintenanceActionDetails: Optional[PendingMaintenanceActionDetails]


class ApplyPendingMaintenanceActionResult(TypedDict, total=False):
    ResourcePendingMaintenanceActions: Optional[ResourcePendingMaintenanceActions]


AttributeValueList = List[String]


class AuthorizeDBSecurityGroupIngressMessage(ServiceRequest):
    DBSecurityGroupName: String
    CIDRIP: Optional[String]
    EC2SecurityGroupName: Optional[String]
    EC2SecurityGroupId: Optional[String]
    EC2SecurityGroupOwnerId: Optional[String]


class IPRange(TypedDict, total=False):
    """This data type is used as a response element in the
    ``DescribeDBSecurityGroups`` action.
    """

    Status: Optional[String]
    CIDRIP: Optional[String]


IPRangeList = List[IPRange]


class EC2SecurityGroup(TypedDict, total=False):
    """This data type is used as a response element in the following actions:

    -  ``AuthorizeDBSecurityGroupIngress``

    -  ``DescribeDBSecurityGroups``

    -  ``RevokeDBSecurityGroupIngress``
    """

    Status: Optional[String]
    EC2SecurityGroupName: Optional[String]
    EC2SecurityGroupId: Optional[String]
    EC2SecurityGroupOwnerId: Optional[String]


EC2SecurityGroupList = List[EC2SecurityGroup]


class DBSecurityGroup(TypedDict, total=False):
    """Contains the details for an Amazon RDS DB security group.

    This data type is used as a response element in the
    ``DescribeDBSecurityGroups`` action.
    """

    OwnerId: Optional[String]
    DBSecurityGroupName: Optional[String]
    DBSecurityGroupDescription: Optional[String]
    VpcId: Optional[String]
    EC2SecurityGroups: Optional[EC2SecurityGroupList]
    IPRanges: Optional[IPRangeList]
    DBSecurityGroupArn: Optional[String]


class AuthorizeDBSecurityGroupIngressResult(TypedDict, total=False):
    DBSecurityGroup: Optional[DBSecurityGroup]


class AvailabilityZone(TypedDict, total=False):
    """Contains Availability Zone information.

    This data type is used as an element in the
    ``OrderableDBInstanceOption`` data type.
    """

    Name: Optional[String]


AvailabilityZoneList = List[AvailabilityZone]
AvailabilityZones = List[String]


class AvailableProcessorFeature(TypedDict, total=False):
    """Contains the available processor feature information for the DB instance
    class of a DB instance.

    For more information, see `Configuring the Processor of the DB Instance
    Class <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor>`__
    in the *Amazon RDS User Guide.*
    """

    Name: Optional[String]
    DefaultValue: Optional[String]
    AllowedValues: Optional[String]


AvailableProcessorFeatureList = List[AvailableProcessorFeature]


class BacktrackDBClusterMessage(ServiceRequest):
    DBClusterIdentifier: String
    BacktrackTo: TStamp
    Force: Optional[BooleanOptional]
    UseEarliestTimeOnPointInTimeUnavailable: Optional[BooleanOptional]


class CancelExportTaskMessage(ServiceRequest):
    ExportTaskIdentifier: String


class Certificate(TypedDict, total=False):
    """A CA certificate for an Amazon Web Services account."""

    CertificateIdentifier: Optional[String]
    CertificateType: Optional[String]
    Thumbprint: Optional[String]
    ValidFrom: Optional[TStamp]
    ValidTill: Optional[TStamp]
    CertificateArn: Optional[String]
    CustomerOverride: Optional[BooleanOptional]
    CustomerOverrideValidTill: Optional[TStamp]


CertificateList = List[Certificate]


class CertificateMessage(TypedDict, total=False):
    """Data returned by the **DescribeCertificates** action."""

    Certificates: Optional[CertificateList]
    Marker: Optional[String]


class CharacterSet(TypedDict, total=False):
    """This data type is used as a response element in the action
    ``DescribeDBEngineVersions``.
    """

    CharacterSetName: Optional[String]
    CharacterSetDescription: Optional[String]


LogTypeList = List[String]


class CloudwatchLogsExportConfiguration(TypedDict, total=False):
    """The configuration setting for the log types to be enabled for export to
    CloudWatch Logs for a specific DB instance or DB cluster.

    The ``EnableLogTypes`` and ``DisableLogTypes`` arrays determine which
    logs will be exported (or not exported) to CloudWatch Logs. The values
    within these arrays depend on the DB engine being used.

    For more information about exporting CloudWatch Logs for Amazon RDS DB
    instances, see `Publishing Database Logs to Amazon CloudWatch
    Logs <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.html#USER_LogAccess.Procedural.UploadtoCloudWatch>`__
    in the *Amazon RDS User Guide*.

    For more information about exporting CloudWatch Logs for Amazon Aurora
    DB clusters, see `Publishing Database Logs to Amazon CloudWatch
    Logs <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_LogAccess.html#USER_LogAccess.Procedural.UploadtoCloudWatch>`__
    in the *Amazon Aurora User Guide*.
    """

    EnableLogTypes: Optional[LogTypeList]
    DisableLogTypes: Optional[LogTypeList]


class PendingCloudwatchLogsExports(TypedDict, total=False):
    """A list of the log types whose configuration is still pending. In other
    words, these log types are in the process of being activated or
    deactivated.
    """

    LogTypesToEnable: Optional[LogTypeList]
    LogTypesToDisable: Optional[LogTypeList]


class ClusterPendingModifiedValues(TypedDict, total=False):
    """This data type is used as a response element in the ``ModifyDBCluster``
    operation and contains changes that will be applied during the next
    maintenance window.
    """

    PendingCloudwatchLogsExports: Optional[PendingCloudwatchLogsExports]
    DBClusterIdentifier: Optional[String]
    MasterUserPassword: Optional[String]
    IAMDatabaseAuthenticationEnabled: Optional[BooleanOptional]
    EngineVersion: Optional[String]


StringList = List[String]


class ConnectionPoolConfiguration(TypedDict, total=False):
    """Specifies the settings that control the size and behavior of the
    connection pool associated with a ``DBProxyTargetGroup``.
    """

    MaxConnectionsPercent: Optional[IntegerOptional]
    MaxIdleConnectionsPercent: Optional[IntegerOptional]
    ConnectionBorrowTimeout: Optional[IntegerOptional]
    SessionPinningFilters: Optional[StringList]
    InitQuery: Optional[String]


class ConnectionPoolConfigurationInfo(TypedDict, total=False):
    """Displays the settings that control the size and behavior of the
    connection pool associated with a ``DBProxyTarget``.
    """

    MaxConnectionsPercent: Optional[Integer]
    MaxIdleConnectionsPercent: Optional[Integer]
    ConnectionBorrowTimeout: Optional[Integer]
    SessionPinningFilters: Optional[StringList]
    InitQuery: Optional[String]


class CopyDBClusterParameterGroupMessage(ServiceRequest):
    SourceDBClusterParameterGroupIdentifier: String
    TargetDBClusterParameterGroupIdentifier: String
    TargetDBClusterParameterGroupDescription: String
    Tags: Optional[TagList]


class DBClusterParameterGroup(TypedDict, total=False):
    """Contains the details of an Amazon RDS DB cluster parameter group.

    This data type is used as a response element in the
    ``DescribeDBClusterParameterGroups`` action.
    """

    DBClusterParameterGroupName: Optional[String]
    DBParameterGroupFamily: Optional[String]
    Description: Optional[String]
    DBClusterParameterGroupArn: Optional[String]


class CopyDBClusterParameterGroupResult(TypedDict, total=False):
    DBClusterParameterGroup: Optional[DBClusterParameterGroup]


class CopyDBClusterSnapshotMessage(ServiceRequest):
    SourceDBClusterSnapshotIdentifier: String
    TargetDBClusterSnapshotIdentifier: String
    KmsKeyId: Optional[String]
    PreSignedUrl: Optional[String]
    CopyTags: Optional[BooleanOptional]
    Tags: Optional[TagList]
    SourceRegion: Optional[String]


class DBClusterSnapshot(TypedDict, total=False):
    """Contains the details for an Amazon RDS DB cluster snapshot

    This data type is used as a response element in the
    ``DescribeDBClusterSnapshots`` action.
    """

    AvailabilityZones: Optional[AvailabilityZones]
    DBClusterSnapshotIdentifier: Optional[String]
    DBClusterIdentifier: Optional[String]
    SnapshotCreateTime: Optional[TStamp]
    Engine: Optional[String]
    EngineMode: Optional[String]
    AllocatedStorage: Optional[Integer]
    Status: Optional[String]
    Port: Optional[Integer]
    VpcId: Optional[String]
    ClusterCreateTime: Optional[TStamp]
    MasterUsername: Optional[String]
    EngineVersion: Optional[String]
    LicenseModel: Optional[String]
    SnapshotType: Optional[String]
    PercentProgress: Optional[Integer]
    StorageEncrypted: Optional[Boolean]
    KmsKeyId: Optional[String]
    DBClusterSnapshotArn: Optional[String]
    SourceDBClusterSnapshotArn: Optional[String]
    IAMDatabaseAuthenticationEnabled: Optional[Boolean]
    TagList: Optional[TagList]


class CopyDBClusterSnapshotResult(TypedDict, total=False):
    DBClusterSnapshot: Optional[DBClusterSnapshot]


class CopyDBParameterGroupMessage(ServiceRequest):
    SourceDBParameterGroupIdentifier: String
    TargetDBParameterGroupIdentifier: String
    TargetDBParameterGroupDescription: String
    Tags: Optional[TagList]


class DBParameterGroup(TypedDict, total=False):
    """Contains the details of an Amazon RDS DB parameter group.

    This data type is used as a response element in the
    ``DescribeDBParameterGroups`` action.
    """

    DBParameterGroupName: Optional[String]
    DBParameterGroupFamily: Optional[String]
    Description: Optional[String]
    DBParameterGroupArn: Optional[String]


class CopyDBParameterGroupResult(TypedDict, total=False):
    DBParameterGroup: Optional[DBParameterGroup]


class CopyDBSnapshotMessage(ServiceRequest):
    SourceDBSnapshotIdentifier: String
    TargetDBSnapshotIdentifier: String
    KmsKeyId: Optional[String]
    Tags: Optional[TagList]
    CopyTags: Optional[BooleanOptional]
    PreSignedUrl: Optional[String]
    OptionGroupName: Optional[String]
    TargetCustomAvailabilityZone: Optional[String]
    SourceRegion: Optional[String]


class ProcessorFeature(TypedDict, total=False):
    """Contains the processor features of a DB instance class.

    To specify the number of CPU cores, use the ``coreCount`` feature name
    for the ``Name`` parameter. To specify the number of threads per core,
    use the ``threadsPerCore`` feature name for the ``Name`` parameter.

    You can set the processor features of the DB instance class for a DB
    instance when you call one of the following actions:

    -  ``CreateDBInstance``

    -  ``ModifyDBInstance``

    -  ``RestoreDBInstanceFromDBSnapshot``

    -  ``RestoreDBInstanceFromS3``

    -  ``RestoreDBInstanceToPointInTime``

    You can view the valid processor values for a particular instance class
    by calling the ``DescribeOrderableDBInstanceOptions`` action and
    specifying the instance class for the ``DBInstanceClass`` parameter.

    In addition, you can use the following actions for DB instance class
    processor information:

    -  ``DescribeDBInstances``

    -  ``DescribeDBSnapshots``

    -  ``DescribeValidDBInstanceModifications``

    If you call ``DescribeDBInstances``, ``ProcessorFeature`` returns
    non-null values only if the following conditions are met:

    -  You are accessing an Oracle DB instance.

    -  Your Oracle DB instance class supports configuring the number of CPU
       cores and threads per core.

    -  The current number CPU cores and threads is set to a non-default
       value.

    For more information, see `Configuring the Processor of the DB Instance
    Class <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html#USER_ConfigureProcessor>`__
    in the *Amazon RDS User Guide.*
    """

    Name: Optional[String]
    Value: Optional[String]


ProcessorFeatureList = List[ProcessorFeature]


class DBSnapshot(TypedDict, total=False):
    """Contains the details of an Amazon RDS DB snapshot.

    This data type is used as a response element in the
    ``DescribeDBSnapshots`` action.
    """

    DBSnapshotIdentifier: Optional[String]
    DBInstanceIdentifier: Optional[String]
    SnapshotCreateTime: Optional[TStamp]
    Engine: Optional[String]
    AllocatedStorage: Optional[Integer]
    Status: Optional[String]
    Port: Optional[Integer]
    AvailabilityZone: Optional[String]
    VpcId: Optional[String]
    InstanceCreateTime: Optional[TStamp]
    MasterUsername: Optional[String]
    EngineVersion: Optional[String]
    LicenseModel: Optional[String]
    SnapshotType: Optional[String]
    Iops: Optional[IntegerOptional]
    OptionGroupName: Optional[String]
    PercentProgress: Optional[Integer]
    SourceRegion: Optional[String]
    SourceDBSnapshotIdentifier: Optional[String]
    StorageType: Optional[String]
    TdeCredentialArn: Optional[String]
    Encrypted: Optional[Boolean]
    KmsKeyId: Optional[String]
    DBSnapshotArn: Optional[String]
    Timezone: Optional[String]
    IAMDatabaseAuthenticationEnabled: Optional[Boolean]
    ProcessorFeatures: Optional[ProcessorFeatureList]
    DbiResourceId: Optional[String]
    TagList: Optional[TagList]
    OriginalSnapshotCreateTime: Optional[TStamp]
    SnapshotTarget: Optional[String]


class CopyDBSnapshotResult(TypedDict, total=False):
    DBSnapshot: Optional[DBSnapshot]


class CopyOptionGroupMessage(ServiceRequest):
    SourceOptionGroupIdentifier: String
    TargetOptionGroupIdentifier: String
    TargetOptionGroupDescription: String
    Tags: Optional[TagList]


class VpcSecurityGroupMembership(TypedDict, total=False):
    """This data type is used as a response element for queries on VPC security
    group membership.
    """

    VpcSecurityGroupId: Optional[String]
    Status: Optional[String]


VpcSecurityGroupMembershipList = List[VpcSecurityGroupMembership]


class DBSecurityGroupMembership(TypedDict, total=False):
    """This data type is used as a response element in the following actions:

    -  ``ModifyDBInstance``

    -  ``RebootDBInstance``

    -  ``RestoreDBInstanceFromDBSnapshot``

    -  ``RestoreDBInstanceToPointInTime``
    """

    DBSecurityGroupName: Optional[String]
    Status: Optional[String]


DBSecurityGroupMembershipList = List[DBSecurityGroupMembership]


class OptionSetting(TypedDict, total=False):
    """Option settings are the actual settings being applied or configured for
    that option. It is used when you modify an option group or describe
    option groups. For example, the NATIVE_NETWORK_ENCRYPTION option has a
    setting called SQLNET.ENCRYPTION_SERVER that can have several different
    values.
    """

    Name: Optional[String]
    Value: Optional[String]
    DefaultValue: Optional[String]
    Description: Optional[String]
    ApplyType: Optional[String]
    DataType: Optional[String]
    AllowedValues: Optional[String]
    IsModifiable: Optional[Boolean]
    IsCollection: Optional[Boolean]


OptionSettingConfigurationList = List[OptionSetting]


class Option(TypedDict, total=False):
    """Option details."""

    OptionName: Optional[String]
    OptionDescription: Optional[String]
    Persistent: Optional[Boolean]
    Permanent: Optional[Boolean]
    Port: Optional[IntegerOptional]
    OptionVersion: Optional[String]
    OptionSettings: Optional[OptionSettingConfigurationList]
    DBSecurityGroupMemberships: Optional[DBSecurityGroupMembershipList]
    VpcSecurityGroupMemberships: Optional[VpcSecurityGroupMembershipList]


OptionsList = List[Option]


class OptionGroup(TypedDict, total=False):
    OptionGroupName: Optional[String]
    OptionGroupDescription: Optional[String]
    EngineName: Optional[String]
    MajorEngineVersion: Optional[String]
    Options: Optional[OptionsList]
    AllowsVpcAndNonVpcInstanceMemberships: Optional[Boolean]
    VpcId: Optional[String]
    OptionGroupArn: Optional[String]


class CopyOptionGroupResult(TypedDict, total=False):
    OptionGroup: Optional[OptionGroup]


class CreateCustomDBEngineVersionMessage(ServiceRequest):
    Engine: CustomEngineName
    EngineVersion: CustomEngineVersion
    DatabaseInstallationFilesS3BucketName: BucketName
    DatabaseInstallationFilesS3Prefix: Optional[String255]
    KMSKeyId: KmsKeyIdOrArn
    Description: Optional[Description]
    Manifest: CustomDBEngineVersionManifest
    Tags: Optional[TagList]


class CreateDBClusterEndpointMessage(ServiceRequest):
    DBClusterIdentifier: String
    DBClusterEndpointIdentifier: String
    EndpointType: String
    StaticMembers: Optional[StringList]
    ExcludedMembers: Optional[StringList]
    Tags: Optional[TagList]


class ServerlessV2ScalingConfiguration(TypedDict, total=False):
    """Contains the scaling configuration of an Aurora Serverless v2 DB
    cluster.

    For more information, see `Using Amazon Aurora Serverless
    v2 <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html>`__
    in the *Amazon Aurora User Guide*.
    """

    MinCapacity: Optional[DoubleOptional]
    MaxCapacity: Optional[DoubleOptional]


class ScalingConfiguration(TypedDict, total=False):
    """Contains the scaling configuration of an Aurora Serverless v1 DB
    cluster.

    For more information, see `Using Amazon Aurora Serverless
    v1 <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless.html>`__
    in the *Amazon Aurora User Guide*.
    """

    MinCapacity: Optional[IntegerOptional]
    MaxCapacity: Optional[IntegerOptional]
    AutoPause: Optional[BooleanOptional]
    SecondsUntilAutoPause: Optional[IntegerOptional]
    TimeoutAction: Optional[String]
    SecondsBeforeTimeout: Optional[IntegerOptional]


LongOptional = int
VpcSecurityGroupIdList = List[String]


class CreateDBClusterMessage(ServiceRequest):
    AvailabilityZones: Optional[AvailabilityZones]
    BackupRetentionPeriod: Optional[IntegerOptional]
    CharacterSetName: Optional[String]
    DatabaseName: Optional[String]
    DBClusterIdentifier: String
    DBClusterParameterGroupName: Optional[String]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    DBSubnetGroupName: Optional[String]
    Engine: String
    EngineVersion: Optional[String]
    Port: Optional[IntegerOptional]
    MasterUsername: Optional[String]
    MasterUserPassword: Optional[String]
    OptionGroupName: Optional[String]
    PreferredBackupWindow: Optional[String]
    PreferredMaintenanceWindow: Optional[String]
    ReplicationSourceIdentifier: Optional[String]
    Tags: Optional[TagList]
    StorageEncrypted: Optional[BooleanOptional]
    KmsKeyId: Optional[String]
    PreSignedUrl: Optional[String]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    BacktrackWindow: Optional[LongOptional]
    EnableCloudwatchLogsExports: Optional[LogTypeList]
    EngineMode: Optional[String]
    ScalingConfiguration: Optional[ScalingConfiguration]
    DeletionProtection: Optional[BooleanOptional]
    GlobalClusterIdentifier: Optional[String]
    EnableHttpEndpoint: Optional[BooleanOptional]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    Domain: Optional[String]
    DomainIAMRoleName: Optional[String]
    EnableGlobalWriteForwarding: Optional[BooleanOptional]
    DBClusterInstanceClass: Optional[String]
    AllocatedStorage: Optional[IntegerOptional]
    StorageType: Optional[String]
    Iops: Optional[IntegerOptional]
    PubliclyAccessible: Optional[BooleanOptional]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    MonitoringInterval: Optional[IntegerOptional]
    MonitoringRoleArn: Optional[String]
    EnablePerformanceInsights: Optional[BooleanOptional]
    PerformanceInsightsKMSKeyId: Optional[String]
    PerformanceInsightsRetentionPeriod: Optional[IntegerOptional]
    ServerlessV2ScalingConfiguration: Optional[ServerlessV2ScalingConfiguration]
    SourceRegion: Optional[String]


class CreateDBClusterParameterGroupMessage(ServiceRequest):
    DBClusterParameterGroupName: String
    DBParameterGroupFamily: String
    Description: String
    Tags: Optional[TagList]


class CreateDBClusterParameterGroupResult(TypedDict, total=False):
    DBClusterParameterGroup: Optional[DBClusterParameterGroup]


class ServerlessV2ScalingConfigurationInfo(TypedDict, total=False):
    """Shows the scaling configuration for an Aurora Serverless v2 DB cluster.

    For more information, see `Using Amazon Aurora Serverless
    v2 <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html>`__
    in the *Amazon Aurora User Guide*.
    """

    MinCapacity: Optional[DoubleOptional]
    MaxCapacity: Optional[DoubleOptional]


class DomainMembership(TypedDict, total=False):
    """An Active Directory Domain membership record associated with the DB
    instance or cluster.
    """

    Domain: Optional[String]
    Status: Optional[String]
    FQDN: Optional[String]
    IAMRoleName: Optional[String]


DomainMembershipList = List[DomainMembership]


class ScalingConfigurationInfo(TypedDict, total=False):
    """Shows the scaling configuration for an Aurora DB cluster in
    ``serverless`` DB engine mode.

    For more information, see `Using Amazon Aurora Serverless
    v1 <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless.html>`__
    in the *Amazon Aurora User Guide*.
    """

    MinCapacity: Optional[IntegerOptional]
    MaxCapacity: Optional[IntegerOptional]
    AutoPause: Optional[BooleanOptional]
    SecondsUntilAutoPause: Optional[IntegerOptional]
    TimeoutAction: Optional[String]
    SecondsBeforeTimeout: Optional[IntegerOptional]


class DBClusterRole(TypedDict, total=False):
    """Describes an Amazon Web Services Identity and Access Management (IAM)
    role that is associated with a DB cluster.
    """

    RoleArn: Optional[String]
    Status: Optional[String]
    FeatureName: Optional[String]


DBClusterRoles = List[DBClusterRole]


class DBClusterMember(TypedDict, total=False):
    """Contains information about an instance that is part of a DB cluster."""

    DBInstanceIdentifier: Optional[String]
    IsClusterWriter: Optional[Boolean]
    DBClusterParameterGroupStatus: Optional[String]
    PromotionTier: Optional[IntegerOptional]


DBClusterMemberList = List[DBClusterMember]
ReadReplicaIdentifierList = List[String]


class DBClusterOptionGroupStatus(TypedDict, total=False):
    """Contains status information for a DB cluster option group."""

    DBClusterOptionGroupName: Optional[String]
    Status: Optional[String]


DBClusterOptionGroupMemberships = List[DBClusterOptionGroupStatus]


class DBCluster(TypedDict, total=False):
    """Contains the details of an Amazon Aurora DB cluster or Multi-AZ DB
    cluster.

    For an Amazon Aurora DB cluster, this data type is used as a response
    element in the operations ``CreateDBCluster``, ``DeleteDBCluster``,
    ``DescribeDBClusters``, ``FailoverDBCluster``, ``ModifyDBCluster``,
    ``PromoteReadReplicaDBCluster``, ``RestoreDBClusterFromS3``,
    ``RestoreDBClusterFromSnapshot``, ``RestoreDBClusterToPointInTime``,
    ``StartDBCluster``, and ``StopDBCluster``.

    For a Multi-AZ DB cluster, this data type is used as a response element
    in the operations ``CreateDBCluster``, ``DeleteDBCluster``,
    ``DescribeDBClusters``, ``FailoverDBCluster``, ``ModifyDBCluster``,
    ``RebootDBCluster``, ``RestoreDBClusterFromSnapshot``, and
    ``RestoreDBClusterToPointInTime``.

    For more information on Amazon Aurora DB clusters, see `What is Amazon
    Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
    in the *Amazon Aurora User Guide.*

    For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
    with two readable standby DB
    instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
    in the *Amazon RDS User Guide.*
    """

    AllocatedStorage: Optional[IntegerOptional]
    AvailabilityZones: Optional[AvailabilityZones]
    BackupRetentionPeriod: Optional[IntegerOptional]
    CharacterSetName: Optional[String]
    DatabaseName: Optional[String]
    DBClusterIdentifier: Optional[String]
    DBClusterParameterGroup: Optional[String]
    DBSubnetGroup: Optional[String]
    Status: Optional[String]
    AutomaticRestartTime: Optional[TStamp]
    PercentProgress: Optional[String]
    EarliestRestorableTime: Optional[TStamp]
    Endpoint: Optional[String]
    ReaderEndpoint: Optional[String]
    CustomEndpoints: Optional[StringList]
    MultiAZ: Optional[BooleanOptional]
    Engine: Optional[String]
    EngineVersion: Optional[String]
    LatestRestorableTime: Optional[TStamp]
    Port: Optional[IntegerOptional]
    MasterUsername: Optional[String]
    DBClusterOptionGroupMemberships: Optional[DBClusterOptionGroupMemberships]
    PreferredBackupWindow: Optional[String]
    PreferredMaintenanceWindow: Optional[String]
    ReplicationSourceIdentifier: Optional[String]
    ReadReplicaIdentifiers: Optional[ReadReplicaIdentifierList]
    DBClusterMembers: Optional[DBClusterMemberList]
    VpcSecurityGroups: Optional[VpcSecurityGroupMembershipList]
    HostedZoneId: Optional[String]
    StorageEncrypted: Optional[Boolean]
    KmsKeyId: Optional[String]
    DbClusterResourceId: Optional[String]
    DBClusterArn: Optional[String]
    AssociatedRoles: Optional[DBClusterRoles]
    IAMDatabaseAuthenticationEnabled: Optional[BooleanOptional]
    CloneGroupId: Optional[String]
    ClusterCreateTime: Optional[TStamp]
    EarliestBacktrackTime: Optional[TStamp]
    BacktrackWindow: Optional[LongOptional]
    BacktrackConsumedChangeRecords: Optional[LongOptional]
    EnabledCloudwatchLogsExports: Optional[LogTypeList]
    Capacity: Optional[IntegerOptional]
    EngineMode: Optional[String]
    ScalingConfigurationInfo: Optional[ScalingConfigurationInfo]
    DeletionProtection: Optional[BooleanOptional]
    HttpEndpointEnabled: Optional[BooleanOptional]
    ActivityStreamMode: Optional[ActivityStreamMode]
    ActivityStreamStatus: Optional[ActivityStreamStatus]
    ActivityStreamKmsKeyId: Optional[String]
    ActivityStreamKinesisStreamName: Optional[String]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    CrossAccountClone: Optional[BooleanOptional]
    DomainMemberships: Optional[DomainMembershipList]
    TagList: Optional[TagList]
    GlobalWriteForwardingStatus: Optional[WriteForwardingStatus]
    GlobalWriteForwardingRequested: Optional[BooleanOptional]
    PendingModifiedValues: Optional[ClusterPendingModifiedValues]
    DBClusterInstanceClass: Optional[String]
    StorageType: Optional[String]
    Iops: Optional[IntegerOptional]
    PubliclyAccessible: Optional[BooleanOptional]
    AutoMinorVersionUpgrade: Optional[Boolean]
    MonitoringInterval: Optional[IntegerOptional]
    MonitoringRoleArn: Optional[String]
    PerformanceInsightsEnabled: Optional[BooleanOptional]
    PerformanceInsightsKMSKeyId: Optional[String]
    PerformanceInsightsRetentionPeriod: Optional[IntegerOptional]
    ServerlessV2ScalingConfiguration: Optional[ServerlessV2ScalingConfigurationInfo]


class CreateDBClusterResult(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class CreateDBClusterSnapshotMessage(ServiceRequest):
    DBClusterSnapshotIdentifier: String
    DBClusterIdentifier: String
    Tags: Optional[TagList]


class CreateDBClusterSnapshotResult(TypedDict, total=False):
    DBClusterSnapshot: Optional[DBClusterSnapshot]


DBSecurityGroupNameList = List[String]


class CreateDBInstanceMessage(ServiceRequest):
    DBName: Optional[String]
    DBInstanceIdentifier: String
    AllocatedStorage: Optional[IntegerOptional]
    DBInstanceClass: String
    Engine: String
    MasterUsername: Optional[String]
    MasterUserPassword: Optional[String]
    DBSecurityGroups: Optional[DBSecurityGroupNameList]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    AvailabilityZone: Optional[String]
    DBSubnetGroupName: Optional[String]
    PreferredMaintenanceWindow: Optional[String]
    DBParameterGroupName: Optional[String]
    BackupRetentionPeriod: Optional[IntegerOptional]
    PreferredBackupWindow: Optional[String]
    Port: Optional[IntegerOptional]
    MultiAZ: Optional[BooleanOptional]
    EngineVersion: Optional[String]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    LicenseModel: Optional[String]
    Iops: Optional[IntegerOptional]
    OptionGroupName: Optional[String]
    CharacterSetName: Optional[String]
    NcharCharacterSetName: Optional[String]
    PubliclyAccessible: Optional[BooleanOptional]
    Tags: Optional[TagList]
    DBClusterIdentifier: Optional[String]
    StorageType: Optional[String]
    TdeCredentialArn: Optional[String]
    TdeCredentialPassword: Optional[String]
    StorageEncrypted: Optional[BooleanOptional]
    KmsKeyId: Optional[String]
    Domain: Optional[String]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    MonitoringInterval: Optional[IntegerOptional]
    MonitoringRoleArn: Optional[String]
    DomainIAMRoleName: Optional[String]
    PromotionTier: Optional[IntegerOptional]
    Timezone: Optional[String]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    EnablePerformanceInsights: Optional[BooleanOptional]
    PerformanceInsightsKMSKeyId: Optional[String]
    PerformanceInsightsRetentionPeriod: Optional[IntegerOptional]
    EnableCloudwatchLogsExports: Optional[LogTypeList]
    ProcessorFeatures: Optional[ProcessorFeatureList]
    DeletionProtection: Optional[BooleanOptional]
    MaxAllocatedStorage: Optional[IntegerOptional]
    EnableCustomerOwnedIp: Optional[BooleanOptional]
    CustomIamInstanceProfile: Optional[String]
    BackupTarget: Optional[String]
    NetworkType: Optional[String]


class CreateDBInstanceReadReplicaMessage(ServiceRequest):
    DBInstanceIdentifier: String
    SourceDBInstanceIdentifier: String
    DBInstanceClass: Optional[String]
    AvailabilityZone: Optional[String]
    Port: Optional[IntegerOptional]
    MultiAZ: Optional[BooleanOptional]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    Iops: Optional[IntegerOptional]
    OptionGroupName: Optional[String]
    DBParameterGroupName: Optional[String]
    PubliclyAccessible: Optional[BooleanOptional]
    Tags: Optional[TagList]
    DBSubnetGroupName: Optional[String]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    StorageType: Optional[String]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    MonitoringInterval: Optional[IntegerOptional]
    MonitoringRoleArn: Optional[String]
    KmsKeyId: Optional[String]
    PreSignedUrl: Optional[String]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    EnablePerformanceInsights: Optional[BooleanOptional]
    PerformanceInsightsKMSKeyId: Optional[String]
    PerformanceInsightsRetentionPeriod: Optional[IntegerOptional]
    EnableCloudwatchLogsExports: Optional[LogTypeList]
    ProcessorFeatures: Optional[ProcessorFeatureList]
    UseDefaultProcessorFeatures: Optional[BooleanOptional]
    DeletionProtection: Optional[BooleanOptional]
    Domain: Optional[String]
    DomainIAMRoleName: Optional[String]
    ReplicaMode: Optional[ReplicaMode]
    MaxAllocatedStorage: Optional[IntegerOptional]
    CustomIamInstanceProfile: Optional[String]
    NetworkType: Optional[String]
    SourceRegion: Optional[String]


class DBInstanceAutomatedBackupsReplication(TypedDict, total=False):
    """Automated backups of a DB instance replicated to another Amazon Web
    Services Region. They consist of system backups, transaction logs, and
    database instance properties.
    """

    DBInstanceAutomatedBackupsArn: Optional[String]


DBInstanceAutomatedBackupsReplicationList = List[DBInstanceAutomatedBackupsReplication]


class Endpoint(TypedDict, total=False):
    """This data type represents the information you need to connect to an
    Amazon RDS DB instance. This data type is used as a response element in
    the following actions:

    -  ``CreateDBInstance``

    -  ``DescribeDBInstances``

    -  ``DeleteDBInstance``

    For the data structure that represents Amazon Aurora DB cluster
    endpoints, see ``DBClusterEndpoint``.
    """

    Address: Optional[String]
    Port: Optional[Integer]
    HostedZoneId: Optional[String]


class DBInstanceRole(TypedDict, total=False):
    """Describes an Amazon Web Services Identity and Access Management (IAM)
    role that is associated with a DB instance.
    """

    RoleArn: Optional[String]
    FeatureName: Optional[String]
    Status: Optional[String]


DBInstanceRoles = List[DBInstanceRole]


class DBInstanceStatusInfo(TypedDict, total=False):
    """Provides a list of status information for a DB instance."""

    StatusType: Optional[String]
    Normal: Optional[Boolean]
    Status: Optional[String]
    Message: Optional[String]


DBInstanceStatusInfoList = List[DBInstanceStatusInfo]


class OptionGroupMembership(TypedDict, total=False):
    """Provides information on the option groups the DB instance is a member
    of.
    """

    OptionGroupName: Optional[String]
    Status: Optional[String]


OptionGroupMembershipList = List[OptionGroupMembership]
ReadReplicaDBClusterIdentifierList = List[String]
ReadReplicaDBInstanceIdentifierList = List[String]


class PendingModifiedValues(TypedDict, total=False):
    """This data type is used as a response element in the ``ModifyDBInstance``
    operation and contains changes that will be applied during the next
    maintenance window.
    """

    DBInstanceClass: Optional[String]
    AllocatedStorage: Optional[IntegerOptional]
    MasterUserPassword: Optional[String]
    Port: Optional[IntegerOptional]
    BackupRetentionPeriod: Optional[IntegerOptional]
    MultiAZ: Optional[BooleanOptional]
    EngineVersion: Optional[String]
    LicenseModel: Optional[String]
    Iops: Optional[IntegerOptional]
    DBInstanceIdentifier: Optional[String]
    StorageType: Optional[String]
    CACertificateIdentifier: Optional[String]
    DBSubnetGroupName: Optional[String]
    PendingCloudwatchLogsExports: Optional[PendingCloudwatchLogsExports]
    ProcessorFeatures: Optional[ProcessorFeatureList]
    IAMDatabaseAuthenticationEnabled: Optional[BooleanOptional]
    AutomationMode: Optional[AutomationMode]
    ResumeFullAutomationModeTime: Optional[TStamp]


class Outpost(TypedDict, total=False):
    """A data type that represents an Outpost.

    For more information about RDS on Outposts, see `Amazon RDS on Amazon
    Web Services
    Outposts <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-on-outposts.html>`__
    in the *Amazon RDS User Guide.*
    """

    Arn: Optional[String]


class Subnet(TypedDict, total=False):
    """This data type is used as a response element for the
    ``DescribeDBSubnetGroups`` operation.
    """

    SubnetIdentifier: Optional[String]
    SubnetAvailabilityZone: Optional[AvailabilityZone]
    SubnetOutpost: Optional[Outpost]
    SubnetStatus: Optional[String]


SubnetList = List[Subnet]


class DBSubnetGroup(TypedDict, total=False):
    """Contains the details of an Amazon RDS DB subnet group.

    This data type is used as a response element in the
    ``DescribeDBSubnetGroups`` action.
    """

    DBSubnetGroupName: Optional[String]
    DBSubnetGroupDescription: Optional[String]
    VpcId: Optional[String]
    SubnetGroupStatus: Optional[String]
    Subnets: Optional[SubnetList]
    DBSubnetGroupArn: Optional[String]
    SupportedNetworkTypes: Optional[StringList]


class DBParameterGroupStatus(TypedDict, total=False):
    """The status of the DB parameter group.

    This data type is used as a response element in the following actions:

    -  ``CreateDBInstance``

    -  ``CreateDBInstanceReadReplica``

    -  ``DeleteDBInstance``

    -  ``ModifyDBInstance``

    -  ``RebootDBInstance``

    -  ``RestoreDBInstanceFromDBSnapshot``
    """

    DBParameterGroupName: Optional[String]
    ParameterApplyStatus: Optional[String]


DBParameterGroupStatusList = List[DBParameterGroupStatus]


class DBInstance(TypedDict, total=False):
    """Contains the details of an Amazon RDS DB instance.

    This data type is used as a response element in the operations
    ``CreateDBInstance``, ``CreateDBInstanceReadReplica``,
    ``DeleteDBInstance``, ``DescribeDBInstances``, ``ModifyDBInstance``,
    ``PromoteReadReplica``, ``RebootDBInstance``,
    ``RestoreDBInstanceFromDBSnapshot``, ``RestoreDBInstanceFromS3``,
    ``RestoreDBInstanceToPointInTime``, ``StartDBInstance``, and
    ``StopDBInstance``.
    """

    DBInstanceIdentifier: Optional[String]
    DBInstanceClass: Optional[String]
    Engine: Optional[String]
    DBInstanceStatus: Optional[String]
    AutomaticRestartTime: Optional[TStamp]
    MasterUsername: Optional[String]
    DBName: Optional[String]
    Endpoint: Optional[Endpoint]
    AllocatedStorage: Optional[Integer]
    InstanceCreateTime: Optional[TStamp]
    PreferredBackupWindow: Optional[String]
    BackupRetentionPeriod: Optional[Integer]
    DBSecurityGroups: Optional[DBSecurityGroupMembershipList]
    VpcSecurityGroups: Optional[VpcSecurityGroupMembershipList]
    DBParameterGroups: Optional[DBParameterGroupStatusList]
    AvailabilityZone: Optional[String]
    DBSubnetGroup: Optional[DBSubnetGroup]
    PreferredMaintenanceWindow: Optional[String]
    PendingModifiedValues: Optional[PendingModifiedValues]
    LatestRestorableTime: Optional[TStamp]
    MultiAZ: Optional[Boolean]
    EngineVersion: Optional[String]
    AutoMinorVersionUpgrade: Optional[Boolean]
    ReadReplicaSourceDBInstanceIdentifier: Optional[String]
    ReadReplicaDBInstanceIdentifiers: Optional[ReadReplicaDBInstanceIdentifierList]
    ReadReplicaDBClusterIdentifiers: Optional[ReadReplicaDBClusterIdentifierList]
    ReplicaMode: Optional[ReplicaMode]
    LicenseModel: Optional[String]
    Iops: Optional[IntegerOptional]
    OptionGroupMemberships: Optional[OptionGroupMembershipList]
    CharacterSetName: Optional[String]
    NcharCharacterSetName: Optional[String]
    SecondaryAvailabilityZone: Optional[String]
    PubliclyAccessible: Optional[Boolean]
    StatusInfos: Optional[DBInstanceStatusInfoList]
    StorageType: Optional[String]
    TdeCredentialArn: Optional[String]
    DbInstancePort: Optional[Integer]
    DBClusterIdentifier: Optional[String]
    StorageEncrypted: Optional[Boolean]
    KmsKeyId: Optional[String]
    DbiResourceId: Optional[String]
    CACertificateIdentifier: Optional[String]
    DomainMemberships: Optional[DomainMembershipList]
    CopyTagsToSnapshot: Optional[Boolean]
    MonitoringInterval: Optional[IntegerOptional]
    EnhancedMonitoringResourceArn: Optional[String]
    MonitoringRoleArn: Optional[String]
    PromotionTier: Optional[IntegerOptional]
    DBInstanceArn: Optional[String]
    Timezone: Optional[String]
    IAMDatabaseAuthenticationEnabled: Optional[Boolean]
    PerformanceInsightsEnabled: Optional[BooleanOptional]
    PerformanceInsightsKMSKeyId: Optional[String]
    PerformanceInsightsRetentionPeriod: Optional[IntegerOptional]
    EnabledCloudwatchLogsExports: Optional[LogTypeList]
    ProcessorFeatures: Optional[ProcessorFeatureList]
    DeletionProtection: Optional[Boolean]
    AssociatedRoles: Optional[DBInstanceRoles]
    ListenerEndpoint: Optional[Endpoint]
    MaxAllocatedStorage: Optional[IntegerOptional]
    TagList: Optional[TagList]
    DBInstanceAutomatedBackupsReplications: Optional[DBInstanceAutomatedBackupsReplicationList]
    CustomerOwnedIpEnabled: Optional[BooleanOptional]
    AwsBackupRecoveryPointArn: Optional[String]
    ActivityStreamStatus: Optional[ActivityStreamStatus]
    ActivityStreamKmsKeyId: Optional[String]
    ActivityStreamKinesisStreamName: Optional[String]
    ActivityStreamMode: Optional[ActivityStreamMode]
    ActivityStreamEngineNativeAuditFieldsIncluded: Optional[BooleanOptional]
    AutomationMode: Optional[AutomationMode]
    ResumeFullAutomationModeTime: Optional[TStamp]
    CustomIamInstanceProfile: Optional[String]
    BackupTarget: Optional[String]
    NetworkType: Optional[String]


class CreateDBInstanceReadReplicaResult(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class CreateDBInstanceResult(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class CreateDBParameterGroupMessage(ServiceRequest):
    DBParameterGroupName: String
    DBParameterGroupFamily: String
    Description: String
    Tags: Optional[TagList]


class CreateDBParameterGroupResult(TypedDict, total=False):
    DBParameterGroup: Optional[DBParameterGroup]


class CreateDBProxyEndpointRequest(ServiceRequest):
    DBProxyName: DBProxyName
    DBProxyEndpointName: DBProxyEndpointName
    VpcSubnetIds: StringList
    VpcSecurityGroupIds: Optional[StringList]
    TargetRole: Optional[DBProxyEndpointTargetRole]
    Tags: Optional[TagList]


class DBProxyEndpoint(TypedDict, total=False):
    """The data structure representing an endpoint associated with a DB proxy.
    RDS automatically creates one endpoint for each DB proxy. For Aurora DB
    clusters, you can associate additional endpoints with the same DB proxy.
    These endpoints can be read/write or read-only. They can also reside in
    different VPCs than the associated DB proxy.

    This data type is used as a response element in the
    ``DescribeDBProxyEndpoints`` operation.
    """

    DBProxyEndpointName: Optional[String]
    DBProxyEndpointArn: Optional[String]
    DBProxyName: Optional[String]
    Status: Optional[DBProxyEndpointStatus]
    VpcId: Optional[String]
    VpcSecurityGroupIds: Optional[StringList]
    VpcSubnetIds: Optional[StringList]
    Endpoint: Optional[String]
    CreatedDate: Optional[TStamp]
    TargetRole: Optional[DBProxyEndpointTargetRole]
    IsDefault: Optional[Boolean]


class CreateDBProxyEndpointResponse(TypedDict, total=False):
    DBProxyEndpoint: Optional[DBProxyEndpoint]


class UserAuthConfig(TypedDict, total=False):
    """Specifies the details of authentication used by a proxy to log in as a
    specific database user.
    """

    Description: Optional[String]
    UserName: Optional[String]
    AuthScheme: Optional[AuthScheme]
    SecretArn: Optional[String]
    IAMAuth: Optional[IAMAuthMode]


UserAuthConfigList = List[UserAuthConfig]


class CreateDBProxyRequest(ServiceRequest):
    DBProxyName: String
    EngineFamily: EngineFamily
    Auth: UserAuthConfigList
    RoleArn: String
    VpcSubnetIds: StringList
    VpcSecurityGroupIds: Optional[StringList]
    RequireTLS: Optional[Boolean]
    IdleClientTimeout: Optional[IntegerOptional]
    DebugLogging: Optional[Boolean]
    Tags: Optional[TagList]


class UserAuthConfigInfo(TypedDict, total=False):
    """Returns the details of authentication used by a proxy to log in as a
    specific database user.
    """

    Description: Optional[String]
    UserName: Optional[String]
    AuthScheme: Optional[AuthScheme]
    SecretArn: Optional[String]
    IAMAuth: Optional[IAMAuthMode]


UserAuthConfigInfoList = List[UserAuthConfigInfo]


class DBProxy(TypedDict, total=False):
    """The data structure representing a proxy managed by the RDS Proxy.

    This data type is used as a response element in the
    ``DescribeDBProxies`` action.
    """

    DBProxyName: Optional[String]
    DBProxyArn: Optional[String]
    Status: Optional[DBProxyStatus]
    EngineFamily: Optional[String]
    VpcId: Optional[String]
    VpcSecurityGroupIds: Optional[StringList]
    VpcSubnetIds: Optional[StringList]
    Auth: Optional[UserAuthConfigInfoList]
    RoleArn: Optional[String]
    Endpoint: Optional[String]
    RequireTLS: Optional[Boolean]
    IdleClientTimeout: Optional[Integer]
    DebugLogging: Optional[Boolean]
    CreatedDate: Optional[TStamp]
    UpdatedDate: Optional[TStamp]


class CreateDBProxyResponse(TypedDict, total=False):
    DBProxy: Optional[DBProxy]


class CreateDBSecurityGroupMessage(ServiceRequest):
    DBSecurityGroupName: String
    DBSecurityGroupDescription: String
    Tags: Optional[TagList]


class CreateDBSecurityGroupResult(TypedDict, total=False):
    DBSecurityGroup: Optional[DBSecurityGroup]


class CreateDBSnapshotMessage(ServiceRequest):
    DBSnapshotIdentifier: String
    DBInstanceIdentifier: String
    Tags: Optional[TagList]


class CreateDBSnapshotResult(TypedDict, total=False):
    DBSnapshot: Optional[DBSnapshot]


SubnetIdentifierList = List[String]


class CreateDBSubnetGroupMessage(ServiceRequest):
    DBSubnetGroupName: String
    DBSubnetGroupDescription: String
    SubnetIds: SubnetIdentifierList
    Tags: Optional[TagList]


class CreateDBSubnetGroupResult(TypedDict, total=False):
    DBSubnetGroup: Optional[DBSubnetGroup]


class CreateEventSubscriptionMessage(ServiceRequest):
    SubscriptionName: String
    SnsTopicArn: String
    SourceType: Optional[String]
    EventCategories: Optional[EventCategoriesList]
    SourceIds: Optional[SourceIdsList]
    Enabled: Optional[BooleanOptional]
    Tags: Optional[TagList]


class CreateEventSubscriptionResult(TypedDict, total=False):
    EventSubscription: Optional[EventSubscription]


class CreateGlobalClusterMessage(ServiceRequest):
    GlobalClusterIdentifier: Optional[String]
    SourceDBClusterIdentifier: Optional[String]
    Engine: Optional[String]
    EngineVersion: Optional[String]
    DeletionProtection: Optional[BooleanOptional]
    DatabaseName: Optional[String]
    StorageEncrypted: Optional[BooleanOptional]


class FailoverState(TypedDict, total=False):
    """Contains the state of scheduled or in-process failover operations on an
    Aurora global database (GlobalCluster). This Data type is empty unless a
    failover operation is scheduled or is currently underway on the Aurora
    global database.
    """

    Status: Optional[FailoverStatus]
    FromDbClusterArn: Optional[String]
    ToDbClusterArn: Optional[String]


ReadersArnList = List[String]


class GlobalClusterMember(TypedDict, total=False):
    """A data structure with information about any primary and secondary
    clusters associated with an Aurora global database.
    """

    DBClusterArn: Optional[String]
    Readers: Optional[ReadersArnList]
    IsWriter: Optional[Boolean]
    GlobalWriteForwardingStatus: Optional[WriteForwardingStatus]


GlobalClusterMemberList = List[GlobalClusterMember]


class GlobalCluster(TypedDict, total=False):
    """A data type representing an Aurora global database."""

    GlobalClusterIdentifier: Optional[String]
    GlobalClusterResourceId: Optional[String]
    GlobalClusterArn: Optional[String]
    Status: Optional[String]
    Engine: Optional[String]
    EngineVersion: Optional[String]
    DatabaseName: Optional[String]
    StorageEncrypted: Optional[BooleanOptional]
    DeletionProtection: Optional[BooleanOptional]
    GlobalClusterMembers: Optional[GlobalClusterMemberList]
    FailoverState: Optional[FailoverState]


class CreateGlobalClusterResult(TypedDict, total=False):
    GlobalCluster: Optional[GlobalCluster]


class CreateOptionGroupMessage(ServiceRequest):
    OptionGroupName: String
    EngineName: String
    MajorEngineVersion: String
    OptionGroupDescription: String
    Tags: Optional[TagList]


class CreateOptionGroupResult(TypedDict, total=False):
    OptionGroup: Optional[OptionGroup]


class DBClusterBacktrack(TypedDict, total=False):
    """This data type is used as a response element in the
    ``DescribeDBClusterBacktracks`` action.
    """

    DBClusterIdentifier: Optional[String]
    BacktrackIdentifier: Optional[String]
    BacktrackTo: Optional[TStamp]
    BacktrackedFrom: Optional[TStamp]
    BacktrackRequestCreationTime: Optional[TStamp]
    Status: Optional[String]


DBClusterBacktrackList = List[DBClusterBacktrack]


class DBClusterBacktrackMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeDBClusterBacktracks`` action.
    """

    Marker: Optional[String]
    DBClusterBacktracks: Optional[DBClusterBacktrackList]


class DBClusterCapacityInfo(TypedDict, total=False):
    DBClusterIdentifier: Optional[String]
    PendingCapacity: Optional[IntegerOptional]
    CurrentCapacity: Optional[IntegerOptional]
    SecondsBeforeTimeout: Optional[IntegerOptional]
    TimeoutAction: Optional[String]


class DBClusterEndpoint(TypedDict, total=False):
    """This data type represents the information you need to connect to an
    Amazon Aurora DB cluster. This data type is used as a response element
    in the following actions:

    -  ``CreateDBClusterEndpoint``

    -  ``DescribeDBClusterEndpoints``

    -  ``ModifyDBClusterEndpoint``

    -  ``DeleteDBClusterEndpoint``

    For the data structure that represents Amazon RDS DB instance endpoints,
    see ``Endpoint``.
    """

    DBClusterEndpointIdentifier: Optional[String]
    DBClusterIdentifier: Optional[String]
    DBClusterEndpointResourceIdentifier: Optional[String]
    Endpoint: Optional[String]
    Status: Optional[String]
    EndpointType: Optional[String]
    CustomEndpointType: Optional[String]
    StaticMembers: Optional[StringList]
    ExcludedMembers: Optional[StringList]
    DBClusterEndpointArn: Optional[String]


DBClusterEndpointList = List[DBClusterEndpoint]


class DBClusterEndpointMessage(TypedDict, total=False):
    Marker: Optional[String]
    DBClusterEndpoints: Optional[DBClusterEndpointList]


DBClusterList = List[DBCluster]


class DBClusterMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeDBClusters`` action.
    """

    Marker: Optional[String]
    DBClusters: Optional[DBClusterList]


EngineModeList = List[String]


class Parameter(TypedDict, total=False):
    """This data type is used as a request parameter in the
    ``ModifyDBParameterGroup`` and ``ResetDBParameterGroup`` actions.

    This data type is used as a response element in the
    ``DescribeEngineDefaultParameters`` and ``DescribeDBParameters``
    actions.
    """

    ParameterName: Optional[String]
    ParameterValue: Optional[String]
    Description: Optional[String]
    Source: Optional[String]
    ApplyType: Optional[String]
    DataType: Optional[String]
    AllowedValues: Optional[String]
    IsModifiable: Optional[Boolean]
    MinimumEngineVersion: Optional[String]
    ApplyMethod: Optional[ApplyMethod]
    SupportedEngineModes: Optional[EngineModeList]


ParametersList = List[Parameter]


class DBClusterParameterGroupDetails(TypedDict, total=False):
    """Provides details about a DB cluster parameter group including the
    parameters in the DB cluster parameter group.
    """

    Parameters: Optional[ParametersList]
    Marker: Optional[String]


DBClusterParameterGroupList = List[DBClusterParameterGroup]


class DBClusterParameterGroupNameMessage(TypedDict, total=False):
    DBClusterParameterGroupName: Optional[String]


class DBClusterParameterGroupsMessage(TypedDict, total=False):
    Marker: Optional[String]
    DBClusterParameterGroups: Optional[DBClusterParameterGroupList]


class DBClusterSnapshotAttribute(TypedDict, total=False):
    """Contains the name and values of a manual DB cluster snapshot attribute.

    Manual DB cluster snapshot attributes are used to authorize other Amazon
    Web Services accounts to restore a manual DB cluster snapshot. For more
    information, see the ``ModifyDBClusterSnapshotAttribute`` API action.
    """

    AttributeName: Optional[String]
    AttributeValues: Optional[AttributeValueList]


DBClusterSnapshotAttributeList = List[DBClusterSnapshotAttribute]


class DBClusterSnapshotAttributesResult(TypedDict, total=False):
    """Contains the results of a successful call to the
    ``DescribeDBClusterSnapshotAttributes`` API action.

    Manual DB cluster snapshot attributes are used to authorize other Amazon
    Web Services accounts to copy or restore a manual DB cluster snapshot.
    For more information, see the ``ModifyDBClusterSnapshotAttribute`` API
    action.
    """

    DBClusterSnapshotIdentifier: Optional[String]
    DBClusterSnapshotAttributes: Optional[DBClusterSnapshotAttributeList]


DBClusterSnapshotList = List[DBClusterSnapshot]


class DBClusterSnapshotMessage(TypedDict, total=False):
    """Provides a list of DB cluster snapshots for the user as the result of a
    call to the ``DescribeDBClusterSnapshots`` action.
    """

    Marker: Optional[String]
    DBClusterSnapshots: Optional[DBClusterSnapshotList]


FeatureNameList = List[String]


class Timezone(TypedDict, total=False):
    """A time zone associated with a ``DBInstance`` or a ``DBSnapshot``. This
    data type is an element in the response to the ``DescribeDBInstances``,
    the ``DescribeDBSnapshots``, and the ``DescribeDBEngineVersions``
    actions.
    """

    TimezoneName: Optional[String]


SupportedTimezonesList = List[Timezone]


class UpgradeTarget(TypedDict, total=False):
    """The version of the database engine that a DB instance can be upgraded
    to.
    """

    Engine: Optional[String]
    EngineVersion: Optional[String]
    Description: Optional[String]
    AutoUpgrade: Optional[Boolean]
    IsMajorVersionUpgrade: Optional[Boolean]
    SupportedEngineModes: Optional[EngineModeList]
    SupportsParallelQuery: Optional[BooleanOptional]
    SupportsGlobalDatabases: Optional[BooleanOptional]
    SupportsBabelfish: Optional[BooleanOptional]


ValidUpgradeTargetList = List[UpgradeTarget]
SupportedCharacterSetsList = List[CharacterSet]


class DBEngineVersion(TypedDict, total=False):
    """This data type is used as a response element in the action
    ``DescribeDBEngineVersions``.
    """

    Engine: Optional[String]
    EngineVersion: Optional[String]
    DBParameterGroupFamily: Optional[String]
    DBEngineDescription: Optional[String]
    DBEngineVersionDescription: Optional[String]
    DefaultCharacterSet: Optional[CharacterSet]
    SupportedCharacterSets: Optional[SupportedCharacterSetsList]
    SupportedNcharCharacterSets: Optional[SupportedCharacterSetsList]
    ValidUpgradeTarget: Optional[ValidUpgradeTargetList]
    SupportedTimezones: Optional[SupportedTimezonesList]
    ExportableLogTypes: Optional[LogTypeList]
    SupportsLogExportsToCloudwatchLogs: Optional[Boolean]
    SupportsReadReplica: Optional[Boolean]
    SupportedEngineModes: Optional[EngineModeList]
    SupportedFeatureNames: Optional[FeatureNameList]
    Status: Optional[String]
    SupportsParallelQuery: Optional[Boolean]
    SupportsGlobalDatabases: Optional[Boolean]
    MajorEngineVersion: Optional[String]
    DatabaseInstallationFilesS3BucketName: Optional[String]
    DatabaseInstallationFilesS3Prefix: Optional[String]
    DBEngineVersionArn: Optional[String]
    KMSKeyId: Optional[String]
    CreateTime: Optional[TStamp]
    TagList: Optional[TagList]
    SupportsBabelfish: Optional[Boolean]


DBEngineVersionList = List[DBEngineVersion]


class DBEngineVersionMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeDBEngineVersions`` action.
    """

    Marker: Optional[String]
    DBEngineVersions: Optional[DBEngineVersionList]


class RestoreWindow(TypedDict, total=False):
    """Earliest and latest time an instance can be restored to:"""

    EarliestTime: Optional[TStamp]
    LatestTime: Optional[TStamp]


class DBInstanceAutomatedBackup(TypedDict, total=False):
    """An automated backup of a DB instance. It consists of system backups,
    transaction logs, and the database instance properties that existed at
    the time you deleted the source instance.
    """

    DBInstanceArn: Optional[String]
    DbiResourceId: Optional[String]
    Region: Optional[String]
    DBInstanceIdentifier: Optional[String]
    RestoreWindow: Optional[RestoreWindow]
    AllocatedStorage: Optional[Integer]
    Status: Optional[String]
    Port: Optional[Integer]
    AvailabilityZone: Optional[String]
    VpcId: Optional[String]
    InstanceCreateTime: Optional[TStamp]
    MasterUsername: Optional[String]
    Engine: Optional[String]
    EngineVersion: Optional[String]
    LicenseModel: Optional[String]
    Iops: Optional[IntegerOptional]
    OptionGroupName: Optional[String]
    TdeCredentialArn: Optional[String]
    Encrypted: Optional[Boolean]
    StorageType: Optional[String]
    KmsKeyId: Optional[String]
    Timezone: Optional[String]
    IAMDatabaseAuthenticationEnabled: Optional[Boolean]
    BackupRetentionPeriod: Optional[IntegerOptional]
    DBInstanceAutomatedBackupsArn: Optional[String]
    DBInstanceAutomatedBackupsReplications: Optional[DBInstanceAutomatedBackupsReplicationList]
    BackupTarget: Optional[String]


DBInstanceAutomatedBackupList = List[DBInstanceAutomatedBackup]


class DBInstanceAutomatedBackupMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeDBInstanceAutomatedBackups`` action.
    """

    Marker: Optional[String]
    DBInstanceAutomatedBackups: Optional[DBInstanceAutomatedBackupList]


DBInstanceList = List[DBInstance]


class DBInstanceMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeDBInstances`` action.
    """

    Marker: Optional[String]
    DBInstances: Optional[DBInstanceList]


class DBParameterGroupDetails(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeDBParameters`` action.
    """

    Parameters: Optional[ParametersList]
    Marker: Optional[String]


DBParameterGroupList = List[DBParameterGroup]


class DBParameterGroupNameMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``ModifyDBParameterGroup`` or ``ResetDBParameterGroup`` action.
    """

    DBParameterGroupName: Optional[String]


class DBParameterGroupsMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeDBParameterGroups`` action.
    """

    Marker: Optional[String]
    DBParameterGroups: Optional[DBParameterGroupList]


DBProxyEndpointList = List[DBProxyEndpoint]
DBProxyList = List[DBProxy]


class TargetHealth(TypedDict, total=False):
    """Information about the connection health of an RDS Proxy target."""

    State: Optional[TargetState]
    Reason: Optional[TargetHealthReason]
    Description: Optional[String]


class DBProxyTarget(TypedDict, total=False):
    """Contains the details for an RDS Proxy target. It represents an RDS DB
    instance or Aurora DB cluster that the proxy can connect to. One or more
    targets are associated with an RDS Proxy target group.

    This data type is used as a response element in the
    ``DescribeDBProxyTargets`` action.
    """

    TargetArn: Optional[String]
    Endpoint: Optional[String]
    TrackedClusterId: Optional[String]
    RdsResourceId: Optional[String]
    Port: Optional[Integer]
    Type: Optional[TargetType]
    Role: Optional[TargetRole]
    TargetHealth: Optional[TargetHealth]


class DBProxyTargetGroup(TypedDict, total=False):
    """Represents a set of RDS DB instances, Aurora DB clusters, or both that a
    proxy can connect to. Currently, each target group is associated with
    exactly one RDS DB instance or Aurora DB cluster.

    This data type is used as a response element in the
    ``DescribeDBProxyTargetGroups`` action.
    """

    DBProxyName: Optional[String]
    TargetGroupName: Optional[String]
    TargetGroupArn: Optional[String]
    IsDefault: Optional[Boolean]
    Status: Optional[String]
    ConnectionPoolConfig: Optional[ConnectionPoolConfigurationInfo]
    CreatedDate: Optional[TStamp]
    UpdatedDate: Optional[TStamp]


DBSecurityGroups = List[DBSecurityGroup]


class DBSecurityGroupMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeDBSecurityGroups`` action.
    """

    Marker: Optional[String]
    DBSecurityGroups: Optional[DBSecurityGroups]


class DBSnapshotAttribute(TypedDict, total=False):
    """Contains the name and values of a manual DB snapshot attribute

    Manual DB snapshot attributes are used to authorize other Amazon Web
    Services accounts to restore a manual DB snapshot. For more information,
    see the ``ModifyDBSnapshotAttribute`` API.
    """

    AttributeName: Optional[String]
    AttributeValues: Optional[AttributeValueList]


DBSnapshotAttributeList = List[DBSnapshotAttribute]


class DBSnapshotAttributesResult(TypedDict, total=False):
    """Contains the results of a successful call to the
    ``DescribeDBSnapshotAttributes`` API action.

    Manual DB snapshot attributes are used to authorize other Amazon Web
    Services accounts to copy or restore a manual DB snapshot. For more
    information, see the ``ModifyDBSnapshotAttribute`` API action.
    """

    DBSnapshotIdentifier: Optional[String]
    DBSnapshotAttributes: Optional[DBSnapshotAttributeList]


DBSnapshotList = List[DBSnapshot]


class DBSnapshotMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeDBSnapshots`` action.
    """

    Marker: Optional[String]
    DBSnapshots: Optional[DBSnapshotList]


DBSubnetGroups = List[DBSubnetGroup]


class DBSubnetGroupMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeDBSubnetGroups`` action.
    """

    Marker: Optional[String]
    DBSubnetGroups: Optional[DBSubnetGroups]


class DeleteCustomDBEngineVersionMessage(ServiceRequest):
    Engine: CustomEngineName
    EngineVersion: CustomEngineVersion


class DeleteDBClusterEndpointMessage(ServiceRequest):
    DBClusterEndpointIdentifier: String


class DeleteDBClusterMessage(ServiceRequest):
    DBClusterIdentifier: String
    SkipFinalSnapshot: Optional[Boolean]
    FinalDBSnapshotIdentifier: Optional[String]


class DeleteDBClusterParameterGroupMessage(ServiceRequest):
    DBClusterParameterGroupName: String


class DeleteDBClusterResult(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class DeleteDBClusterSnapshotMessage(ServiceRequest):
    DBClusterSnapshotIdentifier: String


class DeleteDBClusterSnapshotResult(TypedDict, total=False):
    DBClusterSnapshot: Optional[DBClusterSnapshot]


class DeleteDBInstanceAutomatedBackupMessage(ServiceRequest):
    """Parameter input for the ``DeleteDBInstanceAutomatedBackup`` operation."""

    DbiResourceId: Optional[String]
    DBInstanceAutomatedBackupsArn: Optional[String]


class DeleteDBInstanceAutomatedBackupResult(TypedDict, total=False):
    DBInstanceAutomatedBackup: Optional[DBInstanceAutomatedBackup]


class DeleteDBInstanceMessage(ServiceRequest):
    DBInstanceIdentifier: String
    SkipFinalSnapshot: Optional[Boolean]
    FinalDBSnapshotIdentifier: Optional[String]
    DeleteAutomatedBackups: Optional[BooleanOptional]


class DeleteDBInstanceResult(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class DeleteDBParameterGroupMessage(ServiceRequest):
    DBParameterGroupName: String


class DeleteDBProxyEndpointRequest(ServiceRequest):
    DBProxyEndpointName: DBProxyEndpointName


class DeleteDBProxyEndpointResponse(TypedDict, total=False):
    DBProxyEndpoint: Optional[DBProxyEndpoint]


class DeleteDBProxyRequest(ServiceRequest):
    DBProxyName: String


class DeleteDBProxyResponse(TypedDict, total=False):
    DBProxy: Optional[DBProxy]


class DeleteDBSecurityGroupMessage(ServiceRequest):
    DBSecurityGroupName: String


class DeleteDBSnapshotMessage(ServiceRequest):
    DBSnapshotIdentifier: String


class DeleteDBSnapshotResult(TypedDict, total=False):
    DBSnapshot: Optional[DBSnapshot]


class DeleteDBSubnetGroupMessage(ServiceRequest):
    DBSubnetGroupName: String


class DeleteEventSubscriptionMessage(ServiceRequest):
    SubscriptionName: String


class DeleteEventSubscriptionResult(TypedDict, total=False):
    EventSubscription: Optional[EventSubscription]


class DeleteGlobalClusterMessage(ServiceRequest):
    GlobalClusterIdentifier: String


class DeleteGlobalClusterResult(TypedDict, total=False):
    GlobalCluster: Optional[GlobalCluster]


class DeleteOptionGroupMessage(ServiceRequest):
    OptionGroupName: String


class DeregisterDBProxyTargetsRequest(ServiceRequest):
    DBProxyName: String
    TargetGroupName: Optional[String]
    DBInstanceIdentifiers: Optional[StringList]
    DBClusterIdentifiers: Optional[StringList]


class DeregisterDBProxyTargetsResponse(TypedDict, total=False):
    pass


class DescribeAccountAttributesMessage(ServiceRequest):
    pass


FilterValueList = List[String]


class Filter(TypedDict, total=False):
    """A filter name and value pair that is used to return a more specific list
    of results from a describe operation. Filters can be used to match a set
    of resources by specific criteria, such as IDs. The filters supported by
    a describe operation are documented with the describe operation.

    Currently, wildcards are not supported in filters.

    The following actions can be filtered:

    -  ``DescribeDBClusterBacktracks``

    -  ``DescribeDBClusterEndpoints``

    -  ``DescribeDBClusters``

    -  ``DescribeDBInstances``

    -  ``DescribePendingMaintenanceActions``
    """

    Name: String
    Values: FilterValueList


FilterList = List[Filter]


class DescribeCertificatesMessage(ServiceRequest):
    CertificateIdentifier: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeDBClusterBacktracksMessage(ServiceRequest):
    DBClusterIdentifier: String
    BacktrackIdentifier: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeDBClusterEndpointsMessage(ServiceRequest):
    DBClusterIdentifier: Optional[String]
    DBClusterEndpointIdentifier: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeDBClusterParameterGroupsMessage(ServiceRequest):
    DBClusterParameterGroupName: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeDBClusterParametersMessage(ServiceRequest):
    DBClusterParameterGroupName: String
    Source: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeDBClusterSnapshotAttributesMessage(ServiceRequest):
    DBClusterSnapshotIdentifier: String


class DescribeDBClusterSnapshotAttributesResult(TypedDict, total=False):
    DBClusterSnapshotAttributesResult: Optional[DBClusterSnapshotAttributesResult]


class DescribeDBClusterSnapshotsMessage(ServiceRequest):
    DBClusterIdentifier: Optional[String]
    DBClusterSnapshotIdentifier: Optional[String]
    SnapshotType: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]
    IncludeShared: Optional[Boolean]
    IncludePublic: Optional[Boolean]


class DescribeDBClustersMessage(ServiceRequest):
    DBClusterIdentifier: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]
    IncludeShared: Optional[Boolean]


class DescribeDBEngineVersionsMessage(ServiceRequest):
    Engine: Optional[String]
    EngineVersion: Optional[String]
    DBParameterGroupFamily: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]
    DefaultOnly: Optional[Boolean]
    ListSupportedCharacterSets: Optional[BooleanOptional]
    ListSupportedTimezones: Optional[BooleanOptional]
    IncludeAll: Optional[BooleanOptional]


class DescribeDBInstanceAutomatedBackupsMessage(ServiceRequest):
    """Parameter input for DescribeDBInstanceAutomatedBackups."""

    DbiResourceId: Optional[String]
    DBInstanceIdentifier: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]
    DBInstanceAutomatedBackupsArn: Optional[String]


class DescribeDBInstancesMessage(ServiceRequest):
    DBInstanceIdentifier: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeDBLogFilesDetails(TypedDict, total=False):
    """This data type is used as a response element to ``DescribeDBLogFiles``."""

    LogFileName: Optional[String]
    LastWritten: Optional[Long]
    Size: Optional[Long]


DescribeDBLogFilesList = List[DescribeDBLogFilesDetails]


class DescribeDBLogFilesMessage(ServiceRequest):
    DBInstanceIdentifier: String
    FilenameContains: Optional[String]
    FileLastWritten: Optional[Long]
    FileSize: Optional[Long]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeDBLogFilesResponse(TypedDict, total=False):
    """The response from a call to ``DescribeDBLogFiles``."""

    DescribeDBLogFiles: Optional[DescribeDBLogFilesList]
    Marker: Optional[String]


class DescribeDBParameterGroupsMessage(ServiceRequest):
    DBParameterGroupName: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeDBParametersMessage(ServiceRequest):
    DBParameterGroupName: String
    Source: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeDBProxiesRequest(ServiceRequest):
    DBProxyName: Optional[String]
    Filters: Optional[FilterList]
    Marker: Optional[String]
    MaxRecords: Optional[MaxRecords]


class DescribeDBProxiesResponse(TypedDict, total=False):
    DBProxies: Optional[DBProxyList]
    Marker: Optional[String]


class DescribeDBProxyEndpointsRequest(ServiceRequest):
    DBProxyName: Optional[DBProxyName]
    DBProxyEndpointName: Optional[DBProxyEndpointName]
    Filters: Optional[FilterList]
    Marker: Optional[String]
    MaxRecords: Optional[MaxRecords]


class DescribeDBProxyEndpointsResponse(TypedDict, total=False):
    DBProxyEndpoints: Optional[DBProxyEndpointList]
    Marker: Optional[String]


class DescribeDBProxyTargetGroupsRequest(ServiceRequest):
    DBProxyName: String
    TargetGroupName: Optional[String]
    Filters: Optional[FilterList]
    Marker: Optional[String]
    MaxRecords: Optional[MaxRecords]


TargetGroupList = List[DBProxyTargetGroup]


class DescribeDBProxyTargetGroupsResponse(TypedDict, total=False):
    TargetGroups: Optional[TargetGroupList]
    Marker: Optional[String]


class DescribeDBProxyTargetsRequest(ServiceRequest):
    DBProxyName: String
    TargetGroupName: Optional[String]
    Filters: Optional[FilterList]
    Marker: Optional[String]
    MaxRecords: Optional[MaxRecords]


TargetList = List[DBProxyTarget]


class DescribeDBProxyTargetsResponse(TypedDict, total=False):
    Targets: Optional[TargetList]
    Marker: Optional[String]


class DescribeDBSecurityGroupsMessage(ServiceRequest):
    DBSecurityGroupName: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeDBSnapshotAttributesMessage(ServiceRequest):
    DBSnapshotIdentifier: String


class DescribeDBSnapshotAttributesResult(TypedDict, total=False):
    DBSnapshotAttributesResult: Optional[DBSnapshotAttributesResult]


class DescribeDBSnapshotsMessage(ServiceRequest):
    DBInstanceIdentifier: Optional[String]
    DBSnapshotIdentifier: Optional[String]
    SnapshotType: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]
    IncludeShared: Optional[Boolean]
    IncludePublic: Optional[Boolean]
    DbiResourceId: Optional[String]


class DescribeDBSubnetGroupsMessage(ServiceRequest):
    DBSubnetGroupName: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeEngineDefaultClusterParametersMessage(ServiceRequest):
    DBParameterGroupFamily: String
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class EngineDefaults(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeEngineDefaultParameters`` action.
    """

    DBParameterGroupFamily: Optional[String]
    Marker: Optional[String]
    Parameters: Optional[ParametersList]


class DescribeEngineDefaultClusterParametersResult(TypedDict, total=False):
    EngineDefaults: Optional[EngineDefaults]


class DescribeEngineDefaultParametersMessage(ServiceRequest):
    DBParameterGroupFamily: String
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeEngineDefaultParametersResult(TypedDict, total=False):
    EngineDefaults: Optional[EngineDefaults]


class DescribeEventCategoriesMessage(ServiceRequest):
    SourceType: Optional[String]
    Filters: Optional[FilterList]


class DescribeEventSubscriptionsMessage(ServiceRequest):
    SubscriptionName: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeEventsMessage(ServiceRequest):
    SourceIdentifier: Optional[String]
    SourceType: Optional[SourceType]
    StartTime: Optional[TStamp]
    EndTime: Optional[TStamp]
    Duration: Optional[IntegerOptional]
    EventCategories: Optional[EventCategoriesList]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeExportTasksMessage(ServiceRequest):
    ExportTaskIdentifier: Optional[String]
    SourceArn: Optional[String]
    Filters: Optional[FilterList]
    Marker: Optional[String]
    MaxRecords: Optional[MaxRecords]


class DescribeGlobalClustersMessage(ServiceRequest):
    GlobalClusterIdentifier: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeOptionGroupOptionsMessage(ServiceRequest):
    EngineName: String
    MajorEngineVersion: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeOptionGroupsMessage(ServiceRequest):
    OptionGroupName: Optional[String]
    Filters: Optional[FilterList]
    Marker: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    EngineName: Optional[String]
    MajorEngineVersion: Optional[String]


class DescribeOrderableDBInstanceOptionsMessage(ServiceRequest):
    Engine: String
    EngineVersion: Optional[String]
    DBInstanceClass: Optional[String]
    LicenseModel: Optional[String]
    AvailabilityZoneGroup: Optional[String]
    Vpc: Optional[BooleanOptional]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribePendingMaintenanceActionsMessage(ServiceRequest):
    ResourceIdentifier: Optional[String]
    Filters: Optional[FilterList]
    Marker: Optional[String]
    MaxRecords: Optional[IntegerOptional]


class DescribeReservedDBInstancesMessage(ServiceRequest):
    ReservedDBInstanceId: Optional[String]
    ReservedDBInstancesOfferingId: Optional[String]
    DBInstanceClass: Optional[String]
    Duration: Optional[String]
    ProductDescription: Optional[String]
    OfferingType: Optional[String]
    MultiAZ: Optional[BooleanOptional]
    LeaseId: Optional[String]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeReservedDBInstancesOfferingsMessage(ServiceRequest):
    ReservedDBInstancesOfferingId: Optional[String]
    DBInstanceClass: Optional[String]
    Duration: Optional[String]
    ProductDescription: Optional[String]
    OfferingType: Optional[String]
    MultiAZ: Optional[BooleanOptional]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeSourceRegionsMessage(ServiceRequest):
    RegionName: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]
    Filters: Optional[FilterList]


class DescribeValidDBInstanceModificationsMessage(ServiceRequest):
    DBInstanceIdentifier: String


class DoubleRange(TypedDict, total=False):
    """A range of double values."""

    From: Optional[Double]
    To: Optional[Double]


DoubleRangeList = List[DoubleRange]


class Range(TypedDict, total=False):
    """A range of integer values."""

    From: Optional[Integer]
    To: Optional[Integer]
    Step: Optional[IntegerOptional]


RangeList = List[Range]


class ValidStorageOptions(TypedDict, total=False):
    """Information about valid modifications that you can make to your DB
    instance. Contains the result of a successful call to the
    ``DescribeValidDBInstanceModifications`` action.
    """

    StorageType: Optional[String]
    StorageSize: Optional[RangeList]
    ProvisionedIops: Optional[RangeList]
    IopsToStorageRatio: Optional[DoubleRangeList]
    SupportsStorageAutoscaling: Optional[Boolean]


ValidStorageOptionsList = List[ValidStorageOptions]


class ValidDBInstanceModificationsMessage(TypedDict, total=False):
    """Information about valid modifications that you can make to your DB
    instance. Contains the result of a successful call to the
    ``DescribeValidDBInstanceModifications`` action. You can use this
    information when you call ``ModifyDBInstance``.
    """

    Storage: Optional[ValidStorageOptionsList]
    ValidProcessorFeatures: Optional[AvailableProcessorFeatureList]


class DescribeValidDBInstanceModificationsResult(TypedDict, total=False):
    ValidDBInstanceModificationsMessage: Optional[ValidDBInstanceModificationsMessage]


class DownloadDBLogFilePortionDetails(TypedDict, total=False):
    """This data type is used as a response element to
    ``DownloadDBLogFilePortion``.
    """

    LogFileData: Optional[String]
    Marker: Optional[String]
    AdditionalDataPending: Optional[Boolean]


class DownloadDBLogFilePortionMessage(ServiceRequest):
    DBInstanceIdentifier: String
    LogFileName: String
    Marker: Optional[String]
    NumberOfLines: Optional[Integer]


class Event(TypedDict, total=False):
    """This data type is used as a response element in the ``DescribeEvents``
    action.
    """

    SourceIdentifier: Optional[String]
    SourceType: Optional[SourceType]
    Message: Optional[String]
    EventCategories: Optional[EventCategoriesList]
    Date: Optional[TStamp]
    SourceArn: Optional[String]


class EventCategoriesMap(TypedDict, total=False):
    """Contains the results of a successful invocation of the
    ``DescribeEventCategories`` operation.
    """

    SourceType: Optional[String]
    EventCategories: Optional[EventCategoriesList]


EventCategoriesMapList = List[EventCategoriesMap]


class EventCategoriesMessage(TypedDict, total=False):
    """Data returned from the ``DescribeEventCategories`` operation."""

    EventCategoriesMapList: Optional[EventCategoriesMapList]


EventList = List[Event]
EventSubscriptionsList = List[EventSubscription]


class EventSubscriptionsMessage(TypedDict, total=False):
    """Data returned by the **DescribeEventSubscriptions** action."""

    Marker: Optional[String]
    EventSubscriptionsList: Optional[EventSubscriptionsList]


class EventsMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the ``DescribeEvents``
    action.
    """

    Marker: Optional[String]
    Events: Optional[EventList]


class ExportTask(TypedDict, total=False):
    """Contains the details of a snapshot export to Amazon S3.

    This data type is used as a response element in the
    ``DescribeExportTasks`` action.
    """

    ExportTaskIdentifier: Optional[String]
    SourceArn: Optional[String]
    ExportOnly: Optional[StringList]
    SnapshotTime: Optional[TStamp]
    TaskStartTime: Optional[TStamp]
    TaskEndTime: Optional[TStamp]
    S3Bucket: Optional[String]
    S3Prefix: Optional[String]
    IamRoleArn: Optional[String]
    KmsKeyId: Optional[String]
    Status: Optional[String]
    PercentProgress: Optional[Integer]
    TotalExtractedDataInGB: Optional[Integer]
    FailureCause: Optional[String]
    WarningMessage: Optional[String]


ExportTasksList = List[ExportTask]


class ExportTasksMessage(TypedDict, total=False):
    Marker: Optional[String]
    ExportTasks: Optional[ExportTasksList]


class FailoverDBClusterMessage(ServiceRequest):
    DBClusterIdentifier: String
    TargetDBInstanceIdentifier: Optional[String]


class FailoverDBClusterResult(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class FailoverGlobalClusterMessage(ServiceRequest):
    GlobalClusterIdentifier: GlobalClusterIdentifier
    TargetDbClusterIdentifier: DBClusterIdentifier


class FailoverGlobalClusterResult(TypedDict, total=False):
    GlobalCluster: Optional[GlobalCluster]


GlobalClusterList = List[GlobalCluster]


class GlobalClustersMessage(TypedDict, total=False):
    Marker: Optional[String]
    GlobalClusters: Optional[GlobalClusterList]


KeyList = List[String]


class ListTagsForResourceMessage(ServiceRequest):
    ResourceName: String
    Filters: Optional[FilterList]


class MinimumEngineVersionPerAllowedValue(TypedDict, total=False):
    """The minimum DB engine version required for each corresponding allowed
    value for an option setting.
    """

    AllowedValue: Optional[String]
    MinimumEngineVersion: Optional[String]


MinimumEngineVersionPerAllowedValueList = List[MinimumEngineVersionPerAllowedValue]


class ModifyCertificatesMessage(ServiceRequest):
    CertificateIdentifier: Optional[String]
    RemoveCustomerOverride: Optional[BooleanOptional]


class ModifyCertificatesResult(TypedDict, total=False):
    Certificate: Optional[Certificate]


class ModifyCurrentDBClusterCapacityMessage(ServiceRequest):
    DBClusterIdentifier: String
    Capacity: Optional[IntegerOptional]
    SecondsBeforeTimeout: Optional[IntegerOptional]
    TimeoutAction: Optional[String]


class ModifyCustomDBEngineVersionMessage(ServiceRequest):
    Engine: CustomEngineName
    EngineVersion: CustomEngineVersion
    Description: Optional[Description]
    Status: Optional[CustomEngineVersionStatus]


class ModifyDBClusterEndpointMessage(ServiceRequest):
    DBClusterEndpointIdentifier: String
    EndpointType: Optional[String]
    StaticMembers: Optional[StringList]
    ExcludedMembers: Optional[StringList]


class ModifyDBClusterMessage(ServiceRequest):
    DBClusterIdentifier: String
    NewDBClusterIdentifier: Optional[String]
    ApplyImmediately: Optional[Boolean]
    BackupRetentionPeriod: Optional[IntegerOptional]
    DBClusterParameterGroupName: Optional[String]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    Port: Optional[IntegerOptional]
    MasterUserPassword: Optional[String]
    OptionGroupName: Optional[String]
    PreferredBackupWindow: Optional[String]
    PreferredMaintenanceWindow: Optional[String]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    BacktrackWindow: Optional[LongOptional]
    CloudwatchLogsExportConfiguration: Optional[CloudwatchLogsExportConfiguration]
    EngineVersion: Optional[String]
    AllowMajorVersionUpgrade: Optional[Boolean]
    DBInstanceParameterGroupName: Optional[String]
    Domain: Optional[String]
    DomainIAMRoleName: Optional[String]
    ScalingConfiguration: Optional[ScalingConfiguration]
    DeletionProtection: Optional[BooleanOptional]
    EnableHttpEndpoint: Optional[BooleanOptional]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    EnableGlobalWriteForwarding: Optional[BooleanOptional]
    DBClusterInstanceClass: Optional[String]
    AllocatedStorage: Optional[IntegerOptional]
    StorageType: Optional[String]
    Iops: Optional[IntegerOptional]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    MonitoringInterval: Optional[IntegerOptional]
    MonitoringRoleArn: Optional[String]
    EnablePerformanceInsights: Optional[BooleanOptional]
    PerformanceInsightsKMSKeyId: Optional[String]
    PerformanceInsightsRetentionPeriod: Optional[IntegerOptional]
    ServerlessV2ScalingConfiguration: Optional[ServerlessV2ScalingConfiguration]


class ModifyDBClusterParameterGroupMessage(ServiceRequest):
    DBClusterParameterGroupName: String
    Parameters: ParametersList


class ModifyDBClusterResult(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class ModifyDBClusterSnapshotAttributeMessage(ServiceRequest):
    DBClusterSnapshotIdentifier: String
    AttributeName: String
    ValuesToAdd: Optional[AttributeValueList]
    ValuesToRemove: Optional[AttributeValueList]


class ModifyDBClusterSnapshotAttributeResult(TypedDict, total=False):
    DBClusterSnapshotAttributesResult: Optional[DBClusterSnapshotAttributesResult]


class ModifyDBInstanceMessage(ServiceRequest):
    DBInstanceIdentifier: String
    AllocatedStorage: Optional[IntegerOptional]
    DBInstanceClass: Optional[String]
    DBSubnetGroupName: Optional[String]
    DBSecurityGroups: Optional[DBSecurityGroupNameList]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    ApplyImmediately: Optional[Boolean]
    MasterUserPassword: Optional[String]
    DBParameterGroupName: Optional[String]
    BackupRetentionPeriod: Optional[IntegerOptional]
    PreferredBackupWindow: Optional[String]
    PreferredMaintenanceWindow: Optional[String]
    MultiAZ: Optional[BooleanOptional]
    EngineVersion: Optional[String]
    AllowMajorVersionUpgrade: Optional[Boolean]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    LicenseModel: Optional[String]
    Iops: Optional[IntegerOptional]
    OptionGroupName: Optional[String]
    NewDBInstanceIdentifier: Optional[String]
    StorageType: Optional[String]
    TdeCredentialArn: Optional[String]
    TdeCredentialPassword: Optional[String]
    CACertificateIdentifier: Optional[String]
    Domain: Optional[String]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    MonitoringInterval: Optional[IntegerOptional]
    DBPortNumber: Optional[IntegerOptional]
    PubliclyAccessible: Optional[BooleanOptional]
    MonitoringRoleArn: Optional[String]
    DomainIAMRoleName: Optional[String]
    PromotionTier: Optional[IntegerOptional]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    EnablePerformanceInsights: Optional[BooleanOptional]
    PerformanceInsightsKMSKeyId: Optional[String]
    PerformanceInsightsRetentionPeriod: Optional[IntegerOptional]
    CloudwatchLogsExportConfiguration: Optional[CloudwatchLogsExportConfiguration]
    ProcessorFeatures: Optional[ProcessorFeatureList]
    UseDefaultProcessorFeatures: Optional[BooleanOptional]
    DeletionProtection: Optional[BooleanOptional]
    MaxAllocatedStorage: Optional[IntegerOptional]
    CertificateRotationRestart: Optional[BooleanOptional]
    ReplicaMode: Optional[ReplicaMode]
    EnableCustomerOwnedIp: Optional[BooleanOptional]
    AwsBackupRecoveryPointArn: Optional[AwsBackupRecoveryPointArn]
    AutomationMode: Optional[AutomationMode]
    ResumeFullAutomationModeMinutes: Optional[IntegerOptional]
    NetworkType: Optional[String]


class ModifyDBInstanceResult(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class ModifyDBParameterGroupMessage(ServiceRequest):
    DBParameterGroupName: String
    Parameters: ParametersList


class ModifyDBProxyEndpointRequest(ServiceRequest):
    DBProxyEndpointName: DBProxyEndpointName
    NewDBProxyEndpointName: Optional[DBProxyEndpointName]
    VpcSecurityGroupIds: Optional[StringList]


class ModifyDBProxyEndpointResponse(TypedDict, total=False):
    DBProxyEndpoint: Optional[DBProxyEndpoint]


class ModifyDBProxyRequest(ServiceRequest):
    DBProxyName: String
    NewDBProxyName: Optional[String]
    Auth: Optional[UserAuthConfigList]
    RequireTLS: Optional[BooleanOptional]
    IdleClientTimeout: Optional[IntegerOptional]
    DebugLogging: Optional[BooleanOptional]
    RoleArn: Optional[String]
    SecurityGroups: Optional[StringList]


class ModifyDBProxyResponse(TypedDict, total=False):
    DBProxy: Optional[DBProxy]


class ModifyDBProxyTargetGroupRequest(ServiceRequest):
    TargetGroupName: String
    DBProxyName: String
    ConnectionPoolConfig: Optional[ConnectionPoolConfiguration]
    NewName: Optional[String]


class ModifyDBProxyTargetGroupResponse(TypedDict, total=False):
    DBProxyTargetGroup: Optional[DBProxyTargetGroup]


class ModifyDBSnapshotAttributeMessage(ServiceRequest):
    DBSnapshotIdentifier: String
    AttributeName: String
    ValuesToAdd: Optional[AttributeValueList]
    ValuesToRemove: Optional[AttributeValueList]


class ModifyDBSnapshotAttributeResult(TypedDict, total=False):
    DBSnapshotAttributesResult: Optional[DBSnapshotAttributesResult]


class ModifyDBSnapshotMessage(ServiceRequest):
    DBSnapshotIdentifier: String
    EngineVersion: Optional[String]
    OptionGroupName: Optional[String]


class ModifyDBSnapshotResult(TypedDict, total=False):
    DBSnapshot: Optional[DBSnapshot]


class ModifyDBSubnetGroupMessage(ServiceRequest):
    DBSubnetGroupName: String
    DBSubnetGroupDescription: Optional[String]
    SubnetIds: SubnetIdentifierList


class ModifyDBSubnetGroupResult(TypedDict, total=False):
    DBSubnetGroup: Optional[DBSubnetGroup]


class ModifyEventSubscriptionMessage(ServiceRequest):
    SubscriptionName: String
    SnsTopicArn: Optional[String]
    SourceType: Optional[String]
    EventCategories: Optional[EventCategoriesList]
    Enabled: Optional[BooleanOptional]


class ModifyEventSubscriptionResult(TypedDict, total=False):
    EventSubscription: Optional[EventSubscription]


class ModifyGlobalClusterMessage(ServiceRequest):
    GlobalClusterIdentifier: Optional[String]
    NewGlobalClusterIdentifier: Optional[String]
    DeletionProtection: Optional[BooleanOptional]
    EngineVersion: Optional[String]
    AllowMajorVersionUpgrade: Optional[BooleanOptional]


class ModifyGlobalClusterResult(TypedDict, total=False):
    GlobalCluster: Optional[GlobalCluster]


OptionNamesList = List[String]
OptionSettingsList = List[OptionSetting]


class OptionConfiguration(TypedDict, total=False):
    """A list of all available options"""

    OptionName: String
    Port: Optional[IntegerOptional]
    OptionVersion: Optional[String]
    DBSecurityGroupMemberships: Optional[DBSecurityGroupNameList]
    VpcSecurityGroupMemberships: Optional[VpcSecurityGroupIdList]
    OptionSettings: Optional[OptionSettingsList]


OptionConfigurationList = List[OptionConfiguration]


class ModifyOptionGroupMessage(ServiceRequest):
    OptionGroupName: String
    OptionsToInclude: Optional[OptionConfigurationList]
    OptionsToRemove: Optional[OptionNamesList]
    ApplyImmediately: Optional[Boolean]


class ModifyOptionGroupResult(TypedDict, total=False):
    OptionGroup: Optional[OptionGroup]


class OptionVersion(TypedDict, total=False):
    """The version for an option. Option group option versions are returned by
    the ``DescribeOptionGroupOptions`` action.
    """

    Version: Optional[String]
    IsDefault: Optional[Boolean]


OptionGroupOptionVersionsList = List[OptionVersion]


class OptionGroupOptionSetting(TypedDict, total=False):
    """Option group option settings are used to display settings available for
    each option with their default values and other information. These
    values are used with the DescribeOptionGroupOptions action.
    """

    SettingName: Optional[String]
    SettingDescription: Optional[String]
    DefaultValue: Optional[String]
    ApplyType: Optional[String]
    AllowedValues: Optional[String]
    IsModifiable: Optional[Boolean]
    IsRequired: Optional[Boolean]
    MinimumEngineVersionPerAllowedValue: Optional[MinimumEngineVersionPerAllowedValueList]


OptionGroupOptionSettingsList = List[OptionGroupOptionSetting]
OptionsConflictsWith = List[String]
OptionsDependedOn = List[String]


class OptionGroupOption(TypedDict, total=False):
    """Available option."""

    Name: Optional[String]
    Description: Optional[String]
    EngineName: Optional[String]
    MajorEngineVersion: Optional[String]
    MinimumRequiredMinorEngineVersion: Optional[String]
    PortRequired: Optional[Boolean]
    DefaultPort: Optional[IntegerOptional]
    OptionsDependedOn: Optional[OptionsDependedOn]
    OptionsConflictsWith: Optional[OptionsConflictsWith]
    Persistent: Optional[Boolean]
    Permanent: Optional[Boolean]
    RequiresAutoMinorEngineVersionUpgrade: Optional[Boolean]
    VpcOnly: Optional[Boolean]
    SupportsOptionVersionDowngrade: Optional[BooleanOptional]
    OptionGroupOptionSettings: Optional[OptionGroupOptionSettingsList]
    OptionGroupOptionVersions: Optional[OptionGroupOptionVersionsList]


OptionGroupOptionsList = List[OptionGroupOption]


class OptionGroupOptionsMessage(TypedDict, total=False):
    OptionGroupOptions: Optional[OptionGroupOptionsList]
    Marker: Optional[String]


OptionGroupsList = List[OptionGroup]


class OptionGroups(TypedDict, total=False):
    """List of option groups."""

    OptionGroupsList: Optional[OptionGroupsList]
    Marker: Optional[String]


class OrderableDBInstanceOption(TypedDict, total=False):
    """Contains a list of available options for a DB instance.

    This data type is used as a response element in the
    ``DescribeOrderableDBInstanceOptions`` action.
    """

    Engine: Optional[String]
    EngineVersion: Optional[String]
    DBInstanceClass: Optional[String]
    LicenseModel: Optional[String]
    AvailabilityZoneGroup: Optional[String]
    AvailabilityZones: Optional[AvailabilityZoneList]
    MultiAZCapable: Optional[Boolean]
    ReadReplicaCapable: Optional[Boolean]
    Vpc: Optional[Boolean]
    SupportsStorageEncryption: Optional[Boolean]
    StorageType: Optional[String]
    SupportsIops: Optional[Boolean]
    SupportsEnhancedMonitoring: Optional[Boolean]
    SupportsIAMDatabaseAuthentication: Optional[Boolean]
    SupportsPerformanceInsights: Optional[Boolean]
    MinStorageSize: Optional[IntegerOptional]
    MaxStorageSize: Optional[IntegerOptional]
    MinIopsPerDbInstance: Optional[IntegerOptional]
    MaxIopsPerDbInstance: Optional[IntegerOptional]
    MinIopsPerGib: Optional[DoubleOptional]
    MaxIopsPerGib: Optional[DoubleOptional]
    AvailableProcessorFeatures: Optional[AvailableProcessorFeatureList]
    SupportedEngineModes: Optional[EngineModeList]
    SupportsStorageAutoscaling: Optional[BooleanOptional]
    SupportsKerberosAuthentication: Optional[BooleanOptional]
    OutpostCapable: Optional[Boolean]
    SupportedActivityStreamModes: Optional[ActivityStreamModeList]
    SupportsGlobalDatabases: Optional[Boolean]
    SupportsClusters: Optional[Boolean]
    SupportedNetworkTypes: Optional[StringList]


OrderableDBInstanceOptionsList = List[OrderableDBInstanceOption]


class OrderableDBInstanceOptionsMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeOrderableDBInstanceOptions`` action.
    """

    OrderableDBInstanceOptions: Optional[OrderableDBInstanceOptionsList]
    Marker: Optional[String]


PendingMaintenanceActions = List[ResourcePendingMaintenanceActions]


class PendingMaintenanceActionsMessage(TypedDict, total=False):
    """Data returned from the **DescribePendingMaintenanceActions** action."""

    PendingMaintenanceActions: Optional[PendingMaintenanceActions]
    Marker: Optional[String]


class PromoteReadReplicaDBClusterMessage(ServiceRequest):
    DBClusterIdentifier: String


class PromoteReadReplicaDBClusterResult(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class PromoteReadReplicaMessage(ServiceRequest):
    DBInstanceIdentifier: String
    BackupRetentionPeriod: Optional[IntegerOptional]
    PreferredBackupWindow: Optional[String]


class PromoteReadReplicaResult(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class PurchaseReservedDBInstancesOfferingMessage(ServiceRequest):
    ReservedDBInstancesOfferingId: String
    ReservedDBInstanceId: Optional[String]
    DBInstanceCount: Optional[IntegerOptional]
    Tags: Optional[TagList]


class RecurringCharge(TypedDict, total=False):
    """This data type is used as a response element in the
    ``DescribeReservedDBInstances`` and
    ``DescribeReservedDBInstancesOfferings`` actions.
    """

    RecurringChargeAmount: Optional[Double]
    RecurringChargeFrequency: Optional[String]


RecurringChargeList = List[RecurringCharge]


class ReservedDBInstance(TypedDict, total=False):
    """This data type is used as a response element in the
    ``DescribeReservedDBInstances`` and
    ``PurchaseReservedDBInstancesOffering`` actions.
    """

    ReservedDBInstanceId: Optional[String]
    ReservedDBInstancesOfferingId: Optional[String]
    DBInstanceClass: Optional[String]
    StartTime: Optional[TStamp]
    Duration: Optional[Integer]
    FixedPrice: Optional[Double]
    UsagePrice: Optional[Double]
    CurrencyCode: Optional[String]
    DBInstanceCount: Optional[Integer]
    ProductDescription: Optional[String]
    OfferingType: Optional[String]
    MultiAZ: Optional[Boolean]
    State: Optional[String]
    RecurringCharges: Optional[RecurringChargeList]
    ReservedDBInstanceArn: Optional[String]
    LeaseId: Optional[String]


class PurchaseReservedDBInstancesOfferingResult(TypedDict, total=False):
    ReservedDBInstance: Optional[ReservedDBInstance]


class RebootDBClusterMessage(ServiceRequest):
    DBClusterIdentifier: String


class RebootDBClusterResult(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class RebootDBInstanceMessage(ServiceRequest):
    DBInstanceIdentifier: String
    ForceFailover: Optional[BooleanOptional]


class RebootDBInstanceResult(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class RegisterDBProxyTargetsRequest(ServiceRequest):
    DBProxyName: String
    TargetGroupName: Optional[String]
    DBInstanceIdentifiers: Optional[StringList]
    DBClusterIdentifiers: Optional[StringList]


class RegisterDBProxyTargetsResponse(TypedDict, total=False):
    DBProxyTargets: Optional[TargetList]


class RemoveFromGlobalClusterMessage(ServiceRequest):
    GlobalClusterIdentifier: Optional[String]
    DbClusterIdentifier: Optional[String]


class RemoveFromGlobalClusterResult(TypedDict, total=False):
    GlobalCluster: Optional[GlobalCluster]


class RemoveRoleFromDBClusterMessage(ServiceRequest):
    DBClusterIdentifier: String
    RoleArn: String
    FeatureName: Optional[String]


class RemoveRoleFromDBInstanceMessage(ServiceRequest):
    DBInstanceIdentifier: String
    RoleArn: String
    FeatureName: String


class RemoveSourceIdentifierFromSubscriptionMessage(ServiceRequest):
    SubscriptionName: String
    SourceIdentifier: String


class RemoveSourceIdentifierFromSubscriptionResult(TypedDict, total=False):
    EventSubscription: Optional[EventSubscription]


class RemoveTagsFromResourceMessage(ServiceRequest):
    ResourceName: String
    TagKeys: KeyList


ReservedDBInstanceList = List[ReservedDBInstance]


class ReservedDBInstanceMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeReservedDBInstances`` action.
    """

    Marker: Optional[String]
    ReservedDBInstances: Optional[ReservedDBInstanceList]


class ReservedDBInstancesOffering(TypedDict, total=False):
    """This data type is used as a response element in the
    ``DescribeReservedDBInstancesOfferings`` action.
    """

    ReservedDBInstancesOfferingId: Optional[String]
    DBInstanceClass: Optional[String]
    Duration: Optional[Integer]
    FixedPrice: Optional[Double]
    UsagePrice: Optional[Double]
    CurrencyCode: Optional[String]
    ProductDescription: Optional[String]
    OfferingType: Optional[String]
    MultiAZ: Optional[Boolean]
    RecurringCharges: Optional[RecurringChargeList]


ReservedDBInstancesOfferingList = List[ReservedDBInstancesOffering]


class ReservedDBInstancesOfferingMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeReservedDBInstancesOfferings`` action.
    """

    Marker: Optional[String]
    ReservedDBInstancesOfferings: Optional[ReservedDBInstancesOfferingList]


class ResetDBClusterParameterGroupMessage(ServiceRequest):
    DBClusterParameterGroupName: String
    ResetAllParameters: Optional[Boolean]
    Parameters: Optional[ParametersList]


class ResetDBParameterGroupMessage(ServiceRequest):
    DBParameterGroupName: String
    ResetAllParameters: Optional[Boolean]
    Parameters: Optional[ParametersList]


class RestoreDBClusterFromS3Message(ServiceRequest):
    AvailabilityZones: Optional[AvailabilityZones]
    BackupRetentionPeriod: Optional[IntegerOptional]
    CharacterSetName: Optional[String]
    DatabaseName: Optional[String]
    DBClusterIdentifier: String
    DBClusterParameterGroupName: Optional[String]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    DBSubnetGroupName: Optional[String]
    Engine: String
    EngineVersion: Optional[String]
    Port: Optional[IntegerOptional]
    MasterUsername: String
    MasterUserPassword: String
    OptionGroupName: Optional[String]
    PreferredBackupWindow: Optional[String]
    PreferredMaintenanceWindow: Optional[String]
    Tags: Optional[TagList]
    StorageEncrypted: Optional[BooleanOptional]
    KmsKeyId: Optional[String]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    SourceEngine: String
    SourceEngineVersion: String
    S3BucketName: String
    S3Prefix: Optional[String]
    S3IngestionRoleArn: String
    BacktrackWindow: Optional[LongOptional]
    EnableCloudwatchLogsExports: Optional[LogTypeList]
    DeletionProtection: Optional[BooleanOptional]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    Domain: Optional[String]
    DomainIAMRoleName: Optional[String]
    ServerlessV2ScalingConfiguration: Optional[ServerlessV2ScalingConfiguration]


class RestoreDBClusterFromS3Result(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class RestoreDBClusterFromSnapshotMessage(ServiceRequest):
    AvailabilityZones: Optional[AvailabilityZones]
    DBClusterIdentifier: String
    SnapshotIdentifier: String
    Engine: String
    EngineVersion: Optional[String]
    Port: Optional[IntegerOptional]
    DBSubnetGroupName: Optional[String]
    DatabaseName: Optional[String]
    OptionGroupName: Optional[String]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    Tags: Optional[TagList]
    KmsKeyId: Optional[String]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    BacktrackWindow: Optional[LongOptional]
    EnableCloudwatchLogsExports: Optional[LogTypeList]
    EngineMode: Optional[String]
    ScalingConfiguration: Optional[ScalingConfiguration]
    DBClusterParameterGroupName: Optional[String]
    DeletionProtection: Optional[BooleanOptional]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    Domain: Optional[String]
    DomainIAMRoleName: Optional[String]
    DBClusterInstanceClass: Optional[String]
    StorageType: Optional[String]
    Iops: Optional[IntegerOptional]
    PubliclyAccessible: Optional[BooleanOptional]
    ServerlessV2ScalingConfiguration: Optional[ServerlessV2ScalingConfiguration]


class RestoreDBClusterFromSnapshotResult(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class RestoreDBClusterToPointInTimeMessage(ServiceRequest):
    DBClusterIdentifier: String
    RestoreType: Optional[String]
    SourceDBClusterIdentifier: String
    RestoreToTime: Optional[TStamp]
    UseLatestRestorableTime: Optional[Boolean]
    Port: Optional[IntegerOptional]
    DBSubnetGroupName: Optional[String]
    OptionGroupName: Optional[String]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    Tags: Optional[TagList]
    KmsKeyId: Optional[String]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    BacktrackWindow: Optional[LongOptional]
    EnableCloudwatchLogsExports: Optional[LogTypeList]
    DBClusterParameterGroupName: Optional[String]
    DeletionProtection: Optional[BooleanOptional]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    Domain: Optional[String]
    DomainIAMRoleName: Optional[String]
    ScalingConfiguration: Optional[ScalingConfiguration]
    EngineMode: Optional[String]
    DBClusterInstanceClass: Optional[String]
    StorageType: Optional[String]
    PubliclyAccessible: Optional[BooleanOptional]
    Iops: Optional[IntegerOptional]
    ServerlessV2ScalingConfiguration: Optional[ServerlessV2ScalingConfiguration]


class RestoreDBClusterToPointInTimeResult(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class RestoreDBInstanceFromDBSnapshotMessage(ServiceRequest):
    DBInstanceIdentifier: String
    DBSnapshotIdentifier: String
    DBInstanceClass: Optional[String]
    Port: Optional[IntegerOptional]
    AvailabilityZone: Optional[String]
    DBSubnetGroupName: Optional[String]
    MultiAZ: Optional[BooleanOptional]
    PubliclyAccessible: Optional[BooleanOptional]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    LicenseModel: Optional[String]
    DBName: Optional[String]
    Engine: Optional[String]
    Iops: Optional[IntegerOptional]
    OptionGroupName: Optional[String]
    Tags: Optional[TagList]
    StorageType: Optional[String]
    TdeCredentialArn: Optional[String]
    TdeCredentialPassword: Optional[String]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    Domain: Optional[String]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    DomainIAMRoleName: Optional[String]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    EnableCloudwatchLogsExports: Optional[LogTypeList]
    ProcessorFeatures: Optional[ProcessorFeatureList]
    UseDefaultProcessorFeatures: Optional[BooleanOptional]
    DBParameterGroupName: Optional[String]
    DeletionProtection: Optional[BooleanOptional]
    EnableCustomerOwnedIp: Optional[BooleanOptional]
    CustomIamInstanceProfile: Optional[String]
    BackupTarget: Optional[String]
    NetworkType: Optional[String]


class RestoreDBInstanceFromDBSnapshotResult(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class RestoreDBInstanceFromS3Message(ServiceRequest):
    DBName: Optional[String]
    DBInstanceIdentifier: String
    AllocatedStorage: Optional[IntegerOptional]
    DBInstanceClass: String
    Engine: String
    MasterUsername: Optional[String]
    MasterUserPassword: Optional[String]
    DBSecurityGroups: Optional[DBSecurityGroupNameList]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    AvailabilityZone: Optional[String]
    DBSubnetGroupName: Optional[String]
    PreferredMaintenanceWindow: Optional[String]
    DBParameterGroupName: Optional[String]
    BackupRetentionPeriod: Optional[IntegerOptional]
    PreferredBackupWindow: Optional[String]
    Port: Optional[IntegerOptional]
    MultiAZ: Optional[BooleanOptional]
    EngineVersion: Optional[String]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    LicenseModel: Optional[String]
    Iops: Optional[IntegerOptional]
    OptionGroupName: Optional[String]
    PubliclyAccessible: Optional[BooleanOptional]
    Tags: Optional[TagList]
    StorageType: Optional[String]
    StorageEncrypted: Optional[BooleanOptional]
    KmsKeyId: Optional[String]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    MonitoringInterval: Optional[IntegerOptional]
    MonitoringRoleArn: Optional[String]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    SourceEngine: String
    SourceEngineVersion: String
    S3BucketName: String
    S3Prefix: Optional[String]
    S3IngestionRoleArn: String
    EnablePerformanceInsights: Optional[BooleanOptional]
    PerformanceInsightsKMSKeyId: Optional[String]
    PerformanceInsightsRetentionPeriod: Optional[IntegerOptional]
    EnableCloudwatchLogsExports: Optional[LogTypeList]
    ProcessorFeatures: Optional[ProcessorFeatureList]
    UseDefaultProcessorFeatures: Optional[BooleanOptional]
    DeletionProtection: Optional[BooleanOptional]
    MaxAllocatedStorage: Optional[IntegerOptional]
    NetworkType: Optional[String]


class RestoreDBInstanceFromS3Result(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class RestoreDBInstanceToPointInTimeMessage(ServiceRequest):
    SourceDBInstanceIdentifier: Optional[String]
    TargetDBInstanceIdentifier: String
    RestoreTime: Optional[TStamp]
    UseLatestRestorableTime: Optional[Boolean]
    DBInstanceClass: Optional[String]
    Port: Optional[IntegerOptional]
    AvailabilityZone: Optional[String]
    DBSubnetGroupName: Optional[String]
    MultiAZ: Optional[BooleanOptional]
    PubliclyAccessible: Optional[BooleanOptional]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    LicenseModel: Optional[String]
    DBName: Optional[String]
    Engine: Optional[String]
    Iops: Optional[IntegerOptional]
    OptionGroupName: Optional[String]
    CopyTagsToSnapshot: Optional[BooleanOptional]
    Tags: Optional[TagList]
    StorageType: Optional[String]
    TdeCredentialArn: Optional[String]
    TdeCredentialPassword: Optional[String]
    VpcSecurityGroupIds: Optional[VpcSecurityGroupIdList]
    Domain: Optional[String]
    DomainIAMRoleName: Optional[String]
    EnableIAMDatabaseAuthentication: Optional[BooleanOptional]
    EnableCloudwatchLogsExports: Optional[LogTypeList]
    ProcessorFeatures: Optional[ProcessorFeatureList]
    UseDefaultProcessorFeatures: Optional[BooleanOptional]
    DBParameterGroupName: Optional[String]
    DeletionProtection: Optional[BooleanOptional]
    SourceDbiResourceId: Optional[String]
    MaxAllocatedStorage: Optional[IntegerOptional]
    SourceDBInstanceAutomatedBackupsArn: Optional[String]
    EnableCustomerOwnedIp: Optional[BooleanOptional]
    CustomIamInstanceProfile: Optional[String]
    BackupTarget: Optional[String]
    NetworkType: Optional[String]


class RestoreDBInstanceToPointInTimeResult(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class RevokeDBSecurityGroupIngressMessage(ServiceRequest):
    DBSecurityGroupName: String
    CIDRIP: Optional[String]
    EC2SecurityGroupName: Optional[String]
    EC2SecurityGroupId: Optional[String]
    EC2SecurityGroupOwnerId: Optional[String]


class RevokeDBSecurityGroupIngressResult(TypedDict, total=False):
    DBSecurityGroup: Optional[DBSecurityGroup]


class SourceRegion(TypedDict, total=False):
    """Contains an Amazon Web Services Region name as the result of a
    successful call to the ``DescribeSourceRegions`` action.
    """

    RegionName: Optional[String]
    Endpoint: Optional[String]
    Status: Optional[String]
    SupportsDBInstanceAutomatedBackupsReplication: Optional[Boolean]


SourceRegionList = List[SourceRegion]


class SourceRegionMessage(TypedDict, total=False):
    """Contains the result of a successful invocation of the
    ``DescribeSourceRegions`` action.
    """

    Marker: Optional[String]
    SourceRegions: Optional[SourceRegionList]


class StartActivityStreamRequest(ServiceRequest):
    ResourceArn: String
    Mode: ActivityStreamMode
    KmsKeyId: String
    ApplyImmediately: Optional[BooleanOptional]
    EngineNativeAuditFieldsIncluded: Optional[BooleanOptional]


class StartActivityStreamResponse(TypedDict, total=False):
    KmsKeyId: Optional[String]
    KinesisStreamName: Optional[String]
    Status: Optional[ActivityStreamStatus]
    Mode: Optional[ActivityStreamMode]
    ApplyImmediately: Optional[Boolean]
    EngineNativeAuditFieldsIncluded: Optional[BooleanOptional]


class StartDBClusterMessage(ServiceRequest):
    DBClusterIdentifier: String


class StartDBClusterResult(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class StartDBInstanceAutomatedBackupsReplicationMessage(ServiceRequest):
    SourceDBInstanceArn: String
    BackupRetentionPeriod: Optional[IntegerOptional]
    KmsKeyId: Optional[String]
    PreSignedUrl: Optional[String]
    SourceRegion: Optional[String]


class StartDBInstanceAutomatedBackupsReplicationResult(TypedDict, total=False):
    DBInstanceAutomatedBackup: Optional[DBInstanceAutomatedBackup]


class StartDBInstanceMessage(ServiceRequest):
    DBInstanceIdentifier: String


class StartDBInstanceResult(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class StartExportTaskMessage(ServiceRequest):
    ExportTaskIdentifier: String
    SourceArn: String
    S3BucketName: String
    IamRoleArn: String
    KmsKeyId: String
    S3Prefix: Optional[String]
    ExportOnly: Optional[StringList]


class StopActivityStreamRequest(ServiceRequest):
    ResourceArn: String
    ApplyImmediately: Optional[BooleanOptional]


class StopActivityStreamResponse(TypedDict, total=False):
    KmsKeyId: Optional[String]
    KinesisStreamName: Optional[String]
    Status: Optional[ActivityStreamStatus]


class StopDBClusterMessage(ServiceRequest):
    DBClusterIdentifier: String


class StopDBClusterResult(TypedDict, total=False):
    DBCluster: Optional[DBCluster]


class StopDBInstanceAutomatedBackupsReplicationMessage(ServiceRequest):
    SourceDBInstanceArn: String


class StopDBInstanceAutomatedBackupsReplicationResult(TypedDict, total=False):
    DBInstanceAutomatedBackup: Optional[DBInstanceAutomatedBackup]


class StopDBInstanceMessage(ServiceRequest):
    DBInstanceIdentifier: String
    DBSnapshotIdentifier: Optional[String]


class StopDBInstanceResult(TypedDict, total=False):
    DBInstance: Optional[DBInstance]


class TagListMessage(TypedDict, total=False):
    TagList: Optional[TagList]


class RdsApi:

    service = "rds"
    version = "2014-10-31"

    @handler("AddRoleToDBCluster")
    def add_role_to_db_cluster(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        role_arn: String,
        feature_name: String = None,
    ) -> None:
        """Associates an Identity and Access Management (IAM) role with a DB
        cluster.

        :param db_cluster_identifier: The name of the DB cluster to associate the IAM role with.
        :param role_arn: The Amazon Resource Name (ARN) of the IAM role to associate with the
        Aurora DB cluster, for example
        ``arn:aws:iam::123456789012:role/AuroraAccessRole``.
        :param feature_name: The name of the feature for the DB cluster that the IAM role is to be
        associated with.
        :raises DBClusterNotFoundFault:
        :raises DBClusterRoleAlreadyExistsFault:
        :raises InvalidDBClusterStateFault:
        :raises DBClusterRoleQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("AddRoleToDBInstance")
    def add_role_to_db_instance(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        role_arn: String,
        feature_name: String,
    ) -> None:
        """Associates an Amazon Web Services Identity and Access Management (IAM)
        role with a DB instance.

        To add a role to a DB instance, the status of the DB instance must be
        ``available``.

        This command doesn't apply to RDS Custom.

        :param db_instance_identifier: The name of the DB instance to associate the IAM role with.
        :param role_arn: The Amazon Resource Name (ARN) of the IAM role to associate with the DB
        instance, for example ``arn:aws:iam::123456789012:role/AccessRole``.
        :param feature_name: The name of the feature for the DB instance that the IAM role is to be
        associated with.
        :raises DBInstanceNotFoundFault:
        :raises DBInstanceRoleAlreadyExistsFault:
        :raises InvalidDBInstanceStateFault:
        :raises DBInstanceRoleQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("AddSourceIdentifierToSubscription")
    def add_source_identifier_to_subscription(
        self, context: RequestContext, subscription_name: String, source_identifier: String
    ) -> AddSourceIdentifierToSubscriptionResult:
        """Adds a source identifier to an existing RDS event notification
        subscription.

        :param subscription_name: The name of the RDS event notification subscription you want to add a
        source identifier to.
        :param source_identifier: The identifier of the event source to be added.
        :returns: AddSourceIdentifierToSubscriptionResult
        :raises SubscriptionNotFoundFault:
        :raises SourceNotFoundFault:
        """
        raise NotImplementedError

    @handler("AddTagsToResource")
    def add_tags_to_resource(
        self, context: RequestContext, resource_name: String, tags: TagList
    ) -> None:
        """Adds metadata tags to an Amazon RDS resource. These tags can also be
        used with cost allocation reporting to track cost associated with Amazon
        RDS resources, or used in a Condition statement in an IAM policy for
        Amazon RDS.

        For an overview on tagging Amazon RDS resources, see `Tagging Amazon RDS
        Resources <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Tagging.html>`__.

        :param resource_name: The Amazon RDS resource that the tags are added to.
        :param tags: The tags to be assigned to the Amazon RDS resource.
        :raises DBInstanceNotFoundFault:
        :raises DBClusterNotFoundFault:
        :raises DBSnapshotNotFoundFault:
        :raises DBProxyNotFoundFault:
        :raises DBProxyTargetGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("ApplyPendingMaintenanceAction")
    def apply_pending_maintenance_action(
        self,
        context: RequestContext,
        resource_identifier: String,
        apply_action: String,
        opt_in_type: String,
    ) -> ApplyPendingMaintenanceActionResult:
        """Applies a pending maintenance action to a resource (for example, to a DB
        instance).

        :param resource_identifier: The RDS Amazon Resource Name (ARN) of the resource that the pending
        maintenance action applies to.
        :param apply_action: The pending maintenance action to apply to this resource.
        :param opt_in_type: A value that specifies the type of opt-in request, or undoes an opt-in
        request.
        :returns: ApplyPendingMaintenanceActionResult
        :raises ResourceNotFoundFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError

    @handler("AuthorizeDBSecurityGroupIngress")
    def authorize_db_security_group_ingress(
        self,
        context: RequestContext,
        db_security_group_name: String,
        cidrip: String = None,
        ec2_security_group_name: String = None,
        ec2_security_group_id: String = None,
        ec2_security_group_owner_id: String = None,
    ) -> AuthorizeDBSecurityGroupIngressResult:
        """Enables ingress to a DBSecurityGroup using one of two forms of
        authorization. First, EC2 or VPC security groups can be added to the
        DBSecurityGroup if the application using the database is running on EC2
        or VPC instances. Second, IP ranges are available if the application
        accessing your database is running on the internet. Required parameters
        for this API are one of CIDR range, EC2SecurityGroupId for VPC, or
        (EC2SecurityGroupOwnerId and either EC2SecurityGroupName or
        EC2SecurityGroupId for non-VPC).

        You can't authorize ingress from an EC2 security group in one Amazon Web
        Services Region to an Amazon RDS DB instance in another. You can't
        authorize ingress from a VPC security group in one VPC to an Amazon RDS
        DB instance in another.

        For an overview of CIDR ranges, go to the `Wikipedia
        Tutorial <http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing>`__.

        :param db_security_group_name: The name of the DB security group to add authorization to.
        :param cidrip: The IP range to authorize.
        :param ec2_security_group_name: Name of the EC2 security group to authorize.
        :param ec2_security_group_id: Id of the EC2 security group to authorize.
        :param ec2_security_group_owner_id: Amazon Web Services account number of the owner of the EC2 security
        group specified in the ``EC2SecurityGroupName`` parameter.
        :returns: AuthorizeDBSecurityGroupIngressResult
        :raises DBSecurityGroupNotFoundFault:
        :raises InvalidDBSecurityGroupStateFault:
        :raises AuthorizationAlreadyExistsFault:
        :raises AuthorizationQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("BacktrackDBCluster")
    def backtrack_db_cluster(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        backtrack_to: TStamp,
        force: BooleanOptional = None,
        use_earliest_time_on_point_in_time_unavailable: BooleanOptional = None,
    ) -> DBClusterBacktrack:
        """Backtracks a DB cluster to a specific time, without creating a new DB
        cluster.

        For more information on backtracking, see `Backtracking an Aurora DB
        Cluster <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Managing.Backtrack.html>`__
        in the *Amazon Aurora User Guide*.

        This action only applies to Aurora MySQL DB clusters.

        :param db_cluster_identifier: The DB cluster identifier of the DB cluster to be backtracked.
        :param backtrack_to: The timestamp of the time to backtrack the DB cluster to, specified in
        ISO 8601 format.
        :param force: A value that indicates whether to force the DB cluster to backtrack when
        binary logging is enabled.
        :param use_earliest_time_on_point_in_time_unavailable: A value that indicates whether to backtrack the DB cluster to the
        earliest possible backtrack time when *BacktrackTo* is set to a
        timestamp earlier than the earliest backtrack time.
        :returns: DBClusterBacktrack
        :raises DBClusterNotFoundFault:
        :raises InvalidDBClusterStateFault:
        """
        raise NotImplementedError

    @handler("CancelExportTask")
    def cancel_export_task(
        self, context: RequestContext, export_task_identifier: String
    ) -> ExportTask:
        """Cancels an export task in progress that is exporting a snapshot to
        Amazon S3. Any data that has already been written to the S3 bucket isn't
        removed.

        :param export_task_identifier: The identifier of the snapshot export task to cancel.
        :returns: ExportTask
        :raises ExportTaskNotFoundFault:
        :raises InvalidExportTaskStateFault:
        """
        raise NotImplementedError

    @handler("CopyDBClusterParameterGroup")
    def copy_db_cluster_parameter_group(
        self,
        context: RequestContext,
        source_db_cluster_parameter_group_identifier: String,
        target_db_cluster_parameter_group_identifier: String,
        target_db_cluster_parameter_group_description: String,
        tags: TagList = None,
    ) -> CopyDBClusterParameterGroupResult:
        """Copies the specified DB cluster parameter group.

        :param source_db_cluster_parameter_group_identifier: The identifier or Amazon Resource Name (ARN) for the source DB cluster
        parameter group.
        :param target_db_cluster_parameter_group_identifier: The identifier for the copied DB cluster parameter group.
        :param target_db_cluster_parameter_group_description: A description for the copied DB cluster parameter group.
        :param tags: A list of tags.
        :returns: CopyDBClusterParameterGroupResult
        :raises DBParameterGroupNotFoundFault:
        :raises DBParameterGroupQuotaExceededFault:
        :raises DBParameterGroupAlreadyExistsFault:
        """
        raise NotImplementedError

    @handler("CopyDBClusterSnapshot")
    def copy_db_cluster_snapshot(
        self,
        context: RequestContext,
        source_db_cluster_snapshot_identifier: String,
        target_db_cluster_snapshot_identifier: String,
        kms_key_id: String = None,
        pre_signed_url: String = None,
        copy_tags: BooleanOptional = None,
        tags: TagList = None,
        source_region: String = None,
    ) -> CopyDBClusterSnapshotResult:
        """Copies a snapshot of a DB cluster.

        To copy a DB cluster snapshot from a shared manual DB cluster snapshot,
        ``SourceDBClusterSnapshotIdentifier`` must be the Amazon Resource Name
        (ARN) of the shared DB cluster snapshot.

        You can copy an encrypted DB cluster snapshot from another Amazon Web
        Services Region. In that case, the Amazon Web Services Region where you
        call the ``CopyDBClusterSnapshot`` action is the destination Amazon Web
        Services Region for the encrypted DB cluster snapshot to be copied to.
        To copy an encrypted DB cluster snapshot from another Amazon Web
        Services Region, you must provide the following values:

        -  ``KmsKeyId`` - The Amazon Web Services Key Management System (Amazon
           Web Services KMS) key identifier for the key to use to encrypt the
           copy of the DB cluster snapshot in the destination Amazon Web
           Services Region.

        -  ``PreSignedUrl`` - A URL that contains a Signature Version 4 signed
           request for the ``CopyDBClusterSnapshot`` action to be called in the
           source Amazon Web Services Region where the DB cluster snapshot is
           copied from. The pre-signed URL must be a valid request for the
           ``CopyDBClusterSnapshot`` API action that can be executed in the
           source Amazon Web Services Region that contains the encrypted DB
           cluster snapshot to be copied.

           The pre-signed URL request must contain the following parameter
           values:

           -  ``KmsKeyId`` - The Amazon Web Services KMS key identifier for the
              KMS key to use to encrypt the copy of the DB cluster snapshot in
              the destination Amazon Web Services Region. This is the same
              identifier for both the ``CopyDBClusterSnapshot`` action that is
              called in the destination Amazon Web Services Region, and the
              action contained in the pre-signed URL.

           -  ``DestinationRegion`` - The name of the Amazon Web Services Region
              that the DB cluster snapshot is to be created in.

           -  ``SourceDBClusterSnapshotIdentifier`` - The DB cluster snapshot
              identifier for the encrypted DB cluster snapshot to be copied.
              This identifier must be in the Amazon Resource Name (ARN) format
              for the source Amazon Web Services Region. For example, if you are
              copying an encrypted DB cluster snapshot from the us-west-2 Amazon
              Web Services Region, then your
              ``SourceDBClusterSnapshotIdentifier`` looks like the following
              example:
              ``arn:aws:rds:us-west-2:123456789012:cluster-snapshot:aurora-cluster1-snapshot-20161115``.

           To learn how to generate a Signature Version 4 signed request, see
           `Authenticating Requests: Using Query Parameters (Amazon Web Services
           Signature Version
           4) <https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-query-string-auth.html>`__
           and `Signature Version 4 Signing
           Process <https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html>`__.

           If you are using an Amazon Web Services SDK tool or the CLI, you can
           specify ``SourceRegion`` (or ``--source-region`` for the CLI) instead
           of specifying ``PreSignedUrl`` manually. Specifying ``SourceRegion``
           autogenerates a pre-signed URL that is a valid request for the
           operation that can be executed in the source Amazon Web Services
           Region.

        -  ``TargetDBClusterSnapshotIdentifier`` - The identifier for the new
           copy of the DB cluster snapshot in the destination Amazon Web
           Services Region.

        -  ``SourceDBClusterSnapshotIdentifier`` - The DB cluster snapshot
           identifier for the encrypted DB cluster snapshot to be copied. This
           identifier must be in the ARN format for the source Amazon Web
           Services Region and is the same value as the
           ``SourceDBClusterSnapshotIdentifier`` in the pre-signed URL.

        To cancel the copy operation once it is in progress, delete the target
        DB cluster snapshot identified by ``TargetDBClusterSnapshotIdentifier``
        while that DB cluster snapshot is in "copying" status.

        For more information on copying encrypted Amazon Aurora DB cluster
        snapshots from one Amazon Web Services Region to another, see `Copying a
        Snapshot <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_CopySnapshot.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Amazon Aurora DB clusters, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param source_db_cluster_snapshot_identifier: The identifier of the DB cluster snapshot to copy.
        :param target_db_cluster_snapshot_identifier: The identifier of the new DB cluster snapshot to create from the source
        DB cluster snapshot.
        :param kms_key_id: The Amazon Web Services KMS key identifier for an encrypted DB cluster
        snapshot.
        :param pre_signed_url: The URL that contains a Signature Version 4 signed request for the
        ``CopyDBClusterSnapshot`` API action in the Amazon Web Services Region
        that contains the source DB cluster snapshot to copy.
        :param copy_tags: A value that indicates whether to copy all tags from the source DB
        cluster snapshot to the target DB cluster snapshot.
        :param tags: A list of tags.
        :param source_region: The ID of the region that contains the snapshot to be copied.
        :returns: CopyDBClusterSnapshotResult
        :raises DBClusterSnapshotAlreadyExistsFault:
        :raises DBClusterSnapshotNotFoundFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBClusterSnapshotStateFault:
        :raises SnapshotQuotaExceededFault:
        :raises KMSKeyNotAccessibleFault:
        """
        raise NotImplementedError

    @handler("CopyDBParameterGroup")
    def copy_db_parameter_group(
        self,
        context: RequestContext,
        source_db_parameter_group_identifier: String,
        target_db_parameter_group_identifier: String,
        target_db_parameter_group_description: String,
        tags: TagList = None,
    ) -> CopyDBParameterGroupResult:
        """Copies the specified DB parameter group.

        :param source_db_parameter_group_identifier: The identifier or ARN for the source DB parameter group.
        :param target_db_parameter_group_identifier: The identifier for the copied DB parameter group.
        :param target_db_parameter_group_description: A description for the copied DB parameter group.
        :param tags: A list of tags.
        :returns: CopyDBParameterGroupResult
        :raises DBParameterGroupNotFoundFault:
        :raises DBParameterGroupAlreadyExistsFault:
        :raises DBParameterGroupQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("CopyDBSnapshot")
    def copy_db_snapshot(
        self,
        context: RequestContext,
        source_db_snapshot_identifier: String,
        target_db_snapshot_identifier: String,
        kms_key_id: String = None,
        tags: TagList = None,
        copy_tags: BooleanOptional = None,
        pre_signed_url: String = None,
        option_group_name: String = None,
        target_custom_availability_zone: String = None,
        source_region: String = None,
    ) -> CopyDBSnapshotResult:
        """Copies the specified DB snapshot. The source DB snapshot must be in the
        ``available`` state.

        You can copy a snapshot from one Amazon Web Services Region to another.
        In that case, the Amazon Web Services Region where you call the
        ``CopyDBSnapshot`` action is the destination Amazon Web Services Region
        for the DB snapshot copy.

        This command doesn't apply to RDS Custom.

        For more information about copying snapshots, see `Copying a DB
        Snapshot <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_CopySnapshot.html#USER_CopyDBSnapshot>`__
        in the *Amazon RDS User Guide*.

        :param source_db_snapshot_identifier: The identifier for the source DB snapshot.
        :param target_db_snapshot_identifier: The identifier for the copy of the snapshot.
        :param kms_key_id: The Amazon Web Services KMS key identifier for an encrypted DB snapshot.
        :param tags: A list of tags.
        :param copy_tags: A value that indicates whether to copy all tags from the source DB
        snapshot to the target DB snapshot.
        :param pre_signed_url: The URL that contains a Signature Version 4 signed request for the
        ``CopyDBSnapshot`` API action in the source Amazon Web Services Region
        that contains the source DB snapshot to copy.
        :param option_group_name: The name of an option group to associate with the copy of the snapshot.
        :param target_custom_availability_zone: The external custom Availability Zone (CAZ) identifier for the target
        CAZ.
        :param source_region: The ID of the region that contains the snapshot to be copied.
        :returns: CopyDBSnapshotResult
        :raises DBSnapshotAlreadyExistsFault:
        :raises DBSnapshotNotFoundFault:
        :raises InvalidDBSnapshotStateFault:
        :raises SnapshotQuotaExceededFault:
        :raises KMSKeyNotAccessibleFault:
        :raises CustomAvailabilityZoneNotFoundFault:
        """
        raise NotImplementedError

    @handler("CopyOptionGroup")
    def copy_option_group(
        self,
        context: RequestContext,
        source_option_group_identifier: String,
        target_option_group_identifier: String,
        target_option_group_description: String,
        tags: TagList = None,
    ) -> CopyOptionGroupResult:
        """Copies the specified option group.

        :param source_option_group_identifier: The identifier for the source option group.
        :param target_option_group_identifier: The identifier for the copied option group.
        :param target_option_group_description: The description for the copied option group.
        :param tags: A list of tags.
        :returns: CopyOptionGroupResult
        :raises OptionGroupAlreadyExistsFault:
        :raises OptionGroupNotFoundFault:
        :raises OptionGroupQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("CreateCustomDBEngineVersion")
    def create_custom_db_engine_version(
        self,
        context: RequestContext,
        engine: CustomEngineName,
        engine_version: CustomEngineVersion,
        database_installation_files_s3_bucket_name: BucketName,
        kms_key_id: KmsKeyIdOrArn,
        manifest: CustomDBEngineVersionManifest,
        database_installation_files_s3_prefix: String255 = None,
        description: Description = None,
        tags: TagList = None,
    ) -> DBEngineVersion:
        """Creates a custom DB engine version (CEV). A CEV is a binary volume
        snapshot of a database engine and specific AMI. The supported engines
        are the following:

        -  Oracle Database 12.1 Enterprise Edition with the January 2021 or
           later RU/RUR

        -  Oracle Database 19c Enterprise Edition with the January 2021 or later
           RU/RUR

        Amazon RDS, which is a fully managed service, supplies the Amazon
        Machine Image (AMI) and database software. The Amazon RDS database
        software is preinstalled, so you need only select a DB engine and
        version, and create your database. With Amazon RDS Custom for Oracle,
        you upload your database installation files in Amazon S3.

        When you create a custom engine version, you specify the files in a JSON
        document called a CEV manifest. This document describes installation
        .zip files stored in Amazon S3. RDS Custom creates your CEV from the
        installation files that you provided. This service model is called Bring
        Your Own Media (BYOM).

        Creation takes approximately two hours. If creation fails, RDS Custom
        issues ``RDS-EVENT-0196`` with the message
        ``Creation failed for custom engine version``, and includes details
        about the failure. For example, the event prints missing files.

        After you create the CEV, it is available for use. You can create
        multiple CEVs, and create multiple RDS Custom instances from any CEV.
        You can also change the status of a CEV to make it available or
        inactive.

        The MediaImport service that imports files from Amazon S3 to create CEVs
        isn't integrated with Amazon Web Services CloudTrail. If you turn on
        data logging for Amazon RDS in CloudTrail, calls to the
        ``CreateCustomDbEngineVersion`` event aren't logged. However, you might
        see calls from the API gateway that accesses your Amazon S3 bucket.
        These calls originate from the MediaImport service for the
        ``CreateCustomDbEngineVersion`` event.

        For more information, see `Creating a
        CEV <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/custom-cev.html#custom-cev.create>`__
        in the *Amazon RDS User Guide*.

        :param engine: The database engine to use for your custom engine version (CEV).
        :param engine_version: The name of your CEV.
        :param database_installation_files_s3_bucket_name: The name of an Amazon S3 bucket that contains database installation
        files for your CEV.
        :param kms_key_id: The Amazon Web Services KMS key identifier for an encrypted CEV.
        :param manifest: The CEV manifest, which is a JSON document that describes the
        installation .
        :param database_installation_files_s3_prefix: The Amazon S3 directory that contains the database installation files
        for your CEV.
        :param description: An optional description of your CEV.
        :param tags: A list of tags.
        :returns: DBEngineVersion
        :raises CustomDBEngineVersionAlreadyExistsFault:
        :raises CustomDBEngineVersionQuotaExceededFault:
        :raises KMSKeyNotAccessibleFault:
        """
        raise NotImplementedError

    @handler("CreateDBCluster")
    def create_db_cluster(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        engine: String,
        availability_zones: AvailabilityZones = None,
        backup_retention_period: IntegerOptional = None,
        character_set_name: String = None,
        database_name: String = None,
        db_cluster_parameter_group_name: String = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        db_subnet_group_name: String = None,
        engine_version: String = None,
        port: IntegerOptional = None,
        master_username: String = None,
        master_user_password: String = None,
        option_group_name: String = None,
        preferred_backup_window: String = None,
        preferred_maintenance_window: String = None,
        replication_source_identifier: String = None,
        tags: TagList = None,
        storage_encrypted: BooleanOptional = None,
        kms_key_id: String = None,
        pre_signed_url: String = None,
        enable_iam_database_authentication: BooleanOptional = None,
        backtrack_window: LongOptional = None,
        enable_cloudwatch_logs_exports: LogTypeList = None,
        engine_mode: String = None,
        scaling_configuration: ScalingConfiguration = None,
        deletion_protection: BooleanOptional = None,
        global_cluster_identifier: String = None,
        enable_http_endpoint: BooleanOptional = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        domain: String = None,
        domain_iam_role_name: String = None,
        enable_global_write_forwarding: BooleanOptional = None,
        db_cluster_instance_class: String = None,
        allocated_storage: IntegerOptional = None,
        storage_type: String = None,
        iops: IntegerOptional = None,
        publicly_accessible: BooleanOptional = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        monitoring_interval: IntegerOptional = None,
        monitoring_role_arn: String = None,
        enable_performance_insights: BooleanOptional = None,
        performance_insights_kms_key_id: String = None,
        performance_insights_retention_period: IntegerOptional = None,
        serverless_v2_scaling_configuration: ServerlessV2ScalingConfiguration = None,
        source_region: String = None,
    ) -> CreateDBClusterResult:
        """Creates a new Amazon Aurora DB cluster or Multi-AZ DB cluster.

        You can use the ``ReplicationSourceIdentifier`` parameter to create an
        Amazon Aurora DB cluster as a read replica of another DB cluster or
        Amazon RDS MySQL or PostgreSQL DB instance. For cross-Region replication
        where the DB cluster identified by ``ReplicationSourceIdentifier`` is
        encrypted, also specify the ``PreSignedUrl`` parameter.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_identifier: The DB cluster identifier.
        :param engine: The name of the database engine to be used for this DB cluster.
        :param availability_zones: A list of Availability Zones (AZs) where DB instances in the DB cluster
        can be created.
        :param backup_retention_period: The number of days for which automated backups are retained.
        :param character_set_name: A value that indicates that the DB cluster should be associated with the
        specified CharacterSet.
        :param database_name: The name for your database of up to 64 alphanumeric characters.
        :param db_cluster_parameter_group_name: The name of the DB cluster parameter group to associate with this DB
        cluster.
        :param vpc_security_group_ids: A list of EC2 VPC security groups to associate with this DB cluster.
        :param db_subnet_group_name: A DB subnet group to associate with this DB cluster.
        :param engine_version: The version number of the database engine to use.
        :param port: The port number on which the instances in the DB cluster accept
        connections.
        :param master_username: The name of the master user for the DB cluster.
        :param master_user_password: The password for the master database user.
        :param option_group_name: A value that indicates that the DB cluster should be associated with the
        specified option group.
        :param preferred_backup_window: The daily time range during which automated backups are created if
        automated backups are enabled using the ``BackupRetentionPeriod``
        parameter.
        :param preferred_maintenance_window: The weekly time range during which system maintenance can occur, in
        Universal Coordinated Time (UTC).
        :param replication_source_identifier: The Amazon Resource Name (ARN) of the source DB instance or DB cluster
        if this DB cluster is created as a read replica.
        :param tags: Tags to assign to the DB cluster.
        :param storage_encrypted: A value that indicates whether the DB cluster is encrypted.
        :param kms_key_id: The Amazon Web Services KMS key identifier for an encrypted DB cluster.
        :param pre_signed_url: A URL that contains a Signature Version 4 signed request for the
        ``CreateDBCluster`` action to be called in the source Amazon Web
        Services Region where the DB cluster is replicated from.
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param backtrack_window: The target backtrack window, in seconds.
        :param enable_cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to
        CloudWatch Logs.
        :param engine_mode: The DB engine mode of the DB cluster, either ``provisioned``,
        ``serverless``, ``parallelquery``, ``global``, or ``multimaster``.
        :param scaling_configuration: For DB clusters in ``serverless`` DB engine mode, the scaling properties
        of the DB cluster.
        :param deletion_protection: A value that indicates whether the DB cluster has deletion protection
        enabled.
        :param global_cluster_identifier: The global cluster ID of an Aurora cluster that becomes the primary
        cluster in the new global database cluster.
        :param enable_http_endpoint: A value that indicates whether to enable the HTTP endpoint for an Aurora
        Serverless v1 DB cluster.
        :param copy_tags_to_snapshot: A value that indicates whether to copy all tags from the DB cluster to
        snapshots of the DB cluster.
        :param domain: The Active Directory directory ID to create the DB cluster in.
        :param domain_iam_role_name: Specify the name of the IAM role to be used when making API calls to the
        Directory Service.
        :param enable_global_write_forwarding: A value that indicates whether to enable this DB cluster to forward
        write operations to the primary cluster of an Aurora global database
        (GlobalCluster).
        :param db_cluster_instance_class: The compute and memory capacity of each DB instance in the Multi-AZ DB
        cluster, for example db.
        :param allocated_storage: The amount of storage in gibibytes (GiB) to allocate to each DB instance
        in the Multi-AZ DB cluster.
        :param storage_type: Specifies the storage type to be associated with the DB cluster.
        :param iops: The amount of Provisioned IOPS (input/output operations per second) to
        be initially allocated for each DB instance in the Multi-AZ DB cluster.
        :param publicly_accessible: A value that indicates whether the DB cluster is publicly accessible.
        :param auto_minor_version_upgrade: A value that indicates whether minor engine upgrades are applied
        automatically to the DB cluster during the maintenance window.
        :param monitoring_interval: The interval, in seconds, between points when Enhanced Monitoring
        metrics are collected for the DB cluster.
        :param monitoring_role_arn: The Amazon Resource Name (ARN) for the IAM role that permits RDS to send
        Enhanced Monitoring metrics to Amazon CloudWatch Logs.
        :param enable_performance_insights: A value that indicates whether to turn on Performance Insights for the
        DB cluster.
        :param performance_insights_kms_key_id: The Amazon Web Services KMS key identifier for encryption of Performance
        Insights data.
        :param performance_insights_retention_period: The amount of time, in days, to retain Performance Insights data.
        :param serverless_v2_scaling_configuration: Contains the scaling configuration of an Aurora Serverless v2 DB
        cluster.
        :param source_region: The ID of the region that contains the source for the db cluster.
        :returns: CreateDBClusterResult
        :raises DBClusterAlreadyExistsFault:
        :raises InsufficientStorageClusterCapacityFault:
        :raises DBClusterQuotaExceededFault:
        :raises StorageQuotaExceededFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBSubnetGroupStateFault:
        :raises InvalidSubnet:
        :raises InvalidDBInstanceStateFault:
        :raises DBClusterParameterGroupNotFoundFault:
        :raises KMSKeyNotAccessibleFault:
        :raises DBClusterNotFoundFault:
        :raises DBInstanceNotFoundFault:
        :raises DBSubnetGroupDoesNotCoverEnoughAZs:
        :raises GlobalClusterNotFoundFault:
        :raises InvalidGlobalClusterStateFault:
        :raises DomainNotFoundFault:
        """
        raise NotImplementedError

    @handler("CreateDBClusterEndpoint")
    def create_db_cluster_endpoint(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        db_cluster_endpoint_identifier: String,
        endpoint_type: String,
        static_members: StringList = None,
        excluded_members: StringList = None,
        tags: TagList = None,
    ) -> DBClusterEndpoint:
        """Creates a new custom endpoint and associates it with an Amazon Aurora DB
        cluster.

        This action only applies to Aurora DB clusters.

        :param db_cluster_identifier: The DB cluster identifier of the DB cluster associated with the
        endpoint.
        :param db_cluster_endpoint_identifier: The identifier to use for the new endpoint.
        :param endpoint_type: The type of the endpoint, one of: ``READER``, ``WRITER``, ``ANY``.
        :param static_members: List of DB instance identifiers that are part of the custom endpoint
        group.
        :param excluded_members: List of DB instance identifiers that aren't part of the custom endpoint
        group.
        :param tags: The tags to be assigned to the Amazon RDS resource.
        :returns: DBClusterEndpoint
        :raises DBClusterEndpointQuotaExceededFault:
        :raises DBClusterEndpointAlreadyExistsFault:
        :raises DBClusterNotFoundFault:
        :raises InvalidDBClusterStateFault:
        :raises DBInstanceNotFoundFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError

    @handler("CreateDBClusterParameterGroup")
    def create_db_cluster_parameter_group(
        self,
        context: RequestContext,
        db_cluster_parameter_group_name: String,
        db_parameter_group_family: String,
        description: String,
        tags: TagList = None,
    ) -> CreateDBClusterParameterGroupResult:
        """Creates a new DB cluster parameter group.

        Parameters in a DB cluster parameter group apply to all of the instances
        in a DB cluster.

        A DB cluster parameter group is initially created with the default
        parameters for the database engine used by instances in the DB cluster.
        To provide custom values for any of the parameters, you must modify the
        group after creating it using ``ModifyDBClusterParameterGroup``. Once
        you've created a DB cluster parameter group, you need to associate it
        with your DB cluster using ``ModifyDBCluster``.

        When you associate a new DB cluster parameter group with a running
        Aurora DB cluster, reboot the DB instances in the DB cluster without
        failover for the new DB cluster parameter group and associated settings
        to take effect.

        When you associate a new DB cluster parameter group with a running
        Multi-AZ DB cluster, reboot the DB cluster without failover for the new
        DB cluster parameter group and associated settings to take effect.

        After you create a DB cluster parameter group, you should wait at least
        5 minutes before creating your first DB cluster that uses that DB
        cluster parameter group as the default parameter group. This allows
        Amazon RDS to fully complete the create action before the DB cluster
        parameter group is used as the default for a new DB cluster. This is
        especially important for parameters that are critical when creating the
        default database for a DB cluster, such as the character set for the
        default database defined by the ``character_set_database`` parameter.
        You can use the *Parameter Groups* option of the `Amazon RDS
        console <https://console.aws.amazon.com/rds/>`__ or the
        ``DescribeDBClusterParameters`` action to verify that your DB cluster
        parameter group has been created or modified.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_parameter_group_name: The name of the DB cluster parameter group.
        :param db_parameter_group_family: The DB cluster parameter group family name.
        :param description: The description for the DB cluster parameter group.
        :param tags: Tags to assign to the DB cluster parameter group.
        :returns: CreateDBClusterParameterGroupResult
        :raises DBParameterGroupQuotaExceededFault:
        :raises DBParameterGroupAlreadyExistsFault:
        """
        raise NotImplementedError

    @handler("CreateDBClusterSnapshot")
    def create_db_cluster_snapshot(
        self,
        context: RequestContext,
        db_cluster_snapshot_identifier: String,
        db_cluster_identifier: String,
        tags: TagList = None,
    ) -> CreateDBClusterSnapshotResult:
        """Creates a snapshot of a DB cluster.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_snapshot_identifier: The identifier of the DB cluster snapshot.
        :param db_cluster_identifier: The identifier of the DB cluster to create a snapshot for.
        :param tags: The tags to be assigned to the DB cluster snapshot.
        :returns: CreateDBClusterSnapshotResult
        :raises DBClusterSnapshotAlreadyExistsFault:
        :raises InvalidDBClusterStateFault:
        :raises DBClusterNotFoundFault:
        :raises SnapshotQuotaExceededFault:
        :raises InvalidDBClusterSnapshotStateFault:
        """
        raise NotImplementedError

    @handler("CreateDBInstance")
    def create_db_instance(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        db_instance_class: String,
        engine: String,
        db_name: String = None,
        allocated_storage: IntegerOptional = None,
        master_username: String = None,
        master_user_password: String = None,
        db_security_groups: DBSecurityGroupNameList = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        availability_zone: String = None,
        db_subnet_group_name: String = None,
        preferred_maintenance_window: String = None,
        db_parameter_group_name: String = None,
        backup_retention_period: IntegerOptional = None,
        preferred_backup_window: String = None,
        port: IntegerOptional = None,
        multi_az: BooleanOptional = None,
        engine_version: String = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        license_model: String = None,
        iops: IntegerOptional = None,
        option_group_name: String = None,
        character_set_name: String = None,
        nchar_character_set_name: String = None,
        publicly_accessible: BooleanOptional = None,
        tags: TagList = None,
        db_cluster_identifier: String = None,
        storage_type: String = None,
        tde_credential_arn: String = None,
        tde_credential_password: String = None,
        storage_encrypted: BooleanOptional = None,
        kms_key_id: String = None,
        domain: String = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        monitoring_interval: IntegerOptional = None,
        monitoring_role_arn: String = None,
        domain_iam_role_name: String = None,
        promotion_tier: IntegerOptional = None,
        timezone: String = None,
        enable_iam_database_authentication: BooleanOptional = None,
        enable_performance_insights: BooleanOptional = None,
        performance_insights_kms_key_id: String = None,
        performance_insights_retention_period: IntegerOptional = None,
        enable_cloudwatch_logs_exports: LogTypeList = None,
        processor_features: ProcessorFeatureList = None,
        deletion_protection: BooleanOptional = None,
        max_allocated_storage: IntegerOptional = None,
        enable_customer_owned_ip: BooleanOptional = None,
        custom_iam_instance_profile: String = None,
        backup_target: String = None,
        network_type: String = None,
    ) -> CreateDBInstanceResult:
        """Creates a new DB instance.

        :param db_instance_identifier: The DB instance identifier.
        :param db_instance_class: The compute and memory capacity of the DB instance, for example
        db.
        :param engine: The name of the database engine to be used for this instance.
        :param db_name: The meaning of this parameter differs according to the database engine
        you use.
        :param allocated_storage: The amount of storage in gibibytes (GiB) to allocate for the DB
        instance.
        :param master_username: The name for the master user.
        :param master_user_password: The password for the master user.
        :param db_security_groups: A list of DB security groups to associate with this DB instance.
        :param vpc_security_group_ids: A list of Amazon EC2 VPC security groups to associate with this DB
        instance.
        :param availability_zone: The Availability Zone (AZ) where the database will be created.
        :param db_subnet_group_name: A DB subnet group to associate with this DB instance.
        :param preferred_maintenance_window: The time range each week during which system maintenance can occur, in
        Universal Coordinated Time (UTC).
        :param db_parameter_group_name: The name of the DB parameter group to associate with this DB instance.
        :param backup_retention_period: The number of days for which automated backups are retained.
        :param preferred_backup_window: The daily time range during which automated backups are created if
        automated backups are enabled, using the ``BackupRetentionPeriod``
        parameter.
        :param port: The port number on which the database accepts connections.
        :param multi_az: A value that indicates whether the DB instance is a Multi-AZ deployment.
        :param engine_version: The version number of the database engine to use.
        :param auto_minor_version_upgrade: A value that indicates whether minor engine upgrades are applied
        automatically to the DB instance during the maintenance window.
        :param license_model: License model information for this DB instance.
        :param iops: The amount of Provisioned IOPS (input/output operations per second) to
        be initially allocated for the DB instance.
        :param option_group_name: A value that indicates that the DB instance should be associated with
        the specified option group.
        :param character_set_name: For supported engines, this value indicates that the DB instance should
        be associated with the specified ``CharacterSet``.
        :param nchar_character_set_name: The name of the NCHAR character set for the Oracle DB instance.
        :param publicly_accessible: A value that indicates whether the DB instance is publicly accessible.
        :param tags: Tags to assign to the DB instance.
        :param db_cluster_identifier: The identifier of the DB cluster that the instance will belong to.
        :param storage_type: Specifies the storage type to be associated with the DB instance.
        :param tde_credential_arn: The ARN from the key store with which to associate the instance for TDE
        encryption.
        :param tde_credential_password: The password for the given ARN from the key store in order to access the
        device.
        :param storage_encrypted: A value that indicates whether the DB instance is encrypted.
        :param kms_key_id: The Amazon Web Services KMS key identifier for an encrypted DB instance.
        :param domain: The Active Directory directory ID to create the DB instance in.
        :param copy_tags_to_snapshot: A value that indicates whether to copy tags from the DB instance to
        snapshots of the DB instance.
        :param monitoring_interval: The interval, in seconds, between points when Enhanced Monitoring
        metrics are collected for the DB instance.
        :param monitoring_role_arn: The ARN for the IAM role that permits RDS to send enhanced monitoring
        metrics to Amazon CloudWatch Logs.
        :param domain_iam_role_name: Specify the name of the IAM role to be used when making API calls to the
        Directory Service.
        :param promotion_tier: A value that specifies the order in which an Aurora Replica is promoted
        to the primary instance after a failure of the existing primary
        instance.
        :param timezone: The time zone of the DB instance.
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param enable_performance_insights: A value that indicates whether to enable Performance Insights for the DB
        instance.
        :param performance_insights_kms_key_id: The Amazon Web Services KMS key identifier for encryption of Performance
        Insights data.
        :param performance_insights_retention_period: The amount of time, in days, to retain Performance Insights data.
        :param enable_cloudwatch_logs_exports: The list of log types that need to be enabled for exporting to
        CloudWatch Logs.
        :param processor_features: The number of CPU cores and the number of threads per core for the DB
        instance class of the DB instance.
        :param deletion_protection: A value that indicates whether the DB instance has deletion protection
        enabled.
        :param max_allocated_storage: The upper limit in gibibytes (GiB) to which Amazon RDS can automatically
        scale the storage of the DB instance.
        :param enable_customer_owned_ip: A value that indicates whether to enable a customer-owned IP address
        (CoIP) for an RDS on Outposts DB instance.
        :param custom_iam_instance_profile: The instance profile associated with the underlying Amazon EC2 instance
        of an RDS Custom DB instance.
        :param backup_target: Specifies where automated backups and manual snapshots are stored.
        :param network_type: The network type of the DB instance.
        :returns: CreateDBInstanceResult
        :raises DBInstanceAlreadyExistsFault:
        :raises InsufficientDBInstanceCapacityFault:
        :raises DBParameterGroupNotFoundFault:
        :raises DBSecurityGroupNotFoundFault:
        :raises InstanceQuotaExceededFault:
        :raises StorageQuotaExceededFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises DBSubnetGroupDoesNotCoverEnoughAZs:
        :raises InvalidDBClusterStateFault:
        :raises InvalidSubnet:
        :raises InvalidVPCNetworkStateFault:
        :raises ProvisionedIopsNotAvailableInAZFault:
        :raises OptionGroupNotFoundFault:
        :raises DBClusterNotFoundFault:
        :raises StorageTypeNotSupportedFault:
        :raises AuthorizationNotFoundFault:
        :raises KMSKeyNotAccessibleFault:
        :raises DomainNotFoundFault:
        :raises BackupPolicyNotFoundFault:
        :raises NetworkTypeNotSupported:
        """
        raise NotImplementedError

    @handler("CreateDBInstanceReadReplica")
    def create_db_instance_read_replica(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        source_db_instance_identifier: String,
        db_instance_class: String = None,
        availability_zone: String = None,
        port: IntegerOptional = None,
        multi_az: BooleanOptional = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        iops: IntegerOptional = None,
        option_group_name: String = None,
        db_parameter_group_name: String = None,
        publicly_accessible: BooleanOptional = None,
        tags: TagList = None,
        db_subnet_group_name: String = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        storage_type: String = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        monitoring_interval: IntegerOptional = None,
        monitoring_role_arn: String = None,
        kms_key_id: String = None,
        pre_signed_url: String = None,
        enable_iam_database_authentication: BooleanOptional = None,
        enable_performance_insights: BooleanOptional = None,
        performance_insights_kms_key_id: String = None,
        performance_insights_retention_period: IntegerOptional = None,
        enable_cloudwatch_logs_exports: LogTypeList = None,
        processor_features: ProcessorFeatureList = None,
        use_default_processor_features: BooleanOptional = None,
        deletion_protection: BooleanOptional = None,
        domain: String = None,
        domain_iam_role_name: String = None,
        replica_mode: ReplicaMode = None,
        max_allocated_storage: IntegerOptional = None,
        custom_iam_instance_profile: String = None,
        network_type: String = None,
        source_region: String = None,
    ) -> CreateDBInstanceReadReplicaResult:
        """Creates a new DB instance that acts as a read replica for an existing
        source DB instance. You can create a read replica for a DB instance
        running MySQL, MariaDB, Oracle, PostgreSQL, or SQL Server. For more
        information, see `Working with Read
        Replicas <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html>`__
        in the *Amazon RDS User Guide*.

        Amazon Aurora doesn't support this action. Call the ``CreateDBInstance``
        action to create a DB instance for an Aurora DB cluster.

        All read replica DB instances are created with backups disabled. All
        other DB instance attributes (including DB security groups and DB
        parameter groups) are inherited from the source DB instance, except as
        specified.

        Your source DB instance must have backup retention enabled.

        :param db_instance_identifier: The DB instance identifier of the read replica.
        :param source_db_instance_identifier: The identifier of the DB instance that will act as the source for the
        read replica.
        :param db_instance_class: The compute and memory capacity of the read replica, for example
        db.
        :param availability_zone: The Availability Zone (AZ) where the read replica will be created.
        :param port: The port number that the DB instance uses for connections.
        :param multi_az: A value that indicates whether the read replica is in a Multi-AZ
        deployment.
        :param auto_minor_version_upgrade: A value that indicates whether minor engine upgrades are applied
        automatically to the read replica during the maintenance window.
        :param iops: The amount of Provisioned IOPS (input/output operations per second) to
        be initially allocated for the DB instance.
        :param option_group_name: The option group the DB instance is associated with.
        :param db_parameter_group_name: The name of the DB parameter group to associate with this DB instance.
        :param publicly_accessible: A value that indicates whether the DB instance is publicly accessible.
        :param tags: A list of tags.
        :param db_subnet_group_name: Specifies a DB subnet group for the DB instance.
        :param vpc_security_group_ids: A list of Amazon EC2 VPC security groups to associate with the read
        replica.
        :param storage_type: Specifies the storage type to be associated with the read replica.
        :param copy_tags_to_snapshot: A value that indicates whether to copy all tags from the read replica to
        snapshots of the read replica.
        :param monitoring_interval: The interval, in seconds, between points when Enhanced Monitoring
        metrics are collected for the read replica.
        :param monitoring_role_arn: The ARN for the IAM role that permits RDS to send enhanced monitoring
        metrics to Amazon CloudWatch Logs.
        :param kms_key_id: The Amazon Web Services KMS key identifier for an encrypted read
        replica.
        :param pre_signed_url: The URL that contains a Signature Version 4 signed request for the
        ``CreateDBInstanceReadReplica`` API action in the source Amazon Web
        Services Region that contains the source DB instance.
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param enable_performance_insights: A value that indicates whether to enable Performance Insights for the
        read replica.
        :param performance_insights_kms_key_id: The Amazon Web Services KMS key identifier for encryption of Performance
        Insights data.
        :param performance_insights_retention_period: The amount of time, in days, to retain Performance Insights data.
        :param enable_cloudwatch_logs_exports: The list of logs that the new DB instance is to export to CloudWatch
        Logs.
        :param processor_features: The number of CPU cores and the number of threads per core for the DB
        instance class of the DB instance.
        :param use_default_processor_features: A value that indicates whether the DB instance class of the DB instance
        uses its default processor features.
        :param deletion_protection: A value that indicates whether the DB instance has deletion protection
        enabled.
        :param domain: The Active Directory directory ID to create the DB instance in.
        :param domain_iam_role_name: Specify the name of the IAM role to be used when making API calls to the
        Directory Service.
        :param replica_mode: The open mode of the replica database: mounted or read-only.
        :param max_allocated_storage: The upper limit in gibibytes (GiB) to which Amazon RDS can automatically
        scale the storage of the DB instance.
        :param custom_iam_instance_profile: The instance profile associated with the underlying Amazon EC2 instance
        of an RDS Custom DB instance.
        :param network_type: The network type of the DB instance.
        :param source_region: The ID of the region that contains the source for the read replica.
        :returns: CreateDBInstanceReadReplicaResult
        :raises DBInstanceAlreadyExistsFault:
        :raises InsufficientDBInstanceCapacityFault:
        :raises DBParameterGroupNotFoundFault:
        :raises DBSecurityGroupNotFoundFault:
        :raises InstanceQuotaExceededFault:
        :raises StorageQuotaExceededFault:
        :raises DBInstanceNotFoundFault:
        :raises InvalidDBInstanceStateFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises DBSubnetGroupDoesNotCoverEnoughAZs:
        :raises InvalidSubnet:
        :raises InvalidVPCNetworkStateFault:
        :raises ProvisionedIopsNotAvailableInAZFault:
        :raises OptionGroupNotFoundFault:
        :raises DBSubnetGroupNotAllowedFault:
        :raises InvalidDBSubnetGroupFault:
        :raises StorageTypeNotSupportedFault:
        :raises KMSKeyNotAccessibleFault:
        :raises DomainNotFoundFault:
        :raises NetworkTypeNotSupported:
        """
        raise NotImplementedError

    @handler("CreateDBParameterGroup")
    def create_db_parameter_group(
        self,
        context: RequestContext,
        db_parameter_group_name: String,
        db_parameter_group_family: String,
        description: String,
        tags: TagList = None,
    ) -> CreateDBParameterGroupResult:
        """Creates a new DB parameter group.

        A DB parameter group is initially created with the default parameters
        for the database engine used by the DB instance. To provide custom
        values for any of the parameters, you must modify the group after
        creating it using ``ModifyDBParameterGroup``. Once you've created a DB
        parameter group, you need to associate it with your DB instance using
        ``ModifyDBInstance``. When you associate a new DB parameter group with a
        running DB instance, you need to reboot the DB instance without failover
        for the new DB parameter group and associated settings to take effect.

        This command doesn't apply to RDS Custom.

        After you create a DB parameter group, you should wait at least 5
        minutes before creating your first DB instance that uses that DB
        parameter group as the default parameter group. This allows Amazon RDS
        to fully complete the create action before the parameter group is used
        as the default for a new DB instance. This is especially important for
        parameters that are critical when creating the default database for a DB
        instance, such as the character set for the default database defined by
        the ``character_set_database`` parameter. You can use the *Parameter
        Groups* option of the `Amazon RDS
        console <https://console.aws.amazon.com/rds/>`__ or the
        *DescribeDBParameters* command to verify that your DB parameter group
        has been created or modified.

        :param db_parameter_group_name: The name of the DB parameter group.
        :param db_parameter_group_family: The DB parameter group family name.
        :param description: The description for the DB parameter group.
        :param tags: Tags to assign to the DB parameter group.
        :returns: CreateDBParameterGroupResult
        :raises DBParameterGroupQuotaExceededFault:
        :raises DBParameterGroupAlreadyExistsFault:
        """
        raise NotImplementedError

    @handler("CreateDBProxy")
    def create_db_proxy(
        self,
        context: RequestContext,
        db_proxy_name: String,
        engine_family: EngineFamily,
        auth: UserAuthConfigList,
        role_arn: String,
        vpc_subnet_ids: StringList,
        vpc_security_group_ids: StringList = None,
        require_tls: Boolean = None,
        idle_client_timeout: IntegerOptional = None,
        debug_logging: Boolean = None,
        tags: TagList = None,
    ) -> CreateDBProxyResponse:
        """Creates a new DB proxy.

        :param db_proxy_name: The identifier for the proxy.
        :param engine_family: The kinds of databases that the proxy can connect to.
        :param auth: The authorization mechanism that the proxy uses.
        :param role_arn: The Amazon Resource Name (ARN) of the IAM role that the proxy uses to
        access secrets in Amazon Web Services Secrets Manager.
        :param vpc_subnet_ids: One or more VPC subnet IDs to associate with the new proxy.
        :param vpc_security_group_ids: One or more VPC security group IDs to associate with the new proxy.
        :param require_tls: A Boolean parameter that specifies whether Transport Layer Security
        (TLS) encryption is required for connections to the proxy.
        :param idle_client_timeout: The number of seconds that a connection to the proxy can be inactive
        before the proxy disconnects it.
        :param debug_logging: Whether the proxy includes detailed information about SQL statements in
        its logs.
        :param tags: An optional set of key-value pairs to associate arbitrary data of your
        choosing with the proxy.
        :returns: CreateDBProxyResponse
        :raises InvalidSubnet:
        :raises DBProxyAlreadyExistsFault:
        :raises DBProxyQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("CreateDBProxyEndpoint")
    def create_db_proxy_endpoint(
        self,
        context: RequestContext,
        db_proxy_name: DBProxyName,
        db_proxy_endpoint_name: DBProxyEndpointName,
        vpc_subnet_ids: StringList,
        vpc_security_group_ids: StringList = None,
        target_role: DBProxyEndpointTargetRole = None,
        tags: TagList = None,
    ) -> CreateDBProxyEndpointResponse:
        """Creates a ``DBProxyEndpoint``. Only applies to proxies that are
        associated with Aurora DB clusters. You can use DB proxy endpoints to
        specify read/write or read-only access to the DB cluster. You can also
        use DB proxy endpoints to access a DB proxy through a different VPC than
        the proxy's default VPC.

        :param db_proxy_name: The name of the DB proxy associated with the DB proxy endpoint that you
        create.
        :param db_proxy_endpoint_name: The name of the DB proxy endpoint to create.
        :param vpc_subnet_ids: The VPC subnet IDs for the DB proxy endpoint that you create.
        :param vpc_security_group_ids: The VPC security group IDs for the DB proxy endpoint that you create.
        :param target_role: A value that indicates whether the DB proxy endpoint can be used for
        read/write or read-only operations.
        :param tags: A list of tags.
        :returns: CreateDBProxyEndpointResponse
        :raises InvalidSubnet:
        :raises DBProxyNotFoundFault:
        :raises DBProxyEndpointAlreadyExistsFault:
        :raises DBProxyEndpointQuotaExceededFault:
        :raises InvalidDBProxyStateFault:
        """
        raise NotImplementedError

    @handler("CreateDBSecurityGroup")
    def create_db_security_group(
        self,
        context: RequestContext,
        db_security_group_name: String,
        db_security_group_description: String,
        tags: TagList = None,
    ) -> CreateDBSecurityGroupResult:
        """Creates a new DB security group. DB security groups control access to a
        DB instance.

        A DB security group controls access to EC2-Classic DB instances that are
        not in a VPC.

        :param db_security_group_name: The name for the DB security group.
        :param db_security_group_description: The description for the DB security group.
        :param tags: Tags to assign to the DB security group.
        :returns: CreateDBSecurityGroupResult
        :raises DBSecurityGroupAlreadyExistsFault:
        :raises DBSecurityGroupQuotaExceededFault:
        :raises DBSecurityGroupNotSupportedFault:
        """
        raise NotImplementedError

    @handler("CreateDBSnapshot")
    def create_db_snapshot(
        self,
        context: RequestContext,
        db_snapshot_identifier: String,
        db_instance_identifier: String,
        tags: TagList = None,
    ) -> CreateDBSnapshotResult:
        """Creates a snapshot of a DB instance. The source DB instance must be in
        the ``available`` or ``storage-optimization`` state.

        :param db_snapshot_identifier: The identifier for the DB snapshot.
        :param db_instance_identifier: The identifier of the DB instance that you want to create the snapshot
        of.
        :param tags: A list of tags.
        :returns: CreateDBSnapshotResult
        :raises DBSnapshotAlreadyExistsFault:
        :raises InvalidDBInstanceStateFault:
        :raises DBInstanceNotFoundFault:
        :raises SnapshotQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("CreateDBSubnetGroup")
    def create_db_subnet_group(
        self,
        context: RequestContext,
        db_subnet_group_name: String,
        db_subnet_group_description: String,
        subnet_ids: SubnetIdentifierList,
        tags: TagList = None,
    ) -> CreateDBSubnetGroupResult:
        """Creates a new DB subnet group. DB subnet groups must contain at least
        one subnet in at least two AZs in the Amazon Web Services Region.

        :param db_subnet_group_name: The name for the DB subnet group.
        :param db_subnet_group_description: The description for the DB subnet group.
        :param subnet_ids: The EC2 Subnet IDs for the DB subnet group.
        :param tags: Tags to assign to the DB subnet group.
        :returns: CreateDBSubnetGroupResult
        :raises DBSubnetGroupAlreadyExistsFault:
        :raises DBSubnetGroupQuotaExceededFault:
        :raises DBSubnetQuotaExceededFault:
        :raises DBSubnetGroupDoesNotCoverEnoughAZs:
        :raises InvalidSubnet:
        """
        raise NotImplementedError

    @handler("CreateEventSubscription")
    def create_event_subscription(
        self,
        context: RequestContext,
        subscription_name: String,
        sns_topic_arn: String,
        source_type: String = None,
        event_categories: EventCategoriesList = None,
        source_ids: SourceIdsList = None,
        enabled: BooleanOptional = None,
        tags: TagList = None,
    ) -> CreateEventSubscriptionResult:
        """Creates an RDS event notification subscription. This action requires a
        topic Amazon Resource Name (ARN) created by either the RDS console, the
        SNS console, or the SNS API. To obtain an ARN with SNS, you must create
        a topic in Amazon SNS and subscribe to the topic. The ARN is displayed
        in the SNS console.

        You can specify the type of source (``SourceType``) that you want to be
        notified of and provide a list of RDS sources (``SourceIds``) that
        triggers the events. You can also provide a list of event categories
        (``EventCategories``) for events that you want to be notified of. For
        example, you can specify ``SourceType`` = ``db-instance``, ``SourceIds``
        = ``mydbinstance1``, ``mydbinstance2`` and ``EventCategories`` =
        ``Availability``, ``Backup``.

        If you specify both the ``SourceType`` and ``SourceIds``, such as
        ``SourceType`` = ``db-instance`` and ``SourceIds`` = ``myDBInstance1``,
        you are notified of all the ``db-instance`` events for the specified
        source. If you specify a ``SourceType`` but do not specify
        ``SourceIds``, you receive notice of the events for that source type for
        all your RDS sources. If you don't specify either the SourceType or the
        ``SourceIds``, you are notified of events generated from all RDS sources
        belonging to your customer account.

        RDS event notification is only available for unencrypted SNS topics. If
        you specify an encrypted SNS topic, event notifications aren't sent for
        the topic.

        :param subscription_name: The name of the subscription.
        :param sns_topic_arn: The Amazon Resource Name (ARN) of the SNS topic created for event
        notification.
        :param source_type: The type of source that is generating the events.
        :param event_categories: A list of event categories for a particular source type (``SourceType``)
        that you want to subscribe to.
        :param source_ids: The list of identifiers of the event sources for which events are
        returned.
        :param enabled: A value that indicates whether to activate the subscription.
        :param tags: A list of tags.
        :returns: CreateEventSubscriptionResult
        :raises EventSubscriptionQuotaExceededFault:
        :raises SubscriptionAlreadyExistFault:
        :raises SNSInvalidTopicFault:
        :raises SNSNoAuthorizationFault:
        :raises SNSTopicArnNotFoundFault:
        :raises SubscriptionCategoryNotFoundFault:
        :raises SourceNotFoundFault:
        """
        raise NotImplementedError

    @handler("CreateGlobalCluster")
    def create_global_cluster(
        self,
        context: RequestContext,
        global_cluster_identifier: String = None,
        source_db_cluster_identifier: String = None,
        engine: String = None,
        engine_version: String = None,
        deletion_protection: BooleanOptional = None,
        database_name: String = None,
        storage_encrypted: BooleanOptional = None,
    ) -> CreateGlobalClusterResult:
        """Creates an Aurora global database spread across multiple Amazon Web
        Services Regions. The global database contains a single primary cluster
        with read-write capability, and a read-only secondary cluster that
        receives data from the primary cluster through high-speed replication
        performed by the Aurora storage subsystem.

        You can create a global database that is initially empty, and then add a
        primary cluster and a secondary cluster to it. Or you can specify an
        existing Aurora cluster during the create operation, and this cluster
        becomes the primary cluster of the global database.

        This action only applies to Aurora DB clusters.

        :param global_cluster_identifier: The cluster identifier of the new global database cluster.
        :param source_db_cluster_identifier: The Amazon Resource Name (ARN) to use as the primary cluster of the
        global database.
        :param engine: The name of the database engine to be used for this DB cluster.
        :param engine_version: The engine version of the Aurora global database.
        :param deletion_protection: The deletion protection setting for the new global database.
        :param database_name: The name for your database of up to 64 alpha-numeric characters.
        :param storage_encrypted: The storage encryption setting for the new global database cluster.
        :returns: CreateGlobalClusterResult
        :raises GlobalClusterAlreadyExistsFault:
        :raises GlobalClusterQuotaExceededFault:
        :raises InvalidDBClusterStateFault:
        :raises DBClusterNotFoundFault:
        """
        raise NotImplementedError

    @handler("CreateOptionGroup")
    def create_option_group(
        self,
        context: RequestContext,
        option_group_name: String,
        engine_name: String,
        major_engine_version: String,
        option_group_description: String,
        tags: TagList = None,
    ) -> CreateOptionGroupResult:
        """Creates a new option group. You can create up to 20 option groups.

        This command doesn't apply to RDS Custom.

        :param option_group_name: Specifies the name of the option group to be created.
        :param engine_name: Specifies the name of the engine that this option group should be
        associated with.
        :param major_engine_version: Specifies the major version of the engine that this option group should
        be associated with.
        :param option_group_description: The description of the option group.
        :param tags: Tags to assign to the option group.
        :returns: CreateOptionGroupResult
        :raises OptionGroupAlreadyExistsFault:
        :raises OptionGroupQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("DeleteCustomDBEngineVersion")
    def delete_custom_db_engine_version(
        self, context: RequestContext, engine: CustomEngineName, engine_version: CustomEngineVersion
    ) -> DBEngineVersion:
        """Deletes a custom engine version. To run this command, make sure you meet
        the following prerequisites:

        -  The CEV must not be the default for RDS Custom. If it is, change the
           default before running this command.

        -  The CEV must not be associated with an RDS Custom DB instance, RDS
           Custom instance snapshot, or automated backup of your RDS Custom
           instance.

        Typically, deletion takes a few minutes.

        The MediaImport service that imports files from Amazon S3 to create CEVs
        isn't integrated with Amazon Web Services CloudTrail. If you turn on
        data logging for Amazon RDS in CloudTrail, calls to the
        ``DeleteCustomDbEngineVersion`` event aren't logged. However, you might
        see calls from the API gateway that accesses your Amazon S3 bucket.
        These calls originate from the MediaImport service for the
        ``DeleteCustomDbEngineVersion`` event.

        For more information, see `Deleting a
        CEV <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/custom-cev.html#custom-cev.delete>`__
        in the *Amazon RDS User Guide*.

        :param engine: The database engine.
        :param engine_version: The custom engine version (CEV) for your DB instance.
        :returns: DBEngineVersion
        :raises CustomDBEngineVersionNotFoundFault:
        :raises InvalidCustomDBEngineVersionStateFault:
        """
        raise NotImplementedError

    @handler("DeleteDBCluster")
    def delete_db_cluster(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        skip_final_snapshot: Boolean = None,
        final_db_snapshot_identifier: String = None,
    ) -> DeleteDBClusterResult:
        """The DeleteDBCluster action deletes a previously provisioned DB cluster.
        When you delete a DB cluster, all automated backups for that DB cluster
        are deleted and can't be recovered. Manual DB cluster snapshots of the
        specified DB cluster are not deleted.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_identifier: The DB cluster identifier for the DB cluster to be deleted.
        :param skip_final_snapshot: A value that indicates whether to skip the creation of a final DB
        cluster snapshot before the DB cluster is deleted.
        :param final_db_snapshot_identifier: The DB cluster snapshot identifier of the new DB cluster snapshot
        created when ``SkipFinalSnapshot`` is disabled.
        :returns: DeleteDBClusterResult
        :raises DBClusterNotFoundFault:
        :raises InvalidDBClusterStateFault:
        :raises DBClusterSnapshotAlreadyExistsFault:
        :raises SnapshotQuotaExceededFault:
        :raises InvalidDBClusterSnapshotStateFault:
        """
        raise NotImplementedError

    @handler("DeleteDBClusterEndpoint")
    def delete_db_cluster_endpoint(
        self, context: RequestContext, db_cluster_endpoint_identifier: String
    ) -> DBClusterEndpoint:
        """Deletes a custom endpoint and removes it from an Amazon Aurora DB
        cluster.

        This action only applies to Aurora DB clusters.

        :param db_cluster_endpoint_identifier: The identifier associated with the custom endpoint.
        :returns: DBClusterEndpoint
        :raises InvalidDBClusterEndpointStateFault:
        :raises DBClusterEndpointNotFoundFault:
        :raises InvalidDBClusterStateFault:
        """
        raise NotImplementedError

    @handler("DeleteDBClusterParameterGroup")
    def delete_db_cluster_parameter_group(
        self, context: RequestContext, db_cluster_parameter_group_name: String
    ) -> None:
        """Deletes a specified DB cluster parameter group. The DB cluster parameter
        group to be deleted can't be associated with any DB clusters.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_parameter_group_name: The name of the DB cluster parameter group.
        :raises InvalidDBParameterGroupStateFault:
        :raises DBParameterGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DeleteDBClusterSnapshot")
    def delete_db_cluster_snapshot(
        self, context: RequestContext, db_cluster_snapshot_identifier: String
    ) -> DeleteDBClusterSnapshotResult:
        """Deletes a DB cluster snapshot. If the snapshot is being copied, the copy
        operation is terminated.

        The DB cluster snapshot must be in the ``available`` state to be
        deleted.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_snapshot_identifier: The identifier of the DB cluster snapshot to delete.
        :returns: DeleteDBClusterSnapshotResult
        :raises InvalidDBClusterSnapshotStateFault:
        :raises DBClusterSnapshotNotFoundFault:
        """
        raise NotImplementedError

    @handler("DeleteDBInstance")
    def delete_db_instance(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        skip_final_snapshot: Boolean = None,
        final_db_snapshot_identifier: String = None,
        delete_automated_backups: BooleanOptional = None,
    ) -> DeleteDBInstanceResult:
        """The DeleteDBInstance action deletes a previously provisioned DB
        instance. When you delete a DB instance, all automated backups for that
        instance are deleted and can't be recovered. Manual DB snapshots of the
        DB instance to be deleted by ``DeleteDBInstance`` are not deleted.

        If you request a final DB snapshot the status of the Amazon RDS DB
        instance is ``deleting`` until the DB snapshot is created. The API
        action ``DescribeDBInstance`` is used to monitor the status of this
        operation. The action can't be canceled or reverted once submitted.

        When a DB instance is in a failure state and has a status of ``failed``,
        ``incompatible-restore``, or ``incompatible-network``, you can only
        delete it when you skip creation of the final snapshot with the
        ``SkipFinalSnapshot`` parameter.

        If the specified DB instance is part of an Amazon Aurora DB cluster, you
        can't delete the DB instance if both of the following conditions are
        true:

        -  The DB cluster is a read replica of another Amazon Aurora DB cluster.

        -  The DB instance is the only instance in the DB cluster.

        To delete a DB instance in this case, first call the
        ``PromoteReadReplicaDBCluster`` API action to promote the DB cluster so
        it's no longer a read replica. After the promotion completes, then call
        the ``DeleteDBInstance`` API action to delete the final instance in the
        DB cluster.

        :param db_instance_identifier: The DB instance identifier for the DB instance to be deleted.
        :param skip_final_snapshot: A value that indicates whether to skip the creation of a final DB
        snapshot before deleting the instance.
        :param final_db_snapshot_identifier: The ``DBSnapshotIdentifier`` of the new ``DBSnapshot`` created when the
        ``SkipFinalSnapshot`` parameter is disabled.
        :param delete_automated_backups: A value that indicates whether to remove automated backups immediately
        after the DB instance is deleted.
        :returns: DeleteDBInstanceResult
        :raises DBInstanceNotFoundFault:
        :raises InvalidDBInstanceStateFault:
        :raises DBSnapshotAlreadyExistsFault:
        :raises SnapshotQuotaExceededFault:
        :raises InvalidDBClusterStateFault:
        :raises DBInstanceAutomatedBackupQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("DeleteDBInstanceAutomatedBackup")
    def delete_db_instance_automated_backup(
        self,
        context: RequestContext,
        dbi_resource_id: String = None,
        db_instance_automated_backups_arn: String = None,
    ) -> DeleteDBInstanceAutomatedBackupResult:
        """Deletes automated backups using the ``DbiResourceId`` value of the
        source DB instance or the Amazon Resource Name (ARN) of the automated
        backups.

        :param dbi_resource_id: The identifier for the source DB instance, which can't be changed and
        which is unique to an Amazon Web Services Region.
        :param db_instance_automated_backups_arn: The Amazon Resource Name (ARN) of the automated backups to delete, for
        example,
        ``arn:aws:rds:us-east-1:123456789012:auto-backup:ab-L2IJCEXJP7XQ7HOJ4SIEXAMPLE``.
        :returns: DeleteDBInstanceAutomatedBackupResult
        :raises InvalidDBInstanceAutomatedBackupStateFault:
        :raises DBInstanceAutomatedBackupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DeleteDBParameterGroup")
    def delete_db_parameter_group(
        self, context: RequestContext, db_parameter_group_name: String
    ) -> None:
        """Deletes a specified DB parameter group. The DB parameter group to be
        deleted can't be associated with any DB instances.

        :param db_parameter_group_name: The name of the DB parameter group.
        :raises InvalidDBParameterGroupStateFault:
        :raises DBParameterGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DeleteDBProxy")
    def delete_db_proxy(
        self, context: RequestContext, db_proxy_name: String
    ) -> DeleteDBProxyResponse:
        """Deletes an existing DB proxy.

        :param db_proxy_name: The name of the DB proxy to delete.
        :returns: DeleteDBProxyResponse
        :raises DBProxyNotFoundFault:
        :raises InvalidDBProxyStateFault:
        """
        raise NotImplementedError

    @handler("DeleteDBProxyEndpoint")
    def delete_db_proxy_endpoint(
        self, context: RequestContext, db_proxy_endpoint_name: DBProxyEndpointName
    ) -> DeleteDBProxyEndpointResponse:
        """Deletes a ``DBProxyEndpoint``. Doing so removes the ability to access
        the DB proxy using the endpoint that you defined. The endpoint that you
        delete might have provided capabilities such as read/write or read-only
        operations, or using a different VPC than the DB proxy's default VPC.

        :param db_proxy_endpoint_name: The name of the DB proxy endpoint to delete.
        :returns: DeleteDBProxyEndpointResponse
        :raises DBProxyEndpointNotFoundFault:
        :raises InvalidDBProxyEndpointStateFault:
        """
        raise NotImplementedError

    @handler("DeleteDBSecurityGroup")
    def delete_db_security_group(
        self, context: RequestContext, db_security_group_name: String
    ) -> None:
        """Deletes a DB security group.

        The specified DB security group must not be associated with any DB
        instances.

        :param db_security_group_name: The name of the DB security group to delete.
        :raises InvalidDBSecurityGroupStateFault:
        :raises DBSecurityGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DeleteDBSnapshot")
    def delete_db_snapshot(
        self, context: RequestContext, db_snapshot_identifier: String
    ) -> DeleteDBSnapshotResult:
        """Deletes a DB snapshot. If the snapshot is being copied, the copy
        operation is terminated.

        The DB snapshot must be in the ``available`` state to be deleted.

        :param db_snapshot_identifier: The DB snapshot identifier.
        :returns: DeleteDBSnapshotResult
        :raises InvalidDBSnapshotStateFault:
        :raises DBSnapshotNotFoundFault:
        """
        raise NotImplementedError

    @handler("DeleteDBSubnetGroup")
    def delete_db_subnet_group(self, context: RequestContext, db_subnet_group_name: String) -> None:
        """Deletes a DB subnet group.

        The specified database subnet group must not be associated with any DB
        instances.

        :param db_subnet_group_name: The name of the database subnet group to delete.
        :raises InvalidDBSubnetGroupStateFault:
        :raises InvalidDBSubnetStateFault:
        :raises DBSubnetGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DeleteEventSubscription")
    def delete_event_subscription(
        self, context: RequestContext, subscription_name: String
    ) -> DeleteEventSubscriptionResult:
        """Deletes an RDS event notification subscription.

        :param subscription_name: The name of the RDS event notification subscription you want to delete.
        :returns: DeleteEventSubscriptionResult
        :raises SubscriptionNotFoundFault:
        :raises InvalidEventSubscriptionStateFault:
        """
        raise NotImplementedError

    @handler("DeleteGlobalCluster")
    def delete_global_cluster(
        self, context: RequestContext, global_cluster_identifier: String
    ) -> DeleteGlobalClusterResult:
        """Deletes a global database cluster. The primary and secondary clusters
        must already be detached or destroyed first.

        This action only applies to Aurora DB clusters.

        :param global_cluster_identifier: The cluster identifier of the global database cluster being deleted.
        :returns: DeleteGlobalClusterResult
        :raises GlobalClusterNotFoundFault:
        :raises InvalidGlobalClusterStateFault:
        """
        raise NotImplementedError

    @handler("DeleteOptionGroup")
    def delete_option_group(self, context: RequestContext, option_group_name: String) -> None:
        """Deletes an existing option group.

        :param option_group_name: The name of the option group to be deleted.
        :raises OptionGroupNotFoundFault:
        :raises InvalidOptionGroupStateFault:
        """
        raise NotImplementedError

    @handler("DeregisterDBProxyTargets")
    def deregister_db_proxy_targets(
        self,
        context: RequestContext,
        db_proxy_name: String,
        target_group_name: String = None,
        db_instance_identifiers: StringList = None,
        db_cluster_identifiers: StringList = None,
    ) -> DeregisterDBProxyTargetsResponse:
        """Remove the association between one or more ``DBProxyTarget`` data
        structures and a ``DBProxyTargetGroup``.

        :param db_proxy_name: The identifier of the ``DBProxy`` that is associated with the
        ``DBProxyTargetGroup``.
        :param target_group_name: The identifier of the ``DBProxyTargetGroup``.
        :param db_instance_identifiers: One or more DB instance identifiers.
        :param db_cluster_identifiers: One or more DB cluster identifiers.
        :returns: DeregisterDBProxyTargetsResponse
        :raises DBProxyTargetNotFoundFault:
        :raises DBProxyTargetGroupNotFoundFault:
        :raises DBProxyNotFoundFault:
        :raises InvalidDBProxyStateFault:
        """
        raise NotImplementedError

    @handler("DescribeAccountAttributes")
    def describe_account_attributes(
        self,
        context: RequestContext,
    ) -> AccountAttributesMessage:
        """Lists all of the attributes for a customer account. The attributes
        include Amazon RDS quotas for the account, such as the number of DB
        instances allowed. The description for a quota includes the quota name,
        current usage toward that quota, and the quota's maximum value.

        This command doesn't take any parameters.

        :returns: AccountAttributesMessage
        """
        raise NotImplementedError

    @handler("DescribeCertificates")
    def describe_certificates(
        self,
        context: RequestContext,
        certificate_identifier: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> CertificateMessage:
        """Lists the set of CA certificates provided by Amazon RDS for this Amazon
        Web Services account.

        :param certificate_identifier: The user-supplied certificate identifier.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeCertificates`` request.
        :returns: CertificateMessage
        :raises CertificateNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBClusterBacktracks")
    def describe_db_cluster_backtracks(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        backtrack_identifier: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DBClusterBacktrackMessage:
        """Returns information about backtracks for a DB cluster.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        This action only applies to Aurora MySQL DB clusters.

        :param db_cluster_identifier: The DB cluster identifier of the DB cluster to be described.
        :param backtrack_identifier: If specified, this value is the backtrack identifier of the backtrack to
        be described.
        :param filters: A filter that specifies one or more DB clusters to describe.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBClusterBacktracks`` request.
        :returns: DBClusterBacktrackMessage
        :raises DBClusterNotFoundFault:
        :raises DBClusterBacktrackNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBClusterEndpoints")
    def describe_db_cluster_endpoints(
        self,
        context: RequestContext,
        db_cluster_identifier: String = None,
        db_cluster_endpoint_identifier: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DBClusterEndpointMessage:
        """Returns information about endpoints for an Amazon Aurora DB cluster.

        This action only applies to Aurora DB clusters.

        :param db_cluster_identifier: The DB cluster identifier of the DB cluster associated with the
        endpoint.
        :param db_cluster_endpoint_identifier: The identifier of the endpoint to describe.
        :param filters: A set of name-value pairs that define which endpoints to include in the
        output.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBClusterEndpoints`` request.
        :returns: DBClusterEndpointMessage
        :raises DBClusterNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBClusterParameterGroups")
    def describe_db_cluster_parameter_groups(
        self,
        context: RequestContext,
        db_cluster_parameter_group_name: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DBClusterParameterGroupsMessage:
        """Returns a list of ``DBClusterParameterGroup`` descriptions. If a
        ``DBClusterParameterGroupName`` parameter is specified, the list will
        contain only the description of the specified DB cluster parameter
        group.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_parameter_group_name: The name of a specific DB cluster parameter group to return details for.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBClusterParameterGroups`` request.
        :returns: DBClusterParameterGroupsMessage
        :raises DBParameterGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBClusterParameters")
    def describe_db_cluster_parameters(
        self,
        context: RequestContext,
        db_cluster_parameter_group_name: String,
        source: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DBClusterParameterGroupDetails:
        """Returns the detailed parameter list for a particular DB cluster
        parameter group.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_parameter_group_name: The name of a specific DB cluster parameter group to return parameter
        details for.
        :param source: A value that indicates to return only parameters for a specific source.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBClusterParameters`` request.
        :returns: DBClusterParameterGroupDetails
        :raises DBParameterGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBClusterSnapshotAttributes")
    def describe_db_cluster_snapshot_attributes(
        self, context: RequestContext, db_cluster_snapshot_identifier: String
    ) -> DescribeDBClusterSnapshotAttributesResult:
        """Returns a list of DB cluster snapshot attribute names and values for a
        manual DB cluster snapshot.

        When sharing snapshots with other Amazon Web Services accounts,
        ``DescribeDBClusterSnapshotAttributes`` returns the ``restore``
        attribute and a list of IDs for the Amazon Web Services accounts that
        are authorized to copy or restore the manual DB cluster snapshot. If
        ``all`` is included in the list of values for the ``restore`` attribute,
        then the manual DB cluster snapshot is public and can be copied or
        restored by all Amazon Web Services accounts.

        To add or remove access for an Amazon Web Services account to copy or
        restore a manual DB cluster snapshot, or to make the manual DB cluster
        snapshot public or private, use the ``ModifyDBClusterSnapshotAttribute``
        API action.

        :param db_cluster_snapshot_identifier: The identifier for the DB cluster snapshot to describe the attributes
        for.
        :returns: DescribeDBClusterSnapshotAttributesResult
        :raises DBClusterSnapshotNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBClusterSnapshots")
    def describe_db_cluster_snapshots(
        self,
        context: RequestContext,
        db_cluster_identifier: String = None,
        db_cluster_snapshot_identifier: String = None,
        snapshot_type: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
        include_shared: Boolean = None,
        include_public: Boolean = None,
    ) -> DBClusterSnapshotMessage:
        """Returns information about DB cluster snapshots. This API action supports
        pagination.

        For more information on Amazon Aurora DB clusters, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_identifier: The ID of the DB cluster to retrieve the list of DB cluster snapshots
        for.
        :param db_cluster_snapshot_identifier: A specific DB cluster snapshot identifier to describe.
        :param snapshot_type: The type of DB cluster snapshots to be returned.
        :param filters: A filter that specifies one or more DB cluster snapshots to describe.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBClusterSnapshots`` request.
        :param include_shared: A value that indicates whether to include shared manual DB cluster
        snapshots from other Amazon Web Services accounts that this Amazon Web
        Services account has been given permission to copy or restore.
        :param include_public: A value that indicates whether to include manual DB cluster snapshots
        that are public and can be copied or restored by any Amazon Web Services
        account.
        :returns: DBClusterSnapshotMessage
        :raises DBClusterSnapshotNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBClusters")
    def describe_db_clusters(
        self,
        context: RequestContext,
        db_cluster_identifier: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
        include_shared: Boolean = None,
    ) -> DBClusterMessage:
        """Returns information about Amazon Aurora DB clusters and Multi-AZ DB
        clusters. This API supports pagination.

        For more information on Amazon Aurora DB clusters, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        This operation can also return information for Amazon Neptune DB
        instances and Amazon DocumentDB instances.

        :param db_cluster_identifier: The user-supplied DB cluster identifier.
        :param filters: A filter that specifies one or more DB clusters to describe.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBClusters`` request.
        :param include_shared: Optional Boolean parameter that specifies whether the output includes
        information about clusters shared from other Amazon Web Services
        accounts.
        :returns: DBClusterMessage
        :raises DBClusterNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBEngineVersions")
    def describe_db_engine_versions(
        self,
        context: RequestContext,
        engine: String = None,
        engine_version: String = None,
        db_parameter_group_family: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
        default_only: Boolean = None,
        list_supported_character_sets: BooleanOptional = None,
        list_supported_timezones: BooleanOptional = None,
        include_all: BooleanOptional = None,
    ) -> DBEngineVersionMessage:
        """Returns a list of the available DB engines.

        :param engine: The database engine to return.
        :param engine_version: The database engine version to return.
        :param db_parameter_group_family: The name of a specific DB parameter group family to return details for.
        :param filters: A filter that specifies one or more DB engine versions to describe.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous request.
        :param default_only: A value that indicates whether only the default version of the specified
        engine or engine and major version combination is returned.
        :param list_supported_character_sets: A value that indicates whether to list the supported character sets for
        each engine version.
        :param list_supported_timezones: A value that indicates whether to list the supported time zones for each
        engine version.
        :param include_all: A value that indicates whether to include engine versions that aren't
        available in the list.
        :returns: DBEngineVersionMessage
        """
        raise NotImplementedError

    @handler("DescribeDBInstanceAutomatedBackups")
    def describe_db_instance_automated_backups(
        self,
        context: RequestContext,
        dbi_resource_id: String = None,
        db_instance_identifier: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
        db_instance_automated_backups_arn: String = None,
    ) -> DBInstanceAutomatedBackupMessage:
        """Displays backups for both current and deleted instances. For example,
        use this operation to find details about automated backups for
        previously deleted instances. Current instances with retention periods
        greater than zero (0) are returned for both the
        ``DescribeDBInstanceAutomatedBackups`` and ``DescribeDBInstances``
        operations.

        All parameters are optional.

        :param dbi_resource_id: The resource ID of the DB instance that is the source of the automated
        backup.
        :param db_instance_identifier: (Optional) The user-supplied instance identifier.
        :param filters: A filter that specifies which resources to return based on status.
        :param max_records: The maximum number of records to include in the response.
        :param marker: The pagination token provided in the previous request.
        :param db_instance_automated_backups_arn: The Amazon Resource Name (ARN) of the replicated automated backups, for
        example,
        ``arn:aws:rds:us-east-1:123456789012:auto-backup:ab-L2IJCEXJP7XQ7HOJ4SIEXAMPLE``.
        :returns: DBInstanceAutomatedBackupMessage
        :raises DBInstanceAutomatedBackupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBInstances")
    def describe_db_instances(
        self,
        context: RequestContext,
        db_instance_identifier: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DBInstanceMessage:
        """Returns information about provisioned RDS instances. This API supports
        pagination.

        This operation can also return information for Amazon Neptune DB
        instances and Amazon DocumentDB instances.

        :param db_instance_identifier: The user-supplied instance identifier.
        :param filters: A filter that specifies one or more DB instances to describe.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBInstances`` request.
        :returns: DBInstanceMessage
        :raises DBInstanceNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBLogFiles")
    def describe_db_log_files(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        filename_contains: String = None,
        file_last_written: Long = None,
        file_size: Long = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DescribeDBLogFilesResponse:
        """Returns a list of DB log files for the DB instance.

        This command doesn't apply to RDS Custom.

        :param db_instance_identifier: The customer-assigned name of the DB instance that contains the log
        files you want to list.
        :param filename_contains: Filters the available log files for log file names that contain the
        specified string.
        :param file_last_written: Filters the available log files for files written since the specified
        date, in POSIX timestamp format with milliseconds.
        :param file_size: Filters the available log files for files larger than the specified
        size.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: The pagination token provided in the previous request.
        :returns: DescribeDBLogFilesResponse
        :raises DBInstanceNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBParameterGroups")
    def describe_db_parameter_groups(
        self,
        context: RequestContext,
        db_parameter_group_name: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DBParameterGroupsMessage:
        """Returns a list of ``DBParameterGroup`` descriptions. If a
        ``DBParameterGroupName`` is specified, the list will contain only the
        description of the specified DB parameter group.

        :param db_parameter_group_name: The name of a specific DB parameter group to return details for.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBParameterGroups`` request.
        :returns: DBParameterGroupsMessage
        :raises DBParameterGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBParameters")
    def describe_db_parameters(
        self,
        context: RequestContext,
        db_parameter_group_name: String,
        source: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DBParameterGroupDetails:
        """Returns the detailed parameter list for a particular DB parameter group.

        :param db_parameter_group_name: The name of a specific DB parameter group to return details for.
        :param source: The parameter types to return.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBParameters`` request.
        :returns: DBParameterGroupDetails
        :raises DBParameterGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBProxies")
    def describe_db_proxies(
        self,
        context: RequestContext,
        db_proxy_name: String = None,
        filters: FilterList = None,
        marker: String = None,
        max_records: MaxRecords = None,
    ) -> DescribeDBProxiesResponse:
        """Returns information about DB proxies.

        :param db_proxy_name: The name of the DB proxy.
        :param filters: This parameter is not currently supported.
        :param marker: An optional pagination token provided by a previous request.
        :param max_records: The maximum number of records to include in the response.
        :returns: DescribeDBProxiesResponse
        :raises DBProxyNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBProxyEndpoints")
    def describe_db_proxy_endpoints(
        self,
        context: RequestContext,
        db_proxy_name: DBProxyName = None,
        db_proxy_endpoint_name: DBProxyEndpointName = None,
        filters: FilterList = None,
        marker: String = None,
        max_records: MaxRecords = None,
    ) -> DescribeDBProxyEndpointsResponse:
        """Returns information about DB proxy endpoints.

        :param db_proxy_name: The name of the DB proxy whose endpoints you want to describe.
        :param db_proxy_endpoint_name: The name of a DB proxy endpoint to describe.
        :param filters: This parameter is not currently supported.
        :param marker: An optional pagination token provided by a previous request.
        :param max_records: The maximum number of records to include in the response.
        :returns: DescribeDBProxyEndpointsResponse
        :raises DBProxyNotFoundFault:
        :raises DBProxyEndpointNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBProxyTargetGroups")
    def describe_db_proxy_target_groups(
        self,
        context: RequestContext,
        db_proxy_name: String,
        target_group_name: String = None,
        filters: FilterList = None,
        marker: String = None,
        max_records: MaxRecords = None,
    ) -> DescribeDBProxyTargetGroupsResponse:
        """Returns information about DB proxy target groups, represented by
        ``DBProxyTargetGroup`` data structures.

        :param db_proxy_name: The identifier of the ``DBProxy`` associated with the target group.
        :param target_group_name: The identifier of the ``DBProxyTargetGroup`` to describe.
        :param filters: This parameter is not currently supported.
        :param marker: An optional pagination token provided by a previous request.
        :param max_records: The maximum number of records to include in the response.
        :returns: DescribeDBProxyTargetGroupsResponse
        :raises DBProxyNotFoundFault:
        :raises DBProxyTargetGroupNotFoundFault:
        :raises InvalidDBProxyStateFault:
        """
        raise NotImplementedError

    @handler("DescribeDBProxyTargets")
    def describe_db_proxy_targets(
        self,
        context: RequestContext,
        db_proxy_name: String,
        target_group_name: String = None,
        filters: FilterList = None,
        marker: String = None,
        max_records: MaxRecords = None,
    ) -> DescribeDBProxyTargetsResponse:
        """Returns information about ``DBProxyTarget`` objects. This API supports
        pagination.

        :param db_proxy_name: The identifier of the ``DBProxyTarget`` to describe.
        :param target_group_name: The identifier of the ``DBProxyTargetGroup`` to describe.
        :param filters: This parameter is not currently supported.
        :param marker: An optional pagination token provided by a previous request.
        :param max_records: The maximum number of records to include in the response.
        :returns: DescribeDBProxyTargetsResponse
        :raises DBProxyNotFoundFault:
        :raises DBProxyTargetNotFoundFault:
        :raises DBProxyTargetGroupNotFoundFault:
        :raises InvalidDBProxyStateFault:
        """
        raise NotImplementedError

    @handler("DescribeDBSecurityGroups")
    def describe_db_security_groups(
        self,
        context: RequestContext,
        db_security_group_name: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DBSecurityGroupMessage:
        """Returns a list of ``DBSecurityGroup`` descriptions. If a
        ``DBSecurityGroupName`` is specified, the list will contain only the
        descriptions of the specified DB security group.

        :param db_security_group_name: The name of the DB security group to return details for.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBSecurityGroups`` request.
        :returns: DBSecurityGroupMessage
        :raises DBSecurityGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBSnapshotAttributes")
    def describe_db_snapshot_attributes(
        self, context: RequestContext, db_snapshot_identifier: String
    ) -> DescribeDBSnapshotAttributesResult:
        """Returns a list of DB snapshot attribute names and values for a manual DB
        snapshot.

        When sharing snapshots with other Amazon Web Services accounts,
        ``DescribeDBSnapshotAttributes`` returns the ``restore`` attribute and a
        list of IDs for the Amazon Web Services accounts that are authorized to
        copy or restore the manual DB snapshot. If ``all`` is included in the
        list of values for the ``restore`` attribute, then the manual DB
        snapshot is public and can be copied or restored by all Amazon Web
        Services accounts.

        To add or remove access for an Amazon Web Services account to copy or
        restore a manual DB snapshot, or to make the manual DB snapshot public
        or private, use the ``ModifyDBSnapshotAttribute`` API action.

        :param db_snapshot_identifier: The identifier for the DB snapshot to describe the attributes for.
        :returns: DescribeDBSnapshotAttributesResult
        :raises DBSnapshotNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBSnapshots")
    def describe_db_snapshots(
        self,
        context: RequestContext,
        db_instance_identifier: String = None,
        db_snapshot_identifier: String = None,
        snapshot_type: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
        include_shared: Boolean = None,
        include_public: Boolean = None,
        dbi_resource_id: String = None,
    ) -> DBSnapshotMessage:
        """Returns information about DB snapshots. This API action supports
        pagination.

        :param db_instance_identifier: The ID of the DB instance to retrieve the list of DB snapshots for.
        :param db_snapshot_identifier: A specific DB snapshot identifier to describe.
        :param snapshot_type: The type of snapshots to be returned.
        :param filters: A filter that specifies one or more DB snapshots to describe.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeDBSnapshots`` request.
        :param include_shared: A value that indicates whether to include shared manual DB cluster
        snapshots from other Amazon Web Services accounts that this Amazon Web
        Services account has been given permission to copy or restore.
        :param include_public: A value that indicates whether to include manual DB cluster snapshots
        that are public and can be copied or restored by any Amazon Web Services
        account.
        :param dbi_resource_id: A specific DB resource ID to describe.
        :returns: DBSnapshotMessage
        :raises DBSnapshotNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeDBSubnetGroups")
    def describe_db_subnet_groups(
        self,
        context: RequestContext,
        db_subnet_group_name: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DBSubnetGroupMessage:
        """Returns a list of DBSubnetGroup descriptions. If a DBSubnetGroupName is
        specified, the list will contain only the descriptions of the specified
        DBSubnetGroup.

        For an overview of CIDR ranges, go to the `Wikipedia
        Tutorial <http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing>`__.

        :param db_subnet_group_name: The name of the DB subnet group to return details for.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        DescribeDBSubnetGroups request.
        :returns: DBSubnetGroupMessage
        :raises DBSubnetGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeEngineDefaultClusterParameters")
    def describe_engine_default_cluster_parameters(
        self,
        context: RequestContext,
        db_parameter_group_family: String,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DescribeEngineDefaultClusterParametersResult:
        """Returns the default engine and system parameter information for the
        cluster database engine.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        :param db_parameter_group_family: The name of the DB cluster parameter group family to return engine
        parameter information for.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeEngineDefaultClusterParameters`` request.
        :returns: DescribeEngineDefaultClusterParametersResult
        """
        raise NotImplementedError

    @handler("DescribeEngineDefaultParameters")
    def describe_engine_default_parameters(
        self,
        context: RequestContext,
        db_parameter_group_family: String,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DescribeEngineDefaultParametersResult:
        """Returns the default engine and system parameter information for the
        specified database engine.

        :param db_parameter_group_family: The name of the DB parameter group family.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeEngineDefaultParameters`` request.
        :returns: DescribeEngineDefaultParametersResult
        """
        raise NotImplementedError

    @handler("DescribeEventCategories")
    def describe_event_categories(
        self, context: RequestContext, source_type: String = None, filters: FilterList = None
    ) -> EventCategoriesMessage:
        """Displays a list of categories for all event source types, or, if
        specified, for a specified source type. You can also see this list in
        the "Amazon RDS event categories and event messages" section of the
        `Amazon RDS User
        Guide <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Events.Messages.html>`__
        or the `Amazon Aurora User
        Guide <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_Events.Messages.html>`__
        .

        :param source_type: The type of source that is generating the events.
        :param filters: This parameter isn't currently supported.
        :returns: EventCategoriesMessage
        """
        raise NotImplementedError

    @handler("DescribeEventSubscriptions")
    def describe_event_subscriptions(
        self,
        context: RequestContext,
        subscription_name: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> EventSubscriptionsMessage:
        """Lists all the subscription descriptions for a customer account. The
        description for a subscription includes ``SubscriptionName``,
        ``SNSTopicARN``, ``CustomerID``, ``SourceType``, ``SourceID``,
        ``CreationTime``, and ``Status``.

        If you specify a ``SubscriptionName``, lists the description for that
        subscription.

        :param subscription_name: The name of the RDS event notification subscription you want to
        describe.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        DescribeOrderableDBInstanceOptions request.
        :returns: EventSubscriptionsMessage
        :raises SubscriptionNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeEvents")
    def describe_events(
        self,
        context: RequestContext,
        source_identifier: String = None,
        source_type: SourceType = None,
        start_time: TStamp = None,
        end_time: TStamp = None,
        duration: IntegerOptional = None,
        event_categories: EventCategoriesList = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> EventsMessage:
        """Returns events related to DB instances, DB clusters, DB parameter
        groups, DB security groups, DB snapshots, DB cluster snapshots, and RDS
        Proxies for the past 14 days. Events specific to a particular DB
        instance, DB cluster, DB parameter group, DB security group, DB
        snapshot, DB cluster snapshot group, or RDS Proxy can be obtained by
        providing the name as a parameter.

        By default, RDS returns events that were generated in the past hour.

        :param source_identifier: The identifier of the event source for which events are returned.
        :param source_type: The event source to retrieve events for.
        :param start_time: The beginning of the time interval to retrieve events for, specified in
        ISO 8601 format.
        :param end_time: The end of the time interval for which to retrieve events, specified in
        ISO 8601 format.
        :param duration: The number of minutes to retrieve events for.
        :param event_categories: A list of event categories that trigger notifications for a event
        notification subscription.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous DescribeEvents
        request.
        :returns: EventsMessage
        """
        raise NotImplementedError

    @handler("DescribeExportTasks")
    def describe_export_tasks(
        self,
        context: RequestContext,
        export_task_identifier: String = None,
        source_arn: String = None,
        filters: FilterList = None,
        marker: String = None,
        max_records: MaxRecords = None,
    ) -> ExportTasksMessage:
        """Returns information about a snapshot export to Amazon S3. This API
        operation supports pagination.

        :param export_task_identifier: The identifier of the snapshot export task to be described.
        :param source_arn: The Amazon Resource Name (ARN) of the snapshot exported to Amazon S3.
        :param filters: Filters specify one or more snapshot exports to describe.
        :param marker: An optional pagination token provided by a previous
        ``DescribeExportTasks`` request.
        :param max_records: The maximum number of records to include in the response.
        :returns: ExportTasksMessage
        :raises ExportTaskNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeGlobalClusters")
    def describe_global_clusters(
        self,
        context: RequestContext,
        global_cluster_identifier: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> GlobalClustersMessage:
        """Returns information about Aurora global database clusters. This API
        supports pagination.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        This action only applies to Aurora DB clusters.

        :param global_cluster_identifier: The user-supplied DB cluster identifier.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeGlobalClusters`` request.
        :returns: GlobalClustersMessage
        :raises GlobalClusterNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeOptionGroupOptions")
    def describe_option_group_options(
        self,
        context: RequestContext,
        engine_name: String,
        major_engine_version: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> OptionGroupOptionsMessage:
        """Describes all available options.

        :param engine_name: A required parameter.
        :param major_engine_version: If specified, filters the results to include only options for the
        specified major engine version.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous request.
        :returns: OptionGroupOptionsMessage
        """
        raise NotImplementedError

    @handler("DescribeOptionGroups")
    def describe_option_groups(
        self,
        context: RequestContext,
        option_group_name: String = None,
        filters: FilterList = None,
        marker: String = None,
        max_records: IntegerOptional = None,
        engine_name: String = None,
        major_engine_version: String = None,
    ) -> OptionGroups:
        """Describes the available option groups.

        :param option_group_name: The name of the option group to describe.
        :param filters: This parameter isn't currently supported.
        :param marker: An optional pagination token provided by a previous DescribeOptionGroups
        request.
        :param max_records: The maximum number of records to include in the response.
        :param engine_name: Filters the list of option groups to only include groups associated with
        a specific database engine.
        :param major_engine_version: Filters the list of option groups to only include groups associated with
        a specific database engine version.
        :returns: OptionGroups
        :raises OptionGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeOrderableDBInstanceOptions")
    def describe_orderable_db_instance_options(
        self,
        context: RequestContext,
        engine: String,
        engine_version: String = None,
        db_instance_class: String = None,
        license_model: String = None,
        availability_zone_group: String = None,
        vpc: BooleanOptional = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> OrderableDBInstanceOptionsMessage:
        """Returns a list of orderable DB instance options for the specified DB
        engine, DB engine version, and DB instance class.

        :param engine: The name of the engine to retrieve DB instance options for.
        :param engine_version: The engine version filter value.
        :param db_instance_class: The DB instance class filter value.
        :param license_model: The license model filter value.
        :param availability_zone_group: The Availability Zone group associated with a Local Zone.
        :param vpc: A value that indicates whether to show only VPC or non-VPC offerings.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        DescribeOrderableDBInstanceOptions request.
        :returns: OrderableDBInstanceOptionsMessage
        """
        raise NotImplementedError

    @handler("DescribePendingMaintenanceActions")
    def describe_pending_maintenance_actions(
        self,
        context: RequestContext,
        resource_identifier: String = None,
        filters: FilterList = None,
        marker: String = None,
        max_records: IntegerOptional = None,
    ) -> PendingMaintenanceActionsMessage:
        """Returns a list of resources (for example, DB instances) that have at
        least one pending maintenance action.

        :param resource_identifier: The ARN of a resource to return pending maintenance actions for.
        :param filters: A filter that specifies one or more resources to return pending
        maintenance actions for.
        :param marker: An optional pagination token provided by a previous
        ``DescribePendingMaintenanceActions`` request.
        :param max_records: The maximum number of records to include in the response.
        :returns: PendingMaintenanceActionsMessage
        :raises ResourceNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeReservedDBInstances")
    def describe_reserved_db_instances(
        self,
        context: RequestContext,
        reserved_db_instance_id: String = None,
        reserved_db_instances_offering_id: String = None,
        db_instance_class: String = None,
        duration: String = None,
        product_description: String = None,
        offering_type: String = None,
        multi_az: BooleanOptional = None,
        lease_id: String = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> ReservedDBInstanceMessage:
        """Returns information about reserved DB instances for this account, or
        about a specified reserved DB instance.

        :param reserved_db_instance_id: The reserved DB instance identifier filter value.
        :param reserved_db_instances_offering_id: The offering identifier filter value.
        :param db_instance_class: The DB instance class filter value.
        :param duration: The duration filter value, specified in years or seconds.
        :param product_description: The product description filter value.
        :param offering_type: The offering type filter value.
        :param multi_az: A value that indicates whether to show only those reservations that
        support Multi-AZ.
        :param lease_id: The lease identifier filter value.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous request.
        :returns: ReservedDBInstanceMessage
        :raises ReservedDBInstanceNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeReservedDBInstancesOfferings")
    def describe_reserved_db_instances_offerings(
        self,
        context: RequestContext,
        reserved_db_instances_offering_id: String = None,
        db_instance_class: String = None,
        duration: String = None,
        product_description: String = None,
        offering_type: String = None,
        multi_az: BooleanOptional = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> ReservedDBInstancesOfferingMessage:
        """Lists available reserved DB instance offerings.

        :param reserved_db_instances_offering_id: The offering identifier filter value.
        :param db_instance_class: The DB instance class filter value.
        :param duration: Duration filter value, specified in years or seconds.
        :param product_description: Product description filter value.
        :param offering_type: The offering type filter value.
        :param multi_az: A value that indicates whether to show only those reservations that
        support Multi-AZ.
        :param filters: This parameter isn't currently supported.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous request.
        :returns: ReservedDBInstancesOfferingMessage
        :raises ReservedDBInstancesOfferingNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeSourceRegions")
    def describe_source_regions(
        self,
        context: RequestContext,
        region_name: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
        filters: FilterList = None,
    ) -> SourceRegionMessage:
        """Returns a list of the source Amazon Web Services Regions where the
        current Amazon Web Services Region can create a read replica, copy a DB
        snapshot from, or replicate automated backups from. This API action
        supports pagination.

        :param region_name: The source Amazon Web Services Region name.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional pagination token provided by a previous
        ``DescribeSourceRegions`` request.
        :param filters: This parameter isn't currently supported.
        :returns: SourceRegionMessage
        """
        raise NotImplementedError

    @handler("DescribeValidDBInstanceModifications")
    def describe_valid_db_instance_modifications(
        self, context: RequestContext, db_instance_identifier: String
    ) -> DescribeValidDBInstanceModificationsResult:
        """You can call ``DescribeValidDBInstanceModifications`` to learn what
        modifications you can make to your DB instance. You can use this
        information when you call ``ModifyDBInstance``.

        This command doesn't apply to RDS Custom.

        :param db_instance_identifier: The customer identifier or the ARN of your DB instance.
        :returns: DescribeValidDBInstanceModificationsResult
        :raises DBInstanceNotFoundFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError

    @handler("DownloadDBLogFilePortion")
    def download_db_log_file_portion(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        log_file_name: String,
        marker: String = None,
        number_of_lines: Integer = None,
    ) -> DownloadDBLogFilePortionDetails:
        """Downloads all or a portion of the specified log file, up to 1 MB in
        size.

        This command doesn't apply to RDS Custom.

        :param db_instance_identifier: The customer-assigned name of the DB instance that contains the log
        files you want to list.
        :param log_file_name: The name of the log file to be downloaded.
        :param marker: The pagination token provided in the previous request or "0".
        :param number_of_lines: The number of lines to download.
        :returns: DownloadDBLogFilePortionDetails
        :raises DBInstanceNotFoundFault:
        :raises DBLogFileNotFoundFault:
        """
        raise NotImplementedError

    @handler("FailoverDBCluster")
    def failover_db_cluster(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        target_db_instance_identifier: String = None,
    ) -> FailoverDBClusterResult:
        """Forces a failover for a DB cluster.

        For an Aurora DB cluster, failover for a DB cluster promotes one of the
        Aurora Replicas (read-only instances) in the DB cluster to be the
        primary DB instance (the cluster writer).

        For a Multi-AZ DB cluster, failover for a DB cluster promotes one of the
        readable standby DB instances (read-only instances) in the DB cluster to
        be the primary DB instance (the cluster writer).

        An Amazon Aurora DB cluster automatically fails over to an Aurora
        Replica, if one exists, when the primary DB instance fails. A Multi-AZ
        DB cluster automatically fails over to a readbable standby DB instance
        when the primary DB instance fails.

        To simulate a failure of a primary instance for testing, you can force a
        failover. Because each instance in a DB cluster has its own endpoint
        address, make sure to clean up and re-establish any existing connections
        that use those endpoint addresses when the failover is complete.

        For more information on Amazon Aurora DB clusters, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_identifier: A DB cluster identifier to force a failover for.
        :param target_db_instance_identifier: The name of the DB instance to promote to the primary DB instance.
        :returns: FailoverDBClusterResult
        :raises DBClusterNotFoundFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError

    @handler("FailoverGlobalCluster")
    def failover_global_cluster(
        self,
        context: RequestContext,
        global_cluster_identifier: GlobalClusterIdentifier,
        target_db_cluster_identifier: DBClusterIdentifier,
    ) -> FailoverGlobalClusterResult:
        """Initiates the failover process for an Aurora global database
        (GlobalCluster).

        A failover for an Aurora global database promotes one of secondary
        read-only DB clusters to be the primary DB cluster and demotes the
        primary DB cluster to being a secondary (read-only) DB cluster. In other
        words, the role of the current primary DB cluster and the selected
        (target) DB cluster are switched. The selected secondary DB cluster
        assumes full read/write capabilities for the Aurora global database.

        For more information about failing over an Amazon Aurora global
        database, see `Managed planned failover for Amazon Aurora global
        databases <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html#aurora-global-database-disaster-recovery.managed-failover>`__
        in the *Amazon Aurora User Guide*.

        This action applies to GlobalCluster (Aurora global databases) only. Use
        this action only on healthy Aurora global databases with running Aurora
        DB clusters and no Region-wide outages, to test disaster recovery
        scenarios or to reconfigure your Aurora global database topology.

        :param global_cluster_identifier: Identifier of the Aurora global database (GlobalCluster) that should be
        failed over.
        :param target_db_cluster_identifier: Identifier of the secondary Aurora DB cluster that you want to promote
        to primary for the Aurora global database (GlobalCluster.
        :returns: FailoverGlobalClusterResult
        :raises GlobalClusterNotFoundFault:
        :raises InvalidGlobalClusterStateFault:
        :raises InvalidDBClusterStateFault:
        :raises DBClusterNotFoundFault:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_name: String, filters: FilterList = None
    ) -> TagListMessage:
        """Lists all tags on an Amazon RDS resource.

        For an overview on tagging an Amazon RDS resource, see `Tagging Amazon
        RDS
        Resources <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Tagging.html>`__
        in the *Amazon RDS User Guide*.

        :param resource_name: The Amazon RDS resource with tags to be listed.
        :param filters: This parameter isn't currently supported.
        :returns: TagListMessage
        :raises DBInstanceNotFoundFault:
        :raises DBSnapshotNotFoundFault:
        :raises DBClusterNotFoundFault:
        :raises DBProxyNotFoundFault:
        :raises DBProxyTargetGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("ModifyCertificates")
    def modify_certificates(
        self,
        context: RequestContext,
        certificate_identifier: String = None,
        remove_customer_override: BooleanOptional = None,
    ) -> ModifyCertificatesResult:
        """Override the system-default Secure Sockets Layer/Transport Layer
        Security (SSL/TLS) certificate for Amazon RDS for new DB instances, or
        remove the override.

        By using this operation, you can specify an RDS-approved SSL/TLS
        certificate for new DB instances that is different from the default
        certificate provided by RDS. You can also use this operation to remove
        the override, so that new DB instances use the default certificate
        provided by RDS.

        You might need to override the default certificate in the following
        situations:

        -  You already migrated your applications to support the latest
           certificate authority (CA) certificate, but the new CA certificate is
           not yet the RDS default CA certificate for the specified Amazon Web
           Services Region.

        -  RDS has already moved to a new default CA certificate for the
           specified Amazon Web Services Region, but you are still in the
           process of supporting the new CA certificate. In this case, you
           temporarily need additional time to finish your application changes.

        For more information about rotating your SSL/TLS certificate for RDS DB
        engines, see `Rotating Your SSL/TLS
        Certificate <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL-certificate-rotation.html>`__
        in the *Amazon RDS User Guide*.

        For more information about rotating your SSL/TLS certificate for Aurora
        DB engines, see `Rotating Your SSL/TLS
        Certificate <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.SSL-certificate-rotation.html>`__
        in the *Amazon Aurora User Guide*.

        :param certificate_identifier: The new default certificate identifier to override the current one with.
        :param remove_customer_override: A value that indicates whether to remove the override for the default
        certificate.
        :returns: ModifyCertificatesResult
        :raises CertificateNotFoundFault:
        """
        raise NotImplementedError

    @handler("ModifyCurrentDBClusterCapacity")
    def modify_current_db_cluster_capacity(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        capacity: IntegerOptional = None,
        seconds_before_timeout: IntegerOptional = None,
        timeout_action: String = None,
    ) -> DBClusterCapacityInfo:
        """Set the capacity of an Aurora Serverless v1 DB cluster to a specific
        value.

        Aurora Serverless v1 scales seamlessly based on the workload on the DB
        cluster. In some cases, the capacity might not scale fast enough to meet
        a sudden change in workload, such as a large number of new transactions.
        Call ``ModifyCurrentDBClusterCapacity`` to set the capacity explicitly.

        After this call sets the DB cluster capacity, Aurora Serverless v1 can
        automatically scale the DB cluster based on the cooldown period for
        scaling up and the cooldown period for scaling down.

        For more information about Aurora Serverless v1, see `Using Amazon
        Aurora Serverless
        v1 <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless.html>`__
        in the *Amazon Aurora User Guide*.

        If you call ``ModifyCurrentDBClusterCapacity`` with the default
        ``TimeoutAction``, connections that prevent Aurora Serverless v1 from
        finding a scaling point might be dropped. For more information about
        scaling points, see `Autoscaling for Aurora Serverless
        v1 <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless.how-it-works.html#aurora-serverless.how-it-works.auto-scaling>`__
        in the *Amazon Aurora User Guide*.

        This action only applies to Aurora Serverless v1 DB clusters.

        :param db_cluster_identifier: The DB cluster identifier for the cluster being modified.
        :param capacity: The DB cluster capacity.
        :param seconds_before_timeout: The amount of time, in seconds, that Aurora Serverless v1 tries to find
        a scaling point to perform seamless scaling before enforcing the timeout
        action.
        :param timeout_action: The action to take when the timeout is reached, either
        ``ForceApplyCapacityChange`` or ``RollbackCapacityChange``.
        :returns: DBClusterCapacityInfo
        :raises DBClusterNotFoundFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBClusterCapacityFault:
        """
        raise NotImplementedError

    @handler("ModifyCustomDBEngineVersion")
    def modify_custom_db_engine_version(
        self,
        context: RequestContext,
        engine: CustomEngineName,
        engine_version: CustomEngineVersion,
        description: Description = None,
        status: CustomEngineVersionStatus = None,
    ) -> DBEngineVersion:
        """Modifies the status of a custom engine version (CEV). You can find CEVs
        to modify by calling ``DescribeDBEngineVersions``.

        The MediaImport service that imports files from Amazon S3 to create CEVs
        isn't integrated with Amazon Web Services CloudTrail. If you turn on
        data logging for Amazon RDS in CloudTrail, calls to the
        ``ModifyCustomDbEngineVersion`` event aren't logged. However, you might
        see calls from the API gateway that accesses your Amazon S3 bucket.
        These calls originate from the MediaImport service for the
        ``ModifyCustomDbEngineVersion`` event.

        For more information, see `Modifying CEV
        status <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/custom-cev.html#custom-cev.modify>`__
        in the *Amazon RDS User Guide*.

        :param engine: The DB engine.
        :param engine_version: The custom engine version (CEV) that you want to modify.
        :param description: An optional description of your CEV.
        :param status: The availability status to be assigned to the CEV.
        :returns: DBEngineVersion
        :raises CustomDBEngineVersionNotFoundFault:
        :raises InvalidCustomDBEngineVersionStateFault:
        """
        raise NotImplementedError

    @handler("ModifyDBCluster")
    def modify_db_cluster(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        new_db_cluster_identifier: String = None,
        apply_immediately: Boolean = None,
        backup_retention_period: IntegerOptional = None,
        db_cluster_parameter_group_name: String = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        port: IntegerOptional = None,
        master_user_password: String = None,
        option_group_name: String = None,
        preferred_backup_window: String = None,
        preferred_maintenance_window: String = None,
        enable_iam_database_authentication: BooleanOptional = None,
        backtrack_window: LongOptional = None,
        cloudwatch_logs_export_configuration: CloudwatchLogsExportConfiguration = None,
        engine_version: String = None,
        allow_major_version_upgrade: Boolean = None,
        db_instance_parameter_group_name: String = None,
        domain: String = None,
        domain_iam_role_name: String = None,
        scaling_configuration: ScalingConfiguration = None,
        deletion_protection: BooleanOptional = None,
        enable_http_endpoint: BooleanOptional = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        enable_global_write_forwarding: BooleanOptional = None,
        db_cluster_instance_class: String = None,
        allocated_storage: IntegerOptional = None,
        storage_type: String = None,
        iops: IntegerOptional = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        monitoring_interval: IntegerOptional = None,
        monitoring_role_arn: String = None,
        enable_performance_insights: BooleanOptional = None,
        performance_insights_kms_key_id: String = None,
        performance_insights_retention_period: IntegerOptional = None,
        serverless_v2_scaling_configuration: ServerlessV2ScalingConfiguration = None,
    ) -> ModifyDBClusterResult:
        """Modify the settings for an Amazon Aurora DB cluster or a Multi-AZ DB
        cluster. You can change one or more settings by specifying these
        parameters and the new values in the request.

        For more information on Amazon Aurora DB clusters, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide*.

        :param db_cluster_identifier: The DB cluster identifier for the cluster being modified.
        :param new_db_cluster_identifier: The new DB cluster identifier for the DB cluster when renaming a DB
        cluster.
        :param apply_immediately: A value that indicates whether the modifications in this request and any
        pending modifications are asynchronously applied as soon as possible,
        regardless of the ``PreferredMaintenanceWindow`` setting for the DB
        cluster.
        :param backup_retention_period: The number of days for which automated backups are retained.
        :param db_cluster_parameter_group_name: The name of the DB cluster parameter group to use for the DB cluster.
        :param vpc_security_group_ids: A list of VPC security groups that the DB cluster will belong to.
        :param port: The port number on which the DB cluster accepts connections.
        :param master_user_password: The new password for the master database user.
        :param option_group_name: A value that indicates that the DB cluster should be associated with the
        specified option group.
        :param preferred_backup_window: The daily time range during which automated backups are created if
        automated backups are enabled, using the ``BackupRetentionPeriod``
        parameter.
        :param preferred_maintenance_window: The weekly time range during which system maintenance can occur, in
        Universal Coordinated Time (UTC).
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param backtrack_window: The target backtrack window, in seconds.
        :param cloudwatch_logs_export_configuration: The configuration setting for the log types to be enabled for export to
        CloudWatch Logs for a specific DB cluster.
        :param engine_version: The version number of the database engine to which you want to upgrade.
        :param allow_major_version_upgrade: A value that indicates whether major version upgrades are allowed.
        :param db_instance_parameter_group_name: The name of the DB parameter group to apply to all instances of the DB
        cluster.
        :param domain: The Active Directory directory ID to move the DB cluster to.
        :param domain_iam_role_name: Specify the name of the IAM role to be used when making API calls to the
        Directory Service.
        :param scaling_configuration: The scaling properties of the DB cluster.
        :param deletion_protection: A value that indicates whether the DB cluster has deletion protection
        enabled.
        :param enable_http_endpoint: A value that indicates whether to enable the HTTP endpoint for an Aurora
        Serverless v1 DB cluster.
        :param copy_tags_to_snapshot: A value that indicates whether to copy all tags from the DB cluster to
        snapshots of the DB cluster.
        :param enable_global_write_forwarding: A value that indicates whether to enable this DB cluster to forward
        write operations to the primary cluster of an Aurora global database
        (GlobalCluster).
        :param db_cluster_instance_class: The compute and memory capacity of each DB instance in the Multi-AZ DB
        cluster, for example db.
        :param allocated_storage: The amount of storage in gibibytes (GiB) to allocate to each DB instance
        in the Multi-AZ DB cluster.
        :param storage_type: Specifies the storage type to be associated with the DB cluster.
        :param iops: The amount of Provisioned IOPS (input/output operations per second) to
        be initially allocated for each DB instance in the Multi-AZ DB cluster.
        :param auto_minor_version_upgrade: A value that indicates whether minor engine upgrades are applied
        automatically to the DB cluster during the maintenance window.
        :param monitoring_interval: The interval, in seconds, between points when Enhanced Monitoring
        metrics are collected for the DB cluster.
        :param monitoring_role_arn: The Amazon Resource Name (ARN) for the IAM role that permits RDS to send
        Enhanced Monitoring metrics to Amazon CloudWatch Logs.
        :param enable_performance_insights: A value that indicates whether to turn on Performance Insights for the
        DB cluster.
        :param performance_insights_kms_key_id: The Amazon Web Services KMS key identifier for encryption of Performance
        Insights data.
        :param performance_insights_retention_period: The amount of time, in days, to retain Performance Insights data.
        :param serverless_v2_scaling_configuration: Contains the scaling configuration of an Aurora Serverless v2 DB
        cluster.
        :returns: ModifyDBClusterResult
        :raises DBClusterNotFoundFault:
        :raises InvalidDBClusterStateFault:
        :raises StorageQuotaExceededFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InvalidDBSubnetGroupStateFault:
        :raises InvalidSubnet:
        :raises DBClusterParameterGroupNotFoundFault:
        :raises InvalidDBSecurityGroupStateFault:
        :raises InvalidDBInstanceStateFault:
        :raises DBClusterAlreadyExistsFault:
        :raises DomainNotFoundFault:
        """
        raise NotImplementedError

    @handler("ModifyDBClusterEndpoint")
    def modify_db_cluster_endpoint(
        self,
        context: RequestContext,
        db_cluster_endpoint_identifier: String,
        endpoint_type: String = None,
        static_members: StringList = None,
        excluded_members: StringList = None,
    ) -> DBClusterEndpoint:
        """Modifies the properties of an endpoint in an Amazon Aurora DB cluster.

        This action only applies to Aurora DB clusters.

        :param db_cluster_endpoint_identifier: The identifier of the endpoint to modify.
        :param endpoint_type: The type of the endpoint.
        :param static_members: List of DB instance identifiers that are part of the custom endpoint
        group.
        :param excluded_members: List of DB instance identifiers that aren't part of the custom endpoint
        group.
        :returns: DBClusterEndpoint
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBClusterEndpointStateFault:
        :raises DBClusterEndpointNotFoundFault:
        :raises DBInstanceNotFoundFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError

    @handler("ModifyDBClusterParameterGroup")
    def modify_db_cluster_parameter_group(
        self,
        context: RequestContext,
        db_cluster_parameter_group_name: String,
        parameters: ParametersList,
    ) -> DBClusterParameterGroupNameMessage:
        """Modifies the parameters of a DB cluster parameter group. To modify more
        than one parameter, submit a list of the following: ``ParameterName``,
        ``ParameterValue``, and ``ApplyMethod``. A maximum of 20 parameters can
        be modified in a single request.

        After you create a DB cluster parameter group, you should wait at least
        5 minutes before creating your first DB cluster that uses that DB
        cluster parameter group as the default parameter group. This allows
        Amazon RDS to fully complete the create action before the parameter
        group is used as the default for a new DB cluster. This is especially
        important for parameters that are critical when creating the default
        database for a DB cluster, such as the character set for the default
        database defined by the ``character_set_database`` parameter. You can
        use the *Parameter Groups* option of the `Amazon RDS
        console <https://console.aws.amazon.com/rds/>`__ or the
        ``DescribeDBClusterParameters`` action to verify that your DB cluster
        parameter group has been created or modified.

        If the modified DB cluster parameter group is used by an Aurora
        Serverless v1 cluster, Aurora applies the update immediately. The
        cluster restart might interrupt your workload. In that case, your
        application must reopen any connections and retry any transactions that
        were active when the parameter changes took effect.

        For more information on Amazon Aurora DB clusters, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide.*

        :param db_cluster_parameter_group_name: The name of the DB cluster parameter group to modify.
        :param parameters: A list of parameters in the DB cluster parameter group to modify.
        :returns: DBClusterParameterGroupNameMessage
        :raises DBParameterGroupNotFoundFault:
        :raises InvalidDBParameterGroupStateFault:
        """
        raise NotImplementedError

    @handler("ModifyDBClusterSnapshotAttribute")
    def modify_db_cluster_snapshot_attribute(
        self,
        context: RequestContext,
        db_cluster_snapshot_identifier: String,
        attribute_name: String,
        values_to_add: AttributeValueList = None,
        values_to_remove: AttributeValueList = None,
    ) -> ModifyDBClusterSnapshotAttributeResult:
        """Adds an attribute and values to, or removes an attribute and values
        from, a manual DB cluster snapshot.

        To share a manual DB cluster snapshot with other Amazon Web Services
        accounts, specify ``restore`` as the ``AttributeName`` and use the
        ``ValuesToAdd`` parameter to add a list of IDs of the Amazon Web
        Services accounts that are authorized to restore the manual DB cluster
        snapshot. Use the value ``all`` to make the manual DB cluster snapshot
        public, which means that it can be copied or restored by all Amazon Web
        Services accounts.

        Don't add the ``all`` value for any manual DB cluster snapshots that
        contain private information that you don't want available to all Amazon
        Web Services accounts.

        If a manual DB cluster snapshot is encrypted, it can be shared, but only
        by specifying a list of authorized Amazon Web Services account IDs for
        the ``ValuesToAdd`` parameter. You can't use ``all`` as a value for that
        parameter in this case.

        To view which Amazon Web Services accounts have access to copy or
        restore a manual DB cluster snapshot, or whether a manual DB cluster
        snapshot is public or private, use the
        DescribeDBClusterSnapshotAttributes API action. The accounts are
        returned as values for the ``restore`` attribute.

        :param db_cluster_snapshot_identifier: The identifier for the DB cluster snapshot to modify the attributes for.
        :param attribute_name: The name of the DB cluster snapshot attribute to modify.
        :param values_to_add: A list of DB cluster snapshot attributes to add to the attribute
        specified by ``AttributeName``.
        :param values_to_remove: A list of DB cluster snapshot attributes to remove from the attribute
        specified by ``AttributeName``.
        :returns: ModifyDBClusterSnapshotAttributeResult
        :raises DBClusterSnapshotNotFoundFault:
        :raises InvalidDBClusterSnapshotStateFault:
        :raises SharedSnapshotQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("ModifyDBInstance")
    def modify_db_instance(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        allocated_storage: IntegerOptional = None,
        db_instance_class: String = None,
        db_subnet_group_name: String = None,
        db_security_groups: DBSecurityGroupNameList = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        apply_immediately: Boolean = None,
        master_user_password: String = None,
        db_parameter_group_name: String = None,
        backup_retention_period: IntegerOptional = None,
        preferred_backup_window: String = None,
        preferred_maintenance_window: String = None,
        multi_az: BooleanOptional = None,
        engine_version: String = None,
        allow_major_version_upgrade: Boolean = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        license_model: String = None,
        iops: IntegerOptional = None,
        option_group_name: String = None,
        new_db_instance_identifier: String = None,
        storage_type: String = None,
        tde_credential_arn: String = None,
        tde_credential_password: String = None,
        ca_certificate_identifier: String = None,
        domain: String = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        monitoring_interval: IntegerOptional = None,
        db_port_number: IntegerOptional = None,
        publicly_accessible: BooleanOptional = None,
        monitoring_role_arn: String = None,
        domain_iam_role_name: String = None,
        promotion_tier: IntegerOptional = None,
        enable_iam_database_authentication: BooleanOptional = None,
        enable_performance_insights: BooleanOptional = None,
        performance_insights_kms_key_id: String = None,
        performance_insights_retention_period: IntegerOptional = None,
        cloudwatch_logs_export_configuration: CloudwatchLogsExportConfiguration = None,
        processor_features: ProcessorFeatureList = None,
        use_default_processor_features: BooleanOptional = None,
        deletion_protection: BooleanOptional = None,
        max_allocated_storage: IntegerOptional = None,
        certificate_rotation_restart: BooleanOptional = None,
        replica_mode: ReplicaMode = None,
        enable_customer_owned_ip: BooleanOptional = None,
        aws_backup_recovery_point_arn: AwsBackupRecoveryPointArn = None,
        automation_mode: AutomationMode = None,
        resume_full_automation_mode_minutes: IntegerOptional = None,
        network_type: String = None,
    ) -> ModifyDBInstanceResult:
        """Modifies settings for a DB instance. You can change one or more database
        configuration parameters by specifying these parameters and the new
        values in the request. To learn what modifications you can make to your
        DB instance, call ``DescribeValidDBInstanceModifications`` before you
        call ``ModifyDBInstance``.

        :param db_instance_identifier: The DB instance identifier.
        :param allocated_storage: The new amount of storage in gibibytes (GiB) to allocate for the DB
        instance.
        :param db_instance_class: The new compute and memory capacity of the DB instance, for example
        db.
        :param db_subnet_group_name: The new DB subnet group for the DB instance.
        :param db_security_groups: A list of DB security groups to authorize on this DB instance.
        :param vpc_security_group_ids: A list of Amazon EC2 VPC security groups to authorize on this DB
        instance.
        :param apply_immediately: A value that indicates whether the modifications in this request and any
        pending modifications are asynchronously applied as soon as possible,
        regardless of the ``PreferredMaintenanceWindow`` setting for the DB
        instance.
        :param master_user_password: The new password for the master user.
        :param db_parameter_group_name: The name of the DB parameter group to apply to the DB instance.
        :param backup_retention_period: The number of days to retain automated backups.
        :param preferred_backup_window: The daily time range during which automated backups are created if
        automated backups are enabled, as determined by the
        ``BackupRetentionPeriod`` parameter.
        :param preferred_maintenance_window: The weekly time range (in UTC) during which system maintenance can
        occur, which might result in an outage.
        :param multi_az: A value that indicates whether the DB instance is a Multi-AZ deployment.
        :param engine_version: The version number of the database engine to upgrade to.
        :param allow_major_version_upgrade: A value that indicates whether major version upgrades are allowed.
        :param auto_minor_version_upgrade: A value that indicates whether minor version upgrades are applied
        automatically to the DB instance during the maintenance window.
        :param license_model: The license model for the DB instance.
        :param iops: The new Provisioned IOPS (I/O operations per second) value for the RDS
        instance.
        :param option_group_name: A value that indicates the DB instance should be associated with the
        specified option group.
        :param new_db_instance_identifier: The new DB instance identifier for the DB instance when renaming a DB
        instance.
        :param storage_type: Specifies the storage type to be associated with the DB instance.
        :param tde_credential_arn: The ARN from the key store with which to associate the instance for TDE
        encryption.
        :param tde_credential_password: The password for the given ARN from the key store in order to access the
        device.
        :param ca_certificate_identifier: Specifies the certificate to associate with the DB instance.
        :param domain: The Active Directory directory ID to move the DB instance to.
        :param copy_tags_to_snapshot: A value that indicates whether to copy all tags from the DB instance to
        snapshots of the DB instance.
        :param monitoring_interval: The interval, in seconds, between points when Enhanced Monitoring
        metrics are collected for the DB instance.
        :param db_port_number: The port number on which the database accepts connections.
        :param publicly_accessible: A value that indicates whether the DB instance is publicly accessible.
        :param monitoring_role_arn: The ARN for the IAM role that permits RDS to send enhanced monitoring
        metrics to Amazon CloudWatch Logs.
        :param domain_iam_role_name: The name of the IAM role to use when making API calls to the Directory
        Service.
        :param promotion_tier: A value that specifies the order in which an Aurora Replica is promoted
        to the primary instance after a failure of the existing primary
        instance.
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param enable_performance_insights: A value that indicates whether to enable Performance Insights for the DB
        instance.
        :param performance_insights_kms_key_id: The Amazon Web Services KMS key identifier for encryption of Performance
        Insights data.
        :param performance_insights_retention_period: The amount of time, in days, to retain Performance Insights data.
        :param cloudwatch_logs_export_configuration: The configuration setting for the log types to be enabled for export to
        CloudWatch Logs for a specific DB instance.
        :param processor_features: The number of CPU cores and the number of threads per core for the DB
        instance class of the DB instance.
        :param use_default_processor_features: A value that indicates whether the DB instance class of the DB instance
        uses its default processor features.
        :param deletion_protection: A value that indicates whether the DB instance has deletion protection
        enabled.
        :param max_allocated_storage: The upper limit in gibibytes (GiB) to which Amazon RDS can automatically
        scale the storage of the DB instance.
        :param certificate_rotation_restart: A value that indicates whether the DB instance is restarted when you
        rotate your SSL/TLS certificate.
        :param replica_mode: A value that sets the open mode of a replica database to either mounted
        or read-only.
        :param enable_customer_owned_ip: A value that indicates whether to enable a customer-owned IP address
        (CoIP) for an RDS on Outposts DB instance.
        :param aws_backup_recovery_point_arn: The Amazon Resource Name (ARN) of the recovery point in Amazon Web
        Services Backup.
        :param automation_mode: The automation mode of the RDS Custom DB instance: ``full`` or
        ``all paused``.
        :param resume_full_automation_mode_minutes: The number of minutes to pause the automation.
        :param network_type: The network type of the DB instance.
        :returns: ModifyDBInstanceResult
        :raises InvalidDBInstanceStateFault:
        :raises InvalidDBSecurityGroupStateFault:
        :raises DBInstanceAlreadyExistsFault:
        :raises DBInstanceNotFoundFault:
        :raises DBSecurityGroupNotFoundFault:
        :raises DBParameterGroupNotFoundFault:
        :raises InsufficientDBInstanceCapacityFault:
        :raises StorageQuotaExceededFault:
        :raises InvalidVPCNetworkStateFault:
        :raises ProvisionedIopsNotAvailableInAZFault:
        :raises OptionGroupNotFoundFault:
        :raises DBUpgradeDependencyFailureFault:
        :raises StorageTypeNotSupportedFault:
        :raises AuthorizationNotFoundFault:
        :raises CertificateNotFoundFault:
        :raises DomainNotFoundFault:
        :raises BackupPolicyNotFoundFault:
        :raises KMSKeyNotAccessibleFault:
        :raises InvalidDBClusterStateFault:
        :raises NetworkTypeNotSupported:
        """
        raise NotImplementedError

    @handler("ModifyDBParameterGroup")
    def modify_db_parameter_group(
        self, context: RequestContext, db_parameter_group_name: String, parameters: ParametersList
    ) -> DBParameterGroupNameMessage:
        """Modifies the parameters of a DB parameter group. To modify more than one
        parameter, submit a list of the following: ``ParameterName``,
        ``ParameterValue``, and ``ApplyMethod``. A maximum of 20 parameters can
        be modified in a single request.

        After you modify a DB parameter group, you should wait at least 5
        minutes before creating your first DB instance that uses that DB
        parameter group as the default parameter group. This allows Amazon RDS
        to fully complete the modify action before the parameter group is used
        as the default for a new DB instance. This is especially important for
        parameters that are critical when creating the default database for a DB
        instance, such as the character set for the default database defined by
        the ``character_set_database`` parameter. You can use the *Parameter
        Groups* option of the `Amazon RDS
        console <https://console.aws.amazon.com/rds/>`__ or the
        *DescribeDBParameters* command to verify that your DB parameter group
        has been created or modified.

        :param db_parameter_group_name: The name of the DB parameter group.
        :param parameters: An array of parameter names, values, and the application methods for the
        parameter update.
        :returns: DBParameterGroupNameMessage
        :raises DBParameterGroupNotFoundFault:
        :raises InvalidDBParameterGroupStateFault:
        """
        raise NotImplementedError

    @handler("ModifyDBProxy")
    def modify_db_proxy(
        self,
        context: RequestContext,
        db_proxy_name: String,
        new_db_proxy_name: String = None,
        auth: UserAuthConfigList = None,
        require_tls: BooleanOptional = None,
        idle_client_timeout: IntegerOptional = None,
        debug_logging: BooleanOptional = None,
        role_arn: String = None,
        security_groups: StringList = None,
    ) -> ModifyDBProxyResponse:
        """Changes the settings for an existing DB proxy.

        :param db_proxy_name: The identifier for the ``DBProxy`` to modify.
        :param new_db_proxy_name: The new identifier for the ``DBProxy``.
        :param auth: The new authentication settings for the ``DBProxy``.
        :param require_tls: Whether Transport Layer Security (TLS) encryption is required for
        connections to the proxy.
        :param idle_client_timeout: The number of seconds that a connection to the proxy can be inactive
        before the proxy disconnects it.
        :param debug_logging: Whether the proxy includes detailed information about SQL statements in
        its logs.
        :param role_arn: The Amazon Resource Name (ARN) of the IAM role that the proxy uses to
        access secrets in Amazon Web Services Secrets Manager.
        :param security_groups: The new list of security groups for the ``DBProxy``.
        :returns: ModifyDBProxyResponse
        :raises DBProxyNotFoundFault:
        :raises DBProxyAlreadyExistsFault:
        :raises InvalidDBProxyStateFault:
        """
        raise NotImplementedError

    @handler("ModifyDBProxyEndpoint")
    def modify_db_proxy_endpoint(
        self,
        context: RequestContext,
        db_proxy_endpoint_name: DBProxyEndpointName,
        new_db_proxy_endpoint_name: DBProxyEndpointName = None,
        vpc_security_group_ids: StringList = None,
    ) -> ModifyDBProxyEndpointResponse:
        """Changes the settings for an existing DB proxy endpoint.

        :param db_proxy_endpoint_name: The name of the DB proxy sociated with the DB proxy endpoint that you
        want to modify.
        :param new_db_proxy_endpoint_name: The new identifier for the ``DBProxyEndpoint``.
        :param vpc_security_group_ids: The VPC security group IDs for the DB proxy endpoint.
        :returns: ModifyDBProxyEndpointResponse
        :raises DBProxyEndpointNotFoundFault:
        :raises DBProxyEndpointAlreadyExistsFault:
        :raises InvalidDBProxyEndpointStateFault:
        :raises InvalidDBProxyStateFault:
        """
        raise NotImplementedError

    @handler("ModifyDBProxyTargetGroup")
    def modify_db_proxy_target_group(
        self,
        context: RequestContext,
        target_group_name: String,
        db_proxy_name: String,
        connection_pool_config: ConnectionPoolConfiguration = None,
        new_name: String = None,
    ) -> ModifyDBProxyTargetGroupResponse:
        """Modifies the properties of a ``DBProxyTargetGroup``.

        :param target_group_name: The name of the new target group to assign to the proxy.
        :param db_proxy_name: The name of the new proxy to which to assign the target group.
        :param connection_pool_config: The settings that determine the size and behavior of the connection pool
        for the target group.
        :param new_name: The new name for the modified ``DBProxyTarget``.
        :returns: ModifyDBProxyTargetGroupResponse
        :raises DBProxyNotFoundFault:
        :raises DBProxyTargetGroupNotFoundFault:
        :raises InvalidDBProxyStateFault:
        """
        raise NotImplementedError

    @handler("ModifyDBSnapshot")
    def modify_db_snapshot(
        self,
        context: RequestContext,
        db_snapshot_identifier: String,
        engine_version: String = None,
        option_group_name: String = None,
    ) -> ModifyDBSnapshotResult:
        """Updates a manual DB snapshot with a new engine version. The snapshot can
        be encrypted or unencrypted, but not shared or public.

        Amazon RDS supports upgrading DB snapshots for MySQL, PostgreSQL, and
        Oracle. This command doesn't apply to RDS Custom.

        :param db_snapshot_identifier: The identifier of the DB snapshot to modify.
        :param engine_version: The engine version to upgrade the DB snapshot to.
        :param option_group_name: The option group to identify with the upgraded DB snapshot.
        :returns: ModifyDBSnapshotResult
        :raises DBSnapshotNotFoundFault:
        """
        raise NotImplementedError

    @handler("ModifyDBSnapshotAttribute")
    def modify_db_snapshot_attribute(
        self,
        context: RequestContext,
        db_snapshot_identifier: String,
        attribute_name: String,
        values_to_add: AttributeValueList = None,
        values_to_remove: AttributeValueList = None,
    ) -> ModifyDBSnapshotAttributeResult:
        """Adds an attribute and values to, or removes an attribute and values
        from, a manual DB snapshot.

        To share a manual DB snapshot with other Amazon Web Services accounts,
        specify ``restore`` as the ``AttributeName`` and use the ``ValuesToAdd``
        parameter to add a list of IDs of the Amazon Web Services accounts that
        are authorized to restore the manual DB snapshot. Uses the value ``all``
        to make the manual DB snapshot public, which means it can be copied or
        restored by all Amazon Web Services accounts.

        Don't add the ``all`` value for any manual DB snapshots that contain
        private information that you don't want available to all Amazon Web
        Services accounts.

        If the manual DB snapshot is encrypted, it can be shared, but only by
        specifying a list of authorized Amazon Web Services account IDs for the
        ``ValuesToAdd`` parameter. You can't use ``all`` as a value for that
        parameter in this case.

        To view which Amazon Web Services accounts have access to copy or
        restore a manual DB snapshot, or whether a manual DB snapshot public or
        private, use the DescribeDBSnapshotAttributes API action. The accounts
        are returned as values for the ``restore`` attribute.

        :param db_snapshot_identifier: The identifier for the DB snapshot to modify the attributes for.
        :param attribute_name: The name of the DB snapshot attribute to modify.
        :param values_to_add: A list of DB snapshot attributes to add to the attribute specified by
        ``AttributeName``.
        :param values_to_remove: A list of DB snapshot attributes to remove from the attribute specified
        by ``AttributeName``.
        :returns: ModifyDBSnapshotAttributeResult
        :raises DBSnapshotNotFoundFault:
        :raises InvalidDBSnapshotStateFault:
        :raises SharedSnapshotQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("ModifyDBSubnetGroup")
    def modify_db_subnet_group(
        self,
        context: RequestContext,
        db_subnet_group_name: String,
        subnet_ids: SubnetIdentifierList,
        db_subnet_group_description: String = None,
    ) -> ModifyDBSubnetGroupResult:
        """Modifies an existing DB subnet group. DB subnet groups must contain at
        least one subnet in at least two AZs in the Amazon Web Services Region.

        :param db_subnet_group_name: The name for the DB subnet group.
        :param subnet_ids: The EC2 subnet IDs for the DB subnet group.
        :param db_subnet_group_description: The description for the DB subnet group.
        :returns: ModifyDBSubnetGroupResult
        :raises DBSubnetGroupNotFoundFault:
        :raises DBSubnetQuotaExceededFault:
        :raises SubnetAlreadyInUse:
        :raises DBSubnetGroupDoesNotCoverEnoughAZs:
        :raises InvalidSubnet:
        """
        raise NotImplementedError

    @handler("ModifyEventSubscription")
    def modify_event_subscription(
        self,
        context: RequestContext,
        subscription_name: String,
        sns_topic_arn: String = None,
        source_type: String = None,
        event_categories: EventCategoriesList = None,
        enabled: BooleanOptional = None,
    ) -> ModifyEventSubscriptionResult:
        """Modifies an existing RDS event notification subscription. You can't
        modify the source identifiers using this call. To change source
        identifiers for a subscription, use the
        ``AddSourceIdentifierToSubscription`` and
        ``RemoveSourceIdentifierFromSubscription`` calls.

        You can see a list of the event categories for a given source type
        (``SourceType``) in
        `Events <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Events.html>`__
        in the *Amazon RDS User Guide* or by using the
        ``DescribeEventCategories`` operation.

        :param subscription_name: The name of the RDS event notification subscription.
        :param sns_topic_arn: The Amazon Resource Name (ARN) of the SNS topic created for event
        notification.
        :param source_type: The type of source that is generating the events.
        :param event_categories: A list of event categories for a source type (``SourceType``) that you
        want to subscribe to.
        :param enabled: A value that indicates whether to activate the subscription.
        :returns: ModifyEventSubscriptionResult
        :raises EventSubscriptionQuotaExceededFault:
        :raises SubscriptionNotFoundFault:
        :raises SNSInvalidTopicFault:
        :raises SNSNoAuthorizationFault:
        :raises SNSTopicArnNotFoundFault:
        :raises SubscriptionCategoryNotFoundFault:
        """
        raise NotImplementedError

    @handler("ModifyGlobalCluster")
    def modify_global_cluster(
        self,
        context: RequestContext,
        global_cluster_identifier: String = None,
        new_global_cluster_identifier: String = None,
        deletion_protection: BooleanOptional = None,
        engine_version: String = None,
        allow_major_version_upgrade: BooleanOptional = None,
    ) -> ModifyGlobalClusterResult:
        """Modify a setting for an Amazon Aurora global cluster. You can change one
        or more database configuration parameters by specifying these parameters
        and the new values in the request. For more information on Amazon
        Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        This action only applies to Aurora DB clusters.

        :param global_cluster_identifier: The DB cluster identifier for the global cluster being modified.
        :param new_global_cluster_identifier: The new cluster identifier for the global database cluster when
        modifying a global database cluster.
        :param deletion_protection: Indicates if the global database cluster has deletion protection
        enabled.
        :param engine_version: The version number of the database engine to which you want to upgrade.
        :param allow_major_version_upgrade: A value that indicates whether major version upgrades are allowed.
        :returns: ModifyGlobalClusterResult
        :raises GlobalClusterNotFoundFault:
        :raises InvalidGlobalClusterStateFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError

    @handler("ModifyOptionGroup")
    def modify_option_group(
        self,
        context: RequestContext,
        option_group_name: String,
        options_to_include: OptionConfigurationList = None,
        options_to_remove: OptionNamesList = None,
        apply_immediately: Boolean = None,
    ) -> ModifyOptionGroupResult:
        """Modifies an existing option group.

        :param option_group_name: The name of the option group to be modified.
        :param options_to_include: Options in this list are added to the option group or, if already
        present, the specified configuration is used to update the existing
        configuration.
        :param options_to_remove: Options in this list are removed from the option group.
        :param apply_immediately: A value that indicates whether to apply the change immediately or during
        the next maintenance window for each instance associated with the option
        group.
        :returns: ModifyOptionGroupResult
        :raises InvalidOptionGroupStateFault:
        :raises OptionGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("PromoteReadReplica")
    def promote_read_replica(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        backup_retention_period: IntegerOptional = None,
        preferred_backup_window: String = None,
    ) -> PromoteReadReplicaResult:
        """Promotes a read replica DB instance to a standalone DB instance.

        -  Backup duration is a function of the amount of changes to the
           database since the previous backup. If you plan to promote a read
           replica to a standalone instance, we recommend that you enable
           backups and complete at least one backup prior to promotion. In
           addition, a read replica cannot be promoted to a standalone instance
           when it is in the ``backing-up`` status. If you have enabled backups
           on your read replica, configure the automated backup window so that
           daily backups do not interfere with read replica promotion.

        -  This command doesn't apply to Aurora MySQL, Aurora PostgreSQL, or RDS
           Custom.

        :param db_instance_identifier: The DB instance identifier.
        :param backup_retention_period: The number of days for which automated backups are retained.
        :param preferred_backup_window: The daily time range during which automated backups are created if
        automated backups are enabled, using the ``BackupRetentionPeriod``
        parameter.
        :returns: PromoteReadReplicaResult
        :raises InvalidDBInstanceStateFault:
        :raises DBInstanceNotFoundFault:
        """
        raise NotImplementedError

    @handler("PromoteReadReplicaDBCluster")
    def promote_read_replica_db_cluster(
        self, context: RequestContext, db_cluster_identifier: String
    ) -> PromoteReadReplicaDBClusterResult:
        """Promotes a read replica DB cluster to a standalone DB cluster.

        :param db_cluster_identifier: The identifier of the DB cluster read replica to promote.
        :returns: PromoteReadReplicaDBClusterResult
        :raises DBClusterNotFoundFault:
        :raises InvalidDBClusterStateFault:
        """
        raise NotImplementedError

    @handler("PurchaseReservedDBInstancesOffering")
    def purchase_reserved_db_instances_offering(
        self,
        context: RequestContext,
        reserved_db_instances_offering_id: String,
        reserved_db_instance_id: String = None,
        db_instance_count: IntegerOptional = None,
        tags: TagList = None,
    ) -> PurchaseReservedDBInstancesOfferingResult:
        """Purchases a reserved DB instance offering.

        :param reserved_db_instances_offering_id: The ID of the Reserved DB instance offering to purchase.
        :param reserved_db_instance_id: Customer-specified identifier to track this reservation.
        :param db_instance_count: The number of instances to reserve.
        :param tags: A list of tags.
        :returns: PurchaseReservedDBInstancesOfferingResult
        :raises ReservedDBInstancesOfferingNotFoundFault:
        :raises ReservedDBInstanceAlreadyExistsFault:
        :raises ReservedDBInstanceQuotaExceededFault:
        """
        raise NotImplementedError

    @handler("RebootDBCluster")
    def reboot_db_cluster(
        self, context: RequestContext, db_cluster_identifier: String
    ) -> RebootDBClusterResult:
        """You might need to reboot your DB cluster, usually for maintenance
        reasons. For example, if you make certain modifications, or if you
        change the DB cluster parameter group associated with the DB cluster,
        reboot the DB cluster for the changes to take effect.

        Rebooting a DB cluster restarts the database engine service. Rebooting a
        DB cluster results in a momentary outage, during which the DB cluster
        status is set to rebooting.

        Use this operation only for a non-Aurora Multi-AZ DB cluster.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide.*

        :param db_cluster_identifier: The DB cluster identifier.
        :returns: RebootDBClusterResult
        :raises DBClusterNotFoundFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError

    @handler("RebootDBInstance")
    def reboot_db_instance(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        force_failover: BooleanOptional = None,
    ) -> RebootDBInstanceResult:
        """You might need to reboot your DB instance, usually for maintenance
        reasons. For example, if you make certain modifications, or if you
        change the DB parameter group associated with the DB instance, you must
        reboot the instance for the changes to take effect.

        Rebooting a DB instance restarts the database engine service. Rebooting
        a DB instance results in a momentary outage, during which the DB
        instance status is set to rebooting.

        For more information about rebooting, see `Rebooting a DB
        Instance <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_RebootInstance.html>`__
        in the *Amazon RDS User Guide.*

        This command doesn't apply to RDS Custom.

        :param db_instance_identifier: The DB instance identifier.
        :param force_failover: A value that indicates whether the reboot is conducted through a
        Multi-AZ failover.
        :returns: RebootDBInstanceResult
        :raises InvalidDBInstanceStateFault:
        :raises DBInstanceNotFoundFault:
        """
        raise NotImplementedError

    @handler("RegisterDBProxyTargets")
    def register_db_proxy_targets(
        self,
        context: RequestContext,
        db_proxy_name: String,
        target_group_name: String = None,
        db_instance_identifiers: StringList = None,
        db_cluster_identifiers: StringList = None,
    ) -> RegisterDBProxyTargetsResponse:
        """Associate one or more ``DBProxyTarget`` data structures with a
        ``DBProxyTargetGroup``.

        :param db_proxy_name: The identifier of the ``DBProxy`` that is associated with the
        ``DBProxyTargetGroup``.
        :param target_group_name: The identifier of the ``DBProxyTargetGroup``.
        :param db_instance_identifiers: One or more DB instance identifiers.
        :param db_cluster_identifiers: One or more DB cluster identifiers.
        :returns: RegisterDBProxyTargetsResponse
        :raises DBProxyNotFoundFault:
        :raises DBProxyTargetGroupNotFoundFault:
        :raises DBClusterNotFoundFault:
        :raises DBInstanceNotFoundFault:
        :raises DBProxyTargetAlreadyRegisteredFault:
        :raises InvalidDBInstanceStateFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBProxyStateFault:
        :raises InsufficientAvailableIPsInSubnetFault:
        """
        raise NotImplementedError

    @handler("RemoveFromGlobalCluster")
    def remove_from_global_cluster(
        self,
        context: RequestContext,
        global_cluster_identifier: String = None,
        db_cluster_identifier: String = None,
    ) -> RemoveFromGlobalClusterResult:
        """Detaches an Aurora secondary cluster from an Aurora global database
        cluster. The cluster becomes a standalone cluster with read-write
        capability instead of being read-only and receiving data from a primary
        cluster in a different Region.

        This action only applies to Aurora DB clusters.

        :param global_cluster_identifier: The cluster identifier to detach from the Aurora global database
        cluster.
        :param db_cluster_identifier: The Amazon Resource Name (ARN) identifying the cluster that was detached
        from the Aurora global database cluster.
        :returns: RemoveFromGlobalClusterResult
        :raises GlobalClusterNotFoundFault:
        :raises InvalidGlobalClusterStateFault:
        :raises DBClusterNotFoundFault:
        """
        raise NotImplementedError

    @handler("RemoveRoleFromDBCluster")
    def remove_role_from_db_cluster(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        role_arn: String,
        feature_name: String = None,
    ) -> None:
        """Removes the asssociation of an Amazon Web Services Identity and Access
        Management (IAM) role from a DB cluster.

        For more information on Amazon Aurora DB clusters, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide.*

        :param db_cluster_identifier: The name of the DB cluster to disassociate the IAM role from.
        :param role_arn: The Amazon Resource Name (ARN) of the IAM role to disassociate from the
        Aurora DB cluster, for example
        ``arn:aws:iam::123456789012:role/AuroraAccessRole``.
        :param feature_name: The name of the feature for the DB cluster that the IAM role is to be
        disassociated from.
        :raises DBClusterNotFoundFault:
        :raises DBClusterRoleNotFoundFault:
        :raises InvalidDBClusterStateFault:
        """
        raise NotImplementedError

    @handler("RemoveRoleFromDBInstance")
    def remove_role_from_db_instance(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        role_arn: String,
        feature_name: String,
    ) -> None:
        """Disassociates an Amazon Web Services Identity and Access Management
        (IAM) role from a DB instance.

        :param db_instance_identifier: The name of the DB instance to disassociate the IAM role from.
        :param role_arn: The Amazon Resource Name (ARN) of the IAM role to disassociate from the
        DB instance, for example, ``arn:aws:iam::123456789012:role/AccessRole``.
        :param feature_name: The name of the feature for the DB instance that the IAM role is to be
        disassociated from.
        :raises DBInstanceNotFoundFault:
        :raises DBInstanceRoleNotFoundFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError

    @handler("RemoveSourceIdentifierFromSubscription")
    def remove_source_identifier_from_subscription(
        self, context: RequestContext, subscription_name: String, source_identifier: String
    ) -> RemoveSourceIdentifierFromSubscriptionResult:
        """Removes a source identifier from an existing RDS event notification
        subscription.

        :param subscription_name: The name of the RDS event notification subscription you want to remove a
        source identifier from.
        :param source_identifier: The source identifier to be removed from the subscription, such as the
        **DB instance identifier** for a DB instance or the name of a security
        group.
        :returns: RemoveSourceIdentifierFromSubscriptionResult
        :raises SubscriptionNotFoundFault:
        :raises SourceNotFoundFault:
        """
        raise NotImplementedError

    @handler("RemoveTagsFromResource")
    def remove_tags_from_resource(
        self, context: RequestContext, resource_name: String, tag_keys: KeyList
    ) -> None:
        """Removes metadata tags from an Amazon RDS resource.

        For an overview on tagging an Amazon RDS resource, see `Tagging Amazon
        RDS
        Resources <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Tagging.html>`__
        in the *Amazon RDS User Guide.*

        :param resource_name: The Amazon RDS resource that the tags are removed from.
        :param tag_keys: The tag key (name) of the tag to be removed.
        :raises DBInstanceNotFoundFault:
        :raises DBSnapshotNotFoundFault:
        :raises DBClusterNotFoundFault:
        :raises DBProxyNotFoundFault:
        :raises DBProxyTargetGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("ResetDBClusterParameterGroup")
    def reset_db_cluster_parameter_group(
        self,
        context: RequestContext,
        db_cluster_parameter_group_name: String,
        reset_all_parameters: Boolean = None,
        parameters: ParametersList = None,
    ) -> DBClusterParameterGroupNameMessage:
        """Modifies the parameters of a DB cluster parameter group to the default
        value. To reset specific parameters submit a list of the following:
        ``ParameterName`` and ``ApplyMethod``. To reset the entire DB cluster
        parameter group, specify the ``DBClusterParameterGroupName`` and
        ``ResetAllParameters`` parameters.

        When resetting the entire group, dynamic parameters are updated
        immediately and static parameters are set to ``pending-reboot`` to take
        effect on the next DB instance restart or ``RebootDBInstance`` request.
        You must call ``RebootDBInstance`` for every DB instance in your DB
        cluster that you want the updated static parameter to apply to.

        For more information on Amazon Aurora DB clusters, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide.*

        :param db_cluster_parameter_group_name: The name of the DB cluster parameter group to reset.
        :param reset_all_parameters: A value that indicates whether to reset all parameters in the DB cluster
        parameter group to their default values.
        :param parameters: A list of parameter names in the DB cluster parameter group to reset to
        the default values.
        :returns: DBClusterParameterGroupNameMessage
        :raises InvalidDBParameterGroupStateFault:
        :raises DBParameterGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("ResetDBParameterGroup")
    def reset_db_parameter_group(
        self,
        context: RequestContext,
        db_parameter_group_name: String,
        reset_all_parameters: Boolean = None,
        parameters: ParametersList = None,
    ) -> DBParameterGroupNameMessage:
        """Modifies the parameters of a DB parameter group to the engine/system
        default value. To reset specific parameters, provide a list of the
        following: ``ParameterName`` and ``ApplyMethod``. To reset the entire DB
        parameter group, specify the ``DBParameterGroup`` name and
        ``ResetAllParameters`` parameters. When resetting the entire group,
        dynamic parameters are updated immediately and static parameters are set
        to ``pending-reboot`` to take effect on the next DB instance restart or
        ``RebootDBInstance`` request.

        :param db_parameter_group_name: The name of the DB parameter group.
        :param reset_all_parameters: A value that indicates whether to reset all parameters in the DB
        parameter group to default values.
        :param parameters: To reset the entire DB parameter group, specify the ``DBParameterGroup``
        name and ``ResetAllParameters`` parameters.
        :returns: DBParameterGroupNameMessage
        :raises InvalidDBParameterGroupStateFault:
        :raises DBParameterGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("RestoreDBClusterFromS3")
    def restore_db_cluster_from_s3(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        engine: String,
        master_username: String,
        master_user_password: String,
        source_engine: String,
        source_engine_version: String,
        s3_bucket_name: String,
        s3_ingestion_role_arn: String,
        availability_zones: AvailabilityZones = None,
        backup_retention_period: IntegerOptional = None,
        character_set_name: String = None,
        database_name: String = None,
        db_cluster_parameter_group_name: String = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        db_subnet_group_name: String = None,
        engine_version: String = None,
        port: IntegerOptional = None,
        option_group_name: String = None,
        preferred_backup_window: String = None,
        preferred_maintenance_window: String = None,
        tags: TagList = None,
        storage_encrypted: BooleanOptional = None,
        kms_key_id: String = None,
        enable_iam_database_authentication: BooleanOptional = None,
        s3_prefix: String = None,
        backtrack_window: LongOptional = None,
        enable_cloudwatch_logs_exports: LogTypeList = None,
        deletion_protection: BooleanOptional = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        domain: String = None,
        domain_iam_role_name: String = None,
        serverless_v2_scaling_configuration: ServerlessV2ScalingConfiguration = None,
    ) -> RestoreDBClusterFromS3Result:
        """Creates an Amazon Aurora DB cluster from MySQL data stored in an Amazon
        S3 bucket. Amazon RDS must be authorized to access the Amazon S3 bucket
        and the data must be created using the Percona XtraBackup utility as
        described in `Migrating Data from MySQL by Using an Amazon S3
        Bucket <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Migrating.ExtMySQL.html#AuroraMySQL.Migrating.ExtMySQL.S3>`__
        in the *Amazon Aurora User Guide*.

        This action only restores the DB cluster, not the DB instances for that
        DB cluster. You must invoke the ``CreateDBInstance`` action to create DB
        instances for the restored DB cluster, specifying the identifier of the
        restored DB cluster in ``DBClusterIdentifier``. You can create DB
        instances only after the ``RestoreDBClusterFromS3`` action has completed
        and the DB cluster is available.

        For more information on Amazon Aurora, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        This action only applies to Aurora DB clusters. The source DB engine
        must be MySQL.

        :param db_cluster_identifier: The name of the DB cluster to create from the source data in the Amazon
        S3 bucket.
        :param engine: The name of the database engine to be used for this DB cluster.
        :param master_username: The name of the master user for the restored DB cluster.
        :param master_user_password: The password for the master database user.
        :param source_engine: The identifier for the database engine that was backed up to create the
        files stored in the Amazon S3 bucket.
        :param source_engine_version: The version of the database that the backup files were created from.
        :param s3_bucket_name: The name of the Amazon S3 bucket that contains the data used to create
        the Amazon Aurora DB cluster.
        :param s3_ingestion_role_arn: The Amazon Resource Name (ARN) of the Amazon Web Services Identity and
        Access Management (IAM) role that authorizes Amazon RDS to access the
        Amazon S3 bucket on your behalf.
        :param availability_zones: A list of Availability Zones (AZs) where instances in the restored DB
        cluster can be created.
        :param backup_retention_period: The number of days for which automated backups of the restored DB
        cluster are retained.
        :param character_set_name: A value that indicates that the restored DB cluster should be associated
        with the specified CharacterSet.
        :param database_name: The database name for the restored DB cluster.
        :param db_cluster_parameter_group_name: The name of the DB cluster parameter group to associate with the
        restored DB cluster.
        :param vpc_security_group_ids: A list of EC2 VPC security groups to associate with the restored DB
        cluster.
        :param db_subnet_group_name: A DB subnet group to associate with the restored DB cluster.
        :param engine_version: The version number of the database engine to use.
        :param port: The port number on which the instances in the restored DB cluster accept
        connections.
        :param option_group_name: A value that indicates that the restored DB cluster should be associated
        with the specified option group.
        :param preferred_backup_window: The daily time range during which automated backups are created if
        automated backups are enabled using the ``BackupRetentionPeriod``
        parameter.
        :param preferred_maintenance_window: The weekly time range during which system maintenance can occur, in
        Universal Coordinated Time (UTC).
        :param tags: A list of tags.
        :param storage_encrypted: A value that indicates whether the restored DB cluster is encrypted.
        :param kms_key_id: The Amazon Web Services KMS key identifier for an encrypted DB cluster.
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param s3_prefix: The prefix for all of the file names that contain the data used to
        create the Amazon Aurora DB cluster.
        :param backtrack_window: The target backtrack window, in seconds.
        :param enable_cloudwatch_logs_exports: The list of logs that the restored DB cluster is to export to CloudWatch
        Logs.
        :param deletion_protection: A value that indicates whether the DB cluster has deletion protection
        enabled.
        :param copy_tags_to_snapshot: A value that indicates whether to copy all tags from the restored DB
        cluster to snapshots of the restored DB cluster.
        :param domain: Specify the Active Directory directory ID to restore the DB cluster in.
        :param domain_iam_role_name: Specify the name of the IAM role to be used when making API calls to the
        Directory Service.
        :param serverless_v2_scaling_configuration: Contains the scaling configuration of an Aurora Serverless v2 DB
        cluster.
        :returns: RestoreDBClusterFromS3Result
        :raises DBClusterAlreadyExistsFault:
        :raises DBClusterQuotaExceededFault:
        :raises StorageQuotaExceededFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBSubnetGroupStateFault:
        :raises InvalidSubnet:
        :raises InvalidS3BucketFault:
        :raises DBClusterParameterGroupNotFoundFault:
        :raises KMSKeyNotAccessibleFault:
        :raises DBClusterNotFoundFault:
        :raises DomainNotFoundFault:
        :raises InsufficientStorageClusterCapacityFault:
        """
        raise NotImplementedError

    @handler("RestoreDBClusterFromSnapshot")
    def restore_db_cluster_from_snapshot(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        snapshot_identifier: String,
        engine: String,
        availability_zones: AvailabilityZones = None,
        engine_version: String = None,
        port: IntegerOptional = None,
        db_subnet_group_name: String = None,
        database_name: String = None,
        option_group_name: String = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        tags: TagList = None,
        kms_key_id: String = None,
        enable_iam_database_authentication: BooleanOptional = None,
        backtrack_window: LongOptional = None,
        enable_cloudwatch_logs_exports: LogTypeList = None,
        engine_mode: String = None,
        scaling_configuration: ScalingConfiguration = None,
        db_cluster_parameter_group_name: String = None,
        deletion_protection: BooleanOptional = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        domain: String = None,
        domain_iam_role_name: String = None,
        db_cluster_instance_class: String = None,
        storage_type: String = None,
        iops: IntegerOptional = None,
        publicly_accessible: BooleanOptional = None,
        serverless_v2_scaling_configuration: ServerlessV2ScalingConfiguration = None,
    ) -> RestoreDBClusterFromSnapshotResult:
        """Creates a new DB cluster from a DB snapshot or DB cluster snapshot.

        The target DB cluster is created from the source snapshot with a default
        configuration. If you don't specify a security group, the new DB cluster
        is associated with the default security group.

        This action only restores the DB cluster, not the DB instances for that
        DB cluster. You must invoke the ``CreateDBInstance`` action to create DB
        instances for the restored DB cluster, specifying the identifier of the
        restored DB cluster in ``DBClusterIdentifier``. You can create DB
        instances only after the ``RestoreDBClusterFromSnapshot`` action has
        completed and the DB cluster is available.

        For more information on Amazon Aurora DB clusters, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide.*

        :param db_cluster_identifier: The name of the DB cluster to create from the DB snapshot or DB cluster
        snapshot.
        :param snapshot_identifier: The identifier for the DB snapshot or DB cluster snapshot to restore
        from.
        :param engine: The database engine to use for the new DB cluster.
        :param availability_zones: Provides the list of Availability Zones (AZs) where instances in the
        restored DB cluster can be created.
        :param engine_version: The version of the database engine to use for the new DB cluster.
        :param port: The port number on which the new DB cluster accepts connections.
        :param db_subnet_group_name: The name of the DB subnet group to use for the new DB cluster.
        :param database_name: The database name for the restored DB cluster.
        :param option_group_name: The name of the option group to use for the restored DB cluster.
        :param vpc_security_group_ids: A list of VPC security groups that the new DB cluster will belong to.
        :param tags: The tags to be assigned to the restored DB cluster.
        :param kms_key_id: The Amazon Web Services KMS key identifier to use when restoring an
        encrypted DB cluster from a DB snapshot or DB cluster snapshot.
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param backtrack_window: The target backtrack window, in seconds.
        :param enable_cloudwatch_logs_exports: The list of logs that the restored DB cluster is to export to Amazon
        CloudWatch Logs.
        :param engine_mode: The DB engine mode of the DB cluster, either ``provisioned``,
        ``serverless``, ``parallelquery``, ``global``, or ``multimaster``.
        :param scaling_configuration: For DB clusters in ``serverless`` DB engine mode, the scaling properties
        of the DB cluster.
        :param db_cluster_parameter_group_name: The name of the DB cluster parameter group to associate with this DB
        cluster.
        :param deletion_protection: A value that indicates whether the DB cluster has deletion protection
        enabled.
        :param copy_tags_to_snapshot: A value that indicates whether to copy all tags from the restored DB
        cluster to snapshots of the restored DB cluster.
        :param domain: Specify the Active Directory directory ID to restore the DB cluster in.
        :param domain_iam_role_name: Specify the name of the IAM role to be used when making API calls to the
        Directory Service.
        :param db_cluster_instance_class: The compute and memory capacity of the each DB instance in the Multi-AZ
        DB cluster, for example db.
        :param storage_type: Specifies the storage type to be associated with the each DB instance in
        the Multi-AZ DB cluster.
        :param iops: The amount of Provisioned IOPS (input/output operations per second) to
        be initially allocated for each DB instance in the Multi-AZ DB cluster.
        :param publicly_accessible: A value that indicates whether the DB cluster is publicly accessible.
        :param serverless_v2_scaling_configuration: Contains the scaling configuration of an Aurora Serverless v2 DB
        cluster.
        :returns: RestoreDBClusterFromSnapshotResult
        :raises DBClusterAlreadyExistsFault:
        :raises DBClusterQuotaExceededFault:
        :raises StorageQuotaExceededFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises DBSnapshotNotFoundFault:
        :raises DBClusterSnapshotNotFoundFault:
        :raises InsufficientDBClusterCapacityFault:
        :raises InsufficientStorageClusterCapacityFault:
        :raises InvalidDBSnapshotStateFault:
        :raises InvalidDBClusterSnapshotStateFault:
        :raises StorageQuotaExceededFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InvalidRestoreFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises InvalidSubnet:
        :raises OptionGroupNotFoundFault:
        :raises KMSKeyNotAccessibleFault:
        :raises DomainNotFoundFault:
        :raises DBClusterParameterGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("RestoreDBClusterToPointInTime")
    def restore_db_cluster_to_point_in_time(
        self,
        context: RequestContext,
        db_cluster_identifier: String,
        source_db_cluster_identifier: String,
        restore_type: String = None,
        restore_to_time: TStamp = None,
        use_latest_restorable_time: Boolean = None,
        port: IntegerOptional = None,
        db_subnet_group_name: String = None,
        option_group_name: String = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        tags: TagList = None,
        kms_key_id: String = None,
        enable_iam_database_authentication: BooleanOptional = None,
        backtrack_window: LongOptional = None,
        enable_cloudwatch_logs_exports: LogTypeList = None,
        db_cluster_parameter_group_name: String = None,
        deletion_protection: BooleanOptional = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        domain: String = None,
        domain_iam_role_name: String = None,
        scaling_configuration: ScalingConfiguration = None,
        engine_mode: String = None,
        db_cluster_instance_class: String = None,
        storage_type: String = None,
        publicly_accessible: BooleanOptional = None,
        iops: IntegerOptional = None,
        serverless_v2_scaling_configuration: ServerlessV2ScalingConfiguration = None,
    ) -> RestoreDBClusterToPointInTimeResult:
        """Restores a DB cluster to an arbitrary point in time. Users can restore
        to any point in time before ``LatestRestorableTime`` for up to
        ``BackupRetentionPeriod`` days. The target DB cluster is created from
        the source DB cluster with the same configuration as the original DB
        cluster, except that the new DB cluster is created with the default DB
        security group.

        For Aurora, this action only restores the DB cluster, not the DB
        instances for that DB cluster. You must invoke the ``CreateDBInstance``
        action to create DB instances for the restored DB cluster, specifying
        the identifier of the restored DB cluster in ``DBClusterIdentifier``.
        You can create DB instances only after the
        ``RestoreDBClusterToPointInTime`` action has completed and the DB
        cluster is available.

        For more information on Amazon Aurora DB clusters, see `What is Amazon
        Aurora? <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html>`__
        in the *Amazon Aurora User Guide*.

        For more information on Multi-AZ DB clusters, see `Multi-AZ deployments
        with two readable standby DB
        instances <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html>`__
        in the *Amazon RDS User Guide.*

        :param db_cluster_identifier: The name of the new DB cluster to be created.
        :param source_db_cluster_identifier: The identifier of the source DB cluster from which to restore.
        :param restore_type: The type of restore to be performed.
        :param restore_to_time: The date and time to restore the DB cluster to.
        :param use_latest_restorable_time: A value that indicates whether to restore the DB cluster to the latest
        restorable backup time.
        :param port: The port number on which the new DB cluster accepts connections.
        :param db_subnet_group_name: The DB subnet group name to use for the new DB cluster.
        :param option_group_name: The name of the option group for the new DB cluster.
        :param vpc_security_group_ids: A list of VPC security groups that the new DB cluster belongs to.
        :param tags: A list of tags.
        :param kms_key_id: The Amazon Web Services KMS key identifier to use when restoring an
        encrypted DB cluster from an encrypted DB cluster.
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param backtrack_window: The target backtrack window, in seconds.
        :param enable_cloudwatch_logs_exports: The list of logs that the restored DB cluster is to export to CloudWatch
        Logs.
        :param db_cluster_parameter_group_name: The name of the DB cluster parameter group to associate with this DB
        cluster.
        :param deletion_protection: A value that indicates whether the DB cluster has deletion protection
        enabled.
        :param copy_tags_to_snapshot: A value that indicates whether to copy all tags from the restored DB
        cluster to snapshots of the restored DB cluster.
        :param domain: Specify the Active Directory directory ID to restore the DB cluster in.
        :param domain_iam_role_name: Specify the name of the IAM role to be used when making API calls to the
        Directory Service.
        :param scaling_configuration: For DB clusters in ``serverless`` DB engine mode, the scaling properties
        of the DB cluster.
        :param engine_mode: The engine mode of the new cluster.
        :param db_cluster_instance_class: The compute and memory capacity of the each DB instance in the Multi-AZ
        DB cluster, for example db.
        :param storage_type: Specifies the storage type to be associated with the each DB instance in
        the Multi-AZ DB cluster.
        :param publicly_accessible: A value that indicates whether the DB cluster is publicly accessible.
        :param iops: The amount of Provisioned IOPS (input/output operations per second) to
        be initially allocated for each DB instance in the Multi-AZ DB cluster.
        :param serverless_v2_scaling_configuration: Contains the scaling configuration of an Aurora Serverless v2 DB
        cluster.
        :returns: RestoreDBClusterToPointInTimeResult
        :raises DBClusterAlreadyExistsFault:
        :raises DBClusterNotFoundFault:
        :raises DBClusterQuotaExceededFault:
        :raises DBClusterSnapshotNotFoundFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises InsufficientDBClusterCapacityFault:
        :raises InsufficientStorageClusterCapacityFault:
        :raises InvalidDBClusterSnapshotStateFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBSnapshotStateFault:
        :raises InvalidRestoreFault:
        :raises InvalidSubnet:
        :raises InvalidVPCNetworkStateFault:
        :raises KMSKeyNotAccessibleFault:
        :raises OptionGroupNotFoundFault:
        :raises StorageQuotaExceededFault:
        :raises DomainNotFoundFault:
        :raises DBClusterParameterGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("RestoreDBInstanceFromDBSnapshot")
    def restore_db_instance_from_db_snapshot(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        db_snapshot_identifier: String,
        db_instance_class: String = None,
        port: IntegerOptional = None,
        availability_zone: String = None,
        db_subnet_group_name: String = None,
        multi_az: BooleanOptional = None,
        publicly_accessible: BooleanOptional = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        license_model: String = None,
        db_name: String = None,
        engine: String = None,
        iops: IntegerOptional = None,
        option_group_name: String = None,
        tags: TagList = None,
        storage_type: String = None,
        tde_credential_arn: String = None,
        tde_credential_password: String = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        domain: String = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        domain_iam_role_name: String = None,
        enable_iam_database_authentication: BooleanOptional = None,
        enable_cloudwatch_logs_exports: LogTypeList = None,
        processor_features: ProcessorFeatureList = None,
        use_default_processor_features: BooleanOptional = None,
        db_parameter_group_name: String = None,
        deletion_protection: BooleanOptional = None,
        enable_customer_owned_ip: BooleanOptional = None,
        custom_iam_instance_profile: String = None,
        backup_target: String = None,
        network_type: String = None,
    ) -> RestoreDBInstanceFromDBSnapshotResult:
        """Creates a new DB instance from a DB snapshot. The target database is
        created from the source database restore point with most of the source's
        original configuration, including the default security group and DB
        parameter group. By default, the new DB instance is created as a
        Single-AZ deployment, except when the instance is a SQL Server instance
        that has an option group associated with mirroring. In this case, the
        instance becomes a Multi-AZ deployment, not a Single-AZ deployment.

        If you want to replace your original DB instance with the new, restored
        DB instance, then rename your original DB instance before you call the
        RestoreDBInstanceFromDBSnapshot action. RDS doesn't allow two DB
        instances with the same name. After you have renamed your original DB
        instance with a different identifier, then you can pass the original
        name of the DB instance as the DBInstanceIdentifier in the call to the
        RestoreDBInstanceFromDBSnapshot action. The result is that you replace
        the original DB instance with the DB instance created from the snapshot.

        If you are restoring from a shared manual DB snapshot, the
        ``DBSnapshotIdentifier`` must be the ARN of the shared DB snapshot.

        This command doesn't apply to Aurora MySQL and Aurora PostgreSQL. For
        Aurora, use ``RestoreDBClusterFromSnapshot``.

        :param db_instance_identifier: Name of the DB instance to create from the DB snapshot.
        :param db_snapshot_identifier: The identifier for the DB snapshot to restore from.
        :param db_instance_class: The compute and memory capacity of the Amazon RDS DB instance, for
        example db.
        :param port: The port number on which the database accepts connections.
        :param availability_zone: The Availability Zone (AZ) where the DB instance will be created.
        :param db_subnet_group_name: The DB subnet group name to use for the new instance.
        :param multi_az: A value that indicates whether the DB instance is a Multi-AZ deployment.
        :param publicly_accessible: A value that indicates whether the DB instance is publicly accessible.
        :param auto_minor_version_upgrade: A value that indicates whether minor version upgrades are applied
        automatically to the DB instance during the maintenance window.
        :param license_model: License model information for the restored DB instance.
        :param db_name: The database name for the restored DB instance.
        :param engine: The database engine to use for the new instance.
        :param iops: Specifies the amount of provisioned IOPS for the DB instance, expressed
        in I/O operations per second.
        :param option_group_name: The name of the option group to be used for the restored DB instance.
        :param tags: A list of tags.
        :param storage_type: Specifies the storage type to be associated with the DB instance.
        :param tde_credential_arn: The ARN from the key store with which to associate the instance for TDE
        encryption.
        :param tde_credential_password: The password for the given ARN from the key store in order to access the
        device.
        :param vpc_security_group_ids: A list of EC2 VPC security groups to associate with this DB instance.
        :param domain: Specify the Active Directory directory ID to restore the DB instance in.
        :param copy_tags_to_snapshot: A value that indicates whether to copy all tags from the restored DB
        instance to snapshots of the DB instance.
        :param domain_iam_role_name: Specify the name of the IAM role to be used when making API calls to the
        Directory Service.
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param enable_cloudwatch_logs_exports: The list of logs that the restored DB instance is to export to
        CloudWatch Logs.
        :param processor_features: The number of CPU cores and the number of threads per core for the DB
        instance class of the DB instance.
        :param use_default_processor_features: A value that indicates whether the DB instance class of the DB instance
        uses its default processor features.
        :param db_parameter_group_name: The name of the DB parameter group to associate with this DB instance.
        :param deletion_protection: A value that indicates whether the DB instance has deletion protection
        enabled.
        :param enable_customer_owned_ip: A value that indicates whether to enable a customer-owned IP address
        (CoIP) for an RDS on Outposts DB instance.
        :param custom_iam_instance_profile: The instance profile associated with the underlying Amazon EC2 instance
        of an RDS Custom DB instance.
        :param backup_target: Specifies where automated backups and manual snapshots are stored for
        the restored DB instance.
        :param network_type: The network type of the DB instance.
        :returns: RestoreDBInstanceFromDBSnapshotResult
        :raises DBInstanceAlreadyExistsFault:
        :raises DBSnapshotNotFoundFault:
        :raises InstanceQuotaExceededFault:
        :raises InsufficientDBInstanceCapacityFault:
        :raises InvalidDBSnapshotStateFault:
        :raises StorageQuotaExceededFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InvalidRestoreFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises DBSubnetGroupDoesNotCoverEnoughAZs:
        :raises InvalidSubnet:
        :raises ProvisionedIopsNotAvailableInAZFault:
        :raises OptionGroupNotFoundFault:
        :raises StorageTypeNotSupportedFault:
        :raises AuthorizationNotFoundFault:
        :raises KMSKeyNotAccessibleFault:
        :raises DBSecurityGroupNotFoundFault:
        :raises DomainNotFoundFault:
        :raises DBParameterGroupNotFoundFault:
        :raises BackupPolicyNotFoundFault:
        :raises NetworkTypeNotSupported:
        """
        raise NotImplementedError

    @handler("RestoreDBInstanceFromS3")
    def restore_db_instance_from_s3(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        db_instance_class: String,
        engine: String,
        source_engine: String,
        source_engine_version: String,
        s3_bucket_name: String,
        s3_ingestion_role_arn: String,
        db_name: String = None,
        allocated_storage: IntegerOptional = None,
        master_username: String = None,
        master_user_password: String = None,
        db_security_groups: DBSecurityGroupNameList = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        availability_zone: String = None,
        db_subnet_group_name: String = None,
        preferred_maintenance_window: String = None,
        db_parameter_group_name: String = None,
        backup_retention_period: IntegerOptional = None,
        preferred_backup_window: String = None,
        port: IntegerOptional = None,
        multi_az: BooleanOptional = None,
        engine_version: String = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        license_model: String = None,
        iops: IntegerOptional = None,
        option_group_name: String = None,
        publicly_accessible: BooleanOptional = None,
        tags: TagList = None,
        storage_type: String = None,
        storage_encrypted: BooleanOptional = None,
        kms_key_id: String = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        monitoring_interval: IntegerOptional = None,
        monitoring_role_arn: String = None,
        enable_iam_database_authentication: BooleanOptional = None,
        s3_prefix: String = None,
        enable_performance_insights: BooleanOptional = None,
        performance_insights_kms_key_id: String = None,
        performance_insights_retention_period: IntegerOptional = None,
        enable_cloudwatch_logs_exports: LogTypeList = None,
        processor_features: ProcessorFeatureList = None,
        use_default_processor_features: BooleanOptional = None,
        deletion_protection: BooleanOptional = None,
        max_allocated_storage: IntegerOptional = None,
        network_type: String = None,
    ) -> RestoreDBInstanceFromS3Result:
        """Amazon Relational Database Service (Amazon RDS) supports importing MySQL
        databases by using backup files. You can create a backup of your
        on-premises database, store it on Amazon Simple Storage Service (Amazon
        S3), and then restore the backup file onto a new Amazon RDS DB instance
        running MySQL. For more information, see `Importing Data into an Amazon
        RDS MySQL DB
        Instance <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MySQL.Procedural.Importing.html>`__
        in the *Amazon RDS User Guide.*

        This command doesn't apply to RDS Custom.

        :param db_instance_identifier: The DB instance identifier.
        :param db_instance_class: The compute and memory capacity of the DB instance, for example
        db.
        :param engine: The name of the database engine to be used for this instance.
        :param source_engine: The name of the engine of your source database.
        :param source_engine_version: The version of the database that the backup files were created from.
        :param s3_bucket_name: The name of your Amazon S3 bucket that contains your database backup
        file.
        :param s3_ingestion_role_arn: An Amazon Web Services Identity and Access Management (IAM) role to
        allow Amazon RDS to access your Amazon S3 bucket.
        :param db_name: The name of the database to create when the DB instance is created.
        :param allocated_storage: The amount of storage (in gigabytes) to allocate initially for the DB
        instance.
        :param master_username: The name for the master user.
        :param master_user_password: The password for the master user.
        :param db_security_groups: A list of DB security groups to associate with this DB instance.
        :param vpc_security_group_ids: A list of VPC security groups to associate with this DB instance.
        :param availability_zone: The Availability Zone that the DB instance is created in.
        :param db_subnet_group_name: A DB subnet group to associate with this DB instance.
        :param preferred_maintenance_window: The time range each week during which system maintenance can occur, in
        Universal Coordinated Time (UTC).
        :param db_parameter_group_name: The name of the DB parameter group to associate with this DB instance.
        :param backup_retention_period: The number of days for which automated backups are retained.
        :param preferred_backup_window: The time range each day during which automated backups are created if
        automated backups are enabled.
        :param port: The port number on which the database accepts connections.
        :param multi_az: A value that indicates whether the DB instance is a Multi-AZ deployment.
        :param engine_version: The version number of the database engine to use.
        :param auto_minor_version_upgrade: A value that indicates whether minor engine upgrades are applied
        automatically to the DB instance during the maintenance window.
        :param license_model: The license model for this DB instance.
        :param iops: The amount of Provisioned IOPS (input/output operations per second) to
        allocate initially for the DB instance.
        :param option_group_name: The name of the option group to associate with this DB instance.
        :param publicly_accessible: A value that indicates whether the DB instance is publicly accessible.
        :param tags: A list of tags to associate with this DB instance.
        :param storage_type: Specifies the storage type to be associated with the DB instance.
        :param storage_encrypted: A value that indicates whether the new DB instance is encrypted or not.
        :param kms_key_id: The Amazon Web Services KMS key identifier for an encrypted DB instance.
        :param copy_tags_to_snapshot: A value that indicates whether to copy all tags from the DB instance to
        snapshots of the DB instance.
        :param monitoring_interval: The interval, in seconds, between points when Enhanced Monitoring
        metrics are collected for the DB instance.
        :param monitoring_role_arn: The ARN for the IAM role that permits RDS to send enhanced monitoring
        metrics to Amazon CloudWatch Logs.
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param s3_prefix: The prefix of your Amazon S3 bucket.
        :param enable_performance_insights: A value that indicates whether to enable Performance Insights for the DB
        instance.
        :param performance_insights_kms_key_id: The Amazon Web Services KMS key identifier for encryption of Performance
        Insights data.
        :param performance_insights_retention_period: The amount of time, in days, to retain Performance Insights data.
        :param enable_cloudwatch_logs_exports: The list of logs that the restored DB instance is to export to
        CloudWatch Logs.
        :param processor_features: The number of CPU cores and the number of threads per core for the DB
        instance class of the DB instance.
        :param use_default_processor_features: A value that indicates whether the DB instance class of the DB instance
        uses its default processor features.
        :param deletion_protection: A value that indicates whether the DB instance has deletion protection
        enabled.
        :param max_allocated_storage: The upper limit in gibibytes (GiB) to which Amazon RDS can automatically
        scale the storage of the DB instance.
        :param network_type: The network type of the DB instance.
        :returns: RestoreDBInstanceFromS3Result
        :raises DBInstanceAlreadyExistsFault:
        :raises InsufficientDBInstanceCapacityFault:
        :raises DBParameterGroupNotFoundFault:
        :raises DBSecurityGroupNotFoundFault:
        :raises InstanceQuotaExceededFault:
        :raises StorageQuotaExceededFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises DBSubnetGroupDoesNotCoverEnoughAZs:
        :raises InvalidSubnet:
        :raises InvalidVPCNetworkStateFault:
        :raises InvalidS3BucketFault:
        :raises ProvisionedIopsNotAvailableInAZFault:
        :raises OptionGroupNotFoundFault:
        :raises StorageTypeNotSupportedFault:
        :raises AuthorizationNotFoundFault:
        :raises KMSKeyNotAccessibleFault:
        :raises BackupPolicyNotFoundFault:
        :raises NetworkTypeNotSupported:
        """
        raise NotImplementedError

    @handler("RestoreDBInstanceToPointInTime")
    def restore_db_instance_to_point_in_time(
        self,
        context: RequestContext,
        target_db_instance_identifier: String,
        source_db_instance_identifier: String = None,
        restore_time: TStamp = None,
        use_latest_restorable_time: Boolean = None,
        db_instance_class: String = None,
        port: IntegerOptional = None,
        availability_zone: String = None,
        db_subnet_group_name: String = None,
        multi_az: BooleanOptional = None,
        publicly_accessible: BooleanOptional = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        license_model: String = None,
        db_name: String = None,
        engine: String = None,
        iops: IntegerOptional = None,
        option_group_name: String = None,
        copy_tags_to_snapshot: BooleanOptional = None,
        tags: TagList = None,
        storage_type: String = None,
        tde_credential_arn: String = None,
        tde_credential_password: String = None,
        vpc_security_group_ids: VpcSecurityGroupIdList = None,
        domain: String = None,
        domain_iam_role_name: String = None,
        enable_iam_database_authentication: BooleanOptional = None,
        enable_cloudwatch_logs_exports: LogTypeList = None,
        processor_features: ProcessorFeatureList = None,
        use_default_processor_features: BooleanOptional = None,
        db_parameter_group_name: String = None,
        deletion_protection: BooleanOptional = None,
        source_dbi_resource_id: String = None,
        max_allocated_storage: IntegerOptional = None,
        source_db_instance_automated_backups_arn: String = None,
        enable_customer_owned_ip: BooleanOptional = None,
        custom_iam_instance_profile: String = None,
        backup_target: String = None,
        network_type: String = None,
    ) -> RestoreDBInstanceToPointInTimeResult:
        """Restores a DB instance to an arbitrary point in time. You can restore to
        any point in time before the time identified by the LatestRestorableTime
        property. You can restore to a point up to the number of days specified
        by the BackupRetentionPeriod property.

        The target database is created with most of the original configuration,
        but in a system-selected Availability Zone, with the default security
        group, the default subnet group, and the default DB parameter group. By
        default, the new DB instance is created as a single-AZ deployment except
        when the instance is a SQL Server instance that has an option group that
        is associated with mirroring; in this case, the instance becomes a
        mirrored deployment and not a single-AZ deployment.

        This command doesn't apply to Aurora MySQL and Aurora PostgreSQL. For
        Aurora, use ``RestoreDBClusterToPointInTime``.

        :param target_db_instance_identifier: The name of the new DB instance to be created.
        :param source_db_instance_identifier: The identifier of the source DB instance from which to restore.
        :param restore_time: The date and time to restore from.
        :param use_latest_restorable_time: A value that indicates whether the DB instance is restored from the
        latest backup time.
        :param db_instance_class: The compute and memory capacity of the Amazon RDS DB instance, for
        example db.
        :param port: The port number on which the database accepts connections.
        :param availability_zone: The Availability Zone (AZ) where the DB instance will be created.
        :param db_subnet_group_name: The DB subnet group name to use for the new instance.
        :param multi_az: A value that indicates whether the DB instance is a Multi-AZ deployment.
        :param publicly_accessible: A value that indicates whether the DB instance is publicly accessible.
        :param auto_minor_version_upgrade: A value that indicates whether minor version upgrades are applied
        automatically to the DB instance during the maintenance window.
        :param license_model: License model information for the restored DB instance.
        :param db_name: The database name for the restored DB instance.
        :param engine: The database engine to use for the new instance.
        :param iops: The amount of Provisioned IOPS (input/output operations per second) to
        be initially allocated for the DB instance.
        :param option_group_name: The name of the option group to be used for the restored DB instance.
        :param copy_tags_to_snapshot: A value that indicates whether to copy all tags from the restored DB
        instance to snapshots of the DB instance.
        :param tags: A list of tags.
        :param storage_type: Specifies the storage type to be associated with the DB instance.
        :param tde_credential_arn: The ARN from the key store with which to associate the instance for TDE
        encryption.
        :param tde_credential_password: The password for the given ARN from the key store in order to access the
        device.
        :param vpc_security_group_ids: A list of EC2 VPC security groups to associate with this DB instance.
        :param domain: Specify the Active Directory directory ID to restore the DB instance in.
        :param domain_iam_role_name: Specify the name of the IAM role to be used when making API calls to the
        Directory Service.
        :param enable_iam_database_authentication: A value that indicates whether to enable mapping of Amazon Web Services
        Identity and Access Management (IAM) accounts to database accounts.
        :param enable_cloudwatch_logs_exports: The list of logs that the restored DB instance is to export to
        CloudWatch Logs.
        :param processor_features: The number of CPU cores and the number of threads per core for the DB
        instance class of the DB instance.
        :param use_default_processor_features: A value that indicates whether the DB instance class of the DB instance
        uses its default processor features.
        :param db_parameter_group_name: The name of the DB parameter group to associate with this DB instance.
        :param deletion_protection: A value that indicates whether the DB instance has deletion protection
        enabled.
        :param source_dbi_resource_id: The resource ID of the source DB instance from which to restore.
        :param max_allocated_storage: The upper limit in gibibytes (GiB) to which Amazon RDS can automatically
        scale the storage of the DB instance.
        :param source_db_instance_automated_backups_arn: The Amazon Resource Name (ARN) of the replicated automated backups from
        which to restore, for example,
        ``arn:aws:rds:useast-1:123456789012:auto-backup:ab-L2IJCEXJP7XQ7HOJ4SIEXAMPLE``.
        :param enable_customer_owned_ip: A value that indicates whether to enable a customer-owned IP address
        (CoIP) for an RDS on Outposts DB instance.
        :param custom_iam_instance_profile: The instance profile associated with the underlying Amazon EC2 instance
        of an RDS Custom DB instance.
        :param backup_target: Specifies where automated backups and manual snapshots are stored for
        the restored DB instance.
        :param network_type: The network type of the DB instance.
        :returns: RestoreDBInstanceToPointInTimeResult
        :raises DBInstanceAlreadyExistsFault:
        :raises DBInstanceNotFoundFault:
        :raises InstanceQuotaExceededFault:
        :raises InsufficientDBInstanceCapacityFault:
        :raises InvalidDBInstanceStateFault:
        :raises PointInTimeRestoreNotEnabledFault:
        :raises StorageQuotaExceededFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InvalidRestoreFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises DBSubnetGroupDoesNotCoverEnoughAZs:
        :raises InvalidSubnet:
        :raises ProvisionedIopsNotAvailableInAZFault:
        :raises OptionGroupNotFoundFault:
        :raises StorageTypeNotSupportedFault:
        :raises AuthorizationNotFoundFault:
        :raises KMSKeyNotAccessibleFault:
        :raises DBSecurityGroupNotFoundFault:
        :raises DomainNotFoundFault:
        :raises BackupPolicyNotFoundFault:
        :raises DBParameterGroupNotFoundFault:
        :raises DBInstanceAutomatedBackupNotFoundFault:
        :raises NetworkTypeNotSupported:
        """
        raise NotImplementedError

    @handler("RevokeDBSecurityGroupIngress")
    def revoke_db_security_group_ingress(
        self,
        context: RequestContext,
        db_security_group_name: String,
        cidrip: String = None,
        ec2_security_group_name: String = None,
        ec2_security_group_id: String = None,
        ec2_security_group_owner_id: String = None,
    ) -> RevokeDBSecurityGroupIngressResult:
        """Revokes ingress from a DBSecurityGroup for previously authorized IP
        ranges or EC2 or VPC security groups. Required parameters for this API
        are one of CIDRIP, EC2SecurityGroupId for VPC, or
        (EC2SecurityGroupOwnerId and either EC2SecurityGroupName or
        EC2SecurityGroupId).

        :param db_security_group_name: The name of the DB security group to revoke ingress from.
        :param cidrip: The IP range to revoke access from.
        :param ec2_security_group_name: The name of the EC2 security group to revoke access from.
        :param ec2_security_group_id: The id of the EC2 security group to revoke access from.
        :param ec2_security_group_owner_id: The Amazon Web Services account number of the owner of the EC2 security
        group specified in the ``EC2SecurityGroupName`` parameter.
        :returns: RevokeDBSecurityGroupIngressResult
        :raises DBSecurityGroupNotFoundFault:
        :raises AuthorizationNotFoundFault:
        :raises InvalidDBSecurityGroupStateFault:
        """
        raise NotImplementedError

    @handler("StartActivityStream")
    def start_activity_stream(
        self,
        context: RequestContext,
        resource_arn: String,
        mode: ActivityStreamMode,
        kms_key_id: String,
        apply_immediately: BooleanOptional = None,
        engine_native_audit_fields_included: BooleanOptional = None,
    ) -> StartActivityStreamResponse:
        """Starts a database activity stream to monitor activity on the database.
        For more information, see `Database Activity
        Streams <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/DBActivityStreams.html>`__
        in the *Amazon Aurora User Guide*.

        :param resource_arn: The Amazon Resource Name (ARN) of the DB cluster, for example,
        ``arn:aws:rds:us-east-1:12345667890:cluster:das-cluster``.
        :param mode: Specifies the mode of the database activity stream.
        :param kms_key_id: The Amazon Web Services KMS key identifier for encrypting messages in
        the database activity stream.
        :param apply_immediately: Specifies whether or not the database activity stream is to start as
        soon as possible, regardless of the maintenance window for the database.
        :param engine_native_audit_fields_included: Specifies whether the database activity stream includes engine-native
        audit fields.
        :returns: StartActivityStreamResponse
        :raises InvalidDBInstanceStateFault:
        :raises InvalidDBClusterStateFault:
        :raises ResourceNotFoundFault:
        :raises DBClusterNotFoundFault:
        :raises DBInstanceNotFoundFault:
        :raises KMSKeyNotAccessibleFault:
        """
        raise NotImplementedError

    @handler("StartDBCluster")
    def start_db_cluster(
        self, context: RequestContext, db_cluster_identifier: String
    ) -> StartDBClusterResult:
        """Starts an Amazon Aurora DB cluster that was stopped using the Amazon Web
        Services console, the stop-db-cluster CLI command, or the StopDBCluster
        action.

        For more information, see `Stopping and Starting an Aurora
        Cluster <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-cluster-stop-start.html>`__
        in the *Amazon Aurora User Guide*.

        This action only applies to Aurora DB clusters.

        :param db_cluster_identifier: The DB cluster identifier of the Amazon Aurora DB cluster to be started.
        :returns: StartDBClusterResult
        :raises DBClusterNotFoundFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError

    @handler("StartDBInstance")
    def start_db_instance(
        self, context: RequestContext, db_instance_identifier: String
    ) -> StartDBInstanceResult:
        """Starts an Amazon RDS DB instance that was stopped using the Amazon Web
        Services console, the stop-db-instance CLI command, or the
        StopDBInstance action.

        For more information, see `Starting an Amazon RDS DB instance That Was
        Previously
        Stopped <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_StartInstance.html>`__
        in the *Amazon RDS User Guide.*

        This command doesn't apply to RDS Custom, Aurora MySQL, and Aurora
        PostgreSQL. For Aurora DB clusters, use ``StartDBCluster`` instead.

        :param db_instance_identifier: The user-supplied instance identifier.
        :returns: StartDBInstanceResult
        :raises DBInstanceNotFoundFault:
        :raises InvalidDBInstanceStateFault:
        :raises InsufficientDBInstanceCapacityFault:
        :raises DBSubnetGroupNotFoundFault:
        :raises DBSubnetGroupDoesNotCoverEnoughAZs:
        :raises InvalidDBClusterStateFault:
        :raises InvalidSubnet:
        :raises InvalidVPCNetworkStateFault:
        :raises DBClusterNotFoundFault:
        :raises AuthorizationNotFoundFault:
        :raises KMSKeyNotAccessibleFault:
        """
        raise NotImplementedError

    @handler("StartDBInstanceAutomatedBackupsReplication")
    def start_db_instance_automated_backups_replication(
        self,
        context: RequestContext,
        source_db_instance_arn: String,
        backup_retention_period: IntegerOptional = None,
        kms_key_id: String = None,
        pre_signed_url: String = None,
        source_region: String = None,
    ) -> StartDBInstanceAutomatedBackupsReplicationResult:
        """Enables replication of automated backups to a different Amazon Web
        Services Region.

        This command doesn't apply to RDS Custom.

        For more information, see `Replicating Automated Backups to Another
        Amazon Web Services
        Region <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReplicateBackups.html>`__
        in the *Amazon RDS User Guide.*

        :param source_db_instance_arn: The Amazon Resource Name (ARN) of the source DB instance for the
        replicated automated backups, for example,
        ``arn:aws:rds:us-west-2:123456789012:db:mydatabase``.
        :param backup_retention_period: The retention period for the replicated automated backups.
        :param kms_key_id: The Amazon Web Services KMS key identifier for encryption of the
        replicated automated backups.
        :param pre_signed_url: A URL that contains a Signature Version 4 signed request for the
        StartDBInstanceAutomatedBackupsReplication action to be called in the
        Amazon Web Services Region of the source DB instance.
        :param source_region: The ID of the region that contains the source for the db instance.
        :returns: StartDBInstanceAutomatedBackupsReplicationResult
        :raises DBInstanceNotFoundFault:
        :raises InvalidDBInstanceStateFault:
        :raises KMSKeyNotAccessibleFault:
        :raises DBInstanceAutomatedBackupQuotaExceededFault:
        :raises StorageTypeNotSupportedFault:
        """
        raise NotImplementedError

    @handler("StartExportTask")
    def start_export_task(
        self,
        context: RequestContext,
        export_task_identifier: String,
        source_arn: String,
        s3_bucket_name: String,
        iam_role_arn: String,
        kms_key_id: String,
        s3_prefix: String = None,
        export_only: StringList = None,
    ) -> ExportTask:
        """Starts an export of a snapshot to Amazon S3. The provided IAM role must
        have access to the S3 bucket.

        This command doesn't apply to RDS Custom.

        :param export_task_identifier: A unique identifier for the snapshot export task.
        :param source_arn: The Amazon Resource Name (ARN) of the snapshot to export to Amazon S3.
        :param s3_bucket_name: The name of the Amazon S3 bucket to export the snapshot to.
        :param iam_role_arn: The name of the IAM role to use for writing to the Amazon S3 bucket when
        exporting a snapshot.
        :param kms_key_id: The ID of the Amazon Web Services KMS key to use to encrypt the snapshot
        exported to Amazon S3.
        :param s3_prefix: The Amazon S3 bucket prefix to use as the file name and path of the
        exported snapshot.
        :param export_only: The data to be exported from the snapshot.
        :returns: ExportTask
        :raises DBSnapshotNotFoundFault:
        :raises DBClusterSnapshotNotFoundFault:
        :raises ExportTaskAlreadyExistsFault:
        :raises InvalidS3BucketFault:
        :raises IamRoleNotFoundFault:
        :raises IamRoleMissingPermissionsFault:
        :raises InvalidExportOnlyFault:
        :raises KMSKeyNotAccessibleFault:
        :raises InvalidExportSourceStateFault:
        """
        raise NotImplementedError

    @handler("StopActivityStream")
    def stop_activity_stream(
        self,
        context: RequestContext,
        resource_arn: String,
        apply_immediately: BooleanOptional = None,
    ) -> StopActivityStreamResponse:
        """Stops a database activity stream that was started using the Amazon Web
        Services console, the ``start-activity-stream`` CLI command, or the
        ``StartActivityStream`` action.

        For more information, see `Database Activity
        Streams <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/DBActivityStreams.html>`__
        in the *Amazon Aurora User Guide*.

        :param resource_arn: The Amazon Resource Name (ARN) of the DB cluster for the database
        activity stream.
        :param apply_immediately: Specifies whether or not the database activity stream is to stop as soon
        as possible, regardless of the maintenance window for the database.
        :returns: StopActivityStreamResponse
        :raises InvalidDBInstanceStateFault:
        :raises InvalidDBClusterStateFault:
        :raises ResourceNotFoundFault:
        :raises DBClusterNotFoundFault:
        :raises DBInstanceNotFoundFault:
        """
        raise NotImplementedError

    @handler("StopDBCluster")
    def stop_db_cluster(
        self, context: RequestContext, db_cluster_identifier: String
    ) -> StopDBClusterResult:
        """Stops an Amazon Aurora DB cluster. When you stop a DB cluster, Aurora
        retains the DB cluster's metadata, including its endpoints and DB
        parameter groups. Aurora also retains the transaction logs so you can do
        a point-in-time restore if necessary.

        For more information, see `Stopping and Starting an Aurora
        Cluster <https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-cluster-stop-start.html>`__
        in the *Amazon Aurora User Guide*.

        This action only applies to Aurora DB clusters.

        :param db_cluster_identifier: The DB cluster identifier of the Amazon Aurora DB cluster to be stopped.
        :returns: StopDBClusterResult
        :raises DBClusterNotFoundFault:
        :raises InvalidDBClusterStateFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError

    @handler("StopDBInstance")
    def stop_db_instance(
        self,
        context: RequestContext,
        db_instance_identifier: String,
        db_snapshot_identifier: String = None,
    ) -> StopDBInstanceResult:
        """Stops an Amazon RDS DB instance. When you stop a DB instance, Amazon RDS
        retains the DB instance's metadata, including its endpoint, DB parameter
        group, and option group membership. Amazon RDS also retains the
        transaction logs so you can do a point-in-time restore if necessary.

        For more information, see `Stopping an Amazon RDS DB Instance
        Temporarily <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_StopInstance.html>`__
        in the *Amazon RDS User Guide.*

        This command doesn't apply to RDS Custom, Aurora MySQL, and Aurora
        PostgreSQL. For Aurora clusters, use ``StopDBCluster`` instead.

        :param db_instance_identifier: The user-supplied instance identifier.
        :param db_snapshot_identifier: The user-supplied instance identifier of the DB Snapshot created
        immediately before the DB instance is stopped.
        :returns: StopDBInstanceResult
        :raises DBInstanceNotFoundFault:
        :raises InvalidDBInstanceStateFault:
        :raises DBSnapshotAlreadyExistsFault:
        :raises SnapshotQuotaExceededFault:
        :raises InvalidDBClusterStateFault:
        """
        raise NotImplementedError

    @handler("StopDBInstanceAutomatedBackupsReplication")
    def stop_db_instance_automated_backups_replication(
        self, context: RequestContext, source_db_instance_arn: String
    ) -> StopDBInstanceAutomatedBackupsReplicationResult:
        """Stops automated backup replication for a DB instance.

        This command doesn't apply to RDS Custom.

        For more information, see `Replicating Automated Backups to Another
        Amazon Web Services
        Region <https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReplicateBackups.html>`__
        in the *Amazon RDS User Guide.*

        :param source_db_instance_arn: The Amazon Resource Name (ARN) of the source DB instance for which to
        stop replicating automated backups, for example,
        ``arn:aws:rds:us-west-2:123456789012:db:mydatabase``.
        :returns: StopDBInstanceAutomatedBackupsReplicationResult
        :raises DBInstanceNotFoundFault:
        :raises InvalidDBInstanceStateFault:
        """
        raise NotImplementedError
