import sys
from datetime import datetime
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

Cooldown = int
DisableScaleIn = bool
ErrorMessage = str
MaxResults = int
MetricDimensionName = str
MetricDimensionValue = str
MetricName = str
MetricNamespace = str
MetricScale = float
MetricUnit = str
MinAdjustmentMagnitude = int
PolicyName = str
ResourceCapacity = int
ResourceId = str
ResourceIdMaxLen1600 = str
ResourceLabel = str
ScalingAdjustment = int
ScalingSuspended = bool
ScheduledActionName = str
XmlString = str


class AdjustmentType(str):
    ChangeInCapacity = "ChangeInCapacity"
    PercentChangeInCapacity = "PercentChangeInCapacity"
    ExactCapacity = "ExactCapacity"


class MetricAggregationType(str):
    Average = "Average"
    Minimum = "Minimum"
    Maximum = "Maximum"


class MetricStatistic(str):
    Average = "Average"
    Minimum = "Minimum"
    Maximum = "Maximum"
    SampleCount = "SampleCount"
    Sum = "Sum"


class MetricType(str):
    DynamoDBReadCapacityUtilization = "DynamoDBReadCapacityUtilization"
    DynamoDBWriteCapacityUtilization = "DynamoDBWriteCapacityUtilization"
    ALBRequestCountPerTarget = "ALBRequestCountPerTarget"
    RDSReaderAverageCPUUtilization = "RDSReaderAverageCPUUtilization"
    RDSReaderAverageDatabaseConnections = "RDSReaderAverageDatabaseConnections"
    EC2SpotFleetRequestAverageCPUUtilization = "EC2SpotFleetRequestAverageCPUUtilization"
    EC2SpotFleetRequestAverageNetworkIn = "EC2SpotFleetRequestAverageNetworkIn"
    EC2SpotFleetRequestAverageNetworkOut = "EC2SpotFleetRequestAverageNetworkOut"
    SageMakerVariantInvocationsPerInstance = "SageMakerVariantInvocationsPerInstance"
    ECSServiceAverageCPUUtilization = "ECSServiceAverageCPUUtilization"
    ECSServiceAverageMemoryUtilization = "ECSServiceAverageMemoryUtilization"
    AppStreamAverageCapacityUtilization = "AppStreamAverageCapacityUtilization"
    ComprehendInferenceUtilization = "ComprehendInferenceUtilization"
    LambdaProvisionedConcurrencyUtilization = "LambdaProvisionedConcurrencyUtilization"
    CassandraReadCapacityUtilization = "CassandraReadCapacityUtilization"
    CassandraWriteCapacityUtilization = "CassandraWriteCapacityUtilization"
    KafkaBrokerStorageUtilization = "KafkaBrokerStorageUtilization"
    ElastiCachePrimaryEngineCPUUtilization = "ElastiCachePrimaryEngineCPUUtilization"
    ElastiCacheReplicaEngineCPUUtilization = "ElastiCacheReplicaEngineCPUUtilization"
    ElastiCacheDatabaseMemoryUsageCountedForEvictPercentage = (
        "ElastiCacheDatabaseMemoryUsageCountedForEvictPercentage"
    )
    NeptuneReaderAverageCPUUtilization = "NeptuneReaderAverageCPUUtilization"


class PolicyType(str):
    StepScaling = "StepScaling"
    TargetTrackingScaling = "TargetTrackingScaling"


class ScalableDimension(str):
    ecs_service_DesiredCount = "ecs:service:DesiredCount"
    ec2_spot_fleet_request_TargetCapacity = "ec2:spot-fleet-request:TargetCapacity"
    elasticmapreduce_instancegroup_InstanceCount = "elasticmapreduce:instancegroup:InstanceCount"
    appstream_fleet_DesiredCapacity = "appstream:fleet:DesiredCapacity"
    dynamodb_table_ReadCapacityUnits = "dynamodb:table:ReadCapacityUnits"
    dynamodb_table_WriteCapacityUnits = "dynamodb:table:WriteCapacityUnits"
    dynamodb_index_ReadCapacityUnits = "dynamodb:index:ReadCapacityUnits"
    dynamodb_index_WriteCapacityUnits = "dynamodb:index:WriteCapacityUnits"
    rds_cluster_ReadReplicaCount = "rds:cluster:ReadReplicaCount"
    sagemaker_variant_DesiredInstanceCount = "sagemaker:variant:DesiredInstanceCount"
    custom_resource_ResourceType_Property = "custom-resource:ResourceType:Property"
    comprehend_document_classifier_endpoint_DesiredInferenceUnits = (
        "comprehend:document-classifier-endpoint:DesiredInferenceUnits"
    )
    comprehend_entity_recognizer_endpoint_DesiredInferenceUnits = (
        "comprehend:entity-recognizer-endpoint:DesiredInferenceUnits"
    )
    lambda_function_ProvisionedConcurrency = "lambda:function:ProvisionedConcurrency"
    cassandra_table_ReadCapacityUnits = "cassandra:table:ReadCapacityUnits"
    cassandra_table_WriteCapacityUnits = "cassandra:table:WriteCapacityUnits"
    kafka_broker_storage_VolumeSize = "kafka:broker-storage:VolumeSize"
    elasticache_replication_group_NodeGroups = "elasticache:replication-group:NodeGroups"
    elasticache_replication_group_Replicas = "elasticache:replication-group:Replicas"
    neptune_cluster_ReadReplicaCount = "neptune:cluster:ReadReplicaCount"


