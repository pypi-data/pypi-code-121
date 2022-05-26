"""DataIntegration scheduler commands for the cmem command line interface."""
import click

from cmem.cmemc.cli import completion
from cmem.cmemc.cli.commands import CmemcCommand, CmemcGroup
from cmem.cmemc.cli.utils import split_task_id, struct_to_table
from cmem.cmempy.config import get_cmem_base_uri
from cmem.cmempy.workflow.workflow import get_workflow_editor_uri
from cmem.cmempy.workspace.search import list_items
from cmem.cmempy.workspace.tasks import get_task, patch_parameter


def _get_schedulers():
    """Return the exported list of schedulers."""
    schedulers = list_items(
        item_type="task",
        add_task_parameter=True,
        facets=[{
            "facetId": "taskType",
            "keywordIds": ["Scheduler"],
            "type": "keyword"
        }]
    )["results"]
    return schedulers


def _get_sorted_scheduler_ids():
    """Return sorted list of scheduler IDs."""
    return sorted(
        [_["projectId"] + ":" + _["id"] for _ in _get_schedulers()],
        key=lambda k: k[0].lower()
    )


@click.command(cls=CmemcCommand, name="open")
@click.argument(
    "scheduler_ids",
    nargs=-1,
    required=True,
    type=click.STRING,
    autocompletion=completion.scheduler_ids
)
@click.option(
    "--workflow",
    is_flag=True,
    help="Instead of opening the scheduler page, open the page of the "
         "scheduled workflow."
)
@click.pass_obj
def open_command(app, scheduler_ids, workflow):
    """Open scheduler(s) in the browser.

    With this command, you can open a scheduler in the workspace in
    your browser to change it.

    The command accepts multiple scheduler IDs which results in
    opening multiple browser tabs.
    """
    schedulers = _get_schedulers()
    all_scheduler_ids = [s["projectId"] + ":" + s["id"] for s in schedulers]
    for scheduler_id in scheduler_ids:
        if scheduler_id not in all_scheduler_ids:
            raise ValueError(f"Scheduler '{scheduler_id}' not found.")
    for scheduler_id in scheduler_ids:
        for _ in schedulers:
            current_id = _["projectId"] + ":" + _["id"]
            if scheduler_id == current_id:
                if workflow:
                    uri = get_workflow_editor_uri().format(
                        _["projectId"], _["parameters"]["task"]
                    )
                else:
                    uri = get_cmem_base_uri() + _["itemLinks"][0]["path"]
                app.echo_debug(f"Open {_}: {uri}")
                click.launch(uri)


@click.command(cls=CmemcCommand, name="list")
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON."
)
@click.option(
    "--id-only",
    is_flag=True,
    help="Lists only task identifier and no labels or other "
         "meta data. This is useful for piping the IDs into other commands."
)
@click.pass_obj
def list_command(app, raw, id_only):
    """List available scheduler.

    Outputs a table or a list of scheduler IDs which can be used as
    reference for the scheduler commands.
    """
    schedulers = _get_schedulers()
    if raw:
        app.echo_info_json(schedulers)
        return
    if id_only:
        for _ in sorted(s["projectId"] + ":" + s["id"] for s in schedulers):
            app.echo_result(_)
        return
    # output a user table
    table = []
    headers = ["Scheduler ID", "Interval", "Enabled", "Label"]
    for _ in schedulers:
        if "parameters" in _:
            row = [
                _["projectId"] + ":" + _["id"],
                _["parameters"]["interval"],
                _["parameters"]["enabled"],
                _["label"],
            ]
        else:
            # This is the case for DI Version < 21.09
            headers = ["Scheduler ID", "Label"]
            row = [
                _["projectId"] + ":" + _["id"],
                _["label"],
            ]
        table.append(row)
    # sort output by label - https://docs.python.org/3/howto/sorting.html
    app.echo_info_table(table, headers=headers, sort_column=1)


