import os

import rich_click as click

TEMP_FOLDER = ".servicefoundry_templates"
ENABLE_CLUSTER_COMMANDS = False
ENABLE_AUTHORIZE_COMMANDS = False
ENABLE_SECRETS_COMMANDS = False
HIDE_CLUSTER_COMMANDS = not ENABLE_CLUSTER_COMMANDS
HIDE_AUTHORIZE_COMMANDS = not ENABLE_AUTHORIZE_COMMANDS
HIDE_SECRETS_COMMANDS = not ENABLE_SECRETS_COMMANDS
IS_DEBUG = True if os.getenv("SFY_DEBUG") else False
MAX_WIDTH = 100
DISPLAY_DATETIME_FORMAT = "%d %b %Y %H:%M:%S %Z"

# TODO (chiragjn): This is a hacky solution used while generating docs. Although
#                  this does not cover cases where custom cls class already inherited from rich_click classes
#                  is being used
RICH_CLICK_DISABLED = os.getenv("RICH_CLICK_DISABLED")
GROUP_CLS = click.Group if RICH_CLICK_DISABLED else click.RichGroup
COMMAND_CLS = click.Command if RICH_CLICK_DISABLED else click.RichCommand
