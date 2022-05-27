import requests
from datetime import datetime, timedelta

from src.listrak import email


class Listrak:
    """https://api.listrak.com/email
    """
    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret

        self._root_endpoint = "https://api.listrak.com"
        self._session = requests.Session()
        self._get_auth_token_data()

        self.uri_list = email.ListEndpoint(self._root_endpoint, self._session)
        self.uri_list_import = email.ListImportEndpoint(self._root_endpoint, self._session)
        self.uri_contact = email.ContactEndpoint(self._root_endpoint, self._session)
        self.uri_segmentation_field = email.SegmentationFieldEndpoint(self._root_endpoint, self._session)
        self.uri_segmentation_field_group = email.SegmentationFieldGroupEndpoint(self._root_endpoint, self._session)

    def _get_auth_token_data(self) -> None:
        """Authenticate using OAuth 2.0.
        Returns bearer token which is used for all subsequent API calls.
        Datetime is calculated for when the bearer token will expire (1 hour).
        https://api.listrak.com/email#section/Authentication
        """
        body = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret
        }
        r = requests.post("https://auth.listrak.com/OAuth2/Token", data=body)
        try:
            r.raise_for_status()
            self._session.headers.update({"Authorization": f"Bearer {r.json()['access_token']}"})
            self._auth_expire_dt = datetime.now() + timedelta(seconds=r.json()["expires_in"])
        except requests.exceptions.HTTPError as e:
            print(e)
        return
