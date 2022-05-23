import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Arn = str
Boolean = bool
DeletionProtection = bool
ErrorMessage = str
IonText = str
KmsKey = str
LedgerName = str
MaxResults = int
NextToken = str
ParameterName = str
ResourceName = str
ResourceType = str
S3Bucket = str
S3Prefix = str
StreamName = str
TagKey = str
TagValue = str
UniqueId = str


class EncryptionStatus(str):
    ENABLED = "ENABLED"
    UPDATING = "UPDATING"
    KMS_KEY_INACCESSIBLE = "KMS_KEY_INACCESSIBLE"


class ErrorCause(str):
    KINESIS_STREAM_NOT_FOUND = "KINESIS_STREAM_NOT_FOUND"
    IAM_PERMISSION_REVOKED = "IAM_PERMISSION_REVOKED"


class ExportStatus(str):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class LedgerState(str):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"
    DELETED = "DELETED"


class OutputFormat(str):
    ION_BINARY = "ION_BINARY"
    ION_TEXT = "ION_TEXT"
    JSON = "JSON"


class PermissionsMode(str):
    ALLOW_ALL = "ALLOW_ALL"
    STANDARD = "STANDARD"


class S3ObjectEncryptionType(str):
    SSE_KMS = "SSE_KMS"
    SSE_S3 = "SSE_S3"
    NO_ENCRYPTION = "NO_ENCRYPTION"


class StreamStatus(str):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    FAILED = "FAILED"
    IMPAIRED = "IMPAIRED"


class InvalidParameterException(ServiceException):
    """One or more parameters in the request aren't valid."""

    Message: Optional[ErrorMessage]
    ParameterName: Optional[ParameterName]


class LimitExceededException(ServiceException):
    """You have reached the limit on the maximum number of resources allowed."""

    Message: Optional[ErrorMessage]
    ResourceType: Optional[ResourceType]


class ResourceAlreadyExistsException(ServiceException):
    """The specified resource already exists."""

    Message: Optional[ErrorMessage]
    ResourceType: Optional[ResourceType]
    ResourceName: Optional[ResourceName]


class ResourceInUseException(ServiceException):
    """The specified resource can't be modified at this time."""

    Message: Optional[ErrorMessage]
    ResourceType: Optional[ResourceType]
    ResourceName: Optional[ResourceName]


class ResourceNotFoundException(ServiceException):
    """The specified resource doesn't exist."""

    Message: Optional[ErrorMessage]
    ResourceType: Optional[ResourceType]
    ResourceName: Optional[ResourceName]


class ResourcePreconditionNotMetException(ServiceException):
    """The operation failed because a condition wasn't satisfied in advance."""

    Message: Optional[ErrorMessage]
    ResourceType: Optional[ResourceType]
    ResourceName: Optional[ResourceName]


class CancelJournalKinesisStreamRequest(ServiceRequest):
    LedgerName: LedgerName
    StreamId: UniqueId


class CancelJournalKinesisStreamResponse(TypedDict, total=False):
    StreamId: Optional[UniqueId]


Tags = Dict[TagKey, TagValue]


class CreateLedgerRequest(ServiceRequest):
    Name: LedgerName
    Tags: Optional[Tags]
    PermissionsMode: PermissionsMode
    DeletionProtection: Optional[DeletionProtection]
    KmsKey: Optional[KmsKey]


Timestamp = datetime


class CreateLedgerResponse(TypedDict, total=False):
    Name: Optional[LedgerName]
    Arn: Optional[Arn]
    State: Optional[LedgerState]
    CreationDateTime: Optional[Timestamp]
    PermissionsMode: Optional[PermissionsMode]
    DeletionProtection: Optional[DeletionProtection]
    KmsKeyArn: Optional[Arn]


class DeleteLedgerRequest(ServiceRequest):
    Name: LedgerName


class DescribeJournalKinesisStreamRequest(ServiceRequest):
    LedgerName: LedgerName
    StreamId: UniqueId


