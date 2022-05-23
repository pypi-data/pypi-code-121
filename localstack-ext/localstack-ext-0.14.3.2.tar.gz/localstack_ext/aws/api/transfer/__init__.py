import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AddressAllocationId = str
Arn = str
CallbackToken = str
Certificate = str
CustomStepTarget = str
CustomStepTimeoutSeconds = int
DirectoryId = str
EfsFileSystemId = str
EfsPath = str
ExecutionErrorMessage = str
ExecutionId = str
ExternalId = str
Fips = bool
Function = str
HomeDirectory = str
HostKey = str
HostKeyFingerprint = str
LogGroupName = str
MapEntry = str
MapTarget = str
MaxResults = int
Message = str
NextToken = str
NullableRole = str
PassiveIp = str
Policy = str
PostAuthenticationLoginBanner = str
PreAuthenticationLoginBanner = str
Resource = str
ResourceType = str
Response = str
RetryAfterSeconds = str
Role = str
S3Bucket = str
S3Etag = str
S3Key = str
S3TagKey = str
S3TagValue = str
S3VersionId = str
SecurityGroupId = str
SecurityPolicyName = str
SecurityPolicyOption = str
ServerId = str
ServiceErrorMessage = str
SessionId = str
SourceFileLocation = str
SourceIp = str
SshPublicKeyBody = str
SshPublicKeyCount = int
SshPublicKeyId = str
StatusCode = int
StepResultOutputsJson = str
SubnetId = str
TagKey = str
TagValue = str
Url = str
UserCount = int
UserName = str
UserPassword = str
VpcEndpointId = str
VpcId = str
WorkflowDescription = str
WorkflowId = str
WorkflowStepName = str


class CustomStepStatus(str):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class Domain(str):
    S3 = "S3"
    EFS = "EFS"


class EndpointType(str):
    PUBLIC = "PUBLIC"
    VPC = "VPC"
    VPC_ENDPOINT = "VPC_ENDPOINT"


class ExecutionErrorType(str):
    PERMISSION_DENIED = "PERMISSION_DENIED"
    CUSTOM_STEP_FAILED = "CUSTOM_STEP_FAILED"
    THROTTLED = "THROTTLED"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    TIMEOUT = "TIMEOUT"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


class ExecutionStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    EXCEPTION = "EXCEPTION"
    HANDLING_EXCEPTION = "HANDLING_EXCEPTION"


class HomeDirectoryType(str):
    PATH = "PATH"
    LOGICAL = "LOGICAL"


class IdentityProviderType(str):
    SERVICE_MANAGED = "SERVICE_MANAGED"
    API_GATEWAY = "API_GATEWAY"
    AWS_DIRECTORY_SERVICE = "AWS_DIRECTORY_SERVICE"
    AWS_LAMBDA = "AWS_LAMBDA"


class OverwriteExisting(str):
    TRUE = "TRUE"
    FALSE = "FALSE"


class Protocol(str):
    SFTP = "SFTP"
    FTP = "FTP"
    FTPS = "FTPS"


class State(str):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    STARTING = "STARTING"
    STOPPING = "STOPPING"
    START_FAILED = "START_FAILED"
    STOP_FAILED = "STOP_FAILED"


class TlsSessionResumptionMode(str):
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    ENFORCED = "ENFORCED"


class WorkflowStepType(str):
    COPY = "COPY"
    CUSTOM = "CUSTOM"
    TAG = "TAG"
    DELETE = "DELETE"


class AccessDeniedException(ServiceException):
    """You do not have sufficient access to perform this action."""

    Message: Optional[ServiceErrorMessage]


class ConflictException(ServiceException):
    """This exception is thrown when the ``UpdateServer`` is called for a file
    transfer protocol-enabled server that has VPC as the endpoint type and
    the server's ``VpcEndpointID`` is not in the available state.
    """

    Message: Message


class InternalServiceError(ServiceException):
    """This exception is thrown when an error occurs in the Amazon Web
    ServicesTransfer Family service.
    """

    Message: Message


class InvalidNextTokenException(ServiceException):
    """The ``NextToken`` parameter that was passed is invalid."""

    Message: Message


class InvalidRequestException(ServiceException):
    """This exception is thrown when the client submits a malformed request."""

    Message: Message


class ResourceExistsException(ServiceException):
    """The requested resource does not exist."""

    Message: Message
    Resource: Resource
    ResourceType: ResourceType


class ResourceNotFoundException(ServiceException):
    """This exception is thrown when a resource is not found by the Amazon Web
    ServicesTransfer Family service.
    """

    Message: Message
    Resource: Resource
    ResourceType: ResourceType


class ServiceUnavailableException(ServiceException):
    """The request has failed because the Amazon Web ServicesTransfer Family
    service is not available.
    """

    Message: Optional[ServiceErrorMessage]


class ThrottlingException(ServiceException):
    """The request was denied due to request throttling.

    HTTP Status Code: 400
    """

    RetryAfterSeconds: Optional[RetryAfterSeconds]


AddressAllocationIds = List[AddressAllocationId]


class EfsFileLocation(TypedDict, total=False):
    """Reserved for future use."""

    FileSystemId: Optional[EfsFileSystemId]
    Path: Optional[EfsPath]


class S3InputFileLocation(TypedDict, total=False):
    """Specifies the customer input S3 file location. If it is used inside
    ``copyStepDetails.DestinationFileLocation``, it should be the S3 copy
    destination.

    You need to provide the bucket and key. The key can represent either a
    path or a file. This is determined by whether or not you end the key
    value with the forward slash (/) character. If the final character is
    "/", then your file is copied to the folder, and its name does not
    change. If, rather, the final character is alphanumeric, your uploaded
    file is renamed to the path value. In this case, if a file with that
    name already exists, it is overwritten.

    For example, if your path is ``shared-files/bob/``, your uploaded files
    are copied to the ``shared-files/bob/``, folder. If your path is
    ``shared-files/today``, each uploaded file is copied to the
    ``shared-files`` folder and named ``today``: each upload overwrites the
    previous version of the *bob* file.
    """

    Bucket: Optional[S3Bucket]
    Key: Optional[S3Key]


class InputFileLocation(TypedDict, total=False):
    """Specifies the location for the file being copied. Only applicable for
    the Copy type of workflow steps.
    """

    S3FileLocation: Optional[S3InputFileLocation]
    EfsFileLocation: Optional[EfsFileLocation]


class CopyStepDetails(TypedDict, total=False):
    """Each step type has its own ``StepDetails`` structure."""

    Name: Optional[WorkflowStepName]
    DestinationFileLocation: Optional[InputFileLocation]
    OverwriteExisting: Optional[OverwriteExisting]
    SourceFileLocation: Optional[SourceFileLocation]


PosixId = int
SecondaryGids = List[PosixId]


class PosixProfile(TypedDict, total=False):
    """The full POSIX identity, including user ID (``Uid``), group ID
    (``Gid``), and any secondary groups IDs (``SecondaryGids``), that
    controls your users' access to your Amazon EFS file systems. The POSIX
    permissions that are set on files and directories in your file system
    determine the level of access your users get when transferring files
    into and out of your Amazon EFS file systems.
    """

    Uid: PosixId
    Gid: PosixId
    SecondaryGids: Optional[SecondaryGids]


