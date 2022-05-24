import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Boolean = bool
ErrorMessage = str
EventDataStoreArn = str
EventDataStoreName = str
Integer = int
ListEventDataStoresMaxResultsCount = int
ListQueriesMaxResultsCount = int
MaxQueryResults = int
MaxResults = int
NextToken = str
OperatorValue = str
PaginationToken = str
QueryResultKey = str
QueryResultValue = str
QueryStatement = str
RetentionPeriod = int
SelectorField = str
SelectorName = str
String = str
TagKey = str
TagValue = str
TerminationProtectionEnabled = bool
UUID = str


class EventCategory(str):
    insight = "insight"


class EventDataStoreStatus(str):
    CREATED = "CREATED"
    ENABLED = "ENABLED"
    PENDING_DELETION = "PENDING_DELETION"


class InsightType(str):
    ApiCallRateInsight = "ApiCallRateInsight"
    ApiErrorRateInsight = "ApiErrorRateInsight"


class LookupAttributeKey(str):
    EventId = "EventId"
    EventName = "EventName"
    ReadOnly = "ReadOnly"
    Username = "Username"
    ResourceType = "ResourceType"
    ResourceName = "ResourceName"
    EventSource = "EventSource"
    AccessKeyId = "AccessKeyId"


class QueryStatus(str):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


class ReadWriteType(str):
    ReadOnly = "ReadOnly"
    WriteOnly = "WriteOnly"
    All = "All"


class CloudTrailARNInvalidException(ServiceException):
    """This exception is thrown when an operation is called with a trail ARN
    that is not valid. The following is the format of a trail ARN.

    ``arn:aws:cloudtrail:us-east-2:123456789012:trail/MyTrail``
    """


class CloudTrailAccessNotEnabledException(ServiceException):
    """This exception is thrown when trusted access has not been enabled
    between CloudTrail and Organizations. For more information, see
    `Enabling Trusted Access with Other Amazon Web Services
    Services <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services.html>`__
    and `Prepare For Creating a Trail For Your
    Organization <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-an-organizational-trail-prepare.html>`__.
    """


class CloudTrailInvalidClientTokenIdException(ServiceException):
    """This exception is thrown when a call results in the
    ``InvalidClientTokenId`` error code. This can occur when you are
    creating or updating a trail to send notifications to an Amazon SNS
    topic that is in a suspended Amazon Web Services account.
    """


class CloudWatchLogsDeliveryUnavailableException(ServiceException):
    """Cannot set a CloudWatch Logs delivery for this region."""


class ConflictException(ServiceException):
    """This exception is thrown when the specified resource is not ready for an
    operation. This can occur when you try to run an operation on a resource
    before CloudTrail has time to fully load the resource. If this exception
    occurs, wait a few minutes, and then try the operation again.
    """


class EventDataStoreARNInvalidException(ServiceException):
    """The specified event data store ARN is not valid or does not map to an
    event data store in your account.
    """


class EventDataStoreAlreadyExistsException(ServiceException):
    """An event data store with that name already exists."""


class EventDataStoreMaxLimitExceededException(ServiceException):
    """Your account has used the maximum number of event data stores."""


class EventDataStoreNotFoundException(ServiceException):
    """The specified event data store was not found."""


class EventDataStoreTerminationProtectedException(ServiceException):
    """The event data store cannot be deleted because termination protection is
    enabled for it.
    """


class InactiveEventDataStoreException(ServiceException):
    """The event data store is inactive."""


class InactiveQueryException(ServiceException):
    """The specified query cannot be canceled because it is in the
    ``FINISHED``, ``FAILED``, ``TIMED_OUT``, or ``CANCELLED`` state.
    """


class InsightNotEnabledException(ServiceException):
    """If you run ``GetInsightSelectors`` on a trail that does not have
    Insights events enabled, the operation throws the exception
    ``InsightNotEnabledException``.
    """


class InsufficientDependencyServiceAccessPermissionException(ServiceException):
    """This exception is thrown when the IAM user or role that is used to
    create the organization resource lacks one or more required permissions
    for creating an organization resource in a required service.
    """


class InsufficientEncryptionPolicyException(ServiceException):
    """This exception is thrown when the policy on the S3 bucket or KMS key is
    not sufficient.
    """


class InsufficientS3BucketPolicyException(ServiceException):
    """This exception is thrown when the policy on the S3 bucket is not
    sufficient.
    """


class InsufficientSnsTopicPolicyException(ServiceException):
    """This exception is thrown when the policy on the Amazon SNS topic is not
    sufficient.
    """


class InvalidCloudWatchLogsLogGroupArnException(ServiceException):
    """This exception is thrown when the provided CloudWatch Logs log group is
    not valid.
    """


class InvalidCloudWatchLogsRoleArnException(ServiceException):
    """This exception is thrown when the provided role is not valid."""


class InvalidDateRangeException(ServiceException):
    """A date range for the query was specified that is not valid. Be sure that
    the start time is chronologically before the end time. For more
    information about writing a query, see `Create or edit a
    query <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/query-create-edit-query.html>`__
    in the *CloudTrail User Guide*.
    """


class InvalidEventCategoryException(ServiceException):
    """Occurs if an event category that is not valid is specified as a value of
    ``EventCategory``.
    """


class InvalidEventDataStoreStatusException(ServiceException):
    """The event data store is not in a status that supports the operation."""


class InvalidEventSelectorsException(ServiceException):
    """This exception is thrown when the ``PutEventSelectors`` operation is
    called with a number of event selectors, advanced event selectors, or
    data resources that is not valid. The combination of event selectors or
    advanced event selectors and data resources is not valid. A trail can
    have up to 5 event selectors. If a trail uses advanced event selectors,
    a maximum of 500 total values for all conditions in all advanced event
    selectors is allowed. A trail is limited to 250 data resources. These
    data resources can be distributed across event selectors, but the
    overall total cannot exceed 250.

    You can:

    -  Specify a valid number of event selectors (1 to 5) for a trail.

    -  Specify a valid number of data resources (1 to 250) for an event
       selector. The limit of number of resources on an individual event
       selector is configurable up to 250. However, this upper limit is
       allowed only if the total number of data resources does not exceed
       250 across all event selectors for a trail.

    -  Specify up to 500 values for all conditions in all advanced event
       selectors for a trail.

    -  Specify a valid value for a parameter. For example, specifying the
       ``ReadWriteType`` parameter with a value of ``read-only`` is not
       valid.
    """


class InvalidHomeRegionException(ServiceException):
    """This exception is thrown when an operation is called on a trail from a
    region other than the region in which the trail was created.
    """


class InvalidInsightSelectorsException(ServiceException):
    """The formatting or syntax of the ``InsightSelectors`` JSON statement in
    your ``PutInsightSelectors`` or ``GetInsightSelectors`` request is not
    valid, or the specified insight type in the ``InsightSelectors``
    statement is not a valid insight type.
    """


class InvalidKmsKeyIdException(ServiceException):
    """This exception is thrown when the KMS key ARN is not valid."""


class InvalidLookupAttributesException(ServiceException):
    """Occurs when a lookup attribute is specified that is not valid."""


class InvalidMaxResultsException(ServiceException):
    """This exception is thrown if the limit specified is not valid."""


class InvalidNextTokenException(ServiceException):
    """A token that is not valid, or a token that was previously used in a
    request with different parameters. This exception is thrown if the token
    is not valid.
    """


class InvalidParameterCombinationException(ServiceException):
    """This exception is thrown when the combination of parameters provided is
    not valid.
    """


class InvalidParameterException(ServiceException):
    """The request includes a parameter that is not valid."""


class InvalidQueryStatementException(ServiceException):
    """The query that was submitted has validation errors, or uses incorrect
    syntax or unsupported keywords. For more information about writing a
    query, see `Create or edit a
    query <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/query-create-edit-query.html>`__
    in the *CloudTrail User Guide*.
    """


class InvalidQueryStatusException(ServiceException):
    """The query status is not valid for the operation."""


class InvalidS3BucketNameException(ServiceException):
    """This exception is thrown when the provided S3 bucket name is not valid."""


class InvalidS3PrefixException(ServiceException):
    """This exception is thrown when the provided S3 prefix is not valid."""


class InvalidSnsTopicNameException(ServiceException):
    """This exception is thrown when the provided SNS topic name is not valid."""


class InvalidTagParameterException(ServiceException):
    """This exception is thrown when the specified tag key or values are not
    valid. It can also occur if there are duplicate tags or too many tags on
    the resource.
    """


class InvalidTimeRangeException(ServiceException):
    """Occurs if the timestamp values are not valid. Either the start time
    occurs after the end time, or the time range is outside the range of
    possible values.
    """


class InvalidTokenException(ServiceException):
    """Reserved for future use."""


