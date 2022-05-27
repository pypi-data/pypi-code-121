from collections import OrderedDict
from typing import Any
from typing import Dict

from deepdiff import DeepDiff

"""
 Utility functions to support aws auto scaling group operations
"""


def convert_raw_auto_scaling_group_to_present(
    hub, auto_scaling_group: Dict[str, Any]
) -> Dict[str, Any]:
    result = {}
    if auto_scaling_group is None:
        return result

    resource_parameters = OrderedDict(
        {
            "LaunchConfigurationName": "launch_configuration_name",
            "LaunchTemplate": "launch_template",
            "InstanceId": "instance_id",
            "MinSize": "min_size",
            "MaxSize": "max_size",
            "DesiredCapacity": "desired_capacity",
            "DefaultCooldown": "default_cooldown",
            "AvailabilityZones": "availability_zones",
            "LoadBalancerNames": "load_balancer_names",
            "TargetGroupARNs": "target_group_ar_ns",
            "HealthCheckType": "health_check_type",
            "HealthCheckGracePeriod": "health_check_grace_period",
            "PlacementGroup": "placement_group",
            "MixedInstancesPolicy": "mixed_instances_policy",
            "VPCZoneIdentifier": "vpc_zone_identifier",
            "TerminationPolicies": "termination_policies",
            "NewInstancesProtectedFromScaleIn": "new_instances_protected_from_scale_in",
            "CapacityRebalance": "capacity_rebalance",
            "LifecycleHookSpecificationList": "lifecycle_hook_specification_list",
            "Tags": "tags",
            "MaxInstanceLifetime": "max_instance_lifetime",
            "DesiredCapacityType": "desired_capacity_type",
        }
    )

    tag_parameters = OrderedDict(
        {"Key": "key", "Value": "value", "PropagateAtLaunch": "propagate_at_launch"}
    )

    result = {
        "name": auto_scaling_group.get("AutoScalingGroupName"),
        "resource_id": auto_scaling_group.get("AutoScalingGroupName"),
    }
    for parameter_key, parameter_value in resource_parameters.items():
        if parameter_key in auto_scaling_group:
            result[parameter_value] = auto_scaling_group.get(parameter_key)

    # Special handling for tags
    translated_tags = []
    for tag in auto_scaling_group.get("Tags"):
        new_tag = {}
        for parameter_key, parameter_value in tag_parameters.items():
            new_tag[parameter_value] = tag.get(parameter_key)
        translated_tags.append(new_tag)
    result["tags"] = translated_tags
    return result


def is_auto_scaling_group_updated(
    hub,
    current_state: Dict[str, Any],
    desired_state: Dict[str, Any],
) -> bool:
    if not current_state:
        return True
    list_parameters = [
        "availability_zones",
        "load_balancer_names",
        "target_group_ar_ns",
        "termination_policies",
        "lifecycle_hook_specification_list",
    ]
    dict_parameters = ["launch_template", "mixed_instances_policy"]
    exclusion_list = ["tags"]
    for parameter in desired_state:
        if parameter in exclusion_list:
            continue
        if desired_state.get(parameter) is None:
            # To favour optional parameters of resource
            continue
        if parameter == "vpc_zone_identifier":
            current_zone_ids = (
                current_state.get("vpc_zone_identifier").split(",")
                if current_state.get("vpc_zone_identifier")
                else []
            )
            desired_zone_ids = (
                desired_state.get("vpc_zone_identifier").split(",")
                if desired_state.get("vpc_zone_identifier")
                else []
            )
            if not hub.tool.aws.state_comparison_utils.are_lists_identical(
                current_zone_ids, desired_zone_ids
            ):
                return True
            else:
                continue
        if parameter in list_parameters:
            if not hub.tool.aws.state_comparison_utils.are_lists_identical(
                current_state.get(parameter), desired_state.get(parameter)
            ):
                return True
            else:
                continue
        if parameter in dict_parameters:
            if DeepDiff(
                current_state.get(parameter),
                desired_state.get(parameter),
                ignore_order=True,
            ):
                return True
            else:
                continue
        if current_state.get(parameter) != desired_state.get(parameter):
            return True
    return False


def convert_present_tags_to_raw_tags(
    hub, resource_id, tags: [Dict[str, Any]]
) -> [Dict[str, Any]]:
    result = []
    for tag in tags:
        result.append(convert_tag_to_raw(resource_id, tag))
    return result


def convert_tag_to_raw(resource_id: str, tag: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ResourceType": "auto-scaling-group",
        "ResourceId": resource_id,
        "Key": tag.get("key"),
        "PropagateAtLaunch": tag.get("propagate_at_launch"),
        "Value": tag.get("value"),
    }
