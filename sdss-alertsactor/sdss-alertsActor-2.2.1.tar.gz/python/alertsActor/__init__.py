
import os
import yaml

# Inits the logging system. Only shell logging, and exception and warning catching.
# File logging can be started by calling log.start_file_logger(name).
from .utils import get_logger

# Monkeypatches formatwarning and error handling

import click
import warnings


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):

    basename = os.path.basename(filename)
    category_colour = click.style('[{}]'.format(category.__name__), fg='yellow')

    return '{}: {} ({}:{})\n'.format(category_colour, message, basename, lineno)


warnings.formatwarning = warning_on_one_line

warnings.filterwarnings(
    'ignore', 'Matplotlib is building the font cache using fc-list. This may take a moment.')


log = get_logger('alerts')


# Loads config

if os.path.isfile(os.path.expanduser('~/.alertsConfig.yml')):
    configFile = os.path.expanduser('~/.alertsConfig.yml')
else:
    print("Local config not found! Using default")
    configFile = os.path.join(os.path.dirname(__file__), 'etc/alerts.cfg')

if os.path.isfile(os.path.expanduser("~/.alertActions.yml")):
    actionsFile = os.path.expanduser("~/.alertActions.yml")
else:
    print("Local alert actions not found! Using default")
    actionsFile = os.path.join(os.path.dirname(__file__), 'etc/alertActions.yml')

try:
    config = yaml.load(open(configFile), Loader=yaml.FullLoader)

    alertActions = yaml.load(open(actionsFile), Loader=yaml.UnsafeLoader)
except AttributeError:
    # using pyyaml < 5, enforce old behavior
    config = yaml.load(open(configFile))

    alertActions = yaml.load(open(actionsFile))

__version__ = '2.2.1'
