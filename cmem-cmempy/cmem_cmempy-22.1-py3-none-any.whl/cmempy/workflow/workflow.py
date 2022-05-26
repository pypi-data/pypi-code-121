"""API methods for working with a single workflow."""
from cmem.cmempy import config
from cmem.cmempy.api import (
    get_json,
    request,
    send_request
)


def get_workflow_uri():
    """Get endpoint URI pattern for a workflow."""
    return config.get_di_api_endpoint() + "/workflow/workflows/{}/{}"


def get_workflow_execute_uri():
    """Get execute URI pattern for a workflow."""
    return get_workflow_uri() + "/execute"


def get_workflow_status_uri():
    """Get status URI pattern for a workflow."""
    return get_workflow_uri() + "/status"


def get_workflow_execute_on_payload_uri():
    """Get execute on payload URI pattern for a workflow."""
    return get_workflow_uri() + "/executeOnPayload"


def get_workflow_editor_uri():
    """Get execute URI pattern for a workflow.

    Since 21.01 this is changed to the new workbench
    """
    return config.get_di_api_endpoint() + "/workbench/projects/{}/workflow/{}"


def get_workflow(project_name, task_name):
    """GET retrieve single workflow."""
    return send_request(
        get_workflow_uri().format(project_name, task_name),
        method="GET"
    ).decode("utf-8")


def make_new_workflow(project_name, task_name, data=None):
    """PUT create workflow."""
    headers = {"Content-Type": "application/xml"}
    return send_request(
        get_workflow_uri().format(project_name, task_name),
        method="PUT",
        data=data,
        headers=headers
    ).decode("utf-8")


def execute_on_payload(project_name, task_name, data=None,
                       headers=None):
    """POST execute on payload."""
    if not headers:
        headers = {"Content-Type": "application/xml"}

    # pylint: disable-msg=duplicate-code
    return send_request(
        get_workflow_execute_on_payload_uri().format(project_name, task_name),
        method="POST",
        data=data,
        headers=headers
    ).decode("utf-8")


def delete_workflow(project_name, task_name):
    """DELETE remove workflow."""
    return send_request(
        get_workflow_uri().format(project_name, task_name),
        method="DELETE"
    ).decode("utf-8")


def execute_workflow(project_name, task_name):
    """PUT execute workflow."""
    return send_request(
        get_workflow_execute_uri().format(project_name, task_name),
        method="PUT"
    ).decode("utf-8")


def get_workflow_status(project_name, task_name):
    """GET workflow status.

    Returns gibberish, internal API endpoint
    use cmempy.workspace.activities.taskactivities.get_activity_status
    instead
    """
    return send_request(
        get_workflow_status_uri().format(project_name, task_name),
        method="GET"
    ).decode("utf-8")


def get_workflows_io():
    """Get a list of suitable io workflow incl. input/output information.

    see CMEM-3089

    Args:
        project_name: project ID

    Returns:
        list of dicts of workflow infos
    """
    endpoint = "{}/api/workflow/info".format(config.get_di_api_endpoint())
    params = {}
    io_workflows = []
    for _ in get_json(endpoint, method="GET", params=params):
        ins = len(_["variableInputs"])
        outs = len(_["variableOutputs"])
        if ins == 1 or outs == 1:
            io_workflows.append(_)
    return io_workflows


def execute_workflow_io(
        project_name,
        task_name,
        input_file=None,
        input_mime_type="application/xml",
        output_mime_type="application/xml"
):
    """Execute a workflow with variable input or output from or to a file.

    see CMEM-3089

    Args:
        project_name: project ID
        task_name: workflow ID
        input_file: file path
        input_mime_type: A mime type string
        output_mime_type: A mime type string

    Returns:
        Response object from requests API
    """
    endpoint = "{}/api/workflow/result/{}/{}".format(
        config.get_di_api_endpoint(), project_name, task_name
    )
    headers = {
        "Accept": output_mime_type
    }
    if input_file:
        # in case an input is given do a streaming upload
        headers["Content-Type"] = input_mime_type
        with open(input_file, 'rb') as data:
            return request(
                endpoint,
                method="POST",
                headers=headers,
                data=data,
                stream=True
            )
    # without an input, just a post without a body
    return request(
        endpoint,
        method="POST",
        headers=headers,
        stream=True
    )
