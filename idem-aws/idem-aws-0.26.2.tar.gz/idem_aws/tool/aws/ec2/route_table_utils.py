from typing import Dict
from typing import List

ALLOWED_ROUTE_DESTINATION_CIDR_BLOCKS = {
    "DestinationCidrBlock",
    "DestinationIpv6CidrBlock",
    "DestinationPrefixListId",
}

ALLOWED_ROUTE_TARGET_GATEWAYS = {
    "VpcEndpointId",
    "EgressOnlyInternetGatewayId",
    "GatewayId",
    "InstanceId",
    "NatGatewayId",
    "TransitGatewayId",
    "LocalGatewayId",
    "CarrierGatewayId",
    "NetworkInterfaceId",
    "RouteTableId",
    "VpcPeeringConnectionId",
    "CoreNetworkArn",
}

ALLOWED_DEFAULT_ROUTE_TARGET_GATEWAYS = {
    "VpcEndpointId",
    "GatewayId",
    "InstanceId",
    "NetworkInterfaceId",
}


def get_route_table_routes_modifications(
    hub, old_routes: List[Dict], new_routes: List[Dict]
):
    """
    Given old routes i.e, the routes of current route table and new_routes
    i.e, the routes we want to modify to, this function will compare differences between
    old and new routes and return routes to be added and removed

    Args:
        hub:
        old_routes(List):  routes of existing route table
        new_routes(List): new routes to update

    Returns:
        Dict[str, List]

    """
    result = dict(
        comment=(),
        routes_to_add=list(),
        routes_to_delete=list(),
        routes_to_replace=list(),
        result=True,
    )
    routes_to_add = list()
    routes_to_delete = list()
    routes_to_replace = list()
    old_routes_map = dict()
    default_destination_cidr_block: str = ""
    # Creates a map of destination cidr block -> route to easily retrieve further
    for route in old_routes:
        if route.get("State") == "active":
            # Route table route allows three types of destinations
            # 1) DestinationCidrBlock,
            # 2) DestinationIpv6CidrBlock,
            # 3) DestinationPrefixListId,
            # We need to determine which type of  destination is used
            destination_cidr_key = get_common_key_in_dict(
                route, ALLOWED_ROUTE_DESTINATION_CIDR_BLOCKS
            )
            old_routes_map[route.get(destination_cidr_key)] = route
            if route.get("Origin") == "CreateRouteTable":
                default_destination_cidr_block = route.get(destination_cidr_key)
    new_destination_cidr_blocks = list()
    for new_route in new_routes:
        # Loop through new routes and determine which destination is used
        destination_cidr_key = get_common_key_in_dict(
            new_route, ALLOWED_ROUTE_DESTINATION_CIDR_BLOCKS
        )
        destination_cidr_block = new_route.get(destination_cidr_key)

        # checking for duplicate destination cidr blocks. There can be only unique destination cidr block
        if destination_cidr_block in new_destination_cidr_blocks:
            result["result"] = False
            result["comment"] = (
                "Duplicate destination cidr blocks are not allowed, they should be unique.",
            )
            return result
        else:
            new_destination_cidr_blocks.append(destination_cidr_block)
        allowed_targets = (
            ALLOWED_DEFAULT_ROUTE_TARGET_GATEWAYS
            if destination_cidr_block == default_destination_cidr_block
            else ALLOWED_ROUTE_TARGET_GATEWAYS
        )
        new_target_key = get_common_key_in_dict(new_route, allowed_targets)
        if new_target_key is None or destination_cidr_key is None:
            result["result"] = False
            result["comment"] = (
                "There should be at least one valid destination cidr block and one target",
            )
            return result
        new_target_value = new_route.get(new_target_key)
        # Destination cidr is unique for a route. After retrieving destination cidr check in old routes
        # if the new route cidr block is not present in old routes we associate it to route table
        # if the destination cidr is already present in old routes we need to check if there is any changes in target
        # The allowed targets can be any one of Internet gateway, Virtual private gateway and many more.
        # If the target key is modified or value is modified we need to delete old route and create
        # a new route with updated values
        # example the target might be changed from an Internet gateway to Transit gateway the key changes
        # So we need to delete Internet gateway route and create Transit gateway route
        if destination_cidr_block not in old_routes_map:
            routes_to_add.append(
                {
                    destination_cidr_key: destination_cidr_block,
                    new_target_key: new_target_value,
                }
            )
        else:
            old_route = old_routes_map.get(destination_cidr_block)
            old_target_key = get_common_key_in_dict(
                old_route, ALLOWED_ROUTE_TARGET_GATEWAYS
            )
            old_target_value = old_route.get(old_target_key)
            if old_target_key != new_target_key or old_target_value != new_target_value:
                routes_to_replace.append(
                    {
                        destination_cidr_key: destination_cidr_block,
                        new_target_key: new_target_value,
                    }
                )
            del old_routes_map[destination_cidr_block]

    # delete the remaining routes which are still present in old routes and not in new routes
    for old_route in old_routes_map.values():
        destination_cidr_key = get_common_key_in_dict(
            old_route, ALLOWED_ROUTE_DESTINATION_CIDR_BLOCKS
        )
        destination_cidr_block = old_route.get(destination_cidr_key)
        if old_route.get("Origin") != "CreateRouteTable":
            routes_to_delete.append({destination_cidr_key: destination_cidr_block})

    result["routes_to_add"] = routes_to_add
    result["routes_to_delete"] = routes_to_delete
    result["routes_to_replace"] = routes_to_replace
    return result


