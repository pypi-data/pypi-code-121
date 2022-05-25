from PyQt6.QtCore import QCoreApplication, QLocale
from PyQt6.QtWidgets import QDialog, QColorDialog
from .Functions import select_combo_box_data
from .Settings import Settings
from PyQt6 import uic
import os


class SettingsDialog(QDialog):
    def __init__(self, env):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "SettingsDialog.ui"), self)

        self._env = env

        self.box_language.addItem(QCoreApplication.translate("SettingsDialog", "System language"), "default")
        self.box_language.addItem("English", "en")
        for i in os.listdir(os.path.join(env.program_dir, "translations")):
            if i.endswith(".qm"):
                self.box_language.addItem(QLocale.languageToString(QLocale(i.removeprefix("jdDiff_").removesuffix(".qm")).language()), i.removeprefix("jdDiff_").removesuffix(".qm"))

        self.box_sort.addItem(QCoreApplication.translate("SettingsDialog", "Alphabetically ascending"), "alphabeticallyAscending")
        self.box_sort.addItem(QCoreApplication.translate("SettingsDialog", "Alphabetically descending"), "alphabeticallyDescending")
        self.box_sort.addItem(QCoreApplication.translate("SettingsDialog", "Natural ascending"), "naturalAscending")
        self.box_sort.addItem(QCoreApplication.translate("SettingsDialog", "Natural descending"), "naturalDescending")

        self.button_color_added.clicked.connect(self._added_color_clicked)
        self.button_color_removed.clicked.connect(self._removed_color_clicked)
        self.button_reset.clicked.connect(lambda: self._update_widgets(Settings()))
        self.button_ok.clicked.connect(self._ok_clicked)
        self.button_cancel.clicked.connect(self.close)

    def _update_widgets(self, settings: Settings):
        select_combo_box_data(self.box_language, settings.get("language"))
        select_combo_box_data(self.box_sort, settings.get("fileSortAlgorithm"))
        self.button_color_added.setStyleSheet("QPushButton {background-color: " + settings.get("addedColor") + "}")
        self.button_color_removed.setStyleSheet("QPushButton {background-color: " + settings.get("removedColor") + "}")

        self._added_color = settings.get("addedColor")
        self._removed_color = settings.get("removedColor")

    def _added_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.button_color_added.setStyleSheet("QPushButton {background-color: " + color.name() + "}")
            self._added_color = color.name()

    def _removed_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.button_color_removed.setStyleSheet("QPushButton {background-color: " + color.name() + "}")
            self._removed_color = color.name()

    def _ok_clicked(self):
        self._env.settings.set("language", self.box_language.currentData())
        self._env.settings.set("fileSortAlgorithm", self.box_sort.currentData())
        self._env.settings.set("addedColor", self._added_color)
        self._env.settings.set("removedColor", self._removed_color)

        self._env.settings.save(os.path.join(self._env.data_dir, "settings.json"))
        self.close()

    def show_dialog(self):
        self._update_widgets(self._env.settings)
        self.exec()