class ScalingActivityStatusCode(str):
    Pending = "Pending"
    InProgress = "InProgress"
    Successful = "Successful"
    Overridden = "Overridden"
    Unfulfilled = "Unfulfilled"
    Failed = "Failed"


class ServiceNamespace(str):
    ecs = "ecs"
    elasticmapreduce = "elasticmapreduce"
    ec2 = "ec2"
    appstream = "appstream"
    dynamodb = "dynamodb"
    rds = "rds"
    sagemaker = "sagemaker"
    custom_resource = "custom-resource"
    comprehend = "comprehend"
    lambda_ = "lambda"
    cassandra = "cassandra"
    kafka = "kafka"
    elasticache = "elasticache"
    neptune = "neptune"


class ConcurrentUpdateException(ServiceException):
    """Concurrent updates caused an exception, for example, if you request an
    update to an Application Auto Scaling resource that already has a
    pending update.
    """

    Message: Optional[ErrorMessage]


class FailedResourceAccessException(ServiceException):
    """Failed access to resources caused an exception. This exception is thrown
    when Application Auto Scaling is unable to retrieve the alarms
    associated with a scaling policy due to a client error, for example, if
    the role ARN specified for a scalable target does not have permission to
    call the CloudWatch
    `DescribeAlarms <https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/API_DescribeAlarms.html>`__
    on your behalf.
    """

    Message: Optional[ErrorMessage]


class InternalServiceException(ServiceException):
    """The service encountered an internal error."""

    Message: Optional[ErrorMessage]


class InvalidNextTokenException(ServiceException):
    """The next token supplied was invalid."""

    Message: Optional[ErrorMessage]


class LimitExceededException(ServiceException):
    """A per-account resource limit is exceeded. For more information, see
    `Application Auto Scaling service
    quotas <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-limits.html>`__.
    """

    Message: Optional[ErrorMessage]


class ObjectNotFoundException(ServiceException):
    """The specified object could not be found. For any operation that depends
    on the existence of a scalable target, this exception is thrown if the
    scalable target with the specified service namespace, resource ID, and
    scalable dimension does not exist. For any operation that deletes or
    deregisters a resource, this exception is thrown if the resource cannot
    be found.
    """

    Message: Optional[ErrorMessage]


class ValidationException(ServiceException):
    """An exception was thrown for a validation issue. Review the available
    parameters for the API request.
    """

    Message: Optional[ErrorMessage]


class Alarm(TypedDict, total=False):
    """Represents a CloudWatch alarm associated with a scaling policy."""

    AlarmName: ResourceId
    AlarmARN: ResourceId


Alarms = List[Alarm]


class MetricDimension(TypedDict, total=False):
    """Describes the dimension names and values associated with a metric."""

    Name: MetricDimensionName
    Value: MetricDimensionValue


MetricDimensions = List[MetricDimension]


class CustomizedMetricSpecification(TypedDict, total=False):
    """Represents a CloudWatch metric of your choosing for a target tracking
    scaling policy to use with Application Auto Scaling.

    For information about the available metrics for a service, see `Amazon
    Web Services Services That Publish CloudWatch
    Metrics <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html>`__
    in the *Amazon CloudWatch User Guide*.

    To create your customized metric specification:

    -  Add values for each required parameter from CloudWatch. You can use
       an existing metric, or a new metric that you create. To use your own
       metric, you must first publish the metric to CloudWatch. For more
       information, see `Publish Custom
       Metrics <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/publishingMetrics.html>`__
       in the *Amazon CloudWatch User Guide*.

    -  Choose a metric that changes proportionally with capacity. The value
       of the metric should increase or decrease in inverse proportion to
       the number of capacity units. That is, the value of the metric should
       decrease when capacity increases, and increase when capacity
       decreases.

    For more information about CloudWatch, see `Amazon CloudWatch
    Concepts <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html>`__.
    """

    MetricName: MetricName
    Namespace: MetricNamespace
    Dimensions: Optional[MetricDimensions]
    Statistic: MetricStatistic
    Unit: Optional[MetricUnit]


