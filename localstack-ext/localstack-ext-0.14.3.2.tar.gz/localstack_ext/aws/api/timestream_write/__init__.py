import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AmazonResourceName = str
Boolean = bool
ErrorMessage = str
Integer = int
PaginationLimit = int
RecordIndex = int
ResourceCreateAPIName = str
ResourceName = str
S3BucketName = str
S3ObjectKeyPrefix = str
SchemaName = str
SchemaValue = str
String = str
StringValue2048 = str
StringValue256 = str
TagKey = str
TagValue = str


class DimensionValueType(str):
    VARCHAR = "VARCHAR"


class MeasureValueType(str):
    DOUBLE = "DOUBLE"
    BIGINT = "BIGINT"
    VARCHAR = "VARCHAR"
    BOOLEAN = "BOOLEAN"
    TIMESTAMP = "TIMESTAMP"
    MULTI = "MULTI"


class S3EncryptionOption(str):
    SSE_S3 = "SSE_S3"
    SSE_KMS = "SSE_KMS"


class TableStatus(str):
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"


class TimeUnit(str):
    MILLISECONDS = "MILLISECONDS"
    SECONDS = "SECONDS"
    MICROSECONDS = "MICROSECONDS"
    NANOSECONDS = "NANOSECONDS"


class AccessDeniedException(ServiceException):
    """You are not authorized to perform this action."""

    Message: ErrorMessage


class ConflictException(ServiceException):
    """Timestream was unable to process this request because it contains
    resource that already exists.
    """

    Message: ErrorMessage


class InternalServerException(ServiceException):
    """Timestream was unable to fully process this request because of an
    internal server error.
    """

    Message: ErrorMessage


class InvalidEndpointException(ServiceException):
    """The requested endpoint was invalid."""

    Message: Optional[ErrorMessage]


RecordVersion = int


class RejectedRecord(TypedDict, total=False):
    """Records that were not successfully inserted into Timestream due to data
    validation issues that must be resolved prior to reinserting time series
    data into the system.
    """

    RecordIndex: Optional[RecordIndex]
    Reason: Optional[ErrorMessage]
    ExistingVersion: Optional[RecordVersion]


RejectedRecords = List[RejectedRecord]


class RejectedRecordsException(ServiceException):
    """WriteRecords would throw this exception in the following cases:

    -  Records with duplicate data where there are multiple records with the
       same dimensions, timestamps, and measure names but:

       -  Measure values are different

       -  Version is not present in the request *or* the value of version in
          the new record is equal to or lower than the existing value

       In this case, if Timestream rejects data, the ``ExistingVersion``
       field in the ``RejectedRecords`` response will indicate the current
       record’s version. To force an update, you can resend the request with
       a version for the record set to a value greater than the
       ``ExistingVersion``.

    -  Records with timestamps that lie outside the retention duration of
       the memory store

    -  Records with dimensions or measures that exceed the Timestream
       defined limits.

    For more information, see
    `Quotas <https://docs.aws.amazon.com/timestream/latest/developerguide/ts-limits.html>`__
    in the Timestream Developer Guide.
    """

    Message: Optional[ErrorMessage]
    RejectedRecords: Optional[RejectedRecords]


class ResourceNotFoundException(ServiceException):
    """The operation tried to access a nonexistent resource. The resource might
    not be specified correctly, or its status might not be ACTIVE.
    """

    Message: Optional[ErrorMessage]


class ServiceQuotaExceededException(ServiceException):
    """Instance quota of resource exceeded for this account."""

    Message: Optional[ErrorMessage]


class ThrottlingException(ServiceException):
    """Too many requests were made by a user exceeding service quotas. The
    request was throttled.
    """

    Message: ErrorMessage


class ValidationException(ServiceException):
    """Invalid or malformed request."""

    Message: ErrorMessage


class Tag(TypedDict, total=False):
    """A tag is a label that you assign to a Timestream database and/or table.
    Each tag consists of a key and an optional value, both of which you
    define. Tags enable you to categorize databases and/or tables, for
    example, by purpose, owner, or environment.
    """

    Key: TagKey
    Value: TagValue


TagList = List[Tag]


