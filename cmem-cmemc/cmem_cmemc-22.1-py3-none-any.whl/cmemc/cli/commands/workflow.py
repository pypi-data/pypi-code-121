"""workflow commands for cmem command line interface."""
import datetime
import os
import sys
import time

import click

import requests

import timeago

from cmem.cmemc.cli import completion
from cmem.cmemc.cli.commands import CmemcCommand, CmemcGroup
from cmem.cmemc.cli.commands.scheduler import scheduler
from cmem.cmempy.workflow import get_workflows
from cmem.cmempy.workflow.workflow import (
    execute_workflow_io,
    get_workflow_editor_uri,
    get_workflows_io
)
from cmem.cmempy.workspace.activities import (
    ACTIVITY_TYPE_EXECUTE_DEFAULTWORKFLOW,
    VALID_ACTIVITY_STATUS
)
from cmem.cmempy.workspace.activities.taskactivities import (
    get_activities_status
)
from cmem.cmempy.workspace.activities.taskactivity import (
    get_activity_status,
    start_task_activity
)
from cmem.cmempy.workspace.projects.project import get_projects
from cmem.cmempy.workspace.search import list_items

IO_WARNING_NO_RESULT = "The workflow was executed but produced no result."
IO_WARNING_NO_OUTPUT_DEFINED = "The workflow was executed, a result was "\
                               "received but dropped."

MIME_CSV = "text/csv"
MIME_XLS = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MIME_NT = "application/n-triples"
MIME_JSON = "application/json"
MIME_XML = "application/xml"

VALID_OUTPUT_EXTENSIONS = {
    ".csv": MIME_CSV,
    ".xlsx": MIME_XLS,
    ".nt": MIME_NT,
    ".ttl": MIME_NT,
    ".json": MIME_JSON,
    ".xml": MIME_XML
}

VALID_INPUT_EXTENSIONS = {
    ".csv": MIME_CSV,
    ".json": MIME_JSON,
    ".xml": MIME_XML
}


def _get_workflows_filtered_by_project(project):
    """Get workflows but filtered by project.

    Args:
        project (str): project ID

    Returns:
        list of filtered workflows form the list_items API call
    """
    return list_items(
        project=project, item_type="workflow"
    )["results"]


def _get_workflows_filtered_by_io_feature(feature):
    """Get workflows filtered by io feature.

    Args:
        feature (str): one of input-only|output-only|input-output or any

    Returns:
        list of filtered workflows form the list_items API call

    Raises:
        ValueError
    """
    possible_io_filter_values = (
        "input-only", "output-only", "input-output", "any"
    )
    if feature not in possible_io_filter_values:
        raise ValueError(
            f"{feature} is an unknown filter value. "
            f"Use one of {possible_io_filter_values}."
        )
    filtered_workflows_ids = []
    for _ in get_workflows_io():
        ins = len(_["variableInputs"])
        outs = len(_["variableOutputs"])
        if feature == "any" and (ins == 1 or outs == 1):
            filtered_workflows_ids.append(_["projectId"] + ":" + _["id"])
            continue
        if feature == "input-only" and (ins == 1 and outs == 0):
            filtered_workflows_ids.append(_["projectId"] + ":" + _["id"])
            continue
        if feature == "output-only" and (ins == 0 and outs == 1):
            filtered_workflows_ids.append(_["projectId"] + ":" + _["id"])
            continue
        if feature == "input-output" and (ins == 1 and outs == 1):
            filtered_workflows_ids.append(_["projectId"] + ":" + _["id"])
            continue
    filtered_workflows = []
    for _ in list_items(item_type="workflow")["results"]:
        if _["projectId"] + ":" + _["id"] in filtered_workflows_ids:
            filtered_workflows.append(_)
    return filtered_workflows


