from typing import Dict
from urllib.parse import urljoin

from tecton import version
from tecton._internals.metadata_service_impl import auth_lib
from tecton._internals.metadata_service_impl.trace import get_trace_id
from tecton_spark import conf
from tecton_spark.id_helper import IdHelper


def request_headers() -> Dict[str, str]:
    """
    :return: Dictionary of request metadata.
    """
    metadata = {}

    metadata["x-request-id"] = IdHelper.generate_string_id()
    trace_id = get_trace_id()
    if trace_id:
        metadata["x-trace-id"] = trace_id

    ver = version.get_version()
    # when running from dev environment, package version might not be set
    if ver:
        metadata["x-tecton-client-version"] = ver

    workspace = conf.get_or_none("TECTON_WORKSPACE")
    if workspace:
        metadata["x-workspace"] = workspace
        # Warning: This is a hack to make it possible to integration test both EMR and Databricks
        # in a single deployment.
        if workspace.endswith("__emr"):
            metadata["x-tecton-force-emr"] = "true"

    authorization = auth_lib.get_auth_header()
    if authorization:
        metadata["authorization"] = authorization

    return metadata


def request_url() -> str:
    """
    :return: A Validated API service URL.
    """
    api_service = conf.get_or_raise("API_SERVICE")
    if "localhost" not in api_service and "ingress" not in api_service:
        assert api_service.endswith("/api"), "API_SERVICE should be formatted https://<deployment-name>.tecton.ai/api"
    return urljoin(api_service + "/", "proxy")