class HomeDirectoryMapEntry(TypedDict, total=False):
    """Represents an object that contains entries and targets for
    ``HomeDirectoryMappings``.

    The following is an ``Entry`` and ``Target`` pair example for
    ``chroot``.

    ``[ { "Entry": "/", "Target": "/bucket_name/home/mydirectory" } ]``
    """

    Entry: MapEntry
    Target: MapTarget


HomeDirectoryMappings = List[HomeDirectoryMapEntry]


class CreateAccessRequest(ServiceRequest):
    HomeDirectory: Optional[HomeDirectory]
    HomeDirectoryType: Optional[HomeDirectoryType]
    HomeDirectoryMappings: Optional[HomeDirectoryMappings]
    Policy: Optional[Policy]
    PosixProfile: Optional[PosixProfile]
    Role: Role
    ServerId: ServerId
    ExternalId: ExternalId


class CreateAccessResponse(TypedDict, total=False):
    ServerId: ServerId
    ExternalId: ExternalId


class WorkflowDetail(TypedDict, total=False):
    """Specifies the workflow ID for the workflow to assign and the execution
    role used for executing the workflow.
    """

    WorkflowId: WorkflowId
    ExecutionRole: Role


OnUploadWorkflowDetails = List[WorkflowDetail]


class WorkflowDetails(TypedDict, total=False):
    """Container for the ``WorkflowDetail`` data type. It is used by actions
    that trigger a workflow to begin execution.
    """

    OnUpload: OnUploadWorkflowDetails


class Tag(TypedDict, total=False):
    """Creates a key-value pair for a specific resource. Tags are metadata that
    you can use to search for and group a resource for various purposes. You
    can apply tags to servers, users, and roles. A tag key can take more
    than one value. For example, to group servers for accounting purposes,
    you might create a tag called ``Group`` and assign the values
    ``Research`` and ``Accounting`` to that group.
    """

    Key: TagKey
    Value: TagValue


Tags = List[Tag]


class ProtocolDetails(TypedDict, total=False):
    """The protocol settings that are configured for your server."""

    PassiveIp: Optional[PassiveIp]
    TlsSessionResumptionMode: Optional[TlsSessionResumptionMode]


Protocols = List[Protocol]


class IdentityProviderDetails(TypedDict, total=False):
    """Returns information related to the type of user authentication that is
    in use for a file transfer protocol-enabled server's users. A server can
    have only one method of authentication.
    """

    Url: Optional[Url]
    InvocationRole: Optional[Role]
    DirectoryId: Optional[DirectoryId]
    Function: Optional[Function]


SecurityGroupIds = List[SecurityGroupId]
SubnetIds = List[SubnetId]


class EndpointDetails(TypedDict, total=False):
    """The virtual private cloud (VPC) endpoint settings that are configured
    for your file transfer protocol-enabled server. With a VPC endpoint, you
    can restrict access to your server and resources only within your VPC.
    To control incoming internet traffic, invoke the ``UpdateServer`` API
    and attach an Elastic IP address to your server's endpoint.

    After May 19, 2021, you won't be able to create a server using
    ``EndpointType=VPC_ENDPOINT`` in your Amazon Web Servicesaccount if your
    account hasn't already done so before May 19, 2021. If you have already
    created servers with ``EndpointType=VPC_ENDPOINT`` in your Amazon Web
    Servicesaccount on or before May 19, 2021, you will not be affected.
    After this date, use ``EndpointType`` = ``VPC``.

    For more information, see
    https://docs.aws.amazon.com/transfer/latest/userguide/create-server-in-vpc.html#deprecate-vpc-endpoint.
    """

    AddressAllocationIds: Optional[AddressAllocationIds]
    SubnetIds: Optional[SubnetIds]
    VpcEndpointId: Optional[VpcEndpointId]
    VpcId: Optional[VpcId]
    SecurityGroupIds: Optional[SecurityGroupIds]


class CreateServerRequest(ServiceRequest):
    Certificate: Optional[Certificate]
    Domain: Optional[Domain]
    EndpointDetails: Optional[EndpointDetails]
    EndpointType: Optional[EndpointType]
    HostKey: Optional[HostKey]
    IdentityProviderDetails: Optional[IdentityProviderDetails]
    IdentityProviderType: Optional[IdentityProviderType]
    LoggingRole: Optional[Role]
    PostAuthenticationLoginBanner: Optional[PostAuthenticationLoginBanner]
    PreAuthenticationLoginBanner: Optional[PreAuthenticationLoginBanner]
    Protocols: Optional[Protocols]
    ProtocolDetails: Optional[ProtocolDetails]
    SecurityPolicyName: Optional[SecurityPolicyName]
    Tags: Optional[Tags]
    WorkflowDetails: Optional[WorkflowDetails]


class CreateServerResponse(TypedDict, total=False):
    ServerId: ServerId


class CreateUserRequest(ServiceRequest):
    HomeDirectory: Optional[HomeDirectory]
    HomeDirectoryType: Optional[HomeDirectoryType]
    HomeDirectoryMappings: Optional[HomeDirectoryMappings]
    Policy: Optional[Policy]
    PosixProfile: Optional[PosixProfile]
    Role: Role
    ServerId: ServerId
    SshPublicKeyBody: Optional[SshPublicKeyBody]
    Tags: Optional[Tags]
    UserName: UserName


class CreateUserResponse(TypedDict, total=False):
    ServerId: ServerId
    UserName: UserName


class S3Tag(TypedDict, total=False):
    """Specifies the key-value pair that are assigned to a file during the
    execution of a Tagging step.
    """

    Key: S3TagKey
    Value: S3TagValue


S3Tags = List[S3Tag]


class TagStepDetails(TypedDict, total=False):
    """Each step type has its own ``StepDetails`` structure.

    The key/value pairs used to tag a file during the execution of a
    workflow step.
    """

    Name: Optional[WorkflowStepName]
    Tags: Optional[S3Tags]
    SourceFileLocation: Optional[SourceFileLocation]


class DeleteStepDetails(TypedDict, total=False):
    """The name of the step, used to identify the delete step."""

    Name: Optional[WorkflowStepName]
    SourceFileLocation: Optional[SourceFileLocation]


class CustomStepDetails(TypedDict, total=False):
    """Each step type has its own ``StepDetails`` structure."""

    Name: Optional[WorkflowStepName]
    Target: Optional[CustomStepTarget]
    TimeoutSeconds: Optional[CustomStepTimeoutSeconds]
    SourceFileLocation: Optional[SourceFileLocation]


class WorkflowStep(TypedDict, total=False):
    """The basic building block of a workflow."""

    Type: Optional[WorkflowStepType]
    CopyStepDetails: Optional[CopyStepDetails]
    CustomStepDetails: Optional[CustomStepDetails]
    DeleteStepDetails: Optional[DeleteStepDetails]
    TagStepDetails: Optional[TagStepDetails]


