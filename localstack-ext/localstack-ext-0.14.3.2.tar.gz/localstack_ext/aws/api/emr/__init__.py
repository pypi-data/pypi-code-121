import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

ArnType = str
Boolean = bool
BooleanObject = bool
ClusterId = str
ErrorCode = str
ErrorMessage = str
InstanceFleetId = str
InstanceGroupId = str
InstanceId = str
InstanceType = str
Integer = int
Marker = str
MaxResultsNumber = int
NonNegativeDouble = float
OptionalArnType = str
Port = int
ResourceId = str
StepId = str
String = str
WholeNumber = int
XmlString = str
XmlStringMaxLen256 = str


class ActionOnFailure(str):
    TERMINATE_JOB_FLOW = "TERMINATE_JOB_FLOW"
    TERMINATE_CLUSTER = "TERMINATE_CLUSTER"
    CANCEL_AND_WAIT = "CANCEL_AND_WAIT"
    CONTINUE = "CONTINUE"


class AdjustmentType(str):
    CHANGE_IN_CAPACITY = "CHANGE_IN_CAPACITY"
    PERCENT_CHANGE_IN_CAPACITY = "PERCENT_CHANGE_IN_CAPACITY"
    EXACT_CAPACITY = "EXACT_CAPACITY"


class AuthMode(str):
    SSO = "SSO"
    IAM = "IAM"


class AutoScalingPolicyState(str):
    PENDING = "PENDING"
    ATTACHING = "ATTACHING"
    ATTACHED = "ATTACHED"
    DETACHING = "DETACHING"
    DETACHED = "DETACHED"
    FAILED = "FAILED"


class AutoScalingPolicyStateChangeReasonCode(str):
    USER_REQUEST = "USER_REQUEST"
    PROVISION_FAILURE = "PROVISION_FAILURE"
    CLEANUP_FAILURE = "CLEANUP_FAILURE"


class CancelStepsRequestStatus(str):
    SUBMITTED = "SUBMITTED"
    FAILED = "FAILED"


class ClusterState(str):
    STARTING = "STARTING"
    BOOTSTRAPPING = "BOOTSTRAPPING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATING = "TERMINATING"
    TERMINATED = "TERMINATED"
    TERMINATED_WITH_ERRORS = "TERMINATED_WITH_ERRORS"


class ClusterStateChangeReasonCode(str):
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INSTANCE_FAILURE = "INSTANCE_FAILURE"
    INSTANCE_FLEET_TIMEOUT = "INSTANCE_FLEET_TIMEOUT"
    BOOTSTRAP_FAILURE = "BOOTSTRAP_FAILURE"
    USER_REQUEST = "USER_REQUEST"
    STEP_FAILURE = "STEP_FAILURE"
    ALL_STEPS_COMPLETED = "ALL_STEPS_COMPLETED"


class ComparisonOperator(str):
    GREATER_THAN_OR_EQUAL = "GREATER_THAN_OR_EQUAL"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"


class ComputeLimitsUnitType(str):
    InstanceFleetUnits = "InstanceFleetUnits"
    Instances = "Instances"
    VCPU = "VCPU"


class ExecutionEngineType(str):
    EMR = "EMR"


class IdentityType(str):
    USER = "USER"
    GROUP = "GROUP"


class InstanceCollectionType(str):
    INSTANCE_FLEET = "INSTANCE_FLEET"
    INSTANCE_GROUP = "INSTANCE_GROUP"


class InstanceFleetState(str):
    PROVISIONING = "PROVISIONING"
    BOOTSTRAPPING = "BOOTSTRAPPING"
    RUNNING = "RUNNING"
    RESIZING = "RESIZING"
    SUSPENDED = "SUSPENDED"
    TERMINATING = "TERMINATING"
    TERMINATED = "TERMINATED"


class InstanceFleetStateChangeReasonCode(str):
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INSTANCE_FAILURE = "INSTANCE_FAILURE"
    CLUSTER_TERMINATED = "CLUSTER_TERMINATED"


class InstanceFleetType(str):
    MASTER = "MASTER"
    CORE = "CORE"
    TASK = "TASK"


class InstanceGroupState(str):
    PROVISIONING = "PROVISIONING"
    BOOTSTRAPPING = "BOOTSTRAPPING"
    RUNNING = "RUNNING"
    RECONFIGURING = "RECONFIGURING"
    RESIZING = "RESIZING"
    SUSPENDED = "SUSPENDED"
    TERMINATING = "TERMINATING"
    TERMINATED = "TERMINATED"
    ARRESTED = "ARRESTED"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    ENDED = "ENDED"


class InstanceGroupStateChangeReasonCode(str):
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INSTANCE_FAILURE = "INSTANCE_FAILURE"
    CLUSTER_TERMINATED = "CLUSTER_TERMINATED"


class InstanceGroupType(str):
    MASTER = "MASTER"
    CORE = "CORE"
    TASK = "TASK"


class InstanceRoleType(str):
    MASTER = "MASTER"
    CORE = "CORE"
    TASK = "TASK"


class InstanceState(str):
    AWAITING_FULFILLMENT = "AWAITING_FULFILLMENT"
    PROVISIONING = "PROVISIONING"
    BOOTSTRAPPING = "BOOTSTRAPPING"
    RUNNING = "RUNNING"
    TERMINATED = "TERMINATED"


class InstanceStateChangeReasonCode(str):
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INSTANCE_FAILURE = "INSTANCE_FAILURE"
    BOOTSTRAP_FAILURE = "BOOTSTRAP_FAILURE"
    CLUSTER_TERMINATED = "CLUSTER_TERMINATED"


class JobFlowExecutionState(str):
    STARTING = "STARTING"
    BOOTSTRAPPING = "BOOTSTRAPPING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    TERMINATED = "TERMINATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MarketType(str):
    ON_DEMAND = "ON_DEMAND"
    SPOT = "SPOT"


class NotebookExecutionStatus(str):
    START_PENDING = "START_PENDING"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    FINISHING = "FINISHING"
    FINISHED = "FINISHED"
    FAILING = "FAILING"
    FAILED = "FAILED"
    STOP_PENDING = "STOP_PENDING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"


class OnDemandCapacityReservationPreference(str):
    open = "open"
    none = "none"


class OnDemandCapacityReservationUsageStrategy(str):
    use_capacity_reservations_first = "use-capacity-reservations-first"


class OnDemandProvisioningAllocationStrategy(str):
    lowest_price = "lowest-price"


class PlacementGroupStrategy(str):
    SPREAD = "SPREAD"
    PARTITION = "PARTITION"
    CLUSTER = "CLUSTER"
    NONE = "NONE"


class ReconfigurationType(str):
    OVERWRITE = "OVERWRITE"
    MERGE = "MERGE"


class RepoUpgradeOnBoot(str):
    SECURITY = "SECURITY"
    NONE = "NONE"


class ScaleDownBehavior(str):
    TERMINATE_AT_INSTANCE_HOUR = "TERMINATE_AT_INSTANCE_HOUR"
    TERMINATE_AT_TASK_COMPLETION = "TERMINATE_AT_TASK_COMPLETION"


class SpotProvisioningAllocationStrategy(str):
    capacity_optimized = "capacity-optimized"


class SpotProvisioningTimeoutAction(str):
    SWITCH_TO_ON_DEMAND = "SWITCH_TO_ON_DEMAND"
    TERMINATE_CLUSTER = "TERMINATE_CLUSTER"


class Statistic(str):
    SAMPLE_COUNT = "SAMPLE_COUNT"
    AVERAGE = "AVERAGE"
    SUM = "SUM"
    MINIMUM = "MINIMUM"
    MAXIMUM = "MAXIMUM"


class StepCancellationOption(str):
    SEND_INTERRUPT = "SEND_INTERRUPT"
    TERMINATE_PROCESS = "TERMINATE_PROCESS"


class StepExecutionState(str):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    CONTINUE = "CONTINUE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"


class StepState(str):
    PENDING = "PENDING"
    CANCEL_PENDING = "CANCEL_PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"


class StepStateChangeReasonCode(str):
    NONE = "NONE"


class Unit(str):
    NONE = "NONE"
    SECONDS = "SECONDS"
    MICRO_SECONDS = "MICRO_SECONDS"
    MILLI_SECONDS = "MILLI_SECONDS"
    BYTES = "BYTES"
    KILO_BYTES = "KILO_BYTES"
    MEGA_BYTES = "MEGA_BYTES"
    GIGA_BYTES = "GIGA_BYTES"
    TERA_BYTES = "TERA_BYTES"
    BITS = "BITS"
    KILO_BITS = "KILO_BITS"
    MEGA_BITS = "MEGA_BITS"
    GIGA_BITS = "GIGA_BITS"
    TERA_BITS = "TERA_BITS"
    PERCENT = "PERCENT"
    COUNT = "COUNT"
    BYTES_PER_SECOND = "BYTES_PER_SECOND"
    KILO_BYTES_PER_SECOND = "KILO_BYTES_PER_SECOND"
    MEGA_BYTES_PER_SECOND = "MEGA_BYTES_PER_SECOND"
    GIGA_BYTES_PER_SECOND = "GIGA_BYTES_PER_SECOND"
    TERA_BYTES_PER_SECOND = "TERA_BYTES_PER_SECOND"
    BITS_PER_SECOND = "BITS_PER_SECOND"
    KILO_BITS_PER_SECOND = "KILO_BITS_PER_SECOND"
    MEGA_BITS_PER_SECOND = "MEGA_BITS_PER_SECOND"
    GIGA_BITS_PER_SECOND = "GIGA_BITS_PER_SECOND"
    TERA_BITS_PER_SECOND = "TERA_BITS_PER_SECOND"
    COUNT_PER_SECOND = "COUNT_PER_SECOND"


class InternalServerError(ServiceException):
    """Indicates that an error occurred while processing the request and that
    the request was not completed.
    """


class InternalServerException(ServiceException):
    """This exception occurs when there is an internal failure in the Amazon
    EMR service.
    """

    Message: Optional[ErrorMessage]


class InvalidRequestException(ServiceException):
    """This exception occurs when there is something wrong with user input."""

    ErrorCode: Optional[ErrorCode]
    Message: Optional[ErrorMessage]


class OnDemandCapacityReservationOptions(TypedDict, total=False):
    """Describes the strategy for using unused Capacity Reservations for
    fulfilling On-Demand capacity.
    """

    UsageStrategy: Optional[OnDemandCapacityReservationUsageStrategy]
    CapacityReservationPreference: Optional[OnDemandCapacityReservationPreference]
    CapacityReservationResourceGroupArn: Optional[XmlStringMaxLen256]


class OnDemandProvisioningSpecification(TypedDict, total=False):
    """The launch specification for On-Demand Instances in the instance fleet,
    which determines the allocation strategy.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions. On-Demand Instances
    allocation strategy is available in Amazon EMR version 5.12.1 and later.
    """

    AllocationStrategy: OnDemandProvisioningAllocationStrategy
    CapacityReservationOptions: Optional[OnDemandCapacityReservationOptions]


class SpotProvisioningSpecification(TypedDict, total=False):
    """The launch specification for Spot Instances in the instance fleet, which
    determines the defined duration, provisioning timeout behavior, and
    allocation strategy.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions. Spot Instance
    allocation strategy is available in Amazon EMR version 5.12.1 and later.

    Spot Instances with a defined duration (also known as Spot blocks) are
    no longer available to new customers from July 1, 2021. For customers
    who have previously used the feature, we will continue to support Spot
    Instances with a defined duration until December 31, 2022.
    """

    TimeoutDurationMinutes: WholeNumber
    TimeoutAction: SpotProvisioningTimeoutAction
    BlockDurationMinutes: Optional[WholeNumber]
    AllocationStrategy: Optional[SpotProvisioningAllocationStrategy]


class InstanceFleetProvisioningSpecifications(TypedDict, total=False):
    """The launch specification for Spot Instances in the fleet, which
    determines the defined duration, provisioning timeout behavior, and
    allocation strategy.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions. On-Demand and Spot
    Instance allocation strategies are available in Amazon EMR version
    5.12.1 and later.
    """

    SpotSpecification: Optional[SpotProvisioningSpecification]
    OnDemandSpecification: Optional[OnDemandProvisioningSpecification]


StringMap = Dict[String, String]
ConfigurationList = List["Configuration"]


class Configuration(TypedDict, total=False):
    """Amazon EMR releases 4.x or later.

    An optional configuration specification to be used when provisioning
    cluster instances, which can include configurations for applications and
    software bundled with Amazon EMR. A configuration consists of a
    classification, properties, and optional nested configurations. A
    classification refers to an application-specific configuration file.
    Properties are the settings you want to change in that file. For more
    information, see `Configuring
    Applications <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-configure-apps.html>`__.
    """

    Classification: Optional[String]
    Configurations: Optional[ConfigurationList]
    Properties: Optional[StringMap]


class VolumeSpecification(TypedDict, total=False):
    """EBS volume specifications such as volume type, IOPS, and size (GiB) that
    will be requested for the EBS volume attached to an EC2 instance in the
    cluster.
    """

    VolumeType: String
    Iops: Optional[Integer]
    SizeInGB: Integer


class EbsBlockDeviceConfig(TypedDict, total=False):
    """Configuration of requested EBS block device associated with the instance
    group with count of volumes that will be associated to every instance.
    """

    VolumeSpecification: VolumeSpecification
    VolumesPerInstance: Optional[Integer]


EbsBlockDeviceConfigList = List[EbsBlockDeviceConfig]


class EbsConfiguration(TypedDict, total=False):
    """The Amazon EBS configuration of a cluster instance."""

    EbsBlockDeviceConfigs: Optional[EbsBlockDeviceConfigList]
    EbsOptimized: Optional[BooleanObject]


