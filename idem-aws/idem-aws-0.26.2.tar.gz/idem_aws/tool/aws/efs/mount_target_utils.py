from collections import OrderedDict
from typing import Any
from typing import Dict

"""
 Utility functions to support aws efs file-system mount target operations
"""


def convert_raw_mount_target_to_present(
    hub, ctx, mount_target: Dict[str, Any], security_groups: []
) -> Dict[str, Any]:
    result = {}
    if mount_target is None:
        return None

    resource_parameters = OrderedDict(
        {
            "FileSystemId": "file_system_id",
            "SubnetId": "subnet_id",
            "IpAddress": "ip_address",
        }
    )
    # Populate state parameters
    result["name"] = mount_target.get("MountTargetId")
    result["resource_id"] = mount_target.get("MountTargetId")
    result["security_groups"] = security_groups

    for parameter_key, parameter_value in resource_parameters.items():
        if parameter_key in mount_target:
            result[parameter_value] = mount_target.get(parameter_key)

    return result
