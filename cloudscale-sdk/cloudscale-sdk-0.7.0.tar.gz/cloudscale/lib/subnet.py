from typing import Optional

from . import CloudscaleMutable


class Subnet(CloudscaleMutable):
    resource = "subnets"

    def create(
        self,
        cidr: str,
        network_uuid: str,
        gateway_address: Optional[str] = None,
        dns_servers: Optional[list] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Creates a subnet.

        Args:
            cidr (str): The address range in CIDR notation. Must be at least /24.
            network_uuid (str): The network UUID of the subnet.
            gateway_address (str, optional): The gateway address of the subnet. Defaults to None.
            dns_servers (list, optional): A list of custom DNS resolver IP addresses. Defaults to None.
            tags (dict, optional): The tags assigned to the subnet. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            "cidr": cidr,
            "network": network_uuid,
            "gateway_address": gateway_address,
            "dns_servers": dns_servers,
            "tags": tags,
        }
        return super().create(payload=payload)

    def update(
        self,
        uuid: str,
        gateway_address: Optional[str] = None,
        dns_servers: Optional[list] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Updates a subnet.

        Args:
            uuid (str): The UUID of the subnet.
            gateway_address (str, optional): The gateway address of the subnet. Defaults to None.
            dns_servers (list, optional): A list of custom DNS resolver IP addresses. Defaults to None.
            tags (dict, optional): The tags assigned to the subnet. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            "gateway_address": gateway_address,
            "dns_servers": dns_servers,
            "tags": tags,
        }
        return super().update(uuid=uuid, payload=payload)
