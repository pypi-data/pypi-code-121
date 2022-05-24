import os

import click
import click_completion
import click_completion.core


def custom_startswith(string, incomplete):
    """A custom completion matching that supports case insensitive matching"""
    if os.environ.get('_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE'):
        string = string.lower()
        incomplete = incomplete.lower()
    return string.startswith(incomplete)


cmd_help = """Shell completion for click-completion-command
Available shell types:
\b
  %s
Default type: auto
""" % "\n  ".join('{:<12} {}'.format(k, click_completion.core.shells[k]) for k in sorted(click_completion.core.shells.keys()))


@click.group(help=cmd_help)
def autocompletion():
    pass


@autocompletion.command(help="To enable command autocompletion in shell")
@click.option('--append/--overwrite', help="Append the completion code to the file", default=None)
@click.option('-i', '--case-insensitive/--no-case-insensitive', help="Case insensitive completion", default=True)
@click.argument('shell', required=False, type=click_completion.DocumentedChoice(click_completion.core.shells))
@click.argument('path', required=False)
def enableautocomplete(append, case_insensitive, shell, path):
    """Install the click-completion-command completion"""
    click.echo('This setup assumes you have bash-completion installed. If not use following links to install and configure. \n1) For ubuntu: https://bit.ly/38Ac0jH \n2) For mac: https://bit.ly/2uRBdYr')
    extra_env = {'_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE': 'ON'} if case_insensitive else {}
    shell, path = click_completion.core.install(shell=shell, path=path, append=append, extra_env=extra_env)
    click.echo('%s completion installed in %s' % (shell, path))
    click.echo('If you already have bash_completion installed make sure following line is present in your ~/.bashrc "[ -f /usr/local/etc/bash_completion ] && . /usr/local/etc/bash_completion" ')