class KinesisConfiguration(TypedDict, total=False):
    """The configuration settings of the Amazon Kinesis Data Streams
    destination for an Amazon QLDB journal stream.
    """

    StreamArn: Arn
    AggregationEnabled: Optional[Boolean]


class JournalKinesisStreamDescription(TypedDict, total=False):
    """Information about an Amazon QLDB journal stream, including the Amazon
    Resource Name (ARN), stream name, creation time, current status, and the
    parameters of the original stream creation request.
    """

    LedgerName: LedgerName
    CreationTime: Optional[Timestamp]
    InclusiveStartTime: Optional[Timestamp]
    ExclusiveEndTime: Optional[Timestamp]
    RoleArn: Arn
    StreamId: UniqueId
    Arn: Optional[Arn]
    Status: StreamStatus
    KinesisConfiguration: KinesisConfiguration
    ErrorCause: Optional[ErrorCause]
    StreamName: StreamName


class DescribeJournalKinesisStreamResponse(TypedDict, total=False):
    Stream: Optional[JournalKinesisStreamDescription]


class DescribeJournalS3ExportRequest(ServiceRequest):
    Name: LedgerName
    ExportId: UniqueId


class S3EncryptionConfiguration(TypedDict, total=False):
    """The encryption settings that are used by a journal export job to write
    data in an Amazon Simple Storage Service (Amazon S3) bucket.
    """

    ObjectEncryptionType: S3ObjectEncryptionType
    KmsKeyArn: Optional[Arn]


class S3ExportConfiguration(TypedDict, total=False):
    """The Amazon Simple Storage Service (Amazon S3) bucket location in which a
    journal export job writes the journal contents.
    """

    Bucket: S3Bucket
    Prefix: S3Prefix
    EncryptionConfiguration: S3EncryptionConfiguration


class JournalS3ExportDescription(TypedDict, total=False):
    """Information about a journal export job, including the ledger name,
    export ID, creation time, current status, and the parameters of the
    original export creation request.
    """

    LedgerName: LedgerName
    ExportId: UniqueId
    ExportCreationTime: Timestamp
    Status: ExportStatus
    InclusiveStartTime: Timestamp
    ExclusiveEndTime: Timestamp
    S3ExportConfiguration: S3ExportConfiguration
    RoleArn: Arn
    OutputFormat: Optional[OutputFormat]


class DescribeJournalS3ExportResponse(TypedDict, total=False):
    ExportDescription: JournalS3ExportDescription


class DescribeLedgerRequest(ServiceRequest):
    Name: LedgerName


class LedgerEncryptionDescription(TypedDict, total=False):
    """Information about the encryption of data at rest in an Amazon QLDB
    ledger. This includes the current status, the key in Key Management
    Service (KMS), and when the key became inaccessible (in the case of an
    error).

    For more information, see `Encryption at
    rest <https://docs.aws.amazon.com/qldb/latest/developerguide/encryption-at-rest.html>`__
    in the *Amazon QLDB Developer Guide*.
    """

    KmsKeyArn: Arn
    EncryptionStatus: EncryptionStatus
    InaccessibleKmsKeyDateTime: Optional[Timestamp]


class DescribeLedgerResponse(TypedDict, total=False):
    Name: Optional[LedgerName]
    Arn: Optional[Arn]
    State: Optional[LedgerState]
    CreationDateTime: Optional[Timestamp]
    PermissionsMode: Optional[PermissionsMode]
    DeletionProtection: Optional[DeletionProtection]
    EncryptionDescription: Optional[LedgerEncryptionDescription]


Digest = bytes


class ExportJournalToS3Request(ServiceRequest):
    Name: LedgerName
    InclusiveStartTime: Timestamp
    ExclusiveEndTime: Timestamp
    S3ExportConfiguration: S3ExportConfiguration
    RoleArn: Arn
    OutputFormat: Optional[OutputFormat]


class ExportJournalToS3Response(TypedDict, total=False):
    ExportId: UniqueId


class ValueHolder(TypedDict, total=False):
    """A structure that can contain a value in multiple encoding formats."""

    IonText: Optional[IonText]


