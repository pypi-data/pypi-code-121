"""API for working with transformation tasks."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_task_uri():
    """Get endpoint URI pattern for a transformation task."""
    path = "/transform/tasks/{}/{}"
    return config.get_di_api_endpoint() + path


def get_transformation_task(project_name, task_name):
    """GET retrieve transformation task."""
    headers = {"Accept": "application/json"}
    response = send_request(
        get_task_uri().format(project_name, task_name),
        method="GET",
        headers=headers
    )
    return json.loads(response.decode("utf-8"))


def make_new_transformation_task(project_name, task_name, data=None):
    """PUT create transformation task."""
    headers = {"Content-Type": "application/json"}
    send_request(
        get_task_uri().format(project_name, task_name),
        method="PUT",
        data=data,
        headers=headers
    )


def delete_transformation_task(project_name, task_name,
                               remove_dependent_tasks=False):
    """DELETE transformation task."""
    params = {"removeDependentTasks": str(remove_dependent_tasks).lower()}
    send_request(
        get_task_uri().format(project_name, task_name),
        method="DELETE",
        params=params
    )
