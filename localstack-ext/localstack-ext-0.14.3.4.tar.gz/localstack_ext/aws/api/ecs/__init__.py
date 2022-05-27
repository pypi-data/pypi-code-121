import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Boolean = bool
BoxedBoolean = bool
BoxedInteger = int
CapacityProviderStrategyItemBase = int
CapacityProviderStrategyItemWeight = int
Double = float
Integer = int
ManagedScalingInstanceWarmupPeriod = int
ManagedScalingStepSize = int
ManagedScalingTargetCapacity = int
SensitiveString = str
String = str
TagKey = str
TagValue = str


class AgentUpdateStatus(str):
    PENDING = "PENDING"
    STAGING = "STAGING"
    STAGED = "STAGED"
    UPDATING = "UPDATING"
    UPDATED = "UPDATED"
    FAILED = "FAILED"


class AssignPublicIp(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class CPUArchitecture(str):
    X86_64 = "X86_64"
    ARM64 = "ARM64"


class CapacityProviderField(str):
    TAGS = "TAGS"


class CapacityProviderStatus(str):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class CapacityProviderUpdateStatus(str):
    DELETE_IN_PROGRESS = "DELETE_IN_PROGRESS"
    DELETE_COMPLETE = "DELETE_COMPLETE"
    DELETE_FAILED = "DELETE_FAILED"
    UPDATE_IN_PROGRESS = "UPDATE_IN_PROGRESS"
    UPDATE_COMPLETE = "UPDATE_COMPLETE"
    UPDATE_FAILED = "UPDATE_FAILED"


class ClusterField(str):
    ATTACHMENTS = "ATTACHMENTS"
    CONFIGURATIONS = "CONFIGURATIONS"
    SETTINGS = "SETTINGS"
    STATISTICS = "STATISTICS"
    TAGS = "TAGS"


class ClusterSettingName(str):
    containerInsights = "containerInsights"


class Compatibility(str):
    EC2 = "EC2"
    FARGATE = "FARGATE"
    EXTERNAL = "EXTERNAL"


class Connectivity(str):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"


class ContainerCondition(str):
    START = "START"
    COMPLETE = "COMPLETE"
    SUCCESS = "SUCCESS"
    HEALTHY = "HEALTHY"


class ContainerInstanceField(str):
    TAGS = "TAGS"
    CONTAINER_INSTANCE_HEALTH = "CONTAINER_INSTANCE_HEALTH"


class ContainerInstanceStatus(str):
    ACTIVE = "ACTIVE"
    DRAINING = "DRAINING"
    REGISTERING = "REGISTERING"
    DEREGISTERING = "DEREGISTERING"
    REGISTRATION_FAILED = "REGISTRATION_FAILED"


class DeploymentControllerType(str):
    ECS = "ECS"
    CODE_DEPLOY = "CODE_DEPLOY"
    EXTERNAL = "EXTERNAL"


class DeploymentRolloutState(str):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN_PROGRESS"


class DesiredStatus(str):
    RUNNING = "RUNNING"
    PENDING = "PENDING"
    STOPPED = "STOPPED"


class DeviceCgroupPermission(str):
    read = "read"
    write = "write"
    mknod = "mknod"


class EFSAuthorizationConfigIAM(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class EFSTransitEncryption(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class EnvironmentFileType(str):
    s3 = "s3"


class ExecuteCommandLogging(str):
    NONE = "NONE"
    DEFAULT = "DEFAULT"
    OVERRIDE = "OVERRIDE"


class FirelensConfigurationType(str):
    fluentd = "fluentd"
    fluentbit = "fluentbit"


class HealthStatus(str):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class InstanceHealthCheckState(str):
    OK = "OK"
    IMPAIRED = "IMPAIRED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    INITIALIZING = "INITIALIZING"


class InstanceHealthCheckType(str):
    CONTAINER_RUNTIME = "CONTAINER_RUNTIME"


class IpcMode(str):
    host = "host"
    task = "task"
    none = "none"


class LaunchType(str):
    EC2 = "EC2"
    FARGATE = "FARGATE"
    EXTERNAL = "EXTERNAL"


class LogDriver(str):
    json_file = "json-file"
    syslog = "syslog"
    journald = "journald"
    gelf = "gelf"
    fluentd = "fluentd"
    awslogs = "awslogs"
    splunk = "splunk"
    awsfirelens = "awsfirelens"


class ManagedAgentName(str):
    ExecuteCommandAgent = "ExecuteCommandAgent"


class ManagedScalingStatus(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class ManagedTerminationProtection(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class NetworkMode(str):
    bridge = "bridge"
    host = "host"
    awsvpc = "awsvpc"
    none = "none"


class OSFamily(str):
    WINDOWS_SERVER_2019_FULL = "WINDOWS_SERVER_2019_FULL"
    WINDOWS_SERVER_2019_CORE = "WINDOWS_SERVER_2019_CORE"
    WINDOWS_SERVER_2016_FULL = "WINDOWS_SERVER_2016_FULL"
    WINDOWS_SERVER_2004_CORE = "WINDOWS_SERVER_2004_CORE"
    WINDOWS_SERVER_2022_CORE = "WINDOWS_SERVER_2022_CORE"
    WINDOWS_SERVER_2022_FULL = "WINDOWS_SERVER_2022_FULL"
    WINDOWS_SERVER_20H2_CORE = "WINDOWS_SERVER_20H2_CORE"
    LINUX = "LINUX"


class PidMode(str):
    host = "host"
    task = "task"


class PlacementConstraintType(str):
    distinctInstance = "distinctInstance"
    memberOf = "memberOf"


class PlacementStrategyType(str):
    random = "random"
    spread = "spread"
    binpack = "binpack"


class PlatformDeviceType(str):
    GPU = "GPU"


class PropagateTags(str):
    TASK_DEFINITION = "TASK_DEFINITION"
    SERVICE = "SERVICE"
    NONE = "NONE"


class ProxyConfigurationType(str):
    APPMESH = "APPMESH"


class ResourceType(str):
    GPU = "GPU"
    InferenceAccelerator = "InferenceAccelerator"


class ScaleUnit(str):
    PERCENT = "PERCENT"


class SchedulingStrategy(str):
    REPLICA = "REPLICA"
    DAEMON = "DAEMON"


class Scope(str):
    task = "task"
    shared = "shared"


class ServiceField(str):
    TAGS = "TAGS"


class SettingName(str):
    serviceLongArnFormat = "serviceLongArnFormat"
    taskLongArnFormat = "taskLongArnFormat"
    containerInstanceLongArnFormat = "containerInstanceLongArnFormat"
    awsvpcTrunking = "awsvpcTrunking"
    containerInsights = "containerInsights"


class SortOrder(str):
    ASC = "ASC"
    DESC = "DESC"


class StabilityStatus(str):
    STEADY_STATE = "STEADY_STATE"
    STABILIZING = "STABILIZING"


class TargetType(str):
    container_instance = "container-instance"


class TaskDefinitionFamilyStatus(str):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ALL = "ALL"


class TaskDefinitionField(str):
    TAGS = "TAGS"


class TaskDefinitionPlacementConstraintType(str):
    memberOf = "memberOf"


class TaskDefinitionStatus(str):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class TaskField(str):
    TAGS = "TAGS"


class TaskSetField(str):
    TAGS = "TAGS"


class TaskStopCode(str):
    TaskFailedToStart = "TaskFailedToStart"
    EssentialContainerExited = "EssentialContainerExited"
    UserInitiated = "UserInitiated"


class TransportProtocol(str):
    tcp = "tcp"
    udp = "udp"


class UlimitName(str):
    core = "core"
    cpu = "cpu"
    data = "data"
    fsize = "fsize"
    locks = "locks"
    memlock = "memlock"
    msgqueue = "msgqueue"
    nice = "nice"
    nofile = "nofile"
    nproc = "nproc"
    rss = "rss"
    rtprio = "rtprio"
    rttime = "rttime"
    sigpending = "sigpending"
    stack = "stack"


class AccessDeniedException(ServiceException):
    """You don't have authorization to perform the requested action."""


class AttributeLimitExceededException(ServiceException):
    """You can apply up to 10 custom attributes for each resource. You can view
    the attributes of a resource with ListAttributes. You can remove
    existing attributes on a resource with DeleteAttributes.
    """


class BlockedException(ServiceException):
    """Your Amazon Web Services account was blocked. For more information,
    contact `Amazon Web Services
    Support <http://aws.amazon.com/contact-us/>`__.
    """


class ClientException(ServiceException):
    """These errors are usually caused by a client action. This client action
    might be using an action or resource on behalf of a user that doesn't
    have permissions to use the action or resource,. Or, it might be
    specifying an identifier that isn't valid.
    """

    message: Optional[String]


class ClusterContainsContainerInstancesException(ServiceException):
    """You can't delete a cluster that has registered container instances.
    First, deregister the container instances before you can delete the
    cluster. For more information, see DeregisterContainerInstance.
    """


class ClusterContainsServicesException(ServiceException):
    """You can't delete a cluster that contains services. First, update the
    service to reduce its desired task count to 0, and then delete the
    service. For more information, see UpdateService and DeleteService.
    """


class ClusterContainsTasksException(ServiceException):
    """You can't delete a cluster that has active tasks."""


class ClusterNotFoundException(ServiceException):
    """The specified cluster wasn't found. You can view your available clusters
    with ListClusters. Amazon ECS clusters are Region specific.
    """


class InvalidParameterException(ServiceException):
    """The specified parameter isn't valid. Review the available parameters for
    the API request.
    """


class LimitExceededException(ServiceException):
    """The limit for the resource was exceeded."""


class MissingVersionException(ServiceException):
    """Amazon ECS can't determine the current version of the Amazon ECS
    container agent on the container instance and doesn't have enough
    information to proceed with an update. This could be because the agent
    running on the container instance is a previous or custom version that
    doesn't use our version information.
    """


class NoUpdateAvailableException(ServiceException):
    """There's no update available for this Amazon ECS container agent. This
    might be because the agent is already running the latest version or
    because it's so old that there's no update path to the current version.
    """


class PlatformTaskDefinitionIncompatibilityException(ServiceException):
    """The specified platform version doesn't satisfy the required capabilities
    of the task definition.
    """


class PlatformUnknownException(ServiceException):
    """The specified platform version doesn't exist."""


class ResourceInUseException(ServiceException):
    """The specified resource is in-use and can't be removed."""


class ResourceNotFoundException(ServiceException):
    """The specified resource wasn't found."""


class ServerException(ServiceException):
    """These errors are usually caused by a server issue."""

    message: Optional[String]


class ServiceNotActiveException(ServiceException):
    """The specified service isn't active. You can't update a service that's
    inactive. If you have previously deleted a service, you can re-create it
    with CreateService.
    """


class ServiceNotFoundException(ServiceException):
    """The specified service wasn't found. You can view your available services
    with ListServices. Amazon ECS services are cluster specific and Region
    specific.
    """


class TargetNotConnectedException(ServiceException):
    """The execute command cannot run. This error can be caused by any of the
    following configuration issues:

    -  Incorrect IAM permissions

    -  The SSM agent is not installed or is not running

    -  There is an interface Amazon VPC endpoint for Amazon ECS, but there
       is not one for for Systems Manager Session Manager

    For information about how to troubleshoot the issues, see
    `Troubleshooting issues with ECS
    Exec <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """


class TargetNotFoundException(ServiceException):
    """The specified target wasn't found. You can view your available container
    instances with ListContainerInstances. Amazon ECS container instances
    are cluster-specific and Region-specific.
    """


class TaskSetNotFoundException(ServiceException):
    """The specified task set wasn't found. You can view your available task
    sets with DescribeTaskSets. Task sets are specific to each cluster,
    service and Region.
    """


class UnsupportedFeatureException(ServiceException):
    """The specified task isn't supported in this Region."""


class UpdateInProgressException(ServiceException):
    """There's already a current Amazon ECS container agent update in progress
    on the container instance that's specified. If the container agent
    becomes disconnected while it's in a transitional stage, such as
    ``PENDING`` or ``STAGING``, the update process can get stuck in that
    state. However, when the agent reconnects, it resumes where it stopped
    previously.
    """


class KeyValuePair(TypedDict, total=False):
    """A key-value pair object."""

    name: Optional[String]
    value: Optional[String]


AttachmentDetails = List[KeyValuePair]
Attachment = TypedDict(
    "Attachment",
    {
        "id": Optional[String],
        "type": Optional[String],
        "status": Optional[String],
        "details": Optional[AttachmentDetails],
    },
    total=False,
)


class AttachmentStateChange(TypedDict, total=False):
    """An object representing a change in state for a task attachment."""

    attachmentArn: String
    status: String


AttachmentStateChanges = List[AttachmentStateChange]
Attachments = List[Attachment]


class Attribute(TypedDict, total=False):
    """An attribute is a name-value pair that's associated with an Amazon ECS
    object. Use attributes to extend the Amazon ECS data model by adding
    custom metadata to your resources. For more information, see
    `Attributes <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-placement-constraints.html#attributes>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    name: String
    value: Optional[String]
    targetType: Optional[TargetType]
    targetId: Optional[String]


Attributes = List[Attribute]


class ManagedScaling(TypedDict, total=False):
    """The managed scaling settings for the Auto Scaling group capacity
    provider.

    When managed scaling is enabled, Amazon ECS manages the scale-in and
    scale-out actions of the Auto Scaling group. Amazon ECS manages a target
    tracking scaling policy using an Amazon ECS managed CloudWatch metric
    with the specified ``targetCapacity`` value as the target value for the
    metric. For more information, see `Using Managed
    Scaling <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/asg-capacity-providers.html#asg-capacity-providers-managed-scaling>`__
    in the *Amazon Elastic Container Service Developer Guide*.

    If managed scaling is disabled, the user must manage the scaling of the
    Auto Scaling group.
    """

    status: Optional[ManagedScalingStatus]
    targetCapacity: Optional[ManagedScalingTargetCapacity]
    minimumScalingStepSize: Optional[ManagedScalingStepSize]
    maximumScalingStepSize: Optional[ManagedScalingStepSize]
    instanceWarmupPeriod: Optional[ManagedScalingInstanceWarmupPeriod]


class AutoScalingGroupProvider(TypedDict, total=False):
    """The details of the Auto Scaling group for the capacity provider."""

    autoScalingGroupArn: String
    managedScaling: Optional[ManagedScaling]
    managedTerminationProtection: Optional[ManagedTerminationProtection]


class AutoScalingGroupProviderUpdate(TypedDict, total=False):
    """The details of the Auto Scaling group capacity provider to update."""

    managedScaling: Optional[ManagedScaling]
    managedTerminationProtection: Optional[ManagedTerminationProtection]


StringList = List[String]


class AwsVpcConfiguration(TypedDict, total=False):
    """An object representing the networking details for a task or service."""

    subnets: StringList
    securityGroups: Optional[StringList]
    assignPublicIp: Optional[AssignPublicIp]


class Tag(TypedDict, total=False):
    """The metadata that you apply to a resource to help you categorize and
    organize them. Each tag consists of a key and an optional value. You
    define them.

    The following basic restrictions apply to tags:

    -  Maximum number of tags per resource - 50

    -  For each resource, each tag key must be unique, and each tag key can
       have only one value.

    -  Maximum key length - 128 Unicode characters in UTF-8

    -  Maximum value length - 256 Unicode characters in UTF-8

    -  If your tagging schema is used across multiple services and
       resources, remember that other services may have restrictions on
       allowed characters. Generally allowed characters are: letters,
       numbers, and spaces representable in UTF-8, and the following
       characters: + - = . _ : / @.

    -  Tag keys and values are case-sensitive.

    -  Do not use ``aws:``, ``AWS:``, or any upper or lowercase combination
       of such as a prefix for either keys or values as it is reserved for
       Amazon Web Services use. You cannot edit or delete tag keys or values
       with this prefix. Tags with this prefix do not count against your
       tags per resource limit.
    """

    key: Optional[TagKey]
    value: Optional[TagValue]


Tags = List[Tag]


class CapacityProvider(TypedDict, total=False):
    """The details for a capacity provider."""

    capacityProviderArn: Optional[String]
    name: Optional[String]
    status: Optional[CapacityProviderStatus]
    autoScalingGroupProvider: Optional[AutoScalingGroupProvider]
    updateStatus: Optional[CapacityProviderUpdateStatus]
    updateStatusReason: Optional[String]
    tags: Optional[Tags]


CapacityProviderFieldList = List[CapacityProviderField]


class CapacityProviderStrategyItem(TypedDict, total=False):
    """The details of a capacity provider strategy. A capacity provider
    strategy can be set when using the RunTask or CreateCluster APIs or as
    the default capacity provider strategy for a cluster with the
    CreateCluster API.

    Only capacity providers that are already associated with a cluster and
    have an ``ACTIVE`` or ``UPDATING`` status can be used in a capacity
    provider strategy. The PutClusterCapacityProviders API is used to
    associate a capacity provider with a cluster.

    If specifying a capacity provider that uses an Auto Scaling group, the
    capacity provider must already be created. New Auto Scaling group
    capacity providers can be created with the CreateCapacityProvider API
    operation.

    To use a Fargate capacity provider, specify either the ``FARGATE`` or
    ``FARGATE_SPOT`` capacity providers. The Fargate capacity providers are
    available to all accounts and only need to be associated with a cluster
    to be used in a capacity provider strategy.

    A capacity provider strategy may contain a maximum of 6 capacity
    providers.
    """

    capacityProvider: String
    weight: Optional[CapacityProviderStrategyItemWeight]
    base: Optional[CapacityProviderStrategyItemBase]


CapacityProviderStrategy = List[CapacityProviderStrategyItem]
CapacityProviders = List[CapacityProvider]


class ClusterSetting(TypedDict, total=False):
    """The settings to use when creating a cluster. This parameter is used to
    turn on CloudWatch Container Insights for a cluster.
    """

    name: Optional[ClusterSettingName]
    value: Optional[String]


ClusterSettings = List[ClusterSetting]
Statistics = List[KeyValuePair]


class ExecuteCommandLogConfiguration(TypedDict, total=False):
    """The log configuration for the results of the execute command actions.
    The logs can be sent to CloudWatch Logs or an Amazon S3 bucket.
    """

    cloudWatchLogGroupName: Optional[String]
    cloudWatchEncryptionEnabled: Optional[Boolean]
    s3BucketName: Optional[String]
    s3EncryptionEnabled: Optional[Boolean]
    s3KeyPrefix: Optional[String]


class ExecuteCommandConfiguration(TypedDict, total=False):
    """The details of the execute command configuration."""

    kmsKeyId: Optional[String]
    logging: Optional[ExecuteCommandLogging]
    logConfiguration: Optional[ExecuteCommandLogConfiguration]


class ClusterConfiguration(TypedDict, total=False):
    """The execute command configuration for the cluster."""

    executeCommandConfiguration: Optional[ExecuteCommandConfiguration]


class Cluster(TypedDict, total=False):
    """A regional grouping of one or more container instances where you can run
    task requests. Each account receives a default cluster the first time
    you use the Amazon ECS service, but you may also create other clusters.
    Clusters may contain more than one instance type simultaneously.
    """

    clusterArn: Optional[String]
    clusterName: Optional[String]
    configuration: Optional[ClusterConfiguration]
    status: Optional[String]
    registeredContainerInstancesCount: Optional[Integer]
    runningTasksCount: Optional[Integer]
    pendingTasksCount: Optional[Integer]
    activeServicesCount: Optional[Integer]
    statistics: Optional[Statistics]
    tags: Optional[Tags]
    settings: Optional[ClusterSettings]
    capacityProviders: Optional[StringList]
    defaultCapacityProviderStrategy: Optional[CapacityProviderStrategy]
    attachments: Optional[Attachments]
    attachmentsStatus: Optional[String]


ClusterFieldList = List[ClusterField]
Clusters = List[Cluster]
CompatibilityList = List[Compatibility]
GpuIds = List[String]
Timestamp = datetime


class ManagedAgent(TypedDict, total=False):
    """Details about the managed agent status for the container."""

    lastStartedAt: Optional[Timestamp]
    name: Optional[ManagedAgentName]
    reason: Optional[String]
    lastStatus: Optional[String]


ManagedAgents = List[ManagedAgent]


class NetworkInterface(TypedDict, total=False):
    """An object representing the elastic network interface for tasks that use
    the ``awsvpc`` network mode.
    """

    attachmentId: Optional[String]
    privateIpv4Address: Optional[String]
    ipv6Address: Optional[String]


NetworkInterfaces = List[NetworkInterface]


class NetworkBinding(TypedDict, total=False):
    """Details on the network bindings between a container and its host
    container instance. After a task reaches the ``RUNNING`` status, manual
    and automatic host and container port assignments are visible in the
    ``networkBindings`` section of DescribeTasks API responses.
    """

    bindIP: Optional[String]
    containerPort: Optional[BoxedInteger]
    hostPort: Optional[BoxedInteger]
    protocol: Optional[TransportProtocol]


NetworkBindings = List[NetworkBinding]


class Container(TypedDict, total=False):
    """A Docker container that's part of a task."""

    containerArn: Optional[String]
    taskArn: Optional[String]
    name: Optional[String]
    image: Optional[String]
    imageDigest: Optional[String]
    runtimeId: Optional[String]
    lastStatus: Optional[String]
    exitCode: Optional[BoxedInteger]
    reason: Optional[String]
    networkBindings: Optional[NetworkBindings]
    networkInterfaces: Optional[NetworkInterfaces]
    healthStatus: Optional[HealthStatus]
    managedAgents: Optional[ManagedAgents]
    cpu: Optional[String]
    memory: Optional[String]
    memoryReservation: Optional[String]
    gpuIds: Optional[GpuIds]


FirelensConfigurationOptionsMap = Dict[String, String]
FirelensConfiguration = TypedDict(
    "FirelensConfiguration",
    {
        "type": FirelensConfigurationType,
        "options": Optional[FirelensConfigurationOptionsMap],
    },
    total=False,
)
ResourceRequirement = TypedDict(
    "ResourceRequirement",
    {
        "value": String,
        "type": ResourceType,
    },
    total=False,
)
ResourceRequirements = List[ResourceRequirement]


class SystemControl(TypedDict, total=False):
    """A list of namespaced kernel parameters to set in the container. This
    parameter maps to ``Sysctls`` in the `Create a
    container <https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`__
    section of the `Docker Remote
    API <https://docs.docker.com/engine/api/v1.35/>`__ and the ``--sysctl``
    option to `docker
    run <https://docs.docker.com/engine/reference/run/#security-configuration>`__.

    We don't recommend that you specify network-related ``systemControls``
    parameters for multiple containers in a single task. This task also uses
    either the ``awsvpc`` or ``host`` network mode. It does it for the
    following reasons.

    -  For tasks that use the ``awsvpc`` network mode, if you set
       ``systemControls`` for any container, it applies to all containers in
       the task. If you set different ``systemControls`` for multiple
       containers in a single task, the container that's started last
       determines which ``systemControls`` take effect.

    -  For tasks that use the ``host`` network mode, the ``systemControls``
       parameter applies to the container instance's kernel parameter and
       that of all containers of any tasks running on that container
       instance.
    """

    namespace: Optional[String]
    value: Optional[String]


SystemControls = List[SystemControl]


class HealthCheck(TypedDict, total=False):
    """An object representing a container health check. Health check parameters
    that are specified in a container definition override any Docker health
    checks that exist in the container image (such as those specified in a
    parent image or from the image's Dockerfile).

    The Amazon ECS container agent only monitors and reports on the health
    checks specified in the task definition. Amazon ECS does not monitor
    Docker health checks that are embedded in a container image and not
    specified in the container definition. Health check parameters that are
    specified in a container definition override any Docker health checks
    that exist in the container image.

    You can view the health status of both individual containers and a task
    with the DescribeTasks API operation or when viewing the task details in
    the console.

    The following describes the possible ``healthStatus`` values for a
    container:

    -  ``HEALTHY``-The container health check has passed successfully.

    -  ``UNHEALTHY``-The container health check has failed.

    -  ``UNKNOWN``-The container health check is being evaluated or there's
       no container health check defined.

    The following describes the possible ``healthStatus`` values for a task.
    The container health check status of nonessential containers do not have
    an effect on the health status of a task.

    -  ``HEALTHY``-All essential containers within the task have passed
       their health checks.

    -  ``UNHEALTHY``-One or more essential containers have failed their
       health check.

    -  ``UNKNOWN``-The essential containers within the task are still having
       their health checks evaluated or there are no container health checks
       defined.

    If a task is run manually, and not as part of a service, the task will
    continue its lifecycle regardless of its health status. For tasks that
    are part of a service, if the task reports as unhealthy then the task
    will be stopped and the service scheduler will replace it.

    The following are notes about container health check support:

    -  Container health checks require version 1.17.0 or greater of the
       Amazon ECS container agent. For more information, see `Updating the
       Amazon ECS Container
       Agent <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-update.html>`__.

    -  Container health checks are supported for Fargate tasks if you're
       using platform version 1.1.0 or greater. For more information, see
       `Fargate Platform
       Versions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html>`__.

    -  Container health checks aren't supported for tasks that are part of a
       service that's configured to use a Classic Load Balancer.
    """

    command: StringList
    interval: Optional[BoxedInteger]
    timeout: Optional[BoxedInteger]
    retries: Optional[BoxedInteger]
    startPeriod: Optional[BoxedInteger]


class Secret(TypedDict, total=False):
    """An object representing the secret to expose to your container. Secrets
    can be exposed to a container in the following ways:

    -  To inject sensitive data into your containers as environment
       variables, use the ``secrets`` container definition parameter.

    -  To reference sensitive information in the log configuration of a
       container, use the ``secretOptions`` container definition parameter.

    For more information, see `Specifying Sensitive
    Data <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    name: String
    valueFrom: String


SecretList = List[Secret]
LogConfigurationOptionsMap = Dict[String, String]


class LogConfiguration(TypedDict, total=False):
    """The log configuration for the container. This parameter maps to
    ``LogConfig`` in the `Create a
    container <https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`__
    section of the `Docker Remote
    API <https://docs.docker.com/engine/api/v1.35/>`__ and the
    ``--log-driver`` option to
    ```docker run`` <https://docs.docker.com/engine/reference/commandline/run/>`__
    .

    By default, containers use the same logging driver that the Docker
    daemon uses. However, the container might use a different logging driver
    than the Docker daemon by specifying a log driver configuration in the
    container definition. For more information about the options for
    different supported log drivers, see `Configure logging
    drivers <https://docs.docker.com/engine/admin/logging/overview/>`__ in
    the Docker documentation.

    Understand the following when specifying a log configuration for your
    containers.

    -  Amazon ECS currently supports a subset of the logging drivers
       available to the Docker daemon (shown in the valid values below).
       Additional log drivers may be available in future releases of the
       Amazon ECS container agent.

    -  This parameter requires version 1.18 of the Docker Remote API or
       greater on your container instance.

    -  For tasks that are hosted on Amazon EC2 instances, the Amazon ECS
       container agent must register the available logging drivers with the
       ``ECS_AVAILABLE_LOGGING_DRIVERS`` environment variable before
       containers placed on that instance can use these log configuration
       options. For more information, see `Amazon ECS container agent
       configuration <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-config.html>`__
       in the *Amazon Elastic Container Service Developer Guide*.

    -  For tasks that are on Fargate, because you don't have access to the
       underlying infrastructure your tasks are hosted on, any additional
       software needed must be installed outside of the task. For example,
       the Fluentd output aggregators or a remote host running Logstash to
       send Gelf logs to.
    """

    logDriver: LogDriver
    options: Optional[LogConfigurationOptionsMap]
    secretOptions: Optional[SecretList]


class Ulimit(TypedDict, total=False):
    """The ``ulimit`` settings to pass to the container.

    Amazon ECS tasks hosted on Fargate use the default resource limit values
    set by the operating system with the exception of the ``nofile``
    resource limit parameter which Fargate overrides. The ``nofile``
    resource limit sets a restriction on the number of open files that a
    container can use. The default ``nofile`` soft limit is ``1024`` and
    hard limit is ``4096``.
    """

    name: UlimitName
    softLimit: Integer
    hardLimit: Integer


UlimitList = List[Ulimit]
DockerLabelsMap = Dict[String, String]


class HostEntry(TypedDict, total=False):
    """Hostnames and IP address entries that are added to the ``/etc/hosts``
    file of a container via the ``extraHosts`` parameter of its
    ContainerDefinition.
    """

    hostname: String
    ipAddress: String


HostEntryList = List[HostEntry]


class ContainerDependency(TypedDict, total=False):
    """The dependencies defined for container startup and shutdown. A container
    can contain multiple dependencies. When a dependency is defined for
    container startup, for container shutdown it is reversed.

    Your Amazon ECS container instances require at least version 1.26.0 of
    the container agent to use container dependencies. However, we recommend
    using the latest container agent version. For information about checking
    your agent version and updating to the latest version, see `Updating the
    Amazon ECS Container
    Agent <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-update.html>`__
    in the *Amazon Elastic Container Service Developer Guide*. If you're
    using an Amazon ECS-optimized Linux AMI, your instance needs at least
    version 1.26.0-1 of the ``ecs-init`` package. If your container
    instances are launched from version ``20190301`` or later, then they
    contain the required versions of the container agent and ``ecs-init``.
    For more information, see `Amazon ECS-optimized Linux
    AMI <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.

    For tasks that use the Fargate launch type, the task or service requires
    the following platforms:

    -  Linux platform version ``1.3.0`` or later.

    -  Windows platform version ``1.0.0`` or later.
    """

    containerName: String
    condition: ContainerCondition


ContainerDependencies = List[ContainerDependency]


class Tmpfs(TypedDict, total=False):
    """The container path, mount options, and size of the tmpfs mount."""

    containerPath: String
    size: Integer
    mountOptions: Optional[StringList]


TmpfsList = List[Tmpfs]
DeviceCgroupPermissions = List[DeviceCgroupPermission]


class Device(TypedDict, total=False):
    """An object representing a container instance host device."""

    hostPath: String
    containerPath: Optional[String]
    permissions: Optional[DeviceCgroupPermissions]


DevicesList = List[Device]


class KernelCapabilities(TypedDict, total=False):
    """The Linux capabilities for the container that are added to or dropped
    from the default configuration provided by Docker. For more information
    about the default capabilities and the non-default available
    capabilities, see `Runtime privilege and Linux
    capabilities <https://docs.docker.com/engine/reference/run/#runtime-privilege-and-linux-capabilities>`__
    in the *Docker run reference*. For more detailed information about these
    Linux capabilities, see the
    `capabilities(7) <http://man7.org/linux/man-pages/man7/capabilities.7.html>`__
    Linux manual page.
    """

    add: Optional[StringList]
    drop: Optional[StringList]


class LinuxParameters(TypedDict, total=False):
    """Linux-specific options that are applied to the container, such as Linux
    KernelCapabilities.
    """

    capabilities: Optional[KernelCapabilities]
    devices: Optional[DevicesList]
    initProcessEnabled: Optional[BoxedBoolean]
    sharedMemorySize: Optional[BoxedInteger]
    tmpfs: Optional[TmpfsList]
    maxSwap: Optional[BoxedInteger]
    swappiness: Optional[BoxedInteger]


class VolumeFrom(TypedDict, total=False):
    """Details on a data volume from another container in the same task
    definition.
    """

    sourceContainer: Optional[String]
    readOnly: Optional[BoxedBoolean]


VolumeFromList = List[VolumeFrom]


class MountPoint(TypedDict, total=False):
    """Details for a volume mount point that's used in a container definition."""

    sourceVolume: Optional[String]
    containerPath: Optional[String]
    readOnly: Optional[BoxedBoolean]


MountPointList = List[MountPoint]
EnvironmentFile = TypedDict(
    "EnvironmentFile",
    {
        "value": String,
        "type": EnvironmentFileType,
    },
    total=False,
)
EnvironmentFiles = List[EnvironmentFile]
EnvironmentVariables = List[KeyValuePair]


class PortMapping(TypedDict, total=False):
    """Port mappings allow containers to access ports on the host container
    instance to send or receive traffic. Port mappings are specified as part
    of the container definition.

    If you use containers in a task with the ``awsvpc`` or ``host`` network
    mode, specify the exposed ports using ``containerPort``. The
    ``hostPort`` can be left blank or it must be the same value as the
    ``containerPort``.

    You can't expose the same container port for multiple protocols. If you
    attempt this, an error is returned.

    After a task reaches the ``RUNNING`` status, manual and automatic host
    and container port assignments are visible in the ``networkBindings``
    section of DescribeTasks API responses.
    """

    containerPort: Optional[BoxedInteger]
    hostPort: Optional[BoxedInteger]
    protocol: Optional[TransportProtocol]


PortMappingList = List[PortMapping]


class RepositoryCredentials(TypedDict, total=False):
    """The repository credentials for private registry authentication."""

    credentialsParameter: String


class ContainerDefinition(TypedDict, total=False):
    """Container definitions are used in task definitions to describe the
    different containers that are launched as part of a task.
    """

    name: Optional[String]
    image: Optional[String]
    repositoryCredentials: Optional[RepositoryCredentials]
    cpu: Optional[Integer]
    memory: Optional[BoxedInteger]
    memoryReservation: Optional[BoxedInteger]
    links: Optional[StringList]
    portMappings: Optional[PortMappingList]
    essential: Optional[BoxedBoolean]
    entryPoint: Optional[StringList]
    command: Optional[StringList]
    environment: Optional[EnvironmentVariables]
    environmentFiles: Optional[EnvironmentFiles]
    mountPoints: Optional[MountPointList]
    volumesFrom: Optional[VolumeFromList]
    linuxParameters: Optional[LinuxParameters]
    secrets: Optional[SecretList]
    dependsOn: Optional[ContainerDependencies]
    startTimeout: Optional[BoxedInteger]
    stopTimeout: Optional[BoxedInteger]
    hostname: Optional[String]
    user: Optional[String]
    workingDirectory: Optional[String]
    disableNetworking: Optional[BoxedBoolean]
    privileged: Optional[BoxedBoolean]
    readonlyRootFilesystem: Optional[BoxedBoolean]
    dnsServers: Optional[StringList]
    dnsSearchDomains: Optional[StringList]
    extraHosts: Optional[HostEntryList]
    dockerSecurityOptions: Optional[StringList]
    interactive: Optional[BoxedBoolean]
    pseudoTerminal: Optional[BoxedBoolean]
    dockerLabels: Optional[DockerLabelsMap]
    ulimits: Optional[UlimitList]
    logConfiguration: Optional[LogConfiguration]
    healthCheck: Optional[HealthCheck]
    systemControls: Optional[SystemControls]
    resourceRequirements: Optional[ResourceRequirements]
    firelensConfiguration: Optional[FirelensConfiguration]


ContainerDefinitions = List[ContainerDefinition]
InstanceHealthCheckResult = TypedDict(
    "InstanceHealthCheckResult",
    {
        "type": Optional[InstanceHealthCheckType],
        "status": Optional[InstanceHealthCheckState],
        "lastUpdated": Optional[Timestamp],
        "lastStatusChange": Optional[Timestamp],
    },
    total=False,
)
InstanceHealthCheckResultList = List[InstanceHealthCheckResult]


class ContainerInstanceHealthStatus(TypedDict, total=False):
    """An object representing the health status of the container instance."""

    overallStatus: Optional[InstanceHealthCheckState]
    details: Optional[InstanceHealthCheckResultList]


Long = int
Resource = TypedDict(
    "Resource",
    {
        "name": Optional[String],
        "type": Optional[String],
        "doubleValue": Optional[Double],
        "longValue": Optional[Long],
        "integerValue": Optional[Integer],
        "stringSetValue": Optional[StringList],
    },
    total=False,
)
Resources = List[Resource]


class VersionInfo(TypedDict, total=False):
    """The Docker and Amazon ECS container agent version information about a
    container instance.
    """

    agentVersion: Optional[String]
    agentHash: Optional[String]
    dockerVersion: Optional[String]


class ContainerInstance(TypedDict, total=False):
    """An EC2 instance that's running the Amazon ECS agent and has been
    registered with a cluster.
    """

    containerInstanceArn: Optional[String]
    ec2InstanceId: Optional[String]
    capacityProviderName: Optional[String]
    version: Optional[Long]
    versionInfo: Optional[VersionInfo]
    remainingResources: Optional[Resources]
    registeredResources: Optional[Resources]
    status: Optional[String]
    statusReason: Optional[String]
    agentConnected: Optional[Boolean]
    runningTasksCount: Optional[Integer]
    pendingTasksCount: Optional[Integer]
    agentUpdateStatus: Optional[AgentUpdateStatus]
    attributes: Optional[Attributes]
    registeredAt: Optional[Timestamp]
    attachments: Optional[Attachments]
    tags: Optional[Tags]
    healthStatus: Optional[ContainerInstanceHealthStatus]


ContainerInstanceFieldList = List[ContainerInstanceField]
ContainerInstances = List[ContainerInstance]


class ContainerOverride(TypedDict, total=False):
    """The overrides that are sent to a container. An empty container override
    can be passed in. An example of an empty container override is
    ``{"containerOverrides": [ ] }``. If a non-empty container override is
    specified, the ``name`` parameter must be included.
    """

    name: Optional[String]
    command: Optional[StringList]
    environment: Optional[EnvironmentVariables]
    environmentFiles: Optional[EnvironmentFiles]
    cpu: Optional[BoxedInteger]
    memory: Optional[BoxedInteger]
    memoryReservation: Optional[BoxedInteger]
    resourceRequirements: Optional[ResourceRequirements]


ContainerOverrides = List[ContainerOverride]


class ContainerStateChange(TypedDict, total=False):
    """An object that represents a change in state for a container."""

    containerName: Optional[String]
    imageDigest: Optional[String]
    runtimeId: Optional[String]
    exitCode: Optional[BoxedInteger]
    networkBindings: Optional[NetworkBindings]
    reason: Optional[String]
    status: Optional[String]


ContainerStateChanges = List[ContainerStateChange]
Containers = List[Container]


class CreateCapacityProviderRequest(ServiceRequest):
    name: String
    autoScalingGroupProvider: AutoScalingGroupProvider
    tags: Optional[Tags]


class CreateCapacityProviderResponse(TypedDict, total=False):
    capacityProvider: Optional[CapacityProvider]


class CreateClusterRequest(ServiceRequest):
    clusterName: Optional[String]
    tags: Optional[Tags]
    settings: Optional[ClusterSettings]
    configuration: Optional[ClusterConfiguration]
    capacityProviders: Optional[StringList]
    defaultCapacityProviderStrategy: Optional[CapacityProviderStrategy]


class CreateClusterResponse(TypedDict, total=False):
    cluster: Optional[Cluster]


DeploymentController = TypedDict(
    "DeploymentController",
    {
        "type": DeploymentControllerType,
    },
    total=False,
)


class NetworkConfiguration(TypedDict, total=False):
    """An object representing the network configuration for a task or service."""

    awsvpcConfiguration: Optional[AwsVpcConfiguration]


PlacementStrategy = TypedDict(
    "PlacementStrategy",
    {
        "type": Optional[PlacementStrategyType],
        "field": Optional[String],
    },
    total=False,
)
PlacementStrategies = List[PlacementStrategy]
PlacementConstraint = TypedDict(
    "PlacementConstraint",
    {
        "type": Optional[PlacementConstraintType],
        "expression": Optional[String],
    },
    total=False,
)
PlacementConstraints = List[PlacementConstraint]


class DeploymentCircuitBreaker(TypedDict, total=False):
    """The deployment circuit breaker can only be used for services using the
    rolling update (``ECS``) deployment type that aren't behind a Classic
    Load Balancer.

    The **deployment circuit breaker** determines whether a service
    deployment will fail if the service can't reach a steady state. If
    enabled, a service deployment will transition to a failed state and stop
    launching new tasks. You can also configure Amazon ECS to roll back your
    service to the last completed deployment after a failure. For more
    information, see `Rolling
    update <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-ecs.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    enable: Boolean
    rollback: Boolean


class DeploymentConfiguration(TypedDict, total=False):
    """Optional deployment parameters that control how many tasks run during a
    deployment and the ordering of stopping and starting tasks.
    """

    deploymentCircuitBreaker: Optional[DeploymentCircuitBreaker]
    maximumPercent: Optional[BoxedInteger]
    minimumHealthyPercent: Optional[BoxedInteger]


class ServiceRegistry(TypedDict, total=False):
    """The details for the service registry.

    Each service may be associated with one service registry. Multiple
    service registries for each service are not supported.

    When you add, update, or remove the service registries configuration,
    Amazon ECS starts a new deployment. New tasks are registered and
    deregistered to the updated service registry configuration.
    """

    registryArn: Optional[String]
    port: Optional[BoxedInteger]
    containerName: Optional[String]
    containerPort: Optional[BoxedInteger]


ServiceRegistries = List[ServiceRegistry]


class LoadBalancer(TypedDict, total=False):
    """The load balancer configuration to use with a service or task set.

    For specific notes and restrictions regarding the use of load balancers
    with services and task sets, see the CreateService and CreateTaskSet
    actions.

    When you add, update, or remove a load balancer configuration, Amazon
    ECS starts a new deployment with the updated Elastic Load Balancing
    configuration. This causes tasks to register to and deregister from load
    balancers.

    We recommend that you verify this on a test environment before you
    update the Elastic Load Balancing configuration.

    A service-linked role is required for services that use multiple target
    groups. For more information, see `Service-linked
    roles <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using-service-linked-roles.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    targetGroupArn: Optional[String]
    loadBalancerName: Optional[String]
    containerName: Optional[String]
    containerPort: Optional[BoxedInteger]


LoadBalancers = List[LoadBalancer]


class CreateServiceRequest(ServiceRequest):
    cluster: Optional[String]
    serviceName: String
    taskDefinition: Optional[String]
    loadBalancers: Optional[LoadBalancers]
    serviceRegistries: Optional[ServiceRegistries]
    desiredCount: Optional[BoxedInteger]
    clientToken: Optional[String]
    launchType: Optional[LaunchType]
    capacityProviderStrategy: Optional[CapacityProviderStrategy]
    platformVersion: Optional[String]
    role: Optional[String]
    deploymentConfiguration: Optional[DeploymentConfiguration]
    placementConstraints: Optional[PlacementConstraints]
    placementStrategy: Optional[PlacementStrategies]
    networkConfiguration: Optional[NetworkConfiguration]
    healthCheckGracePeriodSeconds: Optional[BoxedInteger]
    schedulingStrategy: Optional[SchedulingStrategy]
    deploymentController: Optional[DeploymentController]
    tags: Optional[Tags]
    enableECSManagedTags: Optional[Boolean]
    propagateTags: Optional[PropagateTags]
    enableExecuteCommand: Optional[Boolean]


class ServiceEvent(TypedDict, total=False):
    """The details for an event that's associated with a service."""

    id: Optional[String]
    createdAt: Optional[Timestamp]
    message: Optional[String]


ServiceEvents = List[ServiceEvent]


class Deployment(TypedDict, total=False):
    """The details of an Amazon ECS service deployment. This is used only when
    a service uses the ``ECS`` deployment controller type.
    """

    id: Optional[String]
    status: Optional[String]
    taskDefinition: Optional[String]
    desiredCount: Optional[Integer]
    pendingCount: Optional[Integer]
    runningCount: Optional[Integer]
    failedTasks: Optional[Integer]
    createdAt: Optional[Timestamp]
    updatedAt: Optional[Timestamp]
    capacityProviderStrategy: Optional[CapacityProviderStrategy]
    launchType: Optional[LaunchType]
    platformVersion: Optional[String]
    platformFamily: Optional[String]
    networkConfiguration: Optional[NetworkConfiguration]
    rolloutState: Optional[DeploymentRolloutState]
    rolloutStateReason: Optional[String]


Deployments = List[Deployment]


class Scale(TypedDict, total=False):
    """A floating-point percentage of the desired number of tasks to place and
    keep running in the task set.
    """

    value: Optional[Double]
    unit: Optional[ScaleUnit]


class TaskSet(TypedDict, total=False):
    """Information about a set of Amazon ECS tasks in either an CodeDeploy or
    an ``EXTERNAL`` deployment. An Amazon ECS task set includes details such
    as the desired number of tasks, how many tasks are running, and whether
    the task set serves production traffic.
    """

    id: Optional[String]
    taskSetArn: Optional[String]
    serviceArn: Optional[String]
    clusterArn: Optional[String]
    startedBy: Optional[String]
    externalId: Optional[String]
    status: Optional[String]
    taskDefinition: Optional[String]
    computedDesiredCount: Optional[Integer]
    pendingCount: Optional[Integer]
    runningCount: Optional[Integer]
    createdAt: Optional[Timestamp]
    updatedAt: Optional[Timestamp]
    launchType: Optional[LaunchType]
    capacityProviderStrategy: Optional[CapacityProviderStrategy]
    platformVersion: Optional[String]
    platformFamily: Optional[String]
    networkConfiguration: Optional[NetworkConfiguration]
    loadBalancers: Optional[LoadBalancers]
    serviceRegistries: Optional[ServiceRegistries]
    scale: Optional[Scale]
    stabilityStatus: Optional[StabilityStatus]
    stabilityStatusAt: Optional[Timestamp]
    tags: Optional[Tags]


TaskSets = List[TaskSet]


class Service(TypedDict, total=False):
    """Details on a service within a cluster"""

    serviceArn: Optional[String]
    serviceName: Optional[String]
    clusterArn: Optional[String]
    loadBalancers: Optional[LoadBalancers]
    serviceRegistries: Optional[ServiceRegistries]
    status: Optional[String]
    desiredCount: Optional[Integer]
    runningCount: Optional[Integer]
    pendingCount: Optional[Integer]
    launchType: Optional[LaunchType]
    capacityProviderStrategy: Optional[CapacityProviderStrategy]
    platformVersion: Optional[String]
    platformFamily: Optional[String]
    taskDefinition: Optional[String]
    deploymentConfiguration: Optional[DeploymentConfiguration]
    taskSets: Optional[TaskSets]
    deployments: Optional[Deployments]
    roleArn: Optional[String]
    events: Optional[ServiceEvents]
    createdAt: Optional[Timestamp]
    placementConstraints: Optional[PlacementConstraints]
    placementStrategy: Optional[PlacementStrategies]
    networkConfiguration: Optional[NetworkConfiguration]
    healthCheckGracePeriodSeconds: Optional[BoxedInteger]
    schedulingStrategy: Optional[SchedulingStrategy]
    deploymentController: Optional[DeploymentController]
    tags: Optional[Tags]
    createdBy: Optional[String]
    enableECSManagedTags: Optional[Boolean]
    propagateTags: Optional[PropagateTags]
    enableExecuteCommand: Optional[Boolean]


class CreateServiceResponse(TypedDict, total=False):
    service: Optional[Service]


class CreateTaskSetRequest(ServiceRequest):
    service: String
    cluster: String
    externalId: Optional[String]
    taskDefinition: String
    networkConfiguration: Optional[NetworkConfiguration]
    loadBalancers: Optional[LoadBalancers]
    serviceRegistries: Optional[ServiceRegistries]
    launchType: Optional[LaunchType]
    capacityProviderStrategy: Optional[CapacityProviderStrategy]
    platformVersion: Optional[String]
    scale: Optional[Scale]
    clientToken: Optional[String]
    tags: Optional[Tags]


class CreateTaskSetResponse(TypedDict, total=False):
    taskSet: Optional[TaskSet]


class DeleteAccountSettingRequest(ServiceRequest):
    name: SettingName
    principalArn: Optional[String]


class Setting(TypedDict, total=False):
    """The current account setting for a resource."""

    name: Optional[SettingName]
    value: Optional[String]
    principalArn: Optional[String]


class DeleteAccountSettingResponse(TypedDict, total=False):
    setting: Optional[Setting]


class DeleteAttributesRequest(ServiceRequest):
    cluster: Optional[String]
    attributes: Attributes


class DeleteAttributesResponse(TypedDict, total=False):
    attributes: Optional[Attributes]


class DeleteCapacityProviderRequest(ServiceRequest):
    capacityProvider: String


class DeleteCapacityProviderResponse(TypedDict, total=False):
    capacityProvider: Optional[CapacityProvider]


class DeleteClusterRequest(ServiceRequest):
    cluster: String


class DeleteClusterResponse(TypedDict, total=False):
    cluster: Optional[Cluster]


class DeleteServiceRequest(ServiceRequest):
    cluster: Optional[String]
    service: String
    force: Optional[BoxedBoolean]


class DeleteServiceResponse(TypedDict, total=False):
    service: Optional[Service]


class DeleteTaskSetRequest(ServiceRequest):
    cluster: String
    service: String
    taskSet: String
    force: Optional[BoxedBoolean]


class DeleteTaskSetResponse(TypedDict, total=False):
    taskSet: Optional[TaskSet]


class DeregisterContainerInstanceRequest(ServiceRequest):
    cluster: Optional[String]
    containerInstance: String
    force: Optional[BoxedBoolean]


class DeregisterContainerInstanceResponse(TypedDict, total=False):
    containerInstance: Optional[ContainerInstance]


class DeregisterTaskDefinitionRequest(ServiceRequest):
    taskDefinition: String


class EphemeralStorage(TypedDict, total=False):
    """The amount of ephemeral storage to allocate for the task. This parameter
    is used to expand the total amount of ephemeral storage available,
    beyond the default amount, for tasks hosted on Fargate. For more
    information, see `Fargate task
    storage <https://docs.aws.amazon.com/AmazonECS/latest/userguide/using_data_volumes.html>`__
    in the *Amazon ECS User Guide for Fargate*.

    This parameter is only supported for tasks hosted on Fargate using Linux
    platform version ``1.4.0`` or later. This parameter is not supported for
    Windows containers on Fargate.
    """

    sizeInGiB: Integer


ProxyConfigurationProperties = List[KeyValuePair]
ProxyConfiguration = TypedDict(
    "ProxyConfiguration",
    {
        "type": Optional[ProxyConfigurationType],
        "containerName": String,
        "properties": Optional[ProxyConfigurationProperties],
    },
    total=False,
)


class InferenceAccelerator(TypedDict, total=False):
    """Details on an Elastic Inference accelerator. For more information, see
    `Working with Amazon Elastic Inference on Amazon
    ECS <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-inference.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    deviceName: String
    deviceType: String


InferenceAccelerators = List[InferenceAccelerator]


class RuntimePlatform(TypedDict, total=False):
    """Information about the platform for the Amazon ECS service or task.

    For more informataion about ``RuntimePlatform``, see
    `RuntimePlatform <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#runtime-platform>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    cpuArchitecture: Optional[CPUArchitecture]
    operatingSystemFamily: Optional[OSFamily]


TaskDefinitionPlacementConstraint = TypedDict(
    "TaskDefinitionPlacementConstraint",
    {
        "type": Optional[TaskDefinitionPlacementConstraintType],
        "expression": Optional[String],
    },
    total=False,
)
TaskDefinitionPlacementConstraints = List[TaskDefinitionPlacementConstraint]
RequiresAttributes = List[Attribute]


class FSxWindowsFileServerAuthorizationConfig(TypedDict, total=False):
    """The authorization configuration details for Amazon FSx for Windows File
    Server file system. See
    `FSxWindowsFileServerVolumeConfiguration <https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_FSxWindowsFileServerVolumeConfiguration.html>`__
    in the *Amazon Elastic Container Service API Reference*.

    For more information and the input format, see `Amazon FSx for Windows
    File Server
    Volumes <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/wfsx-volumes.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    credentialsParameter: String
    domain: String


class FSxWindowsFileServerVolumeConfiguration(TypedDict, total=False):
    """This parameter is specified when you're using `Amazon FSx for Windows
    File
    Server <https://docs.aws.amazon.com/fsx/latest/WindowsGuide/what-is.html>`__
    file system for task storage.

    For more information and the input format, see `Amazon FSx for Windows
    File Server
    Volumes <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/wfsx-volumes.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    fileSystemId: String
    rootDirectory: String
    authorizationConfig: FSxWindowsFileServerAuthorizationConfig


class EFSAuthorizationConfig(TypedDict, total=False):
    """The authorization configuration details for the Amazon EFS file system."""

    accessPointId: Optional[String]
    iam: Optional[EFSAuthorizationConfigIAM]


class EFSVolumeConfiguration(TypedDict, total=False):
    """This parameter is specified when you're using an Amazon Elastic File
    System file system for task storage. For more information, see `Amazon
    EFS
    Volumes <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/efs-volumes.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    fileSystemId: String
    rootDirectory: Optional[String]
    transitEncryption: Optional[EFSTransitEncryption]
    transitEncryptionPort: Optional[BoxedInteger]
    authorizationConfig: Optional[EFSAuthorizationConfig]


StringMap = Dict[String, String]


class DockerVolumeConfiguration(TypedDict, total=False):
    """This parameter is specified when you're using Docker volumes. Docker
    volumes are only supported when you're using the EC2 launch type.
    Windows containers only support the use of the ``local`` driver. To use
    bind mounts, specify a ``host`` instead.
    """

    scope: Optional[Scope]
    autoprovision: Optional[BoxedBoolean]
    driver: Optional[String]
    driverOpts: Optional[StringMap]
    labels: Optional[StringMap]


class HostVolumeProperties(TypedDict, total=False):
    """Details on a container instance bind mount host volume."""

    sourcePath: Optional[String]


class Volume(TypedDict, total=False):
    """A data volume that's used in a task definition. For tasks that use the
    Amazon Elastic File System (Amazon EFS), specify an
    ``efsVolumeConfiguration``. For Windows tasks that use Amazon FSx for
    Windows File Server file system, specify a
    ``fsxWindowsFileServerVolumeConfiguration``. For tasks that use a Docker
    volume, specify a ``DockerVolumeConfiguration``. For tasks that use a
    bind mount host volume, specify a ``host`` and optional ``sourcePath``.
    For more information, see `Using Data Volumes in
    Tasks <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_data_volumes.html>`__.
    """

    name: Optional[String]
    host: Optional[HostVolumeProperties]
    dockerVolumeConfiguration: Optional[DockerVolumeConfiguration]
    efsVolumeConfiguration: Optional[EFSVolumeConfiguration]
    fsxWindowsFileServerVolumeConfiguration: Optional[FSxWindowsFileServerVolumeConfiguration]


VolumeList = List[Volume]


class TaskDefinition(TypedDict, total=False):
    """The details of a task definition which describes the container and
    volume definitions of an Amazon Elastic Container Service task. You can
    specify which Docker images to use, the required resources, and other
    configurations related to launching the task definition through an
    Amazon ECS service or task.
    """

    taskDefinitionArn: Optional[String]
    containerDefinitions: Optional[ContainerDefinitions]
    family: Optional[String]
    taskRoleArn: Optional[String]
    executionRoleArn: Optional[String]
    networkMode: Optional[NetworkMode]
    revision: Optional[Integer]
    volumes: Optional[VolumeList]
    status: Optional[TaskDefinitionStatus]
    requiresAttributes: Optional[RequiresAttributes]
    placementConstraints: Optional[TaskDefinitionPlacementConstraints]
    compatibilities: Optional[CompatibilityList]
    runtimePlatform: Optional[RuntimePlatform]
    requiresCompatibilities: Optional[CompatibilityList]
    cpu: Optional[String]
    memory: Optional[String]
    inferenceAccelerators: Optional[InferenceAccelerators]
    pidMode: Optional[PidMode]
    ipcMode: Optional[IpcMode]
    proxyConfiguration: Optional[ProxyConfiguration]
    registeredAt: Optional[Timestamp]
    deregisteredAt: Optional[Timestamp]
    registeredBy: Optional[String]
    ephemeralStorage: Optional[EphemeralStorage]


class DeregisterTaskDefinitionResponse(TypedDict, total=False):
    taskDefinition: Optional[TaskDefinition]


class DescribeCapacityProvidersRequest(ServiceRequest):
    capacityProviders: Optional[StringList]
    include: Optional[CapacityProviderFieldList]
    maxResults: Optional[BoxedInteger]
    nextToken: Optional[String]


class Failure(TypedDict, total=False):
    """A failed resource. For a list of common causes, see `API failure
    reasons <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/api_failures_messages.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    arn: Optional[String]
    reason: Optional[String]
    detail: Optional[String]


Failures = List[Failure]


class DescribeCapacityProvidersResponse(TypedDict, total=False):
    capacityProviders: Optional[CapacityProviders]
    failures: Optional[Failures]
    nextToken: Optional[String]


class DescribeClustersRequest(ServiceRequest):
    clusters: Optional[StringList]
    include: Optional[ClusterFieldList]


class DescribeClustersResponse(TypedDict, total=False):
    clusters: Optional[Clusters]
    failures: Optional[Failures]


class DescribeContainerInstancesRequest(ServiceRequest):
    cluster: Optional[String]
    containerInstances: StringList
    include: Optional[ContainerInstanceFieldList]


class DescribeContainerInstancesResponse(TypedDict, total=False):
    containerInstances: Optional[ContainerInstances]
    failures: Optional[Failures]


ServiceFieldList = List[ServiceField]


class DescribeServicesRequest(ServiceRequest):
    cluster: Optional[String]
    services: StringList
    include: Optional[ServiceFieldList]


Services = List[Service]


class DescribeServicesResponse(TypedDict, total=False):
    services: Optional[Services]
    failures: Optional[Failures]


TaskDefinitionFieldList = List[TaskDefinitionField]


class DescribeTaskDefinitionRequest(ServiceRequest):
    taskDefinition: String
    include: Optional[TaskDefinitionFieldList]


class DescribeTaskDefinitionResponse(TypedDict, total=False):
    taskDefinition: Optional[TaskDefinition]
    tags: Optional[Tags]


TaskSetFieldList = List[TaskSetField]


class DescribeTaskSetsRequest(ServiceRequest):
    cluster: String
    service: String
    taskSets: Optional[StringList]
    include: Optional[TaskSetFieldList]


class DescribeTaskSetsResponse(TypedDict, total=False):
    taskSets: Optional[TaskSets]
    failures: Optional[Failures]


TaskFieldList = List[TaskField]


class DescribeTasksRequest(ServiceRequest):
    cluster: Optional[String]
    tasks: StringList
    include: Optional[TaskFieldList]


class InferenceAcceleratorOverride(TypedDict, total=False):
    """Details on an Elastic Inference accelerator task override. This
    parameter is used to override the Elastic Inference accelerator
    specified in the task definition. For more information, see `Working
    with Amazon Elastic Inference on Amazon
    ECS <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-inference.html>`__
    in the *Amazon Elastic Container Service Developer Guide*.
    """

    deviceName: Optional[String]
    deviceType: Optional[String]


InferenceAcceleratorOverrides = List[InferenceAcceleratorOverride]


class TaskOverride(TypedDict, total=False):
    """The overrides that are associated with a task."""

    containerOverrides: Optional[ContainerOverrides]
    cpu: Optional[String]
    inferenceAcceleratorOverrides: Optional[InferenceAcceleratorOverrides]
    executionRoleArn: Optional[String]
    memory: Optional[String]
    taskRoleArn: Optional[String]
    ephemeralStorage: Optional[EphemeralStorage]


class Task(TypedDict, total=False):
    """Details on a task in a cluster."""

    attachments: Optional[Attachments]
    attributes: Optional[Attributes]
    availabilityZone: Optional[String]
    capacityProviderName: Optional[String]
    clusterArn: Optional[String]
    connectivity: Optional[Connectivity]
    connectivityAt: Optional[Timestamp]
    containerInstanceArn: Optional[String]
    containers: Optional[Containers]
    cpu: Optional[String]
    createdAt: Optional[Timestamp]
    desiredStatus: Optional[String]
    enableExecuteCommand: Optional[Boolean]
    executionStoppedAt: Optional[Timestamp]
    group: Optional[String]
    healthStatus: Optional[HealthStatus]
    inferenceAccelerators: Optional[InferenceAccelerators]
    lastStatus: Optional[String]
    launchType: Optional[LaunchType]
    memory: Optional[String]
    overrides: Optional[TaskOverride]
    platformVersion: Optional[String]
    platformFamily: Optional[String]
    pullStartedAt: Optional[Timestamp]
    pullStoppedAt: Optional[Timestamp]
    startedAt: Optional[Timestamp]
    startedBy: Optional[String]
    stopCode: Optional[TaskStopCode]
    stoppedAt: Optional[Timestamp]
    stoppedReason: Optional[String]
    stoppingAt: Optional[Timestamp]
    tags: Optional[Tags]
    taskArn: Optional[String]
    taskDefinitionArn: Optional[String]
    version: Optional[Long]
    ephemeralStorage: Optional[EphemeralStorage]


Tasks = List[Task]


class DescribeTasksResponse(TypedDict, total=False):
    tasks: Optional[Tasks]
    failures: Optional[Failures]


class DiscoverPollEndpointRequest(ServiceRequest):
    containerInstance: Optional[String]
    cluster: Optional[String]


class DiscoverPollEndpointResponse(TypedDict, total=False):
    endpoint: Optional[String]
    telemetryEndpoint: Optional[String]


class ExecuteCommandRequest(ServiceRequest):
    cluster: Optional[String]
    container: Optional[String]
    command: String
    interactive: Boolean
    task: String


class Session(TypedDict, total=False):
    """The details for the execute command session."""

    sessionId: Optional[String]
    streamUrl: Optional[String]
    tokenValue: Optional[SensitiveString]


class ExecuteCommandResponse(TypedDict, total=False):
    clusterArn: Optional[String]
    containerArn: Optional[String]
    containerName: Optional[String]
    interactive: Optional[Boolean]
    session: Optional[Session]
    taskArn: Optional[String]


class ListAccountSettingsRequest(ServiceRequest):
    name: Optional[SettingName]
    value: Optional[String]
    principalArn: Optional[String]
    effectiveSettings: Optional[Boolean]
    nextToken: Optional[String]
    maxResults: Optional[Integer]


Settings = List[Setting]


class ListAccountSettingsResponse(TypedDict, total=False):
    settings: Optional[Settings]
    nextToken: Optional[String]


class ListAttributesRequest(ServiceRequest):
    cluster: Optional[String]
    targetType: TargetType
    attributeName: Optional[String]
    attributeValue: Optional[String]
    nextToken: Optional[String]
    maxResults: Optional[BoxedInteger]


class ListAttributesResponse(TypedDict, total=False):
    attributes: Optional[Attributes]
    nextToken: Optional[String]


class ListClustersRequest(ServiceRequest):
    nextToken: Optional[String]
    maxResults: Optional[BoxedInteger]


class ListClustersResponse(TypedDict, total=False):
    clusterArns: Optional[StringList]
    nextToken: Optional[String]


class ListContainerInstancesRequest(ServiceRequest):
    cluster: Optional[String]
    filter: Optional[String]
    nextToken: Optional[String]
    maxResults: Optional[BoxedInteger]
    status: Optional[ContainerInstanceStatus]


class ListContainerInstancesResponse(TypedDict, total=False):
    containerInstanceArns: Optional[StringList]
    nextToken: Optional[String]


class ListServicesRequest(ServiceRequest):
    cluster: Optional[String]
    nextToken: Optional[String]
    maxResults: Optional[BoxedInteger]
    launchType: Optional[LaunchType]
    schedulingStrategy: Optional[SchedulingStrategy]


class ListServicesResponse(TypedDict, total=False):
    serviceArns: Optional[StringList]
    nextToken: Optional[String]


class ListTagsForResourceRequest(ServiceRequest):
    resourceArn: String


class ListTagsForResourceResponse(TypedDict, total=False):
    tags: Optional[Tags]


class ListTaskDefinitionFamiliesRequest(ServiceRequest):
    familyPrefix: Optional[String]
    status: Optional[TaskDefinitionFamilyStatus]
    nextToken: Optional[String]
    maxResults: Optional[BoxedInteger]


class ListTaskDefinitionFamiliesResponse(TypedDict, total=False):
    families: Optional[StringList]
    nextToken: Optional[String]


class ListTaskDefinitionsRequest(ServiceRequest):
    familyPrefix: Optional[String]
    status: Optional[TaskDefinitionStatus]
    sort: Optional[SortOrder]
    nextToken: Optional[String]
    maxResults: Optional[BoxedInteger]


class ListTaskDefinitionsResponse(TypedDict, total=False):
    taskDefinitionArns: Optional[StringList]
    nextToken: Optional[String]


class ListTasksRequest(ServiceRequest):
    cluster: Optional[String]
    containerInstance: Optional[String]
    family: Optional[String]
    nextToken: Optional[String]
    maxResults: Optional[BoxedInteger]
    startedBy: Optional[String]
    serviceName: Optional[String]
    desiredStatus: Optional[DesiredStatus]
    launchType: Optional[LaunchType]


class ListTasksResponse(TypedDict, total=False):
    taskArns: Optional[StringList]
    nextToken: Optional[String]


class ManagedAgentStateChange(TypedDict, total=False):
    """An object representing a change in state for a managed agent."""

    containerName: String
    managedAgentName: ManagedAgentName
    status: String
    reason: Optional[String]


ManagedAgentStateChanges = List[ManagedAgentStateChange]
PlatformDevice = TypedDict(
    "PlatformDevice",
    {
        "id": String,
        "type": PlatformDeviceType,
    },
    total=False,
)
PlatformDevices = List[PlatformDevice]


class PutAccountSettingDefaultRequest(ServiceRequest):
    name: SettingName
    value: String


class PutAccountSettingDefaultResponse(TypedDict, total=False):
    setting: Optional[Setting]


class PutAccountSettingRequest(ServiceRequest):
    name: SettingName
    value: String
    principalArn: Optional[String]


class PutAccountSettingResponse(TypedDict, total=False):
    setting: Optional[Setting]


class PutAttributesRequest(ServiceRequest):
    cluster: Optional[String]
    attributes: Attributes


class PutAttributesResponse(TypedDict, total=False):
    attributes: Optional[Attributes]


class PutClusterCapacityProvidersRequest(ServiceRequest):
    cluster: String
    capacityProviders: StringList
    defaultCapacityProviderStrategy: CapacityProviderStrategy


class PutClusterCapacityProvidersResponse(TypedDict, total=False):
    cluster: Optional[Cluster]


class RegisterContainerInstanceRequest(ServiceRequest):
    cluster: Optional[String]
    instanceIdentityDocument: Optional[String]
    instanceIdentityDocumentSignature: Optional[String]
    totalResources: Optional[Resources]
    versionInfo: Optional[VersionInfo]
    containerInstanceArn: Optional[String]
    attributes: Optional[Attributes]
    platformDevices: Optional[PlatformDevices]
    tags: Optional[Tags]


class RegisterContainerInstanceResponse(TypedDict, total=False):
    containerInstance: Optional[ContainerInstance]


class RegisterTaskDefinitionRequest(ServiceRequest):
    family: String
    taskRoleArn: Optional[String]
    executionRoleArn: Optional[String]
    networkMode: Optional[NetworkMode]
    containerDefinitions: ContainerDefinitions
    volumes: Optional[VolumeList]
    placementConstraints: Optional[TaskDefinitionPlacementConstraints]
    requiresCompatibilities: Optional[CompatibilityList]
    cpu: Optional[String]
    memory: Optional[String]
    tags: Optional[Tags]
    pidMode: Optional[PidMode]
    ipcMode: Optional[IpcMode]
    proxyConfiguration: Optional[ProxyConfiguration]
    inferenceAccelerators: Optional[InferenceAccelerators]
    ephemeralStorage: Optional[EphemeralStorage]
    runtimePlatform: Optional[RuntimePlatform]


class RegisterTaskDefinitionResponse(TypedDict, total=False):
    taskDefinition: Optional[TaskDefinition]
    tags: Optional[Tags]


class RunTaskRequest(ServiceRequest):
    capacityProviderStrategy: Optional[CapacityProviderStrategy]
    cluster: Optional[String]
    count: Optional[BoxedInteger]
    enableECSManagedTags: Optional[Boolean]
    enableExecuteCommand: Optional[Boolean]
    group: Optional[String]
    launchType: Optional[LaunchType]
    networkConfiguration: Optional[NetworkConfiguration]
    overrides: Optional[TaskOverride]
    placementConstraints: Optional[PlacementConstraints]
    placementStrategy: Optional[PlacementStrategies]
    platformVersion: Optional[String]
    propagateTags: Optional[PropagateTags]
    referenceId: Optional[String]
    startedBy: Optional[String]
    tags: Optional[Tags]
    taskDefinition: String


class RunTaskResponse(TypedDict, total=False):
    tasks: Optional[Tasks]
    failures: Optional[Failures]


class StartTaskRequest(ServiceRequest):
    cluster: Optional[String]
    containerInstances: StringList
    enableECSManagedTags: Optional[Boolean]
    enableExecuteCommand: Optional[Boolean]
    group: Optional[String]
    networkConfiguration: Optional[NetworkConfiguration]
    overrides: Optional[TaskOverride]
    propagateTags: Optional[PropagateTags]
    referenceId: Optional[String]
    startedBy: Optional[String]
    tags: Optional[Tags]
    taskDefinition: String


class StartTaskResponse(TypedDict, total=False):
    tasks: Optional[Tasks]
    failures: Optional[Failures]


class StopTaskRequest(ServiceRequest):
    cluster: Optional[String]
    task: String
    reason: Optional[String]


class StopTaskResponse(TypedDict, total=False):
    task: Optional[Task]


class SubmitAttachmentStateChangesRequest(ServiceRequest):
    cluster: Optional[String]
    attachments: AttachmentStateChanges


class SubmitAttachmentStateChangesResponse(TypedDict, total=False):
    acknowledgment: Optional[String]


class SubmitContainerStateChangeRequest(ServiceRequest):
    cluster: Optional[String]
    task: Optional[String]
    containerName: Optional[String]
    runtimeId: Optional[String]
    status: Optional[String]
    exitCode: Optional[BoxedInteger]
    reason: Optional[String]
    networkBindings: Optional[NetworkBindings]


class SubmitContainerStateChangeResponse(TypedDict, total=False):
    acknowledgment: Optional[String]


class SubmitTaskStateChangeRequest(ServiceRequest):
    cluster: Optional[String]
    task: Optional[String]
    status: Optional[String]
    reason: Optional[String]
    containers: Optional[ContainerStateChanges]
    attachments: Optional[AttachmentStateChanges]
    managedAgents: Optional[ManagedAgentStateChanges]
    pullStartedAt: Optional[Timestamp]
    pullStoppedAt: Optional[Timestamp]
    executionStoppedAt: Optional[Timestamp]


class SubmitTaskStateChangeResponse(TypedDict, total=False):
    acknowledgment: Optional[String]


TagKeys = List[TagKey]


class TagResourceRequest(ServiceRequest):
    resourceArn: String
    tags: Tags


class TagResourceResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    resourceArn: String
    tagKeys: TagKeys


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateCapacityProviderRequest(ServiceRequest):
    name: String
    autoScalingGroupProvider: AutoScalingGroupProviderUpdate


class UpdateCapacityProviderResponse(TypedDict, total=False):
    capacityProvider: Optional[CapacityProvider]


class UpdateClusterRequest(ServiceRequest):
    cluster: String
    settings: Optional[ClusterSettings]
    configuration: Optional[ClusterConfiguration]


class UpdateClusterResponse(TypedDict, total=False):
    cluster: Optional[Cluster]


class UpdateClusterSettingsRequest(ServiceRequest):
    cluster: String
    settings: ClusterSettings


class UpdateClusterSettingsResponse(TypedDict, total=False):
    cluster: Optional[Cluster]


class UpdateContainerAgentRequest(ServiceRequest):
    cluster: Optional[String]
    containerInstance: String


class UpdateContainerAgentResponse(TypedDict, total=False):
    containerInstance: Optional[ContainerInstance]


class UpdateContainerInstancesStateRequest(ServiceRequest):
    cluster: Optional[String]
    containerInstances: StringList
    status: ContainerInstanceStatus


class UpdateContainerInstancesStateResponse(TypedDict, total=False):
    containerInstances: Optional[ContainerInstances]
    failures: Optional[Failures]


class UpdateServicePrimaryTaskSetRequest(ServiceRequest):
    cluster: String
    service: String
    primaryTaskSet: String


class UpdateServicePrimaryTaskSetResponse(TypedDict, total=False):
    taskSet: Optional[TaskSet]


class UpdateServiceRequest(ServiceRequest):
    cluster: Optional[String]
    service: String
    desiredCount: Optional[BoxedInteger]
    taskDefinition: Optional[String]
    capacityProviderStrategy: Optional[CapacityProviderStrategy]
    deploymentConfiguration: Optional[DeploymentConfiguration]
    networkConfiguration: Optional[NetworkConfiguration]
    placementConstraints: Optional[PlacementConstraints]
    placementStrategy: Optional[PlacementStrategies]
    platformVersion: Optional[String]
    forceNewDeployment: Optional[Boolean]
    healthCheckGracePeriodSeconds: Optional[BoxedInteger]
    enableExecuteCommand: Optional[BoxedBoolean]
    enableECSManagedTags: Optional[BoxedBoolean]
    loadBalancers: Optional[LoadBalancers]
    propagateTags: Optional[PropagateTags]
    serviceRegistries: Optional[ServiceRegistries]


class UpdateServiceResponse(TypedDict, total=False):
    service: Optional[Service]


class UpdateTaskSetRequest(ServiceRequest):
    cluster: String
    service: String
    taskSet: String
    scale: Scale


class UpdateTaskSetResponse(TypedDict, total=False):
    taskSet: Optional[TaskSet]


class EcsApi:

    service = "ecs"
    version = "2014-11-13"

    @handler("CreateCapacityProvider")
    def create_capacity_provider(
        self,
        context: RequestContext,
        name: String,
        auto_scaling_group_provider: AutoScalingGroupProvider,
        tags: Tags = None,
    ) -> CreateCapacityProviderResponse:
        """Creates a new capacity provider. Capacity providers are associated with
        an Amazon ECS cluster and are used in capacity provider strategies to
        facilitate cluster auto scaling.

        Only capacity providers that use an Auto Scaling group can be created.
        Amazon ECS tasks on Fargate use the ``FARGATE`` and ``FARGATE_SPOT``
        capacity providers. These providers are available to all accounts in the
        Amazon Web Services Regions that Fargate supports.

        :param name: The name of the capacity provider.
        :param auto_scaling_group_provider: The details of the Auto Scaling group for the capacity provider.
        :param tags: The metadata that you apply to the capacity provider to categorize and
        organize them more conveniently.
        :returns: CreateCapacityProviderResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises LimitExceededException:
        :raises UpdateInProgressException:
        """
        raise NotImplementedError

    @handler("CreateCluster")
    def create_cluster(
        self,
        context: RequestContext,
        cluster_name: String = None,
        tags: Tags = None,
        settings: ClusterSettings = None,
        configuration: ClusterConfiguration = None,
        capacity_providers: StringList = None,
        default_capacity_provider_strategy: CapacityProviderStrategy = None,
    ) -> CreateClusterResponse:
        """Creates a new Amazon ECS cluster. By default, your account receives a
        ``default`` cluster when you launch your first container instance.
        However, you can create your own cluster with a unique name with the
        ``CreateCluster`` action.

        When you call the CreateCluster API operation, Amazon ECS attempts to
        create the Amazon ECS service-linked role for your account. This is so
        that it can manage required resources in other Amazon Web Services
        services on your behalf. However, if the IAM user that makes the call
        doesn't have permissions to create the service-linked role, it isn't
        created. For more information, see `Using Service-Linked Roles for
        Amazon
        ECS <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using-service-linked-roles.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param cluster_name: The name of your cluster.
        :param tags: The metadata that you apply to the cluster to help you categorize and
        organize them.
        :param settings: The setting to use when creating a cluster.
        :param configuration: The ``execute`` command configuration for the cluster.
        :param capacity_providers: The short name of one or more capacity providers to associate with the
        cluster.
        :param default_capacity_provider_strategy: The capacity provider strategy to set as the default for the cluster.
        :returns: CreateClusterResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("CreateService")
    def create_service(
        self,
        context: RequestContext,
        service_name: String,
        cluster: String = None,
        task_definition: String = None,
        load_balancers: LoadBalancers = None,
        service_registries: ServiceRegistries = None,
        desired_count: BoxedInteger = None,
        client_token: String = None,
        launch_type: LaunchType = None,
        capacity_provider_strategy: CapacityProviderStrategy = None,
        platform_version: String = None,
        role: String = None,
        deployment_configuration: DeploymentConfiguration = None,
        placement_constraints: PlacementConstraints = None,
        placement_strategy: PlacementStrategies = None,
        network_configuration: NetworkConfiguration = None,
        health_check_grace_period_seconds: BoxedInteger = None,
        scheduling_strategy: SchedulingStrategy = None,
        deployment_controller: DeploymentController = None,
        tags: Tags = None,
        enable_ecs_managed_tags: Boolean = None,
        propagate_tags: PropagateTags = None,
        enable_execute_command: Boolean = None,
    ) -> CreateServiceResponse:
        """Runs and maintains your desired number of tasks from a specified task
        definition. If the number of tasks running in a service drops below the
        ``desiredCount``, Amazon ECS runs another copy of the task in the
        specified cluster. To update an existing service, see the UpdateService
        action.

        In addition to maintaining the desired count of tasks in your service,
        you can optionally run your service behind one or more load balancers.
        The load balancers distribute traffic across the tasks that are
        associated with the service. For more information, see `Service Load
        Balancing <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-load-balancing.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        Tasks for services that don't use a load balancer are considered healthy
        if they're in the ``RUNNING`` state. Tasks for services that use a load
        balancer are considered healthy if they're in the ``RUNNING`` state and
        are reported as healthy by the load balancer.

        There are two service scheduler strategies available:

        -  ``REPLICA`` - The replica scheduling strategy places and maintains
           your desired number of tasks across your cluster. By default, the
           service scheduler spreads tasks across Availability Zones. You can
           use task placement strategies and constraints to customize task
           placement decisions. For more information, see `Service Scheduler
           Concepts <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html>`__
           in the *Amazon Elastic Container Service Developer Guide*.

        -  ``DAEMON`` - The daemon scheduling strategy deploys exactly one task
           on each active container instance that meets all of the task
           placement constraints that you specify in your cluster. The service
           scheduler also evaluates the task placement constraints for running
           tasks. It also stops tasks that don't meet the placement constraints.
           When using this strategy, you don't need to specify a desired number
           of tasks, a task placement strategy, or use Service Auto Scaling
           policies. For more information, see `Service Scheduler
           Concepts <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html>`__
           in the *Amazon Elastic Container Service Developer Guide*.

        You can optionally specify a deployment configuration for your service.
        The deployment is initiated by changing properties. For example, the
        deployment might be initiated by the task definition or by your desired
        count of a service. This is done with an UpdateService operation. The
        default value for a replica service for ``minimumHealthyPercent`` is
        100%. The default value for a daemon service for
        ``minimumHealthyPercent`` is 0%.

        If a service uses the ``ECS`` deployment controller, the minimum healthy
        percent represents a lower limit on the number of tasks in a service
        that must remain in the ``RUNNING`` state during a deployment.
        Specifically, it represents it as a percentage of your desired number of
        tasks (rounded up to the nearest integer). This happens when any of your
        container instances are in the ``DRAINING`` state if the service
        contains tasks using the EC2 launch type. Using this parameter, you can
        deploy without using additional cluster capacity. For example, if you
        set your service to have desired number of four tasks and a minimum
        healthy percent of 50%, the scheduler might stop two existing tasks to
        free up cluster capacity before starting two new tasks. If they're in
        the ``RUNNING`` state, tasks for services that don't use a load balancer
        are considered healthy . If they're in the ``RUNNING`` state and
        reported as healthy by the load balancer, tasks for services that *do*
        use a load balancer are considered healthy . The default value for
        minimum healthy percent is 100%.

        If a service uses the ``ECS`` deployment controller, the **maximum
        percent** parameter represents an upper limit on the number of tasks in
        a service that are allowed in the ``RUNNING`` or ``PENDING`` state
        during a deployment. Specifically, it represents it as a percentage of
        the desired number of tasks (rounded down to the nearest integer). This
        happens when any of your container instances are in the ``DRAINING``
        state if the service contains tasks using the EC2 launch type. Using
        this parameter, you can define the deployment batch size. For example,
        if your service has a desired number of four tasks and a maximum percent
        value of 200%, the scheduler may start four new tasks before stopping
        the four older tasks (provided that the cluster resources required to do
        this are available). The default value for maximum percent is 200%.

        If a service uses either the ``CODE_DEPLOY`` or ``EXTERNAL`` deployment
        controller types and tasks that use the EC2 launch type, the **minimum
        healthy percent** and **maximum percent** values are used only to define
        the lower and upper limit on the number of the tasks in the service that
        remain in the ``RUNNING`` state. This is while the container instances
        are in the ``DRAINING`` state. If the tasks in the service use the
        Fargate launch type, the minimum healthy percent and maximum percent
        values aren't used. This is the case even if they're currently visible
        when describing your service.

        When creating a service that uses the ``EXTERNAL`` deployment
        controller, you can specify only parameters that aren't controlled at
        the task set level. The only required parameter is the service name. You
        control your services using the CreateTaskSet operation. For more
        information, see `Amazon ECS Deployment
        Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        When the service scheduler launches new tasks, it determines task
        placement in your cluster using the following logic:

        -  Determine which of the container instances in your cluster can
           support the task definition of your service. For example, they have
           the required CPU, memory, ports, and container instance attributes.

        -  By default, the service scheduler attempts to balance tasks across
           Availability Zones in this manner. This is the case even if you can
           choose a different placement strategy with the ``placementStrategy``
           parameter.

           -  Sort the valid container instances, giving priority to instances
              that have the fewest number of running tasks for this service in
              their respective Availability Zone. For example, if zone A has one
              running service task and zones B and C each have zero, valid
              container instances in either zone B or C are considered optimal
              for placement.

           -  Place the new service task on a valid container instance in an
              optimal Availability Zone based on the previous steps, favoring
              container instances with the fewest number of running tasks for
              this service.

        :param service_name: The name of your service.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        you run your service on.
        :param task_definition: The ``family`` and ``revision`` (``family:revision``) or full ARN of the
        task definition to run in your service.
        :param load_balancers: A load balancer object representing the load balancers to use with your
        service.
        :param service_registries: The details of the service discovery registry to associate with this
        service.
        :param desired_count: The number of instantiations of the specified task definition to place
        and keep running on your cluster.
        :param client_token: An identifier that you provide to ensure the idempotency of the request.
        :param launch_type: The infrastructure that you run your service on.
        :param capacity_provider_strategy: The capacity provider strategy to use for the service.
        :param platform_version: The platform version that your tasks in the service are running on.
        :param role: The name or full Amazon Resource Name (ARN) of the IAM role that allows
        Amazon ECS to make calls to your load balancer on your behalf.
        :param deployment_configuration: Optional deployment parameters that control how many tasks run during
        the deployment and the ordering of stopping and starting tasks.
        :param placement_constraints: An array of placement constraint objects to use for tasks in your
        service.
        :param placement_strategy: The placement strategy objects to use for tasks in your service.
        :param network_configuration: The network configuration for the service.
        :param health_check_grace_period_seconds: The period of time, in seconds, that the Amazon ECS service scheduler
        ignores unhealthy Elastic Load Balancing target health checks after a
        task has first started.
        :param scheduling_strategy: The scheduling strategy to use for the service.
        :param deployment_controller: The deployment controller to use for the service.
        :param tags: The metadata that you apply to the service to help you categorize and
        organize them.
        :param enable_ecs_managed_tags: Specifies whether to turn on Amazon ECS managed tags for the tasks
        within the service.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition to the
        task.
        :param enable_execute_command: Determines whether the execute command functionality is enabled for the
        service.
        :returns: CreateServiceResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises UnsupportedFeatureException:
        :raises PlatformUnknownException:
        :raises PlatformTaskDefinitionIncompatibilityException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("CreateTaskSet")
    def create_task_set(
        self,
        context: RequestContext,
        service: String,
        cluster: String,
        task_definition: String,
        external_id: String = None,
        network_configuration: NetworkConfiguration = None,
        load_balancers: LoadBalancers = None,
        service_registries: ServiceRegistries = None,
        launch_type: LaunchType = None,
        capacity_provider_strategy: CapacityProviderStrategy = None,
        platform_version: String = None,
        scale: Scale = None,
        client_token: String = None,
        tags: Tags = None,
    ) -> CreateTaskSetResponse:
        """Create a task set in the specified cluster and service. This is used
        when a service uses the ``EXTERNAL`` deployment controller type. For
        more information, see `Amazon ECS Deployment
        Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param service: The short name or full Amazon Resource Name (ARN) of the service to
        create the task set in.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the service to create the task set in.
        :param task_definition: The task definition for the tasks in the task set to use.
        :param external_id: An optional non-unique tag that identifies this task set in external
        systems.
        :param network_configuration: An object representing the network configuration for a task set.
        :param load_balancers: A load balancer object representing the load balancer to use with the
        task set.
        :param service_registries: The details of the service discovery registries to assign to this task
        set.
        :param launch_type: The launch type that new tasks in the task set uses.
        :param capacity_provider_strategy: The capacity provider strategy to use for the task set.
        :param platform_version: The platform version that the tasks in the task set uses.
        :param scale: A floating-point percentage of the desired number of tasks to place and
        keep running in the task set.
        :param client_token: The identifier that you provide to ensure the idempotency of the
        request.
        :param tags: The metadata that you apply to the task set to help you categorize and
        organize them.
        :returns: CreateTaskSetResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises UnsupportedFeatureException:
        :raises PlatformUnknownException:
        :raises PlatformTaskDefinitionIncompatibilityException:
        :raises AccessDeniedException:
        :raises ServiceNotFoundException:
        :raises ServiceNotActiveException:
        """
        raise NotImplementedError

    @handler("DeleteAccountSetting")
    def delete_account_setting(
        self, context: RequestContext, name: SettingName, principal_arn: String = None
    ) -> DeleteAccountSettingResponse:
        """Disables an account setting for a specified IAM user, IAM role, or the
        root user for an account.

        :param name: The resource name to disable the account setting for.
        :param principal_arn: The Amazon Resource Name (ARN) of the principal.
        :returns: DeleteAccountSettingResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("DeleteAttributes")
    def delete_attributes(
        self, context: RequestContext, attributes: Attributes, cluster: String = None
    ) -> DeleteAttributesResponse:
        """Deletes one or more custom attributes from an Amazon ECS resource.

        :param attributes: The attributes to delete from your resource.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        contains the resource to delete attributes.
        :returns: DeleteAttributesResponse
        :raises ClusterNotFoundException:
        :raises TargetNotFoundException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("DeleteCapacityProvider")
    def delete_capacity_provider(
        self, context: RequestContext, capacity_provider: String
    ) -> DeleteCapacityProviderResponse:
        """Deletes the specified capacity provider.

        The ``FARGATE`` and ``FARGATE_SPOT`` capacity providers are reserved and
        can't be deleted. You can disassociate them from a cluster using either
        the PutClusterCapacityProviders API or by deleting the cluster.

        Prior to a capacity provider being deleted, the capacity provider must
        be removed from the capacity provider strategy from all services. The
        UpdateService API can be used to remove a capacity provider from a
        service's capacity provider strategy. When updating a service, the
        ``forceNewDeployment`` option can be used to ensure that any tasks using
        the Amazon EC2 instance capacity provided by the capacity provider are
        transitioned to use the capacity from the remaining capacity providers.
        Only capacity providers that aren't associated with a cluster can be
        deleted. To remove a capacity provider from a cluster, you can either
        use PutClusterCapacityProviders or delete the cluster.

        :param capacity_provider: The short name or full Amazon Resource Name (ARN) of the capacity
        provider to delete.
        :returns: DeleteCapacityProviderResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("DeleteCluster")
    def delete_cluster(self, context: RequestContext, cluster: String) -> DeleteClusterResponse:
        """Deletes the specified cluster. The cluster transitions to the
        ``INACTIVE`` state. Clusters with an ``INACTIVE`` status might remain
        discoverable in your account for a period of time. However, this
        behavior is subject to change in the future. We don't recommend that you
        rely on ``INACTIVE`` clusters persisting.

        You must deregister all container instances from this cluster before you
        may delete it. You can list the container instances in a cluster with
        ListContainerInstances and deregister them with
        DeregisterContainerInstance.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster to
        delete.
        :returns: DeleteClusterResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises ClusterContainsContainerInstancesException:
        :raises ClusterContainsServicesException:
        :raises ClusterContainsTasksException:
        :raises UpdateInProgressException:
        """
        raise NotImplementedError

    @handler("DeleteService")
    def delete_service(
        self,
        context: RequestContext,
        service: String,
        cluster: String = None,
        force: BoxedBoolean = None,
    ) -> DeleteServiceResponse:
        """Deletes a specified service within a cluster. You can delete a service
        if you have no running tasks in it and the desired task count is zero.
        If the service is actively maintaining tasks, you can't delete it, and
        you must update the service to a desired task count of zero. For more
        information, see UpdateService.

        When you delete a service, if there are still running tasks that require
        cleanup, the service status moves from ``ACTIVE`` to ``DRAINING``, and
        the service is no longer visible in the console or in the ListServices
        API operation. After all tasks have transitioned to either ``STOPPING``
        or ``STOPPED`` status, the service status moves from ``DRAINING`` to
        ``INACTIVE``. Services in the ``DRAINING`` or ``INACTIVE`` status can
        still be viewed with the DescribeServices API operation. However, in the
        future, ``INACTIVE`` services may be cleaned up and purged from Amazon
        ECS record keeping, and DescribeServices calls on those services return
        a ``ServiceNotFoundException`` error.

        If you attempt to create a new service with the same name as an existing
        service in either ``ACTIVE`` or ``DRAINING`` status, you receive an
        error.

        :param service: The name of the service to delete.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the service to delete.
        :param force: If ``true``, allows you to delete a service even if it wasn't scaled
        down to zero tasks.
        :returns: DeleteServiceResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises ServiceNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteTaskSet")
    def delete_task_set(
        self,
        context: RequestContext,
        cluster: String,
        service: String,
        task_set: String,
        force: BoxedBoolean = None,
    ) -> DeleteTaskSetResponse:
        """Deletes a specified task set within a service. This is used when a
        service uses the ``EXTERNAL`` deployment controller type. For more
        information, see `Amazon ECS Deployment
        Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the service that the task set found in to delete.
        :param service: The short name or full Amazon Resource Name (ARN) of the service that
        hosts the task set to delete.
        :param task_set: The task set ID or full Amazon Resource Name (ARN) of the task set to
        delete.
        :param force: If ``true``, you can delete a task set even if it hasn't been scaled
        down to zero.
        :returns: DeleteTaskSetResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises UnsupportedFeatureException:
        :raises AccessDeniedException:
        :raises ServiceNotFoundException:
        :raises ServiceNotActiveException:
        :raises TaskSetNotFoundException:
        """
        raise NotImplementedError

    @handler("DeregisterContainerInstance")
    def deregister_container_instance(
        self,
        context: RequestContext,
        container_instance: String,
        cluster: String = None,
        force: BoxedBoolean = None,
    ) -> DeregisterContainerInstanceResponse:
        """Deregisters an Amazon ECS container instance from the specified cluster.
        This instance is no longer available to run tasks.

        If you intend to use the container instance for some other purpose after
        deregistration, we recommend that you stop all of the tasks running on
        the container instance before deregistration. That prevents any orphaned
        tasks from consuming resources.

        Deregistering a container instance removes the instance from a cluster,
        but it doesn't terminate the EC2 instance. If you are finished using the
        instance, be sure to terminate it in the Amazon EC2 console to stop
        billing.

        If you terminate a running container instance, Amazon ECS automatically
        deregisters the instance from your cluster (stopped container instances
        or instances with disconnected agents aren't automatically deregistered
        when terminated).

        :param container_instance: The container instance ID or full ARN of the container instance to
        deregister.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the container instance to deregister.
        :param force: Forces the container instance to be deregistered.
        :returns: DeregisterContainerInstanceResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        """
        raise NotImplementedError

    @handler("DeregisterTaskDefinition")
    def deregister_task_definition(
        self, context: RequestContext, task_definition: String
    ) -> DeregisterTaskDefinitionResponse:
        """Deregisters the specified task definition by family and revision. Upon
        deregistration, the task definition is marked as ``INACTIVE``. Existing
        tasks and services that reference an ``INACTIVE`` task definition
        continue to run without disruption. Existing services that reference an
        ``INACTIVE`` task definition can still scale up or down by modifying the
        service's desired count.

        You can't use an ``INACTIVE`` task definition to run new tasks or create
        new services, and you can't update an existing service to reference an
        ``INACTIVE`` task definition. However, there may be up to a 10-minute
        window following deregistration where these restrictions have not yet
        taken effect.

        At this time, ``INACTIVE`` task definitions remain discoverable in your
        account indefinitely. However, this behavior is subject to change in the
        future. We don't recommend that you rely on ``INACTIVE`` task
        definitions persisting beyond the lifecycle of any associated tasks and
        services.

        :param task_definition: The ``family`` and ``revision`` (``family:revision``) or full Amazon
        Resource Name (ARN) of the task definition to deregister.
        :returns: DeregisterTaskDefinitionResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("DescribeCapacityProviders")
    def describe_capacity_providers(
        self,
        context: RequestContext,
        capacity_providers: StringList = None,
        include: CapacityProviderFieldList = None,
        max_results: BoxedInteger = None,
        next_token: String = None,
    ) -> DescribeCapacityProvidersResponse:
        """Describes one or more of your capacity providers.

        :param capacity_providers: The short name or full Amazon Resource Name (ARN) of one or more
        capacity providers.
        :param include: Specifies whether or not you want to see the resource tags for the
        capacity provider.
        :param max_results: The maximum number of account setting results returned by
        ``DescribeCapacityProviders`` in paginated output.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``DescribeCapacityProviders`` request where ``maxResults`` was used and
        the results exceeded the value of that parameter.
        :returns: DescribeCapacityProvidersResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("DescribeClusters")
    def describe_clusters(
        self, context: RequestContext, clusters: StringList = None, include: ClusterFieldList = None
    ) -> DescribeClustersResponse:
        """Describes one or more of your clusters.

        :param clusters: A list of up to 100 cluster names or full cluster Amazon Resource Name
        (ARN) entries.
        :param include: Determines whether to include additional information about the clusters
        in the response.
        :returns: DescribeClustersResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("DescribeContainerInstances")
    def describe_container_instances(
        self,
        context: RequestContext,
        container_instances: StringList,
        cluster: String = None,
        include: ContainerInstanceFieldList = None,
    ) -> DescribeContainerInstancesResponse:
        """Describes one or more container instances. Returns metadata about each
        container instance requested.

        :param container_instances: A list of up to 100 container instance IDs or full Amazon Resource Name
        (ARN) entries.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the container instances to describe.
        :param include: Specifies whether you want to see the resource tags for the container
        instance.
        :returns: DescribeContainerInstancesResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeServices")
    def describe_services(
        self,
        context: RequestContext,
        services: StringList,
        cluster: String = None,
        include: ServiceFieldList = None,
    ) -> DescribeServicesResponse:
        """Describes the specified services running in your cluster.

        :param services: A list of services to describe.
        :param cluster: The short name or full Amazon Resource Name (ARN)the cluster that hosts
        the service to describe.
        :param include: Determines whether you want to see the resource tags for the service.
        :returns: DescribeServicesResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeTaskDefinition")
    def describe_task_definition(
        self,
        context: RequestContext,
        task_definition: String,
        include: TaskDefinitionFieldList = None,
    ) -> DescribeTaskDefinitionResponse:
        """Describes a task definition. You can specify a ``family`` and
        ``revision`` to find information about a specific task definition, or
        you can simply specify the family to find the latest ``ACTIVE`` revision
        in that family.

        You can only describe ``INACTIVE`` task definitions while an active task
        or service references them.

        :param task_definition: The ``family`` for the latest ``ACTIVE`` revision, ``family`` and
        ``revision`` (``family:revision``) for a specific revision in the
        family, or full Amazon Resource Name (ARN) of the task definition to
        describe.
        :param include: Determines whether to see the resource tags for the task definition.
        :returns: DescribeTaskDefinitionResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("DescribeTaskSets")
    def describe_task_sets(
        self,
        context: RequestContext,
        cluster: String,
        service: String,
        task_sets: StringList = None,
        include: TaskSetFieldList = None,
    ) -> DescribeTaskSetsResponse:
        """Describes the task sets in the specified cluster and service. This is
        used when a service uses the ``EXTERNAL`` deployment controller type.
        For more information, see `Amazon ECS Deployment
        Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the service that the task sets exist in.
        :param service: The short name or full Amazon Resource Name (ARN) of the service that
        the task sets exist in.
        :param task_sets: The ID or full Amazon Resource Name (ARN) of task sets to describe.
        :param include: Specifies whether to see the resource tags for the task set.
        :returns: DescribeTaskSetsResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises UnsupportedFeatureException:
        :raises AccessDeniedException:
        :raises ServiceNotFoundException:
        :raises ServiceNotActiveException:
        """
        raise NotImplementedError

    @handler("DescribeTasks")
    def describe_tasks(
        self,
        context: RequestContext,
        tasks: StringList,
        cluster: String = None,
        include: TaskFieldList = None,
    ) -> DescribeTasksResponse:
        """Describes a specified task or tasks.

        :param tasks: A list of up to 100 task IDs or full ARN entries.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the task or tasks to describe.
        :param include: Specifies whether you want to see the resource tags for the task.
        :returns: DescribeTasksResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        """
        raise NotImplementedError

    @handler("DiscoverPollEndpoint")
    def discover_poll_endpoint(
        self, context: RequestContext, container_instance: String = None, cluster: String = None
    ) -> DiscoverPollEndpointResponse:
        """This action is only used by the Amazon ECS agent, and it is not intended
        for use outside of the agent.

        Returns an endpoint for the Amazon ECS agent to poll for updates.

        :param container_instance: The container instance ID or full ARN of the container instance.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        the container instance belongs to.
        :returns: DiscoverPollEndpointResponse
        :raises ServerException:
        :raises ClientException:
        """
        raise NotImplementedError

    @handler("ExecuteCommand")
    def execute_command(
        self,
        context: RequestContext,
        command: String,
        interactive: Boolean,
        task: String,
        cluster: String = None,
        container: String = None,
    ) -> ExecuteCommandResponse:
        """Runs a command remotely on a container within a task.

        :param command: The command to run on the container.
        :param interactive: Use this flag to run your command in interactive mode.
        :param task: The Amazon Resource Name (ARN) or ID of the task the container is part
        of.
        :param cluster: The Amazon Resource Name (ARN) or short name of the cluster the task is
        running in.
        :param container: The name of the container to execute the command on.
        :returns: ExecuteCommandResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises AccessDeniedException:
        :raises ClusterNotFoundException:
        :raises TargetNotConnectedException:
        """
        raise NotImplementedError

    @handler("ListAccountSettings")
    def list_account_settings(
        self,
        context: RequestContext,
        name: SettingName = None,
        value: String = None,
        principal_arn: String = None,
        effective_settings: Boolean = None,
        next_token: String = None,
        max_results: Integer = None,
    ) -> ListAccountSettingsResponse:
        """Lists the account settings for a specified principal.

        :param name: The name of the account setting you want to list the settings for.
        :param value: The value of the account settings to filter results with.
        :param principal_arn: The ARN of the principal, which can be an IAM user, IAM role, or the
        root user.
        :param effective_settings: Determines whether to return the effective settings.
        :param next_token: The ``nextToken`` value returned from a ``ListAccountSettings`` request
        indicating that more results are available to fulfill the request and
        further calls will be needed.
        :param max_results: The maximum number of account setting results returned by
        ``ListAccountSettings`` in paginated output.
        :returns: ListAccountSettingsResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("ListAttributes")
    def list_attributes(
        self,
        context: RequestContext,
        target_type: TargetType,
        cluster: String = None,
        attribute_name: String = None,
        attribute_value: String = None,
        next_token: String = None,
        max_results: BoxedInteger = None,
    ) -> ListAttributesResponse:
        """Lists the attributes for Amazon ECS resources within a specified target
        type and cluster. When you specify a target type and cluster,
        ``ListAttributes`` returns a list of attribute objects, one for each
        attribute on each resource. You can filter the list of results to a
        single attribute name to only return results that have that name. You
        can also filter the results by attribute name and value. You can do
        this, for example, to see which container instances in a cluster are
        running a Linux AMI (``ecs.os-type=linux``).

        :param target_type: The type of the target to list attributes with.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster to list
        attributes.
        :param attribute_name: The name of the attribute to filter the results with.
        :param attribute_value: The value of the attribute to filter results with.
        :param next_token: The ``nextToken`` value returned from a ``ListAttributes`` request
        indicating that more results are available to fulfill the request and
        further calls are needed.
        :param max_results: The maximum number of cluster results that ``ListAttributes`` returned
        in paginated output.
        :returns: ListAttributesResponse
        :raises ClusterNotFoundException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("ListClusters")
    def list_clusters(
        self, context: RequestContext, next_token: String = None, max_results: BoxedInteger = None
    ) -> ListClustersResponse:
        """Returns a list of existing clusters.

        :param next_token: The ``nextToken`` value returned from a ``ListClusters`` request
        indicating that more results are available to fulfill the request and
        further calls are needed.
        :param max_results: The maximum number of cluster results that ``ListClusters`` returned in
        paginated output.
        :returns: ListClustersResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("ListContainerInstances")
    def list_container_instances(
        self,
        context: RequestContext,
        cluster: String = None,
        filter: String = None,
        next_token: String = None,
        max_results: BoxedInteger = None,
        status: ContainerInstanceStatus = None,
    ) -> ListContainerInstancesResponse:
        """Returns a list of container instances in a specified cluster. You can
        filter the results of a ``ListContainerInstances`` operation with
        cluster query language statements inside the ``filter`` parameter. For
        more information, see `Cluster Query
        Language <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cluster-query-language.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the container instances to list.
        :param filter: You can filter the results of a ``ListContainerInstances`` operation
        with cluster query language statements.
        :param next_token: The ``nextToken`` value returned from a ``ListContainerInstances``
        request indicating that more results are available to fulfill the
        request and further calls are needed.
        :param max_results: The maximum number of container instance results that
        ``ListContainerInstances`` returned in paginated output.
        :param status: Filters the container instances by status.
        :returns: ListContainerInstancesResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        """
        raise NotImplementedError

    @handler("ListServices")
    def list_services(
        self,
        context: RequestContext,
        cluster: String = None,
        next_token: String = None,
        max_results: BoxedInteger = None,
        launch_type: LaunchType = None,
        scheduling_strategy: SchedulingStrategy = None,
    ) -> ListServicesResponse:
        """Returns a list of services. You can filter the results by cluster,
        launch type, and scheduling strategy.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster to use
        when filtering the ``ListServices`` results.
        :param next_token: The ``nextToken`` value returned from a ``ListServices`` request
        indicating that more results are available to fulfill the request and
        further calls will be needed.
        :param max_results: The maximum number of service results that ``ListServices`` returned in
        paginated output.
        :param launch_type: The launch type to use when filtering the ``ListServices`` results.
        :param scheduling_strategy: The scheduling strategy to use when filtering the ``ListServices``
        results.
        :returns: ListServicesResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: String
    ) -> ListTagsForResourceResponse:
        """List the tags for an Amazon ECS resource.

        :param resource_arn: The Amazon Resource Name (ARN) that identifies the resource to list the
        tags for.
        :returns: ListTagsForResourceResponse
        :raises ServerException:
        :raises ClientException:
        :raises ClusterNotFoundException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("ListTaskDefinitionFamilies")
    def list_task_definition_families(
        self,
        context: RequestContext,
        family_prefix: String = None,
        status: TaskDefinitionFamilyStatus = None,
        next_token: String = None,
        max_results: BoxedInteger = None,
    ) -> ListTaskDefinitionFamiliesResponse:
        """Returns a list of task definition families that are registered to your
        account. This list includes task definition families that no longer have
        any ``ACTIVE`` task definition revisions.

        You can filter out task definition families that don't contain any
        ``ACTIVE`` task definition revisions by setting the ``status`` parameter
        to ``ACTIVE``. You can also filter the results with the ``familyPrefix``
        parameter.

        :param family_prefix: The ``familyPrefix`` is a string that's used to filter the results of
        ``ListTaskDefinitionFamilies``.
        :param status: The task definition family status to filter the
        ``ListTaskDefinitionFamilies`` results with.
        :param next_token: The ``nextToken`` value returned from a ``ListTaskDefinitionFamilies``
        request indicating that more results are available to fulfill the
        request and further calls will be needed.
        :param max_results: The maximum number of task definition family results that
        ``ListTaskDefinitionFamilies`` returned in paginated output.
        :returns: ListTaskDefinitionFamiliesResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("ListTaskDefinitions")
    def list_task_definitions(
        self,
        context: RequestContext,
        family_prefix: String = None,
        status: TaskDefinitionStatus = None,
        sort: SortOrder = None,
        next_token: String = None,
        max_results: BoxedInteger = None,
    ) -> ListTaskDefinitionsResponse:
        """Returns a list of task definitions that are registered to your account.
        You can filter the results by family name with the ``familyPrefix``
        parameter or by status with the ``status`` parameter.

        :param family_prefix: The full family name to filter the ``ListTaskDefinitions`` results with.
        :param status: The task definition status to filter the ``ListTaskDefinitions`` results
        with.
        :param sort: The order to sort the results in.
        :param next_token: The ``nextToken`` value returned from a ``ListTaskDefinitions`` request
        indicating that more results are available to fulfill the request and
        further calls will be needed.
        :param max_results: The maximum number of task definition results that
        ``ListTaskDefinitions`` returned in paginated output.
        :returns: ListTaskDefinitionsResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("ListTasks")
    def list_tasks(
        self,
        context: RequestContext,
        cluster: String = None,
        container_instance: String = None,
        family: String = None,
        next_token: String = None,
        max_results: BoxedInteger = None,
        started_by: String = None,
        service_name: String = None,
        desired_status: DesiredStatus = None,
        launch_type: LaunchType = None,
    ) -> ListTasksResponse:
        """Returns a list of tasks. You can filter the results by cluster, task
        definition family, container instance, launch type, what IAM principal
        started the task, or by the desired status of the task.

        Recently stopped tasks might appear in the returned results. Currently,
        stopped tasks appear in the returned results for at least one hour.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster to use
        when filtering the ``ListTasks`` results.
        :param container_instance: The container instance ID or full ARN of the container instance to use
        when filtering the ``ListTasks`` results.
        :param family: The name of the task definition family to use when filtering the
        ``ListTasks`` results.
        :param next_token: The ``nextToken`` value returned from a ``ListTasks`` request indicating
        that more results are available to fulfill the request and further calls
        will be needed.
        :param max_results: The maximum number of task results that ``ListTasks`` returned in
        paginated output.
        :param started_by: The ``startedBy`` value to filter the task results with.
        :param service_name: The name of the service to use when filtering the ``ListTasks`` results.
        :param desired_status: The task desired status to use when filtering the ``ListTasks`` results.
        :param launch_type: The launch type to use when filtering the ``ListTasks`` results.
        :returns: ListTasksResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises ServiceNotFoundException:
        """
        raise NotImplementedError

    @handler("PutAccountSetting")
    def put_account_setting(
        self,
        context: RequestContext,
        name: SettingName,
        value: String,
        principal_arn: String = None,
    ) -> PutAccountSettingResponse:
        """Modifies an account setting. Account settings are set on a per-Region
        basis.

        If you change the account setting for the root user, the default
        settings for all of the IAM users and roles that no individual account
        setting was specified are reset for. For more information, see `Account
        Settings <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-account-settings.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        When ``serviceLongArnFormat``, ``taskLongArnFormat``, or
        ``containerInstanceLongArnFormat`` are specified, the Amazon Resource
        Name (ARN) and resource ID format of the resource type for a specified
        IAM user, IAM role, or the root user for an account is affected. The
        opt-in and opt-out account setting must be set for each Amazon ECS
        resource separately. The ARN and resource ID format of a resource is
        defined by the opt-in status of the IAM user or role that created the
        resource. You must turn on this setting to use Amazon ECS features such
        as resource tagging.

        When ``awsvpcTrunking`` is specified, the elastic network interface
        (ENI) limit for any new container instances that support the feature is
        changed. If ``awsvpcTrunking`` is enabled, any new container instances
        that support the feature are launched have the increased ENI limits
        available to them. For more information, see `Elastic Network Interface
        Trunking <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/container-instance-eni.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        When ``containerInsights`` is specified, the default setting indicating
        whether CloudWatch Container Insights is enabled for your clusters is
        changed. If ``containerInsights`` is enabled, any new clusters that are
        created will have Container Insights enabled unless you disable it
        during cluster creation. For more information, see `CloudWatch Container
        Insights <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cloudwatch-container-insights.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param name: The Amazon ECS resource name for which to modify the account setting.
        :param value: The account setting value for the specified principal ARN.
        :param principal_arn: The ARN of the principal, which can be an IAM user, IAM role, or the
        root user.
        :returns: PutAccountSettingResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("PutAccountSettingDefault")
    def put_account_setting_default(
        self, context: RequestContext, name: SettingName, value: String
    ) -> PutAccountSettingDefaultResponse:
        """Modifies an account setting for all IAM users on an account for whom no
        individual account setting has been specified. Account settings are set
        on a per-Region basis.

        :param name: The resource name for which to modify the account setting.
        :param value: The account setting value for the specified principal ARN.
        :returns: PutAccountSettingDefaultResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("PutAttributes")
    def put_attributes(
        self, context: RequestContext, attributes: Attributes, cluster: String = None
    ) -> PutAttributesResponse:
        """Create or update an attribute on an Amazon ECS resource. If the
        attribute doesn't exist, it's created. If the attribute exists, its
        value is replaced with the specified value. To delete an attribute, use
        DeleteAttributes. For more information, see
        `Attributes <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-placement-constraints.html#attributes>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param attributes: The attributes to apply to your resource.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        contains the resource to apply attributes.
        :returns: PutAttributesResponse
        :raises ClusterNotFoundException:
        :raises TargetNotFoundException:
        :raises AttributeLimitExceededException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("PutClusterCapacityProviders")
    def put_cluster_capacity_providers(
        self,
        context: RequestContext,
        cluster: String,
        capacity_providers: StringList,
        default_capacity_provider_strategy: CapacityProviderStrategy,
    ) -> PutClusterCapacityProvidersResponse:
        """Modifies the available capacity providers and the default capacity
        provider strategy for a cluster.

        You must specify both the available capacity providers and a default
        capacity provider strategy for the cluster. If the specified cluster has
        existing capacity providers associated with it, you must specify all
        existing capacity providers in addition to any new ones you want to add.
        Any existing capacity providers that are associated with a cluster that
        are omitted from a PutClusterCapacityProviders API call will be
        disassociated with the cluster. You can only disassociate an existing
        capacity provider from a cluster if it's not being used by any existing
        tasks.

        When creating a service or running a task on a cluster, if no capacity
        provider or launch type is specified, then the cluster's default
        capacity provider strategy is used. We recommend that you define a
        default capacity provider strategy for your cluster. However, you must
        specify an empty array (``[]``) to bypass defining a default strategy.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster to
        modify the capacity provider settings for.
        :param capacity_providers: The name of one or more capacity providers to associate with the
        cluster.
        :param default_capacity_provider_strategy: The capacity provider strategy to use by default for the cluster.
        :returns: PutClusterCapacityProvidersResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises ResourceInUseException:
        :raises UpdateInProgressException:
        """
        raise NotImplementedError

    @handler("RegisterContainerInstance")
    def register_container_instance(
        self,
        context: RequestContext,
        cluster: String = None,
        instance_identity_document: String = None,
        instance_identity_document_signature: String = None,
        total_resources: Resources = None,
        version_info: VersionInfo = None,
        container_instance_arn: String = None,
        attributes: Attributes = None,
        platform_devices: PlatformDevices = None,
        tags: Tags = None,
    ) -> RegisterContainerInstanceResponse:
        """This action is only used by the Amazon ECS agent, and it is not intended
        for use outside of the agent.

        Registers an EC2 instance into the specified cluster. This instance
        becomes available to place containers on.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster to
        register your container instance with.
        :param instance_identity_document: The instance identity document for the EC2 instance to register.
        :param instance_identity_document_signature: The instance identity document signature for the EC2 instance to
        register.
        :param total_resources: The resources available on the instance.
        :param version_info: The version information for the Amazon ECS container agent and Docker
        daemon that runs on the container instance.
        :param container_instance_arn: The ARN of the container instance (if it was previously registered).
        :param attributes: The container instance attributes that this container instance supports.
        :param platform_devices: The devices that are available on the container instance.
        :param tags: The metadata that you apply to the container instance to help you
        categorize and organize them.
        :returns: RegisterContainerInstanceResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("RegisterTaskDefinition")
    def register_task_definition(
        self,
        context: RequestContext,
        family: String,
        container_definitions: ContainerDefinitions,
        task_role_arn: String = None,
        execution_role_arn: String = None,
        network_mode: NetworkMode = None,
        volumes: VolumeList = None,
        placement_constraints: TaskDefinitionPlacementConstraints = None,
        requires_compatibilities: CompatibilityList = None,
        cpu: String = None,
        memory: String = None,
        tags: Tags = None,
        pid_mode: PidMode = None,
        ipc_mode: IpcMode = None,
        proxy_configuration: ProxyConfiguration = None,
        inference_accelerators: InferenceAccelerators = None,
        ephemeral_storage: EphemeralStorage = None,
        runtime_platform: RuntimePlatform = None,
    ) -> RegisterTaskDefinitionResponse:
        """Registers a new task definition from the supplied ``family`` and
        ``containerDefinitions``. Optionally, you can add data volumes to your
        containers with the ``volumes`` parameter. For more information about
        task definition parameters and defaults, see `Amazon ECS Task
        Definitions <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_defintions.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        You can specify an IAM role for your task with the ``taskRoleArn``
        parameter. When you specify an IAM role for a task, its containers can
        then use the latest versions of the CLI or SDKs to make API requests to
        the Amazon Web Services services that are specified in the IAM policy
        that's associated with the role. For more information, see `IAM Roles
        for
        Tasks <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        You can specify a Docker networking mode for the containers in your task
        definition with the ``networkMode`` parameter. The available network
        modes correspond to those described in `Network
        settings <https://docs.docker.com/engine/reference/run/#/network-settings>`__
        in the Docker run reference. If you specify the ``awsvpc`` network mode,
        the task is allocated an elastic network interface, and you must specify
        a NetworkConfiguration when you create a service or run a task with the
        task definition. For more information, see `Task
        Networking <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-networking.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param family: You must specify a ``family`` for a task definition.
        :param container_definitions: A list of container definitions in JSON format that describe the
        different containers that make up your task.
        :param task_role_arn: The short name or full Amazon Resource Name (ARN) of the IAM role that
        containers in this task can assume.
        :param execution_role_arn: The Amazon Resource Name (ARN) of the task execution role that grants
        the Amazon ECS container agent permission to make Amazon Web Services
        API calls on your behalf.
        :param network_mode: The Docker networking mode to use for the containers in the task.
        :param volumes: A list of volume definitions in JSON format that containers in your task
        might use.
        :param placement_constraints: An array of placement constraint objects to use for the task.
        :param requires_compatibilities: The task launch type that Amazon ECS validates the task definition
        against.
        :param cpu: The number of CPU units used by the task.
        :param memory: The amount of memory (in MiB) used by the task.
        :param tags: The metadata that you apply to the task definition to help you
        categorize and organize them.
        :param pid_mode: The process namespace to use for the containers in the task.
        :param ipc_mode: The IPC resource namespace to use for the containers in the task.
        :param proxy_configuration: The configuration details for the App Mesh proxy.
        :param inference_accelerators: The Elastic Inference accelerators to use for the containers in the
        task.
        :param ephemeral_storage: The amount of ephemeral storage to allocate for the task.
        :param runtime_platform: The operating system that your tasks definitions run on.
        :returns: RegisterTaskDefinitionResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("RunTask")
    def run_task(
        self,
        context: RequestContext,
        task_definition: String,
        capacity_provider_strategy: CapacityProviderStrategy = None,
        cluster: String = None,
        count: BoxedInteger = None,
        enable_ecs_managed_tags: Boolean = None,
        enable_execute_command: Boolean = None,
        group: String = None,
        launch_type: LaunchType = None,
        network_configuration: NetworkConfiguration = None,
        overrides: TaskOverride = None,
        placement_constraints: PlacementConstraints = None,
        placement_strategy: PlacementStrategies = None,
        platform_version: String = None,
        propagate_tags: PropagateTags = None,
        reference_id: String = None,
        started_by: String = None,
        tags: Tags = None,
    ) -> RunTaskResponse:
        """Starts a new task using the specified task definition.

        You can allow Amazon ECS to place tasks for you, or you can customize
        how Amazon ECS places tasks using placement constraints and placement
        strategies. For more information, see `Scheduling
        Tasks <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/scheduling_tasks.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        Alternatively, you can use StartTask to use your own scheduler or place
        tasks manually on specific container instances.

        The Amazon ECS API follows an eventual consistency model. This is
        because of the distributed nature of the system supporting the API. This
        means that the result of an API command you run that affects your Amazon
        ECS resources might not be immediately visible to all subsequent
        commands you run. Keep this in mind when you carry out an API command
        that immediately follows a previous API command.

        To manage eventual consistency, you can do the following:

        -  Confirm the state of the resource before you run a command to modify
           it. Run the DescribeTasks command using an exponential backoff
           algorithm to ensure that you allow enough time for the previous
           command to propagate through the system. To do this, run the
           DescribeTasks command repeatedly, starting with a couple of seconds
           of wait time and increasing gradually up to five minutes of wait
           time.

        -  Add wait time between subsequent commands, even if the DescribeTasks
           command returns an accurate response. Apply an exponential backoff
           algorithm starting with a couple of seconds of wait time, and
           increase gradually up to about five minutes of wait time.

        :param task_definition: The ``family`` and ``revision`` (``family:revision``) or full ARN of the
        task definition to run.
        :param capacity_provider_strategy: The capacity provider strategy to use for the task.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster to run
        your task on.
        :param count: The number of instantiations of the specified task to place on your
        cluster.
        :param enable_ecs_managed_tags: Specifies whether to use Amazon ECS managed tags for the task.
        :param enable_execute_command: Determines whether to use the execute command functionality for the
        containers in this task.
        :param group: The name of the task group to associate with the task.
        :param launch_type: The infrastructure to run your standalone task on.
        :param network_configuration: The network configuration for the task.
        :param overrides: A list of container overrides in JSON format that specify the name of a
        container in the specified task definition and the overrides it should
        receive.
        :param placement_constraints: An array of placement constraint objects to use for the task.
        :param placement_strategy: The placement strategy objects to use for the task.
        :param platform_version: The platform version the task uses.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition to the
        task.
        :param reference_id: The reference ID to use for the task.
        :param started_by: An optional tag specified when a task is started.
        :param tags: The metadata that you apply to the task to help you categorize and
        organize them.
        :returns: RunTaskResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises UnsupportedFeatureException:
        :raises PlatformUnknownException:
        :raises PlatformTaskDefinitionIncompatibilityException:
        :raises AccessDeniedException:
        :raises BlockedException:
        """
        raise NotImplementedError

    @handler("StartTask")
    def start_task(
        self,
        context: RequestContext,
        container_instances: StringList,
        task_definition: String,
        cluster: String = None,
        enable_ecs_managed_tags: Boolean = None,
        enable_execute_command: Boolean = None,
        group: String = None,
        network_configuration: NetworkConfiguration = None,
        overrides: TaskOverride = None,
        propagate_tags: PropagateTags = None,
        reference_id: String = None,
        started_by: String = None,
        tags: Tags = None,
    ) -> StartTaskResponse:
        """Starts a new task from the specified task definition on the specified
        container instance or instances.

        Alternatively, you can use RunTask to place tasks for you. For more
        information, see `Scheduling
        Tasks <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/scheduling_tasks.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param container_instances: The container instance IDs or full ARN entries for the container
        instances where you would like to place your task.
        :param task_definition: The ``family`` and ``revision`` (``family:revision``) or full ARN of the
        task definition to start.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster where
        to start your task.
        :param enable_ecs_managed_tags: Specifies whether to use Amazon ECS managed tags for the task.
        :param enable_execute_command: Whether or not the execute command functionality is enabled for the
        task.
        :param group: The name of the task group to associate with the task.
        :param network_configuration: The VPC subnet and security group configuration for tasks that receive
        their own elastic network interface by using the ``awsvpc`` networking
        mode.
        :param overrides: A list of container overrides in JSON format that specify the name of a
        container in the specified task definition and the overrides it
        receives.
        :param propagate_tags: Specifies whether to propagate the tags from the task definition or the
        service to the task.
        :param reference_id: The reference ID to use for the task.
        :param started_by: An optional tag specified when a task is started.
        :param tags: The metadata that you apply to the task to help you categorize and
        organize them.
        :returns: StartTaskResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        """
        raise NotImplementedError

    @handler("StopTask")
    def stop_task(
        self, context: RequestContext, task: String, cluster: String = None, reason: String = None
    ) -> StopTaskResponse:
        """Stops a running task. Any tags associated with the task will be deleted.

        When StopTask is called on a task, the equivalent of ``docker stop`` is
        issued to the containers running in the task. This results in a
        ``SIGTERM`` value and a default 30-second timeout, after which the
        ``SIGKILL`` value is sent and the containers are forcibly stopped. If
        the container handles the ``SIGTERM`` value gracefully and exits within
        30 seconds from receiving it, no ``SIGKILL`` value is sent.

        The default 30-second timeout can be configured on the Amazon ECS
        container agent with the ``ECS_CONTAINER_STOP_TIMEOUT`` variable. For
        more information, see `Amazon ECS Container Agent
        Configuration <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-config.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param task: The task ID or full Amazon Resource Name (ARN) of the task to stop.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the task to stop.
        :param reason: An optional message specified when a task is stopped.
        :returns: StopTaskResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        """
        raise NotImplementedError

    @handler("SubmitAttachmentStateChanges")
    def submit_attachment_state_changes(
        self, context: RequestContext, attachments: AttachmentStateChanges, cluster: String = None
    ) -> SubmitAttachmentStateChangesResponse:
        """This action is only used by the Amazon ECS agent, and it is not intended
        for use outside of the agent.

        Sent to acknowledge that an attachment changed states.

        :param attachments: Any attachments associated with the state change request.
        :param cluster: The short name or full ARN of the cluster that hosts the container
        instance the attachment belongs to.
        :returns: SubmitAttachmentStateChangesResponse
        :raises ServerException:
        :raises ClientException:
        :raises AccessDeniedException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("SubmitContainerStateChange")
    def submit_container_state_change(
        self,
        context: RequestContext,
        cluster: String = None,
        task: String = None,
        container_name: String = None,
        runtime_id: String = None,
        status: String = None,
        exit_code: BoxedInteger = None,
        reason: String = None,
        network_bindings: NetworkBindings = None,
    ) -> SubmitContainerStateChangeResponse:
        """This action is only used by the Amazon ECS agent, and it is not intended
        for use outside of the agent.

        Sent to acknowledge that a container changed states.

        :param cluster: The short name or full ARN of the cluster that hosts the container.
        :param task: The task ID or full Amazon Resource Name (ARN) of the task that hosts
        the container.
        :param container_name: The name of the container.
        :param runtime_id: The ID of the Docker container.
        :param status: The status of the state change request.
        :param exit_code: The exit code that's returned for the state change request.
        :param reason: The reason for the state change request.
        :param network_bindings: The network bindings of the container.
        :returns: SubmitContainerStateChangeResponse
        :raises ServerException:
        :raises ClientException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("SubmitTaskStateChange")
    def submit_task_state_change(
        self,
        context: RequestContext,
        cluster: String = None,
        task: String = None,
        status: String = None,
        reason: String = None,
        containers: ContainerStateChanges = None,
        attachments: AttachmentStateChanges = None,
        managed_agents: ManagedAgentStateChanges = None,
        pull_started_at: Timestamp = None,
        pull_stopped_at: Timestamp = None,
        execution_stopped_at: Timestamp = None,
    ) -> SubmitTaskStateChangeResponse:
        """This action is only used by the Amazon ECS agent, and it is not intended
        for use outside of the agent.

        Sent to acknowledge that a task changed states.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the task.
        :param task: The task ID or full ARN of the task in the state change request.
        :param status: The status of the state change request.
        :param reason: The reason for the state change request.
        :param containers: Any containers that's associated with the state change request.
        :param attachments: Any attachments associated with the state change request.
        :param managed_agents: The details for the managed agent that's associated with the task.
        :param pull_started_at: The Unix timestamp for the time when the container image pull started.
        :param pull_stopped_at: The Unix timestamp for the time when the container image pull completed.
        :param execution_stopped_at: The Unix timestamp for the time when the task execution stopped.
        :returns: SubmitTaskStateChangeResponse
        :raises ServerException:
        :raises ClientException:
        :raises AccessDeniedException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: String, tags: Tags
    ) -> TagResourceResponse:
        """Associates the specified tags to a resource with the specified
        ``resourceArn``. If existing tags on a resource aren't specified in the
        request parameters, they aren't changed. When a resource is deleted, the
        tags that are associated with that resource are deleted as well.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource to add tags to.
        :param tags: The tags to add to the resource.
        :returns: TagResourceResponse
        :raises ServerException:
        :raises ClientException:
        :raises ClusterNotFoundException:
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: String, tag_keys: TagKeys
    ) -> UntagResourceResponse:
        """Deletes specified tags from a resource.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource to delete tags from.
        :param tag_keys: The keys of the tags to be removed.
        :returns: UntagResourceResponse
        :raises ServerException:
        :raises ClientException:
        :raises ClusterNotFoundException:
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("UpdateCapacityProvider")
    def update_capacity_provider(
        self,
        context: RequestContext,
        name: String,
        auto_scaling_group_provider: AutoScalingGroupProviderUpdate,
    ) -> UpdateCapacityProviderResponse:
        """Modifies the parameters for a capacity provider.

        :param name: The name of the capacity provider to update.
        :param auto_scaling_group_provider: An object that represent the parameters to update for the Auto Scaling
        group capacity provider.
        :returns: UpdateCapacityProviderResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("UpdateCluster")
    def update_cluster(
        self,
        context: RequestContext,
        cluster: String,
        settings: ClusterSettings = None,
        configuration: ClusterConfiguration = None,
    ) -> UpdateClusterResponse:
        """Updates the cluster.

        :param cluster: The name of the cluster to modify the settings for.
        :param settings: The cluster settings for your cluster.
        :param configuration: The execute command configuration for the cluster.
        :returns: UpdateClusterResponse
        :raises ServerException:
        :raises ClientException:
        :raises ClusterNotFoundException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("UpdateClusterSettings")
    def update_cluster_settings(
        self, context: RequestContext, cluster: String, settings: ClusterSettings
    ) -> UpdateClusterSettingsResponse:
        """Modifies the settings to use for a cluster.

        :param cluster: The name of the cluster to modify the settings for.
        :param settings: The setting to use by default for a cluster.
        :returns: UpdateClusterSettingsResponse
        :raises ServerException:
        :raises ClientException:
        :raises ClusterNotFoundException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("UpdateContainerAgent")
    def update_container_agent(
        self, context: RequestContext, container_instance: String, cluster: String = None
    ) -> UpdateContainerAgentResponse:
        """Updates the Amazon ECS container agent on a specified container
        instance. Updating the Amazon ECS container agent doesn't interrupt
        running tasks or services on the container instance. The process for
        updating the agent differs depending on whether your container instance
        was launched with the Amazon ECS-optimized AMI or another operating
        system.

        The ``UpdateContainerAgent`` API isn't supported for container instances
        using the Amazon ECS-optimized Amazon Linux 2 (arm64) AMI. To update the
        container agent, you can update the ``ecs-init`` package. This updates
        the agent. For more information, see `Updating the Amazon ECS container
        agent <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/agent-update-ecs-ami.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        The ``UpdateContainerAgent`` API requires an Amazon ECS-optimized AMI or
        Amazon Linux AMI with the ``ecs-init`` service installed and running.
        For help updating the Amazon ECS container agent on other operating
        systems, see `Manually updating the Amazon ECS container
        agent <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-update.html#manually_update_agent>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param container_instance: The container instance ID or full ARN entries for the container instance
        where you would like to update the Amazon ECS container agent.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        your container instance is running on.
        :returns: UpdateContainerAgentResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises UpdateInProgressException:
        :raises NoUpdateAvailableException:
        :raises MissingVersionException:
        """
        raise NotImplementedError

    @handler("UpdateContainerInstancesState")
    def update_container_instances_state(
        self,
        context: RequestContext,
        container_instances: StringList,
        status: ContainerInstanceStatus,
        cluster: String = None,
    ) -> UpdateContainerInstancesStateResponse:
        """Modifies the status of an Amazon ECS container instance.

        Once a container instance has reached an ``ACTIVE`` state, you can
        change the status of a container instance to ``DRAINING`` to manually
        remove an instance from a cluster, for example to perform system
        updates, update the Docker daemon, or scale down the cluster size.

        A container instance can't be changed to ``DRAINING`` until it has
        reached an ``ACTIVE`` status. If the instance is in any other status, an
        error will be received.

        When you set a container instance to ``DRAINING``, Amazon ECS prevents
        new tasks from being scheduled for placement on the container instance
        and replacement service tasks are started on other container instances
        in the cluster if the resources are available. Service tasks on the
        container instance that are in the ``PENDING`` state are stopped
        immediately.

        Service tasks on the container instance that are in the ``RUNNING``
        state are stopped and replaced according to the service's deployment
        configuration parameters, ``minimumHealthyPercent`` and
        ``maximumPercent``. You can change the deployment configuration of your
        service using UpdateService.

        -  If ``minimumHealthyPercent`` is below 100%, the scheduler can ignore
           ``desiredCount`` temporarily during task replacement. For example,
           ``desiredCount`` is four tasks, a minimum of 50% allows the scheduler
           to stop two existing tasks before starting two new tasks. If the
           minimum is 100%, the service scheduler can't remove existing tasks
           until the replacement tasks are considered healthy. Tasks for
           services that do not use a load balancer are considered healthy if
           they're in the ``RUNNING`` state. Tasks for services that use a load
           balancer are considered healthy if they're in the ``RUNNING`` state
           and are reported as healthy by the load balancer.

        -  The ``maximumPercent`` parameter represents an upper limit on the
           number of running tasks during task replacement. You can use this to
           define the replacement batch size. For example, if ``desiredCount``
           is four tasks, a maximum of 200% starts four new tasks before
           stopping the four tasks to be drained, provided that the cluster
           resources required to do this are available. If the maximum is 100%,
           then replacement tasks can't start until the draining tasks have
           stopped.

        Any ``PENDING`` or ``RUNNING`` tasks that do not belong to a service
        aren't affected. You must wait for them to finish or stop them manually.

        A container instance has completed draining when it has no more
        ``RUNNING`` tasks. You can verify this using ListTasks.

        When a container instance has been drained, you can set a container
        instance to ``ACTIVE`` status and once it has reached that status the
        Amazon ECS scheduler can begin scheduling tasks on the instance again.

        :param container_instances: A list of up to 10 container instance IDs or full ARN entries.
        :param status: The container instance state to update the container instance with.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the container instance to update.
        :returns: UpdateContainerInstancesStateResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateService")
    def update_service(
        self,
        context: RequestContext,
        service: String,
        cluster: String = None,
        desired_count: BoxedInteger = None,
        task_definition: String = None,
        capacity_provider_strategy: CapacityProviderStrategy = None,
        deployment_configuration: DeploymentConfiguration = None,
        network_configuration: NetworkConfiguration = None,
        placement_constraints: PlacementConstraints = None,
        placement_strategy: PlacementStrategies = None,
        platform_version: String = None,
        force_new_deployment: Boolean = None,
        health_check_grace_period_seconds: BoxedInteger = None,
        enable_execute_command: BoxedBoolean = None,
        enable_ecs_managed_tags: BoxedBoolean = None,
        load_balancers: LoadBalancers = None,
        propagate_tags: PropagateTags = None,
        service_registries: ServiceRegistries = None,
    ) -> UpdateServiceResponse:
        """Updating the task placement strategies and constraints on an Amazon ECS
        service remains in preview and is a Beta Service as defined by and
        subject to the Beta Service Participation Service Terms located at
        https://aws.amazon.com/service-terms ("Beta Terms"). These Beta Terms
        apply to your participation in this preview.

        Modifies the parameters of a service.

        For services using the rolling update (``ECS``) you can update the
        desired count, deployment configuration, network configuration, load
        balancers, service registries, enable ECS managed tags option, propagate
        tags option, task placement constraints and strategies, and task
        definition. When you update any of these parameters, Amazon ECS starts
        new tasks with the new configuration.

        For services using the blue/green (``CODE_DEPLOY``) deployment
        controller, only the desired count, deployment configuration, health
        check grace period, task placement constraints and strategies, enable
        ECS managed tags option, and propagate tags can be updated using this
        API. If the network configuration, platform version, task definition, or
        load balancer need to be updated, create a new CodeDeploy deployment.
        For more information, see
        `CreateDeployment <https://docs.aws.amazon.com/codedeploy/latest/APIReference/API_CreateDeployment.html>`__
        in the *CodeDeploy API Reference*.

        For services using an external deployment controller, you can update
        only the desired count, task placement constraints and strategies,
        health check grace period, enable ECS managed tags option, and propagate
        tags option, using this API. If the launch type, load balancer, network
        configuration, platform version, or task definition need to be updated,
        create a new task set For more information, see CreateTaskSet.

        You can add to or subtract from the number of instantiations of a task
        definition in a service by specifying the cluster that the service is
        running in and a new ``desiredCount`` parameter.

        If you have updated the Docker image of your application, you can create
        a new task definition with that image and deploy it to your service. The
        service scheduler uses the minimum healthy percent and maximum percent
        parameters (in the service's deployment configuration) to determine the
        deployment strategy.

        If your updated Docker image uses the same tag as what is in the
        existing task definition for your service (for example,
        ``my_image:latest``), you don't need to create a new revision of your
        task definition. You can update the service using the
        ``forceNewDeployment`` option. The new tasks launched by the deployment
        pull the current image/tag combination from your repository when they
        start.

        You can also update the deployment configuration of a service. When a
        deployment is triggered by updating the task definition of a service,
        the service scheduler uses the deployment configuration parameters,
        ``minimumHealthyPercent`` and ``maximumPercent``, to determine the
        deployment strategy.

        -  If ``minimumHealthyPercent`` is below 100%, the scheduler can ignore
           ``desiredCount`` temporarily during a deployment. For example, if
           ``desiredCount`` is four tasks, a minimum of 50% allows the scheduler
           to stop two existing tasks before starting two new tasks. Tasks for
           services that don't use a load balancer are considered healthy if
           they're in the ``RUNNING`` state. Tasks for services that use a load
           balancer are considered healthy if they're in the ``RUNNING`` state
           and are reported as healthy by the load balancer.

        -  The ``maximumPercent`` parameter represents an upper limit on the
           number of running tasks during a deployment. You can use it to define
           the deployment batch size. For example, if ``desiredCount`` is four
           tasks, a maximum of 200% starts four new tasks before stopping the
           four older tasks (provided that the cluster resources required to do
           this are available).

        When UpdateService stops a task during a deployment, the equivalent of
        ``docker stop`` is issued to the containers running in the task. This
        results in a ``SIGTERM`` and a 30-second timeout. After this,
        ``SIGKILL`` is sent and the containers are forcibly stopped. If the
        container handles the ``SIGTERM`` gracefully and exits within 30 seconds
        from receiving it, no ``SIGKILL`` is sent.

        When the service scheduler launches new tasks, it determines task
        placement in your cluster with the following logic.

        -  Determine which of the container instances in your cluster can
           support your service's task definition. For example, they have the
           required CPU, memory, ports, and container instance attributes.

        -  By default, the service scheduler attempts to balance tasks across
           Availability Zones in this manner even though you can choose a
           different placement strategy.

           -  Sort the valid container instances by the fewest number of running
              tasks for this service in the same Availability Zone as the
              instance. For example, if zone A has one running service task and
              zones B and C each have zero, valid container instances in either
              zone B or C are considered optimal for placement.

           -  Place the new service task on a valid container instance in an
              optimal Availability Zone (based on the previous steps), favoring
              container instances with the fewest number of running tasks for
              this service.

        When the service scheduler stops running tasks, it attempts to maintain
        balance across the Availability Zones in your cluster using the
        following logic:

        -  Sort the container instances by the largest number of running tasks
           for this service in the same Availability Zone as the instance. For
           example, if zone A has one running service task and zones B and C
           each have two, container instances in either zone B or C are
           considered optimal for termination.

        -  Stop the task on a container instance in an optimal Availability Zone
           (based on the previous steps), favoring container instances with the
           largest number of running tasks for this service.

        You must have a service-linked role when you update any of the following
        service properties. If you specified a custom IAM role when you created
        the service, Amazon ECS automatically replaces the
        `roleARN <https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_Service.html#ECS-Type-Service-roleArn>`__
        associated with the service with the ARN of your service-linked role.
        For more information, see `Service-linked
        roles <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using-service-linked-roles.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        -  ``loadBalancers,``

        -  ``serviceRegistries``

        :param service: The name of the service to update.
        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        your service runs on.
        :param desired_count: The number of instantiations of the task to place and keep running in
        your service.
        :param task_definition: The ``family`` and ``revision`` (``family:revision``) or full ARN of the
        task definition to run in your service.
        :param capacity_provider_strategy: The capacity provider strategy to update the service to use.
        :param deployment_configuration: Optional deployment parameters that control how many tasks run during
        the deployment and the ordering of stopping and starting tasks.
        :param network_configuration: An object representing the network configuration for the service.
        :param placement_constraints: An array of task placement constraint objects to update the service to
        use.
        :param placement_strategy: The task placement strategy objects to update the service to use.
        :param platform_version: The platform version that your tasks in the service run on.
        :param force_new_deployment: Determines whether to force a new deployment of the service.
        :param health_check_grace_period_seconds: The period of time, in seconds, that the Amazon ECS service scheduler
        ignores unhealthy Elastic Load Balancing target health checks after a
        task has first started.
        :param enable_execute_command: If ``true``, this enables execute command functionality on all task
        containers.
        :param enable_ecs_managed_tags: Determines whether to turn on Amazon ECS managed tags for the tasks in
        the service.
        :param load_balancers: A list of Elastic Load Balancing load balancer objects.
        :param propagate_tags: Determines whether to propagate the tags from the task definition or the
        service to the task.
        :param service_registries: The details for the service discovery registries to assign to this
        service.
        :returns: UpdateServiceResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises ServiceNotFoundException:
        :raises ServiceNotActiveException:
        :raises PlatformUnknownException:
        :raises PlatformTaskDefinitionIncompatibilityException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("UpdateServicePrimaryTaskSet")
    def update_service_primary_task_set(
        self, context: RequestContext, cluster: String, service: String, primary_task_set: String
    ) -> UpdateServicePrimaryTaskSetResponse:
        """Modifies which task set in a service is the primary task set. Any
        parameters that are updated on the primary task set in a service will
        transition to the service. This is used when a service uses the
        ``EXTERNAL`` deployment controller type. For more information, see
        `Amazon ECS Deployment
        Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the service that the task set exists in.
        :param service: The short name or full Amazon Resource Name (ARN) of the service that
        the task set exists in.
        :param primary_task_set: The short name or full Amazon Resource Name (ARN) of the task set to set
        as the primary task set in the deployment.
        :returns: UpdateServicePrimaryTaskSetResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises UnsupportedFeatureException:
        :raises ServiceNotFoundException:
        :raises ServiceNotActiveException:
        :raises TaskSetNotFoundException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("UpdateTaskSet")
    def update_task_set(
        self,
        context: RequestContext,
        cluster: String,
        service: String,
        task_set: String,
        scale: Scale,
    ) -> UpdateTaskSetResponse:
        """Modifies a task set. This is used when a service uses the ``EXTERNAL``
        deployment controller type. For more information, see `Amazon ECS
        Deployment
        Types <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        :param cluster: The short name or full Amazon Resource Name (ARN) of the cluster that
        hosts the service that the task set is found in.
        :param service: The short name or full Amazon Resource Name (ARN) of the service that
        the task set is found in.
        :param task_set: The short name or full Amazon Resource Name (ARN) of the task set to
        update.
        :param scale: A floating-point percentage of the desired number of tasks to place and
        keep running in the task set.
        :returns: UpdateTaskSetResponse
        :raises ServerException:
        :raises ClientException:
        :raises InvalidParameterException:
        :raises ClusterNotFoundException:
        :raises UnsupportedFeatureException:
        :raises AccessDeniedException:
        :raises ServiceNotFoundException:
        :raises ServiceNotActiveException:
        :raises TaskSetNotFoundException:
        """
        raise NotImplementedError
