"""
Malacanang API Module for calling endpoints.
"""

import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import json


class MalacanangAPI:
    def __init__(self, env="dev"):
        """
        Initializes the Malacanang API.

        Parameters
        ----------
        env : str, optional
            Environment to be called (e.g. live or dev) (default is "dev")

        Attributes
        ----------
        base_url : str
            Base URL of the Malacanang API endpoint

        headers : Object
            Headers to be passed into requests
        """
        self.base_url = f"https://{env}-malacanang.kumuapi.com/v1"
        self.headers = {"Content-Type": "application/json"}

    def get_variant(self, body):
        """
        Retrieves the variant for the specified request body.

        Parameters
        ----------
        body : Python object, required
            Takes in `user_id` and `use_case` attributes (default is None)

            Example ::
                {
                    "user_id": "user_1",
                    "use_case": "use_case_1",
                }

        Returns
        -------
        Python object
        """
        variants_url = self.base_url + "/variants"
        try:
            res = requests.get(
                url=variants_url, data=json.dumps(body), headers=self.headers
            )
            res.raise_for_status()
            return res.json()
        except HTTPError as errh:
            raise HTTPError("HTTP ERROR:", errh)
        except ConnectionError as errc:
            raise ConnectionError("CONNECTION ERROR:", errc)
        except Timeout as errt:
            raise Timeout("TIMEOUT ERROR:", errt)
        except RequestException as err:
            raise RequestException("REQUEST ERROR:", err)

    def get_use_case_variants(self, use_case, enabled=True):
        """
        Retrieves variants of a specific use case

        Parameters
        ----------
        use_case : str, required
            Name of the use case

        enabled : bool, optional
            To return active variants only or all variants

        Returns
        -------
        Python object
        """
        use_case_variants_url = (
            self.base_url
            + f"/use-cases/{use_case}/variants{ '?enabled=true' if enabled else '' }"
        )
        try:
            res = requests.get(url=use_case_variants_url, headers=self.headers)
            res.raise_for_status()
            return res.json()
        except HTTPError as errh:
            raise HTTPError("HTTP ERROR:", errh)
        except ConnectionError as errc:
            raise ConnectionError("CONNECTION ERROR:", errc)
        except Timeout as errt:
            raise Timeout("TIMEOUT ERROR:", errt)
        except RequestException as err:
            raise RequestException("REQUEST ERROR:", err)

    def get_variant_multi(self, body):
        """
        Retrieves the variants for the specified request body that contains multiple use cases for a single user.

        Parameters
        ----------
        body : Python object, required
            Takes in `user_id` and `use_case` attributes (default is None)

            Example ::
                {
                    "user_id": "user_1",
                    "use_cases": [ "use_case_1", "use_case_2", "use_case_3" ]
                }

        Returns
        -------
        Python object
        """
        multi_variants_url = self.base_url + "/variants/multi"
        try:
            res = requests.get(
                url=multi_variants_url, data=json.dumps(body), headers=self.headers
            )
            res.raise_for_status()
            return res.json()
        except HTTPError as errh:
            raise HTTPError("HTTP ERROR:", errh)
        except ConnectionError as errc:
            raise ConnectionError("CONNECTION ERROR:", errc)
        except Timeout as errt:
            raise Timeout("TIMEOUT ERROR:", errt)
        except RequestException as err:
            raise RequestException("REQUEST ERROR:", err)
