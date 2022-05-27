import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

ActivityBatchSize = int
ActivityName = str
AttributeName = str
BucketKeyExpression = str
BucketName = str
ChannelArn = str
ChannelName = str
ColumnDataType = str
ColumnName = str
DatasetActionName = str
DatasetArn = str
DatasetContentVersion = str
DatasetName = str
DatastoreArn = str
DatastoreName = str
DoubleValue = float
EntryName = str
ErrorCode = str
ErrorMessage = str
FilterExpression = str
GlueDatabaseName = str
GlueTableName = str
Image = str
IncludeStatisticsFlag = bool
IotEventsInputName = str
LambdaName = str
LateDataRuleName = str
LogResult = str
LoggingEnabled = bool
MathExpression = str
MaxMessages = int
MaxResults = int
MaxVersions = int
MessageId = str
NextToken = str
OffsetSeconds = int
OutputFileName = str
PartitionAttributeName = str
PipelineArn = str
PipelineName = str
PresignedURI = str
Reason = str
ReprocessingId = str
ResourceArn = str
RetentionPeriodInDays = int
RoleArn = str
S3KeyPrefix = str
S3PathChannelMessage = str
ScheduleExpression = str
SessionTimeoutInMinutes = int
SizeInBytes = float
SqlQuery = str
StringValue = str
TagKey = str
TagValue = str
TimeExpression = str
TimestampFormat = str
UnlimitedRetentionPeriod = bool
UnlimitedVersioning = bool
VariableName = str
VolumeSizeInGB = int
errorMessage = str
resourceArn = str
resourceId = str


class ChannelStatus(str):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"


class ComputeType(str):
    ACU_1 = "ACU_1"
    ACU_2 = "ACU_2"


class DatasetActionType(str):
    QUERY = "QUERY"
    CONTAINER = "CONTAINER"


class DatasetContentState(str):
    CREATING = "CREATING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class DatasetStatus(str):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"


class DatastoreStatus(str):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    DELETING = "DELETING"


class FileFormatType(str):
    JSON = "JSON"
    PARQUET = "PARQUET"


class LoggingLevel(str):
    ERROR = "ERROR"


class ReprocessingStatus(str):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class InternalFailureException(ServiceException):
    """There was an internal failure."""

    message: Optional[errorMessage]


class InvalidRequestException(ServiceException):
    """The request was not valid."""

    message: Optional[errorMessage]


class LimitExceededException(ServiceException):
    """The command caused an internal limit to be exceeded."""

    message: Optional[errorMessage]


class ResourceAlreadyExistsException(ServiceException):
    """A resource with the same name already exists."""

    message: Optional[errorMessage]
    resourceId: Optional[resourceId]
    resourceArn: Optional[resourceArn]


class ResourceNotFoundException(ServiceException):
    """A resource with the specified name could not be found."""

    message: Optional[errorMessage]


class ServiceUnavailableException(ServiceException):
    """The service is temporarily unavailable."""

    message: Optional[errorMessage]


class ThrottlingException(ServiceException):
    """The request was denied due to request throttling."""

    message: Optional[errorMessage]


AttributeNameMapping = Dict[AttributeName, AttributeName]


class AddAttributesActivity(TypedDict, total=False):
    """An activity that adds other attributes based on existing attributes in
    the message.
    """

    name: ActivityName
    attributes: AttributeNameMapping
    next: Optional[ActivityName]


AttributeNames = List[AttributeName]


class BatchPutMessageErrorEntry(TypedDict, total=False):
    """Contains informations about errors."""

    messageId: Optional[MessageId]
    errorCode: Optional[ErrorCode]
    errorMessage: Optional[ErrorMessage]


BatchPutMessageErrorEntries = List[BatchPutMessageErrorEntry]
MessagePayload = bytes


class Message(TypedDict, total=False):
    """Information about a message."""

    messageId: MessageId
    payload: MessagePayload


Messages = List[Message]


class BatchPutMessageRequest(ServiceRequest):
    channelName: ChannelName
    messages: Messages


class BatchPutMessageResponse(TypedDict, total=False):
    batchPutMessageErrorEntries: Optional[BatchPutMessageErrorEntries]


class CancelPipelineReprocessingRequest(ServiceRequest):
    pipelineName: PipelineName
    reprocessingId: ReprocessingId


class CancelPipelineReprocessingResponse(TypedDict, total=False):
    pass


Timestamp = datetime


class RetentionPeriod(TypedDict, total=False):
    """How long, in days, message data is kept."""

    unlimited: Optional[UnlimitedRetentionPeriod]
    numberOfDays: Optional[RetentionPeriodInDays]


class CustomerManagedChannelS3Storage(TypedDict, total=False):
    """Used to store channel data in an S3 bucket that you manage. If
    customer-managed storage is selected, the ``retentionPeriod`` parameter
    is ignored. You can't change the choice of S3 storage after the data
    store is created.
    """

    bucket: BucketName
    keyPrefix: Optional[S3KeyPrefix]
    roleArn: RoleArn


class ServiceManagedChannelS3Storage(TypedDict, total=False):
    """Used to store channel data in an S3 bucket managed by IoT Analytics. You
    can't change the choice of S3 storage after the data store is created.
    """


class ChannelStorage(TypedDict, total=False):
    """Where channel data is stored. You may choose one of
    ``serviceManagedS3``, ``customerManagedS3`` storage. If not specified,
    the default is ``serviceManagedS3``. This can't be changed after
    creation of the channel.
    """

    serviceManagedS3: Optional[ServiceManagedChannelS3Storage]
    customerManagedS3: Optional[CustomerManagedChannelS3Storage]


class Channel(TypedDict, total=False):
    """A collection of data from an MQTT topic. Channels archive the raw,
    unprocessed messages before publishing the data to a pipeline.
    """

    name: Optional[ChannelName]
    storage: Optional[ChannelStorage]
    arn: Optional[ChannelArn]
    status: Optional[ChannelStatus]
    retentionPeriod: Optional[RetentionPeriod]
    creationTime: Optional[Timestamp]
    lastUpdateTime: Optional[Timestamp]
    lastMessageArrivalTime: Optional[Timestamp]


