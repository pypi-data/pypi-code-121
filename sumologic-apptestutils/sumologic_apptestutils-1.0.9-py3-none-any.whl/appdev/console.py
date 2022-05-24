import os
import click
import click_completion.core

os.environ["AWS_REGION"] = os.getenv("AWS_REGION", "us-east-1")
os.environ["SUMO_APP_UTILS_MODE"] = "APPDEV"

from sumoapputils.common.autocomplete import custom_startswith, autocompletion
#initialize the click_completion module
click_completion.core.startswith = custom_startswith
click_completion.init(complete_options=True)

from sumoapputils.appdev.appinstall import appinstallcmd
from sumoapputils.appdev.apptasks import appcmd
from sumoapputils.common.appmanifest import manifestcmd
from sumoapputils.common.initapp import initializeapp
from sumoapputils.appdev.runapptests import apptestcmd
from sumoapputils.appdev.cicdtasks import partnercicdcmd, appdevcicdcmd
from sumoapputils.appdev import __version__

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@initializeapp.command(help="To show cli version. Run pip install --upgrade sumologic-apptestutils for upgrading version")
def version():
    click.echo('Version: ' + __version__)

cmd_sources = [autocompletion, manifestcmd, apptestcmd, initializeapp, appcmd, appinstallcmd]

if os.environ.get("ENABLE_PARTNER_CICD_COMMANDS", None):
    cmd_sources.append(partnercicdcmd)

if os.environ.get("ENABLE_APPDEV_CICD_COMMANDS", None):
    cmd_sources.append(appdevcicdcmd)


apputilscli = click.CommandCollection(sources=cmd_sources, context_settings=CONTEXT_SETTINGS)

if __name__ == '__main__':
    apputilscli()
