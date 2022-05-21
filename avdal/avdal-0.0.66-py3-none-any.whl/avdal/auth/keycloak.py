import requests


class Keycloak:
    def __init__(self, host, realm, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

        self.token_endpoint = f"https://{host}/auth/realms/{realm}/protocol/openid-connect/token"

    def access_token(self):
        h = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        d = f"grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}"
        response = requests.request("POST", self.token_endpoint, headers=h, data=d)

        if not response.ok:
            return None, response.json()

        return response.json()["access_token"], None
