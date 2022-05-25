import os
import requests
import warnings

from typing import Optional, Any

from ..base.logger import MetaLogger


__all__ = ["create_agent"]


class Agent(metaclass=MetaLogger):
    """
    Manages the connection to Carta.
    """
    def __init__(self, *args, **kwds):
        """
        Parameters
        ----------
        url : str
            Base URL to access Carta.
        auth : str
            Authorization key used to access the Carta API.
        """
        # Carta base URL can be specified, read from an environment variable
        # or a global default.
        self._url = kwds.get("url") or os.environ.get(
            "CARTA_URL",
            "https://dev.carta.contextualize.us.com/api"
        )
        # Authentication token used to access Carta.
        self.__auth = kwds.get("auth")

    @property
    def auth(self):
        warnings.warn("Authentication token cannot be accessed.")
    @auth.setter
    def auth(self, token: str):
        self.__auth = token

    @property
    def url(self):
        return self._url
    @url.setter
    def url(self, url: str):
        if not url.strip("/").endswith("api"):
            self.logger.info("URL does not end in 'api', adding 'api'")
            url = url.strip("/") + "/api"
        self._url = url

    def endpoint(self, *path):
        return self.url.strip("/") + "/" + "/".join([p.strip("/") for p in path])
        # return os.path.join(self.url, *path)

    def _set_auth(self, kwds: dict[str, Any]):
        kwds["cookies"] = {
            **{"CartaAuth": self.__auth},
            **kwds.get("cookies", dict())
        }
        return kwds

    def get(self, endpoint, **kwds):
        """
        Perform a `GET` operation using the default parameters, if
        not specified. This function accepts all parameters valid for
        `requests.get`, but provides defaults for Carta-specific
        requirements stored by this Agent.

        Parameters
        ----------
        endpoint : str
            Endpoint from the base URL to access.

        Example
        -------

            agent = Agent(url="https://localhost:5001/api")
            response = agent.get("user") # calls GET("https://localhost:5001/api/user")
        """
        url = self.endpoint(endpoint)
        kwds = self._set_auth(kwds)
        return requests.get(url, **kwds)

    def post(self, endpoint, **kwds):
        """
        Perform a `POST` operation using the default parameters, if
        not specified. This function accepts all parameters valid for
        `requests.post`, but provides defaults for Carta-specific
        requirements stored by this Agent.

        Parameters
        ----------
        endpoint : str
            Endpoint from the base URL to post.
        data/json : dict or str
            Data to be posted. Use `data` if the data is already JSON-encoded.
            If not, `json` will automatically encode the dict.

        Example
        -------

            agent = Agent(url="https://localhost:5001/api")
            package = {"foo": "bar"}
            response = agent.post("user", data=package)
        """
        url = self.endpoint(endpoint)
        kwds = self._set_auth(kwds)
        return requests.post(url, **kwds)

    def delete(self, endpoint, **kwds):
        """
        Perform a `DELETE` operation using the default parameters, if
        not specified. This function accepts all parameters valid for
        `requests.delete`, but provides defaults for Carta-specific
        requirements stored by this Agent.

        Parameters
        ----------
        endpoint : str
            Endpoint from the base URL to delete.

        Example
        -------

            agent = Agent(url="https://localhost:5001/api")
            response = agent.delete("user/0")
        """
        url = self.endpoint(endpoint)
        kwds = self._set_auth(kwds)
        return requests.delete(url, **kwds)


def create_agent(token: str, url: Optional[str]=None):
    """
    Creates an Agent to handle communications to/from the Carta server.

    Parameters
    ----------
    token : str
        User authentication token to access Carta.
    url : str (optional)
        URL for the Carta instance.
    """
    agent = Agent()
    agent.auth = token
    if url: agent.url = url
    return agent
