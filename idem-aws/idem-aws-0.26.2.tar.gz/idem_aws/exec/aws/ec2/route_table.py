from typing import List


async def update_associations_routes(
    hub,
    ctx,
    route_table_id: str,
    old_routes: List = None,
    new_routes: List = None,
    old_associations: List = None,
    new_associations: List = None,
    old_propagating_vgws: List = None,
    new_propagating_vgws: List = None,
):
    """
    Update associations, routes and route propagations of a route table. This function compares the existing(old)
    associations or routes or route propagations of route table and the new associations or routes or route propagations.
    associations or routes or route propagations that are in the new route table but not in the old
    route table will be associated to route table. associations or routes or route propagations that are in the
    old route table  but not in the new route table will be disassociated from transit route table.

    Args:
        hub:
        ctx:
        route_table_id(Text): The AWS resource id of the existing route table
        old_routes(List):  routes of existing route table
        new_routes(List): new routes to update
        old_associations(List): associations of existing route table
        new_associations(List): new associations to be updated
        old_propagating_vgws(List): propagating virtual gateways of existing route table
        new_propagating_vgws(List): new propagating virtual gateways to be updated

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """
    result = dict(comment=(), result=True, ret=None)

    # compare old_routes and new_routes and update if routes are modified
    if new_routes is []:
        result["result"] = False
        result["comment"] = (
            "Route Table routes cannot be None. There should be at least one route in Route Table",
        )
        return result
    elif new_routes is not None:
        routes_to_modify = (
            hub.tool.aws.ec2.route_table_utils.get_route_table_routes_modifications(
                old_routes, new_routes
            )
        )
        if not routes_to_modify["result"]:
            result["comment"] = routes_to_modify["comment"]
            result["result"] = False
            return result
        routes_to_add = routes_to_modify["routes_to_add"]
        routes_to_delete = routes_to_modify["routes_to_delete"]
        routes_to_replace = routes_to_modify["routes_to_replace"]

        if not ctx.get("test", False):
            if routes_to_delete:
                for route_to_delete in routes_to_delete:
                    ret = await hub.exec.boto3.client.ec2.delete_route(
                        ctx, RouteTableId=route_table_id, **route_to_delete
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + ret["comment"]
                        result["result"] = False
                        return result
                result["comment"] = result["comment"] + (
                    f"Deleted Routes: {routes_to_delete}, ",
                )
            if routes_to_replace:
                for route_to_replace in routes_to_replace:
                    ret = await hub.exec.boto3.client.ec2.replace_route(
                        ctx, RouteTableId=route_table_id, **route_to_replace
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + ret["comment"]
                        result["result"] = False
                        return result
                result["comment"] = result["comment"] + (
                    f"Replace Routes: {routes_to_replace}, ",
                )
            if routes_to_add:
                for route_to_add in routes_to_add:
                    ret = await hub.exec.boto3.client.ec2.create_route(
                        ctx, RouteTableId=route_table_id, **route_to_add
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + ret["comment"]
                        result["result"] = False
                        return result
                result["comment"] = result["comment"] + (
                    f"Added Routes: {routes_to_add}, ",
                )
    # If associations are None, we'll skip updating associations.
    if new_associations is not None:
        # compare old associations and new associations and update if associations are modified
        associations_to_modify = hub.tool.aws.ec2.route_table_utils.get_route_table_associations_modifications(
            old_associations, new_associations
        )
        if not associations_to_modify["result"]:
            result["comment"] = result["comment"] + associations_to_modify["comment"]
            return result
        associations_to_add = associations_to_modify["associations_to_add"]
        associations_to_delete = associations_to_modify["associations_to_delete"]

        if not ctx.get("test", False):
            if associations_to_delete:
                for association_to_delete in associations_to_delete:
                    ret = await hub.exec.boto3.client.ec2.disassociate_route_table(
                        ctx, **association_to_delete
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + ret["comment"]
                        result["result"] = False
                        return result
                result["comment"] = result["comment"] + (
                    f"Deleted Associations: {associations_to_delete}, ",
                )
            if associations_to_add:
                for association_to_add in associations_to_add:
                    ret = await hub.exec.boto3.client.ec2.associate_route_table(
                        ctx, RouteTableId=route_table_id, **association_to_add
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + ret["comment"]
                        result["result"] = False
                        return result
                result["comment"] = result["comment"] + (
                    f"Added Associations: {associations_to_add}, ",
                )
    if new_propagating_vgws is not None:
        # compare old and new propagating virtual gateways, update if propagating virtual gateways are modified
        propagating_vgws_to_modify = hub.tool.aws.ec2.route_table_utils.get_route_table_propagating_vgws_modifications(
            old_propagating_vgws, new_propagating_vgws
        )
        propagating_vgws_to_add = propagating_vgws_to_modify["propagating_vgws_to_add"]
        propagating_vgws_to_delete = propagating_vgws_to_modify[
            "propagating_vgws_to_delete"
        ]
        if not ctx.get("test", False):
            if propagating_vgws_to_delete:
                for propagating_vgw_to_delete in propagating_vgws_to_delete:
                    ret = await hub.exec.boto3.client.ec2.disable_vgw_route_propagation(
                        ctx,
                        RouteTableId=route_table_id,
                        GatewayId=propagating_vgw_to_delete,
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + ret["comment"]
                        result["result"] = False
                        return result
                result["comment"] = result["comment"] + (
                    f"Deleted Propagating Virtual Gateways: {propagating_vgws_to_delete}, ",
                )
            if propagating_vgws_to_add:
                for propagating_vgw_to_add in propagating_vgws_to_add:
                    ret = await hub.exec.boto3.client.ec2.enable_vgw_route_propagation(
                        ctx,
                        RouteTableId=route_table_id,
                        GatewayId=propagating_vgw_to_add,
                    )
                    if not ret.get("result"):
                        result["comment"] = result["comment"] + ret["comment"]
                        result["result"] = False
                        return result
                result["comment"] = result["comment"] + (
                    f"Added Propagating Virtual Gateways: {propagating_vgws_to_add}, ",
                )

    if result["comment"]:
        result["comment"] = result["comment"] + (
            f"Updated route table {route_table_id}",
        )
    result["ret"] = {
        "routes": new_routes,
        "associations": new_associations,
        "vgws": new_propagating_vgws,
    }
    return result
