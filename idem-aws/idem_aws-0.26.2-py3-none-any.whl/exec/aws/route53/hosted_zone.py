from typing import Any
from typing import Dict


async def get_all_hosted_zones(hub, ctx) -> Dict[str, Any]:
    """
    Describes all the hosted zones available.

    Args:
        hub:
        ctx:

    Returns:
        {"result": True|False, "comment": "A message Tuple", "ret": None}
    """
    result = dict(comment=(), result=True, ret=None)
    hosted_zones = []
    ret = await hub.exec.boto3.client.route53.list_hosted_zones(ctx)
    if not ret["result"]:
        result["result"] = ret["result"]
        result["comment"] = ret["comment"]
        return result
    for hosted_zone in ret["ret"]["HostedZones"]:
        resource_id = hosted_zone.get("Id")
        ret = await hub.exec.boto3.client.route53.get_hosted_zone(ctx, Id=resource_id)
        temp_hosted_zone = ret["ret"]["HostedZone"]

        if ret["ret"].get("VPCs"):
            temp_hosted_zone["VPCs"] = ret["ret"].get("VPCs")
        if ret["ret"].get("DelegationSet"):
            temp_hosted_zone["DelegationSet"] = ret["ret"].get("DelegationSet")

        tags_ret = await hub.exec.boto3.client.route53.list_tags_for_resource(
            ctx, ResourceType="hostedzone", ResourceId=resource_id.split("/")[-1]
        )
        if tags_ret["result"] and tags_ret["ret"].get("ResourceTagSet").get("Tags"):
            temp_hosted_zone["Tags"] = tags_ret["ret"]["ResourceTagSet"].get("Tags")
        hosted_zones.append(temp_hosted_zone)

    result["ret"] = {"HostedZones": hosted_zones}
    return result