class InstanceTypeConfig(TypedDict, total=False):
    """An instance type configuration for each instance type in an instance
    fleet, which determines the EC2 instances Amazon EMR attempts to
    provision to fulfill On-Demand and Spot target capacities. When you use
    an allocation strategy, you can include a maximum of 30 instance type
    configurations for a fleet. For more information about how to use an
    allocation strategy, see `Configure Instance
    Fleets <https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-instance-fleet.html>`__.
    Without an allocation strategy, you may specify a maximum of five
    instance type configurations for a fleet.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions.
    """

    InstanceType: InstanceType
    WeightedCapacity: Optional[WholeNumber]
    BidPrice: Optional[XmlStringMaxLen256]
    BidPriceAsPercentageOfOnDemandPrice: Optional[NonNegativeDouble]
    EbsConfiguration: Optional[EbsConfiguration]
    Configurations: Optional[ConfigurationList]
    CustomAmiId: Optional[XmlStringMaxLen256]


InstanceTypeConfigList = List[InstanceTypeConfig]


class InstanceFleetConfig(TypedDict, total=False):
    """The configuration that defines an instance fleet.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions.
    """

    Name: Optional[XmlStringMaxLen256]
    InstanceFleetType: InstanceFleetType
    TargetOnDemandCapacity: Optional[WholeNumber]
    TargetSpotCapacity: Optional[WholeNumber]
    InstanceTypeConfigs: Optional[InstanceTypeConfigList]
    LaunchSpecifications: Optional[InstanceFleetProvisioningSpecifications]


class AddInstanceFleetInput(ServiceRequest):
    ClusterId: XmlStringMaxLen256
    InstanceFleet: InstanceFleetConfig


class AddInstanceFleetOutput(TypedDict, total=False):
    ClusterId: Optional[XmlStringMaxLen256]
    InstanceFleetId: Optional[InstanceFleetId]
    ClusterArn: Optional[ArnType]


class MetricDimension(TypedDict, total=False):
    """A CloudWatch dimension, which is specified using a ``Key`` (known as a
    ``Name`` in CloudWatch), ``Value`` pair. By default, Amazon EMR uses one
    dimension whose ``Key`` is ``JobFlowID`` and ``Value`` is a variable
    representing the cluster ID, which is ``${emr.clusterId}``. This enables
    the rule to bootstrap when the cluster ID becomes available.
    """

    Key: Optional[String]
    Value: Optional[String]


MetricDimensionList = List[MetricDimension]


class CloudWatchAlarmDefinition(TypedDict, total=False):
    """The definition of a CloudWatch metric alarm, which determines when an
    automatic scaling activity is triggered. When the defined alarm
    conditions are satisfied, scaling activity begins.
    """

    ComparisonOperator: ComparisonOperator
    EvaluationPeriods: Optional[Integer]
    MetricName: String
    Namespace: Optional[String]
    Period: Integer
    Statistic: Optional[Statistic]
    Threshold: NonNegativeDouble
    Unit: Optional[Unit]
    Dimensions: Optional[MetricDimensionList]


class ScalingTrigger(TypedDict, total=False):
    """The conditions that trigger an automatic scaling activity."""

    CloudWatchAlarmDefinition: CloudWatchAlarmDefinition


class SimpleScalingPolicyConfiguration(TypedDict, total=False):
    """An automatic scaling configuration, which describes how the policy adds
    or removes instances, the cooldown period, and the number of EC2
    instances that will be added each time the CloudWatch metric alarm
    condition is satisfied.
    """

    AdjustmentType: Optional[AdjustmentType]
    ScalingAdjustment: Integer
    CoolDown: Optional[Integer]


class ScalingAction(TypedDict, total=False):
    """The type of adjustment the automatic scaling activity makes when
    triggered, and the periodicity of the adjustment.
    """

    Market: Optional[MarketType]
    SimpleScalingPolicyConfiguration: SimpleScalingPolicyConfiguration


class ScalingRule(TypedDict, total=False):
    """A scale-in or scale-out rule that defines scaling activity, including
    the CloudWatch metric alarm that triggers activity, how EC2 instances
    are added or removed, and the periodicity of adjustments. The automatic
    scaling policy for an instance group can comprise one or more automatic
    scaling rules.
    """

    Name: String
    Description: Optional[String]
    Action: ScalingAction
    Trigger: ScalingTrigger


ScalingRuleList = List[ScalingRule]


class ScalingConstraints(TypedDict, total=False):
    """The upper and lower EC2 instance limits for an automatic scaling policy.
    Automatic scaling activities triggered by automatic scaling rules will
    not cause an instance group to grow above or below these limits.
    """

    MinCapacity: Integer
    MaxCapacity: Integer


class AutoScalingPolicy(TypedDict, total=False):
    """An automatic scaling policy for a core instance group or task instance
    group in an Amazon EMR cluster. An automatic scaling policy defines how
    an instance group dynamically adds and terminates EC2 instances in
    response to the value of a CloudWatch metric. See PutAutoScalingPolicy.
    """

    Constraints: ScalingConstraints
    Rules: ScalingRuleList


class InstanceGroupConfig(TypedDict, total=False):
    """Configuration defining a new instance group."""

    Name: Optional[XmlStringMaxLen256]
    Market: Optional[MarketType]
    InstanceRole: InstanceRoleType
    BidPrice: Optional[XmlStringMaxLen256]
    InstanceType: InstanceType
    InstanceCount: Integer
    Configurations: Optional[ConfigurationList]
    EbsConfiguration: Optional[EbsConfiguration]
    AutoScalingPolicy: Optional[AutoScalingPolicy]
    CustomAmiId: Optional[XmlStringMaxLen256]


InstanceGroupConfigList = List[InstanceGroupConfig]


class AddInstanceGroupsInput(ServiceRequest):
    """Input to an AddInstanceGroups call."""

    InstanceGroups: InstanceGroupConfigList
    JobFlowId: XmlStringMaxLen256


InstanceGroupIdsList = List[XmlStringMaxLen256]


class AddInstanceGroupsOutput(TypedDict, total=False):
    """Output from an AddInstanceGroups call."""

    JobFlowId: Optional[XmlStringMaxLen256]
    InstanceGroupIds: Optional[InstanceGroupIdsList]
    ClusterArn: Optional[ArnType]


XmlStringList = List[XmlString]


class KeyValue(TypedDict, total=False):
    """A key-value pair."""

    Key: Optional[XmlString]
    Value: Optional[XmlString]


KeyValueList = List[KeyValue]


class HadoopJarStepConfig(TypedDict, total=False):
    """A job flow step consisting of a JAR file whose main function will be
    executed. The main function submits a job for Hadoop to execute and
    waits for the job to finish or fail.
    """

    Properties: Optional[KeyValueList]
    Jar: XmlString
    MainClass: Optional[XmlString]
    Args: Optional[XmlStringList]


class StepConfig(TypedDict, total=False):
    """Specification for a cluster (job flow) step."""

    Name: XmlStringMaxLen256
    ActionOnFailure: Optional[ActionOnFailure]
    HadoopJarStep: HadoopJarStepConfig


StepConfigList = List[StepConfig]


class AddJobFlowStepsInput(ServiceRequest):
    """The input argument to the AddJobFlowSteps operation."""

    JobFlowId: XmlStringMaxLen256
    Steps: StepConfigList


StepIdsList = List[XmlStringMaxLen256]


class AddJobFlowStepsOutput(TypedDict, total=False):
    """The output for the AddJobFlowSteps operation."""

    StepIds: Optional[StepIdsList]


class Tag(TypedDict, total=False):
    """A key-value pair containing user-defined metadata that you can associate
    with an Amazon EMR resource. Tags make it easier to associate clusters
    in various ways, such as grouping clusters to track your Amazon EMR
    resource allocation costs. For more information, see `Tag
    Clusters <https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-tags.html>`__.
    """

    Key: Optional[String]
    Value: Optional[String]


TagList = List[Tag]


class AddTagsInput(ServiceRequest):
    """This input identifies an Amazon EMR resource and a list of tags to
    attach.
    """

    ResourceId: ResourceId
    Tags: TagList


class AddTagsOutput(TypedDict, total=False):
    """This output indicates the result of adding tags to a resource."""


StringList = List[String]


class Application(TypedDict, total=False):
    """With Amazon EMR release version 4.0 and later, the only accepted
    parameter is the application name. To pass arguments to applications,
    you use configuration classifications specified using configuration JSON
    objects. For more information, see `Configuring
    Applications <https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-configure-apps.html>`__.

    With earlier Amazon EMR releases, the application is any Amazon or
    third-party software that you can add to the cluster. This structure
    contains a list of strings that indicates the software to use with the
    cluster and accepts a user argument list. Amazon EMR accepts and
    forwards the argument list to the corresponding installation script as
    bootstrap action argument.
    """

    Name: Optional[String]
    Version: Optional[String]
    Args: Optional[StringList]
    AdditionalInfo: Optional[StringMap]


ApplicationList = List[Application]


class AutoScalingPolicyStateChangeReason(TypedDict, total=False):
    """The reason for an AutoScalingPolicyStatus change."""

    Code: Optional[AutoScalingPolicyStateChangeReasonCode]
    Message: Optional[String]


class AutoScalingPolicyStatus(TypedDict, total=False):
    """The status of an automatic scaling policy."""

    State: Optional[AutoScalingPolicyState]
    StateChangeReason: Optional[AutoScalingPolicyStateChangeReason]


class AutoScalingPolicyDescription(TypedDict, total=False):
    """An automatic scaling policy for a core instance group or task instance
    group in an Amazon EMR cluster. The automatic scaling policy defines how
    an instance group dynamically adds and terminates EC2 instances in
    response to the value of a CloudWatch metric. See PutAutoScalingPolicy.
    """

    Status: Optional[AutoScalingPolicyStatus]
    Constraints: Optional[ScalingConstraints]
    Rules: Optional[ScalingRuleList]


Long = int


class AutoTerminationPolicy(TypedDict, total=False):
    """An auto-termination policy for an Amazon EMR cluster. An
    auto-termination policy defines the amount of idle time in seconds after
    which a cluster automatically terminates. For alternative cluster
    termination options, see `Control cluster
    termination <https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-termination.html>`__.
    """

    IdleTimeout: Optional[Long]


class PortRange(TypedDict, total=False):
    """A list of port ranges that are permitted to allow inbound traffic from
    all public IP addresses. To specify a single port, use the same value
    for ``MinRange`` and ``MaxRange``.
    """

    MinRange: Port
    MaxRange: Optional[Port]


PortRanges = List[PortRange]


class BlockPublicAccessConfiguration(TypedDict, total=False):
    """A configuration for Amazon EMR block public access. When
    ``BlockPublicSecurityGroupRules`` is set to ``true``, Amazon EMR
    prevents cluster creation if one of the cluster's security groups has a
    rule that allows inbound traffic from 0.0.0.0/0 or ::/0 on a port,
    unless the port is specified as an exception using
    ``PermittedPublicSecurityGroupRuleRanges``.
    """

    BlockPublicSecurityGroupRules: Boolean
    PermittedPublicSecurityGroupRuleRanges: Optional[PortRanges]


Date = datetime


class BlockPublicAccessConfigurationMetadata(TypedDict, total=False):
    """Properties that describe the Amazon Web Services principal that created
    the ``BlockPublicAccessConfiguration`` using the
    ``PutBlockPublicAccessConfiguration`` action as well as the date and
    time that the configuration was created. Each time a configuration for
    block public access is updated, Amazon EMR updates this metadata.
    """

    CreationDateTime: Date
    CreatedByArn: ArnType


class ScriptBootstrapActionConfig(TypedDict, total=False):
    """Configuration of the script to run during a bootstrap action."""

    Path: XmlString
    Args: Optional[XmlStringList]


class BootstrapActionConfig(TypedDict, total=False):
    """Configuration of a bootstrap action."""

    Name: XmlStringMaxLen256
    ScriptBootstrapAction: ScriptBootstrapActionConfig


BootstrapActionConfigList = List[BootstrapActionConfig]


class BootstrapActionDetail(TypedDict, total=False):
    """Reports the configuration of a bootstrap action in a cluster (job flow)."""

    BootstrapActionConfig: Optional[BootstrapActionConfig]


BootstrapActionDetailList = List[BootstrapActionDetail]


class CancelStepsInfo(TypedDict, total=False):
    """Specification of the status of a CancelSteps request. Available only in
    Amazon EMR version 4.8.0 and later, excluding version 5.0.0.
    """

    StepId: Optional[StepId]
    Status: Optional[CancelStepsRequestStatus]
    Reason: Optional[String]


CancelStepsInfoList = List[CancelStepsInfo]


class CancelStepsInput(ServiceRequest):
    """The input argument to the CancelSteps operation."""

    ClusterId: XmlStringMaxLen256
    StepIds: StepIdsList
    StepCancellationOption: Optional[StepCancellationOption]


class CancelStepsOutput(TypedDict, total=False):
    """The output for the CancelSteps operation."""

    CancelStepsInfoList: Optional[CancelStepsInfoList]


class PlacementGroupConfig(TypedDict, total=False):
    """Placement group configuration for an Amazon EMR cluster. The
    configuration specifies the placement strategy that can be applied to
    instance roles during cluster creation.

    To use this configuration, consider attaching managed policy
    AmazonElasticMapReducePlacementGroupPolicy to the EMR role.
    """

    InstanceRole: InstanceRoleType
    PlacementStrategy: Optional[PlacementGroupStrategy]


PlacementGroupConfigList = List[PlacementGroupConfig]


class KerberosAttributes(TypedDict, total=False):
    """Attributes for Kerberos configuration when Kerberos authentication is
    enabled using a security configuration. For more information see `Use
    Kerberos
    Authentication <https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-kerberos.html>`__
    in the *Amazon EMR Management Guide*.
    """

    Realm: XmlStringMaxLen256
    KdcAdminPassword: XmlStringMaxLen256
    CrossRealmTrustPrincipalPassword: Optional[XmlStringMaxLen256]
    ADDomainJoinUser: Optional[XmlStringMaxLen256]
    ADDomainJoinPassword: Optional[XmlStringMaxLen256]