WorkflowSteps = List[WorkflowStep]


class CreateWorkflowRequest(ServiceRequest):
    Description: Optional[WorkflowDescription]
    Steps: WorkflowSteps
    OnExceptionSteps: Optional[WorkflowSteps]
    Tags: Optional[Tags]


class CreateWorkflowResponse(TypedDict, total=False):
    WorkflowId: WorkflowId


DateImported = datetime


class DeleteAccessRequest(ServiceRequest):
    ServerId: ServerId
    ExternalId: ExternalId


class DeleteServerRequest(ServiceRequest):
    ServerId: ServerId


class DeleteSshPublicKeyRequest(ServiceRequest):
    ServerId: ServerId
    SshPublicKeyId: SshPublicKeyId
    UserName: UserName


class DeleteUserRequest(ServiceRequest):
    ServerId: ServerId
    UserName: UserName


class DeleteWorkflowRequest(ServiceRequest):
    WorkflowId: WorkflowId


class DescribeAccessRequest(ServiceRequest):
    ServerId: ServerId
    ExternalId: ExternalId


class DescribedAccess(TypedDict, total=False):
    """Describes the properties of the access that was specified."""

    HomeDirectory: Optional[HomeDirectory]
    HomeDirectoryMappings: Optional[HomeDirectoryMappings]
    HomeDirectoryType: Optional[HomeDirectoryType]
    Policy: Optional[Policy]
    PosixProfile: Optional[PosixProfile]
    Role: Optional[Role]
    ExternalId: Optional[ExternalId]


class DescribeAccessResponse(TypedDict, total=False):
    ServerId: ServerId
    Access: DescribedAccess


class DescribeExecutionRequest(ServiceRequest):
    ExecutionId: ExecutionId
    WorkflowId: WorkflowId


class ExecutionError(TypedDict, total=False):
    """Specifies the error message and type, for an error that occurs during
    the execution of the workflow.
    """

    Type: ExecutionErrorType
    Message: ExecutionErrorMessage


class ExecutionStepResult(TypedDict, total=False):
    """Specifies the following details for the step: error (if any), outputs
    (if any), and the step type.
    """

    StepType: Optional[WorkflowStepType]
    Outputs: Optional[StepResultOutputsJson]
    Error: Optional[ExecutionError]


ExecutionStepResults = List[ExecutionStepResult]


class ExecutionResults(TypedDict, total=False):
    """Specifies the steps in the workflow, as well as the steps to execute in
    case of any errors during workflow execution.
    """

    Steps: Optional[ExecutionStepResults]
    OnExceptionSteps: Optional[ExecutionStepResults]


class LoggingConfiguration(TypedDict, total=False):
    """Consists of the logging role and the log group name."""

    LoggingRole: Optional[Role]
    LogGroupName: Optional[LogGroupName]


class UserDetails(TypedDict, total=False):
    """Specifies the user name, server ID, and session ID for a workflow."""

    UserName: UserName
    ServerId: ServerId
    SessionId: Optional[SessionId]


class ServiceMetadata(TypedDict, total=False):
    """A container object for the session details associated with a workflow."""

    UserDetails: UserDetails


class S3FileLocation(TypedDict, total=False):
    """Specifies the details for the file location for the file being used in
    the workflow. Only applicable if you are using S3 storage.
    """

    Bucket: Optional[S3Bucket]
    Key: Optional[S3Key]
    VersionId: Optional[S3VersionId]
    Etag: Optional[S3Etag]


class FileLocation(TypedDict, total=False):
    """Specifies the Amazon S3 or EFS file details to be used in the step."""

    S3FileLocation: Optional[S3FileLocation]
    EfsFileLocation: Optional[EfsFileLocation]


class DescribedExecution(TypedDict, total=False):
    """The details for an execution object."""

    ExecutionId: Optional[ExecutionId]
    InitialFileLocation: Optional[FileLocation]
    ServiceMetadata: Optional[ServiceMetadata]
    ExecutionRole: Optional[Role]
    LoggingConfiguration: Optional[LoggingConfiguration]
    PosixProfile: Optional[PosixProfile]
    Status: Optional[ExecutionStatus]
    Results: Optional[ExecutionResults]


class DescribeExecutionResponse(TypedDict, total=False):
    WorkflowId: WorkflowId
    Execution: DescribedExecution


class DescribeSecurityPolicyRequest(ServiceRequest):
    SecurityPolicyName: SecurityPolicyName


SecurityPolicyOptions = List[SecurityPolicyOption]


class DescribedSecurityPolicy(TypedDict, total=False):
    """Describes the properties of a security policy that was specified. For
    more information about security policies, see `Working with security
    policies <https://docs.aws.amazon.com/transfer/latest/userguide/security-policies.html>`__.
    """

    Fips: Optional[Fips]
    SecurityPolicyName: SecurityPolicyName
    SshCiphers: Optional[SecurityPolicyOptions]
    SshKexs: Optional[SecurityPolicyOptions]
    SshMacs: Optional[SecurityPolicyOptions]
    TlsCiphers: Optional[SecurityPolicyOptions]


class DescribeSecurityPolicyResponse(TypedDict, total=False):
    SecurityPolicy: DescribedSecurityPolicy


class DescribeServerRequest(ServiceRequest):
    ServerId: ServerId


class DescribedServer(TypedDict, total=False):
    """Describes the properties of a file transfer protocol-enabled server that
    was specified.
    """

    Arn: Arn
    Certificate: Optional[Certificate]
    ProtocolDetails: Optional[ProtocolDetails]
    Domain: Optional[Domain]
    EndpointDetails: Optional[EndpointDetails]
    EndpointType: Optional[EndpointType]
    HostKeyFingerprint: Optional[HostKeyFingerprint]
    IdentityProviderDetails: Optional[IdentityProviderDetails]
    IdentityProviderType: Optional[IdentityProviderType]
    LoggingRole: Optional[Role]
    PostAuthenticationLoginBanner: Optional[PostAuthenticationLoginBanner]
    PreAuthenticationLoginBanner: Optional[PreAuthenticationLoginBanner]
    Protocols: Optional[Protocols]
    SecurityPolicyName: Optional[SecurityPolicyName]
    ServerId: Optional[ServerId]
    State: Optional[State]
    Tags: Optional[Tags]
    UserCount: Optional[UserCount]
    WorkflowDetails: Optional[WorkflowDetails]


class DescribeServerResponse(TypedDict, total=False):
    Server: DescribedServer


class DescribeUserRequest(ServiceRequest):
    ServerId: ServerId
    UserName: UserName


class SshPublicKey(TypedDict, total=False):
    """Provides information about the public Secure Shell (SSH) key that is
    associated with a user account for the specific file transfer
    protocol-enabled server (as identified by ``ServerId``). The information
    returned includes the date the key was imported, the public key
    contents, and the public key ID. A user can store more than one SSH
    public key associated with their user name on a specific server.
    """

    DateImported: DateImported
    SshPublicKeyBody: SshPublicKeyBody
    SshPublicKeyId: SshPublicKeyId


