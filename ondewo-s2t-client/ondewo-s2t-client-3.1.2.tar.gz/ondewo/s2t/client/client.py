from ondewo.utils.base_client import BaseClient
from ondewo.utils.base_client_config import BaseClientConfig

from ondewo.s2t.client.services.speech_to_text import Speech2Text
from ondewo.s2t.client.services_container import ServicesContainer


class Client(BaseClient):
    """
    The core python client for interacting with ONDEWO S2T services.
    """

    def _initialize_services(self, config: BaseClientConfig, use_secure_channel: bool) -> None:
        """
        Login with the current config and setup the services in self.services

        Returns:
            None
        """
        self.services: ServicesContainer = ServicesContainer(
            speech_to_text=Speech2Text(config=config, use_secure_channel=use_secure_channel),
        )
