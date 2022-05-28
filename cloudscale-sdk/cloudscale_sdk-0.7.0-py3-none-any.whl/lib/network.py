from typing import Optional

from . import CloudscaleMutable


class Network(CloudscaleMutable):
    resource = "networks"

    def create(
        self,
        name: str,
        zone: Optional[str] = None,
        mtu: Optional[int] = None,
        auto_create_ipv4_subnet: Optional[bool] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Creates a network.

        Args:
            name (str): The name of the network.
            zone (str, optional): The slug of the zone the network should be placed in. Defaults to None.
            mtu (int, optional): The MTU size for the network. Defaults to None.
            auto_create_ipv4_subnet (bool, optional): Create an IPv4 Subnet in the network. Defaults to None.
            tags (dict, optional): The tags assigned to the network. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            "name": name,
            "zone": zone,
            "mtu": mtu,
            "auto_create_ipv4_subnet": auto_create_ipv4_subnet,
            "tags": tags,
        }
        return super().create(payload=payload)

    def update(
        self,
        uuid: str,
        name: Optional[str] = None,
        mtu: Optional[int] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Updates a network.

        Args:
            uuid (str): The UUID of the network.
            name (str): The name of the network. Defaults to None.
            mtu (int, optional): The MTU size for the network. Defaults to None.
            tags (dict, optional): The tags assigned to the network. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            "name": name,
            "mtu": mtu,
            "tags": tags,
        }
        return super().update(uuid=uuid, payload=payload)
