import json
import logging
import os
import re
import time
from math import ceil
from threading import Lock
from typing import Any, Dict

import pandas as pd
from PyQt5.QtCore import (
    QAbstractTableModel,
    Qt,
    pyqtSlot,
    QModelIndex,
    pyqtSignal,
    QItemSelection,
)
from PyQt5.QtGui import QBrush, QColor, QKeySequence
from PyQt5.QtWidgets import (
    QWidget,
    QColorDialog,
    QHeaderView,
    QShortcut,
    QButtonGroup,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from natsort import humansorted

import kamzik3
from kamzik3 import DeviceError, SEP, session, units
from kamzik3.constants import *
from kamzik3.devices.deviceSavedAttributes import (
    UPDATE_INSERT_GROUPS,
    UPDATE_REMOVE_GROUP,
    UPDATE_INSERT_ROW,
    UPDATE_VALUE,
    UPDATE_REMOVE_ROW,
)
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.templates.savedAttributesTemplate import Ui_Form
from kamzik3.snippets.snippetsUnits import device_units
from kamzik3.snippets.snippetsWidgets import (
    show_question_dialog,
    show_prompt_dialog,
    show_error_message,
)


class ViewModel(QAbstractTableModel):
    sig_value_update = pyqtSignal(int, int, str)
    colors: Dict[Any, Any] = {}

    def __init__(self, model_data, from_index=0, to_index=0, parent=None):
        self.model_data = model_data
        self.from_index = from_index
        self.to_index = to_index
        self.previous_table = None
        QAbstractTableModel.__init__(self, parent)

    # pylint: disable=unused-argument
    def columnCount(self, parent=None):
        columns = self.model_data.columns
        return len(columns) - 1

    # pylint: disable=unused-argument
    def rowCount(self, parent=None):
        display = self.to_index - self.from_index
        return display

    def data(self, index, role=None):
        row, column = index.row(), index.column()
        row += self.from_index + 1
        if role == Qt.DisplayRole:
            if column <= 1:
                return "   " + self.model_data.loc[row][column + 1] + "   "
            else:
                return self.model_data.loc[row][column + 1]
        elif role == Qt.BackgroundRole:
            color = self.model_data.loc[row][0]
            if color not in self.colors:
                self.colors[color] = QBrush(QColor(color))
            return self.colors[color]
        elif role == Qt.EditRole:
            current_value = self.model_data.loc[row][column + 1]
            return current_value
        return None

    def headerData(self, p_int, Qt_Orientation, role=None):
        if role == Qt.DisplayRole and Qt_Orientation == Qt.Horizontal:
            data = self.model_data.columns[p_int + 1]
            return data
        elif role == Qt.DisplayRole and Qt_Orientation == Qt.Vertical:
            return " " + str(self.from_index + p_int + 1) + " "
        return None

    def setData(self, index, value, role=None):
        if role == Qt.EditRole:
            row, column = index.row(), index.column()
            self.sig_value_update.emit(self.from_index + row + 1, column + 1, value)
            return True
        return False

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

        return Qt.ItemIsSelectable | Qt.ItemIsEnabled


class SavedAttributesWidget(Ui_Form, DeviceWidget):
    default_row_color = "#ffffff"
    file_path = None
    page_size = 100
    sig_refresh_group_tables = pyqtSignal(str)
    sig_refresh_group_table = pyqtSignal(bool, str, object)
    displayed_group_path = None
    column_pattern = re.compile(r"(.*) \[(.*)]\[(.*)]")

    def __init__(self, device=None, config=None, parent=None):
        self.rows_selection_mode = False
        self.button_group = QButtonGroup()
        self.update_lock = Lock()
        self.cache_h5_file = os.path.join(
            kamzik3.session.get_value(ATTR_CACHE_DIRECTORY), "client_save.h5"
        )
        self.cache_h5_content = None
        self.groups = {}
        self.logger = logging.getLogger("Gui.Device.SavedAttributeWidget")

        if device is None:
            # pylint: disable=non-parent-init-called
            QWidget.__init__(self, parent)
        else:
            DeviceWidget.__init__(self, device, config=config, parent=parent)

        self.manipulation_buttons = [
            self.button_set_value,
            self.button_change_color,
            self.button_remove,
        ]
        for button in self.manipulation_buttons:
            button.setDisabled(True)

        self.preset_group_buttons = (
            self.combo_preset,
            self.button_remove_preset_group,
            self.button_add_preset_group,
        )
        self.sig_refresh_group_tables.connect(self.slot_refresh_group_tables)
        self.sig_refresh_group_table.connect(self.slot_refresh_group_table)

        self.shortcut_x = QShortcut(QKeySequence("Alt+X"), self)
        self.shortcut_x.activated.connect(self.set_attribute_value)

        self.shortcut_a = QShortcut(QKeySequence("Alt+A"), self)
        self.shortcut_a.activated.connect(self.add_row)

        self.shortcut_d = QShortcut(QKeySequence("Alt+D"), self)
        self.shortcut_d.activated.connect(self.remove_rows)

        self.shortcut_c = QShortcut(QKeySequence("Alt+C"), self)
        self.shortcut_c.activated.connect(self.select_color)

        self.table_attributes.setSelectionBehavior(self.table_attributes.SelectItems)
        self.table_attributes.setSelectionMode(self.table_attributes.SingleSelection)
        self.table_attributes.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.table_attributes.horizontalHeader().setStretchLastSection(True)
        self.table_attributes.doubleClicked.connect(self.on_double_click)

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        if value in READY_DEVICE_STATUSES and not self.configured:
            self.configured = False
            self.slot_handle_configuration()
            self.device.attach_attribute_callback(
                ATTR_LAST_UPDATE, self.content_update, key_filter=VALUE
            )
            with open(self.cache_h5_file, "wb") as h5_fp:
                h5_fp.write(self.device.get_value(ATTR_CONTENT))
            self.device.attach_attribute_callback(
                ATTR_GROUPS, self.groups_changed, key_filter=VALUE
            )
            self.configured = True

    @pyqtSlot(object)
    def groups_changed(self, groups):
        if groups is None:
            return

        selected_item = self.combo_preset.currentText()
        self.combo_preset.clear()
        self.groups = {}
        # Add only top groups to selection
        for group in groups:
            group_path = group.split("/")[1:]
            if group_path[0] not in self.groups:
                self.groups[group_path[0]] = [group_path[1]]
            else:
                self.groups[group_path[0]].append(group_path[1])

        # We want alphabetically sorted group names
        sorted_groups = humansorted(self.groups.keys())
        self.combo_preset.addItems(sorted_groups)
        item_index = self.combo_preset.findText(selected_item)

        # Select group which was previously selected
        if item_index != -1:
            self.combo_preset.setCurrentIndex(item_index)
        else:
            self.combo_preset.setCurrentIndex(0)

    def slot_handle_configuration(self):
        pass

    @pyqtSlot()
    def content_update(self, value):
        if value is None or not self.configured:
            return
        with self.update_lock:
            values = value.split(SEP)
            if values[0] == UPDATE_INSERT_GROUPS:
                groups_data = json.loads(values[1])
                for group, data in groups_data.items():
                    df = pd.DataFrame(data, columns=list(data.keys()))
                    df.to_hdf(
                        self.cache_h5_file, key=group, format="table", complevel=1
                    )
            elif values[0] == UPDATE_REMOVE_GROUP:
                with pd.HDFStore(self.cache_h5_file) as hdf:
                    for group_path in self.device.get_value(ATTR_GROUPS):
                        if group_path.startswith(f"/{values[1]}/"):
                            hdf.remove(group_path)
            elif values[0] == UPDATE_INSERT_ROW:
                group = values[1]
                df = pd.read_hdf(self.cache_h5_file, key=group, mode="a")
                data = json.loads(values[2])
                position = int(values[3])
                line = pd.DataFrame(data, index=[position])
                df2 = pd.concat(
                    [df.iloc[: position - 1], line, df.iloc[position - 1 :]]
                )
                df2.reset_index(drop=True, inplace=True)
                df2.to_hdf(self.cache_h5_file, group, format="fixed")
                subgroup = values[1].split("/")
                if (
                    subgroup[1] == self.combo_preset.currentText()
                    and subgroup[2] == self.button_group.checkedButton().text()
                ):
                    self.sig_refresh_group_table.emit(True, subgroup[-1], df2)
            elif values[0] == UPDATE_VALUE:
                group = values[1]
                df = pd.read_hdf(self.cache_h5_file, key=group, mode="a")
                df.loc[int(values[2]), df.columns[int(values[3])]] = values[4]
                df.to_hdf(self.cache_h5_file, group, format="fixed")
                subgroup = values[1].split("/")
                if (
                    subgroup[1] == self.combo_preset.currentText()
                    and subgroup[2] == self.button_group.checkedButton().text()
                ):
                    self.sig_refresh_group_table.emit(True, subgroup[-1], df)
            elif values[0] == UPDATE_REMOVE_ROW:
                group = values[1]
                df = pd.read_hdf(self.cache_h5_file, key=group, mode="a")
                df.drop(labels=int(values[2]), axis=0, inplace=True)
                df.reset_index(drop=True, inplace=True)
                df.to_hdf(self.cache_h5_file, group, format="fixed")
                subgroup = values[1].split("/")
                if (
                    subgroup[1] == self.combo_preset.currentText()
                    and subgroup[2] == self.button_group.checkedButton().text()
                ):
                    self.sig_refresh_group_table.emit(True, subgroup[-1], df)

    @pyqtSlot(int, int, str)
    def slot_value_update(self, row, column, value):
        top_group = self.combo_preset.currentText()
        for sub_group in self.groups[top_group]:
            group_path = "/".join(("", top_group, sub_group))
            self.device.update_value(
                group=group_path, row=row, column=column, value=value
            )

    @pyqtSlot(QItemSelection, QItemSelection)
    # pylint: disable=unused-argument
    def current_selection_changed(self, selected, deselected):
        if self.rows_selection_mode:
            for button in self.manipulation_buttons + [self.button_add]:
                button.setDisabled(True)
        else:
            self.button_add.setDisabled(False)
            for button in self.manipulation_buttons:
                button.setDisabled(len(selected) == 0)

            if len(selected) > 0:
                if selected[0].topLeft().column() <= 1:
                    self.button_set_value.setDisabled(True)

    @pyqtSlot(QModelIndex)
    # pylint: disable=unused-argument
    def on_double_click(self, index):
        selected_index = self.table_attributes.selectedIndexes()[0]
        if self.checkbox_allow_double_click.isChecked() and selected_index.column() > 0:
            self.set_attribute_value()

    @pyqtSlot()
    def set_attribute_value(self):
        row, column = self.get_selected_cell()
        if column is None or column <= 1:
            return

        attribute_value = self.table_attributes.model().model_data.iloc[row, column]
        column_header = self.table_attributes.model().model_data.columns[column]
        result = self.column_pattern.search(column_header)
        if result is not None:
            try:
                device_id, attribute_name, unit = (
                    result.group(1),
                    result.group(2),
                    result.group(3),
                )
                self.logger.info(
                    f"Set {device_id} {attribute_name} to value {attribute_value} {unit}"
                )
                device = session.get_device(device_id)
                attribute_as_list = eval(f"[{attribute_name}]")
                value_in_device_units = device_units(
                    device, attribute_as_list, units.Quantity(attribute_value, unit)
                )
                device.set_value(attribute_as_list, value_in_device_units.m)
            except (DeviceError, Exception) as e:
                error_message = f"Cannot set {device_id} {attribute_name} to value {attribute_value} {unit}.\r\n{e}"
                show_error_message(error_message, self)

    def get_selected_cell(self):
        selected_index = self.table_attributes.selectedIndexes()
        if not selected_index:
            return None, None
        row = selected_index[0].row()

        if row is not None:
            row_offset = self.table_attributes.model().from_index
            row = row_offset + selected_index[0].row() + 1
            return row, selected_index[0].column() + 1
        else:
            return None, None

    @pyqtSlot()
    def remove_rows(self):
        with self.update_lock:
            row, column = self.get_selected_cell()
            if column is None:
                return

            answer = show_question_dialog(
                f"Do You really want to remove row {row} ?", "Confirmation", self
            )
            if answer:
                top_group = self.combo_preset.currentText()
                self.logger.info(f"Removing row {row} from group {top_group}")
                for sub_group in self.groups[top_group]:
                    group_path = "/".join(("", top_group, sub_group))
                    self.device.remove_row(group=group_path, row=row)

    @pyqtSlot()
    def add_row(self):
        with self.update_lock:
            user_comment = show_prompt_dialog("Type Your comment:", "Add new row", self)
            if user_comment:
                top_group = self.combo_preset.currentText()
                self.logger.info(f"Prepending new row in group {top_group}")
                for sub_group in self.groups[top_group]:
                    group_path = "/".join(("", top_group, sub_group))
                    df = pd.read_hdf(self.cache_h5_file, key=group_path)
                    table_row = [
                        "#fff",
                        time.strftime("%d-%m-%Y %H:%M:%S"),
                        user_comment,
                    ]
                    for column in df.columns[3:]:
                        result = self.column_pattern.search(column)
                        if result is not None:
                            try:
                                device_id, attribute_name, unit = (
                                    result.group(1),
                                    result.group(2),
                                    result.group(3),
                                )
                                attribute_as_list = eval(f"[{attribute_name}]")
                                device = session.get_device(device_id)
                                current_value = (
                                    device.get_attribute(attribute_as_list)
                                    .value()
                                    .to(unit)
                                )
                                table_row.append(current_value.m)
                            except (DeviceError, Exception):
                                table_row.append(None)
                        else:
                            table_row.append(None)
                    table_row = [str(v) for v in table_row]
                    self.device.insert_row(
                        group=group_path,
                        data=dict(zip(df.columns, table_row)),
                        position=2,
                    )

    @pyqtSlot()
    def select_color(self):
        with self.update_lock:
            row, _column = self.get_selected_cell()
            if row is None:
                return

            color = QColorDialog().getColor()
            if color is not None and color.name() != "#000000":
                self.slot_value_update(row, 0, str(color.name()))

    @pyqtSlot()
    def add_preset_group(self):
        with self.update_lock:
            group_name = show_prompt_dialog("Set name of a new group", "New save group")
            if group_name and group_name != "":
                self.logger.info(f"Adding new group {group_name}")
                groups = {}
                top_group = self.combo_preset.currentText()
                for sub_group in self.groups[top_group]:
                    group_path = "/".join(("", top_group, sub_group))
                    new_group_path = "/".join(("", group_name, sub_group))
                    df = pd.read_hdf(self.cache_h5_file, key=group_path)
                    groups[new_group_path] = dict(
                        zip(df.columns, [["None"]] * len(df.columns))
                    )
                self.device.insert_groups(groups_data=groups)

    @pyqtSlot()
    def remove_preset_group(self):
        with self.update_lock:
            current_group = self.combo_preset.currentText()
            answer = show_question_dialog(
                f"Do You really want to remove group {current_group} ?",
                "Confirmation",
                self,
            )
            if answer:
                self.logger.info(f"Removing group {current_group}")
                self.device.remove_group(group=current_group)

    @pyqtSlot("QString")
    def slot_refresh_group_tables(self, top_group):
        """
        Preset group was changed.

        We need to update attribute table.

        :param top_group: name of top group
        :type top_group: string
        """
        if top_group == "":
            return

        self.input_page.blockSignals(True)
        self.input_page.setValue(1)
        self.input_page.blockSignals(False)

        while self.layout_subgroups_select.count() != 0:
            self.layout_subgroups_select.removeItem(
                self.layout_subgroups_select.itemAt(0)
            )
        self.button_group = QButtonGroup()
        for button_index, subgroup in enumerate(self.groups[top_group]):
            button = QPushButton(subgroup)
            button.setStyleSheet(
                "QPushButton {background-color:silver;} QPushButton:checked {background-color:#f6b442;font-weight:bold}"
            )
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setMinimumHeight(30)
            button.toggled.connect(
                lambda state, subgroup=subgroup: self.slot_refresh_group_table(
                    state, subgroup
                )
            )
            self.button_group.addButton(button, button_index)
            self.layout_subgroups_select.addWidget(button)
        self.layout_subgroups_select.addSpacerItem(
            QSpacerItem(0, 0, hPolicy=QSizePolicy.Expanding)
        )
        self.button_group.button(0).setChecked(True)
        self.check_page_borders()

    pyqtSignal(bool, str)
    pyqtSignal(bool, str, object)

    def slot_refresh_group_table(self, state, subgroup, model_data=None):
        if not state:
            return

        row_offset = (self.input_page.value() - 1) * self.page_size
        top_group = self.combo_preset.currentText()
        with self.update_lock:
            if model_data is None:
                model_data = pd.read_hdf(
                    self.cache_h5_file, "/".join([top_group, subgroup])
                )
            row_count = len(model_data.index) - 1
            to_index = (
                (row_offset + self.page_size)
                if row_count >= (row_offset + self.page_size)
                else row_count
            )
            view_model = ViewModel(model_data, from_index=row_offset, to_index=to_index)
            view_model.sig_value_update.connect(self.slot_value_update)
            self.table_attributes.setModel(view_model)
            self.table_attributes.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeToContents
            )
            self.table_attributes.horizontalHeader().setSectionResizeMode(
                1, QHeaderView.Interactive
            )
            self.table_attributes.selectionModel().selectionChanged.connect(
                self.current_selection_changed
            )
            self.input_page.blockSignals(True)
            pages_count = ceil(row_count / self.page_size)
            self.input_page.setMaximum(pages_count if pages_count > 0 else 1)
            self.input_page.blockSignals(False)

    @pyqtSlot()
    def slot_jump_to_first_page(self):
        self.input_page.setValue(1)

    @pyqtSlot()
    def slot_jump_to_last_page(self):
        self.input_page.setValue(self.input_page.maximum())

    @pyqtSlot("int")
    def slot_jump_to_page(self, page_index):
        self.slot_refresh_group_table(True, self.button_group.checkedButton().text())
        self.check_page_borders()

    def check_page_borders(self):
        page_index = self.input_page.value()
        at_max = page_index == self.input_page.maximum()
        at_min = page_index == 1
        self.input_page.setSuffix(f" / {self.input_page.maximum()}")
        self.button_next_page.setDisabled(at_max)
        self.button_last_page.setDisabled(at_max)
        self.button_previous_page.setDisabled(at_min)
        self.button_first_page.setDisabled(at_min)
