from typing import Optional

from tecton import okta
from tecton_spark import conf


def get_auth_header() -> Optional[str]:
    token = okta.get_token_refresh_if_needed()
    if token:
        return f"Bearer {token}"

    token = conf.get_or_none("TECTON_API_KEY")
    if token:
        return f"Tecton-key {token}"

    return None


def request_has_token() -> bool:
    return get_auth_header() != None
