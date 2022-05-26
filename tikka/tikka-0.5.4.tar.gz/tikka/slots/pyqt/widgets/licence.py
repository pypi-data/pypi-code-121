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
from typing import Optional

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from tikka.domains.application import Application
from tikka.domains.config import Config
from tikka.domains.entities.constants import DATA_PATH, LOCALES_PATH
from tikka.slots.pyqt.resources.gui.widgets.licence_rc import Ui_LicenceWidget


class LicenceWidget(QWidget, Ui_LicenceWidget):
    """
    LicenceWidget class
    """

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init licence widget

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        with open(
            LOCALES_PATH.joinpath(
                application.config.get(Config.LANGUAGE_KEY), "licence_g1.md"
            ),
            "r",
            encoding="utf-8",
        ) as input_file:
            markdown_text = input_file.read()
        self.textBrowser.setMarkdown(markdown_text)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.show()

    main_window.setCentralWidget(LicenceWidget(application_, main_window))

    sys.exit(qapp.exec_())
