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
Capacity = int
ClusterName = str
DescribeAddonVersionsRequestMaxResults = int
FargateProfilesRequestMaxResults = int
ListAddonsRequestMaxResults = int
ListClustersRequestMaxResults = int
ListIdentityProviderConfigsRequestMaxResults = int
ListNodegroupsRequestMaxResults = int
ListUpdatesRequestMaxResults = int
NonZeroInteger = int
PercentCapacity = int
RoleArn = str
String = str
TagKey = str
TagValue = str
ZeroCapacity = int
labelKey = str
labelValue = str
requiredClaimsKey = str
requiredClaimsValue = str
taintKey = str
taintValue = str


class AMITypes(str):
    AL2_x86_64 = "AL2_x86_64"
    AL2_x86_64_GPU = "AL2_x86_64_GPU"
    AL2_ARM_64 = "AL2_ARM_64"
    CUSTOM = "CUSTOM"
    BOTTLEROCKET_ARM_64 = "BOTTLEROCKET_ARM_64"
    BOTTLEROCKET_x86_64 = "BOTTLEROCKET_x86_64"
    BOTTLEROCKET_ARM_64_NVIDIA = "BOTTLEROCKET_ARM_64_NVIDIA"
    BOTTLEROCKET_x86_64_NVIDIA = "BOTTLEROCKET_x86_64_NVIDIA"


class AddonIssueCode(str):
    AccessDenied = "AccessDenied"
    InternalFailure = "InternalFailure"
    ClusterUnreachable = "ClusterUnreachable"
    InsufficientNumberOfReplicas = "InsufficientNumberOfReplicas"
    ConfigurationConflict = "ConfigurationConflict"
    AdmissionRequestDenied = "AdmissionRequestDenied"
    UnsupportedAddonModification = "UnsupportedAddonModification"
    K8sResourceNotFound = "K8sResourceNotFound"


class AddonStatus(str):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    CREATE_FAILED = "CREATE_FAILED"
    UPDATING = "UPDATING"
    DELETING = "DELETING"
    DELETE_FAILED = "DELETE_FAILED"
    DEGRADED = "DEGRADED"


class CapacityTypes(str):
    ON_DEMAND = "ON_DEMAND"
    SPOT = "SPOT"


class ClusterStatus(str):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"
    FAILED = "FAILED"
    UPDATING = "UPDATING"
    PENDING = "PENDING"


class ConnectorConfigProvider(str):
    EKS_ANYWHERE = "EKS_ANYWHERE"
    ANTHOS = "ANTHOS"
    GKE = "GKE"
    AKS = "AKS"
    OPENSHIFT = "OPENSHIFT"
    TANZU = "TANZU"
    RANCHER = "RANCHER"
    EC2 = "EC2"
    OTHER = "OTHER"


class ErrorCode(str):
    SubnetNotFound = "SubnetNotFound"
    SecurityGroupNotFound = "SecurityGroupNotFound"
    EniLimitReached = "EniLimitReached"
    IpNotAvailable = "IpNotAvailable"
    AccessDenied = "AccessDenied"
    OperationNotPermitted = "OperationNotPermitted"
    VpcIdNotFound = "VpcIdNotFound"
    Unknown = "Unknown"
    NodeCreationFailure = "NodeCreationFailure"
    PodEvictionFailure = "PodEvictionFailure"
    InsufficientFreeAddresses = "InsufficientFreeAddresses"
    ClusterUnreachable = "ClusterUnreachable"
    InsufficientNumberOfReplicas = "InsufficientNumberOfReplicas"
    ConfigurationConflict = "ConfigurationConflict"
    AdmissionRequestDenied = "AdmissionRequestDenied"
    UnsupportedAddonModification = "UnsupportedAddonModification"
    K8sResourceNotFound = "K8sResourceNotFound"


class FargateProfileStatus(str):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"
    CREATE_FAILED = "CREATE_FAILED"
    DELETE_FAILED = "DELETE_FAILED"


class IpFamily(str):
    ipv4 = "ipv4"
    ipv6 = "ipv6"


class LogType(str):
    api = "api"
    audit = "audit"
    authenticator = "authenticator"
    controllerManager = "controllerManager"
    scheduler = "scheduler"


class NodegroupIssueCode(str):
    AutoScalingGroupNotFound = "AutoScalingGroupNotFound"
    AutoScalingGroupInvalidConfiguration = "AutoScalingGroupInvalidConfiguration"
    Ec2SecurityGroupNotFound = "Ec2SecurityGroupNotFound"
    Ec2SecurityGroupDeletionFailure = "Ec2SecurityGroupDeletionFailure"
    Ec2LaunchTemplateNotFound = "Ec2LaunchTemplateNotFound"
    Ec2LaunchTemplateVersionMismatch = "Ec2LaunchTemplateVersionMismatch"
    Ec2SubnetNotFound = "Ec2SubnetNotFound"
    Ec2SubnetInvalidConfiguration = "Ec2SubnetInvalidConfiguration"
    IamInstanceProfileNotFound = "IamInstanceProfileNotFound"
    IamLimitExceeded = "IamLimitExceeded"
    IamNodeRoleNotFound = "IamNodeRoleNotFound"
    NodeCreationFailure = "NodeCreationFailure"
    AsgInstanceLaunchFailures = "AsgInstanceLaunchFailures"
    InstanceLimitExceeded = "InstanceLimitExceeded"
    InsufficientFreeAddresses = "InsufficientFreeAddresses"
    AccessDenied = "AccessDenied"
    InternalFailure = "InternalFailure"
    ClusterUnreachable = "ClusterUnreachable"
    Ec2SubnetMissingIpv6Assignment = "Ec2SubnetMissingIpv6Assignment"


class NodegroupStatus(str):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    UPDATING = "UPDATING"
    DELETING = "DELETING"
    CREATE_FAILED = "CREATE_FAILED"
    DELETE_FAILED = "DELETE_FAILED"
    DEGRADED = "DEGRADED"


class ResolveConflicts(str):
    OVERWRITE = "OVERWRITE"
    NONE = "NONE"


class TaintEffect(str):
    NO_SCHEDULE = "NO_SCHEDULE"
    NO_EXECUTE = "NO_EXECUTE"
    PREFER_NO_SCHEDULE = "PREFER_NO_SCHEDULE"


class UpdateParamType(str):
    Version = "Version"
    PlatformVersion = "PlatformVersion"
    EndpointPrivateAccess = "EndpointPrivateAccess"
    EndpointPublicAccess = "EndpointPublicAccess"
    ClusterLogging = "ClusterLogging"
    DesiredSize = "DesiredSize"
    LabelsToAdd = "LabelsToAdd"
    LabelsToRemove = "LabelsToRemove"
    TaintsToAdd = "TaintsToAdd"
    TaintsToRemove = "TaintsToRemove"
    MaxSize = "MaxSize"
    MinSize = "MinSize"
    ReleaseVersion = "ReleaseVersion"
    PublicAccessCidrs = "PublicAccessCidrs"
    LaunchTemplateName = "LaunchTemplateName"
    LaunchTemplateVersion = "LaunchTemplateVersion"
    IdentityProviderConfig = "IdentityProviderConfig"
    EncryptionConfig = "EncryptionConfig"
    AddonVersion = "AddonVersion"
    ServiceAccountRoleArn = "ServiceAccountRoleArn"
    ResolveConflicts = "ResolveConflicts"
    MaxUnavailable = "MaxUnavailable"
    MaxUnavailablePercentage = "MaxUnavailablePercentage"


class UpdateStatus(str):
    InProgress = "InProgress"
    Failed = "Failed"
    Cancelled = "Cancelled"
    Successful = "Successful"


class UpdateType(str):
    VersionUpdate = "VersionUpdate"
    EndpointAccessUpdate = "EndpointAccessUpdate"
    LoggingUpdate = "LoggingUpdate"
    ConfigUpdate = "ConfigUpdate"
    AssociateIdentityProviderConfig = "AssociateIdentityProviderConfig"
    DisassociateIdentityProviderConfig = "DisassociateIdentityProviderConfig"
    AssociateEncryptionConfig = "AssociateEncryptionConfig"
    AddonUpdate = "AddonUpdate"


class configStatus(str):
    CREATING = "CREATING"
    DELETING = "DELETING"
    ACTIVE = "ACTIVE"


class AccessDeniedException(ServiceException):
    """You don't have permissions to perform the requested operation. The user
    or role that is making the request must have at least one IAM
    permissions policy attached that grants the required permissions. For
    more information, see `Access
    Management <https://docs.aws.amazon.com/IAM/latest/UserGuide/access.html>`__
    in the *IAM User Guide*.
    """

    message: Optional[String]


class BadRequestException(ServiceException):
    """This exception is thrown if the request contains a semantic error. The
    precise meaning will depend on the API, and will be documented in the
    error message.
    """

    message: Optional[String]