def _get_workflows_filtered(filter_name, filter_value):
    """Get workflows filtered according to filter name and value.

    Args:
        filter_name (str): one of "project" or "io"
        filter_value (str): value according to fileter

    Returns:
        list of filtered workflows from the list_items API call

    Raises:
        ValueError
    """
    # filter by project
    if filter_name == "project":
        return _get_workflows_filtered_by_project(filter_value)
    # filter by io feature
    if filter_name == "io":
        return _get_workflows_filtered_by_io_feature(filter_value)
    # default is unfiltered
    return list_items(item_type="workflow")["results"]


def _io_check_request(
        info=None,
        input_file=None,
        output_file=None,
        output_mimetype=None
):
    """Check the requested io execution."""
    if len(info["variableInputs"]) == 0 and input_file:
        raise ValueError(
            "You are trying to send data to a workflow without a variable "
            "input. Please remove the '-i' parameter."
        )
    if len(info["variableOutputs"]) == 0 and output_file:
        raise ValueError(
            "You are trying to retrieve data to a workflow without a variable "
            "output. Please remove the '-o' parameter."
        )
    if len(info["variableInputs"]) == 1 and not input_file:
        raise ValueError(
            "This workflow has a defined input so you need to use the '-i' "
            "parameter to send data to it."
        )
    if len(info["variableOutputs"]) == 1 and not output_file:
        raise ValueError(
            "This workflow has a defined output so you need to use the '-o' "
            "parameter to retrieve data from it."
        )
    if output_mimetype == MIME_XLS and output_file == "-":
        raise ValueError(
            "Trying to output an excel document to stdout will fail.\n"
            "Please output to a regular file instead "
            "(workflow was not executed)."
        )


def _io_get_info(project_id, workflow_id):
    """Get the io info dictionary of the workflow."""
    for _ in get_workflows_io():
        if _["id"] == workflow_id and _["projectId"] == project_id:
            return _
    raise ValueError(
        "The given workflow does not exist or is not suitable to be executed "
        "with this command.\n"
        "An io workflow needs exactly one variable input and/or one variable "
        "output."
    )


def _io_process_response(response, app, output_file):
    """Process the workflow response of the io command."""
    with response:
        if output_file == "-":
            for line in response.iter_lines():
                if line:
                    app.echo_info(line.decode("UTF-8"))
        else:
            with click.open_file(output_file, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)


def _io_guess_output(output_file):
    """Guess the mime type of an output file name."""
    if output_file == "-":
        return None
    _, file_extension = os.path.splitext(output_file)
    if file_extension in VALID_OUTPUT_EXTENSIONS:
        return VALID_OUTPUT_EXTENSIONS[file_extension]
    valid_extensions = ', '.join(VALID_OUTPUT_EXTENSIONS.keys())
    raise ValueError(
        f"Files with the extension {file_extension} can not be generated. "
        f"Try one of {valid_extensions}"
    )


def _io_guess_input(input_file):
    """Guess the mime type of an input file name."""
    if input_file == "-":
        return None
    _, file_extension = os.path.splitext(input_file)
    if file_extension in VALID_INPUT_EXTENSIONS:
        return VALID_INPUT_EXTENSIONS[file_extension]
    valid_extensions = ', '.join(VALID_INPUT_EXTENSIONS.keys())
    raise ValueError(
        f"Files with the extension {file_extension} can not be processed. "
        f"Try one of {valid_extensions}"
    )


def _workflows_get_ids():
    """Get a list of workflow IDs."""
    ids = []
    for project_desc in get_projects():
        for workflow_id in get_workflows(project_desc["name"]):
            ids.append(project_desc["name"] + ":" + workflow_id)
    return ids


def _workflow_wait_until_finished(project_id, task_id, polling_interval):
    """Poll workflow status until workflow is finished and return status.

    :type project_id: string
    :type task_id: string
    :type polling_interval: int
    """
    while True:
        status = get_activity_status(project_id, task_id)
        # wait until isRunning is false
        if not status['isRunning']:
            break
        time.sleep(polling_interval)
    return status


