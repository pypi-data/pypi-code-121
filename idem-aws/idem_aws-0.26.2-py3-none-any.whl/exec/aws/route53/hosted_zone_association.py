from typing import Any
from typing import Dict


async def is_hosted_zone_associated_to_vpc(
    hub, ctx, zone_id: str, vpc_id: str, vpc_region: str
) -> Dict[str, Any]:
    """
    Check if a vpc is attached to a hosted zone

    Args:
        hub: The redistributed pop central hub.
        ctx: A dict with the keys/values for the execution of the Idem run located in
        `hub.idem.RUNS[ctx['run_name']]`.
        zone_id: The ID of the hosted zone to be associated with.
        vpc_id: The ID of the vpc you want to associate.
        vpc_region: The AWS region where the vpc belongs to.

    Returns:
        {"result": True|False, "comment": (f"A message",), "ret": None}
    """
    result = dict(comment=(), result=True, ret=None)
    ret_list = await hub.exec.boto3.client.route53.list_hosted_zones_by_vpc(
        ctx, VPCId=vpc_id, VPCRegion=vpc_region
    )
    if ret_list["result"]:
        if ret_list["ret"].get("HostedZoneSummaries"):
            associated_zone_summaries = ret_list["ret"].get("HostedZoneSummaries")
            hosted_zone_list = [
                hosted_zone_summary.get("HostedZoneId")
                for hosted_zone_summary in associated_zone_summaries
            ]
            if zone_id in hosted_zone_list:
                result["ret"] = {"HostedZone": zone_id}
    else:
        result["result"] = False
        result["comment"] = ret_list["comment"]
    return result