class InvalidTrailNameException(ServiceException):
    """This exception is thrown when the provided trail name is not valid.
    Trail names must meet the following requirements:

    -  Contain only ASCII letters (a-z, A-Z), numbers (0-9), periods (.),
       underscores (_), or dashes (-)

    -  Start with a letter or number, and end with a letter or number

    -  Be between 3 and 128 characters

    -  Have no adjacent periods, underscores or dashes. Names like
       ``my-_namespace`` and ``my--namespace`` are not valid.

    -  Not be in IP address format (for example, 192.168.5.4)
    """


class KmsException(ServiceException):
    """This exception is thrown when there is an issue with the specified KMS
    key and the trail can’t be updated.
    """


class KmsKeyDisabledException(ServiceException):
    """This exception is no longer in use."""


class KmsKeyNotFoundException(ServiceException):
    """This exception is thrown when the KMS key does not exist, when the S3
    bucket and the KMS key are not in the same region, or when the KMS key
    associated with the Amazon SNS topic either does not exist or is not in
    the same region.
    """


class MaxConcurrentQueriesException(ServiceException):
    """You are already running the maximum number of concurrent queries. Wait a
    minute for some queries to finish, and then run the query again.
    """


class MaximumNumberOfTrailsExceededException(ServiceException):
    """This exception is thrown when the maximum number of trails is reached."""


class NotOrganizationMasterAccountException(ServiceException):
    """This exception is thrown when the Amazon Web Services account making the
    request to create or update an organization trail or event data store is
    not the management account for an organization in Organizations. For
    more information, see `Prepare For Creating a Trail For Your
    Organization <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-an-organizational-trail-prepare.html>`__
    or `Create an event data
    store <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/query-event-data-store.html>`__.
    """


class OperationNotPermittedException(ServiceException):
    """This exception is thrown when the requested operation is not permitted."""


class OrganizationNotInAllFeaturesModeException(ServiceException):
    """This exception is thrown when Organizations is not configured to support
    all features. All features must be enabled in Organizations to support
    creating an organization trail or event data store.
    """


class OrganizationsNotInUseException(ServiceException):
    """This exception is thrown when the request is made from an Amazon Web
    Services account that is not a member of an organization. To make this
    request, sign in using the credentials of an account that belongs to an
    organization.
    """


class QueryIdNotFoundException(ServiceException):
    """The query ID does not exist or does not map to a query."""


class ResourceNotFoundException(ServiceException):
    """This exception is thrown when the specified resource is not found."""


class ResourceTypeNotSupportedException(ServiceException):
    """This exception is thrown when the specified resource type is not
    supported by CloudTrail.
    """


class S3BucketDoesNotExistException(ServiceException):
    """This exception is thrown when the specified S3 bucket does not exist."""


class TagsLimitExceededException(ServiceException):
    """The number of tags per trail has exceeded the permitted amount.
    Currently, the limit is 50.
    """


class TrailAlreadyExistsException(ServiceException):
    """This exception is thrown when the specified trail already exists."""


class TrailNotFoundException(ServiceException):
    """This exception is thrown when the trail with the given name is not
    found.
    """


class TrailNotProvidedException(ServiceException):
    """This exception is no longer in use."""


class UnsupportedOperationException(ServiceException):
    """This exception is thrown when the requested operation is not supported."""


class Tag(TypedDict, total=False):
    """A custom key-value pair associated with a resource such as a CloudTrail
    trail.
    """

    Key: TagKey
    Value: Optional[TagValue]


TagsList = List[Tag]


class AddTagsRequest(ServiceRequest):
    """Specifies the tags to add to a trail or event data store."""

    ResourceId: String
    TagsList: TagsList


class AddTagsResponse(TypedDict, total=False):
    """Returns the objects or data if successful. Otherwise, returns an error."""


Operator = List[OperatorValue]


class AdvancedFieldSelector(TypedDict, total=False):
    """A single selector statement in an advanced event selector."""

    Field: SelectorField
    Equals: Optional[Operator]
    StartsWith: Optional[Operator]
    EndsWith: Optional[Operator]
    NotEquals: Optional[Operator]
    NotStartsWith: Optional[Operator]
    NotEndsWith: Optional[Operator]


AdvancedFieldSelectors = List[AdvancedFieldSelector]


class AdvancedEventSelector(TypedDict, total=False):
    """Advanced event selectors let you create fine-grained selectors for the
    following CloudTrail event record ﬁelds. They help you control costs by
    logging only those events that are important to you. For more
    information about advanced event selectors, see `Logging data events for
    trails <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html>`__
    in the *CloudTrail User Guide*.

    -  ``readOnly``

    -  ``eventSource``

    -  ``eventName``

    -  ``eventCategory``

    -  ``resources.type``

    -  ``resources.ARN``

    You cannot apply both event selectors and advanced event selectors to a
    trail.
    """

    Name: Optional[SelectorName]
    FieldSelectors: AdvancedFieldSelectors


AdvancedEventSelectors = List[AdvancedEventSelector]
ByteBuffer = bytes


class CancelQueryRequest(ServiceRequest):
    EventDataStore: EventDataStoreArn
    QueryId: UUID


class CancelQueryResponse(TypedDict, total=False):
    QueryId: UUID
    QueryStatus: QueryStatus


class CreateEventDataStoreRequest(ServiceRequest):
    Name: EventDataStoreName
    AdvancedEventSelectors: Optional[AdvancedEventSelectors]
    MultiRegionEnabled: Optional[Boolean]
    OrganizationEnabled: Optional[Boolean]
    RetentionPeriod: Optional[RetentionPeriod]
    TerminationProtectionEnabled: Optional[TerminationProtectionEnabled]
    TagsList: Optional[TagsList]


Date = datetime


class CreateEventDataStoreResponse(TypedDict, total=False):
    EventDataStoreArn: Optional[EventDataStoreArn]
    Name: Optional[EventDataStoreName]
    Status: Optional[EventDataStoreStatus]
    AdvancedEventSelectors: Optional[AdvancedEventSelectors]
    MultiRegionEnabled: Optional[Boolean]
    OrganizationEnabled: Optional[Boolean]
    RetentionPeriod: Optional[RetentionPeriod]
    TerminationProtectionEnabled: Optional[TerminationProtectionEnabled]
    TagsList: Optional[TagsList]
    CreatedTimestamp: Optional[Date]
    UpdatedTimestamp: Optional[Date]


class CreateTrailRequest(ServiceRequest):
    """Specifies the settings for each trail."""

    Name: String
    S3BucketName: String
    S3KeyPrefix: Optional[String]
    SnsTopicName: Optional[String]
    IncludeGlobalServiceEvents: Optional[Boolean]
    IsMultiRegionTrail: Optional[Boolean]
    EnableLogFileValidation: Optional[Boolean]
    CloudWatchLogsLogGroupArn: Optional[String]
    CloudWatchLogsRoleArn: Optional[String]
    KmsKeyId: Optional[String]
    IsOrganizationTrail: Optional[Boolean]
    TagsList: Optional[TagsList]


class CreateTrailResponse(TypedDict, total=False):
    """Returns the objects or data listed below if successful. Otherwise,
    returns an error.
    """

    Name: Optional[String]
    S3BucketName: Optional[String]
    S3KeyPrefix: Optional[String]
    SnsTopicName: Optional[String]
    SnsTopicARN: Optional[String]
    IncludeGlobalServiceEvents: Optional[Boolean]
    IsMultiRegionTrail: Optional[Boolean]
    TrailARN: Optional[String]
    LogFileValidationEnabled: Optional[Boolean]
    CloudWatchLogsLogGroupArn: Optional[String]
    CloudWatchLogsRoleArn: Optional[String]
    KmsKeyId: Optional[String]
    IsOrganizationTrail: Optional[Boolean]


DataResourceValues = List[String]


class DataResource(TypedDict, total=False):
    """The Amazon S3 buckets, Lambda functions, or Amazon DynamoDB tables that
    you specify in your event selectors for your trail to log data events.
    Data events provide information about the resource operations performed
    on or within a resource itself. These are also known as data plane
    operations. You can specify up to 250 data resources for a trail.

    The total number of allowed data resources is 250. This number can be
    distributed between 1 and 5 event selectors, but the total cannot exceed
    250 across all selectors.

    If you are using advanced event selectors, the maximum total number of
    values for all conditions, across all advanced event selectors for the
    trail, is 500.

    The following example demonstrates how logging works when you configure
    logging of all data events for an S3 bucket named ``bucket-1``. In this
    example, the CloudTrail user specified an empty prefix, and the option
    to log both ``Read`` and ``Write`` data events.

    #. A user uploads an image file to ``bucket-1``.

    #. The ``PutObject`` API operation is an Amazon S3 object-level API. It
       is recorded as a data event in CloudTrail. Because the CloudTrail
       user specified an S3 bucket with an empty prefix, events that occur
       on any object in that bucket are logged. The trail processes and logs
       the event.

    #. A user uploads an object to an Amazon S3 bucket named
       ``arn:aws:s3:::bucket-2``.

    #. The ``PutObject`` API operation occurred for an object in an S3
       bucket that the CloudTrail user didn't specify for the trail. The
       trail doesn’t log the event.

    The following example demonstrates how logging works when you configure
    logging of Lambda data events for a Lambda function named
    *MyLambdaFunction*, but not for all Lambda functions.

    #. A user runs a script that includes a call to the *MyLambdaFunction*
       function and the *MyOtherLambdaFunction* function.

    #. The ``Invoke`` API operation on *MyLambdaFunction* is an Lambda API.
       It is recorded as a data event in CloudTrail. Because the CloudTrail
       user specified logging data events for *MyLambdaFunction*, any
       invocations of that function are logged. The trail processes and logs
       the event.

    #. The ``Invoke`` API operation on *MyOtherLambdaFunction* is an Lambda
       API. Because the CloudTrail user did not specify logging data events
       for all Lambda functions, the ``Invoke`` operation for
       *MyOtherLambdaFunction* does not match the function specified for the
       trail. The trail doesn’t log the event.
    """

    Type: Optional[String]
    Values: Optional[DataResourceValues]


