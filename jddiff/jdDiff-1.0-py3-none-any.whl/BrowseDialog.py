from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox
from .Functions import read_json_file, remove_list_duplicates
from PyQt6.QtCore import QCoreApplication
from typing import Optional
from PyQt6 import uic
import json
import os


class BrowseDialog(QDialog):
    def __init__(self, env):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "BrowseDialog.ui"), self)

        self._env = env

        self.button_browse_original.clicked.connect(self._browse_original_clicked)
        self.button_browse_copy.clicked.connect(self._browse_copy_clicked)

        self.button_ok.clicked.connect(self._ok_clicked)
        self.button_cancel.clicked.connect(self.close)

    def _prepare_edit_fields(self):
        self.edit_original.clear()
        self.edit_copy.clear()

        self.edit_original.addItems(self._current_history["original"])
        self.edit_copy.addItems(self._current_history["copy"])

        self.edit_original.lineEdit().setText("")
        self.edit_copy.lineEdit().setText("")

    def _save_history(self):
        self._current_history["original"] = remove_list_duplicates(self._current_history["original"][:10])
        self._current_history["copy"] = remove_list_duplicates(self._current_history["copy"][:10])

        try:
            os.makedirs(self._env.data_dir)
        except Exception:
            pass

        if self._mode == "file":
            filename = "recentFiles.json"
        elif self._mode == "directory":
            filename = "recentDirectories.json"

        with open(os.path.join(self._env.data_dir, filename), "w", encoding="utf-8") as f:
            json.dump(self._current_history, f, ensure_ascii=False, indent=4)

    def _browse_original_clicked(self) -> None:
        if self._mode == "file":
            path, ok = QFileDialog.getOpenFileName(directory=os.path.dirname(self.edit_original.currentText()))
            if path:
                self.edit_original.lineEdit().setText(path)
        elif self._mode == "directory":
            path = QFileDialog.getExistingDirectory(directory=self.edit_original.currentText())
            if path:
                self.edit_original.lineEdit().setText(path)

    def _browse_copy_clicked(self) -> None:
        if self._mode == "file":
            path, ok = QFileDialog.getOpenFileName(directory=os.path.dirname(self.edit_copy.currentText()))
            if path:
                self.edit_copy.lineEdit().setText(path)
        elif self._mode == "directory":
            path = QFileDialog.getExistingDirectory(directory=self.edit_copy.currentText())
            if path:
                self.edit_copy.lineEdit().setText(path)

    def _ok_clicked(self) -> None:
        if self.edit_original.currentText() == "":
            QMessageBox.critical(self, QCoreApplication.translate("BrowseDialog", "No Original"), QCoreApplication.translate("BrowseDialog", "You have not set a Original path"))
            return
        if self.edit_copy.currentText() == "":
            QMessageBox.critical(self, QCoreApplication.translate("BrowseDialog", "No Copy"), QCoreApplication.translate("BrowseDialog", "You have not set a Copy path"))
            return

        if self.edit_original.currentText() == self.edit_copy.currentText():
            QMessageBox.critical(self, QCoreApplication.translate("BrowseDialog", "Same Paths"), QCoreApplication.translate("BrowseDialog", "Original and Copy have the same Paths"))
            return

        if self._mode == "file":
            for i in [self.edit_original.currentText(), self.edit_copy.currentText()]:
                if not os.path.isfile(i):
                    QMessageBox.critical(self, QCoreApplication.translate("BrowseDialog", "Not a File"), QCoreApplication.translate("BrowseDialog", "{{path}} is not a File").replace("{{path}}", i))
                    return
        elif self._mode == "directory":
            for i in [self.edit_original.currentText(), self.edit_copy.currentText()]:
                if not os.path.isdir(i):
                    QMessageBox.critical(self, QCoreApplication.translate("BrowseDialog", "Not a Directory"), QCoreApplication.translate("BrowseDialog", "{{path}} is not a Directory").replace("{{path}}", i))
                    return

        self._current_history["original"].append(self.edit_original.currentText())
        self._current_history["copy"].append(self.edit_copy.currentText())
        self._save_history()

        self._ok = True
        self.close()

    def get_files(self) -> Optional[list[str]]:
        self.setWindowTitle(QCoreApplication.translate("BrowseDialog", "Select Files"))

        self._current_history = read_json_file(os.path.join(self._env.data_dir, "recentFiles.json"), {"original": [], "copy": []})
        self._prepare_edit_fields()

        self._mode = "file"
        self._ok = False

        self.exec()

        if self._ok:
            return [self.edit_original.currentText(), self.edit_copy.currentText()]
        else:
            return None

    def get_directories(self) -> Optional[list[str]]:
        self.setWindowTitle(QCoreApplication.translate("BrowseDialog", "Select Directories"))

        self._current_history = read_json_file(os.path.join(self._env.data_dir, "recentDirectories.json"), {"original": [], "copy": []})
        self._prepare_edit_fields()

        self._mode = "directory"
        self._ok = False

        self.exec()

        if self._ok:
            return [self.edit_original.currentText(), self.edit_copy.currentText()]
        else:
            return None