XmlStringMaxLen256List = List[XmlStringMaxLen256]


class Ec2InstanceAttributes(TypedDict, total=False):
    """Provides information about the EC2 instances in a cluster grouped by
    category. For example, key name, subnet ID, IAM instance profile, and so
    on.
    """

    Ec2KeyName: Optional[String]
    Ec2SubnetId: Optional[String]
    RequestedEc2SubnetIds: Optional[XmlStringMaxLen256List]
    Ec2AvailabilityZone: Optional[String]
    RequestedEc2AvailabilityZones: Optional[XmlStringMaxLen256List]
    IamInstanceProfile: Optional[String]
    EmrManagedMasterSecurityGroup: Optional[String]
    EmrManagedSlaveSecurityGroup: Optional[String]
    ServiceAccessSecurityGroup: Optional[String]
    AdditionalMasterSecurityGroups: Optional[StringList]
    AdditionalSlaveSecurityGroups: Optional[StringList]


class ClusterTimeline(TypedDict, total=False):
    """Represents the timeline of the cluster's lifecycle."""

    CreationDateTime: Optional[Date]
    ReadyDateTime: Optional[Date]
    EndDateTime: Optional[Date]


class ClusterStateChangeReason(TypedDict, total=False):
    """The reason that the cluster changed to its current state."""

    Code: Optional[ClusterStateChangeReasonCode]
    Message: Optional[String]


class ClusterStatus(TypedDict, total=False):
    """The detailed status of the cluster."""

    State: Optional[ClusterState]
    StateChangeReason: Optional[ClusterStateChangeReason]
    Timeline: Optional[ClusterTimeline]


class Cluster(TypedDict, total=False):
    """The detailed description of the cluster."""

    Id: Optional[ClusterId]
    Name: Optional[String]
    Status: Optional[ClusterStatus]
    Ec2InstanceAttributes: Optional[Ec2InstanceAttributes]
    InstanceCollectionType: Optional[InstanceCollectionType]
    LogUri: Optional[String]
    LogEncryptionKmsKeyId: Optional[String]
    RequestedAmiVersion: Optional[String]
    RunningAmiVersion: Optional[String]
    ReleaseLabel: Optional[String]
    AutoTerminate: Optional[Boolean]
    TerminationProtected: Optional[Boolean]
    VisibleToAllUsers: Optional[Boolean]
    Applications: Optional[ApplicationList]
    Tags: Optional[TagList]
    ServiceRole: Optional[String]
    NormalizedInstanceHours: Optional[Integer]
    MasterPublicDnsName: Optional[String]
    Configurations: Optional[ConfigurationList]
    SecurityConfiguration: Optional[XmlString]
    AutoScalingRole: Optional[XmlString]
    ScaleDownBehavior: Optional[ScaleDownBehavior]
    CustomAmiId: Optional[XmlStringMaxLen256]
    EbsRootVolumeSize: Optional[Integer]
    RepoUpgradeOnBoot: Optional[RepoUpgradeOnBoot]
    KerberosAttributes: Optional[KerberosAttributes]
    ClusterArn: Optional[ArnType]
    OutpostArn: Optional[OptionalArnType]
    StepConcurrencyLevel: Optional[Integer]
    PlacementGroups: Optional[PlacementGroupConfigList]
    OSReleaseLabel: Optional[String]


ClusterStateList = List[ClusterState]


class ClusterSummary(TypedDict, total=False):
    """The summary description of the cluster."""

    Id: Optional[ClusterId]
    Name: Optional[String]
    Status: Optional[ClusterStatus]
    NormalizedInstanceHours: Optional[Integer]
    ClusterArn: Optional[ArnType]
    OutpostArn: Optional[OptionalArnType]


ClusterSummaryList = List[ClusterSummary]


class Command(TypedDict, total=False):
    """An entity describing an executable that runs on a cluster."""

    Name: Optional[String]
    ScriptPath: Optional[String]
    Args: Optional[StringList]


CommandList = List[Command]


class ComputeLimits(TypedDict, total=False):
    """The EC2 unit limits for a managed scaling policy. The managed scaling
    activity of a cluster can not be above or below these limits. The limit
    only applies to the core and task nodes. The master node cannot be
    scaled after initial configuration.
    """

    UnitType: ComputeLimitsUnitType
    MinimumCapacityUnits: Integer
    MaximumCapacityUnits: Integer
    MaximumOnDemandCapacityUnits: Optional[Integer]
    MaximumCoreCapacityUnits: Optional[Integer]


class CreateSecurityConfigurationInput(ServiceRequest):
    Name: XmlString
    SecurityConfiguration: String


class CreateSecurityConfigurationOutput(TypedDict, total=False):
    Name: XmlString
    CreationDateTime: Date


SubnetIdList = List[String]


class CreateStudioInput(ServiceRequest):
    Name: XmlStringMaxLen256
    Description: Optional[XmlStringMaxLen256]
    AuthMode: AuthMode
    VpcId: XmlStringMaxLen256
    SubnetIds: SubnetIdList
    ServiceRole: XmlString
    UserRole: Optional[XmlString]
    WorkspaceSecurityGroupId: XmlStringMaxLen256
    EngineSecurityGroupId: XmlStringMaxLen256
    DefaultS3Location: XmlString
    IdpAuthUrl: Optional[XmlString]
    IdpRelayStateParameterName: Optional[XmlStringMaxLen256]
    Tags: Optional[TagList]


class CreateStudioOutput(TypedDict, total=False):
    StudioId: Optional[XmlStringMaxLen256]
    Url: Optional[XmlString]


class CreateStudioSessionMappingInput(ServiceRequest):
    StudioId: XmlStringMaxLen256
    IdentityId: Optional[XmlStringMaxLen256]
    IdentityName: Optional[XmlStringMaxLen256]
    IdentityType: IdentityType
    SessionPolicyArn: XmlStringMaxLen256


class DeleteSecurityConfigurationInput(ServiceRequest):
    Name: XmlString


class DeleteSecurityConfigurationOutput(TypedDict, total=False):
    pass


class DeleteStudioInput(ServiceRequest):
    StudioId: XmlStringMaxLen256


class DeleteStudioSessionMappingInput(ServiceRequest):
    StudioId: XmlStringMaxLen256
    IdentityId: Optional[XmlStringMaxLen256]
    IdentityName: Optional[XmlStringMaxLen256]
    IdentityType: IdentityType


class DescribeClusterInput(ServiceRequest):
    """This input determines which cluster to describe."""

    ClusterId: ClusterId


class DescribeClusterOutput(TypedDict, total=False):
    """This output contains the description of the cluster."""

    Cluster: Optional[Cluster]


JobFlowExecutionStateList = List[JobFlowExecutionState]


class DescribeJobFlowsInput(ServiceRequest):
    """The input for the DescribeJobFlows operation."""

    CreatedAfter: Optional[Date]
    CreatedBefore: Optional[Date]
    JobFlowIds: Optional[XmlStringList]
    JobFlowStates: Optional[JobFlowExecutionStateList]


SupportedProductsList = List[XmlStringMaxLen256]


class StepExecutionStatusDetail(TypedDict, total=False):
    """The execution state of a step."""

    State: StepExecutionState
    CreationDateTime: Date
    StartDateTime: Optional[Date]
    EndDateTime: Optional[Date]
    LastStateChangeReason: Optional[XmlString]


class StepDetail(TypedDict, total=False):
    """Combines the execution state and configuration of a step."""

    StepConfig: StepConfig
    ExecutionStatusDetail: StepExecutionStatusDetail


StepDetailList = List[StepDetail]


class PlacementType(TypedDict, total=False):
    """The Amazon EC2 Availability Zone configuration of the cluster (job
    flow).
    """

    AvailabilityZone: Optional[XmlString]
    AvailabilityZones: Optional[XmlStringMaxLen256List]


class InstanceGroupDetail(TypedDict, total=False):
    """Detailed information about an instance group."""

    InstanceGroupId: Optional[XmlStringMaxLen256]
    Name: Optional[XmlStringMaxLen256]
    Market: MarketType
    InstanceRole: InstanceRoleType
    BidPrice: Optional[XmlStringMaxLen256]
    InstanceType: InstanceType
    InstanceRequestCount: Integer
    InstanceRunningCount: Integer
    State: InstanceGroupState
    LastStateChangeReason: Optional[XmlString]
    CreationDateTime: Date
    StartDateTime: Optional[Date]
    ReadyDateTime: Optional[Date]
    EndDateTime: Optional[Date]
    CustomAmiId: Optional[XmlStringMaxLen256]


InstanceGroupDetailList = List[InstanceGroupDetail]


class JobFlowInstancesDetail(TypedDict, total=False):
    """Specify the type of Amazon EC2 instances that the cluster (job flow)
    runs on.
    """

    MasterInstanceType: InstanceType
    MasterPublicDnsName: Optional[XmlString]
    MasterInstanceId: Optional[XmlString]
    SlaveInstanceType: InstanceType
    InstanceCount: Integer
    InstanceGroups: Optional[InstanceGroupDetailList]
    NormalizedInstanceHours: Optional[Integer]
    Ec2KeyName: Optional[XmlStringMaxLen256]
    Ec2SubnetId: Optional[XmlStringMaxLen256]
    Placement: Optional[PlacementType]
    KeepJobFlowAliveWhenNoSteps: Optional[Boolean]
    TerminationProtected: Optional[Boolean]
    HadoopVersion: Optional[XmlStringMaxLen256]


class JobFlowExecutionStatusDetail(TypedDict, total=False):
    """Describes the status of the cluster (job flow)."""

    State: JobFlowExecutionState
    CreationDateTime: Date
    StartDateTime: Optional[Date]
    ReadyDateTime: Optional[Date]
    EndDateTime: Optional[Date]
    LastStateChangeReason: Optional[XmlString]


class JobFlowDetail(TypedDict, total=False):
    """A description of a cluster (job flow)."""

    JobFlowId: XmlStringMaxLen256
    Name: XmlStringMaxLen256
    LogUri: Optional[XmlString]
    LogEncryptionKmsKeyId: Optional[XmlString]
    AmiVersion: Optional[XmlStringMaxLen256]
    ExecutionStatusDetail: JobFlowExecutionStatusDetail
    Instances: JobFlowInstancesDetail
    Steps: Optional[StepDetailList]
    BootstrapActions: Optional[BootstrapActionDetailList]
    SupportedProducts: Optional[SupportedProductsList]
    VisibleToAllUsers: Optional[Boolean]
    JobFlowRole: Optional[XmlString]
    ServiceRole: Optional[XmlString]
    AutoScalingRole: Optional[XmlString]
    ScaleDownBehavior: Optional[ScaleDownBehavior]


JobFlowDetailList = List[JobFlowDetail]


class DescribeJobFlowsOutput(TypedDict, total=False):
    """The output for the DescribeJobFlows operation."""

    JobFlows: Optional[JobFlowDetailList]


class DescribeNotebookExecutionInput(ServiceRequest):
    NotebookExecutionId: XmlStringMaxLen256


class ExecutionEngineConfig(TypedDict, total=False):
    """Specifies the execution engine (cluster) to run the notebook and perform
    the notebook execution, for example, an EMR cluster.
    """

    Id: XmlStringMaxLen256
    Type: Optional[ExecutionEngineType]
    MasterInstanceSecurityGroupId: Optional[XmlStringMaxLen256]


class NotebookExecution(TypedDict, total=False):
    """A notebook execution. An execution is a specific instance that an EMR
    Notebook is run using the ``StartNotebookExecution`` action.
    """

    NotebookExecutionId: Optional[XmlStringMaxLen256]
    EditorId: Optional[XmlStringMaxLen256]
    ExecutionEngine: Optional[ExecutionEngineConfig]
    NotebookExecutionName: Optional[XmlStringMaxLen256]
    NotebookParams: Optional[XmlString]
    Status: Optional[NotebookExecutionStatus]
    StartTime: Optional[Date]
    EndTime: Optional[Date]
    Arn: Optional[XmlStringMaxLen256]
    OutputNotebookURI: Optional[XmlString]
    LastStateChangeReason: Optional[XmlString]
    NotebookInstanceSecurityGroupId: Optional[XmlStringMaxLen256]
    Tags: Optional[TagList]


class DescribeNotebookExecutionOutput(TypedDict, total=False):
    NotebookExecution: Optional[NotebookExecution]


class DescribeReleaseLabelInput(ServiceRequest):
    ReleaseLabel: Optional[String]
    NextToken: Optional[String]
    MaxResults: Optional[MaxResultsNumber]


class OSRelease(TypedDict, total=False):
    """The Amazon Linux release specified for a cluster in the RunJobFlow
    request.
    """

    Label: Optional[String]


OSReleaseList = List[OSRelease]


class SimplifiedApplication(TypedDict, total=False):
    """The returned release label application names or versions."""

    Name: Optional[String]
    Version: Optional[String]


SimplifiedApplicationList = List[SimplifiedApplication]


class DescribeReleaseLabelOutput(TypedDict, total=False):
    ReleaseLabel: Optional[String]
    Applications: Optional[SimplifiedApplicationList]
    NextToken: Optional[String]
    AvailableOSReleases: Optional[OSReleaseList]


class DescribeSecurityConfigurationInput(ServiceRequest):
    Name: XmlString


class DescribeSecurityConfigurationOutput(TypedDict, total=False):
    Name: Optional[XmlString]
    SecurityConfiguration: Optional[String]
    CreationDateTime: Optional[Date]


class DescribeStepInput(ServiceRequest):
    """This input determines which step to describe."""

    ClusterId: ClusterId
    StepId: StepId


class StepTimeline(TypedDict, total=False):
    """The timeline of the cluster step lifecycle."""

    CreationDateTime: Optional[Date]
    StartDateTime: Optional[Date]
    EndDateTime: Optional[Date]


class FailureDetails(TypedDict, total=False):
    """The details of the step failure. The service attempts to detect the root
    cause for many common failures.
    """

    Reason: Optional[String]
    Message: Optional[String]
    LogFile: Optional[String]


