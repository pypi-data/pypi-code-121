from typing import Dict
from typing import List

IPV4_PARAMETERS = {"CidrBlock", "Ipv4IpamPoolId", "Ipv4NetmaskLength"}
IPV6_PARAMETERS = {
    "AmazonProvidedIpv6CidrBlock",
    "Ipv6CidrBlockNetworkBorderGroup",
    "Ipv6Pool",
    "Ipv6CidrBlock",
    "Ipv6IpamPoolId",
    "Ipv6NetmaskLength",
}


def generate_cidr_request_payload_for_vpc(
    hub, cidr_block_association: Dict, ip_type: str
):
    """
    Generate a set of cidr request parameters. These parameters can be used as input parameters when associating a cidr
    block to a vpc.

    Args:
        hub: required for functions in hub
        cidr_block_association:
        ip_type: ipv4 or ipv6

    Returns: A dict that can be used as input parameters to create/update vpc cidr association

    """
    request_payload = {}
    if ip_type == "ipv4":
        for ipv4_parameter in IPV4_PARAMETERS:
            if ipv4_parameter in cidr_block_association:
                request_payload[ipv4_parameter] = cidr_block_association.get(
                    ipv4_parameter
                )
    elif ip_type == "ipv6":
        for ipv6_parameter in IPV6_PARAMETERS:
            if ipv6_parameter in cidr_block_association:
                request_payload[ipv6_parameter] = cidr_block_association.get(
                    ipv6_parameter
                )
    else:
        raise TypeError(
            f"Unknown ip type: {ip_type} . The ip type should either be ipv4 or ipv6."
        )

    return request_payload


def get_associated_ipv6_cidr_blocks(hub, ipv6_cidr_block_association_set: List[Dict]):
    """
    Given a list of ipv6 cidr block associations, retrieving the cidr associations that have
     'associating' or 'associated' status
    """
    result = list()
    if ipv6_cidr_block_association_set:
        for ipv6_cidr_block_association in ipv6_cidr_block_association_set:
            if ipv6_cidr_block_association.get("Ipv6CidrBlockState").get("State") in [
                "associating",
                "associated",
            ]:
                result.append(ipv6_cidr_block_association)
    return result
