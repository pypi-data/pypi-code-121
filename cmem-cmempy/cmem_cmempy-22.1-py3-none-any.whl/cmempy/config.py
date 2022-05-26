"""cmempy configuration."""
import os

import certifi


def get_cmem_user_agent():
    """Get the CMEM_USER_AGENT config value.

    The value of user agent is send with each request.
    """
    return os.environ.get(
        "CMEM_USER_AGENT",
        "unknown"
    )


def get_cmem_base_protocol():
    """Get the CMEM_BASE_PROTOCOL config value."""
    return os.environ.get(
        "CMEM_BASE_PROTOCOL",
        "http"
    )


def get_cmem_base_domain():
    """Get the CMEM_BASE_DOMAIN config value."""
    return os.environ.get(
        "CMEM_BASE_DOMAIN",
        "docker.localhost"
    )


def get_cmem_base_uri():
    """Get the CMEM_BASE_URI config value (no ending slash)."""
    return str(
        os.environ.get(
            "CMEM_BASE_URI",
            "%s://%s" % (get_cmem_base_protocol(), get_cmem_base_domain())
        )
        .strip("/")
    )


def get_ssl_verify():
    """Get the SSL_VERIFY config value."""
    ssl_verify = os.environ.get(
        "SSL_VERIFY",
        "True"
    )
    if ssl_verify.lower() == "false":
        ssl_verify = False
    else:
        ssl_verify = True
    return ssl_verify


def get_requests_ca_bundle():
    """Get the REQUESTS_CA_BUNDLE config value."""
    requests_ca_bundle = os.environ.get(
        "REQUESTS_CA_BUNDLE",
        certifi.where()
    )
    requests_ca_bundle = os.path.abspath(requests_ca_bundle)
    if not os.path.isfile(requests_ca_bundle):
        raise ValueError("The value of REQUESTS_CA_BUNDLE does not point to "
                         "a CA bundle file ({}).".format(requests_ca_bundle))
    return requests_ca_bundle


def get_di_api_endpoint():
    """Get the DI_API_ENDPOINT config value."""
    return os.environ.get(
        "DI_API_ENDPOINT",
        "%s/dataintegration" % (get_cmem_base_uri(),)
    )


def get_dp_api_endpoint():
    """Get the DP_API_ENDPOINT config value."""
    return os.environ.get(
        "DP_API_ENDPOINT",
        "%s/dataplatform" % (get_cmem_base_uri(),)
    )


def get_oauth_token_uri():
    """Get the OAUTH_TOKEN_URI config value."""
    return os.environ.get(
        "OAUTH_TOKEN_URI",
        "%s/auth/realms/cmem/protocol/openid-connect/token"
        % (get_cmem_base_uri(),)
    )


def get_oauth_grant_type():
    """Get the OAUTH_GRANT_TYPE config value."""
    valid_values = (
        "password",
        "client_credentials",
        "prefetched_token"
    )
    value = os.environ.get(
        "OAUTH_GRANT_TYPE",
        "client_credentials"
    )
    if value not in valid_values:
        raise ValueError(
            "OAUTH_GRANT_TYPE is set to {} which is not set valid value {}"
            .format(value, valid_values)
        )
    if value == "prefetched_token" and get_oauth_access_token() is None:
        raise ValueError(
            "OAUTH_GRANT_TYPE is set to 'prefetched_token', "
            "but no OAUTH_ACCESS_TOKEN is given."
        )
    return value


def get_oauth_access_token():
    """Get the OAUTH_ACCESS_TOKEN config value."""
    return os.environ.get(
        "OAUTH_ACCESS_TOKEN",
        None
    )


def get_oauth_user():
    """Get the OAUTH_USER config value."""
    default_value = None
    if get_oauth_grant_type() == "password":
        default_value = "admin"
    return os.environ.get(
        "OAUTH_USER",
        default_value
    )


def get_oauth_password():
    """Get the OAUTH_PASSWORD config value."""
    default_value = None
    if get_oauth_grant_type() == "password":
        default_value = "admin"
    return os.environ.get(
        "OAUTH_PASSWORD",
        default_value
    )


def get_oauth_client_id():
    """Get the OAUTH_CLIENT_ID config value."""
    return os.environ.get(
        "OAUTH_CLIENT_ID",
        "cmem-service-account"
    )


def get_oauth_client_secret():
    """Get the OAUTH_CLIENT_SECRET config value."""
    return os.environ.get(
        "OAUTH_CLIENT_SECRET",
        "c8c12828-000c-467b-9b6d-2d6b5e16df4a"
    )


def get_oauth_default_credentials():
    """Get the default credentials object."""
    return {
        "grant_type": get_oauth_grant_type(),
        "username": get_oauth_user(),
        "password": get_oauth_password(),
        "client_id": get_oauth_client_id(),
        "client_secret": get_oauth_client_secret()
    }


def is_chatty():
    """Check if API is in chatty mode. True means additional print outputs."""
    env = os.environ.get(
        "CMEMPY_IS_CHATTY",
        "true"
    )
    if env.lower() == "false":
        # silentio
        return False
    # oratio
    return True


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "..", "data")
