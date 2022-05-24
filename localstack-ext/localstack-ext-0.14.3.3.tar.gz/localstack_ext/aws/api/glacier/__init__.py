import sys
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

DateTime = str
TagKey = str
TagValue = str
boolean = bool
httpstatus = int
string = str


class ActionCode(str):
    ArchiveRetrieval = "ArchiveRetrieval"
    InventoryRetrieval = "InventoryRetrieval"
    Select = "Select"


class CannedACL(str):
    private = "private"
    public_read = "public-read"
    public_read_write = "public-read-write"
    aws_exec_read = "aws-exec-read"
    authenticated_read = "authenticated-read"
    bucket_owner_read = "bucket-owner-read"
    bucket_owner_full_control = "bucket-owner-full-control"


class EncryptionType(str):
    aws_kms = "aws:kms"
    AES256 = "AES256"


class ExpressionType(str):
    SQL = "SQL"


class FileHeaderInfo(str):
    USE = "USE"
    IGNORE = "IGNORE"
    NONE = "NONE"


class Permission(str):
    FULL_CONTROL = "FULL_CONTROL"
    WRITE = "WRITE"
    WRITE_ACP = "WRITE_ACP"
    READ = "READ"
    READ_ACP = "READ_ACP"


class QuoteFields(str):
    ALWAYS = "ALWAYS"
    ASNEEDED = "ASNEEDED"


class StatusCode(str):
    InProgress = "InProgress"
    Succeeded = "Succeeded"
    Failed = "Failed"


class StorageClass(str):
    STANDARD = "STANDARD"
    REDUCED_REDUNDANCY = "REDUCED_REDUNDANCY"
    STANDARD_IA = "STANDARD_IA"


class Type(str):
    AmazonCustomerByEmail = "AmazonCustomerByEmail"
    CanonicalUser = "CanonicalUser"
    Group = "Group"


class InsufficientCapacityException(ServiceException):
    """Returned if there is insufficient capacity to process this expedited
    request. This error only applies to expedited retrievals and not to
    standard or bulk retrievals.
    """

    type: Optional[string]
    code: Optional[string]
    message: Optional[string]


class InvalidParameterValueException(ServiceException):
    """Returned if a parameter of the request is incorrectly specified."""

    type: Optional[string]
    code: Optional[string]
    message: Optional[string]


class LimitExceededException(ServiceException):
    """Returned if the request results in a vault or account limit being
    exceeded.
    """

    type: Optional[string]
    code: Optional[string]
    message: Optional[string]


class MissingParameterValueException(ServiceException):
    """Returned if a required header or parameter is missing from the request."""

    type: Optional[string]
    code: Optional[string]
    message: Optional[string]


class PolicyEnforcedException(ServiceException):
    """Returned if a retrieval job would exceed the current data policy's
    retrieval rate limit. For more information about data retrieval
    policies,
    """

    type: Optional[string]
    code: Optional[string]
    message: Optional[string]


class RequestTimeoutException(ServiceException):
    """Returned if, when uploading an archive, Amazon S3 Glacier times out
    while receiving the upload.
    """

    type: Optional[string]
    code: Optional[string]
    message: Optional[string]


class ResourceNotFoundException(ServiceException):
    """Returned if the specified resource (such as a vault, upload ID, or job
    ID) doesn't exist.
    """

    type: Optional[string]
    code: Optional[string]
    message: Optional[string]


class ServiceUnavailableException(ServiceException):
    """Returned if the service cannot complete the request."""

    type: Optional[string]
    code: Optional[string]
    message: Optional[string]


class AbortMultipartUploadInput(ServiceRequest):
    """Provides options to abort a multipart upload identified by the upload
    ID.

    For information about the underlying REST API, see `Abort Multipart
    Upload <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-multipart-abort-upload.html>`__.
    For conceptual information, see `Working with Archives in Amazon S3
    Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/working-with-archives.html>`__.
    """

    accountId: string
    vaultName: string
    uploadId: string


class AbortVaultLockInput(ServiceRequest):
    """The input values for ``AbortVaultLock``."""

    accountId: string
    vaultName: string


class Grantee(TypedDict, total=False):
    """Contains information about the grantee."""

    Type: Type
    DisplayName: Optional[string]
    URI: Optional[string]
    ID: Optional[string]
    EmailAddress: Optional[string]


class Grant(TypedDict, total=False):
    """Contains information about a grant."""

    Grantee: Optional[Grantee]
    Permission: Optional[Permission]


AccessControlPolicyList = List[Grant]
TagMap = Dict[TagKey, TagValue]


class AddTagsToVaultInput(ServiceRequest):
    """The input values for ``AddTagsToVault``."""

    accountId: string
    vaultName: string
    Tags: Optional[TagMap]


class ArchiveCreationOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request.

    For information about the underlying REST API, see `Upload
    Archive <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-archive-post.html>`__.
    For conceptual information, see `Working with Archives in Amazon S3
    Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/working-with-archives.html>`__.
    """

    location: Optional[string]
    checksum: Optional[string]
    archiveId: Optional[string]


class CSVInput(TypedDict, total=False):
    """Contains information about the comma-separated value (CSV) file to
    select from.
    """

    FileHeaderInfo: Optional[FileHeaderInfo]
    Comments: Optional[string]
    QuoteEscapeCharacter: Optional[string]
    RecordDelimiter: Optional[string]
    FieldDelimiter: Optional[string]
    QuoteCharacter: Optional[string]


class CSVOutput(TypedDict, total=False):
    """Contains information about the comma-separated value (CSV) file that the
    job results are stored in.
    """

    QuoteFields: Optional[QuoteFields]
    QuoteEscapeCharacter: Optional[string]
    RecordDelimiter: Optional[string]
    FieldDelimiter: Optional[string]
    QuoteCharacter: Optional[string]


class CompleteMultipartUploadInput(ServiceRequest):
    """Provides options to complete a multipart upload operation. This informs
    Amazon Glacier that all the archive parts have been uploaded and Amazon
    S3 Glacier (Glacier) can now assemble the archive from the uploaded
    parts. After assembling and saving the archive to the vault, Glacier
    returns the URI path of the newly created archive resource.
    """

    accountId: string
    vaultName: string
    uploadId: string
    archiveSize: Optional[string]
    checksum: Optional[string]


class CompleteVaultLockInput(ServiceRequest):
    """The input values for ``CompleteVaultLock``."""

    accountId: string
    vaultName: string
    lockId: string


class CreateVaultInput(ServiceRequest):
    """Provides options to create a vault."""

    accountId: string
    vaultName: string


class CreateVaultOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    location: Optional[string]


NullableLong = int


class DataRetrievalRule(TypedDict, total=False):
    """Data retrieval policy rule."""

    Strategy: Optional[string]
    BytesPerHour: Optional[NullableLong]


DataRetrievalRulesList = List[DataRetrievalRule]


class DataRetrievalPolicy(TypedDict, total=False):
    """Data retrieval policy."""

    Rules: Optional[DataRetrievalRulesList]


class DeleteArchiveInput(ServiceRequest):
    """Provides options for deleting an archive from an Amazon S3 Glacier
    vault.
    """

    accountId: string
    vaultName: string
    archiveId: string


class DeleteVaultAccessPolicyInput(ServiceRequest):
    """DeleteVaultAccessPolicy input."""

    accountId: string
    vaultName: string


class DeleteVaultInput(ServiceRequest):
    """Provides options for deleting a vault from Amazon S3 Glacier."""

    accountId: string
    vaultName: string


class DeleteVaultNotificationsInput(ServiceRequest):
    """Provides options for deleting a vault notification configuration from an
    Amazon Glacier vault.
    """

    accountId: string
    vaultName: string


class DescribeJobInput(ServiceRequest):
    """Provides options for retrieving a job description."""

    accountId: string
    vaultName: string
    jobId: string


class DescribeVaultInput(ServiceRequest):
    """Provides options for retrieving metadata for a specific vault in Amazon
    Glacier.
    """

    accountId: string
    vaultName: string


long = int


class DescribeVaultOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    VaultARN: Optional[string]
    VaultName: Optional[string]
    CreationDate: Optional[string]
    LastInventoryDate: Optional[string]
    NumberOfArchives: Optional[long]
    SizeInBytes: Optional[long]


class Encryption(TypedDict, total=False):
    """Contains information about the encryption used to store the job results
    in Amazon S3.
    """

    EncryptionType: Optional[EncryptionType]
    KMSKeyId: Optional[string]
    KMSContext: Optional[string]


class GetDataRetrievalPolicyInput(ServiceRequest):
    """Input for GetDataRetrievalPolicy."""

    accountId: string


class GetDataRetrievalPolicyOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to the
    ``GetDataRetrievalPolicy`` request.
    """

    Policy: Optional[DataRetrievalPolicy]