class ChannelActivity(TypedDict, total=False):
    """The activity that determines the source of the messages to be processed."""

    name: ActivityName
    channelName: ChannelName
    next: Optional[ActivityName]


S3PathChannelMessages = List[S3PathChannelMessage]


class ChannelMessages(TypedDict, total=False):
    """Specifies one or more sets of channel messages."""

    s3Paths: Optional[S3PathChannelMessages]


class EstimatedResourceSize(TypedDict, total=False):
    """The estimated size of the resource."""

    estimatedSizeInBytes: Optional[SizeInBytes]
    estimatedOn: Optional[Timestamp]


class ChannelStatistics(TypedDict, total=False):
    """Statistics information about the channel."""

    size: Optional[EstimatedResourceSize]


class CustomerManagedChannelS3StorageSummary(TypedDict, total=False):
    """Used to store channel data in an S3 bucket that you manage."""

    bucket: Optional[BucketName]
    keyPrefix: Optional[S3KeyPrefix]
    roleArn: Optional[RoleArn]


class ServiceManagedChannelS3StorageSummary(TypedDict, total=False):
    """Used to store channel data in an S3 bucket managed by IoT Analytics."""


class ChannelStorageSummary(TypedDict, total=False):
    """Where channel data is stored."""

    serviceManagedS3: Optional[ServiceManagedChannelS3StorageSummary]
    customerManagedS3: Optional[CustomerManagedChannelS3StorageSummary]


class ChannelSummary(TypedDict, total=False):
    """A summary of information about a channel."""

    channelName: Optional[ChannelName]
    channelStorage: Optional[ChannelStorageSummary]
    status: Optional[ChannelStatus]
    creationTime: Optional[Timestamp]
    lastUpdateTime: Optional[Timestamp]
    lastMessageArrivalTime: Optional[Timestamp]


ChannelSummaries = List[ChannelSummary]
Column = TypedDict(
    "Column",
    {
        "name": ColumnName,
        "type": ColumnDataType,
    },
    total=False,
)
Columns = List[Column]


class OutputFileUriValue(TypedDict, total=False):
    """The value of the variable as a structure that specifies an output file
    URI.
    """

    fileName: OutputFileName


class DatasetContentVersionValue(TypedDict, total=False):
    """The dataset whose latest contents are used as input to the notebook or
    application.
    """

    datasetName: DatasetName


class Variable(TypedDict, total=False):
    """An instance of a variable to be passed to the ``containerAction``
    execution. Each variable must have a name and a value given by one of
    ``stringValue``, ``datasetContentVersionValue``, or
    ``outputFileUriValue``.
    """

    name: VariableName
    stringValue: Optional[StringValue]
    doubleValue: Optional[DoubleValue]
    datasetContentVersionValue: Optional[DatasetContentVersionValue]
    outputFileUriValue: Optional[OutputFileUriValue]


Variables = List[Variable]


class ResourceConfiguration(TypedDict, total=False):
    """The configuration of the resource used to execute the
    ``containerAction``.
    """

    computeType: ComputeType
    volumeSizeInGB: VolumeSizeInGB


class ContainerDatasetAction(TypedDict, total=False):
    """Information required to run the ``containerAction`` to produce dataset
    contents.
    """

    image: Image
    executionRoleArn: RoleArn
    resourceConfiguration: ResourceConfiguration
    variables: Optional[Variables]


class Tag(TypedDict, total=False):
    """A set of key-value pairs that are used to manage the resource."""

    key: TagKey
    value: TagValue


TagList = List[Tag]


class CreateChannelRequest(ServiceRequest):
    channelName: ChannelName
    channelStorage: Optional[ChannelStorage]
    retentionPeriod: Optional[RetentionPeriod]
    tags: Optional[TagList]


class CreateChannelResponse(TypedDict, total=False):
    channelName: Optional[ChannelName]
    channelArn: Optional[ChannelArn]
    retentionPeriod: Optional[RetentionPeriod]


class CreateDatasetContentRequest(ServiceRequest):
    datasetName: DatasetName
    versionId: Optional[DatasetContentVersion]


class CreateDatasetContentResponse(TypedDict, total=False):
    versionId: Optional[DatasetContentVersion]


class DeltaTimeSessionWindowConfiguration(TypedDict, total=False):
    """A structure that contains the configuration information of a delta time
    session window.

    ```DeltaTime`` <https://docs.aws.amazon.com/iotanalytics/latest/APIReference/API_DeltaTime.html>`__
    specifies a time interval. You can use ``DeltaTime`` to create dataset
    contents with data that has arrived in the data store since the last
    execution. For an example of ``DeltaTime``, see `Creating a SQL dataset
    with a delta window
    (CLI) <https://docs.aws.amazon.com/iotanalytics/latest/userguide/automate-create-dataset.html#automate-example6>`__
    in the *IoT Analytics User Guide*.
    """

    timeoutInMinutes: SessionTimeoutInMinutes


class LateDataRuleConfiguration(TypedDict, total=False):
    """The information needed to configure a delta time session window."""

    deltaTimeSessionWindowConfiguration: Optional[DeltaTimeSessionWindowConfiguration]


class LateDataRule(TypedDict, total=False):
    """A structure that contains the name and configuration information of a
    late data rule.
    """

    ruleName: Optional[LateDataRuleName]
    ruleConfiguration: LateDataRuleConfiguration


LateDataRules = List[LateDataRule]


class VersioningConfiguration(TypedDict, total=False):
    """Information about the versioning of dataset contents."""

    unlimited: Optional[UnlimitedVersioning]
    maxVersions: Optional[MaxVersions]


class GlueConfiguration(TypedDict, total=False):
    """Configuration information for coordination with Glue, a fully managed
    extract, transform and load (ETL) service.
    """

    tableName: GlueTableName
    databaseName: GlueDatabaseName


class S3DestinationConfiguration(TypedDict, total=False):
    """Configuration information for delivery of dataset contents to Amazon
    Simple Storage Service (Amazon S3).
    """

    bucket: BucketName
    key: BucketKeyExpression
    glueConfiguration: Optional[GlueConfiguration]
    roleArn: RoleArn


class IotEventsDestinationConfiguration(TypedDict, total=False):
    """Configuration information for delivery of dataset contents to IoT
    Events.
    """

    inputName: IotEventsInputName
    roleArn: RoleArn


