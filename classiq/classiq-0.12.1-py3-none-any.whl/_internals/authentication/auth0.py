import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from httpx import AsyncClient, Response, codes

from classiq.interface.server import authentication

from classiq.exceptions import ClassiqAuthenticationError


@dataclass
class Tokens:
    access_token: str
    refresh_token: Optional[str]


class Auth0:
    _SDK_CLIENT_ID = "f6721qMOVoDAOVkzrv8YaWassRKSFX6Y"
    _CONTENT_TYPE = "application/x-www-form-urlencoded"
    _HEADERS = {"content-type": _CONTENT_TYPE}
    _BASE_URL = f"https://{authentication.AUTH0_DOMAIN}"

    @classmethod
    async def _make_request(
        cls,
        url: str,
        payload: Dict[str, str],
        allow_error: Union[bool, int] = False,
    ) -> Dict[str, Any]:
        encoded_payload = urllib.parse.urlencode(payload)
        client: AsyncClient
        async with AsyncClient(base_url=cls._BASE_URL, headers=cls._HEADERS) as client:
            response: Response = await client.post(url=url, content=encoded_payload)
            code = response.status_code
            error_code_allowed = allow_error is True or allow_error == code
            data = response.json()

        if code == codes.OK or error_code_allowed:
            return data

        raise ClassiqAuthenticationError(
            f"Request to Auth0 failed with error code {code}: {data.get('error')}"
        )

    @classmethod
    async def get_device_data(cls, get_refresh_token: bool = True) -> Dict[str, Any]:
        payload = {
            "client_id": cls._SDK_CLIENT_ID,
            "audience": authentication.API_AUDIENCE,
        }
        if get_refresh_token:
            payload["scope"] = "offline_access"

        return await cls._make_request(
            url="/oauth/device/code",
            payload=payload,
        )

    @classmethod
    async def poll_tokens(cls, device_code: str) -> Dict[str, Any]:
        payload = {
            "client_id": cls._SDK_CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }

        return await cls._make_request(
            url="/oauth/token",
            payload=payload,
            allow_error=codes.FORBIDDEN,
        )

    @classmethod
    async def refresh_access_token(cls, refresh_token: str) -> Tokens:
        # TODO handle failure
        payload = {
            "client_id": cls._SDK_CLIENT_ID,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        data = await cls._make_request(
            url="/oauth/token",
            payload=payload,
        )

        return Tokens(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", None),
        )
