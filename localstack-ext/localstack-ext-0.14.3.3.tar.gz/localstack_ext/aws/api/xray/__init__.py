import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AmazonResourceName = str
AnnotationKey = str
AttributeKey = str
AttributeValue = str
Boolean = bool
BorrowCount = int
ClientID = str
Double = float
EC2InstanceId = str
EncryptionKeyId = str
EntitySelectorExpression = str
ErrorMessage = str
EventSummaryText = str
FilterExpression = str
FixedRate = float
GetGroupsNextToken = str
GetInsightEventsMaxResults = int
GetInsightSummariesMaxResults = int
GroupARN = str
GroupName = str
HTTPMethod = str
Host = str
Hostname = str
InsightId = str
InsightSummaryText = str
Integer = int
NullableBoolean = bool
NullableDouble = float
NullableInteger = int
Priority = int
RequestCount = int
ReservoirSize = int
ResourceARN = str
RuleName = str
SampledCount = int
SegmentDocument = str
SegmentId = str
ServiceName = str
ServiceType = str
String = str
TagKey = str
TagValue = str
Token = str
TraceId = str
TraceSegmentDocument = str
URLPath = str
Version = int


class EncryptionStatus(str):
    UPDATING = "UPDATING"
    ACTIVE = "ACTIVE"


class EncryptionType(str):
    NONE = "NONE"
    KMS = "KMS"


class InsightCategory(str):
    FAULT = "FAULT"


class InsightState(str):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class SamplingStrategyName(str):
    PartialScan = "PartialScan"
    FixedRate = "FixedRate"


class TimeRangeType(str):
    TraceId = "TraceId"
    Event = "Event"


class InvalidRequestException(ServiceException):
    """The request is missing required parameters or has invalid parameters."""

    Message: Optional[ErrorMessage]


class ResourceNotFoundException(ServiceException):
    """The resource was not found. Verify that the name or Amazon Resource Name
    (ARN) of the resource is correct.
    """

    Message: Optional[ErrorMessage]
    ResourceName: Optional[AmazonResourceName]


class RuleLimitExceededException(ServiceException):
    """You have reached the maximum number of sampling rules."""

    Message: Optional[ErrorMessage]


class ThrottledException(ServiceException):
    """The request exceeds the maximum number of requests per second."""

    Message: Optional[ErrorMessage]


class TooManyTagsException(ServiceException):
    """You have exceeded the maximum number of tags you can apply to this
    resource.
    """

    Message: Optional[ErrorMessage]
    ResourceName: Optional[AmazonResourceName]


AliasNames = List[String]


class Alias(TypedDict, total=False):
    """An alias for an edge."""

    Name: Optional[String]
    Names: Optional[AliasNames]
    Type: Optional[String]


AliasList = List[Alias]


class AnnotationValue(TypedDict, total=False):
    """Value of a segment annotation. Has one of three value types: Number,
    Boolean, or String.
    """

    NumberValue: Optional[NullableDouble]
    BooleanValue: Optional[NullableBoolean]
    StringValue: Optional[String]


ServiceNames = List[String]


class ServiceId(TypedDict, total=False):
    Name: Optional[String]
    Names: Optional[ServiceNames]
    AccountId: Optional[String]
    Type: Optional[String]


ServiceIds = List[ServiceId]


class ValueWithServiceIds(TypedDict, total=False):
    """Information about a segment annotation."""

    AnnotationValue: Optional[AnnotationValue]
    ServiceIds: Optional[ServiceIds]


ValuesWithServiceIds = List[ValueWithServiceIds]
Annotations = Dict[AnnotationKey, ValuesWithServiceIds]


class AnomalousService(TypedDict, total=False):
    """The service within the service graph that has anomalously high fault
    rates.
    """

    ServiceId: Optional[ServiceId]


AnomalousServiceList = List[AnomalousService]
AttributeMap = Dict[AttributeKey, AttributeValue]


class AvailabilityZoneDetail(TypedDict, total=False):
    """A list of Availability Zones corresponding to the segments in a trace."""

    Name: Optional[String]


class BackendConnectionErrors(TypedDict, total=False):
    TimeoutCount: Optional[NullableInteger]
    ConnectionRefusedCount: Optional[NullableInteger]
    HTTPCode4XXCount: Optional[NullableInteger]
    HTTPCode5XXCount: Optional[NullableInteger]
    UnknownHostCount: Optional[NullableInteger]
    OtherCount: Optional[NullableInteger]


TraceIdList = List[TraceId]


class BatchGetTracesRequest(ServiceRequest):
    TraceIds: TraceIdList
    NextToken: Optional[String]


UnprocessedTraceIdList = List[TraceId]


class Segment(TypedDict, total=False):
    """A segment from a trace that has been ingested by the X-Ray service. The
    segment can be compiled from documents uploaded with
    `PutTraceSegments <https://docs.aws.amazon.com/xray/latest/api/API_PutTraceSegments.html>`__,
    or an ``inferred`` segment for a downstream service, generated from a
    subsegment sent by the service that called it.

    For the full segment document schema, see `Amazon Web Services X-Ray
    Segment
    Documents <https://docs.aws.amazon.com/xray/latest/devguide/xray-api-segmentdocuments.html>`__
    in the *Amazon Web Services X-Ray Developer Guide*.
    """

    Id: Optional[SegmentId]
    Document: Optional[SegmentDocument]


SegmentList = List[Segment]


class Trace(TypedDict, total=False):
    """A collection of segment documents with matching trace IDs."""

    Id: Optional[TraceId]
    Duration: Optional[NullableDouble]
    LimitExceeded: Optional[NullableBoolean]
    Segments: Optional[SegmentList]


TraceList = List[Trace]


class BatchGetTracesResult(TypedDict, total=False):
    Traces: Optional[TraceList]
    UnprocessedTraceIds: Optional[UnprocessedTraceIdList]
    NextToken: Optional[String]


class Tag(TypedDict, total=False):
    """A map that contains tag keys and tag values to attach to an Amazon Web
    Services X-Ray group or sampling rule. For more information about ways
    to use tags, see `Tagging Amazon Web Services
    resources <https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html>`__
    in the *Amazon Web Services General Reference*.

    The following restrictions apply to tags:

    -  Maximum number of user-applied tags per resource: 50

    -  Tag keys and values are case sensitive.

    -  Don't use ``aws:`` as a prefix for keys; it's reserved for Amazon Web
       Services use. You cannot edit or delete system tags.
    """

    Key: TagKey
    Value: TagValue


