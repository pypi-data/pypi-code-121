import click
from click_didyoumean import DYMGroup

from ..core.local_cfg import LocalConfig
from ..core.const import LOCAL_CONFIG_PATH
from .root import cli


@cli.group(cls=DYMGroup)
def config():
    """ CLI configuration """


@config.command('init')
def config_init():
    """
    Initialize local configuration file

    File will only be generated if no configuration file already exists
    on default path.
    """
    cfg = LocalConfig(auto_file_creation=False)

    if not cfg.file_exists():
        if cfg.create_file():
            click.echo('Configuration file successfully generated at "{}"'
                       .format(LOCAL_CONFIG_PATH)
                       )
        else:
            click.echo('Can not generate configuration file at "{}"'
                       .format(LOCAL_CONFIG_PATH)
                       )
    else:
        click.echo('Configuration file already exists on path: "{}"'
                   .format(LOCAL_CONFIG_PATH)
                   )


@config.command('remove')
def config_remove():
    """ Erase local configuration """

    if LocalConfig.erase_config() is True:
        click.echo("All local configuration files and dirs successfully erased")
    else:
        click.echo("No local configuration files detected")


@config.command('path')
def config_get_path():
    """
    Path to local configuration file

    Note that this command will show the hardcoded path to config file, so it
    doesn't mean that this file actually exists at the time the command is
    called
    """
    click.echo(LOCAL_CONFIG_PATH)


@config.command('exist')
def config_exist():
    """ Check does the local configuration file exists """
    if LOCAL_CONFIG_PATH.exists() is True:
        click.echo("Configuration file do exist")
    else:
        click.echo("Configuration file doesn't exist")