class GetBlockRequest(ServiceRequest):
    Name: LedgerName
    BlockAddress: ValueHolder
    DigestTipAddress: Optional[ValueHolder]


class GetBlockResponse(TypedDict, total=False):
    Block: ValueHolder
    Proof: Optional[ValueHolder]


class GetDigestRequest(ServiceRequest):
    Name: LedgerName


class GetDigestResponse(TypedDict, total=False):
    Digest: Digest
    DigestTipAddress: ValueHolder


class GetRevisionRequest(ServiceRequest):
    Name: LedgerName
    BlockAddress: ValueHolder
    DocumentId: UniqueId
    DigestTipAddress: Optional[ValueHolder]


class GetRevisionResponse(TypedDict, total=False):
    Proof: Optional[ValueHolder]
    Revision: ValueHolder


JournalKinesisStreamDescriptionList = List[JournalKinesisStreamDescription]
JournalS3ExportList = List[JournalS3ExportDescription]


class LedgerSummary(TypedDict, total=False):
    """Information about a ledger, including its name, state, and when it was
    created.
    """

    Name: Optional[LedgerName]
    State: Optional[LedgerState]
    CreationDateTime: Optional[Timestamp]


LedgerList = List[LedgerSummary]


class ListJournalKinesisStreamsForLedgerRequest(ServiceRequest):
    LedgerName: LedgerName
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListJournalKinesisStreamsForLedgerResponse(TypedDict, total=False):
    Streams: Optional[JournalKinesisStreamDescriptionList]
    NextToken: Optional[NextToken]


class ListJournalS3ExportsForLedgerRequest(ServiceRequest):
    Name: LedgerName
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListJournalS3ExportsForLedgerResponse(TypedDict, total=False):
    JournalS3Exports: Optional[JournalS3ExportList]
    NextToken: Optional[NextToken]


class ListJournalS3ExportsRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListJournalS3ExportsResponse(TypedDict, total=False):
    JournalS3Exports: Optional[JournalS3ExportList]
    NextToken: Optional[NextToken]


class ListLedgersRequest(ServiceRequest):
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class ListLedgersResponse(TypedDict, total=False):
    Ledgers: Optional[LedgerList]
    NextToken: Optional[NextToken]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceArn: Arn


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: Optional[Tags]


class StreamJournalToKinesisRequest(ServiceRequest):
    LedgerName: LedgerName
    RoleArn: Arn
    Tags: Optional[Tags]
    InclusiveStartTime: Timestamp
    ExclusiveEndTime: Optional[Timestamp]
    KinesisConfiguration: KinesisConfiguration
    StreamName: StreamName


class StreamJournalToKinesisResponse(TypedDict, total=False):
    StreamId: Optional[UniqueId]


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    ResourceArn: Arn
    Tags: Tags


class TagResourceResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    ResourceArn: Arn
    TagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateLedgerPermissionsModeRequest(ServiceRequest):
    Name: LedgerName
    PermissionsMode: PermissionsMode


class UpdateLedgerPermissionsModeResponse(TypedDict, total=False):
    Name: Optional[LedgerName]
    Arn: Optional[Arn]
    PermissionsMode: Optional[PermissionsMode]


class UpdateLedgerRequest(ServiceRequest):
    Name: LedgerName
    DeletionProtection: Optional[DeletionProtection]
    KmsKey: Optional[KmsKey]


class UpdateLedgerResponse(TypedDict, total=False):
    Name: Optional[LedgerName]
    Arn: Optional[Arn]
    State: Optional[LedgerState]
    CreationDateTime: Optional[Timestamp]
    DeletionProtection: Optional[DeletionProtection]
    EncryptionDescription: Optional[LedgerEncryptionDescription]


