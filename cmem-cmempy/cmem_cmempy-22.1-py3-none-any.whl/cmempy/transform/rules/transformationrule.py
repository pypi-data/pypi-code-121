"""API for working with single transformation rule."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_transformation_rule_uri():
    """Get endpoint URI pattern for a transformation task rule."""
    path = "/transform/tasks/{}/{}/rule/{}"
    return config.get_di_api_endpoint() + path


def get_transformation_rule(project_name, task_name, rule_name):
    """GET transformation rule for the task by name."""
    headers = {"Accept": "application/json"}
    response = send_request(
        get_transformation_rule_uri().format(project_name,
                                             task_name,
                                             rule_name),
        method="GET",
        headers=headers
    )
    return json.loads(response.decode("utf-8"))


def update_transformation_rule(project_name, task_name, rule_name, data=None):
    """PUT update transformation rule for the task."""
    headers = {"Content-Type": "application/json"}
    send_request(
        get_transformation_rule_uri().format(project_name,
                                             task_name,
                                             rule_name),
        method="PUT",
        data=data,
        headers=headers
    )
