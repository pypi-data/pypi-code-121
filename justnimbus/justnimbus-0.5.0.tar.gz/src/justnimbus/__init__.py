import requests

from justnimbus.exceptions import InvalidClientID
from justnimbus.model import JustNimbusModel


class JustNimbusClient:
    def __init__(self, client_id: str):
        self._client_id = client_id

    def get_data(self) -> JustNimbusModel:
        response = requests.get(url=f"https://dashboard.justnimbus.com/api/installation/{self._client_id}/data")

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            if response.status_code == 404:
                raise InvalidClientID(client_id=self._client_id) from error
            raise error

        return JustNimbusModel.from_dict(response.json())
