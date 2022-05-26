"""admin commands for cmem command line interface."""
import click

import jwt

from cmem.cmemc.cli.utils import (
    get_graphs_as_dict, struct_to_table
)
from cmem.cmempy.api import (
    get_access_token, get_token
)
from cmem.cmempy.config import (
    get_cmem_base_uri
)
from cmem.cmempy.health import (
    di_is_healthy, dp_is_healthy,
    get_di_version, get_dm_version, get_dp_version,
    get_shape_catalog_version
)
from cmem.cmemc.cli.commands import CmemcCommand, CmemcGroup
from cmem.cmemc.cli.commands.store import (
    bootstrap_command,
    showcase_command,
    store
)
from cmem.cmemc.cli.commands.metrics import metrics
from cmem.cmemc.cli.commands.workspace import workspace


@click.command(cls=CmemcCommand, name="status")
@click.pass_obj
def status_command(app):
    """Output health and version information.

    This command outputs version and health information of the
    selected deployment. If the version information can not be retrieved,
    UNKNOWN is shown if the endpoint is not available or ERROR is shown,
    if the endpoints returns an error.

    In addition to that, this command warns you if the
    target version of your cmemc client is newer than the version of your
    backend and if the ShapeCatalog has a different version then your
    DataPlatform component.

    To get status information of all configured
    deployments use this command in combination with parallel:

    cmemc config list | parallel --ctag cmemc -c {} admin status
    """
    app.check_versions()
    app.echo_result(get_cmem_base_uri())
    # check DI
    app.echo_result("- DataIntegration ", nl=False)
    app.echo_result(get_di_version() + " ... ", nl=False)
    if di_is_healthy():
        app.echo_success("UP")
    else:
        app.echo_error("DOWN")
    # check DP
    app.echo_result("- DataPlatform ", nl=False)
    dp_version = get_dp_version()
    app.echo_result(dp_version + " ... ", nl=False)
    if dp_is_healthy():
        app.echo_success("UP")
    else:
        app.echo_error("DOWN")
    # check shape catalog
    shapes_version = get_shape_catalog_version()
    app.echo_result("-- ShapesCatalog ", nl=False)
    app.echo_result(shapes_version + " ... ", nl=False)
    if "https://vocab.eccenca.com/shacl/" not in get_graphs_as_dict():
        app.echo_error("DOWN")
    else:
        app.echo_success("UP")
    if shapes_version not in (dp_version, "UNKNOWN"):
        app.echo_warning(
            "Your ShapeCatalog version does not match your DataPlatform "
            "version. Please consider updating your bootstrap data."
        )
    # check DM
    app.echo_result("- DataManager ", nl=False)
    dm_version = get_dm_version()
    app.echo_result(dm_version + " ... ", nl=False)
    if dm_version == "ERROR":
        app.echo_error("DOWN")
    else:
        app.echo_success("UP")


@click.command(cls=CmemcCommand, name="token")
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON. Note that this option will always try to fetch "
         "a new JSON token response. In case you are working with "
         "OAUTH_GRANT_TYPE=prefetched_token, this may lead to an error."
)
@click.option(
    "--decode",
    is_flag=True,
    help="Decode the access token and outputs the raw JSON. Note that the "
         "access token is only decoded and esp. not validated."
)
@click.pass_obj
def token_command(app, raw, decode):
    """Fetch and output an access token.

    This command can be used to check for correct authentication as well as
    to use the token with wget / curl or similar standard tools:

    Example Usage: curl -H "Authorization: Bearer $(cmemc -c my admin token)"
    $(cmemc -c my config get DP_API_ENDPOINT)/api/custom/slug

    Please be aware that this command can reveal secrets, which you do not
    want to have in log files or on the screen.
    """
    # Note:
    # - get_access_token returns the token string which is maybe from conf
    # - get_token fetches a new token incl. envelope from keycloak

    if decode:
        token = get_access_token()
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        if raw:
            app.echo_info_json(decoded_token)
        else:
            table = struct_to_table(decoded_token)
            app.echo_info_table(
                table,
                headers=["Key", "Value"],
                sort_column=0
            )
    else:
        if raw:
            app.echo_info_json(get_token())
        else:
            token = get_access_token()
            app.echo_info(token)


@click.group(cls=CmemcGroup)
def admin():
    """Import bootstrap data, backup/restore workspace or get status.

    This command group consists of commands for setting up and
    configuring eccenca Corporate Memory.
    """


admin.add_command(showcase_command)
admin.add_command(bootstrap_command)
admin.add_command(status_command)
admin.add_command(token_command)
admin.add_command(metrics)
admin.add_command(workspace)
admin.add_command(store)