DataResources = List[DataResource]


class DeleteEventDataStoreRequest(ServiceRequest):
    EventDataStore: EventDataStoreArn


class DeleteEventDataStoreResponse(TypedDict, total=False):
    pass


class DeleteTrailRequest(ServiceRequest):
    """The request that specifies the name of a trail to delete."""

    Name: String


class DeleteTrailResponse(TypedDict, total=False):
    """Returns the objects or data listed below if successful. Otherwise,
    returns an error.
    """


class DescribeQueryRequest(ServiceRequest):
    EventDataStore: EventDataStoreArn
    QueryId: UUID


Long = int


class QueryStatisticsForDescribeQuery(TypedDict, total=False):
    """Gets metadata about a query, including the number of events that were
    matched, the total number of events scanned, the query run time in
    milliseconds, and the query's creation time.
    """

    EventsMatched: Optional[Long]
    EventsScanned: Optional[Long]
    BytesScanned: Optional[Long]
    ExecutionTimeInMillis: Optional[Integer]
    CreationTime: Optional[Date]


class DescribeQueryResponse(TypedDict, total=False):
    QueryId: Optional[UUID]
    QueryString: Optional[QueryStatement]
    QueryStatus: Optional[QueryStatus]
    QueryStatistics: Optional[QueryStatisticsForDescribeQuery]
    ErrorMessage: Optional[ErrorMessage]


TrailNameList = List[String]


class DescribeTrailsRequest(ServiceRequest):
    """Returns information about the trail."""

    trailNameList: Optional[TrailNameList]
    includeShadowTrails: Optional[Boolean]


class Trail(TypedDict, total=False):
    """The settings for a trail."""

    Name: Optional[String]
    S3BucketName: Optional[String]
    S3KeyPrefix: Optional[String]
    SnsTopicName: Optional[String]
    SnsTopicARN: Optional[String]
    IncludeGlobalServiceEvents: Optional[Boolean]
    IsMultiRegionTrail: Optional[Boolean]
    HomeRegion: Optional[String]
    TrailARN: Optional[String]
    LogFileValidationEnabled: Optional[Boolean]
    CloudWatchLogsLogGroupArn: Optional[String]
    CloudWatchLogsRoleArn: Optional[String]
    KmsKeyId: Optional[String]
    HasCustomEventSelectors: Optional[Boolean]
    HasInsightSelectors: Optional[Boolean]
    IsOrganizationTrail: Optional[Boolean]


TrailList = List[Trail]


class DescribeTrailsResponse(TypedDict, total=False):
    """Returns the objects or data listed below if successful. Otherwise,
    returns an error.
    """

    trailList: Optional[TrailList]


class Resource(TypedDict, total=False):
    """Specifies the type and name of a resource referenced by an event."""

    ResourceType: Optional[String]
    ResourceName: Optional[String]


ResourceList = List[Resource]


class Event(TypedDict, total=False):
    """Contains information about an event that was returned by a lookup
    request. The result includes a representation of a CloudTrail event.
    """

    EventId: Optional[String]
    EventName: Optional[String]
    ReadOnly: Optional[String]
    AccessKeyId: Optional[String]
    EventTime: Optional[Date]
    EventSource: Optional[String]
    Username: Optional[String]
    Resources: Optional[ResourceList]
    CloudTrailEvent: Optional[String]


class EventDataStore(TypedDict, total=False):
    """A storage lake of event data against which you can run complex SQL-based
    queries. An event data store can include events that you have logged on
    your account from the last 90 to 2555 days (about three months to up to
    seven years). To select events for an event data store, use `advanced
    event
    selectors <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html#creating-data-event-selectors-advanced>`__.
    """

    EventDataStoreArn: Optional[EventDataStoreArn]
    Name: Optional[EventDataStoreName]
    TerminationProtectionEnabled: Optional[TerminationProtectionEnabled]
    Status: Optional[EventDataStoreStatus]
    AdvancedEventSelectors: Optional[AdvancedEventSelectors]
    MultiRegionEnabled: Optional[Boolean]
    OrganizationEnabled: Optional[Boolean]
    RetentionPeriod: Optional[RetentionPeriod]
    CreatedTimestamp: Optional[Date]
    UpdatedTimestamp: Optional[Date]


EventDataStores = List[EventDataStore]
ExcludeManagementEventSources = List[String]


class EventSelector(TypedDict, total=False):
    """Use event selectors to further specify the management and data event
    settings for your trail. By default, trails created without specific
    event selectors will be configured to log all read and write management
    events, and no data events. When an event occurs in your account,
    CloudTrail evaluates the event selector for all trails. For each trail,
    if the event matches any event selector, the trail processes and logs
    the event. If the event doesn't match any event selector, the trail
    doesn't log the event.

    You can configure up to five event selectors for a trail.

    You cannot apply both event selectors and advanced event selectors to a
    trail.
    """

    ReadWriteType: Optional[ReadWriteType]
    IncludeManagementEvents: Optional[Boolean]
    DataResources: Optional[DataResources]
    ExcludeManagementEventSources: Optional[ExcludeManagementEventSources]


EventSelectors = List[EventSelector]
EventsList = List[Event]


class GetEventDataStoreRequest(ServiceRequest):
    EventDataStore: EventDataStoreArn


class GetEventDataStoreResponse(TypedDict, total=False):
    EventDataStoreArn: Optional[EventDataStoreArn]
    Name: Optional[EventDataStoreName]
    Status: Optional[EventDataStoreStatus]
    AdvancedEventSelectors: Optional[AdvancedEventSelectors]
    MultiRegionEnabled: Optional[Boolean]
    OrganizationEnabled: Optional[Boolean]
    RetentionPeriod: Optional[RetentionPeriod]
    TerminationProtectionEnabled: Optional[TerminationProtectionEnabled]
    CreatedTimestamp: Optional[Date]
    UpdatedTimestamp: Optional[Date]


class GetEventSelectorsRequest(ServiceRequest):
    TrailName: String


class GetEventSelectorsResponse(TypedDict, total=False):
    TrailARN: Optional[String]
    EventSelectors: Optional[EventSelectors]
    AdvancedEventSelectors: Optional[AdvancedEventSelectors]


class GetInsightSelectorsRequest(ServiceRequest):
    TrailName: String


class InsightSelector(TypedDict, total=False):
    """A JSON string that contains a list of insight types that are logged on a
    trail.
    """

    InsightType: Optional[InsightType]


InsightSelectors = List[InsightSelector]


class GetInsightSelectorsResponse(TypedDict, total=False):
    TrailARN: Optional[String]
    InsightSelectors: Optional[InsightSelectors]


class GetQueryResultsRequest(ServiceRequest):
    EventDataStore: EventDataStoreArn
    QueryId: UUID
    NextToken: Optional[PaginationToken]
    MaxQueryResults: Optional[MaxQueryResults]


QueryResultColumn = Dict[QueryResultKey, QueryResultValue]
QueryResultRow = List[QueryResultColumn]
QueryResultRows = List[QueryResultRow]


class QueryStatistics(TypedDict, total=False):
    """Metadata about a query, such as the number of results."""

    ResultsCount: Optional[Integer]
    TotalResultsCount: Optional[Integer]
    BytesScanned: Optional[Long]


class GetQueryResultsResponse(TypedDict, total=False):
    QueryStatus: Optional[QueryStatus]
    QueryStatistics: Optional[QueryStatistics]
    QueryResultRows: Optional[QueryResultRows]
    NextToken: Optional[PaginationToken]
    ErrorMessage: Optional[ErrorMessage]


class GetTrailRequest(ServiceRequest):
    Name: String


class GetTrailResponse(TypedDict, total=False):
    Trail: Optional[Trail]


class GetTrailStatusRequest(ServiceRequest):
    """The name of a trail about which you want the current status."""

    Name: String


