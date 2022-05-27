"""
hub.exec.boto3.client.cloudwatch.put_metric_alarm
hub.exec.boto3.client.cloudwatch.delete_alarms
hub.exec.boto3.client.cloudwatch.describe_alarms

"""
import copy
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    period: int,
    evaluation_periods: int,
    comparison_operator: str,
    resource_id: str = None,
    alarm_description: str = None,
    actions_enabled: bool = True,
    ok_actions: List = None,
    alarm_actions: List = None,
    insufficient_data_actions: List = None,
    metric_name: str = None,
    namespace: str = None,
    statistic: str = None,
    extended_statistic: str = None,
    dimensions: List = None,
    unit: str = None,
    datapoints_to_alarm: int = None,
    threshold: float = None,
    treat_missing_data: str = None,
    evaluate_low_sample_count_percentile: str = None,
    metrics: List = None,
    threshold_metric_id: str = None,
    tags: List = None,
):
    r"""

    Creates or updates an alarm and associates it with the specified metric, metric math expression, or anomaly
    detection model.Alarms based on anomaly detection models cannot have Auto Scaling actions. When this operation
    creates an alarm, the alarm state is immediately set to INSUFFICIENT_DATA . The alarm is then evaluated and its
    state is set appropriately. Any actions associated with the new state are then executed. When you update an
    existing alarm, its state is left unchanged, but the update completely overwrites the previous configuration
    of the alarm. If you are an IAM user,
    you must have Amazon EC2 permissions for some alarm operations:
        * The iam:CreateServiceLinkedRole for all alarms with EC2 actions
        * The iam:CreateServiceLinkedRole to create an alarm with Systems Manager OpsItem actions.
    The first time you create an alarm in the Amazon Web Services Management Console, the CLI, or by using the
    PutMetricAlarm API, CloudWatch creates the necessary service-linked role for you. The service-linked roles are
    called AWSServiceRoleForCloudWatchEvents and AWSServiceRoleForCloudWatchAlarms_ActionSSM.

    Args:
        name(Text): The name for the alarm. This name must be unique within the Region.
        resource_id(Text): The AWS name of the metric alarm.
        alarm_description(Text, Optional): The description for the alarm.
        actions_enabled(Boolean, Optional): Indicates whether actions should be executed during any changes to the alarm
        state.
            The default is TRUE .
        ok_actions(List, Optional): The actions to execute when this alarm transitions to an OK state from any other
        state.
            Each action is specified as an Amazon Resource Name (ARN).
            Valid Values:
                arn:aws:automate:*region* :ec2:stop | arn:aws:automate:*region* :ec2:terminate |
                arn:aws:automate:*region* :ec2:recover | arn:aws:automate:*region* :ec2:reboot |
                ``arn:aws:sns:region :account-id :sns-topic-name `` |
                ``arn:aws:autoscaling:region :account-id :scalingPolicy:policy-id
                :autoScalingGroupName/group-friendly-name :policyName/policy-friendly-name ``
            Valid Values (for use with IAM roles):
                arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Stop/1.0 |
                arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Terminate/1.0 |
                arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Reboot/1.0 |
                arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Recover/1.0
        alarm_actions(List, Optional):The actions to execute when this alarm transitions to the ALARM state from any
        other state.
            Each action is specified as an Amazon Resource Name (ARN).
            Valid Values:
                arn:aws:automate:*region* :ec2:stop |
                arn:aws:automate:*region* :ec2:terminate |
                arn:aws:automate:*region* :ec2:recover |
                arn:aws:automate:*region* :ec2:reboot |
                ``arn:aws:sns:region :account-id :sns-topic-name `` |
                 ``arn:aws:autoscaling:region :account-id :scalingPolicy:policy-id
                 :autoScalingGroupName/group-friendly-name :policyName/policy-friendly-name `` |
                ``arn:aws:ssm:region :account-id :opsitem:severity `` |
                ``arn:aws:ssm-incidents::account-id :response-plan:response-plan-name ``
           Valid Values (for use with IAM roles):
                arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Stop/1.0 |
                arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Terminate/1.0 |
                arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Reboot/1.0 |
                arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Recover/1.0

        insufficient_data_actions(List, Optional):The actions to execute when this alarm transitions to the
        INSUFFICIENT_DATA state from any other state. Each action is specified as an Amazon Resource Name (ARN).
            Valid Values:
                arn:aws:automate:*region* :ec2:stop |
                arn:aws:automate:*region* :ec2:terminate |
                arn:aws:automate:*region* :ec2:recover |
                arn:aws:automate:*region* :ec2:reboot |
                ``arn:aws:sns:region :account-id :sns-topic-name `` |
                ``arn:aws:autoscaling:region :account-id :scalingPolicy:policy-id
                :autoScalingGroupName/group-friendly-name :policyName/policy-friendly-name ``
            Valid Values (for use with IAM roles):
                >arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Stop/1.0 |
                arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Terminate/1.0 |
                arn:aws:swf:*region* :*account-id* :action/actions/AWS_EC2.InstanceId.Reboot/1.0
        metric_name(Text, Optional): The name for the metric associated with the alarm. For each PutMetricAlarm operation,
            you must specify either MetricName or a Metrics array.
        namespace(Text, Optional): The namespace for the metric associated specified in MetricName .
        statistic(Text, Optional): The statistic for the metric specified in MetricName , other than percentile. For
            percentile statistics, use ExtendedStatistic . When you call PutMetricAlarm and specify a MetricName ,
            you must specify either Statistic or ExtendedStatistic, but not both.
        extended_statistic(Text, Optional): The percentile statistic for the metric specified in MetricName . Specify a value
            between p0.0 and p100. When you call PutMetricAlarm and specify a MetricName , you must specify either
            Statistic or ExtendedStatistic, but not both.
        dimensions(List, Optional): The dimensions for the metric specified in MetricName. A dimension is a name/value pair that
            is part of the identity of a metric. You can assign up to 10 dimensions to a metric. Because dimensions are
            part of the unique identifier for a metric, whenever you add a unique name/value pair to one of your
            metrics, you are creating a new variation of that metric.
            * Name (Text) -- The name of the dimension. Dimension names must contain only ASCII characters and must
                include at least one non-whitespace character.
            * Value (Text) -- The value of the dimension. Dimension values must contain only ASCII characters and must
                include at least one non-whitespace character.
        period(Integer): The length, in seconds, used each time the metric specified in MetricName is evaluated.
            Valid values are 10, 30, and any multiple of 60.
        unit(Text, Optional): The unit of measure for the statistic. For example, the units for the Amazon EC2 NetworkIn metric are
            Bytes because NetworkIn tracks the number of bytes that an instance receives on all network interfaces.
            You can also specify a unit when you create a custom metric. Units help provide conceptual meaning to your
            data. Metric data points that specify a unit of measure, such as Percent, are aggregated separately.
        evaluation_periods(Integer): The number of periods over which data is compared to the specified threshold.
            If you are setting an alarm that requires that a number of consecutive data points be breaching to trigger
            the alarm, this value specifies that number. If you are setting an "M out of N" alarm, this value is the N.
            An alarm's total current evaluation period can be no longer than one day, so this number multiplied by
            Period cannot be more than 86,400 seconds.

        datapoints_to_alarm(Integer, Optional): The number of data points that must be breaching to trigger the alarm.
            This is used only if you are setting an "M out of N" alarm. In that case, this value is the M.
        threshold(float, optional): The value against which the specified statistic is compared.  This parameter is required for
            alarms based on static thresholds, but should not be used for alarms based on anomaly detection models.
        comparison_operator(Text): The arithmetic operation to use when comparing the specified statistic and
            threshold. The specified statistic value is used as the first operand.
            The values LessThanLowerOrGreaterThanUpperThreshold , LessThanLowerThreshold , and
            GreaterThanUpperThreshold are used only for alarms based on anomaly detection models.
        treat_missing_data(Text, Optional): Sets how this alarm is to handle missing data points. If TreatMissingData is
            omitted, the default behavior of missing is used.
            Valid Values: breaching | notBreaching | ignore | missing
        evaluate_low_sample_count_percentile(Text, Optional): Used only for alarms based on percentiles. If you specify ignore ,
            the alarm state does not change during periods with too few data points to be statistically significant.
            If you specify evaluate or omit this parameter, the alarm is always evaluated and possibly changes state
            no matter how many data points are available.
        metrics(List, Optional): An array of MetricDataQuery structures that enable you to create an alarm based on the result
            of a metric math expression. For each PutMetricAlarm operation, you must specify either MetricName or a
            Metrics array.
        threshold_metric_id(Text, Optional): If this is an alarm based on an anomaly detection model, make this value match the
            ID of the ANOMALY_DETECTION_BAND function.
        tags(List, Optional): A list of key-value pairs to associate with the alarm. You can associate as many as 50 tags with an
            alarm.
            * Key (Text) -- A string that you can use to assign a value. The combination of tag keys and values can
                help you organize and categorize your resources.
            * Value (Text) -- The value for the specified tag key.

    Request Syntax:
        [metric-alarm-name]::
            aws.cloudwatch.metric_alarm.present:
            - name: 'string'
            - alarm_description: 'string'
            - actions_enabled: True|False
            - ok_actions= ['string']
            - alarm_actions: ['string']
            - insufficient_data_actions: ['string']
            - metric_name: 'string'
            - namespace: 'string'
            - statistic: 'SampleCount'|'Average'|'Sum'|'Minimum'|'Maximum'
            - dimensions: 'list'
            - period: 'integer'
            - unit: 'string'
            - evaluation_periods: 'integer'
            - datapoints_to_alarm: 'integer'
            - threshold: 'integer'
            - comparison_operator: 'string'
            - treat_missing_data: 'string',
            - evaluate_low_sample_count_percentile: 'string',
            - metrics: 'list'
            - threshold_metric_id: 'string'
            - tags:
              - Key: 'string'
                Value: 'string'

    Returns:
         Dict[str, Any]


    Examples:

        .. code-block:: sls

            awsec2-i-0f36e2b10a7463129-LessThanOrEqualToThreshold-CPUUtilization:
              aws.cloudwatch.metric_alarm.present:
                - name: awsec2-i-0f36e2b10a7463129-LessThanOrEqualToThreshold-CPUUtilization
                - alarm_description: "stop EC2 instance if it utilizes CPU less than 5"
                - actions_enabled: True
                - alarm_actions:
                  - arn:aws:swf:*region*:*account-id*:action/actions/AWS_EC2.InstanceId.Stop/1.0
                - insufficient_data_actions: []
                - metric_name: CPUUtilization
                - namespace: AWS/EC2
                - statistic: Average
                - dimensions:
                  - Name: InstanceId
                    Value: i-0f36e2b10a7463129
                - period: 60
                - evaluation_periods: 1
                - datapoints_to_alarm: 1
                - threshold: 20
                - comparison_operator: LessThanThreshold
                - tags:
                  - Key: type
                    Value: metric_alarm

    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    resource_updated = False
    before = None
    resource_parameters = {
        "AlarmName": name,
        "AlarmDescription": alarm_description,
        "ActionsEnabled": actions_enabled,
        "OKActions": ok_actions,
        "AlarmActions": alarm_actions,
        "InsufficientDataActions": insufficient_data_actions,
        "MetricName": metric_name,
        "Namespace": namespace,
        "Statistic": statistic,
        "ExtendedStatistic": extended_statistic,
        "Dimensions": dimensions,
        "Period": period,
        "Unit": unit,
        "EvaluationPeriods": evaluation_periods,
        "DatapointsToAlarm": datapoints_to_alarm,
        "Threshold": threshold,
        "ComparisonOperator": comparison_operator,
        "TreatMissingData": treat_missing_data,
        "EvaluateLowSampleCountPercentile": evaluate_low_sample_count_percentile,
        "Metrics": metrics,
        "ThresholdMetricId": threshold_metric_id,
        "Tags": tags,
    }

    if resource_id:
        resource = hub.tool.boto3.resource.create(
            ctx, "cloudwatch", "Alarm", resource_id
        )
        before = await hub.tool.boto3.resource.describe(resource)

    if before:
        try:
            convert_ret = await hub.tool.aws.cloudwatch.conversion_utils.convert_raw_metric_alarm_to_present(
                ctx, raw_resource=before, idem_resource_name=name
            )
            result["result"] = convert_ret["result"]
            if not result["result"]:
                result["comment"] = result["comment"] + convert_ret["comment"]
            result["old_state"] = convert_ret["ret"]

            plan_state = copy.deepcopy(result["old_state"])
            # Update metric alarm
            update_ret = await hub.exec.aws.cloudwatch.metric_alarm.update_metric(
                ctx,
                alarm_name=name,
                raw_resource=before,
                resource_parameters=resource_parameters,
            )
            result["comment"] = result["comment"] + update_ret["comment"]
            result["result"] = update_ret["result"]
            resource_updated = resource_updated or bool(update_ret["ret"])
            if update_ret["ret"] and ctx.get("test", False):
                for key in [
                    "alarm_description",
                    "actions_enabled",
                    "ok_actions",
                    "alarm_actions",
                    "metric_name",
                    "namespace",
                    "statistic",
                    "dimensions",
                    "period",
                    "evaluation_periods",
                    "datapoints_to_alarm",
                    "threshold",
                    "comparison_operator",
                ]:
                    if key in update_ret["ret"]:
                        plan_state[key] = update_ret["ret"][key]
            if (tags is not None) and (
                not hub.tool.aws.state_comparison_utils.are_lists_identical(
                    tags, result["old_state"].get("tags")
                )
            ):
                # Update tags
                update_tag_ret = (
                    await hub.exec.aws.cloudwatch.metric_alarm.update_metric_tags(
                        ctx=ctx,
                        alarm_arn=before.get("AlarmArn"),
                        old_tags=result["old_state"].get("tags", []),
                        new_tags=tags,
                    )
                )
                result["result"] = result["result"] and update_tag_ret["result"]
                result["comment"] = result["comment"] + update_tag_ret["comment"]
                resource_updated = resource_updated or bool(update_tag_ret["ret"])
                if ctx.get("test", False) and update_tag_ret["ret"] is not None:
                    plan_state["tags"] = update_tag_ret["ret"].get("tags")

            if not resource_updated:
                result["comment"] = result["comment"] + (
                    f"aws.cloudwatch.metric_alarm '{name}' has no property need to be updated.",
                )
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False
    else:
        try:
            if ctx.get("test", False):
                result["new_state"] = hub.tool.aws.test_state_utils.generate_test_state(
                    enforced_state={},
                    desired_state={
                        "name": name,
                        "alarm_description": alarm_description,
                        "actions_enabled": actions_enabled,
                        "ok_actions": ok_actions,
                        "alarm_actions": alarm_actions,
                        "insufficient_data_actions": insufficient_data_actions,
                        "metric_name": metric_name,
                        "namespace": namespace,
                        "statistic": statistic,
                        "extended_statistic": extended_statistic,
                        "dimensions": dimensions,
                        "period": period,
                        "unit": unit,
                        "evaluation_periods": evaluation_periods,
                        "datapoints_to_alarm": datapoints_to_alarm,
                        "threshold": threshold,
                        "comparison_operator": comparison_operator,
                        "treat_missing_data": treat_missing_data,
                        "evaluate_low_sample_count_percentile": evaluate_low_sample_count_percentile,
                        "metrics": metrics,
                        "tags": tags,
                        "threshold_metric_id": threshold_metric_id,
                    },
                )
                result["comment"] = (
                    f"Would create aws.cloudwatch.metric_alarm {name}",
                )
                return result

            # Create metric alarm
            ret = await hub.exec.boto3.client.cloudwatch.put_metric_alarm(
                ctx, **resource_parameters
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = result["comment"] + ret["comment"]
                return result
            result["comment"] = result["comment"] + (f"Created '{name}'",)
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)
            result["result"] = False

    try:
        if ctx.get("test", False):
            result["new_state"] = plan_state
        elif (not before) or resource_updated:
            resource = hub.tool.boto3.resource.create(ctx, "cloudwatch", "Alarm", name)
            after = await hub.tool.boto3.resource.describe(resource)
            convert_ret = await hub.tool.aws.cloudwatch.conversion_utils.convert_raw_metric_alarm_to_present(
                ctx, raw_resource=after, idem_resource_name=name
            )
            result["result"] = convert_ret["result"]
            if not result["result"]:
                result["comment"] = result["comment"] + convert_ret["comment"]
            result["new_state"] = convert_ret["ret"]
        else:
            result["new_state"] = copy.deepcopy(result["old_state"])
    except Exception as e:
        result["comment"] = result["comment"] + (str(e),)
        result["result"] = False

    return result


async def absent(hub, ctx, name: str, resource_id: str = None) -> Dict[str, Any]:
    r"""
    Deletes the specified alarms. You can delete up to 100 alarms in one operation. However, this total can include no
    more than one composite alarm. For example, you could delete 99 metric alarms and one composite alarms with one
    operation, but you can't delete two composite alarms with one operation.

    Args:
        name(Text): The AWS name of the metric alarm.
        resource_id(Text, optional): The AWS name of the metric alarm. Idem automatically considers this resource
         being absent if this field is not specified.

    Returns:
        Dict[str, Any]

    Examples:

        .. code-block:: sls

            [alarm name]:
               aws.cloudwatch.metric_alarm.absent:
                - resource_id: value

    """

    result = dict(comment=(), old_state=None, new_state=None, name=name, result=True)
    if not resource_id:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.cloudwatch.metric_alarm", name=name
        )
        return result
    resource = hub.tool.boto3.resource.create(ctx, "cloudwatch", "Alarm", resource_id)
    before = await hub.tool.boto3.resource.describe(resource)

    if not before:
        result["comment"] = hub.tool.aws.comment_utils.already_absent_comment(
            resource_type="aws.cloudwatch.metric_alarm", name=name
        )
    elif ctx.get("test", False):
        convert_ret = await hub.tool.aws.cloudwatch.conversion_utils.convert_raw_metric_alarm_to_present(
            ctx, raw_resource=before, idem_resource_name=name
        )
        result["result"] = convert_ret["result"]
        if not result["result"]:
            result["comment"] = result["comment"] + convert_ret["comment"]
        result["old_state"] = convert_ret["ret"]
        result["comment"] = hub.tool.aws.comment_utils.would_delete_comment(
            resource_type="aws.cloudwatch.metric_alarm", name=name
        )
        return result
    else:
        try:
            convert_ret = await hub.tool.aws.cloudwatch.conversion_utils.convert_raw_metric_alarm_to_present(
                ctx, raw_resource=before, idem_resource_name=name
            )
            result["result"] = convert_ret["result"]
            if not result["result"]:
                result["comment"] = result["comment"] + convert_ret["comment"]
            result["old_state"] = convert_ret["ret"]
            ret = await hub.exec.boto3.client.cloudwatch.delete_alarms(
                ctx, AlarmNames=[resource_id]
            )
            result["result"] = ret["result"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                result["result"] = False
                return result
            result["comment"] = hub.tool.aws.comment_utils.delete_comment(
                resource_type="aws.cloudwatch.metric_alarm", name=name
            )

        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = result["comment"] + (f"{e.__class__.__name__}: {e}",)

    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""
    Retrieves the specified alarms. You can filter the results by specifying a prefix for the alarm name, the alarm
    state, or a prefix for any action. To use this operation and return information about composite alarms, you must
    be signed on with the cloudwatch:DescribeAlarms permission that is scoped to * . You can't return information
    about composite alarms if your cloudwatch:DescribeAlarms permission has a narrower scope.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe aws.cloudwatch.metric_alarm
    """
    result = {}
    ret = await hub.exec.boto3.client.cloudwatch.describe_alarms(ctx)

    if not ret["result"]:
        hub.log.debug(f"Could not describe alarm metrics {ret['comment']}")
        return {}

    for resource in ret["ret"]["MetricAlarms"]:
        alarm_name = resource["AlarmName"]
        convert_ret = await hub.tool.aws.cloudwatch.conversion_utils.convert_raw_metric_alarm_to_present(
            ctx, raw_resource=resource, idem_resource_name=alarm_name
        )
        if not convert_ret["result"]:
            hub.log.warning(
                f"Could not describe alarm metrics '{alarm_name}' with error {convert_ret['comment']}"
            )
            continue
        translated_resource = convert_ret["ret"]
        result[translated_resource["resource_id"]] = {
            "aws.cloudwatch.metric_alarm.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in translated_resource.items()
            ]
        }

    return result
