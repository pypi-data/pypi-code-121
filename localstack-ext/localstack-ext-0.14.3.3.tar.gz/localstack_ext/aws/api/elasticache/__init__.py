import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AccessString = str
AllowedNodeGroupId = str
AwsQueryErrorMessage = str
Boolean = bool
BooleanOptional = bool
Double = float
EngineType = str
FilterName = str
FilterValue = str
Integer = int
IntegerOptional = int
String = str
UserGroupId = str
UserId = str
UserName = str


class AZMode(str):
    single_az = "single-az"
    cross_az = "cross-az"


class AuthTokenUpdateStatus(str):
    SETTING = "SETTING"
    ROTATING = "ROTATING"


class AuthTokenUpdateStrategyType(str):
    SET = "SET"
    ROTATE = "ROTATE"
    DELETE = "DELETE"


class AuthenticationType(str):
    password = "password"
    no_password = "no-password"


class AutomaticFailoverStatus(str):
    enabled = "enabled"
    disabled = "disabled"
    enabling = "enabling"
    disabling = "disabling"


class ChangeType(str):
    immediate = "immediate"
    requires_reboot = "requires-reboot"


class DataTieringStatus(str):
    enabled = "enabled"
    disabled = "disabled"


class DestinationType(str):
    cloudwatch_logs = "cloudwatch-logs"
    kinesis_firehose = "kinesis-firehose"


class LogDeliveryConfigurationStatus(str):
    active = "active"
    enabling = "enabling"
    modifying = "modifying"
    disabling = "disabling"
    error = "error"


class LogFormat(str):
    text = "text"
    json = "json"


class LogType(str):
    slow_log = "slow-log"
    engine_log = "engine-log"


class MultiAZStatus(str):
    enabled = "enabled"
    disabled = "disabled"


class NodeUpdateInitiatedBy(str):
    system = "system"
    customer = "customer"


class NodeUpdateStatus(str):
    not_applied = "not-applied"
    waiting_to_start = "waiting-to-start"
    in_progress = "in-progress"
    stopping = "stopping"
    stopped = "stopped"
    complete = "complete"


class OutpostMode(str):
    single_outpost = "single-outpost"
    cross_outpost = "cross-outpost"


class PendingAutomaticFailoverStatus(str):
    enabled = "enabled"
    disabled = "disabled"


class ServiceUpdateSeverity(str):
    critical = "critical"
    important = "important"
    medium = "medium"
    low = "low"


class ServiceUpdateStatus(str):
    available = "available"
    cancelled = "cancelled"
    expired = "expired"


class ServiceUpdateType(str):
    security_update = "security-update"


class SlaMet(str):
    yes = "yes"
    no = "no"
    n_a = "n/a"


class SourceType(str):
    cache_cluster = "cache-cluster"
    cache_parameter_group = "cache-parameter-group"
    cache_security_group = "cache-security-group"
    cache_subnet_group = "cache-subnet-group"
    replication_group = "replication-group"
    user = "user"
    user_group = "user-group"


class UpdateActionStatus(str):
    not_applied = "not-applied"
    waiting_to_start = "waiting-to-start"
    in_progress = "in-progress"
    stopping = "stopping"
    stopped = "stopped"
    complete = "complete"
    scheduling = "scheduling"
    scheduled = "scheduled"
    not_applicable = "not-applicable"


class APICallRateForCustomerExceededFault(ServiceException):
    """The customer has exceeded the allowed rate of API calls."""


class AuthorizationAlreadyExistsFault(ServiceException):
    """The specified Amazon EC2 security group is already authorized for the
    specified cache security group.
    """


class AuthorizationNotFoundFault(ServiceException):
    """The specified Amazon EC2 security group is not authorized for the
    specified cache security group.
    """


class CacheClusterAlreadyExistsFault(ServiceException):
    """You already have a cluster with the given identifier."""


class CacheClusterNotFoundFault(ServiceException):
    """The requested cluster ID does not refer to an existing cluster."""


class CacheParameterGroupAlreadyExistsFault(ServiceException):
    """A cache parameter group with the requested name already exists."""


class CacheParameterGroupNotFoundFault(ServiceException):
    """The requested cache parameter group name does not refer to an existing
    cache parameter group.
    """


class CacheParameterGroupQuotaExceededFault(ServiceException):
    """The request cannot be processed because it would exceed the maximum
    number of cache security groups.
    """


class CacheSecurityGroupAlreadyExistsFault(ServiceException):
    """A cache security group with the specified name already exists."""


class CacheSecurityGroupNotFoundFault(ServiceException):
    """The requested cache security group name does not refer to an existing
    cache security group.
    """


class CacheSecurityGroupQuotaExceededFault(ServiceException):
    """The request cannot be processed because it would exceed the allowed
    number of cache security groups.
    """


class CacheSubnetGroupAlreadyExistsFault(ServiceException):
    """The requested cache subnet group name is already in use by an existing
    cache subnet group.
    """


class CacheSubnetGroupInUse(ServiceException):
    """The requested cache subnet group is currently in use."""


class CacheSubnetGroupNotFoundFault(ServiceException):
    """The requested cache subnet group name does not refer to an existing
    cache subnet group.
    """


class CacheSubnetGroupQuotaExceededFault(ServiceException):
    """The request cannot be processed because it would exceed the allowed
    number of cache subnet groups.
    """


class CacheSubnetQuotaExceededFault(ServiceException):
    """The request cannot be processed because it would exceed the allowed
    number of subnets in a cache subnet group.
    """


class ClusterQuotaForCustomerExceededFault(ServiceException):
    """The request cannot be processed because it would exceed the allowed
    number of clusters per customer.
    """


class DefaultUserAssociatedToUserGroupFault(ServiceException):
    """The default user assigned to the user group."""


class DefaultUserRequired(ServiceException):
    """You must add default user to a user group."""


class DuplicateUserNameFault(ServiceException):
    """A user with this username already exists."""


class GlobalReplicationGroupAlreadyExistsFault(ServiceException):
    """The Global datastore name already exists."""


class GlobalReplicationGroupNotFoundFault(ServiceException):
    """The Global datastore does not exist"""


class InsufficientCacheClusterCapacityFault(ServiceException):
    """The requested cache node type is not available in the specified
    Availability Zone. For more information, see
    `InsufficientCacheClusterCapacity <http://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/ErrorMessages.html#ErrorMessages.INSUFFICIENT_CACHE_CLUSTER_CAPACITY>`__
    in the ElastiCache User Guide.
    """


class InvalidARNFault(ServiceException):
    """The requested Amazon Resource Name (ARN) does not refer to an existing
    resource.
    """


class InvalidCacheClusterStateFault(ServiceException):
    """The requested cluster is not in the ``available`` state."""


class InvalidCacheParameterGroupStateFault(ServiceException):
    """The current state of the cache parameter group does not allow the
    requested operation to occur.
    """


class InvalidCacheSecurityGroupStateFault(ServiceException):
    """The current state of the cache security group does not allow deletion."""


class InvalidGlobalReplicationGroupStateFault(ServiceException):
    """The Global datastore is not available or in primary-only state."""


class InvalidKMSKeyFault(ServiceException):
    """The KMS key supplied is not valid."""


class InvalidParameterCombinationException(ServiceException):
    """Two or more incompatible parameters were specified."""

    message: Optional[AwsQueryErrorMessage]


class InvalidParameterValueException(ServiceException):
    """The value for a parameter is invalid."""

    message: Optional[AwsQueryErrorMessage]


class InvalidReplicationGroupStateFault(ServiceException):
    """The requested replication group is not in the ``available`` state."""


class InvalidSnapshotStateFault(ServiceException):
    """The current state of the snapshot does not allow the requested operation
    to occur.
    """


class InvalidSubnet(ServiceException):
    """An invalid subnet identifier was specified."""


class InvalidUserGroupStateFault(ServiceException):
    """The user group is not in an active state."""


class InvalidUserStateFault(ServiceException):
    """The user is not in active state."""


class InvalidVPCNetworkStateFault(ServiceException):
    """The VPC network is in an invalid state."""


class NoOperationFault(ServiceException):
    """The operation was not performed because no changes were required."""


class NodeGroupNotFoundFault(ServiceException):
    """The node group specified by the ``NodeGroupId`` parameter could not be
    found. Please verify that the node group exists and that you spelled the
    ``NodeGroupId`` value correctly.
    """


class NodeGroupsPerReplicationGroupQuotaExceededFault(ServiceException):
    """The request cannot be processed because it would exceed the maximum
    allowed number of node groups (shards) in a single replication group.
    The default maximum is 90
    """


class NodeQuotaForClusterExceededFault(ServiceException):
    """The request cannot be processed because it would exceed the allowed
    number of cache nodes in a single cluster.
    """


class NodeQuotaForCustomerExceededFault(ServiceException):
    """The request cannot be processed because it would exceed the allowed
    number of cache nodes per customer.
    """


class ReplicationGroupAlreadyExistsFault(ServiceException):
    """The specified replication group already exists."""


class ReplicationGroupAlreadyUnderMigrationFault(ServiceException):
    """The targeted replication group is not available."""


class ReplicationGroupNotFoundFault(ServiceException):
    """The specified replication group does not exist."""


class ReplicationGroupNotUnderMigrationFault(ServiceException):
    """The designated replication group is not available for data migration."""


class ReservedCacheNodeAlreadyExistsFault(ServiceException):
    """You already have a reservation with the given identifier."""


class ReservedCacheNodeNotFoundFault(ServiceException):
    """The requested reserved cache node was not found."""


class ReservedCacheNodeQuotaExceededFault(ServiceException):
    """The request cannot be processed because it would exceed the user's cache
    node quota.
    """


class ReservedCacheNodesOfferingNotFoundFault(ServiceException):
    """The requested cache node offering does not exist."""


class ServiceLinkedRoleNotFoundFault(ServiceException):
    """The specified service linked role (SLR) was not found."""


class ServiceUpdateNotFoundFault(ServiceException):
    """The service update doesn't exist"""


class SnapshotAlreadyExistsFault(ServiceException):
    """You already have a snapshot with the given name."""


class SnapshotFeatureNotSupportedFault(ServiceException):
    """You attempted one of the following operations:

    -  Creating a snapshot of a Redis cluster running on a
       ``cache.t1.micro`` cache node.

    -  Creating a snapshot of a cluster that is running Memcached rather
       than Redis.

    Neither of these are supported by ElastiCache.
    """


class SnapshotNotFoundFault(ServiceException):
    """The requested snapshot name does not refer to an existing snapshot."""


class SnapshotQuotaExceededFault(ServiceException):
    """The request cannot be processed because it would exceed the maximum
    number of snapshots.
    """


class SubnetInUse(ServiceException):
    """The requested subnet is being used by another cache subnet group."""


class SubnetNotAllowedFault(ServiceException):
    """At least one subnet ID does not match the other subnet IDs. This
    mismatch typically occurs when a user sets one subnet ID to a regional
    Availability Zone and a different one to an outpost. Or when a user sets
    the subnet ID to an Outpost when not subscribed on this service.
    """


class TagNotFoundFault(ServiceException):
    """The requested tag was not found on this resource."""


class TagQuotaPerResourceExceeded(ServiceException):
    """The request cannot be processed because it would cause the resource to
    have more than the allowed number of tags. The maximum number of tags
    permitted on a resource is 50.
    """


class TestFailoverNotAvailableFault(ServiceException):
    """The ``TestFailover`` action is not available."""


class UserAlreadyExistsFault(ServiceException):
    """A user with this ID already exists."""


class UserGroupAlreadyExistsFault(ServiceException):
    """The user group with this ID already exists."""


class UserGroupNotFoundFault(ServiceException):
    """The user group was not found or does not exist"""


class UserGroupQuotaExceededFault(ServiceException):
    """The number of users exceeds the user group limit."""


class UserNotFoundFault(ServiceException):
    """The user does not exist or could not be found."""


class UserQuotaExceededFault(ServiceException):
    """The quota of users has been exceeded."""


class Tag(TypedDict, total=False):
    """A tag that can be added to an ElastiCache cluster or replication group.
    Tags are composed of a Key/Value pair. You can use tags to categorize
    and track all your ElastiCache resources, with the exception of global
    replication group. When you add or remove tags on replication groups,
    those actions will be replicated to all nodes in the replication group.
    A tag with a null Value is permitted.
    """

    Key: Optional[String]
    Value: Optional[String]


TagList = List[Tag]


class AddTagsToResourceMessage(ServiceRequest):
    """Represents the input of an AddTagsToResource operation."""

    ResourceName: String
    Tags: TagList


NodeTypeList = List[String]


class AllowedNodeTypeModificationsMessage(TypedDict, total=False):
    """Represents the allowed node types you can use to modify your cluster or
    replication group.
    """

    ScaleUpModifications: Optional[NodeTypeList]
    ScaleDownModifications: Optional[NodeTypeList]


class Authentication(TypedDict, total=False):
    """Indicates whether the user requires a password to authenticate."""

    Type: Optional[AuthenticationType]
    PasswordCount: Optional[IntegerOptional]


class AuthorizeCacheSecurityGroupIngressMessage(ServiceRequest):
    """Represents the input of an AuthorizeCacheSecurityGroupIngress operation."""

    CacheSecurityGroupName: String
    EC2SecurityGroupName: String
    EC2SecurityGroupOwnerId: String


class EC2SecurityGroup(TypedDict, total=False):
    """Provides ownership and status information for an Amazon EC2 security
    group.
    """

    Status: Optional[String]
    EC2SecurityGroupName: Optional[String]
    EC2SecurityGroupOwnerId: Optional[String]


EC2SecurityGroupList = List[EC2SecurityGroup]


class CacheSecurityGroup(TypedDict, total=False):
    """Represents the output of one of the following operations:

    -  ``AuthorizeCacheSecurityGroupIngress``

    -  ``CreateCacheSecurityGroup``

    -  ``RevokeCacheSecurityGroupIngress``
    """

    OwnerId: Optional[String]
    CacheSecurityGroupName: Optional[String]
    Description: Optional[String]
    EC2SecurityGroups: Optional[EC2SecurityGroupList]
    ARN: Optional[String]


class AuthorizeCacheSecurityGroupIngressResult(TypedDict, total=False):
    CacheSecurityGroup: Optional[CacheSecurityGroup]


class AvailabilityZone(TypedDict, total=False):
    """Describes an Availability Zone in which the cluster is launched."""

    Name: Optional[String]


AvailabilityZonesList = List[String]
CacheClusterIdList = List[String]
ReplicationGroupIdList = List[String]


class BatchApplyUpdateActionMessage(ServiceRequest):
    ReplicationGroupIds: Optional[ReplicationGroupIdList]
    CacheClusterIds: Optional[CacheClusterIdList]
    ServiceUpdateName: String


class BatchStopUpdateActionMessage(ServiceRequest):
    ReplicationGroupIds: Optional[ReplicationGroupIdList]
    CacheClusterIds: Optional[CacheClusterIdList]
    ServiceUpdateName: String


class KinesisFirehoseDestinationDetails(TypedDict, total=False):
    """The configuration details of the Kinesis Data Firehose destination."""

    DeliveryStream: Optional[String]


class CloudWatchLogsDestinationDetails(TypedDict, total=False):
    """The configuration details of the CloudWatch Logs destination."""

    LogGroup: Optional[String]


class DestinationDetails(TypedDict, total=False):
    """Configuration details of either a CloudWatch Logs destination or Kinesis
    Data Firehose destination.
    """

    CloudWatchLogsDetails: Optional[CloudWatchLogsDestinationDetails]
    KinesisFirehoseDetails: Optional[KinesisFirehoseDestinationDetails]


class LogDeliveryConfiguration(TypedDict, total=False):
    """Returns the destination, format and type of the logs."""

    LogType: Optional[LogType]
    DestinationType: Optional[DestinationType]
    DestinationDetails: Optional[DestinationDetails]
    LogFormat: Optional[LogFormat]
    Status: Optional[LogDeliveryConfigurationStatus]
    Message: Optional[String]


LogDeliveryConfigurationList = List[LogDeliveryConfiguration]
TStamp = datetime


class SecurityGroupMembership(TypedDict, total=False):
    """Represents a single cache security group and its status."""

    SecurityGroupId: Optional[String]
    Status: Optional[String]


SecurityGroupMembershipList = List[SecurityGroupMembership]


class Endpoint(TypedDict, total=False):
    """Represents the information required for client programs to connect to a
    cache node.
    """

    Address: Optional[String]
    Port: Optional[Integer]


class CacheNode(TypedDict, total=False):
    """Represents an individual cache node within a cluster. Each cache node
    runs its own instance of the cluster's protocol-compliant caching
    software - either Memcached or Redis.

    The following node types are supported by ElastiCache. Generally
    speaking, the current generation types provide more memory and
    computational power at lower cost when compared to their equivalent
    previous generation counterparts.

    -  General purpose:

       -  Current generation:

          **M6g node types:** (available only for Redis engine version 5.0.6
          onward and for Memcached engine version 1.5.16 onward):
          ``cache.m6g.large``, ``cache.m6g.xlarge``, ``cache.m6g.2xlarge``,
          ``cache.m6g.4xlarge``, ``cache.m6g.8xlarge``,
          ``cache.m6g.12xlarge``, ``cache.m6g.16xlarge``

          For region availability, see `Supported Node
          Types <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/CacheNodes.SupportedTypes.html#CacheNodes.SupportedTypesByRegion>`__

          **M5 node types:** ``cache.m5.large``, ``cache.m5.xlarge``,
          ``cache.m5.2xlarge``, ``cache.m5.4xlarge``, ``cache.m5.12xlarge``,
          ``cache.m5.24xlarge``

          **M4 node types:** ``cache.m4.large``, ``cache.m4.xlarge``,
          ``cache.m4.2xlarge``, ``cache.m4.4xlarge``, ``cache.m4.10xlarge``

          **T4g node types** (available only for Redis engine version 5.0.6
          onward and for Memcached engine version 1.5.16 onward):
          ``cache.t4g.micro``, ``cache.t4g.small``, ``cache.t4g.medium``

          **T3 node types:** ``cache.t3.micro``, ``cache.t3.small``,
          ``cache.t3.medium``

          **T2 node types:** ``cache.t2.micro``, ``cache.t2.small``,
          ``cache.t2.medium``

       -  Previous generation: (not recommended. Existing clusters are still
          supported but creation of new clusters is not supported for these
          types.)

          **T1 node types:** ``cache.t1.micro``

          **M1 node types:** ``cache.m1.small``, ``cache.m1.medium``,
          ``cache.m1.large``, ``cache.m1.xlarge``

          **M3 node types:** ``cache.m3.medium``, ``cache.m3.large``,
          ``cache.m3.xlarge``, ``cache.m3.2xlarge``

    -  Compute optimized:

       -  Previous generation: (not recommended. Existing clusters are still
          supported but creation of new clusters is not supported for these
          types.)

          **C1 node types:** ``cache.c1.xlarge``

    -  Memory optimized with data tiering:

       -  Current generation:

          **R6gd node types** (available only for Redis engine version 6.2
          onward).

          ``cache.r6gd.xlarge``, ``cache.r6gd.2xlarge``,
          ``cache.r6gd.4xlarge``, ``cache.r6gd.8xlarge``,
          ``cache.r6gd.12xlarge``, ``cache.r6gd.16xlarge``

    -  Memory optimized:

       -  Current generation:

          **R6g node types** (available only for Redis engine version 5.0.6
          onward and for Memcached engine version 1.5.16 onward).

          ``cache.r6g.large``, ``cache.r6g.xlarge``, ``cache.r6g.2xlarge``,
          ``cache.r6g.4xlarge``, ``cache.r6g.8xlarge``,
          ``cache.r6g.12xlarge``, ``cache.r6g.16xlarge``

          For region availability, see `Supported Node
          Types <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/CacheNodes.SupportedTypes.html#CacheNodes.SupportedTypesByRegion>`__

          **R5 node types:** ``cache.r5.large``, ``cache.r5.xlarge``,
          ``cache.r5.2xlarge``, ``cache.r5.4xlarge``, ``cache.r5.12xlarge``,
          ``cache.r5.24xlarge``

          **R4 node types:** ``cache.r4.large``, ``cache.r4.xlarge``,
          ``cache.r4.2xlarge``, ``cache.r4.4xlarge``, ``cache.r4.8xlarge``,
          ``cache.r4.16xlarge``

       -  Previous generation: (not recommended. Existing clusters are still
          supported but creation of new clusters is not supported for these
          types.)

          **M2 node types:** ``cache.m2.xlarge``, ``cache.m2.2xlarge``,
          ``cache.m2.4xlarge``

          **R3 node types:** ``cache.r3.large``, ``cache.r3.xlarge``,
          ``cache.r3.2xlarge``, ``cache.r3.4xlarge``, ``cache.r3.8xlarge``

    **Additional node type info**

    -  All current generation instance types are created in Amazon VPC by
       default.

    -  Redis append-only files (AOF) are not supported for T1 or T2
       instances.

    -  Redis Multi-AZ with automatic failover is not supported on T1
       instances.

    -  Redis configuration variables ``appendonly`` and ``appendfsync`` are
       not supported on Redis version 2.8.22 and later.
    """

    CacheNodeId: Optional[String]
    CacheNodeStatus: Optional[String]
    CacheNodeCreateTime: Optional[TStamp]
    Endpoint: Optional[Endpoint]
    ParameterGroupStatus: Optional[String]
    SourceCacheNodeId: Optional[String]
    CustomerAvailabilityZone: Optional[String]
    CustomerOutpostArn: Optional[String]


