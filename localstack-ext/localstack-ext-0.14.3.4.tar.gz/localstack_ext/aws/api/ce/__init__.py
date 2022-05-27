import sys
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AmortizedRecurringFee = str
AmortizedUpfrontFee = str
Arn = str
AttributeType = str
AttributeValue = str
CostCategoryMaxResults = int
CostCategoryName = str
CostCategoryValue = str
CoverageHoursPercentage = str
CoverageNormalizedUnitsPercentage = str
Entity = str
ErrorMessage = str
Estimated = bool
GenericBoolean = bool
GenericDouble = float
GenericString = str
GroupDefinitionKey = str
Key = str
MaxResults = int
MetricAmount = str
MetricName = str
MetricUnit = str
NetRISavings = str
NextPageToken = str
NonNegativeInteger = int
NullableNonNegativeDouble = float
OnDemandCost = str
OnDemandCostOfRIHoursUsed = str
OnDemandHours = str
OnDemandNormalizedUnits = str
PageSize = int
PredictionIntervalLevel = int
PurchasedHours = str
PurchasedUnits = str
RICostForUnusedHours = str
RealizedSavings = str
ReservationGroupKey = str
ReservationGroupValue = str
ReservedHours = str
ReservedNormalizedUnits = str
ResourceTagKey = str
ResourceTagValue = str
SavingsPlanArn = str
SearchString = str
SortDefinitionKey = str
SubscriberAddress = str
TagKey = str
TotalActualHours = str
TotalActualUnits = str
TotalAmortizedFee = str
TotalPotentialRISavings = str
TotalRunningHours = str
TotalRunningNormalizedUnits = str
UnrealizedSavings = str
UnusedHours = str
UnusedUnits = str
UtilizationPercentage = str
UtilizationPercentageInUnits = str
Value = str
YearMonthDay = str
ZonedDateTime = str


class AccountScope(str):
    PAYER = "PAYER"
    LINKED = "LINKED"


class AnomalyFeedbackType(str):
    YES = "YES"
    NO = "NO"
    PLANNED_ACTIVITY = "PLANNED_ACTIVITY"


class AnomalySubscriptionFrequency(str):
    DAILY = "DAILY"
    IMMEDIATE = "IMMEDIATE"
    WEEKLY = "WEEKLY"


class Context(str):
    COST_AND_USAGE = "COST_AND_USAGE"
    RESERVATIONS = "RESERVATIONS"
    SAVINGS_PLANS = "SAVINGS_PLANS"


class CostCategoryInheritedValueDimensionName(str):
    LINKED_ACCOUNT_NAME = "LINKED_ACCOUNT_NAME"
    TAG = "TAG"


class CostCategoryRuleType(str):
    REGULAR = "REGULAR"
    INHERITED_VALUE = "INHERITED_VALUE"


class CostCategoryRuleVersion(str):
    CostCategoryExpression_v1 = "CostCategoryExpression.v1"


class CostCategorySplitChargeMethod(str):
    FIXED = "FIXED"
    PROPORTIONAL = "PROPORTIONAL"
    EVEN = "EVEN"


class CostCategorySplitChargeRuleParameterType(str):
    ALLOCATION_PERCENTAGES = "ALLOCATION_PERCENTAGES"


class CostCategoryStatus(str):
    PROCESSING = "PROCESSING"
    APPLIED = "APPLIED"


class CostCategoryStatusComponent(str):
    COST_EXPLORER = "COST_EXPLORER"


class Dimension(str):
    AZ = "AZ"
    INSTANCE_TYPE = "INSTANCE_TYPE"
    LINKED_ACCOUNT = "LINKED_ACCOUNT"
    LINKED_ACCOUNT_NAME = "LINKED_ACCOUNT_NAME"
    OPERATION = "OPERATION"
    PURCHASE_TYPE = "PURCHASE_TYPE"
    REGION = "REGION"
    SERVICE = "SERVICE"
    SERVICE_CODE = "SERVICE_CODE"
    USAGE_TYPE = "USAGE_TYPE"
    USAGE_TYPE_GROUP = "USAGE_TYPE_GROUP"
    RECORD_TYPE = "RECORD_TYPE"
    OPERATING_SYSTEM = "OPERATING_SYSTEM"
    TENANCY = "TENANCY"
    SCOPE = "SCOPE"
    PLATFORM = "PLATFORM"
    SUBSCRIPTION_ID = "SUBSCRIPTION_ID"
    LEGAL_ENTITY_NAME = "LEGAL_ENTITY_NAME"
    DEPLOYMENT_OPTION = "DEPLOYMENT_OPTION"
    DATABASE_ENGINE = "DATABASE_ENGINE"
    CACHE_ENGINE = "CACHE_ENGINE"
    INSTANCE_TYPE_FAMILY = "INSTANCE_TYPE_FAMILY"
    BILLING_ENTITY = "BILLING_ENTITY"
    RESERVATION_ID = "RESERVATION_ID"
    RESOURCE_ID = "RESOURCE_ID"
    RIGHTSIZING_TYPE = "RIGHTSIZING_TYPE"
    SAVINGS_PLANS_TYPE = "SAVINGS_PLANS_TYPE"
    SAVINGS_PLAN_ARN = "SAVINGS_PLAN_ARN"
    PAYMENT_OPTION = "PAYMENT_OPTION"
    AGREEMENT_END_DATE_TIME_AFTER = "AGREEMENT_END_DATE_TIME_AFTER"
    AGREEMENT_END_DATE_TIME_BEFORE = "AGREEMENT_END_DATE_TIME_BEFORE"
    INVOICING_ENTITY = "INVOICING_ENTITY"


class FindingReasonCode(str):
    CPU_OVER_PROVISIONED = "CPU_OVER_PROVISIONED"
    CPU_UNDER_PROVISIONED = "CPU_UNDER_PROVISIONED"
    MEMORY_OVER_PROVISIONED = "MEMORY_OVER_PROVISIONED"
    MEMORY_UNDER_PROVISIONED = "MEMORY_UNDER_PROVISIONED"
    EBS_THROUGHPUT_OVER_PROVISIONED = "EBS_THROUGHPUT_OVER_PROVISIONED"
    EBS_THROUGHPUT_UNDER_PROVISIONED = "EBS_THROUGHPUT_UNDER_PROVISIONED"
    EBS_IOPS_OVER_PROVISIONED = "EBS_IOPS_OVER_PROVISIONED"
    EBS_IOPS_UNDER_PROVISIONED = "EBS_IOPS_UNDER_PROVISIONED"
    NETWORK_BANDWIDTH_OVER_PROVISIONED = "NETWORK_BANDWIDTH_OVER_PROVISIONED"
    NETWORK_BANDWIDTH_UNDER_PROVISIONED = "NETWORK_BANDWIDTH_UNDER_PROVISIONED"
    NETWORK_PPS_OVER_PROVISIONED = "NETWORK_PPS_OVER_PROVISIONED"
    NETWORK_PPS_UNDER_PROVISIONED = "NETWORK_PPS_UNDER_PROVISIONED"
    DISK_IOPS_OVER_PROVISIONED = "DISK_IOPS_OVER_PROVISIONED"
    DISK_IOPS_UNDER_PROVISIONED = "DISK_IOPS_UNDER_PROVISIONED"
    DISK_THROUGHPUT_OVER_PROVISIONED = "DISK_THROUGHPUT_OVER_PROVISIONED"
    DISK_THROUGHPUT_UNDER_PROVISIONED = "DISK_THROUGHPUT_UNDER_PROVISIONED"


class Granularity(str):
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    HOURLY = "HOURLY"


class GroupDefinitionType(str):
    DIMENSION = "DIMENSION"
    TAG = "TAG"
    COST_CATEGORY = "COST_CATEGORY"


class LookbackPeriodInDays(str):
    SEVEN_DAYS = "SEVEN_DAYS"
    THIRTY_DAYS = "THIRTY_DAYS"
    SIXTY_DAYS = "SIXTY_DAYS"


class MatchOption(str):
    EQUALS = "EQUALS"
    ABSENT = "ABSENT"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    CONTAINS = "CONTAINS"
    CASE_SENSITIVE = "CASE_SENSITIVE"
    CASE_INSENSITIVE = "CASE_INSENSITIVE"


class Metric(str):
    BLENDED_COST = "BLENDED_COST"
    UNBLENDED_COST = "UNBLENDED_COST"
    AMORTIZED_COST = "AMORTIZED_COST"
    NET_UNBLENDED_COST = "NET_UNBLENDED_COST"
    NET_AMORTIZED_COST = "NET_AMORTIZED_COST"
    USAGE_QUANTITY = "USAGE_QUANTITY"
    NORMALIZED_USAGE_AMOUNT = "NORMALIZED_USAGE_AMOUNT"


class MonitorDimension(str):
    SERVICE = "SERVICE"


class MonitorType(str):
    DIMENSIONAL = "DIMENSIONAL"
    CUSTOM = "CUSTOM"


class NumericOperator(str):
    EQUAL = "EQUAL"
    GREATER_THAN_OR_EQUAL = "GREATER_THAN_OR_EQUAL"
    LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    BETWEEN = "BETWEEN"


class OfferingClass(str):
    STANDARD = "STANDARD"
    CONVERTIBLE = "CONVERTIBLE"


class PaymentOption(str):
    NO_UPFRONT = "NO_UPFRONT"
    PARTIAL_UPFRONT = "PARTIAL_UPFRONT"
    ALL_UPFRONT = "ALL_UPFRONT"
    LIGHT_UTILIZATION = "LIGHT_UTILIZATION"
    MEDIUM_UTILIZATION = "MEDIUM_UTILIZATION"
    HEAVY_UTILIZATION = "HEAVY_UTILIZATION"


class PlatformDifference(str):
    HYPERVISOR = "HYPERVISOR"
    NETWORK_INTERFACE = "NETWORK_INTERFACE"
    STORAGE_INTERFACE = "STORAGE_INTERFACE"
    INSTANCE_STORE_AVAILABILITY = "INSTANCE_STORE_AVAILABILITY"
    VIRTUALIZATION_TYPE = "VIRTUALIZATION_TYPE"


class RecommendationTarget(str):
    SAME_INSTANCE_FAMILY = "SAME_INSTANCE_FAMILY"
    CROSS_INSTANCE_FAMILY = "CROSS_INSTANCE_FAMILY"


class RightsizingType(str):
    TERMINATE = "TERMINATE"
    MODIFY = "MODIFY"


class SavingsPlansDataType(str):
    ATTRIBUTES = "ATTRIBUTES"
    UTILIZATION = "UTILIZATION"
    AMORTIZED_COMMITMENT = "AMORTIZED_COMMITMENT"
    SAVINGS = "SAVINGS"


class SortOrder(str):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"


class SubscriberStatus(str):
    CONFIRMED = "CONFIRMED"
    DECLINED = "DECLINED"


class SubscriberType(str):
    EMAIL = "EMAIL"
    SNS = "SNS"


class SupportedSavingsPlansType(str):
    COMPUTE_SP = "COMPUTE_SP"
    EC2_INSTANCE_SP = "EC2_INSTANCE_SP"
    SAGEMAKER_SP = "SAGEMAKER_SP"


class TermInYears(str):
    ONE_YEAR = "ONE_YEAR"
    THREE_YEARS = "THREE_YEARS"


class BillExpirationException(ServiceException):
    """The requested report expired. Update the date interval and try again."""

    Message: Optional[ErrorMessage]


class DataUnavailableException(ServiceException):
    """The requested data is unavailable."""

    Message: Optional[ErrorMessage]


class InvalidNextTokenException(ServiceException):
    """The pagination token is invalid. Try again without a pagination token."""

    Message: Optional[ErrorMessage]


class LimitExceededException(ServiceException):
    """You made too many calls in a short period of time. Try again later."""

    Message: Optional[ErrorMessage]


class RequestChangedException(ServiceException):
    """Your request parameters changed between pages. Try again with the old
    parameters or without a pagination token.
    """

    Message: Optional[ErrorMessage]


class ResourceNotFoundException(ServiceException):
    """The specified ARN in the request doesn't exist."""

    Message: Optional[ErrorMessage]
    ResourceName: Optional[Arn]


class ServiceQuotaExceededException(ServiceException):
    """You've reached the limit on the number of resources you can create, or
    exceeded the size of an individual resource.
    """

    Message: Optional[ErrorMessage]


