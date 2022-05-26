import logging
import time

import requests

from servicefoundry.internal.const import (
    AUTH_SERVER,
    AUTH_UI,
    MAX_POLLING_RETRY,
    POLLING_SLEEP_TIME_IN_SEC,
)
from servicefoundry.internal.model.session import ServiceFoundrySession
from servicefoundry.internal.util import request_handling

logger = logging.getLogger(__name__)

TRUE_FOUNDRY_AUTH_TOKEN = "TRUE_FOUNDRY_AUTH_TOKEN"


class AuthServiceClient:
    def __init__(self, host=AUTH_SERVER, auth_ui=AUTH_UI):
        self.host = host
        self.auth_ui = auth_ui

    def refresh_token(self, session: ServiceFoundrySession):
        url = f"{self.host}/api/v1/oauth/token/refresh"
        data = {"clientId": session.client_id, "refreshToken": session.refresh_token}
        res = requests.post(url, data=data)
        res = request_handling(res)
        return res["accessToken"], res["refreshToken"]

    def get_device_code(self, client_id):
        url = f"{self.host}/api/v1/oauth/device"
        data = {"clientId": client_id}
        res = requests.post(url, data=data)
        res = request_handling(res)
        return (
            f"{self.auth_ui}/authorize/device?userCode={res['userCode']}",
            res["userCode"],
            res["deviceCode"],
        )

    def poll_for_auth(self, tenant_id, device_code):
        i = 0
        while i < MAX_POLLING_RETRY:
            try:
                return self._poll_for_auth(tenant_id, device_code)
            except RetryError:
                time.sleep(POLLING_SLEEP_TIME_IN_SEC)
                i = i + 1

    def _poll_for_auth(self, tenant_id, device_code):
        url = f"{self.host}/api/v1/oauth/device/token"
        data = {"clientId": tenant_id, "deviceCode": device_code}
        res = requests.post(url, data=data)
        res = request_handling(res)
        if "message" in res and res["message"] == "authorization_pending":
            raise RetryError()
        return ServiceFoundrySession(
            tenant_id,
            res["accessToken"],
            res["refreshToken"],
            refresher=self.refresh_token,
        )

    def login_with_api_token(self, client_id, api_key):
        url = f"{self.host}/api/v1/oauth/api-keys/token"
        data = {"clientId": client_id, "apiKey": api_key}
        res = requests.post(url, data=data)
        res = request_handling(res)
        return ServiceFoundrySession(
            client_id,
            res["accessToken"],
            res["refreshToken"],
            refresher=self.refresh_token,
        )

    def validate_user_code(self, session: ServiceFoundrySession, user_code):
        url = f"{self.host}/api/v1/oauth/device/validate"
        data = {
            "clientId": session.client_id,
            "refreshToken": session.refresh_token,
            "userCode": user_code,
        }
        res = requests.post(url, data=data)
        res = request_handling(res)
        return ServiceFoundrySession(
            session.client_id,
            res["accessToken"],
            res["refreshToken"],
            self.refresh_token,
        )


class RetryError(Exception):
    def __init__(self):
        super()
