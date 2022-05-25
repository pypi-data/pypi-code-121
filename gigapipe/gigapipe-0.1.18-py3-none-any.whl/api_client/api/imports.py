import requests
from http import HTTPStatus
from typing import Dict, Any
from requests import Response
from gigapipe.exceptions import GigapipeServerError, GigapipeClientError
from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Imports(Base):
    """
    Imports Class
    """

    def __init__(self, api):
        """
        Imports Constructor
        :param api: The API instance
        """
        super(Imports, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def import_s3_data(self, cluster_slug: str, payload: Dict[str, Any]) -> Response:
        """
        Imports S3 data to a database table
        :param cluster_slug: the cluster slug
        :param payload: the import payload
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/imports/s3"

        try:
            response: Response = requests.post(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=payload)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        except TypeError:
            raise GigapipeClientError(
                status_code=HTTPStatus.BAD_REQUEST,
                message=f"Wrong Payload"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_imports(self, cluster_slug: str) -> Response:
        """
        Obtains the cluster imports
        :param cluster_slug: the cluster slug
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/clusters/{cluster_slug}/imports"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response