class TooManyTagsException(ServiceException):
    """Can occur if you specify a number of tags for a resource greater than
    the maximum 50 user tags per resource.
    """

    Message: Optional[ErrorMessage]
    ResourceName: Optional[Arn]


class UnknownMonitorException(ServiceException):
    """The cost anomaly monitor does not exist for the account."""

    Message: Optional[ErrorMessage]


class UnknownSubscriptionException(ServiceException):
    """The cost anomaly subscription does not exist for the account."""

    Message: Optional[ErrorMessage]


class UnresolvableUsageUnitException(ServiceException):
    """Cost Explorer was unable to identify the usage unit. Provide
    ``UsageType/UsageTypeGroup`` filter selections that contain matching
    units, for example: ``hours``.
    """

    Message: Optional[ErrorMessage]


class Impact(TypedDict, total=False):
    """The dollar value of the anomaly."""

    MaxImpact: GenericDouble
    TotalImpact: Optional[GenericDouble]


class AnomalyScore(TypedDict, total=False):
    """Quantifies the anomaly. The higher score means that it's more anomalous."""

    MaxScore: GenericDouble
    CurrentScore: GenericDouble


class RootCause(TypedDict, total=False):
    """The combination of Amazon Web Services service, linked account, Region,
    and usage type where a cost anomaly is observed.
    """

    Service: Optional[GenericString]
    Region: Optional[GenericString]
    LinkedAccount: Optional[GenericString]
    UsageType: Optional[GenericString]


RootCauses = List[RootCause]


class Anomaly(TypedDict, total=False):
    """An unusual cost pattern. This consists of the detailed metadata and the
    current status of the anomaly object.
    """

    AnomalyId: GenericString
    AnomalyStartDate: Optional[YearMonthDay]
    AnomalyEndDate: Optional[YearMonthDay]
    DimensionValue: Optional[GenericString]
    RootCauses: Optional[RootCauses]
    AnomalyScore: AnomalyScore
    Impact: Impact
    MonitorArn: GenericString
    Feedback: Optional[AnomalyFeedbackType]


Anomalies = List[Anomaly]


class AnomalyDateInterval(TypedDict, total=False):
    """The time period for an anomaly."""

    StartDate: YearMonthDay
    EndDate: Optional[YearMonthDay]


MatchOptions = List[MatchOption]
Values = List[Value]


class CostCategoryValues(TypedDict, total=False):
    """The Cost Categories values used for filtering the costs.

    If ``Values`` and ``Key`` are not specified, the ``ABSENT``
    ``MatchOption`` is applied to all Cost Categories. That is, it filters
    on resources that aren't mapped to any Cost Categories.

    If ``Values`` is provided and ``Key`` isn't specified, the ``ABSENT``
    ``MatchOption`` is applied to the Cost Categories ``Key`` only. That is,
    it filters on resources without the given Cost Categories key.
    """

    Key: Optional[CostCategoryName]
    Values: Optional[Values]
    MatchOptions: Optional[MatchOptions]


class TagValues(TypedDict, total=False):
    """The values that are available for a tag.

    If ``Values`` and ``Key`` aren't specified, the ``ABSENT``
    ``MatchOption`` is applied to all tags. That is, it's filtered on
    resources with no tags.

    If ``Values`` is provided and ``Key`` isn't specified, the ``ABSENT``
    ``MatchOption`` is applied to the tag ``Key`` only. That is, it's
    filtered on resources without the given tag key.
    """

    Key: Optional[TagKey]
    Values: Optional[Values]
    MatchOptions: Optional[MatchOptions]


class DimensionValues(TypedDict, total=False):
    """The metadata that you can use to filter and group your results. You can
    use ``GetDimensionValues`` to find specific values.
    """

    Key: Optional[Dimension]
    Values: Optional[Values]
    MatchOptions: Optional[MatchOptions]


class Expression(TypedDict, total=False):
    """Use ``Expression`` to filter by cost or by usage. There are two
    patterns:

    -  Simple dimension values - You can set the dimension name and values
       for the filters that you plan to use. For example, you can filter for
       ``REGION==us-east-1 OR REGION==us-west-1``. For
       ``GetRightsizingRecommendation``, the Region is a full name (for
       example, ``REGION==US East (N. Virginia)``. The ``Expression``
       example is as follows:

       ``{ "Dimensions": { "Key": "REGION", "Values": [ "us-east-1", “us-west-1” ] } }``

       The list of dimension values are OR'd together to retrieve cost or
       usage data. You can create ``Expression`` and ``DimensionValues``
       objects using either ``with*`` methods or ``set*`` methods in
       multiple lines.

    -  Compound dimension values with logical operations - You can use
       multiple ``Expression`` types and the logical operators
       ``AND/OR/NOT`` to create a list of one or more ``Expression``
       objects. By doing this, you can filter on more advanced options. For
       example, you can filter on
       ``((REGION == us-east-1 OR REGION == us-west-1) OR (TAG.Type == Type1)) AND (USAGE_TYPE != DataTransfer)``.
       The ``Expression`` for that is as follows:

       ``{ "And": [ {"Or": [ {"Dimensions": { "Key": "REGION", "Values": [ "us-east-1", "us-west-1" ] }}, {"Tags": { "Key": "TagName", "Values": ["Value1"] } } ]}, {"Not": {"Dimensions": { "Key": "USAGE_TYPE", "Values": ["DataTransfer"] }}} ] }``

       Because each ``Expression`` can have only one operator, the service
       returns an error if more than one is specified. The following example
       shows an ``Expression`` object that creates an error.

       ``{ "And": [ ... ], "DimensionValues": { "Dimension": "USAGE_TYPE", "Values": [ "DataTransfer" ] } }``

    For the ``GetRightsizingRecommendation`` action, a combination of OR and
    NOT isn't supported. OR isn't supported between different dimensions, or
    dimensions and tags. NOT operators aren't supported. Dimensions are also
    limited to ``LINKED_ACCOUNT``, ``REGION``, or ``RIGHTSIZING_TYPE``.

    For the ``GetReservationPurchaseRecommendation`` action, only NOT is
    supported. AND and OR aren't supported. Dimensions are limited to
    ``LINKED_ACCOUNT``.
    """

    Or: Optional["Expressions"]
    And: Optional["Expressions"]
    Not: Optional["Expression"]
    Dimensions: Optional["DimensionValues"]
    Tags: Optional["TagValues"]
    CostCategories: Optional["CostCategoryValues"]


Expressions = List[Expression]


class AnomalyMonitor(TypedDict, total=False):
    """This object continuously inspects your account's cost data for
    anomalies. It's based on ``MonitorType`` and ``MonitorSpecification``.
    The content consists of detailed metadata and the current status of the
    monitor object.
    """

    MonitorArn: Optional[GenericString]
    MonitorName: GenericString
    CreationDate: Optional[YearMonthDay]
    LastUpdatedDate: Optional[YearMonthDay]
    LastEvaluatedDate: Optional[YearMonthDay]
    MonitorType: MonitorType
    MonitorDimension: Optional[MonitorDimension]
    MonitorSpecification: Optional[Expression]
    DimensionalValueCount: Optional[NonNegativeInteger]


AnomalyMonitors = List[AnomalyMonitor]


class Subscriber(TypedDict, total=False):
    """The recipient of ``AnomalySubscription`` notifications."""

    Address: Optional[SubscriberAddress]
    Type: Optional[SubscriberType]
    Status: Optional[SubscriberStatus]


Subscribers = List[Subscriber]
MonitorArnList = List[Arn]


class AnomalySubscription(TypedDict, total=False):
    """The association between a monitor, threshold, and list of subscribers
    used to deliver notifications about anomalies detected by a monitor that
    exceeds a threshold. The content consists of the detailed metadata and
    the current status of the ``AnomalySubscription`` object.
    """

    SubscriptionArn: Optional[GenericString]
    AccountId: Optional[GenericString]
    MonitorArnList: MonitorArnList
    Subscribers: Subscribers
    Threshold: NullableNonNegativeDouble
    Frequency: AnomalySubscriptionFrequency
    SubscriptionName: GenericString


AnomalySubscriptions = List[AnomalySubscription]
Attributes = Dict[AttributeType, AttributeValue]


class CostCategoryProcessingStatus(TypedDict, total=False):
    """The list of processing statuses for Cost Management products for a
    specific cost category.
    """

    Component: Optional[CostCategoryStatusComponent]
    Status: Optional[CostCategoryStatus]


CostCategoryProcessingStatusList = List[CostCategoryProcessingStatus]
CostCategorySplitChargeRuleParameterValuesList = List[GenericString]


class CostCategorySplitChargeRuleParameter(TypedDict, total=False):
    """The parameters for a split charge method."""

    Type: CostCategorySplitChargeRuleParameterType
    Values: CostCategorySplitChargeRuleParameterValuesList


CostCategorySplitChargeRuleParametersList = List[CostCategorySplitChargeRuleParameter]
CostCategorySplitChargeRuleTargetsList = List[GenericString]


class CostCategorySplitChargeRule(TypedDict, total=False):
    """Use the split charge rule to split the cost of one Cost Category value
    across several other target values.
    """

    Source: GenericString
    Targets: CostCategorySplitChargeRuleTargetsList
    Method: CostCategorySplitChargeMethod
    Parameters: Optional[CostCategorySplitChargeRuleParametersList]


CostCategorySplitChargeRulesList = List[CostCategorySplitChargeRule]


class CostCategoryInheritedValueDimension(TypedDict, total=False):
    """When creating or updating a cost category, you can define the
    ``CostCategoryRule`` rule type as ``INHERITED_VALUE``. This rule type
    adds the flexibility of defining a rule that dynamically inherits the
    cost category value from the dimension value defined by
    ``CostCategoryInheritedValueDimension``. For example, if you want to
    dynamically group costs that are based on the value of a specific tag
    key, first choose an inherited value rule type, then choose the tag
    dimension and specify the tag key to use.
    """

    DimensionName: Optional[CostCategoryInheritedValueDimensionName]
    DimensionKey: Optional[GenericString]


class CostCategoryRule(TypedDict, total=False):
    """Rules are processed in order. If there are multiple rules that match the
    line item, then the first rule to match is used to determine that Cost
    Category value.
    """

    Value: Optional[CostCategoryValue]
    Rule: Optional[Expression]
    InheritedValue: Optional[CostCategoryInheritedValueDimension]
    Type: Optional[CostCategoryRuleType]


CostCategoryRulesList = List[CostCategoryRule]


class CostCategory(TypedDict, total=False):
    """The structure of Cost Categories. This includes detailed metadata and
    the set of rules for the ``CostCategory`` object.
    """

    CostCategoryArn: Arn
    EffectiveStart: ZonedDateTime
    EffectiveEnd: Optional[ZonedDateTime]
    Name: CostCategoryName
    RuleVersion: CostCategoryRuleVersion
    Rules: CostCategoryRulesList
    SplitChargeRules: Optional[CostCategorySplitChargeRulesList]
    ProcessingStatus: Optional[CostCategoryProcessingStatusList]
    DefaultValue: Optional[CostCategoryValue]


CostCategoryNamesList = List[CostCategoryName]
CostCategoryValuesList = List[CostCategoryValue]


class CostCategoryReference(TypedDict, total=False):
    """A reference to a Cost Category containing only enough information to
    identify the Cost Category.

    You can use this information to retrieve the full Cost Category
    information using ``DescribeCostCategory``.
    """

    CostCategoryArn: Optional[Arn]
    Name: Optional[CostCategoryName]
    EffectiveStart: Optional[ZonedDateTime]
    EffectiveEnd: Optional[ZonedDateTime]
    NumberOfRules: Optional[NonNegativeInteger]
    ProcessingStatus: Optional[CostCategoryProcessingStatusList]
    Values: Optional[CostCategoryValuesList]
    DefaultValue: Optional[CostCategoryValue]


CostCategoryReferencesList = List[CostCategoryReference]


class CoverageCost(TypedDict, total=False):
    """How much it costs to run an instance."""

    OnDemandCost: Optional[OnDemandCost]


