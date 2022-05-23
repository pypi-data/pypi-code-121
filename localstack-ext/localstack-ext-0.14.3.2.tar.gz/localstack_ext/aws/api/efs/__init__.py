import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AccessPointArn = str
AccessPointId = str
AvailabilityZoneId = str
AvailabilityZoneName = str
AwsAccountId = str
Backup = bool
BypassPolicyLockoutSafetyCheck = bool
ClientToken = str
CreationToken = str
Encrypted = bool
ErrorCode = str
ErrorMessage = str
FileSystemArn = str
FileSystemId = str
IpAddress = str
KmsKeyId = str
Marker = str
MaxItems = int
MaxResults = int
MountTargetCount = int
MountTargetId = str
Name = str
NetworkInterfaceId = str
Path = str
Permissions = str
Policy = str
ProvisionedThroughputInMibps = float
RegionName = str
ResourceId = str
SecurityGroup = str
SubnetId = str
TagKey = str
TagValue = str
Token = str
VpcId = str


class LifeCycleState(str):
    creating = "creating"
    available = "available"
    updating = "updating"
    deleting = "deleting"
    deleted = "deleted"
    error = "error"


class PerformanceMode(str):
    generalPurpose = "generalPurpose"
    maxIO = "maxIO"


class ReplicationStatus(str):
    ENABLED = "ENABLED"
    ENABLING = "ENABLING"
    DELETING = "DELETING"
    ERROR = "ERROR"


class Resource(str):
    FILE_SYSTEM = "FILE_SYSTEM"
    MOUNT_TARGET = "MOUNT_TARGET"


class ResourceIdType(str):
    LONG_ID = "LONG_ID"
    SHORT_ID = "SHORT_ID"


class Status(str):
    ENABLED = "ENABLED"
    ENABLING = "ENABLING"
    DISABLED = "DISABLED"
    DISABLING = "DISABLING"


class ThroughputMode(str):
    bursting = "bursting"
    provisioned = "provisioned"


class TransitionToIARules(str):
    AFTER_7_DAYS = "AFTER_7_DAYS"
    AFTER_14_DAYS = "AFTER_14_DAYS"
    AFTER_30_DAYS = "AFTER_30_DAYS"
    AFTER_60_DAYS = "AFTER_60_DAYS"
    AFTER_90_DAYS = "AFTER_90_DAYS"


class TransitionToPrimaryStorageClassRules(str):
    AFTER_1_ACCESS = "AFTER_1_ACCESS"


class AccessPointAlreadyExists(ServiceException):
    """Returned if the access point that you are trying to create already
    exists, with the creation token you provided in the request.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]
    AccessPointId: AccessPointId


class AccessPointLimitExceeded(ServiceException):
    """Returned if the Amazon Web Services account has already created the
    maximum number of access points allowed per file system. For more
    informaton, see
    https://docs.aws.amazon.com/efs/latest/ug/limits.html#limits-efs-resources-per-account-per-region.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class AccessPointNotFound(ServiceException):
    """Returned if the specified ``AccessPointId`` value doesn't exist in the
    requester's Amazon Web Services account.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class AvailabilityZonesMismatch(ServiceException):
    """Returned if the Availability Zone that was specified for a mount target
    is different from the Availability Zone that was specified for One Zone
    storage. For more information, see `Regional and One Zone storage
    redundancy <https://docs.aws.amazon.com/efs/latest/ug/availability-durability.html>`__.
    """

    ErrorCode: Optional[ErrorCode]
    Message: Optional[ErrorMessage]


class BadRequest(ServiceException):
    """Returned if the request is malformed or contains an error such as an
    invalid parameter value or a missing required parameter.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class DependencyTimeout(ServiceException):
    """The service timed out trying to fulfill the request, and the client
    should try the call again.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class FileSystemAlreadyExists(ServiceException):
    """Returned if the file system you are trying to create already exists,
    with the creation token you provided.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]
    FileSystemId: FileSystemId


class FileSystemInUse(ServiceException):
    """Returned if a file system has mount targets."""

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class FileSystemLimitExceeded(ServiceException):
    """Returned if the Amazon Web Services account has already created the
    maximum number of file systems allowed per account.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class FileSystemNotFound(ServiceException):
    """Returned if the specified ``FileSystemId`` value doesn't exist in the
    requester's Amazon Web Services account.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class IncorrectFileSystemLifeCycleState(ServiceException):
    """Returned if the file system's lifecycle state is not "available"."""

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class IncorrectMountTargetState(ServiceException):
    """Returned if the mount target is not in the correct state for the
    operation.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class InsufficientThroughputCapacity(ServiceException):
    """Returned if there's not enough capacity to provision additional
    throughput. This value might be returned when you try to create a file
    system in provisioned throughput mode, when you attempt to increase the
    provisioned throughput of an existing file system, or when you attempt
    to change an existing file system from Bursting Throughput to
    Provisioned Throughput mode. Try again later.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class InternalServerError(ServiceException):
    """Returned if an error occurred on the server side."""

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class InvalidPolicyException(ServiceException):
    """Returned if the ``FileSystemPolicy`` is malformed or contains an error
    such as a parameter value that is not valid or a missing required
    parameter. Returned in the case of a policy lockout safety check error.
    """

    ErrorCode: Optional[ErrorCode]
    Message: Optional[ErrorMessage]


class IpAddressInUse(ServiceException):
    """Returned if the request specified an ``IpAddress`` that is already in
    use in the subnet.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class MountTargetConflict(ServiceException):
    """Returned if the mount target would violate one of the specified
    restrictions based on the file system's existing mount targets.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class MountTargetNotFound(ServiceException):
    """Returned if there is no mount target with the specified ID found in the
    caller's Amazon Web Services account.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class NetworkInterfaceLimitExceeded(ServiceException):
    """The calling account has reached the limit for elastic network interfaces
    for the specific Amazon Web Services Region. Either delete some network
    interfaces or request that the account quota be raised. For more
    information, see `Amazon VPC
    Quotas <https://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Appendix_Limits.html>`__
    in the *Amazon VPC User Guide* (see the **Network interfaces per
    Region** entry in the **Network interfaces** table).
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class NoFreeAddressesInSubnet(ServiceException):
    """Returned if ``IpAddress`` was not specified in the request and there are
    no free IP addresses in the subnet.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class PolicyNotFound(ServiceException):
    """Returned if the default file system policy is in effect for the EFS file
    system specified.
    """

    ErrorCode: Optional[ErrorCode]
    Message: Optional[ErrorMessage]


class ReplicationNotFound(ServiceException):
    """Returned if the specified file system does not have a replication
    configuration.
    """

    ErrorCode: Optional[ErrorCode]
    Message: Optional[ErrorMessage]


class SecurityGroupLimitExceeded(ServiceException):
    """Returned if the size of ``SecurityGroups`` specified in the request is
    greater than five.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class SecurityGroupNotFound(ServiceException):
    """Returned if one of the specified security groups doesn't exist in the
    subnet's virtual private cloud (VPC).
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class SubnetNotFound(ServiceException):
    """Returned if there is no subnet with ID ``SubnetId`` provided in the
    request.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class ThrottlingException(ServiceException):
    """Returned when the ``CreateAccessPoint`` API action is called too quickly
    and the number of Access Points in the account is nearing the limit of
    120.
    """

    ErrorCode: Optional[ErrorCode]
    Message: Optional[ErrorMessage]