SshPublicKeys = List[SshPublicKey]


class DescribedUser(TypedDict, total=False):
    """Describes the properties of a user that was specified."""

    Arn: Arn
    HomeDirectory: Optional[HomeDirectory]
    HomeDirectoryMappings: Optional[HomeDirectoryMappings]
    HomeDirectoryType: Optional[HomeDirectoryType]
    Policy: Optional[Policy]
    PosixProfile: Optional[PosixProfile]
    Role: Optional[Role]
    SshPublicKeys: Optional[SshPublicKeys]
    Tags: Optional[Tags]
    UserName: Optional[UserName]


class DescribeUserResponse(TypedDict, total=False):
    ServerId: ServerId
    User: DescribedUser


class DescribeWorkflowRequest(ServiceRequest):
    WorkflowId: WorkflowId


class DescribedWorkflow(TypedDict, total=False):
    """Describes the properties of the specified workflow"""

    Arn: Arn
    Description: Optional[WorkflowDescription]
    Steps: Optional[WorkflowSteps]
    OnExceptionSteps: Optional[WorkflowSteps]
    WorkflowId: Optional[WorkflowId]
    Tags: Optional[Tags]


class DescribeWorkflowResponse(TypedDict, total=False):
    Workflow: DescribedWorkflow


class ImportSshPublicKeyRequest(ServiceRequest):
    ServerId: ServerId
    SshPublicKeyBody: SshPublicKeyBody
    UserName: UserName


class ImportSshPublicKeyResponse(TypedDict, total=False):
    """Identifies the user, the server they belong to, and the identifier of
    the SSH public key associated with that user. A user can have more than
    one key on each server that they are associated with.
    """

    ServerId: ServerId
    SshPublicKeyId: SshPublicKeyId
    UserName: UserName


class ListAccessesRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]
    ServerId: ServerId


class ListedAccess(TypedDict, total=False):
    """Lists the properties for one or more specified associated accesses."""

    HomeDirectory: Optional[HomeDirectory]
    HomeDirectoryType: Optional[HomeDirectoryType]
    Role: Optional[Role]
    ExternalId: Optional[ExternalId]


ListedAccesses = List[ListedAccess]


class ListAccessesResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    ServerId: ServerId
    Accesses: ListedAccesses


class ListExecutionsRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]
    WorkflowId: WorkflowId


class ListedExecution(TypedDict, total=False):
    """Returns properties of the execution that is specified."""

    ExecutionId: Optional[ExecutionId]
    InitialFileLocation: Optional[FileLocation]
    ServiceMetadata: Optional[ServiceMetadata]
    Status: Optional[ExecutionStatus]


ListedExecutions = List[ListedExecution]


class ListExecutionsResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    WorkflowId: WorkflowId
    Executions: ListedExecutions


class ListSecurityPoliciesRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


SecurityPolicyNames = List[SecurityPolicyName]


class ListSecurityPoliciesResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    SecurityPolicyNames: SecurityPolicyNames


class ListServersRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListedServer(TypedDict, total=False):
    """Returns properties of a file transfer protocol-enabled server that was
    specified.
    """

    Arn: Arn
    Domain: Optional[Domain]
    IdentityProviderType: Optional[IdentityProviderType]
    EndpointType: Optional[EndpointType]
    LoggingRole: Optional[Role]
    ServerId: Optional[ServerId]
    State: Optional[State]
    UserCount: Optional[UserCount]


ListedServers = List[ListedServer]


class ListServersResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    Servers: ListedServers


class ListTagsForResourceRequest(ServiceRequest):
    Arn: Arn
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListTagsForResourceResponse(TypedDict, total=False):
    Arn: Optional[Arn]
    NextToken: Optional[NextToken]
    Tags: Optional[Tags]


class ListUsersRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]
    ServerId: ServerId


class ListedUser(TypedDict, total=False):
    """Returns properties of the user that you specify."""

    Arn: Arn
    HomeDirectory: Optional[HomeDirectory]
    HomeDirectoryType: Optional[HomeDirectoryType]
    Role: Optional[Role]
    SshPublicKeyCount: Optional[SshPublicKeyCount]
    UserName: Optional[UserName]


ListedUsers = List[ListedUser]


class ListUsersResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    ServerId: ServerId
    Users: ListedUsers


class ListWorkflowsRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListedWorkflow(TypedDict, total=False):
    """Contains the ID, text description, and Amazon Resource Name (ARN) for
    the workflow.
    """

    WorkflowId: Optional[WorkflowId]
    Description: Optional[WorkflowDescription]
    Arn: Optional[Arn]


ListedWorkflows = List[ListedWorkflow]


class ListWorkflowsResponse(TypedDict, total=False):
    NextToken: Optional[NextToken]
    Workflows: ListedWorkflows


class SendWorkflowStepStateRequest(ServiceRequest):
    WorkflowId: WorkflowId
    ExecutionId: ExecutionId
    Token: CallbackToken
    Status: CustomStepStatus


class SendWorkflowStepStateResponse(TypedDict, total=False):
    pass


class StartServerRequest(ServiceRequest):
    ServerId: ServerId


class StopServerRequest(ServiceRequest):
    ServerId: ServerId


TagKeys = List[TagKey]


class TagResourceRequest(ServiceRequest):
    Arn: Arn
    Tags: Tags


class TestIdentityProviderRequest(ServiceRequest):
    ServerId: ServerId
    ServerProtocol: Optional[Protocol]
    SourceIp: Optional[SourceIp]
    UserName: UserName
    UserPassword: Optional[UserPassword]


class TestIdentityProviderResponse(TypedDict, total=False):
    Response: Optional[Response]
    StatusCode: StatusCode
    Message: Optional[Message]
    Url: Url


class UntagResourceRequest(ServiceRequest):
    Arn: Arn
    TagKeys: TagKeys


class UpdateAccessRequest(ServiceRequest):
    HomeDirectory: Optional[HomeDirectory]
    HomeDirectoryType: Optional[HomeDirectoryType]
    HomeDirectoryMappings: Optional[HomeDirectoryMappings]
    Policy: Optional[Policy]
    PosixProfile: Optional[PosixProfile]
    Role: Optional[Role]
    ServerId: ServerId
    ExternalId: ExternalId


class UpdateAccessResponse(TypedDict, total=False):
    ServerId: ServerId
    ExternalId: ExternalId


class UpdateServerRequest(ServiceRequest):
    Certificate: Optional[Certificate]
    ProtocolDetails: Optional[ProtocolDetails]
    EndpointDetails: Optional[EndpointDetails]
    EndpointType: Optional[EndpointType]
    HostKey: Optional[HostKey]
    IdentityProviderDetails: Optional[IdentityProviderDetails]
    LoggingRole: Optional[NullableRole]
    PostAuthenticationLoginBanner: Optional[PostAuthenticationLoginBanner]
    PreAuthenticationLoginBanner: Optional[PreAuthenticationLoginBanner]
    Protocols: Optional[Protocols]
    SecurityPolicyName: Optional[SecurityPolicyName]
    ServerId: ServerId
    WorkflowDetails: Optional[WorkflowDetails]


