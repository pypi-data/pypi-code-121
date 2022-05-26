"""API for working with several workflows."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_workflow_uri():
    """Get endpoint URI pattern for a workflow."""
    path = "/workflow/workflows/{}"
    return config.get_di_api_endpoint() + path


def get_workflows(project_name):
    """GET retrieve list of workflows."""
    response = send_request(get_workflow_uri().format(project_name),
                            method="GET")
    return json.loads(response.decode("utf-8"))