class DatasetContentDeliveryDestination(TypedDict, total=False):
    """The destination to which dataset contents are delivered."""

    iotEventsDestinationConfiguration: Optional[IotEventsDestinationConfiguration]
    s3DestinationConfiguration: Optional[S3DestinationConfiguration]


class DatasetContentDeliveryRule(TypedDict, total=False):
    """When dataset contents are created, they are delivered to destination
    specified here.
    """

    entryName: Optional[EntryName]
    destination: DatasetContentDeliveryDestination


DatasetContentDeliveryRules = List[DatasetContentDeliveryRule]


class TriggeringDataset(TypedDict, total=False):
    """Information about the dataset whose content generation triggers the new
    dataset content generation.
    """

    name: DatasetName


class Schedule(TypedDict, total=False):
    """The schedule for when to trigger an update."""

    expression: Optional[ScheduleExpression]


class DatasetTrigger(TypedDict, total=False):
    """The ``DatasetTrigger`` that specifies when the dataset is automatically
    updated.
    """

    schedule: Optional[Schedule]
    dataset: Optional[TriggeringDataset]


DatasetTriggers = List[DatasetTrigger]


class DeltaTime(TypedDict, total=False):
    """Used to limit data to that which has arrived since the last execution of
    the action.
    """

    offsetSeconds: OffsetSeconds
    timeExpression: TimeExpression


class QueryFilter(TypedDict, total=False):
    """Information that is used to filter message data, to segregate it
    according to the timeframe in which it arrives.
    """

    deltaTime: Optional[DeltaTime]


QueryFilters = List[QueryFilter]


class SqlQueryDatasetAction(TypedDict, total=False):
    """The SQL query to modify the message."""

    sqlQuery: SqlQuery
    filters: Optional[QueryFilters]


class DatasetAction(TypedDict, total=False):
    """A ``DatasetAction`` object that specifies how dataset contents are
    automatically created.
    """

    actionName: Optional[DatasetActionName]
    queryAction: Optional[SqlQueryDatasetAction]
    containerAction: Optional[ContainerDatasetAction]


DatasetActions = List[DatasetAction]


class CreateDatasetRequest(ServiceRequest):
    datasetName: DatasetName
    actions: DatasetActions
    triggers: Optional[DatasetTriggers]
    contentDeliveryRules: Optional[DatasetContentDeliveryRules]
    retentionPeriod: Optional[RetentionPeriod]
    versioningConfiguration: Optional[VersioningConfiguration]
    tags: Optional[TagList]
    lateDataRules: Optional[LateDataRules]


class CreateDatasetResponse(TypedDict, total=False):
    datasetName: Optional[DatasetName]
    datasetArn: Optional[DatasetArn]
    retentionPeriod: Optional[RetentionPeriod]


class TimestampPartition(TypedDict, total=False):
    """A partition dimension defined by a timestamp attribute."""

    attributeName: PartitionAttributeName
    timestampFormat: Optional[TimestampFormat]


class Partition(TypedDict, total=False):
    """A partition dimension defined by an attribute."""

    attributeName: PartitionAttributeName


class DatastorePartition(TypedDict, total=False):
    """A single dimension to partition a data store. The dimension must be an
    ``AttributePartition`` or a ``TimestampPartition``.
    """

    attributePartition: Optional[Partition]
    timestampPartition: Optional[TimestampPartition]


Partitions = List[DatastorePartition]


class DatastorePartitions(TypedDict, total=False):
    """Contains information about the partition dimensions in a data store."""

    partitions: Optional[Partitions]


class SchemaDefinition(TypedDict, total=False):
    """Information needed to define a schema."""

    columns: Optional[Columns]


class ParquetConfiguration(TypedDict, total=False):
    """Contains the configuration information of the Parquet format."""

    schemaDefinition: Optional[SchemaDefinition]


class JsonConfiguration(TypedDict, total=False):
    """Contains the configuration information of the JSON format."""


class FileFormatConfiguration(TypedDict, total=False):
    """Contains the configuration information of file formats. IoT Analytics
    data stores support JSON and `Parquet <https://parquet.apache.org/>`__.

    The default file format is JSON. You can specify only one format.

    You can't change the file format after you create the data store.
    """

    jsonConfiguration: Optional[JsonConfiguration]
    parquetConfiguration: Optional[ParquetConfiguration]


class IotSiteWiseCustomerManagedDatastoreS3Storage(TypedDict, total=False):
    """Used to store data used by IoT SiteWise in an Amazon S3 bucket that you
    manage. You can't change the choice of Amazon S3 storage after your data
    store is created.
    """

    bucket: BucketName
    keyPrefix: Optional[S3KeyPrefix]


class DatastoreIotSiteWiseMultiLayerStorage(TypedDict, total=False):
    """Used to store data used by IoT SiteWise in an Amazon S3 bucket that you
    manage. You can't change the choice of Amazon S3 storage after your data
    store is created.
    """

    customerManagedS3Storage: IotSiteWiseCustomerManagedDatastoreS3Storage


class CustomerManagedDatastoreS3Storage(TypedDict, total=False):
    """S3-customer-managed; When you choose customer-managed storage, the
    ``retentionPeriod`` parameter is ignored. You can't change the choice of
    Amazon S3 storage after your data store is created.
    """

    bucket: BucketName
    keyPrefix: Optional[S3KeyPrefix]
    roleArn: RoleArn


class ServiceManagedDatastoreS3Storage(TypedDict, total=False):
    """Used to store data in an Amazon S3 bucket managed by IoT Analytics. You
    can't change the choice of Amazon S3 storage after your data store is
    created.
    """


class DatastoreStorage(TypedDict, total=False):
    """Where data in a data store is stored.. You can choose
    ``serviceManagedS3`` storage, ``customerManagedS3`` storage, or
    ``iotSiteWiseMultiLayerStorage`` storage. The default is
    ``serviceManagedS3``. You can't change the choice of Amazon S3 storage
    after your data store is created.
    """

    serviceManagedS3: Optional[ServiceManagedDatastoreS3Storage]
    customerManagedS3: Optional[CustomerManagedDatastoreS3Storage]
    iotSiteWiseMultiLayerStorage: Optional[DatastoreIotSiteWiseMultiLayerStorage]