class CreateDatabaseRequest(ServiceRequest):
    DatabaseName: ResourceCreateAPIName
    KmsKeyId: Optional[StringValue2048]
    Tags: Optional[TagList]


Date = datetime
Long = int


class Database(TypedDict, total=False):
    """A top level container for a table. Databases and tables are the
    fundamental management concepts in Amazon Timestream. All tables in a
    database are encrypted with the same KMS key.
    """

    Arn: Optional[String]
    DatabaseName: Optional[ResourceName]
    TableCount: Optional[Long]
    KmsKeyId: Optional[StringValue2048]
    CreationTime: Optional[Date]
    LastUpdatedTime: Optional[Date]


class CreateDatabaseResponse(TypedDict, total=False):
    Database: Optional[Database]


class S3Configuration(TypedDict, total=False):
    """Configuration specifing an S3 location."""

    BucketName: Optional[S3BucketName]
    ObjectKeyPrefix: Optional[S3ObjectKeyPrefix]
    EncryptionOption: Optional[S3EncryptionOption]
    KmsKeyId: Optional[StringValue2048]


class MagneticStoreRejectedDataLocation(TypedDict, total=False):
    """The location to write error reports for records rejected,
    asynchronously, during magnetic store writes.
    """

    S3Configuration: Optional[S3Configuration]


class MagneticStoreWriteProperties(TypedDict, total=False):
    """The set of properties on a table for configuring magnetic store writes."""

    EnableMagneticStoreWrites: Boolean
    MagneticStoreRejectedDataLocation: Optional[MagneticStoreRejectedDataLocation]


MagneticStoreRetentionPeriodInDays = int
MemoryStoreRetentionPeriodInHours = int


class RetentionProperties(TypedDict, total=False):
    """Retention properties contain the duration for which your time series
    data must be stored in the magnetic store and the memory store.
    """

    MemoryStoreRetentionPeriodInHours: MemoryStoreRetentionPeriodInHours
    MagneticStoreRetentionPeriodInDays: MagneticStoreRetentionPeriodInDays


class CreateTableRequest(ServiceRequest):
    DatabaseName: ResourceCreateAPIName
    TableName: ResourceCreateAPIName
    RetentionProperties: Optional[RetentionProperties]
    Tags: Optional[TagList]
    MagneticStoreWriteProperties: Optional[MagneticStoreWriteProperties]


class Table(TypedDict, total=False):
    """Table represents a database table in Timestream. Tables contain one or
    more related time series. You can modify the retention duration of the
    memory store and the magnetic store for a table.
    """

    Arn: Optional[String]
    TableName: Optional[ResourceName]
    DatabaseName: Optional[ResourceName]
    TableStatus: Optional[TableStatus]
    RetentionProperties: Optional[RetentionProperties]
    CreationTime: Optional[Date]
    LastUpdatedTime: Optional[Date]
    MagneticStoreWriteProperties: Optional[MagneticStoreWriteProperties]


class CreateTableResponse(TypedDict, total=False):
    Table: Optional[Table]


DatabaseList = List[Database]


class DeleteDatabaseRequest(ServiceRequest):
    DatabaseName: ResourceName


class DeleteTableRequest(ServiceRequest):
    DatabaseName: ResourceName
    TableName: ResourceName


class DescribeDatabaseRequest(ServiceRequest):
    DatabaseName: ResourceName


class DescribeDatabaseResponse(TypedDict, total=False):
    Database: Optional[Database]


class DescribeEndpointsRequest(ServiceRequest):
    pass


class Endpoint(TypedDict, total=False):
    """Represents an available endpoint against which to make API calls
    agaisnt, as well as the TTL for that endpoint.
    """

    Address: String
    CachePeriodInMinutes: Long


Endpoints = List[Endpoint]


class DescribeEndpointsResponse(TypedDict, total=False):
    Endpoints: Endpoints


class DescribeTableRequest(ServiceRequest):
    DatabaseName: ResourceName
    TableName: ResourceName


class DescribeTableResponse(TypedDict, total=False):
    Table: Optional[Table]


class Dimension(TypedDict, total=False):
    """Dimension represents the meta data attributes of the time series. For
    example, the name and availability zone of an EC2 instance or the name
    of the manufacturer of a wind turbine are dimensions.
    """

    Name: SchemaName
    Value: SchemaValue
    DimensionValueType: Optional[DimensionValueType]


