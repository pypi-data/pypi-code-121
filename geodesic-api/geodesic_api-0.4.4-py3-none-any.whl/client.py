import json
import os

import requests

from geodesic.config import ConfigManager
from geodesic.oauth import AuthManager

os.environ["AWS_NO_SIGN_REQUEST"] = "YES"

DEBUG = os.getenv("DEBUG", "false")

if DEBUG.lower() in ("1", "true", "yes", "external"):
    DEBUG = True
else:
    DEBUG = False

API_VERSION = 1
client = None


def get_client():
    global client
    if client is not None:
        return client

    client = Client()
    return client


def raise_on_error(res: requests.Response) -> requests.Response:
    """
    Checks a Response for errors. Returns the original Response if none are found.
    """
    try:
        if res.status_code >= 400:
            try:
                res_json = res.json()
                if 'error' in res_json:
                    raise requests.exceptions.HTTPError(res_json)
            except json.decoder.JSONDecodeError:
                raise requests.exceptions.HTTPError(res.text)
        return res
    except Exception as e:
        raise requests.exceptions.HTTPError(e, res.text[:200])


class Client:
    def __init__(self):
        self._auth = AuthManager()
        self._conf = ConfigManager()
        self._conf.get_active_config()
        self._session = None
        self._api_version = API_VERSION

    def request(self, uri, method="GET", **params):
        # Get the active config, this could have been switched at runtime.
        # Note: doesn't sync with config file, must be explicitly reloaded.
        cfg = self._conf.get_active_config()

        url = cfg.host
        if url.endswith("/"):
            url = url[:-1]

        # Route request to correct endpoint
        if uri.startswith("/spacetime"):
            uri = uri.replace("/spacetime", "", 1)
            url = f"{cfg.service_host('spacetime')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/entanglement"):
            uri = uri.replace("/entanglement", "", 1)
            url = f"{cfg.service_host('entanglement')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/tesseract"):
            uri = uri.replace("/tesseract", "", 1)
            url = f"{cfg.service_host('tesseract')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/krampus"):
            uri = uri.replace("/krampus", "", 1)
            url = f"{cfg.service_host('krampus')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/"):
            url = url + uri

        if uri.startswith("http"):
            url = uri

        send_auth_headers = False
        if cfg.host in url:
            send_auth_headers = True

        if method == "GET":
            req = requests.Request("GET", url, params=params)
        elif method == "POST":
            req = requests.Request("POST", url, json=params)
        elif method == "PUT":
            req = requests.Request("PUT", url, json=params)
        elif method == "DELETE":
            body = params.get("__delete_body", None)
            if body is not None:
                req = requests.Request("DELETE", url, json=body)
            else:
                req = requests.Request("DELETE", url, params=params)
        else:
            raise Exception(f"unknown method: {method}")

        # Only send headers for requests to our services, but client could be used instead of requests if you choose.
        if send_auth_headers:
            req.headers["Authorization"] = "Bearer {0}".format(self._auth.id_token)
            req.headers["X-Auth-Request-Access-Token"] = "Bearer {0}".format(self._auth.access_token)

        if self._session is None:
            self._session = requests.Session()

        prepped = req.prepare()

        res = self._session.send(prepped)

        return res

    def get(self, uri, **query):
        return self.request(uri, method="GET", **query)

    def post(self, uri, **body):
        return self.request(uri, method="POST", **body)

    def put(self, uri, **body):
        return self.request(uri, method="PUT", **body)

    def delete(self, uri, **query):
        return self.request(uri, method="DELETE", **query)

    def delete_with_body(self, uri, **body):
        return self.request(uri, method="DELETE", __delete_body=body)
