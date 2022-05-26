"""API for working with project activities."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request
from cmem.cmempy.workspace.activities.projectactivity \
    import start_project_activity


def get_activities_uri():
    """Get endpoint URI pattern for activities."""
    path = "/workspace/projects/{}/activities"
    return config.get_di_api_endpoint() + path


def get_project_activities(project_name):
    """GET retrieve project activities."""
    response = send_request(
        get_activities_uri().format(project_name),
        method="GET"
    )
    return json.loads(response.decode("utf-8"))


# This function is kept here for backward compatibility
def start_activity(project_name, activity_name, blocking=False, data=None):
    """Kept for backward compatibility reasons, do not use."""
    return start_project_activity(
        project_name,
        activity_name,
        blocking=blocking,
        data=data
    )
