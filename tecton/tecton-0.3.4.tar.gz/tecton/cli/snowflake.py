import click

from tecton.cli.command import tecton_config_option
from tecton.cli.command import TectonGroup
from tecton_spark import conf


# TODO(snowflake): Unhide
@click.command(cls=TectonGroup, hidden=True)
def snowflake():
    """Snowflake-related commands."""


@snowflake.command(requires_auth=False)
@tecton_config_option(
    "SNOWFLAKE_USER", param_decls=["--user"], help="The Snowflake user to use for interactive queries."
)
@tecton_config_option(
    "SNOWFLAKE_PASSWORD", param_decls=["--password"], hide_input=True, help="The password for the Snowflake user."
)
@tecton_config_option(
    "SNOWFLAKE_WAREHOUSE", param_decls=["--warehouse"], help="The Snowflake warehouse to use for interactive queries."
)
def configure(user, password, warehouse):
    conf.set("ALPHA_SNOWFLAKE_COMPUTE_ENABLED", "true")
    conf.set("SNOWFLAKE_USER", user)
    conf.set("SNOWFLAKE_PASSWORD", password)
    conf.set("SNOWFLAKE_WAREHOUSE", warehouse)
    conf.save_tecton_configs()
