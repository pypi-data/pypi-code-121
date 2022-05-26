"""
Unleash Feature Toggles Module for accessing Unleash Server via API_TOKEN
"""

import requests
import json
from UnleashClient import UnleashClient as unleash_client


class UnleashAdmin:
    def __init__(self, address, admin_auth_token):
        self.headers = {
            "Authorization": admin_auth_token,
            "Content-Type": "application/json",
        }
        self.admin_uri = f"{address}/api/admin"
        self.address = address

    def get_server_health(self):
        url = f"{self.address}/health"
        try:
            res = requests.get(url=url)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def create_feature_toggle(self, input):
        """
        Used to create a toggle.
        `name` MUST BE GLOBALLY UNIQUE, otherwise 403
        `type` is optional. Defaults to `release`

        Input:
        POST
        {
            "name": "Feature.A",
            "description": "lorem ipsum..",
            "type": "release",
            "enabled": false,
            "stale": false,
            "strategies": [
                {
                    "name": "default",
                    "parameters": {}
                }
            ]
        }
        """
        url = f"{self.admin_uri}/features"
        try:
            res = requests.post(url=url, headers=self.headers, data=json.dumps(input))
            res.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def get_feature_toggles(self):
        """
        Used to get all feature toggles
        """
        url = f"{self.admin_uri}/features"
        try:
            res = requests.get(url=url, headers=self.headers)
            res.raise_for_status()
            data = res.json()
            return data["features"]
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def get_feature_toggle(self, feature_name):
        """
        Used to get a feature toggle by name
        """
        url = f"{self.admin_uri}/features/{feature_name}"
        try:
            res = requests.get(url=url, headers=self.headers)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def update_feature_toggle(self, feature_name, input):
        """
        Used to update a toggle, or add variants, or modify variants, strategies, description, etc.

        Input:
        PUT
        {
            "name": "Feature.A",
            "description": "lorem ipsum..",
            "type": "release",
            "enabled": false,
            "stale": false,
            "strategies": [
                {
                    "name": "default",
                    "parameters": {}
                }
            ],
            "variants": [
                {
                    "name": "variant1",
                    "weight": 1000,
                    "payload": {
                        "type": "json",
                        "value": "<JSONSTRING>"
                    },
                    "weightType": "variable or fix",
                    "stickiness": "default"
                }
            ]
        }
        """
        url = f"{self.admin_uri}/features/{feature_name}"
        try:
            res = requests.put(url=url, headers=self.headers, data=json.dumps(input))
            res.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def update_feature_variants(self, feature_name, input_variants):
        """
        Used to add/update feature toggle variants.
        NOTE: It WILL OVERWRITE existing variants.
        Input:
        ```json
        {
            "name": "variant1",
            "weight": 1000,
            "payload": {
                "type": "json/string/csv",
                "value": "{ 'variant_name': 'variant1', 'model_id': 'model_id', 'endpoint_name': 'model_endpoint_name' }"
            }
            "weightType": "variable/fix"
        }
        ```
        """
        # Check if feature toggle existing, get existing data
        feat_toggle = self.get_feature_toggle(feature_name)
        if feat_toggle:
            feat_toggle["variants"] = input_variants

            # Update feature toggle
            self.update_feature_toggle(feature_name, feat_toggle)
            return feat_toggle
        else:
            raise Exception("ERROR - ADD FEATURE VARIANTS: Feature toggle not existing")

    def tag_feature_toggle(self, feature_name, type, value):
        """
        Used to tag a feature

        Input:
        POST
        {
            "type": "new-user",
            "value": "gbdt"
        }
        """
        url = f"{self.admin_uri}/features/{feature_name}/tags"
        input = {"type": type, "value": value}
        try:
            res = requests.post(url=url, headers=self.headers, data=json.dumps(input))
            res.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def remove_tag_feature_toggle(self, feature_name, type, value):
        """
        Used to remove tag from a feature toggle
        """
        url = f"{self.admin_uri}/features/{feature_name}/tags/{type}/{value}"
        try:
            res = requests.delete(url=url, headers=self.headers)
            res.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def enable_feature_toggle(self, feature_name):
        """
        Used to enable a feature toggle
        """
        url = f"{self.admin_uri}/features/{feature_name}/toggle/on"
        try:
            res = requests.post(url=url, headers=self.headers, json={})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def disable_feature_toggle(self, feature_name):
        """
        Used to disable a feature toggle
        """
        url = f"{self.admin_uri}/features/{feature_name}/toggle/off"
        try:
            res = requests.post(url=url, headers=self.headers, json={})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def archive_feature_toggle(self, feature_name):
        """
        Used to archive a feature toggle
        """
        url = f"{self.admin_uri}/features/{feature_name}"
        try:
            res = requests.delete(url=url, headers=self.headers)
            res.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def mark_stale_feature_toggle(self, feature_name):
        """
        Used to mark a feature toggle as stale
        """
        url = f"{self.admin_uri}/features/{feature_name}/stale/on"
        try:
            res = requests.post(url=url, headers=self.headers)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise

    def mark_active_feature_toggle(self, feature_name):
        """
        Used to mark a feature toggle as active
        """
        url = f"{self.admin_uri}/features/{feature_name}/stale/off"
        try:
            res = requests.post(url=url, headers=self.headers)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as errh:
            print("HTTP ERROR:", errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("CONNECTION ERROR:", errc)
            raise
        except requests.exceptions.Timeout as errt:
            print("TIMEOUT ERROR:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("REQEUST ERROR:", err)
            raise


class UnleashClient:
    def __init__(
        self,
        address,
        auth_token,
        app_name,
        refresh_interval=15,
    ):
        self.client = unleash_client(
            url=f"{address}/api",
            app_name=app_name,
            custom_headers={"Authorization": auth_token},
            refresh_interval=refresh_interval,
        )
        self.client.initialize_client()

    def get_variant(self, feature_name, context=None):
        return self.client.get_variant(feature_name, context)
