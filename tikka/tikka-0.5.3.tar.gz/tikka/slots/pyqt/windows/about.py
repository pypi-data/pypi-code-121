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

import sys
from typing import TYPE_CHECKING, Optional

from PyQt5.QtWidgets import QApplication, QDialog, QWidget

from tikka import __version__
from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.slots.pyqt.resources.gui.windows.about_rc import Ui_AboutDialog

if TYPE_CHECKING:
    import _

AUTHORS = [
    "Vincent Texier",
]


class AboutWindow(QDialog, Ui_AboutDialog):
    """
    AboutWindow class
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Init about window

        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.versionLabel.setText(f"Version {__version__}")
        self.authorListLabel.setText("\n".join(AUTHORS))


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    AboutWindow().exec_()