class CreateDatastoreRequest(ServiceRequest):
    datastoreName: DatastoreName
    datastoreStorage: Optional[DatastoreStorage]
    retentionPeriod: Optional[RetentionPeriod]
    tags: Optional[TagList]
    fileFormatConfiguration: Optional[FileFormatConfiguration]
    datastorePartitions: Optional[DatastorePartitions]


class CreateDatastoreResponse(TypedDict, total=False):
    datastoreName: Optional[DatastoreName]
    datastoreArn: Optional[DatastoreArn]
    retentionPeriod: Optional[RetentionPeriod]


class DeviceShadowEnrichActivity(TypedDict, total=False):
    """An activity that adds information from the IoT Device Shadow service to
    a message.
    """

    name: ActivityName
    attribute: AttributeName
    thingName: AttributeName
    roleArn: RoleArn
    next: Optional[ActivityName]


class DeviceRegistryEnrichActivity(TypedDict, total=False):
    """An activity that adds data from the IoT device registry to your message."""

    name: ActivityName
    attribute: AttributeName
    thingName: AttributeName
    roleArn: RoleArn
    next: Optional[ActivityName]


class MathActivity(TypedDict, total=False):
    """An activity that computes an arithmetic expression using the message's
    attributes.
    """

    name: ActivityName
    attribute: AttributeName
    math: MathExpression
    next: Optional[ActivityName]


class FilterActivity(TypedDict, total=False):
    """An activity that filters a message based on its attributes."""

    name: ActivityName
    filter: FilterExpression
    next: Optional[ActivityName]


class SelectAttributesActivity(TypedDict, total=False):
    """Used to create a new message using only the specified attributes from
    the original message.
    """

    name: ActivityName
    attributes: AttributeNames
    next: Optional[ActivityName]


class RemoveAttributesActivity(TypedDict, total=False):
    """An activity that removes attributes from a message."""

    name: ActivityName
    attributes: AttributeNames
    next: Optional[ActivityName]


class DatastoreActivity(TypedDict, total=False):
    """The datastore activity that specifies where to store the processed data."""

    name: ActivityName
    datastoreName: DatastoreName


class LambdaActivity(TypedDict, total=False):
    """An activity that runs a Lambda function to modify the message."""

    name: ActivityName
    lambdaName: LambdaName
    batchSize: ActivityBatchSize
    next: Optional[ActivityName]


PipelineActivity = TypedDict(
    "PipelineActivity",
    {
        "channel": Optional[ChannelActivity],
        "lambda": Optional[LambdaActivity],
        "datastore": Optional[DatastoreActivity],
        "addAttributes": Optional[AddAttributesActivity],
        "removeAttributes": Optional[RemoveAttributesActivity],
        "selectAttributes": Optional[SelectAttributesActivity],
        "filter": Optional[FilterActivity],
        "math": Optional[MathActivity],
        "deviceRegistryEnrich": Optional[DeviceRegistryEnrichActivity],
        "deviceShadowEnrich": Optional[DeviceShadowEnrichActivity],
    },
    total=False,
)
PipelineActivities = List[PipelineActivity]


class CreatePipelineRequest(ServiceRequest):
    pipelineName: PipelineName
    pipelineActivities: PipelineActivities
    tags: Optional[TagList]


class CreatePipelineResponse(TypedDict, total=False):
    pipelineName: Optional[PipelineName]
    pipelineArn: Optional[PipelineArn]


class CustomerManagedDatastoreS3StorageSummary(TypedDict, total=False):
    """Contains information about the data store that you manage."""

    bucket: Optional[BucketName]
    keyPrefix: Optional[S3KeyPrefix]
    roleArn: Optional[RoleArn]


class Dataset(TypedDict, total=False):
    """Information about a dataset."""

    name: Optional[DatasetName]
    arn: Optional[DatasetArn]
    actions: Optional[DatasetActions]
    triggers: Optional[DatasetTriggers]
    contentDeliveryRules: Optional[DatasetContentDeliveryRules]
    status: Optional[DatasetStatus]
    creationTime: Optional[Timestamp]
    lastUpdateTime: Optional[Timestamp]
    retentionPeriod: Optional[RetentionPeriod]
    versioningConfiguration: Optional[VersioningConfiguration]
    lateDataRules: Optional[LateDataRules]


class DatasetActionSummary(TypedDict, total=False):
    """Information about the action that automatically creates the dataset's
    contents.
    """

    actionName: Optional[DatasetActionName]
    actionType: Optional[DatasetActionType]


DatasetActionSummaries = List[DatasetActionSummary]


class DatasetContentStatus(TypedDict, total=False):
    """The state of the dataset contents and the reason they are in this state."""

    state: Optional[DatasetContentState]
    reason: Optional[Reason]


class DatasetContentSummary(TypedDict, total=False):
    """Summary information about dataset contents."""

    version: Optional[DatasetContentVersion]
    status: Optional[DatasetContentStatus]
    creationTime: Optional[Timestamp]
    scheduleTime: Optional[Timestamp]
    completionTime: Optional[Timestamp]


DatasetContentSummaries = List[DatasetContentSummary]


class DatasetEntry(TypedDict, total=False):
    """The reference to a dataset entry."""

    entryName: Optional[EntryName]
    dataURI: Optional[PresignedURI]


DatasetEntries = List[DatasetEntry]


class DatasetSummary(TypedDict, total=False):
    """A summary of information about a dataset."""

    datasetName: Optional[DatasetName]
    status: Optional[DatasetStatus]
    creationTime: Optional[Timestamp]
    lastUpdateTime: Optional[Timestamp]
    triggers: Optional[DatasetTriggers]
    actions: Optional[DatasetActionSummaries]


DatasetSummaries = List[DatasetSummary]


class Datastore(TypedDict, total=False):
    """Information about a data store."""

    name: Optional[DatastoreName]
    storage: Optional[DatastoreStorage]
    arn: Optional[DatastoreArn]
    status: Optional[DatastoreStatus]
    retentionPeriod: Optional[RetentionPeriod]
    creationTime: Optional[Timestamp]
    lastUpdateTime: Optional[Timestamp]
    lastMessageArrivalTime: Optional[Timestamp]
    fileFormatConfiguration: Optional[FileFormatConfiguration]
    datastorePartitions: Optional[DatastorePartitions]


