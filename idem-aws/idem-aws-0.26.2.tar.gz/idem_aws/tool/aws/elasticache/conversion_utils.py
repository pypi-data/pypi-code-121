from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util functions to convert raw resource state from AWS Elasticache to present input format.
"""


async def convert_raw_elasticache_subnet_to_present(
    hub,
    ctx,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
) -> Dict[str, Any]:
    """
    Return converted raw resource state from AWS Elasticache subnet group to required input format for present.

     Args:
        raw_resource(Text): resource obtained from describe API
        idem_resource_name(Text): name of idem resource

    Return: Dict[str, Any]
    """
    result = dict(comment=(), result=True, ret=None)
    resource_id = raw_resource.get("CacheSubnetGroupName")
    resource_parameters = OrderedDict(
        {
            "CacheSubnetGroupDescription": "cache_subnet_group_description",
            "ARN": "arn",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    if raw_resource.get("Subnets"):
        subnet_ids_list = []
        for subnet in raw_resource.get("Subnets"):
            if "SubnetIdentifier" in subnet:
                subnet_ids_list.append(subnet.get("SubnetIdentifier"))
        resource_translated["subnet_ids"] = subnet_ids_list

    if raw_resource.get("ARN"):
        tags = await hub.exec.boto3.client.elasticache.list_tags_for_resource(
            ctx, ResourceName=raw_resource.get("ARN")
        )
        result["result"] = tags["result"]
        if tags["result"] and tags.get("ret"):
            resource_translated["tags"] = tags["ret"]["TagList"]
        if not result["result"]:
            result["comment"] = result["comment"] + tags["comment"]
    result["ret"] = resource_translated
    return result


async def convert_raw_elasticache_parameter_group_to_present(
    hub,
    ctx,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
) -> Dict[str, Any]:
    """
    Return converted raw resource state from AWS Elasticache parameter group to required input format for present.

     Args:
        raw_resource(Text): resource obtained from describe API
        idem_resource_name(Text): name of idem resource

    Return: Dict[str, Any]
    """
    result = dict(comment=(), result=True, ret=None)
    resource_id = raw_resource.get("CacheParameterGroupName")
    resource_parameters = OrderedDict(
        {
            "CacheParameterGroupFamily": "cache_parameter_group_family",
            "Description": "description",
            "ARN": "arn",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    if raw_resource.get("ARN"):
        tags = await hub.exec.boto3.client.elasticache.list_tags_for_resource(
            ctx, ResourceName=raw_resource.get("ARN")
        )
        result["result"] = tags["result"]
        if tags["result"] and tags.get("ret"):
            resource_translated["tags"] = tags["ret"]["TagList"]
        if not tags["result"]:
            result["comment"] = result["comment"] + tags["comment"]

    ret_parameters = await hub.exec.boto3.client.elasticache.describe_cache_parameters(
        ctx, CacheParameterGroupName=resource_id
    )
    result["result"] = result["result"] and ret_parameters["result"]
    if not ret_parameters["result"]:
        result["comment"] = result["comment"] + ret_parameters["comment"]
    elif ret_parameters["result"] and ret_parameters.get("ret"):
        updated_parameter_list = []
        for parameter in ret_parameters["ret"].get("Parameters"):
            parameter_list = {}
            if "ParameterName" in parameter:
                parameter_list["ParameterName"] = parameter.get("ParameterName")
            if "ParameterValue" in parameter:
                parameter_list["ParameterValue"] = parameter.get("ParameterValue")
            updated_parameter_list.append(parameter_list)
        resource_translated["parameter_name_values"] = updated_parameter_list

    result["ret"] = resource_translated
    return result