def _status_command_pre_cmem_20_10(
        app, raw, _filter, workflow_ids
):
    """Get status of workflows without new taskActivitiesStatus API."""
    if workflow_ids == ():
        workflow_ids += tuple(_workflows_get_ids())

    for workflow_id in workflow_ids:
        project_id, task_id = workflow_id.split(":")
        status = get_activity_status(project_id, task_id)
        # filter for running activities
        if _filter == "running"\
                and 'isRunning' in status and not status['isRunning']:
            continue
        # filter for failed activities
        if _filter == "failed"\
                and "failed" in status and not status['failed']:
            continue
        # output raw json if wanted
        if raw:
            app.echo_info_json(status)
        # output single line status
        else:
            app.echo_info(f"{workflow_id} ... ", nl=False)
            _workflow_echo_status(app, status)


def _workflow_echo_status(app, status):
    """Print a colored status based on the returned JSON.

    Status can be Idle, Running, Canceling, Waiting, Finished
    isRunning is true for Running, Canceling, Waiting
    canceled only exists sometimes
    """
    # prepare human friendly relative time
    now = datetime.datetime.now()
    stamp = datetime.datetime.fromtimestamp(status["lastUpdateTime"] / 1000)
    time_ago = timeago.format(stamp, now, 'en')
    status_name = status["statusName"]
    status_message = status["message"]
    # prepare message
    if status_name == status["message"]:
        message = f"{status_name} ({time_ago})"
    else:
        message = f"{status_name} ({status_message}, {time_ago})"

    if status["isRunning"]:
        if status_name == "Running":
            app.echo_warning(message)
        elif status_name == "Canceling":
            app.echo_warning(message)
        elif status_name == "Waiting":
            app.echo_warning(message)
        else:
            raise ValueError(
                f"statusName is {status_name}, expecting one of: "
                "Running, Canceling or Waiting."
            )
    else:
        # not running can be Idle or Finished
        if "failed" in status and status["failed"]:
            app.echo_error(message, nl=True, err=False)
        elif "cancelled" in status and status["cancelled"]:
            app.echo_warning(message)
        elif status["statusName"] == "Idle":
            app.echo_info(message)
        else:
            # Finished and without failed or canceled status
            app.echo_success(message)


@click.command(cls=CmemcCommand, name="execute")
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Execute all available workflows."
)
@click.option(
    "--wait",
    is_flag=True,
    help="Wait until all executed workflows are completed."
)
@click.option(
    "--polling-interval",
    type=click.IntRange(min=0, max=60),
    show_default=True,
    default=1,
    help="How many seconds to wait between status polls. Status polls are"
         " cheap, so a higher polling interval is most likely not needed."
)
@click.argument(
    "workflow_ids",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.workflow_ids
)
@click.pass_obj
def execute_command(app, all_, wait, polling_interval, workflow_ids):
    """Execute workflow(s).

    With this command, you can start one or more workflows at the same time or
    in a sequence, depending on the result of the predecessor.

    Executing a workflow can be done in two ways: Without --wait just sends
    the starting signal and does not look for the workflow and its result
    (fire and forget). Starting workflows in this way, starts all given
    workflows at the same time.

    The optional --wait option starts the workflows in the same way, but also
    polls the status of a workflow until it is finished. In case of an error of
    a workflow, the next workflow is not started.
    """
    all_workflow_ids = _workflows_get_ids()
    if workflow_ids == () and not all_:
        raise ValueError("Either specify at least one workflow or use the"
                         + " --all option to execute all workflows.")
    if all_:
        workflow_ids = all_workflow_ids

    for workflow_id in workflow_ids:
        if workflow_id not in all_workflow_ids:
            raise ValueError(
                f"Workflow '{workflow_id}' is not available."
            )
        project_id, task_id = workflow_id.split(":")
        app.echo_info(f"{workflow_id} ... ", nl=False)

        # before we start, we fetch the status
        status = get_activity_status(project_id, task_id)
        if not wait:
            if status['isRunning']:
                # in case of a running workflow, we only output status
                app.echo_info('Already Running')
            else:
                # in case of simple call, we just start and forget
                start_task_activity(project_id, task_id)
                app.echo_info('Started')
        else:
            # in case of --wait, we poll the status until finished
            if status['isRunning']:
                # in case of a running workflow, we only output status
                app.echo_info('Already Running ... ', nl=False)
            else:
                start_task_activity(project_id, task_id)
                app.echo_info('Started ... ', nl=False)

            status = _workflow_wait_until_finished(
                project_id, task_id, polling_interval
            )
            # when we have a Finished status, we output it
            _workflow_echo_status(app, status)
            # in case of failure, the following workflows are not executed
            if status['failed']:
                sys.exit(1)