CacheNodeList = List[CacheNode]
CacheNodeIdsList = List[String]


class CacheParameterGroupStatus(TypedDict, total=False):
    """Status of the cache parameter group."""

    CacheParameterGroupName: Optional[String]
    ParameterApplyStatus: Optional[String]
    CacheNodeIdsToReboot: Optional[CacheNodeIdsList]


class CacheSecurityGroupMembership(TypedDict, total=False):
    """Represents a cluster's status within a particular cache security group."""

    CacheSecurityGroupName: Optional[String]
    Status: Optional[String]


CacheSecurityGroupMembershipList = List[CacheSecurityGroupMembership]


class NotificationConfiguration(TypedDict, total=False):
    """Describes a notification topic and its status. Notification topics are
    used for publishing ElastiCache events to subscribers using Amazon
    Simple Notification Service (SNS).
    """

    TopicArn: Optional[String]
    TopicStatus: Optional[String]


class PendingLogDeliveryConfiguration(TypedDict, total=False):
    """The log delivery configurations being modified"""

    LogType: Optional[LogType]
    DestinationType: Optional[DestinationType]
    DestinationDetails: Optional[DestinationDetails]
    LogFormat: Optional[LogFormat]


PendingLogDeliveryConfigurationList = List[PendingLogDeliveryConfiguration]


class PendingModifiedValues(TypedDict, total=False):
    """A group of settings that are applied to the cluster in the future, or
    that are currently being applied.
    """

    NumCacheNodes: Optional[IntegerOptional]
    CacheNodeIdsToRemove: Optional[CacheNodeIdsList]
    EngineVersion: Optional[String]
    CacheNodeType: Optional[String]
    AuthTokenStatus: Optional[AuthTokenUpdateStatus]
    LogDeliveryConfigurations: Optional[PendingLogDeliveryConfigurationList]


class CacheCluster(TypedDict, total=False):
    """Contains all of the attributes of a specific cluster."""

    CacheClusterId: Optional[String]
    ConfigurationEndpoint: Optional[Endpoint]
    ClientDownloadLandingPage: Optional[String]
    CacheNodeType: Optional[String]
    Engine: Optional[String]
    EngineVersion: Optional[String]
    CacheClusterStatus: Optional[String]
    NumCacheNodes: Optional[IntegerOptional]
    PreferredAvailabilityZone: Optional[String]
    PreferredOutpostArn: Optional[String]
    CacheClusterCreateTime: Optional[TStamp]
    PreferredMaintenanceWindow: Optional[String]
    PendingModifiedValues: Optional[PendingModifiedValues]
    NotificationConfiguration: Optional[NotificationConfiguration]
    CacheSecurityGroups: Optional[CacheSecurityGroupMembershipList]
    CacheParameterGroup: Optional[CacheParameterGroupStatus]
    CacheSubnetGroupName: Optional[String]
    CacheNodes: Optional[CacheNodeList]
    AutoMinorVersionUpgrade: Optional[Boolean]
    SecurityGroups: Optional[SecurityGroupMembershipList]
    ReplicationGroupId: Optional[String]
    SnapshotRetentionLimit: Optional[IntegerOptional]
    SnapshotWindow: Optional[String]
    AuthTokenEnabled: Optional[BooleanOptional]
    AuthTokenLastModifiedDate: Optional[TStamp]
    TransitEncryptionEnabled: Optional[BooleanOptional]
    AtRestEncryptionEnabled: Optional[BooleanOptional]
    ARN: Optional[String]
    ReplicationGroupLogDeliveryEnabled: Optional[Boolean]
    LogDeliveryConfigurations: Optional[LogDeliveryConfigurationList]


CacheClusterList = List[CacheCluster]


class CacheClusterMessage(TypedDict, total=False):
    """Represents the output of a ``DescribeCacheClusters`` operation."""

    Marker: Optional[String]
    CacheClusters: Optional[CacheClusterList]


class CacheEngineVersion(TypedDict, total=False):
    """Provides all of the details about a particular cache engine version."""

    Engine: Optional[String]
    EngineVersion: Optional[String]
    CacheParameterGroupFamily: Optional[String]
    CacheEngineDescription: Optional[String]
    CacheEngineVersionDescription: Optional[String]


CacheEngineVersionList = List[CacheEngineVersion]


class CacheEngineVersionMessage(TypedDict, total=False):
    """Represents the output of a DescribeCacheEngineVersions operation."""

    Marker: Optional[String]
    CacheEngineVersions: Optional[CacheEngineVersionList]


class CacheNodeTypeSpecificValue(TypedDict, total=False):
    """A value that applies only to a certain cache node type."""

    CacheNodeType: Optional[String]
    Value: Optional[String]


CacheNodeTypeSpecificValueList = List[CacheNodeTypeSpecificValue]


class CacheNodeTypeSpecificParameter(TypedDict, total=False):
    """A parameter that has a different value for each cache node type it is
    applied to. For example, in a Redis cluster, a ``cache.m1.large`` cache
    node type would have a larger ``maxmemory`` value than a
    ``cache.m1.small`` type.
    """

    ParameterName: Optional[String]
    Description: Optional[String]
    Source: Optional[String]
    DataType: Optional[String]
    AllowedValues: Optional[String]
    IsModifiable: Optional[Boolean]
    MinimumEngineVersion: Optional[String]
    CacheNodeTypeSpecificValues: Optional[CacheNodeTypeSpecificValueList]
    ChangeType: Optional[ChangeType]


CacheNodeTypeSpecificParametersList = List[CacheNodeTypeSpecificParameter]


class CacheNodeUpdateStatus(TypedDict, total=False):
    """The status of the service update on the cache node"""

    CacheNodeId: Optional[String]
    NodeUpdateStatus: Optional[NodeUpdateStatus]
    NodeDeletionDate: Optional[TStamp]
    NodeUpdateStartDate: Optional[TStamp]
    NodeUpdateEndDate: Optional[TStamp]
    NodeUpdateInitiatedBy: Optional[NodeUpdateInitiatedBy]
    NodeUpdateInitiatedDate: Optional[TStamp]
    NodeUpdateStatusModifiedDate: Optional[TStamp]


CacheNodeUpdateStatusList = List[CacheNodeUpdateStatus]


class CacheParameterGroup(TypedDict, total=False):
    """Represents the output of a ``CreateCacheParameterGroup`` operation."""

    CacheParameterGroupName: Optional[String]
    CacheParameterGroupFamily: Optional[String]
    Description: Optional[String]
    IsGlobal: Optional[Boolean]
    ARN: Optional[String]


class Parameter(TypedDict, total=False):
    """Describes an individual setting that controls some aspect of ElastiCache
    behavior.
    """

    ParameterName: Optional[String]
    ParameterValue: Optional[String]
    Description: Optional[String]
    Source: Optional[String]
    DataType: Optional[String]
    AllowedValues: Optional[String]
    IsModifiable: Optional[Boolean]
    MinimumEngineVersion: Optional[String]
    ChangeType: Optional[ChangeType]


ParametersList = List[Parameter]


class CacheParameterGroupDetails(TypedDict, total=False):
    """Represents the output of a ``DescribeCacheParameters`` operation."""

    Marker: Optional[String]
    Parameters: Optional[ParametersList]
    CacheNodeTypeSpecificParameters: Optional[CacheNodeTypeSpecificParametersList]


CacheParameterGroupList = List[CacheParameterGroup]


class CacheParameterGroupNameMessage(TypedDict, total=False):
    """Represents the output of one of the following operations:

    -  ``ModifyCacheParameterGroup``

    -  ``ResetCacheParameterGroup``
    """

    CacheParameterGroupName: Optional[String]


class CacheParameterGroupsMessage(TypedDict, total=False):
    """Represents the output of a ``DescribeCacheParameterGroups`` operation."""

    Marker: Optional[String]
    CacheParameterGroups: Optional[CacheParameterGroupList]


CacheSecurityGroups = List[CacheSecurityGroup]


class CacheSecurityGroupMessage(TypedDict, total=False):
    """Represents the output of a ``DescribeCacheSecurityGroups`` operation."""

    Marker: Optional[String]
    CacheSecurityGroups: Optional[CacheSecurityGroups]


CacheSecurityGroupNameList = List[String]


class SubnetOutpost(TypedDict, total=False):
    """The ID of the outpost subnet."""

    SubnetOutpostArn: Optional[String]


class Subnet(TypedDict, total=False):
    """Represents the subnet associated with a cluster. This parameter refers
    to subnets defined in Amazon Virtual Private Cloud (Amazon VPC) and used
    with ElastiCache.
    """

    SubnetIdentifier: Optional[String]
    SubnetAvailabilityZone: Optional[AvailabilityZone]
    SubnetOutpost: Optional[SubnetOutpost]


SubnetList = List[Subnet]


class CacheSubnetGroup(TypedDict, total=False):
    """Represents the output of one of the following operations:

    -  ``CreateCacheSubnetGroup``

    -  ``ModifyCacheSubnetGroup``
    """

    CacheSubnetGroupName: Optional[String]
    CacheSubnetGroupDescription: Optional[String]
    VpcId: Optional[String]
    Subnets: Optional[SubnetList]
    ARN: Optional[String]


CacheSubnetGroups = List[CacheSubnetGroup]


class CacheSubnetGroupMessage(TypedDict, total=False):
    """Represents the output of a ``DescribeCacheSubnetGroups`` operation."""

    Marker: Optional[String]
    CacheSubnetGroups: Optional[CacheSubnetGroups]


ClusterIdList = List[String]


class CompleteMigrationMessage(ServiceRequest):
    ReplicationGroupId: String
    Force: Optional[Boolean]


UserGroupIdList = List[UserGroupId]
ReplicationGroupOutpostArnList = List[String]


class NodeGroupMember(TypedDict, total=False):
    """Represents a single node within a node group (shard)."""

    CacheClusterId: Optional[String]
    CacheNodeId: Optional[String]
    ReadEndpoint: Optional[Endpoint]
    PreferredAvailabilityZone: Optional[String]
    PreferredOutpostArn: Optional[String]
    CurrentRole: Optional[String]


NodeGroupMemberList = List[NodeGroupMember]


class NodeGroup(TypedDict, total=False):
    """Represents a collection of cache nodes in a replication group. One node
    in the node group is the read/write primary node. All the other nodes
    are read-only Replica nodes.
    """

    NodeGroupId: Optional[String]
    Status: Optional[String]
    PrimaryEndpoint: Optional[Endpoint]
    ReaderEndpoint: Optional[Endpoint]
    Slots: Optional[String]
    NodeGroupMembers: Optional[NodeGroupMemberList]


NodeGroupList = List[NodeGroup]


class UserGroupsUpdateStatus(TypedDict, total=False):
    """The status of the user group update."""

    UserGroupIdsToAdd: Optional[UserGroupIdList]
    UserGroupIdsToRemove: Optional[UserGroupIdList]


class SlotMigration(TypedDict, total=False):
    """Represents the progress of an online resharding operation."""

    ProgressPercentage: Optional[Double]


class ReshardingStatus(TypedDict, total=False):
    """The status of an online resharding operation."""

    SlotMigration: Optional[SlotMigration]


class ReplicationGroupPendingModifiedValues(TypedDict, total=False):
    """The settings to be applied to the Redis replication group, either
    immediately or during the next maintenance window.
    """

    PrimaryClusterId: Optional[String]
    AutomaticFailoverStatus: Optional[PendingAutomaticFailoverStatus]
    Resharding: Optional[ReshardingStatus]
    AuthTokenStatus: Optional[AuthTokenUpdateStatus]
    UserGroups: Optional[UserGroupsUpdateStatus]
    LogDeliveryConfigurations: Optional[PendingLogDeliveryConfigurationList]


class GlobalReplicationGroupInfo(TypedDict, total=False):
    """The name of the Global datastore and role of this replication group in
    the Global datastore.
    """

    GlobalReplicationGroupId: Optional[String]
    GlobalReplicationGroupMemberRole: Optional[String]


class ReplicationGroup(TypedDict, total=False):
    """Contains all of the attributes of a specific Redis replication group."""

    ReplicationGroupId: Optional[String]
    Description: Optional[String]
    GlobalReplicationGroupInfo: Optional[GlobalReplicationGroupInfo]
    Status: Optional[String]
    PendingModifiedValues: Optional[ReplicationGroupPendingModifiedValues]
    MemberClusters: Optional[ClusterIdList]
    NodeGroups: Optional[NodeGroupList]
    SnapshottingClusterId: Optional[String]
    AutomaticFailover: Optional[AutomaticFailoverStatus]
    MultiAZ: Optional[MultiAZStatus]
    ConfigurationEndpoint: Optional[Endpoint]
    SnapshotRetentionLimit: Optional[IntegerOptional]
    SnapshotWindow: Optional[String]
    ClusterEnabled: Optional[BooleanOptional]
    CacheNodeType: Optional[String]
    AuthTokenEnabled: Optional[BooleanOptional]
    AuthTokenLastModifiedDate: Optional[TStamp]
    TransitEncryptionEnabled: Optional[BooleanOptional]
    AtRestEncryptionEnabled: Optional[BooleanOptional]
    MemberClustersOutpostArns: Optional[ReplicationGroupOutpostArnList]
    KmsKeyId: Optional[String]
    ARN: Optional[String]
    UserGroupIds: Optional[UserGroupIdList]
    LogDeliveryConfigurations: Optional[LogDeliveryConfigurationList]
    ReplicationGroupCreateTime: Optional[TStamp]
    DataTiering: Optional[DataTieringStatus]


class CompleteMigrationResponse(TypedDict, total=False):
    ReplicationGroup: Optional[ReplicationGroup]


PreferredOutpostArnList = List[String]
PreferredAvailabilityZoneList = List[String]


class ConfigureShard(TypedDict, total=False):
    """Node group (shard) configuration options when adding or removing
    replicas. Each node group (shard) configuration has the following
    members: NodeGroupId, NewReplicaCount, and PreferredAvailabilityZones.
    """

    NodeGroupId: AllowedNodeGroupId
    NewReplicaCount: Integer
    PreferredAvailabilityZones: Optional[PreferredAvailabilityZoneList]
    PreferredOutpostArns: Optional[PreferredOutpostArnList]


class CopySnapshotMessage(ServiceRequest):
    """Represents the input of a ``CopySnapshotMessage`` operation."""

    SourceSnapshotName: String
    TargetSnapshotName: String
    TargetBucket: Optional[String]
    KmsKeyId: Optional[String]
    Tags: Optional[TagList]


OutpostArnsList = List[String]


class NodeGroupConfiguration(TypedDict, total=False):
    """Node group (shard) configuration options. Each node group (shard)
    configuration has the following: ``Slots``, ``PrimaryAvailabilityZone``,
    ``ReplicaAvailabilityZones``, ``ReplicaCount``.
    """

    NodeGroupId: Optional[AllowedNodeGroupId]
    Slots: Optional[String]
    ReplicaCount: Optional[IntegerOptional]
    PrimaryAvailabilityZone: Optional[String]
    ReplicaAvailabilityZones: Optional[AvailabilityZonesList]
    PrimaryOutpostArn: Optional[String]
    ReplicaOutpostArns: Optional[OutpostArnsList]


class NodeSnapshot(TypedDict, total=False):
    """Represents an individual cache node in a snapshot of a cluster."""

    CacheClusterId: Optional[String]
    NodeGroupId: Optional[String]
    CacheNodeId: Optional[String]
    NodeGroupConfiguration: Optional[NodeGroupConfiguration]
    CacheSize: Optional[String]
    CacheNodeCreateTime: Optional[TStamp]
    SnapshotCreateTime: Optional[TStamp]


NodeSnapshotList = List[NodeSnapshot]


class Snapshot(TypedDict, total=False):
    """Represents a copy of an entire Redis cluster as of the time when the
    snapshot was taken.
    """

    SnapshotName: Optional[String]
    ReplicationGroupId: Optional[String]
    ReplicationGroupDescription: Optional[String]
    CacheClusterId: Optional[String]
    SnapshotStatus: Optional[String]
    SnapshotSource: Optional[String]
    CacheNodeType: Optional[String]
    Engine: Optional[String]
    EngineVersion: Optional[String]
    NumCacheNodes: Optional[IntegerOptional]
    PreferredAvailabilityZone: Optional[String]
    PreferredOutpostArn: Optional[String]
    CacheClusterCreateTime: Optional[TStamp]
    PreferredMaintenanceWindow: Optional[String]
    TopicArn: Optional[String]
    Port: Optional[IntegerOptional]
    CacheParameterGroupName: Optional[String]
    CacheSubnetGroupName: Optional[String]
    VpcId: Optional[String]
    AutoMinorVersionUpgrade: Optional[Boolean]
    SnapshotRetentionLimit: Optional[IntegerOptional]
    SnapshotWindow: Optional[String]
    NumNodeGroups: Optional[IntegerOptional]
    AutomaticFailover: Optional[AutomaticFailoverStatus]
    NodeSnapshots: Optional[NodeSnapshotList]
    KmsKeyId: Optional[String]
    ARN: Optional[String]
    DataTiering: Optional[DataTieringStatus]


class CopySnapshotResult(TypedDict, total=False):
    Snapshot: Optional[Snapshot]


class LogDeliveryConfigurationRequest(TypedDict, total=False):
    """Specifies the destination, format and type of the logs."""

    LogType: Optional[LogType]
    DestinationType: Optional[DestinationType]
    DestinationDetails: Optional[DestinationDetails]
    LogFormat: Optional[LogFormat]
    Enabled: Optional[BooleanOptional]


