"""configuration commands for cmem command line interface."""
import click

from cmem.cmemc.cli.commands import CmemcCommand, CmemcGroup
from cmem.cmemc.cli.context import KNOWN_CONFIG_KEYS


@click.command(cls=CmemcCommand, name="list")
@click.pass_obj
def list_command(app):
    """List configured connections.

    This command lists all configured
    connections from the currently used config file.

    The connection identifier can be used with the --connection option
    in order to use a specific Corporate Memory instance.

    In order to apply commands on more than one instance, you need to use
    typical unix gear such as xargs or parallel:

    cmemc config list | xargs -I % sh -c 'cmemc -c % admin status'

    cmemc config list | parallel --jobs 5 cmemc -c {} admin status
    """
    for section_string in sorted(app.config, key=str.casefold):
        if section_string != "DEFAULT":
            app.echo_result(section_string)


@click.command(cls=CmemcCommand, name="edit")
@click.pass_obj
def edit_command(app):
    """Edit the user-scope configuration file."""
    app.echo_info("Open editor for config file " + app.config_file)
    click.edit(filename=app.config_file)


@click.command(cls=CmemcCommand, name="get")
@click.argument(
    "KEY",
    nargs=1,
    type=click.Choice(
        KNOWN_CONFIG_KEYS.keys(),
        case_sensitive=False
    )
)
@click.pass_obj
def get_command(app, key):
    """Get the value of a known cmemc configuration key.

    In order to automate processes such as fetching custom API data
    from multiple Corporate Memory instances, this command provides a way to
    get the value of a cmemc configuration key for the selected deployment.

    Example Usage: curl -H "Authorization: Bearer $(cmemc -c my admin token)"
    $(cmemc -c my config get DP_API_ENDPOINT)/api/custom/slug

    The commands returns with exit code 1 if the config key is not used in
    the current configuration.
    """
    value = KNOWN_CONFIG_KEYS[key]()
    app.echo_debug(f"Type of {key} value is {type(value)}")
    if value is None:
        raise ValueError(
            f"Configuration key {key} is not used in this configuration."
        )
    app.echo_info(str(value))


@click.command(cls=CmemcCommand, name="eval")
@click.option(
    "--unset",
    is_flag=True,
    help="Instead of export all configuration keys, "
         "this option will unset all key."
)
@click.pass_obj
def eval_command(app, unset):
    """Export all configuration values of a configuration for evaluation.

    The output of this command is suitable to be used by a shells eval
    command. It will output the complete configuration as 'export key="value"'
    statements. This allows for preparation of a shell environment.

    eval $(cmemc -c my config eval)

    Please be aware that credential details are shown in cleartext with
    this command.
    """
    for key in sorted(KNOWN_CONFIG_KEYS):
        if unset:
            app.echo_info(f"unset {str(key)}")
        else:
            value = KNOWN_CONFIG_KEYS[key]()
            if value is None or value == "None":
                app.echo_info(f"unset {str(key)}")
            else:
                app.echo_info(f"export {str(key)}=\"{value}\"")


@click.group(cls=CmemcGroup)
def config():
    u"""List and edit configs as well as get config values.

    Configurations are identified by the section identifier in the
    config file. Each configuration represent a Corporate Memory deployment
    with its specific access method as well as credentials.

    A minimal configuration which uses client credentials has the following
    entries:

    \b
    [example.org]
    CMEM_BASE_URI=https://cmem.example.org/
    OAUTH_GRANT_TYPE=client_credentials
    OAUTH_CLIENT_ID=cmem-service-account
    OAUTH_CLIENT_SECRET=my-secret-account-pass

    Note that OAUTH_GRANT_TYPE can be either client_credentials, password or
    prefetched_token.

    In addition to that, the following config parameters can be used as well:

    \b
    SSL_VERIFY=False    - for ignoring certificate issues (not recommended)
    DP_API_ENDPOINT=URL - to point to a non-standard DataPlatform location
    DI_API_ENDPOINT=URL - to point to a non-standard DataIntegration location
    OAUTH_TOKEN_URI=URL - to point to an external IdentityProvider location
    OAUTH_USER=username - only if OAUTH_GRANT_TYPE=password
    OAUTH_PASSWORD=password - only if OAUTH_GRANT_TYPE=password
    OAUTH_ACCESS_TOKEN=token - only if OAUTH_GRANT_TYPE=prefetched_token

    In order to get credential information from an external process, you can
    use the parameter OAUTH_PASSWORD_PROCESS, OAUTH_CLIENT_SECRET_PROCESS and
    OAUTH_ACCESS_TOKEN_PROCESS to setup an external executable.

    \b
    OAUTH_CLIENT_SECRET_PROCESS=/path/to/getpass.sh
    OAUTH_PASSWORD_PROCESS=["getpass.sh", "parameter1", "parameter2"]

    The credential executable can use the cmemc environment for fetching the
    credential (e.g. CMEM_BASE_URI and OAUTH_USER).
    If the credential executable is not given with a full path, cmemc
    will look into your environment PATH for something which can be executed.
    The configured process needs to return the credential on the first line
    of stdout. In addition to that, the process needs to exit with exit
    code 0 (without failure). There are examples available in the online
    manual.
    """


config.add_command(list_command)
config.add_command(edit_command)
config.add_command(get_command)
config.add_command(eval_command)
