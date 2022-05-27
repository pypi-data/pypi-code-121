from collections import OrderedDict
from typing import Any
from typing import Dict


def is_subscription_filter_updated(
    hub,
    current_state: Dict[str, Any],
    desired_state: Dict[str, Any],
) -> bool:
    for param in desired_state:
        # For optional parameters of resource
        if desired_state.get(param) is None:
            continue
        # Checking if the str params are different
        if desired_state.get(param) != current_state.get(param):
            return True
    return False


def convert_raw_subscription_filter_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_parameters = OrderedDict(
        {
            "logGroupName": "log_group_name",
            "filterName": "name",
            "filterPattern": "filter_pattern",
            "destinationArn": "destination_arn",
            "roleArn": "role_arn",
            "distribution": "distribution",
        }
    )
    resource_id = raw_resource.get("filterName")
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)
    return resource_translated
