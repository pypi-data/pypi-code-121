from typing import Any, Dict

from jwt.algorithms import get_default_algorithms
from jwt.api_jwt import decode, decode_complete

from fastel.config import SdkConfig

from .pem_coder import pem_decode


def decode_static(token: str, pem: bool = False) -> Dict[str, Any]:
    if pem:
        return pem_decode(token)
    unverified = decode_complete(token, options={"verify_signature": False})
    signing_key = None
    signing_keys = SdkConfig.public_key
    for key in signing_keys["keys"]:
        if key["kid"] == unverified["header"]["kid"]:
            signing_key = key
            break

    algo = get_default_algorithms()["RS256"]  # type: ignore
    signing_key = algo.from_jwk(signing_key)
    verified = decode(
        token, key=signing_key, algorithms=["RS256"], options={"verify_aud": False}
    )

    return verified