class GetTrailStatusResponse(TypedDict, total=False):
    """Returns the objects or data listed below if successful. Otherwise,
    returns an error.
    """

    IsLogging: Optional[Boolean]
    LatestDeliveryError: Optional[String]
    LatestNotificationError: Optional[String]
    LatestDeliveryTime: Optional[Date]
    LatestNotificationTime: Optional[Date]
    StartLoggingTime: Optional[Date]
    StopLoggingTime: Optional[Date]
    LatestCloudWatchLogsDeliveryError: Optional[String]
    LatestCloudWatchLogsDeliveryTime: Optional[Date]
    LatestDigestDeliveryTime: Optional[Date]
    LatestDigestDeliveryError: Optional[String]
    LatestDeliveryAttemptTime: Optional[String]
    LatestNotificationAttemptTime: Optional[String]
    LatestNotificationAttemptSucceeded: Optional[String]
    LatestDeliveryAttemptSucceeded: Optional[String]
    TimeLoggingStarted: Optional[String]
    TimeLoggingStopped: Optional[String]


class ListEventDataStoresRequest(ServiceRequest):
    NextToken: Optional[PaginationToken]
    MaxResults: Optional[ListEventDataStoresMaxResultsCount]


class ListEventDataStoresResponse(TypedDict, total=False):
    EventDataStores: Optional[EventDataStores]
    NextToken: Optional[PaginationToken]


class ListPublicKeysRequest(ServiceRequest):
    """Requests the public keys for a specified time range."""

    StartTime: Optional[Date]
    EndTime: Optional[Date]
    NextToken: Optional[String]


class PublicKey(TypedDict, total=False):
    """Contains information about a returned public key."""

    Value: Optional[ByteBuffer]
    ValidityStartTime: Optional[Date]
    ValidityEndTime: Optional[Date]
    Fingerprint: Optional[String]


PublicKeyList = List[PublicKey]


class ListPublicKeysResponse(TypedDict, total=False):
    """Returns the objects or data listed below if successful. Otherwise,
    returns an error.
    """

    PublicKeyList: Optional[PublicKeyList]
    NextToken: Optional[String]


class ListQueriesRequest(ServiceRequest):
    EventDataStore: EventDataStoreArn
    NextToken: Optional[PaginationToken]
    MaxResults: Optional[ListQueriesMaxResultsCount]
    StartTime: Optional[Date]
    EndTime: Optional[Date]
    QueryStatus: Optional[QueryStatus]


class Query(TypedDict, total=False):
    """A SQL string of criteria about events that you want to collect in an
    event data store.
    """

    QueryId: Optional[UUID]
    QueryStatus: Optional[QueryStatus]
    CreationTime: Optional[Date]


Queries = List[Query]


class ListQueriesResponse(TypedDict, total=False):
    Queries: Optional[Queries]
    NextToken: Optional[PaginationToken]


ResourceIdList = List[String]


class ListTagsRequest(ServiceRequest):
    """Specifies a list of tags to return."""

    ResourceIdList: ResourceIdList
    NextToken: Optional[String]


class ResourceTag(TypedDict, total=False):
    """A resource tag."""

    ResourceId: Optional[String]
    TagsList: Optional[TagsList]


ResourceTagList = List[ResourceTag]


class ListTagsResponse(TypedDict, total=False):
    """Returns the objects or data listed below if successful. Otherwise,
    returns an error.
    """

    ResourceTagList: Optional[ResourceTagList]
    NextToken: Optional[String]


class ListTrailsRequest(ServiceRequest):
    NextToken: Optional[String]


class TrailInfo(TypedDict, total=False):
    """Information about a CloudTrail trail, including the trail's name, home
    region, and Amazon Resource Name (ARN).
    """

    TrailARN: Optional[String]
    Name: Optional[String]
    HomeRegion: Optional[String]


Trails = List[TrailInfo]


class ListTrailsResponse(TypedDict, total=False):
    Trails: Optional[Trails]
    NextToken: Optional[String]


class LookupAttribute(TypedDict, total=False):
    """Specifies an attribute and value that filter the events returned."""

    AttributeKey: LookupAttributeKey
    AttributeValue: String


LookupAttributesList = List[LookupAttribute]


class LookupEventsRequest(ServiceRequest):
    """Contains a request for LookupEvents."""

    LookupAttributes: Optional[LookupAttributesList]
    StartTime: Optional[Date]
    EndTime: Optional[Date]
    EventCategory: Optional[EventCategory]
    MaxResults: Optional[MaxResults]
    NextToken: Optional[NextToken]


class LookupEventsResponse(TypedDict, total=False):
    """Contains a response to a LookupEvents action."""

    Events: Optional[EventsList]
    NextToken: Optional[NextToken]


class PutEventSelectorsRequest(ServiceRequest):
    TrailName: String
    EventSelectors: Optional[EventSelectors]
    AdvancedEventSelectors: Optional[AdvancedEventSelectors]


class PutEventSelectorsResponse(TypedDict, total=False):
    TrailARN: Optional[String]
    EventSelectors: Optional[EventSelectors]
    AdvancedEventSelectors: Optional[AdvancedEventSelectors]


class PutInsightSelectorsRequest(ServiceRequest):
    TrailName: String
    InsightSelectors: InsightSelectors


class PutInsightSelectorsResponse(TypedDict, total=False):
    TrailARN: Optional[String]
    InsightSelectors: Optional[InsightSelectors]


class RemoveTagsRequest(ServiceRequest):
    """Specifies the tags to remove from a trail or event data store."""

    ResourceId: String
    TagsList: TagsList


class RemoveTagsResponse(TypedDict, total=False):
    """Returns the objects or data listed below if successful. Otherwise,
    returns an error.
    """


class RestoreEventDataStoreRequest(ServiceRequest):
    EventDataStore: EventDataStoreArn


class RestoreEventDataStoreResponse(TypedDict, total=False):
    EventDataStoreArn: Optional[EventDataStoreArn]
    Name: Optional[EventDataStoreName]
    Status: Optional[EventDataStoreStatus]
    AdvancedEventSelectors: Optional[AdvancedEventSelectors]
    MultiRegionEnabled: Optional[Boolean]
    OrganizationEnabled: Optional[Boolean]
    RetentionPeriod: Optional[RetentionPeriod]
    TerminationProtectionEnabled: Optional[TerminationProtectionEnabled]
    CreatedTimestamp: Optional[Date]
    UpdatedTimestamp: Optional[Date]


class StartLoggingRequest(ServiceRequest):
    """The request to CloudTrail to start logging Amazon Web Services API calls
    for an account.
    """

    Name: String


class StartLoggingResponse(TypedDict, total=False):
    """Returns the objects or data listed below if successful. Otherwise,
    returns an error.
    """


class StartQueryRequest(ServiceRequest):
    QueryStatement: QueryStatement


class StartQueryResponse(TypedDict, total=False):
    QueryId: Optional[UUID]


class StopLoggingRequest(ServiceRequest):
    """Passes the request to CloudTrail to stop logging Amazon Web Services API
    calls for the specified account.
    """

    Name: String


class StopLoggingResponse(TypedDict, total=False):
    """Returns the objects or data listed below if successful. Otherwise,
    returns an error.
    """


class UpdateEventDataStoreRequest(ServiceRequest):
    EventDataStore: EventDataStoreArn
    Name: Optional[EventDataStoreName]
    AdvancedEventSelectors: Optional[AdvancedEventSelectors]
    MultiRegionEnabled: Optional[Boolean]
    OrganizationEnabled: Optional[Boolean]
    RetentionPeriod: Optional[RetentionPeriod]
    TerminationProtectionEnabled: Optional[TerminationProtectionEnabled]


class UpdateEventDataStoreResponse(TypedDict, total=False):
    EventDataStoreArn: Optional[EventDataStoreArn]
    Name: Optional[EventDataStoreName]
    Status: Optional[EventDataStoreStatus]
    AdvancedEventSelectors: Optional[AdvancedEventSelectors]
    MultiRegionEnabled: Optional[Boolean]
    OrganizationEnabled: Optional[Boolean]
    RetentionPeriod: Optional[RetentionPeriod]
    TerminationProtectionEnabled: Optional[TerminationProtectionEnabled]
    CreatedTimestamp: Optional[Date]
    UpdatedTimestamp: Optional[Date]


class UpdateTrailRequest(ServiceRequest):
    """Specifies settings to update for the trail."""

    Name: String
    S3BucketName: Optional[String]
    S3KeyPrefix: Optional[String]
    SnsTopicName: Optional[String]
    IncludeGlobalServiceEvents: Optional[Boolean]
    IsMultiRegionTrail: Optional[Boolean]
    EnableLogFileValidation: Optional[Boolean]
    CloudWatchLogsLogGroupArn: Optional[String]
    CloudWatchLogsRoleArn: Optional[String]
    KmsKeyId: Optional[String]
    IsOrganizationTrail: Optional[Boolean]


