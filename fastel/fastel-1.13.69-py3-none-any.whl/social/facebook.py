from typing import Any, Dict
from urllib.parse import quote_plus, urlencode

import requests

from fastel.exceptions import APIException
from fastel.social import SocialModel


class FacebookLogin:
    def __init__(self, data: SocialModel) -> None:
        self.project_client_id = data.project_client_id
        self.project_api_host = data.project_api_host
        self.client_id = data.client_id
        self.client_secret = data.client_secret

        self.CALLBACK_URL = f"{self.project_api_host}/facebook/callback"
        self.FACEBOOK_AUTH_DIALOG = f"https://www.facebook.com/v9.0/dialog/oauth?client_id={self.client_id}&redirect_uri={self.CALLBACK_URL}&scope=email,public_profile"
        self.FACEBOOK_URL = "https://graph.facebook.com"

    def redirect(self, state: str) -> str:
        url = self.FACEBOOK_AUTH_DIALOG + f"&state={state}"
        return url

    def callback(self, state: Dict[str, Any], code: str) -> Dict[str, Any]:
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.CALLBACK_URL,
            "code": code,
        }
        path = urlencode(query=payload, quote_via=quote_plus)  # type: ignore
        resp = requests.get(self.FACEBOOK_URL + "/v9.0/oauth/access_token?" + path)

        try:
            resp.raise_for_status()
            resp_json = resp.json()
            access_token = resp_json["access_token"]
        except Exception as e:
            raise APIException(
                status_code=401,
                error="callback_error",
                detail=str(e),
            )

        return self.get_profile(access_token)

    def get_profile(self, access_token: str) -> Dict[str, Any]:
        profile_resp = requests.get(
            self.FACEBOOK_URL
            + f"/v9.0/me?fields=name,email,id&access_token={access_token}"
        )
        profile = profile_resp.json()
        result = {}
        try:
            result["social_id"] = profile["id"]
            result["provider"] = "facebook"
        except Exception:
            raise APIException(
                status_code=403, error="get_profile_error", detail=profile["error"]
            )

        try:
            result["email"] = profile["email"]
            result["name"] = profile["name"]
        except Exception:
            print(
                f"[WARNING] fb social user {result['social_id']} doesn't have email or name"
            )

        return result