class CoverageNormalizedUnits(TypedDict, total=False):
    """The amount of instance usage, in normalized units. You can use
    normalized units to see your EC2 usage for multiple sizes of instances
    in a uniform way. For example, suppose that you run an xlarge instance
    and a 2xlarge instance. If you run both instances for the same amount of
    time, the 2xlarge instance uses twice as much of your reservation as the
    xlarge instance, even though both instances show only one instance-hour.
    When you use normalized units instead of instance-hours, the xlarge
    instance used 8 normalized units, and the 2xlarge instance used 16
    normalized units.

    For more information, see `Modifying Reserved
    Instances <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ri-modifying.html>`__
    in the *Amazon Elastic Compute Cloud User Guide for Linux Instances*.
    """

    OnDemandNormalizedUnits: Optional[OnDemandNormalizedUnits]
    ReservedNormalizedUnits: Optional[ReservedNormalizedUnits]
    TotalRunningNormalizedUnits: Optional[TotalRunningNormalizedUnits]
    CoverageNormalizedUnitsPercentage: Optional[CoverageNormalizedUnitsPercentage]


class CoverageHours(TypedDict, total=False):
    """How long a running instance either used a reservation or was On-Demand."""

    OnDemandHours: Optional[OnDemandHours]
    ReservedHours: Optional[ReservedHours]
    TotalRunningHours: Optional[TotalRunningHours]
    CoverageHoursPercentage: Optional[CoverageHoursPercentage]


class Coverage(TypedDict, total=False):
    """The amount of instance usage that a reservation covered."""

    CoverageHours: Optional[CoverageHours]
    CoverageNormalizedUnits: Optional[CoverageNormalizedUnits]
    CoverageCost: Optional[CoverageCost]


class ReservationCoverageGroup(TypedDict, total=False):
    """A group of reservations that share a set of attributes."""

    Attributes: Optional[Attributes]
    Coverage: Optional[Coverage]


ReservationCoverageGroups = List[ReservationCoverageGroup]


class DateInterval(TypedDict, total=False):
    """The time period of the request."""

    Start: YearMonthDay
    End: YearMonthDay


class CoverageByTime(TypedDict, total=False):
    """Reservation coverage for a specified period, in hours."""

    TimePeriod: Optional[DateInterval]
    Groups: Optional[ReservationCoverageGroups]
    Total: Optional[Coverage]


CoveragesByTime = List[CoverageByTime]


class ResourceTag(TypedDict, total=False):
    """The tag structure that contains a tag key and value.

    Tagging is supported only for the following Cost Explorer resource
    types:
    ```AnomalyMonitor`` <https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_AnomalyMonitor.html>`__
    ,
    ```AnomalySubscription`` <https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_AnomalySubscription.html>`__
    ,
    ```CostCategory`` <https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_CostCategory.html>`__
    .
    """

    Key: ResourceTagKey
    Value: ResourceTagValue


ResourceTagList = List[ResourceTag]


class CreateAnomalyMonitorRequest(ServiceRequest):
    AnomalyMonitor: AnomalyMonitor
    ResourceTags: Optional[ResourceTagList]


class CreateAnomalyMonitorResponse(TypedDict, total=False):
    MonitorArn: GenericString


class CreateAnomalySubscriptionRequest(ServiceRequest):
    AnomalySubscription: AnomalySubscription
    ResourceTags: Optional[ResourceTagList]


class CreateAnomalySubscriptionResponse(TypedDict, total=False):
    SubscriptionArn: GenericString


class CreateCostCategoryDefinitionRequest(ServiceRequest):
    Name: CostCategoryName
    RuleVersion: CostCategoryRuleVersion
    Rules: CostCategoryRulesList
    DefaultValue: Optional[CostCategoryValue]
    SplitChargeRules: Optional[CostCategorySplitChargeRulesList]
    ResourceTags: Optional[ResourceTagList]


class CreateCostCategoryDefinitionResponse(TypedDict, total=False):
    CostCategoryArn: Optional[Arn]
    EffectiveStart: Optional[ZonedDateTime]


class NetworkResourceUtilization(TypedDict, total=False):
    """The network field that contains a list of network metrics that are
    associated with the current instance.
    """

    NetworkInBytesPerSecond: Optional[GenericString]
    NetworkOutBytesPerSecond: Optional[GenericString]
    NetworkPacketsInPerSecond: Optional[GenericString]
    NetworkPacketsOutPerSecond: Optional[GenericString]


class DiskResourceUtilization(TypedDict, total=False):
    """The field that contains a list of disk (local storage) metrics that are
    associated with the current instance.
    """

    DiskReadOpsPerSecond: Optional[GenericString]
    DiskWriteOpsPerSecond: Optional[GenericString]
    DiskReadBytesPerSecond: Optional[GenericString]
    DiskWriteBytesPerSecond: Optional[GenericString]


class EBSResourceUtilization(TypedDict, total=False):
    """The EBS field that contains a list of EBS metrics that are associated
    with the current instance.
    """

    EbsReadOpsPerSecond: Optional[GenericString]
    EbsWriteOpsPerSecond: Optional[GenericString]
    EbsReadBytesPerSecond: Optional[GenericString]
    EbsWriteBytesPerSecond: Optional[GenericString]


class EC2ResourceUtilization(TypedDict, total=False):
    """Utilization metrics of the instance."""

    MaxCpuUtilizationPercentage: Optional[GenericString]
    MaxMemoryUtilizationPercentage: Optional[GenericString]
    MaxStorageUtilizationPercentage: Optional[GenericString]
    EBSResourceUtilization: Optional[EBSResourceUtilization]
    DiskResourceUtilization: Optional[DiskResourceUtilization]
    NetworkResourceUtilization: Optional[NetworkResourceUtilization]


class ResourceUtilization(TypedDict, total=False):
    """Resource utilization of current resource."""

    EC2ResourceUtilization: Optional[EC2ResourceUtilization]


class EC2ResourceDetails(TypedDict, total=False):
    """Details on the Amazon EC2 Resource."""

    HourlyOnDemandRate: Optional[GenericString]
    InstanceType: Optional[GenericString]
    Platform: Optional[GenericString]
    Region: Optional[GenericString]
    Sku: Optional[GenericString]
    Memory: Optional[GenericString]
    NetworkPerformance: Optional[GenericString]
    Storage: Optional[GenericString]
    Vcpu: Optional[GenericString]


class ResourceDetails(TypedDict, total=False):
    """Details on the resource."""

    EC2ResourceDetails: Optional[EC2ResourceDetails]


TagValuesList = List[TagValues]


class CurrentInstance(TypedDict, total=False):
    """Context about the current instance."""

    ResourceId: Optional[GenericString]
    InstanceName: Optional[GenericString]
    Tags: Optional[TagValuesList]
    ResourceDetails: Optional[ResourceDetails]
    ResourceUtilization: Optional[ResourceUtilization]
    ReservationCoveredHoursInLookbackPeriod: Optional[GenericString]
    SavingsPlansCoveredHoursInLookbackPeriod: Optional[GenericString]
    OnDemandHoursInLookbackPeriod: Optional[GenericString]
    TotalRunningHoursInLookbackPeriod: Optional[GenericString]
    MonthlyCost: Optional[GenericString]
    CurrencyCode: Optional[GenericString]


class DeleteAnomalyMonitorRequest(ServiceRequest):
    MonitorArn: GenericString


class DeleteAnomalyMonitorResponse(TypedDict, total=False):
    pass


class DeleteAnomalySubscriptionRequest(ServiceRequest):
    SubscriptionArn: GenericString


class DeleteAnomalySubscriptionResponse(TypedDict, total=False):
    pass


class DeleteCostCategoryDefinitionRequest(ServiceRequest):
    CostCategoryArn: Arn


class DeleteCostCategoryDefinitionResponse(TypedDict, total=False):
    CostCategoryArn: Optional[Arn]
    EffectiveEnd: Optional[ZonedDateTime]


class DescribeCostCategoryDefinitionRequest(ServiceRequest):
    CostCategoryArn: Arn
    EffectiveOn: Optional[ZonedDateTime]


class DescribeCostCategoryDefinitionResponse(TypedDict, total=False):
    CostCategory: Optional[CostCategory]


class DimensionValuesWithAttributes(TypedDict, total=False):
    """The metadata of a specific type that you can use to filter and group
    your results. You can use ``GetDimensionValues`` to find specific
    values.
    """

    Value: Optional[Value]
    Attributes: Optional[Attributes]


DimensionValuesWithAttributesList = List[DimensionValuesWithAttributes]


class EC2InstanceDetails(TypedDict, total=False):
    """Details about the Amazon EC2 instances that Amazon Web Services
    recommends that you purchase.
    """

    Family: Optional[GenericString]
    InstanceType: Optional[GenericString]
    Region: Optional[GenericString]
    AvailabilityZone: Optional[GenericString]
    Platform: Optional[GenericString]
    Tenancy: Optional[GenericString]
    CurrentGeneration: Optional[GenericBoolean]
    SizeFlexEligible: Optional[GenericBoolean]


class EC2Specification(TypedDict, total=False):
    """The Amazon EC2 hardware specifications that you want Amazon Web Services
    to provide recommendations for.
    """

    OfferingClass: Optional[OfferingClass]


class ESInstanceDetails(TypedDict, total=False):
    """Details about the Amazon OpenSearch Service instances that Amazon Web
    Services recommends that you purchase.
    """

    InstanceClass: Optional[GenericString]
    InstanceSize: Optional[GenericString]
    Region: Optional[GenericString]
    CurrentGeneration: Optional[GenericBoolean]
    SizeFlexEligible: Optional[GenericBoolean]


class ElastiCacheInstanceDetails(TypedDict, total=False):
    """Details about the Amazon ElastiCache instances that Amazon Web Services
    recommends that you purchase.
    """

    Family: Optional[GenericString]
    NodeType: Optional[GenericString]
    Region: Optional[GenericString]
    ProductDescription: Optional[GenericString]
    CurrentGeneration: Optional[GenericBoolean]
    SizeFlexEligible: Optional[GenericBoolean]


FindingReasonCodes = List[FindingReasonCode]


class ForecastResult(TypedDict, total=False):
    """The forecast that's created for your query."""

    TimePeriod: Optional[DateInterval]
    MeanValue: Optional[GenericString]
    PredictionIntervalLowerBound: Optional[GenericString]
    PredictionIntervalUpperBound: Optional[GenericString]


ForecastResultsByTime = List[ForecastResult]


class TotalImpactFilter(TypedDict, total=False):
    """Filters cost anomalies based on the total impact."""

    NumericOperator: NumericOperator
    StartValue: GenericDouble
    EndValue: Optional[GenericDouble]


class GetAnomaliesRequest(ServiceRequest):
    MonitorArn: Optional[GenericString]
    DateInterval: AnomalyDateInterval
    Feedback: Optional[AnomalyFeedbackType]
    TotalImpact: Optional[TotalImpactFilter]
    NextPageToken: Optional[NextPageToken]
    MaxResults: Optional[PageSize]


class GetAnomaliesResponse(TypedDict, total=False):
    Anomalies: Anomalies
    NextPageToken: Optional[NextPageToken]


class GetAnomalyMonitorsRequest(ServiceRequest):
    MonitorArnList: Optional[Values]
    NextPageToken: Optional[NextPageToken]
    MaxResults: Optional[PageSize]


class GetAnomalyMonitorsResponse(TypedDict, total=False):
    AnomalyMonitors: AnomalyMonitors
    NextPageToken: Optional[NextPageToken]


class GetAnomalySubscriptionsRequest(ServiceRequest):
    SubscriptionArnList: Optional[Values]
    MonitorArn: Optional[GenericString]
    NextPageToken: Optional[NextPageToken]
    MaxResults: Optional[PageSize]


class GetAnomalySubscriptionsResponse(TypedDict, total=False):
    AnomalySubscriptions: AnomalySubscriptions
    NextPageToken: Optional[NextPageToken]


class GroupDefinition(TypedDict, total=False):
    """Represents a group when you specify a group by criteria or in the
    response to a query with a specific grouping.
    """

    Type: Optional[GroupDefinitionType]
    Key: Optional[GroupDefinitionKey]


GroupDefinitions = List[GroupDefinition]
MetricNames = List[MetricName]


class GetCostAndUsageRequest(ServiceRequest):
    TimePeriod: DateInterval
    Granularity: Granularity
    Filter: Optional[Expression]
    Metrics: MetricNames
    GroupBy: Optional[GroupDefinitions]
    NextPageToken: Optional[NextPageToken]


class MetricValue(TypedDict, total=False):
    """The aggregated value for a metric."""

    Amount: Optional[MetricAmount]
    Unit: Optional[MetricUnit]


Metrics = Dict[MetricName, MetricValue]
Keys = List[Key]


