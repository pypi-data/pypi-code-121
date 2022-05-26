"""API for working with several resources."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request
from cmem.cmempy.workspace.projects.project import get_projects


def get_resources_uri():
    """Get endpoint URI pattern for resource list."""
    path = "/workspace/projects/{}/resources"
    return config.get_di_api_endpoint() + path


def get_resources(project_name):
    """GET retrieve list of resources."""
    response = send_request(get_resources_uri().format(project_name),
                            method="GET")
    return json.loads(response.decode("utf-8"))


def get_all_resources():
    """Get all resources of all projects."""
    resources = []
    for project_id in [_["name"] for _ in get_projects()]:
        for resource in list(get_resources(project_id)):
            resource["project"] = project_id
            resource["id"] = project_id + ":" + resource["name"]
            resources.append(resource)
    return resources
