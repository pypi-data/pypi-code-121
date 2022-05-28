import codecs
import json
import os
from typing import List, Optional

import click
from click.core import Context, Option

from .environ import _load_environ
from .event import _load_dispatch_getter
from .exception import _raise_exception_with_exit_code
from ..event import _DEFAULT_FILENAME
from ..script.result import result_to_json
from ...config.meta import __TITLE__, __VERSION__, __AUTHOR__, __AUTHOR_EMAIL__


# noinspection DuplicatedCode,PyUnusedLocal
def print_version(ctx: Context, param: Option, value: bool) -> None:
    """
    Print version information of cli
    :param ctx: click context
    :param param: current parameter's metadata
    :param value: value of current parameter
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo('{title}, version {version}.'.format(title=__TITLE__.capitalize(), version=__VERSION__))
    click.echo('Developed by {author}, {email}.'.format(author=__AUTHOR__, email=__AUTHOR_EMAIL__))
    ctx.exit()


CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)

_DEFAULT_TASK = 'main'


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True,
              help="Show package's version information.")
@click.option('-s', '--script', type=click.Path(exists=True, readable=True),
              help='Path of pji script.', default=_DEFAULT_FILENAME, show_default=True)
@click.option('-t', '--task', type=str, help='Task going to be executed.',
              default=_DEFAULT_TASK, show_default=True)
@click.option('-e', '--environ', type=str, multiple=True,
              help='Environment variables (loaded before global config).')
@click.option('-E', '--environ_after', type=str, multiple=True,
              help='Environment variables (loaded after global config).')
@click.option('-i', '--information', type=click.Path(dir_okay=False),
              help='Information dump file (no dumping when not given).')
def cli(script: str, task: str, environ: List[str], environ_after: List[str],
        information: Optional[str] = None):
    _dispatch_getter = _load_dispatch_getter(script)
    _success, _result = _dispatch_getter(
        environ=_load_environ(environ),
        environ_after=_load_environ(environ_after),
    )(task)

    if information:
        click.echo(
            click.style('Dumping result of this work to {info} ... '.format(
                info=repr(os.path.abspath(information))), bold=False),
            nl=False,
        )

        with codecs.open(information, 'w') as info_file:
            json.dump(result_to_json(_success, _result), info_file, indent=4, sort_keys=True)

        click.echo(click.style('COMPLETE', fg='green'), nl=True)

    if _success:
        click.echo(click.style('Task success.', fg='green'))
    else:
        click.echo(click.style('Task failed.', fg='red'))
        raise _raise_exception_with_exit_code(1, 'task failed.')
