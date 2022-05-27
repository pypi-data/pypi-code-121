import os
from datetime import datetime
from pathlib import PurePath
import re
import natsort
from PyQt5.QtCore import QAbstractItemModel, QAbstractListModel, Qt, QAbstractTableModel
from PyQt5.QtWidgets import QDialog, QHeaderView, QFileIconProvider

from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.gui.templates.customOpenDialogTemplate import Ui_Dialog
from kamzik3.snippets.snippetsUnits import get_printable_size
from kamzik3.snippets.snippetsWidgets import show_error_message


class CategoryModel(QAbstractListModel):
    def __init__(self, model_data):
        self.model_data = list(model_data)
        self.icon_provider = QFileIconProvider()
        QAbstractItemModel.__init__(self)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.model_data)

    def data(self, model_index, role=None):
        if role == Qt.DisplayRole:
            return self.model_data[model_index.row()]
        elif role == Qt.DecorationRole:
            return self.icon_provider.icon(QFileIconProvider.Drive)


class DirContentModel(QAbstractTableModel):
    def __init__(self, model_data):
        self.sorted_by = (0, 1)
        self.model_data_unfiltered = list(model_data)
        self.model_data = list(model_data)
        self.columns = ["Name", "Size", "Modified"]
        self.icon_provider = QFileIconProvider()
        self.filter_regexp = None
        QAbstractTableModel.__init__(self)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.model_data[1]) + len(self.model_data[3])

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.columns)

    def headerData(self, p_int, Qt_Orientation, role=None):
        if role == Qt.DisplayRole and Qt_Orientation == Qt.Horizontal:
            return self.columns[p_int]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            name, (file_size, mod_time) = self.get_item(index)
            if index.column() == 0:
                return name
            elif index.column() == 1:
                return get_printable_size(file_size)
            elif index.column() == 2:
                dt_object = datetime.fromtimestamp(mod_time)
                return str(dt_object.strftime("%d.%m.%Y %H:%M"))
        elif role == Qt.DecorationRole and index.column() == 0:
            if self.is_folder(index):
                return self.icon_provider.icon(QFileIconProvider.Folder)
            else:
                return self.icon_provider.icon(QFileIconProvider.File)

    def is_folder(self, model_index):
        return model_index.row() < len(self.model_data[1])

    def get_item(self, model_index):
        dir_offset = len(self.model_data[1])
        file_index = model_index.row() - dir_offset
        if file_index < 0:
            return (
                self.model_data[1][model_index.row()],
                self.model_data[2][model_index.row()],
            )
        else:
            return self.model_data[3][file_index], self.model_data[4][file_index]

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def sort(self, p_int, order=None):
        if p_int == 0:
            if len(self.model_data[1]) > 0:
                self.model_data[1], self.model_data[2] = zip(
                    *natsort.humansorted(
                        zip(self.model_data[1], self.model_data[2]), reverse=not order
                    )
                )
            if len(self.model_data[3]) > 0:
                self.model_data[3], self.model_data[4] = zip(
                    *natsort.humansorted(
                        zip(self.model_data[3], self.model_data[4]), reverse=not order
                    )
                )
        if p_int == 1:
            if len(self.model_data[3]) > 0:
                self.model_data[3], self.model_data[4] = zip(
                    *sorted(
                        zip(self.model_data[3], self.model_data[4]),
                        reverse=not order,
                        key=lambda x: x[1][0],
                    )
                )
        if p_int == 2:
            if len(self.model_data[1]) > 0:
                self.model_data[1], self.model_data[2] = zip(
                    *sorted(
                        zip(self.model_data[1], self.model_data[2]),
                        reverse=not order,
                        key=lambda x: x[1][1],
                    )
                )
            if len(self.model_data[3]) > 0:
                self.model_data[3], self.model_data[4] = zip(
                    *sorted(
                        zip(self.model_data[3], self.model_data[4]),
                        reverse=not order,
                        key=lambda x: x[1][1],
                    )
                )
        self.sorted_by = (p_int, order)
        self.layoutChanged.emit()

    def name_filter(self, name):
        self.filter_regexp = re.compile(f".*{name}.*")
        self.model_data[3], self.model_data[4] = [], []
        for index, file_name in enumerate(self.model_data_unfiltered[3]):
            if re.search(self.filter_regexp, file_name) is not None:
                self.model_data[3].append(self.model_data_unfiltered[3][index])
                self.model_data[4].append(self.model_data_unfiltered[4][index])
        self.sort(*self.sorted_by)


