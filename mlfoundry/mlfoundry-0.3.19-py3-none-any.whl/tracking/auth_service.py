from mlflow.utils.rest_utils import MlflowHostCreds, http_request_safe

from mlfoundry.tracking.entities import TenantInfo


class AuthService:
    def __init__(self, tenant_info: TenantInfo):
        self.host_creds = MlflowHostCreds(host=tenant_info.auth_server_url)
        self.tenant_id = tenant_info.tenant_id

    def get_token(self, api_key: str) -> str:
        response = http_request_safe(
            host_creds=self.host_creds,
            endpoint="/api/v1/oauth/api-keys/token",
            method="post",
            json={"apiKey": api_key, "clientId": self.tenant_id},
        )
        response = response.json()
        token = response["accessToken"]
        return token