class GetJobOutputInput(ServiceRequest):
    """Provides options for downloading output of an Amazon S3 Glacier job."""

    accountId: string
    vaultName: string
    jobId: string
    range: Optional[string]


Stream = bytes


class GetJobOutputOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    body: Optional[Stream]
    checksum: Optional[string]
    status: Optional[httpstatus]
    contentRange: Optional[string]
    acceptRanges: Optional[string]
    contentType: Optional[string]
    archiveDescription: Optional[string]


class GetVaultAccessPolicyInput(ServiceRequest):
    """Input for GetVaultAccessPolicy."""

    accountId: string
    vaultName: string


class VaultAccessPolicy(TypedDict, total=False):
    """Contains the vault access policy."""

    Policy: Optional[string]


class GetVaultAccessPolicyOutput(TypedDict, total=False):
    """Output for GetVaultAccessPolicy."""

    policy: Optional[VaultAccessPolicy]


class GetVaultLockInput(ServiceRequest):
    """The input values for ``GetVaultLock``."""

    accountId: string
    vaultName: string


class GetVaultLockOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    Policy: Optional[string]
    State: Optional[string]
    ExpirationDate: Optional[string]
    CreationDate: Optional[string]


class GetVaultNotificationsInput(ServiceRequest):
    """Provides options for retrieving the notification configuration set on an
    Amazon Glacier vault.
    """

    accountId: string
    vaultName: string


NotificationEventList = List[string]


class VaultNotificationConfig(TypedDict, total=False):
    """Represents a vault's notification configuration."""

    SNSTopic: Optional[string]
    Events: Optional[NotificationEventList]


class GetVaultNotificationsOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    vaultNotificationConfig: Optional[VaultNotificationConfig]


hashmap = Dict[string, string]


class S3Location(TypedDict, total=False):
    """Contains information about the location in Amazon S3 where the select
    job results are stored.
    """

    BucketName: Optional[string]
    Prefix: Optional[string]
    Encryption: Optional[Encryption]
    CannedACL: Optional[CannedACL]
    AccessControlList: Optional[AccessControlPolicyList]
    Tagging: Optional[hashmap]
    UserMetadata: Optional[hashmap]
    StorageClass: Optional[StorageClass]


class OutputLocation(TypedDict, total=False):
    """Contains information about the location where the select job results are
    stored.
    """

    S3: Optional[S3Location]


class OutputSerialization(TypedDict, total=False):
    """Describes how the select output is serialized."""

    csv: Optional[CSVOutput]


class InputSerialization(TypedDict, total=False):
    """Describes how the archive is serialized."""

    csv: Optional[CSVInput]


class SelectParameters(TypedDict, total=False):
    """Contains information about the parameters used for a select."""

    InputSerialization: Optional[InputSerialization]
    ExpressionType: Optional[ExpressionType]
    Expression: Optional[string]
    OutputSerialization: Optional[OutputSerialization]


class InventoryRetrievalJobDescription(TypedDict, total=False):
    """Describes the options for a range inventory retrieval job."""

    Format: Optional[string]
    StartDate: Optional[DateTime]
    EndDate: Optional[DateTime]
    Limit: Optional[string]
    Marker: Optional[string]


Size = int


class GlacierJobDescription(TypedDict, total=False):
    """Contains the description of an Amazon S3 Glacier job."""

    JobId: Optional[string]
    JobDescription: Optional[string]
    Action: Optional[ActionCode]
    ArchiveId: Optional[string]
    VaultARN: Optional[string]
    CreationDate: Optional[string]
    Completed: Optional[boolean]
    StatusCode: Optional[StatusCode]
    StatusMessage: Optional[string]
    ArchiveSizeInBytes: Optional[Size]
    InventorySizeInBytes: Optional[Size]
    SNSTopic: Optional[string]
    CompletionDate: Optional[string]
    SHA256TreeHash: Optional[string]
    ArchiveSHA256TreeHash: Optional[string]
    RetrievalByteRange: Optional[string]
    Tier: Optional[string]
    InventoryRetrievalParameters: Optional[InventoryRetrievalJobDescription]
    JobOutputPath: Optional[string]
    SelectParameters: Optional[SelectParameters]
    OutputLocation: Optional[OutputLocation]


class InventoryRetrievalJobInput(TypedDict, total=False):
    """Provides options for specifying a range inventory retrieval job."""

    StartDate: Optional[string]
    EndDate: Optional[string]
    Limit: Optional[string]
    Marker: Optional[string]


class JobParameters(TypedDict, total=False):
    """Provides options for defining a job."""

    Format: Optional[string]
    Type: Optional[string]
    ArchiveId: Optional[string]
    Description: Optional[string]
    SNSTopic: Optional[string]
    RetrievalByteRange: Optional[string]
    Tier: Optional[string]
    InventoryRetrievalParameters: Optional[InventoryRetrievalJobInput]
    SelectParameters: Optional[SelectParameters]
    OutputLocation: Optional[OutputLocation]


class InitiateJobInput(ServiceRequest):
    """Provides options for initiating an Amazon S3 Glacier job."""

    accountId: string
    vaultName: string
    jobParameters: Optional[JobParameters]


class InitiateJobOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    location: Optional[string]
    jobId: Optional[string]
    jobOutputPath: Optional[string]


