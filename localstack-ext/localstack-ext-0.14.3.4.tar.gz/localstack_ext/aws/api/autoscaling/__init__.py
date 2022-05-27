import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AsciiStringMaxLen255 = str
AssociatePublicIpAddress = bool
AutoScalingGroupDesiredCapacity = int
AutoScalingGroupMaxSize = int
AutoScalingGroupMinSize = int
AutoScalingGroupPredictedCapacity = int
AutoScalingGroupState = str
BlockDeviceEbsDeleteOnTermination = bool
BlockDeviceEbsEncrypted = bool
BlockDeviceEbsIops = int
BlockDeviceEbsThroughput = int
BlockDeviceEbsVolumeSize = int
BlockDeviceEbsVolumeType = str
CapacityRebalanceEnabled = bool
CheckpointDelay = int
Context = str
Cooldown = int
DefaultInstanceWarmup = int
DisableScaleIn = bool
EbsOptimized = bool
EstimatedInstanceWarmup = int
ExcludedInstance = str
ForceDelete = bool
GlobalTimeout = int
HealthCheckGracePeriod = int
HeartbeatTimeout = int
HonorCooldown = bool
IncludeDeletedGroups = bool
InstanceMetadataHttpPutResponseHopLimit = int
InstanceProtected = bool
InstancesToUpdate = int
IntPercent = int
LaunchTemplateName = str
LifecycleActionResult = str
LifecycleActionToken = str
LifecycleTransition = str
MaxGroupPreparedCapacity = int
MaxInstanceLifetime = int
MaxNumberOfAutoScalingGroups = int
MaxNumberOfLaunchConfigurations = int
MaxRecords = int
MetricDimensionName = str
MetricDimensionValue = str
MetricName = str
MetricNamespace = str
MetricScale = float
MetricUnit = str
MinAdjustmentMagnitude = int
MinAdjustmentStep = int
MixedInstanceSpotPrice = str
MonitoringEnabled = bool
NoDevice = bool
NonZeroIntPercent = int
NotificationTargetResourceName = str
NullableBoolean = bool
NullablePositiveDouble = float
NullablePositiveInteger = int
NumberOfAutoScalingGroups = int
NumberOfLaunchConfigurations = int
OnDemandBaseCapacity = int
OnDemandPercentageAboveBaseCapacity = int
PolicyIncrement = int
PredictiveScalingMaxCapacityBuffer = int
PredictiveScalingSchedulingBufferTime = int
Progress = int
PropagateAtLaunch = bool
ProtectedFromScaleIn = bool
RefreshInstanceWarmup = int
ResourceName = str
ReturnData = bool
ReuseOnScaleIn = bool
ScalingPolicyEnabled = bool
ShouldDecrementDesiredCapacity = bool
ShouldRespectGracePeriod = bool
SkipMatching = bool
SpotInstancePools = int
SpotPrice = str
TagKey = str
TagValue = str
WarmPoolMinSize = int
WarmPoolSize = int
XmlString = str
XmlStringMaxLen1023 = str
XmlStringMaxLen1600 = str
XmlStringMaxLen19 = str
XmlStringMaxLen2047 = str
XmlStringMaxLen255 = str
XmlStringMaxLen32 = str
XmlStringMaxLen511 = str
XmlStringMaxLen64 = str
XmlStringMetricLabel = str
XmlStringMetricStat = str
XmlStringUserData = str


class AcceleratorManufacturer(str):
    nvidia = "nvidia"
    amd = "amd"
    amazon_web_services = "amazon-web-services"
    xilinx = "xilinx"


class AcceleratorName(str):
    a100 = "a100"
    v100 = "v100"
    k80 = "k80"
    t4 = "t4"
    m60 = "m60"
    radeon_pro_v520 = "radeon-pro-v520"
    vu9p = "vu9p"


class AcceleratorType(str):
    gpu = "gpu"
    fpga = "fpga"
    inference = "inference"


class BareMetal(str):
    included = "included"
    excluded = "excluded"
    required = "required"


class BurstablePerformance(str):
    included = "included"
    excluded = "excluded"
    required = "required"


class CpuManufacturer(str):
    intel = "intel"
    amd = "amd"
    amazon_web_services = "amazon-web-services"


class InstanceGeneration(str):
    current = "current"
    previous = "previous"


class InstanceMetadataEndpointState(str):
    disabled = "disabled"
    enabled = "enabled"


class InstanceMetadataHttpTokensState(str):
    optional = "optional"
    required = "required"


class InstanceRefreshStatus(str):
    Pending = "Pending"
    InProgress = "InProgress"
    Successful = "Successful"
    Failed = "Failed"
    Cancelling = "Cancelling"
    Cancelled = "Cancelled"


class LifecycleState(str):
    Pending = "Pending"
    Pending_Wait = "Pending:Wait"
    Pending_Proceed = "Pending:Proceed"
    Quarantined = "Quarantined"
    InService = "InService"
    Terminating = "Terminating"
    Terminating_Wait = "Terminating:Wait"
    Terminating_Proceed = "Terminating:Proceed"
    Terminated = "Terminated"
    Detaching = "Detaching"
    Detached = "Detached"
    EnteringStandby = "EnteringStandby"
    Standby = "Standby"
    Warmed_Pending = "Warmed:Pending"
    Warmed_Pending_Wait = "Warmed:Pending:Wait"
    Warmed_Pending_Proceed = "Warmed:Pending:Proceed"
    Warmed_Terminating = "Warmed:Terminating"
    Warmed_Terminating_Wait = "Warmed:Terminating:Wait"
    Warmed_Terminating_Proceed = "Warmed:Terminating:Proceed"
    Warmed_Terminated = "Warmed:Terminated"
    Warmed_Stopped = "Warmed:Stopped"
    Warmed_Running = "Warmed:Running"
    Warmed_Hibernated = "Warmed:Hibernated"


class LocalStorage(str):
    included = "included"
    excluded = "excluded"
    required = "required"


class LocalStorageType(str):
    hdd = "hdd"
    ssd = "ssd"


class MetricStatistic(str):
    Average = "Average"
    Minimum = "Minimum"
    Maximum = "Maximum"
    SampleCount = "SampleCount"
    Sum = "Sum"


class MetricType(str):
    ASGAverageCPUUtilization = "ASGAverageCPUUtilization"
    ASGAverageNetworkIn = "ASGAverageNetworkIn"
    ASGAverageNetworkOut = "ASGAverageNetworkOut"
    ALBRequestCountPerTarget = "ALBRequestCountPerTarget"


class PredefinedLoadMetricType(str):
    ASGTotalCPUUtilization = "ASGTotalCPUUtilization"
    ASGTotalNetworkIn = "ASGTotalNetworkIn"
    ASGTotalNetworkOut = "ASGTotalNetworkOut"
    ALBTargetGroupRequestCount = "ALBTargetGroupRequestCount"


class PredefinedMetricPairType(str):
    ASGCPUUtilization = "ASGCPUUtilization"
    ASGNetworkIn = "ASGNetworkIn"
    ASGNetworkOut = "ASGNetworkOut"
    ALBRequestCount = "ALBRequestCount"


class PredefinedScalingMetricType(str):
    ASGAverageCPUUtilization = "ASGAverageCPUUtilization"
    ASGAverageNetworkIn = "ASGAverageNetworkIn"
    ASGAverageNetworkOut = "ASGAverageNetworkOut"
    ALBRequestCountPerTarget = "ALBRequestCountPerTarget"


class PredictiveScalingMaxCapacityBreachBehavior(str):
    HonorMaxCapacity = "HonorMaxCapacity"
    IncreaseMaxCapacity = "IncreaseMaxCapacity"


class PredictiveScalingMode(str):
    ForecastAndScale = "ForecastAndScale"
    ForecastOnly = "ForecastOnly"


class RefreshStrategy(str):
    Rolling = "Rolling"


class ScalingActivityStatusCode(str):
    PendingSpotBidPlacement = "PendingSpotBidPlacement"
    WaitingForSpotInstanceRequestId = "WaitingForSpotInstanceRequestId"
    WaitingForSpotInstanceId = "WaitingForSpotInstanceId"
    WaitingForInstanceId = "WaitingForInstanceId"
    PreInService = "PreInService"
    InProgress = "InProgress"
    WaitingForELBConnectionDraining = "WaitingForELBConnectionDraining"
    MidLifecycleAction = "MidLifecycleAction"
    WaitingForInstanceWarmup = "WaitingForInstanceWarmup"
    Successful = "Successful"
    Failed = "Failed"
    Cancelled = "Cancelled"


class WarmPoolState(str):
    Stopped = "Stopped"
    Running = "Running"
    Hibernated = "Hibernated"


class WarmPoolStatus(str):
    PendingDelete = "PendingDelete"


class ActiveInstanceRefreshNotFoundFault(ServiceException):
    """The request failed because an active instance refresh for the specified
    Auto Scaling group was not found.
    """

    message: Optional[XmlStringMaxLen255]


class AlreadyExistsFault(ServiceException):
    """You already have an Auto Scaling group or launch configuration with this
    name.
    """

    message: Optional[XmlStringMaxLen255]


class InstanceRefreshInProgressFault(ServiceException):
    """The request failed because an active instance refresh operation already
    exists for the specified Auto Scaling group.
    """

    message: Optional[XmlStringMaxLen255]


class InvalidNextToken(ServiceException):
    """The ``NextToken`` value is not valid."""

    message: Optional[XmlStringMaxLen255]


class LimitExceededFault(ServiceException):
    """You have already reached a limit for your Amazon EC2 Auto Scaling
    resources (for example, Auto Scaling groups, launch configurations, or
    lifecycle hooks). For more information, see
    `DescribeAccountLimits <https://docs.aws.amazon.com/autoscaling/ec2/APIReference/API_DescribeAccountLimits.html>`__
    in the *Amazon EC2 Auto Scaling API Reference*.
    """

    message: Optional[XmlStringMaxLen255]


class ResourceContentionFault(ServiceException):
    """You already have a pending update to an Amazon EC2 Auto Scaling resource
    (for example, an Auto Scaling group, instance, or load balancer).
    """

    message: Optional[XmlStringMaxLen255]


class ResourceInUseFault(ServiceException):
    """The operation can't be performed because the resource is in use."""

    message: Optional[XmlStringMaxLen255]


class ScalingActivityInProgressFault(ServiceException):
    """The operation can't be performed because there are scaling activities in
    progress.
    """

    message: Optional[XmlStringMaxLen255]


class ServiceLinkedRoleFailure(ServiceException):
    """The service-linked role is not yet ready for use."""

    message: Optional[XmlStringMaxLen255]


class AcceleratorCountRequest(TypedDict, total=False):
    """Specifies the minimum and maximum for the ``AcceleratorCount`` object
    when you specify InstanceRequirements for an Auto Scaling group.
    """

    Min: Optional[NullablePositiveInteger]
    Max: Optional[NullablePositiveInteger]


AcceleratorManufacturers = List[AcceleratorManufacturer]
AcceleratorNames = List[AcceleratorName]


class AcceleratorTotalMemoryMiBRequest(TypedDict, total=False):
    """Specifies the minimum and maximum for the ``AcceleratorTotalMemoryMiB``
    object when you specify InstanceRequirements for an Auto Scaling group.
    """

    Min: Optional[NullablePositiveInteger]
    Max: Optional[NullablePositiveInteger]


AcceleratorTypes = List[AcceleratorType]
TimestampType = datetime


class Activity(TypedDict, total=False):
    """Describes scaling activity, which is a long-running process that
    represents a change to your Auto Scaling group, such as changing its
    size or replacing an instance.
    """

    ActivityId: XmlString
    AutoScalingGroupName: XmlStringMaxLen255
    Description: Optional[XmlString]
    Cause: XmlStringMaxLen1023
    StartTime: TimestampType
    EndTime: Optional[TimestampType]
    StatusCode: ScalingActivityStatusCode
    StatusMessage: Optional[XmlStringMaxLen255]
    Progress: Optional[Progress]
    Details: Optional[XmlString]
    AutoScalingGroupState: Optional[AutoScalingGroupState]
    AutoScalingGroupARN: Optional[ResourceName]


Activities = List[Activity]


class ActivitiesType(TypedDict, total=False):
    Activities: Activities
    NextToken: Optional[XmlString]


ActivityIds = List[XmlString]


class ActivityType(TypedDict, total=False):
    Activity: Optional[Activity]


class AdjustmentType(TypedDict, total=False):
    """Describes a policy adjustment type."""

    AdjustmentType: Optional[XmlStringMaxLen255]


AdjustmentTypes = List[AdjustmentType]


class Alarm(TypedDict, total=False):
    """Describes an alarm."""

    AlarmName: Optional[XmlStringMaxLen255]
    AlarmARN: Optional[ResourceName]


Alarms = List[Alarm]
InstanceIds = List[XmlStringMaxLen19]


class AttachInstancesQuery(ServiceRequest):
    InstanceIds: Optional[InstanceIds]
    AutoScalingGroupName: XmlStringMaxLen255


class AttachLoadBalancerTargetGroupsResultType(TypedDict, total=False):
    pass


TargetGroupARNs = List[XmlStringMaxLen511]


class AttachLoadBalancerTargetGroupsType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    TargetGroupARNs: TargetGroupARNs


class AttachLoadBalancersResultType(TypedDict, total=False):
    pass


LoadBalancerNames = List[XmlStringMaxLen255]


class AttachLoadBalancersType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    LoadBalancerNames: LoadBalancerNames


class InstanceReusePolicy(TypedDict, total=False):
    """Describes an instance reuse policy for a warm pool.

    For more information, see `Warm pools for Amazon EC2 Auto
    Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-warm-pools.html>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    ReuseOnScaleIn: Optional[ReuseOnScaleIn]


class WarmPoolConfiguration(TypedDict, total=False):
    """Describes a warm pool configuration."""

    MaxGroupPreparedCapacity: Optional[MaxGroupPreparedCapacity]
    MinSize: Optional[WarmPoolMinSize]
    PoolState: Optional[WarmPoolState]
    Status: Optional[WarmPoolStatus]
    InstanceReusePolicy: Optional[InstanceReusePolicy]


TerminationPolicies = List[XmlStringMaxLen1600]


class TagDescription(TypedDict, total=False):
    """Describes a tag for an Auto Scaling group."""

    ResourceId: Optional[XmlString]
    ResourceType: Optional[XmlString]
    Key: Optional[TagKey]
    Value: Optional[TagValue]
    PropagateAtLaunch: Optional[PropagateAtLaunch]


TagDescriptionList = List[TagDescription]


class EnabledMetric(TypedDict, total=False):
    """Describes an enabled metric."""

    Metric: Optional[XmlStringMaxLen255]
    Granularity: Optional[XmlStringMaxLen255]


EnabledMetrics = List[EnabledMetric]


class SuspendedProcess(TypedDict, total=False):
    """Describes an auto scaling process that has been suspended.

    For more information, see `Scaling
    processes <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-suspend-resume-processes.html#process-types>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    ProcessName: Optional[XmlStringMaxLen255]
    SuspensionReason: Optional[XmlStringMaxLen255]


SuspendedProcesses = List[SuspendedProcess]


class LaunchTemplateSpecification(TypedDict, total=False):
    """Describes the launch template and the version of the launch template
    that Amazon EC2 Auto Scaling uses to launch Amazon EC2 instances. For
    more information about launch templates, see `Launch
    templates <https://docs.aws.amazon.com/autoscaling/ec2/userguide/LaunchTemplates.html>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    LaunchTemplateId: Optional[XmlStringMaxLen255]
    LaunchTemplateName: Optional[LaunchTemplateName]
    Version: Optional[XmlStringMaxLen255]


class Instance(TypedDict, total=False):
    """Describes an EC2 instance."""

    InstanceId: XmlStringMaxLen19
    InstanceType: Optional[XmlStringMaxLen255]
    AvailabilityZone: XmlStringMaxLen255
    LifecycleState: LifecycleState
    HealthStatus: XmlStringMaxLen32
    LaunchConfigurationName: Optional[XmlStringMaxLen255]
    LaunchTemplate: Optional[LaunchTemplateSpecification]
    ProtectedFromScaleIn: InstanceProtected
    WeightedCapacity: Optional[XmlStringMaxLen32]


Instances = List[Instance]
AvailabilityZones = List[XmlStringMaxLen255]


