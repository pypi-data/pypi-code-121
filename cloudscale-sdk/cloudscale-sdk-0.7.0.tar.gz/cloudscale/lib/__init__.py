from typing import Optional

from cloudscale.http import RestAPIClient

from ..error import CloudscaleApiException, CloudscaleException  # noqa F401


class CloudscaleBase:

    resource: str = ""

    def __init__(self, config):
        """
        :param config: Cloudscale
        :return self
        """
        self._client = RestAPIClient(
            api_token=config.api_token,
            api_url=config.api_url,
            user_agent=f"cloudscale-sdk {config.version}",
            timeout=config.timeout,
        )

    def _process_response(self, response: dict):
        status_code: int = int(response.get("status_code"))
        if status_code not in (200, 201, 204):
            data: dict = response.get("data", dict())
            raise CloudscaleApiException(
                f"API Response Error ({status_code}): {data.get('detail', data)}",
                response=response,
                status_code=status_code,
            )
        return response.get("data")

    def get_all(self, path: str = "", filter_tag: Optional[str] = None) -> list:
        """Lists all API resources.

        Args:
            path (str, optional): Path the resource is located under. Default to "".
            filter_tag (str, optional): Filter by tag in format <key>=<value> or <key>. Defaults to None.

        Returns:
            list: API data response.
        """
        if filter_tag is not None:
            if "=" in filter_tag:
                tag_key, tag_value = filter_tag.split("=")
            else:
                tag_key = filter_tag
                tag_value = None

            if not tag_key.startswith("tag:"):
                tag_key = f"tag:{tag_key}"

            payload = {tag_key: tag_value}
        else:
            payload = None

        result = self._client.get_resources(self.resource + path, payload=payload)

        return self._process_response(result) or list()


class CloudscaleBaseExt(CloudscaleBase):
    def get_by_uuid(self, uuid: str, path: str = "") -> dict:
        """Queries an API resource by UUID.

        Args:
            uuid (str): UUID of the resource.
            path (str, optional): Path the resource is located under. Default to "".

        Returns:
            dict: API data response.
        """
        response = self._client.get_resources(self.resource + path, resource_id=uuid)
        return self._process_response(response) or dict()


class CloudscaleMutable(CloudscaleBaseExt):
    def delete(self, uuid: str, path: str = ""):
        """Deletes an API resource by UUID.

        Args:
            uuid (str): UUID of the resource.
            path (str, optional): Path the resource is located under. Default to "".

        Returns:
            dict: API data response.
        """
        response = self._client.delete_resource(self.resource + path, resource_id=uuid)
        return self._process_response(response)

    def update(self, uuid: str, payload: dict, path: str = "") -> dict:
        """Updates an API resource by UUID.

        Args:
            uuid (str): UUID of the resource.
            payload (dict): API arguments.
            path (str, optional): Path the resource is located under. Default to "".

        Returns:
            dict: API data response.
        """
        response = self._client.post_patch_resource(
            self.resource + path, resource_id=uuid, payload=payload
        )
        return self._process_response(response) or dict()

    def create(self, payload: dict, path: str = "") -> dict:
        """Creates an API resource.

        Args:
            payload (dict): API arguments.
            path (str, optional): Path the resource is located under. Default to "".

        Returns:
            dict: API data response.
        """
        response = self._client.post_patch_resource(
            self.resource + path, payload=payload
        )
        return self._process_response(response) or dict()
