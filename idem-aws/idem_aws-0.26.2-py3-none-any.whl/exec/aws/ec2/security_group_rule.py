from collections import OrderedDict
from typing import Any
from typing import Dict


async def update_security_group_rule(
    hub,
    ctx,
    before: Dict[str, Any],
    cidr_ipv4: str,
    cidr_ipv6: str,
    description: str,
    from_port: int,
    to_port: int,
    group_id: str,
    ip_protocol: str,
    prefix_list_id: str,
    referenced_group_info: Dict,
    resource_id: str,
):
    """
    Updates the Security group rule
    Args:
        before: existing resource
        ip_protocol(str): The IP protocol name (tcp , udp , icmp , icmpv6 ) or number (see Protocol Numbers ). [VPC only] Use -1 to specify all protocols.
                          When authorizing security group rules, specifying -1 or a protocol number other than tcp , udp , icmp , or icmpv6 allows traffic
                          on all ports, regardless of any port range you specify. For tcp , udp , and icmp , you must specify a port range. For icmpv6 ,
                          the port range is optional; if you omit the port range, traffic for all types and codes is allowed.
        from_port(int): The start of port range for the TCP and UDP protocols, or an ICMP/ICMPv6 type number. A value of -1 indicates all ICMP/ICMPv6 types.
                        If you specify all ICMP/ICMPv6 types, you must specify all codes.
        to_port(int): The end of port range for the TCP and UDP protocols, or an ICMP/ICMPv6 code. A value of -1 indicates all ICMP/ICMPv6 codes.
                      If you specify all ICMP/ICMPv6 types, you must specify all codes.
        cidr_ipv4(str, optional): The IPv4 CIDR range. You can either specify a CIDR range or a source security group, not both.
                        To specify a single IPv4 address, use the /32 prefix length.
        resource_id(Text, optional): AWS Security group rule ID.
        cidr_ipv6(str, optional): The IPv6 CIDR range. You can either specify a CIDR range or a source security group, not both.
                                  To specify a single IPv6 address, use the /128 prefix length.
        prefix_list_id(str, optional): The ID of the prefix.
        referenced_group_info(Dict, optional): The security group and Amazon Web Services account ID pairs.
        description(str, optional): The description of the security group rule.

    Returns:
        {"result": True|False, "comment": A message Tuple, "ret": Dict}

    """
    result = dict(comment=(), result=True, ret=None)
    updated_payload = {}
    updated_rule = {}
    new_modified_rule = dict(SecurityGroupRuleId=None, SecurityGroupRule=None)
    new_modified_rule["SecurityGroupRuleId"] = resource_id
    resource_parameters = OrderedDict(
        {
            "IpProtocol": ip_protocol,
            "FromPort": from_port,
            "ToPort": to_port,
            "CidrIpv4": cidr_ipv4,
            "CidrIpv6": cidr_ipv6,
            "PrefixListId": prefix_list_id,
            "Description": description,
        }
    )
    for key, value in resource_parameters.items():
        if key in before.keys():
            updated_payload[key] = resource_parameters[key]
            if (value is not None) and value != before[key]:
                updated_rule[key] = resource_parameters[key]
        elif resource_parameters[key]:
            updated_payload[key] = resource_parameters[key]
            updated_rule[key] = resource_parameters[key]
    # You must either specify cidr_ipv4 or referenced_group_info. You cannot change source from cidr to reference
    # group id or vice versa
    if before.get(
        "CidrIpv4"
    ) is None and not hub.tool.aws.state_comparison_utils.compare_dicts(
        referenced_group_info,
        before.get("ReferencedGroupInfo"),
    ):
        updated_rule["ReferencedGroupId"] = referenced_group_info.get("GroupId")
    if updated_rule:
        if before.get("CidrIpv4") is None and referenced_group_info is not None:
            updated_payload["ReferencedGroupId"] = referenced_group_info.get("GroupId")
        new_modified_rule["SecurityGroupRule"] = updated_payload
        if not ctx.get("test", False):
            update_ret = await hub.exec.boto3.client.ec2.modify_security_group_rules(
                ctx,
                GroupId=group_id,
                SecurityGroupRules=[new_modified_rule],
            )
            if not update_ret["result"]:
                result["comment"] = update_ret["comment"]
                result["result"] = False
                return result
        result["ret"] = {}
        result = update_result(result, updated_rule)

    return result


def update_result(
    result: Dict[str, Any], update_payload: Dict[str, Any]
) -> Dict[str, Any]:
    parameters = OrderedDict(
        {
            "IpProtocol": "ip_protocol",
            "FromPort": "from_port",
            "ToPort": "to_port",
            "CidrIpv4": "cidr_ipv4",
            "CidrIpv6": "cidr_ipv6",
            "PrefixListId": "prefix_list_id",
            "Description": "description",
            "ReferencedGroupId": "referenced_group_id",
        }
    )

    for raw_parameter, present_parameter in parameters.items():
        if raw_parameter in update_payload:
            result["ret"][present_parameter] = update_payload[raw_parameter]
            result["comment"] = result["comment"] + (
                f"Update {present_parameter}: {update_payload[raw_parameter]}",
            )
    return result
