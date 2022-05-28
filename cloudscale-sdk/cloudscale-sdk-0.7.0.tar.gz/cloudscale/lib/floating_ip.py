from typing import Optional

from . import CloudscaleMutable


class FloatingIp(CloudscaleMutable):
    resource = "floating-ips"

    def create(
        self,
        ip_version: int,
        prefix_length: Optional[int] = None,
        reverse_ptr: Optional[str] = None,
        server_uuid: Optional[str] = None,
        scope: Optional[str] = None,
        region: Optional[str] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Creates a floating IP.

        Args:
            ip_version (int): The IP version of the floating IP.
            prefix_length (int, optional): The prefix length of the floating IP. Defaults to None.
            reverse_ptr (str, optional): The reverse pointer of the floating IP. Defaults to None.
            server_uuid (str, optional): The destination server of the floating IP. Defaults to None.
            scope (str, optional): The scope (type) of the floating IP. Defaults to None.
            region (str, optional): The slug of the region in which the regional floating IP will be created in. Defaults to None.
            tags (dict, optional): The tags assigned to the floating IP. Defaults to None.
        Returns:
            dict: API data response.
        """
        payload = {
            "ip_version": ip_version,
            "prefix_length": prefix_length,
            "reverse_ptr": reverse_ptr,
            "server": server_uuid,
            "type": scope,
            "region": region,
            "tags": tags,
        }
        return super().create(payload=payload)

    def update(
        self,
        uuid: str,
        reverse_ptr: Optional[str] = None,
        server_uuid: Optional[str] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Updates a floating IP.

        Args:
            uuid (str): The UUID of the floating IP.
            reverse_ptr (str, optional): The reverse pointer of the floating IP. Defaults to None.
            server_uuid (str, optional): The destination server of the floating IP. Defaults to None.
            tags (dict, optional): The tags assigned to the floating IP. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            "reverse_ptr": reverse_ptr,
            "server": server_uuid,
            "tags": tags,
        }
        return super().update(uuid=uuid, payload=payload)
