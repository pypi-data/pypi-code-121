from typing import Any
from typing import Dict
from typing import List


async def update_transit_gateway_vpc_attachment(
    hub,
    ctx,
    transit_gateway_vpc_attachment_id: str,
    old_subnets: List,
    new_subnets: List,
    old_options: Dict[str, Any],
    new_options: Dict[str, Any],
):
    """
    Update options and subnets of a transit_gateway vpc attachment. This function compares the existing(old) options
    or subnets and the new options or subnets. subnets that are in the new new_subnets but not in the
    old_subnets will be associated to transit gateway vpc attachment. subnets that are in the
    old_subnets but not in the new_subnets will be disassociated from transit gateway vpc attachment.

    Args:
        hub:
        ctx:
        transit_gateway_vpc_attachment_id(Text): The AWS resource id of the existing transit gateway vpc attachment
        old_subnets(List):  subnets of existing transit gateway vpc attachment
        new_subnets(List): new subnets to update
        old_options(dict): options of existing transit gateway vpc attachment
        new_options(dict): options to be updated

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """
    result = dict(comment=(), result=True, ret=None)
    if set(old_subnets) == set(new_subnets) and (
        new_options is None or old_options == new_options
    ):
        result["comment"] = (f"no changes to update",)
        return result

    subnets_to_add = list(set(new_subnets).difference(old_subnets))
    subnets_to_remove = list(set(old_subnets).difference(new_subnets))

    if ctx.get("test", False):
        result["comment"] = result["comment"] + (
            f"Would update transit gateway vpc attachment {transit_gateway_vpc_attachment_id}",
        )
    else:
        ret = await hub.exec.boto3.client.ec2.modify_transit_gateway_vpc_attachment(
            ctx,
            TransitGatewayAttachmentId=transit_gateway_vpc_attachment_id,
            AddSubnetIds=subnets_to_add,
            RemoveSubnetIds=subnets_to_remove,
            Options=new_options,
        )
        result["result"] = ret["result"]
        if not ret["result"]:
            result["comment"] = result["comment"] + ret["comment"]
            return result
        result["comment"] = result["comment"] + (
            f"Updated transit gateway vpc attachment {transit_gateway_vpc_attachment_id}",
        )
    result["ret"] = {
        "subnet_ids": new_subnets,
        "options": new_options,
    }
    return result


async def get_transit_gateway_vpc_attachment_by_id(
    hub, ctx, transit_gateway_vpc_attachment_id
):
    ret = {}
    result = dict(comment=(), result=True, ret=None)
    before = await hub.exec.boto3.client.ec2.describe_transit_gateway_vpc_attachments(
        ctx, TransitGatewayAttachmentIds=[transit_gateway_vpc_attachment_id]
    )
    result["result"] = before["result"]
    result["comment"] = before["comment"]
    if before["result"]:
        for transit_gateway_vpc_attachment in before["ret"][
            "TransitGatewayVpcAttachments"
        ]:
            ret = transit_gateway_vpc_attachment
    result["ret"] = ret
    return result
