from ssb_altinn3_util.clients.auth.altinn_auth_client import AltinnAuthClient
import ssb_altinn3_util.clients.altinn.api.storage as storage_api
import ssb_altinn3_util.clients.altinn.api.application as application_api
from ssb_altinn3_util.models.basic_file import BasicFile


class AltinnApiClient:
    """
    This client implementation provides a basic interface for communication with Altinn's
    APIs required by the components in the 'Altinn3 datamottak' solution.
    """

    def __init__(
        self,
        auth_client: AltinnAuthClient,
        altinn_platform_base_url: str,
        altinn_apps_base_url: str,
    ):
        """
        :param auth_client: An instance of the AltinnAuthClient class
        :param altinn_platform_base_url: The base url for the Altinn platform.
        :param altinn_apps_base_url: The base url for Altinn's application platform
        """
        self.auth_client = auth_client
        self.altinn_platform_base_url = altinn_platform_base_url
        self.altinn_apps_base_url = altinn_apps_base_url

    def get_instance(self, instance_owner_id: int, instance_guid: str) -> str:
        """
        Retrieves an application instance from Altinn's API based on the instance owner
        and the instance's unique identifier.

        :param instance_owner_id: A unique id for the party owning the requested instance.
        :param instance_guid: A unique id representing a single instance stored in the Altinn platform.
        :return: A json representation of the requested instance
        """
        token = self.auth_client.get_altinn_auth_token()
        instance_json = storage_api.get_instance(
            token=token,
            instance_owner_id=instance_owner_id,
            instance_guid=instance_guid,
            platform_base_url=self.altinn_platform_base_url,
        )
        return instance_json

    def get_instance_data_object(
        self, instance_owner_id: int, instance_guid: str, data_guid: str
    ) -> BasicFile:
        """
        Retrieves a data object (file) belonging to a given instance.

        :param instance_owner_id: A unique id for the party owning the requested instance.
        :param instance_guid: A unique id representing a single instance stored in the Altinn platform.
        :param data_guid: A unique id representing a single data object belonging to the instance
        :return: A 'BasicFile'-object containing filename, content type and a base64 representation of the file.
        """
        token = self.auth_client.get_altinn_auth_token()
        data = storage_api.get_data_for_instance(
            token=token,
            instance_owner_id=instance_owner_id,
            instance_guid=instance_guid,
            data_guid=data_guid,
            platform_base_url=self.altinn_platform_base_url,
        )
        return data

    def confirm_completed_instance(
        self, org: str, app: str, instance_owner_id: int, instance_guid: str
    ) -> str:
        """
        Used to confirm that we have finished processing an instance (event), and it is no longer required by
        the "Altinn3 datamottak" solution.

        :param org: A string identifier for the organization (typically 'ssb')
        :param app: A string identifier for the application the instance belongs to.
        :param instance_owner_id: A unique id for the party owning the requested instance.
        :param instance_guid: A unique id representing a single instance stored in the Altinn platform.
        :return: An updated json representation of the instance, containing the confirmation
        """
        token = self.auth_client.get_altinn_auth_token()
        response = application_api.complete_instance(
            token=token,
            base_url=self.altinn_apps_base_url,
            org=org,
            app=app,
            instance_owner_party_id=instance_owner_id,
            instance_guid=instance_guid,
        )
        return response
