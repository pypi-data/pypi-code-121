from .Functions import get_sha512_hash, sort_tree_widget_item_child
from PyQt6.QtCore import QThread, QCoreApplication
from PyQt6.QtWidgets import QTreeWidgetItem
import difflib
import html
import os


class CompareTreeItem(QTreeWidgetItem):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.original_html = ""
        self.copy_html = ""
        self.modified = False


def formatDiffLine(line: str, settings) -> str:
    line = line.replace("\n", "")
    line = html.escape(line)
    line = line.replace("\x01", "</span>")
    line = line.replace("\x00+", f'<span style="background-color: {settings.get("addedColor")}">')
    line = line.replace("\x00-", f'<span style="background-color: {settings.get("removedColor")}">')
    line += "<br>"
    return line


class CompareThread(QThread):
    def __init__(self, env):
        QThread.__init__(self)
        self._env = env

    def _compare_files(self, original_path, copy_path: str, item):
        try:
            with open(original_path, "r") as f:
                original_lines = f.readlines()
            with open(copy_path, "r") as f:
                copy_lines = f.readlines()
        except UnicodeDecodeError:
            item.original_html = QCoreApplication.translate("CompareThread", "Can't show diff for binary file")
            item.copy_html = QCoreApplication.translate("CompareThread", "Can't show diff for binary file")
            if get_sha512_hash(original_path) == get_sha512_hash(copy_path):
                item.setText(1, QCoreApplication.translate("CompareThread", "Same"))
                item.modified = False
            else:
                item.setText(1, QCoreApplication.translate("CompareThread", "Modified"))
                item.modified = True
            return

        original_html = "<pre>"
        copy_html = "<pre>"
        for original_diff, copy_diff, c in difflib._mdiff(original_lines, copy_lines):
            original_html += formatDiffLine(original_diff[1], self._env.settings)
            copy_html += formatDiffLine(copy_diff[1], self._env.settings)
        item.original_html = original_html + "</pre>"
        item.copy_html = copy_html + "<pre>"

        if "</span>" in original_html or "</span>" in copy_html:
            item.setText(1, QCoreApplication.translate("CompareThread", "Modified"))
            item.modified = True
        else:
            item.setText(1, QCoreApplication.translate("CompareThread", "Same"))
            item.modified = False
        return

    def _compare_directory(self, internal_path: str, parent_item: CompareTreeItem):
        for i in os.listdir(os.path.join(self._original_path, internal_path)):
            current_item = CompareTreeItem(parent_item)
            current_item.setText(0, i)

            if not os.path.exists(os.path.join(self._copy_path, internal_path, i)):
                current_item.setText(1, QCoreApplication.translate("CompareThread", "Not in Copy"))
                current_item.modified = True
                parent_item.modified = True
                continue

            current_path = os.path.join(self._original_path, internal_path, i)

            if os.path.isfile(current_path):
                self._compare_files(current_path, os.path.join(self._copy_path, internal_path, i), current_item)
            elif os.path.isdir(current_path):
                self._compare_directory(os.path.join(internal_path, i), current_item)

        for i in os.listdir(os.path.join(self._copy_path, internal_path)):
            if not os.path.exists(os.path.join(self._original_path, internal_path, i)):
                current_item = CompareTreeItem(parent_item)
                current_item.setText(0, i)

                current_item.setText(1, QCoreApplication.translate("CompareThread", "Not in Original"))
                current_item.modified = True
                parent_item.modified = True

        if not parent_item.modified:
            for i in range(parent_item.childCount()):
                if parent_item.child(i).modified:
                    parent_item.setText(1, QCoreApplication.translate("CompareThread", "Modified"))
                    parent_item.modified = True
                    break
            else:
                parent_item.setText(1, QCoreApplication.translate("CompareThread", "Same"))
                parent_item.modified = False

        sort_tree_widget_item_child(parent_item, self._env.settings.get("fileSortAlgorithm"))

    def setup(self, original_path: str, copy_path: str):
        self._original_path = original_path
        self._copy_path = copy_path

    def get_root_item(self) -> CompareTreeItem:
        return self._root_item

    def run(self):
        self._root_item = CompareTreeItem()
        self._root_item.setText(0, os.path.basename(self._original_path))

        if os.path.isfile(self._original_path):
            self._compare_files(self._original_path, self._copy_path, self._root_item)
        else:
            self._compare_directory("", self._root_item)
