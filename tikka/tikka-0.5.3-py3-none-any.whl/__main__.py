#!/usr/bin/env python3

# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.slots.pyqt.main import PyQtMainApplication

logging.basicConfig(level=logging.DEBUG)


def main():
    """
    Main function for build executable

    [tool.poetry.scripts]
    tikka = "tikka.__main__:main"

    :return:
    """
    # create domain application
    application_ = Application(DATA_PATH)
    # init main application
    PyQtMainApplication(application_)


if __name__ == "__main__":
    main()
