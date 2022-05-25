import requests
from ..env import Environment


class IAM:
    def __init__(self, env: Environment):
        realm = env.get("IAM_REALM")
        host = env.get("IAM_HOST", default="iam.avd.al")
        protocol = env.get("IAM_PROTOCOL", default="https")

        self.client_id = env.get("IAM_CLIENT_ID")
        self.client_secret = env.get("IAM_CLIENT_SECRET")

        self.token_endpoint = f"{protocol}://{host}/auth/realms/{realm}/protocol/openid-connect/token"

    def access_token(self):
        h = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        d = f"grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}"
        response = requests.request("POST", self.token_endpoint, headers=h, data=d)

        if not response.ok:
            raise Exception(response.json())

        return response.json()["access_token"]
