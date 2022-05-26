"""API for working with custom tasks."""
from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_custom_tasks_uri():
    """Get endpoint URI pattern for a custom task."""
    path = "/workspace/projects/{}/customTasks/{}"
    return config.get_di_api_endpoint() + path


def get_custom_task(project_name, task_name):
    """GET retrieve custom task for the project."""
    response = send_request(
        get_custom_tasks_uri().format(project_name, task_name),
        method="GET"
    )
    return response.decode("utf-8")


def create_custom_task(project_name, task_name, data=None):
    """PUT create custom task for the project."""
    headers = {"Content-Type": "text/xml"}
    send_request(
        get_custom_tasks_uri().format(project_name, task_name),
        method="PUT",
        data=data,
        headers=headers
    )


def delete_custom_task(project_name, task_name):
    """DELETE remove custom task from the project."""
    send_request(
        get_custom_tasks_uri().format(project_name, task_name),
        method="DELETE"
    )