class StepStateChangeReason(TypedDict, total=False):
    """The details of the step state change reason."""

    Code: Optional[StepStateChangeReasonCode]
    Message: Optional[String]


class StepStatus(TypedDict, total=False):
    """The execution status details of the cluster step."""

    State: Optional[StepState]
    StateChangeReason: Optional[StepStateChangeReason]
    FailureDetails: Optional[FailureDetails]
    Timeline: Optional[StepTimeline]


class HadoopStepConfig(TypedDict, total=False):
    """A cluster step consisting of a JAR file whose main function will be
    executed. The main function submits a job for Hadoop to execute and
    waits for the job to finish or fail.
    """

    Jar: Optional[String]
    Properties: Optional[StringMap]
    MainClass: Optional[String]
    Args: Optional[StringList]


class Step(TypedDict, total=False):
    """This represents a step in a cluster."""

    Id: Optional[StepId]
    Name: Optional[String]
    Config: Optional[HadoopStepConfig]
    ActionOnFailure: Optional[ActionOnFailure]
    Status: Optional[StepStatus]


class DescribeStepOutput(TypedDict, total=False):
    """This output contains the description of the cluster step."""

    Step: Optional[Step]


class DescribeStudioInput(ServiceRequest):
    StudioId: XmlStringMaxLen256


class Studio(TypedDict, total=False):
    """Details for an Amazon EMR Studio including ID, creation time, name, and
    so on.
    """

    StudioId: Optional[XmlStringMaxLen256]
    StudioArn: Optional[XmlStringMaxLen256]
    Name: Optional[XmlStringMaxLen256]
    Description: Optional[XmlStringMaxLen256]
    AuthMode: Optional[AuthMode]
    VpcId: Optional[XmlStringMaxLen256]
    SubnetIds: Optional[SubnetIdList]
    ServiceRole: Optional[XmlString]
    UserRole: Optional[XmlString]
    WorkspaceSecurityGroupId: Optional[XmlStringMaxLen256]
    EngineSecurityGroupId: Optional[XmlStringMaxLen256]
    Url: Optional[XmlString]
    CreationTime: Optional[Date]
    DefaultS3Location: Optional[XmlString]
    IdpAuthUrl: Optional[XmlString]
    IdpRelayStateParameterName: Optional[XmlStringMaxLen256]
    Tags: Optional[TagList]


class DescribeStudioOutput(TypedDict, total=False):
    Studio: Optional[Studio]


EC2InstanceIdsList = List[InstanceId]
EC2InstanceIdsToTerminateList = List[InstanceId]


class EbsBlockDevice(TypedDict, total=False):
    """Configuration of requested EBS block device associated with the instance
    group.
    """

    VolumeSpecification: Optional[VolumeSpecification]
    Device: Optional[String]


EbsBlockDeviceList = List[EbsBlockDevice]


class EbsVolume(TypedDict, total=False):
    """EBS block device that's attached to an EC2 instance."""

    Device: Optional[String]
    VolumeId: Optional[String]


EbsVolumeList = List[EbsVolume]


class GetAutoTerminationPolicyInput(ServiceRequest):
    ClusterId: ClusterId


class GetAutoTerminationPolicyOutput(TypedDict, total=False):
    AutoTerminationPolicy: Optional[AutoTerminationPolicy]


class GetBlockPublicAccessConfigurationInput(ServiceRequest):
    pass


class GetBlockPublicAccessConfigurationOutput(TypedDict, total=False):
    BlockPublicAccessConfiguration: BlockPublicAccessConfiguration
    BlockPublicAccessConfigurationMetadata: BlockPublicAccessConfigurationMetadata


class GetManagedScalingPolicyInput(ServiceRequest):
    ClusterId: ClusterId


class ManagedScalingPolicy(TypedDict, total=False):
    """Managed scaling policy for an Amazon EMR cluster. The policy specifies
    the limits for resources that can be added or terminated from a cluster.
    The policy only applies to the core and task nodes. The master node
    cannot be scaled after initial configuration.
    """

    ComputeLimits: Optional[ComputeLimits]


class GetManagedScalingPolicyOutput(TypedDict, total=False):
    ManagedScalingPolicy: Optional[ManagedScalingPolicy]


class GetStudioSessionMappingInput(ServiceRequest):
    StudioId: XmlStringMaxLen256
    IdentityId: Optional[XmlStringMaxLen256]
    IdentityName: Optional[XmlStringMaxLen256]
    IdentityType: IdentityType


class SessionMappingDetail(TypedDict, total=False):
    """Details for an Amazon EMR Studio session mapping including creation
    time, user or group ID, Studio ID, and so on.
    """

    StudioId: Optional[XmlStringMaxLen256]
    IdentityId: Optional[XmlStringMaxLen256]
    IdentityName: Optional[XmlStringMaxLen256]
    IdentityType: Optional[IdentityType]
    SessionPolicyArn: Optional[XmlStringMaxLen256]
    CreationTime: Optional[Date]
    LastModifiedTime: Optional[Date]


class GetStudioSessionMappingOutput(TypedDict, total=False):
    SessionMapping: Optional[SessionMappingDetail]


class InstanceTimeline(TypedDict, total=False):
    """The timeline of the instance lifecycle."""

    CreationDateTime: Optional[Date]
    ReadyDateTime: Optional[Date]
    EndDateTime: Optional[Date]


class InstanceStateChangeReason(TypedDict, total=False):
    """The details of the status change reason for the instance."""

    Code: Optional[InstanceStateChangeReasonCode]
    Message: Optional[String]


class InstanceStatus(TypedDict, total=False):
    """The instance status details."""

    State: Optional[InstanceState]
    StateChangeReason: Optional[InstanceStateChangeReason]
    Timeline: Optional[InstanceTimeline]


class Instance(TypedDict, total=False):
    """Represents an EC2 instance provisioned as part of cluster."""

    Id: Optional[InstanceId]
    Ec2InstanceId: Optional[InstanceId]
    PublicDnsName: Optional[String]
    PublicIpAddress: Optional[String]
    PrivateDnsName: Optional[String]
    PrivateIpAddress: Optional[String]
    Status: Optional[InstanceStatus]
    InstanceGroupId: Optional[String]
    InstanceFleetId: Optional[InstanceFleetId]
    Market: Optional[MarketType]
    InstanceType: Optional[InstanceType]
    EbsVolumes: Optional[EbsVolumeList]


class InstanceTypeSpecification(TypedDict, total=False):
    """The configuration specification for each instance type in an instance
    fleet.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions.
    """

    InstanceType: Optional[InstanceType]
    WeightedCapacity: Optional[WholeNumber]
    BidPrice: Optional[XmlStringMaxLen256]
    BidPriceAsPercentageOfOnDemandPrice: Optional[NonNegativeDouble]
    Configurations: Optional[ConfigurationList]
    EbsBlockDevices: Optional[EbsBlockDeviceList]
    EbsOptimized: Optional[BooleanObject]
    CustomAmiId: Optional[XmlStringMaxLen256]


InstanceTypeSpecificationList = List[InstanceTypeSpecification]


class InstanceFleetTimeline(TypedDict, total=False):
    """Provides historical timestamps for the instance fleet, including the
    time of creation, the time it became ready to run jobs, and the time of
    termination.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions.
    """

    CreationDateTime: Optional[Date]
    ReadyDateTime: Optional[Date]
    EndDateTime: Optional[Date]


class InstanceFleetStateChangeReason(TypedDict, total=False):
    """Provides status change reason details for the instance fleet.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions.
    """

    Code: Optional[InstanceFleetStateChangeReasonCode]
    Message: Optional[String]


class InstanceFleetStatus(TypedDict, total=False):
    """The status of the instance fleet.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions.
    """

    State: Optional[InstanceFleetState]
    StateChangeReason: Optional[InstanceFleetStateChangeReason]
    Timeline: Optional[InstanceFleetTimeline]


class InstanceFleet(TypedDict, total=False):
    """Describes an instance fleet, which is a group of EC2 instances that host
    a particular node type (master, core, or task) in an Amazon EMR cluster.
    Instance fleets can consist of a mix of instance types and On-Demand and
    Spot Instances, which are provisioned to meet a defined target capacity.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions.
    """

    Id: Optional[InstanceFleetId]
    Name: Optional[XmlStringMaxLen256]
    Status: Optional[InstanceFleetStatus]
    InstanceFleetType: Optional[InstanceFleetType]
    TargetOnDemandCapacity: Optional[WholeNumber]
    TargetSpotCapacity: Optional[WholeNumber]
    ProvisionedOnDemandCapacity: Optional[WholeNumber]
    ProvisionedSpotCapacity: Optional[WholeNumber]
    InstanceTypeSpecifications: Optional[InstanceTypeSpecificationList]
    LaunchSpecifications: Optional[InstanceFleetProvisioningSpecifications]


InstanceFleetConfigList = List[InstanceFleetConfig]
InstanceFleetList = List[InstanceFleet]


class InstanceFleetModifyConfig(TypedDict, total=False):
    """Configuration parameters for an instance fleet modification request.

    The instance fleet configuration is available only in Amazon EMR
    versions 4.8.0 and later, excluding 5.0.x versions.
    """

    InstanceFleetId: InstanceFleetId
    TargetOnDemandCapacity: Optional[WholeNumber]
    TargetSpotCapacity: Optional[WholeNumber]


class InstanceResizePolicy(TypedDict, total=False):
    """Custom policy for requesting termination protection or termination of
    specific instances when shrinking an instance group.
    """

    InstancesToTerminate: Optional[EC2InstanceIdsList]
    InstancesToProtect: Optional[EC2InstanceIdsList]
    InstanceTerminationTimeout: Optional[Integer]


class ShrinkPolicy(TypedDict, total=False):
    """Policy for customizing shrink operations. Allows configuration of
    decommissioning timeout and targeted instance shrinking.
    """

    DecommissionTimeout: Optional[Integer]
    InstanceResizePolicy: Optional[InstanceResizePolicy]


class InstanceGroupTimeline(TypedDict, total=False):
    """The timeline of the instance group lifecycle."""

    CreationDateTime: Optional[Date]
    ReadyDateTime: Optional[Date]
    EndDateTime: Optional[Date]


class InstanceGroupStateChangeReason(TypedDict, total=False):
    """The status change reason details for the instance group."""

    Code: Optional[InstanceGroupStateChangeReasonCode]
    Message: Optional[String]


class InstanceGroupStatus(TypedDict, total=False):
    """The details of the instance group status."""

    State: Optional[InstanceGroupState]
    StateChangeReason: Optional[InstanceGroupStateChangeReason]
    Timeline: Optional[InstanceGroupTimeline]


class InstanceGroup(TypedDict, total=False):
    """This entity represents an instance group, which is a group of instances
    that have common purpose. For example, CORE instance group is used for
    HDFS.
    """

    Id: Optional[InstanceGroupId]
    Name: Optional[String]
    Market: Optional[MarketType]
    InstanceGroupType: Optional[InstanceGroupType]
    BidPrice: Optional[String]
    InstanceType: Optional[InstanceType]
    RequestedInstanceCount: Optional[Integer]
    RunningInstanceCount: Optional[Integer]
    Status: Optional[InstanceGroupStatus]
    Configurations: Optional[ConfigurationList]
    ConfigurationsVersion: Optional[Long]
    LastSuccessfullyAppliedConfigurations: Optional[ConfigurationList]
    LastSuccessfullyAppliedConfigurationsVersion: Optional[Long]
    EbsBlockDevices: Optional[EbsBlockDeviceList]
    EbsOptimized: Optional[BooleanObject]
    ShrinkPolicy: Optional[ShrinkPolicy]
    AutoScalingPolicy: Optional[AutoScalingPolicyDescription]
    CustomAmiId: Optional[XmlStringMaxLen256]


InstanceGroupList = List[InstanceGroup]


class InstanceGroupModifyConfig(TypedDict, total=False):
    """Modify the size or configurations of an instance group."""

    InstanceGroupId: XmlStringMaxLen256
    InstanceCount: Optional[Integer]
    EC2InstanceIdsToTerminate: Optional[EC2InstanceIdsToTerminateList]
    ShrinkPolicy: Optional[ShrinkPolicy]
    ReconfigurationType: Optional[ReconfigurationType]
    Configurations: Optional[ConfigurationList]


InstanceGroupModifyConfigList = List[InstanceGroupModifyConfig]
InstanceGroupTypeList = List[InstanceGroupType]
InstanceList = List[Instance]
InstanceStateList = List[InstanceState]
SecurityGroupsList = List[XmlStringMaxLen256]


class JobFlowInstancesConfig(TypedDict, total=False):
    """A description of the Amazon EC2 instance on which the cluster (job flow)
    runs. A valid JobFlowInstancesConfig must contain either InstanceGroups
    or InstanceFleets. They cannot be used together. You may also have
    MasterInstanceType, SlaveInstanceType, and InstanceCount (all three must
    be present), but we don't recommend this configuration.
    """

    MasterInstanceType: Optional[InstanceType]
    SlaveInstanceType: Optional[InstanceType]
    InstanceCount: Optional[Integer]
    InstanceGroups: Optional[InstanceGroupConfigList]
    InstanceFleets: Optional[InstanceFleetConfigList]
    Ec2KeyName: Optional[XmlStringMaxLen256]
    Placement: Optional[PlacementType]
    KeepJobFlowAliveWhenNoSteps: Optional[Boolean]
    TerminationProtected: Optional[Boolean]
    HadoopVersion: Optional[XmlStringMaxLen256]
    Ec2SubnetId: Optional[XmlStringMaxLen256]
    Ec2SubnetIds: Optional[XmlStringMaxLen256List]
    EmrManagedMasterSecurityGroup: Optional[XmlStringMaxLen256]
    EmrManagedSlaveSecurityGroup: Optional[XmlStringMaxLen256]
    ServiceAccessSecurityGroup: Optional[XmlStringMaxLen256]
    AdditionalMasterSecurityGroups: Optional[SecurityGroupsList]
    AdditionalSlaveSecurityGroups: Optional[SecurityGroupsList]