class Group(TypedDict, total=False):
    """One level of grouped data in the results."""

    Keys: Optional[Keys]
    Metrics: Optional[Metrics]


Groups = List[Group]


class ResultByTime(TypedDict, total=False):
    """The result that's associated with a time period."""

    TimePeriod: Optional[DateInterval]
    Total: Optional[Metrics]
    Groups: Optional[Groups]
    Estimated: Optional[Estimated]


ResultsByTime = List[ResultByTime]


class GetCostAndUsageResponse(TypedDict, total=False):
    NextPageToken: Optional[NextPageToken]
    GroupDefinitions: Optional[GroupDefinitions]
    ResultsByTime: Optional[ResultsByTime]
    DimensionValueAttributes: Optional[DimensionValuesWithAttributesList]


class GetCostAndUsageWithResourcesRequest(ServiceRequest):
    TimePeriod: DateInterval
    Granularity: Granularity
    Filter: Expression
    Metrics: Optional[MetricNames]
    GroupBy: Optional[GroupDefinitions]
    NextPageToken: Optional[NextPageToken]


class GetCostAndUsageWithResourcesResponse(TypedDict, total=False):
    NextPageToken: Optional[NextPageToken]
    GroupDefinitions: Optional[GroupDefinitions]
    ResultsByTime: Optional[ResultsByTime]
    DimensionValueAttributes: Optional[DimensionValuesWithAttributesList]


class SortDefinition(TypedDict, total=False):
    """The details of how to sort the data."""

    Key: SortDefinitionKey
    SortOrder: Optional[SortOrder]


SortDefinitions = List[SortDefinition]


class GetCostCategoriesRequest(ServiceRequest):
    SearchString: Optional[SearchString]
    TimePeriod: DateInterval
    CostCategoryName: Optional[CostCategoryName]
    Filter: Optional[Expression]
    SortBy: Optional[SortDefinitions]
    MaxResults: Optional[MaxResults]
    NextPageToken: Optional[NextPageToken]


class GetCostCategoriesResponse(TypedDict, total=False):
    NextPageToken: Optional[NextPageToken]
    CostCategoryNames: Optional[CostCategoryNamesList]
    CostCategoryValues: Optional[CostCategoryValuesList]
    ReturnSize: PageSize
    TotalSize: PageSize


class GetCostForecastRequest(ServiceRequest):
    TimePeriod: DateInterval
    Metric: Metric
    Granularity: Granularity
    Filter: Optional[Expression]
    PredictionIntervalLevel: Optional[PredictionIntervalLevel]


class GetCostForecastResponse(TypedDict, total=False):
    Total: Optional[MetricValue]
    ForecastResultsByTime: Optional[ForecastResultsByTime]


class GetDimensionValuesRequest(ServiceRequest):
    SearchString: Optional[SearchString]
    TimePeriod: DateInterval
    Dimension: Dimension
    Context: Optional[Context]
    Filter: Optional[Expression]
    SortBy: Optional[SortDefinitions]
    MaxResults: Optional[MaxResults]
    NextPageToken: Optional[NextPageToken]


class GetDimensionValuesResponse(TypedDict, total=False):
    DimensionValues: DimensionValuesWithAttributesList
    ReturnSize: PageSize
    TotalSize: PageSize
    NextPageToken: Optional[NextPageToken]


class GetReservationCoverageRequest(ServiceRequest):
    """You can use the following request parameters to query for how much of
    your instance usage a reservation covered.
    """

    TimePeriod: DateInterval
    GroupBy: Optional[GroupDefinitions]
    Granularity: Optional[Granularity]
    Filter: Optional[Expression]
    Metrics: Optional[MetricNames]
    NextPageToken: Optional[NextPageToken]
    SortBy: Optional[SortDefinition]
    MaxResults: Optional[MaxResults]


class GetReservationCoverageResponse(TypedDict, total=False):
    CoveragesByTime: CoveragesByTime
    Total: Optional[Coverage]
    NextPageToken: Optional[NextPageToken]


class ServiceSpecification(TypedDict, total=False):
    """Hardware specifications for the service that you want recommendations
    for.
    """

    EC2Specification: Optional[EC2Specification]


class GetReservationPurchaseRecommendationRequest(ServiceRequest):
    AccountId: Optional[GenericString]
    Service: GenericString
    Filter: Optional[Expression]
    AccountScope: Optional[AccountScope]
    LookbackPeriodInDays: Optional[LookbackPeriodInDays]
    TermInYears: Optional[TermInYears]
    PaymentOption: Optional[PaymentOption]
    ServiceSpecification: Optional[ServiceSpecification]
    PageSize: Optional[NonNegativeInteger]
    NextPageToken: Optional[NextPageToken]


class ReservationPurchaseRecommendationSummary(TypedDict, total=False):
    """A summary about this recommendation, such as the currency code, the
    amount that Amazon Web Services estimates that you could save, and the
    total amount of reservation to purchase.
    """

    TotalEstimatedMonthlySavingsAmount: Optional[GenericString]
    TotalEstimatedMonthlySavingsPercentage: Optional[GenericString]
    CurrencyCode: Optional[GenericString]


class RedshiftInstanceDetails(TypedDict, total=False):
    """Details about the Amazon Redshift instances that Amazon Web Services
    recommends that you purchase.
    """

    Family: Optional[GenericString]
    NodeType: Optional[GenericString]
    Region: Optional[GenericString]
    CurrentGeneration: Optional[GenericBoolean]
    SizeFlexEligible: Optional[GenericBoolean]


class RDSInstanceDetails(TypedDict, total=False):
    """Details about the Amazon RDS instances that Amazon Web Services
    recommends that you purchase.
    """

    Family: Optional[GenericString]
    InstanceType: Optional[GenericString]
    Region: Optional[GenericString]
    DatabaseEngine: Optional[GenericString]
    DatabaseEdition: Optional[GenericString]
    DeploymentOption: Optional[GenericString]
    LicenseModel: Optional[GenericString]
    CurrentGeneration: Optional[GenericBoolean]
    SizeFlexEligible: Optional[GenericBoolean]


class InstanceDetails(TypedDict, total=False):
    """Details about the instances that Amazon Web Services recommends that you
    purchase.
    """

    EC2InstanceDetails: Optional[EC2InstanceDetails]
    RDSInstanceDetails: Optional[RDSInstanceDetails]
    RedshiftInstanceDetails: Optional[RedshiftInstanceDetails]
    ElastiCacheInstanceDetails: Optional[ElastiCacheInstanceDetails]
    ESInstanceDetails: Optional[ESInstanceDetails]


class ReservationPurchaseRecommendationDetail(TypedDict, total=False):
    """Details about your recommended reservation purchase."""

    AccountId: Optional[GenericString]
    InstanceDetails: Optional[InstanceDetails]
    RecommendedNumberOfInstancesToPurchase: Optional[GenericString]
    RecommendedNormalizedUnitsToPurchase: Optional[GenericString]
    MinimumNumberOfInstancesUsedPerHour: Optional[GenericString]
    MinimumNormalizedUnitsUsedPerHour: Optional[GenericString]
    MaximumNumberOfInstancesUsedPerHour: Optional[GenericString]
    MaximumNormalizedUnitsUsedPerHour: Optional[GenericString]
    AverageNumberOfInstancesUsedPerHour: Optional[GenericString]
    AverageNormalizedUnitsUsedPerHour: Optional[GenericString]
    AverageUtilization: Optional[GenericString]
    EstimatedBreakEvenInMonths: Optional[GenericString]
    CurrencyCode: Optional[GenericString]
    EstimatedMonthlySavingsAmount: Optional[GenericString]
    EstimatedMonthlySavingsPercentage: Optional[GenericString]
    EstimatedMonthlyOnDemandCost: Optional[GenericString]
    EstimatedReservationCostForLookbackPeriod: Optional[GenericString]
    UpfrontCost: Optional[GenericString]
    RecurringStandardMonthlyCost: Optional[GenericString]


ReservationPurchaseRecommendationDetails = List[ReservationPurchaseRecommendationDetail]


class ReservationPurchaseRecommendation(TypedDict, total=False):
    """A specific reservation that Amazon Web Services recommends for purchase."""

    AccountScope: Optional[AccountScope]
    LookbackPeriodInDays: Optional[LookbackPeriodInDays]
    TermInYears: Optional[TermInYears]
    PaymentOption: Optional[PaymentOption]
    ServiceSpecification: Optional[ServiceSpecification]
    RecommendationDetails: Optional[ReservationPurchaseRecommendationDetails]
    RecommendationSummary: Optional[ReservationPurchaseRecommendationSummary]


ReservationPurchaseRecommendations = List[ReservationPurchaseRecommendation]


class ReservationPurchaseRecommendationMetadata(TypedDict, total=False):
    """Information about this specific recommendation, such as the timestamp
    for when Amazon Web Services made a specific recommendation.
    """

    RecommendationId: Optional[GenericString]
    GenerationTimestamp: Optional[GenericString]


class GetReservationPurchaseRecommendationResponse(TypedDict, total=False):
    Metadata: Optional[ReservationPurchaseRecommendationMetadata]
    Recommendations: Optional[ReservationPurchaseRecommendations]
    NextPageToken: Optional[NextPageToken]


class GetReservationUtilizationRequest(ServiceRequest):
    TimePeriod: DateInterval
    GroupBy: Optional[GroupDefinitions]
    Granularity: Optional[Granularity]
    Filter: Optional[Expression]
    SortBy: Optional[SortDefinition]
    NextPageToken: Optional[NextPageToken]
    MaxResults: Optional[MaxResults]


class ReservationAggregates(TypedDict, total=False):
    """The aggregated numbers for your reservation usage."""

    UtilizationPercentage: Optional[UtilizationPercentage]
    UtilizationPercentageInUnits: Optional[UtilizationPercentageInUnits]
    PurchasedHours: Optional[PurchasedHours]
    PurchasedUnits: Optional[PurchasedUnits]
    TotalActualHours: Optional[TotalActualHours]
    TotalActualUnits: Optional[TotalActualUnits]
    UnusedHours: Optional[UnusedHours]
    UnusedUnits: Optional[UnusedUnits]
    OnDemandCostOfRIHoursUsed: Optional[OnDemandCostOfRIHoursUsed]
    NetRISavings: Optional[NetRISavings]
    TotalPotentialRISavings: Optional[TotalPotentialRISavings]
    AmortizedUpfrontFee: Optional[AmortizedUpfrontFee]
    AmortizedRecurringFee: Optional[AmortizedRecurringFee]
    TotalAmortizedFee: Optional[TotalAmortizedFee]
    RICostForUnusedHours: Optional[RICostForUnusedHours]
    RealizedSavings: Optional[RealizedSavings]
    UnrealizedSavings: Optional[UnrealizedSavings]


class ReservationUtilizationGroup(TypedDict, total=False):
    """A group of reservations that share a set of attributes."""

    Key: Optional[ReservationGroupKey]
    Value: Optional[ReservationGroupValue]
    Attributes: Optional[Attributes]
    Utilization: Optional[ReservationAggregates]


ReservationUtilizationGroups = List[ReservationUtilizationGroup]


class UtilizationByTime(TypedDict, total=False):
    """The amount of utilization, in hours."""

    TimePeriod: Optional[DateInterval]
    Groups: Optional[ReservationUtilizationGroups]
    Total: Optional[ReservationAggregates]


UtilizationsByTime = List[UtilizationByTime]


class GetReservationUtilizationResponse(TypedDict, total=False):
    UtilizationsByTime: UtilizationsByTime
    Total: Optional[ReservationAggregates]
    NextPageToken: Optional[NextPageToken]


class RightsizingRecommendationConfiguration(TypedDict, total=False):
    """You can use ``RightsizingRecommendationConfiguration`` to customize
    recommendations across two attributes. You can choose to view
    recommendations for instances within the same instance families or
    across different instance families. You can also choose to view your
    estimated savings that are associated with recommendations with
    consideration of existing Savings Plans or RI benefits, or neither.
    """

    RecommendationTarget: RecommendationTarget
    BenefitsConsidered: GenericBoolean


class GetRightsizingRecommendationRequest(ServiceRequest):
    Filter: Optional[Expression]
    Configuration: Optional[RightsizingRecommendationConfiguration]
    Service: GenericString
    PageSize: Optional[NonNegativeInteger]
    NextPageToken: Optional[NextPageToken]


