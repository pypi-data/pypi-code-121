import functools
import os

import click
import configobj

APP_DIR = click.get_app_dir('vgs', force_posix=True)
OPTION_NAME = '--config'


class ConfigObjProvider:
    """
    When invoked, reads a config file and returns its content as a dictionary.
    """

    def __init__(self, section=None):
        self.section = section

    def __call__(self, *args, **kwargs):
        config = configobj.ConfigObj(args[0])
        if self.section:
            config = config[self.section] if self.section in config else {}
        return config


# noinspection PyUnusedLocal
def callback(provider, ctx: click.Context, param: click.Parameter, value: str):
    """
    Change the execution flow to populate the default map first.
    """
    ctx.default_map = ctx.default_map or {}

    if value:
        try:
            config = provider(value)
        except Exception as cause:
            raise click.BadOptionUsage(OPTION_NAME, f'Failed to read configuration file: {cause}', ctx)
        ctx.default_map.update(config)

    return value


def configuration_option(section=None):
    def decorator(f):
        return click.option(
            OPTION_NAME,
            callback=functools.partial(callback, ConfigObjProvider(section)),
            default=os.path.join(APP_DIR, 'config'),
            envvar='VGS_CONFIG_FILE',
            expose_value=False,
            help='Read configuration from FILE.',
            is_eager=True,
            type=click.Path(dir_okay=False),
        )(f)

    return decorator