class DeleteScalingPolicyRequest(ServiceRequest):
    PolicyName: ResourceIdMaxLen1600
    ServiceNamespace: ServiceNamespace
    ResourceId: ResourceIdMaxLen1600
    ScalableDimension: ScalableDimension


class DeleteScalingPolicyResponse(TypedDict, total=False):
    pass


class DeleteScheduledActionRequest(ServiceRequest):
    ServiceNamespace: ServiceNamespace
    ScheduledActionName: ResourceIdMaxLen1600
    ResourceId: ResourceIdMaxLen1600
    ScalableDimension: ScalableDimension


class DeleteScheduledActionResponse(TypedDict, total=False):
    pass


class DeregisterScalableTargetRequest(ServiceRequest):
    ServiceNamespace: ServiceNamespace
    ResourceId: ResourceIdMaxLen1600
    ScalableDimension: ScalableDimension


class DeregisterScalableTargetResponse(TypedDict, total=False):
    pass


ResourceIdsMaxLen1600 = List[ResourceIdMaxLen1600]


class DescribeScalableTargetsRequest(ServiceRequest):
    ServiceNamespace: ServiceNamespace
    ResourceIds: Optional[ResourceIdsMaxLen1600]
    ScalableDimension: Optional[ScalableDimension]
    MaxResults: Optional[MaxResults]
    NextToken: Optional[XmlString]


class SuspendedState(TypedDict, total=False):
    """Specifies whether the scaling activities for a scalable target are in a
    suspended state.
    """

    DynamicScalingInSuspended: Optional[ScalingSuspended]
    DynamicScalingOutSuspended: Optional[ScalingSuspended]
    ScheduledScalingSuspended: Optional[ScalingSuspended]


TimestampType = datetime


class ScalableTarget(TypedDict, total=False):
    """Represents a scalable target."""

    ServiceNamespace: ServiceNamespace
    ResourceId: ResourceIdMaxLen1600
    ScalableDimension: ScalableDimension
    MinCapacity: ResourceCapacity
    MaxCapacity: ResourceCapacity
    RoleARN: ResourceIdMaxLen1600
    CreationTime: TimestampType
    SuspendedState: Optional[SuspendedState]


ScalableTargets = List[ScalableTarget]


class DescribeScalableTargetsResponse(TypedDict, total=False):
    ScalableTargets: Optional[ScalableTargets]
    NextToken: Optional[XmlString]


class DescribeScalingActivitiesRequest(ServiceRequest):
    ServiceNamespace: ServiceNamespace
    ResourceId: Optional[ResourceIdMaxLen1600]
    ScalableDimension: Optional[ScalableDimension]
    MaxResults: Optional[MaxResults]
    NextToken: Optional[XmlString]


class ScalingActivity(TypedDict, total=False):
    """Represents a scaling activity."""

    ActivityId: ResourceId
    ServiceNamespace: ServiceNamespace
    ResourceId: ResourceIdMaxLen1600
    ScalableDimension: ScalableDimension
    Description: XmlString
    Cause: XmlString
    StartTime: TimestampType
    EndTime: Optional[TimestampType]
    StatusCode: ScalingActivityStatusCode
    StatusMessage: Optional[XmlString]
    Details: Optional[XmlString]


ScalingActivities = List[ScalingActivity]


class DescribeScalingActivitiesResponse(TypedDict, total=False):
    ScalingActivities: Optional[ScalingActivities]
    NextToken: Optional[XmlString]


class DescribeScalingPoliciesRequest(ServiceRequest):
    PolicyNames: Optional[ResourceIdsMaxLen1600]
    ServiceNamespace: ServiceNamespace
    ResourceId: Optional[ResourceIdMaxLen1600]
    ScalableDimension: Optional[ScalableDimension]
    MaxResults: Optional[MaxResults]
    NextToken: Optional[XmlString]


class PredefinedMetricSpecification(TypedDict, total=False):
    """Represents a predefined metric for a target tracking scaling policy to
    use with Application Auto Scaling.

    Only the Amazon Web Services that you're using send metrics to Amazon
    CloudWatch. To determine whether a desired metric already exists by
    looking up its namespace and dimension using the CloudWatch metrics
    dashboard in the console, follow the procedure in `Building dashboards
    with
    CloudWatch <https://docs.aws.amazon.com/autoscaling/application/userguide/monitoring-cloudwatch.html>`__
    in the *Application Auto Scaling User Guide*.
    """

    PredefinedMetricType: MetricType
    ResourceLabel: Optional[ResourceLabel]


