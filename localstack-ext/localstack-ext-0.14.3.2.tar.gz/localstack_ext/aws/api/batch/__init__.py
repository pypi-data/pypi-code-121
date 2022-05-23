import sys
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Boolean = bool
Float = float
ImageIdOverride = str
ImageType = str
Integer = int
String = str
TagKey = str
TagValue = str


class ArrayJobDependency(str):
    N_TO_N = "N_TO_N"
    SEQUENTIAL = "SEQUENTIAL"


class AssignPublicIp(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class CEState(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class CEStatus(str):
    CREATING = "CREATING"
    UPDATING = "UPDATING"
    DELETING = "DELETING"
    DELETED = "DELETED"
    VALID = "VALID"
    INVALID = "INVALID"


class CEType(str):
    MANAGED = "MANAGED"
    UNMANAGED = "UNMANAGED"


class CRAllocationStrategy(str):
    BEST_FIT = "BEST_FIT"
    BEST_FIT_PROGRESSIVE = "BEST_FIT_PROGRESSIVE"
    SPOT_CAPACITY_OPTIMIZED = "SPOT_CAPACITY_OPTIMIZED"


class CRType(str):
    EC2 = "EC2"
    SPOT = "SPOT"
    FARGATE = "FARGATE"
    FARGATE_SPOT = "FARGATE_SPOT"


class CRUpdateAllocationStrategy(str):
    BEST_FIT_PROGRESSIVE = "BEST_FIT_PROGRESSIVE"
    SPOT_CAPACITY_OPTIMIZED = "SPOT_CAPACITY_OPTIMIZED"


class DeviceCgroupPermission(str):
    READ = "READ"
    WRITE = "WRITE"
    MKNOD = "MKNOD"


class EFSAuthorizationConfigIAM(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class EFSTransitEncryption(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class JQState(str):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class JQStatus(str):
    CREATING = "CREATING"
    UPDATING = "UPDATING"
    DELETING = "DELETING"
    DELETED = "DELETED"
    VALID = "VALID"
    INVALID = "INVALID"


class JobDefinitionType(str):
    container = "container"
    multinode = "multinode"


class JobStatus(str):
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"
    RUNNABLE = "RUNNABLE"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class LogDriver(str):
    json_file = "json-file"
    syslog = "syslog"
    journald = "journald"
    gelf = "gelf"
    fluentd = "fluentd"
    awslogs = "awslogs"
    splunk = "splunk"


class PlatformCapability(str):
    EC2 = "EC2"
    FARGATE = "FARGATE"


class ResourceType(str):
    GPU = "GPU"
    VCPU = "VCPU"
    MEMORY = "MEMORY"


class RetryAction(str):
    RETRY = "RETRY"
    EXIT = "EXIT"


class ClientException(ServiceException):
    """These errors are usually caused by a client action, such as using an
    action or resource on behalf of a user that doesn't have permissions to
    use the action or resource, or specifying an identifier that's not
    valid.
    """

    message: Optional[String]


class ServerException(ServiceException):
    """These errors are usually caused by a server issue."""

    message: Optional[String]


ArrayJobStatusSummary = Dict[String, Integer]


class ArrayProperties(TypedDict, total=False):
    """An object representing an Batch array job."""

    size: Optional[Integer]


class ArrayPropertiesDetail(TypedDict, total=False):
    """An object representing the array properties of a job."""

    statusSummary: Optional[ArrayJobStatusSummary]
    size: Optional[Integer]
    index: Optional[Integer]


class ArrayPropertiesSummary(TypedDict, total=False):
    """An object representing the array properties of a job."""

    size: Optional[Integer]
    index: Optional[Integer]


class NetworkInterface(TypedDict, total=False):
    """An object representing the elastic network interface for a multi-node
    parallel job node.
    """

    attachmentId: Optional[String]
    ipv6Address: Optional[String]
    privateIpv4Address: Optional[String]


NetworkInterfaceList = List[NetworkInterface]


class AttemptContainerDetail(TypedDict, total=False):
    """An object representing the details of a container that's part of a job
    attempt.
    """

    containerInstanceArn: Optional[String]
    taskArn: Optional[String]
    exitCode: Optional[Integer]
    reason: Optional[String]
    logStreamName: Optional[String]
    networkInterfaces: Optional[NetworkInterfaceList]


Long = int


class AttemptDetail(TypedDict, total=False):
    """An object representing a job attempt."""

    container: Optional[AttemptContainerDetail]
    startedAt: Optional[Long]
    stoppedAt: Optional[Long]
    statusReason: Optional[String]


AttemptDetails = List[AttemptDetail]


class CancelJobRequest(ServiceRequest):
    """Contains the parameters for ``CancelJob``."""

    jobId: String
    reason: String


class CancelJobResponse(TypedDict, total=False):
    pass


JobExecutionTimeoutMinutes = int


class UpdatePolicy(TypedDict, total=False):
    """Specifies the infrastructure update policy for the compute environment.
    For more information about infrastructure updates, see `Infrastructure
    updates <https://docs.aws.amazon.com/batch/latest/userguide/infrastructure-updates.html>`__
    in the *Batch User Guide*.
    """

    terminateJobsOnUpdate: Optional[Boolean]
    jobExecutionTimeoutMinutes: Optional[JobExecutionTimeoutMinutes]


class Ec2Configuration(TypedDict, total=False):
    """Provides information used to select Amazon Machine Images (AMIs) for
    instances in the compute environment. If ``Ec2Configuration`` isn't
    specified, the default is ``ECS_AL2`` (`Amazon Linux
    2 <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html#al2ami>`__).

    This object isn't applicable to jobs that are running on Fargate
    resources.
    """

    imageType: ImageType
    imageIdOverride: Optional[ImageIdOverride]


Ec2ConfigurationList = List[Ec2Configuration]


class LaunchTemplateSpecification(TypedDict, total=False):
    """An object representing a launch template associated with a compute
    resource. You must specify either the launch template ID or launch
    template name in the request, but not both.

    If security groups are specified using both the ``securityGroupIds``
    parameter of ``CreateComputeEnvironment`` and the launch template, the
    values in the ``securityGroupIds`` parameter of
    ``CreateComputeEnvironment`` will be used.

    This object isn't applicable to jobs that are running on Fargate
    resources.
    """

    launchTemplateId: Optional[String]
    launchTemplateName: Optional[String]
    version: Optional[String]


TagsMap = Dict[String, String]
StringList = List[String]
ComputeResource = TypedDict(
    "ComputeResource",
    {
        "type": CRType,
        "allocationStrategy": Optional[CRAllocationStrategy],
        "minvCpus": Optional[Integer],
        "maxvCpus": Integer,
        "desiredvCpus": Optional[Integer],
        "instanceTypes": Optional[StringList],
        "imageId": Optional[String],
        "subnets": StringList,
        "securityGroupIds": Optional[StringList],
        "ec2KeyPair": Optional[String],
        "instanceRole": Optional[String],
        "tags": Optional[TagsMap],
        "placementGroup": Optional[String],
        "bidPercentage": Optional[Integer],
        "spotIamFleetRole": Optional[String],
        "launchTemplate": Optional[LaunchTemplateSpecification],
        "ec2Configuration": Optional[Ec2ConfigurationList],
    },
    total=False,
)
TagrisTagsMap = Dict[TagKey, TagValue]
ComputeEnvironmentDetail = TypedDict(
    "ComputeEnvironmentDetail",
    {
        "computeEnvironmentName": String,
        "computeEnvironmentArn": String,
        "unmanagedvCpus": Optional[Integer],
        "ecsClusterArn": Optional[String],
        "tags": Optional[TagrisTagsMap],
        "type": Optional[CEType],
        "state": Optional[CEState],
        "status": Optional[CEStatus],
        "statusReason": Optional[String],
        "computeResources": Optional[ComputeResource],
        "serviceRole": Optional[String],
        "updatePolicy": Optional[UpdatePolicy],
    },
    total=False,
)
ComputeEnvironmentDetailList = List[ComputeEnvironmentDetail]


class ComputeEnvironmentOrder(TypedDict, total=False):
    """The order in which compute environments are tried for job placement
    within a queue. Compute environments are tried in ascending order. For
    example, if two compute environments are associated with a job queue,
    the compute environment with a lower order integer value is tried for
    job placement first. Compute environments must be in the ``VALID`` state
    before you can associate them with a job queue. All of the compute
    environments must be either EC2 (``EC2`` or ``SPOT``) or Fargate
    (``FARGATE`` or ``FARGATE_SPOT``); EC2 and Fargate compute environments
    can't be mixed.

    All compute environments that are associated with a job queue must share
    the same architecture. Batch doesn't support mixing compute environment
    architecture types in a single job queue.
    """

    order: Integer
    computeEnvironment: String


ComputeEnvironmentOrders = List[ComputeEnvironmentOrder]
ComputeResourceUpdate = TypedDict(
    "ComputeResourceUpdate",
    {
        "minvCpus": Optional[Integer],
        "maxvCpus": Optional[Integer],
        "desiredvCpus": Optional[Integer],
        "subnets": Optional[StringList],
        "securityGroupIds": Optional[StringList],
        "allocationStrategy": Optional[CRUpdateAllocationStrategy],
        "instanceTypes": Optional[StringList],
        "ec2KeyPair": Optional[String],
        "instanceRole": Optional[String],
        "tags": Optional[TagsMap],
        "placementGroup": Optional[String],
        "bidPercentage": Optional[Integer],
        "launchTemplate": Optional[LaunchTemplateSpecification],
        "ec2Configuration": Optional[Ec2ConfigurationList],
        "updateToLatestImageVersion": Optional[Boolean],
        "type": Optional[CRType],
        "imageId": Optional[String],
    },
    total=False,
)


class FargatePlatformConfiguration(TypedDict, total=False):
    """The platform configuration for jobs that are running on Fargate
    resources. Jobs that run on EC2 resources must not specify this
    parameter.
    """

    platformVersion: Optional[String]


class NetworkConfiguration(TypedDict, total=False):
    """The network configuration for jobs that are running on Fargate
    resources. Jobs that are running on EC2 resources must not specify this
    parameter.
    """

    assignPublicIp: Optional[AssignPublicIp]


class Secret(TypedDict, total=False):
    """An object representing the secret to expose to your container. Secrets
    can be exposed to a container in the following ways:

    -  To inject sensitive data into your containers as environment
       variables, use the ``secrets`` container definition parameter.

    -  To reference sensitive information in the log configuration of a
       container, use the ``secretOptions`` container definition parameter.

    For more information, see `Specifying sensitive
    data <https://docs.aws.amazon.com/batch/latest/userguide/specifying-sensitive-data.html>`__
    in the *Batch User Guide*.
    """

    name: String
    valueFrom: String


SecretList = List[Secret]
LogConfigurationOptionsMap = Dict[String, String]


class LogConfiguration(TypedDict, total=False):
    """Log configuration options to send to a custom log driver for the
    container.
    """

    logDriver: LogDriver
    options: Optional[LogConfigurationOptionsMap]
    secretOptions: Optional[SecretList]


class Tmpfs(TypedDict, total=False):
    """The container path, mount options, and size of the tmpfs mount.

    This object isn't applicable to jobs that are running on Fargate
    resources.
    """

    containerPath: String
    size: Integer
    mountOptions: Optional[StringList]


TmpfsList = List[Tmpfs]
DeviceCgroupPermissions = List[DeviceCgroupPermission]


class Device(TypedDict, total=False):
    """An object representing a container instance host device.

    This object isn't applicable to jobs that are running on Fargate
    resources and shouldn't be provided.
    """

    hostPath: String
    containerPath: Optional[String]
    permissions: Optional[DeviceCgroupPermissions]


DevicesList = List[Device]


class LinuxParameters(TypedDict, total=False):
    """Linux-specific modifications that are applied to the container, such as
    details for device mappings.
    """

    devices: Optional[DevicesList]
    initProcessEnabled: Optional[Boolean]
    sharedMemorySize: Optional[Integer]
    tmpfs: Optional[TmpfsList]
    maxSwap: Optional[Integer]
    swappiness: Optional[Integer]


ResourceRequirement = TypedDict(
    "ResourceRequirement",
    {
        "value": String,
        "type": ResourceType,
    },
    total=False,
)
ResourceRequirements = List[ResourceRequirement]


class Ulimit(TypedDict, total=False):
    """The ``ulimit`` settings to pass to the container.

    This object isn't applicable to jobs that are running on Fargate
    resources.
    """

    hardLimit: Integer
    name: String
    softLimit: Integer


Ulimits = List[Ulimit]


class MountPoint(TypedDict, total=False):
    """Details on a Docker volume mount point that's used in a job's container
    properties. This parameter maps to ``Volumes`` in the `Create a
    container <https://docs.docker.com/engine/reference/api/docker_remote_api_v1.19/#create-a-container>`__
    section of the Docker Remote API and the ``--volume`` option to docker
    run.
    """

    containerPath: Optional[String]
    readOnly: Optional[Boolean]
    sourceVolume: Optional[String]


MountPoints = List[MountPoint]


class KeyValuePair(TypedDict, total=False):
    """A key-value pair object."""

    name: Optional[String]
    value: Optional[String]


EnvironmentVariables = List[KeyValuePair]


class EFSAuthorizationConfig(TypedDict, total=False):
    """The authorization configuration details for the Amazon EFS file system."""

    accessPointId: Optional[String]
    iam: Optional[EFSAuthorizationConfigIAM]


class EFSVolumeConfiguration(TypedDict, total=False):
    """This is used when you're using an Amazon Elastic File System file system
    for job storage. For more information, see `Amazon EFS
    Volumes <https://docs.aws.amazon.com/batch/latest/userguide/efs-volumes.html>`__
    in the *Batch User Guide*.
    """

    fileSystemId: String
    rootDirectory: Optional[String]
    transitEncryption: Optional[EFSTransitEncryption]
    transitEncryptionPort: Optional[Integer]
    authorizationConfig: Optional[EFSAuthorizationConfig]


class Host(TypedDict, total=False):
    """Determine whether your data volume persists on the host container
    instance and where it is stored. If this parameter is empty, then the
    Docker daemon assigns a host path for your data volume, but the data
    isn't guaranteed to persist after the containers associated with it stop
    running.
    """

    sourcePath: Optional[String]


class Volume(TypedDict, total=False):
    """A data volume used in a job's container properties."""

    host: Optional[Host]
    name: Optional[String]
    efsVolumeConfiguration: Optional[EFSVolumeConfiguration]


Volumes = List[Volume]


class ContainerDetail(TypedDict, total=False):
    """An object representing the details of a container that's part of a job."""

    image: Optional[String]
    vcpus: Optional[Integer]
    memory: Optional[Integer]
    command: Optional[StringList]
    jobRoleArn: Optional[String]
    executionRoleArn: Optional[String]
    volumes: Optional[Volumes]
    environment: Optional[EnvironmentVariables]
    mountPoints: Optional[MountPoints]
    readonlyRootFilesystem: Optional[Boolean]
    ulimits: Optional[Ulimits]
    privileged: Optional[Boolean]
    user: Optional[String]
    exitCode: Optional[Integer]
    reason: Optional[String]
    containerInstanceArn: Optional[String]
    taskArn: Optional[String]
    logStreamName: Optional[String]
    instanceType: Optional[String]
    networkInterfaces: Optional[NetworkInterfaceList]
    resourceRequirements: Optional[ResourceRequirements]
    linuxParameters: Optional[LinuxParameters]
    logConfiguration: Optional[LogConfiguration]
    secrets: Optional[SecretList]
    networkConfiguration: Optional[NetworkConfiguration]
    fargatePlatformConfiguration: Optional[FargatePlatformConfiguration]


class ContainerOverrides(TypedDict, total=False):
    """The overrides that should be sent to a container."""

    vcpus: Optional[Integer]
    memory: Optional[Integer]
    command: Optional[StringList]
    instanceType: Optional[String]
    environment: Optional[EnvironmentVariables]
    resourceRequirements: Optional[ResourceRequirements]


class ContainerProperties(TypedDict, total=False):
    """Container properties are used in job definitions to describe the
    container that's launched as part of a job.
    """

    image: Optional[String]
    vcpus: Optional[Integer]
    memory: Optional[Integer]
    command: Optional[StringList]
    jobRoleArn: Optional[String]
    executionRoleArn: Optional[String]
    volumes: Optional[Volumes]
    environment: Optional[EnvironmentVariables]
    mountPoints: Optional[MountPoints]
    readonlyRootFilesystem: Optional[Boolean]
    privileged: Optional[Boolean]
    ulimits: Optional[Ulimits]
    user: Optional[String]
    instanceType: Optional[String]
    resourceRequirements: Optional[ResourceRequirements]
    linuxParameters: Optional[LinuxParameters]
    logConfiguration: Optional[LogConfiguration]
    secrets: Optional[SecretList]
    networkConfiguration: Optional[NetworkConfiguration]
    fargatePlatformConfiguration: Optional[FargatePlatformConfiguration]


class ContainerSummary(TypedDict, total=False):
    """An object representing summary details of a container within a job."""

    exitCode: Optional[Integer]
    reason: Optional[String]


CreateComputeEnvironmentRequest = TypedDict(
    "CreateComputeEnvironmentRequest",
    {
        "computeEnvironmentName": String,
        "type": CEType,
        "state": Optional[CEState],
        "unmanagedvCpus": Optional[Integer],
        "computeResources": Optional[ComputeResource],
        "serviceRole": Optional[String],
        "tags": Optional[TagrisTagsMap],
    },
    total=False,
)


class CreateComputeEnvironmentResponse(TypedDict, total=False):
    computeEnvironmentName: Optional[String]
    computeEnvironmentArn: Optional[String]


class CreateJobQueueRequest(ServiceRequest):
    """Contains the parameters for ``CreateJobQueue``."""

    jobQueueName: String
    state: Optional[JQState]
    schedulingPolicyArn: Optional[String]
    priority: Integer
    computeEnvironmentOrder: ComputeEnvironmentOrders
    tags: Optional[TagrisTagsMap]


class CreateJobQueueResponse(TypedDict, total=False):
    jobQueueName: String
    jobQueueArn: String


class ShareAttributes(TypedDict, total=False):
    """Specifies the weights for the fair share identifiers for the fair share
    policy. Fair share identifiers that aren't included have a default
    weight of ``1.0``.
    """

    shareIdentifier: String
    weightFactor: Optional[Float]


ShareAttributesList = List[ShareAttributes]


class FairsharePolicy(TypedDict, total=False):
    """The fair share policy for a scheduling policy."""

    shareDecaySeconds: Optional[Integer]
    computeReservation: Optional[Integer]
    shareDistribution: Optional[ShareAttributesList]


class CreateSchedulingPolicyRequest(ServiceRequest):
    """Contains the parameters for ``CreateSchedulingPolicy``."""

    name: String
    fairsharePolicy: Optional[FairsharePolicy]
    tags: Optional[TagrisTagsMap]


class CreateSchedulingPolicyResponse(TypedDict, total=False):
    name: String
    arn: String


class DeleteComputeEnvironmentRequest(ServiceRequest):
    """Contains the parameters for ``DeleteComputeEnvironment``."""

    computeEnvironment: String


class DeleteComputeEnvironmentResponse(TypedDict, total=False):
    pass


class DeleteJobQueueRequest(ServiceRequest):
    """Contains the parameters for ``DeleteJobQueue``."""

    jobQueue: String


class DeleteJobQueueResponse(TypedDict, total=False):
    pass


class DeleteSchedulingPolicyRequest(ServiceRequest):
    """Contains the parameters for ``DeleteSchedulingPolicy``."""

    arn: String


class DeleteSchedulingPolicyResponse(TypedDict, total=False):
    pass


class DeregisterJobDefinitionRequest(ServiceRequest):
    jobDefinition: String


class DeregisterJobDefinitionResponse(TypedDict, total=False):
    pass


class DescribeComputeEnvironmentsRequest(ServiceRequest):
    """Contains the parameters for ``DescribeComputeEnvironments``."""

    computeEnvironments: Optional[StringList]
    maxResults: Optional[Integer]
    nextToken: Optional[String]


class DescribeComputeEnvironmentsResponse(TypedDict, total=False):
    computeEnvironments: Optional[ComputeEnvironmentDetailList]
    nextToken: Optional[String]


class DescribeJobDefinitionsRequest(ServiceRequest):
    """Contains the parameters for ``DescribeJobDefinitions``."""

    jobDefinitions: Optional[StringList]
    maxResults: Optional[Integer]
    jobDefinitionName: Optional[String]
    status: Optional[String]
    nextToken: Optional[String]


PlatformCapabilityList = List[PlatformCapability]


class NodeRangeProperty(TypedDict, total=False):
    """An object representing the properties of the node range for a multi-node
    parallel job.
    """

    targetNodes: String
    container: Optional[ContainerProperties]


NodeRangeProperties = List[NodeRangeProperty]


class NodeProperties(TypedDict, total=False):
    """An object representing the node properties of a multi-node parallel job."""

    numNodes: Integer
    mainNode: Integer
    nodeRangeProperties: NodeRangeProperties


class JobTimeout(TypedDict, total=False):
    """An object representing a job timeout configuration."""

    attemptDurationSeconds: Optional[Integer]


class EvaluateOnExit(TypedDict, total=False):
    """Specifies a set of conditions to be met, and an action to take
    (``RETRY`` or ``EXIT``) if all conditions are met.
    """

    onStatusReason: Optional[String]
    onReason: Optional[String]
    onExitCode: Optional[String]
    action: RetryAction


EvaluateOnExitList = List[EvaluateOnExit]


class RetryStrategy(TypedDict, total=False):
    """The retry strategy associated with a job. For more information, see
    `Automated job
    retries <https://docs.aws.amazon.com/batch/latest/userguide/job_retries.html>`__
    in the *Batch User Guide*.
    """

    attempts: Optional[Integer]
    evaluateOnExit: Optional[EvaluateOnExitList]


ParametersMap = Dict[String, String]
JobDefinition = TypedDict(
    "JobDefinition",
    {
        "jobDefinitionName": String,
        "jobDefinitionArn": String,
        "revision": Integer,
        "status": Optional[String],
        "type": String,
        "schedulingPriority": Optional[Integer],
        "parameters": Optional[ParametersMap],
        "retryStrategy": Optional[RetryStrategy],
        "containerProperties": Optional[ContainerProperties],
        "timeout": Optional[JobTimeout],
        "nodeProperties": Optional[NodeProperties],
        "tags": Optional[TagrisTagsMap],
        "propagateTags": Optional[Boolean],
        "platformCapabilities": Optional[PlatformCapabilityList],
    },
    total=False,
)
JobDefinitionList = List[JobDefinition]


class DescribeJobDefinitionsResponse(TypedDict, total=False):
    jobDefinitions: Optional[JobDefinitionList]
    nextToken: Optional[String]


class DescribeJobQueuesRequest(ServiceRequest):
    """Contains the parameters for ``DescribeJobQueues``."""

    jobQueues: Optional[StringList]
    maxResults: Optional[Integer]
    nextToken: Optional[String]


class JobQueueDetail(TypedDict, total=False):
    """An object representing the details of an Batch job queue."""

    jobQueueName: String
    jobQueueArn: String
    state: JQState
    schedulingPolicyArn: Optional[String]
    status: Optional[JQStatus]
    statusReason: Optional[String]
    priority: Integer
    computeEnvironmentOrder: ComputeEnvironmentOrders
    tags: Optional[TagrisTagsMap]


JobQueueDetailList = List[JobQueueDetail]


class DescribeJobQueuesResponse(TypedDict, total=False):
    jobQueues: Optional[JobQueueDetailList]
    nextToken: Optional[String]


class DescribeJobsRequest(ServiceRequest):
    """Contains the parameters for ``DescribeJobs``."""

    jobs: StringList


class NodeDetails(TypedDict, total=False):
    """An object representing the details of a multi-node parallel job node."""

    nodeIndex: Optional[Integer]
    isMainNode: Optional[Boolean]


JobDependency = TypedDict(
    "JobDependency",
    {
        "jobId": Optional[String],
        "type": Optional[ArrayJobDependency],
    },
    total=False,
)
JobDependencyList = List[JobDependency]


class JobDetail(TypedDict, total=False):
    """An object representing an Batch job."""

    jobArn: Optional[String]
    jobName: String
    jobId: String
    jobQueue: String
    status: JobStatus
    shareIdentifier: Optional[String]
    schedulingPriority: Optional[Integer]
    attempts: Optional[AttemptDetails]
    statusReason: Optional[String]
    createdAt: Optional[Long]
    retryStrategy: Optional[RetryStrategy]
    startedAt: Long
    stoppedAt: Optional[Long]
    dependsOn: Optional[JobDependencyList]
    jobDefinition: String
    parameters: Optional[ParametersMap]
    container: Optional[ContainerDetail]
    nodeDetails: Optional[NodeDetails]
    nodeProperties: Optional[NodeProperties]
    arrayProperties: Optional[ArrayPropertiesDetail]
    timeout: Optional[JobTimeout]
    tags: Optional[TagrisTagsMap]
    propagateTags: Optional[Boolean]
    platformCapabilities: Optional[PlatformCapabilityList]


JobDetailList = List[JobDetail]


class DescribeJobsResponse(TypedDict, total=False):
    jobs: Optional[JobDetailList]


class DescribeSchedulingPoliciesRequest(ServiceRequest):
    """Contains the parameters for ``DescribeSchedulingPolicies``."""

    arns: StringList


class SchedulingPolicyDetail(TypedDict, total=False):
    """An object that represents a scheduling policy."""

    name: String
    arn: String
    fairsharePolicy: Optional[FairsharePolicy]
    tags: Optional[TagrisTagsMap]


SchedulingPolicyDetailList = List[SchedulingPolicyDetail]


class DescribeSchedulingPoliciesResponse(TypedDict, total=False):
    schedulingPolicies: Optional[SchedulingPolicyDetailList]


class NodePropertiesSummary(TypedDict, total=False):
    """An object representing the properties of a node that's associated with a
    multi-node parallel job.
    """

    isMainNode: Optional[Boolean]
    numNodes: Optional[Integer]
    nodeIndex: Optional[Integer]


class JobSummary(TypedDict, total=False):
    """An object representing summary details of a job."""

    jobArn: Optional[String]
    jobId: String
    jobName: String
    createdAt: Optional[Long]
    status: Optional[JobStatus]
    statusReason: Optional[String]
    startedAt: Optional[Long]
    stoppedAt: Optional[Long]
    container: Optional[ContainerSummary]
    arrayProperties: Optional[ArrayPropertiesSummary]
    nodeProperties: Optional[NodePropertiesSummary]
    jobDefinition: Optional[String]


JobSummaryList = List[JobSummary]


class KeyValuesPair(TypedDict, total=False):
    """A filter name and value pair that's used to return a more specific list
    of results from a ``ListJobs`` API operation.
    """

    name: Optional[String]
    values: Optional[StringList]


ListJobsFilterList = List[KeyValuesPair]


class ListJobsRequest(ServiceRequest):
    """Contains the parameters for ``ListJobs``."""

    jobQueue: Optional[String]
    arrayJobId: Optional[String]
    multiNodeJobId: Optional[String]
    jobStatus: Optional[JobStatus]
    maxResults: Optional[Integer]
    nextToken: Optional[String]
    filters: Optional[ListJobsFilterList]


class ListJobsResponse(TypedDict, total=False):
    jobSummaryList: JobSummaryList
    nextToken: Optional[String]


class ListSchedulingPoliciesRequest(ServiceRequest):
    """Contains the parameters for ``ListSchedulingPolicies``."""

    maxResults: Optional[Integer]
    nextToken: Optional[String]


class SchedulingPolicyListingDetail(TypedDict, total=False):
    """An object that contains the details of a scheduling policy that's
    returned in a ``ListSchedulingPolicy`` action.
    """

    arn: String


SchedulingPolicyListingDetailList = List[SchedulingPolicyListingDetail]


class ListSchedulingPoliciesResponse(TypedDict, total=False):
    schedulingPolicies: Optional[SchedulingPolicyListingDetailList]
    nextToken: Optional[String]


class ListTagsForResourceRequest(ServiceRequest):
    """Contains the parameters for ``ListTagsForResource``."""

    resourceArn: String


class ListTagsForResourceResponse(TypedDict, total=False):
    tags: Optional[TagrisTagsMap]


class NodePropertyOverride(TypedDict, total=False):
    """Object representing any node overrides to a job definition that's used
    in a SubmitJob API operation.
    """

    targetNodes: String
    containerOverrides: Optional[ContainerOverrides]


NodePropertyOverrides = List[NodePropertyOverride]


class NodeOverrides(TypedDict, total=False):
    """Object representing any node overrides to a job definition that's used
    in a SubmitJob API operation.

    This isn't applicable to jobs that are running on Fargate resources and
    shouldn't be provided; use ``containerOverrides`` instead.
    """

    numNodes: Optional[Integer]
    nodePropertyOverrides: Optional[NodePropertyOverrides]


RegisterJobDefinitionRequest = TypedDict(
    "RegisterJobDefinitionRequest",
    {
        "jobDefinitionName": String,
        "type": JobDefinitionType,
        "parameters": Optional[ParametersMap],
        "schedulingPriority": Optional[Integer],
        "containerProperties": Optional[ContainerProperties],
        "nodeProperties": Optional[NodeProperties],
        "retryStrategy": Optional[RetryStrategy],
        "propagateTags": Optional[Boolean],
        "timeout": Optional[JobTimeout],
        "tags": Optional[TagrisTagsMap],
        "platformCapabilities": Optional[PlatformCapabilityList],
    },
    total=False,
)


class RegisterJobDefinitionResponse(TypedDict, total=False):
    jobDefinitionName: String
    jobDefinitionArn: String
    revision: Integer


class SubmitJobRequest(ServiceRequest):
    """Contains the parameters for ``SubmitJob``."""

    jobName: String
    jobQueue: String
    shareIdentifier: Optional[String]
    schedulingPriorityOverride: Optional[Integer]
    arrayProperties: Optional[ArrayProperties]
    dependsOn: Optional[JobDependencyList]
    jobDefinition: String
    parameters: Optional[ParametersMap]
    containerOverrides: Optional[ContainerOverrides]
    nodeOverrides: Optional[NodeOverrides]
    retryStrategy: Optional[RetryStrategy]
    propagateTags: Optional[Boolean]
    timeout: Optional[JobTimeout]
    tags: Optional[TagrisTagsMap]


class SubmitJobResponse(TypedDict, total=False):
    jobArn: Optional[String]
    jobName: String
    jobId: String


TagKeysList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    """Contains the parameters for ``TagResource``."""

    resourceArn: String
    tags: TagrisTagsMap


class TagResourceResponse(TypedDict, total=False):
    pass


class TerminateJobRequest(ServiceRequest):
    """Contains the parameters for ``TerminateJob``."""

    jobId: String
    reason: String


class TerminateJobResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    """Contains the parameters for ``UntagResource``."""

    resourceArn: String
    tagKeys: TagKeysList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateComputeEnvironmentRequest(ServiceRequest):
    """Contains the parameters for ``UpdateComputeEnvironment``."""

    computeEnvironment: String
    state: Optional[CEState]
    unmanagedvCpus: Optional[Integer]
    computeResources: Optional[ComputeResourceUpdate]
    serviceRole: Optional[String]
    updatePolicy: Optional[UpdatePolicy]


class UpdateComputeEnvironmentResponse(TypedDict, total=False):
    computeEnvironmentName: Optional[String]
    computeEnvironmentArn: Optional[String]


class UpdateJobQueueRequest(ServiceRequest):
    """Contains the parameters for ``UpdateJobQueue``."""

    jobQueue: String
    state: Optional[JQState]
    schedulingPolicyArn: Optional[String]
    priority: Optional[Integer]
    computeEnvironmentOrder: Optional[ComputeEnvironmentOrders]


class UpdateJobQueueResponse(TypedDict, total=False):
    jobQueueName: Optional[String]
    jobQueueArn: Optional[String]


class UpdateSchedulingPolicyRequest(ServiceRequest):
    """Contains the parameters for ``UpdateSchedulingPolicy``."""

    arn: String
    fairsharePolicy: Optional[FairsharePolicy]


class UpdateSchedulingPolicyResponse(TypedDict, total=False):
    pass


class BatchApi:

    service = "batch"
    version = "2016-08-10"

    @handler("CancelJob")
    def cancel_job(
        self, context: RequestContext, job_id: String, reason: String
    ) -> CancelJobResponse:
        """Cancels a job in an Batch job queue. Jobs that are in the ``SUBMITTED``,
        ``PENDING``, or ``RUNNABLE`` state are canceled. Jobs that have
        progressed to ``STARTING`` or ``RUNNING`` aren't canceled, but the API
        operation still succeeds, even if no job is canceled. These jobs must be
        terminated with the TerminateJob operation.

        :param job_id: The Batch job ID of the job to cancel.
        :param reason: A message to attach to the job that explains the reason for canceling
        it.
        :returns: CancelJobResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("CreateComputeEnvironment", expand=False)
    def create_compute_environment(
        self, context: RequestContext, request: CreateComputeEnvironmentRequest
    ) -> CreateComputeEnvironmentResponse:
        """Creates an Batch compute environment. You can create ``MANAGED`` or
        ``UNMANAGED`` compute environments. ``MANAGED`` compute environments can
        use Amazon EC2 or Fargate resources. ``UNMANAGED`` compute environments
        can only use EC2 resources.

        In a managed compute environment, Batch manages the capacity and
        instance types of the compute resources within the environment. This is
        based on the compute resource specification that you define or the
        `launch
        template <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-templates.html>`__
        that you specify when you create the compute environment. Either, you
        can choose to use EC2 On-Demand Instances and EC2 Spot Instances. Or,
        you can use Fargate and Fargate Spot capacity in your managed compute
        environment. You can optionally set a maximum price so that Spot
        Instances only launch when the Spot Instance price is less than a
        specified percentage of the On-Demand price.

        Multi-node parallel jobs aren't supported on Spot Instances.

        In an unmanaged compute environment, you can manage your own EC2 compute
        resources and have a lot of flexibility with how you configure your
        compute resources. For example, you can use custom AMIs. However, you
        must verify that each of your AMIs meet the Amazon ECS container
        instance AMI specification. For more information, see `container
        instance
        AMIs <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/container_instance_AMIs.html>`__
        in the *Amazon Elastic Container Service Developer Guide*. After you
        created your unmanaged compute environment, you can use the
        DescribeComputeEnvironments operation to find the Amazon ECS cluster
        that's associated with it. Then, launch your container instances into
        that Amazon ECS cluster. For more information, see `Launching an Amazon
        ECS container
        instance <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_container_instance.html>`__
        in the *Amazon Elastic Container Service Developer Guide*.

        Batch doesn't upgrade the AMIs in a compute environment after the
        environment is created. For example, it doesn't update the AMIs when a
        newer version of the Amazon ECS optimized AMI is available. Therefore,
        you're responsible for managing the guest operating system (including
        its updates and security patches) and any additional application
        software or utilities that you install on the compute resources. To use
        a new AMI for your Batch jobs, complete these steps:

        #. Create a new compute environment with the new AMI.

        #. Add the compute environment to an existing job queue.

        #. Remove the earlier compute environment from your job queue.

        #. Delete the earlier compute environment.

        :param compute_environment_name: The name for your compute environment.
        :param type: The type of the compute environment: ``MANAGED`` or ``UNMANAGED``.
        :param state: The state of the compute environment.
        :param unmanagedv_cpus: The maximum number of vCPUs for an unmanaged compute environment.
        :param compute_resources: Details about the compute resources managed by the compute environment.
        :param service_role: The full Amazon Resource Name (ARN) of the IAM role that allows Batch to
        make calls to other Amazon Web Services services on your behalf.
        :param tags: The tags that you apply to the compute environment to help you
        categorize and organize your resources.
        :returns: CreateComputeEnvironmentResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("CreateJobQueue")
    def create_job_queue(
        self,
        context: RequestContext,
        job_queue_name: String,
        priority: Integer,
        compute_environment_order: ComputeEnvironmentOrders,
        state: JQState = None,
        scheduling_policy_arn: String = None,
        tags: TagrisTagsMap = None,
    ) -> CreateJobQueueResponse:
        """Creates an Batch job queue. When you create a job queue, you associate
        one or more compute environments to the queue and assign an order of
        preference for the compute environments.

        You also set a priority to the job queue that determines the order that
        the Batch scheduler places jobs onto its associated compute
        environments. For example, if a compute environment is associated with
        more than one job queue, the job queue with a higher priority is given
        preference for scheduling jobs to that compute environment.

        :param job_queue_name: The name of the job queue.
        :param priority: The priority of the job queue.
        :param compute_environment_order: The set of compute environments mapped to a job queue and their order
        relative to each other.
        :param state: The state of the job queue.
        :param scheduling_policy_arn: The Amazon Resource Name (ARN) of the fair share scheduling policy.
        :param tags: The tags that you apply to the job queue to help you categorize and
        organize your resources.
        :returns: CreateJobQueueResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("CreateSchedulingPolicy")
    def create_scheduling_policy(
        self,
        context: RequestContext,
        name: String,
        fairshare_policy: FairsharePolicy = None,
        tags: TagrisTagsMap = None,
    ) -> CreateSchedulingPolicyResponse:
        """Creates an Batch scheduling policy.

        :param name: The name of the scheduling policy.
        :param fairshare_policy: The fair share policy of the scheduling policy.
        :param tags: The tags that you apply to the scheduling policy to help you categorize
        and organize your resources.
        :returns: CreateSchedulingPolicyResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DeleteComputeEnvironment")
    def delete_compute_environment(
        self, context: RequestContext, compute_environment: String
    ) -> DeleteComputeEnvironmentResponse:
        """Deletes an Batch compute environment.

        Before you can delete a compute environment, you must set its state to
        ``DISABLED`` with the UpdateComputeEnvironment API operation and
        disassociate it from any job queues with the UpdateJobQueue API
        operation. Compute environments that use Fargate resources must
        terminate all active jobs on that compute environment before deleting
        the compute environment. If this isn't done, the compute environment
        enters an invalid state.

        :param compute_environment: The name or Amazon Resource Name (ARN) of the compute environment to
        delete.
        :returns: DeleteComputeEnvironmentResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DeleteJobQueue")
    def delete_job_queue(
        self, context: RequestContext, job_queue: String
    ) -> DeleteJobQueueResponse:
        """Deletes the specified job queue. You must first disable submissions for
        a queue with the UpdateJobQueue operation. All jobs in the queue are
        eventually terminated when you delete a job queue. The jobs are
        terminated at a rate of about 16 jobs each second.

        It's not necessary to disassociate compute environments from a queue
        before submitting a ``DeleteJobQueue`` request.

        :param job_queue: The short name or full Amazon Resource Name (ARN) of the queue to
        delete.
        :returns: DeleteJobQueueResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DeleteSchedulingPolicy")
    def delete_scheduling_policy(
        self, context: RequestContext, arn: String
    ) -> DeleteSchedulingPolicyResponse:
        """Deletes the specified scheduling policy.

        You can't delete a scheduling policy that's used in any job queues.

        :param arn: The Amazon Resource Name (ARN) of the scheduling policy to delete.
        :returns: DeleteSchedulingPolicyResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DeregisterJobDefinition")
    def deregister_job_definition(
        self, context: RequestContext, job_definition: String
    ) -> DeregisterJobDefinitionResponse:
        """Deregisters an Batch job definition. Job definitions are permanently
        deleted after 180 days.

        :param job_definition: The name and revision (``name:revision``) or full Amazon Resource Name
        (ARN) of the job definition to deregister.
        :returns: DeregisterJobDefinitionResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DescribeComputeEnvironments")
    def describe_compute_environments(
        self,
        context: RequestContext,
        compute_environments: StringList = None,
        max_results: Integer = None,
        next_token: String = None,
    ) -> DescribeComputeEnvironmentsResponse:
        """Describes one or more of your compute environments.

        If you're using an unmanaged compute environment, you can use the
        ``DescribeComputeEnvironment`` operation to determine the
        ``ecsClusterArn`` that you launch your Amazon ECS container instances
        into.

        :param compute_environments: A list of up to 100 compute environment names or full Amazon Resource
        Name (ARN) entries.
        :param max_results: The maximum number of cluster results returned by
        ``DescribeComputeEnvironments`` in paginated output.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``DescribeComputeEnvironments`` request where ``maxResults`` was used
        and the results exceeded the value of that parameter.
        :returns: DescribeComputeEnvironmentsResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DescribeJobDefinitions")
    def describe_job_definitions(
        self,
        context: RequestContext,
        job_definitions: StringList = None,
        max_results: Integer = None,
        job_definition_name: String = None,
        status: String = None,
        next_token: String = None,
    ) -> DescribeJobDefinitionsResponse:
        """Describes a list of job definitions. You can specify a ``status`` (such
        as ``ACTIVE``) to only return job definitions that match that status.

        :param job_definitions: A list of up to 100 job definitions.
        :param max_results: The maximum number of results returned by ``DescribeJobDefinitions`` in
        paginated output.
        :param job_definition_name: The name of the job definition to describe.
        :param status: The status used to filter job definitions.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``DescribeJobDefinitions`` request where ``maxResults`` was used and the
        results exceeded the value of that parameter.
        :returns: DescribeJobDefinitionsResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DescribeJobQueues")
    def describe_job_queues(
        self,
        context: RequestContext,
        job_queues: StringList = None,
        max_results: Integer = None,
        next_token: String = None,
    ) -> DescribeJobQueuesResponse:
        """Describes one or more of your job queues.

        :param job_queues: A list of up to 100 queue names or full queue Amazon Resource Name (ARN)
        entries.
        :param max_results: The maximum number of results returned by ``DescribeJobQueues`` in
        paginated output.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``DescribeJobQueues`` request where ``maxResults`` was used and the
        results exceeded the value of that parameter.
        :returns: DescribeJobQueuesResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DescribeJobs")
    def describe_jobs(self, context: RequestContext, jobs: StringList) -> DescribeJobsResponse:
        """Describes a list of Batch jobs.

        :param jobs: A list of up to 100 job IDs.
        :returns: DescribeJobsResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DescribeSchedulingPolicies")
    def describe_scheduling_policies(
        self, context: RequestContext, arns: StringList
    ) -> DescribeSchedulingPoliciesResponse:
        """Describes one or more of your scheduling policies.

        :param arns: A list of up to 100 scheduling policy Amazon Resource Name (ARN)
        entries.
        :returns: DescribeSchedulingPoliciesResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("ListJobs")
    def list_jobs(
        self,
        context: RequestContext,
        job_queue: String = None,
        array_job_id: String = None,
        multi_node_job_id: String = None,
        job_status: JobStatus = None,
        max_results: Integer = None,
        next_token: String = None,
        filters: ListJobsFilterList = None,
    ) -> ListJobsResponse:
        """Returns a list of Batch jobs.

        You must specify only one of the following items:

        -  A job queue ID to return a list of jobs in that job queue

        -  A multi-node parallel job ID to return a list of nodes for that job

        -  An array job ID to return a list of the children for that job

        You can filter the results by job status with the ``jobStatus``
        parameter. If you don't specify a status, only ``RUNNING`` jobs are
        returned.

        :param job_queue: The name or full Amazon Resource Name (ARN) of the job queue used to
        list jobs.
        :param array_job_id: The job ID for an array job.
        :param multi_node_job_id: The job ID for a multi-node parallel job.
        :param job_status: The job status used to filter jobs in the specified queue.
        :param max_results: The maximum number of results returned by ``ListJobs`` in paginated
        output.
        :param next_token: The ``nextToken`` value returned from a previous paginated ``ListJobs``
        request where ``maxResults`` was used and the results exceeded the value
        of that parameter.
        :param filters: The filter to apply to the query.
        :returns: ListJobsResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("ListSchedulingPolicies")
    def list_scheduling_policies(
        self, context: RequestContext, max_results: Integer = None, next_token: String = None
    ) -> ListSchedulingPoliciesResponse:
        """Returns a list of Batch scheduling policies.

        :param max_results: The maximum number of results that's returned by
        ``ListSchedulingPolicies`` in paginated output.
        :param next_token: The ``nextToken`` value that's returned from a previous paginated
        ``ListSchedulingPolicies`` request where ``maxResults`` was used and the
        results exceeded the value of that parameter.
        :returns: ListSchedulingPoliciesResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: String
    ) -> ListTagsForResourceResponse:
        """Lists the tags for an Batch resource. Batch resources that support tags
        are compute environments, jobs, job definitions, job queues, and
        scheduling policies. ARNs for child jobs of array and multi-node
        parallel (MNP) jobs are not supported.

        :param resource_arn: The Amazon Resource Name (ARN) that identifies the resource that tags
        are listed for.
        :returns: ListTagsForResourceResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("RegisterJobDefinition", expand=False)
    def register_job_definition(
        self, context: RequestContext, request: RegisterJobDefinitionRequest
    ) -> RegisterJobDefinitionResponse:
        """Registers an Batch job definition.

        :param job_definition_name: The name of the job definition to register.
        :param type: The type of job definition.
        :param parameters: Default parameter substitution placeholders to set in the job
        definition.
        :param scheduling_priority: The scheduling priority for jobs that are submitted with this job
        definition.
        :param container_properties: An object with various properties specific to single-node
        container-based jobs.
        :param node_properties: An object with various properties specific to multi-node parallel jobs.
        :param retry_strategy: The retry strategy to use for failed jobs that are submitted with this
        job definition.
        :param propagate_tags: Specifies whether to propagate the tags from the job or job definition
        to the corresponding Amazon ECS task.
        :param timeout: The timeout configuration for jobs that are submitted with this job
        definition, after which Batch terminates your jobs if they have not
        finished.
        :param tags: The tags that you apply to the job definition to help you categorize and
        organize your resources.
        :param platform_capabilities: The platform capabilities required by the job definition.
        :returns: RegisterJobDefinitionResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("SubmitJob")
    def submit_job(
        self,
        context: RequestContext,
        job_name: String,
        job_queue: String,
        job_definition: String,
        share_identifier: String = None,
        scheduling_priority_override: Integer = None,
        array_properties: ArrayProperties = None,
        depends_on: JobDependencyList = None,
        parameters: ParametersMap = None,
        container_overrides: ContainerOverrides = None,
        node_overrides: NodeOverrides = None,
        retry_strategy: RetryStrategy = None,
        propagate_tags: Boolean = None,
        timeout: JobTimeout = None,
        tags: TagrisTagsMap = None,
    ) -> SubmitJobResponse:
        """Submits an Batch job from a job definition. Parameters that are
        specified during SubmitJob override parameters defined in the job
        definition. vCPU and memory requirements that are specified in the
        ``resourceRequirements`` objects in the job definition are the
        exception. They can't be overridden this way using the ``memory`` and
        ``vcpus`` parameters. Rather, you must specify updates to job definition
        parameters in a ``resourceRequirements`` object that's included in the
        ``containerOverrides`` parameter.

        Job queues with a scheduling policy are limited to 500 active fair share
        identifiers at a time.

        Jobs that run on Fargate resources can't be guaranteed to run for more
        than 14 days. This is because, after 14 days, Fargate resources might
        become unavailable and job might be terminated.

        :param job_name: The name of the job.
        :param job_queue: The job queue where the job is submitted.
        :param job_definition: The job definition used by this job.
        :param share_identifier: The share identifier for the job.
        :param scheduling_priority_override: The scheduling priority for the job.
        :param array_properties: The array properties for the submitted job, such as the size of the
        array.
        :param depends_on: A list of dependencies for the job.
        :param parameters: Additional parameters passed to the job that replace parameter
        substitution placeholders that are set in the job definition.
        :param container_overrides: A list of container overrides in the JSON format that specify the name
        of a container in the specified job definition and the overrides it
        receives.
        :param node_overrides: A list of node overrides in JSON format that specify the node range to
        target and the container overrides for that node range.
        :param retry_strategy: The retry strategy to use for failed jobs from this SubmitJob operation.
        :param propagate_tags: Specifies whether to propagate the tags from the job or job definition
        to the corresponding Amazon ECS task.
        :param timeout: The timeout configuration for this SubmitJob operation.
        :param tags: The tags that you apply to the job request to help you categorize and
        organize your resources.
        :returns: SubmitJobResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: String, tags: TagrisTagsMap
    ) -> TagResourceResponse:
        """Associates the specified tags to a resource with the specified
        ``resourceArn``. If existing tags on a resource aren't specified in the
        request parameters, they aren't changed. When a resource is deleted, the
        tags that are associated with that resource are deleted as well. Batch
        resources that support tags are compute environments, jobs, job
        definitions, job queues, and scheduling policies. ARNs for child jobs of
        array and multi-node parallel (MNP) jobs are not supported.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource that tags are added to.
        :param tags: The tags that you apply to the resource to help you categorize and
        organize your resources.
        :returns: TagResourceResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("TerminateJob")
    def terminate_job(
        self, context: RequestContext, job_id: String, reason: String
    ) -> TerminateJobResponse:
        """Terminates a job in a job queue. Jobs that are in the ``STARTING`` or
        ``RUNNING`` state are terminated, which causes them to transition to
        ``FAILED``. Jobs that have not progressed to the ``STARTING`` state are
        cancelled.

        :param job_id: The Batch job ID of the job to terminate.
        :param reason: A message to attach to the job that explains the reason for canceling
        it.
        :returns: TerminateJobResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: String, tag_keys: TagKeysList
    ) -> UntagResourceResponse:
        """Deletes specified tags from an Batch resource.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource from which to delete
        tags.
        :param tag_keys: The keys of the tags to be removed.
        :returns: UntagResourceResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("UpdateComputeEnvironment")
    def update_compute_environment(
        self,
        context: RequestContext,
        compute_environment: String,
        state: CEState = None,
        unmanagedv_cpus: Integer = None,
        compute_resources: ComputeResourceUpdate = None,
        service_role: String = None,
        update_policy: UpdatePolicy = None,
    ) -> UpdateComputeEnvironmentResponse:
        """Updates an Batch compute environment.

        :param compute_environment: The name or full Amazon Resource Name (ARN) of the compute environment
        to update.
        :param state: The state of the compute environment.
        :param unmanagedv_cpus: The maximum number of vCPUs expected to be used for an unmanaged compute
        environment.
        :param compute_resources: Details of the compute resources managed by the compute environment.
        :param service_role: The full Amazon Resource Name (ARN) of the IAM role that allows Batch to
        make calls to other Amazon Web Services services on your behalf.
        :param update_policy: Specifies the updated infrastructure update policy for the compute
        environment.
        :returns: UpdateComputeEnvironmentResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("UpdateJobQueue")
    def update_job_queue(
        self,
        context: RequestContext,
        job_queue: String,
        state: JQState = None,
        scheduling_policy_arn: String = None,
        priority: Integer = None,
        compute_environment_order: ComputeEnvironmentOrders = None,
    ) -> UpdateJobQueueResponse:
        """Updates a job queue.

        :param job_queue: The name or the Amazon Resource Name (ARN) of the job queue.
        :param state: Describes the queue's ability to accept new jobs.
        :param scheduling_policy_arn: Amazon Resource Name (ARN) of the fair share scheduling policy.
        :param priority: The priority of the job queue.
        :param compute_environment_order: Details the set of compute environments mapped to a job queue and their
        order relative to each other.
        :returns: UpdateJobQueueResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("UpdateSchedulingPolicy")
    def update_scheduling_policy(
        self, context: RequestContext, arn: String, fairshare_policy: FairsharePolicy = None
    ) -> UpdateSchedulingPolicyResponse:
        """Updates a scheduling policy.

        :param arn: The Amazon Resource Name (ARN) of the scheduling policy to update.
        :param fairshare_policy: The fair share policy.
        :returns: UpdateSchedulingPolicyResponse
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError
