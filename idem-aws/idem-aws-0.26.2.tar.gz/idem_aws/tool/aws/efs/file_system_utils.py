from collections import OrderedDict
from typing import Any
from typing import Dict

"""
 Utility functions to support aws efs file system operations
"""


def convert_raw_file_system_to_present(
    hub, file_system: Dict[str, Any], backup_enabled: bool
) -> Dict[str, Any]:
    result = {}
    if file_system is None:
        return None

    resource_parameters = OrderedDict(
        {
            "PerformanceMode": "performance_mode",
            "Encrypted": "encrypted",
            "KmsKeyId": "kms_key_id",
            "CreationToken": "creation_token",
            "ThroughputMode": "throughput_mode",
            "ProvisionedThroughputInMibps": "provisioned_throughput_in_mibps",
            "AvailabilityZoneName": "availability_zone_name",
        }
    )

    tag_parameters = OrderedDict({"Key": "key", "Value": "value"})
    # Populate state parameters
    result["name"] = file_system.get("Name")
    result["resource_id"] = file_system.get("FileSystemId")

    for parameter_key, parameter_value in resource_parameters.items():
        if parameter_key in file_system:
            result[parameter_value] = file_system.get(parameter_key)

    # Special handling for backup
    result["backup"] = backup_enabled

    # Special handling for tags
    translated_tags = []
    for tag in file_system.get("Tags"):
        if tag.get("Key") == "aws:elasticfilesystem:default-backup":
            continue
        translated_tags.append(tag)
    result["tags"] = translated_tags
    return result


def is_throughput_mode_updated(
    hub,
    current_state: Dict[str, Any],
    desired_state: Dict[str, Any],
) -> bool:
    return current_state.get("throughput_mode") != desired_state.get(
        "throughput_mode"
    ) or (
        current_state.get("throughput_mode") == "provisioned"
        and current_state.get("provisioned_throughput_in_mibps")
        != desired_state.get("provisioned_throughput_in_mibps")
    )


def is_backup_enabled(hub, backup_result):
    return (
        True
        if backup_result["result"]
        and backup_result["ret"]["BackupPolicy"]["Status"] in ["ENABLED", "ENABLING"]
        else False
    )


def is_backup_policy_not_found(hub, backup_result):
    return bool(
        [item for item in backup_result["comment"] if item.startswith("PolicyNotFound")]
    )
