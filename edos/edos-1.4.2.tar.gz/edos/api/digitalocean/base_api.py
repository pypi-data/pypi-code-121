import abc
import json

from requests import request

from edos.api.constants import do_base_url
from edos.exceptions import UserReadableException
from edos.settings import conf


class DigitalOceanApi(abc.ABC):
    path = ""

    def __init__(self, token=None):
        try:
            self._token = token if token else conf.DIGITAL_OCEAN_CONFIG["token"]
        except (AttributeError, TypeError) as ex:
            raise UserReadableException(
                "Could not find DO token in {}".format(conf.CONFIG_PATH)
            ) from ex

    def create_request(self, method, url, headers, payload=None):
        try:
            response = request(method=method, url=url, headers=headers, data=payload)
            response.raise_for_status()
        except Exception as ex:
            raise UserReadableException(
                "DO API {} Request Failed: {})".format(method, url) + str(ex)
            ) from ex
        return response.json()

    def get_request(self, url, headers=None):
        if not headers:
            headers = {
                "Authorization": "Bearer " + self._token,
            }
        return self.create_request("GET", url, headers)

    def post_request(self, url, payload, headers=None):
        if not headers:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._token,
            }
        return self.create_request("POST", url, headers, json.dumps(payload))

    def delete_request(self, url, headers=None):
        if not headers:
            headers = {
                "Authorization": "Bearer " + self._token,
            }
        try:
            response = request(method="DELETE", url=url, headers=headers)
            response.raise_for_status()
        except Exception as ex:
            raise UserReadableException(
                "DO API Request Failed: {})".format(url)
            ) from ex
        return self.create_request("DELETE", url, headers)

    def build_url(self):
        return do_base_url + self.path