class ListBootstrapActionsInput(ServiceRequest):
    """This input determines which bootstrap actions to retrieve."""

    ClusterId: ClusterId
    Marker: Optional[Marker]


class ListBootstrapActionsOutput(TypedDict, total=False):
    """This output contains the bootstrap actions detail."""

    BootstrapActions: Optional[CommandList]
    Marker: Optional[Marker]


class ListClustersInput(ServiceRequest):
    """This input determines how the ListClusters action filters the list of
    clusters that it returns.
    """

    CreatedAfter: Optional[Date]
    CreatedBefore: Optional[Date]
    ClusterStates: Optional[ClusterStateList]
    Marker: Optional[Marker]


class ListClustersOutput(TypedDict, total=False):
    """This contains a ClusterSummaryList with the cluster details; for
    example, the cluster IDs, names, and status.
    """

    Clusters: Optional[ClusterSummaryList]
    Marker: Optional[Marker]


class ListInstanceFleetsInput(ServiceRequest):
    ClusterId: ClusterId
    Marker: Optional[Marker]


class ListInstanceFleetsOutput(TypedDict, total=False):
    InstanceFleets: Optional[InstanceFleetList]
    Marker: Optional[Marker]


class ListInstanceGroupsInput(ServiceRequest):
    """This input determines which instance groups to retrieve."""

    ClusterId: ClusterId
    Marker: Optional[Marker]


class ListInstanceGroupsOutput(TypedDict, total=False):
    """This input determines which instance groups to retrieve."""

    InstanceGroups: Optional[InstanceGroupList]
    Marker: Optional[Marker]


class ListInstancesInput(ServiceRequest):
    """This input determines which instances to list."""

    ClusterId: ClusterId
    InstanceGroupId: Optional[InstanceGroupId]
    InstanceGroupTypes: Optional[InstanceGroupTypeList]
    InstanceFleetId: Optional[InstanceFleetId]
    InstanceFleetType: Optional[InstanceFleetType]
    InstanceStates: Optional[InstanceStateList]
    Marker: Optional[Marker]


class ListInstancesOutput(TypedDict, total=False):
    """This output contains the list of instances."""

    Instances: Optional[InstanceList]
    Marker: Optional[Marker]


class ListNotebookExecutionsInput(ServiceRequest):
    EditorId: Optional[XmlStringMaxLen256]
    Status: Optional[NotebookExecutionStatus]
    From: Optional[Date]
    To: Optional[Date]
    Marker: Optional[Marker]


class NotebookExecutionSummary(TypedDict, total=False):
    """Details for a notebook execution. The details include information such
    as the unique ID and status of the notebook execution.
    """

    NotebookExecutionId: Optional[XmlStringMaxLen256]
    EditorId: Optional[XmlStringMaxLen256]
    NotebookExecutionName: Optional[XmlStringMaxLen256]
    Status: Optional[NotebookExecutionStatus]
    StartTime: Optional[Date]
    EndTime: Optional[Date]


NotebookExecutionSummaryList = List[NotebookExecutionSummary]


class ListNotebookExecutionsOutput(TypedDict, total=False):
    NotebookExecutions: Optional[NotebookExecutionSummaryList]
    Marker: Optional[Marker]


class ReleaseLabelFilter(TypedDict, total=False):
    """The release label filters by application or version prefix."""

    Prefix: Optional[String]
    Application: Optional[String]


class ListReleaseLabelsInput(ServiceRequest):
    Filters: Optional[ReleaseLabelFilter]
    NextToken: Optional[String]
    MaxResults: Optional[MaxResultsNumber]


class ListReleaseLabelsOutput(TypedDict, total=False):
    ReleaseLabels: Optional[StringList]
    NextToken: Optional[String]


class ListSecurityConfigurationsInput(ServiceRequest):
    Marker: Optional[Marker]


class SecurityConfigurationSummary(TypedDict, total=False):
    """The creation date and time, and name, of a security configuration."""

    Name: Optional[XmlString]
    CreationDateTime: Optional[Date]


SecurityConfigurationList = List[SecurityConfigurationSummary]


class ListSecurityConfigurationsOutput(TypedDict, total=False):
    SecurityConfigurations: Optional[SecurityConfigurationList]
    Marker: Optional[Marker]


StepStateList = List[StepState]


class ListStepsInput(ServiceRequest):
    """This input determines which steps to list."""

    ClusterId: ClusterId
    StepStates: Optional[StepStateList]
    StepIds: Optional[XmlStringList]
    Marker: Optional[Marker]


class StepSummary(TypedDict, total=False):
    """The summary of the cluster step."""

    Id: Optional[StepId]
    Name: Optional[String]
    Config: Optional[HadoopStepConfig]
    ActionOnFailure: Optional[ActionOnFailure]
    Status: Optional[StepStatus]


StepSummaryList = List[StepSummary]


class ListStepsOutput(TypedDict, total=False):
    """This output contains the list of steps returned in reverse order. This
    means that the last step is the first element in the list.
    """

    Steps: Optional[StepSummaryList]
    Marker: Optional[Marker]


class ListStudioSessionMappingsInput(ServiceRequest):
    StudioId: Optional[XmlStringMaxLen256]
    IdentityType: Optional[IdentityType]
    Marker: Optional[Marker]


class SessionMappingSummary(TypedDict, total=False):
    """Details for an Amazon EMR Studio session mapping. The details do not
    include the time the session mapping was last modified.
    """

    StudioId: Optional[XmlStringMaxLen256]
    IdentityId: Optional[XmlStringMaxLen256]
    IdentityName: Optional[XmlStringMaxLen256]
    IdentityType: Optional[IdentityType]
    SessionPolicyArn: Optional[XmlStringMaxLen256]
    CreationTime: Optional[Date]


SessionMappingSummaryList = List[SessionMappingSummary]


class ListStudioSessionMappingsOutput(TypedDict, total=False):
    SessionMappings: Optional[SessionMappingSummaryList]
    Marker: Optional[Marker]


class ListStudiosInput(ServiceRequest):
    Marker: Optional[Marker]


class StudioSummary(TypedDict, total=False):
    """Details for an Amazon EMR Studio, including ID, Name, VPC, and
    Description. The details do not include subnets, IAM roles, security
    groups, or tags associated with the Studio.
    """

    StudioId: Optional[XmlStringMaxLen256]
    Name: Optional[XmlStringMaxLen256]
    VpcId: Optional[XmlStringMaxLen256]
    Description: Optional[XmlStringMaxLen256]
    Url: Optional[XmlStringMaxLen256]
    AuthMode: Optional[AuthMode]
    CreationTime: Optional[Date]


StudioSummaryList = List[StudioSummary]


class ListStudiosOutput(TypedDict, total=False):
    Studios: Optional[StudioSummaryList]
    Marker: Optional[Marker]


class ModifyClusterInput(ServiceRequest):
    ClusterId: String
    StepConcurrencyLevel: Optional[Integer]


class ModifyClusterOutput(TypedDict, total=False):
    StepConcurrencyLevel: Optional[Integer]


class ModifyInstanceFleetInput(ServiceRequest):
    ClusterId: ClusterId
    InstanceFleet: InstanceFleetModifyConfig


class ModifyInstanceGroupsInput(ServiceRequest):
    """Change the size of some instance groups."""

    ClusterId: Optional[ClusterId]
    InstanceGroups: Optional[InstanceGroupModifyConfigList]


class SupportedProductConfig(TypedDict, total=False):
    """The list of supported product configurations that allow user-supplied
    arguments. EMR accepts these arguments and forwards them to the
    corresponding installation script as bootstrap action arguments.
    """

    Name: Optional[XmlStringMaxLen256]
    Args: Optional[XmlStringList]


NewSupportedProductsList = List[SupportedProductConfig]


class PutAutoScalingPolicyInput(ServiceRequest):
    ClusterId: ClusterId
    InstanceGroupId: InstanceGroupId
    AutoScalingPolicy: AutoScalingPolicy


class PutAutoScalingPolicyOutput(TypedDict, total=False):
    ClusterId: Optional[ClusterId]
    InstanceGroupId: Optional[InstanceGroupId]
    AutoScalingPolicy: Optional[AutoScalingPolicyDescription]
    ClusterArn: Optional[ArnType]


class PutAutoTerminationPolicyInput(ServiceRequest):
    ClusterId: ClusterId
    AutoTerminationPolicy: Optional[AutoTerminationPolicy]


class PutAutoTerminationPolicyOutput(TypedDict, total=False):
    pass


class PutBlockPublicAccessConfigurationInput(ServiceRequest):
    BlockPublicAccessConfiguration: BlockPublicAccessConfiguration


class PutBlockPublicAccessConfigurationOutput(TypedDict, total=False):
    pass


class PutManagedScalingPolicyInput(ServiceRequest):
    ClusterId: ClusterId
    ManagedScalingPolicy: ManagedScalingPolicy


class PutManagedScalingPolicyOutput(TypedDict, total=False):
    pass


class RemoveAutoScalingPolicyInput(ServiceRequest):
    ClusterId: ClusterId
    InstanceGroupId: InstanceGroupId


class RemoveAutoScalingPolicyOutput(TypedDict, total=False):
    pass


class RemoveAutoTerminationPolicyInput(ServiceRequest):
    ClusterId: ClusterId


class RemoveAutoTerminationPolicyOutput(TypedDict, total=False):
    pass


class RemoveManagedScalingPolicyInput(ServiceRequest):
    ClusterId: ClusterId


class RemoveManagedScalingPolicyOutput(TypedDict, total=False):
    pass


class RemoveTagsInput(ServiceRequest):
    """This input identifies an Amazon EMR resource and a list of tags to
    remove.
    """

    ResourceId: ResourceId
    TagKeys: StringList


class RemoveTagsOutput(TypedDict, total=False):
    """This output indicates the result of removing tags from the resource."""


class RunJobFlowInput(ServiceRequest):
    """Input to the RunJobFlow operation."""

    Name: XmlStringMaxLen256
    LogUri: Optional[XmlString]
    LogEncryptionKmsKeyId: Optional[XmlString]
    AdditionalInfo: Optional[XmlString]
    AmiVersion: Optional[XmlStringMaxLen256]
    ReleaseLabel: Optional[XmlStringMaxLen256]
    Instances: JobFlowInstancesConfig
    Steps: Optional[StepConfigList]
    BootstrapActions: Optional[BootstrapActionConfigList]
    SupportedProducts: Optional[SupportedProductsList]
    NewSupportedProducts: Optional[NewSupportedProductsList]
    Applications: Optional[ApplicationList]
    Configurations: Optional[ConfigurationList]
    VisibleToAllUsers: Optional[Boolean]
    JobFlowRole: Optional[XmlString]
    ServiceRole: Optional[XmlString]
    Tags: Optional[TagList]
    SecurityConfiguration: Optional[XmlString]
    AutoScalingRole: Optional[XmlString]
    ScaleDownBehavior: Optional[ScaleDownBehavior]
    CustomAmiId: Optional[XmlStringMaxLen256]
    EbsRootVolumeSize: Optional[Integer]
    RepoUpgradeOnBoot: Optional[RepoUpgradeOnBoot]
    KerberosAttributes: Optional[KerberosAttributes]
    StepConcurrencyLevel: Optional[Integer]
    ManagedScalingPolicy: Optional[ManagedScalingPolicy]
    PlacementGroupConfigs: Optional[PlacementGroupConfigList]
    AutoTerminationPolicy: Optional[AutoTerminationPolicy]
    OSReleaseLabel: Optional[XmlStringMaxLen256]


class RunJobFlowOutput(TypedDict, total=False):
    """The result of the RunJobFlow operation."""

    JobFlowId: Optional[XmlStringMaxLen256]
    ClusterArn: Optional[ArnType]


class SetTerminationProtectionInput(ServiceRequest):
    """The input argument to the TerminationProtection operation."""

    JobFlowIds: XmlStringList
    TerminationProtected: Boolean


class SetVisibleToAllUsersInput(ServiceRequest):
    """The input to the SetVisibleToAllUsers action."""

    JobFlowIds: XmlStringList
    VisibleToAllUsers: Boolean


class StartNotebookExecutionInput(ServiceRequest):
    EditorId: XmlStringMaxLen256
    RelativePath: XmlString
    NotebookExecutionName: Optional[XmlStringMaxLen256]
    NotebookParams: Optional[XmlString]
    ExecutionEngine: ExecutionEngineConfig
    ServiceRole: XmlString
    NotebookInstanceSecurityGroupId: Optional[XmlStringMaxLen256]
    Tags: Optional[TagList]


class StartNotebookExecutionOutput(TypedDict, total=False):
    NotebookExecutionId: Optional[XmlStringMaxLen256]


class StopNotebookExecutionInput(ServiceRequest):
    NotebookExecutionId: XmlStringMaxLen256


class TerminateJobFlowsInput(ServiceRequest):
    """Input to the TerminateJobFlows operation."""

    JobFlowIds: XmlStringList


class UpdateStudioInput(ServiceRequest):
    StudioId: XmlStringMaxLen256
    Name: Optional[XmlStringMaxLen256]
    Description: Optional[XmlStringMaxLen256]
    SubnetIds: Optional[SubnetIdList]
    DefaultS3Location: Optional[XmlString]


class UpdateStudioSessionMappingInput(ServiceRequest):
    StudioId: XmlStringMaxLen256
    IdentityId: Optional[XmlStringMaxLen256]
    IdentityName: Optional[XmlStringMaxLen256]
    IdentityType: IdentityType
    SessionPolicyArn: XmlStringMaxLen256