TagList = List[Tag]


class InsightsConfiguration(TypedDict, total=False):
    """The structure containing configurations related to insights."""

    InsightsEnabled: Optional[NullableBoolean]
    NotificationsEnabled: Optional[NullableBoolean]


class CreateGroupRequest(ServiceRequest):
    GroupName: GroupName
    FilterExpression: Optional[FilterExpression]
    InsightsConfiguration: Optional[InsightsConfiguration]
    Tags: Optional[TagList]


class Group(TypedDict, total=False):
    """Details and metadata for a group."""

    GroupName: Optional[String]
    GroupARN: Optional[String]
    FilterExpression: Optional[String]
    InsightsConfiguration: Optional[InsightsConfiguration]


class CreateGroupResult(TypedDict, total=False):
    Group: Optional[Group]


class SamplingRule(TypedDict, total=False):
    """A sampling rule that services use to decide whether to instrument a
    request. Rule fields can match properties of the service, or properties
    of a request. The service can ignore rules that don't match its
    properties.
    """

    RuleName: Optional[RuleName]
    RuleARN: Optional[String]
    ResourceARN: ResourceARN
    Priority: Priority
    FixedRate: FixedRate
    ReservoirSize: ReservoirSize
    ServiceName: ServiceName
    ServiceType: ServiceType
    Host: Host
    HTTPMethod: HTTPMethod
    URLPath: URLPath
    Version: Version
    Attributes: Optional[AttributeMap]


class CreateSamplingRuleRequest(ServiceRequest):
    SamplingRule: SamplingRule
    Tags: Optional[TagList]


Timestamp = datetime


class SamplingRuleRecord(TypedDict, total=False):
    """A
    `SamplingRule <https://docs.aws.amazon.com/xray/latest/api/API_SamplingRule.html>`__
    and its metadata.
    """

    SamplingRule: Optional[SamplingRule]
    CreatedAt: Optional[Timestamp]
    ModifiedAt: Optional[Timestamp]


class CreateSamplingRuleResult(TypedDict, total=False):
    SamplingRuleRecord: Optional[SamplingRuleRecord]


class DeleteGroupRequest(ServiceRequest):
    GroupName: Optional[GroupName]
    GroupARN: Optional[GroupARN]


class DeleteGroupResult(TypedDict, total=False):
    pass


class DeleteSamplingRuleRequest(ServiceRequest):
    RuleName: Optional[String]
    RuleARN: Optional[String]


class DeleteSamplingRuleResult(TypedDict, total=False):
    SamplingRuleRecord: Optional[SamplingRuleRecord]


class HistogramEntry(TypedDict, total=False):
    """An entry in a histogram for a statistic. A histogram maps the range of
    observed values on the X axis, and the prevalence of each value on the Y
    axis.
    """

    Value: Optional[Double]
    Count: Optional[Integer]


Histogram = List[HistogramEntry]
NullableLong = int


class FaultStatistics(TypedDict, total=False):
    """Information about requests that failed with a 5xx Server Error status
    code.
    """

    OtherCount: Optional[NullableLong]
    TotalCount: Optional[NullableLong]


class ErrorStatistics(TypedDict, total=False):
    """Information about requests that failed with a 4xx Client Error status
    code.
    """

    ThrottleCount: Optional[NullableLong]
    OtherCount: Optional[NullableLong]
    TotalCount: Optional[NullableLong]


class EdgeStatistics(TypedDict, total=False):
    """Response statistics for an edge."""

    OkCount: Optional[NullableLong]
    ErrorStatistics: Optional[ErrorStatistics]
    FaultStatistics: Optional[FaultStatistics]
    TotalCount: Optional[NullableLong]
    TotalResponseTime: Optional[NullableDouble]


class Edge(TypedDict, total=False):
    """Information about a connection between two services."""

    ReferenceId: Optional[NullableInteger]
    StartTime: Optional[Timestamp]
    EndTime: Optional[Timestamp]
    SummaryStatistics: Optional[EdgeStatistics]
    ResponseTimeHistogram: Optional[Histogram]
    Aliases: Optional[AliasList]


EdgeList = List[Edge]


class EncryptionConfig(TypedDict, total=False):
    """A configuration document that specifies encryption configuration
    settings.
    """

    KeyId: Optional[String]
    Status: Optional[EncryptionStatus]
    Type: Optional[EncryptionType]


class RootCauseException(TypedDict, total=False):
    """The exception associated with a root cause."""

    Name: Optional[String]
    Message: Optional[String]


RootCauseExceptions = List[RootCauseException]


class ErrorRootCauseEntity(TypedDict, total=False):
    """A collection of segments and corresponding subsegments associated to a
    trace summary error.
    """

    Name: Optional[String]
    Exceptions: Optional[RootCauseExceptions]
    Remote: Optional[NullableBoolean]


ErrorRootCauseEntityPath = List[ErrorRootCauseEntity]


class ErrorRootCauseService(TypedDict, total=False):
    """A collection of fields identifying the services in a trace summary
    error.
    """

    Name: Optional[String]
    Names: Optional[ServiceNames]
    Type: Optional[String]
    AccountId: Optional[String]
    EntityPath: Optional[ErrorRootCauseEntityPath]
    Inferred: Optional[NullableBoolean]


ErrorRootCauseServices = List[ErrorRootCauseService]


class ErrorRootCause(TypedDict, total=False):
    """The root cause of a trace summary error."""

    Services: Optional[ErrorRootCauseServices]
    ClientImpacting: Optional[NullableBoolean]


ErrorRootCauses = List[ErrorRootCause]


class FaultRootCauseEntity(TypedDict, total=False):
    """A collection of segments and corresponding subsegments associated to a
    trace summary fault error.
    """

    Name: Optional[String]
    Exceptions: Optional[RootCauseExceptions]
    Remote: Optional[NullableBoolean]


FaultRootCauseEntityPath = List[FaultRootCauseEntity]


