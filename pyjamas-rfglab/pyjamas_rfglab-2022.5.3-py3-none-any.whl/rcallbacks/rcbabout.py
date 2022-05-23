"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys

from PyQt5.QtWidgets import QDialog

import pyjamas.pjscore as pjscore
from pyjamas.dialogs.textdialog import TextDialog
from .rcallback import RCallback

class RCBAbout(RCallback):

    LICENSE_FILE = 'LICENSE'

    def __init__(self, ui: pjscore.PyJAMAS):
        super().__init__(ui)
        file_path: str = __file__
        self.license_path = os.path.join(file_path[:file_path.rfind('rcallbacks')], RCBAbout.LICENSE_FILE)

    def cbAbout(self) -> bool:
        """
        Displays the PyJAMAS license file (contained in LICENSE).

        :return: True.
        """
        if os.path.exists(self.license_path):
            with open(self.license_path) as file:  # Use file to refer to the file object
                text = file.read()
                dialog = TextDialog(f"PyJAMAS {self.pjs.__version__}\n\n" + text, "About")
                dialog.show()

        return True
