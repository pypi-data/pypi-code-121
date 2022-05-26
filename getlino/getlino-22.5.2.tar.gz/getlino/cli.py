# Copyright 2019-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""The main entry point for the :command:`getlino` command.
"""

import click
import distro

from .setup_info import SETUP_INFO

from .configure import configure
from .startsite import startsite
from .startproject import startproject
from .list import list

@click.group(help="""
{}
See https://getlino.lino-framework.org for more information.

This is getlino version {} running on {}.
""".format(SETUP_INFO['description'], SETUP_INFO['version'], distro.name(pretty=True)))
def main():
    pass

main.add_command(configure)
main.add_command(startsite)
main.add_command(startproject)
main.add_command(list)

if __name__ == '__main__':
    main()
    # main(auto_envvar_prefix='GETLINO')
