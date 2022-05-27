import sys

import click
from colorama import Fore

from tecton import conf
from tecton import Workspace
from tecton._internals import metadata_service
from tecton._internals.utils import is_live_workspace
from tecton._internals.workspace_utils import PROD_WORKSPACE_NAME_CLIENT
from tecton.cli import printer
from tecton.cli.command import TectonGroup
from tecton.cli.common import get_current_workspace
from tecton.cli.engine import update_tecton_state
from tecton_proto.metadataservice.metadata_service_pb2 import CreateWorkspaceRequest
from tecton_proto.metadataservice.metadata_service_pb2 import DeleteWorkspaceRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetWorkspaceRequest
from tecton_proto.metadataservice.metadata_service_pb2 import ListWorkspacesRequest


@click.group("workspace", cls=TectonGroup)
def workspace():
    """Manipulate a tecton workspace."""


@workspace.command()
@click.argument("workspace")
def select(workspace):
    """Select WORKSPACE."""
    # validate
    workspace_names = {w.name for w in _list_workspaces()}
    if workspace not in workspace_names:
        printer.safe_print(
            f'Workspace "{workspace}" not found. Run `tecton workspace list` to see list of available workspaces.'
        )
        sys.exit(1)

    _switch_to_workspace(workspace)


@workspace.command()
def list():
    """List available workspaces."""
    current_workspace = get_current_workspace()
    workspaces = _list_workspaces()
    materializable = [w.name for w in workspaces if w.capabilities.materializable]
    nonmaterializable = [w.name for w in workspaces if not w.capabilities.materializable]

    if materializable:
        printer.safe_print("Live Workspaces:")
        for name in materializable:
            marker = "*" if name == current_workspace else " "
            printer.safe_print(f"{marker} {name}")

    # Print whitespace between the two sections if needed.
    if materializable and nonmaterializable:
        printer.safe_print()

    if nonmaterializable:
        printer.safe_print("Development Workspaces:")
        for name in nonmaterializable:
            marker = "*" if name == current_workspace else " "
            printer.safe_print(f"{marker} {name}")


@workspace.command()
def show():
    """Show active workspace."""
    workspace_name = get_current_workspace()
    workspace = _get_workspace(workspace_name)
    workspace_type = "Live" if workspace.capabilities.materializable else "Development"
    printer.safe_print(f"{workspace_name} ({workspace_type})")


@workspace.command()
@click.argument("workspace")
@click.option(
    "--live/--no-live",
    # Kept for backwards compatibility
    "--automatic-materialization-enabled/--automatic-materialization-disabled",
    default=False,
    help="Create a live workspace, which enables materialization and online serving.",
)
def create(workspace, live):
    """Create a new workspace named WORKSPACE."""
    # There is a check for this on the server side too, but we optimistically validate
    # here as well to show a pretty error message.
    workspace_names = {w.name for w in _list_workspaces()}
    if workspace in workspace_names:
        printer.safe_print(f"Workspace {workspace} already exists", file=sys.stderr)
        sys.exit(1)

    # create
    _create_workspace(workspace, live)

    # switch to new workspace
    _switch_to_workspace(workspace)
    printer.safe_print(
        """
You're now on a new, empty workspace. Workspaces isolate their state,
so if you run "tecton plan" Tecton will not see any existing state
for this configuration.
    """
    )


@workspace.command()
@click.argument("workspace")
@click.option("--yes", "-y", is_flag=True)
def delete(workspace, yes):
    """Delete workspace named WORKSPACE."""
    # validate
    if workspace == PROD_WORKSPACE_NAME_CLIENT:
        printer.safe_print(f"Deleting workspace '{PROD_WORKSPACE_NAME_CLIENT}' not allowed.")
        sys.exit(1)

    is_live = is_live_workspace(workspace)

    # confirm deletion
    confirmation = "y" if yes else None
    while confirmation not in ("y", "n", ""):
        confirmation_text = f'Are you sure you want to delete the workspace "{workspace}"? (y/N)'
        if is_live:
            confirmation_text = f"{Fore.RED}Warning{Fore.RESET}: This will delete any materialized data in this workspace.\n{confirmation_text}"
        confirmation = input(confirmation_text).lower().strip()
    if confirmation == "n" or confirmation == "":
        printer.safe_print("Cancelling delete action.")
        sys.exit(1)

    # archive all fcos in the remote state unconditionally.
    # This will need to be updated when workspaces support materialization.
    with Workspace(workspace):
        update_tecton_state(
            objects=[],
            repo_root="",
            repo_files=[],
            apply=True,
            # Set interactive to False to avoid duplicate confirmation.
            # Confirmation of this action is handled above already.
            interactive=False,
            debug=False,
            upgrade_all=False,
        )

    # delete
    _delete_workspace(workspace)

    # switch to prod if deleted current
    if workspace == get_current_workspace():
        _switch_to_workspace(PROD_WORKSPACE_NAME_CLIENT)


def _switch_to_workspace(workspace_name: str):
    conf.set("TECTON_WORKSPACE", workspace_name)
    conf.save_tecton_configs()
    printer.safe_print(f'Switched to workspace "{workspace_name}".')


def _create_workspace(workspace_name: str, materializable: bool):
    request = CreateWorkspaceRequest()
    request.workspace_name = workspace_name
    request.capabilities.materializable = materializable
    metadata_service.instance().CreateWorkspace(request)
    printer.safe_print(f'Created workspace "{workspace_name}".')


def _delete_workspace(workspace_name: str):
    with Workspace(workspace_name):
        request = DeleteWorkspaceRequest()
        request.workspace = workspace_name
        metadata_service.instance().DeleteWorkspace(request)
    printer.safe_print(f'Deleted workspace "{workspace_name}".')


def _get_workspace(workspace_name: str):
    request = GetWorkspaceRequest()
    request.workspace_name = workspace_name
    response = metadata_service.instance().GetWorkspace(request)
    return response.workspace


def _list_workspaces():
    request = ListWorkspacesRequest()
    response = metadata_service.instance().ListWorkspaces(request)
    return response.workspaces