class InstancesDistribution(TypedDict, total=False):
    """Describes an instances distribution for an Auto Scaling group."""

    OnDemandAllocationStrategy: Optional[XmlString]
    OnDemandBaseCapacity: Optional[OnDemandBaseCapacity]
    OnDemandPercentageAboveBaseCapacity: Optional[OnDemandPercentageAboveBaseCapacity]
    SpotAllocationStrategy: Optional[XmlString]
    SpotInstancePools: Optional[SpotInstancePools]
    SpotMaxPrice: Optional[MixedInstanceSpotPrice]


class BaselineEbsBandwidthMbpsRequest(TypedDict, total=False):
    """Specifies the minimum and maximum for the ``BaselineEbsBandwidthMbps``
    object when you specify InstanceRequirements for an Auto Scaling group.
    """

    Min: Optional[NullablePositiveInteger]
    Max: Optional[NullablePositiveInteger]


class TotalLocalStorageGBRequest(TypedDict, total=False):
    """Specifies the minimum and maximum for the ``TotalLocalStorageGB`` object
    when you specify InstanceRequirements for an Auto Scaling group.
    """

    Min: Optional[NullablePositiveDouble]
    Max: Optional[NullablePositiveDouble]


LocalStorageTypes = List[LocalStorageType]


class NetworkInterfaceCountRequest(TypedDict, total=False):
    """Specifies the minimum and maximum for the ``NetworkInterfaceCount``
    object when you specify InstanceRequirements for an Auto Scaling group.
    """

    Min: Optional[NullablePositiveInteger]
    Max: Optional[NullablePositiveInteger]


InstanceGenerations = List[InstanceGeneration]
ExcludedInstanceTypes = List[ExcludedInstance]


class MemoryGiBPerVCpuRequest(TypedDict, total=False):
    """Specifies the minimum and maximum for the ``MemoryGiBPerVCpu`` object
    when you specify InstanceRequirements for an Auto Scaling group.
    """

    Min: Optional[NullablePositiveDouble]
    Max: Optional[NullablePositiveDouble]


CpuManufacturers = List[CpuManufacturer]


class MemoryMiBRequest(TypedDict, total=False):
    """Specifies the minimum and maximum for the ``MemoryMiB`` object when you
    specify InstanceRequirements for an Auto Scaling group.
    """

    Min: NullablePositiveInteger
    Max: Optional[NullablePositiveInteger]


class VCpuCountRequest(TypedDict, total=False):
    """Specifies the minimum and maximum for the ``VCpuCount`` object when you
    specify InstanceRequirements for an Auto Scaling group.
    """

    Min: NullablePositiveInteger
    Max: Optional[NullablePositiveInteger]


class InstanceRequirements(TypedDict, total=False):
    """When you specify multiple parameters, you get instance types that
    satisfy all of the specified parameters. If you specify multiple values
    for a parameter, you get instance types that satisfy any of the
    specified values.

    Represents requirements for the types of instances that can be launched.
    You must specify ``VCpuCount`` and ``MemoryMiB``, but all other
    parameters are optional. For more information, see `Creating an Auto
    Scaling group using attribute-based instance type
    selection <https://docs.aws.amazon.com/autoscaling/ec2/userguide/create-asg-instance-type-requirements.html>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    VCpuCount: VCpuCountRequest
    MemoryMiB: MemoryMiBRequest
    CpuManufacturers: Optional[CpuManufacturers]
    MemoryGiBPerVCpu: Optional[MemoryGiBPerVCpuRequest]
    ExcludedInstanceTypes: Optional[ExcludedInstanceTypes]
    InstanceGenerations: Optional[InstanceGenerations]
    SpotMaxPricePercentageOverLowestPrice: Optional[NullablePositiveInteger]
    OnDemandMaxPricePercentageOverLowestPrice: Optional[NullablePositiveInteger]
    BareMetal: Optional[BareMetal]
    BurstablePerformance: Optional[BurstablePerformance]
    RequireHibernateSupport: Optional[NullableBoolean]
    NetworkInterfaceCount: Optional[NetworkInterfaceCountRequest]
    LocalStorage: Optional[LocalStorage]
    LocalStorageTypes: Optional[LocalStorageTypes]
    TotalLocalStorageGB: Optional[TotalLocalStorageGBRequest]
    BaselineEbsBandwidthMbps: Optional[BaselineEbsBandwidthMbpsRequest]
    AcceleratorTypes: Optional[AcceleratorTypes]
    AcceleratorCount: Optional[AcceleratorCountRequest]
    AcceleratorManufacturers: Optional[AcceleratorManufacturers]
    AcceleratorNames: Optional[AcceleratorNames]
    AcceleratorTotalMemoryMiB: Optional[AcceleratorTotalMemoryMiBRequest]


class LaunchTemplateOverrides(TypedDict, total=False):
    """Describes an override for a launch template. For more information, see
    `Configuring
    overrides <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-configuring-overrides.html>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    InstanceType: Optional[XmlStringMaxLen255]
    WeightedCapacity: Optional[XmlStringMaxLen32]
    LaunchTemplateSpecification: Optional[LaunchTemplateSpecification]
    InstanceRequirements: Optional[InstanceRequirements]


Overrides = List[LaunchTemplateOverrides]


class LaunchTemplate(TypedDict, total=False):
    """Describes a launch template and overrides. You specify these properties
    as part of a mixed instances policy.
    """

    LaunchTemplateSpecification: Optional[LaunchTemplateSpecification]
    Overrides: Optional[Overrides]


class MixedInstancesPolicy(TypedDict, total=False):
    """Describes a mixed instances policy. A mixed instances policy contains
    the instance types that Amazon EC2 Auto Scaling can launch and other
    information that Amazon EC2 Auto Scaling can use to launch instances and
    help optimize your costs. For more information, see `Auto Scaling groups
    with multiple instance types and purchase
    options <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-mixed-instances-groups.html>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    LaunchTemplate: Optional[LaunchTemplate]
    InstancesDistribution: Optional[InstancesDistribution]


class AutoScalingGroup(TypedDict, total=False):
    """Describes an Auto Scaling group."""

    AutoScalingGroupName: XmlStringMaxLen255
    AutoScalingGroupARN: Optional[ResourceName]
    LaunchConfigurationName: Optional[XmlStringMaxLen255]
    LaunchTemplate: Optional[LaunchTemplateSpecification]
    MixedInstancesPolicy: Optional[MixedInstancesPolicy]
    MinSize: AutoScalingGroupMinSize
    MaxSize: AutoScalingGroupMaxSize
    DesiredCapacity: AutoScalingGroupDesiredCapacity
    PredictedCapacity: Optional[AutoScalingGroupPredictedCapacity]
    DefaultCooldown: Cooldown
    AvailabilityZones: AvailabilityZones
    LoadBalancerNames: Optional[LoadBalancerNames]
    TargetGroupARNs: Optional[TargetGroupARNs]
    HealthCheckType: XmlStringMaxLen32
    HealthCheckGracePeriod: Optional[HealthCheckGracePeriod]
    Instances: Optional[Instances]
    CreatedTime: TimestampType
    SuspendedProcesses: Optional[SuspendedProcesses]
    PlacementGroup: Optional[XmlStringMaxLen255]
    VPCZoneIdentifier: Optional[XmlStringMaxLen2047]
    EnabledMetrics: Optional[EnabledMetrics]
    Status: Optional[XmlStringMaxLen255]
    Tags: Optional[TagDescriptionList]
    TerminationPolicies: Optional[TerminationPolicies]
    NewInstancesProtectedFromScaleIn: Optional[InstanceProtected]
    ServiceLinkedRoleARN: Optional[ResourceName]
    MaxInstanceLifetime: Optional[MaxInstanceLifetime]
    CapacityRebalance: Optional[CapacityRebalanceEnabled]
    WarmPoolConfiguration: Optional[WarmPoolConfiguration]
    WarmPoolSize: Optional[WarmPoolSize]
    Context: Optional[Context]
    DesiredCapacityType: Optional[XmlStringMaxLen255]
    DefaultInstanceWarmup: Optional[DefaultInstanceWarmup]


AutoScalingGroupNames = List[XmlStringMaxLen255]
Values = List[XmlString]


class Filter(TypedDict, total=False):
    """Describes a filter that is used to return a more specific list of
    results from a describe operation.

    If you specify multiple filters, the filters are automatically logically
    joined with an ``AND``, and the request returns only the results that
    match all of the specified filters.

    For more information, see `Tagging Auto Scaling groups and
    instances <https://docs.aws.amazon.com/autoscaling/ec2/userguide/autoscaling-tagging.html>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    Name: Optional[XmlString]
    Values: Optional[Values]


Filters = List[Filter]


class AutoScalingGroupNamesType(ServiceRequest):
    AutoScalingGroupNames: Optional[AutoScalingGroupNames]
    NextToken: Optional[XmlString]
    MaxRecords: Optional[MaxRecords]
    Filters: Optional[Filters]


AutoScalingGroups = List[AutoScalingGroup]


class AutoScalingGroupsType(TypedDict, total=False):
    AutoScalingGroups: AutoScalingGroups
    NextToken: Optional[XmlString]


class AutoScalingInstanceDetails(TypedDict, total=False):
    """Describes an EC2 instance associated with an Auto Scaling group."""

    InstanceId: XmlStringMaxLen19
    InstanceType: Optional[XmlStringMaxLen255]
    AutoScalingGroupName: XmlStringMaxLen255
    AvailabilityZone: XmlStringMaxLen255
    LifecycleState: XmlStringMaxLen32
    HealthStatus: XmlStringMaxLen32
    LaunchConfigurationName: Optional[XmlStringMaxLen255]
    LaunchTemplate: Optional[LaunchTemplateSpecification]
    ProtectedFromScaleIn: InstanceProtected
    WeightedCapacity: Optional[XmlStringMaxLen32]


AutoScalingInstances = List[AutoScalingInstanceDetails]


class AutoScalingInstancesType(TypedDict, total=False):
    AutoScalingInstances: Optional[AutoScalingInstances]
    NextToken: Optional[XmlString]


AutoScalingNotificationTypes = List[XmlStringMaxLen255]


class FailedScheduledUpdateGroupActionRequest(TypedDict, total=False):
    """Describes a scheduled action that could not be created, updated, or
    deleted.
    """

    ScheduledActionName: XmlStringMaxLen255
    ErrorCode: Optional[XmlStringMaxLen64]
    ErrorMessage: Optional[XmlString]


FailedScheduledUpdateGroupActionRequests = List[FailedScheduledUpdateGroupActionRequest]


class BatchDeleteScheduledActionAnswer(TypedDict, total=False):
    FailedScheduledActions: Optional[FailedScheduledUpdateGroupActionRequests]


ScheduledActionNames = List[XmlStringMaxLen255]


class BatchDeleteScheduledActionType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    ScheduledActionNames: ScheduledActionNames


class BatchPutScheduledUpdateGroupActionAnswer(TypedDict, total=False):
    FailedScheduledUpdateGroupActions: Optional[FailedScheduledUpdateGroupActionRequests]


class ScheduledUpdateGroupActionRequest(TypedDict, total=False):
    """Describes information used for one or more scheduled scaling action
    updates in a BatchPutScheduledUpdateGroupAction operation.
    """

    ScheduledActionName: XmlStringMaxLen255
    StartTime: Optional[TimestampType]
    EndTime: Optional[TimestampType]
    Recurrence: Optional[XmlStringMaxLen255]
    MinSize: Optional[AutoScalingGroupMinSize]
    MaxSize: Optional[AutoScalingGroupMaxSize]
    DesiredCapacity: Optional[AutoScalingGroupDesiredCapacity]
    TimeZone: Optional[XmlStringMaxLen255]


ScheduledUpdateGroupActionRequests = List[ScheduledUpdateGroupActionRequest]


class BatchPutScheduledUpdateGroupActionType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    ScheduledUpdateGroupActions: ScheduledUpdateGroupActionRequests


class Ebs(TypedDict, total=False):
    """Describes information used to set up an Amazon EBS volume specified in a
    block device mapping.
    """

    SnapshotId: Optional[XmlStringMaxLen255]
    VolumeSize: Optional[BlockDeviceEbsVolumeSize]
    VolumeType: Optional[BlockDeviceEbsVolumeType]
    DeleteOnTermination: Optional[BlockDeviceEbsDeleteOnTermination]
    Iops: Optional[BlockDeviceEbsIops]
    Encrypted: Optional[BlockDeviceEbsEncrypted]
    Throughput: Optional[BlockDeviceEbsThroughput]


class BlockDeviceMapping(TypedDict, total=False):
    """Describes a block device mapping."""

    VirtualName: Optional[XmlStringMaxLen255]
    DeviceName: XmlStringMaxLen255
    Ebs: Optional[Ebs]
    NoDevice: Optional[NoDevice]


BlockDeviceMappings = List[BlockDeviceMapping]


class CancelInstanceRefreshAnswer(TypedDict, total=False):
    InstanceRefreshId: Optional[XmlStringMaxLen255]


class CancelInstanceRefreshType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255


PredictiveScalingForecastValues = List[MetricScale]
PredictiveScalingForecastTimestamps = List[TimestampType]


class CapacityForecast(TypedDict, total=False):
    """A ``GetPredictiveScalingForecast`` call returns the capacity forecast
    for a predictive scaling policy. This structure includes the data points
    for that capacity forecast, along with the timestamps of those data
    points.
    """

    Timestamps: PredictiveScalingForecastTimestamps
    Values: PredictiveScalingForecastValues


CheckpointPercentages = List[NonZeroIntPercent]
ClassicLinkVPCSecurityGroups = List[XmlStringMaxLen255]


class CompleteLifecycleActionAnswer(TypedDict, total=False):
    pass


class CompleteLifecycleActionType(ServiceRequest):
    LifecycleHookName: AsciiStringMaxLen255
    AutoScalingGroupName: ResourceName
    LifecycleActionToken: Optional[LifecycleActionToken]
    LifecycleActionResult: LifecycleActionResult
    InstanceId: Optional[XmlStringMaxLen19]


class Tag(TypedDict, total=False):
    """Describes a tag for an Auto Scaling group."""

    ResourceId: Optional[XmlString]
    ResourceType: Optional[XmlString]
    Key: TagKey
    Value: Optional[TagValue]
    PropagateAtLaunch: Optional[PropagateAtLaunch]


Tags = List[Tag]


class LifecycleHookSpecification(TypedDict, total=False):
    """Describes information used to specify a lifecycle hook for an Auto
    Scaling group.

    For more information, see `Amazon EC2 Auto Scaling lifecycle
    hooks <https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    LifecycleHookName: AsciiStringMaxLen255
    LifecycleTransition: LifecycleTransition
    NotificationMetadata: Optional[XmlStringMaxLen1023]
    HeartbeatTimeout: Optional[HeartbeatTimeout]
    DefaultResult: Optional[LifecycleActionResult]
    NotificationTargetARN: Optional[NotificationTargetResourceName]
    RoleARN: Optional[XmlStringMaxLen255]


LifecycleHookSpecifications = List[LifecycleHookSpecification]


class CreateAutoScalingGroupType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    LaunchConfigurationName: Optional[XmlStringMaxLen255]
    LaunchTemplate: Optional[LaunchTemplateSpecification]
    MixedInstancesPolicy: Optional[MixedInstancesPolicy]
    InstanceId: Optional[XmlStringMaxLen19]
    MinSize: AutoScalingGroupMinSize
    MaxSize: AutoScalingGroupMaxSize
    DesiredCapacity: Optional[AutoScalingGroupDesiredCapacity]
    DefaultCooldown: Optional[Cooldown]
    AvailabilityZones: Optional[AvailabilityZones]
    LoadBalancerNames: Optional[LoadBalancerNames]
    TargetGroupARNs: Optional[TargetGroupARNs]
    HealthCheckType: Optional[XmlStringMaxLen32]
    HealthCheckGracePeriod: Optional[HealthCheckGracePeriod]
    PlacementGroup: Optional[XmlStringMaxLen255]
    VPCZoneIdentifier: Optional[XmlStringMaxLen2047]
    TerminationPolicies: Optional[TerminationPolicies]
    NewInstancesProtectedFromScaleIn: Optional[InstanceProtected]
    CapacityRebalance: Optional[CapacityRebalanceEnabled]
    LifecycleHookSpecificationList: Optional[LifecycleHookSpecifications]
    Tags: Optional[Tags]
    ServiceLinkedRoleARN: Optional[ResourceName]
    MaxInstanceLifetime: Optional[MaxInstanceLifetime]
    Context: Optional[Context]
    DesiredCapacityType: Optional[XmlStringMaxLen255]
    DefaultInstanceWarmup: Optional[DefaultInstanceWarmup]


class InstanceMetadataOptions(TypedDict, total=False):
    """The metadata options for the instances. For more information, see
    `Configuring the Instance Metadata
    Options <https://docs.aws.amazon.com/autoscaling/ec2/userguide/create-launch-config.html#launch-configurations-imds>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    HttpTokens: Optional[InstanceMetadataHttpTokensState]
    HttpPutResponseHopLimit: Optional[InstanceMetadataHttpPutResponseHopLimit]
    HttpEndpoint: Optional[InstanceMetadataEndpointState]


