from pims_api_client.configurator import Configurator
from pims_api_client.client import BaseApiClient

class BaseExecutor:
    client: BaseApiClient

    def __init__(self, configurator: Configurator):
        self.configurator = configurator
        self.client = BaseApiClient(configurator)