import click

from sym.flow.cli.helpers.api import SymAPI


def slack_delete(api: SymAPI, service_id: str) -> None:
    """Pre-delete service hook to uninstall the Sym Slack App from a workspace.
    This will completely revoke Sym's access in the workspace.

    To see what workspaces the Sym App is installed in, and the corresponding
    Workspace IDs, use `symflow services list`.
    """

    api.uninstall_slack(service_id)
    click.echo(
        "Uninstall successful! The Sym App has been removed from your Slack workspace."
    )