class TerminateRecommendationDetail(TypedDict, total=False):
    """Details on termination recommendation."""

    EstimatedMonthlySavings: Optional[GenericString]
    CurrencyCode: Optional[GenericString]


PlatformDifferences = List[PlatformDifference]


class TargetInstance(TypedDict, total=False):
    """Details on recommended instance."""

    EstimatedMonthlyCost: Optional[GenericString]
    EstimatedMonthlySavings: Optional[GenericString]
    CurrencyCode: Optional[GenericString]
    DefaultTargetInstance: Optional[GenericBoolean]
    ResourceDetails: Optional[ResourceDetails]
    ExpectedResourceUtilization: Optional[ResourceUtilization]
    PlatformDifferences: Optional[PlatformDifferences]


TargetInstancesList = List[TargetInstance]


class ModifyRecommendationDetail(TypedDict, total=False):
    """Details on the modification recommendation."""

    TargetInstances: Optional[TargetInstancesList]


class RightsizingRecommendation(TypedDict, total=False):
    """Recommendations to rightsize resources."""

    AccountId: Optional[GenericString]
    CurrentInstance: Optional[CurrentInstance]
    RightsizingType: Optional[RightsizingType]
    ModifyRecommendationDetail: Optional[ModifyRecommendationDetail]
    TerminateRecommendationDetail: Optional[TerminateRecommendationDetail]
    FindingReasonCodes: Optional[FindingReasonCodes]


RightsizingRecommendationList = List[RightsizingRecommendation]


class RightsizingRecommendationSummary(TypedDict, total=False):
    """The summary of rightsizing recommendations"""

    TotalRecommendationCount: Optional[GenericString]
    EstimatedTotalMonthlySavingsAmount: Optional[GenericString]
    SavingsCurrencyCode: Optional[GenericString]
    SavingsPercentage: Optional[GenericString]


class RightsizingRecommendationMetadata(TypedDict, total=False):
    """Metadata for this recommendation set."""

    RecommendationId: Optional[GenericString]
    GenerationTimestamp: Optional[GenericString]
    LookbackPeriodInDays: Optional[LookbackPeriodInDays]
    AdditionalMetadata: Optional[GenericString]


class GetRightsizingRecommendationResponse(TypedDict, total=False):
    Metadata: Optional[RightsizingRecommendationMetadata]
    Summary: Optional[RightsizingRecommendationSummary]
    RightsizingRecommendations: Optional[RightsizingRecommendationList]
    NextPageToken: Optional[NextPageToken]
    Configuration: Optional[RightsizingRecommendationConfiguration]


class GetSavingsPlansCoverageRequest(ServiceRequest):
    TimePeriod: DateInterval
    GroupBy: Optional[GroupDefinitions]
    Granularity: Optional[Granularity]
    Filter: Optional[Expression]
    Metrics: Optional[MetricNames]
    NextToken: Optional[NextPageToken]
    MaxResults: Optional[MaxResults]
    SortBy: Optional[SortDefinition]


class SavingsPlansCoverageData(TypedDict, total=False):
    """Specific coverage percentage, On-Demand costs, and spend covered by
    Savings Plans, and total Savings Plans costs for an account.
    """

    SpendCoveredBySavingsPlans: Optional[GenericString]
    OnDemandCost: Optional[GenericString]
    TotalCost: Optional[GenericString]
    CoveragePercentage: Optional[GenericString]


class SavingsPlansCoverage(TypedDict, total=False):
    """The amount of Savings Plans eligible usage that is covered by Savings
    Plans. All calculations consider the On-Demand equivalent of your
    Savings Plans usage.
    """

    Attributes: Optional[Attributes]
    Coverage: Optional[SavingsPlansCoverageData]
    TimePeriod: Optional[DateInterval]


SavingsPlansCoverages = List[SavingsPlansCoverage]


class GetSavingsPlansCoverageResponse(TypedDict, total=False):
    SavingsPlansCoverages: SavingsPlansCoverages
    NextToken: Optional[NextPageToken]


class GetSavingsPlansPurchaseRecommendationRequest(ServiceRequest):
    SavingsPlansType: SupportedSavingsPlansType
    TermInYears: TermInYears
    PaymentOption: PaymentOption
    AccountScope: Optional[AccountScope]
    NextPageToken: Optional[NextPageToken]
    PageSize: Optional[NonNegativeInteger]
    LookbackPeriodInDays: LookbackPeriodInDays
    Filter: Optional[Expression]


class SavingsPlansPurchaseRecommendationSummary(TypedDict, total=False):
    """Summary metrics for your Savings Plans Purchase Recommendations."""

    EstimatedROI: Optional[GenericString]
    CurrencyCode: Optional[GenericString]
    EstimatedTotalCost: Optional[GenericString]
    CurrentOnDemandSpend: Optional[GenericString]
    EstimatedSavingsAmount: Optional[GenericString]
    TotalRecommendationCount: Optional[GenericString]
    DailyCommitmentToPurchase: Optional[GenericString]
    HourlyCommitmentToPurchase: Optional[GenericString]
    EstimatedSavingsPercentage: Optional[GenericString]
    EstimatedMonthlySavingsAmount: Optional[GenericString]
    EstimatedOnDemandCostWithCurrentCommitment: Optional[GenericString]


class SavingsPlansDetails(TypedDict, total=False):
    """The attribute details on a specific Savings Plan."""

    Region: Optional[GenericString]
    InstanceFamily: Optional[GenericString]
    OfferingId: Optional[GenericString]


class SavingsPlansPurchaseRecommendationDetail(TypedDict, total=False):
    """Details for your recommended Savings Plans."""

    SavingsPlansDetails: Optional[SavingsPlansDetails]
    AccountId: Optional[GenericString]
    UpfrontCost: Optional[GenericString]
    EstimatedROI: Optional[GenericString]
    CurrencyCode: Optional[GenericString]
    EstimatedSPCost: Optional[GenericString]
    EstimatedOnDemandCost: Optional[GenericString]
    EstimatedOnDemandCostWithCurrentCommitment: Optional[GenericString]
    EstimatedSavingsAmount: Optional[GenericString]
    EstimatedSavingsPercentage: Optional[GenericString]
    HourlyCommitmentToPurchase: Optional[GenericString]
    EstimatedAverageUtilization: Optional[GenericString]
    EstimatedMonthlySavingsAmount: Optional[GenericString]
    CurrentMinimumHourlyOnDemandSpend: Optional[GenericString]
    CurrentMaximumHourlyOnDemandSpend: Optional[GenericString]
    CurrentAverageHourlyOnDemandSpend: Optional[GenericString]


SavingsPlansPurchaseRecommendationDetailList = List[SavingsPlansPurchaseRecommendationDetail]


class SavingsPlansPurchaseRecommendation(TypedDict, total=False):
    """Contains your request parameters, Savings Plan Recommendations Summary,
    and Details.
    """

    AccountScope: Optional[AccountScope]
    SavingsPlansType: Optional[SupportedSavingsPlansType]
    TermInYears: Optional[TermInYears]
    PaymentOption: Optional[PaymentOption]
    LookbackPeriodInDays: Optional[LookbackPeriodInDays]
    SavingsPlansPurchaseRecommendationDetails: Optional[
        SavingsPlansPurchaseRecommendationDetailList
    ]
    SavingsPlansPurchaseRecommendationSummary: Optional[SavingsPlansPurchaseRecommendationSummary]


class SavingsPlansPurchaseRecommendationMetadata(TypedDict, total=False):
    """Metadata about your Savings Plans Purchase Recommendations."""

    RecommendationId: Optional[GenericString]
    GenerationTimestamp: Optional[GenericString]
    AdditionalMetadata: Optional[GenericString]


class GetSavingsPlansPurchaseRecommendationResponse(TypedDict, total=False):
    Metadata: Optional[SavingsPlansPurchaseRecommendationMetadata]
    SavingsPlansPurchaseRecommendation: Optional[SavingsPlansPurchaseRecommendation]
    NextPageToken: Optional[NextPageToken]


SavingsPlansDataTypes = List[SavingsPlansDataType]


class GetSavingsPlansUtilizationDetailsRequest(ServiceRequest):
    TimePeriod: DateInterval
    Filter: Optional[Expression]
    DataType: Optional[SavingsPlansDataTypes]
    NextToken: Optional[NextPageToken]
    MaxResults: Optional[MaxResults]
    SortBy: Optional[SortDefinition]


class SavingsPlansAmortizedCommitment(TypedDict, total=False):
    """The amortized amount of Savings Plans purchased in a specific account
    during a specific time interval.
    """

    AmortizedRecurringCommitment: Optional[GenericString]
    AmortizedUpfrontCommitment: Optional[GenericString]
    TotalAmortizedCommitment: Optional[GenericString]


class SavingsPlansSavings(TypedDict, total=False):
    """The amount of savings that you're accumulating, against the public
    On-Demand rate of the usage accrued in an account.
    """

    NetSavings: Optional[GenericString]
    OnDemandCostEquivalent: Optional[GenericString]


class SavingsPlansUtilization(TypedDict, total=False):
    """The measurement of how well you're using your existing Savings Plans."""

    TotalCommitment: Optional[GenericString]
    UsedCommitment: Optional[GenericString]
    UnusedCommitment: Optional[GenericString]
    UtilizationPercentage: Optional[GenericString]


class SavingsPlansUtilizationAggregates(TypedDict, total=False):
    """The aggregated utilization metrics for your Savings Plans usage."""

    Utilization: SavingsPlansUtilization
    Savings: Optional[SavingsPlansSavings]
    AmortizedCommitment: Optional[SavingsPlansAmortizedCommitment]


class SavingsPlansUtilizationDetail(TypedDict, total=False):
    """A single daily or monthly Savings Plans utilization rate, and details
    for your account. A management account in an organization have access to
    member accounts. You can use ``GetDimensionValues`` to determine the
    possible dimension values.
    """

    SavingsPlanArn: Optional[SavingsPlanArn]
    Attributes: Optional[Attributes]
    Utilization: Optional[SavingsPlansUtilization]
    Savings: Optional[SavingsPlansSavings]
    AmortizedCommitment: Optional[SavingsPlansAmortizedCommitment]


SavingsPlansUtilizationDetails = List[SavingsPlansUtilizationDetail]


class GetSavingsPlansUtilizationDetailsResponse(TypedDict, total=False):
    SavingsPlansUtilizationDetails: SavingsPlansUtilizationDetails
    Total: Optional[SavingsPlansUtilizationAggregates]
    TimePeriod: DateInterval
    NextToken: Optional[NextPageToken]


class GetSavingsPlansUtilizationRequest(ServiceRequest):
    TimePeriod: DateInterval
    Granularity: Optional[Granularity]
    Filter: Optional[Expression]
    SortBy: Optional[SortDefinition]


class SavingsPlansUtilizationByTime(TypedDict, total=False):
    """The amount of Savings Plans utilization, in hours."""

    TimePeriod: DateInterval
    Utilization: SavingsPlansUtilization
    Savings: Optional[SavingsPlansSavings]
    AmortizedCommitment: Optional[SavingsPlansAmortizedCommitment]


SavingsPlansUtilizationsByTime = List[SavingsPlansUtilizationByTime]


class GetSavingsPlansUtilizationResponse(TypedDict, total=False):
    SavingsPlansUtilizationsByTime: Optional[SavingsPlansUtilizationsByTime]
    Total: SavingsPlansUtilizationAggregates


class GetTagsRequest(ServiceRequest):
    SearchString: Optional[SearchString]
    TimePeriod: DateInterval
    TagKey: Optional[TagKey]
    Filter: Optional[Expression]
    SortBy: Optional[SortDefinitions]
    MaxResults: Optional[MaxResults]
    NextPageToken: Optional[NextPageToken]


TagList = List[Entity]


class GetTagsResponse(TypedDict, total=False):
    NextPageToken: Optional[NextPageToken]
    Tags: TagList
    ReturnSize: PageSize
    TotalSize: PageSize


class GetUsageForecastRequest(ServiceRequest):
    TimePeriod: DateInterval
    Metric: Metric
    Granularity: Granularity
    Filter: Optional[Expression]
    PredictionIntervalLevel: Optional[PredictionIntervalLevel]


class GetUsageForecastResponse(TypedDict, total=False):
    Total: Optional[MetricValue]
    ForecastResultsByTime: Optional[ForecastResultsByTime]