class InitiateMultipartUploadInput(ServiceRequest):
    """Provides options for initiating a multipart upload to an Amazon S3
    Glacier vault.
    """

    accountId: string
    vaultName: string
    archiveDescription: Optional[string]
    partSize: Optional[string]


class InitiateMultipartUploadOutput(TypedDict, total=False):
    """The Amazon S3 Glacier response to your request."""

    location: Optional[string]
    uploadId: Optional[string]


class VaultLockPolicy(TypedDict, total=False):
    """Contains the vault lock policy."""

    Policy: Optional[string]


class InitiateVaultLockInput(ServiceRequest):
    """The input values for ``InitiateVaultLock``."""

    accountId: string
    vaultName: string
    policy: Optional[VaultLockPolicy]


class InitiateVaultLockOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    lockId: Optional[string]


JobList = List[GlacierJobDescription]


class ListJobsInput(ServiceRequest):
    """Provides options for retrieving a job list for an Amazon S3 Glacier
    vault.
    """

    accountId: string
    vaultName: string
    limit: Optional[string]
    marker: Optional[string]
    statuscode: Optional[string]
    completed: Optional[string]


class ListJobsOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    JobList: Optional[JobList]
    Marker: Optional[string]


class ListMultipartUploadsInput(ServiceRequest):
    """Provides options for retrieving list of in-progress multipart uploads
    for an Amazon Glacier vault.
    """

    accountId: string
    vaultName: string
    marker: Optional[string]
    limit: Optional[string]


class UploadListElement(TypedDict, total=False):
    """A list of in-progress multipart uploads for a vault."""

    MultipartUploadId: Optional[string]
    VaultARN: Optional[string]
    ArchiveDescription: Optional[string]
    PartSizeInBytes: Optional[long]
    CreationDate: Optional[string]


UploadsList = List[UploadListElement]


class ListMultipartUploadsOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    UploadsList: Optional[UploadsList]
    Marker: Optional[string]


class ListPartsInput(ServiceRequest):
    """Provides options for retrieving a list of parts of an archive that have
    been uploaded in a specific multipart upload.
    """

    accountId: string
    vaultName: string
    uploadId: string
    marker: Optional[string]
    limit: Optional[string]


class PartListElement(TypedDict, total=False):
    """A list of the part sizes of the multipart upload."""

    RangeInBytes: Optional[string]
    SHA256TreeHash: Optional[string]


PartList = List[PartListElement]


class ListPartsOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    MultipartUploadId: Optional[string]
    VaultARN: Optional[string]
    ArchiveDescription: Optional[string]
    PartSizeInBytes: Optional[long]
    CreationDate: Optional[string]
    Parts: Optional[PartList]
    Marker: Optional[string]


class ListProvisionedCapacityInput(ServiceRequest):
    accountId: string


class ProvisionedCapacityDescription(TypedDict, total=False):
    """The definition for a provisioned capacity unit."""

    CapacityId: Optional[string]
    StartDate: Optional[string]
    ExpirationDate: Optional[string]


ProvisionedCapacityList = List[ProvisionedCapacityDescription]


class ListProvisionedCapacityOutput(TypedDict, total=False):
    ProvisionedCapacityList: Optional[ProvisionedCapacityList]


class ListTagsForVaultInput(ServiceRequest):
    """The input value for ``ListTagsForVaultInput``."""

    accountId: string
    vaultName: string


class ListTagsForVaultOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    Tags: Optional[TagMap]


class ListVaultsInput(ServiceRequest):
    """Provides options to retrieve the vault list owned by the calling user's
    account. The list provides metadata information for each vault.
    """

    accountId: string
    marker: Optional[string]
    limit: Optional[string]


VaultList = List[DescribeVaultOutput]


class ListVaultsOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    VaultList: Optional[VaultList]
    Marker: Optional[string]


class PurchaseProvisionedCapacityInput(ServiceRequest):
    accountId: string


class PurchaseProvisionedCapacityOutput(TypedDict, total=False):
    capacityId: Optional[string]


TagKeyList = List[string]


class RemoveTagsFromVaultInput(ServiceRequest):
    """The input value for ``RemoveTagsFromVaultInput``."""

    accountId: string
    vaultName: string
    TagKeys: Optional[TagKeyList]


class SetDataRetrievalPolicyInput(ServiceRequest):
    """SetDataRetrievalPolicy input."""

    accountId: string
    Policy: Optional[DataRetrievalPolicy]


class SetVaultAccessPolicyInput(ServiceRequest):
    """SetVaultAccessPolicy input."""

    accountId: string
    vaultName: string
    policy: Optional[VaultAccessPolicy]


class SetVaultNotificationsInput(ServiceRequest):
    """Provides options to configure notifications that will be sent when
    specific events happen to a vault.
    """

    accountId: string
    vaultName: string
    vaultNotificationConfig: Optional[VaultNotificationConfig]


class UploadArchiveInput(ServiceRequest):
    """Provides options to add an archive to a vault."""

    vaultName: string
    accountId: string
    archiveDescription: Optional[string]
    checksum: Optional[string]
    body: Optional[Stream]


class UploadMultipartPartInput(ServiceRequest):
    """Provides options to upload a part of an archive in a multipart upload
    operation.
    """

    accountId: string
    vaultName: string
    uploadId: string
    checksum: Optional[string]
    range: Optional[string]
    body: Optional[Stream]


class UploadMultipartPartOutput(TypedDict, total=False):
    """Contains the Amazon S3 Glacier response to your request."""

    checksum: Optional[string]