class TargetTrackingScalingPolicyConfiguration(TypedDict, total=False):
    """Represents a target tracking scaling policy configuration to use with
    Application Auto Scaling.
    """

    TargetValue: MetricScale
    PredefinedMetricSpecification: Optional[PredefinedMetricSpecification]
    CustomizedMetricSpecification: Optional[CustomizedMetricSpecification]
    ScaleOutCooldown: Optional[Cooldown]
    ScaleInCooldown: Optional[Cooldown]
    DisableScaleIn: Optional[DisableScaleIn]


class StepAdjustment(TypedDict, total=False):
    """Represents a step adjustment for a
    `StepScalingPolicyConfiguration <https://docs.aws.amazon.com/autoscaling/application/APIReference/API_StepScalingPolicyConfiguration.html>`__.
    Describes an adjustment based on the difference between the value of the
    aggregated CloudWatch metric and the breach threshold that you've
    defined for the alarm.

    For the following examples, suppose that you have an alarm with a breach
    threshold of 50:

    -  To trigger the adjustment when the metric is greater than or equal to
       50 and less than 60, specify a lower bound of 0 and an upper bound of
       10.

    -  To trigger the adjustment when the metric is greater than 40 and less
       than or equal to 50, specify a lower bound of -10 and an upper bound
       of 0.

    There are a few rules for the step adjustments for your step policy:

    -  The ranges of your step adjustments can't overlap or have a gap.

    -  At most one step adjustment can have a null lower bound. If one step
       adjustment has a negative lower bound, then there must be a step
       adjustment with a null lower bound.

    -  At most one step adjustment can have a null upper bound. If one step
       adjustment has a positive upper bound, then there must be a step
       adjustment with a null upper bound.

    -  The upper and lower bound can't be null in the same step adjustment.
    """

    MetricIntervalLowerBound: Optional[MetricScale]
    MetricIntervalUpperBound: Optional[MetricScale]
    ScalingAdjustment: ScalingAdjustment


StepAdjustments = List[StepAdjustment]


class StepScalingPolicyConfiguration(TypedDict, total=False):
    """Represents a step scaling policy configuration to use with Application
    Auto Scaling.
    """

    AdjustmentType: Optional[AdjustmentType]
    StepAdjustments: Optional[StepAdjustments]
    MinAdjustmentMagnitude: Optional[MinAdjustmentMagnitude]
    Cooldown: Optional[Cooldown]
    MetricAggregationType: Optional[MetricAggregationType]


class ScalingPolicy(TypedDict, total=False):
    """Represents a scaling policy to use with Application Auto Scaling.

    For more information about configuring scaling policies for a specific
    service, see `Getting started with Application Auto
    Scaling <https://docs.aws.amazon.com/autoscaling/application/userguide/getting-started.html>`__
    in the *Application Auto Scaling User Guide*.
    """

    PolicyARN: ResourceIdMaxLen1600
    PolicyName: PolicyName
    ServiceNamespace: ServiceNamespace
    ResourceId: ResourceIdMaxLen1600
    ScalableDimension: ScalableDimension
    PolicyType: PolicyType
    StepScalingPolicyConfiguration: Optional[StepScalingPolicyConfiguration]
    TargetTrackingScalingPolicyConfiguration: Optional[TargetTrackingScalingPolicyConfiguration]
    Alarms: Optional[Alarms]
    CreationTime: TimestampType


ScalingPolicies = List[ScalingPolicy]


class DescribeScalingPoliciesResponse(TypedDict, total=False):
    ScalingPolicies: Optional[ScalingPolicies]
    NextToken: Optional[XmlString]


class DescribeScheduledActionsRequest(ServiceRequest):
    ScheduledActionNames: Optional[ResourceIdsMaxLen1600]
    ServiceNamespace: ServiceNamespace
    ResourceId: Optional[ResourceIdMaxLen1600]
    ScalableDimension: Optional[ScalableDimension]
    MaxResults: Optional[MaxResults]
    NextToken: Optional[XmlString]


class ScalableTargetAction(TypedDict, total=False):
    """Represents the minimum and maximum capacity for a scheduled action."""

    MinCapacity: Optional[ResourceCapacity]
    MaxCapacity: Optional[ResourceCapacity]


class ScheduledAction(TypedDict, total=False):
    """Represents a scheduled action."""

    ScheduledActionName: ScheduledActionName
    ScheduledActionARN: ResourceIdMaxLen1600
    ServiceNamespace: ServiceNamespace
    Schedule: ResourceIdMaxLen1600
    Timezone: Optional[ResourceIdMaxLen1600]
    ResourceId: ResourceIdMaxLen1600
    ScalableDimension: Optional[ScalableDimension]
    StartTime: Optional[TimestampType]
    EndTime: Optional[TimestampType]
    ScalableTargetAction: Optional[ScalableTargetAction]
    CreationTime: TimestampType