class FaultRootCauseService(TypedDict, total=False):
    """A collection of fields identifying the services in a trace summary
    fault.
    """

    Name: Optional[String]
    Names: Optional[ServiceNames]
    Type: Optional[String]
    AccountId: Optional[String]
    EntityPath: Optional[FaultRootCauseEntityPath]
    Inferred: Optional[NullableBoolean]


FaultRootCauseServices = List[FaultRootCauseService]


class FaultRootCause(TypedDict, total=False):
    """The root cause information for a trace summary fault."""

    Services: Optional[FaultRootCauseServices]
    ClientImpacting: Optional[NullableBoolean]


FaultRootCauses = List[FaultRootCause]


class ForecastStatistics(TypedDict, total=False):
    """The predicted high and low fault count. This is used to determine if a
    service has become anomalous and if an insight should be created.
    """

    FaultCountHigh: Optional[NullableLong]
    FaultCountLow: Optional[NullableLong]


class GetEncryptionConfigRequest(ServiceRequest):
    pass


class GetEncryptionConfigResult(TypedDict, total=False):
    EncryptionConfig: Optional[EncryptionConfig]


class GetGroupRequest(ServiceRequest):
    GroupName: Optional[GroupName]
    GroupARN: Optional[GroupARN]


class GetGroupResult(TypedDict, total=False):
    Group: Optional[Group]


class GetGroupsRequest(ServiceRequest):
    NextToken: Optional[GetGroupsNextToken]


class GroupSummary(TypedDict, total=False):
    """Details for a group without metadata."""

    GroupName: Optional[String]
    GroupARN: Optional[String]
    FilterExpression: Optional[String]
    InsightsConfiguration: Optional[InsightsConfiguration]


GroupSummaryList = List[GroupSummary]


class GetGroupsResult(TypedDict, total=False):
    Groups: Optional[GroupSummaryList]
    NextToken: Optional[String]


class GetInsightEventsRequest(ServiceRequest):
    InsightId: InsightId
    MaxResults: Optional[GetInsightEventsMaxResults]
    NextToken: Optional[Token]


class RequestImpactStatistics(TypedDict, total=False):
    """Statistics that describe how the incident has impacted a service."""

    FaultCount: Optional[NullableLong]
    OkCount: Optional[NullableLong]
    TotalCount: Optional[NullableLong]


class InsightEvent(TypedDict, total=False):
    """X-Ray reevaluates insights periodically until they are resolved, and
    records each intermediate state in an event. You can review incident
    events in the Impact Timeline on the Inspect page in the X-Ray console.
    """

    Summary: Optional[EventSummaryText]
    EventTime: Optional[Timestamp]
    ClientRequestImpactStatistics: Optional[RequestImpactStatistics]
    RootCauseServiceRequestImpactStatistics: Optional[RequestImpactStatistics]
    TopAnomalousServices: Optional[AnomalousServiceList]


InsightEventList = List[InsightEvent]


class GetInsightEventsResult(TypedDict, total=False):
    InsightEvents: Optional[InsightEventList]
    NextToken: Optional[Token]


class GetInsightImpactGraphRequest(ServiceRequest):
    InsightId: InsightId
    StartTime: Timestamp
    EndTime: Timestamp
    NextToken: Optional[Token]


class InsightImpactGraphEdge(TypedDict, total=False):
    """The connection between two service in an insight impact graph."""

    ReferenceId: Optional[NullableInteger]


InsightImpactGraphEdgeList = List[InsightImpactGraphEdge]


class InsightImpactGraphService(TypedDict, total=False):
    """Information about an application that processed requests, users that
    made requests, or downstream services, resources, and applications that
    an application used.
    """

    ReferenceId: Optional[NullableInteger]
    Type: Optional[String]
    Name: Optional[String]
    Names: Optional[ServiceNames]
    AccountId: Optional[String]
    Edges: Optional[InsightImpactGraphEdgeList]


InsightImpactGraphServiceList = List[InsightImpactGraphService]


class GetInsightImpactGraphResult(TypedDict, total=False):
    InsightId: Optional[InsightId]
    StartTime: Optional[Timestamp]
    EndTime: Optional[Timestamp]
    ServiceGraphStartTime: Optional[Timestamp]
    ServiceGraphEndTime: Optional[Timestamp]
    Services: Optional[InsightImpactGraphServiceList]
    NextToken: Optional[Token]


class GetInsightRequest(ServiceRequest):
    InsightId: InsightId


InsightCategoryList = List[InsightCategory]


class Insight(TypedDict, total=False):
    """When fault rates go outside of the expected range, X-Ray creates an
    insight. Insights tracks emergent issues within your applications.
    """

    InsightId: Optional[InsightId]
    GroupARN: Optional[GroupARN]
    GroupName: Optional[GroupName]
    RootCauseServiceId: Optional[ServiceId]
    Categories: Optional[InsightCategoryList]
    State: Optional[InsightState]
    StartTime: Optional[Timestamp]
    EndTime: Optional[Timestamp]
    Summary: Optional[InsightSummaryText]
    ClientRequestImpactStatistics: Optional[RequestImpactStatistics]
    RootCauseServiceRequestImpactStatistics: Optional[RequestImpactStatistics]
    TopAnomalousServices: Optional[AnomalousServiceList]


class GetInsightResult(TypedDict, total=False):
    Insight: Optional[Insight]


InsightStateList = List[InsightState]


class GetInsightSummariesRequest(ServiceRequest):
    States: Optional[InsightStateList]
    GroupARN: Optional[GroupARN]
    GroupName: Optional[GroupName]
    StartTime: Timestamp
    EndTime: Timestamp
    MaxResults: Optional[GetInsightSummariesMaxResults]
    NextToken: Optional[Token]


class InsightSummary(TypedDict, total=False):
    """Information that describes an insight."""

    InsightId: Optional[InsightId]
    GroupARN: Optional[GroupARN]
    GroupName: Optional[GroupName]
    RootCauseServiceId: Optional[ServiceId]
    Categories: Optional[InsightCategoryList]
    State: Optional[InsightState]
    StartTime: Optional[Timestamp]
    EndTime: Optional[Timestamp]
    Summary: Optional[InsightSummaryText]
    ClientRequestImpactStatistics: Optional[RequestImpactStatistics]
    RootCauseServiceRequestImpactStatistics: Optional[RequestImpactStatistics]
    TopAnomalousServices: Optional[AnomalousServiceList]
    LastUpdateTime: Optional[Timestamp]


