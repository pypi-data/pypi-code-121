from pyarrow.flight import (  # type: ignore
    FlightCancelledError,
    FlightClient,
    FlightUnauthenticatedError,
    FlightUnavailableError,
)

from tktl.core.clients import API
from tktl.core.config import settings as tktl_settings
from tktl.core.exceptions import APIClientException


def check_rest_health():
    client = API(api_base=tktl_settings.LOCAL_REST_ENDPOINT)
    assert client.call(verb="get", path="healthz", raw=True).status_code == 204


def check_grpc_health():
    try:
        client = FlightClient(
            tls_root_certs=None,
            location=tktl_settings.LOCAL_ARROW_ENDPOINT,
        )
        client.wait_for_available(timeout=1)
    except FlightUnauthenticatedError:
        return True
    except (FlightCancelledError, FlightUnavailableError) as e:
        error_str = f"Service is not running properly: {repr(e.detail)}"
        raise APIClientException(detail=error_str, status_code=e.status_code)