class GlacierApi:

    service = "glacier"
    version = "2012-06-01"

    @handler("AbortMultipartUpload")
    def abort_multipart_upload(
        self, context: RequestContext, account_id: string, vault_name: string, upload_id: string
    ) -> None:
        """This operation aborts a multipart upload identified by the upload ID.

        After the Abort Multipart Upload request succeeds, you cannot upload any
        more parts to the multipart upload or complete the multipart upload.
        Aborting a completed upload fails. However, aborting an already-aborted
        upload will succeed, for a short time. For more information about
        uploading a part and completing a multipart upload, see
        UploadMultipartPart and CompleteMultipartUpload.

        This operation is idempotent.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Working with
        Archives in Amazon S3
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/working-with-archives.html>`__
        and `Abort Multipart
        Upload <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-multipart-abort-upload.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param upload_id: The upload ID of the multipart upload to delete.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("AbortVaultLock")
    def abort_vault_lock(
        self, context: RequestContext, account_id: string, vault_name: string
    ) -> None:
        """This operation aborts the vault locking process if the vault lock is not
        in the ``Locked`` state. If the vault lock is in the ``Locked`` state
        when this operation is requested, the operation returns an
        ``AccessDeniedException`` error. Aborting the vault locking process
        removes the vault lock policy from the specified vault.

        A vault lock is put into the ``InProgress`` state by calling
        InitiateVaultLock. A vault lock is put into the ``Locked`` state by
        calling CompleteVaultLock. You can get the state of a vault lock by
        calling GetVaultLock. For more information about the vault locking
        process, see `Amazon Glacier Vault
        Lock <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-lock.html>`__.
        For more information about vault lock policies, see `Amazon Glacier
        Access Control with Vault Lock
        Policies <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-lock-policy.html>`__.

        This operation is idempotent. You can successfully invoke this operation
        multiple times, if the vault lock is in the ``InProgress`` state or if
        there is no policy associated with the vault.

        :param account_id: The ``AccountId`` value is the AWS account ID.
        :param vault_name: The name of the vault.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("AddTagsToVault")
    def add_tags_to_vault(
        self, context: RequestContext, account_id: string, vault_name: string, tags: TagMap = None
    ) -> None:
        """This operation adds the specified tags to a vault. Each tag is composed
        of a key and a value. Each vault can have up to 10 tags. If your request
        would cause the tag limit for the vault to be exceeded, the operation
        throws the ``LimitExceededException`` error. If a tag already exists on
        the vault under a specified key, the existing key value will be
        overwritten. For more information about tags, see `Tagging Amazon S3
        Glacier
        Resources <https://docs.aws.amazon.com/amazonglacier/latest/dev/tagging.html>`__.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param tags: The tags to add to the vault.
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ResourceNotFoundException:
        :raises LimitExceededException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("CompleteMultipartUpload")
    def complete_multipart_upload(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        upload_id: string,
        archive_size: string = None,
        checksum: string = None,
    ) -> ArchiveCreationOutput:
        """You call this operation to inform Amazon S3 Glacier (Glacier) that all
        the archive parts have been uploaded and that Glacier can now assemble
        the archive from the uploaded parts. After assembling and saving the
        archive to the vault, Glacier returns the URI path of the newly created
        archive resource. Using the URI path, you can then access the archive.
        After you upload an archive, you should save the archive ID returned to
        retrieve the archive at a later point. You can also get the vault
        inventory to obtain a list of archive IDs in a vault. For more
        information, see InitiateJob.

        In the request, you must include the computed SHA256 tree hash of the
        entire archive you have uploaded. For information about computing a
        SHA256 tree hash, see `Computing
        Checksums <https://docs.aws.amazon.com/amazonglacier/latest/dev/checksum-calculations.html>`__.
        On the server side, Glacier also constructs the SHA256 tree hash of the
        assembled archive. If the values match, Glacier saves the archive to the
        vault; otherwise, it returns an error, and the operation fails. The
        ListParts operation returns a list of parts uploaded for a specific
        multipart upload. It includes checksum information for each uploaded
        part that can be used to debug a bad checksum issue.

        Additionally, Glacier also checks for any missing content ranges when
        assembling the archive, if missing content ranges are found, Glacier
        returns an error and the operation fails.

        Complete Multipart Upload is an idempotent operation. After your first
        successful complete multipart upload, if you call the operation again
        within a short period, the operation will succeed and return the same
        archive ID. This is useful in the event you experience a network issue
        that causes an aborted connection or receive a 500 server error, in
        which case you can repeat your Complete Multipart Upload request and get
        the same archive ID without creating duplicate archives. Note, however,
        that after the multipart upload completes, you cannot call the List
        Parts operation and the multipart upload will not appear in List
        Multipart Uploads response, even if idempotent complete is possible.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Uploading Large
        Archives in Parts (Multipart
        Upload) <https://docs.aws.amazon.com/amazonglacier/latest/dev/uploading-archive-mpu.html>`__
        and `Complete Multipart
        Upload <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-multipart-complete-upload.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param upload_id: The upload ID of the multipart upload.
        :param archive_size: The total size, in bytes, of the entire archive.
        :param checksum: The SHA256 tree hash of the entire archive.
        :returns: ArchiveCreationOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("CompleteVaultLock")
    def complete_vault_lock(
        self, context: RequestContext, account_id: string, vault_name: string, lock_id: string
    ) -> None:
        """This operation completes the vault locking process by transitioning the
        vault lock from the ``InProgress`` state to the ``Locked`` state, which
        causes the vault lock policy to become unchangeable. A vault lock is put
        into the ``InProgress`` state by calling InitiateVaultLock. You can
        obtain the state of the vault lock by calling GetVaultLock. For more
        information about the vault locking process, `Amazon Glacier Vault
        Lock <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-lock.html>`__.

        This operation is idempotent. This request is always successful if the
        vault lock is in the ``Locked`` state and the provided lock ID matches
        the lock ID originally used to lock the vault.

        If an invalid lock ID is passed in the request when the vault lock is in
        the ``Locked`` state, the operation returns an ``AccessDeniedException``
        error. If an invalid lock ID is passed in the request when the vault
        lock is in the ``InProgress`` state, the operation throws an
        ``InvalidParameter`` error.

        :param account_id: The ``AccountId`` value is the AWS account ID.
        :param vault_name: The name of the vault.
        :param lock_id: The ``lockId`` value is the lock ID obtained from a InitiateVaultLock
        request.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("CreateVault")
    def create_vault(
        self, context: RequestContext, account_id: string, vault_name: string
    ) -> CreateVaultOutput:
        """This operation creates a new vault with the specified name. The name of
        the vault must be unique within a region for an AWS account. You can
        create up to 1,000 vaults per account. If you need to create more
        vaults, contact Amazon S3 Glacier.

        You must use the following guidelines when naming a vault.

        -  Names can be between 1 and 255 characters long.

        -  Allowed characters are a-z, A-Z, 0-9, '_' (underscore), '-' (hyphen),
           and '.' (period).

        This operation is idempotent.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Creating a
        Vault in Amazon
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/creating-vaults.html>`__
        and `Create
        Vault <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-vault-put.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID.
        :param vault_name: The name of the vault.
        :returns: CreateVaultOutput
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("DeleteArchive")
    def delete_archive(
        self, context: RequestContext, account_id: string, vault_name: string, archive_id: string
    ) -> None:
        """This operation deletes an archive from a vault. Subsequent requests to
        initiate a retrieval of this archive will fail. Archive retrievals that
        are in progress for this archive ID may or may not succeed according to
        the following scenarios:

        -  If the archive retrieval job is actively preparing the data for
           download when Amazon S3 Glacier receives the delete archive request,
           the archival retrieval operation might fail.

        -  If the archive retrieval job has successfully prepared the archive
           for download when Amazon S3 Glacier receives the delete archive
           request, you will be able to download the output.

        This operation is idempotent. Attempting to delete an already-deleted
        archive does not result in an error.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Deleting an
        Archive in Amazon
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/deleting-an-archive.html>`__
        and `Delete
        Archive <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-archive-delete.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param archive_id: The ID of the archive to delete.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteVault")
    def delete_vault(self, context: RequestContext, account_id: string, vault_name: string) -> None:
        """This operation deletes a vault. Amazon S3 Glacier will delete a vault
        only if there are no archives in the vault as of the last inventory and
        there have been no writes to the vault since the last inventory. If
        either of these conditions is not satisfied, the vault deletion fails
        (that is, the vault is not removed) and Amazon S3 Glacier returns an
        error. You can use DescribeVault to return the number of archives in a
        vault, and you can use `Initiate a Job (POST
        jobs) <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-initiate-job-post.html>`__
        to initiate a new inventory retrieval for a vault. The inventory
        contains the archive IDs you use to delete archives using `Delete
        Archive (DELETE
        archive) <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-archive-delete.html>`__.

        This operation is idempotent.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Deleting a
        Vault in Amazon
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/deleting-vaults.html>`__
        and `Delete
        Vault <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-vault-delete.html>`__
        in the *Amazon S3 Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteVaultAccessPolicy")
    def delete_vault_access_policy(
        self, context: RequestContext, account_id: string, vault_name: string
    ) -> None:
        """This operation deletes the access policy associated with the specified
        vault. The operation is eventually consistent; that is, it might take
        some time for Amazon S3 Glacier to completely remove the access policy,
        and you might still see the effect of the policy for a short time after
        you send the delete request.

        This operation is idempotent. You can invoke delete multiple times, even
        if there is no policy associated with the vault. For more information
        about vault access policies, see `Amazon Glacier Access Control with
        Vault Access
        Policies <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-access-policy.html>`__.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteVaultNotifications")
    def delete_vault_notifications(
        self, context: RequestContext, account_id: string, vault_name: string
    ) -> None:
        """This operation deletes the notification configuration set for a vault.
        The operation is eventually consistent; that is, it might take some time
        for Amazon S3 Glacier to completely disable the notifications and you
        might still receive some notifications for a short time after you send
        the delete request.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Configuring
        Vault Notifications in Amazon S3
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/configuring-notifications.html>`__
        and `Delete Vault Notification
        Configuration <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-vault-notifications-delete.html>`__
        in the Amazon S3 Glacier Developer Guide.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeJob")
    def describe_job(
        self, context: RequestContext, account_id: string, vault_name: string, job_id: string
    ) -> GlacierJobDescription:
        """This operation returns information about a job you previously initiated,
        including the job initiation date, the user who initiated the job, the
        job status code/message and the Amazon SNS topic to notify after Amazon
        S3 Glacier (Glacier) completes the job. For more information about
        initiating a job, see InitiateJob.

        This operation enables you to check the status of your job. However, it
        is strongly recommended that you set up an Amazon SNS topic and specify
        it in your initiate job request so that Glacier can notify the topic
        after it completes the job.

        A job ID will not expire for at least 24 hours after Glacier completes
        the job.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For more information about using this operation, see the documentation
        for the underlying REST API `Describe
        Job <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-describe-job-get.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param job_id: The ID of the job to describe.
        :returns: GlacierJobDescription
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeVault")
    def describe_vault(
        self, context: RequestContext, account_id: string, vault_name: string
    ) -> DescribeVaultOutput:
        """This operation returns information about a vault, including the vault's
        Amazon Resource Name (ARN), the date the vault was created, the number
        of archives it contains, and the total size of all the archives in the
        vault. The number of archives and their total size are as of the last
        inventory generation. This means that if you add or remove an archive
        from a vault, and then immediately use Describe Vault, the change in
        contents will not be immediately reflected. If you want to retrieve the
        latest inventory of the vault, use InitiateJob. Amazon S3 Glacier
        generates vault inventories approximately daily. For more information,
        see `Downloading a Vault Inventory in Amazon S3
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-inventory.html>`__.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Retrieving
        Vault Metadata in Amazon S3
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/retrieving-vault-info.html>`__
        and `Describe
        Vault <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-vault-get.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :returns: DescribeVaultOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetDataRetrievalPolicy")
    def get_data_retrieval_policy(
        self, context: RequestContext, account_id: string
    ) -> GetDataRetrievalPolicyOutput:
        """This operation returns the current data retrieval policy for the account
        and region specified in the GET request. For more information about data
        retrieval policies, see `Amazon Glacier Data Retrieval
        Policies <https://docs.aws.amazon.com/amazonglacier/latest/dev/data-retrieval-policy.html>`__.

        :param account_id: The ``AccountId`` value is the AWS account ID.
        :returns: GetDataRetrievalPolicyOutput
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetJobOutput")
    def get_job_output(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        job_id: string,
        range: string = None,
    ) -> GetJobOutputOutput:
        """This operation downloads the output of the job you initiated using
        InitiateJob. Depending on the job type you specified when you initiated
        the job, the output will be either the content of an archive or a vault
        inventory.

        You can download all the job output or download a portion of the output
        by specifying a byte range. In the case of an archive retrieval job,
        depending on the byte range you specify, Amazon S3 Glacier (Glacier)
        returns the checksum for the portion of the data. You can compute the
        checksum on the client and verify that the values match to ensure the
        portion you downloaded is the correct data.

        A job ID will not expire for at least 24 hours after Glacier completes
        the job. That a byte range. For both archive and inventory retrieval
        jobs, you should verify the downloaded size against the size returned in
        the headers from the **Get Job Output** response.

        For archive retrieval jobs, you should also verify that the size is what
        you expected. If you download a portion of the output, the expected size
        is based on the range of bytes you specified. For example, if you
        specify a range of ``bytes=0-1048575``, you should verify your download
        size is 1,048,576 bytes. If you download an entire archive, the expected
        size is the size of the archive when you uploaded it to Amazon S3
        Glacier The expected size is also returned in the headers from the **Get
        Job Output** response.

        In the case of an archive retrieval job, depending on the byte range you
        specify, Glacier returns the checksum for the portion of the data. To
        ensure the portion you downloaded is the correct data, compute the
        checksum on the client, verify that the values match, and verify that
        the size is what you expected.

        A job ID does not expire for at least 24 hours after Glacier completes
        the job. That is, you can download the job output within the 24 hours
        period after Amazon Glacier completes the job.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and the underlying REST API, see `Downloading
        a Vault
        Inventory <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-inventory.html>`__,
        `Downloading an
        Archive <https://docs.aws.amazon.com/amazonglacier/latest/dev/downloading-an-archive.html>`__,
        and `Get Job
        Output <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-job-output-get.html>`__

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param job_id: The job ID whose data is downloaded.
        :param range: The range of bytes to retrieve from the output.
        :returns: GetJobOutputOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetVaultAccessPolicy")
    def get_vault_access_policy(
        self, context: RequestContext, account_id: string, vault_name: string
    ) -> GetVaultAccessPolicyOutput:
        """This operation retrieves the ``access-policy`` subresource set on the
        vault; for more information on setting this subresource, see `Set Vault
        Access Policy (PUT
        access-policy) <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-SetVaultAccessPolicy.html>`__.
        If there is no access policy set on the vault, the operation returns a
        ``404 Not found`` error. For more information about vault access
        policies, see `Amazon Glacier Access Control with Vault Access
        Policies <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-access-policy.html>`__.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :returns: GetVaultAccessPolicyOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetVaultLock")
    def get_vault_lock(
        self, context: RequestContext, account_id: string, vault_name: string
    ) -> GetVaultLockOutput:
        """This operation retrieves the following attributes from the
        ``lock-policy`` subresource set on the specified vault:

        -  The vault lock policy set on the vault.

        -  The state of the vault lock, which is either ``InProgess`` or
           ``Locked``.

        -  When the lock ID expires. The lock ID is used to complete the vault
           locking process.

        -  When the vault lock was initiated and put into the ``InProgress``
           state.

        A vault lock is put into the ``InProgress`` state by calling
        InitiateVaultLock. A vault lock is put into the ``Locked`` state by
        calling CompleteVaultLock. You can abort the vault locking process by
        calling AbortVaultLock. For more information about the vault locking
        process, `Amazon Glacier Vault
        Lock <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-lock.html>`__.

        If there is no vault lock policy set on the vault, the operation returns
        a ``404 Not found`` error. For more information about vault lock
        policies, `Amazon Glacier Access Control with Vault Lock
        Policies <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-lock-policy.html>`__.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :returns: GetVaultLockOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("GetVaultNotifications")
    def get_vault_notifications(
        self, context: RequestContext, account_id: string, vault_name: string
    ) -> GetVaultNotificationsOutput:
        """This operation retrieves the ``notification-configuration`` subresource
        of the specified vault.

        For information about setting a notification configuration on a vault,
        see SetVaultNotifications. If a notification configuration for a vault
        is not set, the operation returns a ``404 Not Found`` error. For more
        information about vault notifications, see `Configuring Vault
        Notifications in Amazon S3
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/configuring-notifications.html>`__.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Configuring
        Vault Notifications in Amazon S3
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/configuring-notifications.html>`__
        and `Get Vault Notification
        Configuration <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-vault-notifications-get.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :returns: GetVaultNotificationsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("InitiateJob")
    def initiate_job(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        job_parameters: JobParameters = None,
    ) -> InitiateJobOutput:
        """This operation initiates a job of the specified type, which can be a
        select, an archival retrieval, or a vault retrieval. For more
        information about using this operation, see the documentation for the
        underlying REST API `Initiate a
        Job <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-initiate-job-post.html>`__.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param job_parameters: Provides options for specifying job information.
        :returns: InitiateJobOutput
        :raises ResourceNotFoundException:
        :raises PolicyEnforcedException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises InsufficientCapacityException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("InitiateMultipartUpload")
    def initiate_multipart_upload(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        archive_description: string = None,
        part_size: string = None,
    ) -> InitiateMultipartUploadOutput:
        """This operation initiates a multipart upload. Amazon S3 Glacier creates a
        multipart upload resource and returns its ID in the response. The
        multipart upload ID is used in subsequent requests to upload parts of an
        archive (see UploadMultipartPart).

        When you initiate a multipart upload, you specify the part size in
        number of bytes. The part size must be a megabyte (1024 KB) multiplied
        by a power of 2-for example, 1048576 (1 MB), 2097152 (2 MB), 4194304 (4
        MB), 8388608 (8 MB), and so on. The minimum allowable part size is 1 MB,
        and the maximum is 4 GB.

        Every part you upload to this resource (see UploadMultipartPart), except
        the last one, must have the same size. The last one can be the same size
        or smaller. For example, suppose you want to upload a 16.2 MB file. If
        you initiate the multipart upload with a part size of 4 MB, you will
        upload four parts of 4 MB each and one part of 0.2 MB.

        You don't need to know the size of the archive when you start a
        multipart upload because Amazon S3 Glacier does not require you to
        specify the overall archive size.

        After you complete the multipart upload, Amazon S3 Glacier (Glacier)
        removes the multipart upload resource referenced by the ID. Glacier also
        removes the multipart upload resource if you cancel the multipart upload
        or it may be removed if there is no activity for a period of 24 hours.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Uploading Large
        Archives in Parts (Multipart
        Upload) <https://docs.aws.amazon.com/amazonglacier/latest/dev/uploading-archive-mpu.html>`__
        and `Initiate Multipart
        Upload <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-multipart-initiate-upload.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param archive_description: The archive description that you are uploading in parts.
        :param part_size: The size of each part except the last, in bytes.
        :returns: InitiateMultipartUploadOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("InitiateVaultLock")
    def initiate_vault_lock(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        policy: VaultLockPolicy = None,
    ) -> InitiateVaultLockOutput:
        """This operation initiates the vault locking process by doing the
        following:

        -  Installing a vault lock policy on the specified vault.

        -  Setting the lock state of vault lock to ``InProgress``.

        -  Returning a lock ID, which is used to complete the vault locking
           process.

        You can set one vault lock policy for each vault and this policy can be
        up to 20 KB in size. For more information about vault lock policies, see
        `Amazon Glacier Access Control with Vault Lock
        Policies <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-lock-policy.html>`__.

        You must complete the vault locking process within 24 hours after the
        vault lock enters the ``InProgress`` state. After the 24 hour window
        ends, the lock ID expires, the vault automatically exits the
        ``InProgress`` state, and the vault lock policy is removed from the
        vault. You call CompleteVaultLock to complete the vault locking process
        by setting the state of the vault lock to ``Locked``.

        After a vault lock is in the ``Locked`` state, you cannot initiate a new
        vault lock for the vault.

        You can abort the vault locking process by calling AbortVaultLock. You
        can get the state of the vault lock by calling GetVaultLock. For more
        information about the vault locking process, `Amazon Glacier Vault
        Lock <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-lock.html>`__.

        If this operation is called when the vault lock is in the ``InProgress``
        state, the operation returns an ``AccessDeniedException`` error. When
        the vault lock is in the ``InProgress`` state you must call
        AbortVaultLock before you can initiate a new vault lock policy.

        :param account_id: The ``AccountId`` value is the AWS account ID.
        :param vault_name: The name of the vault.
        :param policy: The vault lock policy as a JSON string, which uses "\" as an escape
        character.
        :returns: InitiateVaultLockOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListJobs")
    def list_jobs(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        limit: string = None,
        marker: string = None,
        statuscode: string = None,
        completed: string = None,
    ) -> ListJobsOutput:
        """This operation lists jobs for a vault, including jobs that are
        in-progress and jobs that have recently finished. The List Job operation
        returns a list of these jobs sorted by job initiation time.

        Amazon Glacier retains recently completed jobs for a period before
        deleting them; however, it eventually removes completed jobs. The output
        of completed jobs can be retrieved. Retaining completed jobs for a
        period of time after they have completed enables you to get a job output
        in the event you miss the job completion notification or your first
        attempt to download it fails. For example, suppose you start an archive
        retrieval job to download an archive. After the job completes, you start
        to download the archive but encounter a network error. In this scenario,
        you can retry and download the archive while the job exists.

        The List Jobs operation supports pagination. You should always check the
        response ``Marker`` field. If there are no more jobs to list, the
        ``Marker`` field is set to ``null``. If there are more jobs to list, the
        ``Marker`` field is set to a non-null value, which you can use to
        continue the pagination of the list. To return a list of jobs that
        begins at a specific job, set the marker request parameter to the
        ``Marker`` value for that job that you obtained from a previous List
        Jobs request.

        You can set a maximum limit for the number of jobs returned in the
        response by specifying the ``limit`` parameter in the request. The
        default limit is 50. The number of jobs returned might be fewer than the
        limit, but the number of returned jobs never exceeds the limit.

        Additionally, you can filter the jobs list returned by specifying the
        optional ``statuscode`` parameter or ``completed`` parameter, or both.
        Using the ``statuscode`` parameter, you can specify to return only jobs
        that match either the ``InProgress``, ``Succeeded``, or ``Failed``
        status. Using the ``completed`` parameter, you can specify to return
        only jobs that were completed (``true``) or jobs that were not completed
        (``false``).

        For more information about using this operation, see the documentation
        for the underlying REST API `List
        Jobs <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-jobs-get.html>`__.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param limit: The maximum number of jobs to be returned.
        :param marker: An opaque string used for pagination.
        :param statuscode: The type of job status to return.
        :param completed: The state of the jobs to return.
        :returns: ListJobsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListMultipartUploads")
    def list_multipart_uploads(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        marker: string = None,
        limit: string = None,
    ) -> ListMultipartUploadsOutput:
        """This operation lists in-progress multipart uploads for the specified
        vault. An in-progress multipart upload is a multipart upload that has
        been initiated by an InitiateMultipartUpload request, but has not yet
        been completed or aborted. The list returned in the List Multipart
        Upload response has no guaranteed order.

        The List Multipart Uploads operation supports pagination. By default,
        this operation returns up to 50 multipart uploads in the response. You
        should always check the response for a ``marker`` at which to continue
        the list; if there are no more items the ``marker`` is ``null``. To
        return a list of multipart uploads that begins at a specific upload, set
        the ``marker`` request parameter to the value you obtained from a
        previous List Multipart Upload request. You can also limit the number of
        uploads returned in the response by specifying the ``limit`` parameter
        in the request.

        Note the difference between this operation and listing parts
        (ListParts). The List Multipart Uploads operation lists all multipart
        uploads for a vault and does not require a multipart upload ID. The List
        Parts operation requires a multipart upload ID since parts are
        associated with a single upload.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and the underlying REST API, see `Working
        with Archives in Amazon S3
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/working-with-archives.html>`__
        and `List Multipart
        Uploads <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-multipart-list-uploads.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param marker: An opaque string used for pagination.
        :param limit: Specifies the maximum number of uploads returned in the response body.
        :returns: ListMultipartUploadsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListParts")
    def list_parts(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        upload_id: string,
        marker: string = None,
        limit: string = None,
    ) -> ListPartsOutput:
        """This operation lists the parts of an archive that have been uploaded in
        a specific multipart upload. You can make this request at any time
        during an in-progress multipart upload before you complete the upload
        (see CompleteMultipartUpload. List Parts returns an error for completed
        uploads. The list returned in the List Parts response is sorted by part
        range.

        The List Parts operation supports pagination. By default, this operation
        returns up to 50 uploaded parts in the response. You should always check
        the response for a ``marker`` at which to continue the list; if there
        are no more items the ``marker`` is ``null``. To return a list of parts
        that begins at a specific part, set the ``marker`` request parameter to
        the value you obtained from a previous List Parts request. You can also
        limit the number of parts returned in the response by specifying the
        ``limit`` parameter in the request.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and the underlying REST API, see `Working
        with Archives in Amazon S3
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/working-with-archives.html>`__
        and `List
        Parts <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-multipart-list-parts.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param upload_id: The upload ID of the multipart upload.
        :param marker: An opaque string used for pagination.
        :param limit: The maximum number of parts to be returned.
        :returns: ListPartsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListProvisionedCapacity")
    def list_provisioned_capacity(
        self, context: RequestContext, account_id: string
    ) -> ListProvisionedCapacityOutput:
        """This operation lists the provisioned capacity units for the specified
        AWS account.

        :param account_id: The AWS account ID of the account that owns the vault.
        :returns: ListProvisionedCapacityOutput
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListTagsForVault")
    def list_tags_for_vault(
        self, context: RequestContext, account_id: string, vault_name: string
    ) -> ListTagsForVaultOutput:
        """This operation lists all the tags attached to a vault. The operation
        returns an empty map if there are no tags. For more information about
        tags, see `Tagging Amazon S3 Glacier
        Resources <https://docs.aws.amazon.com/amazonglacier/latest/dev/tagging.html>`__.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :returns: ListTagsForVaultOutput
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ResourceNotFoundException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("ListVaults")
    def list_vaults(
        self,
        context: RequestContext,
        account_id: string,
        marker: string = None,
        limit: string = None,
    ) -> ListVaultsOutput:
        """This operation lists all vaults owned by the calling user's account. The
        list returned in the response is ASCII-sorted by vault name.

        By default, this operation returns up to 10 items. If there are more
        vaults to list, the response ``marker`` field contains the vault Amazon
        Resource Name (ARN) at which to continue the list with a new List Vaults
        request; otherwise, the ``marker`` field is ``null``. To return a list
        of vaults that begins at a specific vault, set the ``marker`` request
        parameter to the vault ARN you obtained from a previous List Vaults
        request. You can also limit the number of vaults returned in the
        response by specifying the ``limit`` parameter in the request.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Retrieving
        Vault Metadata in Amazon S3
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/retrieving-vault-info.html>`__
        and `List
        Vaults <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-vaults-get.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID.
        :param marker: A string used for pagination.
        :param limit: The maximum number of vaults to be returned.
        :returns: ListVaultsOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("PurchaseProvisionedCapacity")
    def purchase_provisioned_capacity(
        self, context: RequestContext, account_id: string
    ) -> PurchaseProvisionedCapacityOutput:
        """This operation purchases a provisioned capacity unit for an AWS account.

        :param account_id: The AWS account ID of the account that owns the vault.
        :returns: PurchaseProvisionedCapacityOutput
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises LimitExceededException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("RemoveTagsFromVault")
    def remove_tags_from_vault(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        tag_keys: TagKeyList = None,
    ) -> None:
        """This operation removes one or more tags from the set of tags attached to
        a vault. For more information about tags, see `Tagging Amazon S3 Glacier
        Resources <https://docs.aws.amazon.com/amazonglacier/latest/dev/tagging.html>`__.
        This operation is idempotent. The operation will be successful, even if
        there are no tags attached to the vault.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param tag_keys: A list of tag keys.
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ResourceNotFoundException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("SetDataRetrievalPolicy")
    def set_data_retrieval_policy(
        self, context: RequestContext, account_id: string, policy: DataRetrievalPolicy = None
    ) -> None:
        """This operation sets and then enacts a data retrieval policy in the
        region specified in the PUT request. You can set one policy per region
        for an AWS account. The policy is enacted within a few minutes of a
        successful PUT operation.

        The set policy operation does not affect retrieval jobs that were in
        progress before the policy was enacted. For more information about data
        retrieval policies, see `Amazon Glacier Data Retrieval
        Policies <https://docs.aws.amazon.com/amazonglacier/latest/dev/data-retrieval-policy.html>`__.

        :param account_id: The ``AccountId`` value is the AWS account ID.
        :param policy: The data retrieval policy in JSON format.
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("SetVaultAccessPolicy")
    def set_vault_access_policy(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        policy: VaultAccessPolicy = None,
    ) -> None:
        """This operation configures an access policy for a vault and will
        overwrite an existing policy. To configure a vault access policy, send a
        PUT request to the ``access-policy`` subresource of the vault. An access
        policy is specific to a vault and is also called a vault subresource.
        You can set one access policy per vault and the policy can be up to 20
        KB in size. For more information about vault access policies, see
        `Amazon Glacier Access Control with Vault Access
        Policies <https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-access-policy.html>`__.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param policy: The vault access policy as a JSON string.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("SetVaultNotifications")
    def set_vault_notifications(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        vault_notification_config: VaultNotificationConfig = None,
    ) -> None:
        """This operation configures notifications that will be sent when specific
        events happen to a vault. By default, you don't get any notifications.

        To configure vault notifications, send a PUT request to the
        ``notification-configuration`` subresource of the vault. The request
        should include a JSON document that provides an Amazon SNS topic and
        specific events for which you want Amazon S3 Glacier to send
        notifications to the topic.

        Amazon SNS topics must grant permission to the vault to be allowed to
        publish notifications to the topic. You can configure a vault to publish
        a notification for the following vault events:

        -  **ArchiveRetrievalCompleted** This event occurs when a job that was
           initiated for an archive retrieval is completed (InitiateJob). The
           status of the completed job can be "Succeeded" or "Failed". The
           notification sent to the SNS topic is the same output as returned
           from DescribeJob.

        -  **InventoryRetrievalCompleted** This event occurs when a job that was
           initiated for an inventory retrieval is completed (InitiateJob). The
           status of the completed job can be "Succeeded" or "Failed". The
           notification sent to the SNS topic is the same output as returned
           from DescribeJob.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Configuring
        Vault Notifications in Amazon S3
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/configuring-notifications.html>`__
        and `Set Vault Notification
        Configuration <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-vault-notifications-put.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param vault_notification_config: Provides options for specifying notification configuration.
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("UploadArchive")
    def upload_archive(
        self,
        context: RequestContext,
        vault_name: string,
        account_id: string,
        archive_description: string = None,
        checksum: string = None,
        body: Stream = None,
    ) -> ArchiveCreationOutput:
        """This operation adds an archive to a vault. This is a synchronous
        operation, and for a successful upload, your data is durably persisted.
        Amazon S3 Glacier returns the archive ID in the ``x-amz-archive-id``
        header of the response.

        You must use the archive ID to access your data in Amazon S3 Glacier.
        After you upload an archive, you should save the archive ID returned so
        that you can retrieve or delete the archive later. Besides saving the
        archive ID, you can also index it and give it a friendly name to allow
        for better searching. You can also use the optional archive description
        field to specify how the archive is referred to in an external index of
        archives, such as you might create in Amazon DynamoDB. You can also get
        the vault inventory to obtain a list of archive IDs in a vault. For more
        information, see InitiateJob.

        You must provide a SHA256 tree hash of the data you are uploading. For
        information about computing a SHA256 tree hash, see `Computing
        Checksums <https://docs.aws.amazon.com/amazonglacier/latest/dev/checksum-calculations.html>`__.

        You can optionally specify an archive description of up to 1,024
        printable ASCII characters. You can get the archive description when you
        either retrieve the archive or get the vault inventory. For more
        information, see InitiateJob. Amazon Glacier does not interpret the
        description in any way. An archive description does not need to be
        unique. You cannot use the description to retrieve or sort the archive
        list.

        Archives are immutable. After you upload an archive, you cannot edit the
        archive or its description.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Uploading an
        Archive in Amazon
        Glacier <https://docs.aws.amazon.com/amazonglacier/latest/dev/uploading-an-archive.html>`__
        and `Upload
        Archive <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-archive-post.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param vault_name: The name of the vault.
        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param archive_description: The optional description of the archive you are uploading.
        :param checksum: The SHA256 tree hash of the data being uploaded.
        :param body: The data to upload.
        :returns: ArchiveCreationOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises RequestTimeoutException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError

    @handler("UploadMultipartPart")
    def upload_multipart_part(
        self,
        context: RequestContext,
        account_id: string,
        vault_name: string,
        upload_id: string,
        checksum: string = None,
        range: string = None,
        body: Stream = None,
    ) -> UploadMultipartPartOutput:
        """This operation uploads a part of an archive. You can upload archive
        parts in any order. You can also upload them in parallel. You can upload
        up to 10,000 parts for a multipart upload.

        Amazon Glacier rejects your upload part request if any of the following
        conditions is true:

        -  **SHA256 tree hash does not match** To ensure that part data is not
           corrupted in transmission, you compute a SHA256 tree hash of the part
           and include it in your request. Upon receiving the part data, Amazon
           S3 Glacier also computes a SHA256 tree hash. If these hash values
           don't match, the operation fails. For information about computing a
           SHA256 tree hash, see `Computing
           Checksums <https://docs.aws.amazon.com/amazonglacier/latest/dev/checksum-calculations.html>`__.

        -  **Part size does not match** The size of each part except the last
           must match the size specified in the corresponding
           InitiateMultipartUpload request. The size of the last part must be
           the same size as, or smaller than, the specified size.

           If you upload a part whose size is smaller than the part size you
           specified in your initiate multipart upload request and that part is
           not the last part, then the upload part request will succeed.
           However, the subsequent Complete Multipart Upload request will fail.

        -  **Range does not align** The byte range value in the request does
           not align with the part size specified in the corresponding initiate
           request. For example, if you specify a part size of 4194304 bytes (4
           MB), then 0 to 4194303 bytes (4 MB - 1) and 4194304 (4 MB) to 8388607
           (8 MB - 1) are valid part ranges. However, if you set a range value
           of 2 MB to 6 MB, the range does not align with the part size and the
           upload will fail.

        This operation is idempotent. If you upload the same part multiple
        times, the data included in the most recent request overwrites the
        previously uploaded data.

        An AWS account has full permission to perform all operations (actions).
        However, AWS Identity and Access Management (IAM) users don't have any
        permissions by default. You must grant them explicit permission to
        perform specific actions. For more information, see `Access Control
        Using AWS Identity and Access Management
        (IAM) <https://docs.aws.amazon.com/amazonglacier/latest/dev/using-iam-with-amazon-glacier.html>`__.

        For conceptual information and underlying REST API, see `Uploading Large
        Archives in Parts (Multipart
        Upload) <https://docs.aws.amazon.com/amazonglacier/latest/dev/uploading-archive-mpu.html>`__
        and `Upload
        Part <https://docs.aws.amazon.com/amazonglacier/latest/dev/api-upload-part.html>`__
        in the *Amazon Glacier Developer Guide*.

        :param account_id: The ``AccountId`` value is the AWS account ID of the account that owns
        the vault.
        :param vault_name: The name of the vault.
        :param upload_id: The upload ID of the multipart upload.
        :param checksum: The SHA256 tree hash of the data being uploaded.
        :param range: Identifies the range of bytes in the assembled archive that will be
        uploaded in this part.
        :param body: The data to upload.
        :returns: UploadMultipartPartOutput
        :raises ResourceNotFoundException:
        :raises InvalidParameterValueException:
        :raises MissingParameterValueException:
        :raises RequestTimeoutException:
        :raises ServiceUnavailableException:
        """
        raise NotImplementedError