ScheduledActions = List[ScheduledAction]


class DescribeScheduledActionsResponse(TypedDict, total=False):
    ScheduledActions: Optional[ScheduledActions]
    NextToken: Optional[XmlString]


class PutScalingPolicyRequest(ServiceRequest):
    PolicyName: PolicyName
    ServiceNamespace: ServiceNamespace
    ResourceId: ResourceIdMaxLen1600
    ScalableDimension: ScalableDimension
    PolicyType: Optional[PolicyType]
    StepScalingPolicyConfiguration: Optional[StepScalingPolicyConfiguration]
    TargetTrackingScalingPolicyConfiguration: Optional[TargetTrackingScalingPolicyConfiguration]


class PutScalingPolicyResponse(TypedDict, total=False):
    PolicyARN: ResourceIdMaxLen1600
    Alarms: Optional[Alarms]


class PutScheduledActionRequest(ServiceRequest):
    ServiceNamespace: ServiceNamespace
    Schedule: Optional[ResourceIdMaxLen1600]
    Timezone: Optional[ResourceIdMaxLen1600]
    ScheduledActionName: ScheduledActionName
    ResourceId: ResourceIdMaxLen1600
    ScalableDimension: ScalableDimension
    StartTime: Optional[TimestampType]
    EndTime: Optional[TimestampType]
    ScalableTargetAction: Optional[ScalableTargetAction]


class PutScheduledActionResponse(TypedDict, total=False):
    pass


class RegisterScalableTargetRequest(ServiceRequest):
    ServiceNamespace: ServiceNamespace
    ResourceId: ResourceIdMaxLen1600
    ScalableDimension: ScalableDimension
    MinCapacity: Optional[ResourceCapacity]
    MaxCapacity: Optional[ResourceCapacity]
    RoleARN: Optional[ResourceIdMaxLen1600]
    SuspendedState: Optional[SuspendedState]


class RegisterScalableTargetResponse(TypedDict, total=False):
    pass