@click.command(cls=CmemcCommand, name="inspect")
@click.argument(
    "scheduler_id",
    type=click.STRING,
    autocompletion=completion.scheduler_ids
)
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON."
)
@click.pass_obj
def inspect_command(app, scheduler_id, raw):
    """Display all meta data of a scheduler."""
    app.echo_debug(f"Scheduler ID is {scheduler_id}")
    project_id, scheduler_id = split_task_id(scheduler_id)
    task = get_task(project_id, scheduler_id)
    if raw:
        app.echo_info_json(task)
    else:
        table = struct_to_table(task)
        app.echo_info_table(
            table,
            headers=["Key", "Value"],
            sort_column=0
        )


@click.command(cls=CmemcCommand, name="disable")
@click.argument(
    "scheduler_ids",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.scheduler_ids
)
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Disable all scheduler."
)
@click.pass_obj
def disable_command(app, scheduler_ids, all_):
    """Disable scheduler(s).

    The command accepts multiple scheduler IDs which results in disabling
    them one after the other.
    """
    if scheduler_ids == () and not all_:
        raise ValueError("Either specify at least one scheduler ID or use "
                         "the --all option to disable all scheduler.")
    if all_:
        scheduler_ids = _get_sorted_scheduler_ids()

    app.echo_debug(f"Scheduler IDs are {scheduler_ids}")
    count = len(scheduler_ids)
    length = len(str(count))
    current = 0
    for scheduler_id in scheduler_ids:
        current = current + 1
        current_string = str(current).zfill(length)
        project_id, scheduler_id = split_task_id(scheduler_id)
        task = get_task(project_id, scheduler_id, with_labels=False)
        app.echo_info(
            f"Disable scheduler {current_string}/{count}: "
            f"{project_id}:{scheduler_id} ... ",
            nl=False
        )
        data = {"data": {"parameters": task["data"]["parameters"]}}
        if data["data"]["parameters"]["enabled"] == "false":
            app.echo_warning("already disabled")
            continue
        data["data"]["parameters"]["enabled"] = "false"
        patch_parameter(project=project_id, task=scheduler_id, data=data)
        app.echo_success("done")


@click.command(cls=CmemcCommand, name="enable")
@click.argument(
    "scheduler_ids",
    nargs=-1,
    type=click.STRING,
    autocompletion=completion.scheduler_ids
)
@click.option(
    "-a", "--all", "all_",
    is_flag=True,
    help="Enable all scheduler."
)
@click.pass_obj
def enable_command(app, scheduler_ids, all_):
    """Enable scheduler(s).

    The command accepts multiple scheduler IDs which results in enabling
    them one after the other.
    """
    if scheduler_ids == () and not all_:
        raise ValueError("Either specify at least one scheduler ID or use "
                         "the --all option to enable all scheduler.")
    if all_:
        scheduler_ids = _get_sorted_scheduler_ids()

    app.echo_debug(f"Scheduler IDs are {scheduler_ids}")
    count = len(scheduler_ids)
    length = len(str(count))
    current = 0
    for scheduler_id in scheduler_ids:
        current = current + 1
        current_string = str(current).zfill(length)
        project_id, scheduler_id = split_task_id(scheduler_id)
        task = get_task(project_id, scheduler_id, with_labels=False)
        app.echo_info(
            f"Enable scheduler {current_string}/{count}: "
            f"{project_id}:{scheduler_id} ... ",
            nl=False
        )
        data = {"data": {"parameters": task["data"]["parameters"]}}
        if data["data"]["parameters"]["enabled"] == "true":
            app.echo_warning("already enabled")
            continue
        data["data"]["parameters"]["enabled"] = "true"
        patch_parameter(project=project_id, task=scheduler_id, data=data)
        app.echo_success("done")


@click.group(cls=CmemcGroup)
def scheduler():
    """List, inspect, enable/disable or open scheduler.

    Schedulers execute workflows in specified intervals. They are identified
    with a SCHEDULERID. To get a list of existing schedulers, execute the
    list command or use tab-completion.
    """


scheduler.add_command(open_command)
scheduler.add_command(list_command)
scheduler.add_command(inspect_command)
scheduler.add_command(disable_command)
scheduler.add_command(enable_command)
