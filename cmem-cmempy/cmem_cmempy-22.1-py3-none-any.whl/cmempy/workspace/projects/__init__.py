"""API methods for working with several projects."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_projects_uri():
    """Get endpoint URI for project list."""
    path = "/workspace/projects"
    return config.get_di_api_endpoint() + path


def get_projects():
    """GET list of projects."""
    response = send_request(get_projects_uri(), method="GET")
    return json.loads(response.decode("utf-8"))