class CustomOpenDialog(QDialog, Ui_Dialog):
    current_path = None
    current_drive = None
    selected_files = None

    def __init__(self, virtual_directory_device, title="Select file", parent=None):
        self.virtual_directory_device = virtual_directory_device
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(title)

        drives = self.virtual_directory_device.get_value(ATTR_DRIVES)
        category_model = CategoryModel(list(drives.keys()))
        self.input_category.setModel(category_model)
        model_index = category_model.createIndex(0, 0)
        self.input_category.setCurrentIndex(model_index)
        self.slot_drive_changed(model_index)

    def showEvent(self, event):
        button_open = self.buttonBox.button(self.buttonBox.Open)
        button_open.clearFocus()
        button_open.setAutoDefault(False)
        button_open.setDefault(False)
        self.input_file_name.setFocus()

    def slot_file_filter(self):
        table_model = self.table_directory_content.model()
        table_model.name_filter(self.input_file_name.text())

    def slot_drive_changed(self, model_index):
        self.current_drive = model_index.data(Qt.DisplayRole)
        drives = self.virtual_directory_device.get_value(ATTR_DRIVES)
        self.slot_change_path(drives[self.current_drive]["path"])

    def slot_file_selected(self, model_index):
        table_model = self.table_directory_content.model()
        selected_index = table_model.createIndex(model_index.row(), 0)
        filename = table_model.data(selected_index, Qt.DisplayRole)
        if table_model.is_folder(selected_index):
            self.slot_change_path(os.path.join(self.current_path, filename))
        else:
            self.accept()

    def slot_change_path(self, path):
        try:
            path = os.path.normpath(path)
            dir_tree = self.virtual_directory_device.get_dir_content(
                drive=self.current_drive, input_dir=path
            )
            self.current_path = path
            self.set_dir_content(dir_tree)
        except DeviceError:
            show_error_message("Virtual directory device is not ready.", parent=self)

    def slot_dir_up(self):
        new_root_dir = os.path.split(self.current_path)[0]
        self.slot_change_path(new_root_dir)

    def set_dir_content(self, dir_tree):
        current_model = self.table_directory_content.model()
        sorted_by = (0, 1)
        if current_model is not None:
            sorted_by = current_model.sorted_by
        dir_content_model_data = dir_tree
        self.table_directory_content.setModel(DirContentModel(dir_content_model_data))
        self.table_directory_content.model().sort(*sorted_by)
        header = self.table_directory_content.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_directory_content.selectRow(0)
        self.set_navigation()

    def set_navigation(self):
        category_root_path = self.virtual_directory_device.get_value(ATTR_DRIVES)[
            self.current_drive
        ]["path"]
        self.button_up.setDisabled(self.current_path == category_root_path)
        category_root_parts = PurePath(
            self.current_path.replace(category_root_path, "")
        ).parts
        self.input_directory.blockSignals(True)
        self.input_directory.clear()
        paths = [category_root_path]
        for part in category_root_parts[1:]:
            paths.insert(0, os.path.join(paths[0], part))
        self.input_directory.addItems(paths)
        self.input_directory.blockSignals(False)

    def accept(self):
        selected_index = self.table_directory_content.selectedIndexes()[0]
        table_model = self.table_directory_content.model()
        selected_index = table_model.createIndex(selected_index.row(), 0)
        filename = table_model.data(selected_index, Qt.DisplayRole)
        file_path = os.path.join(self.current_path, filename)
        if table_model.is_folder(selected_index):
            self.set_dir_content(self.dir_indexes.get(file_path, 0))
        else:
            self.selected_files = [(self.current_drive, file_path)]
            QDialog.accept(self)
