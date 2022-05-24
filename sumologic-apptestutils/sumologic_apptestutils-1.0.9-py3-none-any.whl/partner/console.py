import os


import click

import click_completion.core

from sumoapputils.common.autocomplete import custom_startswith, autocompletion

#initialize the click_completion module
click_completion.core.startswith = custom_startswith
click_completion.init(complete_options=True)


os.environ["SUMO_APP_UTILS_MODE"] = "PARTNER"

from sumoapputils.common.appmanifest import manifestcmd
from sumoapputils.common.initapp import initializeapp
from sumoapputils.partner.runapptests import apptestcmd
from sumoapputils.partner import __version__

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@initializeapp.command(help="To show cli version. Run pip install --upgrade sumologic-apptestutils for upgrading version")
def version():
    click.echo('Version: ' + __version__)

cmd_sources = [autocompletion, manifestcmd, apptestcmd, initializeapp]

apputilscli = click.CommandCollection(sources=cmd_sources, context_settings=CONTEXT_SETTINGS)

if __name__ == '__main__':
    apputilscli()