Dimensions = List[Dimension]


class ListDatabasesRequest(ServiceRequest):
    NextToken: Optional[String]
    MaxResults: Optional[PaginationLimit]


class ListDatabasesResponse(TypedDict, total=False):
    Databases: Optional[DatabaseList]
    NextToken: Optional[String]


class ListTablesRequest(ServiceRequest):
    DatabaseName: Optional[ResourceName]
    NextToken: Optional[String]
    MaxResults: Optional[PaginationLimit]


TableList = List[Table]


class ListTablesResponse(TypedDict, total=False):
    Tables: Optional[TableList]
    NextToken: Optional[String]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceARN: AmazonResourceName


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: Optional[TagList]


class MeasureValue(TypedDict, total=False):
    """MeasureValue represents the data attribute of the time series. For
    example, the CPU utilization of an EC2 instance or the RPM of a wind
    turbine are measures. MeasureValue has both name and value.

    MeasureValue is only allowed for type ``MULTI``. Using ``MULTI`` type,
    you can pass multiple data attributes associated with the same time
    series in a single record
    """

    Name: SchemaName
    Value: StringValue2048
    Type: MeasureValueType


MeasureValues = List[MeasureValue]


class Record(TypedDict, total=False):
    """Record represents a time series data point being written into
    Timestream. Each record contains an array of dimensions. Dimensions
    represent the meta data attributes of a time series data point such as
    the instance name or availability zone of an EC2 instance. A record also
    contains the measure name which is the name of the measure being
    collected for example the CPU utilization of an EC2 instance. A record
    also contains the measure value and the value type which is the data
    type of the measure value. In addition, the record contains the
    timestamp when the measure was collected that the timestamp unit which
    represents the granularity of the timestamp.

    Records have a ``Version`` field, which is a 64-bit ``long`` that you
    can use for updating data points. Writes of a duplicate record with the
    same dimension, timestamp, and measure name but different measure value
    will only succeed if the ``Version`` attribute of the record in the
    write request is higher than that of the existing record. Timestream
    defaults to a ``Version`` of ``1`` for records without the ``Version``
    field.
    """

    Dimensions: Optional[Dimensions]
    MeasureName: Optional[SchemaName]
    MeasureValue: Optional[StringValue2048]
    MeasureValueType: Optional[MeasureValueType]
    Time: Optional[StringValue256]
    TimeUnit: Optional[TimeUnit]
    Version: Optional[RecordVersion]
    MeasureValues: Optional[MeasureValues]


Records = List[Record]


class RecordsIngested(TypedDict, total=False):
    """Information on the records ingested by this request."""

    Total: Optional[Integer]
    MemoryStore: Optional[Integer]
    MagneticStore: Optional[Integer]


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    ResourceARN: AmazonResourceName
    Tags: TagList


class TagResourceResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    ResourceARN: AmazonResourceName
    TagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateDatabaseRequest(ServiceRequest):
    DatabaseName: ResourceName
    KmsKeyId: StringValue2048


class UpdateDatabaseResponse(TypedDict, total=False):
    Database: Optional[Database]


class UpdateTableRequest(ServiceRequest):
    DatabaseName: ResourceName
    TableName: ResourceName
    RetentionProperties: Optional[RetentionProperties]
    MagneticStoreWriteProperties: Optional[MagneticStoreWriteProperties]


class UpdateTableResponse(TypedDict, total=False):
    Table: Optional[Table]


class WriteRecordsRequest(ServiceRequest):
    DatabaseName: ResourceName
    TableName: ResourceName
    CommonAttributes: Optional[Record]
    Records: Records


class WriteRecordsResponse(TypedDict, total=False):
    RecordsIngested: Optional[RecordsIngested]