class ThroughputLimitExceeded(ServiceException):
    """Returned if the throughput mode or amount of provisioned throughput
    can't be changed because the throughput limit of 1024 MiB/s has been
    reached.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class TooManyRequests(ServiceException):
    """Returned if you don’t wait at least 24 hours before either changing the
    throughput mode, or decreasing the Provisioned Throughput value.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class UnsupportedAvailabilityZone(ServiceException):
    """Returned if the requested Amazon EFS functionality is not available in
    the specified Availability Zone.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


class ValidationException(ServiceException):
    """Returned if the Backup service is not available in the Amazon Web
    Services Region in which the request was made.
    """

    ErrorCode: ErrorCode
    Message: Optional[ErrorMessage]


OwnerGid = int
OwnerUid = int


class CreationInfo(TypedDict, total=False):
    """Required if the ``RootDirectory`` > ``Path`` specified does not exist.
    Specifies the POSIX IDs and permissions to apply to the access point's
    ``RootDirectory`` > ``Path``. If the access point root directory does
    not exist, EFS creates it with these settings when a client connects to
    the access point. When specifying ``CreationInfo``, you must include
    values for all properties.

    Amazon EFS creates a root directory only if you have provided the
    CreationInfo: OwnUid, OwnGID, and permissions for the directory. If you
    do not provide this information, Amazon EFS does not create the root
    directory. If the root directory does not exist, attempts to mount using
    the access point will fail.

    If you do not provide ``CreationInfo`` and the specified
    ``RootDirectory`` does not exist, attempts to mount the file system
    using the access point will fail.
    """

    OwnerUid: OwnerUid
    OwnerGid: OwnerGid
    Permissions: Permissions


class RootDirectory(TypedDict, total=False):
    """Specifies the directory on the Amazon EFS file system that the access
    point provides access to. The access point exposes the specified file
    system path as the root directory of your file system to applications
    using the access point. NFS clients using the access point can only
    access data in the access point's ``RootDirectory`` and it's
    subdirectories.
    """

    Path: Optional[Path]
    CreationInfo: Optional[CreationInfo]


Gid = int
SecondaryGids = List[Gid]
Uid = int


class PosixUser(TypedDict, total=False):
    """The full POSIX identity, including the user ID, group ID, and any
    secondary group IDs, on the access point that is used for all file
    system operations performed by NFS clients using the access point.
    """

    Uid: Uid
    Gid: Gid
    SecondaryGids: Optional[SecondaryGids]


class Tag(TypedDict, total=False):
    """A tag is a key-value pair. Allowed characters are letters, white space,
    and numbers that can be represented in UTF-8, and the following
    characters: ``+ - = . _ : /``.
    """

    Key: TagKey
    Value: TagValue


Tags = List[Tag]


class AccessPointDescription(TypedDict, total=False):
    """Provides a description of an EFS file system access point."""

    ClientToken: Optional[ClientToken]
    Name: Optional[Name]
    Tags: Optional[Tags]
    AccessPointId: Optional[AccessPointId]
    AccessPointArn: Optional[AccessPointArn]
    FileSystemId: Optional[FileSystemId]
    PosixUser: Optional[PosixUser]
    RootDirectory: Optional[RootDirectory]
    OwnerId: Optional[AwsAccountId]
    LifeCycleState: Optional[LifeCycleState]


AccessPointDescriptions = List[AccessPointDescription]


class BackupPolicy(TypedDict, total=False):
    """The backup policy for the file system used to create automatic daily
    backups. If status has a value of ``ENABLED``, the file system is being
    automatically backed up. For more information, see `Automatic
    backups <https://docs.aws.amazon.com/efs/latest/ug/awsbackup.html#automatic-backups>`__.
    """

    Status: Status


class BackupPolicyDescription(TypedDict, total=False):
    BackupPolicy: Optional[BackupPolicy]


class CreateAccessPointRequest(ServiceRequest):
    ClientToken: ClientToken
    Tags: Optional[Tags]
    FileSystemId: FileSystemId
    PosixUser: Optional[PosixUser]
    RootDirectory: Optional[RootDirectory]


class CreateFileSystemRequest(ServiceRequest):
    CreationToken: CreationToken
    PerformanceMode: Optional[PerformanceMode]
    Encrypted: Optional[Encrypted]
    KmsKeyId: Optional[KmsKeyId]
    ThroughputMode: Optional[ThroughputMode]
    ProvisionedThroughputInMibps: Optional[ProvisionedThroughputInMibps]
    AvailabilityZoneName: Optional[AvailabilityZoneName]
    Backup: Optional[Backup]
    Tags: Optional[Tags]


SecurityGroups = List[SecurityGroup]


class CreateMountTargetRequest(ServiceRequest):
    FileSystemId: FileSystemId
    SubnetId: SubnetId
    IpAddress: Optional[IpAddress]
    SecurityGroups: Optional[SecurityGroups]


class DestinationToCreate(TypedDict, total=False):
    """Describes the destination file system to create in the replication
    configuration.
    """

    Region: Optional[RegionName]
    AvailabilityZoneName: Optional[AvailabilityZoneName]
    KmsKeyId: Optional[KmsKeyId]


DestinationsToCreate = List[DestinationToCreate]


class CreateReplicationConfigurationRequest(ServiceRequest):
    SourceFileSystemId: FileSystemId
    Destinations: DestinationsToCreate


class CreateTagsRequest(ServiceRequest):
    FileSystemId: FileSystemId
    Tags: Tags


class DeleteAccessPointRequest(ServiceRequest):
    AccessPointId: AccessPointId


class DeleteFileSystemPolicyRequest(ServiceRequest):
    FileSystemId: FileSystemId


class DeleteFileSystemRequest(ServiceRequest):
    FileSystemId: FileSystemId


class DeleteMountTargetRequest(ServiceRequest):
    MountTargetId: MountTargetId


class DeleteReplicationConfigurationRequest(ServiceRequest):
    SourceFileSystemId: FileSystemId


TagKeys = List[TagKey]


class DeleteTagsRequest(ServiceRequest):
    FileSystemId: FileSystemId
    TagKeys: TagKeys


class DescribeAccessPointsRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[Token]
    AccessPointId: Optional[AccessPointId]
    FileSystemId: Optional[FileSystemId]


class DescribeAccessPointsResponse(TypedDict, total=False):
    AccessPoints: Optional[AccessPointDescriptions]
    NextToken: Optional[Token]


class DescribeAccountPreferencesRequest(ServiceRequest):
    NextToken: Optional[Token]
    MaxResults: Optional[MaxResults]


Resources = List[Resource]


class ResourceIdPreference(TypedDict, total=False):
    """Describes the resource type and its ID preference for the user's Amazon
    Web Services account, in the current Amazon Web Services Region.
    """

    ResourceIdType: Optional[ResourceIdType]
    Resources: Optional[Resources]


class DescribeAccountPreferencesResponse(TypedDict, total=False):
    ResourceIdPreference: Optional[ResourceIdPreference]
    NextToken: Optional[Token]


class DescribeBackupPolicyRequest(ServiceRequest):
    FileSystemId: FileSystemId


class DescribeFileSystemPolicyRequest(ServiceRequest):
    FileSystemId: FileSystemId


class DescribeFileSystemsRequest(ServiceRequest):
    MaxItems: Optional[MaxItems]
    Marker: Optional[Marker]
    CreationToken: Optional[CreationToken]
    FileSystemId: Optional[FileSystemId]


FileSystemNullableSizeValue = int
Timestamp = datetime
FileSystemSizeValue = int


class FileSystemSize(TypedDict, total=False):
    """The latest known metered size (in bytes) of data stored in the file
    system, in its ``Value`` field, and the time at which that size was
    determined in its ``Timestamp`` field. The value doesn't represent the
    size of a consistent snapshot of the file system, but it is eventually
    consistent when there are no writes to the file system. That is, the
    value represents the actual size only if the file system is not modified
    for a period longer than a couple of hours. Otherwise, the value is not
    necessarily the exact size the file system was at any instant in time.
    """

    Value: FileSystemSizeValue
    Timestamp: Optional[Timestamp]
    ValueInIA: Optional[FileSystemNullableSizeValue]
    ValueInStandard: Optional[FileSystemNullableSizeValue]


class FileSystemDescription(TypedDict, total=False):
    """A description of the file system."""

    OwnerId: AwsAccountId
    CreationToken: CreationToken
    FileSystemId: FileSystemId
    FileSystemArn: Optional[FileSystemArn]
    CreationTime: Timestamp
    LifeCycleState: LifeCycleState
    Name: Optional[TagValue]
    NumberOfMountTargets: MountTargetCount
    SizeInBytes: FileSystemSize
    PerformanceMode: PerformanceMode
    Encrypted: Optional[Encrypted]
    KmsKeyId: Optional[KmsKeyId]
    ThroughputMode: Optional[ThroughputMode]
    ProvisionedThroughputInMibps: Optional[ProvisionedThroughputInMibps]
    AvailabilityZoneName: Optional[AvailabilityZoneName]
    AvailabilityZoneId: Optional[AvailabilityZoneId]
    Tags: Tags


FileSystemDescriptions = List[FileSystemDescription]


class DescribeFileSystemsResponse(TypedDict, total=False):
    Marker: Optional[Marker]
    FileSystems: Optional[FileSystemDescriptions]
    NextMarker: Optional[Marker]


class DescribeLifecycleConfigurationRequest(ServiceRequest):
    FileSystemId: FileSystemId


class DescribeMountTargetSecurityGroupsRequest(ServiceRequest):
    MountTargetId: MountTargetId


class DescribeMountTargetSecurityGroupsResponse(TypedDict, total=False):
    SecurityGroups: SecurityGroups


class DescribeMountTargetsRequest(ServiceRequest):
    MaxItems: Optional[MaxItems]
    Marker: Optional[Marker]
    FileSystemId: Optional[FileSystemId]
    MountTargetId: Optional[MountTargetId]
    AccessPointId: Optional[AccessPointId]


class MountTargetDescription(TypedDict, total=False):
    """Provides a description of a mount target."""

    OwnerId: Optional[AwsAccountId]
    MountTargetId: MountTargetId
    FileSystemId: FileSystemId
    SubnetId: SubnetId
    LifeCycleState: LifeCycleState
    IpAddress: Optional[IpAddress]
    NetworkInterfaceId: Optional[NetworkInterfaceId]
    AvailabilityZoneId: Optional[AvailabilityZoneId]
    AvailabilityZoneName: Optional[AvailabilityZoneName]
    VpcId: Optional[VpcId]


MountTargetDescriptions = List[MountTargetDescription]


class DescribeMountTargetsResponse(TypedDict, total=False):
    Marker: Optional[Marker]
    MountTargets: Optional[MountTargetDescriptions]
    NextMarker: Optional[Marker]


class DescribeReplicationConfigurationsRequest(ServiceRequest):
    FileSystemId: Optional[FileSystemId]
    NextToken: Optional[Token]
    MaxResults: Optional[MaxResults]


class Destination(TypedDict, total=False):
    """Describes the destination file system in the replication configuration."""

    Status: ReplicationStatus
    FileSystemId: FileSystemId
    Region: RegionName
    LastReplicatedTimestamp: Optional[Timestamp]


Destinations = List[Destination]


class ReplicationConfigurationDescription(TypedDict, total=False):
    SourceFileSystemId: FileSystemId
    SourceFileSystemRegion: RegionName
    SourceFileSystemArn: FileSystemArn
    OriginalSourceFileSystemArn: FileSystemArn
    CreationTime: Timestamp
    Destinations: Destinations


ReplicationConfigurationDescriptions = List[ReplicationConfigurationDescription]


class DescribeReplicationConfigurationsResponse(TypedDict, total=False):
    Replications: Optional[ReplicationConfigurationDescriptions]
    NextToken: Optional[Token]


class DescribeTagsRequest(ServiceRequest):
    MaxItems: Optional[MaxItems]
    Marker: Optional[Marker]
    FileSystemId: FileSystemId


class DescribeTagsResponse(TypedDict, total=False):
    Marker: Optional[Marker]
    Tags: Tags
    NextMarker: Optional[Marker]


class FileSystemPolicyDescription(TypedDict, total=False):
    FileSystemId: Optional[FileSystemId]
    Policy: Optional[Policy]


class LifecyclePolicy(TypedDict, total=False):
    """Describes a policy used by EFS lifecycle management and EFS
    Intelligent-Tiering that specifies when to transition files into and out
    of the file system's Infrequent Access (IA) storage class. For more
    information, see `EFS Intelligent‐Tiering and EFS Lifecycle
    Management <https://docs.aws.amazon.com/efs/latest/ug/lifecycle-management-efs.html>`__.

    When using the ``put-lifecycle-configuration`` CLI command or the
    ``PutLifecycleConfiguration`` API action, Amazon EFS requires that each
    ``LifecyclePolicy`` object have only a single transition. This means
    that in a request body, ``LifecyclePolicies`` must be structured as an
    array of ``LifecyclePolicy`` objects, one object for each transition,
    ``TransitionToIA``, ``TransitionToPrimaryStorageClass``. For more
    information, see the request examples in PutLifecycleConfiguration.
    """

    TransitionToIA: Optional[TransitionToIARules]
    TransitionToPrimaryStorageClass: Optional[TransitionToPrimaryStorageClassRules]


LifecyclePolicies = List[LifecyclePolicy]


class LifecycleConfigurationDescription(TypedDict, total=False):
    LifecyclePolicies: Optional[LifecyclePolicies]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceId: ResourceId
    MaxResults: Optional[MaxResults]
    NextToken: Optional[Token]


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: Optional[Tags]
    NextToken: Optional[Token]


class ModifyMountTargetSecurityGroupsRequest(ServiceRequest):
    MountTargetId: MountTargetId
    SecurityGroups: Optional[SecurityGroups]


class PutAccountPreferencesRequest(ServiceRequest):
    ResourceIdType: ResourceIdType


class PutAccountPreferencesResponse(TypedDict, total=False):
    ResourceIdPreference: Optional[ResourceIdPreference]


class PutBackupPolicyRequest(ServiceRequest):
    FileSystemId: FileSystemId
    BackupPolicy: BackupPolicy


class PutFileSystemPolicyRequest(ServiceRequest):
    FileSystemId: FileSystemId
    Policy: Policy
    BypassPolicyLockoutSafetyCheck: Optional[BypassPolicyLockoutSafetyCheck]


class PutLifecycleConfigurationRequest(ServiceRequest):
    FileSystemId: FileSystemId
    LifecyclePolicies: LifecyclePolicies


class TagResourceRequest(ServiceRequest):
    ResourceId: ResourceId
    Tags: Tags


class UntagResourceRequest(ServiceRequest):
    ResourceId: ResourceId
    TagKeys: TagKeys


class UpdateFileSystemRequest(ServiceRequest):
    FileSystemId: FileSystemId
    ThroughputMode: Optional[ThroughputMode]
    ProvisionedThroughputInMibps: Optional[ProvisionedThroughputInMibps]


class EfsApi:

    service = "efs"
    version = "2015-02-01"

    @handler("CreateAccessPoint")
    def create_access_point(
        self,
        context: RequestContext,
        client_token: ClientToken,
        file_system_id: FileSystemId,
        tags: Tags = None,
        posix_user: PosixUser = None,
        root_directory: RootDirectory = None,
    ) -> AccessPointDescription:
        """Creates an EFS access point. An access point is an application-specific
        view into an EFS file system that applies an operating system user and
        group, and a file system path, to any file system request made through
        the access point. The operating system user and group override any
        identity information provided by the NFS client. The file system path is
        exposed as the access point's root directory. Applications using the
        access point can only access data in the application's own directory and
        any subdirectories. To learn more, see `Mounting a file system using EFS
        access
        points <https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html>`__.

        This operation requires permissions for the
        ``elasticfilesystem:CreateAccessPoint`` action.

        :param client_token: A string of up to 64 ASCII characters that Amazon EFS uses to ensure
        idempotent creation.
        :param file_system_id: The ID of the EFS file system that the access point provides access to.
        :param tags: Creates tags associated with the access point.
        :param posix_user: The operating system user and group applied to all file system requests
        made using the access point.
        :param root_directory: Specifies the directory on the Amazon EFS file system that the access
        point exposes as the root directory of your file system to NFS clients
        using the access point.
        :returns: AccessPointDescription
        :raises BadRequest:
        :raises AccessPointAlreadyExists:
        :raises IncorrectFileSystemLifeCycleState:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises AccessPointLimitExceeded:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateFileSystem")
    def create_file_system(
        self,
        context: RequestContext,
        creation_token: CreationToken,
        performance_mode: PerformanceMode = None,
        encrypted: Encrypted = None,
        kms_key_id: KmsKeyId = None,
        throughput_mode: ThroughputMode = None,
        provisioned_throughput_in_mibps: ProvisionedThroughputInMibps = None,
        availability_zone_name: AvailabilityZoneName = None,
        backup: Backup = None,
        tags: Tags = None,
    ) -> FileSystemDescription:
        """Creates a new, empty file system. The operation requires a creation
        token in the request that Amazon EFS uses to ensure idempotent creation
        (calling the operation with same creation token has no effect). If a
        file system does not currently exist that is owned by the caller's
        Amazon Web Services account with the specified creation token, this
        operation does the following:

        -  Creates a new, empty file system. The file system will have an Amazon
           EFS assigned ID, and an initial lifecycle state ``creating``.

        -  Returns with the description of the created file system.

        Otherwise, this operation returns a ``FileSystemAlreadyExists`` error
        with the ID of the existing file system.

        For basic use cases, you can use a randomly generated UUID for the
        creation token.

        The idempotent operation allows you to retry a ``CreateFileSystem`` call
        without risk of creating an extra file system. This can happen when an
        initial call fails in a way that leaves it uncertain whether or not a
        file system was actually created. An example might be that a transport
        level timeout occurred or your connection was reset. As long as you use
        the same creation token, if the initial call had succeeded in creating a
        file system, the client can learn of its existence from the
        ``FileSystemAlreadyExists`` error.

        For more information, see `Creating a file
        system <https://docs.aws.amazon.com/efs/latest/ug/creating-using-create-fs.html#creating-using-create-fs-part1>`__
        in the *Amazon EFS User Guide*.

        The ``CreateFileSystem`` call returns while the file system's lifecycle
        state is still ``creating``. You can check the file system creation
        status by calling the DescribeFileSystems operation, which among other
        things returns the file system state.

        This operation accepts an optional ``PerformanceMode`` parameter that
        you choose for your file system. We recommend ``generalPurpose``
        performance mode for most file systems. File systems using the ``maxIO``
        performance mode can scale to higher levels of aggregate throughput and
        operations per second with a tradeoff of slightly higher latencies for
        most file operations. The performance mode can't be changed after the
        file system has been created. For more information, see `Amazon EFS
        performance
        modes <https://docs.aws.amazon.com/efs/latest/ug/performance.html#performancemodes.html>`__.

        You can set the throughput mode for the file system using the
        ``ThroughputMode`` parameter.

        After the file system is fully created, Amazon EFS sets its lifecycle
        state to ``available``, at which point you can create one or more mount
        targets for the file system in your VPC. For more information, see
        CreateMountTarget. You mount your Amazon EFS file system on an EC2
        instances in your VPC by using the mount target. For more information,
        see `Amazon EFS: How it
        Works <https://docs.aws.amazon.com/efs/latest/ug/how-it-works.html>`__.

        This operation requires permissions for the
        ``elasticfilesystem:CreateFileSystem`` action.

        :param creation_token: A string of up to 64 ASCII characters.
        :param performance_mode: The performance mode of the file system.
        :param encrypted: A Boolean value that, if true, creates an encrypted file system.
        :param kms_key_id: The ID of the KMS key that you want to use to protect the encrypted file
        system.
        :param throughput_mode: Specifies the throughput mode for the file system, either ``bursting``
        or ``provisioned``.
        :param provisioned_throughput_in_mibps: The throughput, measured in MiB/s, that you want to provision for a file
        system that you're creating.
        :param availability_zone_name: Used to create a file system that uses One Zone storage classes.
        :param backup: Specifies whether automatic backups are enabled on the file system that
        you are creating.
        :param tags: Use to create one or more tags associated with the file system.
        :returns: FileSystemDescription
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemAlreadyExists:
        :raises FileSystemLimitExceeded:
        :raises InsufficientThroughputCapacity:
        :raises ThroughputLimitExceeded:
        :raises UnsupportedAvailabilityZone:
        """
        raise NotImplementedError

    @handler("CreateMountTarget")
    def create_mount_target(
        self,
        context: RequestContext,
        file_system_id: FileSystemId,
        subnet_id: SubnetId,
        ip_address: IpAddress = None,
        security_groups: SecurityGroups = None,
    ) -> MountTargetDescription:
        """Creates a mount target for a file system. You can then mount the file
        system on EC2 instances by using the mount target.

        You can create one mount target in each Availability Zone in your VPC.
        All EC2 instances in a VPC within a given Availability Zone share a
        single mount target for a given file system. If you have multiple
        subnets in an Availability Zone, you create a mount target in one of the
        subnets. EC2 instances do not need to be in the same subnet as the mount
        target in order to access their file system.

        You can create only one mount target for an EFS file system using One
        Zone storage classes. You must create that mount target in the same
        Availability Zone in which the file system is located. Use the
        ``AvailabilityZoneName`` and ``AvailabiltyZoneId`` properties in the
        DescribeFileSystems response object to get this information. Use the
        ``subnetId`` associated with the file system's Availability Zone when
        creating the mount target.

        For more information, see `Amazon EFS: How it
        Works <https://docs.aws.amazon.com/efs/latest/ug/how-it-works.html>`__.

        To create a mount target for a file system, the file system's lifecycle
        state must be ``available``. For more information, see
        DescribeFileSystems.

        In the request, provide the following:

        -  The file system ID for which you are creating the mount target.

        -  A subnet ID, which determines the following:

           -  The VPC in which Amazon EFS creates the mount target

           -  The Availability Zone in which Amazon EFS creates the mount target

           -  The IP address range from which Amazon EFS selects the IP address
              of the mount target (if you don't specify an IP address in the
              request)

        After creating the mount target, Amazon EFS returns a response that
        includes, a ``MountTargetId`` and an ``IpAddress``. You use this IP
        address when mounting the file system in an EC2 instance. You can also
        use the mount target's DNS name when mounting the file system. The EC2
        instance on which you mount the file system by using the mount target
        can resolve the mount target's DNS name to its IP address. For more
        information, see `How it Works: Implementation
        Overview <https://docs.aws.amazon.com/efs/latest/ug/how-it-works.html#how-it-works-implementation>`__.

        Note that you can create mount targets for a file system in only one
        VPC, and there can be only one mount target per Availability Zone. That
        is, if the file system already has one or more mount targets created for
        it, the subnet specified in the request to add another mount target must
        meet the following requirements:

        -  Must belong to the same VPC as the subnets of the existing mount
           targets

        -  Must not be in the same Availability Zone as any of the subnets of
           the existing mount targets

        If the request satisfies the requirements, Amazon EFS does the
        following:

        -  Creates a new mount target in the specified subnet.

        -  Also creates a new network interface in the subnet as follows:

           -  If the request provides an ``IpAddress``, Amazon EFS assigns that
              IP address to the network interface. Otherwise, Amazon EFS assigns
              a free address in the subnet (in the same way that the Amazon EC2
              ``CreateNetworkInterface`` call does when a request does not
              specify a primary private IP address).

           -  If the request provides ``SecurityGroups``, this network interface
              is associated with those security groups. Otherwise, it belongs to
              the default security group for the subnet's VPC.

           -  Assigns the description
              ``Mount target fsmt-id for file system fs-id`` where ``fsmt-id``
              is the mount target ID, and ``fs-id`` is the ``FileSystemId``.

           -  Sets the ``requesterManaged`` property of the network interface to
              ``true``, and the ``requesterId`` value to ``EFS``.

           Each Amazon EFS mount target has one corresponding requester-managed
           EC2 network interface. After the network interface is created, Amazon
           EFS sets the ``NetworkInterfaceId`` field in the mount target's
           description to the network interface ID, and the ``IpAddress`` field
           to its address. If network interface creation fails, the entire
           ``CreateMountTarget`` operation fails.

        The ``CreateMountTarget`` call returns only after creating the network
        interface, but while the mount target state is still ``creating``, you
        can check the mount target creation status by calling the
        DescribeMountTargets operation, which among other things returns the
        mount target state.

        We recommend that you create a mount target in each of the Availability
        Zones. There are cost considerations for using a file system in an
        Availability Zone through a mount target created in another Availability
        Zone. For more information, see `Amazon
        EFS <http://aws.amazon.com/efs/>`__. In addition, by always using a
        mount target local to the instance's Availability Zone, you eliminate a
        partial failure scenario. If the Availability Zone in which your mount
        target is created goes down, then you can't access your file system
        through that mount target.

        This operation requires permissions for the following action on the file
        system:

        -  ``elasticfilesystem:CreateMountTarget``

        This operation also requires permissions for the following Amazon EC2
        actions:

        -  ``ec2:DescribeSubnets``

        -  ``ec2:DescribeNetworkInterfaces``

        -  ``ec2:CreateNetworkInterface``

        :param file_system_id: The ID of the file system for which to create the mount target.
        :param subnet_id: The ID of the subnet to add the mount target in.
        :param ip_address: Valid IPv4 address within the address range of the specified subnet.
        :param security_groups: Up to five VPC security group IDs, of the form ``sg-xxxxxxxx``.
        :returns: MountTargetDescription
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises IncorrectFileSystemLifeCycleState:
        :raises MountTargetConflict:
        :raises SubnetNotFound:
        :raises NoFreeAddressesInSubnet:
        :raises IpAddressInUse:
        :raises NetworkInterfaceLimitExceeded:
        :raises SecurityGroupLimitExceeded:
        :raises SecurityGroupNotFound:
        :raises UnsupportedAvailabilityZone:
        :raises AvailabilityZonesMismatch:
        """
        raise NotImplementedError

    @handler("CreateReplicationConfiguration")
    def create_replication_configuration(
        self,
        context: RequestContext,
        source_file_system_id: FileSystemId,
        destinations: DestinationsToCreate,
    ) -> ReplicationConfigurationDescription:
        """Creates a replication configuration that replicates an existing EFS file
        system to a new, read-only file system. For more information, see
        `Amazon EFS
        replication <https://docs.aws.amazon.com/efs/latest/ug/efs-replication.html>`__
        in the *Amazon EFS User Guide*. The replication configuration specifies
        the following:

        -  **Source file system** - An existing EFS file system that you want
           replicated. The source file system cannot be a destination file
           system in an existing replication configuration.

        -  **Destination file system configuration** - The configuration of the
           destination file system to which the source file system will be
           replicated. There can only be one destination file system in a
           replication configuration. The destination file system configuration
           consists of the following properties:

           -  **Amazon Web Services Region** - The Amazon Web Services Region in
              which the destination file system is created. Amazon EFS
              replication is available in all Amazon Web Services Regions that
              Amazon EFS is available in, except Africa (Cape Town), Asia
              Pacific (Hong Kong), Asia Pacific (Jakarta), Europe (Milan), and
              Middle East (Bahrain).

           -  **Availability Zone** - If you want the destination file system to
              use EFS One Zone availability and durability, you must specify the
              Availability Zone to create the file system in. For more
              information about EFS storage classes, see `Amazon EFS storage
              classes <https://docs.aws.amazon.com/efs/latest/ug/storage-classes.html>`__
              in the *Amazon EFS User Guide*.

           -  **Encryption** - All destination file systems are created with
              encryption at rest enabled. You can specify the Key Management
              Service (KMS) key that is used to encrypt the destination file
              system. If you don't specify a KMS key, your service-managed KMS
              key for Amazon EFS is used.

              After the file system is created, you cannot change the KMS key.

        The following properties are set by default:

        -  **Performance mode** - The destination file system's performance mode
           matches that of the source file system, unless the destination file
           system uses EFS One Zone storage. In that case, the General Purpose
           performance mode is used. The performance mode cannot be changed.

        -  **Throughput mode** - The destination file system uses the Bursting
           Throughput mode by default. After the file system is created, you can
           modify the throughput mode.

        The following properties are turned off by default:

        -  **Lifecycle management** - EFS lifecycle management and EFS
           Intelligent-Tiering are not enabled on the destination file system.
           After the destination file system is created, you can enable EFS
           lifecycle management and EFS Intelligent-Tiering.

        -  **Automatic backups** - Automatic daily backups not enabled on the
           destination file system. After the file system is created, you can
           change this setting.

        For more information, see `Amazon EFS
        replication <https://docs.aws.amazon.com/efs/latest/ug/efs-replication.html>`__
        in the *Amazon EFS User Guide*.

        :param source_file_system_id: Specifies the Amazon EFS file system that you want to replicate.
        :param destinations: An array of destination configuration objects.
        :returns: ReplicationConfigurationDescription
        :raises BadRequest:
        :raises IncorrectFileSystemLifeCycleState:
        :raises ValidationException:
        :raises ReplicationNotFound:
        :raises FileSystemNotFound:
        :raises UnsupportedAvailabilityZone:
        :raises FileSystemLimitExceeded:
        :raises InsufficientThroughputCapacity:
        :raises ThroughputLimitExceeded:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("CreateTags")
    def create_tags(
        self, context: RequestContext, file_system_id: FileSystemId, tags: Tags
    ) -> None:
        """DEPRECATED - ``CreateTags`` is deprecated and not maintained. To create
        tags for EFS resources, use the API action.

        Creates or overwrites tags associated with a file system. Each tag is a
        key-value pair. If a tag key specified in the request already exists on
        the file system, this operation overwrites its value with the value
        provided in the request. If you add the ``Name`` tag to your file
        system, Amazon EFS returns it in the response to the DescribeFileSystems
        operation.

        This operation requires permission for the
        ``elasticfilesystem:CreateTags`` action.

        :param file_system_id: The ID of the file system whose tags you want to modify (String).
        :param tags: An array of ``Tag`` objects to add.
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        """
        raise NotImplementedError

    @handler("DeleteAccessPoint")
    def delete_access_point(self, context: RequestContext, access_point_id: AccessPointId) -> None:
        """Deletes the specified access point. After deletion is complete, new
        clients can no longer connect to the access points. Clients connected to
        the access point at the time of deletion will continue to function until
        they terminate their connection.

        This operation requires permissions for the
        ``elasticfilesystem:DeleteAccessPoint`` action.

        :param access_point_id: The ID of the access point that you want to delete.
        :raises BadRequest:
        :raises InternalServerError:
        :raises AccessPointNotFound:
        """
        raise NotImplementedError

    @handler("DeleteFileSystem")
    def delete_file_system(self, context: RequestContext, file_system_id: FileSystemId) -> None:
        """Deletes a file system, permanently severing access to its contents. Upon
        return, the file system no longer exists and you can't access any
        contents of the deleted file system.

        You need to manually delete mount targets attached to a file system
        before you can delete an EFS file system. This step is performed for you
        when you use the Amazon Web Services console to delete a file system.

        You cannot delete a file system that is part of an EFS Replication
        configuration. You need to delete the replication configuration first.

        You can't delete a file system that is in use. That is, if the file
        system has any mount targets, you must first delete them. For more
        information, see DescribeMountTargets and DeleteMountTarget.

        The ``DeleteFileSystem`` call returns while the file system state is
        still ``deleting``. You can check the file system deletion status by
        calling the DescribeFileSystems operation, which returns a list of file
        systems in your account. If you pass file system ID or creation token
        for the deleted file system, the DescribeFileSystems returns a
        ``404 FileSystemNotFound`` error.

        This operation requires permissions for the
        ``elasticfilesystem:DeleteFileSystem`` action.

        :param file_system_id: The ID of the file system you want to delete.
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises FileSystemInUse:
        """
        raise NotImplementedError

    @handler("DeleteFileSystemPolicy")
    def delete_file_system_policy(
        self, context: RequestContext, file_system_id: FileSystemId
    ) -> None:
        """Deletes the ``FileSystemPolicy`` for the specified file system. The
        default ``FileSystemPolicy`` goes into effect once the existing policy
        is deleted. For more information about the default file system policy,
        see `Using Resource-based Policies with
        EFS <https://docs.aws.amazon.com/efs/latest/ug/res-based-policies-efs.html>`__.

        This operation requires permissions for the
        ``elasticfilesystem:DeleteFileSystemPolicy`` action.

        :param file_system_id: Specifies the EFS file system for which to delete the
        ``FileSystemPolicy``.
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises IncorrectFileSystemLifeCycleState:
        """
        raise NotImplementedError

    @handler("DeleteMountTarget")
    def delete_mount_target(self, context: RequestContext, mount_target_id: MountTargetId) -> None:
        """Deletes the specified mount target.

        This operation forcibly breaks any mounts of the file system by using
        the mount target that is being deleted, which might disrupt instances or
        applications using those mounts. To avoid applications getting cut off
        abruptly, you might consider unmounting any mounts of the mount target,
        if feasible. The operation also deletes the associated network
        interface. Uncommitted writes might be lost, but breaking a mount target
        using this operation does not corrupt the file system itself. The file
        system you created remains. You can mount an EC2 instance in your VPC by
        using another mount target.

        This operation requires permissions for the following action on the file
        system:

        -  ``elasticfilesystem:DeleteMountTarget``

        The ``DeleteMountTarget`` call returns while the mount target state is
        still ``deleting``. You can check the mount target deletion by calling
        the DescribeMountTargets operation, which returns a list of mount target
        descriptions for the given file system.

        The operation also requires permissions for the following Amazon EC2
        action on the mount target's network interface:

        -  ``ec2:DeleteNetworkInterface``

        :param mount_target_id: The ID of the mount target to delete (String).
        :raises BadRequest:
        :raises InternalServerError:
        :raises DependencyTimeout:
        :raises MountTargetNotFound:
        """
        raise NotImplementedError

    @handler("DeleteReplicationConfiguration")
    def delete_replication_configuration(
        self, context: RequestContext, source_file_system_id: FileSystemId
    ) -> None:
        """Deletes an existing replication configuration. To delete a replication
        configuration, you must make the request from the Amazon Web Services
        Region in which the destination file system is located. Deleting a
        replication configuration ends the replication process. After a
        replication configuration is deleted, the destination file system is no
        longer read-only. You can write to the destination file system after its
        status becomes ``Writeable``.

        :param source_file_system_id: The ID of the source file system in the replication configuration.
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises ReplicationNotFound:
        """
        raise NotImplementedError

    @handler("DeleteTags")
    def delete_tags(
        self, context: RequestContext, file_system_id: FileSystemId, tag_keys: TagKeys
    ) -> None:
        """DEPRECATED - ``DeleteTags`` is deprecated and not maintained. To remove
        tags from EFS resources, use the API action.

        Deletes the specified tags from a file system. If the ``DeleteTags``
        request includes a tag key that doesn't exist, Amazon EFS ignores it and
        doesn't cause an error. For more information about tags and related
        restrictions, see `Tag
        restrictions <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html>`__
        in the *Billing and Cost Management User Guide*.

        This operation requires permissions for the
        ``elasticfilesystem:DeleteTags`` action.

        :param file_system_id: The ID of the file system whose tags you want to delete (String).
        :param tag_keys: A list of tag keys to delete.
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        """
        raise NotImplementedError

    @handler("DescribeAccessPoints")
    def describe_access_points(
        self,
        context: RequestContext,
        max_results: MaxResults = None,
        next_token: Token = None,
        access_point_id: AccessPointId = None,
        file_system_id: FileSystemId = None,
    ) -> DescribeAccessPointsResponse:
        """Returns the description of a specific Amazon EFS access point if the
        ``AccessPointId`` is provided. If you provide an EFS ``FileSystemId``,
        it returns descriptions of all access points for that file system. You
        can provide either an ``AccessPointId`` or a ``FileSystemId`` in the
        request, but not both.

        This operation requires permissions for the
        ``elasticfilesystem:DescribeAccessPoints`` action.

        :param max_results: (Optional) When retrieving all access points for a file system, you can
        optionally specify the ``MaxItems`` parameter to limit the number of
        objects returned in a response.
        :param next_token: ``NextToken`` is present if the response is paginated.
        :param access_point_id: (Optional) Specifies an EFS access point to describe in the response;
        mutually exclusive with ``FileSystemId``.
        :param file_system_id: (Optional) If you provide a ``FileSystemId``, EFS returns all access
        points for that file system; mutually exclusive with ``AccessPointId``.
        :returns: DescribeAccessPointsResponse
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises AccessPointNotFound:
        """
        raise NotImplementedError

    @handler("DescribeAccountPreferences")
    def describe_account_preferences(
        self, context: RequestContext, next_token: Token = None, max_results: MaxResults = None
    ) -> DescribeAccountPreferencesResponse:
        """Returns the account preferences settings for the Amazon Web Services
        account associated with the user making the request, in the current
        Amazon Web Services Region. For more information, see `Managing Amazon
        EFS resource IDs <efs/latest/ug/manage-efs-resource-ids.html>`__.

        :param next_token: (Optional) You can use ``NextToken`` in a subsequent request to fetch
        the next page of Amazon Web Services account preferences if the response
        payload was paginated.
        :param max_results: (Optional) When retrieving account preferences, you can optionally
        specify the ``MaxItems`` parameter to limit the number of objects
        returned in a response.
        :returns: DescribeAccountPreferencesResponse
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("DescribeBackupPolicy")
    def describe_backup_policy(
        self, context: RequestContext, file_system_id: FileSystemId
    ) -> BackupPolicyDescription:
        """Returns the backup policy for the specified EFS file system.

        :param file_system_id: Specifies which EFS file system to retrieve the ``BackupPolicy`` for.
        :returns: BackupPolicyDescription
        :raises BadRequest:
        :raises FileSystemNotFound:
        :raises InternalServerError:
        :raises PolicyNotFound:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("DescribeFileSystemPolicy")
    def describe_file_system_policy(
        self, context: RequestContext, file_system_id: FileSystemId
    ) -> FileSystemPolicyDescription:
        """Returns the ``FileSystemPolicy`` for the specified EFS file system.

        This operation requires permissions for the
        ``elasticfilesystem:DescribeFileSystemPolicy`` action.

        :param file_system_id: Specifies which EFS file system to retrieve the ``FileSystemPolicy``
        for.
        :returns: FileSystemPolicyDescription
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises PolicyNotFound:
        """
        raise NotImplementedError

    @handler("DescribeFileSystems")
    def describe_file_systems(
        self,
        context: RequestContext,
        max_items: MaxItems = None,
        marker: Marker = None,
        creation_token: CreationToken = None,
        file_system_id: FileSystemId = None,
    ) -> DescribeFileSystemsResponse:
        """Returns the description of a specific Amazon EFS file system if either
        the file system ``CreationToken`` or the ``FileSystemId`` is provided.
        Otherwise, it returns descriptions of all file systems owned by the
        caller's Amazon Web Services account in the Amazon Web Services Region
        of the endpoint that you're calling.

        When retrieving all file system descriptions, you can optionally specify
        the ``MaxItems`` parameter to limit the number of descriptions in a
        response. Currently, this number is automatically set to 10. If more
        file system descriptions remain, Amazon EFS returns a ``NextMarker``, an
        opaque token, in the response. In this case, you should send a
        subsequent request with the ``Marker`` request parameter set to the
        value of ``NextMarker``.

        To retrieve a list of your file system descriptions, this operation is
        used in an iterative process, where ``DescribeFileSystems`` is called
        first without the ``Marker`` and then the operation continues to call it
        with the ``Marker`` parameter set to the value of the ``NextMarker``
        from the previous response until the response has no ``NextMarker``.

        The order of file systems returned in the response of one
        ``DescribeFileSystems`` call and the order of file systems returned
        across the responses of a multi-call iteration is unspecified.

        This operation requires permissions for the
        ``elasticfilesystem:DescribeFileSystems`` action.

        :param max_items: (Optional) Specifies the maximum number of file systems to return in the
        response (integer).
        :param marker: (Optional) Opaque pagination token returned from a previous
        ``DescribeFileSystems`` operation (String).
        :param creation_token: (Optional) Restricts the list to the file system with this creation
        token (String).
        :param file_system_id: (Optional) ID of the file system whose description you want to retrieve
        (String).
        :returns: DescribeFileSystemsResponse
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        """
        raise NotImplementedError

    @handler("DescribeLifecycleConfiguration")
    def describe_lifecycle_configuration(
        self, context: RequestContext, file_system_id: FileSystemId
    ) -> LifecycleConfigurationDescription:
        """Returns the current ``LifecycleConfiguration`` object for the specified
        Amazon EFS file system. EFS lifecycle management uses the
        ``LifecycleConfiguration`` object to identify which files to move to the
        EFS Infrequent Access (IA) storage class. For a file system without a
        ``LifecycleConfiguration`` object, the call returns an empty array in
        the response.

        When EFS Intelligent-Tiering is enabled,
        ``TransitionToPrimaryStorageClass`` has a value of ``AFTER_1_ACCESS``.

        This operation requires permissions for the
        ``elasticfilesystem:DescribeLifecycleConfiguration`` operation.

        :param file_system_id: The ID of the file system whose ``LifecycleConfiguration`` object you
        want to retrieve (String).
        :returns: LifecycleConfigurationDescription
        :raises InternalServerError:
        :raises BadRequest:
        :raises FileSystemNotFound:
        """
        raise NotImplementedError

    @handler("DescribeMountTargetSecurityGroups")
    def describe_mount_target_security_groups(
        self, context: RequestContext, mount_target_id: MountTargetId
    ) -> DescribeMountTargetSecurityGroupsResponse:
        """Returns the security groups currently in effect for a mount target. This
        operation requires that the network interface of the mount target has
        been created and the lifecycle state of the mount target is not
        ``deleted``.

        This operation requires permissions for the following actions:

        -  ``elasticfilesystem:DescribeMountTargetSecurityGroups`` action on the
           mount target's file system.

        -  ``ec2:DescribeNetworkInterfaceAttribute`` action on the mount
           target's network interface.

        :param mount_target_id: The ID of the mount target whose security groups you want to retrieve.
        :returns: DescribeMountTargetSecurityGroupsResponse
        :raises BadRequest:
        :raises InternalServerError:
        :raises MountTargetNotFound:
        :raises IncorrectMountTargetState:
        """
        raise NotImplementedError

    @handler("DescribeMountTargets")
    def describe_mount_targets(
        self,
        context: RequestContext,
        max_items: MaxItems = None,
        marker: Marker = None,
        file_system_id: FileSystemId = None,
        mount_target_id: MountTargetId = None,
        access_point_id: AccessPointId = None,
    ) -> DescribeMountTargetsResponse:
        """Returns the descriptions of all the current mount targets, or a specific
        mount target, for a file system. When requesting all of the current
        mount targets, the order of mount targets returned in the response is
        unspecified.

        This operation requires permissions for the
        ``elasticfilesystem:DescribeMountTargets`` action, on either the file
        system ID that you specify in ``FileSystemId``, or on the file system of
        the mount target that you specify in ``MountTargetId``.

        :param max_items: (Optional) Maximum number of mount targets to return in the response.
        :param marker: (Optional) Opaque pagination token returned from a previous
        ``DescribeMountTargets`` operation (String).
        :param file_system_id: (Optional) ID of the file system whose mount targets you want to list
        (String).
        :param mount_target_id: (Optional) ID of the mount target that you want to have described
        (String).
        :param access_point_id: (Optional) The ID of the access point whose mount targets that you want
        to list.
        :returns: DescribeMountTargetsResponse
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises MountTargetNotFound:
        :raises AccessPointNotFound:
        """
        raise NotImplementedError

    @handler("DescribeReplicationConfigurations")
    def describe_replication_configurations(
        self,
        context: RequestContext,
        file_system_id: FileSystemId = None,
        next_token: Token = None,
        max_results: MaxResults = None,
    ) -> DescribeReplicationConfigurationsResponse:
        """Retrieves the replication configuration for a specific file system. If a
        file system is not specified, all of the replication configurations for
        the Amazon Web Services account in an Amazon Web Services Region are
        retrieved.

        :param file_system_id: You can retrieve the replication configuration for a specific file
        system by providing its file system ID.
        :param next_token: ``NextToken`` is present if the response is paginated.
        :param max_results: (Optional) To limit the number of objects returned in a response, you
        can specify the ``MaxItems`` parameter.
        :returns: DescribeReplicationConfigurationsResponse
        :raises BadRequest:
        :raises FileSystemNotFound:
        :raises InternalServerError:
        :raises ReplicationNotFound:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("DescribeTags")
    def describe_tags(
        self,
        context: RequestContext,
        file_system_id: FileSystemId,
        max_items: MaxItems = None,
        marker: Marker = None,
    ) -> DescribeTagsResponse:
        """DEPRECATED - The ``DescribeTags`` action is deprecated and not
        maintained. To view tags associated with EFS resources, use the
        ``ListTagsForResource`` API action.

        Returns the tags associated with a file system. The order of tags
        returned in the response of one ``DescribeTags`` call and the order of
        tags returned across the responses of a multiple-call iteration (when
        using pagination) is unspecified.

        This operation requires permissions for the
        ``elasticfilesystem:DescribeTags`` action.

        :param file_system_id: The ID of the file system whose tag set you want to retrieve.
        :param max_items: (Optional) The maximum number of file system tags to return in the
        response.
        :param marker: (Optional) An opaque pagination token returned from a previous
        ``DescribeTags`` operation (String).
        :returns: DescribeTagsResponse
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self,
        context: RequestContext,
        resource_id: ResourceId,
        max_results: MaxResults = None,
        next_token: Token = None,
    ) -> ListTagsForResourceResponse:
        """Lists all tags for a top-level EFS resource. You must provide the ID of
        the resource that you want to retrieve the tags for.

        This operation requires permissions for the
        ``elasticfilesystem:DescribeAccessPoints`` action.

        :param resource_id: Specifies the EFS resource you want to retrieve tags for.
        :param max_results: (Optional) Specifies the maximum number of tag objects to return in the
        response.
        :param next_token: (Optional) You can use ``NextToken`` in a subsequent request to fetch
        the next page of access point descriptions if the response payload was
        paginated.
        :returns: ListTagsForResourceResponse
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises AccessPointNotFound:
        """
        raise NotImplementedError

    @handler("ModifyMountTargetSecurityGroups")
    def modify_mount_target_security_groups(
        self,
        context: RequestContext,
        mount_target_id: MountTargetId,
        security_groups: SecurityGroups = None,
    ) -> None:
        """Modifies the set of security groups in effect for a mount target.

        When you create a mount target, Amazon EFS also creates a new network
        interface. For more information, see CreateMountTarget. This operation
        replaces the security groups in effect for the network interface
        associated with a mount target, with the ``SecurityGroups`` provided in
        the request. This operation requires that the network interface of the
        mount target has been created and the lifecycle state of the mount
        target is not ``deleted``.

        The operation requires permissions for the following actions:

        -  ``elasticfilesystem:ModifyMountTargetSecurityGroups`` action on the
           mount target's file system.

        -  ``ec2:ModifyNetworkInterfaceAttribute`` action on the mount target's
           network interface.

        :param mount_target_id: The ID of the mount target whose security groups you want to modify.
        :param security_groups: An array of up to five VPC security group IDs.
        :raises BadRequest:
        :raises InternalServerError:
        :raises MountTargetNotFound:
        :raises IncorrectMountTargetState:
        :raises SecurityGroupLimitExceeded:
        :raises SecurityGroupNotFound:
        """
        raise NotImplementedError

    @handler("PutAccountPreferences")
    def put_account_preferences(
        self, context: RequestContext, resource_id_type: ResourceIdType
    ) -> PutAccountPreferencesResponse:
        """Use this operation to set the account preference in the current Amazon
        Web Services Region to use long 17 character (63 bit) or short 8
        character (32 bit) resource IDs for new EFS file system and mount target
        resources. All existing resource IDs are not affected by any changes you
        make. You can set the ID preference during the opt-in period as EFS
        transitions to long resource IDs. For more information, see `Managing
        Amazon EFS resource
        IDs <https://docs.aws.amazon.com/efs/latest/ug/manage-efs-resource-ids.html>`__.

        Starting in October, 2021, you will receive an error if you try to set
        the account preference to use the short 8 character format resource ID.
        Contact Amazon Web Services support if you receive an error and must use
        short IDs for file system and mount target resources.

        :param resource_id_type: Specifies the EFS resource ID preference to set for the user's Amazon
        Web Services account, in the current Amazon Web Services Region, either
        ``LONG_ID`` (17 characters), or ``SHORT_ID`` (8 characters).
        :returns: PutAccountPreferencesResponse
        :raises BadRequest:
        :raises InternalServerError:
        """
        raise NotImplementedError

    @handler("PutBackupPolicy")
    def put_backup_policy(
        self, context: RequestContext, file_system_id: FileSystemId, backup_policy: BackupPolicy
    ) -> BackupPolicyDescription:
        """Updates the file system's backup policy. Use this action to start or
        stop automatic backups of the file system.

        :param file_system_id: Specifies which EFS file system to update the backup policy for.
        :param backup_policy: The backup policy included in the ``PutBackupPolicy`` request.
        :returns: BackupPolicyDescription
        :raises BadRequest:
        :raises FileSystemNotFound:
        :raises IncorrectFileSystemLifeCycleState:
        :raises InternalServerError:
        :raises ValidationException:
        """
        raise NotImplementedError

    @handler("PutFileSystemPolicy")
    def put_file_system_policy(
        self,
        context: RequestContext,
        file_system_id: FileSystemId,
        policy: Policy,
        bypass_policy_lockout_safety_check: BypassPolicyLockoutSafetyCheck = None,
    ) -> FileSystemPolicyDescription:
        """Applies an Amazon EFS ``FileSystemPolicy`` to an Amazon EFS file system.
        A file system policy is an IAM resource-based policy and can contain
        multiple policy statements. A file system always has exactly one file
        system policy, which can be the default policy or an explicit policy set
        or updated using this API operation. EFS file system policies have a
        20,000 character limit. When an explicit policy is set, it overrides the
        default policy. For more information about the default file system
        policy, see `Default EFS File System
        Policy <https://docs.aws.amazon.com/efs/latest/ug/iam-access-control-nfs-efs.html#default-filesystempolicy>`__.

        EFS file system policies have a 20,000 character limit.

        This operation requires permissions for the
        ``elasticfilesystem:PutFileSystemPolicy`` action.

        :param file_system_id: The ID of the EFS file system that you want to create or update the
        ``FileSystemPolicy`` for.
        :param policy: The ``FileSystemPolicy`` that you're creating.
        :param bypass_policy_lockout_safety_check: (Optional) A boolean that specifies whether or not to bypass the
        ``FileSystemPolicy`` lockout safety check.
        :returns: FileSystemPolicyDescription
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises InvalidPolicyException:
        :raises IncorrectFileSystemLifeCycleState:
        """
        raise NotImplementedError

    @handler("PutLifecycleConfiguration")
    def put_lifecycle_configuration(
        self,
        context: RequestContext,
        file_system_id: FileSystemId,
        lifecycle_policies: LifecyclePolicies,
    ) -> LifecycleConfigurationDescription:
        """Use this action to manage EFS lifecycle management and intelligent
        tiering. A ``LifecycleConfiguration`` consists of one or more
        ``LifecyclePolicy`` objects that define the following:

        -  **EFS Lifecycle management** - When Amazon EFS automatically
           transitions files in a file system into the lower-cost Infrequent
           Access (IA) storage class.

           To enable EFS Lifecycle management, set the value of
           ``TransitionToIA`` to one of the available options.

        -  **EFS Intelligent tiering** - When Amazon EFS automatically
           transitions files from IA back into the file system's primary storage
           class (Standard or One Zone Standard.

           To enable EFS Intelligent Tiering, set the value of
           ``TransitionToPrimaryStorageClass`` to ``AFTER_1_ACCESS``.

        For more information, see `EFS Lifecycle
        Management <https://docs.aws.amazon.com/efs/latest/ug/lifecycle-management-efs.html>`__.

        Each Amazon EFS file system supports one lifecycle configuration, which
        applies to all files in the file system. If a ``LifecycleConfiguration``
        object already exists for the specified file system, a
        ``PutLifecycleConfiguration`` call modifies the existing configuration.
        A ``PutLifecycleConfiguration`` call with an empty ``LifecyclePolicies``
        array in the request body deletes any existing
        ``LifecycleConfiguration`` and turns off lifecycle management and
        intelligent tiering for the file system.

        In the request, specify the following:

        -  The ID for the file system for which you are enabling, disabling, or
           modifying lifecycle management and intelligent tiering.

        -  A ``LifecyclePolicies`` array of ``LifecyclePolicy`` objects that
           define when files are moved into IA storage, and when they are moved
           back to Standard storage.

           Amazon EFS requires that each ``LifecyclePolicy`` object have only
           have a single transition, so the ``LifecyclePolicies`` array needs to
           be structured with separate ``LifecyclePolicy`` objects. See the
           example requests in the following section for more information.

        This operation requires permissions for the
        ``elasticfilesystem:PutLifecycleConfiguration`` operation.

        To apply a ``LifecycleConfiguration`` object to an encrypted file
        system, you need the same Key Management Service permissions as when you
        created the encrypted file system.

        :param file_system_id: The ID of the file system for which you are creating the
        ``LifecycleConfiguration`` object (String).
        :param lifecycle_policies: An array of ``LifecyclePolicy`` objects that define the file system's
        ``LifecycleConfiguration`` object.
        :returns: LifecycleConfigurationDescription
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises IncorrectFileSystemLifeCycleState:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(self, context: RequestContext, resource_id: ResourceId, tags: Tags) -> None:
        """Creates a tag for an EFS resource. You can create tags for EFS file
        systems and access points using this API operation.

        This operation requires permissions for the
        ``elasticfilesystem:TagResource`` action.

        :param resource_id: The ID specifying the EFS resource that you want to create a tag for.
        :param tags: An array of ``Tag`` objects to add.
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises AccessPointNotFound:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_id: ResourceId, tag_keys: TagKeys
    ) -> None:
        """Removes tags from an EFS resource. You can remove tags from EFS file
        systems and access points using this API operation.

        This operation requires permissions for the
        ``elasticfilesystem:UntagResource`` action.

        :param resource_id: Specifies the EFS resource that you want to remove tags from.
        :param tag_keys: The keys of the key-value tag pairs that you want to remove from the
        specified EFS resource.
        :raises BadRequest:
        :raises InternalServerError:
        :raises FileSystemNotFound:
        :raises AccessPointNotFound:
        """
        raise NotImplementedError

    @handler("UpdateFileSystem")
    def update_file_system(
        self,
        context: RequestContext,
        file_system_id: FileSystemId,
        throughput_mode: ThroughputMode = None,
        provisioned_throughput_in_mibps: ProvisionedThroughputInMibps = None,
    ) -> FileSystemDescription:
        """Updates the throughput mode or the amount of provisioned throughput of
        an existing file system.

        :param file_system_id: The ID of the file system that you want to update.
        :param throughput_mode: (Optional) Updates the file system's throughput mode.
        :param provisioned_throughput_in_mibps: (Optional) Sets the amount of provisioned throughput, in MiB/s, for the
        file system.
        :returns: FileSystemDescription
        :raises BadRequest:
        :raises FileSystemNotFound:
        :raises IncorrectFileSystemLifeCycleState:
        :raises InsufficientThroughputCapacity:
        :raises InternalServerError:
        :raises ThroughputLimitExceeded:
        :raises TooManyRequests:
        """
        raise NotImplementedError
