# Module to read config from toml file

import os
import argparse
from pathlib import Path
import sys
import toml
from types import SimpleNamespace as SNS


def cmd_params(config):
    """Process command line parameters"""
    parser = argparse.ArgumentParser(description='Record and update finger status')
    parser.add_argument('--no-save', action='store_false', dest='record',
                        help="Don't save status. Push previously saved status.")
    parser.add_argument('--no-push', action='store_false', dest='push',
                        help="Don't push status.")
    parser.add_argument('--skip-check', action='store_true', dest='skip_check',
                        help="Skip check for change in status.")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="Print config info for debugging")

    args = parser.parse_args()

    config.options = SNS()
    config.options.record = args.record
    config.options.push = args.push
    config.options.debug = args.debug
    config.options.skip_check = args.skip_check


def read_config(config):
    """Read configuration file"""
    # Get configuration file $XDG_CONFIG_HOME/push-plan/config.toml
    # $HOME/.config/push-plan/config.toml by default
    xdg_cfg_dir = os.environ.get('XDG_CONFIG_HOME', '~/.config')
    configfile = Path(xdg_cfg_dir).expanduser() / 'push-plan/config.toml'
    config.cfgfile = configfile
    if not configfile.is_file():
        print(f'ERROR: Config file {configfile} not found', file=sys.stderr)
        sys.exit(1)

    tomldata = toml.load(configfile)

    config.user = tomldata['user']
    config.apikey = SNS(cmd=tomldata['commands']['apikey'])

    workfiles = tomldata.get('workfiles', dict())
    planfile = workfiles.get('plan', '~/plan')
    planfile = Path(planfile).expanduser()
    config.plan = SNS(work=SNS(abs=planfile))

    projfile = workfiles.get('project', '~/project')
    projfile = Path(projfile).expanduser()
    config.project = SNS(work=SNS(abs=projfile))

    directories = tomldata.get('directories', dict())
    archive = directories.get('archive', '~/.statuses')
    archive = Path(archive).expanduser()
    config.archive = SNS(abs=archive)

    return config
    
