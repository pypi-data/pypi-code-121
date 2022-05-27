from collections import OrderedDict
from typing import Any
from typing import Dict


async def update_ipv6_cidr_blocks(
    hub,
    ctx,
    subnet_id: str,
    old_ipv6_cidr_block: Dict[str, Any],
    new_ipv6_cidr_block: Dict[str, Any],
):
    """
    Update associated ipv6 cidr block of a subnet. This function supports associating an ipv6 cidr block, or updating
     the existing(old) ipv6 cidr block to the new ipv6 cidr block. Disassociating an ipv6 cidr block is not supported,
     due to how an sls file works currently. If ipv6_cidr_block parameter is left as blank, Idem-aws will do no-op
     on the subnet's ipv6 cidr block. To disassociate an ipv6 cidr block, a user will have to delete the subnet and
     re-create it without the ipv6 cidr block.

    Args:
        hub:
        ctx:
        subnet_id: The AWS resource id of the existing subnet
        old_ipv6_cidr_block: The ipv6 cidr block on the existing vpc
        new_ipv6_cidr_block: The expected ipv6 cidr block on the existing vpc

    Returns:
        {"result": True|False, "comment": A message Tuple, "ret": Dict}

    """
    result = dict(comment=(), result=True, ret=None)
    if old_ipv6_cidr_block is None and new_ipv6_cidr_block:
        if ctx.get("test", False):
            result["ret"] = {
                "ipv6_cidr_block": new_ipv6_cidr_block.get("Ipv6CidrBlock")
            }
            return result
        else:
            ret = await hub.exec.boto3.client.ec2.associate_subnet_cidr_block(
                ctx,
                SubnetId=subnet_id,
                Ipv6CidrBlock=new_ipv6_cidr_block.get("Ipv6CidrBlock"),
            )
            result["result"] = ret["result"]
            if result["result"]:
                hub.log.info(
                    f"Add subnet {subnet_id} ipv6 cidr block {new_ipv6_cidr_block.get('Ipv6CidrBlock')}"
                )
                result["ret"] = {
                    "ipv6_cidr_block": new_ipv6_cidr_block.get("Ipv6CidrBlock")
                }
            else:
                result["comment"] = ret["comment"]
            return result
    elif old_ipv6_cidr_block and new_ipv6_cidr_block:
        if old_ipv6_cidr_block.get("Ipv6CidrBlock") != new_ipv6_cidr_block.get(
            "Ipv6CidrBlock"
        ):
            if ctx.get("test", False):
                result["ret"] = {
                    "ipv6_cidr_block": new_ipv6_cidr_block.get("Ipv6CidrBlock")
                }
                return result
            else:
                ret = await hub.exec.boto3.client.ec2.disassociate_subnet_cidr_block(
                    ctx, AssociationId=old_ipv6_cidr_block.get("AssociationId")
                )
                if not ret.get("result"):
                    result["comment"] = ret["comment"]
                    result["result"] = False
                    return result
                ret = await hub.exec.boto3.client.ec2.associate_subnet_cidr_block(
                    ctx,
                    SubnetId=subnet_id,
                    Ipv6CidrBlock=new_ipv6_cidr_block.get("Ipv6CidrBlock"),
                )
                result["result"] = ret["result"]
                if result["result"]:
                    hub.log.info(
                        f"Update subnet {subnet_id} ipv6 cidr block from {old_ipv6_cidr_block.get('Ipv6CidrBlock')}"
                        f" to {new_ipv6_cidr_block.get('Ipv6CidrBlock')}"
                    )
                    result["ret"] = {
                        "ipv6_cidr_block": new_ipv6_cidr_block.get("Ipv6CidrBlock")
                    }
                    return result
                else:
                    result["comment"] = ret["comment"]
    return result


async def update_subnet_attributes(
    hub,
    ctx,
    before: Dict[str, Any],
    resource_id: str,
    map_public_ip_on_launch: bool,
    assign_ipv6_address_on_creation: bool,
    map_customer_owned_ip_on_launch: bool,
    customer_owned_ipv4_pool: str,
    enable_dns_64: bool,
    private_dns_name_options_on_launch: Dict[str, Any],
    enable_lni_at_device_index: int,
    disable_lni_at_device_index: bool,
):
    """
    Updates the Subnet Attributes
    Args:
        before: existing resource
        resource_id (Text): AWS Subnet ID
        map_public_ip_on_launch (boolean): Indicates whether instances launched in this subnet receive a public IPv4 address.
        assign_ipv6_address_on_creation (boolean): Specify true to indicate that network interfaces created in the specified subnet should be assigned an IPv6 address.
        map_customer_owned_ip_on_launch (boolean): Specify true to indicate that network interfaces attached to instances created in the specified subnet should be assigned a customer-owned IPv4 address.
        customer_owned_ipv4_pool (Text): The customer-owned IPv4 address pool associated with the subnet.
        enable_dns_64 (boolean): Indicates whether DNS queries made to the Amazon-provided DNS Resolver in this subnet should return synthetic IPv6 addresses for IPv4-only destinations.
        private_dns_name_options_on_launch (Dict): The type of hostnames to assign to instances in the subnet at launch.
        enable_lni_at_device_index (int): Indicates the device position for local network interfaces in this subnet.
        disable_lni_at_device_index (boolean): Specify true to indicate that local network interfaces at the current position should be disabled.


    Returns:
        {"result": True|False, "comment": A message Tuple, "ret": None|Updated Attributes name and value}

    """
    result = dict(comment=(), result=True, ret={})

    if (
        before.get("PrivateDnsNameOptionsOnLaunch") is not None
        and private_dns_name_options_on_launch is not None
    ):
        update_ret = await modify_subnet_attributes_dns_options(
            hub,
            ctx,
            resource_id,
            private_dns_name_options_on_launch,
            before.get("PrivateDnsNameOptionsOnLaunch"),
        )
        result["ret"] = update_ret["ret"]
        result["comment"] = result["comment"] + update_ret["comment"]
        result["result"] = result["result"] and update_ret["result"]

    resource_parameters = OrderedDict(
        {
            "AssignIpv6AddressOnCreation": assign_ipv6_address_on_creation,
            "MapPublicIpOnLaunch": map_public_ip_on_launch,
            "CustomerOwnedIpv4Pool": customer_owned_ipv4_pool,
            "MapCustomerOwnedIpOnLaunch": map_customer_owned_ip_on_launch,
            "EnableDns64": enable_dns_64,
            "EnableLniAtDeviceIndex": enable_lni_at_device_index,
            "DisableLniAtDeviceIndex": disable_lni_at_device_index,
        }
    )

    for key, value in resource_parameters.items():
        if key in before:
            if (value is not None) and value != before[key]:
                update_ret = await modify_subnet_attribute(
                    hub, ctx, resource_id, key, resource_parameters[key]
                )
                result["ret"].update(update_ret["ret"])
                result["comment"] = result["comment"] + update_ret["comment"]
                result["result"] = result["result"] and update_ret["result"]
    return result


async def modify_subnet_attributes_dns_options(
    hub,
    ctx,
    resource_id: str,
    private_dns_name_options: Dict[str, Any],
    before_dns_name_options: Dict[str, Any],
):
    """
    Modify the subnet attributes for dns name options
    Args:
        before_dns_name_options (Dict): The type of hostnames to assign to instance in the subnet at launch.
        resource_id (Text): AWS Subnet ID
        private_dns_name_options (Dict): The type of hostnames to assign to instance in the subnet at launch.

    Returns:
        {"result": True|False, "comment": A message Tuple, "ret": None|Updated Attributes name and value}

    """
    result = dict(comment=(), result=True, ret={})

    host_name_type = private_dns_name_options.get("HostnameType")
    enable_resource_name_dns_a_record = private_dns_name_options.get(
        "EnableResourceNameDnsARecord"
    )
    enable_resource_name_dns_aaaa_record = private_dns_name_options.get(
        "EnableResourceNameDnsAAAARecord"
    )

    # Added key value for private_dns_options because for update call, parameter names are different.
    private_dns_keys_values = OrderedDict(
        {
            "HostnameType": "PrivateDnsHostnameTypeOnLaunch",
            "EnableResourceNameDnsARecord": "EnableResourceNameDnsARecordOnLaunch",
            "EnableResourceNameDnsAAAARecord": "EnableResourceNameDnsAAAARecordOnLaunch",
        }
    )
    dns_key_values = OrderedDict(
        {
            "HostnameType": host_name_type,
            "EnableResourceNameDnsARecord": enable_resource_name_dns_a_record,
            "EnableResourceNameDnsAAAARecord": enable_resource_name_dns_aaaa_record,
        }
    )

    # This is written separately because all the attributes in dns_name_options dict needs to be updated.
    for key, value in dns_key_values.items():
        if key in before_dns_name_options:
            if (value is not None) and value != before_dns_name_options.get(key):
                update_ret = await modify_subnet_attribute(
                    hub, ctx, resource_id, private_dns_keys_values[key], value
                )
                result["ret"].update(update_ret["ret"])
                result["comment"] = result["comment"] + update_ret["comment"]
                result["result"] = result["result"] and update_ret["result"]

    return result


async def modify_subnet_attribute(
    hub, ctx, resource_id: str, attr_key: str, value: str
):
    result = dict(comment=(), result=True, ret={})
    update_payload = {}
    str_objects = [
        "CustomerOwnedIpv4Pool",
        "PrivateDnsHostnameTypeOnLaunch",
        "EnableLniAtDeviceIndex",
    ]

    resource_parameters = OrderedDict(
        {
            "MapPublicIpOnLaunch": "map_public_ip_on_launch",
            "AssignIpv6AddressOnCreation": "assign_ipv6_address_on_creation",
            "MapCustomerOwnedIpOnLaunch": "map_customer_owned_ip_on_launch",
            "CustomerOwnedIpv4Pool": "customer_owned_ipv4_pool",
            "EnableDns64": "enable_dns_64",
            "PrivateDnsNameOptionsOnLaunch": "private_dns_name_options_on_launch",
            "PrivateDnsHostnameTypeOnLaunch": "HostnameType",
            "EnableResourceNameDnsARecordOnLaunch": "EnableResourceNameDnsARecord",
            "EnableResourceNameDnsAAAARecordOnLaunch": "EnableResourceNameDnsAAAARecord",
            "EnableLniAtDeviceIndex": "enable_lni_at_device_index",
        }
    )

    attr_value = value
    if not ctx.get("test", False):
        if attr_key not in str_objects:
            attr_value = {"Value": value}
        update_payload[attr_key] = attr_value
        update_ret = await hub.exec.boto3.client.ec2.modify_subnet_attribute(
            ctx, SubnetId=resource_id, **update_payload
        )
        if not update_ret["result"]:
            result["comment"] = result["comment"] + update_ret["comment"]
            result["result"] = False
            return result

    result["ret"] = {resource_parameters[attr_key]: value}
    result["comment"] = result["comment"] + (
        f"Update {resource_parameters[attr_key]} : {value}",
    )
    return result
