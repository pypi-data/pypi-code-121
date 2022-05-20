import os

import requests
from notebook.base.handlers import APIHandler
from notebook.utils import url_path_join as ujoin


class Hub_handler(APIHandler):
    """
    Hub Handler.  Currently all we do is DELETE (to shut down a running Lab
    instance) but we can extend this to do anything in the Hub REST API.
    """

    @property
    def lsstquery(self) -> str:
        return self.settings["lsstquery"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def delete(self) -> None:
        """
        Send a DELETE to the Hub API, which will result in this Lab
        instance being terminated (potentially, along with its namespace).

        We will need to make this more clever when and if we have multiple
        named servers.
        """

        user = os.environ.get("JUPYTERHUB_USER")
        if not user:
            self.log.warning("User unknown; Hub communication impossible.")
            return
        token = os.environ.get("JUPYTERHUB_API_TOKEN")
        if not token:
            self.log.warning("Token unknown; Hub communication impossible.")
            return
        api_url = os.environ.get("JUPYTERHUB_API_URL")
        if not api_url:
            self.log.warning("API URL unknown; Hub communication impossible.")
            return
        endpoint = ujoin(api_url, f"/users/{user}/server")
        # Boom goes the dynamite.
        self.log.info("Requesting DELETE from {}".format(endpoint))
        headers = {"Authorization": f"token {token}"}
        requests.delete(endpoint, headers=headers)