def get_route_table_associations_modifications(
    hub, old_associations: List[Dict], new_associations: List[Dict]
):
    """
    Given old associations i.e, the associations of current association table and new_associations
    i.e, the associations we want to modify to, this function will compare differences between
    old and new associations and return associations to be added and removed

    Args:
        hub:
        old_associations(List):  associations of existing association table
        new_associations(List): new associations to update

    Returns:
        Dict[str, List]

    """
    result = dict(
        comment=(),
        associations_to_add=list(),
        associations_to_delete=list(),
        result=True,
    )
    associations_to_add = list()
    associations_to_delete = list()
    old_associations_map = dict()
    # Creates a map of Route table association ID -> association to easily retrieve further
    for association in old_associations:
        if (
            association.get("AssociationState")
            and association.get("AssociationState").get("State") == "associated"
            and association.get("Main") is not True
        ):
            if "SubnetId" in association:
                old_associations_map[association.get("SubnetId")] = association
            elif "GatewayId" in association:
                old_associations_map[association.get("GatewayId")] = association

    for new_association in new_associations:
        # Loop through new associations and determine which target is used
        new_target_key = None

        if "SubnetId" in new_association or "GatewayId" in new_association:
            new_target_key = (
                "SubnetId" if "SubnetId" in new_association else "GatewayId"
            )

        if new_target_key is None:
            result["result"] = False
            result["comment"] = (
                f"There should be at least one valid Subnet or GatewayId. {new_association}",
            )
            return result
        new_target_value = new_association.get(new_target_key)

        # Destination cidr is unique for an association. After retrieving destination cidr check in old associations
        # if the new association cidr block is not present in old associations we associate it to association table
        # if the destination cidr is already present in old associations we need to check
        # if there is any changes in target
        # The allowed targets can be any one of Internet gateway, Virtual private gateway and many more.
        # If the target key is modified or value is modified we need to delete old association and create
        # a new association with updated values
        # example the target might be changed from an Internet gateway to Transit gateway the key changes
        # So we need to delete Internet gateway association and create Transit gateway association
        if new_target_value not in old_associations_map:
            associations_to_add.append({new_target_key: new_target_value})
        else:
            old_association = old_associations_map.get(new_target_value)
            old_target_key = None
            if "SubnetId" in old_association or "GatewayId" in old_association:
                old_target_key = (
                    "SubnetId" if "SubnetId" in new_association else "GatewayId"
                )
            old_target_value = old_association.get(old_target_key)
            if old_target_key != new_target_key or old_target_value != new_target_value:
                associations_to_add.append({new_target_key: new_target_value})
                associations_to_delete.append(
                    {"AssociationId": old_association.get("RouteTableAssociationId")}
                )
            del old_associations_map[new_target_value]

    # delete the remaining associations which are still present in old associations and not in new associations
    for old_association in old_associations_map.values():
        associations_to_delete.append(
            {"AssociationId": old_association.get("RouteTableAssociationId")}
        )

    result["associations_to_add"] = associations_to_add
    result["associations_to_delete"] = associations_to_delete
    return result


def get_route_table_propagating_vgws_modifications(
    hub, old_propagating_vgws: List[Dict], new_propagating_vgws: List[Dict]
):
    result = dict(
        comment="",
        propagating_vgws_to_add=list(),
        propagating_vgws_to_delete=list(),
        result=True,
    )
    old_propagating_vgw_ids = []
    new_propagating_vgw_ids = []
    if old_propagating_vgws:
        for old_propagating_vgw in old_propagating_vgws:
            old_propagating_vgw_ids.append(old_propagating_vgw.get("GatewayId"))
    if new_propagating_vgws:
        for new_propagating_vgw in new_propagating_vgws:
            new_propagating_vgw_ids.append(new_propagating_vgw.get("GatewayId"))
    result["propagating_vgws_to_add"] = list(
        set(new_propagating_vgw_ids).difference(old_propagating_vgw_ids)
    )
    result["propagating_vgws_to_delete"] = list(
        set(old_propagating_vgw_ids).difference(new_propagating_vgw_ids)
    )
    return result


def get_common_key_in_dict(dict1: dict, target_keys_list: set):
    common_keys = set(dict1.keys()).intersection(target_keys_list)
    return common_keys.pop() if common_keys else None