class TimestreamWriteApi:

    service = "timestream-write"
    version = "2018-11-01"

    @handler("CreateDatabase")
    def create_database(
        self,
        context: RequestContext,
        database_name: ResourceCreateAPIName,
        kms_key_id: StringValue2048 = None,
        tags: TagList = None,
    ) -> CreateDatabaseResponse:
        """Creates a new Timestream database. If the KMS key is not specified, the
        database will be encrypted with a Timestream managed KMS key located in
        your account. Refer to `Amazon Web Services managed KMS
        keys <https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#aws-managed-cmk>`__
        for more info. `Service quotas
        apply <https://docs.aws.amazon.com/timestream/latest/developerguide/ts-limits.html>`__.
        See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.create-db.html>`__
        for details.

        :param database_name: The name of the Timestream database.
        :param kms_key_id: The KMS key for the database.
        :param tags: A list of key-value pairs to label the table.
        :returns: CreateDatabaseResponse
        :raises ConflictException:
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ServiceQuotaExceededException:
        :raises ThrottlingException:
        :raises InvalidEndpointException:
        :raises InternalServerException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("CreateTable")
    def create_table(
        self,
        context: RequestContext,
        database_name: ResourceCreateAPIName,
        table_name: ResourceCreateAPIName,
        retention_properties: RetentionProperties = None,
        tags: TagList = None,
        magnetic_store_write_properties: MagneticStoreWriteProperties = None,
    ) -> CreateTableResponse:
        """The CreateTable operation adds a new table to an existing database in
        your account. In an Amazon Web Services account, table names must be at
        least unique within each Region if they are in the same database. You
        may have identical table names in the same Region if the tables are in
        separate databases. While creating the table, you must specify the table
        name, database name, and the retention properties. `Service quotas
        apply <https://docs.aws.amazon.com/timestream/latest/developerguide/ts-limits.html>`__.
        See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.create-table.html>`__
        for details.

        :param database_name: The name of the Timestream database.
        :param table_name: The name of the Timestream table.
        :param retention_properties: The duration for which your time series data must be stored in the
        memory store and the magnetic store.
        :param tags: A list of key-value pairs to label the table.
        :param magnetic_store_write_properties: Contains properties to set on the table when enabling magnetic store
        writes.
        :returns: CreateTableResponse
        :raises ConflictException:
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ServiceQuotaExceededException:
        :raises ThrottlingException:
        :raises InvalidEndpointException:
        :raises InternalServerException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("DeleteDatabase")
    def delete_database(self, context: RequestContext, database_name: ResourceName) -> None:
        """Deletes a given Timestream database. *This is an irreversible operation.
        After a database is deleted, the time series data from its tables cannot
        be recovered.*

        All tables in the database must be deleted first, or a
        ValidationException error will be thrown.

        Due to the nature of distributed retries, the operation can return
        either success or a ResourceNotFoundException. Clients should consider
        them equivalent.

        See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.delete-db.html>`__
        for details.

        :param database_name: The name of the Timestream database to be deleted.
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("DeleteTable")
    def delete_table(
        self, context: RequestContext, database_name: ResourceName, table_name: ResourceName
    ) -> None:
        """Deletes a given Timestream table. This is an irreversible operation.
        After a Timestream database table is deleted, the time series data
        stored in the table cannot be recovered.

        Due to the nature of distributed retries, the operation can return
        either success or a ResourceNotFoundException. Clients should consider
        them equivalent.

        See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.delete-table.html>`__
        for details.

        :param database_name: The name of the database where the Timestream database is to be deleted.
        :param table_name: The name of the Timestream table to be deleted.
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("DescribeDatabase")
    def describe_database(
        self, context: RequestContext, database_name: ResourceName
    ) -> DescribeDatabaseResponse:
        """Returns information about the database, including the database name,
        time that the database was created, and the total number of tables found
        within the database. `Service quotas
        apply <https://docs.aws.amazon.com/timestream/latest/developerguide/ts-limits.html>`__.
        See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.describe-db.html>`__
        for details.

        :param database_name: The name of the Timestream database.
        :returns: DescribeDatabaseResponse
        :raises ResourceNotFoundException:
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ThrottlingException:
        :raises InternalServerException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("DescribeEndpoints")
    def describe_endpoints(
        self,
        context: RequestContext,
    ) -> DescribeEndpointsResponse:
        """DescribeEndpoints returns a list of available endpoints to make
        Timestream API calls against. This API is available through both Write
        and Query.

        Because the Timestream SDKs are designed to transparently work with the
        service’s architecture, including the management and mapping of the
        service endpoints, *it is not recommended that you use this API unless*:

        -  You are using `VPC endpoints (Amazon Web Services PrivateLink) with
           Timestream <https://docs.aws.amazon.com/timestream/latest/developerguide/VPCEndpoints>`__

        -  Your application uses a programming language that does not yet have
           SDK support

        -  You require better control over the client-side implementation

        For detailed information on how and when to use and implement
        DescribeEndpoints, see `The Endpoint Discovery
        Pattern <https://docs.aws.amazon.com/timestream/latest/developerguide/Using.API.html#Using-API.endpoint-discovery>`__.

        :returns: DescribeEndpointsResponse
        :raises InternalServerException:
        :raises ValidationException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DescribeTable")
    def describe_table(
        self, context: RequestContext, database_name: ResourceName, table_name: ResourceName
    ) -> DescribeTableResponse:
        """Returns information about the table, including the table name, database
        name, retention duration of the memory store and the magnetic store.
        `Service quotas
        apply <https://docs.aws.amazon.com/timestream/latest/developerguide/ts-limits.html>`__.
        See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.describe-table.html>`__
        for details.

        :param database_name: The name of the Timestream database.
        :param table_name: The name of the Timestream table.
        :returns: DescribeTableResponse
        :raises ResourceNotFoundException:
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ThrottlingException:
        :raises InternalServerException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("ListDatabases")
    def list_databases(
        self,
        context: RequestContext,
        next_token: String = None,
        max_results: PaginationLimit = None,
    ) -> ListDatabasesResponse:
        """Returns a list of your Timestream databases. `Service quotas
        apply <https://docs.aws.amazon.com/timestream/latest/developerguide/ts-limits.html>`__.
        See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.list-db.html>`__
        for details.

        :param next_token: The pagination token.
        :param max_results: The total number of items to return in the output.
        :returns: ListDatabasesResponse
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("ListTables")
    def list_tables(
        self,
        context: RequestContext,
        database_name: ResourceName = None,
        next_token: String = None,
        max_results: PaginationLimit = None,
    ) -> ListTablesResponse:
        """A list of tables, along with the name, status and retention properties
        of each table. See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.list-table.html>`__
        for details.

        :param database_name: The name of the Timestream database.
        :param next_token: The pagination token.
        :param max_results: The total number of items to return in the output.
        :returns: ListTablesResponse
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName
    ) -> ListTagsForResourceResponse:
        """List all tags on a Timestream resource.

        :param resource_arn: The Timestream resource with tags to be listed.
        :returns: ListTagsForResourceResponse
        :raises ResourceNotFoundException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tags: TagList
    ) -> TagResourceResponse:
        """Associate a set of tags with a Timestream resource. You can then
        activate these user-defined tags so that they appear on the Billing and
        Cost Management console for cost allocation tracking.

        :param resource_arn: Identifies the Timestream resource to which tags should be added.
        :param tags: The tags to be assigned to the Timestream resource.
        :returns: TagResourceResponse
        :raises ResourceNotFoundException:
        :raises ServiceQuotaExceededException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Removes the association of tags from a Timestream resource.

        :param resource_arn: The Timestream resource that the tags will be removed from.
        :param tag_keys: A list of tags keys.
        :returns: UntagResourceResponse
        :raises ValidationException:
        :raises ServiceQuotaExceededException:
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("UpdateDatabase")
    def update_database(
        self, context: RequestContext, database_name: ResourceName, kms_key_id: StringValue2048
    ) -> UpdateDatabaseResponse:
        """Modifies the KMS key for an existing database. While updating the
        database, you must specify the database name and the identifier of the
        new KMS key to be used (``KmsKeyId``). If there are any concurrent
        ``UpdateDatabase`` requests, first writer wins.

        See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.update-db.html>`__
        for details.

        :param database_name: The name of the database.
        :param kms_key_id: The identifier of the new KMS key (``KmsKeyId``) to be used to encrypt
        the data stored in the database.
        :returns: UpdateDatabaseResponse
        :raises ValidationException:
        :raises AccessDeniedException:
        :raises ResourceNotFoundException:
        :raises ServiceQuotaExceededException:
        :raises ThrottlingException:
        :raises InternalServerException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("UpdateTable")
    def update_table(
        self,
        context: RequestContext,
        database_name: ResourceName,
        table_name: ResourceName,
        retention_properties: RetentionProperties = None,
        magnetic_store_write_properties: MagneticStoreWriteProperties = None,
    ) -> UpdateTableResponse:
        """Modifies the retention duration of the memory store and magnetic store
        for your Timestream table. Note that the change in retention duration
        takes effect immediately. For example, if the retention period of the
        memory store was initially set to 2 hours and then changed to 24 hours,
        the memory store will be capable of holding 24 hours of data, but will
        be populated with 24 hours of data 22 hours after this change was made.
        Timestream does not retrieve data from the magnetic store to populate
        the memory store.

        See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.update-table.html>`__
        for details.

        :param database_name: The name of the Timestream database.
        :param table_name: The name of the Timestream table.
        :param retention_properties: The retention duration of the memory store and the magnetic store.
        :param magnetic_store_write_properties: Contains properties to set on the table when enabling magnetic store
        writes.
        :returns: UpdateTableResponse
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError

    @handler("WriteRecords")
    def write_records(
        self,
        context: RequestContext,
        database_name: ResourceName,
        table_name: ResourceName,
        records: Records,
        common_attributes: Record = None,
    ) -> WriteRecordsResponse:
        """The WriteRecords operation enables you to write your time series data
        into Timestream. You can specify a single data point or a batch of data
        points to be inserted into the system. Timestream offers you with a
        flexible schema that auto detects the column names and data types for
        your Timestream tables based on the dimension names and data types of
        the data points you specify when invoking writes into the database.
        Timestream support eventual consistency read semantics. This means that
        when you query data immediately after writing a batch of data into
        Timestream, the query results might not reflect the results of a
        recently completed write operation. The results may also include some
        stale data. If you repeat the query request after a short time, the
        results should return the latest data. `Service quotas
        apply <https://docs.aws.amazon.com/timestream/latest/developerguide/ts-limits.html>`__.

        See `code
        sample <https://docs.aws.amazon.com/timestream/latest/developerguide/code-samples.write.html>`__
        for details.

        **Upserts**

        You can use the ``Version`` parameter in a ``WriteRecords`` request to
        update data points. Timestream tracks a version number with each record.
        ``Version`` defaults to ``1`` when not specified for the record in the
        request. Timestream will update an existing record’s measure value along
        with its ``Version`` upon receiving a write request with a higher
        ``Version`` number for that record. Upon receiving an update request
        where the measure value is the same as that of the existing record,
        Timestream still updates ``Version``, if it is greater than the existing
        value of ``Version``. You can update a data point as many times as
        desired, as long as the value of ``Version`` continuously increases.

        For example, suppose you write a new record without indicating
        ``Version`` in the request. Timestream will store this record, and set
        ``Version`` to ``1``. Now, suppose you try to update this record with a
        ``WriteRecords`` request of the same record with a different measure
        value but, like before, do not provide ``Version``. In this case,
        Timestream will reject this update with a ``RejectedRecordsException``
        since the updated record’s version is not greater than the existing
        value of Version. However, if you were to resend the update request with
        ``Version`` set to ``2``, Timestream would then succeed in updating the
        record’s value, and the ``Version`` would be set to ``2``. Next, suppose
        you sent a ``WriteRecords`` request with this same record and an
        identical measure value, but with ``Version`` set to ``3``. In this
        case, Timestream would only update ``Version`` to ``3``. Any further
        updates would need to send a version number greater than ``3``, or the
        update requests would receive a ``RejectedRecordsException``.

        :param database_name: The name of the Timestream database.
        :param table_name: The name of the Timestream table.
        :param records: An array of records containing the unique measure, dimension, time, and
        version attributes for each time series data point.
        :param common_attributes: A record containing the common measure, dimension, time, and version
        attributes shared across all the records in the request.
        :returns: WriteRecordsResponse
        :raises InternalServerException:
        :raises ThrottlingException:
        :raises ValidationException:
        :raises ResourceNotFoundException:
        :raises AccessDeniedException:
        :raises RejectedRecordsException:
        :raises InvalidEndpointException:
        """
        raise NotImplementedError