# pylint: disable=too-many-arguments
@click.command(cls=CmemcCommand, name="io")
@click.option(
    "--input", "-i", "input_file",
    type=click.Path(
        allow_dash=False,
        dir_okay=False,
        readable=True
    ),
    autocompletion=completion.workflow_io_input_files,
    help="From which file the input is taken: note that the maximum file size "
         "to upload is limited to a server configured value. If the workflow "
         "has no defined variable input dataset, this can be ignored."
)
@click.option(
    "--output", "-o", "output_file",
    type=click.Path(
        allow_dash=False,
        dir_okay=False,
        writable=True,
    ),
    autocompletion=completion.workflow_io_output_files,
    help="To which file the result is written to: use '-' in order to output "
         "the result to stdout. If the workflow has no defined variable "
         "output dataset, this can be ignored. Please note that the io "
         "command will not warn you on overwriting existing output files."
)
@click.option(
    "--input-mimetype",
    help="Which input format should be processed: If not given, cmemc will "
         "try to guess the mime type based on the file extension or will "
         "fail",
    type=click.Choice(
        [
            "guess",
            "application/xml",
            "application/json",
            "text/csv"
        ]
    ),
    default="guess"
)
@click.option(
    "--output-mimetype",
    help="Which output format should be requested: If not given, cmemc will "
         "try to guess the mime type based on the file extension or will "
         "fail. In case of an output to stdout, a default mime type "
         "will be used (currently xml).",
    type=click.Choice(
        ["guess", MIME_XML, MIME_JSON, MIME_NT, MIME_XLS, MIME_CSV]
    ),
    default="guess"
)
@click.argument(
    "workflow_id",
    type=click.STRING,
    autocompletion=completion.workflow_io_ids
)
@click.pass_obj
def io_command(
        app,
        input_file, input_mimetype,
        output_file, output_mimetype,
        workflow_id
):
    """Execute a workflow with file input/output.

    With this command, you can execute a workflow that uses variable datasets
    as input, output or for configuration. Use the input parameter to feed
    data into the workflow. Likewise use output for retrieval of the workflow
    result. Workflows without a variable dataset will throw an error.
    """
    project_id, task_id = workflow_id.split(":")
    if output_file and output_mimetype == "guess":
        output_mimetype = _io_guess_output(output_file)
    if input_file and input_mimetype == "guess":
        input_mimetype = _io_guess_input(input_file)

    _io_check_request(
        info=_io_get_info(project_id, task_id),
        input_file=input_file,
        output_file=output_file,
        output_mimetype=output_mimetype
    )

    response = execute_workflow_io(
        project_name=project_id,
        task_name=task_id,
        input_file=input_file,
        input_mime_type=input_mimetype,
        output_mime_type=output_mimetype
    )
    app.echo_debug(
        f"Workflow response received after {response.elapsed} "
        f"with status {response.status_code}."
    )
    if response.status_code == 204:
        # empty content, warn if output was requested
        # this will happen only if info was wrong
        if output_file:
            app.echo_warning(IO_WARNING_NO_RESULT)
        # execution successful
        return
    if response.status_code == 200 and not output_file:
        # returns with content, warn if NO output was requested
        # this will happen only if info was wrong
        app.echo_warning(IO_WARNING_NO_OUTPUT_DEFINED)
        # execution successful
        return
    _io_process_response(response, app, output_file)


