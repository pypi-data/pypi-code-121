from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List


def convert_raw_resource_record_to_present(
    hub,
    hosted_zone_id: str,
    raw_resource: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Given an object state from aws, this function creates a translated resource object in response.

    Args:
        hub: The redistributed pop central hub.
        hosted_zone_id (Text): hosted zone id which owns this resource record set.
        raw_resource (Dict): The dictionary object from where the raw state of resource needs to be translated.

    Returns:
        Idem representation of the resource record.
    """

    name = raw_resource["Name"]
    record_type = raw_resource["Type"]
    if hosted_zone_id.startswith("/hostedzone/"):
        canonical_hosted_zone_id = hosted_zone_id
    else:
        canonical_hosted_zone_id = f"/hostedzone/{hosted_zone_id}"
    resource_id = hub.tool.aws.route53.resource_record_utils.compose_resource_id(
        canonical_hosted_zone_id, name, record_type
    )

    resource_translated = {
        "name": name,
        "resource_id": resource_id,
        "hosted_zone_id": canonical_hosted_zone_id,
        "record_type": record_type,
    }

    if "TTL" in raw_resource:
        resource_translated["ttl"] = int(raw_resource["TTL"])
    if "ResourceRecords" in raw_resource:
        resource_translated["resource_records"] = []
        for resource_record in raw_resource.get("ResourceRecords"):
            resource_translated["resource_records"].append(resource_record["Value"])
    if "AliasTarget" in raw_resource:
        resource_translated["alias_target"] = {
            "hosted_zone_id": raw_resource["AliasTarget"]["HostedZoneId"],
            "dns_name": raw_resource["AliasTarget"]["DNSName"],
            "evaluate_target_health": raw_resource["AliasTarget"][
                "EvaluateTargetHealth"
            ],
        }
    return resource_translated


def convert_raw_hosted_zone_to_present(
    hub,
    raw_resource: Dict[str, Any],
    idem_resource_name: str = None,
    tags: List = None,
) -> Dict[str, Any]:
    """
    Given an object state from aws, this function creates a translated resource object in response.

    Args:
        hub: required for functions in hub
        raw_resource (Dict): The dictionary object from where the raw state of resource needs to be translated.
        idem_resource_name (Text): The name of the Idem resource
        tags (List): The tags.
                * Key (Text) -- The key of the tag. Tag keys are case-sensitive and accept a maximum of 127 Unicode characters. May not begin with aws: .
                * Value (Text) -- The value of the tag. Tag values are case-sensitive and accept a maximum of 255 Unicode characters.


    Returns: Dict[str, Any]
    """

    hosted_zone = raw_resource["ret"].get("HostedZone")
    vpcs = raw_resource["ret"].get("VPCs")
    delegation_set = raw_resource["ret"].get("DelegationSet")
    resource_id = hosted_zone.get("Id")
    resource_parameters = OrderedDict(
        {
            "Name": "hosted_zone_name",
            "CallerReference": "caller_reference",
        }
    )
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id.split("/")[-1],
    }
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in hosted_zone:
            resource_translated[parameter_present] = hosted_zone.get(parameter_raw)
    resource_translated["config"] = hosted_zone.get("Config").copy()
    if vpcs is not None:
        resource_translated["vpcs"] = vpcs
    if delegation_set is not None:
        resource_translated["delegation_set"] = delegation_set.copy()
    resource_translated["tags"] = tags

    return resource_translated


def convert_raw_zone_association_to_present(
    hub,
    hosted_zone_id: str,
    vpc_id: str,
    vpc_region: str,
    idem_resource_name: str = None,
    comment: str = None,
) -> Dict[str, Any]:
    """
    Given an object state from aws, this function creates a translated resource object in response.

    Args:
        hub: required for functions in hub
        hosted_zone_id(Text): The id of the hosted zone
        vpc_id(Text): The vpc id for association with hosted zone
        vpc_region(Text): The AWS region where the vpc belongs to.
        idem_resource_name (Text): name of resource
        comment (Text, optional): The comment for hosted zone association.

    Returns: Dict[str, Any]
    """
    resource_id = f"{hosted_zone_id}:{vpc_id}:{vpc_region}"
    translated_resource = {
        "resource_id": resource_id,
        "name": idem_resource_name,
        "zone_id": hosted_zone_id,
        "vpc_id": vpc_id,
        "vpc_region": vpc_region,
        "comment": comment if comment else None,
    }

    return translated_resource