class UpdateTrailResponse(TypedDict, total=False):
    """Returns the objects or data listed below if successful. Otherwise,
    returns an error.
    """

    Name: Optional[String]
    S3BucketName: Optional[String]
    S3KeyPrefix: Optional[String]
    SnsTopicName: Optional[String]
    SnsTopicARN: Optional[String]
    IncludeGlobalServiceEvents: Optional[Boolean]
    IsMultiRegionTrail: Optional[Boolean]
    TrailARN: Optional[String]
    LogFileValidationEnabled: Optional[Boolean]
    CloudWatchLogsLogGroupArn: Optional[String]
    CloudWatchLogsRoleArn: Optional[String]
    KmsKeyId: Optional[String]
    IsOrganizationTrail: Optional[Boolean]


class CloudtrailApi:

    service = "cloudtrail"
    version = "2013-11-01"

    @handler("AddTags")
    def add_tags(
        self, context: RequestContext, resource_id: String, tags_list: TagsList
    ) -> AddTagsResponse:
        """Adds one or more tags to a trail or event data store, up to a limit of
        50. Overwrites an existing tag's value when a new value is specified for
        an existing tag key. Tag key names must be unique for a trail; you
        cannot have two keys with the same name but different values. If you
        specify a key without a value, the tag will be created with the
        specified key and a value of null. You can tag a trail or event data
        store that applies to all Amazon Web Services Regions only from the
        Region in which the trail or event data store was created (also known as
        its home region).

        :param resource_id: Specifies the ARN of the trail or event data store to which one or more
        tags will be added.
        :param tags_list: Contains a list of tags, up to a limit of 50.
        :returns: AddTagsResponse
        :raises ResourceNotFoundException:
        :raises CloudTrailARNInvalidException:
        :raises ResourceTypeNotSupportedException:
        :raises TagsLimitExceededException:
        :raises InvalidTrailNameException:
        :raises InvalidTagParameterException:
        :raises InactiveEventDataStoreException:
        :raises EventDataStoreNotFoundException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises NotOrganizationMasterAccountException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CancelQuery")
    def cancel_query(
        self, context: RequestContext, event_data_store: EventDataStoreArn, query_id: UUID
    ) -> CancelQueryResponse:
        """Cancels a query if the query is not in a terminated state, such as
        ``CANCELLED``, ``FAILED``, ``TIMED_OUT``, or ``FINISHED``. You must
        specify an ARN value for ``EventDataStore``. The ID of the query that
        you want to cancel is also required. When you run ``CancelQuery``, the
        query status might show as ``CANCELLED`` even if the operation is not
        yet finished.

        :param event_data_store: The ARN (or the ID suffix of the ARN) of an event data store on which
        the specified query is running.
        :param query_id: The ID of the query that you want to cancel.
        :returns: CancelQueryResponse
        :raises EventDataStoreARNInvalidException:
        :raises EventDataStoreNotFoundException:
        :raises InactiveEventDataStoreException:
        :raises InactiveQueryException:
        :raises InvalidParameterException:
        :raises QueryIdNotFoundException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("CreateEventDataStore")
    def create_event_data_store(
        self,
        context: RequestContext,
        name: EventDataStoreName,
        advanced_event_selectors: AdvancedEventSelectors = None,
        multi_region_enabled: Boolean = None,
        organization_enabled: Boolean = None,
        retention_period: RetentionPeriod = None,
        termination_protection_enabled: TerminationProtectionEnabled = None,
        tags_list: TagsList = None,
    ) -> CreateEventDataStoreResponse:
        """Creates a new event data store.

        :param name: The name of the event data store.
        :param advanced_event_selectors: The advanced event selectors to use to select the events for the data
        store.
        :param multi_region_enabled: Specifies whether the event data store includes events from all regions,
        or only from the region in which the event data store is created.
        :param organization_enabled: Specifies whether an event data store collects events logged for an
        organization in Organizations.
        :param retention_period: The retention period of the event data store, in days.
        :param termination_protection_enabled: Specifies whether termination protection is enabled for the event data
        store.
        :param tags_list: A list of tags.
        :returns: CreateEventDataStoreResponse
        :raises EventDataStoreAlreadyExistsException:
        :raises EventDataStoreMaxLimitExceededException:
        :raises InvalidParameterException:
        :raises InvalidTagParameterException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        :raises ConflictException:
        :raises CloudTrailAccessNotEnabledException:
        :raises InsufficientDependencyServiceAccessPermissionException:
        :raises NotOrganizationMasterAccountException:
        :raises OrganizationsNotInUseException:
        :raises OrganizationNotInAllFeaturesModeException:
        """
        raise NotImplementedError

    @handler("CreateTrail")
    def create_trail(
        self,
        context: RequestContext,
        name: String,
        s3_bucket_name: String,
        s3_key_prefix: String = None,
        sns_topic_name: String = None,
        include_global_service_events: Boolean = None,
        is_multi_region_trail: Boolean = None,
        enable_log_file_validation: Boolean = None,
        cloud_watch_logs_log_group_arn: String = None,
        cloud_watch_logs_role_arn: String = None,
        kms_key_id: String = None,
        is_organization_trail: Boolean = None,
        tags_list: TagsList = None,
    ) -> CreateTrailResponse:
        """Creates a trail that specifies the settings for delivery of log data to
        an Amazon S3 bucket.

        :param name: Specifies the name of the trail.
        :param s3_bucket_name: Specifies the name of the Amazon S3 bucket designated for publishing log
        files.
        :param s3_key_prefix: Specifies the Amazon S3 key prefix that comes after the name of the
        bucket you have designated for log file delivery.
        :param sns_topic_name: Specifies the name of the Amazon SNS topic defined for notification of
        log file delivery.
        :param include_global_service_events: Specifies whether the trail is publishing events from global services
        such as IAM to the log files.
        :param is_multi_region_trail: Specifies whether the trail is created in the current region or in all
        regions.
        :param enable_log_file_validation: Specifies whether log file integrity validation is enabled.
        :param cloud_watch_logs_log_group_arn: Specifies a log group name using an Amazon Resource Name (ARN), a unique
        identifier that represents the log group to which CloudTrail logs will
        be delivered.
        :param cloud_watch_logs_role_arn: Specifies the role for the CloudWatch Logs endpoint to assume to write
        to a user's log group.
        :param kms_key_id: Specifies the KMS key ID to use to encrypt the logs delivered by
        CloudTrail.
        :param is_organization_trail: Specifies whether the trail is created for all accounts in an
        organization in Organizations, or only for the current Amazon Web
        Services account.
        :param tags_list: A list of tags.
        :returns: CreateTrailResponse
        :raises MaximumNumberOfTrailsExceededException:
        :raises TrailAlreadyExistsException:
        :raises S3BucketDoesNotExistException:
        :raises InsufficientS3BucketPolicyException:
        :raises InsufficientSnsTopicPolicyException:
        :raises InsufficientEncryptionPolicyException:
        :raises InvalidS3BucketNameException:
        :raises InvalidS3PrefixException:
        :raises InvalidSnsTopicNameException:
        :raises InvalidKmsKeyIdException:
        :raises InvalidTrailNameException:
        :raises TrailNotProvidedException:
        :raises InvalidParameterCombinationException:
        :raises KmsKeyNotFoundException:
        :raises KmsKeyDisabledException:
        :raises KmsException:
        :raises InvalidCloudWatchLogsLogGroupArnException:
        :raises InvalidCloudWatchLogsRoleArnException:
        :raises CloudWatchLogsDeliveryUnavailableException:
        :raises InvalidTagParameterException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises CloudTrailAccessNotEnabledException:
        :raises InsufficientDependencyServiceAccessPermissionException:
        :raises NotOrganizationMasterAccountException:
        :raises OrganizationsNotInUseException:
        :raises OrganizationNotInAllFeaturesModeException:
        :raises CloudTrailInvalidClientTokenIdException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("DeleteEventDataStore")
    def delete_event_data_store(
        self, context: RequestContext, event_data_store: EventDataStoreArn
    ) -> DeleteEventDataStoreResponse:
        """Disables the event data store specified by ``EventDataStore``, which
        accepts an event data store ARN. After you run ``DeleteEventDataStore``,
        the event data store enters a ``PENDING_DELETION`` state, and is
        automatically deleted after a wait period of seven days.
        ``TerminationProtectionEnabled`` must be set to ``False`` on the event
        data store; this operation cannot work if
        ``TerminationProtectionEnabled`` is ``True``.

        After you run ``DeleteEventDataStore`` on an event data store, you
        cannot run ``ListQueries``, ``DescribeQuery``, or ``GetQueryResults`` on
        queries that are using an event data store in a ``PENDING_DELETION``
        state. An event data store in the ``PENDING_DELETION`` state does not
        incur costs.

        :param event_data_store: The ARN (or the ID suffix of the ARN) of the event data store to delete.
        :returns: DeleteEventDataStoreResponse
        :raises EventDataStoreARNInvalidException:
        :raises EventDataStoreNotFoundException:
        :raises EventDataStoreTerminationProtectedException:
        :raises InvalidParameterException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        :raises NotOrganizationMasterAccountException:
        :raises InsufficientDependencyServiceAccessPermissionException:
        """
        raise NotImplementedError

    @handler("DeleteTrail")
    def delete_trail(self, context: RequestContext, name: String) -> DeleteTrailResponse:
        """Deletes a trail. This operation must be called from the region in which
        the trail was created. ``DeleteTrail`` cannot be called on the shadow
        trails (replicated trails in other regions) of a trail that is enabled
        in all regions.

        :param name: Specifies the name or the CloudTrail ARN of the trail to be deleted.
        :returns: DeleteTrailResponse
        :raises TrailNotFoundException:
        :raises InvalidTrailNameException:
        :raises InvalidHomeRegionException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises NotOrganizationMasterAccountException:
        :raises InsufficientDependencyServiceAccessPermissionException:
        :raises ConflictException:
        """
        raise NotImplementedError

    @handler("DescribeQuery")
    def describe_query(
        self, context: RequestContext, event_data_store: EventDataStoreArn, query_id: UUID
    ) -> DescribeQueryResponse:
        """Returns metadata about a query, including query run time in
        milliseconds, number of events scanned and matched, and query status.
        You must specify an ARN for ``EventDataStore``, and a value for
        ``QueryID``.

        :param event_data_store: The ARN (or the ID suffix of the ARN) of an event data store on which
        the specified query was run.
        :param query_id: The query ID.
        :returns: DescribeQueryResponse
        :raises EventDataStoreARNInvalidException:
        :raises EventDataStoreNotFoundException:
        :raises InactiveEventDataStoreException:
        :raises InvalidParameterException:
        :raises QueryIdNotFoundException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        """
        raise NotImplementedError

    @handler("DescribeTrails")
    def describe_trails(
        self,
        context: RequestContext,
        trail_name_list: TrailNameList = None,
        include_shadow_trails: Boolean = None,
    ) -> DescribeTrailsResponse:
        """Retrieves settings for one or more trails associated with the current
        region for your account.

        :param trail_name_list: Specifies a list of trail names, trail ARNs, or both, of the trails to
        describe.
        :param include_shadow_trails: Specifies whether to include shadow trails in the response.
        :returns: DescribeTrailsResponse
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises InvalidTrailNameException:
        """
        raise NotImplementedError

    @handler("GetEventDataStore")
    def get_event_data_store(
        self, context: RequestContext, event_data_store: EventDataStoreArn
    ) -> GetEventDataStoreResponse:
        """Returns information about an event data store specified as either an ARN
        or the ID portion of the ARN.

        :param event_data_store: The ARN (or ID suffix of the ARN) of the event data store about which
        you want information.
        :returns: GetEventDataStoreResponse
        :raises EventDataStoreARNInvalidException:
        :raises EventDataStoreNotFoundException:
        :raises InvalidParameterException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        """
        raise NotImplementedError

    @handler("GetEventSelectors")
    def get_event_selectors(
        self, context: RequestContext, trail_name: String
    ) -> GetEventSelectorsResponse:
        """Describes the settings for the event selectors that you configured for
        your trail. The information returned for your event selectors includes
        the following:

        -  If your event selector includes read-only events, write-only events,
           or all events. This applies to both management events and data
           events.

        -  If your event selector includes management events.

        -  If your event selector includes data events, the resources on which
           you are logging data events.

        For more information, see `Logging Data and Management Events for
        Trails <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-management-and-data-events-with-cloudtrail.html>`__
        in the *CloudTrail User Guide*.

        :param trail_name: Specifies the name of the trail or trail ARN.
        :returns: GetEventSelectorsResponse
        :raises TrailNotFoundException:
        :raises InvalidTrailNameException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        """
        raise NotImplementedError

    @handler("GetInsightSelectors")
    def get_insight_selectors(
        self, context: RequestContext, trail_name: String
    ) -> GetInsightSelectorsResponse:
        """Describes the settings for the Insights event selectors that you
        configured for your trail. ``GetInsightSelectors`` shows if CloudTrail
        Insights event logging is enabled on the trail, and if it is, which
        insight types are enabled. If you run ``GetInsightSelectors`` on a trail
        that does not have Insights events enabled, the operation throws the
        exception ``InsightNotEnabledException``

        For more information, see `Logging CloudTrail Insights Events for
        Trails <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-insights-events-with-cloudtrail.html>`__
        in the *CloudTrail User Guide*.

        :param trail_name: Specifies the name of the trail or trail ARN.
        :returns: GetInsightSelectorsResponse
        :raises TrailNotFoundException:
        :raises InvalidTrailNameException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises InsightNotEnabledException:
        """
        raise NotImplementedError

    @handler("GetQueryResults")
    def get_query_results(
        self,
        context: RequestContext,
        event_data_store: EventDataStoreArn,
        query_id: UUID,
        next_token: PaginationToken = None,
        max_query_results: MaxQueryResults = None,
    ) -> GetQueryResultsResponse:
        """Gets event data results of a query. You must specify the ``QueryID``
        value returned by the ``StartQuery`` operation, and an ARN for
        ``EventDataStore``.

        :param event_data_store: The ARN (or ID suffix of the ARN) of the event data store against which
        the query was run.
        :param query_id: The ID of the query for which you want to get results.
        :param next_token: A token you can use to get the next page of query results.
        :param max_query_results: The maximum number of query results to display on a single page.
        :returns: GetQueryResultsResponse
        :raises EventDataStoreARNInvalidException:
        :raises EventDataStoreNotFoundException:
        :raises InactiveEventDataStoreException:
        :raises InvalidMaxResultsException:
        :raises InvalidNextTokenException:
        :raises InvalidParameterException:
        :raises QueryIdNotFoundException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        """
        raise NotImplementedError

    @handler("GetTrail")
    def get_trail(self, context: RequestContext, name: String) -> GetTrailResponse:
        """Returns settings information for a specified trail.

        :param name: The name or the Amazon Resource Name (ARN) of the trail for which you
        want to retrieve settings information.
        :returns: GetTrailResponse
        :raises TrailNotFoundException:
        :raises InvalidTrailNameException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        """
        raise NotImplementedError

    @handler("GetTrailStatus")
    def get_trail_status(self, context: RequestContext, name: String) -> GetTrailStatusResponse:
        """Returns a JSON-formatted list of information about the specified trail.
        Fields include information on delivery errors, Amazon SNS and Amazon S3
        errors, and start and stop logging times for each trail. This operation
        returns trail status from a single region. To return trail status from
        all regions, you must call the operation on each region.

        :param name: Specifies the name or the CloudTrail ARN of the trail for which you are
        requesting status.
        :returns: GetTrailStatusResponse
        :raises TrailNotFoundException:
        :raises InvalidTrailNameException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        """
        raise NotImplementedError

    @handler("ListEventDataStores")
    def list_event_data_stores(
        self,
        context: RequestContext,
        next_token: PaginationToken = None,
        max_results: ListEventDataStoresMaxResultsCount = None,
    ) -> ListEventDataStoresResponse:
        """Returns information about all event data stores in the account, in the
        current region.

        :param next_token: A token you can use to get the next page of event data store results.
        :param max_results: The maximum number of event data stores to display on a single page.
        :returns: ListEventDataStoresResponse
        :raises InvalidMaxResultsException:
        :raises InvalidNextTokenException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        """
        raise NotImplementedError

    @handler("ListPublicKeys")
    def list_public_keys(
        self,
        context: RequestContext,
        start_time: Date = None,
        end_time: Date = None,
        next_token: String = None,
    ) -> ListPublicKeysResponse:
        """Returns all public keys whose private keys were used to sign the digest
        files within the specified time range. The public key is needed to
        validate digest files that were signed with its corresponding private
        key.

        CloudTrail uses different private and public key pairs per region. Each
        digest file is signed with a private key unique to its region. When you
        validate a digest file from a specific region, you must look in the same
        region for its corresponding public key.

        :param start_time: Optionally specifies, in UTC, the start of the time range to look up
        public keys for CloudTrail digest files.
        :param end_time: Optionally specifies, in UTC, the end of the time range to look up
        public keys for CloudTrail digest files.
        :param next_token: Reserved for future use.
        :returns: ListPublicKeysResponse
        :raises InvalidTimeRangeException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises InvalidTokenException:
        """
        raise NotImplementedError

    @handler("ListQueries")
    def list_queries(
        self,
        context: RequestContext,
        event_data_store: EventDataStoreArn,
        next_token: PaginationToken = None,
        max_results: ListQueriesMaxResultsCount = None,
        start_time: Date = None,
        end_time: Date = None,
        query_status: QueryStatus = None,
    ) -> ListQueriesResponse:
        """Returns a list of queries and query statuses for the past seven days.
        You must specify an ARN value for ``EventDataStore``. Optionally, to
        shorten the list of results, you can specify a time range, formatted as
        timestamps, by adding ``StartTime`` and ``EndTime`` parameters, and a
        ``QueryStatus`` value. Valid values for ``QueryStatus`` include
        ``QUEUED``, ``RUNNING``, ``FINISHED``, ``FAILED``, ``TIMED_OUT``, or
        ``CANCELLED``.

        :param event_data_store: The ARN (or the ID suffix of the ARN) of an event data store on which
        queries were run.
        :param next_token: A token you can use to get the next page of results.
        :param max_results: The maximum number of queries to show on a page.
        :param start_time: Use with ``EndTime`` to bound a ``ListQueries`` request, and limit its
        results to only those queries run within a specified time period.
        :param end_time: Use with ``StartTime`` to bound a ``ListQueries`` request, and limit its
        results to only those queries run within a specified time period.
        :param query_status: The status of queries that you want to return in results.
        :returns: ListQueriesResponse
        :raises EventDataStoreARNInvalidException:
        :raises EventDataStoreNotFoundException:
        :raises InactiveEventDataStoreException:
        :raises InvalidDateRangeException:
        :raises InvalidMaxResultsException:
        :raises InvalidNextTokenException:
        :raises InvalidParameterException:
        :raises InvalidQueryStatusException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        """
        raise NotImplementedError

    @handler("ListTags")
    def list_tags(
        self, context: RequestContext, resource_id_list: ResourceIdList, next_token: String = None
    ) -> ListTagsResponse:
        """Lists the tags for the trail or event data store in the current region.

        :param resource_id_list: Specifies a list of trail and event data store ARNs whose tags will be
        listed.
        :param next_token: Reserved for future use.
        :returns: ListTagsResponse
        :raises ResourceNotFoundException:
        :raises CloudTrailARNInvalidException:
        :raises ResourceTypeNotSupportedException:
        :raises InvalidTrailNameException:
        :raises InactiveEventDataStoreException:
        :raises EventDataStoreNotFoundException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises InvalidTokenException:
        """
        raise NotImplementedError

    @handler("ListTrails")
    def list_trails(self, context: RequestContext, next_token: String = None) -> ListTrailsResponse:
        """Lists trails that are in the current account.

        :param next_token: The token to use to get the next page of results after a previous API
        call.
        :returns: ListTrailsResponse
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        """
        raise NotImplementedError

    @handler("LookupEvents")
    def lookup_events(
        self,
        context: RequestContext,
        lookup_attributes: LookupAttributesList = None,
        start_time: Date = None,
        end_time: Date = None,
        event_category: EventCategory = None,
        max_results: MaxResults = None,
        next_token: NextToken = None,
    ) -> LookupEventsResponse:
        """Looks up `management
        events <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html#cloudtrail-concepts-management-events>`__
        or `CloudTrail Insights
        events <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html#cloudtrail-concepts-insights-events>`__
        that are captured by CloudTrail. You can look up events that occurred in
        a region within the last 90 days. Lookup supports the following
        attributes for management events:

        -  Amazon Web Services access key

        -  Event ID

        -  Event name

        -  Event source

        -  Read only

        -  Resource name

        -  Resource type

        -  User name

        Lookup supports the following attributes for Insights events:

        -  Event ID

        -  Event name

        -  Event source

        All attributes are optional. The default number of results returned is
        50, with a maximum of 50 possible. The response includes a token that
        you can use to get the next page of results.

        The rate of lookup requests is limited to two per second, per account,
        per region. If this limit is exceeded, a throttling error occurs.

        :param lookup_attributes: Contains a list of lookup attributes.
        :param start_time: Specifies that only events that occur after or at the specified time are
        returned.
        :param end_time: Specifies that only events that occur before or at the specified time
        are returned.
        :param event_category: Specifies the event category.
        :param max_results: The number of events to return.
        :param next_token: The token to use to get the next page of results after a previous API
        call.
        :returns: LookupEventsResponse
        :raises InvalidLookupAttributesException:
        :raises InvalidTimeRangeException:
        :raises InvalidMaxResultsException:
        :raises InvalidNextTokenException:
        :raises InvalidEventCategoryException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        """
        raise NotImplementedError

    @handler("PutEventSelectors")
    def put_event_selectors(
        self,
        context: RequestContext,
        trail_name: String,
        event_selectors: EventSelectors = None,
        advanced_event_selectors: AdvancedEventSelectors = None,
    ) -> PutEventSelectorsResponse:
        """Configures an event selector or advanced event selectors for your trail.
        Use event selectors or advanced event selectors to specify management
        and data event settings for your trail. By default, trails created
        without specific event selectors are configured to log all read and
        write management events, and no data events.

        When an event occurs in your account, CloudTrail evaluates the event
        selectors or advanced event selectors in all trails. For each trail, if
        the event matches any event selector, the trail processes and logs the
        event. If the event doesn't match any event selector, the trail doesn't
        log the event.

        Example

        #. You create an event selector for a trail and specify that you want
           write-only events.

        #. The EC2 ``GetConsoleOutput`` and ``RunInstances`` API operations
           occur in your account.

        #. CloudTrail evaluates whether the events match your event selectors.

        #. The ``RunInstances`` is a write-only event and it matches your event
           selector. The trail logs the event.

        #. The ``GetConsoleOutput`` is a read-only event that doesn't match your
           event selector. The trail doesn't log the event.

        The ``PutEventSelectors`` operation must be called from the region in
        which the trail was created; otherwise, an
        ``InvalidHomeRegionException`` exception is thrown.

        You can configure up to five event selectors for each trail. For more
        information, see `Logging data and management events for
        trails <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-management-and-data-events-with-cloudtrail.html>`__
        and `Quotas in
        CloudTrail <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/WhatIsCloudTrail-Limits.html>`__
        in the *CloudTrail User Guide*.

        You can add advanced event selectors, and conditions for your advanced
        event selectors, up to a maximum of 500 values for all conditions and
        selectors on a trail. You can use either ``AdvancedEventSelectors`` or
        ``EventSelectors``, but not both. If you apply
        ``AdvancedEventSelectors`` to a trail, any existing ``EventSelectors``
        are overwritten. For more information about advanced event selectors,
        see `Logging data events for
        trails <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html>`__
        in the *CloudTrail User Guide*.

        :param trail_name: Specifies the name of the trail or trail ARN.
        :param event_selectors: Specifies the settings for your event selectors.
        :param advanced_event_selectors: Specifies the settings for advanced event selectors.
        :returns: PutEventSelectorsResponse
        :raises TrailNotFoundException:
        :raises InvalidTrailNameException:
        :raises InvalidHomeRegionException:
        :raises InvalidEventSelectorsException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises NotOrganizationMasterAccountException:
        :raises InsufficientDependencyServiceAccessPermissionException:
        """
        raise NotImplementedError

    @handler("PutInsightSelectors")
    def put_insight_selectors(
        self, context: RequestContext, trail_name: String, insight_selectors: InsightSelectors
    ) -> PutInsightSelectorsResponse:
        """Lets you enable Insights event logging by specifying the Insights
        selectors that you want to enable on an existing trail. You also use
        ``PutInsightSelectors`` to turn off Insights event logging, by passing
        an empty list of insight types. The valid Insights event types in this
        release are ``ApiErrorRateInsight`` and ``ApiCallRateInsight``.

        :param trail_name: The name of the CloudTrail trail for which you want to change or add
        Insights selectors.
        :param insight_selectors: A JSON string that contains the insight types you want to log on a
        trail.
        :returns: PutInsightSelectorsResponse
        :raises TrailNotFoundException:
        :raises InvalidTrailNameException:
        :raises InvalidHomeRegionException:
        :raises InvalidInsightSelectorsException:
        :raises InsufficientS3BucketPolicyException:
        :raises InsufficientEncryptionPolicyException:
        :raises S3BucketDoesNotExistException:
        :raises KmsException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises NotOrganizationMasterAccountException:
        """
        raise NotImplementedError

    @handler("RemoveTags")
    def remove_tags(
        self, context: RequestContext, resource_id: String, tags_list: TagsList
    ) -> RemoveTagsResponse:
        """Removes the specified tags from a trail or event data store.

        :param resource_id: Specifies the ARN of the trail or event data store from which tags
        should be removed.
        :param tags_list: Specifies a list of tags to be removed.
        :returns: RemoveTagsResponse
        :raises ResourceNotFoundException:
        :raises CloudTrailARNInvalidException:
        :raises ResourceTypeNotSupportedException:
        :raises InvalidTrailNameException:
        :raises InvalidTagParameterException:
        :raises InactiveEventDataStoreException:
        :raises EventDataStoreNotFoundException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises NotOrganizationMasterAccountException:
        """
        raise NotImplementedError

    @handler("RestoreEventDataStore")
    def restore_event_data_store(
        self, context: RequestContext, event_data_store: EventDataStoreArn
    ) -> RestoreEventDataStoreResponse:
        """Restores a deleted event data store specified by ``EventDataStore``,
        which accepts an event data store ARN. You can only restore a deleted
        event data store within the seven-day wait period after deletion.
        Restoring an event data store can take several minutes, depending on the
        size of the event data store.

        :param event_data_store: The ARN (or the ID suffix of the ARN) of the event data store that you
        want to restore.
        :returns: RestoreEventDataStoreResponse
        :raises EventDataStoreARNInvalidException:
        :raises EventDataStoreNotFoundException:
        :raises EventDataStoreMaxLimitExceededException:
        :raises InvalidEventDataStoreStatusException:
        :raises InvalidParameterException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        :raises CloudTrailAccessNotEnabledException:
        :raises InsufficientDependencyServiceAccessPermissionException:
        :raises OrganizationsNotInUseException:
        :raises NotOrganizationMasterAccountException:
        :raises OrganizationNotInAllFeaturesModeException:
        """
        raise NotImplementedError

    @handler("StartLogging")
    def start_logging(self, context: RequestContext, name: String) -> StartLoggingResponse:
        """Starts the recording of Amazon Web Services API calls and log file
        delivery for a trail. For a trail that is enabled in all regions, this
        operation must be called from the region in which the trail was created.
        This operation cannot be called on the shadow trails (replicated trails
        in other regions) of a trail that is enabled in all regions.

        :param name: Specifies the name or the CloudTrail ARN of the trail for which
        CloudTrail logs Amazon Web Services API calls.
        :returns: StartLoggingResponse
        :raises TrailNotFoundException:
        :raises InvalidTrailNameException:
        :raises InvalidHomeRegionException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises NotOrganizationMasterAccountException:
        :raises InsufficientDependencyServiceAccessPermissionException:
        """
        raise NotImplementedError

    @handler("StartQuery")
    def start_query(
        self, context: RequestContext, query_statement: QueryStatement
    ) -> StartQueryResponse:
        """Starts a CloudTrail Lake query. The required ``QueryStatement``
        parameter provides your SQL query, enclosed in single quotation marks.

        :param query_statement: The SQL code of your query.
        :returns: StartQueryResponse
        :raises EventDataStoreARNInvalidException:
        :raises EventDataStoreNotFoundException:
        :raises InactiveEventDataStoreException:
        :raises InvalidParameterException:
        :raises InvalidQueryStatementException:
        :raises MaxConcurrentQueriesException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        """
        raise NotImplementedError

    @handler("StopLogging")
    def stop_logging(self, context: RequestContext, name: String) -> StopLoggingResponse:
        """Suspends the recording of Amazon Web Services API calls and log file
        delivery for the specified trail. Under most circumstances, there is no
        need to use this action. You can update a trail without stopping it
        first. This action is the only way to stop recording. For a trail
        enabled in all regions, this operation must be called from the region in
        which the trail was created, or an ``InvalidHomeRegionException`` will
        occur. This operation cannot be called on the shadow trails (replicated
        trails in other regions) of a trail enabled in all regions.

        :param name: Specifies the name or the CloudTrail ARN of the trail for which
        CloudTrail will stop logging Amazon Web Services API calls.
        :returns: StopLoggingResponse
        :raises TrailNotFoundException:
        :raises InvalidTrailNameException:
        :raises InvalidHomeRegionException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises NotOrganizationMasterAccountException:
        :raises InsufficientDependencyServiceAccessPermissionException:
        """
        raise NotImplementedError

    @handler("UpdateEventDataStore")
    def update_event_data_store(
        self,
        context: RequestContext,
        event_data_store: EventDataStoreArn,
        name: EventDataStoreName = None,
        advanced_event_selectors: AdvancedEventSelectors = None,
        multi_region_enabled: Boolean = None,
        organization_enabled: Boolean = None,
        retention_period: RetentionPeriod = None,
        termination_protection_enabled: TerminationProtectionEnabled = None,
    ) -> UpdateEventDataStoreResponse:
        """Updates an event data store. The required ``EventDataStore`` value is an
        ARN or the ID portion of the ARN. Other parameters are optional, but at
        least one optional parameter must be specified, or CloudTrail throws an
        error. ``RetentionPeriod`` is in days, and valid values are integers
        between 90 and 2555. By default, ``TerminationProtection`` is enabled.
        ``AdvancedEventSelectors`` includes or excludes management and data
        events in your event data store; for more information about
        ``AdvancedEventSelectors``, see
        PutEventSelectorsRequest$AdvancedEventSelectors.

        :param event_data_store: The ARN (or the ID suffix of the ARN) of the event data store that you
        want to update.
        :param name: The event data store name.
        :param advanced_event_selectors: The advanced event selectors used to select events for the event data
        store.
        :param multi_region_enabled: Specifies whether an event data store collects events from all regions,
        or only from the region in which it was created.
        :param organization_enabled: Specifies whether an event data store collects events logged for an
        organization in Organizations.
        :param retention_period: The retention period, in days.
        :param termination_protection_enabled: Indicates that termination protection is enabled and the event data
        store cannot be automatically deleted.
        :returns: UpdateEventDataStoreResponse
        :raises EventDataStoreARNInvalidException:
        :raises EventDataStoreNotFoundException:
        :raises InactiveEventDataStoreException:
        :raises InvalidParameterException:
        :raises OperationNotPermittedException:
        :raises UnsupportedOperationException:
        :raises CloudTrailAccessNotEnabledException:
        :raises InsufficientDependencyServiceAccessPermissionException:
        :raises OrganizationsNotInUseException:
        :raises NotOrganizationMasterAccountException:
        :raises OrganizationNotInAllFeaturesModeException:
        """
        raise NotImplementedError

    @handler("UpdateTrail")
    def update_trail(
        self,
        context: RequestContext,
        name: String,
        s3_bucket_name: String = None,
        s3_key_prefix: String = None,
        sns_topic_name: String = None,
        include_global_service_events: Boolean = None,
        is_multi_region_trail: Boolean = None,
        enable_log_file_validation: Boolean = None,
        cloud_watch_logs_log_group_arn: String = None,
        cloud_watch_logs_role_arn: String = None,
        kms_key_id: String = None,
        is_organization_trail: Boolean = None,
    ) -> UpdateTrailResponse:
        """Updates trail settings that control what events you are logging, and how
        to handle log files. Changes to a trail do not require stopping the
        CloudTrail service. Use this action to designate an existing bucket for
        log delivery. If the existing bucket has previously been a target for
        CloudTrail log files, an IAM policy exists for the bucket.
        ``UpdateTrail`` must be called from the region in which the trail was
        created; otherwise, an ``InvalidHomeRegionException`` is thrown.

        :param name: Specifies the name of the trail or trail ARN.
        :param s3_bucket_name: Specifies the name of the Amazon S3 bucket designated for publishing log
        files.
        :param s3_key_prefix: Specifies the Amazon S3 key prefix that comes after the name of the
        bucket you have designated for log file delivery.
        :param sns_topic_name: Specifies the name of the Amazon SNS topic defined for notification of
        log file delivery.
        :param include_global_service_events: Specifies whether the trail is publishing events from global services
        such as IAM to the log files.
        :param is_multi_region_trail: Specifies whether the trail applies only to the current region or to all
        regions.
        :param enable_log_file_validation: Specifies whether log file validation is enabled.
        :param cloud_watch_logs_log_group_arn: Specifies a log group name using an Amazon Resource Name (ARN), a unique
        identifier that represents the log group to which CloudTrail logs are
        delivered.
        :param cloud_watch_logs_role_arn: Specifies the role for the CloudWatch Logs endpoint to assume to write
        to a user's log group.
        :param kms_key_id: Specifies the KMS key ID to use to encrypt the logs delivered by
        CloudTrail.
        :param is_organization_trail: Specifies whether the trail is applied to all accounts in an
        organization in Organizations, or only for the current Amazon Web
        Services account.
        :returns: UpdateTrailResponse
        :raises S3BucketDoesNotExistException:
        :raises InsufficientS3BucketPolicyException:
        :raises InsufficientSnsTopicPolicyException:
        :raises InsufficientEncryptionPolicyException:
        :raises TrailNotFoundException:
        :raises InvalidS3BucketNameException:
        :raises InvalidS3PrefixException:
        :raises InvalidSnsTopicNameException:
        :raises InvalidKmsKeyIdException:
        :raises InvalidTrailNameException:
        :raises TrailNotProvidedException:
        :raises InvalidEventSelectorsException:
        :raises InvalidParameterCombinationException:
        :raises InvalidHomeRegionException:
        :raises KmsKeyNotFoundException:
        :raises KmsKeyDisabledException:
        :raises KmsException:
        :raises InvalidCloudWatchLogsLogGroupArnException:
        :raises InvalidCloudWatchLogsRoleArnException:
        :raises CloudWatchLogsDeliveryUnavailableException:
        :raises UnsupportedOperationException:
        :raises OperationNotPermittedException:
        :raises CloudTrailAccessNotEnabledException:
        :raises InsufficientDependencyServiceAccessPermissionException:
        :raises OrganizationsNotInUseException:
        :raises NotOrganizationMasterAccountException:
        :raises OrganizationNotInAllFeaturesModeException:
        :raises CloudTrailInvalidClientTokenIdException:
        """
        raise NotImplementedError
