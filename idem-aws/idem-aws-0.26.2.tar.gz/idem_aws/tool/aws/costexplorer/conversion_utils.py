from collections import OrderedDict
from typing import Any
from typing import Dict


def convert_raw_monitor_to_present(
    hub, ctx, raw_resource: Dict[str, Any], idem_resource_name: str
) -> Dict[str, Any]:
    resource_id = raw_resource.get("MonitorArn")
    resource_parameters = OrderedDict(
        {
            "MonitorSpecification": "monitor_specification",
            "MonitorDimension": "monitor_dimension",
            "MonitorType": "monitor_type",
            "MonitorName": "monitor_name",
        }
    )

    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
    }
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated


def convert_raw_subscription_to_present(
    hub, ctx, raw_resource: Dict[str, Any], idem_resource_name: str
) -> Dict[str, Any]:
    resource_id = raw_resource.get("SubscriptionArn")
    resource_parameters = OrderedDict(
        {
            "MonitorArnList": "monitor_arn_list",
            "Subscribers": "subscribers",
            "Threshold": "threshold",
            "Frequency": "frequency",
            "SubscriptionName": "subscription_name",
        }
    )

    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