class QldbApi:

    service = "qldb"
    version = "2019-01-02"

    @handler("CancelJournalKinesisStream")
    def cancel_journal_kinesis_stream(
        self, context: RequestContext, ledger_name: LedgerName, stream_id: UniqueId
    ) -> CancelJournalKinesisStreamResponse:
        """Ends a given Amazon QLDB journal stream. Before a stream can be
        canceled, its current status must be ``ACTIVE``.

        You can't restart a stream after you cancel it. Canceled QLDB stream
        resources are subject to a 7-day retention period, so they are
        automatically deleted after this limit expires.

        :param ledger_name: The name of the ledger.
        :param stream_id: The UUID (represented in Base62-encoded text) of the QLDB journal stream
        to be canceled.
        :returns: CancelJournalKinesisStreamResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ResourcePreconditionNotMetException:
        """
        raise NotImplementedError

    @handler("CreateLedger")
    def create_ledger(
        self,
        context: RequestContext,
        name: LedgerName,
        permissions_mode: PermissionsMode,
        tags: Tags = None,
        deletion_protection: DeletionProtection = None,
        kms_key: KmsKey = None,
    ) -> CreateLedgerResponse:
        """Creates a new ledger in your Amazon Web Services account in the current
        Region.

        :param name: The name of the ledger that you want to create.
        :param permissions_mode: The permissions mode to assign to the ledger that you want to create.
        :param tags: The key-value pairs to add as tags to the ledger that you want to
        create.
        :param deletion_protection: The flag that prevents a ledger from being deleted by any user.
        :param kms_key: The key in Key Management Service (KMS) to use for encryption of data at
        rest in the ledger.
        :returns: CreateLedgerResponse
        :raises InvalidParameterException:
        :raises ResourceAlreadyExistsException:
        :raises LimitExceededException:
        :raises ResourceInUseException:
        """
        raise NotImplementedError

    @handler("DeleteLedger")
    def delete_ledger(self, context: RequestContext, name: LedgerName) -> None:
        """Deletes a ledger and all of its contents. This action is irreversible.

        If deletion protection is enabled, you must first disable it before you
        can delete the ledger. You can disable it by calling the
        ``UpdateLedger`` operation to set the flag to ``false``.

        :param name: The name of the ledger that you want to delete.
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ResourceInUseException:
        :raises ResourcePreconditionNotMetException:
        """
        raise NotImplementedError

    @handler("DescribeJournalKinesisStream")
    def describe_journal_kinesis_stream(
        self, context: RequestContext, ledger_name: LedgerName, stream_id: UniqueId
    ) -> DescribeJournalKinesisStreamResponse:
        """Returns detailed information about a given Amazon QLDB journal stream.
        The output includes the Amazon Resource Name (ARN), stream name, current
        status, creation time, and the parameters of the original stream
        creation request.

        This action does not return any expired journal streams. For more
        information, see `Expiration for terminal
        streams <https://docs.aws.amazon.com/qldb/latest/developerguide/streams.create.html#streams.create.states.expiration>`__
        in the *Amazon QLDB Developer Guide*.

        :param ledger_name: The name of the ledger.
        :param stream_id: The UUID (represented in Base62-encoded text) of the QLDB journal stream
        to describe.
        :returns: DescribeJournalKinesisStreamResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ResourcePreconditionNotMetException:
        """
        raise NotImplementedError

    @handler("DescribeJournalS3Export")
    def describe_journal_s3_export(
        self, context: RequestContext, name: LedgerName, export_id: UniqueId
    ) -> DescribeJournalS3ExportResponse:
        """Returns information about a journal export job, including the ledger
        name, export ID, creation time, current status, and the parameters of
        the original export creation request.

        This action does not return any expired export jobs. For more
        information, see `Export job
        expiration <https://docs.aws.amazon.com/qldb/latest/developerguide/export-journal.request.html#export-journal.request.expiration>`__
        in the *Amazon QLDB Developer Guide*.

        If the export job with the given ``ExportId`` doesn't exist, then throws
        ``ResourceNotFoundException``.

        If the ledger with the given ``Name`` doesn't exist, then throws
        ``ResourceNotFoundException``.

        :param name: The name of the ledger.
        :param export_id: The UUID (represented in Base62-encoded text) of the journal export job
        to describe.
        :returns: DescribeJournalS3ExportResponse
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("DescribeLedger")
    def describe_ledger(self, context: RequestContext, name: LedgerName) -> DescribeLedgerResponse:
        """Returns information about a ledger, including its state, permissions
        mode, encryption at rest settings, and when it was created.

        :param name: The name of the ledger that you want to describe.
        :returns: DescribeLedgerResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ExportJournalToS3")
    def export_journal_to_s3(
        self,
        context: RequestContext,
        name: LedgerName,
        inclusive_start_time: Timestamp,
        exclusive_end_time: Timestamp,
        s3_export_configuration: S3ExportConfiguration,
        role_arn: Arn,
        output_format: OutputFormat = None,
    ) -> ExportJournalToS3Response:
        """Exports journal contents within a date and time range from a ledger into
        a specified Amazon Simple Storage Service (Amazon S3) bucket. A journal
        export job can write the data objects in either the text or binary
        representation of Amazon Ion format, or in *JSON Lines* text format.

        In JSON Lines format, each journal block in the exported data object is
        a valid JSON object that is delimited by a newline. You can use this
        format to easily integrate JSON exports with analytics tools such as
        Glue and Amazon Athena because these services can parse
        newline-delimited JSON automatically. For more information about the
        format, see `JSON Lines <https://jsonlines.org/>`__.

        If the ledger with the given ``Name`` doesn't exist, then throws
        ``ResourceNotFoundException``.

        If the ledger with the given ``Name`` is in ``CREATING`` status, then
        throws ``ResourcePreconditionNotMetException``.

        You can initiate up to two concurrent journal export requests for each
        ledger. Beyond this limit, journal export requests throw
        ``LimitExceededException``.

        :param name: The name of the ledger.
        :param inclusive_start_time: The inclusive start date and time for the range of journal contents to
        export.
        :param exclusive_end_time: The exclusive end date and time for the range of journal contents to
        export.
        :param s3_export_configuration: The configuration settings of the Amazon S3 bucket destination for your
        export request.
        :param role_arn: The Amazon Resource Name (ARN) of the IAM role that grants QLDB
        permissions for a journal export job to do the following:

        -  Write objects into your Amazon Simple Storage Service (Amazon S3)
           bucket.
        :param output_format: The output format of your exported journal data.
        :returns: ExportJournalToS3Response
        :raises ResourceNotFoundException:
        :raises ResourcePreconditionNotMetException:
        """
        raise NotImplementedError

    @handler("GetBlock")
    def get_block(
        self,
        context: RequestContext,
        name: LedgerName,
        block_address: ValueHolder,
        digest_tip_address: ValueHolder = None,
    ) -> GetBlockResponse:
        """Returns a block object at a specified address in a journal. Also returns
        a proof of the specified block for verification if ``DigestTipAddress``
        is provided.

        For information about the data contents in a block, see `Journal
        contents <https://docs.aws.amazon.com/qldb/latest/developerguide/journal-contents.html>`__
        in the *Amazon QLDB Developer Guide*.

        If the specified ledger doesn't exist or is in ``DELETING`` status, then
        throws ``ResourceNotFoundException``.

        If the specified ledger is in ``CREATING`` status, then throws
        ``ResourcePreconditionNotMetException``.

        If no block exists with the specified address, then throws
        ``InvalidParameterException``.

        :param name: The name of the ledger.
        :param block_address: The location of the block that you want to request.
        :param digest_tip_address: The latest block location covered by the digest for which to request a
        proof.
        :returns: GetBlockResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ResourcePreconditionNotMetException:
        """
        raise NotImplementedError

    @handler("GetDigest")
    def get_digest(self, context: RequestContext, name: LedgerName) -> GetDigestResponse:
        """Returns the digest of a ledger at the latest committed block in the
        journal. The response includes a 256-bit hash value and a block address.

        :param name: The name of the ledger.
        :returns: GetDigestResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ResourcePreconditionNotMetException:
        """
        raise NotImplementedError

    @handler("GetRevision")
    def get_revision(
        self,
        context: RequestContext,
        name: LedgerName,
        block_address: ValueHolder,
        document_id: UniqueId,
        digest_tip_address: ValueHolder = None,
    ) -> GetRevisionResponse:
        """Returns a revision data object for a specified document ID and block
        address. Also returns a proof of the specified revision for verification
        if ``DigestTipAddress`` is provided.

        :param name: The name of the ledger.
        :param block_address: The block location of the document revision to be verified.
        :param document_id: The UUID (represented in Base62-encoded text) of the document to be
        verified.
        :param digest_tip_address: The latest block location covered by the digest for which to request a
        proof.
        :returns: GetRevisionResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ResourcePreconditionNotMetException:
        """
        raise NotImplementedError

    @handler("ListJournalKinesisStreamsForLedger")
    def list_journal_kinesis_streams_for_ledger(
        self,
        context: RequestContext,
        ledger_name: LedgerName,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListJournalKinesisStreamsForLedgerResponse:
        """Returns an array of all Amazon QLDB journal stream descriptors for a
        given ledger. The output of each stream descriptor includes the same
        details that are returned by ``DescribeJournalKinesisStream``.

        This action does not return any expired journal streams. For more
        information, see `Expiration for terminal
        streams <https://docs.aws.amazon.com/qldb/latest/developerguide/streams.create.html#streams.create.states.expiration>`__
        in the *Amazon QLDB Developer Guide*.

        This action returns a maximum of ``MaxResults`` items. It is paginated
        so that you can retrieve all the items by calling
        ``ListJournalKinesisStreamsForLedger`` multiple times.

        :param ledger_name: The name of the ledger.
        :param max_results: The maximum number of results to return in a single
        ``ListJournalKinesisStreamsForLedger`` request.
        :param next_token: A pagination token, indicating that you want to retrieve the next page
        of results.
        :returns: ListJournalKinesisStreamsForLedgerResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ResourcePreconditionNotMetException:
        """
        raise NotImplementedError

    @handler("ListJournalS3Exports")
    def list_journal_s3_exports(
        self, context: RequestContext, max_results: MaxResults = None, next_token: NextToken = None
    ) -> ListJournalS3ExportsResponse:
        """Returns an array of journal export job descriptions for all ledgers that
        are associated with the current Amazon Web Services account and Region.

        This action returns a maximum of ``MaxResults`` items, and is paginated
        so that you can retrieve all the items by calling
        ``ListJournalS3Exports`` multiple times.

        This action does not return any expired export jobs. For more
        information, see `Export job
        expiration <https://docs.aws.amazon.com/qldb/latest/developerguide/export-journal.request.html#export-journal.request.expiration>`__
        in the *Amazon QLDB Developer Guide*.

        :param max_results: The maximum number of results to return in a single
        ``ListJournalS3Exports`` request.
        :param next_token: A pagination token, indicating that you want to retrieve the next page
        of results.
        :returns: ListJournalS3ExportsResponse
        """
        raise NotImplementedError

    @handler("ListJournalS3ExportsForLedger")
    def list_journal_s3_exports_for_ledger(
        self,
        context: RequestContext,
        name: LedgerName,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> ListJournalS3ExportsForLedgerResponse:
        """Returns an array of journal export job descriptions for a specified
        ledger.

        This action returns a maximum of ``MaxResults`` items, and is paginated
        so that you can retrieve all the items by calling
        ``ListJournalS3ExportsForLedger`` multiple times.

        This action does not return any expired export jobs. For more
        information, see `Export job
        expiration <https://docs.aws.amazon.com/qldb/latest/developerguide/export-journal.request.html#export-journal.request.expiration>`__
        in the *Amazon QLDB Developer Guide*.

        :param name: The name of the ledger.
        :param max_results: The maximum number of results to return in a single
        ``ListJournalS3ExportsForLedger`` request.
        :param next_token: A pagination token, indicating that you want to retrieve the next page
        of results.
        :returns: ListJournalS3ExportsForLedgerResponse
        """
        raise NotImplementedError

    @handler("ListLedgers")
    def list_ledgers(
        self, context: RequestContext, max_results: MaxResults = None, next_token: NextToken = None
    ) -> ListLedgersResponse:
        """Returns an array of ledger summaries that are associated with the
        current Amazon Web Services account and Region.

        This action returns a maximum of 100 items and is paginated so that you
        can retrieve all the items by calling ``ListLedgers`` multiple times.

        :param max_results: The maximum number of results to return in a single ``ListLedgers``
        request.
        :param next_token: A pagination token, indicating that you want to retrieve the next page
        of results.
        :returns: ListLedgersResponse
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: Arn
    ) -> ListTagsForResourceResponse:
        """Returns all tags for a specified Amazon QLDB resource.

        :param resource_arn: The Amazon Resource Name (ARN) for which to list the tags.
        :returns: ListTagsForResourceResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("StreamJournalToKinesis")
    def stream_journal_to_kinesis(
        self,
        context: RequestContext,
        ledger_name: LedgerName,
        role_arn: Arn,
        inclusive_start_time: Timestamp,
        kinesis_configuration: KinesisConfiguration,
        stream_name: StreamName,
        tags: Tags = None,
        exclusive_end_time: Timestamp = None,
    ) -> StreamJournalToKinesisResponse:
        """Creates a journal stream for a given Amazon QLDB ledger. The stream
        captures every document revision that is committed to the ledger's
        journal and delivers the data to a specified Amazon Kinesis Data Streams
        resource.

        :param ledger_name: The name of the ledger.
        :param role_arn: The Amazon Resource Name (ARN) of the IAM role that grants QLDB
        permissions for a journal stream to write data records to a Kinesis Data
        Streams resource.
        :param inclusive_start_time: The inclusive start date and time from which to start streaming journal
        data.
        :param kinesis_configuration: The configuration settings of the Kinesis Data Streams destination for
        your stream request.
        :param stream_name: The name that you want to assign to the QLDB journal stream.
        :param tags: The key-value pairs to add as tags to the stream that you want to
        create.
        :param exclusive_end_time: The exclusive date and time that specifies when the stream ends.
        :returns: StreamJournalToKinesisResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        :raises ResourcePreconditionNotMetException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: Arn, tags: Tags
    ) -> TagResourceResponse:
        """Adds one or more tags to a specified Amazon QLDB resource.

        A resource can have up to 50 tags. If you try to create more than 50
        tags for a resource, your request fails and returns an error.

        :param resource_arn: The Amazon Resource Name (ARN) to which you want to add the tags.
        :param tags: The key-value pairs to add as tags to the specified QLDB resource.
        :returns: TagResourceResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: Arn, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Removes one or more tags from a specified Amazon QLDB resource. You can
        specify up to 50 tag keys to remove.

        :param resource_arn: The Amazon Resource Name (ARN) from which to remove the tags.
        :param tag_keys: The list of tag keys to remove.
        :returns: UntagResourceResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateLedger")
    def update_ledger(
        self,
        context: RequestContext,
        name: LedgerName,
        deletion_protection: DeletionProtection = None,
        kms_key: KmsKey = None,
    ) -> UpdateLedgerResponse:
        """Updates properties on a ledger.

        :param name: The name of the ledger.
        :param deletion_protection: The flag that prevents a ledger from being deleted by any user.
        :param kms_key: The key in Key Management Service (KMS) to use for encryption of data at
        rest in the ledger.
        :returns: UpdateLedgerResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateLedgerPermissionsMode")
    def update_ledger_permissions_mode(
        self, context: RequestContext, name: LedgerName, permissions_mode: PermissionsMode
    ) -> UpdateLedgerPermissionsModeResponse:
        """Updates the permissions mode of a ledger.

        Before you switch to the ``STANDARD`` permissions mode, you must first
        create all required IAM policies and table tags to avoid disruption to
        your users. To learn more, see `Migrating to the standard permissions
        mode <https://docs.aws.amazon.com/qldb/latest/developerguide/ledger-management.basics.html#ledger-mgmt.basics.update-permissions.migrating>`__
        in the *Amazon QLDB Developer Guide*.

        :param name: The name of the ledger.
        :param permissions_mode: The permissions mode to assign to the ledger.
        :returns: UpdateLedgerPermissionsModeResponse
        :raises InvalidParameterException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError
