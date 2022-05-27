from typing import Any
from typing import Dict
from typing import List

import boto3.resources.factory


async def update_attachments(
    hub,
    ctx,
    internet_gateway_name: str,
    before: boto3.resources.factory.ServiceResource.meta,
    vpc_id: List = None,
) -> Dict[str, Any]:
    """
    Updates attachments of internet gateway. 1. vpc_id is none then there will be no change in attachments. 2. vpc_id
    is empty then internet gateway will be detached if it is already attached to a vpc 3. vpc_id has one element then
    first detach will be performed if already attached to another vpc and the attach to new vpc. If attached vpc and
    passed in vpc are same then there will be no update to the attachments

    Args:
        hub:
        ctx:
        internet_gateway_name: Internet gateway name
        vpc_id: This list can contain only single element. This is ID of VPC to which internet gateway attaches.
        before: Contains current configuration for the resource

    Returns:
        {"result": True|False, "comment": "A message", "ret": Dict}

    """
    result = dict(comment=(), result=True, ret=None)
    already_attached_vpc_id = (
        before["Attachments"][0]["VpcId"] if before["Attachments"] else None
    )
    if vpc_id is None:
        result["ret"] = {"updated_vpc_id": [already_attached_vpc_id]}
        result["comment"] = (f"'No change in attachments for {internet_gateway_name}'",)
        return result
    updated_vpc_id = []
    if ctx.get("test", False):
        if len(vpc_id) > 0:
            updated_vpc_id = [vpc_id[0]]
    else:
        if vpc_id:
            # Attach to new vpc. First, detach if already attached to another vpc and then perform attach.
            if vpc_id[0] == already_attached_vpc_id:
                result["comment"] = (
                    f"'{internet_gateway_name}' is already attached to vpc '{already_attached_vpc_id}'",
                )
            else:
                try:
                    if already_attached_vpc_id:
                        ret = await hub.exec.boto3.client.ec2.detach_internet_gateway(
                            ctx,
                            InternetGatewayId=internet_gateway_name,
                            VpcId=already_attached_vpc_id,
                        )
                        result["result"] = ret["result"]
                        if not result["result"]:
                            result["comment"] = ret["comment"]
                            result["result"] = False
                            return result
                        result["comment"] = (
                            f"'{internet_gateway_name}' detached from vpc '{already_attached_vpc_id}'",
                        )
                    ret = await hub.exec.boto3.client.ec2.attach_internet_gateway(
                        ctx, InternetGatewayId=internet_gateway_name, VpcId=vpc_id[0]
                    )
                    result["result"] = ret["result"]
                    if not result["result"]:
                        result["comment"] = ret["comment"]
                        result["result"] = False
                        return result
                    result["comment"] = result["comment"] + (
                        f"'{internet_gateway_name}' attached to vpc '{vpc_id[0]}'",
                    )
                except hub.tool.boto3.exception.ClientError as e:
                    result["comment"] = (
                        result["comment"] + f"{e.__class__.__name__}: {e}"
                    )
                    result["result"] = False
        else:
            try:
                # When vpc_id is empty, detach from vpc if already attached
                if before["Attachments"]:
                    ret = await hub.exec.boto3.client.ec2.detach_internet_gateway(
                        ctx,
                        InternetGatewayId=internet_gateway_name,
                        VpcId=already_attached_vpc_id,
                    )
                    result["result"] = ret["result"]
                    if not result["result"]:
                        result["comment"] = ret["comment"]
                        result["result"] = False
                        return result
                    result["comment"] = (
                        f"'{internet_gateway_name}' detached from vpc '{already_attached_vpc_id}'",
                    )
                else:
                    result["comment"] = (
                        f"'{internet_gateway_name}' is already detached'",
                    )
            except hub.tool.boto3.exception.ClientError as e:
                result["comment"] = f"{e.__class__.__name__}: {e}"
                result["result"] = False
    result["ret"] = {"updated_vpc_id": updated_vpc_id}
    return result