class ClientException(ServiceException):
    """These errors are usually caused by a client action. Actions can include
    using an action or resource on behalf of a user that doesn't have
    permissions to use the action or resource or specifying an identifier
    that is not valid.
    """

    clusterName: Optional[String]
    nodegroupName: Optional[String]
    addonName: Optional[String]
    message: Optional[String]


class InvalidParameterException(ServiceException):
    """The specified parameter is invalid. Review the available parameters for
    the API request.
    """

    clusterName: Optional[String]
    nodegroupName: Optional[String]
    fargateProfileName: Optional[String]
    addonName: Optional[String]
    message: Optional[String]


class InvalidRequestException(ServiceException):
    """The request is invalid given the state of the cluster. Check the state
    of the cluster and the associated operations.
    """

    clusterName: Optional[String]
    nodegroupName: Optional[String]
    addonName: Optional[String]
    message: Optional[String]


class NotFoundException(ServiceException):
    """A service resource associated with the request could not be found.
    Clients should not retry such requests.
    """

    message: Optional[String]


class ResourceInUseException(ServiceException):
    """The specified resource is in use."""

    clusterName: Optional[String]
    nodegroupName: Optional[String]
    addonName: Optional[String]
    message: Optional[String]


class ResourceLimitExceededException(ServiceException):
    """You have encountered a service limit on the specified resource."""

    clusterName: Optional[String]
    nodegroupName: Optional[String]
    message: Optional[String]


class ResourceNotFoundException(ServiceException):
    """The specified resource could not be found. You can view your available
    clusters with ListClusters. You can view your available managed node
    groups with ListNodegroups. Amazon EKS clusters and node groups are
    Region-specific.
    """

    clusterName: Optional[String]
    nodegroupName: Optional[String]
    fargateProfileName: Optional[String]
    addonName: Optional[String]
    message: Optional[String]


class ResourcePropagationDelayException(ServiceException):
    """Required resources (such as service-linked roles) were created and are
    still propagating. Retry later.
    """

    message: Optional[String]


class ServerException(ServiceException):
    """These errors are usually caused by a server-side issue."""

    clusterName: Optional[String]
    nodegroupName: Optional[String]
    addonName: Optional[String]
    message: Optional[String]


class ServiceUnavailableException(ServiceException):
    """The service is unavailable. Back off and retry the operation."""

    message: Optional[String]


StringList = List[String]


class UnsupportedAvailabilityZoneException(ServiceException):
    """At least one of your specified cluster subnets is in an Availability
    Zone that does not support Amazon EKS. The exception output specifies
    the supported Availability Zones for your account, from which you can
    choose subnets for your cluster.
    """

    message: Optional[String]
    clusterName: Optional[String]
    nodegroupName: Optional[String]
    validZones: Optional[StringList]


TagMap = Dict[TagKey, TagValue]
Timestamp = datetime


class AddonIssue(TypedDict, total=False):
    """An issue related to an add-on."""

    code: Optional[AddonIssueCode]
    message: Optional[String]
    resourceIds: Optional[StringList]


AddonIssueList = List[AddonIssue]


class AddonHealth(TypedDict, total=False):
    """The health of the add-on."""

    issues: Optional[AddonIssueList]


class Addon(TypedDict, total=False):
    """An Amazon EKS add-on. For more information, see `Amazon EKS
    add-ons <https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html>`__
    in the *Amazon EKS User Guide*.
    """

    addonName: Optional[String]
    clusterName: Optional[ClusterName]
    status: Optional[AddonStatus]
    addonVersion: Optional[String]
    health: Optional[AddonHealth]
    addonArn: Optional[String]
    createdAt: Optional[Timestamp]
    modifiedAt: Optional[Timestamp]
    serviceAccountRoleArn: Optional[String]
    tags: Optional[TagMap]


class Compatibility(TypedDict, total=False):
    """Compatibility information."""

    clusterVersion: Optional[String]
    platformVersions: Optional[StringList]
    defaultVersion: Optional[Boolean]


Compatibilities = List[Compatibility]


class AddonVersionInfo(TypedDict, total=False):
    """Information about an add-on version."""

    addonVersion: Optional[String]
    architecture: Optional[StringList]
    compatibilities: Optional[Compatibilities]


AddonVersionInfoList = List[AddonVersionInfo]
AddonInfo = TypedDict(
    "AddonInfo",
    {
        "addonName": Optional[String],
        "type": Optional[String],
        "addonVersions": Optional[AddonVersionInfoList],
    },
    total=False,
)
Addons = List[AddonInfo]


class Provider(TypedDict, total=False):
    """Identifies the Key Management Service (KMS) key used to encrypt the
    secrets.
    """

    keyArn: Optional[String]


class EncryptionConfig(TypedDict, total=False):
    """The encryption configuration for the cluster."""

    resources: Optional[StringList]
    provider: Optional[Provider]


EncryptionConfigList = List[EncryptionConfig]


class AssociateEncryptionConfigRequest(ServiceRequest):
    clusterName: String
    encryptionConfig: EncryptionConfigList
    clientRequestToken: Optional[String]


class ErrorDetail(TypedDict, total=False):
    """An object representing an error when an asynchronous operation fails."""

    errorCode: Optional[ErrorCode]
    errorMessage: Optional[String]
    resourceIds: Optional[StringList]


ErrorDetails = List[ErrorDetail]
UpdateParam = TypedDict(
    "UpdateParam",
    {
        "type": Optional[UpdateParamType],
        "value": Optional[String],
    },
    total=False,
)
UpdateParams = List[UpdateParam]
Update = TypedDict(
    "Update",
    {
        "id": Optional[String],
        "status": Optional[UpdateStatus],
        "type": Optional[UpdateType],
        "params": Optional[UpdateParams],
        "createdAt": Optional[Timestamp],
        "errors": Optional[ErrorDetails],
    },
    total=False,
)


class AssociateEncryptionConfigResponse(TypedDict, total=False):
    update: Optional[Update]


requiredClaimsMap = Dict[requiredClaimsKey, requiredClaimsValue]


class OidcIdentityProviderConfigRequest(TypedDict, total=False):
    """An object representing an OpenID Connect (OIDC) configuration. Before
    associating an OIDC identity provider to your cluster, review the
    considerations in `Authenticating users for your cluster from an OpenID
    Connect identity
    provider <https://docs.aws.amazon.com/eks/latest/userguide/authenticate-oidc-identity-provider.html>`__
    in the *Amazon EKS User Guide*.
    """

    identityProviderConfigName: String
    issuerUrl: String
    clientId: String
    usernameClaim: Optional[String]
    usernamePrefix: Optional[String]
    groupsClaim: Optional[String]
    groupsPrefix: Optional[String]
    requiredClaims: Optional[requiredClaimsMap]


class AssociateIdentityProviderConfigRequest(ServiceRequest):
    clusterName: String
    oidc: OidcIdentityProviderConfigRequest
    tags: Optional[TagMap]
    clientRequestToken: Optional[String]


class AssociateIdentityProviderConfigResponse(TypedDict, total=False):
    update: Optional[Update]
    tags: Optional[TagMap]


class AutoScalingGroup(TypedDict, total=False):
    """An Auto Scaling group that is associated with an Amazon EKS managed node
    group.
    """

    name: Optional[String]


AutoScalingGroupList = List[AutoScalingGroup]


class Certificate(TypedDict, total=False):
    """An object representing the ``certificate-authority-data`` for your
    cluster.
    """

    data: Optional[String]


class ConnectorConfigResponse(TypedDict, total=False):
    """The full description of your connected cluster."""

    activationId: Optional[String]
    activationCode: Optional[String]
    activationExpiry: Optional[Timestamp]
    provider: Optional[String]
    roleArn: Optional[String]


class OIDC(TypedDict, total=False):
    """An object representing the `OpenID
    Connect <https://openid.net/connect/>`__ (OIDC) identity provider
    information for the cluster.
    """

    issuer: Optional[String]


class Identity(TypedDict, total=False):
    """An object representing an identity provider."""

    oidc: Optional[OIDC]


LogTypes = List[LogType]


class LogSetup(TypedDict, total=False):
    """An object representing the enabled or disabled Kubernetes control plane
    logs for your cluster.
    """

    types: Optional[LogTypes]
    enabled: Optional[BoxedBoolean]


LogSetups = List[LogSetup]


class Logging(TypedDict, total=False):
    """An object representing the logging configuration for resources in your
    cluster.
    """

    clusterLogging: Optional[LogSetups]


class KubernetesNetworkConfigResponse(TypedDict, total=False):
    """The Kubernetes network configuration for the cluster. The response
    contains a value for **serviceIpv6Cidr** or **serviceIpv4Cidr**, but not
    both.
    """

    serviceIpv4Cidr: Optional[String]
    serviceIpv6Cidr: Optional[String]
    ipFamily: Optional[IpFamily]


