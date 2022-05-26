"""API methods for working with one project."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_projects_uri():
    """Get endpoint URI for project list."""
    path = "/workspace/projects"
    return config.get_di_api_endpoint() + path


def get_project_uri():
    """Get endpoint URI pattern for a project."""
    path = "/workspace/projects/{}"
    return config.get_di_api_endpoint() + path


def get_project_api_uri():
    """Get endpoint URI pattern for a project (new API)."""
    path = "/api/workspace/projects/{}"
    return config.get_di_api_endpoint() + path


def get_projects():
    """GET all projects."""
    response = send_request(get_projects_uri(),
                            method="GET")
    return json.loads(response.decode("utf-8"))


def get_project(name):
    """GET one project."""
    response = send_request(get_project_uri().format(name),
                            method="GET")
    return json.loads(response.decode("utf-8"))


def make_new_project(name):
    """PUT make new project."""
    response = send_request(get_project_uri().format(name),
                            method="PUT")
    return json.loads(response.decode("utf-8"))


def delete_project(name):
    """DELETE remove project."""
    send_request(get_project_uri().format(name),
                 method="DELETE")


def get_failed_tasks_report(name):
    """Get a report of tasks that could not be loaded in a project."""
    response = send_request(
        get_project_api_uri().format(name) + "/failedTasksReport",
        method="GET",
        headers={"Accept": "application/json"}
    )
    return json.loads(response.decode("utf-8"))