class UpdateServerResponse(TypedDict, total=False):
    ServerId: ServerId


class UpdateUserRequest(ServiceRequest):
    HomeDirectory: Optional[HomeDirectory]
    HomeDirectoryType: Optional[HomeDirectoryType]
    HomeDirectoryMappings: Optional[HomeDirectoryMappings]
    Policy: Optional[Policy]
    PosixProfile: Optional[PosixProfile]
    Role: Optional[Role]
    ServerId: ServerId
    UserName: UserName


class UpdateUserResponse(TypedDict, total=False):
    """``UpdateUserResponse`` returns the user name and identifier for the
    request to update a user's properties.
    """

    ServerId: ServerId
    UserName: UserName


class TransferApi:

    service = "transfer"
    version = "2018-11-05"

    @handler("CreateAccess")
    def create_access(
        self,
        context: RequestContext,
        role: Role,
        server_id: ServerId,
        external_id: ExternalId,
        home_directory: HomeDirectory = None,
        home_directory_type: HomeDirectoryType = None,
        home_directory_mappings: HomeDirectoryMappings = None,
        policy: Policy = None,
        posix_profile: PosixProfile = None,
    ) -> CreateAccessResponse:
        """Used by administrators to choose which groups in the directory should
        have access to upload and download files over the enabled protocols
        using Amazon Web Services Transfer Family. For example, a Microsoft
        Active Directory might contain 50,000 users, but only a small fraction
        might need the ability to transfer files to the server. An administrator
        can use ``CreateAccess`` to limit the access to the correct set of users
        who need this ability.

        :param role: Specifies the Amazon Resource Name (ARN) of the IAM role that controls
        your users' access to your Amazon S3 bucket or EFS file system.
        :param server_id: A system-assigned unique identifier for a server instance.
        :param external_id: A unique identifier that is required to identify specific groups within
        your directory.
        :param home_directory: The landing directory (folder) for a user when they log in to the server
        using the client.
        :param home_directory_type: The type of landing directory (folder) you want your users' home
        directory to be when they log into the server.
        :param home_directory_mappings: Logical directory mappings that specify what Amazon S3 or Amazon EFS
        paths and keys should be visible to your user and how you want to make
        them visible.
        :param policy: A session policy for your user so that you can use the same IAM role
        across multiple users.
        :param posix_profile: The full POSIX identity, including user ID (``Uid``), group ID
        (``Gid``), and any secondary groups IDs (``SecondaryGids``), that
        controls your users' access to your Amazon EFS file systems.
        :returns: CreateAccessResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceExistsException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("CreateServer")
    def create_server(
        self,
        context: RequestContext,
        certificate: Certificate = None,
        domain: Domain = None,
        endpoint_details: EndpointDetails = None,
        endpoint_type: EndpointType = None,
        host_key: HostKey = None,
        identity_provider_details: IdentityProviderDetails = None,
        identity_provider_type: IdentityProviderType = None,
        logging_role: Role = None,
        post_authentication_login_banner: PostAuthenticationLoginBanner = None,
        pre_authentication_login_banner: PreAuthenticationLoginBanner = None,
        protocols: Protocols = None,
        protocol_details: ProtocolDetails = None,
        security_policy_name: SecurityPolicyName = None,
        tags: Tags = None,
        workflow_details: WorkflowDetails = None,
    ) -> CreateServerResponse:
        """Instantiates an auto-scaling virtual server based on the selected file
        transfer protocol in Amazon Web Services. When you make updates to your
        file transfer protocol-enabled server or when you work with users, use
        the service-generated ``ServerId`` property that is assigned to the
        newly created server.

        :param certificate: The Amazon Resource Name (ARN) of the Amazon Web Services Certificate
        Manager (ACM) certificate.
        :param domain: The domain of the storage system that is used for file transfers.
        :param endpoint_details: The virtual private cloud (VPC) endpoint settings that are configured
        for your server.
        :param endpoint_type: The type of endpoint that you want your server to use.
        :param host_key: The RSA private key as generated by the
        ``ssh-keygen -N "" -m PEM -f my-new-server-key`` command.
        :param identity_provider_details: Required when ``IdentityProviderType`` is set to
        ``AWS_DIRECTORY_SERVICE`` or ``API_GATEWAY``.
        :param identity_provider_type: Specifies the mode of authentication for a server.
        :param logging_role: Specifies the Amazon Resource Name (ARN) of the Amazon Web Services
        Identity and Access Management (IAM) role that allows a server to turn
        on Amazon CloudWatch logging for Amazon S3 or Amazon EFS events.
        :param post_authentication_login_banner: Specify a string to display when users connect to a server.
        :param pre_authentication_login_banner: Specify a string to display when users connect to a server.
        :param protocols: Specifies the file transfer protocol or protocols over which your file
        transfer protocol client can connect to your server's endpoint.
        :param protocol_details: The protocol settings that are configured for your server.
        :param security_policy_name: Specifies the name of the security policy that is attached to the
        server.
        :param tags: Key-value pairs that can be used to group and search for servers.
        :param workflow_details: Specifies the workflow ID for the workflow to assign and the execution
        role used for executing the workflow.
        :returns: CreateServerResponse
        :raises AccessDeniedException:
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceExistsException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateUser")
    def create_user(
        self,
        context: RequestContext,
        role: Role,
        server_id: ServerId,
        user_name: UserName,
        home_directory: HomeDirectory = None,
        home_directory_type: HomeDirectoryType = None,
        home_directory_mappings: HomeDirectoryMappings = None,
        policy: Policy = None,
        posix_profile: PosixProfile = None,
        ssh_public_key_body: SshPublicKeyBody = None,
        tags: Tags = None,
    ) -> CreateUserResponse:
        """Creates a user and associates them with an existing file transfer
        protocol-enabled server. You can only create and associate users with
        servers that have the ``IdentityProviderType`` set to
        ``SERVICE_MANAGED``. Using parameters for ``CreateUser``, you can
        specify the user name, set the home directory, store the user's public
        key, and assign the user's Amazon Web Services Identity and Access
        Management (IAM) role. You can also optionally add a session policy, and
        assign metadata with tags that can be used to group and search for
        users.

        :param role: Specifies the Amazon Resource Name (ARN) of the IAM role that controls
        your users' access to your Amazon S3 bucket or EFS file system.
        :param server_id: A system-assigned unique identifier for a server instance.
        :param user_name: A unique string that identifies a user and is associated with a
        ``ServerId``.
        :param home_directory: The landing directory (folder) for a user when they log in to the server
        using the client.
        :param home_directory_type: The type of landing directory (folder) you want your users' home
        directory to be when they log into the server.
        :param home_directory_mappings: Logical directory mappings that specify what Amazon S3 or Amazon EFS
        paths and keys should be visible to your user and how you want to make
        them visible.
        :param policy: A session policy for your user so that you can use the same IAM role
        across multiple users.
        :param posix_profile: Specifies the full POSIX identity, including user ID (``Uid``), group ID
        (``Gid``), and any secondary groups IDs (``SecondaryGids``), that
        controls your users' access to your Amazon EFS file systems.
        :param ssh_public_key_body: The public portion of the Secure Shell (SSH) key used to authenticate
        the user to the server.
        :param tags: Key-value pairs that can be used to group and search for users.
        :returns: CreateUserResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceExistsException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("CreateWorkflow")
    def create_workflow(
        self,
        context: RequestContext,
        steps: WorkflowSteps,
        description: WorkflowDescription = None,
        on_exception_steps: WorkflowSteps = None,
        tags: Tags = None,
    ) -> CreateWorkflowResponse:
        """Allows you to create a workflow with specified steps and step details
        the workflow invokes after file transfer completes. After creating a
        workflow, you can associate the workflow created with any transfer
        servers by specifying the ``workflow-details`` field in ``CreateServer``
        and ``UpdateServer`` operations.

        :param steps: Specifies the details for the steps that are in the specified workflow.
        :param description: A textual description for the workflow.
        :param on_exception_steps: Specifies the steps (actions) to take if errors are encountered during
        execution of the workflow.
        :param tags: Key-value pairs that can be used to group and search for workflows.
        :returns: CreateWorkflowResponse
        :raises AccessDeniedException:
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceExistsException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteAccess")
    def delete_access(
        self, context: RequestContext, server_id: ServerId, external_id: ExternalId
    ) -> None:
        """Allows you to delete the access specified in the ``ServerID`` and
        ``ExternalID`` parameters.

        :param server_id: A system-assigned unique identifier for a server that has this user
        assigned.
        :param external_id: A unique identifier that is required to identify specific groups within
        your directory.
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteServer")
    def delete_server(self, context: RequestContext, server_id: ServerId) -> None:
        """Deletes the file transfer protocol-enabled server that you specify.

        No response returns from this operation.

        :param server_id: A unique system-assigned identifier for a server instance.
        :raises AccessDeniedException:
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteSshPublicKey")
    def delete_ssh_public_key(
        self,
        context: RequestContext,
        server_id: ServerId,
        ssh_public_key_id: SshPublicKeyId,
        user_name: UserName,
    ) -> None:
        """Deletes a user's Secure Shell (SSH) public key.

        :param server_id: A system-assigned unique identifier for a file transfer protocol-enabled
        server instance that has the user assigned to it.
        :param ssh_public_key_id: A unique identifier used to reference your user's specific SSH key.
        :param user_name: A unique string that identifies a user whose public key is being
        deleted.
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteUser")
    def delete_user(
        self, context: RequestContext, server_id: ServerId, user_name: UserName
    ) -> None:
        """Deletes the user belonging to a file transfer protocol-enabled server
        you specify.

        No response returns from this operation.

        When you delete a user from a server, the user's information is lost.

        :param server_id: A system-assigned unique identifier for a server instance that has the
        user assigned to it.
        :param user_name: A unique string that identifies a user that is being deleted from a
        server.
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DeleteWorkflow")
    def delete_workflow(self, context: RequestContext, workflow_id: WorkflowId) -> None:
        """Deletes the specified workflow.

        :param workflow_id: A unique identifier for the workflow.
        :raises AccessDeniedException:
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeAccess")
    def describe_access(
        self, context: RequestContext, server_id: ServerId, external_id: ExternalId
    ) -> DescribeAccessResponse:
        """Describes the access that is assigned to the specific file transfer
        protocol-enabled server, as identified by its ``ServerId`` property and
        its ``ExternalID``.

        The response from this call returns the properties of the access that is
        associated with the ``ServerId`` value that was specified.

        :param server_id: A system-assigned unique identifier for a server that has this access
        assigned.
        :param external_id: A unique identifier that is required to identify specific groups within
        your directory.
        :returns: DescribeAccessResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeExecution")
    def describe_execution(
        self, context: RequestContext, execution_id: ExecutionId, workflow_id: WorkflowId
    ) -> DescribeExecutionResponse:
        """You can use ``DescribeExecution`` to check the details of the execution
        of the specified workflow.

        :param execution_id: A unique identifier for the execution of a workflow.
        :param workflow_id: A unique identifier for the workflow.
        :returns: DescribeExecutionResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeSecurityPolicy")
    def describe_security_policy(
        self, context: RequestContext, security_policy_name: SecurityPolicyName
    ) -> DescribeSecurityPolicyResponse:
        """Describes the security policy that is attached to your file transfer
        protocol-enabled server. The response contains a description of the
        security policy's properties. For more information about security
        policies, see `Working with security
        policies <https://docs.aws.amazon.com/transfer/latest/userguide/security-policies.html>`__.

        :param security_policy_name: Specifies the name of the security policy that is attached to the
        server.
        :returns: DescribeSecurityPolicyResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeServer")
    def describe_server(
        self, context: RequestContext, server_id: ServerId
    ) -> DescribeServerResponse:
        """Describes a file transfer protocol-enabled server that you specify by
        passing the ``ServerId`` parameter.

        The response contains a description of a server's properties. When you
        set ``EndpointType`` to VPC, the response will contain the
        ``EndpointDetails``.

        :param server_id: A system-assigned unique identifier for a server.
        :returns: DescribeServerResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeUser")
    def describe_user(
        self, context: RequestContext, server_id: ServerId, user_name: UserName
    ) -> DescribeUserResponse:
        """Describes the user assigned to the specific file transfer
        protocol-enabled server, as identified by its ``ServerId`` property.

        The response from this call returns the properties of the user
        associated with the ``ServerId`` value that was specified.

        :param server_id: A system-assigned unique identifier for a server that has this user
        assigned.
        :param user_name: The name of the user assigned to one or more servers.
        :returns: DescribeUserResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeWorkflow")
    def describe_workflow(
        self, context: RequestContext, workflow_id: WorkflowId
    ) -> DescribeWorkflowResponse:
        """Describes the specified workflow.

        :param workflow_id: A unique identifier for the workflow.
        :returns: DescribeWorkflowResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ImportSshPublicKey")
    def import_ssh_public_key(
        self,
        context: RequestContext,
        server_id: ServerId,
        ssh_public_key_body: SshPublicKeyBody,
        user_name: UserName,
    ) -> ImportSshPublicKeyResponse:
        """Adds a Secure Shell (SSH) public key to a user account identified by a
        ``UserName`` value assigned to the specific file transfer
        protocol-enabled server, identified by ``ServerId``.

        The response returns the ``UserName`` value, the ``ServerId`` value, and
        the name of the ``SshPublicKeyId``.

        :param server_id: A system-assigned unique identifier for a server.
        :param ssh_public_key_body: The public key portion of an SSH key pair.
        :param user_name: The name of the user account that is assigned to one or more servers.
        :returns: ImportSshPublicKeyResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceExistsException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListAccesses")
    def list_accesses(
        self,
        context: RequestContext,
        server_id: ServerId,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListAccessesResponse:
        """Lists the details for all the accesses you have on your server.

        :param server_id: A system-assigned unique identifier for a server that has users assigned
        to it.
        :param max_results: Specifies the maximum number of access SIDs to return.
        :param next_token: When you can get additional results from the ``ListAccesses`` call, a
        ``NextToken`` parameter is returned in the output.
        :returns: ListAccessesResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidNextTokenException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListExecutions")
    def list_executions(
        self,
        context: RequestContext,
        workflow_id: WorkflowId,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListExecutionsResponse:
        """Lists all executions for the specified workflow.

        :param workflow_id: A unique identifier for the workflow.
        :param max_results: Specifies the aximum number of executions to return.
        :param next_token: ``ListExecutions`` returns the ``NextToken`` parameter in the output.
        :returns: ListExecutionsResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidNextTokenException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListSecurityPolicies")
    def list_security_policies(
        self, context: RequestContext, max_results: MaxResults = None, next_token: NextToken = None
    ) -> ListSecurityPoliciesResponse:
        """Lists the security policies that are attached to your file transfer
        protocol-enabled servers.

        :param max_results: Specifies the number of security policies to return as a response to the
        ``ListSecurityPolicies`` query.
        :param next_token: When additional results are obtained from the ``ListSecurityPolicies``
        command, a ``NextToken`` parameter is returned in the output.
        :returns: ListSecurityPoliciesResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidNextTokenException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListServers")
    def list_servers(
        self, context: RequestContext, max_results: MaxResults = None, next_token: NextToken = None
    ) -> ListServersResponse:
        """Lists the file transfer protocol-enabled servers that are associated
        with your Amazon Web Services account.

        :param max_results: Specifies the number of servers to return as a response to the
        ``ListServers`` query.
        :param next_token: When additional results are obtained from the ``ListServers`` command, a
        ``NextToken`` parameter is returned in the output.
        :returns: ListServersResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidNextTokenException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self,
        context: RequestContext,
        arn: Arn,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListTagsForResourceResponse:
        """Lists all of the tags associated with the Amazon Resource Name (ARN)
        that you specify. The resource can be a user, server, or role.

        :param arn: Requests the tags associated with a particular Amazon Resource Name
        (ARN).
        :param max_results: Specifies the number of tags to return as a response to the
        ``ListTagsForResource`` request.
        :param next_token: When you request additional results from the ``ListTagsForResource``
        operation, a ``NextToken`` parameter is returned in the input.
        :returns: ListTagsForResourceResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidNextTokenException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("ListUsers")
    def list_users(
        self,
        context: RequestContext,
        server_id: ServerId,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListUsersResponse:
        """Lists the users for a file transfer protocol-enabled server that you
        specify by passing the ``ServerId`` parameter.

        :param server_id: A system-assigned unique identifier for a server that has users assigned
        to it.
        :param max_results: Specifies the number of users to return as a response to the
        ``ListUsers`` request.
        :param next_token: When you can get additional results from the ``ListUsers`` call, a
        ``NextToken`` parameter is returned in the output.
        :returns: ListUsersResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidNextTokenException:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListWorkflows")
    def list_workflows(
        self, context: RequestContext, max_results: MaxResults = None, next_token: NextToken = None
    ) -> ListWorkflowsResponse:
        """Lists all of your workflows.

        :param max_results: Specifies the maximum number of workflows to return.
        :param next_token: ``ListWorkflows`` returns the ``NextToken`` parameter in the output.
        :returns: ListWorkflowsResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidNextTokenException:
        :raises InvalidRequestException:
        """
        raise NotImplementedError

    @handler("SendWorkflowStepState")
    def send_workflow_step_state(
        self,
        context: RequestContext,
        workflow_id: WorkflowId,
        execution_id: ExecutionId,
        token: CallbackToken,
        status: CustomStepStatus,
    ) -> SendWorkflowStepStateResponse:
        """Sends a callback for asynchronous custom steps.

        The ``ExecutionId``, ``WorkflowId``, and ``Token`` are passed to the
        target resource during execution of a custom step of a workflow. You
        must include those with their callback as well as providing a status.

        :param workflow_id: A unique identifier for the workflow.
        :param execution_id: A unique identifier for the execution of a workflow.
        :param token: Used to distinguish between multiple callbacks for multiple Lambda steps
        within the same execution.
        :param status: Indicates whether the specified step succeeded or failed.
        :returns: SendWorkflowStepStateResponse
        :raises AccessDeniedException:
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("StartServer")
    def start_server(self, context: RequestContext, server_id: ServerId) -> None:
        """Changes the state of a file transfer protocol-enabled server from
        ``OFFLINE`` to ``ONLINE``. It has no impact on a server that is already
        ``ONLINE``. An ``ONLINE`` server can accept and process file transfer
        jobs.

        The state of ``STARTING`` indicates that the server is in an
        intermediate state, either not fully able to respond, or not fully
        online. The values of ``START_FAILED`` can indicate an error condition.

        No response is returned from this call.

        :param server_id: A system-assigned unique identifier for a server that you start.
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("StopServer")
    def stop_server(self, context: RequestContext, server_id: ServerId) -> None:
        """Changes the state of a file transfer protocol-enabled server from
        ``ONLINE`` to ``OFFLINE``. An ``OFFLINE`` server cannot accept and
        process file transfer jobs. Information tied to your server, such as
        server and user properties, are not affected by stopping your server.

        Stopping the server will not reduce or impact your file transfer
        protocol endpoint billing; you must delete the server to stop being
        billed.

        The state of ``STOPPING`` indicates that the server is in an
        intermediate state, either not fully able to respond, or not fully
        offline. The values of ``STOP_FAILED`` can indicate an error condition.

        No response is returned from this call.

        :param server_id: A system-assigned unique identifier for a server that you stopped.
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(self, context: RequestContext, arn: Arn, tags: Tags) -> None:
        """Attaches a key-value pair to a resource, as identified by its Amazon
        Resource Name (ARN). Resources are users, servers, roles, and other
        entities.

        There is no response returned from this call.

        :param arn: An Amazon Resource Name (ARN) for a specific Amazon Web Services
        resource, such as a server, user, or role.
        :param tags: Key-value pairs assigned to ARNs that you can use to group and search
        for resources by type.
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("TestIdentityProvider")
    def test_identity_provider(
        self,
        context: RequestContext,
        server_id: ServerId,
        user_name: UserName,
        server_protocol: Protocol = None,
        source_ip: SourceIp = None,
        user_password: UserPassword = None,
    ) -> TestIdentityProviderResponse:
        """If the ``IdentityProviderType`` of a file transfer protocol-enabled
        server is ``AWS_DIRECTORY_SERVICE`` or ``API_Gateway``, tests whether
        your identity provider is set up successfully. We highly recommend that
        you call this operation to test your authentication method as soon as
        you create your server. By doing so, you can troubleshoot issues with
        the identity provider integration to ensure that your users can
        successfully use the service.

        The ``ServerId`` and ``UserName`` parameters are required. The
        ``ServerProtocol``, ``SourceIp``, and ``UserPassword`` are all optional.

        You cannot use ``TestIdentityProvider`` if the ``IdentityProviderType``
        of your server is ``SERVICE_MANAGED``.

        -  If you provide any incorrect values for any parameters, the
           ``Response`` field is empty.

        -  If you provide a server ID for a server that uses service-managed
           users, you get an error:

           ``An error occurred (InvalidRequestException) when calling the TestIdentityProvider operation: s-server-ID not configured for external auth``

        -  If you enter a Server ID for the ``--server-id`` parameter that does
           not identify an actual Transfer server, you receive the following
           error:

           ``An error occurred (ResourceNotFoundException) when calling the TestIdentityProvider operation: Unknown server``

        :param server_id: A system-assigned identifier for a specific server.
        :param user_name: The name of the user account to be tested.
        :param server_protocol: The type of file transfer protocol to be tested.
        :param source_ip: The source IP address of the user account to be tested.
        :param user_password: The password of the user account to be tested.
        :returns: TestIdentityProviderResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(self, context: RequestContext, arn: Arn, tag_keys: TagKeys) -> None:
        """Detaches a key-value pair from a resource, as identified by its Amazon
        Resource Name (ARN). Resources are users, servers, roles, and other
        entities.

        No response is returned from this call.

        :param arn: The value of the resource that will have the tag removed.
        :param tag_keys: TagKeys are key-value pairs assigned to ARNs that can be used to group
        and search for resources by type.
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateAccess")
    def update_access(
        self,
        context: RequestContext,
        server_id: ServerId,
        external_id: ExternalId,
        home_directory: HomeDirectory = None,
        home_directory_type: HomeDirectoryType = None,
        home_directory_mappings: HomeDirectoryMappings = None,
        policy: Policy = None,
        posix_profile: PosixProfile = None,
        role: Role = None,
    ) -> UpdateAccessResponse:
        """Allows you to update parameters for the access specified in the
        ``ServerID`` and ``ExternalID`` parameters.

        :param server_id: A system-assigned unique identifier for a server instance.
        :param external_id: A unique identifier that is required to identify specific groups within
        your directory.
        :param home_directory: The landing directory (folder) for a user when they log in to the server
        using the client.
        :param home_directory_type: The type of landing directory (folder) you want your users' home
        directory to be when they log into the server.
        :param home_directory_mappings: Logical directory mappings that specify what Amazon S3 or Amazon EFS
        paths and keys should be visible to your user and how you want to make
        them visible.
        :param policy: A session policy for your user so that you can use the same IAM role
        across multiple users.
        :param posix_profile: The full POSIX identity, including user ID (``Uid``), group ID
        (``Gid``), and any secondary groups IDs (``SecondaryGids``), that
        controls your users' access to your Amazon EFS file systems.
        :param role: Specifies the Amazon Resource Name (ARN) of the IAM role that controls
        your users' access to your Amazon S3 bucket or EFS file system.
        :returns: UpdateAccessResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceExistsException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateServer")
    def update_server(
        self,
        context: RequestContext,
        server_id: ServerId,
        certificate: Certificate = None,
        protocol_details: ProtocolDetails = None,
        endpoint_details: EndpointDetails = None,
        endpoint_type: EndpointType = None,
        host_key: HostKey = None,
        identity_provider_details: IdentityProviderDetails = None,
        logging_role: NullableRole = None,
        post_authentication_login_banner: PostAuthenticationLoginBanner = None,
        pre_authentication_login_banner: PreAuthenticationLoginBanner = None,
        protocols: Protocols = None,
        security_policy_name: SecurityPolicyName = None,
        workflow_details: WorkflowDetails = None,
    ) -> UpdateServerResponse:
        """Updates the file transfer protocol-enabled server's properties after
        that server has been created.

        The ``UpdateServer`` call returns the ``ServerId`` of the server you
        updated.

        :param server_id: A system-assigned unique identifier for a server instance that the user
        account is assigned to.
        :param certificate: The Amazon Resource Name (ARN) of the Amazon Web ServicesCertificate
        Manager (ACM) certificate.
        :param protocol_details: The protocol settings that are configured for your server.
        :param endpoint_details: The virtual private cloud (VPC) endpoint settings that are configured
        for your server.
        :param endpoint_type: The type of endpoint that you want your server to use.
        :param host_key: The RSA private key as generated by
        ``ssh-keygen -N "" -m PEM -f my-new-server-key``.
        :param identity_provider_details: An array containing all of the information required to call a customer's
        authentication API method.
        :param logging_role: Specifies the Amazon Resource Name (ARN) of the Amazon Web Services
        Identity and Access Management (IAM) role that allows a server to turn
        on Amazon CloudWatch logging for Amazon S3 or Amazon EFS events.
        :param post_authentication_login_banner: Specify a string to display when users connect to a server.
        :param pre_authentication_login_banner: Specify a string to display when users connect to a server.
        :param protocols: Specifies the file transfer protocol or protocols over which your file
        transfer protocol client can connect to your server's endpoint.
        :param security_policy_name: Specifies the name of the security policy that is attached to the
        server.
        :param workflow_details: Specifies the workflow ID for the workflow to assign and the execution
        role used for executing the workflow.
        :returns: UpdateServerResponse
        :raises AccessDeniedException:
        :raises ServiceUnavailableException:
        :raises ConflictException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceExistsException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateUser")
    def update_user(
        self,
        context: RequestContext,
        server_id: ServerId,
        user_name: UserName,
        home_directory: HomeDirectory = None,
        home_directory_type: HomeDirectoryType = None,
        home_directory_mappings: HomeDirectoryMappings = None,
        policy: Policy = None,
        posix_profile: PosixProfile = None,
        role: Role = None,
    ) -> UpdateUserResponse:
        """Assigns new properties to a user. Parameters you pass modify any or all
        of the following: the home directory, role, and policy for the
        ``UserName`` and ``ServerId`` you specify.

        The response returns the ``ServerId`` and the ``UserName`` for the
        updated user.

        :param server_id: A system-assigned unique identifier for a server instance that the user
        account is assigned to.
        :param user_name: A unique string that identifies a user and is associated with a server
        as specified by the ``ServerId``.
        :param home_directory: The landing directory (folder) for a user when they log in to the server
        using the client.
        :param home_directory_type: The type of landing directory (folder) you want your users' home
        directory to be when they log into the server.
        :param home_directory_mappings: Logical directory mappings that specify what Amazon S3 or Amazon EFS
        paths and keys should be visible to your user and how you want to make
        them visible.
        :param policy: A session policy for your user so that you can use the same IAM role
        across multiple users.
        :param posix_profile: Specifies the full POSIX identity, including user ID (``Uid``), group ID
        (``Gid``), and any secondary groups IDs (``SecondaryGids``), that
        controls your users' access to your Amazon Elastic File Systems (Amazon
        EFS).
        :param role: Specifies the Amazon Resource Name (ARN) of the IAM role that controls
        your users' access to your Amazon S3 bucket or EFS file system.
        :returns: UpdateUserResponse
        :raises ServiceUnavailableException:
        :raises InternalServiceError:
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        """
        raise NotImplementedError
