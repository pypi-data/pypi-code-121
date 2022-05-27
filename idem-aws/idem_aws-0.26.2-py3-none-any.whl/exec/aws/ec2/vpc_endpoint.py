from typing import Any
from typing import Dict
from typing import List


async def update_vpc_endpoint(
    hub,
    ctx,
    old_state: Dict[str, Any],
    resource_id: str,
    policy_document: str = None,
    route_table_ids: List = None,
    subnet_ids: List = None,
    security_group_ids: List = None,
    private_dns_enabled: bool = None,
    timeout: Dict = None,
) -> Dict[str, Any]:
    """
    Modifies a vpc endpoint. The values subnet_ids, security_group_ids, route_table_ids will actually become
    the respective values for the vpc endpoint. It will error if you try to enable private dns on a non Interface endpoint.

    Args:
        hub:
        ctx:
        old_state: Dict[Text, Any]: The previous state of the vpc_endpoint.
        resource_id(string): AWS VPC Endpoint id.
        policy_document(string): The new policy document for the vpc endpoint
        route_table_ids(List): List of route table ids for the vpc endpoint
        subnet_ids(List): List of subnet ids for the vpc endpoint
        security_group_ids(List): List of security group ids for the vpc endpoint
        private_dns_enabled(bool): Whether to enable or disable private dns for the vpc endpoint
        timeout(Dict, optional): Timeout configuration for updating the endpoint.
            * update (Dict) -- Timeout configuration for updating the endpoint
                * delay -- The amount of time in seconds to wait between attempts.
                * max_attempts -- Customized timeout configuration containing delay and max attempts.

    Returns:
        {"result": True|False, "comment": "A message tuple", "ret": Dict}

    """

    result = dict(comment=(), result=True, ret=None)
    name = old_state.get("name")

    # For if the vpc_endpoint exists
    hub.log.debug(f"Updating aws.ec2.vpc_endpoint: '{name}'")

    if old_state.get("policy_document") and policy_document == None:
        policy_document = old_state["policy_document"]

    if private_dns_enabled == None:
        policy_document = old_state["private_dns_enabled"]

    find_set_difference = lambda x, y: list(set(x).difference(set(y)))

    if route_table_ids is None:
        route_tables_to_be_removed = []
        new_route_tables = []
    elif old_state.get("route_table_ids"):
        # find the route tables in route_table_ids that aren't in the old state (these are the new ones)
        new_route_tables = find_set_difference(
            route_table_ids, old_state["route_table_ids"]
        )
        # the ones in the old_state not in route_table_ids are the ones to be removed
        route_tables_to_be_removed = find_set_difference(
            old_state["route_table_ids"], route_table_ids
        )
    else:
        new_route_tables = route_table_ids
        route_tables_to_be_removed = old_state.get("route_table_ids", [])
    hub.log.debug(
        f"Updating aws.ec2.vpc_endpoint: '{name}'. Route tables passed in: {route_table_ids}. Old route tables: {old_state.get('route_table_ids', None)}"
    )
    hub.log.debug(
        f"Updating aws.ec2.vpc_endpoint: '{name}'. New route tables: {new_route_tables}. Route tables to be removed: {route_tables_to_be_removed}"
    )

    # The logic for subnets and security group's is the same as Route tables
    if subnet_ids is None:
        subnets_to_be_removed = []
        new_subnets = []
    elif old_state.get("subnet_ids"):
        new_subnets = find_set_difference(subnet_ids, old_state["subnet_ids"])
        subnets_to_be_removed = find_set_difference(old_state["subnet_ids"], subnet_ids)
    else:
        new_subnets = subnet_ids
        subnets_to_be_removed = old_state.get("subnet_ids", [])
    hub.log.debug(
        f"Updating aws.ec2.vpc_endpoint: '{name}'. Subnets passed in: {subnet_ids}. Old subnets: {old_state.get('subnet_ids', None)}"
    )
    hub.log.debug(
        f"Updating aws.ec2.vpc_endpoint: '{name}'. New subnets: {new_subnets}. Subnets to be removed: {subnets_to_be_removed}"
    )

    if security_group_ids is None:
        security_groups_to_be_removed = []
        new_security_groups = []
    elif old_state.get("security_group_ids"):
        new_security_groups = find_set_difference(
            security_group_ids, old_state["security_group_ids"]
        )
        security_groups_to_be_removed = find_set_difference(
            old_state["security_group_ids"], security_group_ids
        )
    else:
        new_security_groups = security_group_ids
        security_groups_to_be_removed = old_state.get("security_group_ids", [])
    hub.log.debug(
        f"Updating aws.ec2.vpc_endpoint: '{name}'. Security groups passed in: {security_group_ids}. Old security groups: {(old_state.get('security_group_ids', None))}"
    )
    hub.log.debug(
        f"Updating aws.ec2.vpc_endpoint: '{name}'. New security groups: {new_security_groups}. Security groups to be removed: {security_groups_to_be_removed}"
    )

    if ctx.get("test", False) and result["result"]:
        plan_state = hub.tool.aws.test_state_utils.generate_test_state(
            enforced_state=old_state,
            desired_state={
                "policy_document": policy_document,
                "route_table_ids": route_table_ids,
                "subnet_ids": subnet_ids,
                "security_group_ids": security_group_ids,
                "private_dns_enabled": private_dns_enabled,
            },
        )
        result["ret"] = {k: v for k, v in plan_state.items() if v is not None}
        result["comment"] = (
            f"Would succeed in modifying aws.ec2.vpc_endpoint '{name}'",
        )
        return result

    ret = await hub.exec.boto3.client.ec2.modify_vpc_endpoint(
        ctx,
        VpcEndpointId=resource_id,
        ResetPolicy=False,
        PolicyDocument=policy_document,
        AddRouteTableIds=new_route_tables,
        RemoveRouteTableIds=route_tables_to_be_removed,
        AddSubnetIds=new_subnets,
        RemoveSubnetIds=subnets_to_be_removed,
        AddSecurityGroupIds=new_security_groups,
        RemoveSecurityGroupIds=security_groups_to_be_removed,
        PrivateDnsEnabled=private_dns_enabled,
    )
    result["result"] = ret["result"]
    if not result["result"]:
        result["comment"] = result["comment"] + ret["comment"]
        return result
    update_waiter_acceptors = [
        {
            "matcher": "pathAll",
            "expected": "available",
            "state": "success",
            "argument": "VpcEndpoints[].State",
        },
        {
            "matcher": "pathAll",
            "expected": "pending",
            "state": "retry",
            "argument": "VpcEndpoints[].State",
        },
    ]
    waiter_config = hub.tool.aws.waiter_utils.create_waiter_config(
        default_delay=15,
        default_max_attempts=40,
        timeout_config=timeout.get("update") if timeout else None,
    )
    endpoint_waiter = hub.tool.boto3.custom_waiter.waiter_wrapper(
        name="VpcEndpointModify",
        operation="DescribeVpcEndpoints",
        argument=["VpcEndpoints[].State"],
        acceptors=update_waiter_acceptors,
        client=hub.tool.boto3.client.get_client(ctx, "ec2"),
    )
    try:
        await hub.tool.boto3.client.wait(
            ctx,
            "ec2",
            "VpcEndpointModify",
            endpoint_waiter,
            VpcEndpointIds=[resource_id],
            WaiterConfig=waiter_config,
        )
    except Exception as e:
        result["comment"] = result["comment"] + (str(e),)
        result["result"] = False
        return result

    result["comment"] = (f"Succeeded modifying aws.ec2.vpc_endpoint '{name}'",)
    return result