class VpcConfigResponse(TypedDict, total=False):
    """An object representing an Amazon EKS cluster VPC configuration response."""

    subnetIds: Optional[StringList]
    securityGroupIds: Optional[StringList]
    clusterSecurityGroupId: Optional[String]
    vpcId: Optional[String]
    endpointPublicAccess: Optional[Boolean]
    endpointPrivateAccess: Optional[Boolean]
    publicAccessCidrs: Optional[StringList]


class Cluster(TypedDict, total=False):
    """An object representing an Amazon EKS cluster."""

    name: Optional[String]
    arn: Optional[String]
    createdAt: Optional[Timestamp]
    version: Optional[String]
    endpoint: Optional[String]
    roleArn: Optional[String]
    resourcesVpcConfig: Optional[VpcConfigResponse]
    kubernetesNetworkConfig: Optional[KubernetesNetworkConfigResponse]
    logging: Optional[Logging]
    identity: Optional[Identity]
    status: Optional[ClusterStatus]
    certificateAuthority: Optional[Certificate]
    clientRequestToken: Optional[String]
    platformVersion: Optional[String]
    tags: Optional[TagMap]
    encryptionConfig: Optional[EncryptionConfigList]
    connectorConfig: Optional[ConnectorConfigResponse]


class ConnectorConfigRequest(TypedDict, total=False):
    """The configuration sent to a cluster for configuration."""

    roleArn: String
    provider: ConnectorConfigProvider


class CreateAddonRequest(ServiceRequest):
    clusterName: ClusterName
    addonName: String
    addonVersion: Optional[String]
    serviceAccountRoleArn: Optional[RoleArn]
    resolveConflicts: Optional[ResolveConflicts]
    clientRequestToken: Optional[String]
    tags: Optional[TagMap]


class CreateAddonResponse(TypedDict, total=False):
    addon: Optional[Addon]


class KubernetesNetworkConfigRequest(TypedDict, total=False):
    """The Kubernetes network configuration for the cluster."""

    serviceIpv4Cidr: Optional[String]
    ipFamily: Optional[IpFamily]


class VpcConfigRequest(TypedDict, total=False):
    """An object representing the VPC configuration to use for an Amazon EKS
    cluster.
    """

    subnetIds: Optional[StringList]
    securityGroupIds: Optional[StringList]
    endpointPublicAccess: Optional[BoxedBoolean]
    endpointPrivateAccess: Optional[BoxedBoolean]
    publicAccessCidrs: Optional[StringList]


class CreateClusterRequest(ServiceRequest):
    name: ClusterName
    version: Optional[String]
    roleArn: String
    resourcesVpcConfig: VpcConfigRequest
    kubernetesNetworkConfig: Optional[KubernetesNetworkConfigRequest]
    logging: Optional[Logging]
    clientRequestToken: Optional[String]
    tags: Optional[TagMap]
    encryptionConfig: Optional[EncryptionConfigList]


class CreateClusterResponse(TypedDict, total=False):
    cluster: Optional[Cluster]


FargateProfileLabel = Dict[String, String]


class FargateProfileSelector(TypedDict, total=False):
    """An object representing an Fargate profile selector."""

    namespace: Optional[String]
    labels: Optional[FargateProfileLabel]


FargateProfileSelectors = List[FargateProfileSelector]


class CreateFargateProfileRequest(ServiceRequest):
    fargateProfileName: String
    clusterName: String
    podExecutionRoleArn: String
    subnets: Optional[StringList]
    selectors: Optional[FargateProfileSelectors]
    clientRequestToken: Optional[String]
    tags: Optional[TagMap]


class FargateProfile(TypedDict, total=False):
    """An object representing an Fargate profile."""

    fargateProfileName: Optional[String]
    fargateProfileArn: Optional[String]
    clusterName: Optional[String]
    createdAt: Optional[Timestamp]
    podExecutionRoleArn: Optional[String]
    subnets: Optional[StringList]
    selectors: Optional[FargateProfileSelectors]
    status: Optional[FargateProfileStatus]
    tags: Optional[TagMap]


class CreateFargateProfileResponse(TypedDict, total=False):
    fargateProfile: Optional[FargateProfile]


class NodegroupUpdateConfig(TypedDict, total=False):
    """The node group update configuration."""

    maxUnavailable: Optional[NonZeroInteger]
    maxUnavailablePercentage: Optional[PercentCapacity]


class LaunchTemplateSpecification(TypedDict, total=False):
    """An object representing a node group launch template specification. The
    launch template cannot include
    ```SubnetId`` <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_CreateNetworkInterface.html>`__
    ,
    ```IamInstanceProfile`` <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_IamInstanceProfile.html>`__
    ,
    ```RequestSpotInstances`` <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_RequestSpotInstances.html>`__
    ,
    ```HibernationOptions`` <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_HibernationOptionsRequest.html>`__
    , or
    ```TerminateInstances`` <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_TerminateInstances.html>`__
    , or the node group deployment or update will fail. For more information
    about launch templates, see
    ```CreateLaunchTemplate`` <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_CreateLaunchTemplate.html>`__
    in the Amazon EC2 API Reference. For more information about using launch
    templates with Amazon EKS, see `Launch template
    support <https://docs.aws.amazon.com/eks/latest/userguide/launch-templates.html>`__
    in the *Amazon EKS User Guide*.

    Specify either ``name`` or ``id``, but not both.
    """

    name: Optional[String]
    version: Optional[String]
    id: Optional[String]


class Taint(TypedDict, total=False):
    """A property that allows a node to repel a set of pods. For more
    information, see `Node taints on managed node
    groups <https://docs.aws.amazon.com/eks/latest/userguide/node-taints-managed-node-groups.html>`__.
    """

    key: Optional[taintKey]
    value: Optional[taintValue]
    effect: Optional[TaintEffect]


taintsList = List[Taint]
labelsMap = Dict[labelKey, labelValue]


class RemoteAccessConfig(TypedDict, total=False):
    """An object representing the remote access configuration for the managed
    node group.
    """

    ec2SshKey: Optional[String]
    sourceSecurityGroups: Optional[StringList]


class NodegroupScalingConfig(TypedDict, total=False):
    """An object representing the scaling configuration details for the Auto
    Scaling group that is associated with your node group. When creating a
    node group, you must specify all or none of the properties. When
    updating a node group, you can specify any or none of the properties.
    """

    minSize: Optional[ZeroCapacity]
    maxSize: Optional[Capacity]
    desiredSize: Optional[ZeroCapacity]


class CreateNodegroupRequest(ServiceRequest):
    clusterName: String
    nodegroupName: String
    scalingConfig: Optional[NodegroupScalingConfig]
    diskSize: Optional[BoxedInteger]
    subnets: StringList
    instanceTypes: Optional[StringList]
    amiType: Optional[AMITypes]
    remoteAccess: Optional[RemoteAccessConfig]
    nodeRole: String
    labels: Optional[labelsMap]
    taints: Optional[taintsList]
    tags: Optional[TagMap]
    clientRequestToken: Optional[String]
    launchTemplate: Optional[LaunchTemplateSpecification]
    updateConfig: Optional[NodegroupUpdateConfig]
    capacityType: Optional[CapacityTypes]
    version: Optional[String]
    releaseVersion: Optional[String]


class Issue(TypedDict, total=False):
    """An object representing an issue with an Amazon EKS resource."""

    code: Optional[NodegroupIssueCode]
    message: Optional[String]
    resourceIds: Optional[StringList]


IssueList = List[Issue]


class NodegroupHealth(TypedDict, total=False):
    """An object representing the health status of the node group."""

    issues: Optional[IssueList]


class NodegroupResources(TypedDict, total=False):
    """An object representing the resources associated with the node group,
    such as Auto Scaling groups and security groups for remote access.
    """

    autoScalingGroups: Optional[AutoScalingGroupList]
    remoteAccessSecurityGroup: Optional[String]


class Nodegroup(TypedDict, total=False):
    """An object representing an Amazon EKS managed node group."""

    nodegroupName: Optional[String]
    nodegroupArn: Optional[String]
    clusterName: Optional[String]
    version: Optional[String]
    releaseVersion: Optional[String]
    createdAt: Optional[Timestamp]
    modifiedAt: Optional[Timestamp]
    status: Optional[NodegroupStatus]
    capacityType: Optional[CapacityTypes]
    scalingConfig: Optional[NodegroupScalingConfig]
    instanceTypes: Optional[StringList]
    subnets: Optional[StringList]
    remoteAccess: Optional[RemoteAccessConfig]
    amiType: Optional[AMITypes]
    nodeRole: Optional[String]
    labels: Optional[labelsMap]
    taints: Optional[taintsList]
    resources: Optional[NodegroupResources]
    diskSize: Optional[BoxedInteger]
    health: Optional[NodegroupHealth]
    updateConfig: Optional[NodegroupUpdateConfig]
    launchTemplate: Optional[LaunchTemplateSpecification]
    tags: Optional[TagMap]


