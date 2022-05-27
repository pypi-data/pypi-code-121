from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util function to convert raw resource state from AWS Launch Configuration to present input format.
"""


def convert_raw_launch_configuration_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("LaunchConfigurationName")
    resource_parameters = OrderedDict(
        {
            "LaunchConfigurationName": "name",
            "ImageId": "image_id",
            "KeyName": "key_name",
            "SecurityGroups": "security_groups",
            "ClassicLinkVPCId": "classic_link_vpc_id",
            "ClassicLinkVPCSecurityGroups": "classic_link_vpc_security_groups",
            "UserData": "user_data",
            "InstanceId": "instance_id",
            "InstanceType": "instance_type",
            "KernelId": "kernel_id",
            "RamdiskId": "ramdisk_id",
            "BlockDeviceMappings": "block_device_mappings",
            "InstanceMonitoring": "instance_monitoring",
            "SpotPrice": "spot_price",
            "IamInstanceProfile": "iam_instance_profile",
            "EbsOptimized": "ebs_optimized",
            "AssociatePublicIpAddress": "associate_public_ip_address",
            "PlacementTenancy": "placement_tenancy",
            "MetadataOptions": "metadata_options",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource and raw_resource.get(parameter_raw):
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
