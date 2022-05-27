from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util functions to convert raw resource state from AWS Cloudwatch to present input format.
"""


async def convert_raw_log_group_to_present(
    hub, ctx, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("logGroupName")
    resource_parameters = OrderedDict(
        {"kmsKeyId": "kms_key_id", "arn": "arn", "retentionInDays": "retention_in_days"}
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)
    if resource_id:
        # list_tags_log_group always returns true even if there is no tag
        tags = await hub.exec.boto3.client.logs.list_tags_log_group(
            ctx, logGroupName=resource_id
        )
        if tags["result"]:
            if tags["ret"]["tags"]:
                resource_translated["tags"] = dict(tags["ret"]["tags"])
    return resource_translated


async def convert_raw_metric_alarm_to_present(
    hub, ctx, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    r"""

    Args:
        hub:
        ctx:
        raw_resource: old state of metric alarm
        idem_resource_name: cloudwatch alarm name

    Returns:
        Dict[str, Any]
    """

    resource_parameters = OrderedDict(
        {
            "AlarmDescription": "alarm_description",
            "ActionsEnabled": "actions_enabled",
            "OKActions": "ok_actions",
            "AlarmActions": "alarm_actions",
            "InsufficientDataActions": "insufficient_data_actions",
            "MetricName": "metric_name",
            "Namespace": "namespace",
            "Statistic": "statistic",
            "ExtendedStatistic": "extended_statistic",
            "Dimensions": "dimensions",
            "Period": "period",
            "Unit": "unit",
            "EvaluationPeriods": "evaluation_periods",
            "DatapointsToAlarm": "datapoints_to_alarm",
            "Threshold": "threshold",
            "ComparisonOperator": "comparison_operator",
            "TreatMissingData": "treat_missing_data",
            "EvaluateLowSampleCountPercentile": "evaluate_low_sample_count_percentile",
            "Metrics": "metrics",
            "ThresholdMetricId": "threshold_metric_id",
            "Tags": "tags",
        }
    )
    resource_id = raw_resource.get("AlarmName")
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
    }
    result = dict(comment=(), result=True, ret=None)
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource[parameter_raw]

    alarm_arn = raw_resource.get("AlarmArn")
    ret_tag = await hub.exec.boto3.client.cloudwatch.list_tags_for_resource(
        ctx, ResourceARN=alarm_arn
    )
    result["result"] = ret_tag["result"]
    if not result["result"]:
        result["comment"] = result["comment"] + ret_tag["comment"]

    if result["result"] and ret_tag["ret"].get("Tags"):
        resource_translated["tags"] = ret_tag["ret"]["Tags"]
    result["ret"] = resource_translated

    return result