class ListCostCategoryDefinitionsRequest(ServiceRequest):
    EffectiveOn: Optional[ZonedDateTime]
    NextToken: Optional[NextPageToken]
    MaxResults: Optional[CostCategoryMaxResults]


class ListCostCategoryDefinitionsResponse(TypedDict, total=False):
    CostCategoryReferences: Optional[CostCategoryReferencesList]
    NextToken: Optional[NextPageToken]


class ListTagsForResourceRequest(ServiceRequest):
    ResourceArn: Arn


class ListTagsForResourceResponse(TypedDict, total=False):
    ResourceTags: Optional[ResourceTagList]


class ProvideAnomalyFeedbackRequest(ServiceRequest):
    AnomalyId: GenericString
    Feedback: AnomalyFeedbackType


class ProvideAnomalyFeedbackResponse(TypedDict, total=False):
    AnomalyId: GenericString


ResourceTagKeyList = List[ResourceTagKey]


class TagResourceRequest(ServiceRequest):
    ResourceArn: Arn
    ResourceTags: ResourceTagList


class TagResourceResponse(TypedDict, total=False):
    pass


class UntagResourceRequest(ServiceRequest):
    ResourceArn: Arn
    ResourceTagKeys: ResourceTagKeyList


class UntagResourceResponse(TypedDict, total=False):
    pass


class UpdateAnomalyMonitorRequest(ServiceRequest):
    MonitorArn: GenericString
    MonitorName: Optional[GenericString]


class UpdateAnomalyMonitorResponse(TypedDict, total=False):
    MonitorArn: GenericString


class UpdateAnomalySubscriptionRequest(ServiceRequest):
    SubscriptionArn: GenericString
    Threshold: Optional[NullableNonNegativeDouble]
    Frequency: Optional[AnomalySubscriptionFrequency]
    MonitorArnList: Optional[MonitorArnList]
    Subscribers: Optional[Subscribers]
    SubscriptionName: Optional[GenericString]


class UpdateAnomalySubscriptionResponse(TypedDict, total=False):
    SubscriptionArn: GenericString


class UpdateCostCategoryDefinitionRequest(ServiceRequest):
    CostCategoryArn: Arn
    RuleVersion: CostCategoryRuleVersion
    Rules: CostCategoryRulesList
    DefaultValue: Optional[CostCategoryValue]
    SplitChargeRules: Optional[CostCategorySplitChargeRulesList]


class UpdateCostCategoryDefinitionResponse(TypedDict, total=False):
    CostCategoryArn: Optional[Arn]
    EffectiveStart: Optional[ZonedDateTime]


