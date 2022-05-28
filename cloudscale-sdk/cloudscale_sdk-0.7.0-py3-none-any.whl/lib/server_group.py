from typing import Optional

from . import CloudscaleMutable


class ServerGroup(CloudscaleMutable):
    resource = "server-groups"

    def create(
        self,
        name: str,
        group_type: Optional[str] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Creates a server group.

        Args:
            name (str, optional): The name of the server group.
            group_type (str, optional): The type of a server group. Defaults to None.
            tags (dict, optional): The tags assigned to the server group. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            "name": name,
            "type": group_type,
            "tags": tags,
        }
        return super().create(payload=payload)

    def update(
        self,
        uuid: str,
        name: Optional[str] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Updates a server group.

        Args:
            uuid (str): The UUID of the server group.
            name (str, optional): The name of the server group. Defaults to None.
            tags (dict, optional): The tags assigned to the server group. Defaults to None.
        Returns:
            dict: API data response.
        """
        payload = {
            "name": name,
            "tags": tags,
        }
        return super().update(uuid=uuid, payload=payload)
