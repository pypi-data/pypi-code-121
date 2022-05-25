import cachetools.func
import json
import jwt
import urllib.request

from rygg.settings import AUTH_ISSUER

# Only try to import them if they have meaning
if AUTH_ISSUER:
    from rygg.settings import AUTH_CERTS_URL, AUTH_AUDIENCE

from django.contrib.auth import authenticate


class AuthError(Exception):
    pass


def jwt_get_username_from_payload_handler(payload):
    username = payload.get("sub").replace("|", ".")
    authenticate(remote_user=username)
    return username


@cachetools.func.ttl_cache(maxsize=1, ttl=10 * 60)
def get_certs_from_issuer():
    import ssl

    # TODO: Fix verification of the cert
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    return urllib.request.urlopen(AUTH_CERTS_URL, context=ctx).read()


@cachetools.func.ttl_cache(maxsize=1, ttl=10 * 60)
def get_keys_from_issuer():
    if not AUTH_ISSUER:
        return None

    def decode_key(jwk):
        as_json = json.dumps(jwk)
        return jwt.algorithms.RSAAlgorithm.from_jwk(as_json)

    jwks_as_json = get_certs_from_issuer()
    jwks = json.loads(jwks_as_json)
    return {jwk["kid"]: decode_key(jwk) for jwk in jwks["keys"]}


def get_issuer_key(id):
    keys = get_keys_from_issuer()
    key = keys.get(id)
    if key is None:
        raise AuthError("Public key not found.")
    return key


def jwt_decode_token(token):
    if not AUTH_ISSUER:
        return None

    header = jwt.get_unverified_header(token)
    received_key_id = header["kid"]
    key = get_issuer_key(received_key_id)

    # audience = API identifier in auth0
    ret = jwt.decode(
        token, key, audience=AUTH_AUDIENCE, issuer=AUTH_ISSUER, algorithms=["RS256"]
    )
    return ret
