from typing import Any, List

from fastel.config import SdkConfig
from fastel.utils import requests


def validation_request(issuer: str, identity: str) -> Any:
    url = f"{SdkConfig.auth_host}/validation/request?client_id={SdkConfig.client_id}&client_secret={SdkConfig.client_secret}&issuer={issuer}"
    result = requests.post(
        url,
        json={"identity": identity},
    )
    return result.json()


def validation_confirm(validation_id: str, code: str) -> Any:
    url = f"{SdkConfig.auth_host}/validation/confirm/{validation_id}/{code}?client_id={SdkConfig.client_id}"
    result = requests.post(url, json={})
    return result.json()


def gen_token_request(identity: str, group: List[str] = []) -> Any:
    url = f"{SdkConfig.auth_host}/jwt/server/encode?client_id={SdkConfig.client_id}&client_secret={SdkConfig.client_secret}"
    result = requests.post(
        url,
        json={"id": identity, "group": group},
    )
    return result.json()


def revoke_token_request(identity: str) -> Any:
    url = f"{SdkConfig.auth_host}/jwt/revoke?client_id={SdkConfig.client_id}&client_secret={SdkConfig.client_secret}"
    result = requests.post(url, json={"sub": identity})
    return result.json()
