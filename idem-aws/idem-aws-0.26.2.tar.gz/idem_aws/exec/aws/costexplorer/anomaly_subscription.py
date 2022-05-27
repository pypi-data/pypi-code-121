from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List


async def update_anomaly_subscription(
    hub,
    ctx,
    before: Dict[str, Any],
    subscription_arn: str,
    threshold: float,
    frequency: str,
    monitor_arn_list: List,
    subscribers: List,
    subscription_name: str,
):
    """
    Updates the Anomaly Subscription
    Args:
        before: existing resource
        subscription_arn (Text) -- ARN of the subscription
        threshold (float) -- The dollar value that triggers a notification if the threshold is exceeded.
        frequency (Text) -- The frequency that anomaly reports are sent over email.
        monitor_arn_list (List) -- An Idem list of cost anomaly monitors.
        subscribers (List) -- A list of subscribers to notify.
        subscription_name: Name of the subscription

    Returns:
        {"result": True|False, "comment": A message Tuple, "ret": None}

    """
    result = dict(comment=(), result=True, ret=None)
    update_payload = {}

    resource_parameters = OrderedDict(
        {
            "Threshold": threshold,
            "Frequency": frequency,
            "SubscriptionName": subscription_name,
        }
    )

    if not hub.tool.aws.state_comparison_utils.are_lists_identical(
        monitor_arn_list,
        before.get("MonitorArnList"),
    ):
        update_payload["MonitorArnList"] = monitor_arn_list

    if not hub.tool.aws.state_comparison_utils.are_lists_identical(
        subscribers,
        before.get("Subscribers"),
    ):
        update_payload["Subscribers"] = subscribers

    for key, value in resource_parameters.items():
        if key in before.keys():
            if (value is not None) and value != before[key]:
                update_payload[key] = resource_parameters[key]

    if update_payload:
        if not ctx.get("test", False):
            update_ret = await hub.exec.boto3.client.ce.update_anomaly_subscription(
                ctx, SubscriptionArn=subscription_arn, **update_payload
            )
            if not update_ret["result"]:
                result["comment"] = result["comment"] + update_ret["comment"]
                result["result"] = False
                return result
        result["ret"] = {}
        result = update_result(result, update_payload)

    return result


def update_result(
    result: Dict[str, Any], update_payload: Dict[str, Any]
) -> Dict[str, Any]:
    parameters = OrderedDict(
        {
            "MonitorArnList": "monitor_arn_list",
            "Subscribers": "subscribers",
            "Threshold": "threshold",
            "Frequency": "frequency",
            "SubscriptionName": "subscription_name",
        }
    )

    for raw_parameter, present_parameter in parameters.items():
        if raw_parameter in update_payload:
            result["ret"][present_parameter] = update_payload[raw_parameter]
            result["comment"] = result["comment"] + (
                f"Update {present_parameter}: {update_payload[raw_parameter]}",
            )
    return result
