"""API for working with task activities."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import (
    get_json,
    send_request
)
from cmem.cmempy.workspace.activities import (
    ACTIVITY_TYPE_EXECUTE_LOCALWORKFLOW,
    VALID_ACTIVITY_STATUS,
    taskactivity
)


def get_activities_uri():
    """Get endpoint URI pattern for a activities."""
    path = "/workspace/projects/{}/tasks/{}/activities"
    return config.get_di_api_endpoint() + path


def get_task_activities(project_name, task_name):
    """GET retrieve a list of task activities."""
    response = send_request(
        get_activities_uri().format(project_name, task_name),
        method="GET"
    )
    return json.loads(response.decode("utf-8"))


# Kept here for backward compatibility
# DO NOT USE
def start_task_activity(project_name,
                        task_name,
                        activity_name=ACTIVITY_TYPE_EXECUTE_LOCALWORKFLOW,
                        blocking=False,
                        data=None):
    """POST start task activity."""
    return taskactivity.start_task_activity(
        project_name,
        task_name,
        activity_name=activity_name,
        blocking=blocking,
        data=data
    )


# Kept here for backward compatibility
# DO NOT USE
def get_activity_status(project_name, task_name, activity_name):
    """GET retrieve activity status."""
    return taskactivity.get_activity_status(
        project_name, task_name, activity_name
    )


def get_activities_status(project_name=None, status=None, activity=None):
    """Retrieve status information of activities.

    The corresponding API is new in CMEM 20.10

    If status is defined only task activities with a specific status are
    returned.
    - Valid values are "Idle", "Not executed", "Finished", "Cancelled",
      "Failed", "Successful", "Canceling", "Running" and "Waiting".
    - States "Idle" and "Not executed" are synonyms and "Idle" is kept only for
      backwards compatibility.
    - State "Finished" is a union of following sub-states "Cancelled",
      "Failed" and "Successful".
    - "Waiting" is the state of an activity being scheduled, but still waiting
      in queue for being executed.

    activity name examples: ExecuteLocalWorkflow, ExecuteDefaultWorkflow,
        ExecuteTransform, TypesCache, ...

    Args:
        project_name (str): The DI project ID.
        status (str): One of the documented status names (e.g. "Finished")
        activity (str): get only activities with a specific name

    Raises:
        ValueError: in case the dataset ID is not splittable
    """
    path = "/api/workspace/taskActivitiesStatus"
    task_activities_status_api = config.get_di_api_endpoint() + path
    params = {}
    if project_name:
        params["projectId"] = project_name
    if status:
        if status not in VALID_ACTIVITY_STATUS:
            raise ValueError(
                "Status {} is not a valid activity status, one of {}"
                .format(status, VALID_ACTIVITY_STATUS)
            )
        params["statusFilter"] = status
    status_info = get_json(
        task_activities_status_api,
        params=params
    )
    if activity:
        status_info = [
            info for info in status_info
            if info["activity"] == activity
        ]
    return status_info
