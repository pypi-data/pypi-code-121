"""API for working with rules."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_transformation_rules_uri():
    """Get endpoint URI pattern for transformation task rules."""
    path = "/transform/tasks/{}/{}/rules"
    return config.get_di_api_endpoint() + path


def get_transformation_rules(project_name, task_name):
    """GET transformation rules for the task."""
    headers = {"Accept": "application/json"}
    response = send_request(
        get_transformation_rules_uri().format(project_name, task_name),
        method="GET",
        headers=headers
    )
    return json.loads(response.decode("utf-8"))


def create_transformation_rules(project_name, task_name, data=None, xml=False):
    """GET transformation rules for the task."""
    if xml:
        headers = {"Content-Type": "application/xml"}
    else:
        headers = {"Content-Type": "application/json"}
    send_request(
        get_transformation_rules_uri().format(project_name, task_name),
        method="PUT",
        headers=headers,
        data=data
    )
