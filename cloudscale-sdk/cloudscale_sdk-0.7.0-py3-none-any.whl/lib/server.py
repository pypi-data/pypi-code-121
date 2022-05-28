from typing import Optional

from . import CloudscaleMutable


class Server(CloudscaleMutable):
    resource = "servers"

    def create(
        self,
        name: str,
        flavor: str,
        image: str,
        zone: Optional[str] = None,
        volume_size: Optional[int] = None,
        volumes: Optional[list] = None,
        interfaces: Optional[list] = None,
        ssh_keys: Optional[list] = None,
        password: Optional[str] = None,
        use_public_network: Optional[bool] = None,
        use_private_network: Optional[bool] = None,
        use_ipv6: Optional[bool] = None,
        server_groups: Optional[list] = None,
        user_data: Optional[str] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Creates a server.

        Args:
            name (str): The name of the server.
            flavor (str): The flavor of the server.
            image (str): The image of the server.
            zone (str, optional): The zone the server is created in. Defaults to None.
            volume_size (int, optional): The volume size of the server. Defaults to None.
            volumes (list, optional): A list of volumes to be created and attached to the server. Defaults to None.
            interfaces (list, optional): A list of interfacs to be attached to the server. Defaults to None.
            ssh_keys (list, optional): A list of SSH public keys to be placed on the server. Defaults to None.
            password (str, optional): The password of the default user of the server. Defaults to None.
            use_public_network (bool, optional): Attach a public network interface to the server. Defaults to None.
            use_private_network (bool, optional): Attach a private network interface to the server. Defaults to None.
            use_ipv6 (bool, optional): Enable IPv6 on the public network interface of the server. Defaults to None.
            server_groups (list, optional): A list of server groups UUIDs the server should be placed in. Defaults to None.
            user_data (str, optional): The user data startup config. Defaults to None.
            tags (dict, optional): The tags assigned to the server. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            "name": name,
            "flavor": flavor,
            "image": image,
            "zone": zone,
            "volumes": volumes,
            "interfaces": interfaces,
            "ssh_keys": ssh_keys,
            "password": password,
            "use_public_network": use_public_network,
            "use_private_network": use_private_network,
            "use_ipv6": use_ipv6,
            "server_groups": server_groups,
            "user_data": user_data,
            "tags": tags,
        }
        return super().create(payload=payload)

    def update(
        self,
        uuid: str,
        name: Optional[str] = None,
        flavor: Optional[str] = None,
        interfaces: Optional[dict] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Updates a server.

        Args:
            uuid (str): The UUID of the server.
            name (str, optional): The name of the server. Defaults to None.
            flavor (str, optional): The flavor of of the server. Defaults to None.
            interfaces (dict, optional): The interfaces of the server. Defaults to None.
            tags (dict, optional): The tags assigned to the server. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            "name": name,
            "flavor": flavor,
            "interfaces": interfaces,
            "tags": tags,
        }
        return super().update(uuid=uuid, payload=payload)

    def start(self, uuid: str) -> dict:
        """Starts a server.

        Args:
            uuid (str): The UUID of the server.

        Returns:
            dict: API data response.
        """
        result = self._client.post_patch_resource(
            self.resource, resource_id=uuid, action="start"
        )
        return self._process_response(result) or dict()

    def stop(self, uuid: str) -> dict:
        """Stops a server.

        Args:
            uuid (str): The UUID of the server.

        Returns:
            dict: API data response.
        """
        result = self._client.post_patch_resource(
            self.resource, resource_id=uuid, action="stop"
        )
        return self._process_response(result) or dict()

    def reboot(self, uuid: str) -> dict:
        """Reboots a server.

        Args:
            uuid (str): The UUID of the server.

        Returns:
            dict: API data response.
        """
        result = self._client.post_patch_resource(
            self.resource, resource_id=uuid, action="reboot"
        )
        return self._process_response(result) or dict()
