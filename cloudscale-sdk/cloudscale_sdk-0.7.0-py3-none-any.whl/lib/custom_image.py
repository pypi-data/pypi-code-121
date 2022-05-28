from typing import Optional

from . import CloudscaleMutable


class CustomImage(CloudscaleMutable):
    resource = "custom-images"

    def import_by_url(
        self,
        name: str,
        url: str,
        slug: str,
        zones: list,
        user_data_handling: str,
        source_format: str,
        tags: Optional[dict] = None,
    ) -> dict:
        """Imports a custom image.

        Args:
            url (str): The URL to import the custom image from.
            name (str): The name of the custom image.
            slug (str): The slug of the custom image.
            zones (list): The zones the custom image should be placed in.
            user_data_handling (str): The user data handling.
            source_format (str): The format of the image.
            tags (dict, optional): The tags assigned to the network. Defaults to None.
        Returns:
            dict: API data response.
        """
        payload = {
            "url": url,
            "name": name,
            "slug": slug,
            "zones": zones,
            "user_data_handling": user_data_handling,
            "source_format": source_format,
            "tags": tags,
        }
        return super().create(payload=payload, path="/import")

    def get_import_by_uuid(self, uuid: str) -> dict:
        """Get the import status of a custom image by UUID.

        Args:
            uuid (str): UUID of the custom image import.

        Returns:
            dict: API data response.
        """
        return super().get_by_uuid(uuid=uuid, path="/import")

    def create(self, **kwargs):
        raise NotImplementedError

    def update(
        self,
        uuid: str,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        user_data_handling: Optional[str] = None,
        tags: Optional[dict] = None,
    ) -> dict:
        """Updates a custom image.

        Args:
            name (str, optional): The name of the custom image. Defaults to None.
            slug (str, optional): The slug of the custom image. Defaults to None.
            user_data_handling (str, optional): The user data handling of the custom image. Defaults to None.
            tags (dict, optional): The tags assigned to the network. Defaults to None.

        Returns:
            dict: API data response.
        """
        payload = {
            "name": name,
            "slug": slug,
            "user_data_handling": user_data_handling,
            "tags": tags,
        }
        return super().update(uuid=uuid, payload=payload)
