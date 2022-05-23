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
from pathlib import Path

from PyQt5.QtCore import QCoreApplication, QLibraryInfo, QLocale, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from tikka.domains.application import Application
from tikka.domains.config import Config
from tikka.interfaces.main import MainApplicationInterface
from tikka.slots.pyqt.windows.main import MainWindow


class PyQtMainApplication(MainApplicationInterface):
    """
    PyQtMainApplication class
    """

    def __init__(
        self, application: Application
    ):  # pylint: disable=super-init-not-called
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            MainApplicationInterface.__init__.__doc__
        )
        qapp = QApplication(sys.argv)

        # qt builtin locales for filedialog or buttonbox...
        QLocale.setDefault(QLocale(application.config.get(Config.LANGUAGE_KEY)))
        translator = QTranslator(qapp)
        filename = "qtbase_" + application.config.get(Config.LANGUAGE_KEY).split("_")[0]
        result = translator.load(
            filename, QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        )
        if result is False:
            raise FileNotFoundError(
                Path(QLibraryInfo.location(QLibraryInfo.TranslationsPath)).joinpath(
                    filename
                )
            )
        QCoreApplication.installTranslator(translator)

        # main window
        qapp.setWindowIcon(QIcon(":/icons/logo"))
        main_window = MainWindow(application)
        main_window.show()

        sys.exit(qapp.exec_())