LogDeliveryConfigurationRequestList = List[LogDeliveryConfigurationRequest]
SnapshotArnsList = List[String]
SecurityGroupIdsList = List[String]


class CreateCacheClusterMessage(ServiceRequest):
    """Represents the input of a CreateCacheCluster operation."""

    CacheClusterId: String
    ReplicationGroupId: Optional[String]
    AZMode: Optional[AZMode]
    PreferredAvailabilityZone: Optional[String]
    PreferredAvailabilityZones: Optional[PreferredAvailabilityZoneList]
    NumCacheNodes: Optional[IntegerOptional]
    CacheNodeType: Optional[String]
    Engine: Optional[String]
    EngineVersion: Optional[String]
    CacheParameterGroupName: Optional[String]
    CacheSubnetGroupName: Optional[String]
    CacheSecurityGroupNames: Optional[CacheSecurityGroupNameList]
    SecurityGroupIds: Optional[SecurityGroupIdsList]
    Tags: Optional[TagList]
    SnapshotArns: Optional[SnapshotArnsList]
    SnapshotName: Optional[String]
    PreferredMaintenanceWindow: Optional[String]
    Port: Optional[IntegerOptional]
    NotificationTopicArn: Optional[String]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    SnapshotRetentionLimit: Optional[IntegerOptional]
    SnapshotWindow: Optional[String]
    AuthToken: Optional[String]
    OutpostMode: Optional[OutpostMode]
    PreferredOutpostArn: Optional[String]
    PreferredOutpostArns: Optional[PreferredOutpostArnList]
    LogDeliveryConfigurations: Optional[LogDeliveryConfigurationRequestList]


class CreateCacheClusterResult(TypedDict, total=False):
    CacheCluster: Optional[CacheCluster]


class CreateCacheParameterGroupMessage(ServiceRequest):
    """Represents the input of a ``CreateCacheParameterGroup`` operation."""

    CacheParameterGroupName: String
    CacheParameterGroupFamily: String
    Description: String
    Tags: Optional[TagList]


class CreateCacheParameterGroupResult(TypedDict, total=False):
    CacheParameterGroup: Optional[CacheParameterGroup]


class CreateCacheSecurityGroupMessage(ServiceRequest):
    """Represents the input of a ``CreateCacheSecurityGroup`` operation."""

    CacheSecurityGroupName: String
    Description: String
    Tags: Optional[TagList]


class CreateCacheSecurityGroupResult(TypedDict, total=False):
    CacheSecurityGroup: Optional[CacheSecurityGroup]


SubnetIdentifierList = List[String]


class CreateCacheSubnetGroupMessage(ServiceRequest):
    """Represents the input of a ``CreateCacheSubnetGroup`` operation."""

    CacheSubnetGroupName: String
    CacheSubnetGroupDescription: String
    SubnetIds: SubnetIdentifierList
    Tags: Optional[TagList]


class CreateCacheSubnetGroupResult(TypedDict, total=False):
    CacheSubnetGroup: Optional[CacheSubnetGroup]


class CreateGlobalReplicationGroupMessage(ServiceRequest):
    GlobalReplicationGroupIdSuffix: String
    GlobalReplicationGroupDescription: Optional[String]
    PrimaryReplicationGroupId: String


class GlobalNodeGroup(TypedDict, total=False):
    """Indicates the slot configuration and global identifier for a slice
    group.
    """

    GlobalNodeGroupId: Optional[String]
    Slots: Optional[String]


GlobalNodeGroupList = List[GlobalNodeGroup]


class GlobalReplicationGroupMember(TypedDict, total=False):
    """A member of a Global datastore. It contains the Replication Group Id,
    the Amazon region and the role of the replication group.
    """

    ReplicationGroupId: Optional[String]
    ReplicationGroupRegion: Optional[String]
    Role: Optional[String]
    AutomaticFailover: Optional[AutomaticFailoverStatus]
    Status: Optional[String]


GlobalReplicationGroupMemberList = List[GlobalReplicationGroupMember]


class GlobalReplicationGroup(TypedDict, total=False):
    """Consists of a primary cluster that accepts writes and an associated
    secondary cluster that resides in a different Amazon region. The
    secondary cluster accepts only reads. The primary cluster automatically
    replicates updates to the secondary cluster.

    -  The **GlobalReplicationGroupIdSuffix** represents the name of the
       Global datastore, which is what you use to associate a secondary
       cluster.
    """

    GlobalReplicationGroupId: Optional[String]
    GlobalReplicationGroupDescription: Optional[String]
    Status: Optional[String]
    CacheNodeType: Optional[String]
    Engine: Optional[String]
    EngineVersion: Optional[String]
    Members: Optional[GlobalReplicationGroupMemberList]
    ClusterEnabled: Optional[BooleanOptional]
    GlobalNodeGroups: Optional[GlobalNodeGroupList]
    AuthTokenEnabled: Optional[BooleanOptional]
    TransitEncryptionEnabled: Optional[BooleanOptional]
    AtRestEncryptionEnabled: Optional[BooleanOptional]
    ARN: Optional[String]


class CreateGlobalReplicationGroupResult(TypedDict, total=False):
    GlobalReplicationGroup: Optional[GlobalReplicationGroup]


UserGroupIdListInput = List[UserGroupId]
NodeGroupConfigurationList = List[NodeGroupConfiguration]


class CreateReplicationGroupMessage(ServiceRequest):
    """Represents the input of a ``CreateReplicationGroup`` operation."""

    ReplicationGroupId: String
    ReplicationGroupDescription: String
    GlobalReplicationGroupId: Optional[String]
    PrimaryClusterId: Optional[String]
    AutomaticFailoverEnabled: Optional[BooleanOptional]
    MultiAZEnabled: Optional[BooleanOptional]
    NumCacheClusters: Optional[IntegerOptional]
    PreferredCacheClusterAZs: Optional[AvailabilityZonesList]
    NumNodeGroups: Optional[IntegerOptional]
    ReplicasPerNodeGroup: Optional[IntegerOptional]
    NodeGroupConfiguration: Optional[NodeGroupConfigurationList]
    CacheNodeType: Optional[String]
    Engine: Optional[String]
    EngineVersion: Optional[String]
    CacheParameterGroupName: Optional[String]
    CacheSubnetGroupName: Optional[String]
    CacheSecurityGroupNames: Optional[CacheSecurityGroupNameList]
    SecurityGroupIds: Optional[SecurityGroupIdsList]
    Tags: Optional[TagList]
    SnapshotArns: Optional[SnapshotArnsList]
    SnapshotName: Optional[String]
    PreferredMaintenanceWindow: Optional[String]
    Port: Optional[IntegerOptional]
    NotificationTopicArn: Optional[String]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    SnapshotRetentionLimit: Optional[IntegerOptional]
    SnapshotWindow: Optional[String]
    AuthToken: Optional[String]
    TransitEncryptionEnabled: Optional[BooleanOptional]
    AtRestEncryptionEnabled: Optional[BooleanOptional]
    KmsKeyId: Optional[String]
    UserGroupIds: Optional[UserGroupIdListInput]
    LogDeliveryConfigurations: Optional[LogDeliveryConfigurationRequestList]
    DataTieringEnabled: Optional[BooleanOptional]


class CreateReplicationGroupResult(TypedDict, total=False):
    ReplicationGroup: Optional[ReplicationGroup]


class CreateSnapshotMessage(ServiceRequest):
    """Represents the input of a ``CreateSnapshot`` operation."""

    ReplicationGroupId: Optional[String]
    CacheClusterId: Optional[String]
    SnapshotName: String
    KmsKeyId: Optional[String]
    Tags: Optional[TagList]


class CreateSnapshotResult(TypedDict, total=False):
    Snapshot: Optional[Snapshot]


UserIdListInput = List[UserId]


class CreateUserGroupMessage(ServiceRequest):
    UserGroupId: String
    Engine: EngineType
    UserIds: Optional[UserIdListInput]
    Tags: Optional[TagList]


PasswordListInput = List[String]


class CreateUserMessage(ServiceRequest):
    UserId: UserId
    UserName: UserName
    Engine: EngineType
    Passwords: Optional[PasswordListInput]
    AccessString: AccessString
    NoPasswordRequired: Optional[BooleanOptional]
    Tags: Optional[TagList]


class CustomerNodeEndpoint(TypedDict, total=False):
    """The endpoint from which data should be migrated."""

    Address: Optional[String]
    Port: Optional[IntegerOptional]


CustomerNodeEndpointList = List[CustomerNodeEndpoint]
GlobalNodeGroupIdList = List[String]


class DecreaseNodeGroupsInGlobalReplicationGroupMessage(ServiceRequest):
    GlobalReplicationGroupId: String
    NodeGroupCount: Integer
    GlobalNodeGroupsToRemove: Optional[GlobalNodeGroupIdList]
    GlobalNodeGroupsToRetain: Optional[GlobalNodeGroupIdList]
    ApplyImmediately: Boolean


class DecreaseNodeGroupsInGlobalReplicationGroupResult(TypedDict, total=False):
    GlobalReplicationGroup: Optional[GlobalReplicationGroup]


RemoveReplicasList = List[String]
ReplicaConfigurationList = List[ConfigureShard]


class DecreaseReplicaCountMessage(ServiceRequest):
    ReplicationGroupId: String
    NewReplicaCount: Optional[IntegerOptional]
    ReplicaConfiguration: Optional[ReplicaConfigurationList]
    ReplicasToRemove: Optional[RemoveReplicasList]
    ApplyImmediately: Boolean


class DecreaseReplicaCountResult(TypedDict, total=False):
    ReplicationGroup: Optional[ReplicationGroup]


class DeleteCacheClusterMessage(ServiceRequest):
    """Represents the input of a ``DeleteCacheCluster`` operation."""

    CacheClusterId: String
    FinalSnapshotIdentifier: Optional[String]


class DeleteCacheClusterResult(TypedDict, total=False):
    CacheCluster: Optional[CacheCluster]


class DeleteCacheParameterGroupMessage(ServiceRequest):
    """Represents the input of a ``DeleteCacheParameterGroup`` operation."""

    CacheParameterGroupName: String


class DeleteCacheSecurityGroupMessage(ServiceRequest):
    """Represents the input of a ``DeleteCacheSecurityGroup`` operation."""

    CacheSecurityGroupName: String


class DeleteCacheSubnetGroupMessage(ServiceRequest):
    """Represents the input of a ``DeleteCacheSubnetGroup`` operation."""

    CacheSubnetGroupName: String


class DeleteGlobalReplicationGroupMessage(ServiceRequest):
    GlobalReplicationGroupId: String
    RetainPrimaryReplicationGroup: Boolean


class DeleteGlobalReplicationGroupResult(TypedDict, total=False):
    GlobalReplicationGroup: Optional[GlobalReplicationGroup]


class DeleteReplicationGroupMessage(ServiceRequest):
    """Represents the input of a ``DeleteReplicationGroup`` operation."""

    ReplicationGroupId: String
    RetainPrimaryCluster: Optional[BooleanOptional]
    FinalSnapshotIdentifier: Optional[String]


class DeleteReplicationGroupResult(TypedDict, total=False):
    ReplicationGroup: Optional[ReplicationGroup]


class DeleteSnapshotMessage(ServiceRequest):
    """Represents the input of a ``DeleteSnapshot`` operation."""

    SnapshotName: String


class DeleteSnapshotResult(TypedDict, total=False):
    Snapshot: Optional[Snapshot]


class DeleteUserGroupMessage(ServiceRequest):
    UserGroupId: String


class DeleteUserMessage(ServiceRequest):
    UserId: UserId


class DescribeCacheClustersMessage(ServiceRequest):
    """Represents the input of a ``DescribeCacheClusters`` operation."""

    CacheClusterId: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]
    ShowCacheNodeInfo: Optional[BooleanOptional]
    ShowCacheClustersNotInReplicationGroups: Optional[BooleanOptional]


class DescribeCacheEngineVersionsMessage(ServiceRequest):
    """Represents the input of a ``DescribeCacheEngineVersions`` operation."""

    Engine: Optional[String]
    EngineVersion: Optional[String]
    CacheParameterGroupFamily: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]
    DefaultOnly: Optional[Boolean]


class DescribeCacheParameterGroupsMessage(ServiceRequest):
    """Represents the input of a ``DescribeCacheParameterGroups`` operation."""

    CacheParameterGroupName: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeCacheParametersMessage(ServiceRequest):
    """Represents the input of a ``DescribeCacheParameters`` operation."""

    CacheParameterGroupName: String
    Source: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeCacheSecurityGroupsMessage(ServiceRequest):
    """Represents the input of a ``DescribeCacheSecurityGroups`` operation."""

    CacheSecurityGroupName: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeCacheSubnetGroupsMessage(ServiceRequest):
    """Represents the input of a ``DescribeCacheSubnetGroups`` operation."""

    CacheSubnetGroupName: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeEngineDefaultParametersMessage(ServiceRequest):
    """Represents the input of a ``DescribeEngineDefaultParameters`` operation."""

    CacheParameterGroupFamily: String
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class EngineDefaults(TypedDict, total=False):
    """Represents the output of a ``DescribeEngineDefaultParameters``
    operation.
    """

    CacheParameterGroupFamily: Optional[String]
    Marker: Optional[String]
    Parameters: Optional[ParametersList]
    CacheNodeTypeSpecificParameters: Optional[CacheNodeTypeSpecificParametersList]


class DescribeEngineDefaultParametersResult(TypedDict, total=False):
    EngineDefaults: Optional[EngineDefaults]


class DescribeEventsMessage(ServiceRequest):
    """Represents the input of a ``DescribeEvents`` operation."""

    SourceIdentifier: Optional[String]
    SourceType: Optional[SourceType]
    StartTime: Optional[TStamp]
    EndTime: Optional[TStamp]
    Duration: Optional[IntegerOptional]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeGlobalReplicationGroupsMessage(ServiceRequest):
    GlobalReplicationGroupId: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]
    ShowMemberInfo: Optional[BooleanOptional]


GlobalReplicationGroupList = List[GlobalReplicationGroup]


class DescribeGlobalReplicationGroupsResult(TypedDict, total=False):
    Marker: Optional[String]
    GlobalReplicationGroups: Optional[GlobalReplicationGroupList]


class DescribeReplicationGroupsMessage(ServiceRequest):
    """Represents the input of a ``DescribeReplicationGroups`` operation."""

    ReplicationGroupId: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeReservedCacheNodesMessage(ServiceRequest):
    """Represents the input of a ``DescribeReservedCacheNodes`` operation."""

    ReservedCacheNodeId: Optional[String]
    ReservedCacheNodesOfferingId: Optional[String]
    CacheNodeType: Optional[String]
    Duration: Optional[String]
    ProductDescription: Optional[String]
    OfferingType: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeReservedCacheNodesOfferingsMessage(ServiceRequest):
    """Represents the input of a ``DescribeReservedCacheNodesOfferings``
    operation.
    """

    ReservedCacheNodesOfferingId: Optional[String]
    CacheNodeType: Optional[String]
    Duration: Optional[String]
    ProductDescription: Optional[String]
    OfferingType: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


ServiceUpdateStatusList = List[ServiceUpdateStatus]