InsightSummaryList = List[InsightSummary]


class GetInsightSummariesResult(TypedDict, total=False):
    InsightSummaries: Optional[InsightSummaryList]
    NextToken: Optional[Token]


class GetSamplingRulesRequest(ServiceRequest):
    NextToken: Optional[String]


SamplingRuleRecordList = List[SamplingRuleRecord]


class GetSamplingRulesResult(TypedDict, total=False):
    SamplingRuleRecords: Optional[SamplingRuleRecordList]
    NextToken: Optional[String]


class GetSamplingStatisticSummariesRequest(ServiceRequest):
    NextToken: Optional[String]


class SamplingStatisticSummary(TypedDict, total=False):
    """Aggregated request sampling data for a sampling rule across all services
    for a 10-second window.
    """

    RuleName: Optional[String]
    Timestamp: Optional[Timestamp]
    RequestCount: Optional[Integer]
    BorrowCount: Optional[Integer]
    SampledCount: Optional[Integer]


SamplingStatisticSummaryList = List[SamplingStatisticSummary]


class GetSamplingStatisticSummariesResult(TypedDict, total=False):
    SamplingStatisticSummaries: Optional[SamplingStatisticSummaryList]
    NextToken: Optional[String]


class SamplingStatisticsDocument(TypedDict, total=False):
    """Request sampling results for a single rule from a service. Results are
    for the last 10 seconds unless the service has been assigned a longer
    reporting interval after a previous call to
    `GetSamplingTargets <https://docs.aws.amazon.com/xray/latest/api/API_GetSamplingTargets.html>`__.
    """

    RuleName: RuleName
    ClientID: ClientID
    Timestamp: Timestamp
    RequestCount: RequestCount
    SampledCount: SampledCount
    BorrowCount: Optional[BorrowCount]


SamplingStatisticsDocumentList = List[SamplingStatisticsDocument]


class GetSamplingTargetsRequest(ServiceRequest):
    SamplingStatisticsDocuments: SamplingStatisticsDocumentList


class UnprocessedStatistics(TypedDict, total=False):
    """Sampling statistics from a call to
    `GetSamplingTargets <https://docs.aws.amazon.com/xray/latest/api/API_GetSamplingTargets.html>`__
    that X-Ray could not process.
    """

    RuleName: Optional[String]
    ErrorCode: Optional[String]
    Message: Optional[String]


UnprocessedStatisticsList = List[UnprocessedStatistics]


class SamplingTargetDocument(TypedDict, total=False):
    """Temporary changes to a sampling rule configuration. To meet the global
    sampling target for a rule, X-Ray calculates a new reservoir for each
    service based on the recent sampling results of all services that called
    `GetSamplingTargets <https://docs.aws.amazon.com/xray/latest/api/API_GetSamplingTargets.html>`__.
    """

    RuleName: Optional[String]
    FixedRate: Optional[Double]
    ReservoirQuota: Optional[NullableInteger]
    ReservoirQuotaTTL: Optional[Timestamp]
    Interval: Optional[NullableInteger]


SamplingTargetDocumentList = List[SamplingTargetDocument]


class GetSamplingTargetsResult(TypedDict, total=False):
    SamplingTargetDocuments: Optional[SamplingTargetDocumentList]
    LastRuleModification: Optional[Timestamp]
    UnprocessedStatistics: Optional[UnprocessedStatisticsList]


class GetServiceGraphRequest(ServiceRequest):
    StartTime: Timestamp
    EndTime: Timestamp
    GroupName: Optional[GroupName]
    GroupARN: Optional[GroupARN]
    NextToken: Optional[String]


class ServiceStatistics(TypedDict, total=False):
    """Response statistics for a service."""

    OkCount: Optional[NullableLong]
    ErrorStatistics: Optional[ErrorStatistics]
    FaultStatistics: Optional[FaultStatistics]
    TotalCount: Optional[NullableLong]
    TotalResponseTime: Optional[NullableDouble]


class Service(TypedDict, total=False):
    """Information about an application that processed requests, users that
    made requests, or downstream services, resources, and applications that
    an application used.
    """

    ReferenceId: Optional[NullableInteger]
    Name: Optional[String]
    Names: Optional[ServiceNames]
    Root: Optional[NullableBoolean]
    AccountId: Optional[String]
    Type: Optional[String]
    State: Optional[String]
    StartTime: Optional[Timestamp]
    EndTime: Optional[Timestamp]
    Edges: Optional[EdgeList]
    SummaryStatistics: Optional[ServiceStatistics]
    DurationHistogram: Optional[Histogram]
    ResponseTimeHistogram: Optional[Histogram]


ServiceList = List[Service]


class GetServiceGraphResult(TypedDict, total=False):
    StartTime: Optional[Timestamp]
    EndTime: Optional[Timestamp]
    Services: Optional[ServiceList]
    ContainsOldGroupVersions: Optional[Boolean]
    NextToken: Optional[String]


class GetTimeSeriesServiceStatisticsRequest(ServiceRequest):
    StartTime: Timestamp
    EndTime: Timestamp
    GroupName: Optional[GroupName]
    GroupARN: Optional[GroupARN]
    EntitySelectorExpression: Optional[EntitySelectorExpression]
    Period: Optional[NullableInteger]
    ForecastStatistics: Optional[NullableBoolean]
    NextToken: Optional[String]


class TimeSeriesServiceStatistics(TypedDict, total=False):
    """A list of TimeSeriesStatistic structures."""

    Timestamp: Optional[Timestamp]
    EdgeSummaryStatistics: Optional[EdgeStatistics]
    ServiceSummaryStatistics: Optional[ServiceStatistics]
    ServiceForecastStatistics: Optional[ForecastStatistics]
    ResponseTimeHistogram: Optional[Histogram]


TimeSeriesServiceStatisticsList = List[TimeSeriesServiceStatistics]


class GetTimeSeriesServiceStatisticsResult(TypedDict, total=False):
    TimeSeriesServiceStatistics: Optional[TimeSeriesServiceStatisticsList]
    ContainsOldGroupVersions: Optional[Boolean]
    NextToken: Optional[String]


class GetTraceGraphRequest(ServiceRequest):
    TraceIds: TraceIdList
    NextToken: Optional[String]