class InstanceMonitoring(TypedDict, total=False):
    """Describes whether detailed monitoring is enabled for the Auto Scaling
    instances.
    """

    Enabled: Optional[MonitoringEnabled]


SecurityGroups = List[XmlString]


class CreateLaunchConfigurationType(ServiceRequest):
    LaunchConfigurationName: XmlStringMaxLen255
    ImageId: Optional[XmlStringMaxLen255]
    KeyName: Optional[XmlStringMaxLen255]
    SecurityGroups: Optional[SecurityGroups]
    ClassicLinkVPCId: Optional[XmlStringMaxLen255]
    ClassicLinkVPCSecurityGroups: Optional[ClassicLinkVPCSecurityGroups]
    UserData: Optional[XmlStringUserData]
    InstanceId: Optional[XmlStringMaxLen19]
    InstanceType: Optional[XmlStringMaxLen255]
    KernelId: Optional[XmlStringMaxLen255]
    RamdiskId: Optional[XmlStringMaxLen255]
    BlockDeviceMappings: Optional[BlockDeviceMappings]
    InstanceMonitoring: Optional[InstanceMonitoring]
    SpotPrice: Optional[SpotPrice]
    IamInstanceProfile: Optional[XmlStringMaxLen1600]
    EbsOptimized: Optional[EbsOptimized]
    AssociatePublicIpAddress: Optional[AssociatePublicIpAddress]
    PlacementTenancy: Optional[XmlStringMaxLen64]
    MetadataOptions: Optional[InstanceMetadataOptions]


class CreateOrUpdateTagsType(ServiceRequest):
    Tags: Tags


class MetricDimension(TypedDict, total=False):
    """Describes the dimension of a metric."""

    Name: MetricDimensionName
    Value: MetricDimensionValue


MetricDimensions = List[MetricDimension]


class CustomizedMetricSpecification(TypedDict, total=False):
    """Represents a CloudWatch metric of your choosing for a target tracking
    scaling policy to use with Amazon EC2 Auto Scaling.

    To create your customized metric specification:

    -  Add values for each required parameter from CloudWatch. You can use
       an existing metric, or a new metric that you create. To use your own
       metric, you must first publish the metric to CloudWatch. For more
       information, see `Publish custom
       metrics <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/publishingMetrics.html>`__
       in the *Amazon CloudWatch User Guide*.

    -  Choose a metric that changes proportionally with capacity. The value
       of the metric should increase or decrease in inverse proportion to
       the number of capacity units. That is, the value of the metric should
       decrease when capacity increases.

    For more information about the CloudWatch terminology below, see `Amazon
    CloudWatch
    concepts <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html>`__.

    Each individual service provides information about the metrics,
    namespace, and dimensions they use. For more information, see `Amazon
    Web Services services that publish CloudWatch
    metrics <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html>`__
    in the *Amazon CloudWatch User Guide*.
    """

    MetricName: MetricName
    Namespace: MetricNamespace
    Dimensions: Optional[MetricDimensions]
    Statistic: MetricStatistic
    Unit: Optional[MetricUnit]


class DeleteAutoScalingGroupType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    ForceDelete: Optional[ForceDelete]


class DeleteLifecycleHookAnswer(TypedDict, total=False):
    pass


class DeleteLifecycleHookType(ServiceRequest):
    LifecycleHookName: AsciiStringMaxLen255
    AutoScalingGroupName: XmlStringMaxLen255


class DeleteNotificationConfigurationType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    TopicARN: XmlStringMaxLen255


class DeletePolicyType(ServiceRequest):
    AutoScalingGroupName: Optional[XmlStringMaxLen255]
    PolicyName: ResourceName


class DeleteScheduledActionType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    ScheduledActionName: XmlStringMaxLen255


class DeleteTagsType(ServiceRequest):
    Tags: Tags


class DeleteWarmPoolAnswer(TypedDict, total=False):
    pass


class DeleteWarmPoolType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    ForceDelete: Optional[ForceDelete]


class DescribeAccountLimitsAnswer(TypedDict, total=False):
    MaxNumberOfAutoScalingGroups: Optional[MaxNumberOfAutoScalingGroups]
    MaxNumberOfLaunchConfigurations: Optional[MaxNumberOfLaunchConfigurations]
    NumberOfAutoScalingGroups: Optional[NumberOfAutoScalingGroups]
    NumberOfLaunchConfigurations: Optional[NumberOfLaunchConfigurations]


class DescribeAdjustmentTypesAnswer(TypedDict, total=False):
    AdjustmentTypes: Optional[AdjustmentTypes]


class DescribeAutoScalingInstancesType(ServiceRequest):
    InstanceIds: Optional[InstanceIds]
    MaxRecords: Optional[MaxRecords]
    NextToken: Optional[XmlString]


class DescribeAutoScalingNotificationTypesAnswer(TypedDict, total=False):
    AutoScalingNotificationTypes: Optional[AutoScalingNotificationTypes]


class DesiredConfiguration(TypedDict, total=False):
    """Describes the desired configuration for an instance refresh.

    If you specify a desired configuration, you must specify either a
    ``LaunchTemplate`` or a ``MixedInstancesPolicy``.
    """

    LaunchTemplate: Optional[LaunchTemplateSpecification]
    MixedInstancesPolicy: Optional[MixedInstancesPolicy]


class RefreshPreferences(TypedDict, total=False):
    """Describes the preferences for an instance refresh."""

    MinHealthyPercentage: Optional[IntPercent]
    InstanceWarmup: Optional[RefreshInstanceWarmup]
    CheckpointPercentages: Optional[CheckpointPercentages]
    CheckpointDelay: Optional[CheckpointDelay]
    SkipMatching: Optional[SkipMatching]


class InstanceRefreshWarmPoolProgress(TypedDict, total=False):
    """Reports the progress of an instance refresh on instances that are in the
    warm pool.
    """

    PercentageComplete: Optional[IntPercent]
    InstancesToUpdate: Optional[InstancesToUpdate]


class InstanceRefreshLivePoolProgress(TypedDict, total=False):
    """Reports the progress of an instance refresh on instances that are in the
    Auto Scaling group.
    """

    PercentageComplete: Optional[IntPercent]
    InstancesToUpdate: Optional[InstancesToUpdate]


class InstanceRefreshProgressDetails(TypedDict, total=False):
    """Reports the progress of an instance refresh on an Auto Scaling group
    that has a warm pool. This includes separate details for instances in
    the warm pool and instances in the Auto Scaling group (the live pool).
    """

    LivePoolProgress: Optional[InstanceRefreshLivePoolProgress]
    WarmPoolProgress: Optional[InstanceRefreshWarmPoolProgress]


class InstanceRefresh(TypedDict, total=False):
    """Describes an instance refresh for an Auto Scaling group."""

    InstanceRefreshId: Optional[XmlStringMaxLen255]
    AutoScalingGroupName: Optional[XmlStringMaxLen255]
    Status: Optional[InstanceRefreshStatus]
    StatusReason: Optional[XmlStringMaxLen1023]
    StartTime: Optional[TimestampType]
    EndTime: Optional[TimestampType]
    PercentageComplete: Optional[IntPercent]
    InstancesToUpdate: Optional[InstancesToUpdate]
    ProgressDetails: Optional[InstanceRefreshProgressDetails]
    Preferences: Optional[RefreshPreferences]
    DesiredConfiguration: Optional[DesiredConfiguration]


InstanceRefreshes = List[InstanceRefresh]


class DescribeInstanceRefreshesAnswer(TypedDict, total=False):
    InstanceRefreshes: Optional[InstanceRefreshes]
    NextToken: Optional[XmlString]


InstanceRefreshIds = List[XmlStringMaxLen255]


class DescribeInstanceRefreshesType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    InstanceRefreshIds: Optional[InstanceRefreshIds]
    NextToken: Optional[XmlString]
    MaxRecords: Optional[MaxRecords]


class DescribeLifecycleHookTypesAnswer(TypedDict, total=False):
    LifecycleHookTypes: Optional[AutoScalingNotificationTypes]


class LifecycleHook(TypedDict, total=False):
    """Describes a lifecycle hook. A lifecycle hook lets you create solutions
    that are aware of events in the Auto Scaling instance lifecycle, and
    then perform a custom action on instances when the corresponding
    lifecycle event occurs.
    """

    LifecycleHookName: Optional[AsciiStringMaxLen255]
    AutoScalingGroupName: Optional[XmlStringMaxLen255]
    LifecycleTransition: Optional[LifecycleTransition]
    NotificationTargetARN: Optional[NotificationTargetResourceName]
    RoleARN: Optional[XmlStringMaxLen255]
    NotificationMetadata: Optional[XmlStringMaxLen1023]
    HeartbeatTimeout: Optional[HeartbeatTimeout]
    GlobalTimeout: Optional[GlobalTimeout]
    DefaultResult: Optional[LifecycleActionResult]


LifecycleHooks = List[LifecycleHook]


class DescribeLifecycleHooksAnswer(TypedDict, total=False):
    LifecycleHooks: Optional[LifecycleHooks]


LifecycleHookNames = List[AsciiStringMaxLen255]


class DescribeLifecycleHooksType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    LifecycleHookNames: Optional[LifecycleHookNames]