class DescribeServiceUpdatesMessage(ServiceRequest):
    ServiceUpdateName: Optional[String]
    ServiceUpdateStatus: Optional[ServiceUpdateStatusList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


SnapshotList = List[Snapshot]


class DescribeSnapshotsListMessage(TypedDict, total=False):
    """Represents the output of a ``DescribeSnapshots`` operation."""

    Marker: Optional[String]
    Snapshots: Optional[SnapshotList]


class DescribeSnapshotsMessage(ServiceRequest):
    """Represents the input of a ``DescribeSnapshotsMessage`` operation."""

    ReplicationGroupId: Optional[String]
    CacheClusterId: Optional[String]
    SnapshotName: Optional[String]
    SnapshotSource: Optional[String]
    Marker: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    ShowNodeGroupConfig: Optional[BooleanOptional]


UpdateActionStatusList = List[UpdateActionStatus]


class TimeRangeFilter(TypedDict, total=False):
    """Filters update actions from the service updates that are in available
    status during the time range.
    """

    StartTime: Optional[TStamp]
    EndTime: Optional[TStamp]


class DescribeUpdateActionsMessage(ServiceRequest):
    ServiceUpdateName: Optional[String]
    ReplicationGroupIds: Optional[ReplicationGroupIdList]
    CacheClusterIds: Optional[CacheClusterIdList]
    Engine: Optional[String]
    ServiceUpdateStatus: Optional[ServiceUpdateStatusList]
    ServiceUpdateTimeRange: Optional[TimeRangeFilter]
    UpdateActionStatus: Optional[UpdateActionStatusList]
    ShowNodeLevelUpdateStatus: Optional[BooleanOptional]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class DescribeUserGroupsMessage(ServiceRequest):
    UserGroupId: Optional[String]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


UGReplicationGroupIdList = List[String]
UserIdList = List[UserId]


class UserGroupPendingChanges(TypedDict, total=False):
    """Returns the updates being applied to the user group."""

    UserIdsToRemove: Optional[UserIdList]
    UserIdsToAdd: Optional[UserIdList]


class UserGroup(TypedDict, total=False):
    UserGroupId: Optional[String]
    Status: Optional[String]
    Engine: Optional[EngineType]
    UserIds: Optional[UserIdList]
    MinimumEngineVersion: Optional[String]
    PendingChanges: Optional[UserGroupPendingChanges]
    ReplicationGroups: Optional[UGReplicationGroupIdList]
    ARN: Optional[String]


UserGroupList = List[UserGroup]


class DescribeUserGroupsResult(TypedDict, total=False):
    UserGroups: Optional[UserGroupList]
    Marker: Optional[String]


FilterValueList = List[FilterValue]


class Filter(TypedDict, total=False):
    """Used to streamline results of a search based on the property being
    filtered.
    """

    Name: FilterName
    Values: FilterValueList


FilterList = List[Filter]


class DescribeUsersMessage(ServiceRequest):
    Engine: Optional[EngineType]
    UserId: Optional[UserId]
    Filters: Optional[FilterList]
    MaxRecords: Optional[IntegerOptional]
    Marker: Optional[String]


class User(TypedDict, total=False):
    UserId: Optional[String]
    UserName: Optional[String]
    Status: Optional[String]
    Engine: Optional[EngineType]
    MinimumEngineVersion: Optional[String]
    AccessString: Optional[String]
    UserGroupIds: Optional[UserGroupIdList]
    Authentication: Optional[Authentication]
    ARN: Optional[String]


UserList = List[User]


class DescribeUsersResult(TypedDict, total=False):
    Users: Optional[UserList]
    Marker: Optional[String]


class DisassociateGlobalReplicationGroupMessage(ServiceRequest):
    GlobalReplicationGroupId: String
    ReplicationGroupId: String
    ReplicationGroupRegion: String


class DisassociateGlobalReplicationGroupResult(TypedDict, total=False):
    GlobalReplicationGroup: Optional[GlobalReplicationGroup]


class Event(TypedDict, total=False):
    """Represents a single occurrence of something interesting within the
    system. Some examples of events are creating a cluster, adding or
    removing a cache node, or rebooting a node.
    """

    SourceIdentifier: Optional[String]
    SourceType: Optional[SourceType]
    Message: Optional[String]
    Date: Optional[TStamp]


EventList = List[Event]


class EventsMessage(TypedDict, total=False):
    """Represents the output of a ``DescribeEvents`` operation."""

    Marker: Optional[String]
    Events: Optional[EventList]


class FailoverGlobalReplicationGroupMessage(ServiceRequest):
    GlobalReplicationGroupId: String
    PrimaryRegion: String
    PrimaryReplicationGroupId: String


class FailoverGlobalReplicationGroupResult(TypedDict, total=False):
    GlobalReplicationGroup: Optional[GlobalReplicationGroup]


class ReshardingConfiguration(TypedDict, total=False):
    """A list of ``PreferredAvailabilityZones`` objects that specifies the
    configuration of a node group in the resharded cluster.
    """

    NodeGroupId: Optional[AllowedNodeGroupId]
    PreferredAvailabilityZones: Optional[AvailabilityZonesList]


ReshardingConfigurationList = List[ReshardingConfiguration]


class RegionalConfiguration(TypedDict, total=False):
    """A list of the replication groups"""

    ReplicationGroupId: String
    ReplicationGroupRegion: String
    ReshardingConfiguration: ReshardingConfigurationList


RegionalConfigurationList = List[RegionalConfiguration]


class IncreaseNodeGroupsInGlobalReplicationGroupMessage(ServiceRequest):
    GlobalReplicationGroupId: String
    NodeGroupCount: Integer
    RegionalConfigurations: Optional[RegionalConfigurationList]
    ApplyImmediately: Boolean


class IncreaseNodeGroupsInGlobalReplicationGroupResult(TypedDict, total=False):
    GlobalReplicationGroup: Optional[GlobalReplicationGroup]


class IncreaseReplicaCountMessage(ServiceRequest):
    ReplicationGroupId: String
    NewReplicaCount: Optional[IntegerOptional]
    ReplicaConfiguration: Optional[ReplicaConfigurationList]
    ApplyImmediately: Boolean


class IncreaseReplicaCountResult(TypedDict, total=False):
    ReplicationGroup: Optional[ReplicationGroup]


KeyList = List[String]


class ListAllowedNodeTypeModificationsMessage(ServiceRequest):
    """The input parameters for the ``ListAllowedNodeTypeModifications``
    operation.
    """

    CacheClusterId: Optional[String]
    ReplicationGroupId: Optional[String]


class ListTagsForResourceMessage(ServiceRequest):
    """The input parameters for the ``ListTagsForResource`` operation."""

    ResourceName: String


class ModifyCacheClusterMessage(ServiceRequest):
    """Represents the input of a ``ModifyCacheCluster`` operation."""

    CacheClusterId: String
    NumCacheNodes: Optional[IntegerOptional]
    CacheNodeIdsToRemove: Optional[CacheNodeIdsList]
    AZMode: Optional[AZMode]
    NewAvailabilityZones: Optional[PreferredAvailabilityZoneList]
    CacheSecurityGroupNames: Optional[CacheSecurityGroupNameList]
    SecurityGroupIds: Optional[SecurityGroupIdsList]
    PreferredMaintenanceWindow: Optional[String]
    NotificationTopicArn: Optional[String]
    CacheParameterGroupName: Optional[String]
    NotificationTopicStatus: Optional[String]
    ApplyImmediately: Optional[Boolean]
    EngineVersion: Optional[String]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    SnapshotRetentionLimit: Optional[IntegerOptional]
    SnapshotWindow: Optional[String]
    CacheNodeType: Optional[String]
    AuthToken: Optional[String]
    AuthTokenUpdateStrategy: Optional[AuthTokenUpdateStrategyType]
    LogDeliveryConfigurations: Optional[LogDeliveryConfigurationRequestList]


class ModifyCacheClusterResult(TypedDict, total=False):
    CacheCluster: Optional[CacheCluster]


class ParameterNameValue(TypedDict, total=False):
    """Describes a name-value pair that is used to update the value of a
    parameter.
    """

    ParameterName: Optional[String]
    ParameterValue: Optional[String]


ParameterNameValueList = List[ParameterNameValue]


class ModifyCacheParameterGroupMessage(ServiceRequest):
    """Represents the input of a ``ModifyCacheParameterGroup`` operation."""

    CacheParameterGroupName: String
    ParameterNameValues: ParameterNameValueList


class ModifyCacheSubnetGroupMessage(ServiceRequest):
    """Represents the input of a ``ModifyCacheSubnetGroup`` operation."""

    CacheSubnetGroupName: String
    CacheSubnetGroupDescription: Optional[String]
    SubnetIds: Optional[SubnetIdentifierList]


class ModifyCacheSubnetGroupResult(TypedDict, total=False):
    CacheSubnetGroup: Optional[CacheSubnetGroup]


class ModifyGlobalReplicationGroupMessage(ServiceRequest):
    GlobalReplicationGroupId: String
    ApplyImmediately: Boolean
    CacheNodeType: Optional[String]
    EngineVersion: Optional[String]
    CacheParameterGroupName: Optional[String]
    GlobalReplicationGroupDescription: Optional[String]
    AutomaticFailoverEnabled: Optional[BooleanOptional]


class ModifyGlobalReplicationGroupResult(TypedDict, total=False):
    GlobalReplicationGroup: Optional[GlobalReplicationGroup]


class ModifyReplicationGroupMessage(ServiceRequest):
    """Represents the input of a ``ModifyReplicationGroups`` operation."""

    ReplicationGroupId: String
    ReplicationGroupDescription: Optional[String]
    PrimaryClusterId: Optional[String]
    SnapshottingClusterId: Optional[String]
    AutomaticFailoverEnabled: Optional[BooleanOptional]
    MultiAZEnabled: Optional[BooleanOptional]
    NodeGroupId: Optional[String]
    CacheSecurityGroupNames: Optional[CacheSecurityGroupNameList]
    SecurityGroupIds: Optional[SecurityGroupIdsList]
    PreferredMaintenanceWindow: Optional[String]
    NotificationTopicArn: Optional[String]
    CacheParameterGroupName: Optional[String]
    NotificationTopicStatus: Optional[String]
    ApplyImmediately: Optional[Boolean]
    EngineVersion: Optional[String]
    AutoMinorVersionUpgrade: Optional[BooleanOptional]
    SnapshotRetentionLimit: Optional[IntegerOptional]
    SnapshotWindow: Optional[String]
    CacheNodeType: Optional[String]
    AuthToken: Optional[String]
    AuthTokenUpdateStrategy: Optional[AuthTokenUpdateStrategyType]
    UserGroupIdsToAdd: Optional[UserGroupIdList]
    UserGroupIdsToRemove: Optional[UserGroupIdList]
    RemoveUserGroups: Optional[BooleanOptional]
    LogDeliveryConfigurations: Optional[LogDeliveryConfigurationRequestList]


class ModifyReplicationGroupResult(TypedDict, total=False):
    ReplicationGroup: Optional[ReplicationGroup]


NodeGroupsToRetainList = List[AllowedNodeGroupId]
NodeGroupsToRemoveList = List[AllowedNodeGroupId]


class ModifyReplicationGroupShardConfigurationMessage(ServiceRequest):
    """Represents the input for a ``ModifyReplicationGroupShardConfiguration``
    operation.
    """

    ReplicationGroupId: String
    NodeGroupCount: Integer
    ApplyImmediately: Boolean
    ReshardingConfiguration: Optional[ReshardingConfigurationList]
    NodeGroupsToRemove: Optional[NodeGroupsToRemoveList]
    NodeGroupsToRetain: Optional[NodeGroupsToRetainList]


class ModifyReplicationGroupShardConfigurationResult(TypedDict, total=False):
    ReplicationGroup: Optional[ReplicationGroup]


class ModifyUserGroupMessage(ServiceRequest):
    UserGroupId: String
    UserIdsToAdd: Optional[UserIdListInput]
    UserIdsToRemove: Optional[UserIdListInput]


class ModifyUserMessage(ServiceRequest):
    UserId: UserId
    AccessString: Optional[AccessString]
    AppendAccessString: Optional[AccessString]
    Passwords: Optional[PasswordListInput]
    NoPasswordRequired: Optional[BooleanOptional]


class NodeGroupMemberUpdateStatus(TypedDict, total=False):
    """The status of the service update on the node group member"""

    CacheClusterId: Optional[String]
    CacheNodeId: Optional[String]
    NodeUpdateStatus: Optional[NodeUpdateStatus]
    NodeDeletionDate: Optional[TStamp]
    NodeUpdateStartDate: Optional[TStamp]
    NodeUpdateEndDate: Optional[TStamp]
    NodeUpdateInitiatedBy: Optional[NodeUpdateInitiatedBy]
    NodeUpdateInitiatedDate: Optional[TStamp]
    NodeUpdateStatusModifiedDate: Optional[TStamp]


NodeGroupMemberUpdateStatusList = List[NodeGroupMemberUpdateStatus]


class NodeGroupUpdateStatus(TypedDict, total=False):
    """The status of the service update on the node group"""

    NodeGroupId: Optional[String]
    NodeGroupMemberUpdateStatus: Optional[NodeGroupMemberUpdateStatusList]


NodeGroupUpdateStatusList = List[NodeGroupUpdateStatus]


class ProcessedUpdateAction(TypedDict, total=False):
    """Update action that has been processed for the corresponding apply/stop
    request
    """

    ReplicationGroupId: Optional[String]
    CacheClusterId: Optional[String]
    ServiceUpdateName: Optional[String]
    UpdateActionStatus: Optional[UpdateActionStatus]


ProcessedUpdateActionList = List[ProcessedUpdateAction]


class PurchaseReservedCacheNodesOfferingMessage(ServiceRequest):
    """Represents the input of a ``PurchaseReservedCacheNodesOffering``
    operation.
    """

    ReservedCacheNodesOfferingId: String
    ReservedCacheNodeId: Optional[String]
    CacheNodeCount: Optional[IntegerOptional]
    Tags: Optional[TagList]


class RecurringCharge(TypedDict, total=False):
    """Contains the specific price and frequency of a recurring charges for a
    reserved cache node, or for a reserved cache node offering.
    """

    RecurringChargeAmount: Optional[Double]
    RecurringChargeFrequency: Optional[String]


RecurringChargeList = List[RecurringCharge]


class ReservedCacheNode(TypedDict, total=False):
    """Represents the output of a ``PurchaseReservedCacheNodesOffering``
    operation.
    """

    ReservedCacheNodeId: Optional[String]
    ReservedCacheNodesOfferingId: Optional[String]
    CacheNodeType: Optional[String]
    StartTime: Optional[TStamp]
    Duration: Optional[Integer]
    FixedPrice: Optional[Double]
    UsagePrice: Optional[Double]
    CacheNodeCount: Optional[Integer]
    ProductDescription: Optional[String]
    OfferingType: Optional[String]
    State: Optional[String]
    RecurringCharges: Optional[RecurringChargeList]
    ReservationARN: Optional[String]


class PurchaseReservedCacheNodesOfferingResult(TypedDict, total=False):
    ReservedCacheNode: Optional[ReservedCacheNode]


class RebalanceSlotsInGlobalReplicationGroupMessage(ServiceRequest):
    GlobalReplicationGroupId: String
    ApplyImmediately: Boolean


class RebalanceSlotsInGlobalReplicationGroupResult(TypedDict, total=False):
    GlobalReplicationGroup: Optional[GlobalReplicationGroup]


class RebootCacheClusterMessage(ServiceRequest):
    """Represents the input of a ``RebootCacheCluster`` operation."""

    CacheClusterId: String
    CacheNodeIdsToReboot: CacheNodeIdsList


class RebootCacheClusterResult(TypedDict, total=False):
    CacheCluster: Optional[CacheCluster]


class RemoveTagsFromResourceMessage(ServiceRequest):
    """Represents the input of a ``RemoveTagsFromResource`` operation."""

    ResourceName: String
    TagKeys: KeyList


ReplicationGroupList = List[ReplicationGroup]


class ReplicationGroupMessage(TypedDict, total=False):
    """Represents the output of a ``DescribeReplicationGroups`` operation."""

    Marker: Optional[String]
    ReplicationGroups: Optional[ReplicationGroupList]


ReservedCacheNodeList = List[ReservedCacheNode]


class ReservedCacheNodeMessage(TypedDict, total=False):
    """Represents the output of a ``DescribeReservedCacheNodes`` operation."""

    Marker: Optional[String]
    ReservedCacheNodes: Optional[ReservedCacheNodeList]


class ReservedCacheNodesOffering(TypedDict, total=False):
    """Describes all of the attributes of a reserved cache node offering."""

    ReservedCacheNodesOfferingId: Optional[String]
    CacheNodeType: Optional[String]
    Duration: Optional[Integer]
    FixedPrice: Optional[Double]
    UsagePrice: Optional[Double]
    ProductDescription: Optional[String]
    OfferingType: Optional[String]
    RecurringCharges: Optional[RecurringChargeList]


ReservedCacheNodesOfferingList = List[ReservedCacheNodesOffering]


class ReservedCacheNodesOfferingMessage(TypedDict, total=False):
    """Represents the output of a ``DescribeReservedCacheNodesOfferings``
    operation.
    """

    Marker: Optional[String]
    ReservedCacheNodesOfferings: Optional[ReservedCacheNodesOfferingList]


class ResetCacheParameterGroupMessage(ServiceRequest):
    """Represents the input of a ``ResetCacheParameterGroup`` operation."""

    CacheParameterGroupName: String
    ResetAllParameters: Optional[Boolean]
    ParameterNameValues: Optional[ParameterNameValueList]


class RevokeCacheSecurityGroupIngressMessage(ServiceRequest):
    """Represents the input of a ``RevokeCacheSecurityGroupIngress`` operation."""

    CacheSecurityGroupName: String
    EC2SecurityGroupName: String
    EC2SecurityGroupOwnerId: String


class RevokeCacheSecurityGroupIngressResult(TypedDict, total=False):
    CacheSecurityGroup: Optional[CacheSecurityGroup]


class ServiceUpdate(TypedDict, total=False):
    """An update that you can apply to your Redis clusters."""

    ServiceUpdateName: Optional[String]
    ServiceUpdateReleaseDate: Optional[TStamp]
    ServiceUpdateEndDate: Optional[TStamp]
    ServiceUpdateSeverity: Optional[ServiceUpdateSeverity]
    ServiceUpdateRecommendedApplyByDate: Optional[TStamp]
    ServiceUpdateStatus: Optional[ServiceUpdateStatus]
    ServiceUpdateDescription: Optional[String]
    ServiceUpdateType: Optional[ServiceUpdateType]
    Engine: Optional[String]
    EngineVersion: Optional[String]
    AutoUpdateAfterRecommendedApplyByDate: Optional[BooleanOptional]
    EstimatedUpdateTime: Optional[String]


ServiceUpdateList = List[ServiceUpdate]


class ServiceUpdatesMessage(TypedDict, total=False):
    Marker: Optional[String]
    ServiceUpdates: Optional[ServiceUpdateList]


class StartMigrationMessage(ServiceRequest):
    ReplicationGroupId: String
    CustomerNodeEndpointList: CustomerNodeEndpointList


class StartMigrationResponse(TypedDict, total=False):
    ReplicationGroup: Optional[ReplicationGroup]


class TagListMessage(TypedDict, total=False):
    """Represents the output from the ``AddTagsToResource``,
    ``ListTagsForResource``, and ``RemoveTagsFromResource`` operations.
    """

    TagList: Optional[TagList]


class TestFailoverMessage(ServiceRequest):
    ReplicationGroupId: String
    NodeGroupId: AllowedNodeGroupId


class TestFailoverResult(TypedDict, total=False):
    ReplicationGroup: Optional[ReplicationGroup]


class UnprocessedUpdateAction(TypedDict, total=False):
    """Update action that has failed to be processed for the corresponding
    apply/stop request
    """

    ReplicationGroupId: Optional[String]
    CacheClusterId: Optional[String]
    ServiceUpdateName: Optional[String]
    ErrorType: Optional[String]
    ErrorMessage: Optional[String]


UnprocessedUpdateActionList = List[UnprocessedUpdateAction]


class UpdateAction(TypedDict, total=False):
    """The status of the service update for a specific replication group"""

    ReplicationGroupId: Optional[String]
    CacheClusterId: Optional[String]
    ServiceUpdateName: Optional[String]
    ServiceUpdateReleaseDate: Optional[TStamp]
    ServiceUpdateSeverity: Optional[ServiceUpdateSeverity]
    ServiceUpdateStatus: Optional[ServiceUpdateStatus]
    ServiceUpdateRecommendedApplyByDate: Optional[TStamp]
    ServiceUpdateType: Optional[ServiceUpdateType]
    UpdateActionAvailableDate: Optional[TStamp]
    UpdateActionStatus: Optional[UpdateActionStatus]
    NodesUpdated: Optional[String]
    UpdateActionStatusModifiedDate: Optional[TStamp]
    SlaMet: Optional[SlaMet]
    NodeGroupUpdateStatus: Optional[NodeGroupUpdateStatusList]
    CacheNodeUpdateStatus: Optional[CacheNodeUpdateStatusList]
    EstimatedUpdateTime: Optional[String]
    Engine: Optional[String]


UpdateActionList = List[UpdateAction]


class UpdateActionResultsMessage(TypedDict, total=False):
    ProcessedUpdateActions: Optional[ProcessedUpdateActionList]
    UnprocessedUpdateActions: Optional[UnprocessedUpdateActionList]


class UpdateActionsMessage(TypedDict, total=False):
    Marker: Optional[String]
    UpdateActions: Optional[UpdateActionList]


class ElasticacheApi:

    service = "elasticache"
    version = "2015-02-02"

    @handler("AddTagsToResource")
    def add_tags_to_resource(
        self, context: RequestContext, resource_name: String, tags: TagList
    ) -> TagListMessage:
        """A tag is a key-value pair where the key and value are case-sensitive.
        You can use tags to categorize and track all your ElastiCache resources,
        with the exception of global replication group. When you add or remove
        tags on replication groups, those actions will be replicated to all
        nodes in the replication group. For more information, see
        `Resource-level
        permissions <http://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/IAM.ResourceLevelPermissions.html>`__.

        For example, you can use cost-allocation tags to your ElastiCache
        resources, Amazon generates a cost allocation report as a
        comma-separated value (CSV) file with your usage and costs aggregated by
        your tags. You can apply tags that represent business categories (such
        as cost centers, application names, or owners) to organize your costs
        across multiple services.

        For more information, see `Using Cost Allocation Tags in Amazon
        ElastiCache <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Tagging.html>`__
        in the *ElastiCache User Guide*.

        :param resource_name: The Amazon Resource Name (ARN) of the resource to which the tags are to
        be added, for example
        ``arn:aws:elasticache:us-west-2:0123456789:cluster:myCluster`` or
        ``arn:aws:elasticache:us-west-2:0123456789:snapshot:mySnapshot``.
        :param tags: A list of tags to be added to this resource.
        :returns: TagListMessage
        :raises CacheClusterNotFoundFault:
        :raises CacheParameterGroupNotFoundFault:
        :raises CacheSecurityGroupNotFoundFault:
        :raises CacheSubnetGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises ReplicationGroupNotFoundFault:
        :raises ReservedCacheNodeNotFoundFault:
        :raises SnapshotNotFoundFault:
        :raises UserNotFoundFault:
        :raises UserGroupNotFoundFault:
        :raises TagQuotaPerResourceExceeded:
        :raises InvalidARNFault:
        """
        raise NotImplementedError

    @handler("AuthorizeCacheSecurityGroupIngress")
    def authorize_cache_security_group_ingress(
        self,
        context: RequestContext,
        cache_security_group_name: String,
        ec2_security_group_name: String,
        ec2_security_group_owner_id: String,
    ) -> AuthorizeCacheSecurityGroupIngressResult:
        """Allows network ingress to a cache security group. Applications using
        ElastiCache must be running on Amazon EC2, and Amazon EC2 security
        groups are used as the authorization mechanism.

        You cannot authorize ingress from an Amazon EC2 security group in one
        region to an ElastiCache cluster in another region.

        :param cache_security_group_name: The cache security group that allows network ingress.
        :param ec2_security_group_name: The Amazon EC2 security group to be authorized for ingress to the cache
        security group.
        :param ec2_security_group_owner_id: The Amazon account number of the Amazon EC2 security group owner.
        :returns: AuthorizeCacheSecurityGroupIngressResult
        :raises CacheSecurityGroupNotFoundFault:
        :raises InvalidCacheSecurityGroupStateFault:
        :raises AuthorizationAlreadyExistsFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("BatchApplyUpdateAction")
    def batch_apply_update_action(
        self,
        context: RequestContext,
        service_update_name: String,
        replication_group_ids: ReplicationGroupIdList = None,
        cache_cluster_ids: CacheClusterIdList = None,
    ) -> UpdateActionResultsMessage:
        """Apply the service update. For more information on service updates and
        applying them, see `Applying Service
        Updates <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/applying-updates.html>`__.

        :param service_update_name: The unique ID of the service update.
        :param replication_group_ids: The replication group IDs.
        :param cache_cluster_ids: The cache cluster IDs.
        :returns: UpdateActionResultsMessage
        :raises ServiceUpdateNotFoundFault:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("BatchStopUpdateAction")
    def batch_stop_update_action(
        self,
        context: RequestContext,
        service_update_name: String,
        replication_group_ids: ReplicationGroupIdList = None,
        cache_cluster_ids: CacheClusterIdList = None,
    ) -> UpdateActionResultsMessage:
        """Stop the service update. For more information on service updates and
        stopping them, see `Stopping Service
        Updates <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/stopping-self-service-updates.html>`__.

        :param service_update_name: The unique ID of the service update.
        :param replication_group_ids: The replication group IDs.
        :param cache_cluster_ids: The cache cluster IDs.
        :returns: UpdateActionResultsMessage
        :raises ServiceUpdateNotFoundFault:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("CompleteMigration")
    def complete_migration(
        self, context: RequestContext, replication_group_id: String, force: Boolean = None
    ) -> CompleteMigrationResponse:
        """Complete the migration of data.

        :param replication_group_id: The ID of the replication group to which data is being migrated.
        :param force: Forces the migration to stop without ensuring that data is in sync.
        :returns: CompleteMigrationResponse
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises ReplicationGroupNotUnderMigrationFault:
        """
        raise NotImplementedError

    @handler("CopySnapshot")
    def copy_snapshot(
        self,
        context: RequestContext,
        source_snapshot_name: String,
        target_snapshot_name: String,
        target_bucket: String = None,
        kms_key_id: String = None,
        tags: TagList = None,
    ) -> CopySnapshotResult:
        """Makes a copy of an existing snapshot.

        This operation is valid for Redis only.

        Users or groups that have permissions to use the ``CopySnapshot``
        operation can create their own Amazon S3 buckets and copy snapshots to
        it. To control access to your snapshots, use an IAM policy to control
        who has the ability to use the ``CopySnapshot`` operation. For more
        information about using IAM to control the use of ElastiCache
        operations, see `Exporting
        Snapshots <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/backups-exporting.html>`__
        and `Authentication & Access
        Control <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/IAM.html>`__.

        You could receive the following error messages.

        **Error Messages**

        -  **Error Message:** The S3 bucket %s is outside of the region.

           **Solution:** Create an Amazon S3 bucket in the same region as your
           snapshot. For more information, see `Step 1: Create an Amazon S3
           Bucket <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/backups-exporting.html#backups-exporting-create-s3-bucket>`__
           in the ElastiCache User Guide.

        -  **Error Message:** The S3 bucket %s does not exist.

           **Solution:** Create an Amazon S3 bucket in the same region as your
           snapshot. For more information, see `Step 1: Create an Amazon S3
           Bucket <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/backups-exporting.html#backups-exporting-create-s3-bucket>`__
           in the ElastiCache User Guide.

        -  **Error Message:** The S3 bucket %s is not owned by the authenticated
           user.

           **Solution:** Create an Amazon S3 bucket in the same region as your
           snapshot. For more information, see `Step 1: Create an Amazon S3
           Bucket <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/backups-exporting.html#backups-exporting-create-s3-bucket>`__
           in the ElastiCache User Guide.

        -  **Error Message:** The authenticated user does not have sufficient
           permissions to perform the desired activity.

           **Solution:** Contact your system administrator to get the needed
           permissions.

        -  **Error Message:** The S3 bucket %s already contains an object with
           key %s.

           **Solution:** Give the ``TargetSnapshotName`` a new and unique value.
           If exporting a snapshot, you could alternatively create a new Amazon
           S3 bucket and use this same value for ``TargetSnapshotName``.

        -  **Error Message:** ElastiCache has not been granted READ permissions
           %s on the S3 Bucket.

           **Solution:** Add List and Read permissions on the bucket. For more
           information, see `Step 2: Grant ElastiCache Access to Your Amazon S3
           Bucket <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/backups-exporting.html#backups-exporting-grant-access>`__
           in the ElastiCache User Guide.

        -  **Error Message:** ElastiCache has not been granted WRITE permissions
           %s on the S3 Bucket.

           **Solution:** Add Upload/Delete permissions on the bucket. For more
           information, see `Step 2: Grant ElastiCache Access to Your Amazon S3
           Bucket <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/backups-exporting.html#backups-exporting-grant-access>`__
           in the ElastiCache User Guide.

        -  **Error Message:** ElastiCache has not been granted READ_ACP
           permissions %s on the S3 Bucket.

           **Solution:** Add View Permissions on the bucket. For more
           information, see `Step 2: Grant ElastiCache Access to Your Amazon S3
           Bucket <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/backups-exporting.html#backups-exporting-grant-access>`__
           in the ElastiCache User Guide.

        :param source_snapshot_name: The name of an existing snapshot from which to make a copy.
        :param target_snapshot_name: A name for the snapshot copy.
        :param target_bucket: The Amazon S3 bucket to which the snapshot is exported.
        :param kms_key_id: The ID of the KMS key used to encrypt the target snapshot.
        :param tags: A list of tags to be added to this resource.
        :returns: CopySnapshotResult
        :raises SnapshotAlreadyExistsFault:
        :raises SnapshotNotFoundFault:
        :raises SnapshotQuotaExceededFault:
        :raises InvalidSnapshotStateFault:
        :raises TagQuotaPerResourceExceeded:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("CreateCacheCluster")
    def create_cache_cluster(
        self,
        context: RequestContext,
        cache_cluster_id: String,
        replication_group_id: String = None,
        az_mode: AZMode = None,
        preferred_availability_zone: String = None,
        preferred_availability_zones: PreferredAvailabilityZoneList = None,
        num_cache_nodes: IntegerOptional = None,
        cache_node_type: String = None,
        engine: String = None,
        engine_version: String = None,
        cache_parameter_group_name: String = None,
        cache_subnet_group_name: String = None,
        cache_security_group_names: CacheSecurityGroupNameList = None,
        security_group_ids: SecurityGroupIdsList = None,
        tags: TagList = None,
        snapshot_arns: SnapshotArnsList = None,
        snapshot_name: String = None,
        preferred_maintenance_window: String = None,
        port: IntegerOptional = None,
        notification_topic_arn: String = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        snapshot_retention_limit: IntegerOptional = None,
        snapshot_window: String = None,
        auth_token: String = None,
        outpost_mode: OutpostMode = None,
        preferred_outpost_arn: String = None,
        preferred_outpost_arns: PreferredOutpostArnList = None,
        log_delivery_configurations: LogDeliveryConfigurationRequestList = None,
    ) -> CreateCacheClusterResult:
        """Creates a cluster. All nodes in the cluster run the same
        protocol-compliant cache engine software, either Memcached or Redis.

        This operation is not supported for Redis (cluster mode enabled)
        clusters.

        :param cache_cluster_id: The node group (shard) identifier.
        :param replication_group_id: The ID of the replication group to which this cluster should belong.
        :param az_mode: Specifies whether the nodes in this Memcached cluster are created in a
        single Availability Zone or created across multiple Availability Zones
        in the cluster's region.
        :param preferred_availability_zone: The EC2 Availability Zone in which the cluster is created.
        :param preferred_availability_zones: A list of the Availability Zones in which cache nodes are created.
        :param num_cache_nodes: The initial number of cache nodes that the cluster has.
        :param cache_node_type: The compute and memory capacity of the nodes in the node group (shard).
        :param engine: The name of the cache engine to be used for this cluster.
        :param engine_version: The version number of the cache engine to be used for this cluster.
        :param cache_parameter_group_name: The name of the parameter group to associate with this cluster.
        :param cache_subnet_group_name: The name of the subnet group to be used for the cluster.
        :param cache_security_group_names: A list of security group names to associate with this cluster.
        :param security_group_ids: One or more VPC security groups associated with the cluster.
        :param tags: A list of tags to be added to this resource.
        :param snapshot_arns: A single-element string list containing an Amazon Resource Name (ARN)
        that uniquely identifies a Redis RDB snapshot file stored in Amazon S3.
        :param snapshot_name: The name of a Redis snapshot from which to restore data into the new
        node group (shard).
        :param preferred_maintenance_window: Specifies the weekly time range during which maintenance on the cluster
        is performed.
        :param port: The port number on which each of the cache nodes accepts connections.
        :param notification_topic_arn: The Amazon Resource Name (ARN) of the Amazon Simple Notification Service
        (SNS) topic to which notifications are sent.
        :param auto_minor_version_upgrade: If you are running Redis engine version 6.
        :param snapshot_retention_limit: The number of days for which ElastiCache retains automatic snapshots
        before deleting them.
        :param snapshot_window: The daily time range (in UTC) during which ElastiCache begins taking a
        daily snapshot of your node group (shard).
        :param auth_token: **Reserved parameter.
        :param outpost_mode: Specifies whether the nodes in the cluster are created in a single
        outpost or across multiple outposts.
        :param preferred_outpost_arn: The outpost ARN in which the cache cluster is created.
        :param preferred_outpost_arns: The outpost ARNs in which the cache cluster is created.
        :param log_delivery_configurations: Specifies the destination, format and type of the logs.
        :returns: CreateCacheClusterResult
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises CacheClusterAlreadyExistsFault:
        :raises InsufficientCacheClusterCapacityFault:
        :raises CacheSecurityGroupNotFoundFault:
        :raises CacheSubnetGroupNotFoundFault:
        :raises ClusterQuotaForCustomerExceededFault:
        :raises NodeQuotaForClusterExceededFault:
        :raises NodeQuotaForCustomerExceededFault:
        :raises CacheParameterGroupNotFoundFault:
        :raises InvalidVPCNetworkStateFault:
        :raises TagQuotaPerResourceExceeded:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("CreateCacheParameterGroup")
    def create_cache_parameter_group(
        self,
        context: RequestContext,
        cache_parameter_group_name: String,
        cache_parameter_group_family: String,
        description: String,
        tags: TagList = None,
    ) -> CreateCacheParameterGroupResult:
        """Creates a new Amazon ElastiCache cache parameter group. An ElastiCache
        cache parameter group is a collection of parameters and their values
        that are applied to all of the nodes in any cluster or replication group
        using the CacheParameterGroup.

        A newly created CacheParameterGroup is an exact duplicate of the default
        parameter group for the CacheParameterGroupFamily. To customize the
        newly created CacheParameterGroup you can change the values of specific
        parameters. For more information, see:

        -  `ModifyCacheParameterGroup <https://docs.aws.amazon.com/AmazonElastiCache/latest/APIReference/API_ModifyCacheParameterGroup.html>`__
           in the ElastiCache API Reference.

        -  `Parameters and Parameter
           Groups <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/ParameterGroups.html>`__
           in the ElastiCache User Guide.

        :param cache_parameter_group_name: A user-specified name for the cache parameter group.
        :param cache_parameter_group_family: The name of the cache parameter group family that the cache parameter
        group can be used with.
        :param description: A user-specified description for the cache parameter group.
        :param tags: A list of tags to be added to this resource.
        :returns: CreateCacheParameterGroupResult
        :raises CacheParameterGroupQuotaExceededFault:
        :raises CacheParameterGroupAlreadyExistsFault:
        :raises InvalidCacheParameterGroupStateFault:
        :raises TagQuotaPerResourceExceeded:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("CreateCacheSecurityGroup")
    def create_cache_security_group(
        self,
        context: RequestContext,
        cache_security_group_name: String,
        description: String,
        tags: TagList = None,
    ) -> CreateCacheSecurityGroupResult:
        """Creates a new cache security group. Use a cache security group to
        control access to one or more clusters.

        Cache security groups are only used when you are creating a cluster
        outside of an Amazon Virtual Private Cloud (Amazon VPC). If you are
        creating a cluster inside of a VPC, use a cache subnet group instead.
        For more information, see
        `CreateCacheSubnetGroup <https://docs.aws.amazon.com/AmazonElastiCache/latest/APIReference/API_CreateCacheSubnetGroup.html>`__.

        :param cache_security_group_name: A name for the cache security group.
        :param description: A description for the cache security group.
        :param tags: A list of tags to be added to this resource.
        :returns: CreateCacheSecurityGroupResult
        :raises CacheSecurityGroupAlreadyExistsFault:
        :raises CacheSecurityGroupQuotaExceededFault:
        :raises TagQuotaPerResourceExceeded:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("CreateCacheSubnetGroup")
    def create_cache_subnet_group(
        self,
        context: RequestContext,
        cache_subnet_group_name: String,
        cache_subnet_group_description: String,
        subnet_ids: SubnetIdentifierList,
        tags: TagList = None,
    ) -> CreateCacheSubnetGroupResult:
        """Creates a new cache subnet group.

        Use this parameter only when you are creating a cluster in an Amazon
        Virtual Private Cloud (Amazon VPC).

        :param cache_subnet_group_name: A name for the cache subnet group.
        :param cache_subnet_group_description: A description for the cache subnet group.
        :param subnet_ids: A list of VPC subnet IDs for the cache subnet group.
        :param tags: A list of tags to be added to this resource.
        :returns: CreateCacheSubnetGroupResult
        :raises CacheSubnetGroupAlreadyExistsFault:
        :raises CacheSubnetGroupQuotaExceededFault:
        :raises CacheSubnetQuotaExceededFault:
        :raises TagQuotaPerResourceExceeded:
        :raises InvalidSubnet:
        :raises SubnetNotAllowedFault:
        """
        raise NotImplementedError

    @handler("CreateGlobalReplicationGroup")
    def create_global_replication_group(
        self,
        context: RequestContext,
        global_replication_group_id_suffix: String,
        primary_replication_group_id: String,
        global_replication_group_description: String = None,
    ) -> CreateGlobalReplicationGroupResult:
        """Global Datastore for Redis offers fully managed, fast, reliable and
        secure cross-region replication. Using Global Datastore for Redis, you
        can create cross-region read replica clusters for ElastiCache for Redis
        to enable low-latency reads and disaster recovery across regions. For
        more information, see `Replication Across Regions Using Global
        Datastore <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Redis-Global-Datastore.html>`__.

        -  The **GlobalReplicationGroupIdSuffix** is the name of the Global
           datastore.

        -  The **PrimaryReplicationGroupId** represents the name of the primary
           cluster that accepts writes and will replicate updates to the
           secondary cluster.

        :param global_replication_group_id_suffix: The suffix name of a Global datastore.
        :param primary_replication_group_id: The name of the primary cluster that accepts writes and will replicate
        updates to the secondary cluster.
        :param global_replication_group_description: Provides details of the Global datastore.
        :returns: CreateGlobalReplicationGroupResult
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises GlobalReplicationGroupAlreadyExistsFault:
        :raises ServiceLinkedRoleNotFoundFault:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("CreateReplicationGroup")
    def create_replication_group(
        self,
        context: RequestContext,
        replication_group_id: String,
        replication_group_description: String,
        global_replication_group_id: String = None,
        primary_cluster_id: String = None,
        automatic_failover_enabled: BooleanOptional = None,
        multi_az_enabled: BooleanOptional = None,
        num_cache_clusters: IntegerOptional = None,
        preferred_cache_cluster_azs: AvailabilityZonesList = None,
        num_node_groups: IntegerOptional = None,
        replicas_per_node_group: IntegerOptional = None,
        node_group_configuration: NodeGroupConfigurationList = None,
        cache_node_type: String = None,
        engine: String = None,
        engine_version: String = None,
        cache_parameter_group_name: String = None,
        cache_subnet_group_name: String = None,
        cache_security_group_names: CacheSecurityGroupNameList = None,
        security_group_ids: SecurityGroupIdsList = None,
        tags: TagList = None,
        snapshot_arns: SnapshotArnsList = None,
        snapshot_name: String = None,
        preferred_maintenance_window: String = None,
        port: IntegerOptional = None,
        notification_topic_arn: String = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        snapshot_retention_limit: IntegerOptional = None,
        snapshot_window: String = None,
        auth_token: String = None,
        transit_encryption_enabled: BooleanOptional = None,
        at_rest_encryption_enabled: BooleanOptional = None,
        kms_key_id: String = None,
        user_group_ids: UserGroupIdListInput = None,
        log_delivery_configurations: LogDeliveryConfigurationRequestList = None,
        data_tiering_enabled: BooleanOptional = None,
    ) -> CreateReplicationGroupResult:
        """Creates a Redis (cluster mode disabled) or a Redis (cluster mode
        enabled) replication group.

        This API can be used to create a standalone regional replication group
        or a secondary replication group associated with a Global datastore.

        A Redis (cluster mode disabled) replication group is a collection of
        clusters, where one of the clusters is a read/write primary and the
        others are read-only replicas. Writes to the primary are asynchronously
        propagated to the replicas.

        A Redis cluster-mode enabled cluster is comprised of from 1 to 90 shards
        (API/CLI: node groups). Each shard has a primary node and up to 5
        read-only replica nodes. The configuration can range from 90 shards and
        0 replicas to 15 shards and 5 replicas, which is the maximum number or
        replicas allowed.

        The node or shard limit can be increased to a maximum of 500 per cluster
        if the Redis engine version is 5.0.6 or higher. For example, you can
        choose to configure a 500 node cluster that ranges between 83 shards
        (one primary and 5 replicas per shard) and 500 shards (single primary
        and no replicas). Make sure there are enough available IP addresses to
        accommodate the increase. Common pitfalls include the subnets in the
        subnet group have too small a CIDR range or the subnets are shared and
        heavily used by other clusters. For more information, see `Creating a
        Subnet
        Group <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/SubnetGroups.Creating.html>`__.
        For versions below 5.0.6, the limit is 250 per cluster.

        To request a limit increase, see `Amazon Service
        Limits <https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html>`__
        and choose the limit type **Nodes per cluster per instance type**.

        When a Redis (cluster mode disabled) replication group has been
        successfully created, you can add one or more read replicas to it, up to
        a total of 5 read replicas. If you need to increase or decrease the
        number of node groups (console: shards), you can avail yourself of
        ElastiCache for Redis' scaling. For more information, see `Scaling
        ElastiCache for Redis
        Clusters <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Scaling.html>`__
        in the *ElastiCache User Guide*.

        This operation is valid for Redis only.

        :param replication_group_id: The replication group identifier.
        :param replication_group_description: A user-created description for the replication group.
        :param global_replication_group_id: The name of the Global datastore.
        :param primary_cluster_id: The identifier of the cluster that serves as the primary for this
        replication group.
        :param automatic_failover_enabled: Specifies whether a read-only replica is automatically promoted to
        read/write primary if the existing primary fails.
        :param multi_az_enabled: A flag indicating if you have Multi-AZ enabled to enhance fault
        tolerance.
        :param num_cache_clusters: The number of clusters this replication group initially has.
        :param preferred_cache_cluster_azs: A list of EC2 Availability Zones in which the replication group's
        clusters are created.
        :param num_node_groups: An optional parameter that specifies the number of node groups (shards)
        for this Redis (cluster mode enabled) replication group.
        :param replicas_per_node_group: An optional parameter that specifies the number of replica nodes in each
        node group (shard).
        :param node_group_configuration: A list of node group (shard) configuration options.
        :param cache_node_type: The compute and memory capacity of the nodes in the node group (shard).
        :param engine: The name of the cache engine to be used for the clusters in this
        replication group.
        :param engine_version: The version number of the cache engine to be used for the clusters in
        this replication group.
        :param cache_parameter_group_name: The name of the parameter group to associate with this replication
        group.
        :param cache_subnet_group_name: The name of the cache subnet group to be used for the replication group.
        :param cache_security_group_names: A list of cache security group names to associate with this replication
        group.
        :param security_group_ids: One or more Amazon VPC security groups associated with this replication
        group.
        :param tags: A list of tags to be added to this resource.
        :param snapshot_arns: A list of Amazon Resource Names (ARN) that uniquely identify the Redis
        RDB snapshot files stored in Amazon S3.
        :param snapshot_name: The name of a snapshot from which to restore data into the new
        replication group.
        :param preferred_maintenance_window: Specifies the weekly time range during which maintenance on the cluster
        is performed.
        :param port: The port number on which each member of the replication group accepts
        connections.
        :param notification_topic_arn: The Amazon Resource Name (ARN) of the Amazon Simple Notification Service
        (SNS) topic to which notifications are sent.
        :param auto_minor_version_upgrade: If you are running Redis engine version 6.
        :param snapshot_retention_limit: The number of days for which ElastiCache retains automatic snapshots
        before deleting them.
        :param snapshot_window: The daily time range (in UTC) during which ElastiCache begins taking a
        daily snapshot of your node group (shard).
        :param auth_token: **Reserved parameter.
        :param transit_encryption_enabled: A flag that enables in-transit encryption when set to ``true``.
        :param at_rest_encryption_enabled: A flag that enables encryption at rest when set to ``true``.
        :param kms_key_id: The ID of the KMS key used to encrypt the disk in the cluster.
        :param user_group_ids: The user group to associate with the replication group.
        :param log_delivery_configurations: Specifies the destination, format and type of the logs.
        :param data_tiering_enabled: Enables data tiering.
        :returns: CreateReplicationGroupResult
        :raises CacheClusterNotFoundFault:
        :raises InvalidCacheClusterStateFault:
        :raises ReplicationGroupAlreadyExistsFault:
        :raises InvalidUserGroupStateFault:
        :raises UserGroupNotFoundFault:
        :raises InsufficientCacheClusterCapacityFault:
        :raises CacheSecurityGroupNotFoundFault:
        :raises CacheSubnetGroupNotFoundFault:
        :raises ClusterQuotaForCustomerExceededFault:
        :raises NodeQuotaForClusterExceededFault:
        :raises NodeQuotaForCustomerExceededFault:
        :raises CacheParameterGroupNotFoundFault:
        :raises InvalidVPCNetworkStateFault:
        :raises TagQuotaPerResourceExceeded:
        :raises NodeGroupsPerReplicationGroupQuotaExceededFault:
        :raises GlobalReplicationGroupNotFoundFault:
        :raises InvalidGlobalReplicationGroupStateFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("CreateSnapshot")
    def create_snapshot(
        self,
        context: RequestContext,
        snapshot_name: String,
        replication_group_id: String = None,
        cache_cluster_id: String = None,
        kms_key_id: String = None,
        tags: TagList = None,
    ) -> CreateSnapshotResult:
        """Creates a copy of an entire cluster or replication group at a specific
        moment in time.

        This operation is valid for Redis only.

        :param snapshot_name: A name for the snapshot being created.
        :param replication_group_id: The identifier of an existing replication group.
        :param cache_cluster_id: The identifier of an existing cluster.
        :param kms_key_id: The ID of the KMS key used to encrypt the snapshot.
        :param tags: A list of tags to be added to this resource.
        :returns: CreateSnapshotResult
        :raises SnapshotAlreadyExistsFault:
        :raises CacheClusterNotFoundFault:
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidCacheClusterStateFault:
        :raises InvalidReplicationGroupStateFault:
        :raises SnapshotQuotaExceededFault:
        :raises SnapshotFeatureNotSupportedFault:
        :raises TagQuotaPerResourceExceeded:
        :raises InvalidParameterCombinationException:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("CreateUser")
    def create_user(
        self,
        context: RequestContext,
        user_id: UserId,
        user_name: UserName,
        engine: EngineType,
        access_string: AccessString,
        passwords: PasswordListInput = None,
        no_password_required: BooleanOptional = None,
        tags: TagList = None,
    ) -> User:
        """For Redis engine version 6.0 onwards: Creates a Redis user. For more
        information, see `Using Role Based Access Control
        (RBAC) <http://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Clusters.RBAC.html>`__.

        :param user_id: The ID of the user.
        :param user_name: The username of the user.
        :param engine: The current supported value is Redis.
        :param access_string: Access permissions string used for this user.
        :param passwords: Passwords used for this user.
        :param no_password_required: Indicates a password is not required for this user.
        :param tags: A list of tags to be added to this resource.
        :returns: User
        :raises UserAlreadyExistsFault:
        :raises UserQuotaExceededFault:
        :raises DuplicateUserNameFault:
        :raises ServiceLinkedRoleNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        :raises TagQuotaPerResourceExceeded:
        """
        raise NotImplementedError

    @handler("CreateUserGroup")
    def create_user_group(
        self,
        context: RequestContext,
        user_group_id: String,
        engine: EngineType,
        user_ids: UserIdListInput = None,
        tags: TagList = None,
    ) -> UserGroup:
        """For Redis engine version 6.0 onwards: Creates a Redis user group. For
        more information, see `Using Role Based Access Control
        (RBAC) <http://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Clusters.RBAC.html>`__

        :param user_group_id: The ID of the user group.
        :param engine: The current supported value is Redis.
        :param user_ids: The list of user IDs that belong to the user group.
        :param tags: A list of tags to be added to this resource.
        :returns: UserGroup
        :raises UserNotFoundFault:
        :raises DuplicateUserNameFault:
        :raises UserGroupAlreadyExistsFault:
        :raises ServiceLinkedRoleNotFoundFault:
        :raises DefaultUserRequired:
        :raises UserGroupQuotaExceededFault:
        :raises InvalidParameterValueException:
        :raises TagQuotaPerResourceExceeded:
        """
        raise NotImplementedError

    @handler("DecreaseNodeGroupsInGlobalReplicationGroup")
    def decrease_node_groups_in_global_replication_group(
        self,
        context: RequestContext,
        global_replication_group_id: String,
        node_group_count: Integer,
        apply_immediately: Boolean,
        global_node_groups_to_remove: GlobalNodeGroupIdList = None,
        global_node_groups_to_retain: GlobalNodeGroupIdList = None,
    ) -> DecreaseNodeGroupsInGlobalReplicationGroupResult:
        """Decreases the number of node groups in a Global datastore

        :param global_replication_group_id: The name of the Global datastore.
        :param node_group_count: The number of node groups (shards) that results from the modification of
        the shard configuration.
        :param apply_immediately: Indicates that the shard reconfiguration process begins immediately.
        :param global_node_groups_to_remove: If the value of NodeGroupCount is less than the current number of node
        groups (shards), then either NodeGroupsToRemove or NodeGroupsToRetain is
        required.
        :param global_node_groups_to_retain: If the value of NodeGroupCount is less than the current number of node
        groups (shards), then either NodeGroupsToRemove or NodeGroupsToRetain is
        required.
        :returns: DecreaseNodeGroupsInGlobalReplicationGroupResult
        :raises GlobalReplicationGroupNotFoundFault:
        :raises InvalidGlobalReplicationGroupStateFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DecreaseReplicaCount")
    def decrease_replica_count(
        self,
        context: RequestContext,
        replication_group_id: String,
        apply_immediately: Boolean,
        new_replica_count: IntegerOptional = None,
        replica_configuration: ReplicaConfigurationList = None,
        replicas_to_remove: RemoveReplicasList = None,
    ) -> DecreaseReplicaCountResult:
        """Dynamically decreases the number of replicas in a Redis (cluster mode
        disabled) replication group or the number of replica nodes in one or
        more node groups (shards) of a Redis (cluster mode enabled) replication
        group. This operation is performed with no cluster down time.

        :param replication_group_id: The id of the replication group from which you want to remove replica
        nodes.
        :param apply_immediately: If ``True``, the number of replica nodes is decreased immediately.
        :param new_replica_count: The number of read replica nodes you want at the completion of this
        operation.
        :param replica_configuration: A list of ``ConfigureShard`` objects that can be used to configure each
        shard in a Redis (cluster mode enabled) replication group.
        :param replicas_to_remove: A list of the node ids to remove from the replication group or node
        group (shard).
        :returns: DecreaseReplicaCountResult
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises InvalidCacheClusterStateFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InsufficientCacheClusterCapacityFault:
        :raises ClusterQuotaForCustomerExceededFault:
        :raises NodeGroupsPerReplicationGroupQuotaExceededFault:
        :raises NodeQuotaForCustomerExceededFault:
        :raises ServiceLinkedRoleNotFoundFault:
        :raises NoOperationFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DeleteCacheCluster")
    def delete_cache_cluster(
        self,
        context: RequestContext,
        cache_cluster_id: String,
        final_snapshot_identifier: String = None,
    ) -> DeleteCacheClusterResult:
        """Deletes a previously provisioned cluster. ``DeleteCacheCluster`` deletes
        all associated cache nodes, node endpoints and the cluster itself. When
        you receive a successful response from this operation, Amazon
        ElastiCache immediately begins deleting the cluster; you cannot cancel
        or revert this operation.

        This operation is not valid for:

        -  Redis (cluster mode enabled) clusters

        -  Redis (cluster mode disabled) clusters

        -  A cluster that is the last read replica of a replication group

        -  A cluster that is the primary node of a replication group

        -  A node group (shard) that has Multi-AZ mode enabled

        -  A cluster from a Redis (cluster mode enabled) replication group

        -  A cluster that is not in the ``available`` state

        :param cache_cluster_id: The cluster identifier for the cluster to be deleted.
        :param final_snapshot_identifier: The user-supplied name of a final cluster snapshot.
        :returns: DeleteCacheClusterResult
        :raises CacheClusterNotFoundFault:
        :raises InvalidCacheClusterStateFault:
        :raises SnapshotAlreadyExistsFault:
        :raises SnapshotFeatureNotSupportedFault:
        :raises SnapshotQuotaExceededFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DeleteCacheParameterGroup")
    def delete_cache_parameter_group(
        self, context: RequestContext, cache_parameter_group_name: String
    ) -> None:
        """Deletes the specified cache parameter group. You cannot delete a cache
        parameter group if it is associated with any cache clusters. You cannot
        delete the default cache parameter groups in your account.

        :param cache_parameter_group_name: The name of the cache parameter group to delete.
        :raises InvalidCacheParameterGroupStateFault:
        :raises CacheParameterGroupNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DeleteCacheSecurityGroup")
    def delete_cache_security_group(
        self, context: RequestContext, cache_security_group_name: String
    ) -> None:
        """Deletes a cache security group.

        You cannot delete a cache security group if it is associated with any
        clusters.

        :param cache_security_group_name: The name of the cache security group to delete.
        :raises InvalidCacheSecurityGroupStateFault:
        :raises CacheSecurityGroupNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DeleteCacheSubnetGroup")
    def delete_cache_subnet_group(
        self, context: RequestContext, cache_subnet_group_name: String
    ) -> None:
        """Deletes a cache subnet group.

        You cannot delete a default cache subnet group or one that is associated
        with any clusters.

        :param cache_subnet_group_name: The name of the cache subnet group to delete.
        :raises CacheSubnetGroupInUse:
        :raises CacheSubnetGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DeleteGlobalReplicationGroup")
    def delete_global_replication_group(
        self,
        context: RequestContext,
        global_replication_group_id: String,
        retain_primary_replication_group: Boolean,
    ) -> DeleteGlobalReplicationGroupResult:
        """Deleting a Global datastore is a two-step process:

        -  First, you must DisassociateGlobalReplicationGroup to remove the
           secondary clusters in the Global datastore.

        -  Once the Global datastore contains only the primary cluster, you can
           use the ``DeleteGlobalReplicationGroup`` API to delete the Global
           datastore while retainining the primary cluster using
           ``RetainPrimaryReplicationGroup=true``.

        Since the Global Datastore has only a primary cluster, you can delete
        the Global Datastore while retaining the primary by setting
        ``RetainPrimaryReplicationGroup=true``. The primary cluster is never
        deleted when deleting a Global Datastore. It can only be deleted when it
        no longer is associated with any Global Datastore.

        When you receive a successful response from this operation, Amazon
        ElastiCache immediately begins deleting the selected resources; you
        cannot cancel or revert this operation.

        :param global_replication_group_id: The name of the Global datastore.
        :param retain_primary_replication_group: The primary replication group is retained as a standalone replication
        group.
        :returns: DeleteGlobalReplicationGroupResult
        :raises GlobalReplicationGroupNotFoundFault:
        :raises InvalidGlobalReplicationGroupStateFault:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("DeleteReplicationGroup")
    def delete_replication_group(
        self,
        context: RequestContext,
        replication_group_id: String,
        retain_primary_cluster: BooleanOptional = None,
        final_snapshot_identifier: String = None,
    ) -> DeleteReplicationGroupResult:
        """Deletes an existing replication group. By default, this operation
        deletes the entire replication group, including the primary/primaries
        and all of the read replicas. If the replication group has only one
        primary, you can optionally delete only the read replicas, while
        retaining the primary by setting ``RetainPrimaryCluster=true``.

        When you receive a successful response from this operation, Amazon
        ElastiCache immediately begins deleting the selected resources; you
        cannot cancel or revert this operation.

        This operation is valid for Redis only.

        :param replication_group_id: The identifier for the cluster to be deleted.
        :param retain_primary_cluster: If set to ``true``, all of the read replicas are deleted, but the
        primary node is retained.
        :param final_snapshot_identifier: The name of a final node group (shard) snapshot.
        :returns: DeleteReplicationGroupResult
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises SnapshotAlreadyExistsFault:
        :raises SnapshotFeatureNotSupportedFault:
        :raises SnapshotQuotaExceededFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DeleteSnapshot")
    def delete_snapshot(
        self, context: RequestContext, snapshot_name: String
    ) -> DeleteSnapshotResult:
        """Deletes an existing snapshot. When you receive a successful response
        from this operation, ElastiCache immediately begins deleting the
        snapshot; you cannot cancel or revert this operation.

        This operation is valid for Redis only.

        :param snapshot_name: The name of the snapshot to be deleted.
        :returns: DeleteSnapshotResult
        :raises SnapshotNotFoundFault:
        :raises InvalidSnapshotStateFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DeleteUser")
    def delete_user(self, context: RequestContext, user_id: UserId) -> User:
        """For Redis engine version 6.0 onwards: Deletes a user. The user will be
        removed from all user groups and in turn removed from all replication
        groups. For more information, see `Using Role Based Access Control
        (RBAC) <http://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Clusters.RBAC.html>`__.

        :param user_id: The ID of the user.
        :returns: User
        :raises InvalidUserStateFault:
        :raises UserNotFoundFault:
        :raises ServiceLinkedRoleNotFoundFault:
        :raises InvalidParameterValueException:
        :raises DefaultUserAssociatedToUserGroupFault:
        """
        raise NotImplementedError

    @handler("DeleteUserGroup")
    def delete_user_group(self, context: RequestContext, user_group_id: String) -> UserGroup:
        """For Redis engine version 6.0 onwards: Deletes a user group. The user
        group must first be disassociated from the replication group before it
        can be deleted. For more information, see `Using Role Based Access
        Control
        (RBAC) <http://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Clusters.RBAC.html>`__.

        :param user_group_id: The ID of the user group.
        :returns: UserGroup
        :raises UserGroupNotFoundFault:
        :raises InvalidUserGroupStateFault:
        :raises ServiceLinkedRoleNotFoundFault:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("DescribeCacheClusters")
    def describe_cache_clusters(
        self,
        context: RequestContext,
        cache_cluster_id: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
        show_cache_node_info: BooleanOptional = None,
        show_cache_clusters_not_in_replication_groups: BooleanOptional = None,
    ) -> CacheClusterMessage:
        """Returns information about all provisioned clusters if no cluster
        identifier is specified, or about a specific cache cluster if a cluster
        identifier is supplied.

        By default, abbreviated information about the clusters is returned. You
        can use the optional *ShowCacheNodeInfo* flag to retrieve detailed
        information about the cache nodes associated with the clusters. These
        details include the DNS address and port for the cache node endpoint.

        If the cluster is in the *creating* state, only cluster-level
        information is displayed until all of the nodes are successfully
        provisioned.

        If the cluster is in the *deleting* state, only cluster-level
        information is displayed.

        If cache nodes are currently being added to the cluster, node endpoint
        information and creation time for the additional nodes are not displayed
        until they are completely provisioned. When the cluster state is
        *available*, the cluster is ready for use.

        If cache nodes are currently being removed from the cluster, no endpoint
        information for the removed nodes is displayed.

        :param cache_cluster_id: The user-supplied cluster identifier.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :param show_cache_node_info: An optional flag that can be included in the ``DescribeCacheCluster``
        request to retrieve information about the individual cache nodes.
        :param show_cache_clusters_not_in_replication_groups: An optional flag that can be included in the ``DescribeCacheCluster``
        request to show only nodes (API/CLI: clusters) that are not members of a
        replication group.
        :returns: CacheClusterMessage
        :raises CacheClusterNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeCacheEngineVersions")
    def describe_cache_engine_versions(
        self,
        context: RequestContext,
        engine: String = None,
        engine_version: String = None,
        cache_parameter_group_family: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
        default_only: Boolean = None,
    ) -> CacheEngineVersionMessage:
        """Returns a list of the available cache engines and their versions.

        :param engine: The cache engine to return.
        :param engine_version: The cache engine version to return.
        :param cache_parameter_group_family: The name of a specific cache parameter group family to return details
        for.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :param default_only: If ``true``, specifies that only the default version of the specified
        engine or engine and major version combination is to be returned.
        :returns: CacheEngineVersionMessage
        """
        raise NotImplementedError

    @handler("DescribeCacheParameterGroups")
    def describe_cache_parameter_groups(
        self,
        context: RequestContext,
        cache_parameter_group_name: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> CacheParameterGroupsMessage:
        """Returns a list of cache parameter group descriptions. If a cache
        parameter group name is specified, the list contains only the
        descriptions for that group.

        :param cache_parameter_group_name: The name of a specific cache parameter group to return details for.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: CacheParameterGroupsMessage
        :raises CacheParameterGroupNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeCacheParameters")
    def describe_cache_parameters(
        self,
        context: RequestContext,
        cache_parameter_group_name: String,
        source: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> CacheParameterGroupDetails:
        """Returns the detailed parameter list for a particular cache parameter
        group.

        :param cache_parameter_group_name: The name of a specific cache parameter group to return details for.
        :param source: The parameter types to return.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: CacheParameterGroupDetails
        :raises CacheParameterGroupNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeCacheSecurityGroups")
    def describe_cache_security_groups(
        self,
        context: RequestContext,
        cache_security_group_name: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> CacheSecurityGroupMessage:
        """Returns a list of cache security group descriptions. If a cache security
        group name is specified, the list contains only the description of that
        group. This applicable only when you have ElastiCache in Classic setup

        :param cache_security_group_name: The name of the cache security group to return details for.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: CacheSecurityGroupMessage
        :raises CacheSecurityGroupNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeCacheSubnetGroups")
    def describe_cache_subnet_groups(
        self,
        context: RequestContext,
        cache_subnet_group_name: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> CacheSubnetGroupMessage:
        """Returns a list of cache subnet group descriptions. If a subnet group
        name is specified, the list contains only the description of that group.
        This is applicable only when you have ElastiCache in VPC setup. All
        ElastiCache clusters now launch in VPC by default.

        :param cache_subnet_group_name: The name of the cache subnet group to return details for.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: CacheSubnetGroupMessage
        :raises CacheSubnetGroupNotFoundFault:
        """
        raise NotImplementedError

    @handler("DescribeEngineDefaultParameters")
    def describe_engine_default_parameters(
        self,
        context: RequestContext,
        cache_parameter_group_family: String,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DescribeEngineDefaultParametersResult:
        """Returns the default engine and system parameter information for the
        specified cache engine.

        :param cache_parameter_group_family: The name of the cache parameter group family.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: DescribeEngineDefaultParametersResult
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
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
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> EventsMessage:
        """Returns events related to clusters, cache security groups, and cache
        parameter groups. You can obtain events specific to a particular
        cluster, cache security group, or cache parameter group by providing the
        name as a parameter.

        By default, only the events occurring within the last hour are returned;
        however, you can retrieve up to 14 days' worth of events if necessary.

        :param source_identifier: The identifier of the event source for which events are returned.
        :param source_type: The event source to retrieve events for.
        :param start_time: The beginning of the time interval to retrieve events for, specified in
        ISO 8601 format.
        :param end_time: The end of the time interval for which to retrieve events, specified in
        ISO 8601 format.
        :param duration: The number of minutes worth of events to retrieve.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: EventsMessage
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeGlobalReplicationGroups")
    def describe_global_replication_groups(
        self,
        context: RequestContext,
        global_replication_group_id: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
        show_member_info: BooleanOptional = None,
    ) -> DescribeGlobalReplicationGroupsResult:
        """Returns information about a particular global replication group. If no
        identifier is specified, returns information about all Global
        datastores.

        :param global_replication_group_id: The name of the Global datastore.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :param show_member_info: Returns the list of members that comprise the Global datastore.
        :returns: DescribeGlobalReplicationGroupsResult
        :raises GlobalReplicationGroupNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeReplicationGroups")
    def describe_replication_groups(
        self,
        context: RequestContext,
        replication_group_id: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> ReplicationGroupMessage:
        """Returns information about a particular replication group. If no
        identifier is specified, ``DescribeReplicationGroups`` returns
        information about all replication groups.

        This operation is valid for Redis only.

        :param replication_group_id: The identifier for the replication group to be described.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: ReplicationGroupMessage
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeReservedCacheNodes")
    def describe_reserved_cache_nodes(
        self,
        context: RequestContext,
        reserved_cache_node_id: String = None,
        reserved_cache_nodes_offering_id: String = None,
        cache_node_type: String = None,
        duration: String = None,
        product_description: String = None,
        offering_type: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> ReservedCacheNodeMessage:
        """Returns information about reserved cache nodes for this account, or
        about a specified reserved cache node.

        :param reserved_cache_node_id: The reserved cache node identifier filter value.
        :param reserved_cache_nodes_offering_id: The offering identifier filter value.
        :param cache_node_type: The cache node type filter value.
        :param duration: The duration filter value, specified in years or seconds.
        :param product_description: The product description filter value.
        :param offering_type: The offering type filter value.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: ReservedCacheNodeMessage
        :raises ReservedCacheNodeNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeReservedCacheNodesOfferings")
    def describe_reserved_cache_nodes_offerings(
        self,
        context: RequestContext,
        reserved_cache_nodes_offering_id: String = None,
        cache_node_type: String = None,
        duration: String = None,
        product_description: String = None,
        offering_type: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> ReservedCacheNodesOfferingMessage:
        """Lists available reserved cache node offerings.

        :param reserved_cache_nodes_offering_id: The offering identifier filter value.
        :param cache_node_type: The cache node type filter value.
        :param duration: Duration filter value, specified in years or seconds.
        :param product_description: The product description filter value.
        :param offering_type: The offering type filter value.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: ReservedCacheNodesOfferingMessage
        :raises ReservedCacheNodesOfferingNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeServiceUpdates")
    def describe_service_updates(
        self,
        context: RequestContext,
        service_update_name: String = None,
        service_update_status: ServiceUpdateStatusList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> ServiceUpdatesMessage:
        """Returns details of the service updates

        :param service_update_name: The unique ID of the service update.
        :param service_update_status: The status of the service update.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: ServiceUpdatesMessage
        :raises ServiceUpdateNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeSnapshots")
    def describe_snapshots(
        self,
        context: RequestContext,
        replication_group_id: String = None,
        cache_cluster_id: String = None,
        snapshot_name: String = None,
        snapshot_source: String = None,
        marker: String = None,
        max_records: IntegerOptional = None,
        show_node_group_config: BooleanOptional = None,
    ) -> DescribeSnapshotsListMessage:
        """Returns information about cluster or replication group snapshots. By
        default, ``DescribeSnapshots`` lists all of your snapshots; it can
        optionally describe a single snapshot, or just the snapshots associated
        with a particular cache cluster.

        This operation is valid for Redis only.

        :param replication_group_id: A user-supplied replication group identifier.
        :param cache_cluster_id: A user-supplied cluster identifier.
        :param snapshot_name: A user-supplied name of the snapshot.
        :param snapshot_source: If set to ``system``, the output shows snapshots that were automatically
        created by ElastiCache.
        :param marker: An optional marker returned from a prior request.
        :param max_records: The maximum number of records to include in the response.
        :param show_node_group_config: A Boolean value which if true, the node group (shard) configuration is
        included in the snapshot description.
        :returns: DescribeSnapshotsListMessage
        :raises CacheClusterNotFoundFault:
        :raises SnapshotNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeUpdateActions")
    def describe_update_actions(
        self,
        context: RequestContext,
        service_update_name: String = None,
        replication_group_ids: ReplicationGroupIdList = None,
        cache_cluster_ids: CacheClusterIdList = None,
        engine: String = None,
        service_update_status: ServiceUpdateStatusList = None,
        service_update_time_range: TimeRangeFilter = None,
        update_action_status: UpdateActionStatusList = None,
        show_node_level_update_status: BooleanOptional = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> UpdateActionsMessage:
        """Returns details of the update actions

        :param service_update_name: The unique ID of the service update.
        :param replication_group_ids: The replication group IDs.
        :param cache_cluster_ids: The cache cluster IDs.
        :param engine: The Elasticache engine to which the update applies.
        :param service_update_status: The status of the service update.
        :param service_update_time_range: The range of time specified to search for service updates that are in
        available status.
        :param update_action_status: The status of the update action.
        :param show_node_level_update_status: Dictates whether to include node level update status in the response.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: UpdateActionsMessage
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeUserGroups")
    def describe_user_groups(
        self,
        context: RequestContext,
        user_group_id: String = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DescribeUserGroupsResult:
        """Returns a list of user groups.

        :param user_group_id: The ID of the user group.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: DescribeUserGroupsResult
        :raises UserGroupNotFoundFault:
        :raises ServiceLinkedRoleNotFoundFault:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DescribeUsers")
    def describe_users(
        self,
        context: RequestContext,
        engine: EngineType = None,
        user_id: UserId = None,
        filters: FilterList = None,
        max_records: IntegerOptional = None,
        marker: String = None,
    ) -> DescribeUsersResult:
        """Returns a list of users.

        :param engine: The Redis engine.
        :param user_id: The ID of the user.
        :param filters: Filter to determine the list of User IDs to return.
        :param max_records: The maximum number of records to include in the response.
        :param marker: An optional marker returned from a prior request.
        :returns: DescribeUsersResult
        :raises UserNotFoundFault:
        :raises ServiceLinkedRoleNotFoundFault:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("DisassociateGlobalReplicationGroup")
    def disassociate_global_replication_group(
        self,
        context: RequestContext,
        global_replication_group_id: String,
        replication_group_id: String,
        replication_group_region: String,
    ) -> DisassociateGlobalReplicationGroupResult:
        """Remove a secondary cluster from the Global datastore using the Global
        datastore name. The secondary cluster will no longer receive updates
        from the primary cluster, but will remain as a standalone cluster in
        that Amazon region.

        :param global_replication_group_id: The name of the Global datastore.
        :param replication_group_id: The name of the secondary cluster you wish to remove from the Global
        datastore.
        :param replication_group_region: The Amazon region of secondary cluster you wish to remove from the
        Global datastore.
        :returns: DisassociateGlobalReplicationGroupResult
        :raises GlobalReplicationGroupNotFoundFault:
        :raises InvalidGlobalReplicationGroupStateFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("FailoverGlobalReplicationGroup")
    def failover_global_replication_group(
        self,
        context: RequestContext,
        global_replication_group_id: String,
        primary_region: String,
        primary_replication_group_id: String,
    ) -> FailoverGlobalReplicationGroupResult:
        """Used to failover the primary region to a selected secondary region. The
        selected secondary region will become primary, and all other clusters
        will become secondary.

        :param global_replication_group_id: The name of the Global datastore.
        :param primary_region: The Amazon region of the primary cluster of the Global datastore.
        :param primary_replication_group_id: The name of the primary replication group.
        :returns: FailoverGlobalReplicationGroupResult
        :raises GlobalReplicationGroupNotFoundFault:
        :raises InvalidGlobalReplicationGroupStateFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("IncreaseNodeGroupsInGlobalReplicationGroup")
    def increase_node_groups_in_global_replication_group(
        self,
        context: RequestContext,
        global_replication_group_id: String,
        node_group_count: Integer,
        apply_immediately: Boolean,
        regional_configurations: RegionalConfigurationList = None,
    ) -> IncreaseNodeGroupsInGlobalReplicationGroupResult:
        """Increase the number of node groups in the Global datastore

        :param global_replication_group_id: The name of the Global datastore.
        :param node_group_count: The number of node groups you wish to add.
        :param apply_immediately: Indicates that the process begins immediately.
        :param regional_configurations: Describes the replication group IDs, the Amazon regions where they are
        stored and the shard configuration for each that comprise the Global
        datastore.
        :returns: IncreaseNodeGroupsInGlobalReplicationGroupResult
        :raises GlobalReplicationGroupNotFoundFault:
        :raises InvalidGlobalReplicationGroupStateFault:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("IncreaseReplicaCount")
    def increase_replica_count(
        self,
        context: RequestContext,
        replication_group_id: String,
        apply_immediately: Boolean,
        new_replica_count: IntegerOptional = None,
        replica_configuration: ReplicaConfigurationList = None,
    ) -> IncreaseReplicaCountResult:
        """Dynamically increases the number of replicas in a Redis (cluster mode
        disabled) replication group or the number of replica nodes in one or
        more node groups (shards) of a Redis (cluster mode enabled) replication
        group. This operation is performed with no cluster down time.

        :param replication_group_id: The id of the replication group to which you want to add replica nodes.
        :param apply_immediately: If ``True``, the number of replica nodes is increased immediately.
        :param new_replica_count: The number of read replica nodes you want at the completion of this
        operation.
        :param replica_configuration: A list of ``ConfigureShard`` objects that can be used to configure each
        shard in a Redis (cluster mode enabled) replication group.
        :returns: IncreaseReplicaCountResult
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises InvalidCacheClusterStateFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InsufficientCacheClusterCapacityFault:
        :raises ClusterQuotaForCustomerExceededFault:
        :raises NodeGroupsPerReplicationGroupQuotaExceededFault:
        :raises NodeQuotaForCustomerExceededFault:
        :raises NoOperationFault:
        :raises InvalidKMSKeyFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("ListAllowedNodeTypeModifications")
    def list_allowed_node_type_modifications(
        self,
        context: RequestContext,
        cache_cluster_id: String = None,
        replication_group_id: String = None,
    ) -> AllowedNodeTypeModificationsMessage:
        """Lists all available node types that you can scale your Redis cluster's
        or replication group's current node type.

        When you use the ``ModifyCacheCluster`` or ``ModifyReplicationGroup``
        operations to scale your cluster or replication group, the value of the
        ``CacheNodeType`` parameter must be one of the node types returned by
        this operation.

        :param cache_cluster_id: The name of the cluster you want to scale up to a larger node instanced
        type.
        :param replication_group_id: The name of the replication group want to scale up to a larger node
        type.
        :returns: AllowedNodeTypeModificationsMessage
        :raises CacheClusterNotFoundFault:
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidParameterCombinationException:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_name: String
    ) -> TagListMessage:
        """Lists all tags currently on a named resource.

        A tag is a key-value pair where the key and value are case-sensitive.
        You can use tags to categorize and track all your ElastiCache resources,
        with the exception of global replication group. When you add or remove
        tags on replication groups, those actions will be replicated to all
        nodes in the replication group. For more information, see
        `Resource-level
        permissions <http://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/IAM.ResourceLevelPermissions.html>`__.

        If the cluster is not in the *available* state, ``ListTagsForResource``
        returns an error.

        :param resource_name: The Amazon Resource Name (ARN) of the resource for which you want the
        list of tags, for example
        ``arn:aws:elasticache:us-west-2:0123456789:cluster:myCluster`` or
        ``arn:aws:elasticache:us-west-2:0123456789:snapshot:mySnapshot``.
        :returns: TagListMessage
        :raises CacheClusterNotFoundFault:
        :raises CacheParameterGroupNotFoundFault:
        :raises CacheSecurityGroupNotFoundFault:
        :raises CacheSubnetGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises ReplicationGroupNotFoundFault:
        :raises ReservedCacheNodeNotFoundFault:
        :raises SnapshotNotFoundFault:
        :raises UserNotFoundFault:
        :raises UserGroupNotFoundFault:
        :raises InvalidARNFault:
        """
        raise NotImplementedError

    @handler("ModifyCacheCluster")
    def modify_cache_cluster(
        self,
        context: RequestContext,
        cache_cluster_id: String,
        num_cache_nodes: IntegerOptional = None,
        cache_node_ids_to_remove: CacheNodeIdsList = None,
        az_mode: AZMode = None,
        new_availability_zones: PreferredAvailabilityZoneList = None,
        cache_security_group_names: CacheSecurityGroupNameList = None,
        security_group_ids: SecurityGroupIdsList = None,
        preferred_maintenance_window: String = None,
        notification_topic_arn: String = None,
        cache_parameter_group_name: String = None,
        notification_topic_status: String = None,
        apply_immediately: Boolean = None,
        engine_version: String = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        snapshot_retention_limit: IntegerOptional = None,
        snapshot_window: String = None,
        cache_node_type: String = None,
        auth_token: String = None,
        auth_token_update_strategy: AuthTokenUpdateStrategyType = None,
        log_delivery_configurations: LogDeliveryConfigurationRequestList = None,
    ) -> ModifyCacheClusterResult:
        """Modifies the settings for a cluster. You can use this operation to
        change one or more cluster configuration parameters by specifying the
        parameters and the new values.

        :param cache_cluster_id: The cluster identifier.
        :param num_cache_nodes: The number of cache nodes that the cluster should have.
        :param cache_node_ids_to_remove: A list of cache node IDs to be removed.
        :param az_mode: Specifies whether the new nodes in this Memcached cluster are all
        created in a single Availability Zone or created across multiple
        Availability Zones.
        :param new_availability_zones: This option is only supported on Memcached clusters.
        :param cache_security_group_names: A list of cache security group names to authorize on this cluster.
        :param security_group_ids: Specifies the VPC Security Groups associated with the cluster.
        :param preferred_maintenance_window: Specifies the weekly time range during which maintenance on the cluster
        is performed.
        :param notification_topic_arn: The Amazon Resource Name (ARN) of the Amazon SNS topic to which
        notifications are sent.
        :param cache_parameter_group_name: The name of the cache parameter group to apply to this cluster.
        :param notification_topic_status: The status of the Amazon SNS notification topic.
        :param apply_immediately: If ``true``, this parameter causes the modifications in this request and
        any pending modifications to be applied, asynchronously and as soon as
        possible, regardless of the ``PreferredMaintenanceWindow`` setting for
        the cluster.
        :param engine_version: The upgraded version of the cache engine to be run on the cache nodes.
        :param auto_minor_version_upgrade: If you are running Redis engine version 6.
        :param snapshot_retention_limit: The number of days for which ElastiCache retains automatic cluster
        snapshots before deleting them.
        :param snapshot_window: The daily time range (in UTC) during which ElastiCache begins taking a
        daily snapshot of your cluster.
        :param cache_node_type: A valid cache node type that you want to scale this cluster up to.
        :param auth_token: Reserved parameter.
        :param auth_token_update_strategy: Specifies the strategy to use to update the AUTH token.
        :param log_delivery_configurations: Specifies the destination, format and type of the logs.
        :returns: ModifyCacheClusterResult
        :raises InvalidCacheClusterStateFault:
        :raises InvalidCacheSecurityGroupStateFault:
        :raises InsufficientCacheClusterCapacityFault:
        :raises CacheClusterNotFoundFault:
        :raises NodeQuotaForClusterExceededFault:
        :raises NodeQuotaForCustomerExceededFault:
        :raises CacheSecurityGroupNotFoundFault:
        :raises CacheParameterGroupNotFoundFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("ModifyCacheParameterGroup")
    def modify_cache_parameter_group(
        self,
        context: RequestContext,
        cache_parameter_group_name: String,
        parameter_name_values: ParameterNameValueList,
    ) -> CacheParameterGroupNameMessage:
        """Modifies the parameters of a cache parameter group. You can modify up to
        20 parameters in a single request by submitting a list parameter name
        and value pairs.

        :param cache_parameter_group_name: The name of the cache parameter group to modify.
        :param parameter_name_values: An array of parameter names and values for the parameter update.
        :returns: CacheParameterGroupNameMessage
        :raises CacheParameterGroupNotFoundFault:
        :raises InvalidCacheParameterGroupStateFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        :raises InvalidGlobalReplicationGroupStateFault:
        """
        raise NotImplementedError

    @handler("ModifyCacheSubnetGroup")
    def modify_cache_subnet_group(
        self,
        context: RequestContext,
        cache_subnet_group_name: String,
        cache_subnet_group_description: String = None,
        subnet_ids: SubnetIdentifierList = None,
    ) -> ModifyCacheSubnetGroupResult:
        """Modifies an existing cache subnet group.

        :param cache_subnet_group_name: The name for the cache subnet group.
        :param cache_subnet_group_description: A description of the cache subnet group.
        :param subnet_ids: The EC2 subnet IDs for the cache subnet group.
        :returns: ModifyCacheSubnetGroupResult
        :raises CacheSubnetGroupNotFoundFault:
        :raises CacheSubnetQuotaExceededFault:
        :raises SubnetInUse:
        :raises InvalidSubnet:
        :raises SubnetNotAllowedFault:
        """
        raise NotImplementedError

    @handler("ModifyGlobalReplicationGroup")
    def modify_global_replication_group(
        self,
        context: RequestContext,
        global_replication_group_id: String,
        apply_immediately: Boolean,
        cache_node_type: String = None,
        engine_version: String = None,
        cache_parameter_group_name: String = None,
        global_replication_group_description: String = None,
        automatic_failover_enabled: BooleanOptional = None,
    ) -> ModifyGlobalReplicationGroupResult:
        """Modifies the settings for a Global datastore.

        :param global_replication_group_id: The name of the Global datastore.
        :param apply_immediately: This parameter causes the modifications in this request and any pending
        modifications to be applied, asynchronously and as soon as possible.
        :param cache_node_type: A valid cache node type that you want to scale this Global datastore to.
        :param engine_version: The upgraded version of the cache engine to be run on the clusters in
        the Global datastore.
        :param cache_parameter_group_name: The name of the cache parameter group to use with the Global datastore.
        :param global_replication_group_description: A description of the Global datastore.
        :param automatic_failover_enabled: Determines whether a read replica is automatically promoted to
        read/write primary if the existing primary encounters a failure.
        :returns: ModifyGlobalReplicationGroupResult
        :raises GlobalReplicationGroupNotFoundFault:
        :raises InvalidGlobalReplicationGroupStateFault:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("ModifyReplicationGroup")
    def modify_replication_group(
        self,
        context: RequestContext,
        replication_group_id: String,
        replication_group_description: String = None,
        primary_cluster_id: String = None,
        snapshotting_cluster_id: String = None,
        automatic_failover_enabled: BooleanOptional = None,
        multi_az_enabled: BooleanOptional = None,
        node_group_id: String = None,
        cache_security_group_names: CacheSecurityGroupNameList = None,
        security_group_ids: SecurityGroupIdsList = None,
        preferred_maintenance_window: String = None,
        notification_topic_arn: String = None,
        cache_parameter_group_name: String = None,
        notification_topic_status: String = None,
        apply_immediately: Boolean = None,
        engine_version: String = None,
        auto_minor_version_upgrade: BooleanOptional = None,
        snapshot_retention_limit: IntegerOptional = None,
        snapshot_window: String = None,
        cache_node_type: String = None,
        auth_token: String = None,
        auth_token_update_strategy: AuthTokenUpdateStrategyType = None,
        user_group_ids_to_add: UserGroupIdList = None,
        user_group_ids_to_remove: UserGroupIdList = None,
        remove_user_groups: BooleanOptional = None,
        log_delivery_configurations: LogDeliveryConfigurationRequestList = None,
    ) -> ModifyReplicationGroupResult:
        """Modifies the settings for a replication group.

        -  `Scaling for Amazon ElastiCache for Redis (cluster mode
           enabled) <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/scaling-redis-cluster-mode-enabled.html>`__
           in the ElastiCache User Guide

        -  `ModifyReplicationGroupShardConfiguration <https://docs.aws.amazon.com/AmazonElastiCache/latest/APIReference/API_ModifyReplicationGroupShardConfiguration.html>`__
           in the ElastiCache API Reference

        This operation is valid for Redis only.

        :param replication_group_id: The identifier of the replication group to modify.
        :param replication_group_description: A description for the replication group.
        :param primary_cluster_id: For replication groups with a single primary, if this parameter is
        specified, ElastiCache promotes the specified cluster in the specified
        replication group to the primary role.
        :param snapshotting_cluster_id: The cluster ID that is used as the daily snapshot source for the
        replication group.
        :param automatic_failover_enabled: Determines whether a read replica is automatically promoted to
        read/write primary if the existing primary encounters a failure.
        :param multi_az_enabled: A flag to indicate MultiAZ is enabled.
        :param node_group_id: Deprecated.
        :param cache_security_group_names: A list of cache security group names to authorize for the clusters in
        this replication group.
        :param security_group_ids: Specifies the VPC Security Groups associated with the clusters in the
        replication group.
        :param preferred_maintenance_window: Specifies the weekly time range during which maintenance on the cluster
        is performed.
        :param notification_topic_arn: The Amazon Resource Name (ARN) of the Amazon SNS topic to which
        notifications are sent.
        :param cache_parameter_group_name: The name of the cache parameter group to apply to all of the clusters in
        this replication group.
        :param notification_topic_status: The status of the Amazon SNS notification topic for the replication
        group.
        :param apply_immediately: If ``true``, this parameter causes the modifications in this request and
        any pending modifications to be applied, asynchronously and as soon as
        possible, regardless of the ``PreferredMaintenanceWindow`` setting for
        the replication group.
        :param engine_version: The upgraded version of the cache engine to be run on the clusters in
        the replication group.
        :param auto_minor_version_upgrade: If you are running Redis engine version 6.
        :param snapshot_retention_limit: The number of days for which ElastiCache retains automatic node group
        (shard) snapshots before deleting them.
        :param snapshot_window: The daily time range (in UTC) during which ElastiCache begins taking a
        daily snapshot of the node group (shard) specified by
        ``SnapshottingClusterId``.
        :param cache_node_type: A valid cache node type that you want to scale this replication group
        to.
        :param auth_token: Reserved parameter.
        :param auth_token_update_strategy: Specifies the strategy to use to update the AUTH token.
        :param user_group_ids_to_add: The ID of the user group you are associating with the replication group.
        :param user_group_ids_to_remove: The ID of the user group to disassociate from the replication group,
        meaning the users in the group no longer can access the replication
        group.
        :param remove_user_groups: Removes the user group associated with this replication group.
        :param log_delivery_configurations: Specifies the destination, format and type of the logs.
        :returns: ModifyReplicationGroupResult
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises InvalidUserGroupStateFault:
        :raises UserGroupNotFoundFault:
        :raises InvalidCacheClusterStateFault:
        :raises InvalidCacheSecurityGroupStateFault:
        :raises InsufficientCacheClusterCapacityFault:
        :raises CacheClusterNotFoundFault:
        :raises NodeQuotaForClusterExceededFault:
        :raises NodeQuotaForCustomerExceededFault:
        :raises CacheSecurityGroupNotFoundFault:
        :raises CacheParameterGroupNotFoundFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InvalidKMSKeyFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("ModifyReplicationGroupShardConfiguration")
    def modify_replication_group_shard_configuration(
        self,
        context: RequestContext,
        replication_group_id: String,
        node_group_count: Integer,
        apply_immediately: Boolean,
        resharding_configuration: ReshardingConfigurationList = None,
        node_groups_to_remove: NodeGroupsToRemoveList = None,
        node_groups_to_retain: NodeGroupsToRetainList = None,
    ) -> ModifyReplicationGroupShardConfigurationResult:
        """Modifies a replication group's shards (node groups) by allowing you to
        add shards, remove shards, or rebalance the keyspaces among existing
        shards.

        :param replication_group_id: The name of the Redis (cluster mode enabled) cluster (replication group)
        on which the shards are to be configured.
        :param node_group_count: The number of node groups (shards) that results from the modification of
        the shard configuration.
        :param apply_immediately: Indicates that the shard reconfiguration process begins immediately.
        :param resharding_configuration: Specifies the preferred availability zones for each node group in the
        cluster.
        :param node_groups_to_remove: If the value of ``NodeGroupCount`` is less than the current number of
        node groups (shards), then either ``NodeGroupsToRemove`` or
        ``NodeGroupsToRetain`` is required.
        :param node_groups_to_retain: If the value of ``NodeGroupCount`` is less than the current number of
        node groups (shards), then either ``NodeGroupsToRemove`` or
        ``NodeGroupsToRetain`` is required.
        :returns: ModifyReplicationGroupShardConfigurationResult
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises InvalidCacheClusterStateFault:
        :raises InvalidVPCNetworkStateFault:
        :raises InsufficientCacheClusterCapacityFault:
        :raises NodeGroupsPerReplicationGroupQuotaExceededFault:
        :raises NodeQuotaForCustomerExceededFault:
        :raises InvalidKMSKeyFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("ModifyUser")
    def modify_user(
        self,
        context: RequestContext,
        user_id: UserId,
        access_string: AccessString = None,
        append_access_string: AccessString = None,
        passwords: PasswordListInput = None,
        no_password_required: BooleanOptional = None,
    ) -> User:
        """Changes user password(s) and/or access string.

        :param user_id: The ID of the user.
        :param access_string: Access permissions string used for this user.
        :param append_access_string: Adds additional user permissions to the access string.
        :param passwords: The passwords belonging to the user.
        :param no_password_required: Indicates no password is required for the user.
        :returns: User
        :raises UserNotFoundFault:
        :raises InvalidUserStateFault:
        :raises ServiceLinkedRoleNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("ModifyUserGroup")
    def modify_user_group(
        self,
        context: RequestContext,
        user_group_id: String,
        user_ids_to_add: UserIdListInput = None,
        user_ids_to_remove: UserIdListInput = None,
    ) -> UserGroup:
        """Changes the list of users that belong to the user group.

        :param user_group_id: The ID of the user group.
        :param user_ids_to_add: The list of user IDs to add to the user group.
        :param user_ids_to_remove: The list of user IDs to remove from the user group.
        :returns: UserGroup
        :raises UserGroupNotFoundFault:
        :raises UserNotFoundFault:
        :raises DuplicateUserNameFault:
        :raises ServiceLinkedRoleNotFoundFault:
        :raises DefaultUserRequired:
        :raises InvalidUserGroupStateFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("PurchaseReservedCacheNodesOffering")
    def purchase_reserved_cache_nodes_offering(
        self,
        context: RequestContext,
        reserved_cache_nodes_offering_id: String,
        reserved_cache_node_id: String = None,
        cache_node_count: IntegerOptional = None,
        tags: TagList = None,
    ) -> PurchaseReservedCacheNodesOfferingResult:
        """Allows you to purchase a reserved cache node offering. Reserved nodes
        are not eligible for cancellation and are non-refundable. For more
        information, see `Managing Costs with Reserved
        Nodes <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/reserved-nodes.html>`__
        for Redis or `Managing Costs with Reserved
        Nodes <https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/reserved-nodes.html>`__
        for Memcached.

        :param reserved_cache_nodes_offering_id: The ID of the reserved cache node offering to purchase.
        :param reserved_cache_node_id: A customer-specified identifier to track this reservation.
        :param cache_node_count: The number of cache node instances to reserve.
        :param tags: A list of tags to be added to this resource.
        :returns: PurchaseReservedCacheNodesOfferingResult
        :raises ReservedCacheNodesOfferingNotFoundFault:
        :raises ReservedCacheNodeAlreadyExistsFault:
        :raises ReservedCacheNodeQuotaExceededFault:
        :raises TagQuotaPerResourceExceeded:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("RebalanceSlotsInGlobalReplicationGroup")
    def rebalance_slots_in_global_replication_group(
        self,
        context: RequestContext,
        global_replication_group_id: String,
        apply_immediately: Boolean,
    ) -> RebalanceSlotsInGlobalReplicationGroupResult:
        """Redistribute slots to ensure uniform distribution across existing shards
        in the cluster.

        :param global_replication_group_id: The name of the Global datastore.
        :param apply_immediately: If ``True``, redistribution is applied immediately.
        :returns: RebalanceSlotsInGlobalReplicationGroupResult
        :raises GlobalReplicationGroupNotFoundFault:
        :raises InvalidGlobalReplicationGroupStateFault:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("RebootCacheCluster")
    def reboot_cache_cluster(
        self,
        context: RequestContext,
        cache_cluster_id: String,
        cache_node_ids_to_reboot: CacheNodeIdsList,
    ) -> RebootCacheClusterResult:
        """Reboots some, or all, of the cache nodes within a provisioned cluster.
        This operation applies any modified cache parameter groups to the
        cluster. The reboot operation takes place as soon as possible, and
        results in a momentary outage to the cluster. During the reboot, the
        cluster status is set to REBOOTING.

        The reboot causes the contents of the cache (for each cache node being
        rebooted) to be lost.

        When the reboot is complete, a cluster event is created.

        Rebooting a cluster is currently supported on Memcached and Redis
        (cluster mode disabled) clusters. Rebooting is not supported on Redis
        (cluster mode enabled) clusters.

        If you make changes to parameters that require a Redis (cluster mode
        enabled) cluster reboot for the changes to be applied, see `Rebooting a
        Cluster <http://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/nodes.rebooting.html>`__
        for an alternate process.

        :param cache_cluster_id: The cluster identifier.
        :param cache_node_ids_to_reboot: A list of cache node IDs to reboot.
        :returns: RebootCacheClusterResult
        :raises InvalidCacheClusterStateFault:
        :raises CacheClusterNotFoundFault:
        """
        raise NotImplementedError

    @handler("RemoveTagsFromResource")
    def remove_tags_from_resource(
        self, context: RequestContext, resource_name: String, tag_keys: KeyList
    ) -> TagListMessage:
        """Removes the tags identified by the ``TagKeys`` list from the named
        resource. A tag is a key-value pair where the key and value are
        case-sensitive. You can use tags to categorize and track all your
        ElastiCache resources, with the exception of global replication group.
        When you add or remove tags on replication groups, those actions will be
        replicated to all nodes in the replication group. For more information,
        see `Resource-level
        permissions <http://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/IAM.ResourceLevelPermissions.html>`__.

        :param resource_name: The Amazon Resource Name (ARN) of the resource from which you want the
        tags removed, for example
        ``arn:aws:elasticache:us-west-2:0123456789:cluster:myCluster`` or
        ``arn:aws:elasticache:us-west-2:0123456789:snapshot:mySnapshot``.
        :param tag_keys: A list of ``TagKeys`` identifying the tags you want removed from the
        named resource.
        :returns: TagListMessage
        :raises CacheClusterNotFoundFault:
        :raises CacheParameterGroupNotFoundFault:
        :raises CacheSecurityGroupNotFoundFault:
        :raises CacheSubnetGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises ReplicationGroupNotFoundFault:
        :raises ReservedCacheNodeNotFoundFault:
        :raises SnapshotNotFoundFault:
        :raises UserNotFoundFault:
        :raises UserGroupNotFoundFault:
        :raises InvalidARNFault:
        :raises TagNotFoundFault:
        """
        raise NotImplementedError

    @handler("ResetCacheParameterGroup")
    def reset_cache_parameter_group(
        self,
        context: RequestContext,
        cache_parameter_group_name: String,
        reset_all_parameters: Boolean = None,
        parameter_name_values: ParameterNameValueList = None,
    ) -> CacheParameterGroupNameMessage:
        """Modifies the parameters of a cache parameter group to the engine or
        system default value. You can reset specific parameters by submitting a
        list of parameter names. To reset the entire cache parameter group,
        specify the ``ResetAllParameters`` and ``CacheParameterGroupName``
        parameters.

        :param cache_parameter_group_name: The name of the cache parameter group to reset.
        :param reset_all_parameters: If ``true``, all parameters in the cache parameter group are reset to
        their default values.
        :param parameter_name_values: An array of parameter names to reset to their default values.
        :returns: CacheParameterGroupNameMessage
        :raises InvalidCacheParameterGroupStateFault:
        :raises CacheParameterGroupNotFoundFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        :raises InvalidGlobalReplicationGroupStateFault:
        """
        raise NotImplementedError

    @handler("RevokeCacheSecurityGroupIngress")
    def revoke_cache_security_group_ingress(
        self,
        context: RequestContext,
        cache_security_group_name: String,
        ec2_security_group_name: String,
        ec2_security_group_owner_id: String,
    ) -> RevokeCacheSecurityGroupIngressResult:
        """Revokes ingress from a cache security group. Use this operation to
        disallow access from an Amazon EC2 security group that had been
        previously authorized.

        :param cache_security_group_name: The name of the cache security group to revoke ingress from.
        :param ec2_security_group_name: The name of the Amazon EC2 security group to revoke access from.
        :param ec2_security_group_owner_id: The Amazon account number of the Amazon EC2 security group owner.
        :returns: RevokeCacheSecurityGroupIngressResult
        :raises CacheSecurityGroupNotFoundFault:
        :raises AuthorizationNotFoundFault:
        :raises InvalidCacheSecurityGroupStateFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError

    @handler("StartMigration")
    def start_migration(
        self,
        context: RequestContext,
        replication_group_id: String,
        customer_node_endpoint_list: CustomerNodeEndpointList,
    ) -> StartMigrationResponse:
        """Start the migration of data.

        :param replication_group_id: The ID of the replication group to which data should be migrated.
        :param customer_node_endpoint_list: List of endpoints from which data should be migrated.
        :returns: StartMigrationResponse
        :raises ReplicationGroupNotFoundFault:
        :raises InvalidReplicationGroupStateFault:
        :raises ReplicationGroupAlreadyUnderMigrationFault:
        :raises InvalidParameterValueException:
        """
        raise NotImplementedError

    @handler("TestFailover")
    def test_failover(
        self,
        context: RequestContext,
        replication_group_id: String,
        node_group_id: AllowedNodeGroupId,
    ) -> TestFailoverResult:
        """Represents the input of a ``TestFailover`` operation which test
        automatic failover on a specified node group (called shard in the
        console) in a replication group (called cluster in the console).

        This API is designed for testing the behavior of your application in
        case of ElastiCache failover. It is not designed to be an operational
        tool for initiating a failover to overcome a problem you may have with
        the cluster. Moreover, in certain conditions such as large-scale
        operational events, Amazon may block this API.

        **Note the following**

        -  A customer can use this operation to test automatic failover on up to
           5 shards (called node groups in the ElastiCache API and Amazon CLI)
           in any rolling 24-hour period.

        -  If calling this operation on shards in different clusters (called
           replication groups in the API and CLI), the calls can be made
           concurrently.

        -  If calling this operation multiple times on different shards in the
           same Redis (cluster mode enabled) replication group, the first node
           replacement must complete before a subsequent call can be made.

        -  To determine whether the node replacement is complete you can check
           Events using the Amazon ElastiCache console, the Amazon CLI, or the
           ElastiCache API. Look for the following automatic failover related
           events, listed here in order of occurrance:

           #. Replication group message:
              ``Test Failover API called for node group <node-group-id>``

           #. Cache cluster message:
              ``Failover from primary node <primary-node-id> to replica node <node-id> completed``

           #. Replication group message:
              ``Failover from primary node <primary-node-id> to replica node <node-id> completed``

           #. Cache cluster message: ``Recovering cache nodes <node-id>``

           #. Cache cluster message:
              ``Finished recovery for cache nodes <node-id>``

           For more information see:

           -  `Viewing ElastiCache
              Events <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/ECEvents.Viewing.html>`__
              in the *ElastiCache User Guide*

           -  `DescribeEvents <https://docs.aws.amazon.com/AmazonElastiCache/latest/APIReference/API_DescribeEvents.html>`__
              in the ElastiCache API Reference

        Also see, `Testing
        Multi-AZ <https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/AutoFailover.html#auto-failover-test>`__
        in the *ElastiCache User Guide*.

        :param replication_group_id: The name of the replication group (console: cluster) whose automatic
        failover is being tested by this operation.
        :param node_group_id: The name of the node group (called shard in the console) in this
        replication group on which automatic failover is to be tested.
        :returns: TestFailoverResult
        :raises APICallRateForCustomerExceededFault:
        :raises InvalidCacheClusterStateFault:
        :raises InvalidReplicationGroupStateFault:
        :raises NodeGroupNotFoundFault:
        :raises ReplicationGroupNotFoundFault:
        :raises TestFailoverNotAvailableFault:
        :raises InvalidKMSKeyFault:
        :raises InvalidParameterValueException:
        :raises InvalidParameterCombinationException:
        """
        raise NotImplementedError