class GetTraceGraphResult(TypedDict, total=False):
    Services: Optional[ServiceList]
    NextToken: Optional[String]


class SamplingStrategy(TypedDict, total=False):
    """The name and value of a sampling rule to apply to a trace summary."""

    Name: Optional[SamplingStrategyName]
    Value: Optional[NullableDouble]


class GetTraceSummariesRequest(ServiceRequest):
    StartTime: Timestamp
    EndTime: Timestamp
    TimeRangeType: Optional[TimeRangeType]
    Sampling: Optional[NullableBoolean]
    SamplingStrategy: Optional[SamplingStrategy]
    FilterExpression: Optional[FilterExpression]
    NextToken: Optional[String]


class ResponseTimeRootCauseEntity(TypedDict, total=False):
    """A collection of segments and corresponding subsegments associated to a
    response time warning.
    """

    Name: Optional[String]
    Coverage: Optional[NullableDouble]
    Remote: Optional[NullableBoolean]


ResponseTimeRootCauseEntityPath = List[ResponseTimeRootCauseEntity]


class ResponseTimeRootCauseService(TypedDict, total=False):
    """A collection of fields identifying the service in a response time
    warning.
    """

    Name: Optional[String]
    Names: Optional[ServiceNames]
    Type: Optional[String]
    AccountId: Optional[String]
    EntityPath: Optional[ResponseTimeRootCauseEntityPath]
    Inferred: Optional[NullableBoolean]


ResponseTimeRootCauseServices = List[ResponseTimeRootCauseService]


class ResponseTimeRootCause(TypedDict, total=False):
    """The root cause information for a response time warning."""

    Services: Optional[ResponseTimeRootCauseServices]
    ClientImpacting: Optional[NullableBoolean]


ResponseTimeRootCauses = List[ResponseTimeRootCause]
TraceAvailabilityZones = List[AvailabilityZoneDetail]


class InstanceIdDetail(TypedDict, total=False):
    """A list of EC2 instance IDs corresponding to the segments in a trace."""

    Id: Optional[String]


TraceInstanceIds = List[InstanceIdDetail]


class ResourceARNDetail(TypedDict, total=False):
    """A list of resources ARNs corresponding to the segments in a trace."""

    ARN: Optional[String]


TraceResourceARNs = List[ResourceARNDetail]


class TraceUser(TypedDict, total=False):
    """Information about a user recorded in segment documents."""

    UserName: Optional[String]
    ServiceIds: Optional[ServiceIds]


TraceUsers = List[TraceUser]


class Http(TypedDict, total=False):
    """Information about an HTTP request."""

    HttpURL: Optional[String]
    HttpStatus: Optional[NullableInteger]
    HttpMethod: Optional[String]
    UserAgent: Optional[String]
    ClientIp: Optional[String]


class TraceSummary(TypedDict, total=False):
    """Metadata generated from the segment documents in a trace."""

    Id: Optional[TraceId]
    Duration: Optional[NullableDouble]
    ResponseTime: Optional[NullableDouble]
    HasFault: Optional[NullableBoolean]
    HasError: Optional[NullableBoolean]
    HasThrottle: Optional[NullableBoolean]
    IsPartial: Optional[NullableBoolean]
    Http: Optional[Http]
    Annotations: Optional[Annotations]
    Users: Optional[TraceUsers]
    ServiceIds: Optional[ServiceIds]
    ResourceARNs: Optional[TraceResourceARNs]
    InstanceIds: Optional[TraceInstanceIds]
    AvailabilityZones: Optional[TraceAvailabilityZones]
    EntryPoint: Optional[ServiceId]
    FaultRootCauses: Optional[FaultRootCauses]
    ErrorRootCauses: Optional[ErrorRootCauses]
    ResponseTimeRootCauses: Optional[ResponseTimeRootCauses]
    Revision: Optional[Integer]
    MatchedEventTime: Optional[Timestamp]


TraceSummaryList = List[TraceSummary]


class GetTraceSummariesResult(TypedDict, total=False):
    TraceSummaries: Optional[TraceSummaryList]
    ApproximateTime: Optional[Timestamp]
    TracesProcessedCount: Optional[NullableLong]
    NextToken: Optional[String]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceARN: AmazonResourceName
    NextToken: Optional[String]


class ListTagsForResourceResponse(TypedDict, total=False):
    Tags: Optional[TagList]
    NextToken: Optional[String]


class PutEncryptionConfigRequest(ServiceRequest):
    KeyId: Optional[EncryptionKeyId]
    Type: EncryptionType


class PutEncryptionConfigResult(TypedDict, total=False):
    EncryptionConfig: Optional[EncryptionConfig]


class TelemetryRecord(TypedDict, total=False):
    Timestamp: Timestamp
    SegmentsReceivedCount: Optional[NullableInteger]
    SegmentsSentCount: Optional[NullableInteger]
    SegmentsSpilloverCount: Optional[NullableInteger]
    SegmentsRejectedCount: Optional[NullableInteger]
    BackendConnectionErrors: Optional[BackendConnectionErrors]


TelemetryRecordList = List[TelemetryRecord]


class PutTelemetryRecordsRequest(ServiceRequest):
    TelemetryRecords: TelemetryRecordList
    EC2InstanceId: Optional[EC2InstanceId]
    Hostname: Optional[Hostname]
    ResourceARN: Optional[ResourceARN]


class PutTelemetryRecordsResult(TypedDict, total=False):
    pass


TraceSegmentDocumentList = List[TraceSegmentDocument]


class PutTraceSegmentsRequest(ServiceRequest):
    TraceSegmentDocuments: TraceSegmentDocumentList


class UnprocessedTraceSegment(TypedDict, total=False):
    """Information about a segment that failed processing."""

    Id: Optional[String]
    ErrorCode: Optional[String]
    Message: Optional[String]


UnprocessedTraceSegmentList = List[UnprocessedTraceSegment]


class PutTraceSegmentsResult(TypedDict, total=False):
    UnprocessedTraceSegments: Optional[UnprocessedTraceSegmentList]