class IotSiteWiseCustomerManagedDatastoreS3StorageSummary(TypedDict, total=False):
    """Contains information about the data store that you manage, which stores
    data used by IoT SiteWise.
    """

    bucket: Optional[BucketName]
    keyPrefix: Optional[S3KeyPrefix]


class DatastoreIotSiteWiseMultiLayerStorageSummary(TypedDict, total=False):
    """Contains information about the data store that you manage, which stores
    data used by IoT SiteWise.
    """

    customerManagedS3Storage: Optional[IotSiteWiseCustomerManagedDatastoreS3StorageSummary]


class DatastoreStatistics(TypedDict, total=False):
    """Statistical information about the data store."""

    size: Optional[EstimatedResourceSize]


class ServiceManagedDatastoreS3StorageSummary(TypedDict, total=False):
    """Contains information about the data store that is managed by IoT
    Analytics.
    """


class DatastoreStorageSummary(TypedDict, total=False):
    """Contains information about your data store."""

    serviceManagedS3: Optional[ServiceManagedDatastoreS3StorageSummary]
    customerManagedS3: Optional[CustomerManagedDatastoreS3StorageSummary]
    iotSiteWiseMultiLayerStorage: Optional[DatastoreIotSiteWiseMultiLayerStorageSummary]


class DatastoreSummary(TypedDict, total=False):
    """A summary of information about a data store."""

    datastoreName: Optional[DatastoreName]
    datastoreStorage: Optional[DatastoreStorageSummary]
    status: Optional[DatastoreStatus]
    creationTime: Optional[Timestamp]
    lastUpdateTime: Optional[Timestamp]
    lastMessageArrivalTime: Optional[Timestamp]
    fileFormatType: Optional[FileFormatType]
    datastorePartitions: Optional[DatastorePartitions]


DatastoreSummaries = List[DatastoreSummary]


class DeleteChannelRequest(ServiceRequest):
    channelName: ChannelName


class DeleteDatasetContentRequest(ServiceRequest):
    datasetName: DatasetName
    versionId: Optional[DatasetContentVersion]


class DeleteDatasetRequest(ServiceRequest):
    datasetName: DatasetName


class DeleteDatastoreRequest(ServiceRequest):
    datastoreName: DatastoreName


class DeletePipelineRequest(ServiceRequest):
    pipelineName: PipelineName


class DescribeChannelRequest(ServiceRequest):
    channelName: ChannelName
    includeStatistics: Optional[IncludeStatisticsFlag]


class DescribeChannelResponse(TypedDict, total=False):
    channel: Optional[Channel]
    statistics: Optional[ChannelStatistics]


class DescribeDatasetRequest(ServiceRequest):
    datasetName: DatasetName


class DescribeDatasetResponse(TypedDict, total=False):
    dataset: Optional[Dataset]


class DescribeDatastoreRequest(ServiceRequest):
    datastoreName: DatastoreName
    includeStatistics: Optional[IncludeStatisticsFlag]


class DescribeDatastoreResponse(TypedDict, total=False):
    datastore: Optional[Datastore]
    statistics: Optional[DatastoreStatistics]


class DescribeLoggingOptionsRequest(ServiceRequest):
    pass


class LoggingOptions(TypedDict, total=False):
    """Information about logging options."""

    roleArn: RoleArn
    level: LoggingLevel
    enabled: LoggingEnabled


class DescribeLoggingOptionsResponse(TypedDict, total=False):
    loggingOptions: Optional[LoggingOptions]


class DescribePipelineRequest(ServiceRequest):
    pipelineName: PipelineName


class ReprocessingSummary(TypedDict, total=False):
    """Information about pipeline reprocessing."""

    id: Optional[ReprocessingId]
    status: Optional[ReprocessingStatus]
    creationTime: Optional[Timestamp]


ReprocessingSummaries = List[ReprocessingSummary]


class Pipeline(TypedDict, total=False):
    """Contains information about a pipeline."""

    name: Optional[PipelineName]
    arn: Optional[PipelineArn]
    activities: Optional[PipelineActivities]
    reprocessingSummaries: Optional[ReprocessingSummaries]
    creationTime: Optional[Timestamp]
    lastUpdateTime: Optional[Timestamp]


class DescribePipelineResponse(TypedDict, total=False):
    pipeline: Optional[Pipeline]


EndTime = datetime


class GetDatasetContentRequest(ServiceRequest):
    datasetName: DatasetName
    versionId: Optional[DatasetContentVersion]


class GetDatasetContentResponse(TypedDict, total=False):
    entries: Optional[DatasetEntries]
    timestamp: Optional[Timestamp]
    status: Optional[DatasetContentStatus]


class ListChannelsRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListChannelsResponse(TypedDict, total=False):
    channelSummaries: Optional[ChannelSummaries]
    nextToken: Optional[NextToken]


class ListDatasetContentsRequest(ServiceRequest):
    datasetName: DatasetName
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]
    scheduledOnOrAfter: Optional[Timestamp]
    scheduledBefore: Optional[Timestamp]


class ListDatasetContentsResponse(TypedDict, total=False):
    datasetContentSummaries: Optional[DatasetContentSummaries]
    nextToken: Optional[NextToken]


class ListDatasetsRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListDatasetsResponse(TypedDict, total=False):
    datasetSummaries: Optional[DatasetSummaries]
    nextToken: Optional[NextToken]


class ListDatastoresRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListDatastoresResponse(TypedDict, total=False):
    datastoreSummaries: Optional[DatastoreSummaries]
    nextToken: Optional[NextToken]


