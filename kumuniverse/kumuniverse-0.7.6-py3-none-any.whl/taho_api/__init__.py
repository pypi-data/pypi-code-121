"""
Taho API Module for calling endpoints.
"""

import requests
import json


class TahoAPI:
    def __init__(self, env="dev"):
        """
        Initializes the Taho API.

        Parameters
        ----------
        env : str, optional
            Environment to be called (e.g. live or dev) (default is "dev")

        Attributes
        ----------
        base_url : str
            Base URL of the Taho API endpoint

        headers : Object
            Headers to be passed into requests
        """
        self.base_url = f"https://{env}-taho.kumuapi.com/v1"
        self.headers = {"Content-Type": "application/json"}

    def get_feature_toggle(self, feature_toggle_name, properties=None):
        """
        Retrieves the feature toggle for the specified request properties body.

        Parameters
        ----------
        feature_toggle_name: str, required
            Feature toggle to be retrieved

        properties : JSON object, optional
            Takes in `os` and `build_version` attributes (default is None)

            {os: str, build_version: int}

            Example ::
                {
                    "os": "android",
                    "build_version": 980
                }

        Returns
        -------
        Python object
        """
        feature_toggle_url = self.base_url + f"/toggles/{feature_toggle_name}"
        try:
            if properties is None:
                res = requests.get(url=feature_toggle_url, headers=self.headers)
            else:
                res = requests.get(
                    url=feature_toggle_url,
                    data=json.dumps(properties),
                    headers=self.headers,
                )
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as errh:
            raise ("HTTP ERROR:", errh)
        except requests.exceptions.ConnectionError as errc:
            raise ("CONNECTION ERROR:", errc)
        except requests.exceptions.Timeout as errt:
            raise ("TIMEOUT ERROR:", errt)
        except requests.exceptions.RequestException as err:
            raise ("REQEUST ERROR:", err)
