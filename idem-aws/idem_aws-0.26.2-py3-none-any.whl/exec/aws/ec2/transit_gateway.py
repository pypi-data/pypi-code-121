from typing import Any
from typing import Dict

from dict_tools import differ


async def update_options(
    hub,
    ctx,
    transit_gateway_id: str,
    old_description: str,
    new_description: str,
    old_options: Dict[str, Any],
    new_options: Dict[str, Any],
):
    """
    Update options and description of a transit_gateway. This function compares the existing(old) options or description
    and the new options or description. TransitGatewayCidrBlocks that are in the new options but not in the old
    TransitGatewayCidrBlocks will be associated to transit gateway. TransitGatewayCidrBlocks that are in the
    options but not in the new options will be disassociated from transit gateway.

    Args:
        hub:
        ctx:
        transit_gateway_id(Text): The AWS resource id of the existing transit gateway
        old_description(string):  description of existing transit gateway
        new_description(string): new description to update
        old_options(dict): options of existing transit gateway
        new_options(dict): options to be updated

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """
    result = dict(comment=(), result=True, ret=None)
    diff_in_options = differ.deep_diff(old_options, new_options)
    if old_description == new_description and (
        not diff_in_options or new_options is None
    ):
        result["comment"] = (f"no changes to update {transit_gateway_id}",)
        return result
    modify_options = None
    if new_options is not None:
        modify_supported_options = [
            "VpnEcmpSupport",
            "DnsSupport",
            "AutoAcceptSharedAttachments",
            "DefaultRouteTableAssociation",
            "AssociationDefaultRouteTableId",
            "DefaultRouteTablePropagation",
            "PropagationDefaultRouteTableId",
        ]
        modify_options = {}
        for modify_option in modify_supported_options:
            if new_options.get(modify_option) is not None:
                modify_options[modify_option] = new_options.get(modify_option)

        old_cidr_blocks = old_options.get("TransitGatewayCidrBlocks", [])
        new_cidr_blocks = new_options.get("TransitGatewayCidrBlocks", [])
        modify_options["AddTransitGatewayCidrBlocks"] = list(
            set(new_cidr_blocks).difference(old_cidr_blocks)
        )
        modify_options["RemoveTransitGatewayCidrBlocks"] = list(
            set(old_cidr_blocks).difference(new_cidr_blocks)
        )
    if not ctx.get("test", False):
        ret = await hub.exec.boto3.client.ec2.modify_transit_gateway(
            ctx,
            TransitGatewayId=transit_gateway_id,
            Description=new_description,
            Options=modify_options,
        )
        if not ret.get("result"):
            result["comment"] = ret["comment"]
            result["result"] = False
            return result
    result["comment"] = (f"Updated transit gateway {transit_gateway_id}",)
    result["ret"] = {"description": new_description, "options": new_options}

    return result


async def get_transit_gateway_by_id(hub, ctx, transit_gateway_id):
    ret = {}
    result = dict(comment=(), result=True, ret=None)
    before = await hub.exec.boto3.client.ec2.describe_transit_gateways(
        ctx, TransitGatewayIds=[transit_gateway_id]
    )
    result["result"] = before["result"]
    result["comment"] = before["comment"]
    if before["result"]:
        for transit_gateway in before["ret"]["TransitGateways"]:
            ret = transit_gateway
    result["ret"] = ret
    return result