class EmrApi:

    service = "emr"
    version = "2009-03-31"

    @handler("AddInstanceFleet")
    def add_instance_fleet(
        self,
        context: RequestContext,
        cluster_id: XmlStringMaxLen256,
        instance_fleet: InstanceFleetConfig,
    ) -> AddInstanceFleetOutput:
        """Adds an instance fleet to a running cluster.

        The instance fleet configuration is available only in Amazon EMR
        versions 4.8.0 and later, excluding 5.0.x.

        :param cluster_id: The unique identifier of the cluster.
        :param instance_fleet: Specifies the configuration of the instance fleet.
        :returns: AddInstanceFleetOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("AddInstanceGroups")
    def add_instance_groups(
        self,
        context: RequestContext,
        instance_groups: InstanceGroupConfigList,
        job_flow_id: XmlStringMaxLen256,
    ) -> AddInstanceGroupsOutput:
        """Adds one or more instance groups to a running cluster.

        :param instance_groups: Instance groups to add.
        :param job_flow_id: Job flow in which to add the instance groups.
        :returns: AddInstanceGroupsOutput
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("AddJobFlowSteps")
    def add_job_flow_steps(
        self, context: RequestContext, job_flow_id: XmlStringMaxLen256, steps: StepConfigList
    ) -> AddJobFlowStepsOutput:
        """AddJobFlowSteps adds new steps to a running cluster. A maximum of 256
        steps are allowed in each job flow.

        If your cluster is long-running (such as a Hive data warehouse) or
        complex, you may require more than 256 steps to process your data. You
        can bypass the 256-step limitation in various ways, including using SSH
        to connect to the master node and submitting queries directly to the
        software running on the master node, such as Hive and Hadoop. For more
        information on how to do this, see `Add More than 256 Steps to a
        Cluster <https://docs.aws.amazon.com/emr/latest/ManagementGuide/AddMoreThan256Steps.html>`__
        in the *Amazon EMR Management Guide*.

        A step specifies the location of a JAR file stored either on the master
        node of the cluster or in Amazon S3. Each step is performed by the main
        function of the main class of the JAR file. The main class can be
        specified either in the manifest of the JAR or by using the MainFunction
        parameter of the step.

        Amazon EMR executes each step in the order listed. For a step to be
        considered complete, the main function must exit with a zero exit code
        and all Hadoop jobs started while the step was running must have
        completed and run successfully.

        You can only add steps to a cluster that is in one of the following
        states: STARTING, BOOTSTRAPPING, RUNNING, or WAITING.

        The string values passed into ``HadoopJarStep`` object cannot exceed a
        total of 10240 characters.

        :param job_flow_id: A string that uniquely identifies the job flow.
        :param steps: A list of StepConfig to be executed by the job flow.
        :returns: AddJobFlowStepsOutput
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("AddTags")
    def add_tags(
        self, context: RequestContext, resource_id: ResourceId, tags: TagList
    ) -> AddTagsOutput:
        """Adds tags to an Amazon EMR resource, such as a cluster or an Amazon EMR
        Studio. Tags make it easier to associate resources in various ways, such
        as grouping clusters to track your Amazon EMR resource allocation costs.
        For more information, see `Tag
        Clusters <https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-tags.html>`__.

        :param resource_id: The Amazon EMR resource identifier to which tags will be added.
        :param tags: A list of tags to associate with a resource.
        :returns: AddTagsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("CancelSteps")
    def cancel_steps(
        self,
        context: RequestContext,
        cluster_id: XmlStringMaxLen256,
        step_ids: StepIdsList,
        step_cancellation_option: StepCancellationOption = None,
    ) -> CancelStepsOutput:
        """Cancels a pending step or steps in a running cluster. Available only in
        Amazon EMR versions 4.8.0 and later, excluding version 5.0.0. A maximum
        of 256 steps are allowed in each CancelSteps request. CancelSteps is
        idempotent but asynchronous; it does not guarantee that a step will be
        canceled, even if the request is successfully submitted. When you use
        Amazon EMR versions 5.28.0 and later, you can cancel steps that are in a
        ``PENDING`` or ``RUNNING`` state. In earlier versions of Amazon EMR, you
        can only cancel steps that are in a ``PENDING`` state.

        :param cluster_id: The ``ClusterID`` for the specified steps that will be canceled.
        :param step_ids: The list of ``StepIDs`` to cancel.
        :param step_cancellation_option: The option to choose to cancel ``RUNNING`` steps.
        :returns: CancelStepsOutput
        :raises InternalServerError:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("CreateSecurityConfiguration")
    def create_security_configuration(
        self, context: RequestContext, name: XmlString, security_configuration: String
    ) -> CreateSecurityConfigurationOutput:
        """Creates a security configuration, which is stored in the service and can
        be specified when a cluster is created.

        :param name: The name of the security configuration.
        :param security_configuration: The security configuration details in JSON format.
        :returns: CreateSecurityConfigurationOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("CreateStudio")
    def create_studio(
        self,
        context: RequestContext,
        name: XmlStringMaxLen256,
        auth_mode: AuthMode,
        vpc_id: XmlStringMaxLen256,
        subnet_ids: SubnetIdList,
        service_role: XmlString,
        workspace_security_group_id: XmlStringMaxLen256,
        engine_security_group_id: XmlStringMaxLen256,
        default_s3_location: XmlString,
        description: XmlStringMaxLen256 = None,
        user_role: XmlString = None,
        idp_auth_url: XmlString = None,
        idp_relay_state_parameter_name: XmlStringMaxLen256 = None,
        tags: TagList = None,
    ) -> CreateStudioOutput:
        """Creates a new Amazon EMR Studio.

        :param name: A descriptive name for the Amazon EMR Studio.
        :param auth_mode: Specifies whether the Studio authenticates users using IAM or Amazon Web
        Services SSO.
        :param vpc_id: The ID of the Amazon Virtual Private Cloud (Amazon VPC) to associate
        with the Studio.
        :param subnet_ids: A list of subnet IDs to associate with the Amazon EMR Studio.
        :param service_role: The IAM role that the Amazon EMR Studio assumes.
        :param workspace_security_group_id: The ID of the Amazon EMR Studio Workspace security group.
        :param engine_security_group_id: The ID of the Amazon EMR Studio Engine security group.
        :param default_s3_location: The Amazon S3 location to back up Amazon EMR Studio Workspaces and
        notebook files.
        :param description: A detailed description of the Amazon EMR Studio.
        :param user_role: The IAM user role that users and groups assume when logged in to an
        Amazon EMR Studio.
        :param idp_auth_url: The authentication endpoint of your identity provider (IdP).
        :param idp_relay_state_parameter_name: The name that your identity provider (IdP) uses for its ``RelayState``
        parameter.
        :param tags: A list of tags to associate with the Amazon EMR Studio.
        :returns: CreateStudioOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("CreateStudioSessionMapping")
    def create_studio_session_mapping(
        self,
        context: RequestContext,
        studio_id: XmlStringMaxLen256,
        identity_type: IdentityType,
        session_policy_arn: XmlStringMaxLen256,
        identity_id: XmlStringMaxLen256 = None,
        identity_name: XmlStringMaxLen256 = None,
    ) -> None:
        """Maps a user or group to the Amazon EMR Studio specified by ``StudioId``,
        and applies a session policy to refine Studio permissions for that user
        or group. Use ``CreateStudioSessionMapping`` to assign users to a Studio
        when you use Amazon Web Services SSO authentication. For instructions on
        how to assign users to a Studio when you use IAM authentication, see
        `Assign a user or group to your EMR
        Studio <https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-studio-manage-users.html#emr-studio-assign-users-groups>`__.

        :param studio_id: The ID of the Amazon EMR Studio to which the user or group will be
        mapped.
        :param identity_type: Specifies whether the identity to map to the Amazon EMR Studio is a user
        or a group.
        :param session_policy_arn: The Amazon Resource Name (ARN) for the session policy that will be
        applied to the user or group.
        :param identity_id: The globally unique identifier (GUID) of the user or group from the
        Amazon Web Services SSO Identity Store.
        :param identity_name: The name of the user or group.
        :raises InternalServerError:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DeleteSecurityConfiguration")
    def delete_security_configuration(
        self, context: RequestContext, name: XmlString
    ) -> DeleteSecurityConfigurationOutput:
        """Deletes a security configuration.

        :param name: The name of the security configuration.
        :returns: DeleteSecurityConfigurationOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DeleteStudio")
    def delete_studio(self, context: RequestContext, studio_id: XmlStringMaxLen256) -> None:
        """Removes an Amazon EMR Studio from the Studio metadata store.

        :param studio_id: The ID of the Amazon EMR Studio.
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DeleteStudioSessionMapping")
    def delete_studio_session_mapping(
        self,
        context: RequestContext,
        studio_id: XmlStringMaxLen256,
        identity_type: IdentityType,
        identity_id: XmlStringMaxLen256 = None,
        identity_name: XmlStringMaxLen256 = None,
    ) -> None:
        """Removes a user or group from an Amazon EMR Studio.

        :param studio_id: The ID of the Amazon EMR Studio.
        :param identity_type: Specifies whether the identity to delete from the Amazon EMR Studio is a
        user or a group.
        :param identity_id: The globally unique identifier (GUID) of the user or group to remove
        from the Amazon EMR Studio.
        :param identity_name: The name of the user name or group to remove from the Amazon EMR Studio.
        :raises InternalServerError:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DescribeCluster")
    def describe_cluster(
        self, context: RequestContext, cluster_id: ClusterId
    ) -> DescribeClusterOutput:
        """Provides cluster-level details including status, hardware and software
        configuration, VPC settings, and so on.

        :param cluster_id: The identifier of the cluster to describe.
        :returns: DescribeClusterOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DescribeJobFlows")
    def describe_job_flows(
        self,
        context: RequestContext,
        created_after: Date = None,
        created_before: Date = None,
        job_flow_ids: XmlStringList = None,
        job_flow_states: JobFlowExecutionStateList = None,
    ) -> DescribeJobFlowsOutput:
        """This API is no longer supported and will eventually be removed. We
        recommend you use ListClusters, DescribeCluster, ListSteps,
        ListInstanceGroups and ListBootstrapActions instead.

        DescribeJobFlows returns a list of job flows that match all of the
        supplied parameters. The parameters can include a list of job flow IDs,
        job flow states, and restrictions on job flow creation date and time.

        Regardless of supplied parameters, only job flows created within the
        last two months are returned.

        If no parameters are supplied, then job flows matching either of the
        following criteria are returned:

        -  Job flows created and completed in the last two weeks

        -  Job flows created within the last two months that are in one of the
           following states: ``RUNNING``, ``WAITING``, ``SHUTTING_DOWN``,
           ``STARTING``

        Amazon EMR can return a maximum of 512 job flow descriptions.

        :param created_after: Return only job flows created after this date and time.
        :param created_before: Return only job flows created before this date and time.
        :param job_flow_ids: Return only job flows whose job flow ID is contained in this list.
        :param job_flow_states: Return only job flows whose state is contained in this list.
        :returns: DescribeJobFlowsOutput
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("DescribeNotebookExecution")
    def describe_notebook_execution(
        self, context: RequestContext, notebook_execution_id: XmlStringMaxLen256
    ) -> DescribeNotebookExecutionOutput:
        """Provides details of a notebook execution.

        :param notebook_execution_id: The unique identifier of the notebook execution.
        :returns: DescribeNotebookExecutionOutput
        :raises InternalServerError:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DescribeReleaseLabel")
    def describe_release_label(
        self,
        context: RequestContext,
        release_label: String = None,
        next_token: String = None,
        max_results: MaxResultsNumber = None,
    ) -> DescribeReleaseLabelOutput:
        """Provides EMR release label details, such as releases available the
        region where the API request is run, and the available applications for
        a specific EMR release label. Can also list EMR release versions that
        support a specified version of Spark.

        :param release_label: The target release label to be described.
        :param next_token: The pagination token.
        :param max_results: Reserved for future use.
        :returns: DescribeReleaseLabelOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DescribeSecurityConfiguration")
    def describe_security_configuration(
        self, context: RequestContext, name: XmlString
    ) -> DescribeSecurityConfigurationOutput:
        """Provides the details of a security configuration by returning the
        configuration JSON.

        :param name: The name of the security configuration.
        :returns: DescribeSecurityConfigurationOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DescribeStep")
    def describe_step(
        self, context: RequestContext, cluster_id: ClusterId, step_id: StepId
    ) -> DescribeStepOutput:
        """Provides more detail about the cluster step.

        :param cluster_id: The identifier of the cluster with steps to describe.
        :param step_id: The identifier of the step to describe.
        :returns: DescribeStepOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("DescribeStudio")
    def describe_studio(
        self, context: RequestContext, studio_id: XmlStringMaxLen256
    ) -> DescribeStudioOutput:
        """Returns details for the specified Amazon EMR Studio including ID, Name,
        VPC, Studio access URL, and so on.

        :param studio_id: The Amazon EMR Studio ID.
        :returns: DescribeStudioOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("GetAutoTerminationPolicy")
    def get_auto_termination_policy(
        self, context: RequestContext, cluster_id: ClusterId
    ) -> GetAutoTerminationPolicyOutput:
        """Returns the auto-termination policy for an Amazon EMR cluster.

        :param cluster_id: Specifies the ID of the Amazon EMR cluster for which the
        auto-termination policy will be fetched.
        :returns: GetAutoTerminationPolicyOutput
        """
        raise NotImplementedError

    @handler("GetBlockPublicAccessConfiguration")
    def get_block_public_access_configuration(
        self,
        context: RequestContext,
    ) -> GetBlockPublicAccessConfigurationOutput:
        """Returns the Amazon EMR block public access configuration for your Amazon
        Web Services account in the current Region. For more information see
        `Configure Block Public Access for Amazon
        EMR <https://docs.aws.amazon.com/emr/latest/ManagementGuide/configure-block-public-access.html>`__
        in the *Amazon EMR Management Guide*.

        :returns: GetBlockPublicAccessConfigurationOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("GetManagedScalingPolicy")
    def get_managed_scaling_policy(
        self, context: RequestContext, cluster_id: ClusterId
    ) -> GetManagedScalingPolicyOutput:
        """Fetches the attached managed scaling policy for an Amazon EMR cluster.

        :param cluster_id: Specifies the ID of the cluster for which the managed scaling policy
        will be fetched.
        :returns: GetManagedScalingPolicyOutput
        """
        raise NotImplementedError

    @handler("GetStudioSessionMapping")
    def get_studio_session_mapping(
        self,
        context: RequestContext,
        studio_id: XmlStringMaxLen256,
        identity_type: IdentityType,
        identity_id: XmlStringMaxLen256 = None,
        identity_name: XmlStringMaxLen256 = None,
    ) -> GetStudioSessionMappingOutput:
        """Fetches mapping details for the specified Amazon EMR Studio and identity
        (user or group).

        :param studio_id: The ID of the Amazon EMR Studio.
        :param identity_type: Specifies whether the identity to fetch is a user or a group.
        :param identity_id: The globally unique identifier (GUID) of the user or group.
        :param identity_name: The name of the user or group to fetch.
        :returns: GetStudioSessionMappingOutput
        :raises InternalServerError:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListBootstrapActions")
    def list_bootstrap_actions(
        self, context: RequestContext, cluster_id: ClusterId, marker: Marker = None
    ) -> ListBootstrapActionsOutput:
        """Provides information about the bootstrap actions associated with a
        cluster.

        :param cluster_id: The cluster identifier for the bootstrap actions to list.
        :param marker: The pagination token that indicates the next set of results to retrieve.
        :returns: ListBootstrapActionsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListClusters")
    def list_clusters(
        self,
        context: RequestContext,
        created_after: Date = None,
        created_before: Date = None,
        cluster_states: ClusterStateList = None,
        marker: Marker = None,
    ) -> ListClustersOutput:
        """Provides the status of all clusters visible to this Amazon Web Services
        account. Allows you to filter the list of clusters based on certain
        criteria; for example, filtering by cluster creation date and time or by
        status. This call returns a maximum of 50 clusters in unsorted order per
        call, but returns a marker to track the paging of the cluster list
        across multiple ListClusters calls.

        :param created_after: The creation date and time beginning value filter for listing clusters.
        :param created_before: The creation date and time end value filter for listing clusters.
        :param cluster_states: The cluster state filters to apply when listing clusters.
        :param marker: The pagination token that indicates the next set of results to retrieve.
        :returns: ListClustersOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListInstanceFleets")
    def list_instance_fleets(
        self, context: RequestContext, cluster_id: ClusterId, marker: Marker = None
    ) -> ListInstanceFleetsOutput:
        """Lists all available details about the instance fleets in a cluster.

        The instance fleet configuration is available only in Amazon EMR
        versions 4.8.0 and later, excluding 5.0.x versions.

        :param cluster_id: The unique identifier of the cluster.
        :param marker: The pagination token that indicates the next set of results to retrieve.
        :returns: ListInstanceFleetsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListInstanceGroups")
    def list_instance_groups(
        self, context: RequestContext, cluster_id: ClusterId, marker: Marker = None
    ) -> ListInstanceGroupsOutput:
        """Provides all available details about the instance groups in a cluster.

        :param cluster_id: The identifier of the cluster for which to list the instance groups.
        :param marker: The pagination token that indicates the next set of results to retrieve.
        :returns: ListInstanceGroupsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListInstances")
    def list_instances(
        self,
        context: RequestContext,
        cluster_id: ClusterId,
        instance_group_id: InstanceGroupId = None,
        instance_group_types: InstanceGroupTypeList = None,
        instance_fleet_id: InstanceFleetId = None,
        instance_fleet_type: InstanceFleetType = None,
        instance_states: InstanceStateList = None,
        marker: Marker = None,
    ) -> ListInstancesOutput:
        """Provides information for all active EC2 instances and EC2 instances
        terminated in the last 30 days, up to a maximum of 2,000. EC2 instances
        in any of the following states are considered active:
        AWAITING_FULFILLMENT, PROVISIONING, BOOTSTRAPPING, RUNNING.

        :param cluster_id: The identifier of the cluster for which to list the instances.
        :param instance_group_id: The identifier of the instance group for which to list the instances.
        :param instance_group_types: The type of instance group for which to list the instances.
        :param instance_fleet_id: The unique identifier of the instance fleet.
        :param instance_fleet_type: The node type of the instance fleet.
        :param instance_states: A list of instance states that will filter the instances returned with
        this request.
        :param marker: The pagination token that indicates the next set of results to retrieve.
        :returns: ListInstancesOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListNotebookExecutions", expand=False)
    def list_notebook_executions(
        self, context: RequestContext, request: ListNotebookExecutionsInput
    ) -> ListNotebookExecutionsOutput:
        """Provides summaries of all notebook executions. You can filter the list
        based on multiple criteria such as status, time range, and editor id.
        Returns a maximum of 50 notebook executions and a marker to track the
        paging of a longer notebook execution list across multiple
        ``ListNotebookExecution`` calls.

        :param editor_id: The unique ID of the editor associated with the notebook execution.
        :param status: The status filter for listing notebook executions.
        :param from: The beginning of time range filter for listing notebook executions.
        :param to: The end of time range filter for listing notebook executions.
        :param marker: The pagination token, returned by a previous ``ListNotebookExecutions``
        call, that indicates the start of the list for this
        ``ListNotebookExecutions`` call.
        :returns: ListNotebookExecutionsOutput
        :raises InternalServerError:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListReleaseLabels")
    def list_release_labels(
        self,
        context: RequestContext,
        filters: ReleaseLabelFilter = None,
        next_token: String = None,
        max_results: MaxResultsNumber = None,
    ) -> ListReleaseLabelsOutput:
        """Retrieves release labels of EMR services in the region where the API is
        called.

        :param filters: Filters the results of the request.
        :param next_token: Specifies the next page of results.
        :param max_results: Defines the maximum number of release labels to return in a single
        response.
        :returns: ListReleaseLabelsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListSecurityConfigurations")
    def list_security_configurations(
        self, context: RequestContext, marker: Marker = None
    ) -> ListSecurityConfigurationsOutput:
        """Lists all the security configurations visible to this account, providing
        their creation dates and times, and their names. This call returns a
        maximum of 50 clusters per call, but returns a marker to track the
        paging of the cluster list across multiple ListSecurityConfigurations
        calls.

        :param marker: The pagination token that indicates the set of results to retrieve.
        :returns: ListSecurityConfigurationsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListSteps")
    def list_steps(
        self,
        context: RequestContext,
        cluster_id: ClusterId,
        step_states: StepStateList = None,
        step_ids: XmlStringList = None,
        marker: Marker = None,
    ) -> ListStepsOutput:
        """Provides a list of steps for the cluster in reverse order unless you
        specify ``stepIds`` with the request or filter by ``StepStates``. You
        can specify a maximum of 10 ``stepIDs``. The CLI automatically paginates
        results to return a list greater than 50 steps. To return more than 50
        steps using the CLI, specify a ``Marker``, which is a pagination token
        that indicates the next set of steps to retrieve.

        :param cluster_id: The identifier of the cluster for which to list the steps.
        :param step_states: The filter to limit the step list based on certain states.
        :param step_ids: The filter to limit the step list based on the identifier of the steps.
        :param marker: The maximum number of steps that a single ``ListSteps`` action returns
        is 50.
        :returns: ListStepsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListStudioSessionMappings")
    def list_studio_session_mappings(
        self,
        context: RequestContext,
        studio_id: XmlStringMaxLen256 = None,
        identity_type: IdentityType = None,
        marker: Marker = None,
    ) -> ListStudioSessionMappingsOutput:
        """Returns a list of all user or group session mappings for the Amazon EMR
        Studio specified by ``StudioId``.

        :param studio_id: The ID of the Amazon EMR Studio.
        :param identity_type: Specifies whether to return session mappings for users or groups.
        :param marker: The pagination token that indicates the set of results to retrieve.
        :returns: ListStudioSessionMappingsOutput
        :raises InternalServerError:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListStudios")
    def list_studios(self, context: RequestContext, marker: Marker = None) -> ListStudiosOutput:
        """Returns a list of all Amazon EMR Studios associated with the Amazon Web
        Services account. The list includes details such as ID, Studio Access
        URL, and creation time for each Studio.

        :param marker: The pagination token that indicates the set of results to retrieve.
        :returns: ListStudiosOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ModifyCluster")
    def modify_cluster(
        self, context: RequestContext, cluster_id: String, step_concurrency_level: Integer = None
    ) -> ModifyClusterOutput:
        """Modifies the number of steps that can be executed concurrently for the
        cluster specified using ClusterID.

        :param cluster_id: The unique identifier of the cluster.
        :param step_concurrency_level: The number of steps that can be executed concurrently.
        :returns: ModifyClusterOutput
        :raises InternalServerError:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ModifyInstanceFleet")
    def modify_instance_fleet(
        self,
        context: RequestContext,
        cluster_id: ClusterId,
        instance_fleet: InstanceFleetModifyConfig,
    ) -> None:
        """Modifies the target On-Demand and target Spot capacities for the
        instance fleet with the specified InstanceFleetID within the cluster
        specified using ClusterID. The call either succeeds or fails atomically.

        The instance fleet configuration is available only in Amazon EMR
        versions 4.8.0 and later, excluding 5.0.x versions.

        :param cluster_id: The unique identifier of the cluster.
        :param instance_fleet: The configuration parameters of the instance fleet.
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ModifyInstanceGroups")
    def modify_instance_groups(
        self,
        context: RequestContext,
        cluster_id: ClusterId = None,
        instance_groups: InstanceGroupModifyConfigList = None,
    ) -> None:
        """ModifyInstanceGroups modifies the number of nodes and configuration
        settings of an instance group. The input parameters include the new
        target instance count for the group and the instance group ID. The call
        will either succeed or fail atomically.

        :param cluster_id: The ID of the cluster to which the instance group belongs.
        :param instance_groups: Instance groups to change.
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("PutAutoScalingPolicy")
    def put_auto_scaling_policy(
        self,
        context: RequestContext,
        cluster_id: ClusterId,
        instance_group_id: InstanceGroupId,
        auto_scaling_policy: AutoScalingPolicy,
    ) -> PutAutoScalingPolicyOutput:
        """Creates or updates an automatic scaling policy for a core instance group
        or task instance group in an Amazon EMR cluster. The automatic scaling
        policy defines how an instance group dynamically adds and terminates EC2
        instances in response to the value of a CloudWatch metric.

        :param cluster_id: Specifies the ID of a cluster.
        :param instance_group_id: Specifies the ID of the instance group to which the automatic scaling
        policy is applied.
        :param auto_scaling_policy: Specifies the definition of the automatic scaling policy.
        :returns: PutAutoScalingPolicyOutput
        """
        raise NotImplementedError

    @handler("PutAutoTerminationPolicy")
    def put_auto_termination_policy(
        self,
        context: RequestContext,
        cluster_id: ClusterId,
        auto_termination_policy: AutoTerminationPolicy = None,
    ) -> PutAutoTerminationPolicyOutput:
        """Auto-termination is supported in Amazon EMR versions 5.30.0 and 6.1.0
        and later. For more information, see `Using an auto-termination
        policy <https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-auto-termination-policy.html>`__.

        Creates or updates an auto-termination policy for an Amazon EMR cluster.
        An auto-termination policy defines the amount of idle time in seconds
        after which a cluster automatically terminates. For alternative cluster
        termination options, see `Control cluster
        termination <https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-termination.html>`__.

        :param cluster_id: Specifies the ID of the Amazon EMR cluster to which the auto-termination
        policy will be attached.
        :param auto_termination_policy: Specifies the auto-termination policy to attach to the cluster.
        :returns: PutAutoTerminationPolicyOutput
        """
        raise NotImplementedError

    @handler("PutBlockPublicAccessConfiguration")
    def put_block_public_access_configuration(
        self,
        context: RequestContext,
        block_public_access_configuration: BlockPublicAccessConfiguration,
    ) -> PutBlockPublicAccessConfigurationOutput:
        """Creates or updates an Amazon EMR block public access configuration for
        your Amazon Web Services account in the current Region. For more
        information see `Configure Block Public Access for Amazon
        EMR <https://docs.aws.amazon.com/emr/latest/ManagementGuide/configure-block-public-access.html>`__
        in the *Amazon EMR Management Guide*.

        :param block_public_access_configuration: A configuration for Amazon EMR block public access.
        :returns: PutBlockPublicAccessConfigurationOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("PutManagedScalingPolicy")
    def put_managed_scaling_policy(
        self,
        context: RequestContext,
        cluster_id: ClusterId,
        managed_scaling_policy: ManagedScalingPolicy,
    ) -> PutManagedScalingPolicyOutput:
        """Creates or updates a managed scaling policy for an Amazon EMR cluster.
        The managed scaling policy defines the limits for resources, such as EC2
        instances that can be added or terminated from a cluster. The policy
        only applies to the core and task nodes. The master node cannot be
        scaled after initial configuration.

        :param cluster_id: Specifies the ID of an EMR cluster where the managed scaling policy is
        attached.
        :param managed_scaling_policy: Specifies the constraints for the managed scaling policy.
        :returns: PutManagedScalingPolicyOutput
        """
        raise NotImplementedError

    @handler("RemoveAutoScalingPolicy")
    def remove_auto_scaling_policy(
        self, context: RequestContext, cluster_id: ClusterId, instance_group_id: InstanceGroupId
    ) -> RemoveAutoScalingPolicyOutput:
        """Removes an automatic scaling policy from a specified instance group
        within an EMR cluster.

        :param cluster_id: Specifies the ID of a cluster.
        :param instance_group_id: Specifies the ID of the instance group to which the scaling policy is
        applied.
        :returns: RemoveAutoScalingPolicyOutput
        """
        raise NotImplementedError

    @handler("RemoveAutoTerminationPolicy")
    def remove_auto_termination_policy(
        self, context: RequestContext, cluster_id: ClusterId
    ) -> RemoveAutoTerminationPolicyOutput:
        """Removes an auto-termination policy from an Amazon EMR cluster.

        :param cluster_id: Specifies the ID of the Amazon EMR cluster from which the
        auto-termination policy will be removed.
        :returns: RemoveAutoTerminationPolicyOutput
        """
        raise NotImplementedError

    @handler("RemoveManagedScalingPolicy")
    def remove_managed_scaling_policy(
        self, context: RequestContext, cluster_id: ClusterId
    ) -> RemoveManagedScalingPolicyOutput:
        """Removes a managed scaling policy from a specified EMR cluster.

        :param cluster_id: Specifies the ID of the cluster from which the managed scaling policy
        will be removed.
        :returns: RemoveManagedScalingPolicyOutput
        """
        raise NotImplementedError

    @handler("RemoveTags")
    def remove_tags(
        self, context: RequestContext, resource_id: ResourceId, tag_keys: StringList
    ) -> RemoveTagsOutput:
        """Removes tags from an Amazon EMR resource, such as a cluster or Amazon
        EMR Studio. Tags make it easier to associate resources in various ways,
        such as grouping clusters to track your Amazon EMR resource allocation
        costs. For more information, see `Tag
        Clusters <https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-tags.html>`__.

        The following example removes the stack tag with value Prod from a
        cluster:

        :param resource_id: The Amazon EMR resource identifier from which tags will be removed.
        :param tag_keys: A list of tag keys to remove from the resource.
        :returns: RemoveTagsOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("RunJobFlow")
    def run_job_flow(
        self,
        context: RequestContext,
        name: XmlStringMaxLen256,
        instances: JobFlowInstancesConfig,
        log_uri: XmlString = None,
        log_encryption_kms_key_id: XmlString = None,
        additional_info: XmlString = None,
        ami_version: XmlStringMaxLen256 = None,
        release_label: XmlStringMaxLen256 = None,
        steps: StepConfigList = None,
        bootstrap_actions: BootstrapActionConfigList = None,
        supported_products: SupportedProductsList = None,
        new_supported_products: NewSupportedProductsList = None,
        applications: ApplicationList = None,
        configurations: ConfigurationList = None,
        visible_to_all_users: Boolean = None,
        job_flow_role: XmlString = None,
        service_role: XmlString = None,
        tags: TagList = None,
        security_configuration: XmlString = None,
        auto_scaling_role: XmlString = None,
        scale_down_behavior: ScaleDownBehavior = None,
        custom_ami_id: XmlStringMaxLen256 = None,
        ebs_root_volume_size: Integer = None,
        repo_upgrade_on_boot: RepoUpgradeOnBoot = None,
        kerberos_attributes: KerberosAttributes = None,
        step_concurrency_level: Integer = None,
        managed_scaling_policy: ManagedScalingPolicy = None,
        placement_group_configs: PlacementGroupConfigList = None,
        auto_termination_policy: AutoTerminationPolicy = None,
        os_release_label: XmlStringMaxLen256 = None,
    ) -> RunJobFlowOutput:
        """RunJobFlow creates and starts running a new cluster (job flow). The
        cluster runs the steps specified. After the steps complete, the cluster
        stops and the HDFS partition is lost. To prevent loss of data, configure
        the last step of the job flow to store results in Amazon S3. If the
        JobFlowInstancesConfig ``KeepJobFlowAliveWhenNoSteps`` parameter is set
        to ``TRUE``, the cluster transitions to the WAITING state rather than
        shutting down after the steps have completed.

        For additional protection, you can set the JobFlowInstancesConfig
        ``TerminationProtected`` parameter to ``TRUE`` to lock the cluster and
        prevent it from being terminated by API call, user intervention, or in
        the event of a job flow error.

        A maximum of 256 steps are allowed in each job flow.

        If your cluster is long-running (such as a Hive data warehouse) or
        complex, you may require more than 256 steps to process your data. You
        can bypass the 256-step limitation in various ways, including using the
        SSH shell to connect to the master node and submitting queries directly
        to the software running on the master node, such as Hive and Hadoop. For
        more information on how to do this, see `Add More than 256 Steps to a
        Cluster <https://docs.aws.amazon.com/emr/latest/ManagementGuide/AddMoreThan256Steps.html>`__
        in the *Amazon EMR Management Guide*.

        For long running clusters, we recommend that you periodically store your
        results.

        The instance fleets configuration is available only in Amazon EMR
        versions 4.8.0 and later, excluding 5.0.x versions. The RunJobFlow
        request can contain InstanceFleets parameters or InstanceGroups
        parameters, but not both.

        :param name: The name of the job flow.
        :param instances: A specification of the number and type of Amazon EC2 instances.
        :param log_uri: The location in Amazon S3 to write the log files of the job flow.
        :param log_encryption_kms_key_id: The KMS key used for encrypting log files.
        :param additional_info: A JSON string for selecting additional features.
        :param ami_version: Applies only to Amazon EMR AMI versions 3.
        :param release_label: The Amazon EMR release label, which determines the version of
        open-source application packages installed on the cluster.
        :param steps: A list of steps to run.
        :param bootstrap_actions: A list of bootstrap actions to run before Hadoop starts on the cluster
        nodes.
        :param supported_products: For Amazon EMR releases 3.
        :param new_supported_products: For Amazon EMR releases 3.
        :param applications: Applies to Amazon EMR releases 4.
        :param configurations: For Amazon EMR releases 4.
        :param visible_to_all_users: The VisibleToAllUsers parameter is no longer supported.
        :param job_flow_role: Also called instance profile and EC2 role.
        :param service_role: The IAM role that Amazon EMR assumes in order to access Amazon Web
        Services resources on your behalf.
        :param tags: A list of tags to associate with a cluster and propagate to Amazon EC2
        instances.
        :param security_configuration: The name of a security configuration to apply to the cluster.
        :param auto_scaling_role: An IAM role for automatic scaling policies.
        :param scale_down_behavior: Specifies the way that individual Amazon EC2 instances terminate when an
        automatic scale-in activity occurs or an instance group is resized.
        :param custom_ami_id: Available only in Amazon EMR version 5.
        :param ebs_root_volume_size: The size, in GiB, of the Amazon EBS root device volume of the Linux AMI
        that is used for each EC2 instance.
        :param repo_upgrade_on_boot: Applies only when ``CustomAmiID`` is used.
        :param kerberos_attributes: Attributes for Kerberos configuration when Kerberos authentication is
        enabled using a security configuration.
        :param step_concurrency_level: Specifies the number of steps that can be executed concurrently.
        :param managed_scaling_policy: The specified managed scaling policy for an Amazon EMR cluster.
        :param placement_group_configs: The specified placement group configuration for an Amazon EMR cluster.
        :param auto_termination_policy: An auto-termination policy for an Amazon EMR cluster.
        :param os_release_label: Specifies a particular Amazon Linux release for all nodes in a cluster
        launch RunJobFlow request.
        :returns: RunJobFlowOutput
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("SetTerminationProtection")
    def set_termination_protection(
        self, context: RequestContext, job_flow_ids: XmlStringList, termination_protected: Boolean
    ) -> None:
        """SetTerminationProtection locks a cluster (job flow) so the EC2 instances
        in the cluster cannot be terminated by user intervention, an API call,
        or in the event of a job-flow error. The cluster still terminates upon
        successful completion of the job flow. Calling
        ``SetTerminationProtection`` on a cluster is similar to calling the
        Amazon EC2 ``DisableAPITermination`` API on all EC2 instances in a
        cluster.

        ``SetTerminationProtection`` is used to prevent accidental termination
        of a cluster and to ensure that in the event of an error, the instances
        persist so that you can recover any data stored in their ephemeral
        instance storage.

        To terminate a cluster that has been locked by setting
        ``SetTerminationProtection`` to ``true``, you must first unlock the job
        flow by a subsequent call to ``SetTerminationProtection`` in which you
        set the value to ``false``.

        For more information, see `Managing Cluster
        Termination <https://docs.aws.amazon.com/emr/latest/ManagementGuide/UsingEMR_TerminationProtection.html>`__
        in the *Amazon EMR Management Guide*.

        :param job_flow_ids: A list of strings that uniquely identify the clusters to protect.
        :param termination_protected: A Boolean that indicates whether to protect the cluster and prevent the
        Amazon EC2 instances in the cluster from shutting down due to API calls,
        user intervention, or job-flow error.
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("SetVisibleToAllUsers")
    def set_visible_to_all_users(
        self, context: RequestContext, job_flow_ids: XmlStringList, visible_to_all_users: Boolean
    ) -> None:
        """The SetVisibleToAllUsers parameter is no longer supported. Your cluster
        may be visible to all users in your account. To restrict cluster access
        using an IAM policy, see `Identity and Access Management for
        EMR <https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-access-iam.html>`__.

        Sets the Cluster$VisibleToAllUsers value for an EMR cluster. When
        ``true``, IAM principals in the Amazon Web Services account can perform
        EMR cluster actions that their IAM policies allow. When ``false``, only
        the IAM principal that created the cluster and the Amazon Web Services
        account root user can perform EMR actions on the cluster, regardless of
        IAM permissions policies attached to other IAM principals.

        This action works on running clusters. When you create a cluster, use
        the RunJobFlowInput$VisibleToAllUsers parameter.

        For more information, see `Understanding the EMR Cluster
        VisibleToAllUsers
        Setting <https://docs.aws.amazon.com/emr/latest/ManagementGuide/security_iam_emr-with-iam.html#security_set_visible_to_all_users>`__
        in the *Amazon EMRManagement Guide*.

        :param job_flow_ids: The unique identifier of the job flow (cluster).
        :param visible_to_all_users: A value of ``true`` indicates that an IAM principal in the Amazon Web
        Services account can perform EMR actions on the cluster that the IAM
        policies attached to the principal allow.
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("StartNotebookExecution")
    def start_notebook_execution(
        self,
        context: RequestContext,
        editor_id: XmlStringMaxLen256,
        relative_path: XmlString,
        execution_engine: ExecutionEngineConfig,
        service_role: XmlString,
        notebook_execution_name: XmlStringMaxLen256 = None,
        notebook_params: XmlString = None,
        notebook_instance_security_group_id: XmlStringMaxLen256 = None,
        tags: TagList = None,
    ) -> StartNotebookExecutionOutput:
        """Starts a notebook execution.

        :param editor_id: The unique identifier of the EMR Notebook to use for notebook execution.
        :param relative_path: The path and file name of the notebook file for this execution, relative
        to the path specified for the EMR Notebook.
        :param execution_engine: Specifies the execution engine (cluster) that runs the notebook
        execution.
        :param service_role: The name or ARN of the IAM role that is used as the service role for
        Amazon EMR (the EMR role) for the notebook execution.
        :param notebook_execution_name: An optional name for the notebook execution.
        :param notebook_params: Input parameters in JSON format passed to the EMR Notebook at runtime
        for execution.
        :param notebook_instance_security_group_id: The unique identifier of the Amazon EC2 security group to associate with
        the EMR Notebook for this notebook execution.
        :param tags: A list of tags associated with a notebook execution.
        :returns: StartNotebookExecutionOutput
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("StopNotebookExecution")
    def stop_notebook_execution(
        self, context: RequestContext, notebook_execution_id: XmlStringMaxLen256
    ) -> None:
        """Stops a notebook execution.

        :param notebook_execution_id: The unique identifier of the notebook execution.
        :raises InternalServerError:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("TerminateJobFlows")
    def terminate_job_flows(self, context: RequestContext, job_flow_ids: XmlStringList) -> None:
        """TerminateJobFlows shuts a list of clusters (job flows) down. When a job
        flow is shut down, any step not yet completed is canceled and the EC2
        instances on which the cluster is running are stopped. Any log files not
        already saved are uploaded to Amazon S3 if a LogUri was specified when
        the cluster was created.

        The maximum number of clusters allowed is 10. The call to
        ``TerminateJobFlows`` is asynchronous. Depending on the configuration of
        the cluster, it may take up to 1-5 minutes for the cluster to completely
        terminate and release allocated resources, such as Amazon EC2 instances.

        :param job_flow_ids: A list of job flows to be shut down.
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("UpdateStudio")
    def update_studio(
        self,
        context: RequestContext,
        studio_id: XmlStringMaxLen256,
        name: XmlStringMaxLen256 = None,
        description: XmlStringMaxLen256 = None,
        subnet_ids: SubnetIdList = None,
        default_s3_location: XmlString = None,
    ) -> None:
        """Updates an Amazon EMR Studio configuration, including attributes such as
        name, description, and subnets.

        :param studio_id: The ID of the Amazon EMR Studio to update.
        :param name: A descriptive name for the Amazon EMR Studio.
        :param description: A detailed description to assign to the Amazon EMR Studio.
        :param subnet_ids: A list of subnet IDs to associate with the Amazon EMR Studio.
        :param default_s3_location: The Amazon S3 location to back up Workspaces and notebook files for the
        Amazon EMR Studio.
        :raises InternalServerException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("UpdateStudioSessionMapping")
    def update_studio_session_mapping(
        self,
        context: RequestContext,
        studio_id: XmlStringMaxLen256,
        identity_type: IdentityType,
        session_policy_arn: XmlStringMaxLen256,
        identity_id: XmlStringMaxLen256 = None,
        identity_name: XmlStringMaxLen256 = None,
    ) -> None:
        """Updates the session policy attached to the user or group for the
        specified Amazon EMR Studio.

        :param studio_id: The ID of the Amazon EMR Studio.
        :param identity_type: Specifies whether the identity to update is a user or a group.
        :param session_policy_arn: The Amazon Resource Name (ARN) of the session policy to associate with
        the specified user or group.
        :param identity_id: The globally unique identifier (GUID) of the user or group.
        :param identity_name: The name of the user or group to update.
        :raises InternalServerError:
        :raises InvalidRequestException:
        """
        raise NotImplementedError