class ListPipelinesRequest(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class PipelineSummary(TypedDict, total=False):
    """A summary of information about a pipeline."""

    pipelineName: Optional[PipelineName]
    reprocessingSummaries: Optional[ReprocessingSummaries]
    creationTime: Optional[Timestamp]
    lastUpdateTime: Optional[Timestamp]


PipelineSummaries = List[PipelineSummary]


class ListPipelinesResponse(TypedDict, total=False):
    pipelineSummaries: Optional[PipelineSummaries]
    nextToken: Optional[NextToken]


class ListTagsForResourceRequest(ServiceRequest):
    resourceArn: ResourceArn


class ListTagsForResourceResponse(TypedDict, total=False):
    tags: Optional[TagList]


MessagePayloads = List[MessagePayload]


class PutLoggingOptionsRequest(ServiceRequest):
    loggingOptions: LoggingOptions


class RunPipelineActivityRequest(ServiceRequest):
    pipelineActivity: PipelineActivity
    payloads: MessagePayloads


class RunPipelineActivityResponse(TypedDict, total=False):
    payloads: Optional[MessagePayloads]
    logResult: Optional[LogResult]


StartTime = datetime


class SampleChannelDataRequest(ServiceRequest):
    channelName: ChannelName
    maxMessages: Optional[MaxMessages]
    startTime: Optional[StartTime]
    endTime: Optional[EndTime]


class SampleChannelDataResponse(TypedDict, total=False):
    payloads: Optional[MessagePayloads]


class StartPipelineReprocessingRequest(ServiceRequest):
    pipelineName: PipelineName
    startTime: Optional[StartTime]
    endTime: Optional[EndTime]
    channelMessages: Optional[ChannelMessages]


class StartPipelineReprocessingResponse(TypedDict, total=False):
    reprocessingId: Optional[ReprocessingId]


TagKeyList = List[TagKey]


class TagResourceRequest(ServiceRequest):
    resourceArn: ResourceArn
    tags: TagList


class TagResourceResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    resourceArn: ResourceArn
    tagKeys: TagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateChannelRequest(ServiceRequest):
    channelName: ChannelName
    channelStorage: Optional[ChannelStorage]
    retentionPeriod: Optional[RetentionPeriod]


class UpdateDatasetRequest(ServiceRequest):
    datasetName: DatasetName
    actions: DatasetActions
    triggers: Optional[DatasetTriggers]
    contentDeliveryRules: Optional[DatasetContentDeliveryRules]
    retentionPeriod: Optional[RetentionPeriod]
    versioningConfiguration: Optional[VersioningConfiguration]
    lateDataRules: Optional[LateDataRules]


class UpdateDatastoreRequest(ServiceRequest):
    datastoreName: DatastoreName
    retentionPeriod: Optional[RetentionPeriod]
    datastoreStorage: Optional[DatastoreStorage]
    fileFormatConfiguration: Optional[FileFormatConfiguration]


class UpdatePipelineRequest(ServiceRequest):
    pipelineName: PipelineName
    pipelineActivities: PipelineActivities


class IotanalyticsApi:

    service = "iotanalytics"
    version = "2017-11-27"

    @handler("BatchPutMessage")
    def batch_put_message(
        self, context: RequestContext, channel_name: ChannelName, messages: Messages
    ) -> BatchPutMessageResponse:
        """Sends messages to a channel.

        :param channel_name: The name of the channel where the messages are sent.
        :param messages: The list of messages to be sent.
        :returns: BatchPutMessageResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CancelPipelineReprocessing")
    def cancel_pipeline_reprocessing(
        self, context: RequestContext, pipeline_name: PipelineName, reprocessing_id: ReprocessingId
    ) -> CancelPipelineReprocessingResponse:
        """Cancels the reprocessing of data through the pipeline.

        :param pipeline_name: The name of pipeline for which data reprocessing is canceled.
        :param reprocessing_id: The ID of the reprocessing task (returned by
        ``StartPipelineReprocessing``).
        :returns: CancelPipelineReprocessingResponse
        :raises ResourceNotFoundException:
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateChannel")
    def create_channel(
        self,
        context: RequestContext,
        channel_name: ChannelName,
        channel_storage: ChannelStorage = None,
        retention_period: RetentionPeriod = None,
        tags: TagList = None,
    ) -> CreateChannelResponse:
        """Used to create a channel. A channel collects data from an MQTT topic and
        archives the raw, unprocessed messages before publishing the data to a
        pipeline.

        :param channel_name: The name of the channel.
        :param channel_storage: Where channel data is stored.
        :param retention_period: How long, in days, message data is kept for the channel.
        :param tags: Metadata which can be used to manage the channel.
        :returns: CreateChannelResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateDataset")
    def create_dataset(
        self,
        context: RequestContext,
        dataset_name: DatasetName,
        actions: DatasetActions,
        triggers: DatasetTriggers = None,
        content_delivery_rules: DatasetContentDeliveryRules = None,
        retention_period: RetentionPeriod = None,
        versioning_configuration: VersioningConfiguration = None,
        tags: TagList = None,
        late_data_rules: LateDataRules = None,
    ) -> CreateDatasetResponse:
        """Used to create a dataset. A dataset stores data retrieved from a data
        store by applying a ``queryAction`` (a SQL query) or a
        ``containerAction`` (executing a containerized application). This
        operation creates the skeleton of a dataset. The dataset can be
        populated manually by calling ``CreateDatasetContent`` or automatically
        according to a trigger you specify.

        :param dataset_name: The name of the dataset.
        :param actions: A list of actions that create the dataset contents.
        :param triggers: A list of triggers.
        :param content_delivery_rules: When dataset contents are created, they are delivered to destinations
        specified here.
        :param retention_period: Optional.
        :param versioning_configuration: Optional.
        :param tags: Metadata which can be used to manage the dataset.
        :param late_data_rules: A list of data rules that send notifications to CloudWatch, when data
        arrives late.
        :returns: CreateDatasetResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateDatasetContent")
    def create_dataset_content(
        self,
        context: RequestContext,
        dataset_name: DatasetName,
        version_id: DatasetContentVersion = None,
    ) -> CreateDatasetContentResponse:
        """Creates the content of a dataset by applying a ``queryAction`` (a SQL
        query) or a ``containerAction`` (executing a containerized application).

        :param dataset_name: The name of the dataset.
        :param version_id: The version ID of the dataset content.
        :returns: CreateDatasetContentResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("CreateDatastore")
    def create_datastore(
        self,
        context: RequestContext,
        datastore_name: DatastoreName,
        datastore_storage: DatastoreStorage = None,
        retention_period: RetentionPeriod = None,
        tags: TagList = None,
        file_format_configuration: FileFormatConfiguration = None,
        datastore_partitions: DatastorePartitions = None,
    ) -> CreateDatastoreResponse:
        """Creates a data store, which is a repository for messages.

        :param datastore_name: The name of the data store.
        :param datastore_storage: Where data in a data store is stored.
        :param retention_period: How long, in days, message data is kept for the data store.
        :param tags: Metadata which can be used to manage the data store.
        :param file_format_configuration: Contains the configuration information of file formats.
        :param datastore_partitions: Contains information about the partition dimensions in a data store.
        :returns: CreateDatastoreResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreatePipeline")
    def create_pipeline(
        self,
        context: RequestContext,
        pipeline_name: PipelineName,
        pipeline_activities: PipelineActivities,
        tags: TagList = None,
    ) -> CreatePipelineResponse:
        """Creates a pipeline. A pipeline consumes messages from a channel and
        allows you to process the messages before storing them in a data store.
        You must specify both a ``channel`` and a ``datastore`` activity and,
        optionally, as many as 23 additional activities in the
        ``pipelineActivities`` array.

        :param pipeline_name: The name of the pipeline.
        :param pipeline_activities: A list of ``PipelineActivity`` objects.
        :param tags: Metadata which can be used to manage the pipeline.
        :returns: CreatePipelineResponse
        :raises InvalidRequestException:
        :raises ResourceAlreadyExistsException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("DeleteChannel")
    def delete_channel(self, context: RequestContext, channel_name: ChannelName) -> None:
        """Deletes the specified channel.

        :param channel_name: The name of the channel to delete.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteDataset")
    def delete_dataset(self, context: RequestContext, dataset_name: DatasetName) -> None:
        """Deletes the specified dataset.

        You do not have to delete the content of the dataset before you perform
        this operation.

        :param dataset_name: The name of the dataset to delete.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteDatasetContent")
    def delete_dataset_content(
        self,
        context: RequestContext,
        dataset_name: DatasetName,
        version_id: DatasetContentVersion = None,
    ) -> None:
        """Deletes the content of the specified dataset.

        :param dataset_name: The name of the dataset whose content is deleted.
        :param version_id: The version of the dataset whose content is deleted.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeleteDatastore")
    def delete_datastore(self, context: RequestContext, datastore_name: DatastoreName) -> None:
        """Deletes the specified data store.

        :param datastore_name: The name of the data store to delete.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DeletePipeline")
    def delete_pipeline(self, context: RequestContext, pipeline_name: PipelineName) -> None:
        """Deletes the specified pipeline.

        :param pipeline_name: The name of the pipeline to delete.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DescribeChannel")
    def describe_channel(
        self,
        context: RequestContext,
        channel_name: ChannelName,
        include_statistics: IncludeStatisticsFlag = None,
    ) -> DescribeChannelResponse:
        """Retrieves information about a channel.

        :param channel_name: The name of the channel whose information is retrieved.
        :param include_statistics: If true, additional statistical information about the channel is
        included in the response.
        :returns: DescribeChannelResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DescribeDataset")
    def describe_dataset(
        self, context: RequestContext, dataset_name: DatasetName
    ) -> DescribeDatasetResponse:
        """Retrieves information about a dataset.

        :param dataset_name: The name of the dataset whose information is retrieved.
        :returns: DescribeDatasetResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DescribeDatastore")
    def describe_datastore(
        self,
        context: RequestContext,
        datastore_name: DatastoreName,
        include_statistics: IncludeStatisticsFlag = None,
    ) -> DescribeDatastoreResponse:
        """Retrieves information about a data store.

        :param datastore_name: The name of the data store.
        :param include_statistics: If true, additional statistical information about the data store is
        included in the response.
        :returns: DescribeDatastoreResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DescribeLoggingOptions")
    def describe_logging_options(
        self,
        context: RequestContext,
    ) -> DescribeLoggingOptionsResponse:
        """Retrieves the current settings of the IoT Analytics logging options.

        :returns: DescribeLoggingOptionsResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("DescribePipeline")
    def describe_pipeline(
        self, context: RequestContext, pipeline_name: PipelineName
    ) -> DescribePipelineResponse:
        """Retrieves information about a pipeline.

        :param pipeline_name: The name of the pipeline whose information is retrieved.
        :returns: DescribePipelineResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("GetDatasetContent")
    def get_dataset_content(
        self,
        context: RequestContext,
        dataset_name: DatasetName,
        version_id: DatasetContentVersion = None,
    ) -> GetDatasetContentResponse:
        """Retrieves the contents of a dataset as presigned URIs.

        :param dataset_name: The name of the dataset whose contents are retrieved.
        :param version_id: The version of the dataset whose contents are retrieved.
        :returns: GetDatasetContentResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListChannels")
    def list_channels(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListChannelsResponse:
        """Retrieves a list of channels.

        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return in this request.
        :returns: ListChannelsResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListDatasetContents")
    def list_dataset_contents(
        self,
        context: RequestContext,
        dataset_name: DatasetName,
        next_token: NextToken = None,
        max_results: MaxResults = None,
        scheduled_on_or_after: Timestamp = None,
        scheduled_before: Timestamp = None,
    ) -> ListDatasetContentsResponse:
        """Lists information about dataset contents that have been created.

        :param dataset_name: The name of the dataset whose contents information you want to list.
        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return in this request.
        :param scheduled_on_or_after: A filter to limit results to those dataset contents whose creation is
        scheduled on or after the given time.
        :param scheduled_before: A filter to limit results to those dataset contents whose creation is
        scheduled before the given time.
        :returns: ListDatasetContentsResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("ListDatasets")
    def list_datasets(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListDatasetsResponse:
        """Retrieves information about datasets.

        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return in this request.
        :returns: ListDatasetsResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListDatastores")
    def list_datastores(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListDatastoresResponse:
        """Retrieves a list of data stores.

        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return in this request.
        :returns: ListDatastoresResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListPipelines")
    def list_pipelines(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListPipelinesResponse:
        """Retrieves a list of pipelines.

        :param next_token: The token for the next set of results.
        :param max_results: The maximum number of results to return in this request.
        :returns: ListPipelinesResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: ResourceArn
    ) -> ListTagsForResourceResponse:
        """Lists the tags (metadata) that you have assigned to the resource.

        :param resource_arn: The ARN of the resource whose tags you want to list.
        :returns: ListTagsForResourceResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        :raises LimitExceededException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("PutLoggingOptions")
    def put_logging_options(self, context: RequestContext, logging_options: LoggingOptions) -> None:
        """Sets or updates the IoT Analytics logging options.

        If you update the value of any ``loggingOptions`` field, it takes up to
        one minute for the change to take effect. Also, if you change the policy
        attached to the role you specified in the ``roleArn`` field (for
        example, to correct an invalid policy), it takes up to five minutes for
        that change to take effect.

        :param logging_options: The new values of the IoT Analytics logging options.
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("RunPipelineActivity")
    def run_pipeline_activity(
        self,
        context: RequestContext,
        pipeline_activity: PipelineActivity,
        payloads: MessagePayloads,
    ) -> RunPipelineActivityResponse:
        """Simulates the results of running a pipeline activity on a message
        payload.

        :param pipeline_activity: The pipeline activity that is run.
        :param payloads: The sample message payloads on which the pipeline activity is run.
        :returns: RunPipelineActivityResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("SampleChannelData")
    def sample_channel_data(
        self,
        context: RequestContext,
        channel_name: ChannelName,
        max_messages: MaxMessages = None,
        start_time: StartTime = None,
        end_time: EndTime = None,
    ) -> SampleChannelDataResponse:
        """Retrieves a sample of messages from the specified channel ingested
        during the specified timeframe. Up to 10 messages can be retrieved.

        :param channel_name: The name of the channel whose message samples are retrieved.
        :param max_messages: The number of sample messages to be retrieved.
        :param start_time: The start of the time window from which sample messages are retrieved.
        :param end_time: The end of the time window from which sample messages are retrieved.
        :returns: SampleChannelDataResponse
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("StartPipelineReprocessing")
    def start_pipeline_reprocessing(
        self,
        context: RequestContext,
        pipeline_name: PipelineName,
        start_time: StartTime = None,
        end_time: EndTime = None,
        channel_messages: ChannelMessages = None,
    ) -> StartPipelineReprocessingResponse:
        """Starts the reprocessing of raw message data through the pipeline.

        :param pipeline_name: The name of the pipeline on which to start reprocessing.
        :param start_time: The start time (inclusive) of raw message data that is reprocessed.
        :param end_time: The end time (exclusive) of raw message data that is reprocessed.
        :param channel_messages: Specifies one or more sets of channel messages that you want to
        reprocess.
        :returns: StartPipelineReprocessingResponse
        :raises ResourceNotFoundException:
        :raises ResourceAlreadyExistsException:
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: ResourceArn, tags: TagList
    ) -> TagResourceResponse:
        """Adds to or modifies the tags of the given resource. Tags are metadata
        that can be used to manage a resource.

        :param resource_arn: The ARN of the resource whose tags you want to modify.
        :param tags: The new or modified tags for the resource.
        :returns: TagResourceResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        :raises LimitExceededException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: ResourceArn, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Removes the given tags (metadata) from the resource.

        :param resource_arn: The ARN of the resource whose tags you want to remove.
        :param tag_keys: The keys of those tags which you want to remove.
        :returns: UntagResourceResponse
        :raises InvalidRequestException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        :raises LimitExceededException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateChannel")
    def update_channel(
        self,
        context: RequestContext,
        channel_name: ChannelName,
        channel_storage: ChannelStorage = None,
        retention_period: RetentionPeriod = None,
    ) -> None:
        """Used to update the settings of a channel.

        :param channel_name: The name of the channel to be updated.
        :param channel_storage: Where channel data is stored.
        :param retention_period: How long, in days, message data is kept for the channel.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateDataset")
    def update_dataset(
        self,
        context: RequestContext,
        dataset_name: DatasetName,
        actions: DatasetActions,
        triggers: DatasetTriggers = None,
        content_delivery_rules: DatasetContentDeliveryRules = None,
        retention_period: RetentionPeriod = None,
        versioning_configuration: VersioningConfiguration = None,
        late_data_rules: LateDataRules = None,
    ) -> None:
        """Updates the settings of a dataset.

        :param dataset_name: The name of the dataset to update.
        :param actions: A list of ``DatasetAction`` objects.
        :param triggers: A list of ``DatasetTrigger`` objects.
        :param content_delivery_rules: When dataset contents are created, they are delivered to destinations
        specified here.
        :param retention_period: How long, in days, dataset contents are kept for the dataset.
        :param versioning_configuration: Optional.
        :param late_data_rules: A list of data rules that send notifications to CloudWatch, when data
        arrives late.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdateDatastore")
    def update_datastore(
        self,
        context: RequestContext,
        datastore_name: DatastoreName,
        retention_period: RetentionPeriod = None,
        datastore_storage: DatastoreStorage = None,
        file_format_configuration: FileFormatConfiguration = None,
    ) -> None:
        """Used to update the settings of a data store.

        :param datastore_name: The name of the data store to be updated.
        :param retention_period: How long, in days, message data is kept for the data store.
        :param datastore_storage: Where data in a data store is stored.
        :param file_format_configuration: Contains the configuration information of file formats.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        """
        raise NotImplementedError

    @handler("UpdatePipeline")
    def update_pipeline(
        self,
        context: RequestContext,
        pipeline_name: PipelineName,
        pipeline_activities: PipelineActivities,
    ) -> None:
        """Updates the settings of a pipeline. You must specify both a ``channel``
        and a ``datastore`` activity and, optionally, as many as 23 additional
        activities in the ``pipelineActivities`` array.

        :param pipeline_name: The name of the pipeline to update.
        :param pipeline_activities: A list of ``PipelineActivity`` objects.
        :raises InvalidRequestException:
        :raises ResourceNotFoundException:
        :raises InternalFailureException:
        :raises ServiceUnavailableException:
        :raises ThrottlingException:
        :raises LimitExceededException:
        """
        raise NotImplementedError