class CreateNodegroupResponse(TypedDict, total=False):
    nodegroup: Optional[Nodegroup]


class DeleteAddonRequest(ServiceRequest):
    clusterName: ClusterName
    addonName: String
    preserve: Optional[Boolean]


class DeleteAddonResponse(TypedDict, total=False):
    addon: Optional[Addon]


class DeleteClusterRequest(ServiceRequest):
    name: String


class DeleteClusterResponse(TypedDict, total=False):
    cluster: Optional[Cluster]


class DeleteFargateProfileRequest(ServiceRequest):
    clusterName: String
    fargateProfileName: String


class DeleteFargateProfileResponse(TypedDict, total=False):
    fargateProfile: Optional[FargateProfile]


class DeleteNodegroupRequest(ServiceRequest):
    clusterName: String
    nodegroupName: String


class DeleteNodegroupResponse(TypedDict, total=False):
    nodegroup: Optional[Nodegroup]


class DeregisterClusterRequest(ServiceRequest):
    name: String


class DeregisterClusterResponse(TypedDict, total=False):
    cluster: Optional[Cluster]


class DescribeAddonRequest(ServiceRequest):
    clusterName: ClusterName
    addonName: String


class DescribeAddonResponse(TypedDict, total=False):
    addon: Optional[Addon]


class DescribeAddonVersionsRequest(ServiceRequest):
    kubernetesVersion: Optional[String]
    maxResults: Optional[DescribeAddonVersionsRequestMaxResults]
    nextToken: Optional[String]
    addonName: Optional[String]


class DescribeAddonVersionsResponse(TypedDict, total=False):
    addons: Optional[Addons]
    nextToken: Optional[String]


class DescribeClusterRequest(ServiceRequest):
    name: String


class DescribeClusterResponse(TypedDict, total=False):
    cluster: Optional[Cluster]


class DescribeFargateProfileRequest(ServiceRequest):
    clusterName: String
    fargateProfileName: String


class DescribeFargateProfileResponse(TypedDict, total=False):
    fargateProfile: Optional[FargateProfile]


IdentityProviderConfig = TypedDict(
    "IdentityProviderConfig",
    {
        "type": String,
        "name": String,
    },
    total=False,
)


class DescribeIdentityProviderConfigRequest(ServiceRequest):
    clusterName: String
    identityProviderConfig: IdentityProviderConfig


class OidcIdentityProviderConfig(TypedDict, total=False):
    """An object that represents the configuration for an OpenID Connect (OIDC)
    identity provider.
    """

    identityProviderConfigName: Optional[String]
    identityProviderConfigArn: Optional[String]
    clusterName: Optional[String]
    issuerUrl: Optional[String]
    clientId: Optional[String]
    usernameClaim: Optional[String]
    usernamePrefix: Optional[String]
    groupsClaim: Optional[String]
    groupsPrefix: Optional[String]
    requiredClaims: Optional[requiredClaimsMap]
    tags: Optional[TagMap]
    status: Optional[configStatus]


class IdentityProviderConfigResponse(TypedDict, total=False):
    """The full description of your identity configuration."""

    oidc: Optional[OidcIdentityProviderConfig]


class DescribeIdentityProviderConfigResponse(TypedDict, total=False):
    identityProviderConfig: Optional[IdentityProviderConfigResponse]


class DescribeNodegroupRequest(ServiceRequest):
    clusterName: String
    nodegroupName: String


class DescribeNodegroupResponse(TypedDict, total=False):
    nodegroup: Optional[Nodegroup]


class DescribeUpdateRequest(ServiceRequest):
    name: String
    updateId: String
    nodegroupName: Optional[String]
    addonName: Optional[String]


class DescribeUpdateResponse(TypedDict, total=False):
    update: Optional[Update]


class DisassociateIdentityProviderConfigRequest(ServiceRequest):
    clusterName: String
    identityProviderConfig: IdentityProviderConfig
    clientRequestToken: Optional[String]


class DisassociateIdentityProviderConfigResponse(TypedDict, total=False):
    update: Optional[Update]


IdentityProviderConfigs = List[IdentityProviderConfig]
IncludeClustersList = List[String]


class ListAddonsRequest(ServiceRequest):
    clusterName: ClusterName
    maxResults: Optional[ListAddonsRequestMaxResults]
    nextToken: Optional[String]


class ListAddonsResponse(TypedDict, total=False):
    addons: Optional[StringList]
    nextToken: Optional[String]


class ListClustersRequest(ServiceRequest):
    maxResults: Optional[ListClustersRequestMaxResults]
    nextToken: Optional[String]
    include: Optional[IncludeClustersList]


class ListClustersResponse(TypedDict, total=False):
    clusters: Optional[StringList]
    nextToken: Optional[String]


class ListFargateProfilesRequest(ServiceRequest):
    clusterName: String
    maxResults: Optional[FargateProfilesRequestMaxResults]
    nextToken: Optional[String]


class ListFargateProfilesResponse(TypedDict, total=False):
    fargateProfileNames: Optional[StringList]
    nextToken: Optional[String]


class ListIdentityProviderConfigsRequest(ServiceRequest):
    clusterName: String
    maxResults: Optional[ListIdentityProviderConfigsRequestMaxResults]
    nextToken: Optional[String]


class ListIdentityProviderConfigsResponse(TypedDict, total=False):
    identityProviderConfigs: Optional[IdentityProviderConfigs]
    nextToken: Optional[String]


class ListNodegroupsRequest(ServiceRequest):
    clusterName: String
    maxResults: Optional[ListNodegroupsRequestMaxResults]
    nextToken: Optional[String]


class ListNodegroupsResponse(TypedDict, total=False):
    nodegroups: Optional[StringList]
    nextToken: Optional[String]


class ListTagsForResourceRequest(ServiceRequest):
    resourceArn: String


class ListTagsForResourceResponse(TypedDict, total=False):
    tags: Optional[TagMap]


class ListUpdatesRequest(ServiceRequest):
    name: String
    nodegroupName: Optional[String]
    addonName: Optional[String]
    nextToken: Optional[String]
    maxResults: Optional[ListUpdatesRequestMaxResults]


class ListUpdatesResponse(TypedDict, total=False):
    updateIds: Optional[StringList]
    nextToken: Optional[String]


class RegisterClusterRequest(ServiceRequest):
    name: ClusterName
    connectorConfig: ConnectorConfigRequest
    clientRequestToken: Optional[String]
    tags: Optional[TagMap]


class RegisterClusterResponse(TypedDict, total=False):
    cluster: Optional[Cluster]


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    resourceArn: String
    tags: TagMap


class TagResourceResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    resourceArn: String
    tagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateAddonRequest(ServiceRequest):
    clusterName: ClusterName
    addonName: String
    addonVersion: Optional[String]
    serviceAccountRoleArn: Optional[RoleArn]
    resolveConflicts: Optional[ResolveConflicts]
    clientRequestToken: Optional[String]


class UpdateAddonResponse(TypedDict, total=False):
    update: Optional[Update]


class UpdateClusterConfigRequest(ServiceRequest):
    name: String
    resourcesVpcConfig: Optional[VpcConfigRequest]
    logging: Optional[Logging]
    clientRequestToken: Optional[String]


class UpdateClusterConfigResponse(TypedDict, total=False):
    update: Optional[Update]


class UpdateClusterVersionRequest(ServiceRequest):
    name: String
    version: String
    clientRequestToken: Optional[String]


class UpdateClusterVersionResponse(TypedDict, total=False):
    update: Optional[Update]


labelsKeyList = List[String]


class UpdateLabelsPayload(TypedDict, total=False):
    """An object representing a Kubernetes label change for a managed node
    group.
    """

    addOrUpdateLabels: Optional[labelsMap]
    removeLabels: Optional[labelsKeyList]


class UpdateTaintsPayload(TypedDict, total=False):
    """An object representing the details of an update to a taints payload. For
    more information, see `Node taints on managed node
    groups <https://docs.aws.amazon.com/eks/latest/userguide/node-taints-managed-node-groups.html>`__.
    """

    addOrUpdateTaints: Optional[taintsList]
    removeTaints: Optional[taintsList]


class UpdateNodegroupConfigRequest(ServiceRequest):
    clusterName: String
    nodegroupName: String
    labels: Optional[UpdateLabelsPayload]
    taints: Optional[UpdateTaintsPayload]
    scalingConfig: Optional[NodegroupScalingConfig]
    updateConfig: Optional[NodegroupUpdateConfig]
    clientRequestToken: Optional[String]


class UpdateNodegroupConfigResponse(TypedDict, total=False):
    update: Optional[Update]


