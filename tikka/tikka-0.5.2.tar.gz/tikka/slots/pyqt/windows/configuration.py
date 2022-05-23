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

from PyQt5.QtWidgets import QApplication, QDialog, QRadioButton, QWidget

from tikka.domains.application import Application
from tikka.domains.config import Config
from tikka.domains.entities.constants import DATA_PATH, LANGUAGES
from tikka.slots.pyqt.resources.gui.windows.configuration_rc import (
    Ui_ConfigurationDialog,
)


class ConfigurationWindow(QDialog, Ui_ConfigurationDialog):
    """
    ConfigurationWindow class
    """

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init configuration window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        # language
        self.language_radio_buttons = {}
        for language_code_name in LANGUAGES:
            self.language_radio_buttons[language_code_name] = QRadioButton()
            if language_code_name == self.application.config.get(Config.LANGUAGE_KEY):
                self.language_radio_buttons[language_code_name].setChecked(True)
            self.language_radio_buttons[language_code_name].setText(
                LANGUAGES[language_code_name]
            )
            self.language_radio_buttons[language_code_name].setObjectName(
                f"languageRadioButton_{language_code_name}"
            )
            self.languageRadioButtonsLayout.addWidget(
                self.language_radio_buttons[language_code_name]
            )

        # currencies
        currency_name_by_code_name = dict(
            zip(
                self.application.currencies.code_names(),
                self.application.currencies.names(),
            )
        )
        self.currency_radio_buttons = {}
        for currency_code_name in currency_name_by_code_name:
            self.currency_radio_buttons[currency_code_name] = QRadioButton()
            if currency_code_name == self.application.config.get(Config.CURRENCY_KEY):
                self.currency_radio_buttons[currency_code_name].setChecked(True)
            self.currency_radio_buttons[currency_code_name].setText(
                self._(currency_name_by_code_name[currency_code_name])
            )
            self.currency_radio_buttons[currency_code_name].setObjectName(
                f"currency_radio_button_{currency_code_name}"
            )
            self.currencyRadioButtonsLayout.addWidget(
                self.currency_radio_buttons[currency_code_name]
            )

        # events
        self.buttonBox.button(self.buttonBox.Save).clicked.connect(self.save)
        self.buttonBox.button(self.buttonBox.Cancel).clicked.connect(self.close)

    def save(self):
        """
        Save configuration

        :return:
        """
        # language
        for language_code_name, radio_button in self.language_radio_buttons.items():
            if (
                radio_button.isChecked()
                and language_code_name
                != self.application.config.get(Config.LANGUAGE_KEY)
            ):
                self.application.select_language(language_code_name)

        for currency_code_name, radio_button in self.currency_radio_buttons.items():
            if (
                radio_button.isChecked()
                and currency_code_name
                != self.application.config.get(Config.CURRENCY_KEY)
            ):
                self.application.select_currency(currency_code_name)

        self.close()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    ConfigurationWindow(application_).exec_()
