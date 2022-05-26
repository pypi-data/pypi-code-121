"""API for health and version information."""
import json
import re

from requests import HTTPError

from cmem.cmempy import config
from cmem.cmempy.api import send_request
from cmem.cmempy.queries import SparqlQuery

SHAPE_CATALOG_VERSION_QUERY = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <https://vocab.eccenca.com/shacl/>
SELECT ?version
FROM :
WHERE {
  : owl:versionInfo ?version
}
ORDER BY ASC(?version)
"""


def get_dp_health_endpoint():
    """Get DataPlatform health endpoint."""
    return config.get_dp_api_endpoint() + "/actuator/health"


def get_dp_info_endpoint():
    """Get DataPlatform version endpoint."""
    return config.get_dp_api_endpoint() + "/actuator/info"


def get_di_health_endpoint():
    """Get DataPlatform health endpoint."""
    return config.get_di_api_endpoint() + "/health"


def get_di_version_endpoint():
    """Get DataPlatform version endpoint."""
    return config.get_di_api_endpoint() + "/version"


def get_dm_version_endpoint():
    """Get DataManager version endpoint."""
    return config.get_cmem_base_uri() + "/version.html"


def get_shape_catalog_version():
    """GET version of the ShapeCatalog."""
    try:
        results = SparqlQuery(
            SHAPE_CATALOG_VERSION_QUERY,
        ).get_json_results()["results"]["bindings"]
        if len(results) > 0:
            return str(results[0]["version"]["value"])
    except (KeyError, HTTPError):
        pass
    return "UNKNOWN"


def get_dm_version():
    """GET version of DataManager."""
    url = get_dm_version_endpoint()
    try:
        response = send_request(url).decode()
    except HTTPError:
        return "ERROR"
    try:
        response = re.findall(r'v[0-9]+\..*', response)[0]
        return response
    except Exception:  # pylint: disable=broad-except
        return "UNKNOWN"


def get_dp_version():
    """GET version of DataPlatform."""
    response = None
    url = get_dp_info_endpoint()
    try:
        response = send_request(url)
    except Exception:  # pylint: disable=broad-except
        response = None
        # TODO: checking health status needs to be improved
    if response is None:
        url = url.replace("/actuator", "")
        response = send_request(url)
    result = json.loads(response)
    return result["version"]


def dp_is_healthy():
    """Check status of DataIntegration."""
    url = get_dp_health_endpoint()
    try:
        response = send_request(url)
    except Exception:  # pylint: disable=broad-except
        response = None
        # TODO: checking health status needs to be improved
    if response is None:
        url = url.replace("/actuator", "")
        response = send_request(url)
    result = json.loads(response)
    if result['status'] == "UP":
        return True
    return False


def get_di_version():
    """GET version of DataIntegration."""
    response = send_request(get_di_version_endpoint())
    return response.decode("utf-8")


def di_is_healthy():
    """Check status of DataIntegration."""
    try:
        result = json.loads(send_request(get_di_health_endpoint()))
    except ValueError:
        return False
    if result['status'] == "UP":
        return True
    return False