class DescribeLoadBalancerTargetGroupsRequest(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    NextToken: Optional[XmlString]
    MaxRecords: Optional[MaxRecords]


class LoadBalancerTargetGroupState(TypedDict, total=False):
    """Describes the state of a target group."""

    LoadBalancerTargetGroupARN: Optional[XmlStringMaxLen511]
    State: Optional[XmlStringMaxLen255]


LoadBalancerTargetGroupStates = List[LoadBalancerTargetGroupState]


class DescribeLoadBalancerTargetGroupsResponse(TypedDict, total=False):
    LoadBalancerTargetGroups: Optional[LoadBalancerTargetGroupStates]
    NextToken: Optional[XmlString]


class DescribeLoadBalancersRequest(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    NextToken: Optional[XmlString]
    MaxRecords: Optional[MaxRecords]


class LoadBalancerState(TypedDict, total=False):
    """Describes the state of a Classic Load Balancer."""

    LoadBalancerName: Optional[XmlStringMaxLen255]
    State: Optional[XmlStringMaxLen255]


LoadBalancerStates = List[LoadBalancerState]


class DescribeLoadBalancersResponse(TypedDict, total=False):
    LoadBalancers: Optional[LoadBalancerStates]
    NextToken: Optional[XmlString]


class MetricGranularityType(TypedDict, total=False):
    """Describes a granularity of a metric."""

    Granularity: Optional[XmlStringMaxLen255]


MetricGranularityTypes = List[MetricGranularityType]


class MetricCollectionType(TypedDict, total=False):
    """Describes a metric."""

    Metric: Optional[XmlStringMaxLen255]


MetricCollectionTypes = List[MetricCollectionType]


class DescribeMetricCollectionTypesAnswer(TypedDict, total=False):
    Metrics: Optional[MetricCollectionTypes]
    Granularities: Optional[MetricGranularityTypes]


class NotificationConfiguration(TypedDict, total=False):
    """Describes a notification."""

    AutoScalingGroupName: Optional[XmlStringMaxLen255]
    TopicARN: Optional[XmlStringMaxLen255]
    NotificationType: Optional[XmlStringMaxLen255]


NotificationConfigurations = List[NotificationConfiguration]


class DescribeNotificationConfigurationsAnswer(TypedDict, total=False):
    NotificationConfigurations: NotificationConfigurations
    NextToken: Optional[XmlString]


class DescribeNotificationConfigurationsType(ServiceRequest):
    AutoScalingGroupNames: Optional[AutoScalingGroupNames]
    NextToken: Optional[XmlString]
    MaxRecords: Optional[MaxRecords]


PolicyTypes = List[XmlStringMaxLen64]
PolicyNames = List[ResourceName]


class DescribePoliciesType(ServiceRequest):
    AutoScalingGroupName: Optional[XmlStringMaxLen255]
    PolicyNames: Optional[PolicyNames]
    PolicyTypes: Optional[PolicyTypes]
    NextToken: Optional[XmlString]
    MaxRecords: Optional[MaxRecords]


class DescribeScalingActivitiesType(ServiceRequest):
    ActivityIds: Optional[ActivityIds]
    AutoScalingGroupName: Optional[XmlStringMaxLen255]
    IncludeDeletedGroups: Optional[IncludeDeletedGroups]
    MaxRecords: Optional[MaxRecords]
    NextToken: Optional[XmlString]


class DescribeScheduledActionsType(ServiceRequest):
    AutoScalingGroupName: Optional[XmlStringMaxLen255]
    ScheduledActionNames: Optional[ScheduledActionNames]
    StartTime: Optional[TimestampType]
    EndTime: Optional[TimestampType]
    NextToken: Optional[XmlString]
    MaxRecords: Optional[MaxRecords]


class DescribeTagsType(ServiceRequest):
    Filters: Optional[Filters]
    NextToken: Optional[XmlString]
    MaxRecords: Optional[MaxRecords]


class DescribeTerminationPolicyTypesAnswer(TypedDict, total=False):
    TerminationPolicyTypes: Optional[TerminationPolicies]


class DescribeWarmPoolAnswer(TypedDict, total=False):
    WarmPoolConfiguration: Optional[WarmPoolConfiguration]
    Instances: Optional[Instances]
    NextToken: Optional[XmlString]


class DescribeWarmPoolType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    MaxRecords: Optional[MaxRecords]
    NextToken: Optional[XmlString]


class DetachInstancesAnswer(TypedDict, total=False):
    Activities: Optional[Activities]


class DetachInstancesQuery(ServiceRequest):
    InstanceIds: Optional[InstanceIds]
    AutoScalingGroupName: XmlStringMaxLen255
    ShouldDecrementDesiredCapacity: ShouldDecrementDesiredCapacity


class DetachLoadBalancerTargetGroupsResultType(TypedDict, total=False):
    pass


class DetachLoadBalancerTargetGroupsType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    TargetGroupARNs: TargetGroupARNs


class DetachLoadBalancersResultType(TypedDict, total=False):
    pass


class DetachLoadBalancersType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    LoadBalancerNames: LoadBalancerNames


Metrics = List[XmlStringMaxLen255]


class DisableMetricsCollectionQuery(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    Metrics: Optional[Metrics]


class EnableMetricsCollectionQuery(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    Metrics: Optional[Metrics]
    Granularity: XmlStringMaxLen255


class EnterStandbyAnswer(TypedDict, total=False):
    Activities: Optional[Activities]


class EnterStandbyQuery(ServiceRequest):
    InstanceIds: Optional[InstanceIds]
    AutoScalingGroupName: XmlStringMaxLen255
    ShouldDecrementDesiredCapacity: ShouldDecrementDesiredCapacity


class ExecutePolicyType(ServiceRequest):
    AutoScalingGroupName: Optional[XmlStringMaxLen255]
    PolicyName: ResourceName
    HonorCooldown: Optional[HonorCooldown]
    MetricValue: Optional[MetricScale]
    BreachThreshold: Optional[MetricScale]


class ExitStandbyAnswer(TypedDict, total=False):
    Activities: Optional[Activities]


class ExitStandbyQuery(ServiceRequest):
    InstanceIds: Optional[InstanceIds]
    AutoScalingGroupName: XmlStringMaxLen255


class Metric(TypedDict, total=False):
    """Represents a specific metric."""

    Namespace: MetricNamespace
    MetricName: MetricName
    Dimensions: Optional[MetricDimensions]


class MetricStat(TypedDict, total=False):
    """This structure defines the CloudWatch metric to return, along with the
    statistic, period, and unit.

    For more information about the CloudWatch terminology below, see `Amazon
    CloudWatch
    concepts <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html>`__
    in the *Amazon CloudWatch User Guide*.
    """

    Metric: Metric
    Stat: XmlStringMetricStat
    Unit: Optional[MetricUnit]


class MetricDataQuery(TypedDict, total=False):
    """The metric data to return. Also defines whether this call is returning
    data for one metric only, or whether it is performing a math expression
    on the values of returned metric statistics to create a new time series.
    A time series is a series of data points, each of which is associated
    with a timestamp.

    For more information and examples, see `Advanced predictive scaling
    policy configurations using custom
    metrics <https://docs.aws.amazon.com/autoscaling/ec2/userguide/predictive-scaling-customized-metric-specification.html>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    Id: XmlStringMaxLen255
    Expression: Optional[XmlStringMaxLen1023]
    MetricStat: Optional[MetricStat]
    Label: Optional[XmlStringMetricLabel]
    ReturnData: Optional[ReturnData]


MetricDataQueries = List[MetricDataQuery]


class PredictiveScalingCustomizedCapacityMetric(TypedDict, total=False):
    """Describes a customized capacity metric for a predictive scaling policy."""

    MetricDataQueries: MetricDataQueries


class PredictiveScalingCustomizedLoadMetric(TypedDict, total=False):
    """Describes a custom load metric for a predictive scaling policy."""

    MetricDataQueries: MetricDataQueries


class PredictiveScalingCustomizedScalingMetric(TypedDict, total=False):
    """Describes a custom scaling metric for a predictive scaling policy."""

    MetricDataQueries: MetricDataQueries


class PredictiveScalingPredefinedLoadMetric(TypedDict, total=False):
    """Describes a load metric for a predictive scaling policy.

    When returned in the output of ``DescribePolicies``, it indicates that a
    predictive scaling policy uses individually specified load and scaling
    metrics instead of a metric pair.
    """

    PredefinedMetricType: PredefinedLoadMetricType
    ResourceLabel: Optional[XmlStringMaxLen1023]


class PredictiveScalingPredefinedScalingMetric(TypedDict, total=False):
    """Describes a scaling metric for a predictive scaling policy.

    When returned in the output of ``DescribePolicies``, it indicates that a
    predictive scaling policy uses individually specified load and scaling
    metrics instead of a metric pair.
    """

    PredefinedMetricType: PredefinedScalingMetricType
    ResourceLabel: Optional[XmlStringMaxLen1023]


class PredictiveScalingPredefinedMetricPair(TypedDict, total=False):
    """Represents a metric pair for a predictive scaling policy."""

    PredefinedMetricType: PredefinedMetricPairType
    ResourceLabel: Optional[XmlStringMaxLen1023]


class PredictiveScalingMetricSpecification(TypedDict, total=False):
    """This structure specifies the metrics and target utilization settings for
    a predictive scaling policy.

    You must specify either a metric pair, or a load metric and a scaling
    metric individually. Specifying a metric pair instead of individual
    metrics provides a simpler way to configure metrics for a scaling
    policy. You choose the metric pair, and the policy automatically knows
    the correct sum and average statistics to use for the load metric and
    the scaling metric.

    Example

    -  You create a predictive scaling policy and specify
       ``ALBRequestCount`` as the value for the metric pair and ``1000.0``
       as the target value. For this type of metric, you must provide the
       metric dimension for the corresponding target group, so you also
       provide a resource label for the Application Load Balancer target
       group that is attached to your Auto Scaling group.

    -  The number of requests the target group receives per minute provides
       the load metric, and the request count averaged between the members
       of the target group provides the scaling metric. In CloudWatch, this
       refers to the ``RequestCount`` and ``RequestCountPerTarget`` metrics,
       respectively.

    -  For optimal use of predictive scaling, you adhere to the best
       practice of using a dynamic scaling policy to automatically scale
       between the minimum capacity and maximum capacity in response to
       real-time changes in resource utilization.

    -  Amazon EC2 Auto Scaling consumes data points for the load metric over
       the last 14 days and creates an hourly load forecast for predictive
       scaling. (A minimum of 24 hours of data is required.)

    -  After creating the load forecast, Amazon EC2 Auto Scaling determines
       when to reduce or increase the capacity of your Auto Scaling group in
       each hour of the forecast period so that the average number of
       requests received by each instance is as close to 1000 requests per
       minute as possible at all times.

    For information about using custom metrics with predictive scaling, see
    `Advanced predictive scaling policy configurations using custom
    metrics <https://docs.aws.amazon.com/autoscaling/ec2/userguide/predictive-scaling-customized-metric-specification.html>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    TargetValue: MetricScale
    PredefinedMetricPairSpecification: Optional[PredictiveScalingPredefinedMetricPair]
    PredefinedScalingMetricSpecification: Optional[PredictiveScalingPredefinedScalingMetric]
    PredefinedLoadMetricSpecification: Optional[PredictiveScalingPredefinedLoadMetric]
    CustomizedScalingMetricSpecification: Optional[PredictiveScalingCustomizedScalingMetric]
    CustomizedLoadMetricSpecification: Optional[PredictiveScalingCustomizedLoadMetric]
    CustomizedCapacityMetricSpecification: Optional[PredictiveScalingCustomizedCapacityMetric]


class LoadForecast(TypedDict, total=False):
    """A ``GetPredictiveScalingForecast`` call returns the load forecast for a
    predictive scaling policy. This structure includes the data points for
    that load forecast, along with the timestamps of those data points and
    the metric specification.
    """

    Timestamps: PredictiveScalingForecastTimestamps
    Values: PredictiveScalingForecastValues
    MetricSpecification: PredictiveScalingMetricSpecification


LoadForecasts = List[LoadForecast]


class GetPredictiveScalingForecastAnswer(TypedDict, total=False):
    LoadForecast: LoadForecasts
    CapacityForecast: CapacityForecast
    UpdateTime: TimestampType


class GetPredictiveScalingForecastType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    PolicyName: XmlStringMaxLen255
    StartTime: TimestampType
    EndTime: TimestampType


class LaunchConfiguration(TypedDict, total=False):
    """Describes a launch configuration."""

    LaunchConfigurationName: XmlStringMaxLen255
    LaunchConfigurationARN: Optional[ResourceName]
    ImageId: XmlStringMaxLen255
    KeyName: Optional[XmlStringMaxLen255]
    SecurityGroups: Optional[SecurityGroups]
    ClassicLinkVPCId: Optional[XmlStringMaxLen255]
    ClassicLinkVPCSecurityGroups: Optional[ClassicLinkVPCSecurityGroups]
    UserData: Optional[XmlStringUserData]
    InstanceType: XmlStringMaxLen255
    KernelId: Optional[XmlStringMaxLen255]
    RamdiskId: Optional[XmlStringMaxLen255]
    BlockDeviceMappings: Optional[BlockDeviceMappings]
    InstanceMonitoring: Optional[InstanceMonitoring]
    SpotPrice: Optional[SpotPrice]
    IamInstanceProfile: Optional[XmlStringMaxLen1600]
    CreatedTime: TimestampType
    EbsOptimized: Optional[EbsOptimized]
    AssociatePublicIpAddress: Optional[AssociatePublicIpAddress]
    PlacementTenancy: Optional[XmlStringMaxLen64]
    MetadataOptions: Optional[InstanceMetadataOptions]


class LaunchConfigurationNameType(ServiceRequest):
    LaunchConfigurationName: XmlStringMaxLen255


LaunchConfigurationNames = List[XmlStringMaxLen255]


class LaunchConfigurationNamesType(ServiceRequest):
    LaunchConfigurationNames: Optional[LaunchConfigurationNames]
    NextToken: Optional[XmlString]
    MaxRecords: Optional[MaxRecords]


LaunchConfigurations = List[LaunchConfiguration]


class LaunchConfigurationsType(TypedDict, total=False):
    LaunchConfigurations: LaunchConfigurations
    NextToken: Optional[XmlString]


PredictiveScalingMetricSpecifications = List[PredictiveScalingMetricSpecification]


class PredictiveScalingConfiguration(TypedDict, total=False):
    """Represents a predictive scaling policy configuration to use with Amazon
    EC2 Auto Scaling.
    """

    MetricSpecifications: PredictiveScalingMetricSpecifications
    Mode: Optional[PredictiveScalingMode]
    SchedulingBufferTime: Optional[PredictiveScalingSchedulingBufferTime]
    MaxCapacityBreachBehavior: Optional[PredictiveScalingMaxCapacityBreachBehavior]
    MaxCapacityBuffer: Optional[PredictiveScalingMaxCapacityBuffer]


class PredefinedMetricSpecification(TypedDict, total=False):
    """Represents a predefined metric for a target tracking scaling policy to
    use with Amazon EC2 Auto Scaling.
    """

    PredefinedMetricType: MetricType
    ResourceLabel: Optional[XmlStringMaxLen1023]


class TargetTrackingConfiguration(TypedDict, total=False):
    """Represents a target tracking scaling policy configuration to use with
    Amazon EC2 Auto Scaling.
    """

    PredefinedMetricSpecification: Optional[PredefinedMetricSpecification]
    CustomizedMetricSpecification: Optional[CustomizedMetricSpecification]
    TargetValue: MetricScale
    DisableScaleIn: Optional[DisableScaleIn]


class StepAdjustment(TypedDict, total=False):
    """Describes information used to create a step adjustment for a step
    scaling policy.

    For the following examples, suppose that you have an alarm with a breach
    threshold of 50:

    -  To trigger the adjustment when the metric is greater than or equal to
       50 and less than 60, specify a lower bound of 0 and an upper bound of
       10.

    -  To trigger the adjustment when the metric is greater than 40 and less
       than or equal to 50, specify a lower bound of -10 and an upper bound
       of 0.

    There are a few rules for the step adjustments for your step policy:

    -  The ranges of your step adjustments can't overlap or have a gap.

    -  At most, one step adjustment can have a null lower bound. If one step
       adjustment has a negative lower bound, then there must be a step
       adjustment with a null lower bound.

    -  At most, one step adjustment can have a null upper bound. If one step
       adjustment has a positive upper bound, then there must be a step
       adjustment with a null upper bound.

    -  The upper and lower bound can't be null in the same step adjustment.

    For more information, see `Step
    adjustments <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-simple-step.html#as-scaling-steps>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    MetricIntervalLowerBound: Optional[MetricScale]
    MetricIntervalUpperBound: Optional[MetricScale]
    ScalingAdjustment: PolicyIncrement


StepAdjustments = List[StepAdjustment]


class ScalingPolicy(TypedDict, total=False):
    """Describes a scaling policy."""

    AutoScalingGroupName: Optional[XmlStringMaxLen255]
    PolicyName: Optional[XmlStringMaxLen255]
    PolicyARN: Optional[ResourceName]
    PolicyType: Optional[XmlStringMaxLen64]
    AdjustmentType: Optional[XmlStringMaxLen255]
    MinAdjustmentStep: Optional[MinAdjustmentStep]
    MinAdjustmentMagnitude: Optional[MinAdjustmentMagnitude]
    ScalingAdjustment: Optional[PolicyIncrement]
    Cooldown: Optional[Cooldown]
    StepAdjustments: Optional[StepAdjustments]
    MetricAggregationType: Optional[XmlStringMaxLen32]
    EstimatedInstanceWarmup: Optional[EstimatedInstanceWarmup]
    Alarms: Optional[Alarms]
    TargetTrackingConfiguration: Optional[TargetTrackingConfiguration]
    Enabled: Optional[ScalingPolicyEnabled]
    PredictiveScalingConfiguration: Optional[PredictiveScalingConfiguration]


ScalingPolicies = List[ScalingPolicy]


class PoliciesType(TypedDict, total=False):
    ScalingPolicies: Optional[ScalingPolicies]
    NextToken: Optional[XmlString]


class PolicyARNType(TypedDict, total=False):
    """Contains the output of PutScalingPolicy."""

    PolicyARN: Optional[ResourceName]
    Alarms: Optional[Alarms]


ProcessNames = List[XmlStringMaxLen255]


class ProcessType(TypedDict, total=False):
    """Describes a process type.

    For more information, see `Scaling
    processes <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-suspend-resume-processes.html#process-types>`__
    in the *Amazon EC2 Auto Scaling User Guide*.
    """

    ProcessName: XmlStringMaxLen255


Processes = List[ProcessType]


class ProcessesType(TypedDict, total=False):
    Processes: Optional[Processes]


class PutLifecycleHookAnswer(TypedDict, total=False):
    pass


class PutLifecycleHookType(ServiceRequest):
    LifecycleHookName: AsciiStringMaxLen255
    AutoScalingGroupName: XmlStringMaxLen255
    LifecycleTransition: Optional[LifecycleTransition]
    RoleARN: Optional[XmlStringMaxLen255]
    NotificationTargetARN: Optional[NotificationTargetResourceName]
    NotificationMetadata: Optional[XmlStringMaxLen1023]
    HeartbeatTimeout: Optional[HeartbeatTimeout]
    DefaultResult: Optional[LifecycleActionResult]


class PutNotificationConfigurationType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    TopicARN: XmlStringMaxLen255
    NotificationTypes: AutoScalingNotificationTypes


class PutScalingPolicyType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    PolicyName: XmlStringMaxLen255
    PolicyType: Optional[XmlStringMaxLen64]
    AdjustmentType: Optional[XmlStringMaxLen255]
    MinAdjustmentStep: Optional[MinAdjustmentStep]
    MinAdjustmentMagnitude: Optional[MinAdjustmentMagnitude]
    ScalingAdjustment: Optional[PolicyIncrement]
    Cooldown: Optional[Cooldown]
    MetricAggregationType: Optional[XmlStringMaxLen32]
    StepAdjustments: Optional[StepAdjustments]
    EstimatedInstanceWarmup: Optional[EstimatedInstanceWarmup]
    TargetTrackingConfiguration: Optional[TargetTrackingConfiguration]
    Enabled: Optional[ScalingPolicyEnabled]
    PredictiveScalingConfiguration: Optional[PredictiveScalingConfiguration]


class PutScheduledUpdateGroupActionType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    ScheduledActionName: XmlStringMaxLen255
    Time: Optional[TimestampType]
    StartTime: Optional[TimestampType]
    EndTime: Optional[TimestampType]
    Recurrence: Optional[XmlStringMaxLen255]
    MinSize: Optional[AutoScalingGroupMinSize]
    MaxSize: Optional[AutoScalingGroupMaxSize]
    DesiredCapacity: Optional[AutoScalingGroupDesiredCapacity]
    TimeZone: Optional[XmlStringMaxLen255]


class PutWarmPoolAnswer(TypedDict, total=False):
    pass


class PutWarmPoolType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    MaxGroupPreparedCapacity: Optional[MaxGroupPreparedCapacity]
    MinSize: Optional[WarmPoolMinSize]
    PoolState: Optional[WarmPoolState]
    InstanceReusePolicy: Optional[InstanceReusePolicy]


class RecordLifecycleActionHeartbeatAnswer(TypedDict, total=False):
    pass


class RecordLifecycleActionHeartbeatType(ServiceRequest):
    LifecycleHookName: AsciiStringMaxLen255
    AutoScalingGroupName: ResourceName
    LifecycleActionToken: Optional[LifecycleActionToken]
    InstanceId: Optional[XmlStringMaxLen19]


class ScalingProcessQuery(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    ScalingProcesses: Optional[ProcessNames]


class ScheduledUpdateGroupAction(TypedDict, total=False):
    """Describes a scheduled scaling action."""

    AutoScalingGroupName: Optional[XmlStringMaxLen255]
    ScheduledActionName: Optional[XmlStringMaxLen255]
    ScheduledActionARN: Optional[ResourceName]
    Time: Optional[TimestampType]
    StartTime: Optional[TimestampType]
    EndTime: Optional[TimestampType]
    Recurrence: Optional[XmlStringMaxLen255]
    MinSize: Optional[AutoScalingGroupMinSize]
    MaxSize: Optional[AutoScalingGroupMaxSize]
    DesiredCapacity: Optional[AutoScalingGroupDesiredCapacity]
    TimeZone: Optional[XmlStringMaxLen255]


ScheduledUpdateGroupActions = List[ScheduledUpdateGroupAction]


class ScheduledActionsType(TypedDict, total=False):
    ScheduledUpdateGroupActions: Optional[ScheduledUpdateGroupActions]
    NextToken: Optional[XmlString]


class SetDesiredCapacityType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    DesiredCapacity: AutoScalingGroupDesiredCapacity
    HonorCooldown: Optional[HonorCooldown]


class SetInstanceHealthQuery(ServiceRequest):
    InstanceId: XmlStringMaxLen19
    HealthStatus: XmlStringMaxLen32
    ShouldRespectGracePeriod: Optional[ShouldRespectGracePeriod]


class SetInstanceProtectionAnswer(TypedDict, total=False):
    pass


class SetInstanceProtectionQuery(ServiceRequest):
    InstanceIds: InstanceIds
    AutoScalingGroupName: XmlStringMaxLen255
    ProtectedFromScaleIn: ProtectedFromScaleIn


class StartInstanceRefreshAnswer(TypedDict, total=False):
    InstanceRefreshId: Optional[XmlStringMaxLen255]


class StartInstanceRefreshType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    Strategy: Optional[RefreshStrategy]
    DesiredConfiguration: Optional[DesiredConfiguration]
    Preferences: Optional[RefreshPreferences]


class TagsType(TypedDict, total=False):
    Tags: Optional[TagDescriptionList]
    NextToken: Optional[XmlString]


class TerminateInstanceInAutoScalingGroupType(ServiceRequest):
    InstanceId: XmlStringMaxLen19
    ShouldDecrementDesiredCapacity: ShouldDecrementDesiredCapacity


class UpdateAutoScalingGroupType(ServiceRequest):
    AutoScalingGroupName: XmlStringMaxLen255
    LaunchConfigurationName: Optional[XmlStringMaxLen255]
    LaunchTemplate: Optional[LaunchTemplateSpecification]
    MixedInstancesPolicy: Optional[MixedInstancesPolicy]
    MinSize: Optional[AutoScalingGroupMinSize]
    MaxSize: Optional[AutoScalingGroupMaxSize]
    DesiredCapacity: Optional[AutoScalingGroupDesiredCapacity]
    DefaultCooldown: Optional[Cooldown]
    AvailabilityZones: Optional[AvailabilityZones]
    HealthCheckType: Optional[XmlStringMaxLen32]
    HealthCheckGracePeriod: Optional[HealthCheckGracePeriod]
    PlacementGroup: Optional[XmlStringMaxLen255]
    VPCZoneIdentifier: Optional[XmlStringMaxLen2047]
    TerminationPolicies: Optional[TerminationPolicies]
    NewInstancesProtectedFromScaleIn: Optional[InstanceProtected]
    ServiceLinkedRoleARN: Optional[ResourceName]
    MaxInstanceLifetime: Optional[MaxInstanceLifetime]
    CapacityRebalance: Optional[CapacityRebalanceEnabled]
    Context: Optional[Context]
    DesiredCapacityType: Optional[XmlStringMaxLen255]
    DefaultInstanceWarmup: Optional[DefaultInstanceWarmup]


class AutoscalingApi:

    service = "autoscaling"
    version = "2011-01-01"

    @handler("AttachInstances")
    def attach_instances(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        instance_ids: InstanceIds = None,
    ) -> None:
        """Attaches one or more EC2 instances to the specified Auto Scaling group.

        When you attach instances, Amazon EC2 Auto Scaling increases the desired
        capacity of the group by the number of instances being attached. If the
        number of instances being attached plus the desired capacity of the
        group exceeds the maximum size of the group, the operation fails.

        If there is a Classic Load Balancer attached to your Auto Scaling group,
        the instances are also registered with the load balancer. If there are
        target groups attached to your Auto Scaling group, the instances are
        also registered with the target groups.

        For more information, see `Attach EC2 instances to your Auto Scaling
        group <https://docs.aws.amazon.com/autoscaling/ec2/userguide/attach-instance-asg.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param instance_ids: The IDs of the instances.
        :raises ResourceContentionFault:
        :raises ServiceLinkedRoleFailure:
        """
        raise NotImplementedError

    @handler("AttachLoadBalancerTargetGroups")
    def attach_load_balancer_target_groups(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        target_group_arns: TargetGroupARNs,
    ) -> AttachLoadBalancerTargetGroupsResultType:
        """Attaches one or more target groups to the specified Auto Scaling group.

        This operation is used with the following load balancer types:

        -  Application Load Balancer - Operates at the application layer (layer
           7) and supports HTTP and HTTPS.

        -  Network Load Balancer - Operates at the transport layer (layer 4) and
           supports TCP, TLS, and UDP.

        -  Gateway Load Balancer - Operates at the network layer (layer 3).

        To describe the target groups for an Auto Scaling group, call the
        DescribeLoadBalancerTargetGroups API. To detach the target group from
        the Auto Scaling group, call the DetachLoadBalancerTargetGroups API.

        This operation is additive and does not detach existing target groups or
        Classic Load Balancers from the Auto Scaling group.

        For more information, see `Elastic Load Balancing and Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/autoscaling-load-balancer.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param target_group_arns: The Amazon Resource Names (ARN) of the target groups.
        :returns: AttachLoadBalancerTargetGroupsResultType
        :raises ResourceContentionFault:
        :raises ServiceLinkedRoleFailure:
        """
        raise NotImplementedError

    @handler("AttachLoadBalancers")
    def attach_load_balancers(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        load_balancer_names: LoadBalancerNames,
    ) -> AttachLoadBalancersResultType:
        """To attach an Application Load Balancer, Network Load Balancer, or
        Gateway Load Balancer, use the AttachLoadBalancerTargetGroups API
        operation instead.

        Attaches one or more Classic Load Balancers to the specified Auto
        Scaling group. Amazon EC2 Auto Scaling registers the running instances
        with these Classic Load Balancers.

        To describe the load balancers for an Auto Scaling group, call the
        DescribeLoadBalancers API. To detach the load balancer from the Auto
        Scaling group, call the DetachLoadBalancers API.

        This operation is additive and does not detach existing Classic Load
        Balancers or target groups from the Auto Scaling group.

        For more information, see `Elastic Load Balancing and Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/autoscaling-load-balancer.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param load_balancer_names: The names of the load balancers.
        :returns: AttachLoadBalancersResultType
        :raises ResourceContentionFault:
        :raises ServiceLinkedRoleFailure:
        """
        raise NotImplementedError

    @handler("BatchDeleteScheduledAction")
    def batch_delete_scheduled_action(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        scheduled_action_names: ScheduledActionNames,
    ) -> BatchDeleteScheduledActionAnswer:
        """Deletes one or more scheduled actions for the specified Auto Scaling
        group.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param scheduled_action_names: The names of the scheduled actions to delete.
        :returns: BatchDeleteScheduledActionAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("BatchPutScheduledUpdateGroupAction")
    def batch_put_scheduled_update_group_action(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        scheduled_update_group_actions: ScheduledUpdateGroupActionRequests,
    ) -> BatchPutScheduledUpdateGroupActionAnswer:
        """Creates or updates one or more scheduled scaling actions for an Auto
        Scaling group.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param scheduled_update_group_actions: One or more scheduled actions.
        :returns: BatchPutScheduledUpdateGroupActionAnswer
        :raises AlreadyExistsFault:
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("CancelInstanceRefresh")
    def cancel_instance_refresh(
        self, context: RequestContext, auto_scaling_group_name: XmlStringMaxLen255
    ) -> CancelInstanceRefreshAnswer:
        """Cancels an instance refresh operation in progress. Cancellation does not
        roll back any replacements that have already been completed, but it
        prevents new replacements from being started.

        This operation is part of the `instance refresh
        feature <https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html>`__
        in Amazon EC2 Auto Scaling, which helps you update instances in your
        Auto Scaling group after you make configuration changes.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :returns: CancelInstanceRefreshAnswer
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        :raises ActiveInstanceRefreshNotFoundFault:
        """
        raise NotImplementedError

    @handler("CompleteLifecycleAction")
    def complete_lifecycle_action(
        self,
        context: RequestContext,
        lifecycle_hook_name: AsciiStringMaxLen255,
        auto_scaling_group_name: ResourceName,
        lifecycle_action_result: LifecycleActionResult,
        lifecycle_action_token: LifecycleActionToken = None,
        instance_id: XmlStringMaxLen19 = None,
    ) -> CompleteLifecycleActionAnswer:
        """Completes the lifecycle action for the specified token or instance with
        the specified result.

        This step is a part of the procedure for adding a lifecycle hook to an
        Auto Scaling group:

        #. (Optional) Create a launch template or launch configuration with a
           user data script that runs while an instance is in a wait state due
           to a lifecycle hook.

        #. (Optional) Create a Lambda function and a rule that allows Amazon
           EventBridge to invoke your Lambda function when an instance is put
           into a wait state due to a lifecycle hook.

        #. (Optional) Create a notification target and an IAM role. The target
           can be either an Amazon SQS queue or an Amazon SNS topic. The role
           allows Amazon EC2 Auto Scaling to publish lifecycle notifications to
           the target.

        #. Create the lifecycle hook. Specify whether the hook is used when the
           instances launch or terminate.

        #. If you need more time, record the lifecycle action heartbeat to keep
           the instance in a wait state.

        #. **If you finish before the timeout period ends, send a callback by
           using the CompleteLifecycleAction API call.**

        For more information, see `Amazon EC2 Auto Scaling lifecycle
        hooks <https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param lifecycle_hook_name: The name of the lifecycle hook.
        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param lifecycle_action_result: The action for the group to take.
        :param lifecycle_action_token: A universally unique identifier (UUID) that identifies a specific
        lifecycle action associated with an instance.
        :param instance_id: The ID of the instance.
        :returns: CompleteLifecycleActionAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("CreateAutoScalingGroup", expand=False)
    def create_auto_scaling_group(
        self, context: RequestContext, request: CreateAutoScalingGroupType
    ) -> None:
        """**We strongly recommend using a launch template when calling this
        operation to ensure full functionality for Amazon EC2 Auto Scaling and
        Amazon EC2.**

        Creates an Auto Scaling group with the specified name and attributes.

        If you exceed your maximum limit of Auto Scaling groups, the call fails.
        To query this limit, call the DescribeAccountLimits API. For information
        about updating this limit, see `Amazon EC2 Auto Scaling service
        quotas <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-account-limits.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        For introductory exercises for creating an Auto Scaling group, see
        `Getting started with Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/GettingStartedTutorial.html>`__
        and `Tutorial: Set up a scaled and load-balanced
        application <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-register-lbs-with-asg.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*. For more information, see
        `Auto Scaling
        groups <https://docs.aws.amazon.com/autoscaling/ec2/userguide/AutoScalingGroup.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        Every Auto Scaling group has three size parameters (``DesiredCapacity``,
        ``MaxSize``, and ``MinSize``). Usually, you set these sizes based on a
        specific number of instances. However, if you configure a mixed
        instances policy that defines weights for the instance types, you must
        specify these sizes with the same units that you use for weighting
        instances.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param min_size: The minimum size of the group.
        :param max_size: The maximum size of the group.
        :param launch_configuration_name: The name of the launch configuration to use to launch instances.
        :param launch_template: Parameters used to specify the launch template and version to use to
        launch instances.
        :param mixed_instances_policy: An embedded object that specifies a mixed instances policy.
        :param instance_id: The ID of the instance used to base the launch configuration on.
        :param desired_capacity: The desired capacity is the initial capacity of the Auto Scaling group
        at the time of its creation and the capacity it attempts to maintain.
        :param default_cooldown: *Only needed if you use simple scaling policies.
        :param availability_zones: A list of Availability Zones where instances in the Auto Scaling group
        can be created.
        :param load_balancer_names: A list of Classic Load Balancers associated with this Auto Scaling
        group.
        :param target_group_arns: The Amazon Resource Names (ARN) of the target groups to associate with
        the Auto Scaling group.
        :param health_check_type: The service to use for the health checks.
        :param health_check_grace_period: The amount of time, in seconds, that Amazon EC2 Auto Scaling waits
        before checking the health status of an EC2 instance that has come into
        service and marking it unhealthy due to a failed Elastic Load Balancing
        or custom health check.
        :param placement_group: The name of an existing placement group into which to launch your
        instances.
        :param vpc_zone_identifier: A comma-separated list of subnet IDs for a virtual private cloud (VPC)
        where instances in the Auto Scaling group can be created.
        :param termination_policies: A policy or a list of policies that are used to select the instance to
        terminate.
        :param new_instances_protected_from_scale_in: Indicates whether newly launched instances are protected from
        termination by Amazon EC2 Auto Scaling when scaling in.
        :param capacity_rebalance: Indicates whether Capacity Rebalancing is enabled.
        :param lifecycle_hook_specification_list: One or more lifecycle hooks for the group, which specify actions to
        perform when Amazon EC2 Auto Scaling launches or terminates instances.
        :param tags: One or more tags.
        :param service_linked_role_arn: The Amazon Resource Name (ARN) of the service-linked role that the Auto
        Scaling group uses to call other Amazon Web Services on your behalf.
        :param max_instance_lifetime: The maximum amount of time, in seconds, that an instance can be in
        service.
        :param context: Reserved.
        :param desired_capacity_type: The unit of measurement for the value specified for desired capacity.
        :param default_instance_warmup: The amount of time, in seconds, until a newly launched instance can
        contribute to the Amazon CloudWatch metrics.
        :raises AlreadyExistsFault:
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        :raises ServiceLinkedRoleFailure:
        """
        raise NotImplementedError

    @handler("CreateLaunchConfiguration")
    def create_launch_configuration(
        self,
        context: RequestContext,
        launch_configuration_name: XmlStringMaxLen255,
        image_id: XmlStringMaxLen255 = None,
        key_name: XmlStringMaxLen255 = None,
        security_groups: SecurityGroups = None,
        classic_link_vpc_id: XmlStringMaxLen255 = None,
        classic_link_vpc_security_groups: ClassicLinkVPCSecurityGroups = None,
        user_data: XmlStringUserData = None,
        instance_id: XmlStringMaxLen19 = None,
        instance_type: XmlStringMaxLen255 = None,
        kernel_id: XmlStringMaxLen255 = None,
        ramdisk_id: XmlStringMaxLen255 = None,
        block_device_mappings: BlockDeviceMappings = None,
        instance_monitoring: InstanceMonitoring = None,
        spot_price: SpotPrice = None,
        iam_instance_profile: XmlStringMaxLen1600 = None,
        ebs_optimized: EbsOptimized = None,
        associate_public_ip_address: AssociatePublicIpAddress = None,
        placement_tenancy: XmlStringMaxLen64 = None,
        metadata_options: InstanceMetadataOptions = None,
    ) -> None:
        """Creates a launch configuration.

        If you exceed your maximum limit of launch configurations, the call
        fails. To query this limit, call the DescribeAccountLimits API. For
        information about updating this limit, see `Amazon EC2 Auto Scaling
        service
        quotas <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-account-limits.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        For more information, see `Launch
        configurations <https://docs.aws.amazon.com/autoscaling/ec2/userguide/LaunchConfiguration.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param launch_configuration_name: The name of the launch configuration.
        :param image_id: The ID of the Amazon Machine Image (AMI) that was assigned during
        registration.
        :param key_name: The name of the key pair.
        :param security_groups: A list that contains the security groups to assign to the instances in
        the Auto Scaling group.
        :param classic_link_vpc_id: *EC2-Classic retires on August 15, 2022.
        :param classic_link_vpc_security_groups: *EC2-Classic retires on August 15, 2022.
        :param user_data: The user data to make available to the launched EC2 instances.
        :param instance_id: The ID of the instance to use to create the launch configuration.
        :param instance_type: Specifies the instance type of the EC2 instance.
        :param kernel_id: The ID of the kernel associated with the AMI.
        :param ramdisk_id: The ID of the RAM disk to select.
        :param block_device_mappings: A block device mapping, which specifies the block devices for the
        instance.
        :param instance_monitoring: Controls whether instances in this group are launched with detailed
        (``true``) or basic (``false``) monitoring.
        :param spot_price: The maximum hourly price to be paid for any Spot Instance launched to
        fulfill the request.
        :param iam_instance_profile: The name or the Amazon Resource Name (ARN) of the instance profile
        associated with the IAM role for the instance.
        :param ebs_optimized: Specifies whether the launch configuration is optimized for EBS I/O
        (``true``) or not (``false``).
        :param associate_public_ip_address: For Auto Scaling groups that are running in a virtual private cloud
        (VPC), specifies whether to assign a public IP address to the group's
        instances.
        :param placement_tenancy: The tenancy of the instance.
        :param metadata_options: The metadata options for the instances.
        :raises AlreadyExistsFault:
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("CreateOrUpdateTags")
    def create_or_update_tags(self, context: RequestContext, tags: Tags) -> None:
        """Creates or updates tags for the specified Auto Scaling group.

        When you specify a tag with a key that already exists, the operation
        overwrites the previous tag definition, and you do not get an error
        message.

        For more information, see `Tagging Auto Scaling groups and
        instances <https://docs.aws.amazon.com/autoscaling/ec2/userguide/autoscaling-tagging.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param tags: One or more tags.
        :raises LimitExceededFault:
        :raises AlreadyExistsFault:
        :raises ResourceContentionFault:
        :raises ResourceInUseFault:
        """
        raise NotImplementedError

    @handler("DeleteAutoScalingGroup")
    def delete_auto_scaling_group(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        force_delete: ForceDelete = None,
    ) -> None:
        """Deletes the specified Auto Scaling group.

        If the group has instances or scaling activities in progress, you must
        specify the option to force the deletion in order for it to succeed.

        If the group has policies, deleting the group deletes the policies, the
        underlying alarm actions, and any alarm that no longer has an associated
        action.

        To remove instances from the Auto Scaling group before deleting it, call
        the DetachInstances API with the list of instances and the option to
        decrement the desired capacity. This ensures that Amazon EC2 Auto
        Scaling does not launch replacement instances.

        To terminate all instances before deleting the Auto Scaling group, call
        the UpdateAutoScalingGroup API and set the minimum size and desired
        capacity of the Auto Scaling group to zero.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param force_delete: Specifies that the group is to be deleted along with all instances
        associated with the group, without waiting for all instances to be
        terminated.
        :raises ScalingActivityInProgressFault:
        :raises ResourceInUseFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DeleteLaunchConfiguration")
    def delete_launch_configuration(
        self, context: RequestContext, launch_configuration_name: XmlStringMaxLen255
    ) -> None:
        """Deletes the specified launch configuration.

        The launch configuration must not be attached to an Auto Scaling group.
        When this call completes, the launch configuration is no longer
        available for use.

        :param launch_configuration_name: The name of the launch configuration.
        :raises ResourceInUseFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DeleteLifecycleHook")
    def delete_lifecycle_hook(
        self,
        context: RequestContext,
        lifecycle_hook_name: AsciiStringMaxLen255,
        auto_scaling_group_name: XmlStringMaxLen255,
    ) -> DeleteLifecycleHookAnswer:
        """Deletes the specified lifecycle hook.

        If there are any outstanding lifecycle actions, they are completed first
        (``ABANDON`` for launching instances, ``CONTINUE`` for terminating
        instances).

        :param lifecycle_hook_name: The name of the lifecycle hook.
        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :returns: DeleteLifecycleHookAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DeleteNotificationConfiguration")
    def delete_notification_configuration(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        topic_arn: XmlStringMaxLen255,
    ) -> None:
        """Deletes the specified notification.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param topic_arn: The Amazon Resource Name (ARN) of the Amazon SNS topic.
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DeletePolicy")
    def delete_policy(
        self,
        context: RequestContext,
        policy_name: ResourceName,
        auto_scaling_group_name: XmlStringMaxLen255 = None,
    ) -> None:
        """Deletes the specified scaling policy.

        Deleting either a step scaling policy or a simple scaling policy deletes
        the underlying alarm action, but does not delete the alarm, even if it
        no longer has an associated action.

        For more information, see `Deleting a scaling
        policy <https://docs.aws.amazon.com/autoscaling/ec2/userguide/deleting-scaling-policy.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param policy_name: The name or Amazon Resource Name (ARN) of the policy.
        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :raises ResourceContentionFault:
        :raises ServiceLinkedRoleFailure:
        """
        raise NotImplementedError

    @handler("DeleteScheduledAction")
    def delete_scheduled_action(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        scheduled_action_name: XmlStringMaxLen255,
    ) -> None:
        """Deletes the specified scheduled action.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param scheduled_action_name: The name of the action to delete.
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DeleteTags")
    def delete_tags(self, context: RequestContext, tags: Tags) -> None:
        """Deletes the specified tags.

        :param tags: One or more tags.
        :raises ResourceContentionFault:
        :raises ResourceInUseFault:
        """
        raise NotImplementedError

    @handler("DeleteWarmPool")
    def delete_warm_pool(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        force_delete: ForceDelete = None,
    ) -> DeleteWarmPoolAnswer:
        """Deletes the warm pool for the specified Auto Scaling group.

        For more information, see `Warm pools for Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-warm-pools.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param force_delete: Specifies that the warm pool is to be deleted along with all of its
        associated instances, without waiting for all instances to be
        terminated.
        :returns: DeleteWarmPoolAnswer
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        :raises ScalingActivityInProgressFault:
        :raises ResourceInUseFault:
        """
        raise NotImplementedError

    @handler("DescribeAccountLimits")
    def describe_account_limits(
        self,
        context: RequestContext,
    ) -> DescribeAccountLimitsAnswer:
        """Describes the current Amazon EC2 Auto Scaling resource quotas for your
        account.

        When you establish an Amazon Web Services account, the account has
        initial quotas on the maximum number of Auto Scaling groups and launch
        configurations that you can create in a given Region. For more
        information, see `Amazon EC2 Auto Scaling service
        quotas <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-account-limits.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :returns: DescribeAccountLimitsAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeAdjustmentTypes")
    def describe_adjustment_types(
        self,
        context: RequestContext,
    ) -> DescribeAdjustmentTypesAnswer:
        """Describes the available adjustment types for step scaling and simple
        scaling policies.

        The following adjustment types are supported:

        -  ``ChangeInCapacity``

        -  ``ExactCapacity``

        -  ``PercentChangeInCapacity``

        :returns: DescribeAdjustmentTypesAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeAutoScalingGroups")
    def describe_auto_scaling_groups(
        self,
        context: RequestContext,
        auto_scaling_group_names: AutoScalingGroupNames = None,
        next_token: XmlString = None,
        max_records: MaxRecords = None,
        filters: Filters = None,
    ) -> AutoScalingGroupsType:
        """Gets information about the Auto Scaling groups in the account and
        Region.

        If you specify Auto Scaling group names, the output includes information
        for only the specified Auto Scaling groups. If you specify filters, the
        output includes information for only those Auto Scaling groups that meet
        the filter criteria. If you do not specify group names or filters, the
        output includes information for all Auto Scaling groups.

        This operation also returns information about instances in Auto Scaling
        groups. To retrieve information about the instances in a warm pool, you
        must call the DescribeWarmPool API.

        :param auto_scaling_group_names: The names of the Auto Scaling groups.
        :param next_token: The token for the next set of items to return.
        :param max_records: The maximum number of items to return with this call.
        :param filters: One or more filters to limit the results based on specific tags.
        :returns: AutoScalingGroupsType
        :raises InvalidNextToken:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeAutoScalingInstances")
    def describe_auto_scaling_instances(
        self,
        context: RequestContext,
        instance_ids: InstanceIds = None,
        max_records: MaxRecords = None,
        next_token: XmlString = None,
    ) -> AutoScalingInstancesType:
        """Gets information about the Auto Scaling instances in the account and
        Region.

        :param instance_ids: The IDs of the instances.
        :param max_records: The maximum number of items to return with this call.
        :param next_token: The token for the next set of items to return.
        :returns: AutoScalingInstancesType
        :raises InvalidNextToken:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeAutoScalingNotificationTypes")
    def describe_auto_scaling_notification_types(
        self,
        context: RequestContext,
    ) -> DescribeAutoScalingNotificationTypesAnswer:
        """Describes the notification types that are supported by Amazon EC2 Auto
        Scaling.

        :returns: DescribeAutoScalingNotificationTypesAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeInstanceRefreshes")
    def describe_instance_refreshes(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        instance_refresh_ids: InstanceRefreshIds = None,
        next_token: XmlString = None,
        max_records: MaxRecords = None,
    ) -> DescribeInstanceRefreshesAnswer:
        """Gets information about the instance refreshes for the specified Auto
        Scaling group.

        This operation is part of the `instance refresh
        feature <https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html>`__
        in Amazon EC2 Auto Scaling, which helps you update instances in your
        Auto Scaling group after you make configuration changes.

        To help you determine the status of an instance refresh, this operation
        returns information about the instance refreshes you previously
        initiated, including their status, end time, the percentage of the
        instance refresh that is complete, and the number of instances remaining
        to update before the instance refresh is complete.

        The following are the possible statuses:

        -  ``Pending`` - The request was created, but the operation has not
           started.

        -  ``InProgress`` - The operation is in progress.

        -  ``Successful`` - The operation completed successfully.

        -  ``Failed`` - The operation failed to complete. You can troubleshoot
           using the status reason and the scaling activities.

        -  ``Cancelling`` - An ongoing operation is being cancelled.
           Cancellation does not roll back any replacements that have already
           been completed, but it prevents new replacements from being started.

        -  ``Cancelled`` - The operation is cancelled.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param instance_refresh_ids: One or more instance refresh IDs.
        :param next_token: The token for the next set of items to return.
        :param max_records: The maximum number of items to return with this call.
        :returns: DescribeInstanceRefreshesAnswer
        :raises InvalidNextToken:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeLaunchConfigurations")
    def describe_launch_configurations(
        self,
        context: RequestContext,
        launch_configuration_names: LaunchConfigurationNames = None,
        next_token: XmlString = None,
        max_records: MaxRecords = None,
    ) -> LaunchConfigurationsType:
        """Gets information about the launch configurations in the account and
        Region.

        :param launch_configuration_names: The launch configuration names.
        :param next_token: The token for the next set of items to return.
        :param max_records: The maximum number of items to return with this call.
        :returns: LaunchConfigurationsType
        :raises InvalidNextToken:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeLifecycleHookTypes")
    def describe_lifecycle_hook_types(
        self,
        context: RequestContext,
    ) -> DescribeLifecycleHookTypesAnswer:
        """Describes the available types of lifecycle hooks.

        The following hook types are supported:

        -  ``autoscaling:EC2_INSTANCE_LAUNCHING``

        -  ``autoscaling:EC2_INSTANCE_TERMINATING``

        :returns: DescribeLifecycleHookTypesAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeLifecycleHooks")
    def describe_lifecycle_hooks(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        lifecycle_hook_names: LifecycleHookNames = None,
    ) -> DescribeLifecycleHooksAnswer:
        """Gets information about the lifecycle hooks for the specified Auto
        Scaling group.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param lifecycle_hook_names: The names of one or more lifecycle hooks.
        :returns: DescribeLifecycleHooksAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeLoadBalancerTargetGroups")
    def describe_load_balancer_target_groups(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        next_token: XmlString = None,
        max_records: MaxRecords = None,
    ) -> DescribeLoadBalancerTargetGroupsResponse:
        """Gets information about the load balancer target groups for the specified
        Auto Scaling group.

        To determine the availability of registered instances, use the ``State``
        element in the response. When you attach a target group to an Auto
        Scaling group, the initial ``State`` value is ``Adding``. The state
        transitions to ``Added`` after all Auto Scaling instances are registered
        with the target group. If Elastic Load Balancing health checks are
        enabled for the Auto Scaling group, the state transitions to
        ``InService`` after at least one Auto Scaling instance passes the health
        check. When the target group is in the ``InService`` state, Amazon EC2
        Auto Scaling can terminate and replace any instances that are reported
        as unhealthy. If no registered instances pass the health checks, the
        target group doesn't enter the ``InService`` state.

        Target groups also have an ``InService`` state if you attach them in the
        CreateAutoScalingGroup API call. If your target group state is
        ``InService``, but it is not working properly, check the scaling
        activities by calling DescribeScalingActivities and take any corrective
        actions necessary.

        For help with failed health checks, see `Troubleshooting Amazon EC2 Auto
        Scaling: Health
        checks <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ts-as-healthchecks.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*. For more information, see
        `Elastic Load Balancing and Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/autoscaling-load-balancer.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param next_token: The token for the next set of items to return.
        :param max_records: The maximum number of items to return with this call.
        :returns: DescribeLoadBalancerTargetGroupsResponse
        :raises ResourceContentionFault:
        :raises InvalidNextToken:
        """
        raise NotImplementedError

    @handler("DescribeLoadBalancers")
    def describe_load_balancers(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        next_token: XmlString = None,
        max_records: MaxRecords = None,
    ) -> DescribeLoadBalancersResponse:
        """Gets information about the load balancers for the specified Auto Scaling
        group.

        This operation describes only Classic Load Balancers. If you have
        Application Load Balancers, Network Load Balancers, or Gateway Load
        Balancers, use the DescribeLoadBalancerTargetGroups API instead.

        To determine the availability of registered instances, use the ``State``
        element in the response. When you attach a load balancer to an Auto
        Scaling group, the initial ``State`` value is ``Adding``. The state
        transitions to ``Added`` after all Auto Scaling instances are registered
        with the load balancer. If Elastic Load Balancing health checks are
        enabled for the Auto Scaling group, the state transitions to
        ``InService`` after at least one Auto Scaling instance passes the health
        check. When the load balancer is in the ``InService`` state, Amazon EC2
        Auto Scaling can terminate and replace any instances that are reported
        as unhealthy. If no registered instances pass the health checks, the
        load balancer doesn't enter the ``InService`` state.

        Load balancers also have an ``InService`` state if you attach them in
        the CreateAutoScalingGroup API call. If your load balancer state is
        ``InService``, but it is not working properly, check the scaling
        activities by calling DescribeScalingActivities and take any corrective
        actions necessary.

        For help with failed health checks, see `Troubleshooting Amazon EC2 Auto
        Scaling: Health
        checks <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ts-as-healthchecks.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*. For more information, see
        `Elastic Load Balancing and Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/autoscaling-load-balancer.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param next_token: The token for the next set of items to return.
        :param max_records: The maximum number of items to return with this call.
        :returns: DescribeLoadBalancersResponse
        :raises ResourceContentionFault:
        :raises InvalidNextToken:
        """
        raise NotImplementedError

    @handler("DescribeMetricCollectionTypes")
    def describe_metric_collection_types(
        self,
        context: RequestContext,
    ) -> DescribeMetricCollectionTypesAnswer:
        """Describes the available CloudWatch metrics for Amazon EC2 Auto Scaling.

        The ``GroupStandbyInstances`` metric is not returned by default. You
        must explicitly request this metric when calling the
        EnableMetricsCollection API.

        :returns: DescribeMetricCollectionTypesAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeNotificationConfigurations")
    def describe_notification_configurations(
        self,
        context: RequestContext,
        auto_scaling_group_names: AutoScalingGroupNames = None,
        next_token: XmlString = None,
        max_records: MaxRecords = None,
    ) -> DescribeNotificationConfigurationsAnswer:
        """Gets information about the Amazon SNS notifications that are configured
        for one or more Auto Scaling groups.

        :param auto_scaling_group_names: The name of the Auto Scaling group.
        :param next_token: The token for the next set of items to return.
        :param max_records: The maximum number of items to return with this call.
        :returns: DescribeNotificationConfigurationsAnswer
        :raises InvalidNextToken:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribePolicies")
    def describe_policies(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255 = None,
        policy_names: PolicyNames = None,
        policy_types: PolicyTypes = None,
        next_token: XmlString = None,
        max_records: MaxRecords = None,
    ) -> PoliciesType:
        """Gets information about the scaling policies in the account and Region.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param policy_names: The names of one or more policies.
        :param policy_types: One or more policy types.
        :param next_token: The token for the next set of items to return.
        :param max_records: The maximum number of items to be returned with each call.
        :returns: PoliciesType
        :raises InvalidNextToken:
        :raises ResourceContentionFault:
        :raises ServiceLinkedRoleFailure:
        """
        raise NotImplementedError

    @handler("DescribeScalingActivities")
    def describe_scaling_activities(
        self,
        context: RequestContext,
        activity_ids: ActivityIds = None,
        auto_scaling_group_name: XmlStringMaxLen255 = None,
        include_deleted_groups: IncludeDeletedGroups = None,
        max_records: MaxRecords = None,
        next_token: XmlString = None,
    ) -> ActivitiesType:
        """Gets information about the scaling activities in the account and Region.

        When scaling events occur, you see a record of the scaling activity in
        the scaling activities. For more information, see `Verifying a scaling
        activity for an Auto Scaling
        group <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-verify-scaling-activity.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        If the scaling event succeeds, the value of the ``StatusCode`` element
        in the response is ``Successful``. If an attempt to launch instances
        failed, the ``StatusCode`` value is ``Failed`` or ``Cancelled`` and the
        ``StatusMessage`` element in the response indicates the cause of the
        failure. For help interpreting the ``StatusMessage``, see
        `Troubleshooting Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/CHAP_Troubleshooting.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param activity_ids: The activity IDs of the desired scaling activities.
        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param include_deleted_groups: Indicates whether to include scaling activity from deleted Auto Scaling
        groups.
        :param max_records: The maximum number of items to return with this call.
        :param next_token: The token for the next set of items to return.
        :returns: ActivitiesType
        :raises InvalidNextToken:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeScalingProcessTypes")
    def describe_scaling_process_types(
        self,
        context: RequestContext,
    ) -> ProcessesType:
        """Describes the scaling process types for use with the ResumeProcesses and
        SuspendProcesses APIs.

        :returns: ProcessesType
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeScheduledActions")
    def describe_scheduled_actions(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255 = None,
        scheduled_action_names: ScheduledActionNames = None,
        start_time: TimestampType = None,
        end_time: TimestampType = None,
        next_token: XmlString = None,
        max_records: MaxRecords = None,
    ) -> ScheduledActionsType:
        """Gets information about the scheduled actions that haven't run or that
        have not reached their end time.

        To describe the scaling activities for scheduled actions that have
        already run, call the DescribeScalingActivities API.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param scheduled_action_names: The names of one or more scheduled actions.
        :param start_time: The earliest scheduled start time to return.
        :param end_time: The latest scheduled start time to return.
        :param next_token: The token for the next set of items to return.
        :param max_records: The maximum number of items to return with this call.
        :returns: ScheduledActionsType
        :raises InvalidNextToken:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeTags")
    def describe_tags(
        self,
        context: RequestContext,
        filters: Filters = None,
        next_token: XmlString = None,
        max_records: MaxRecords = None,
    ) -> TagsType:
        """Describes the specified tags.

        You can use filters to limit the results. For example, you can query for
        the tags for a specific Auto Scaling group. You can specify multiple
        values for a filter. A tag must match at least one of the specified
        values for it to be included in the results.

        You can also specify multiple filters. The result includes information
        for a particular tag only if it matches all the filters. If there's no
        match, no special message is returned.

        For more information, see `Tagging Auto Scaling groups and
        instances <https://docs.aws.amazon.com/autoscaling/ec2/userguide/autoscaling-tagging.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param filters: One or more filters to scope the tags to return.
        :param next_token: The token for the next set of items to return.
        :param max_records: The maximum number of items to return with this call.
        :returns: TagsType
        :raises InvalidNextToken:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeTerminationPolicyTypes")
    def describe_termination_policy_types(
        self,
        context: RequestContext,
    ) -> DescribeTerminationPolicyTypesAnswer:
        """Describes the termination policies supported by Amazon EC2 Auto Scaling.

        For more information, see `Controlling which Auto Scaling instances
        terminate during scale
        in <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-instance-termination.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :returns: DescribeTerminationPolicyTypesAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DescribeWarmPool")
    def describe_warm_pool(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        max_records: MaxRecords = None,
        next_token: XmlString = None,
    ) -> DescribeWarmPoolAnswer:
        """Gets information about a warm pool and its instances.

        For more information, see `Warm pools for Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-warm-pools.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param max_records: The maximum number of instances to return with this call.
        :param next_token: The token for the next set of instances to return.
        :returns: DescribeWarmPoolAnswer
        :raises InvalidNextToken:
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DetachInstances")
    def detach_instances(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        should_decrement_desired_capacity: ShouldDecrementDesiredCapacity,
        instance_ids: InstanceIds = None,
    ) -> DetachInstancesAnswer:
        """Removes one or more instances from the specified Auto Scaling group.

        After the instances are detached, you can manage them independent of the
        Auto Scaling group.

        If you do not specify the option to decrement the desired capacity,
        Amazon EC2 Auto Scaling launches instances to replace the ones that are
        detached.

        If there is a Classic Load Balancer attached to the Auto Scaling group,
        the instances are deregistered from the load balancer. If there are
        target groups attached to the Auto Scaling group, the instances are
        deregistered from the target groups.

        For more information, see `Detach EC2 instances from your Auto Scaling
        group <https://docs.aws.amazon.com/autoscaling/ec2/userguide/detach-instance-asg.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param should_decrement_desired_capacity: Indicates whether the Auto Scaling group decrements the desired capacity
        value by the number of instances detached.
        :param instance_ids: The IDs of the instances.
        :returns: DetachInstancesAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DetachLoadBalancerTargetGroups")
    def detach_load_balancer_target_groups(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        target_group_arns: TargetGroupARNs,
    ) -> DetachLoadBalancerTargetGroupsResultType:
        """Detaches one or more target groups from the specified Auto Scaling
        group.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param target_group_arns: The Amazon Resource Names (ARN) of the target groups.
        :returns: DetachLoadBalancerTargetGroupsResultType
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DetachLoadBalancers")
    def detach_load_balancers(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        load_balancer_names: LoadBalancerNames,
    ) -> DetachLoadBalancersResultType:
        """Detaches one or more Classic Load Balancers from the specified Auto
        Scaling group.

        This operation detaches only Classic Load Balancers. If you have
        Application Load Balancers, Network Load Balancers, or Gateway Load
        Balancers, use the DetachLoadBalancerTargetGroups API instead.

        When you detach a load balancer, it enters the ``Removing`` state while
        deregistering the instances in the group. When all instances are
        deregistered, then you can no longer describe the load balancer using
        the DescribeLoadBalancers API call. The instances remain running.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param load_balancer_names: The names of the load balancers.
        :returns: DetachLoadBalancersResultType
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("DisableMetricsCollection")
    def disable_metrics_collection(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        metrics: Metrics = None,
    ) -> None:
        """Disables group metrics for the specified Auto Scaling group.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param metrics: Specifies one or more of the following metrics:

        -  ``GroupMinSize``

        -  ``GroupMaxSize``

        -  ``GroupDesiredCapacity``

        -  ``GroupInServiceInstances``

        -  ``GroupPendingInstances``

        -  ``GroupStandbyInstances``

        -  ``GroupTerminatingInstances``

        -  ``GroupTotalInstances``

        -  ``GroupInServiceCapacity``

        -  ``GroupPendingCapacity``

        -  ``GroupStandbyCapacity``

        -  ``GroupTerminatingCapacity``

        -  ``GroupTotalCapacity``

        -  ``WarmPoolDesiredCapacity``

        -  ``WarmPoolWarmedCapacity``

        -  ``WarmPoolPendingCapacity``

        -  ``WarmPoolTerminatingCapacity``

        -  ``WarmPoolTotalCapacity``

        -  ``GroupAndWarmPoolDesiredCapacity``

        -  ``GroupAndWarmPoolTotalCapacity``

        If you omit this parameter, all metrics are disabled.
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("EnableMetricsCollection")
    def enable_metrics_collection(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        granularity: XmlStringMaxLen255,
        metrics: Metrics = None,
    ) -> None:
        """Enables group metrics for the specified Auto Scaling group. For more
        information, see `Monitoring CloudWatch metrics for your Auto Scaling
        groups and
        instances <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-instance-monitoring.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param granularity: The granularity to associate with the metrics to collect.
        :param metrics: Specifies which group-level metrics to start collecting.
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("EnterStandby")
    def enter_standby(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        should_decrement_desired_capacity: ShouldDecrementDesiredCapacity,
        instance_ids: InstanceIds = None,
    ) -> EnterStandbyAnswer:
        """Moves the specified instances into the standby state.

        If you choose to decrement the desired capacity of the Auto Scaling
        group, the instances can enter standby as long as the desired capacity
        of the Auto Scaling group after the instances are placed into standby is
        equal to or greater than the minimum capacity of the group.

        If you choose not to decrement the desired capacity of the Auto Scaling
        group, the Auto Scaling group launches new instances to replace the
        instances on standby.

        For more information, see `Temporarily removing instances from your Auto
        Scaling
        group <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-enter-exit-standby.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param should_decrement_desired_capacity: Indicates whether to decrement the desired capacity of the Auto Scaling
        group by the number of instances moved to ``Standby`` mode.
        :param instance_ids: The IDs of the instances.
        :returns: EnterStandbyAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("ExecutePolicy")
    def execute_policy(
        self,
        context: RequestContext,
        policy_name: ResourceName,
        auto_scaling_group_name: XmlStringMaxLen255 = None,
        honor_cooldown: HonorCooldown = None,
        metric_value: MetricScale = None,
        breach_threshold: MetricScale = None,
    ) -> None:
        """Executes the specified policy. This can be useful for testing the design
        of your scaling policy.

        :param policy_name: The name or ARN of the policy.
        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param honor_cooldown: Indicates whether Amazon EC2 Auto Scaling waits for the cooldown period
        to complete before executing the policy.
        :param metric_value: The metric value to compare to ``BreachThreshold``.
        :param breach_threshold: The breach threshold for the alarm.
        :raises ScalingActivityInProgressFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("ExitStandby")
    def exit_standby(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        instance_ids: InstanceIds = None,
    ) -> ExitStandbyAnswer:
        """Moves the specified instances out of the standby state.

        After you put the instances back in service, the desired capacity is
        incremented.

        For more information, see `Temporarily removing instances from your Auto
        Scaling
        group <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-enter-exit-standby.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param instance_ids: The IDs of the instances.
        :returns: ExitStandbyAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("GetPredictiveScalingForecast")
    def get_predictive_scaling_forecast(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        policy_name: XmlStringMaxLen255,
        start_time: TimestampType,
        end_time: TimestampType,
    ) -> GetPredictiveScalingForecastAnswer:
        """Retrieves the forecast data for a predictive scaling policy.

        Load forecasts are predictions of the hourly load values using
        historical load data from CloudWatch and an analysis of historical
        trends. Capacity forecasts are represented as predicted values for the
        minimum capacity that is needed on an hourly basis, based on the hourly
        load forecast.

        A minimum of 24 hours of data is required to create the initial
        forecasts. However, having a full 14 days of historical data results in
        more accurate forecasts.

        For more information, see `Predictive scaling for Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-predictive-scaling.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param policy_name: The name of the policy.
        :param start_time: The inclusive start time of the time range for the forecast data to get.
        :param end_time: The exclusive end time of the time range for the forecast data to get.
        :returns: GetPredictiveScalingForecastAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("PutLifecycleHook")
    def put_lifecycle_hook(
        self,
        context: RequestContext,
        lifecycle_hook_name: AsciiStringMaxLen255,
        auto_scaling_group_name: XmlStringMaxLen255,
        lifecycle_transition: LifecycleTransition = None,
        role_arn: XmlStringMaxLen255 = None,
        notification_target_arn: NotificationTargetResourceName = None,
        notification_metadata: XmlStringMaxLen1023 = None,
        heartbeat_timeout: HeartbeatTimeout = None,
        default_result: LifecycleActionResult = None,
    ) -> PutLifecycleHookAnswer:
        """Creates or updates a lifecycle hook for the specified Auto Scaling
        group.

        Lifecycle hooks let you create solutions that are aware of events in the
        Auto Scaling instance lifecycle, and then perform a custom action on
        instances when the corresponding lifecycle event occurs.

        This step is a part of the procedure for adding a lifecycle hook to an
        Auto Scaling group:

        #. (Optional) Create a launch template or launch configuration with a
           user data script that runs while an instance is in a wait state due
           to a lifecycle hook.

        #. (Optional) Create a Lambda function and a rule that allows Amazon
           EventBridge to invoke your Lambda function when an instance is put
           into a wait state due to a lifecycle hook.

        #. (Optional) Create a notification target and an IAM role. The target
           can be either an Amazon SQS queue or an Amazon SNS topic. The role
           allows Amazon EC2 Auto Scaling to publish lifecycle notifications to
           the target.

        #. **Create the lifecycle hook. Specify whether the hook is used when
           the instances launch or terminate.**

        #. If you need more time, record the lifecycle action heartbeat to keep
           the instance in a wait state using the RecordLifecycleActionHeartbeat
           API call.

        #. If you finish before the timeout period ends, send a callback by
           using the CompleteLifecycleAction API call.

        For more information, see `Amazon EC2 Auto Scaling lifecycle
        hooks <https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        If you exceed your maximum limit of lifecycle hooks, which by default is
        50 per Auto Scaling group, the call fails.

        You can view the lifecycle hooks for an Auto Scaling group using the
        DescribeLifecycleHooks API call. If you are no longer using a lifecycle
        hook, you can delete it by calling the DeleteLifecycleHook API.

        :param lifecycle_hook_name: The name of the lifecycle hook.
        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param lifecycle_transition: The instance state to which you want to attach the lifecycle hook.
        :param role_arn: The ARN of the IAM role that allows the Auto Scaling group to publish to
        the specified notification target.
        :param notification_target_arn: The ARN of the notification target that Amazon EC2 Auto Scaling uses to
        notify you when an instance is in the transition state for the lifecycle
        hook.
        :param notification_metadata: Additional information that you want to include any time Amazon EC2 Auto
        Scaling sends a message to the notification target.
        :param heartbeat_timeout: The maximum time, in seconds, that can elapse before the lifecycle hook
        times out.
        :param default_result: Defines the action the Auto Scaling group should take when the lifecycle
        hook timeout elapses or if an unexpected failure occurs.
        :returns: PutLifecycleHookAnswer
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("PutNotificationConfiguration")
    def put_notification_configuration(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        topic_arn: XmlStringMaxLen255,
        notification_types: AutoScalingNotificationTypes,
    ) -> None:
        """Configures an Auto Scaling group to send notifications when specified
        events take place. Subscribers to the specified topic can have messages
        delivered to an endpoint such as a web server or an email address.

        This configuration overwrites any existing configuration.

        For more information, see `Getting Amazon SNS notifications when your
        Auto Scaling group
        scales <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ASGettingNotifications.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        If you exceed your maximum limit of SNS topics, which is 10 per Auto
        Scaling group, the call fails.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param topic_arn: The Amazon Resource Name (ARN) of the Amazon SNS topic.
        :param notification_types: The type of event that causes the notification to be sent.
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        :raises ServiceLinkedRoleFailure:
        """
        raise NotImplementedError

    @handler("PutScalingPolicy")
    def put_scaling_policy(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        policy_name: XmlStringMaxLen255,
        policy_type: XmlStringMaxLen64 = None,
        adjustment_type: XmlStringMaxLen255 = None,
        min_adjustment_step: MinAdjustmentStep = None,
        min_adjustment_magnitude: MinAdjustmentMagnitude = None,
        scaling_adjustment: PolicyIncrement = None,
        cooldown: Cooldown = None,
        metric_aggregation_type: XmlStringMaxLen32 = None,
        step_adjustments: StepAdjustments = None,
        estimated_instance_warmup: EstimatedInstanceWarmup = None,
        target_tracking_configuration: TargetTrackingConfiguration = None,
        enabled: ScalingPolicyEnabled = None,
        predictive_scaling_configuration: PredictiveScalingConfiguration = None,
    ) -> PolicyARNType:
        """Creates or updates a scaling policy for an Auto Scaling group. Scaling
        policies are used to scale an Auto Scaling group based on configurable
        metrics. If no policies are defined, the dynamic scaling and predictive
        scaling features are not used.

        For more information about using dynamic scaling, see `Target tracking
        scaling
        policies <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html>`__
        and `Step and simple scaling
        policies <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-simple-step.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        For more information about using predictive scaling, see `Predictive
        scaling for Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-predictive-scaling.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        You can view the scaling policies for an Auto Scaling group using the
        DescribePolicies API call. If you are no longer using a scaling policy,
        you can delete it by calling the DeletePolicy API.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param policy_name: The name of the policy.
        :param policy_type: One of the following policy types:

        -  ``TargetTrackingScaling``

        -  ``StepScaling``

        -  ``SimpleScaling`` (default)

        -  ``PredictiveScaling``.
        :param adjustment_type: Specifies how the scaling adjustment is interpreted (for example, an
        absolute number or a percentage).
        :param min_adjustment_step: Available for backward compatibility.
        :param min_adjustment_magnitude: The minimum value to scale by when the adjustment type is
        ``PercentChangeInCapacity``.
        :param scaling_adjustment: The amount by which to scale, based on the specified adjustment type.
        :param cooldown: A cooldown period, in seconds, that applies to a specific simple scaling
        policy.
        :param metric_aggregation_type: The aggregation type for the CloudWatch metrics.
        :param step_adjustments: A set of adjustments that enable you to scale based on the size of the
        alarm breach.
        :param estimated_instance_warmup: *Not needed if the default instance warmup is defined for the group.
        :param target_tracking_configuration: A target tracking scaling policy.
        :param enabled: Indicates whether the scaling policy is enabled or disabled.
        :param predictive_scaling_configuration: A predictive scaling policy.
        :returns: PolicyARNType
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        :raises ServiceLinkedRoleFailure:
        """
        raise NotImplementedError

    @handler("PutScheduledUpdateGroupAction")
    def put_scheduled_update_group_action(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        scheduled_action_name: XmlStringMaxLen255,
        time: TimestampType = None,
        start_time: TimestampType = None,
        end_time: TimestampType = None,
        recurrence: XmlStringMaxLen255 = None,
        min_size: AutoScalingGroupMinSize = None,
        max_size: AutoScalingGroupMaxSize = None,
        desired_capacity: AutoScalingGroupDesiredCapacity = None,
        time_zone: XmlStringMaxLen255 = None,
    ) -> None:
        """Creates or updates a scheduled scaling action for an Auto Scaling group.

        For more information, see `Scheduled
        scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/schedule_time.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        You can view the scheduled actions for an Auto Scaling group using the
        DescribeScheduledActions API call. If you are no longer using a
        scheduled action, you can delete it by calling the DeleteScheduledAction
        API.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param scheduled_action_name: The name of this scaling action.
        :param time: This parameter is no longer used.
        :param start_time: The date and time for this action to start, in YYYY-MM-DDThh:mm:ssZ
        format in UTC/GMT only and in quotes (for example,
        ``"2019-06-01T00:00:00Z"``).
        :param end_time: The date and time for the recurring schedule to end, in UTC.
        :param recurrence: The recurring schedule for this action.
        :param min_size: The minimum size of the Auto Scaling group.
        :param max_size: The maximum size of the Auto Scaling group.
        :param desired_capacity: The desired capacity is the initial capacity of the Auto Scaling group
        after the scheduled action runs and the capacity it attempts to
        maintain.
        :param time_zone: Specifies the time zone for a cron expression.
        :raises AlreadyExistsFault:
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("PutWarmPool")
    def put_warm_pool(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        max_group_prepared_capacity: MaxGroupPreparedCapacity = None,
        min_size: WarmPoolMinSize = None,
        pool_state: WarmPoolState = None,
        instance_reuse_policy: InstanceReusePolicy = None,
    ) -> PutWarmPoolAnswer:
        """Creates or updates a warm pool for the specified Auto Scaling group. A
        warm pool is a pool of pre-initialized EC2 instances that sits alongside
        the Auto Scaling group. Whenever your application needs to scale out,
        the Auto Scaling group can draw on the warm pool to meet its new desired
        capacity. For more information and example configurations, see `Warm
        pools for Amazon EC2 Auto
        Scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-warm-pools.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        This operation must be called from the Region in which the Auto Scaling
        group was created. This operation cannot be called on an Auto Scaling
        group that has a mixed instances policy or a launch template or launch
        configuration that requests Spot Instances.

        You can view the instances in the warm pool using the DescribeWarmPool
        API call. If you are no longer using a warm pool, you can delete it by
        calling the DeleteWarmPool API.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param max_group_prepared_capacity: Specifies the maximum number of instances that are allowed to be in the
        warm pool or in any state except ``Terminated`` for the Auto Scaling
        group.
        :param min_size: Specifies the minimum number of instances to maintain in the warm pool.
        :param pool_state: Sets the instance state to transition to after the lifecycle actions are
        complete.
        :param instance_reuse_policy: Indicates whether instances in the Auto Scaling group can be returned to
        the warm pool on scale in.
        :returns: PutWarmPoolAnswer
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("RecordLifecycleActionHeartbeat")
    def record_lifecycle_action_heartbeat(
        self,
        context: RequestContext,
        lifecycle_hook_name: AsciiStringMaxLen255,
        auto_scaling_group_name: ResourceName,
        lifecycle_action_token: LifecycleActionToken = None,
        instance_id: XmlStringMaxLen19 = None,
    ) -> RecordLifecycleActionHeartbeatAnswer:
        """Records a heartbeat for the lifecycle action associated with the
        specified token or instance. This extends the timeout by the length of
        time defined using the PutLifecycleHook API call.

        This step is a part of the procedure for adding a lifecycle hook to an
        Auto Scaling group:

        #. (Optional) Create a launch template or launch configuration with a
           user data script that runs while an instance is in a wait state due
           to a lifecycle hook.

        #. (Optional) Create a Lambda function and a rule that allows Amazon
           EventBridge to invoke your Lambda function when an instance is put
           into a wait state due to a lifecycle hook.

        #. (Optional) Create a notification target and an IAM role. The target
           can be either an Amazon SQS queue or an Amazon SNS topic. The role
           allows Amazon EC2 Auto Scaling to publish lifecycle notifications to
           the target.

        #. Create the lifecycle hook. Specify whether the hook is used when the
           instances launch or terminate.

        #. **If you need more time, record the lifecycle action heartbeat to
           keep the instance in a wait state.**

        #. If you finish before the timeout period ends, send a callback by
           using the CompleteLifecycleAction API call.

        For more information, see `Amazon EC2 Auto Scaling lifecycle
        hooks <https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param lifecycle_hook_name: The name of the lifecycle hook.
        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param lifecycle_action_token: A token that uniquely identifies a specific lifecycle action associated
        with an instance.
        :param instance_id: The ID of the instance.
        :returns: RecordLifecycleActionHeartbeatAnswer
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("ResumeProcesses")
    def resume_processes(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        scaling_processes: ProcessNames = None,
    ) -> None:
        """Resumes the specified suspended auto scaling processes, or all suspended
        process, for the specified Auto Scaling group.

        For more information, see `Suspending and resuming scaling
        processes <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-suspend-resume-processes.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param scaling_processes: One or more of the following processes:

        -  ``Launch``

        -  ``Terminate``

        -  ``AddToLoadBalancer``

        -  ``AlarmNotification``

        -  ``AZRebalance``

        -  ``HealthCheck``

        -  ``InstanceRefresh``

        -  ``ReplaceUnhealthy``

        -  ``ScheduledActions``

        If you omit this parameter, all processes are specified.
        :raises ResourceInUseFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("SetDesiredCapacity")
    def set_desired_capacity(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        desired_capacity: AutoScalingGroupDesiredCapacity,
        honor_cooldown: HonorCooldown = None,
    ) -> None:
        """Sets the size of the specified Auto Scaling group.

        If a scale-in activity occurs as a result of a new ``DesiredCapacity``
        value that is lower than the current size of the group, the Auto Scaling
        group uses its termination policy to determine which instances to
        terminate.

        For more information, see `Manual
        scaling <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-manual-scaling.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param desired_capacity: The desired capacity is the initial capacity of the Auto Scaling group
        after this operation completes and the capacity it attempts to maintain.
        :param honor_cooldown: Indicates whether Amazon EC2 Auto Scaling waits for the cooldown period
        to complete before initiating a scaling activity to set your Auto
        Scaling group to its new capacity.
        :raises ScalingActivityInProgressFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("SetInstanceHealth")
    def set_instance_health(
        self,
        context: RequestContext,
        instance_id: XmlStringMaxLen19,
        health_status: XmlStringMaxLen32,
        should_respect_grace_period: ShouldRespectGracePeriod = None,
    ) -> None:
        """Sets the health status of the specified instance.

        For more information, see `Health checks for Auto Scaling
        instances <https://docs.aws.amazon.com/autoscaling/ec2/userguide/healthcheck.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param instance_id: The ID of the instance.
        :param health_status: The health status of the instance.
        :param should_respect_grace_period: If the Auto Scaling group of the specified instance has a
        ``HealthCheckGracePeriod`` specified for the group, by default, this
        call respects the grace period.
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("SetInstanceProtection")
    def set_instance_protection(
        self,
        context: RequestContext,
        instance_ids: InstanceIds,
        auto_scaling_group_name: XmlStringMaxLen255,
        protected_from_scale_in: ProtectedFromScaleIn,
    ) -> SetInstanceProtectionAnswer:
        """Updates the instance protection settings of the specified instances.
        This operation cannot be called on instances in a warm pool.

        For more information about preventing instances that are part of an Auto
        Scaling group from terminating on scale in, see `Using instance scale-in
        protection <https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-instance-protection.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        If you exceed your maximum limit of instance IDs, which is 50 per Auto
        Scaling group, the call fails.

        :param instance_ids: One or more instance IDs.
        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param protected_from_scale_in: Indicates whether the instance is protected from termination by Amazon
        EC2 Auto Scaling when scaling in.
        :returns: SetInstanceProtectionAnswer
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("StartInstanceRefresh")
    def start_instance_refresh(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        strategy: RefreshStrategy = None,
        desired_configuration: DesiredConfiguration = None,
        preferences: RefreshPreferences = None,
    ) -> StartInstanceRefreshAnswer:
        """Starts a new instance refresh operation. An instance refresh performs a
        rolling replacement of all or some instances in an Auto Scaling group.
        Each instance is terminated first and then replaced, which temporarily
        reduces the capacity available within your Auto Scaling group.

        This operation is part of the `instance refresh
        feature <https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html>`__
        in Amazon EC2 Auto Scaling, which helps you update instances in your
        Auto Scaling group. This feature is helpful, for example, when you have
        a new AMI or a new user data script. You just need to create a new
        launch template that specifies the new AMI or user data script. Then
        start an instance refresh to immediately begin the process of updating
        instances in the group.

        If the call succeeds, it creates a new instance refresh request with a
        unique ID that you can use to track its progress. To query its status,
        call the DescribeInstanceRefreshes API. To describe the instance
        refreshes that have already run, call the DescribeInstanceRefreshes API.
        To cancel an instance refresh operation in progress, use the
        CancelInstanceRefresh API.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param strategy: The strategy to use for the instance refresh.
        :param desired_configuration: The desired configuration.
        :param preferences: Set of preferences associated with the instance refresh request.
        :returns: StartInstanceRefreshAnswer
        :raises LimitExceededFault:
        :raises ResourceContentionFault:
        :raises InstanceRefreshInProgressFault:
        """
        raise NotImplementedError

    @handler("SuspendProcesses")
    def suspend_processes(
        self,
        context: RequestContext,
        auto_scaling_group_name: XmlStringMaxLen255,
        scaling_processes: ProcessNames = None,
    ) -> None:
        """Suspends the specified auto scaling processes, or all processes, for the
        specified Auto Scaling group.

        If you suspend either the ``Launch`` or ``Terminate`` process types, it
        can prevent other process types from functioning properly. For more
        information, see `Suspending and resuming scaling
        processes <https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-suspend-resume-processes.html>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        To resume processes that have been suspended, call the ResumeProcesses
        API.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param scaling_processes: One or more of the following processes:

        -  ``Launch``

        -  ``Terminate``

        -  ``AddToLoadBalancer``

        -  ``AlarmNotification``

        -  ``AZRebalance``

        -  ``HealthCheck``

        -  ``InstanceRefresh``

        -  ``ReplaceUnhealthy``

        -  ``ScheduledActions``

        If you omit this parameter, all processes are specified.
        :raises ResourceInUseFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("TerminateInstanceInAutoScalingGroup")
    def terminate_instance_in_auto_scaling_group(
        self,
        context: RequestContext,
        instance_id: XmlStringMaxLen19,
        should_decrement_desired_capacity: ShouldDecrementDesiredCapacity,
    ) -> ActivityType:
        """Terminates the specified instance and optionally adjusts the desired
        group size. This operation cannot be called on instances in a warm pool.

        This call simply makes a termination request. The instance is not
        terminated immediately. When an instance is terminated, the instance
        status changes to ``terminated``. You can't connect to or start an
        instance after you've terminated it.

        If you do not specify the option to decrement the desired capacity,
        Amazon EC2 Auto Scaling launches instances to replace the ones that are
        terminated.

        By default, Amazon EC2 Auto Scaling balances instances across all
        Availability Zones. If you decrement the desired capacity, your Auto
        Scaling group can become unbalanced between Availability Zones. Amazon
        EC2 Auto Scaling tries to rebalance the group, and rebalancing might
        terminate instances in other zones. For more information, see
        `Rebalancing
        activities <https://docs.aws.amazon.com/autoscaling/ec2/userguide/auto-scaling-benefits.html#AutoScalingBehavior.InstanceUsage>`__
        in the *Amazon EC2 Auto Scaling User Guide*.

        :param instance_id: The ID of the instance.
        :param should_decrement_desired_capacity: Indicates whether terminating the instance also decrements the size of
        the Auto Scaling group.
        :returns: ActivityType
        :raises ScalingActivityInProgressFault:
        :raises ResourceContentionFault:
        """
        raise NotImplementedError

    @handler("UpdateAutoScalingGroup", expand=False)
    def update_auto_scaling_group(
        self, context: RequestContext, request: UpdateAutoScalingGroupType
    ) -> None:
        """**We strongly recommend that all Auto Scaling groups use launch
        templates to ensure full functionality for Amazon EC2 Auto Scaling and
        Amazon EC2.**

        Updates the configuration for the specified Auto Scaling group.

        To update an Auto Scaling group, specify the name of the group and the
        parameter that you want to change. Any parameters that you don't specify
        are not changed by this update request. The new settings take effect on
        any scaling activities after this call returns.

        If you associate a new launch configuration or template with an Auto
        Scaling group, all new instances will get the updated configuration.
        Existing instances continue to run with the configuration that they were
        originally launched with. When you update a group to specify a mixed
        instances policy instead of a launch configuration or template, existing
        instances may be replaced to match the new purchasing options that you
        specified in the policy. For example, if the group currently has 100%
        On-Demand capacity and the policy specifies 50% Spot capacity, this
        means that half of your instances will be gradually terminated and
        relaunched as Spot Instances. When replacing instances, Amazon EC2 Auto
        Scaling launches new instances before terminating the old ones, so that
        updating your group does not compromise the performance or availability
        of your application.

        Note the following about changing ``DesiredCapacity``, ``MaxSize``, or
        ``MinSize``:

        -  If a scale-in activity occurs as a result of a new
           ``DesiredCapacity`` value that is lower than the current size of the
           group, the Auto Scaling group uses its termination policy to
           determine which instances to terminate.

        -  If you specify a new value for ``MinSize`` without specifying a value
           for ``DesiredCapacity``, and the new ``MinSize`` is larger than the
           current size of the group, this sets the group's ``DesiredCapacity``
           to the new ``MinSize`` value.

        -  If you specify a new value for ``MaxSize`` without specifying a value
           for ``DesiredCapacity``, and the new ``MaxSize`` is smaller than the
           current size of the group, this sets the group's ``DesiredCapacity``
           to the new ``MaxSize`` value.

        To see which parameters have been set, call the
        DescribeAutoScalingGroups API. To view the scaling policies for an Auto
        Scaling group, call the DescribePolicies API. If the group has scaling
        policies, you can update them by calling the PutScalingPolicy API.

        :param auto_scaling_group_name: The name of the Auto Scaling group.
        :param launch_configuration_name: The name of the launch configuration.
        :param launch_template: The launch template and version to use to specify the updates.
        :param mixed_instances_policy: An embedded object that specifies a mixed instances policy.
        :param min_size: The minimum size of the Auto Scaling group.
        :param max_size: The maximum size of the Auto Scaling group.
        :param desired_capacity: The desired capacity is the initial capacity of the Auto Scaling group
        after this operation completes and the capacity it attempts to maintain.
        :param default_cooldown: *Only needed if you use simple scaling policies.
        :param availability_zones: One or more Availability Zones for the group.
        :param health_check_type: The service to use for the health checks.
        :param health_check_grace_period: The amount of time, in seconds, that Amazon EC2 Auto Scaling waits
        before checking the health status of an EC2 instance that has come into
        service and marking it unhealthy due to a failed Elastic Load Balancing
        or custom health check.
        :param placement_group: The name of an existing placement group into which to launch your
        instances.
        :param vpc_zone_identifier: A comma-separated list of subnet IDs for a virtual private cloud (VPC).
        :param termination_policies: A policy or a list of policies that are used to select the instances to
        terminate.
        :param new_instances_protected_from_scale_in: Indicates whether newly launched instances are protected from
        termination by Amazon EC2 Auto Scaling when scaling in.
        :param service_linked_role_arn: The Amazon Resource Name (ARN) of the service-linked role that the Auto
        Scaling group uses to call other Amazon Web Services on your behalf.
        :param max_instance_lifetime: The maximum amount of time, in seconds, that an instance can be in
        service.
        :param capacity_rebalance: Enables or disables Capacity Rebalancing.
        :param context: Reserved.
        :param desired_capacity_type: The unit of measurement for the value specified for desired capacity.
        :param default_instance_warmup: The amount of time, in seconds, until a newly launched instance can
        contribute to the Amazon CloudWatch metrics.
        :raises ScalingActivityInProgressFault:
        :raises ResourceContentionFault:
        :raises ServiceLinkedRoleFailure:
        """
        raise NotImplementedError