class SamplingRuleUpdate(TypedDict, total=False):
    """A document specifying changes to a sampling rule's configuration."""

    RuleName: Optional[RuleName]
    RuleARN: Optional[String]
    ResourceARN: Optional[ResourceARN]
    Priority: Optional[NullableInteger]
    FixedRate: Optional[NullableDouble]
    ReservoirSize: Optional[NullableInteger]
    Host: Optional[Host]
    ServiceName: Optional[ServiceName]
    ServiceType: Optional[ServiceType]
    HTTPMethod: Optional[HTTPMethod]
    URLPath: Optional[URLPath]
    Attributes: Optional[AttributeMap]


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


class UpdateGroupRequest(ServiceRequest):
    GroupName: Optional[GroupName]
    GroupARN: Optional[GroupARN]
    FilterExpression: Optional[FilterExpression]
    InsightsConfiguration: Optional[InsightsConfiguration]


class UpdateGroupResult(TypedDict, total=False):
    Group: Optional[Group]


class UpdateSamplingRuleRequest(ServiceRequest):
    SamplingRuleUpdate: SamplingRuleUpdate


class UpdateSamplingRuleResult(TypedDict, total=False):
    SamplingRuleRecord: Optional[SamplingRuleRecord]


class XrayApi:

    service = "xray"
    version = "2016-04-12"

    @handler("BatchGetTraces")
    def batch_get_traces(
        self, context: RequestContext, trace_ids: TraceIdList, next_token: String = None
    ) -> BatchGetTracesResult:
        """Retrieves a list of traces specified by ID. Each trace is a collection
        of segment documents that originates from a single request. Use
        ``GetTraceSummaries`` to get a list of trace IDs.

        :param trace_ids: Specify the trace IDs of requests for which to retrieve segments.
        :param next_token: Pagination token.
        :returns: BatchGetTracesResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("CreateGroup")
    def create_group(
        self,
        context: RequestContext,
        group_name: GroupName,
        filter_expression: FilterExpression = None,
        insights_configuration: InsightsConfiguration = None,
        tags: TagList = None,
    ) -> CreateGroupResult:
        """Creates a group resource with a name and a filter expression.

        :param group_name: The case-sensitive name of the new group.
        :param filter_expression: The filter expression defining criteria by which to group traces.
        :param insights_configuration: The structure containing configurations related to insights.
        :param tags: A map that contains one or more tag keys and tag values to attach to an
        X-Ray group.
        :returns: CreateGroupResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("CreateSamplingRule")
    def create_sampling_rule(
        self, context: RequestContext, sampling_rule: SamplingRule, tags: TagList = None
    ) -> CreateSamplingRuleResult:
        """Creates a rule to control sampling behavior for instrumented
        applications. Services retrieve rules with
        `GetSamplingRules <https://docs.aws.amazon.com/xray/latest/api/API_GetSamplingRules.html>`__,
        and evaluate each rule in ascending order of *priority* for each
        request. If a rule matches, the service records a trace, borrowing it
        from the reservoir size. After 10 seconds, the service reports back to
        X-Ray with
        `GetSamplingTargets <https://docs.aws.amazon.com/xray/latest/api/API_GetSamplingTargets.html>`__
        to get updated versions of each in-use rule. The updated rule contains a
        trace quota that the service can use instead of borrowing from the
        reservoir.

        :param sampling_rule: The rule definition.
        :param tags: A map that contains one or more tag keys and tag values to attach to an
        X-Ray sampling rule.
        :returns: CreateSamplingRuleResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        :raises RuleLimitExceededException:
        """
        raise NotImplementedError

    @handler("DeleteGroup")
    def delete_group(
        self, context: RequestContext, group_name: GroupName = None, group_arn: GroupARN = None
    ) -> DeleteGroupResult:
        """Deletes a group resource.

        :param group_name: The case-sensitive name of the group.
        :param group_arn: The ARN of the group that was generated on creation.
        :returns: DeleteGroupResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("DeleteSamplingRule")
    def delete_sampling_rule(
        self, context: RequestContext, rule_name: String = None, rule_arn: String = None
    ) -> DeleteSamplingRuleResult:
        """Deletes a sampling rule.

        :param rule_name: The name of the sampling rule.
        :param rule_arn: The ARN of the sampling rule.
        :returns: DeleteSamplingRuleResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetEncryptionConfig")
    def get_encryption_config(
        self,
        context: RequestContext,
    ) -> GetEncryptionConfigResult:
        """Retrieves the current encryption configuration for X-Ray data.

        :returns: GetEncryptionConfigResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetGroup")
    def get_group(
        self, context: RequestContext, group_name: GroupName = None, group_arn: GroupARN = None
    ) -> GetGroupResult:
        """Retrieves group resource details.

        :param group_name: The case-sensitive name of the group.
        :param group_arn: The ARN of the group that was generated on creation.
        :returns: GetGroupResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetGroups")
    def get_groups(
        self, context: RequestContext, next_token: GetGroupsNextToken = None
    ) -> GetGroupsResult:
        """Retrieves all active group details.

        :param next_token: Pagination token.
        :returns: GetGroupsResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetInsight")
    def get_insight(self, context: RequestContext, insight_id: InsightId) -> GetInsightResult:
        """Retrieves the summary information of an insight. This includes impact to
        clients and root cause services, the top anomalous services, the
        category, the state of the insight, and the start and end time of the
        insight.

        :param insight_id: The insight's unique identifier.
        :returns: GetInsightResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetInsightEvents")
    def get_insight_events(
        self,
        context: RequestContext,
        insight_id: InsightId,
        max_results: GetInsightEventsMaxResults = None,
        next_token: Token = None,
    ) -> GetInsightEventsResult:
        """X-Ray reevaluates insights periodically until they're resolved, and
        records each intermediate state as an event. You can review an insight's
        events in the Impact Timeline on the Inspect page in the X-Ray console.

        :param insight_id: The insight's unique identifier.
        :param max_results: Used to retrieve at most the specified value of events.
        :param next_token: Specify the pagination token returned by a previous request to retrieve
        the next page of events.
        :returns: GetInsightEventsResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetInsightImpactGraph")
    def get_insight_impact_graph(
        self,
        context: RequestContext,
        insight_id: InsightId,
        start_time: Timestamp,
        end_time: Timestamp,
        next_token: Token = None,
    ) -> GetInsightImpactGraphResult:
        """Retrieves a service graph structure filtered by the specified insight.
        The service graph is limited to only structural information. For a
        complete service graph, use this API with the GetServiceGraph API.

        :param insight_id: The insight's unique identifier.
        :param start_time: The estimated start time of the insight, in Unix time seconds.
        :param end_time: The estimated end time of the insight, in Unix time seconds.
        :param next_token: Specify the pagination token returned by a previous request to retrieve
        the next page of results.
        :returns: GetInsightImpactGraphResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetInsightSummaries")
    def get_insight_summaries(
        self,
        context: RequestContext,
        start_time: Timestamp,
        end_time: Timestamp,
        states: InsightStateList = None,
        group_arn: GroupARN = None,
        group_name: GroupName = None,
        max_results: GetInsightSummariesMaxResults = None,
        next_token: Token = None,
    ) -> GetInsightSummariesResult:
        """Retrieves the summaries of all insights in the specified group matching
        the provided filter values.

        :param start_time: The beginning of the time frame in which the insights started.
        :param end_time: The end of the time frame in which the insights ended.
        :param states: The list of insight states.
        :param group_arn: The Amazon Resource Name (ARN) of the group.
        :param group_name: The name of the group.
        :param max_results: The maximum number of results to display.
        :param next_token: Pagination token.
        :returns: GetInsightSummariesResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetSamplingRules")
    def get_sampling_rules(
        self, context: RequestContext, next_token: String = None
    ) -> GetSamplingRulesResult:
        """Retrieves all sampling rules.

        :param next_token: Pagination token.
        :returns: GetSamplingRulesResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetSamplingStatisticSummaries")
    def get_sampling_statistic_summaries(
        self, context: RequestContext, next_token: String = None
    ) -> GetSamplingStatisticSummariesResult:
        """Retrieves information about recent sampling results for all sampling
        rules.

        :param next_token: Pagination token.
        :returns: GetSamplingStatisticSummariesResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetSamplingTargets")
    def get_sampling_targets(
        self, context: RequestContext, sampling_statistics_documents: SamplingStatisticsDocumentList
    ) -> GetSamplingTargetsResult:
        """Requests a sampling quota for rules that the service is using to sample
        requests.

        :param sampling_statistics_documents: Information about rules that the service is using to sample requests.
        :returns: GetSamplingTargetsResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetServiceGraph")
    def get_service_graph(
        self,
        context: RequestContext,
        start_time: Timestamp,
        end_time: Timestamp,
        group_name: GroupName = None,
        group_arn: GroupARN = None,
        next_token: String = None,
    ) -> GetServiceGraphResult:
        """Retrieves a document that describes services that process incoming
        requests, and downstream services that they call as a result. Root
        services process incoming requests and make calls to downstream
        services. Root services are applications that use the `Amazon Web
        Services X-Ray SDK <https://docs.aws.amazon.com/xray/index.html>`__.
        Downstream services can be other applications, Amazon Web Services
        resources, HTTP web APIs, or SQL databases.

        :param start_time: The start of the time frame for which to generate a graph.
        :param end_time: The end of the timeframe for which to generate a graph.
        :param group_name: The name of a group based on which you want to generate a graph.
        :param group_arn: The Amazon Resource Name (ARN) of a group based on which you want to
        generate a graph.
        :param next_token: Pagination token.
        :returns: GetServiceGraphResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetTimeSeriesServiceStatistics")
    def get_time_series_service_statistics(
        self,
        context: RequestContext,
        start_time: Timestamp,
        end_time: Timestamp,
        group_name: GroupName = None,
        group_arn: GroupARN = None,
        entity_selector_expression: EntitySelectorExpression = None,
        period: NullableInteger = None,
        forecast_statistics: NullableBoolean = None,
        next_token: String = None,
    ) -> GetTimeSeriesServiceStatisticsResult:
        """Get an aggregation of service statistics defined by a specific time
        range.

        :param start_time: The start of the time frame for which to aggregate statistics.
        :param end_time: The end of the time frame for which to aggregate statistics.
        :param group_name: The case-sensitive name of the group for which to pull statistics from.
        :param group_arn: The Amazon Resource Name (ARN) of the group for which to pull statistics
        from.
        :param entity_selector_expression: A filter expression defining entities that will be aggregated for
        statistics.
        :param period: Aggregation period in seconds.
        :param forecast_statistics: The forecasted high and low fault count values.
        :param next_token: Pagination token.
        :returns: GetTimeSeriesServiceStatisticsResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetTraceGraph")
    def get_trace_graph(
        self, context: RequestContext, trace_ids: TraceIdList, next_token: String = None
    ) -> GetTraceGraphResult:
        """Retrieves a service graph for one or more specific trace IDs.

        :param trace_ids: Trace IDs of requests for which to generate a service graph.
        :param next_token: Pagination token.
        :returns: GetTraceGraphResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("GetTraceSummaries")
    def get_trace_summaries(
        self,
        context: RequestContext,
        start_time: Timestamp,
        end_time: Timestamp,
        time_range_type: TimeRangeType = None,
        sampling: NullableBoolean = None,
        sampling_strategy: SamplingStrategy = None,
        filter_expression: FilterExpression = None,
        next_token: String = None,
    ) -> GetTraceSummariesResult:
        """Retrieves IDs and annotations for traces available for a specified time
        frame using an optional filter. To get the full traces, pass the trace
        IDs to ``BatchGetTraces``.

        A filter expression can target traced requests that hit specific service
        nodes or edges, have errors, or come from a known user. For example, the
        following filter expression targets traces that pass through
        ``api.example.com``:

        ``service("api.example.com")``

        This filter expression finds traces that have an annotation named
        ``account`` with the value ``12345``:

        ``annotation.account = "12345"``

        For a full list of indexed fields and keywords that you can use in
        filter expressions, see `Using Filter
        Expressions <https://docs.aws.amazon.com/xray/latest/devguide/xray-console-filters.html>`__
        in the *Amazon Web Services X-Ray Developer Guide*.

        :param start_time: The start of the time frame for which to retrieve traces.
        :param end_time: The end of the time frame for which to retrieve traces.
        :param time_range_type: A parameter to indicate whether to query trace summaries by TraceId or
        Event time.
        :param sampling: Set to ``true`` to get summaries for only a subset of available traces.
        :param sampling_strategy: A parameter to indicate whether to enable sampling on trace summaries.
        :param filter_expression: Specify a filter expression to retrieve trace summaries for services or
        requests that meet certain requirements.
        :param next_token: Specify the pagination token returned by a previous request to retrieve
        the next page of results.
        :returns: GetTraceSummariesResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, next_token: String = None
    ) -> ListTagsForResourceResponse:
        """Returns a list of tags that are applied to the specified Amazon Web
        Services X-Ray group or sampling rule.

        :param resource_arn: The Amazon Resource Number (ARN) of an X-Ray group or sampling rule.
        :param next_token: A pagination token.
        :returns: ListTagsForResourceResponse
        :raises InvalidRequestException:
        :raises ThrottledException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("PutEncryptionConfig", expand=False)
    def put_encryption_config(
        self, context: RequestContext, request: PutEncryptionConfigRequest
    ) -> PutEncryptionConfigResult:
        """Updates the encryption configuration for X-Ray data.

        :param type: The type of encryption.
        :param key_id: An Amazon Web Services KMS key in one of the following formats:

        -  **Alias** - The name of the key.
        :returns: PutEncryptionConfigResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("PutTelemetryRecords")
    def put_telemetry_records(
        self,
        context: RequestContext,
        telemetry_records: TelemetryRecordList,
        ec2_instance_id: EC2InstanceId = None,
        hostname: Hostname = None,
        resource_arn: ResourceARN = None,
    ) -> PutTelemetryRecordsResult:
        """Used by the Amazon Web Services X-Ray daemon to upload telemetry.

        :param telemetry_records: .
        :param ec2_instance_id: .
        :param hostname: .
        :param resource_arn: .
        :returns: PutTelemetryRecordsResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("PutTraceSegments")
    def put_trace_segments(
        self, context: RequestContext, trace_segment_documents: TraceSegmentDocumentList
    ) -> PutTraceSegmentsResult:
        """Uploads segment documents to Amazon Web Services X-Ray. The `X-Ray
        SDK <https://docs.aws.amazon.com/xray/index.html>`__ generates segment
        documents and sends them to the X-Ray daemon, which uploads them in
        batches. A segment document can be a completed segment, an in-progress
        segment, or an array of subsegments.

        Segments must include the following fields. For the full segment
        document schema, see `Amazon Web Services X-Ray Segment
        Documents <https://docs.aws.amazon.com/xray/latest/devguide/xray-api-segmentdocuments.html>`__
        in the *Amazon Web Services X-Ray Developer Guide*.

        **Required segment document fields**

        -  ``name`` - The name of the service that handled the request.

        -  ``id`` - A 64-bit identifier for the segment, unique among segments
           in the same trace, in 16 hexadecimal digits.

        -  ``trace_id`` - A unique identifier that connects all segments and
           subsegments originating from a single client request.

        -  ``start_time`` - Time the segment or subsegment was created, in
           floating point seconds in epoch time, accurate to milliseconds. For
           example, ``1480615200.010`` or ``1.480615200010E9``.

        -  ``end_time`` - Time the segment or subsegment was closed. For
           example, ``1480615200.090`` or ``1.480615200090E9``. Specify either
           an ``end_time`` or ``in_progress``.

        -  ``in_progress`` - Set to ``true`` instead of specifying an
           ``end_time`` to record that a segment has been started, but is not
           complete. Send an in-progress segment when your application receives
           a request that will take a long time to serve, to trace that the
           request was received. When the response is sent, send the complete
           segment to overwrite the in-progress segment.

        A ``trace_id`` consists of three numbers separated by hyphens. For
        example, 1-58406520-a006649127e371903a2de979. This includes:

        **Trace ID Format**

        -  The version number, for instance, ``1``.

        -  The time of the original request, in Unix epoch time, in 8
           hexadecimal digits. For example, 10:00AM December 2nd, 2016 PST in
           epoch time is ``1480615200`` seconds, or ``58406520`` in hexadecimal.

        -  A 96-bit identifier for the trace, globally unique, in 24 hexadecimal
           digits.

        :param trace_segment_documents: A string containing a JSON document defining one or more segments or
        subsegments.
        :returns: PutTraceSegmentsResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tags: TagList
    ) -> TagResourceResponse:
        """Applies tags to an existing Amazon Web Services X-Ray group or sampling
        rule.

        :param resource_arn: The Amazon Resource Number (ARN) of an X-Ray group or sampling rule.
        :param tags: A map that contains one or more tag keys and tag values to attach to an
        X-Ray group or sampling rule.
        :returns: TagResourceResponse
        :raises InvalidRequestException:
        :raises ThrottledException:
        :raises ResourceNotFoundException:
        :raises TooManyTagsException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tag_keys: TagKeyList
    ) -> UntagResourceResponse:
        """Removes tags from an Amazon Web Services X-Ray group or sampling rule.
        You cannot edit or delete system tags (those with an ``aws:`` prefix).

        :param resource_arn: The Amazon Resource Number (ARN) of an X-Ray group or sampling rule.
        :param tag_keys: Keys for one or more tags that you want to remove from an X-Ray group or
        sampling rule.
        :returns: UntagResourceResponse
        :raises InvalidRequestException:
        :raises ThrottledException:
        :raises ResourceNotFoundException:
        """
        raise NotImplementedError

    @handler("UpdateGroup")
    def update_group(
        self,
        context: RequestContext,
        group_name: GroupName = None,
        group_arn: GroupARN = None,
        filter_expression: FilterExpression = None,
        insights_configuration: InsightsConfiguration = None,
    ) -> UpdateGroupResult:
        """Updates a group resource.

        :param group_name: The case-sensitive name of the group.
        :param group_arn: The ARN that was generated upon creation.
        :param filter_expression: The updated filter expression defining criteria by which to group
        traces.
        :param insights_configuration: The structure containing configurations related to insights.
        :returns: UpdateGroupResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError

    @handler("UpdateSamplingRule")
    def update_sampling_rule(
        self, context: RequestContext, sampling_rule_update: SamplingRuleUpdate
    ) -> UpdateSamplingRuleResult:
        """Modifies a sampling rule's configuration.

        :param sampling_rule_update: The rule and fields to change.
        :returns: UpdateSamplingRuleResult
        :raises InvalidRequestException:
        :raises ThrottledException:
        """
        raise NotImplementedError