class UpdateNodegroupVersionRequest(ServiceRequest):
    clusterName: String
    nodegroupName: String
    version: Optional[String]
    releaseVersion: Optional[String]
    launchTemplate: Optional[LaunchTemplateSpecification]
    force: Optional[Boolean]
    clientRequestToken: Optional[String]


class UpdateNodegroupVersionResponse(TypedDict, total=False):
    update: Optional[Update]


class EksApi:

    service = "eks"
    version = "2017-11-01"

    @handler("AssociateEncryptionConfig")
    def associate_encryption_config(
        self,
        context: RequestContext,
        cluster_name: String,
        encryption_config: EncryptionConfigList,
        client_request_token: String = None,
    ) -> AssociateEncryptionConfigResponse:
        """Associate encryption configuration to an existing cluster.

        You can use this API to enable encryption on existing clusters which do
        not have encryption already enabled. This allows you to implement a
        defense-in-depth security strategy without migrating applications to new
        Amazon EKS clusters.

        :param cluster_name: The name of the cluster that you are associating with encryption
        configuration.
        :param encryption_config: The configuration you are using for encryption.
        :param client_request_token: The client request token you are using with the encryption
        configuration.
        :returns: AssociateEncryptionConfigResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceInUseException:
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("AssociateIdentityProviderConfig")
    def associate_identity_provider_config(
        self,
        context: RequestContext,
        cluster_name: String,
        oidc: OidcIdentityProviderConfigRequest,
        tags: TagMap = None,
        client_request_token: String = None,
    ) -> AssociateIdentityProviderConfigResponse:
        """Associate an identity provider configuration to a cluster.

        If you want to authenticate identities using an identity provider, you
        can create an identity provider configuration and associate it to your
        cluster. After configuring authentication to your cluster you can create
        Kubernetes ``roles`` and ``clusterroles`` to assign permissions to the
        roles, and then bind the roles to the identities using Kubernetes
        ``rolebindings`` and ``clusterrolebindings``. For more information see
        `Using RBAC
        Authorization <https://kubernetes.io/docs/reference/access-authn-authz/rbac/>`__
        in the Kubernetes documentation.

        :param cluster_name: The name of the cluster to associate the configuration to.
        :param oidc: An object that represents an OpenID Connect (OIDC) identity provider
        configuration.
        :param tags: The metadata to apply to the configuration to assist with categorization
        and organization.
        :param client_request_token: Unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :returns: AssociateIdentityProviderConfigResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceInUseException:
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("CreateAddon")
    def create_addon(
        self,
        context: RequestContext,
        cluster_name: ClusterName,
        addon_name: String,
        addon_version: String = None,
        service_account_role_arn: RoleArn = None,
        resolve_conflicts: ResolveConflicts = None,
        client_request_token: String = None,
        tags: TagMap = None,
    ) -> CreateAddonResponse:
        """Creates an Amazon EKS add-on.

        Amazon EKS add-ons help to automate the provisioning and lifecycle
        management of common operational software for Amazon EKS clusters.
        Amazon EKS add-ons require clusters running version 1.18 or later
        because Amazon EKS add-ons rely on the Server-side Apply Kubernetes
        feature, which is only available in Kubernetes 1.18 and later. For more
        information, see `Amazon EKS
        add-ons <https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html>`__
        in the *Amazon EKS User Guide*.

        :param cluster_name: The name of the cluster to create the add-on for.
        :param addon_name: The name of the add-on.
        :param addon_version: The version of the add-on.
        :param service_account_role_arn: The Amazon Resource Name (ARN) of an existing IAM role to bind to the
        add-on's service account.
        :param resolve_conflicts: How to resolve parameter value conflicts when migrating an existing
        add-on to an Amazon EKS add-on.
        :param client_request_token: A unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :param tags: The metadata to apply to the cluster to assist with categorization and
        organization.
        :returns: CreateAddonResponse
        :raises InvalidParameterException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ResourceInUseException:
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("CreateCluster")
    def create_cluster(
        self,
        context: RequestContext,
        name: ClusterName,
        role_arn: String,
        resources_vpc_config: VpcConfigRequest,
        version: String = None,
        kubernetes_network_config: KubernetesNetworkConfigRequest = None,
        logging: Logging = None,
        client_request_token: String = None,
        tags: TagMap = None,
        encryption_config: EncryptionConfigList = None,
    ) -> CreateClusterResponse:
        """Creates an Amazon EKS control plane.

        The Amazon EKS control plane consists of control plane instances that
        run the Kubernetes software, such as ``etcd`` and the API server. The
        control plane runs in an account managed by Amazon Web Services, and the
        Kubernetes API is exposed by the Amazon EKS API server endpoint. Each
        Amazon EKS cluster control plane is single tenant and unique. It runs on
        its own set of Amazon EC2 instances.

        The cluster control plane is provisioned across multiple Availability
        Zones and fronted by an Elastic Load Balancing Network Load Balancer.
        Amazon EKS also provisions elastic network interfaces in your VPC
        subnets to provide connectivity from the control plane instances to the
        nodes (for example, to support ``kubectl exec``, ``logs``, and ``proxy``
        data flows).

        Amazon EKS nodes run in your Amazon Web Services account and connect to
        your cluster's control plane over the Kubernetes API server endpoint and
        a certificate file that is created for your cluster.

        In most cases, it takes several minutes to create a cluster. After you
        create an Amazon EKS cluster, you must configure your Kubernetes tooling
        to communicate with the API server and launch nodes into your cluster.
        For more information, see `Managing Cluster
        Authentication <https://docs.aws.amazon.com/eks/latest/userguide/managing-auth.html>`__
        and `Launching Amazon EKS
        nodes <https://docs.aws.amazon.com/eks/latest/userguide/launch-workers.html>`__
        in the *Amazon EKS User Guide*.

        :param name: The unique name to give to your cluster.
        :param role_arn: The Amazon Resource Name (ARN) of the IAM role that provides permissions
        for the Kubernetes control plane to make calls to Amazon Web Services
        API operations on your behalf.
        :param resources_vpc_config: The VPC configuration that's used by the cluster control plane.
        :param version: The desired Kubernetes version for your cluster.
        :param kubernetes_network_config: The Kubernetes network configuration for the cluster.
        :param logging: Enable or disable exporting the Kubernetes control plane logs for your
        cluster to CloudWatch Logs.
        :param client_request_token: Unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :param tags: The metadata to apply to the cluster to assist with categorization and
        organization.
        :param encryption_config: The encryption configuration for the cluster.
        :returns: CreateClusterResponse
        :raises ResourceInUseException:
        :raises ResourceLimitExceededException:
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        :raises UnsupportedAvailabilityZoneException:
        """
        raise NotImplementedError

    @handler("CreateFargateProfile")
    def create_fargate_profile(
        self,
        context: RequestContext,
        fargate_profile_name: String,
        cluster_name: String,
        pod_execution_role_arn: String,
        subnets: StringList = None,
        selectors: FargateProfileSelectors = None,
        client_request_token: String = None,
        tags: TagMap = None,
    ) -> CreateFargateProfileResponse:
        """Creates an Fargate profile for your Amazon EKS cluster. You must have at
        least one Fargate profile in a cluster to be able to run pods on
        Fargate.

        The Fargate profile allows an administrator to declare which pods run on
        Fargate and specify which pods run on which Fargate profile. This
        declaration is done through the profile’s selectors. Each profile can
        have up to five selectors that contain a namespace and labels. A
        namespace is required for every selector. The label field consists of
        multiple optional key-value pairs. Pods that match the selectors are
        scheduled on Fargate. If a to-be-scheduled pod matches any of the
        selectors in the Fargate profile, then that pod is run on Fargate.

        When you create a Fargate profile, you must specify a pod execution role
        to use with the pods that are scheduled with the profile. This role is
        added to the cluster's Kubernetes `Role Based Access
        Control <https://kubernetes.io/docs/admin/authorization/rbac/>`__ (RBAC)
        for authorization so that the ``kubelet`` that is running on the Fargate
        infrastructure can register with your Amazon EKS cluster so that it can
        appear in your cluster as a node. The pod execution role also provides
        IAM permissions to the Fargate infrastructure to allow read access to
        Amazon ECR image repositories. For more information, see `Pod Execution
        Role <https://docs.aws.amazon.com/eks/latest/userguide/pod-execution-role.html>`__
        in the *Amazon EKS User Guide*.

        Fargate profiles are immutable. However, you can create a new updated
        profile to replace an existing profile and then delete the original
        after the updated profile has finished creating.

        If any Fargate profiles in a cluster are in the ``DELETING`` status, you
        must wait for that Fargate profile to finish deleting before you can
        create any other profiles in that cluster.

        For more information, see `Fargate
        Profile <https://docs.aws.amazon.com/eks/latest/userguide/fargate-profile.html>`__
        in the *Amazon EKS User Guide*.

        :param fargate_profile_name: The name of the Fargate profile.
        :param cluster_name: The name of the Amazon EKS cluster to apply the Fargate profile to.
        :param pod_execution_role_arn: The Amazon Resource Name (ARN) of the pod execution role to use for pods
        that match the selectors in the Fargate profile.
        :param subnets: The IDs of subnets to launch your pods into.
        :param selectors: The selectors to match for pods to use this Fargate profile.
        :param client_request_token: Unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :param tags: The metadata to apply to the Fargate profile to assist with
        categorization and organization.
        :returns: CreateFargateProfileResponse
        :raises InvalidParameterException:
        :raises InvalidRequestException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceLimitExceededException:
        :raises UnsupportedAvailabilityZoneException:
        """
        raise NotImplementedError

    @handler("CreateNodegroup")
    def create_nodegroup(
        self,
        context: RequestContext,
        cluster_name: String,
        nodegroup_name: String,
        subnets: StringList,
        node_role: String,
        scaling_config: NodegroupScalingConfig = None,
        disk_size: BoxedInteger = None,
        instance_types: StringList = None,
        ami_type: AMITypes = None,
        remote_access: RemoteAccessConfig = None,
        labels: labelsMap = None,
        taints: taintsList = None,
        tags: TagMap = None,
        client_request_token: String = None,
        launch_template: LaunchTemplateSpecification = None,
        update_config: NodegroupUpdateConfig = None,
        capacity_type: CapacityTypes = None,
        version: String = None,
        release_version: String = None,
    ) -> CreateNodegroupResponse:
        """Creates a managed node group for an Amazon EKS cluster. You can only
        create a node group for your cluster that is equal to the current
        Kubernetes version for the cluster. All node groups are created with the
        latest AMI release version for the respective minor Kubernetes version
        of the cluster, unless you deploy a custom AMI using a launch template.
        For more information about using launch templates, see `Launch template
        support <https://docs.aws.amazon.com/eks/latest/userguide/launch-templates.html>`__.

        An Amazon EKS managed node group is an Amazon EC2 Auto Scaling group and
        associated Amazon EC2 instances that are managed by Amazon Web Services
        for an Amazon EKS cluster. Each node group uses a version of the Amazon
        EKS optimized Amazon Linux 2 AMI. For more information, see `Managed
        Node
        Groups <https://docs.aws.amazon.com/eks/latest/userguide/managed-node-groups.html>`__
        in the *Amazon EKS User Guide*.

        :param cluster_name: The name of the cluster to create the node group in.
        :param nodegroup_name: The unique name to give your node group.
        :param subnets: The subnets to use for the Auto Scaling group that is created for your
        node group.
        :param node_role: The Amazon Resource Name (ARN) of the IAM role to associate with your
        node group.
        :param scaling_config: The scaling configuration details for the Auto Scaling group that is
        created for your node group.
        :param disk_size: The root device disk size (in GiB) for your node group instances.
        :param instance_types: Specify the instance types for a node group.
        :param ami_type: The AMI type for your node group.
        :param remote_access: The remote access (SSH) configuration to use with your node group.
        :param labels: The Kubernetes labels to be applied to the nodes in the node group when
        they are created.
        :param taints: The Kubernetes taints to be applied to the nodes in the node group.
        :param tags: The metadata to apply to the node group to assist with categorization
        and organization.
        :param client_request_token: Unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :param launch_template: An object representing a node group's launch template specification.
        :param update_config: The node group update configuration.
        :param capacity_type: The capacity type for your node group.
        :param version: The Kubernetes version to use for your managed nodes.
        :param release_version: The AMI version of the Amazon EKS optimized AMI to use with your node
        group.
        :returns: CreateNodegroupResponse
        :raises ResourceInUseException:
        :raises ResourceLimitExceededException:
        :raises InvalidRequestException:
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteAddon")
    def delete_addon(
        self,
        context: RequestContext,
        cluster_name: ClusterName,
        addon_name: String,
        preserve: Boolean = None,
    ) -> DeleteAddonResponse:
        """Delete an Amazon EKS add-on.

        When you remove the add-on, it will also be deleted from the cluster.
        You can always manually start an add-on on the cluster using the
        Kubernetes API.

        :param cluster_name: The name of the cluster to delete the add-on from.
        :param addon_name: The name of the add-on.
        :param preserve: Specifying this option preserves the add-on software on your cluster but
        Amazon EKS stops managing any settings for the add-on.
        :returns: DeleteAddonResponse
        :raises InvalidParameterException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DeleteCluster")
    def delete_cluster(self, context: RequestContext, name: String) -> DeleteClusterResponse:
        """Deletes the Amazon EKS cluster control plane.

        If you have active services in your cluster that are associated with a
        load balancer, you must delete those services before deleting the
        cluster so that the load balancers are deleted properly. Otherwise, you
        can have orphaned resources in your VPC that prevent you from being able
        to delete the VPC. For more information, see `Deleting a
        Cluster <https://docs.aws.amazon.com/eks/latest/userguide/delete-cluster.html>`__
        in the *Amazon EKS User Guide*.

        If you have managed node groups or Fargate profiles attached to the
        cluster, you must delete them first. For more information, see
        DeleteNodegroup and DeleteFargateProfile.

        :param name: The name of the cluster to delete.
        :returns: DeleteClusterResponse
        :raises ResourceInUseException:
        :raises ResourceNotFoundException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteFargateProfile")
    def delete_fargate_profile(
        self, context: RequestContext, cluster_name: String, fargate_profile_name: String
    ) -> DeleteFargateProfileResponse:
        """Deletes an Fargate profile.

        When you delete a Fargate profile, any pods running on Fargate that were
        created with the profile are deleted. If those pods match another
        Fargate profile, then they are scheduled on Fargate with that profile.
        If they no longer match any Fargate profiles, then they are not
        scheduled on Fargate and they may remain in a pending state.

        Only one Fargate profile in a cluster can be in the ``DELETING`` status
        at a time. You must wait for a Fargate profile to finish deleting before
        you can delete any other profiles in that cluster.

        :param cluster_name: The name of the Amazon EKS cluster associated with the Fargate profile
        to delete.
        :param fargate_profile_name: The name of the Fargate profile to delete.
        :returns: DeleteFargateProfileResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteNodegroup")
    def delete_nodegroup(
        self, context: RequestContext, cluster_name: String, nodegroup_name: String
    ) -> DeleteNodegroupResponse:
        """Deletes an Amazon EKS node group for a cluster.

        :param cluster_name: The name of the Amazon EKS cluster that is associated with your node
        group.
        :param nodegroup_name: The name of the node group to delete.
        :returns: DeleteNodegroupResponse
        :raises ResourceInUseException:
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeregisterCluster")
    def deregister_cluster(
        self, context: RequestContext, name: String
    ) -> DeregisterClusterResponse:
        """Deregisters a connected cluster to remove it from the Amazon EKS control
        plane.

        :param name: The name of the connected cluster to deregister.
        :returns: DeregisterClusterResponse
        :raises ResourceInUseException:
        :raises ResourceNotFoundException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        :raises AccessDeniedException:
        """
        raise NotImplementedError

    @handler("DescribeAddon")
    def describe_addon(
        self, context: RequestContext, cluster_name: ClusterName, addon_name: String
    ) -> DescribeAddonResponse:
        """Describes an Amazon EKS add-on.

        :param cluster_name: The name of the cluster.
        :param addon_name: The name of the add-on.
        :returns: DescribeAddonResponse
        :raises InvalidParameterException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("DescribeAddonVersions")
    def describe_addon_versions(
        self,
        context: RequestContext,
        kubernetes_version: String = None,
        max_results: DescribeAddonVersionsRequestMaxResults = None,
        next_token: String = None,
        addon_name: String = None,
    ) -> DescribeAddonVersionsResponse:
        """Describes the Kubernetes versions that the add-on can be used with.

        :param kubernetes_version: The Kubernetes versions that the add-on can be used with.
        :param max_results: The maximum number of results to return.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``DescribeAddonVersionsRequest`` where ``maxResults`` was used and the
        results exceeded the value of that parameter.
        :param addon_name: The name of the add-on.
        :returns: DescribeAddonVersionsResponse
        :raises ServerException:
        :raises ResourceNotFoundException:
        :raises InvalidParameterException:
        """
        raise NotImplementedError

    @handler("DescribeCluster")
    def describe_cluster(self, context: RequestContext, name: String) -> DescribeClusterResponse:
        """Returns descriptive information about an Amazon EKS cluster.

        The API server endpoint and certificate authority data returned by this
        operation are required for ``kubelet`` and ``kubectl`` to communicate
        with your Kubernetes API server. For more information, see `Create a
        kubeconfig for Amazon
        EKS <https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html>`__.

        The API server endpoint and certificate authority data aren't available
        until the cluster reaches the ``ACTIVE`` state.

        :param name: The name of the cluster to describe.
        :returns: DescribeClusterResponse
        :raises ResourceNotFoundException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeFargateProfile")
    def describe_fargate_profile(
        self, context: RequestContext, cluster_name: String, fargate_profile_name: String
    ) -> DescribeFargateProfileResponse:
        """Returns descriptive information about an Fargate profile.

        :param cluster_name: The name of the Amazon EKS cluster associated with the Fargate profile.
        :param fargate_profile_name: The name of the Fargate profile to describe.
        :returns: DescribeFargateProfileResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeIdentityProviderConfig")
    def describe_identity_provider_config(
        self,
        context: RequestContext,
        cluster_name: String,
        identity_provider_config: IdentityProviderConfig,
    ) -> DescribeIdentityProviderConfigResponse:
        """Returns descriptive information about an identity provider
        configuration.

        :param cluster_name: The cluster name that the identity provider configuration is associated
        to.
        :param identity_provider_config: An object that represents an identity provider configuration.
        :returns: DescribeIdentityProviderConfigResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeNodegroup")
    def describe_nodegroup(
        self, context: RequestContext, cluster_name: String, nodegroup_name: String
    ) -> DescribeNodegroupResponse:
        """Returns descriptive information about an Amazon EKS node group.

        :param cluster_name: The name of the Amazon EKS cluster associated with the node group.
        :param nodegroup_name: The name of the node group to describe.
        :returns: DescribeNodegroupResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeUpdate")
    def describe_update(
        self,
        context: RequestContext,
        name: String,
        update_id: String,
        nodegroup_name: String = None,
        addon_name: String = None,
    ) -> DescribeUpdateResponse:
        """Returns descriptive information about an update against your Amazon EKS
        cluster or associated managed node group or Amazon EKS add-on.

        When the status of the update is ``Succeeded``, the update is complete.
        If an update fails, the status is ``Failed``, and an error detail
        explains the reason for the failure.

        :param name: The name of the Amazon EKS cluster associated with the update.
        :param update_id: The ID of the update to describe.
        :param nodegroup_name: The name of the Amazon EKS node group associated with the update.
        :param addon_name: The name of the add-on.
        :returns: DescribeUpdateResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DisassociateIdentityProviderConfig")
    def disassociate_identity_provider_config(
        self,
        context: RequestContext,
        cluster_name: String,
        identity_provider_config: IdentityProviderConfig,
        client_request_token: String = None,
    ) -> DisassociateIdentityProviderConfigResponse:
        """Disassociates an identity provider configuration from a cluster. If you
        disassociate an identity provider from your cluster, users included in
        the provider can no longer access the cluster. However, you can still
        access the cluster with Amazon Web Services IAM users.

        :param cluster_name: The name of the cluster to disassociate an identity provider from.
        :param identity_provider_config: An object that represents an identity provider configuration.
        :param client_request_token: A unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :returns: DisassociateIdentityProviderConfigResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceInUseException:
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListAddons")
    def list_addons(
        self,
        context: RequestContext,
        cluster_name: ClusterName,
        max_results: ListAddonsRequestMaxResults = None,
        next_token: String = None,
    ) -> ListAddonsResponse:
        """Lists the available add-ons.

        :param cluster_name: The name of the cluster.
        :param max_results: The maximum number of add-on results returned by ``ListAddonsRequest``
        in paginated output.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``ListAddonsRequest`` where ``maxResults`` was used and the results
        exceeded the value of that parameter.
        :returns: ListAddonsResponse
        :raises InvalidParameterException:
        :raises InvalidRequestException:
        :raises ClientException:
        :raises ResourceNotFoundException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("ListClusters")
    def list_clusters(
        self,
        context: RequestContext,
        max_results: ListClustersRequestMaxResults = None,
        next_token: String = None,
        include: IncludeClustersList = None,
    ) -> ListClustersResponse:
        """Lists the Amazon EKS clusters in your Amazon Web Services account in the
        specified Region.

        :param max_results: The maximum number of cluster results returned by ``ListClusters`` in
        paginated output.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``ListClusters`` request where ``maxResults`` was used and the results
        exceeded the value of that parameter.
        :param include: Indicates whether external clusters are included in the returned list.
        :returns: ListClustersResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListFargateProfiles")
    def list_fargate_profiles(
        self,
        context: RequestContext,
        cluster_name: String,
        max_results: FargateProfilesRequestMaxResults = None,
        next_token: String = None,
    ) -> ListFargateProfilesResponse:
        """Lists the Fargate profiles associated with the specified cluster in your
        Amazon Web Services account in the specified Region.

        :param cluster_name: The name of the Amazon EKS cluster that you would like to list Fargate
        profiles in.
        :param max_results: The maximum number of Fargate profile results returned by
        ``ListFargateProfiles`` in paginated output.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``ListFargateProfiles`` request where ``maxResults`` was used and the
        results exceeded the value of that parameter.
        :returns: ListFargateProfilesResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("ListIdentityProviderConfigs")
    def list_identity_provider_configs(
        self,
        context: RequestContext,
        cluster_name: String,
        max_results: ListIdentityProviderConfigsRequestMaxResults = None,
        next_token: String = None,
    ) -> ListIdentityProviderConfigsResponse:
        """A list of identity provider configurations.

        :param cluster_name: The cluster name that you want to list identity provider configurations
        for.
        :param max_results: The maximum number of identity provider configurations returned by
        ``ListIdentityProviderConfigs`` in paginated output.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``IdentityProviderConfigsRequest`` where ``maxResults`` was used and the
        results exceeded the value of that parameter.
        :returns: ListIdentityProviderConfigsResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListNodegroups")
    def list_nodegroups(
        self,
        context: RequestContext,
        cluster_name: String,
        max_results: ListNodegroupsRequestMaxResults = None,
        next_token: String = None,
    ) -> ListNodegroupsResponse:
        """Lists the Amazon EKS managed node groups associated with the specified
        cluster in your Amazon Web Services account in the specified Region.
        Self-managed node groups are not listed.

        :param cluster_name: The name of the Amazon EKS cluster that you would like to list node
        groups in.
        :param max_results: The maximum number of node group results returned by ``ListNodegroups``
        in paginated output.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``ListNodegroups`` request where ``maxResults`` was used and the results
        exceeded the value of that parameter.
        :returns: ListNodegroupsResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: String
    ) -> ListTagsForResourceResponse:
        """List the tags for an Amazon EKS resource.

        :param resource_arn: The Amazon Resource Name (ARN) that identifies the resource for which to
        list the tags.
        :returns: ListTagsForResourceResponse
        :raises BadRequestException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("ListUpdates")
    def list_updates(
        self,
        context: RequestContext,
        name: String,
        nodegroup_name: String = None,
        addon_name: String = None,
        next_token: String = None,
        max_results: ListUpdatesRequestMaxResults = None,
    ) -> ListUpdatesResponse:
        """Lists the updates associated with an Amazon EKS cluster or managed node
        group in your Amazon Web Services account, in the specified Region.

        :param name: The name of the Amazon EKS cluster to list updates for.
        :param nodegroup_name: The name of the Amazon EKS managed node group to list updates for.
        :param addon_name: The names of the installed add-ons that have available updates.
        :param next_token: The ``nextToken`` value returned from a previous paginated
        ``ListUpdates`` request where ``maxResults`` was used and the results
        exceeded the value of that parameter.
        :param max_results: The maximum number of update results returned by ``ListUpdates`` in
        paginated output.
        :returns: ListUpdatesResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("RegisterCluster")
    def register_cluster(
        self,
        context: RequestContext,
        name: ClusterName,
        connector_config: ConnectorConfigRequest,
        client_request_token: String = None,
        tags: TagMap = None,
    ) -> RegisterClusterResponse:
        """Connects a Kubernetes cluster to the Amazon EKS control plane.

        Any Kubernetes cluster can be connected to the Amazon EKS control plane
        to view current information about the cluster and its nodes.

        Cluster connection requires two steps. First, send a
        ``RegisterClusterRequest`` to add it to the Amazon EKS control plane.

        Second, a
        `Manifest <https://amazon-eks.s3.us-west-2.amazonaws.com/eks-connector/manifests/eks-connector/latest/eks-connector.yaml>`__
        containing the ``activationID`` and ``activationCode`` must be applied
        to the Kubernetes cluster through it's native provider to provide
        visibility.

        After the Manifest is updated and applied, then the connected cluster is
        visible to the Amazon EKS control plane. If the Manifest is not applied
        within three days, then the connected cluster will no longer be visible
        and must be deregistered. See DeregisterCluster.

        :param name: Define a unique name for this cluster for your Region.
        :param connector_config: The configuration settings required to connect the Kubernetes cluster to
        the Amazon EKS control plane.
        :param client_request_token: Unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :param tags: The metadata that you apply to the cluster to assist with categorization
        and organization.
        :returns: RegisterClusterResponse
        :raises ResourceLimitExceededException:
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ServiceUnavailableException:
        :raises AccessDeniedException:
        :raises ResourceInUseException:
        :raises ResourcePropagationDelayException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: String, tags: TagMap
    ) -> TagResourceResponse:
        """Associates the specified tags to a resource with the specified
        ``resourceArn``. If existing tags on a resource are not specified in the
        request parameters, they are not changed. When a resource is deleted,
        the tags associated with that resource are deleted as well. Tags that
        you create for Amazon EKS resources do not propagate to any other
        resources associated with the cluster. For example, if you tag a cluster
        with this operation, that tag does not automatically propagate to the
        subnets and nodes associated with the cluster.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource to which to add tags.
        :param tags: The tags to add to the resource.
        :returns: TagResourceResponse
        :raises BadRequestException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: String, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Deletes specified tags from a resource.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource from which to delete
        tags.
        :param tag_keys: The keys of the tags to be removed.
        :returns: UntagResourceResponse
        :raises BadRequestException:
        :raises NotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateAddon")
    def update_addon(
        self,
        context: RequestContext,
        cluster_name: ClusterName,
        addon_name: String,
        addon_version: String = None,
        service_account_role_arn: RoleArn = None,
        resolve_conflicts: ResolveConflicts = None,
        client_request_token: String = None,
    ) -> UpdateAddonResponse:
        """Updates an Amazon EKS add-on.

        :param cluster_name: The name of the cluster.
        :param addon_name: The name of the add-on.
        :param addon_version: The version of the add-on.
        :param service_account_role_arn: The Amazon Resource Name (ARN) of an existing IAM role to bind to the
        add-on's service account.
        :param resolve_conflicts: How to resolve parameter value conflicts when applying the new version
        of the add-on to the cluster.
        :param client_request_token: Unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :returns: UpdateAddonResponse
        :raises InvalidParameterException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ResourceInUseException:
        :raises ClientException:
        :raises ServerException:
        """
        raise NotImplementedError

    @handler("UpdateClusterConfig")
    def update_cluster_config(
        self,
        context: RequestContext,
        name: String,
        resources_vpc_config: VpcConfigRequest = None,
        logging: Logging = None,
        client_request_token: String = None,
    ) -> UpdateClusterConfigResponse:
        """Updates an Amazon EKS cluster configuration. Your cluster continues to
        function during the update. The response output includes an update ID
        that you can use to track the status of your cluster update with the
        DescribeUpdate API operation.

        You can use this API operation to enable or disable exporting the
        Kubernetes control plane logs for your cluster to CloudWatch Logs. By
        default, cluster control plane logs aren't exported to CloudWatch Logs.
        For more information, see `Amazon EKS Cluster Control Plane
        Logs <https://docs.aws.amazon.com/eks/latest/userguide/control-plane-logs.html>`__
        in the *Amazon EKS User Guide* .

        CloudWatch Logs ingestion, archive storage, and data scanning rates
        apply to exported control plane logs. For more information, see
        `CloudWatch Pricing <http://aws.amazon.com/cloudwatch/pricing/>`__.

        You can also use this API operation to enable or disable public and
        private access to your cluster's Kubernetes API server endpoint. By
        default, public access is enabled, and private access is disabled. For
        more information, see `Amazon EKS cluster endpoint access
        control <https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html>`__
        in the *Amazon EKS User Guide* .

        You can't update the subnets or security group IDs for an existing
        cluster.

        Cluster updates are asynchronous, and they should finish within a few
        minutes. During an update, the cluster status moves to ``UPDATING``
        (this status transition is eventually consistent). When the update is
        complete (either ``Failed`` or ``Successful``), the cluster status moves
        to ``Active``.

        :param name: The name of the Amazon EKS cluster to update.
        :param resources_vpc_config: An object representing the VPC configuration to use for an Amazon EKS
        cluster.
        :param logging: Enable or disable exporting the Kubernetes control plane logs for your
        cluster to CloudWatch Logs.
        :param client_request_token: Unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :returns: UpdateClusterConfigResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceInUseException:
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("UpdateClusterVersion")
    def update_cluster_version(
        self,
        context: RequestContext,
        name: String,
        version: String,
        client_request_token: String = None,
    ) -> UpdateClusterVersionResponse:
        """Updates an Amazon EKS cluster to the specified Kubernetes version. Your
        cluster continues to function during the update. The response output
        includes an update ID that you can use to track the status of your
        cluster update with the DescribeUpdate API operation.

        Cluster updates are asynchronous, and they should finish within a few
        minutes. During an update, the cluster status moves to ``UPDATING``
        (this status transition is eventually consistent). When the update is
        complete (either ``Failed`` or ``Successful``), the cluster status moves
        to ``Active``.

        If your cluster has managed node groups attached to it, all of your node
        groups’ Kubernetes versions must match the cluster’s Kubernetes version
        in order to update the cluster to a new Kubernetes version.

        :param name: The name of the Amazon EKS cluster to update.
        :param version: The desired Kubernetes version following a successful update.
        :param client_request_token: Unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :returns: UpdateClusterVersionResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceInUseException:
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("UpdateNodegroupConfig")
    def update_nodegroup_config(
        self,
        context: RequestContext,
        cluster_name: String,
        nodegroup_name: String,
        labels: UpdateLabelsPayload = None,
        taints: UpdateTaintsPayload = None,
        scaling_config: NodegroupScalingConfig = None,
        update_config: NodegroupUpdateConfig = None,
        client_request_token: String = None,
    ) -> UpdateNodegroupConfigResponse:
        """Updates an Amazon EKS managed node group configuration. Your node group
        continues to function during the update. The response output includes an
        update ID that you can use to track the status of your node group update
        with the DescribeUpdate API operation. Currently you can update the
        Kubernetes labels for a node group or the scaling configuration.

        :param cluster_name: The name of the Amazon EKS cluster that the managed node group resides
        in.
        :param nodegroup_name: The name of the managed node group to update.
        :param labels: The Kubernetes labels to be applied to the nodes in the node group after
        the update.
        :param taints: The Kubernetes taints to be applied to the nodes in the node group after
        the update.
        :param scaling_config: The scaling configuration details for the Auto Scaling group after the
        update.
        :param update_config: The node group update configuration.
        :param client_request_token: Unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :returns: UpdateNodegroupConfigResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceInUseException:
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("UpdateNodegroupVersion")
    def update_nodegroup_version(
        self,
        context: RequestContext,
        cluster_name: String,
        nodegroup_name: String,
        version: String = None,
        release_version: String = None,
        launch_template: LaunchTemplateSpecification = None,
        force: Boolean = None,
        client_request_token: String = None,
    ) -> UpdateNodegroupVersionResponse:
        """Updates the Kubernetes version or AMI version of an Amazon EKS managed
        node group.

        You can update a node group using a launch template only if the node
        group was originally deployed with a launch template. If you need to
        update a custom AMI in a node group that was deployed with a launch
        template, then update your custom AMI, specify the new ID in a new
        version of the launch template, and then update the node group to the
        new version of the launch template.

        If you update without a launch template, then you can update to the
        latest available AMI version of a node group's current Kubernetes
        version by not specifying a Kubernetes version in the request. You can
        update to the latest AMI version of your cluster's current Kubernetes
        version by specifying your cluster's Kubernetes version in the request.
        For more information, see `Amazon EKS optimized Amazon Linux 2 AMI
        versions <https://docs.aws.amazon.com/eks/latest/userguide/eks-linux-ami-versions.html>`__
        in the *Amazon EKS User Guide*.

        You cannot roll back a node group to an earlier Kubernetes version or
        AMI version.

        When a node in a managed node group is terminated due to a scaling
        action or update, the pods in that node are drained first. Amazon EKS
        attempts to drain the nodes gracefully and will fail if it is unable to
        do so. You can ``force`` the update if Amazon EKS is unable to drain the
        nodes as a result of a pod disruption budget issue.

        :param cluster_name: The name of the Amazon EKS cluster that is associated with the managed
        node group to update.
        :param nodegroup_name: The name of the managed node group to update.
        :param version: The Kubernetes version to update to.
        :param release_version: The AMI version of the Amazon EKS optimized AMI to use for the update.
        :param launch_template: An object representing a node group's launch template specification.
        :param force: Force the update if the existing node group's pods are unable to be
        drained due to a pod disruption budget issue.
        :param client_request_token: Unique, case-sensitive identifier that you provide to ensure the
        idempotency of the request.
        :returns: UpdateNodegroupVersionResponse
        :raises InvalidParameterException:
        :raises ClientException:
        :raises ServerException:
        :raises ResourceInUseException:
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError
