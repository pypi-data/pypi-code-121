from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util functions to convert raw resource state from AWS EC2 to present input format.
"""


async def convert_raw_vpc_to_present(
    hub, ctx, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("VpcId")
    resource_parameters = OrderedDict(
        {
            "InstanceTenancy": "instance_tenancy",
            "Tags": "tags",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)
    # The following code block is to make sure to only output the associated/associating cidr blocks and
    # dis-regard the disassociated cidr blocks.
    if raw_resource.get("CidrBlockAssociationSet"):
        ipv4_cidr_block_association_set = []
        for cidr_block in raw_resource.get("CidrBlockAssociationSet"):
            if cidr_block.get("CidrBlockState").get("State") in [
                "associated",
                "associating",
            ]:
                ipv4_cidr_block_association_set.append(cidr_block)
        resource_translated[
            "cidr_block_association_set"
        ] = ipv4_cidr_block_association_set
    if resource_id:
        enableDnsHostnames = await hub.exec.boto3.client.ec2.describe_vpc_attribute(
            ctx, Attribute="enableDnsHostnames", VpcId=resource_id
        )
        if enableDnsHostnames and enableDnsHostnames["result"] is True:
            resource_translated["enable_dns_hostnames"] = enableDnsHostnames["ret"][
                "EnableDnsHostnames"
            ]["Value"]
        else:
            # TODO - Need to handle the error efficiently.
            hub.log.warning(
                f"Failed on fetching enableDnsHostnames on vpc {resource_id} with error {enableDnsHostnames['comment']}."
            )
        enableDnsSupport = await hub.exec.boto3.client.ec2.describe_vpc_attribute(
            ctx, Attribute="enableDnsSupport", VpcId=resource_id
        )
        if enableDnsSupport and enableDnsSupport["result"] is True:
            resource_translated["enable_dns_support"] = enableDnsSupport["ret"][
                "EnableDnsSupport"
            ]["Value"]
        else:
            # TODO - Need to handle the error efficiently.
            hub.log.warning(
                f"Failed on fetching enableDnsSupport on vpc {resource_id} with error {enableDnsSupport['comment']}."
            )
    if raw_resource.get("Ipv6CidrBlockAssociationSet"):
        ipv6_cidr_block_association_set = []
        for cidr_block in raw_resource.get("Ipv6CidrBlockAssociationSet"):
            if cidr_block.get("Ipv6CidrBlockState").get("State") in [
                "associated",
                "associating",
            ]:
                if "NetworkBorderGroup" in cidr_block:
                    # Translate describe output to the correct present input format
                    ipv6_cidr_block_network_border_group = cidr_block.pop(
                        "NetworkBorderGroup"
                    )
                    cidr_block[
                        "Ipv6CidrBlockNetworkBorderGroup"
                    ] = ipv6_cidr_block_network_border_group
                ipv6_cidr_block_association_set.append(cidr_block)
        resource_translated[
            "ipv6_cidr_block_association_set"
        ] = ipv6_cidr_block_association_set
    return resource_translated


def convert_raw_subnet_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("SubnetId")
    resource_parameters = OrderedDict(
        {
            "VpcId": "vpc_id",
            "CidrBlock": "cidr_block",
            "AvailabilityZone": "availability_zone",
            "OutpostArn": "outpost_arn",
            "MapPublicIpOnLaunch": "map_public_ip_on_launch",
            "AssignIpv6AddressOnCreation": "assign_ipv6_address_on_creation",
            "MapCustomerOwnedIpOnLaunch": "map_customer_owned_ip_on_launch",
            "CustomerOwnedIpv4Pool": "customer_owned_ipv4_pool",
            "EnableDns64": "enable_dns_64",
            "PrivateDnsNameOptionsOnLaunch": "private_dns_name_options_on_launch",
            "EnableLniAtDeviceIndex": "enable_lni_at_device_index",
            "Tags": "tags",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)
    if (not raw_resource.get("AvailabilityZone")) and raw_resource.get(
        "AvailabilityZoneId"
    ):
        # Only populate availability_zone_id field when availability_zone doesn't exist
        resource_translated["availability_zone_id"] = raw_resource.get(
            "AvailabilityZoneId"
        )
    if raw_resource.get("Ipv6CidrBlockAssociationSet"):
        ipv6_cidr_block_association_set = (
            hub.tool.aws.network_utils.get_associated_ipv6_cidr_blocks(
                raw_resource.get("Ipv6CidrBlockAssociationSet")
            )
        )
        # We should only output the associated ipv6 cidr block, and theoretically there should only be one,
        # since AWS only supports one ipv6 cidr block association on a subnet
        if ipv6_cidr_block_association_set:
            resource_translated["ipv6_cidr_block"] = ipv6_cidr_block_association_set[
                0
            ].get("Ipv6CidrBlock")
    return resource_translated


def convert_raw_sg_rule_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("SecurityGroupRuleId")
    resource_parameters = OrderedDict(
        {
            "GroupId": "group_id",
            "IsEgress": "is_egress",
            "IpProtocol": "ip_protocol",
            "FromPort": "from_port",
            "ToPort": "to_port",
            "CidrIpv4": "cidr_ipv4",
            "CidrIpv6": "cidr_ipv6",
            "Tags": "tags",
            "PrefixListId": "prefix_list_id",
            "Description": "description",
            "ReferencedGroupInfo": "referenced_group_info",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)
    return resource_translated


def convert_raw_transit_gateway_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("TransitGatewayId")
    resource_parameters = OrderedDict(
        {
            "State": "state",
            "Description": "description",
            "Options": "options",
            "Tags": "tags",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated


def convert_raw_flow_log_to_present(hub, flow_log: Dict):
    """
    Convert the aws flow log response to a common format

    Args:
        hub: required for functions in hub
        flow_log: describe flow log response

    Returns:
        A dictionary of flow log
    """
    describe_parameters = OrderedDict(
        {
            "DeliverLogsPermissionArn": "iam_role",
            "LogGroupName": "log_group_name",
            "TrafficType": "traffic_type",
            "LogDestinationType": "log_destination_type",
            "LogDestination": "log_destination",
            "LogFormat": "log_format",
            "MaxAggregationInterval": "max_aggregation_interval",
            "Tags": "tags",
        }
    )
    translated_flow_log = {}
    flow_log_id = flow_log.get("FlowLogId")
    resource_id = flow_log.get("ResourceId")
    resource_ids = [resource_id]
    resource_type = resource_id.split("-")[0]
    translated_flow_log["resource_ids"] = resource_ids
    if resource_type == "vpc":
        resource_type = "VPC"
    elif resource_type == "subnet":
        resource_type = "Subnet"
    else:
        resource_type = "NetworkInterface"
    translated_flow_log["resource_type"] = resource_type
    translated_flow_log["resource_id"] = flow_log_id

    for parameter_old_key, parameter_new_key in describe_parameters.items():
        if flow_log.get(parameter_old_key) is not None:
            translated_flow_log[parameter_new_key] = flow_log.get(parameter_old_key)

    return translated_flow_log


def convert_raw_route_table_to_present(
    hub, resource: Dict, idem_resource_name: str = None
) -> Dict[str, Any]:
    describe_parameters = OrderedDict(
        {
            "VpcId": "vpc_id",
            "PropagatingVgws": "propagating_vgws",
            "Tags": "tags",
        }
    )
    if not resource:
        return {}
    resource_id = resource.get("RouteTableId")
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_old_key, parameter_new_key in describe_parameters.items():
        if resource.get(parameter_old_key) is not None:
            resource_translated[parameter_new_key] = resource.get(parameter_old_key)

    # Add only required parameters in Describe
    routes_to_add = []
    if resource.get("Routes"):
        for route_to_add in resource.get("Routes"):
            if route_to_add.get("State") == "active":
                routes_to_add.append(route_to_add)
        resource_translated["routes"] = routes_to_add

    associations_to_add = []
    if resource.get("Associations"):
        for association_to_add in resource.get("Associations"):
            if (
                association_to_add.get("AssociationState").get("State") == "associated"
                and not association_to_add["Main"]
            ):
                associations_to_add.append(association_to_add)
        resource_translated["associations"] = associations_to_add
    return resource_translated


def convert_raw_tg_vpc_attachment(
    hub, raw_resource: Dict, resource_name: str = None
) -> Dict[str, any]:
    resource_id = raw_resource.get("TransitGatewayAttachmentId")
    translated_resource = {"name": resource_name, "resource_id": resource_id}

    resource_parameters_transit_gateway = OrderedDict(
        {
            "TransitGatewayId": "transit_gateway",
            "VpcId": "vpc_id",
            "State": "state",
            "SubnetIds": "subnet_ids",
            "Tags": "tags",
            "Options": "options",
        }
    )

    for camel_case_key, snake_case_key in resource_parameters_transit_gateway.items():
        if raw_resource.get(camel_case_key):
            translated_resource[snake_case_key] = raw_resource.get(camel_case_key)
    return translated_resource


async def convert_raw_dhcp_to_present(
    hub, ctx, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("DhcpOptionsId")
    resource_parameters = OrderedDict({"Tags": "tags"})
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    result = dict(comment=(), result=True, ret=None)
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)
    if raw_resource.get("DhcpConfigurations"):
        dhcp_configs = []
        for dhcp_conf in raw_resource.get("DhcpConfigurations"):
            dhcp_config_values_list = []
            for dhcp in dhcp_conf.get("Values"):
                if "Value" in dhcp:
                    dhcp_config_values_list.append(dhcp.get("Value"))
            dhcp_config = {
                "Key": dhcp_conf.get("Key"),
                "Values": dhcp_config_values_list,
            }
            dhcp_configs.append(dhcp_config)
        resource_translated["dhcp_configurations"] = dhcp_configs
    vpc_list = []
    vpc_ret = await hub.exec.boto3.client.ec2.describe_vpcs(ctx)
    if not vpc_ret["result"]:
        result["comment"] = vpc_ret["comment"]
        result["result"] = vpc_ret["result"]
    else:
        for vpc in vpc_ret["ret"]["Vpcs"]:
            if vpc["DhcpOptionsId"] == resource_id:
                vpc_list.append(vpc["VpcId"])
    if vpc_list:
        resource_translated["vpc_id"] = vpc_list

    result["ret"] = resource_translated
    return result


def convert_raw_sg_to_present(hub, security_group: Dict):
    """
    Convert the aws security group response to a common format

    Args:
        hub: required for functions in hub
        security_group: describe security group response

    Returns:
        A dictionary of sg group
    """
    translated_security_group = {}
    describe_parameters = OrderedDict(
        {
            "GroupId": "resource_id",
            "GroupName": "name",
            "VpcId": "vpc_id",
            "Tags": "tags",
            "Description": "description",
        }
    )
    for parameter_old_key, parameter_new_key in describe_parameters.items():
        if security_group.get(parameter_old_key) is not None:
            translated_security_group[parameter_new_key] = security_group.get(
                parameter_old_key
            )

    return translated_security_group


def convert_raw_internet_gateway_to_present(
    hub, resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource.get("InternetGatewayId"),
    }
    if resource.get("Tags"):
        resource_translated["tags"] = resource.get("Tags")
    if resource.get("Attachments"):
        resource_translated["vpc_id"] = [resource.get("Attachments")[0].get("VpcId")]
        resource_translated["attachments"] = resource.get("Attachments")
    return resource_translated


def convert_raw_nat_gateway_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("NatGatewayId")
    describe_parameters = OrderedDict(
        {
            "SubnetId": "subnet_id",
            "ConnectivityType": "connectivity_type",
            "Tags": "tags",
            "State": "state",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in describe_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)
    if raw_resource.get("NatGatewayAddresses"):
        for nat_gateway_address in raw_resource.get("NatGatewayAddresses"):
            if "AllocationId" in nat_gateway_address:
                resource_translated["allocation_id"] = nat_gateway_address.get(
                    "AllocationId"
                )
                break
    return resource_translated


def convert_raw_elastic_ip_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    """
    Given an object state from aws, this function creates a translated resource object in response.

    Args:
        hub: required for functions in hub
        raw_resource (Dict): The dictionary object from where the raw state of resource needs to be translated.
        idem_resource_name (Text): The idem of the idem resource

    Returns: Dict[str, Any]
    """
    elastic_ip = raw_resource
    resource_id = elastic_ip.get("PublicIp")
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    describe_parameters = OrderedDict(
        {
            "AllocationId": "allocation_id",
            "Domain": "domain",
            "NetworkBorderGroup": "network_border_group",
            "PublicIpv4Pool": "public_ipv4_pool",
            "Tags": "tags",
            "PublicIp": "resource_id",
            "CustomerOwnedIpv4Pool": "customer_owned_ipv4_pool",
        }
    )
    for parameter_raw, parameter_present in describe_parameters.items():
        if elastic_ip.get(parameter_raw) is not None:
            resource_translated[parameter_present] = elastic_ip.get(parameter_raw)
    return resource_translated


def convert_raw_vpc_endpoint_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    """
    Convert AWS returned data structure to correct idem vpc-endpoint present state

     Args:
        hub: required for functions in hub
        raw_resource: The aws response to convert

    Returns: Valid idem state for vpc-endpoint of type Dict['string', Any]
    """
    hub.log.debug(
        f"Converting raw aws.ec2.vpc_endpoint: {raw_resource} to valid present state"
    )
    describe_parameters = OrderedDict(
        {
            "VpcEndpointType": "vpc_endpoint_type",
            "VpcId": "vpc_id",
            "ServiceName": "service_name",
            "PolicyDocument": "policy_document",
            "RouteTableIds": "route_table_ids",
            "SubnetIds": "subnet_ids",
            "SecurityGroupIds": "security_group_ids",
            "PrivateDnsEnabled": "private_dns_enabled",
            "Tags": "tags",
        }
    )
    resource_id = raw_resource.get("VpcEndpointId")
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in describe_parameters.items():
        if raw_resource.get(parameter_raw) is not None:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated


def convert_raw_ami_to_present(hub, raw_resource: Dict[str, Any]) -> Dict[str, Any]:
    """
    Util function to convert raw resource state from AWS AMI to present input format.
    """
    resource_id = raw_resource.get("ImageId")
    resource_parameters = OrderedDict(
        {
            "Name": "name",
            "ImageLocation": "image_location",
            "Architecture": "architecture",
            "KernelId": "kernel_id",
            "BlockDeviceMappings": "block_device_mappings",
            "Description": "description",
            "EnaSupport": "ena_support",
            "BillingProducts": "billing_products",
            "RamdiskId": "ramdisk_id",
            "RootDeviceName": "root_device_name",
            "SriovNetSupport": "sriov_net_support",
            "VirtualizationType": "virtualization_type",
            "BootMode": "boot_mode",
            "Tags": "tags",
        }
    )
    resource_translated = {"resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if raw_resource.get(parameter_raw):
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)

    return resource_translated