class ApplicationAutoscalingApi:

    service = "application-autoscaling"
    version = "2016-02-06"

    @handler("DeleteScalingPolicy")
    def delete_scaling_policy(
        self,
        context: RequestContext,
        policy_name: ResourceIdMaxLen1600,
        service_namespace: ServiceNamespace,
        resource_id: ResourceIdMaxLen1600,
        scalable_dimension: ScalableDimension,
    ) -> DeleteScalingPolicyResponse:
        """Deletes the specified scaling policy for an Application Auto Scaling
        scalable target.

        Deleting a step scaling policy deletes the underlying alarm action, but
        does not delete the CloudWatch alarm associated with the scaling policy,
        even if it no longer has an associated action.

        For more information, see `Delete a step scaling
        policy <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-step-scaling-policies.html#delete-step-scaling-policy>`__
        and `Delete a target tracking scaling
        policy <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-target-tracking.html#delete-target-tracking-policy>`__
        in the *Application Auto Scaling User Guide*.

        :param policy_name: The name of the scaling policy.
        :param service_namespace: The namespace of the Amazon Web Services service that provides the
        resource.
        :param resource_id: The identifier of the resource associated with the scalable target.
        :param scalable_dimension: The scalable dimension.
        :returns: DeleteScalingPolicyResponse
        :raises ValidationException:
        :raises ObjectNotFoundException:
        :raises ConcurrentUpdateException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("DeleteScheduledAction")
    def delete_scheduled_action(
        self,
        context: RequestContext,
        service_namespace: ServiceNamespace,
        scheduled_action_name: ResourceIdMaxLen1600,
        resource_id: ResourceIdMaxLen1600,
        scalable_dimension: ScalableDimension,
    ) -> DeleteScheduledActionResponse:
        """Deletes the specified scheduled action for an Application Auto Scaling
        scalable target.

        For more information, see `Delete a scheduled
        action <https://docs.aws.amazon.com/autoscaling/application/userguide/scheduled-scaling-additional-cli-commands.html#delete-scheduled-action>`__
        in the *Application Auto Scaling User Guide*.

        :param service_namespace: The namespace of the Amazon Web Services service that provides the
        resource.
        :param scheduled_action_name: The name of the scheduled action.
        :param resource_id: The identifier of the resource associated with the scheduled action.
        :param scalable_dimension: The scalable dimension.
        :returns: DeleteScheduledActionResponse
        :raises ValidationException:
        :raises ObjectNotFoundException:
        :raises ConcurrentUpdateException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("DeregisterScalableTarget")
    def deregister_scalable_target(
        self,
        context: RequestContext,
        service_namespace: ServiceNamespace,
        resource_id: ResourceIdMaxLen1600,
        scalable_dimension: ScalableDimension,
    ) -> DeregisterScalableTargetResponse:
        """Deregisters an Application Auto Scaling scalable target when you have
        finished using it. To see which resources have been registered, use
        `DescribeScalableTargets <https://docs.aws.amazon.com/autoscaling/application/APIReference/API_DescribeScalableTargets.html>`__.

        Deregistering a scalable target deletes the scaling policies and the
        scheduled actions that are associated with it.

        :param service_namespace: The namespace of the Amazon Web Services service that provides the
        resource.
        :param resource_id: The identifier of the resource associated with the scalable target.
        :param scalable_dimension: The scalable dimension associated with the scalable target.
        :returns: DeregisterScalableTargetResponse
        :raises ValidationException:
        :raises ObjectNotFoundException:
        :raises ConcurrentUpdateException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("DescribeScalableTargets")
    def describe_scalable_targets(
        self,
        context: RequestContext,
        service_namespace: ServiceNamespace,
        resource_ids: ResourceIdsMaxLen1600 = None,
        scalable_dimension: ScalableDimension = None,
        max_results: MaxResults = None,
        next_token: XmlString = None,
    ) -> DescribeScalableTargetsResponse:
        """Gets information about the scalable targets in the specified namespace.

        You can filter the results using ``ResourceIds`` and
        ``ScalableDimension``.

        :param service_namespace: The namespace of the Amazon Web Services service that provides the
        resource.
        :param resource_ids: The identifier of the resource associated with the scalable target.
        :param scalable_dimension: The scalable dimension associated with the scalable target.
        :param max_results: The maximum number of scalable targets.
        :param next_token: The token for the next set of results.
        :returns: DescribeScalableTargetsResponse
        :raises ValidationException:
        :raises InvalidNextTokenException:
        :raises ConcurrentUpdateException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("DescribeScalingActivities")
    def describe_scaling_activities(
        self,
        context: RequestContext,
        service_namespace: ServiceNamespace,
        resource_id: ResourceIdMaxLen1600 = None,
        scalable_dimension: ScalableDimension = None,
        max_results: MaxResults = None,
        next_token: XmlString = None,
    ) -> DescribeScalingActivitiesResponse:
        """Provides descriptive information about the scaling activities in the
        specified namespace from the previous six weeks.

        You can filter the results using ``ResourceId`` and
        ``ScalableDimension``.

        :param service_namespace: The namespace of the Amazon Web Services service that provides the
        resource.
        :param resource_id: The identifier of the resource associated with the scaling activity.
        :param scalable_dimension: The scalable dimension.
        :param max_results: The maximum number of scalable targets.
        :param next_token: The token for the next set of results.
        :returns: DescribeScalingActivitiesResponse
        :raises ValidationException:
        :raises InvalidNextTokenException:
        :raises ConcurrentUpdateException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("DescribeScalingPolicies")
    def describe_scaling_policies(
        self,
        context: RequestContext,
        service_namespace: ServiceNamespace,
        policy_names: ResourceIdsMaxLen1600 = None,
        resource_id: ResourceIdMaxLen1600 = None,
        scalable_dimension: ScalableDimension = None,
        max_results: MaxResults = None,
        next_token: XmlString = None,
    ) -> DescribeScalingPoliciesResponse:
        """Describes the Application Auto Scaling scaling policies for the
        specified service namespace.

        You can filter the results using ``ResourceId``, ``ScalableDimension``,
        and ``PolicyNames``.

        For more information, see `Target tracking scaling
        policies <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-target-tracking.html>`__
        and `Step scaling
        policies <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-step-scaling-policies.html>`__
        in the *Application Auto Scaling User Guide*.

        :param service_namespace: The namespace of the Amazon Web Services service that provides the
        resource.
        :param policy_names: The names of the scaling policies to describe.
        :param resource_id: The identifier of the resource associated with the scaling policy.
        :param scalable_dimension: The scalable dimension.
        :param max_results: The maximum number of scalable targets.
        :param next_token: The token for the next set of results.
        :returns: DescribeScalingPoliciesResponse
        :raises ValidationException:
        :raises FailedResourceAccessException:
        :raises InvalidNextTokenException:
        :raises ConcurrentUpdateException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("DescribeScheduledActions")
    def describe_scheduled_actions(
        self,
        context: RequestContext,
        service_namespace: ServiceNamespace,
        scheduled_action_names: ResourceIdsMaxLen1600 = None,
        resource_id: ResourceIdMaxLen1600 = None,
        scalable_dimension: ScalableDimension = None,
        max_results: MaxResults = None,
        next_token: XmlString = None,
    ) -> DescribeScheduledActionsResponse:
        """Describes the Application Auto Scaling scheduled actions for the
        specified service namespace.

        You can filter the results using the ``ResourceId``,
        ``ScalableDimension``, and ``ScheduledActionNames`` parameters.

        For more information, see `Scheduled
        scaling <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-scheduled-scaling.html>`__
        and `Managing scheduled
        scaling <https://docs.aws.amazon.com/autoscaling/application/userguide/scheduled-scaling-additional-cli-commands.html>`__
        in the *Application Auto Scaling User Guide*.

        :param service_namespace: The namespace of the Amazon Web Services service that provides the
        resource.
        :param scheduled_action_names: The names of the scheduled actions to describe.
        :param resource_id: The identifier of the resource associated with the scheduled action.
        :param scalable_dimension: The scalable dimension.
        :param max_results: The maximum number of scheduled action results.
        :param next_token: The token for the next set of results.
        :returns: DescribeScheduledActionsResponse
        :raises ValidationException:
        :raises InvalidNextTokenException:
        :raises ConcurrentUpdateException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("PutScalingPolicy")
    def put_scaling_policy(
        self,
        context: RequestContext,
        policy_name: PolicyName,
        service_namespace: ServiceNamespace,
        resource_id: ResourceIdMaxLen1600,
        scalable_dimension: ScalableDimension,
        policy_type: PolicyType = None,
        step_scaling_policy_configuration: StepScalingPolicyConfiguration = None,
        target_tracking_scaling_policy_configuration: TargetTrackingScalingPolicyConfiguration = None,
    ) -> PutScalingPolicyResponse:
        """Creates or updates a scaling policy for an Application Auto Scaling
        scalable target.

        Each scalable target is identified by a service namespace, resource ID,
        and scalable dimension. A scaling policy applies to the scalable target
        identified by those three attributes. You cannot create a scaling policy
        until you have registered the resource as a scalable target.

        Multiple scaling policies can be in force at the same time for the same
        scalable target. You can have one or more target tracking scaling
        policies, one or more step scaling policies, or both. However, there is
        a chance that multiple policies could conflict, instructing the scalable
        target to scale out or in at the same time. Application Auto Scaling
        gives precedence to the policy that provides the largest capacity for
        both scale out and scale in. For example, if one policy increases
        capacity by 3, another policy increases capacity by 200 percent, and the
        current capacity is 10, Application Auto Scaling uses the policy with
        the highest calculated capacity (200% of 10 = 20) and scales out to 30.

        We recommend caution, however, when using target tracking scaling
        policies with step scaling policies because conflicts between these
        policies can cause undesirable behavior. For example, if the step
        scaling policy initiates a scale-in activity before the target tracking
        policy is ready to scale in, the scale-in activity will not be blocked.
        After the scale-in activity completes, the target tracking policy could
        instruct the scalable target to scale out again.

        For more information, see `Target tracking scaling
        policies <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-target-tracking.html>`__
        and `Step scaling
        policies <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-step-scaling-policies.html>`__
        in the *Application Auto Scaling User Guide*.

        If a scalable target is deregistered, the scalable target is no longer
        available to execute scaling policies. Any scaling policies that were
        specified for the scalable target are deleted.

        :param policy_name: The name of the scaling policy.
        :param service_namespace: The namespace of the Amazon Web Services service that provides the
        resource.
        :param resource_id: The identifier of the resource associated with the scaling policy.
        :param scalable_dimension: The scalable dimension.
        :param policy_type: The policy type.
        :param step_scaling_policy_configuration: A step scaling policy.
        :param target_tracking_scaling_policy_configuration: A target tracking scaling policy.
        :returns: PutScalingPolicyResponse
        :raises ValidationException:
        :raises LimitExceededException:
        :raises ObjectNotFoundException:
        :raises ConcurrentUpdateException:
        :raises FailedResourceAccessException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("PutScheduledAction")
    def put_scheduled_action(
        self,
        context: RequestContext,
        service_namespace: ServiceNamespace,
        scheduled_action_name: ScheduledActionName,
        resource_id: ResourceIdMaxLen1600,
        scalable_dimension: ScalableDimension,
        schedule: ResourceIdMaxLen1600 = None,
        timezone: ResourceIdMaxLen1600 = None,
        start_time: TimestampType = None,
        end_time: TimestampType = None,
        scalable_target_action: ScalableTargetAction = None,
    ) -> PutScheduledActionResponse:
        """Creates or updates a scheduled action for an Application Auto Scaling
        scalable target.

        Each scalable target is identified by a service namespace, resource ID,
        and scalable dimension. A scheduled action applies to the scalable
        target identified by those three attributes. You cannot create a
        scheduled action until you have registered the resource as a scalable
        target.

        When start and end times are specified with a recurring schedule using a
        cron expression or rates, they form the boundaries for when the
        recurring action starts and stops.

        To update a scheduled action, specify the parameters that you want to
        change. If you don't specify start and end times, the old values are
        deleted.

        For more information, see `Scheduled
        scaling <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-scheduled-scaling.html>`__
        in the *Application Auto Scaling User Guide*.

        If a scalable target is deregistered, the scalable target is no longer
        available to run scheduled actions. Any scheduled actions that were
        specified for the scalable target are deleted.

        :param service_namespace: The namespace of the Amazon Web Services service that provides the
        resource.
        :param scheduled_action_name: The name of the scheduled action.
        :param resource_id: The identifier of the resource associated with the scheduled action.
        :param scalable_dimension: The scalable dimension.
        :param schedule: The schedule for this action.
        :param timezone: Specifies the time zone used when setting a scheduled action by using an
        at or cron expression.
        :param start_time: The date and time for this scheduled action to start, in UTC.
        :param end_time: The date and time for the recurring schedule to end, in UTC.
        :param scalable_target_action: The new minimum and maximum capacity.
        :returns: PutScheduledActionResponse
        :raises ValidationException:
        :raises LimitExceededException:
        :raises ObjectNotFoundException:
        :raises ConcurrentUpdateException:
        :raises InternalServiceException:
        """
        raise NotImplementedError

    @handler("RegisterScalableTarget")
    def register_scalable_target(
        self,
        context: RequestContext,
        service_namespace: ServiceNamespace,
        resource_id: ResourceIdMaxLen1600,
        scalable_dimension: ScalableDimension,
        min_capacity: ResourceCapacity = None,
        max_capacity: ResourceCapacity = None,
        role_arn: ResourceIdMaxLen1600 = None,
        suspended_state: SuspendedState = None,
    ) -> RegisterScalableTargetResponse:
        """Registers or updates a scalable target.

        A scalable target is a resource that Application Auto Scaling can scale
        out and scale in. Scalable targets are uniquely identified by the
        combination of resource ID, scalable dimension, and namespace.

        When you register a new scalable target, you must specify values for
        minimum and maximum capacity. Current capacity will be adjusted within
        the specified range when scaling starts. Application Auto Scaling
        scaling policies will not scale capacity to values that are outside of
        this range.

        After you register a scalable target, you do not need to register it
        again to use other Application Auto Scaling operations. To see which
        resources have been registered, use
        `DescribeScalableTargets <https://docs.aws.amazon.com/autoscaling/application/APIReference/API_DescribeScalableTargets.html>`__.
        You can also view the scaling policies for a service namespace by using
        `DescribeScalableTargets <https://docs.aws.amazon.com/autoscaling/application/APIReference/API_DescribeScalableTargets.html>`__.
        If you no longer need a scalable target, you can deregister it by using
        `DeregisterScalableTarget <https://docs.aws.amazon.com/autoscaling/application/APIReference/API_DeregisterScalableTarget.html>`__.

        To update a scalable target, specify the parameters that you want to
        change. Include the parameters that identify the scalable target:
        resource ID, scalable dimension, and namespace. Any parameters that you
        don't specify are not changed by this update request.

        If you call the ``RegisterScalableTarget`` API to update an existing
        scalable target, Application Auto Scaling retrieves the current capacity
        of the resource. If it is below the minimum capacity or above the
        maximum capacity, Application Auto Scaling adjusts the capacity of the
        scalable target to place it within these bounds, even if you don't
        include the ``MinCapacity`` or ``MaxCapacity`` request parameters.

        :param service_namespace: The namespace of the Amazon Web Services service that provides the
        resource.
        :param resource_id: The identifier of the resource that is associated with the scalable
        target.
        :param scalable_dimension: The scalable dimension associated with the scalable target.
        :param min_capacity: The minimum value that you plan to scale in to.
        :param max_capacity: The maximum value that you plan to scale out to.
        :param role_arn: This parameter is required for services that do not support
        service-linked roles (such as Amazon EMR), and it must specify the ARN
        of an IAM role that allows Application Auto Scaling to modify the
        scalable target on your behalf.
        :param suspended_state: An embedded object that contains attributes and attribute values that
        are used to suspend and resume automatic scaling.
        :returns: RegisterScalableTargetResponse
        :raises ValidationException:
        :raises LimitExceededException:
        :raises ConcurrentUpdateException:
        :raises InternalServiceException:
        """
        raise NotImplementedError
