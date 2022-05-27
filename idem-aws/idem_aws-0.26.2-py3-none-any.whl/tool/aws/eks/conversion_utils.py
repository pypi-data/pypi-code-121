from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util functions to convert raw resource state from AWS EKS to present input format.
"""


def convert_raw_addon_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("addonName")
    resource_parameters = OrderedDict(
        {
            "clusterName": "cluster_name",
            "addonArn": "addon_arn",
            "addonVersion": "addon_version",
            "releaseVersion": "release_version",
            "status": "status",
            "clientRequestToken": "client_request_token",
            "serviceAccountRoleArn": "service_account_role_arn",
            "tags": "tags",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = (
                raw_resource.get(parameter_raw).copy()
                if isinstance(raw_resource.get(parameter_raw), dict)
                else raw_resource.get(parameter_raw)
            )

    return resource_translated


def convert_raw_cluster_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("name")
    resource_parameters = OrderedDict(
        {
            "roleArn": "role_arn",
            "arn": "arn",
            "status": "status",
            "version": "version",
            "resourcesVpcConfig": "resources_vpc_config",
            "kubernetesNetworkConfig": "kubernetes_network_config",
            "logging": "logging",
            "encryptionConfig": "encryption_config",
            "clientRequestToken": "client_request_token",
            "tags": "tags",
        }
    )

    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = (
                raw_resource.get(parameter_raw).copy()
                if isinstance(raw_resource.get(parameter_raw), dict)
                else raw_resource.get(parameter_raw)
            )

    return resource_translated


def convert_raw_nodegroup_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("nodegroupName")
    resource_parameters = OrderedDict(
        {
            "clusterName": "cluster_name",
            "nodegroupArn": "nodegroup_arn",
            "version": "version",
            "releaseVersion": "release_version",
            "status": "status",
            "capacityType": "capacity_type",
            "scalingConfig": "scaling_config",
            "instanceTypes": "instance_types",
            "subnets": "subnets",
            "remoteAccess": "remote_access",
            "amiType": "ami_type",
            "nodeRole": "node_role",
            "labels": "labels",
            "taints": "taints",
            "diskSize": "disk_size",
            "updateConfig": "update_config",
            "launchTemplate": "launch_template",
            "tags": "tags",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = (
                raw_resource.get(parameter_raw).copy()
                if isinstance(raw_resource.get(parameter_raw), dict)
                else raw_resource.get(parameter_raw)
            )

    return resource_translated


def convert_raw_fargate_profile_to_present(
    hub, raw_resource: Dict[str, Any]
) -> Dict[str, Any]:
    describe_parameters = OrderedDict(
        {
            "clusterName": "cluster_name",
            "podExecutionRoleArn": "pod_execution_role_arn",
            "status": "status",
        }
    )
    name = raw_resource.get("fargateProfileName")
    translated_resource = {"name": name, "resource_id": name}
    for parameter_old, parameter_new in describe_parameters.items():
        if parameter_old in raw_resource:
            translated_resource[parameter_new] = raw_resource.get(parameter_old)
        if "subnets" in raw_resource:
            translated_resource["subnets"] = raw_resource.get("subnets").copy()
        if "selectors" in raw_resource:
            translated_resource["selectors"] = raw_resource.get("selectors").copy()
        if "tags" in raw_resource:
            translated_resource["tags"] = raw_resource.get("tags").copy()
    return translated_resource