class CeApi:

    service = "ce"
    version = "2017-10-25"

    @handler("CreateAnomalyMonitor")
    def create_anomaly_monitor(
        self,
        context: RequestContext,
        anomaly_monitor: AnomalyMonitor,
        resource_tags: ResourceTagList = None,
    ) -> CreateAnomalyMonitorResponse:
        """Creates a new cost anomaly detection monitor with the requested type and
        monitor specification.

        :param anomaly_monitor: The cost anomaly detection monitor object that you want to create.
        :param resource_tags: An optional list of tags to associate with the specified
        ```AnomalyMonitor`` <https://docs.
        :returns: CreateAnomalyMonitorResponse
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateAnomalySubscription")
    def create_anomaly_subscription(
        self,
        context: RequestContext,
        anomaly_subscription: AnomalySubscription,
        resource_tags: ResourceTagList = None,
    ) -> CreateAnomalySubscriptionResponse:
        """Adds a subscription to a cost anomaly detection monitor. You can use
        each subscription to define subscribers with email or SNS notifications.
        Email subscribers can set a dollar threshold and a time frequency for
        receiving notifications.

        :param anomaly_subscription: The cost anomaly subscription object that you want to create.
        :param resource_tags: An optional list of tags to associate with the specified
        ```AnomalySubscription`` <https://docs.
        :returns: CreateAnomalySubscriptionResponse
        :raises UnknownMonitorException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("CreateCostCategoryDefinition")
    def create_cost_category_definition(
        self,
        context: RequestContext,
        name: CostCategoryName,
        rule_version: CostCategoryRuleVersion,
        rules: CostCategoryRulesList,
        default_value: CostCategoryValue = None,
        split_charge_rules: CostCategorySplitChargeRulesList = None,
        resource_tags: ResourceTagList = None,
    ) -> CreateCostCategoryDefinitionResponse:
        """Creates a new Cost Category with the requested name and rules.

        :param name: The unique name of the Cost Category.
        :param rule_version: The rule schema version in this particular Cost Category.
        :param rules: The Cost Category rules used to categorize costs.
        :param default_value: The default value for the cost category.
        :param split_charge_rules: The split charge rules used to allocate your charges between your Cost
        Category values.
        :param resource_tags: An optional list of tags to associate with the specified
        ```CostCategory`` <https://docs.
        :returns: CreateCostCategoryDefinitionResponse
        :raises ServiceQuotaExceededException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("DeleteAnomalyMonitor")
    def delete_anomaly_monitor(
        self, context: RequestContext, monitor_arn: GenericString
    ) -> DeleteAnomalyMonitorResponse:
        """Deletes a cost anomaly monitor.

        :param monitor_arn: The unique identifier of the cost anomaly monitor that you want to
        delete.
        :returns: DeleteAnomalyMonitorResponse
        :raises LimitExceededException:
        :raises UnknownMonitorException:
        """
        raise NotImplementedError

    @handler("DeleteAnomalySubscription")
    def delete_anomaly_subscription(
        self, context: RequestContext, subscription_arn: GenericString
    ) -> DeleteAnomalySubscriptionResponse:
        """Deletes a cost anomaly subscription.

        :param subscription_arn: The unique identifier of the cost anomaly subscription that you want to
        delete.
        :returns: DeleteAnomalySubscriptionResponse
        :raises LimitExceededException:
        :raises UnknownSubscriptionException:
        """
        raise NotImplementedError

    @handler("DeleteCostCategoryDefinition")
    def delete_cost_category_definition(
        self, context: RequestContext, cost_category_arn: Arn
    ) -> DeleteCostCategoryDefinitionResponse:
        """Deletes a Cost Category. Expenses from this month going forward will no
        longer be categorized with this Cost Category.

        :param cost_category_arn: The unique identifier for your Cost Category.
        :returns: DeleteCostCategoryDefinitionResponse
        :raises ResourceNotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("DescribeCostCategoryDefinition")
    def describe_cost_category_definition(
        self, context: RequestContext, cost_category_arn: Arn, effective_on: ZonedDateTime = None
    ) -> DescribeCostCategoryDefinitionResponse:
        """Returns the name, ARN, rules, definition, and effective dates of a Cost
        Category that's defined in the account.

        You have the option to use ``EffectiveOn`` to return a Cost Category
        that is active on a specific date. If there is no ``EffectiveOn``
        specified, you’ll see a Cost Category that is effective on the current
        date. If Cost Category is still effective, ``EffectiveEnd`` is omitted
        in the response.

        :param cost_category_arn: The unique identifier for your Cost Category.
        :param effective_on: The date when the Cost Category was effective.
        :returns: DescribeCostCategoryDefinitionResponse
        :raises ResourceNotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("GetAnomalies")
    def get_anomalies(
        self,
        context: RequestContext,
        date_interval: AnomalyDateInterval,
        monitor_arn: GenericString = None,
        feedback: AnomalyFeedbackType = None,
        total_impact: TotalImpactFilter = None,
        next_page_token: NextPageToken = None,
        max_results: PageSize = None,
    ) -> GetAnomaliesResponse:
        """Retrieves all of the cost anomalies detected on your account during the
        time period that's specified by the ``DateInterval`` object.

        :param date_interval: Assigns the start and end dates for retrieving cost anomalies.
        :param monitor_arn: Retrieves all of the cost anomalies detected for a specific cost anomaly
        monitor Amazon Resource Name (ARN).
        :param feedback: Filters anomaly results by the feedback field on the anomaly object.
        :param total_impact: Filters anomaly results by the total impact field on the anomaly object.
        :param next_page_token: The token to retrieve the next set of results.
        :param max_results: The number of entries a paginated response contains.
        :returns: GetAnomaliesResponse
        :raises LimitExceededException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("GetAnomalyMonitors")
    def get_anomaly_monitors(
        self,
        context: RequestContext,
        monitor_arn_list: Values = None,
        next_page_token: NextPageToken = None,
        max_results: PageSize = None,
    ) -> GetAnomalyMonitorsResponse:
        """Retrieves the cost anomaly monitor definitions for your account. You can
        filter using a list of cost anomaly monitor Amazon Resource Names
        (ARNs).

        :param monitor_arn_list: A list of cost anomaly monitor ARNs.
        :param next_page_token: The token to retrieve the next set of results.
        :param max_results: The number of entries that a paginated response contains.
        :returns: GetAnomalyMonitorsResponse
        :raises LimitExceededException:
        :raises UnknownMonitorException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("GetAnomalySubscriptions")
    def get_anomaly_subscriptions(
        self,
        context: RequestContext,
        subscription_arn_list: Values = None,
        monitor_arn: GenericString = None,
        next_page_token: NextPageToken = None,
        max_results: PageSize = None,
    ) -> GetAnomalySubscriptionsResponse:
        """Retrieves the cost anomaly subscription objects for your account. You
        can filter using a list of cost anomaly monitor Amazon Resource Names
        (ARNs).

        :param subscription_arn_list: A list of cost anomaly subscription ARNs.
        :param monitor_arn: Cost anomaly monitor ARNs.
        :param next_page_token: The token to retrieve the next set of results.
        :param max_results: The number of entries a paginated response contains.
        :returns: GetAnomalySubscriptionsResponse
        :raises LimitExceededException:
        :raises UnknownSubscriptionException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("GetCostAndUsage")
    def get_cost_and_usage(
        self,
        context: RequestContext,
        time_period: DateInterval,
        granularity: Granularity,
        metrics: MetricNames,
        filter: Expression = None,
        group_by: GroupDefinitions = None,
        next_page_token: NextPageToken = None,
    ) -> GetCostAndUsageResponse:
        """Retrieves cost and usage metrics for your account. You can specify which
        cost and usage-related metric that you want the request to return. For
        example, you can specify ``BlendedCosts`` or ``UsageQuantity``. You can
        also filter and group your data by various dimensions, such as
        ``SERVICE`` or ``AZ``, in a specific time range. For a complete list of
        valid dimensions, see the
        `GetDimensionValues <https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_GetDimensionValues.html>`__
        operation. Management account in an organization in Organizations have
        access to all member accounts.

        For information about filter limitations, see `Quotas and
        restrictions <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-limits.html>`__
        in the *Billing and Cost Management User Guide*.

        :param time_period: Sets the start date and end date for retrieving Amazon Web Services
        costs.
        :param granularity: Sets the Amazon Web Services cost granularity to ``MONTHLY`` or
        ``DAILY``, or ``HOURLY``.
        :param metrics: Which metrics are returned in the query.
        :param filter: Filters Amazon Web Services costs by different dimensions.
        :param group_by: You can group Amazon Web Services costs using up to two different
        groups, either dimensions, tag keys, cost categories, or any two group
        by types.
        :param next_page_token: The token to retrieve the next set of results.
        :returns: GetCostAndUsageResponse
        :raises LimitExceededException:
        :raises BillExpirationException:
        :raises DataUnavailableException:
        :raises InvalidNextTokenException:
        :raises RequestChangedException:
        """
        raise NotImplementedError

    @handler("GetCostAndUsageWithResources")
    def get_cost_and_usage_with_resources(
        self,
        context: RequestContext,
        time_period: DateInterval,
        granularity: Granularity,
        filter: Expression,
        metrics: MetricNames = None,
        group_by: GroupDefinitions = None,
        next_page_token: NextPageToken = None,
    ) -> GetCostAndUsageWithResourcesResponse:
        """Retrieves cost and usage metrics with resources for your account. You
        can specify which cost and usage-related metric, such as
        ``BlendedCosts`` or ``UsageQuantity``, that you want the request to
        return. You can also filter and group your data by various dimensions,
        such as ``SERVICE`` or ``AZ``, in a specific time range. For a complete
        list of valid dimensions, see the
        `GetDimensionValues <https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_GetDimensionValues.html>`__
        operation. Management account in an organization in Organizations have
        access to all member accounts. This API is currently available for the
        Amazon Elastic Compute Cloud – Compute service only.

        This is an opt-in only feature. You can enable this feature from the
        Cost Explorer Settings page. For information on how to access the
        Settings page, see `Controlling Access for Cost
        Explorer <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ce-access.html>`__
        in the *Billing and Cost Management User Guide*.

        :param time_period: Sets the start and end dates for retrieving Amazon Web Services costs.
        :param granularity: Sets the Amazon Web Services cost granularity to ``MONTHLY``, ``DAILY``,
        or ``HOURLY``.
        :param filter: Filters Amazon Web Services costs by different dimensions.
        :param metrics: Which metrics are returned in the query.
        :param group_by: You can group Amazon Web Services costs using up to two different
        groups: ``DIMENSION``, ``TAG``, ``COST_CATEGORY``.
        :param next_page_token: The token to retrieve the next set of results.
        :returns: GetCostAndUsageWithResourcesResponse
        :raises DataUnavailableException:
        :raises LimitExceededException:
        :raises BillExpirationException:
        :raises InvalidNextTokenException:
        :raises RequestChangedException:
        """
        raise NotImplementedError

    @handler("GetCostCategories")
    def get_cost_categories(
        self,
        context: RequestContext,
        time_period: DateInterval,
        search_string: SearchString = None,
        cost_category_name: CostCategoryName = None,
        filter: Expression = None,
        sort_by: SortDefinitions = None,
        max_results: MaxResults = None,
        next_page_token: NextPageToken = None,
    ) -> GetCostCategoriesResponse:
        """Retrieves an array of Cost Category names and values incurred cost.

        If some Cost Category names and values are not associated with any cost,
        they will not be returned by this API.

        :param time_period: The time period of the request.
        :param search_string: The value that you want to search the filter values for.
        :param cost_category_name: The unique name of the Cost Category.
        :param filter: Use ``Expression`` to filter by cost or by usage.
        :param sort_by: The value by which you want to sort the data.
        :param max_results: This field is only used when ``SortBy`` is provided in the request.
        :param next_page_token: If the number of objects that are still available for retrieval exceeds
        the limit, Amazon Web Services returns a NextPageToken value in the
        response.
        :returns: GetCostCategoriesResponse
        :raises LimitExceededException:
        :raises BillExpirationException:
        :raises DataUnavailableException:
        :raises InvalidNextTokenException:
        :raises RequestChangedException:
        """
        raise NotImplementedError

    @handler("GetCostForecast")
    def get_cost_forecast(
        self,
        context: RequestContext,
        time_period: DateInterval,
        metric: Metric,
        granularity: Granularity,
        filter: Expression = None,
        prediction_interval_level: PredictionIntervalLevel = None,
    ) -> GetCostForecastResponse:
        """Retrieves a forecast for how much Amazon Web Services predicts that you
        will spend over the forecast time period that you select, based on your
        past costs.

        :param time_period: The period of time that you want the forecast to cover.
        :param metric: Which metric Cost Explorer uses to create your forecast.
        :param granularity: How granular you want the forecast to be.
        :param filter: The filters that you want to use to filter your forecast.
        :param prediction_interval_level: Cost Explorer always returns the mean forecast as a single point.
        :returns: GetCostForecastResponse
        :raises LimitExceededException:
        :raises DataUnavailableException:
        """
        raise NotImplementedError

    @handler("GetDimensionValues", expand=False)
    def get_dimension_values(
        self, context: RequestContext, request: GetDimensionValuesRequest
    ) -> GetDimensionValuesResponse:
        """Retrieves all available filter values for a specified filter over a
        period of time. You can search the dimension values for an arbitrary
        string.

        :param time_period: The start date and end date for retrieving the dimension values.
        :param dimension: The name of the dimension.
        :param search_string: The value that you want to search the filter values for.
        :param context: The context for the call to ``GetDimensionValues``.
        :param filter: Use ``Expression`` to filter by cost or by usage.
        :param sort_by: The value by which you want to sort the data.
        :param max_results: This field is only used when SortBy is provided in the request.
        :param next_page_token: The token to retrieve the next set of results.
        :returns: GetDimensionValuesResponse
        :raises LimitExceededException:
        :raises BillExpirationException:
        :raises DataUnavailableException:
        :raises InvalidNextTokenException:
        :raises RequestChangedException:
        """
        raise NotImplementedError

    @handler("GetReservationCoverage")
    def get_reservation_coverage(
        self,
        context: RequestContext,
        time_period: DateInterval,
        group_by: GroupDefinitions = None,
        granularity: Granularity = None,
        filter: Expression = None,
        metrics: MetricNames = None,
        next_page_token: NextPageToken = None,
        sort_by: SortDefinition = None,
        max_results: MaxResults = None,
    ) -> GetReservationCoverageResponse:
        """Retrieves the reservation coverage for your account. This enables you to
        see how much of your Amazon Elastic Compute Cloud, Amazon ElastiCache,
        Amazon Relational Database Service, or Amazon Redshift usage is covered
        by a reservation. An organization's management account can see the
        coverage of the associated member accounts. This supports dimensions,
        Cost Categories, and nested expressions. For any time period, you can
        filter data about reservation usage by the following dimensions:

        -  AZ

        -  CACHE_ENGINE

        -  DATABASE_ENGINE

        -  DEPLOYMENT_OPTION

        -  INSTANCE_TYPE

        -  LINKED_ACCOUNT

        -  OPERATING_SYSTEM

        -  PLATFORM

        -  REGION

        -  SERVICE

        -  TAG

        -  TENANCY

        To determine valid values for a dimension, use the
        ``GetDimensionValues`` operation.

        :param time_period: The start and end dates of the period that you want to retrieve data
        about reservation coverage for.
        :param group_by: You can group the data by the following attributes:

        -  AZ

        -  CACHE_ENGINE

        -  DATABASE_ENGINE

        -  DEPLOYMENT_OPTION

        -  INSTANCE_TYPE

        -  INVOICING_ENTITY

        -  LINKED_ACCOUNT

        -  OPERATING_SYSTEM

        -  PLATFORM

        -  REGION

        -  TENANCY.
        :param granularity: The granularity of the Amazon Web Services cost data for the
        reservation.
        :param filter: Filters utilization data by dimensions.
        :param metrics: The measurement that you want your reservation coverage reported in.
        :param next_page_token: The token to retrieve the next set of results.
        :param sort_by: The value by which you want to sort the data.
        :param max_results: The maximum number of objects that you returned for this request.
        :returns: GetReservationCoverageResponse
        :raises LimitExceededException:
        :raises DataUnavailableException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("GetReservationPurchaseRecommendation")
    def get_reservation_purchase_recommendation(
        self,
        context: RequestContext,
        service: GenericString,
        account_id: GenericString = None,
        filter: Expression = None,
        account_scope: AccountScope = None,
        lookback_period_in_days: LookbackPeriodInDays = None,
        term_in_years: TermInYears = None,
        payment_option: PaymentOption = None,
        service_specification: ServiceSpecification = None,
        page_size: NonNegativeInteger = None,
        next_page_token: NextPageToken = None,
    ) -> GetReservationPurchaseRecommendationResponse:
        """Gets recommendations for which reservations to purchase. These
        recommendations could help you reduce your costs. Reservations provide a
        discounted hourly rate (up to 75%) compared to On-Demand pricing.

        Amazon Web Services generates your recommendations by identifying your
        On-Demand usage during a specific time period and collecting your usage
        into categories that are eligible for a reservation. After Amazon Web
        Services has these categories, it simulates every combination of
        reservations in each category of usage to identify the best number of
        each type of RI to purchase to maximize your estimated savings.

        For example, Amazon Web Services automatically aggregates your Amazon
        EC2 Linux, shared tenancy, and c4 family usage in the US West (Oregon)
        Region and recommends that you buy size-flexible regional reservations
        to apply to the c4 family usage. Amazon Web Services recommends the
        smallest size instance in an instance family. This makes it easier to
        purchase a size-flexible RI. Amazon Web Services also shows the equal
        number of normalized units so that you can purchase any instance size
        that you want. For this example, your RI recommendation would be for
        ``c4.large`` because that is the smallest size instance in the c4
        instance family.

        :param service: The specific service that you want recommendations for.
        :param account_id: The account ID that is associated with the recommendation.
        :param filter: Use ``Expression`` to filter by cost or by usage.
        :param account_scope: The account scope that you want your recommendations for.
        :param lookback_period_in_days: The number of previous days that you want Amazon Web Services to
        consider when it calculates your recommendations.
        :param term_in_years: The reservation term that you want recommendations for.
        :param payment_option: The reservation purchase option that you want recommendations for.
        :param service_specification: The hardware specifications for the service instances that you want
        recommendations for, such as standard or convertible Amazon EC2
        instances.
        :param page_size: The number of recommendations that you want returned in a single
        response object.
        :param next_page_token: The pagination token that indicates the next set of results that you
        want to retrieve.
        :returns: GetReservationPurchaseRecommendationResponse
        :raises LimitExceededException:
        :raises DataUnavailableException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("GetReservationUtilization")
    def get_reservation_utilization(
        self,
        context: RequestContext,
        time_period: DateInterval,
        group_by: GroupDefinitions = None,
        granularity: Granularity = None,
        filter: Expression = None,
        sort_by: SortDefinition = None,
        next_page_token: NextPageToken = None,
        max_results: MaxResults = None,
    ) -> GetReservationUtilizationResponse:
        """Retrieves the reservation utilization for your account. Management
        account in an organization have access to member accounts. You can
        filter data by dimensions in a time period. You can use
        ``GetDimensionValues`` to determine the possible dimension values.
        Currently, you can group only by ``SUBSCRIPTION_ID``.

        :param time_period: Sets the start and end dates for retrieving RI utilization.
        :param group_by: Groups only by ``SUBSCRIPTION_ID``.
        :param granularity: If ``GroupBy`` is set, ``Granularity`` can't be set.
        :param filter: Filters utilization data by dimensions.
        :param sort_by: The value by which you want to sort the data.
        :param next_page_token: The token to retrieve the next set of results.
        :param max_results: The maximum number of objects that you returned for this request.
        :returns: GetReservationUtilizationResponse
        :raises LimitExceededException:
        :raises DataUnavailableException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("GetRightsizingRecommendation")
    def get_rightsizing_recommendation(
        self,
        context: RequestContext,
        service: GenericString,
        filter: Expression = None,
        configuration: RightsizingRecommendationConfiguration = None,
        page_size: NonNegativeInteger = None,
        next_page_token: NextPageToken = None,
    ) -> GetRightsizingRecommendationResponse:
        """Creates recommendations that help you save cost by identifying idle and
        underutilized Amazon EC2 instances.

        Recommendations are generated to either downsize or terminate instances,
        along with providing savings detail and metrics. For details on
        calculation and function, see `Optimizing Your Cost with Rightsizing
        Recommendations <https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ce-rightsizing.html>`__
        in the *Billing and Cost Management User Guide*.

        :param service: The specific service that you want recommendations for.
        :param filter: Use ``Expression`` to filter by cost or by usage.
        :param configuration: Enables you to customize recommendations across two attributes.
        :param page_size: The number of recommendations that you want returned in a single
        response object.
        :param next_page_token: The pagination token that indicates the next set of results that you
        want to retrieve.
        :returns: GetRightsizingRecommendationResponse
        :raises LimitExceededException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("GetSavingsPlansCoverage")
    def get_savings_plans_coverage(
        self,
        context: RequestContext,
        time_period: DateInterval,
        group_by: GroupDefinitions = None,
        granularity: Granularity = None,
        filter: Expression = None,
        metrics: MetricNames = None,
        next_token: NextPageToken = None,
        max_results: MaxResults = None,
        sort_by: SortDefinition = None,
    ) -> GetSavingsPlansCoverageResponse:
        """Retrieves the Savings Plans covered for your account. This enables you
        to see how much of your cost is covered by a Savings Plan. An
        organization’s management account can see the coverage of the associated
        member accounts. This supports dimensions, Cost Categories, and nested
        expressions. For any time period, you can filter data for Savings Plans
        usage with the following dimensions:

        -  ``LINKED_ACCOUNT``

        -  ``REGION``

        -  ``SERVICE``

        -  ``INSTANCE_FAMILY``

        To determine valid values for a dimension, use the
        ``GetDimensionValues`` operation.

        :param time_period: The time period that you want the usage and costs for.
        :param group_by: You can group the data using the attributes ``INSTANCE_FAMILY``,
        ``REGION``, or ``SERVICE``.
        :param granularity: The granularity of the Amazon Web Services cost data for your Savings
        Plans.
        :param filter: Filters Savings Plans coverage data by dimensions.
        :param metrics: The measurement that you want your Savings Plans coverage reported in.
        :param next_token: The token to retrieve the next set of results.
        :param max_results: The number of items to be returned in a response.
        :param sort_by: The value by which you want to sort the data.
        :returns: GetSavingsPlansCoverageResponse
        :raises LimitExceededException:
        :raises DataUnavailableException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("GetSavingsPlansPurchaseRecommendation")
    def get_savings_plans_purchase_recommendation(
        self,
        context: RequestContext,
        savings_plans_type: SupportedSavingsPlansType,
        term_in_years: TermInYears,
        payment_option: PaymentOption,
        lookback_period_in_days: LookbackPeriodInDays,
        account_scope: AccountScope = None,
        next_page_token: NextPageToken = None,
        page_size: NonNegativeInteger = None,
        filter: Expression = None,
    ) -> GetSavingsPlansPurchaseRecommendationResponse:
        """Retrieves your request parameters, Savings Plan Recommendations Summary
        and Details.

        :param savings_plans_type: The Savings Plans recommendation type requested.
        :param term_in_years: The savings plan recommendation term used to generate these
        recommendations.
        :param payment_option: The payment option used to generate these recommendations.
        :param lookback_period_in_days: The lookback period used to generate the recommendation.
        :param account_scope: The account scope that you want your recommendations for.
        :param next_page_token: The token to retrieve the next set of results.
        :param page_size: The number of recommendations that you want returned in a single
        response object.
        :param filter: You can filter your recommendations by Account ID with the
        ``LINKED_ACCOUNT`` dimension.
        :returns: GetSavingsPlansPurchaseRecommendationResponse
        :raises LimitExceededException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("GetSavingsPlansUtilization")
    def get_savings_plans_utilization(
        self,
        context: RequestContext,
        time_period: DateInterval,
        granularity: Granularity = None,
        filter: Expression = None,
        sort_by: SortDefinition = None,
    ) -> GetSavingsPlansUtilizationResponse:
        """Retrieves the Savings Plans utilization for your account across date
        ranges with daily or monthly granularity. Management account in an
        organization have access to member accounts. You can use
        ``GetDimensionValues`` in ``SAVINGS_PLANS`` to determine the possible
        dimension values.

        You cannot group by any dimension values for
        ``GetSavingsPlansUtilization``.

        :param time_period: The time period that you want the usage and costs for.
        :param granularity: The granularity of the Amazon Web Services utillization data for your
        Savings Plans.
        :param filter: Filters Savings Plans utilization coverage data for active Savings Plans
        dimensions.
        :param sort_by: The value by which you want to sort the data.
        :returns: GetSavingsPlansUtilizationResponse
        :raises LimitExceededException:
        :raises DataUnavailableException:
        """
        raise NotImplementedError

    @handler("GetSavingsPlansUtilizationDetails")
    def get_savings_plans_utilization_details(
        self,
        context: RequestContext,
        time_period: DateInterval,
        filter: Expression = None,
        data_type: SavingsPlansDataTypes = None,
        next_token: NextPageToken = None,
        max_results: MaxResults = None,
        sort_by: SortDefinition = None,
    ) -> GetSavingsPlansUtilizationDetailsResponse:
        """Retrieves attribute data along with aggregate utilization and savings
        data for a given time period. This doesn't support granular or grouped
        data (daily/monthly) in response. You can't retrieve data by dates in a
        single response similar to ``GetSavingsPlanUtilization``, but you have
        the option to make multiple calls to
        ``GetSavingsPlanUtilizationDetails`` by providing individual dates. You
        can use ``GetDimensionValues`` in ``SAVINGS_PLANS`` to determine the
        possible dimension values.

        ``GetSavingsPlanUtilizationDetails`` internally groups data by
        ``SavingsPlansArn``.

        :param time_period: The time period that you want the usage and costs for.
        :param filter: Filters Savings Plans utilization coverage data for active Savings Plans
        dimensions.
        :param data_type: The data type.
        :param next_token: The token to retrieve the next set of results.
        :param max_results: The number of items to be returned in a response.
        :param sort_by: The value by which you want to sort the data.
        :returns: GetSavingsPlansUtilizationDetailsResponse
        :raises LimitExceededException:
        :raises DataUnavailableException:
        :raises InvalidNextTokenException:
        """
        raise NotImplementedError

    @handler("GetTags")
    def get_tags(
        self,
        context: RequestContext,
        time_period: DateInterval,
        search_string: SearchString = None,
        tag_key: TagKey = None,
        filter: Expression = None,
        sort_by: SortDefinitions = None,
        max_results: MaxResults = None,
        next_page_token: NextPageToken = None,
    ) -> GetTagsResponse:
        """Queries for available tag keys and tag values for a specified period.
        You can search the tag values for an arbitrary string.

        :param time_period: The start and end dates for retrieving the dimension values.
        :param search_string: The value that you want to search for.
        :param tag_key: The key of the tag that you want to return values for.
        :param filter: Use ``Expression`` to filter by cost or by usage.
        :param sort_by: The value by which you want to sort the data.
        :param max_results: This field is only used when SortBy is provided in the request.
        :param next_page_token: The token to retrieve the next set of results.
        :returns: GetTagsResponse
        :raises LimitExceededException:
        :raises BillExpirationException:
        :raises DataUnavailableException:
        :raises InvalidNextTokenException:
        :raises RequestChangedException:
        """
        raise NotImplementedError

    @handler("GetUsageForecast")
    def get_usage_forecast(
        self,
        context: RequestContext,
        time_period: DateInterval,
        metric: Metric,
        granularity: Granularity,
        filter: Expression = None,
        prediction_interval_level: PredictionIntervalLevel = None,
    ) -> GetUsageForecastResponse:
        """Retrieves a forecast for how much Amazon Web Services predicts that you
        will use over the forecast time period that you select, based on your
        past usage.

        :param time_period: The start and end dates of the period that you want to retrieve usage
        forecast for.
        :param metric: Which metric Cost Explorer uses to create your forecast.
        :param granularity: How granular you want the forecast to be.
        :param filter: The filters that you want to use to filter your forecast.
        :param prediction_interval_level: Cost Explorer always returns the mean forecast as a single point.
        :returns: GetUsageForecastResponse
        :raises LimitExceededException:
        :raises DataUnavailableException:
        :raises UnresolvableUsageUnitException:
        """
        raise NotImplementedError

    @handler("ListCostCategoryDefinitions")
    def list_cost_category_definitions(
        self,
        context: RequestContext,
        effective_on: ZonedDateTime = None,
        next_token: NextPageToken = None,
        max_results: CostCategoryMaxResults = None,
    ) -> ListCostCategoryDefinitionsResponse:
        """Returns the name, ARN, ``NumberOfRules`` and effective dates of all Cost
        Categories defined in the account. You have the option to use
        ``EffectiveOn`` to return a list of Cost Categories that were active on
        a specific date. If there is no ``EffectiveOn`` specified, you’ll see
        Cost Categories that are effective on the current date. If Cost Category
        is still effective, ``EffectiveEnd`` is omitted in the response.
        ``ListCostCategoryDefinitions`` supports pagination. The request can
        have a ``MaxResults`` range up to 100.

        :param effective_on: The date when the Cost Category was effective.
        :param next_token: The token to retrieve the next set of results.
        :param max_results: The number of entries a paginated response contains.
        :returns: ListCostCategoryDefinitionsResponse
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: Arn
    ) -> ListTagsForResourceResponse:
        """Returns a list of resource tags associated with the resource specified
        by the Amazon Resource Name (ARN).

        :param resource_arn: The Amazon Resource Name (ARN) of the resource.
        :returns: ListTagsForResourceResponse
        :raises ResourceNotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("ProvideAnomalyFeedback")
    def provide_anomaly_feedback(
        self, context: RequestContext, anomaly_id: GenericString, feedback: AnomalyFeedbackType
    ) -> ProvideAnomalyFeedbackResponse:
        """Modifies the feedback property of a given cost anomaly.

        :param anomaly_id: A cost anomaly ID.
        :param feedback: Describes whether the cost anomaly was a planned activity or you
        considered it an anomaly.
        :returns: ProvideAnomalyFeedbackResponse
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: Arn, resource_tags: ResourceTagList
    ) -> TagResourceResponse:
        """An API operation for adding one or more tags (key-value pairs) to a
        resource.

        You can use the ``TagResource`` operation with a resource that already
        has tags. If you specify a new tag key for the resource, this tag is
        appended to the list of tags associated with the resource. If you
        specify a tag key that is already associated with the resource, the new
        tag value you specify replaces the previous value for that tag.

        Although the maximum number of array members is 200, user-tag maximum is
        50. The remaining are reserved for Amazon Web Services use.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource.
        :param resource_tags: A list of tag key-value pairs to be added to the resource.
        :returns: TagResourceResponse
        :raises ResourceNotFoundException:
        :raises TooManyTagsException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: Arn, resource_tag_keys: ResourceTagKeyList
    ) -> UntagResourceResponse:
        """Removes one or more tags from a resource. Specify only tag key(s) in
        your request. Do not specify the value.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource.
        :param resource_tag_keys: A list of tag keys associated with tags that need to be removed from the
        resource.
        :returns: UntagResourceResponse
        :raises ResourceNotFoundException:
        :raises LimitExceededException:
        """
        raise NotImplementedError

    @handler("UpdateAnomalyMonitor")
    def update_anomaly_monitor(
        self,
        context: RequestContext,
        monitor_arn: GenericString,
        monitor_name: GenericString = None,
    ) -> UpdateAnomalyMonitorResponse:
        """Updates an existing cost anomaly monitor. The changes made are applied
        going forward, and doesn't change anomalies detected in the past.

        :param monitor_arn: Cost anomaly monitor Amazon Resource Names (ARNs).
        :param monitor_name: The new name for the cost anomaly monitor.
        :returns: UpdateAnomalyMonitorResponse
        :raises LimitExceededException:
        :raises UnknownMonitorException:
        """
        raise NotImplementedError

    @handler("UpdateAnomalySubscription")
    def update_anomaly_subscription(
        self,
        context: RequestContext,
        subscription_arn: GenericString,
        threshold: NullableNonNegativeDouble = None,
        frequency: AnomalySubscriptionFrequency = None,
        monitor_arn_list: MonitorArnList = None,
        subscribers: Subscribers = None,
        subscription_name: GenericString = None,
    ) -> UpdateAnomalySubscriptionResponse:
        """Updates an existing cost anomaly monitor subscription.

        :param subscription_arn: A cost anomaly subscription Amazon Resource Name (ARN).
        :param threshold: The update to the threshold value for receiving notifications.
        :param frequency: The update to the frequency value that subscribers receive
        notifications.
        :param monitor_arn_list: A list of cost anomaly monitor ARNs.
        :param subscribers: The update to the subscriber list.
        :param subscription_name: The new name of the subscription.
        :returns: UpdateAnomalySubscriptionResponse
        :raises LimitExceededException:
        :raises UnknownMonitorException:
        :raises UnknownSubscriptionException:
        """
        raise NotImplementedError

    @handler("UpdateCostCategoryDefinition")
    def update_cost_category_definition(
        self,
        context: RequestContext,
        cost_category_arn: Arn,
        rule_version: CostCategoryRuleVersion,
        rules: CostCategoryRulesList,
        default_value: CostCategoryValue = None,
        split_charge_rules: CostCategorySplitChargeRulesList = None,
    ) -> UpdateCostCategoryDefinitionResponse:
        """Updates an existing Cost Category. Changes made to the Cost Category
        rules will be used to categorize the current month’s expenses and future
        expenses. This won’t change categorization for the previous months.

        :param cost_category_arn: The unique identifier for your Cost Category.
        :param rule_version: The rule schema version in this particular Cost Category.
        :param rules: The ``Expression`` object used to categorize costs.
        :param default_value: The default value for the cost category.
        :param split_charge_rules: The split charge rules used to allocate your charges between your Cost
        Category values.
        :returns: UpdateCostCategoryDefinitionResponse
        :raises ResourceNotFoundException:
        :raises ServiceQuotaExceededException:
        :raises LimitExceededException:
        """
        raise NotImplementedError