@click.command(cls=CmemcCommand, name="list")
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON objects of workflow task search API response."
)
@click.option(
    "--id-only",
    is_flag=True,
    help="Lists only workflow identifier and no labels or other "
         "meta data. This is useful for piping the IDs into other commands."
)
@click.option(
    "--filter", "filter_",
    type=click.Tuple([
        click.Choice(["project", 'io']),
        str
    ]),
    autocompletion=completion.workflow_list_filter,
    default=[None] * 2,
    help="Filter workflows based on project or suitability for the io "
         "command ."
         "First parameter CHOICE can be 'project' or 'io'. "
         "The second parameter has to be a project ID in case "
         "of 'project' or 'input-only|output-only|input-output|any' in case "
         "of 'io' filter."
)
@click.pass_obj
def list_command(app, raw, id_only, filter_):
    """List available workflow ids."""
    filter_name, filter_value = filter_
    workflows = _get_workflows_filtered(filter_name, filter_value)
    if raw:
        app.echo_info_json(workflows)
        return
    if id_only:
        # sort by combined project + task ID
        for _ in sorted(
                workflows,
                key=lambda k: (k["projectId"] + ":" + k["id"]).lower()
        ):
            app.echo_info(_["projectId"] + ":" + _["id"])
        return
    # output a user table
    table = []
    for _ in workflows:
        row = [
            _["projectId"] + ":" + _["id"],
            _["label"],
        ]
        table.append(row)
    app.echo_info_table(
        table,
        headers=["Workflow ID", "Label"],
        sort_column=1
    )


@click.command(cls=CmemcCommand, name="status")
@click.option(
    "--project", "project_id",
    type=click.STRING,
    autocompletion=completion.project_ids,
    help="The project, from which you want to list the workflows. "
         "Project IDs can be listed with the 'project list' command."
)
@click.option(
    "--raw",
    is_flag=True,
    help="Output raw JSON info."
)
@click.option(
    "--filter", "_filter",
    type=click.Choice(VALID_ACTIVITY_STATUS, case_sensitive=False),
    help="Show only workflows of a specific status."
)
@click.argument(
    "workflow_ids",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.workflow_ids
)
@click.pass_obj
def status_command(app, project_id, raw, _filter, workflow_ids):
    """Get status information of workflow(s)."""
    try:
        workflow_status = get_activities_status(
            status=_filter,
            project_name=project_id,
            activity=ACTIVITY_TYPE_EXECUTE_DEFAULTWORKFLOW
        )
        for status in workflow_status:
            workflow_id = status["project"] + ":" + status["task"]
            if len(workflow_ids) == 0 or workflow_id in workflow_ids:
                if raw:
                    # TODO: output for more than one workflow is not valid JSON
                    app.echo_info_json(status)
                else:
                    app.echo_info(f"{workflow_id} ... ", nl=False)
                    _workflow_echo_status(app, status)
    except requests.exceptions.HTTPError:
        app.echo_warning("CMEM 20.10 taskActivitiesStatus API not available.\n"
                         "Falling back to older and more slow API with less "
                         "filter options.")
        _status_command_pre_cmem_20_10(app, raw, _filter, workflow_ids)


@click.command(cls=CmemcCommand, name="open")
@click.argument(
    "workflow_id",
    type=click.STRING,
    autocompletion=completion.workflow_ids
)
@click.pass_obj
def open_command(app, workflow_id):
    """Open a workflow in your browser."""
    project_id, task_id = workflow_id.split(":")
    workflow_editor_uri = get_workflow_editor_uri()\
        .format(project_id, task_id)
    click.launch(workflow_editor_uri)
    app.echo_debug(workflow_editor_uri)


@click.group(cls=CmemcGroup)
def workflow():
    """List, execute, status or open (io) workflows.

    Workflows are identified by a WORKFLOW_ID. The get a list of existing
    workflows, execute the list command or use tab-completion.
    The WORKFLOW_ID is a concatenation of an PROJECT_ID and a TASK_ID, such as
    "my-project:my-workflow".
    """


workflow.add_command(execute_command)
workflow.add_command(io_command)
workflow.add_command(list_command)
workflow.add_command(status_command)
workflow.add_command(open_command)
workflow.add_command(scheduler)
