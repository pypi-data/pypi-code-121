from typing import Dict
from typing import List


def get_hosted_zone_with_filters(
    hub,
    raw_hosted_zones: Dict,
    hosted_zone_name: str = None,
    private_zone: bool = None,
    vpc_id: str = None,
    tags: List = None,
):
    """
    Returns the hosted_zone with the specified filters, if it is available.

    Args:
        raw_hosted_zones(Dict): Dict of all the described hosted_zones
        hosted_zone_name(string, optional): Domain name of hosted_zone to filter.
        private_zone(bool, optional): Bool argument to specify a private hosted_zone. One of the filter option for hosted_zone
        vpc_id(string, optional): The vpc_id associated with the hosted_zone. One of the filter option for hosted_zone
        tags(List, optional): Tags of the hosted_zone. One of the filter option for hosted_zone

    """
    result = dict(comment=(), result=True, ret=None)
    hosted_zones = raw_hosted_zones["HostedZones"]

    # filter_hosted_zones() returns True if all the filters match for a hosted_zone, and it is added to the list
    filtered_hosted_zones = list(
        filter(
            lambda x: filter_hosted_zones(
                x, hosted_zone_name, private_zone, vpc_id, tags
            ),
            hosted_zones,
        )
    )

    if not filtered_hosted_zones:
        result["comment"] = (
            f"Unable to find aws.route53.hosted_zone resource with given filters",
        )
        return result
    resource_id = filtered_hosted_zones[0].get("Id").split("/")[-1]
    if len(filtered_hosted_zones) > 1:
        result["comment"] = (
            f"More than one aws.route53.hosted_zone resource was found with given filters. Use resource {resource_id}",
        )
    else:
        result["comment"] = (
            f"Found this aws.route53.hosted_zone resource {resource_id} with given filters",
        )
    # Building the format in which hosted_zone conversion_utils takes the hosted_zone resource
    res_hosted_zone = {
        "ret": {
            "HostedZone": filtered_hosted_zones[0],
            "VPCs": filtered_hosted_zones[0].get("VPCs"),
            "DelegationSet": filtered_hosted_zones[0].get("DelegationSet"),
        },
        "tags": filtered_hosted_zones[0].get("Tags"),
    }
    result["ret"] = res_hosted_zone
    return result


def filter_hosted_zones(
    hosted_zone: Dict,
    hosted_zone_name: str = None,
    private_zone: bool = None,
    vpc_id: str = None,
    tags: List = None,
):
    """
    Returns True if the hosted_zone checks all the filters provided or return False

    Args:
        hosted_zone(Dict): The described hosted_zone
        hosted_zone_name(string, optional): Domain name of hosted_zone to filter.
        private_zone(bool, optional): Bool argument to specify a private hosted_zone. One of the filter option for hosted_zone
        vpc_id(string, optional): The vpc_id associated with the hosted_zone. One of the filter option for hosted_zone
        tags(List, optional): Tags of the hosted_zone. One of the filter option for hosted_zone

    """
    # Return True if all the provided filters match or return False.

    if hosted_zone_name:
        if hosted_zone["Name"] != hosted_zone_name:
            return False

    if private_zone is not None:
        if hosted_zone["Config"]["PrivateZone"] != private_zone:
            return False

    if vpc_id:
        found = False
        if hosted_zone["VPCs"]:
            for vpc in hosted_zone["VPCs"]:
                if vpc["VPCId"] == vpc_id:
                    found = True
                    break
            if not found:
                return False

    # Checking if all the tags in the filter match with the tags present in the hosted_zone.If not we return False
    if tags:
        tags2 = hosted_zone.get("Tags")
        if tags2 is None:
            return False
        tags2_map = {tag.get("Key"): tag for tag in tags2}
        for tag in tags:
            if tag["Key"] not in tags2_map or (
                tags2_map.get(tag["Key"]).get("Value") != tag["Value"]
            ):
                return False

    return True
