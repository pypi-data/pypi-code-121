from PyQt5.QtCore import (
    QAbstractTableModel,
    Qt,
    pyqtSignal,
    pyqtSlot,
    QModelIndex,
    QItemSelection,
)
from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import QWidget

import kamzik3
from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.gui.attributeDeviceDisplayWidget import AttributeDeviceDisplayWidget
from kamzik3.gui.templates.attributeSetpointHistoryTemplate import Ui_Form
from kamzik3.snippets.snippetsUnits import seconds_to_datetime, device_units
from kamzik3.snippets.snippetsWidgets import show_question_dialog, show_error_message


class _view(QAbstractTableModel):
    def __init__(self, parent=None):
        self.model_data = AttributeDeviceDisplayWidget.setpoints_history
        self.header = [
            "Datetime",
            "Device",
            "Attribute",
            "Previous value",
            "New setpoint",
        ]
        QAbstractTableModel.__init__(self, parent)

    # pylint: disable=unused-argument
    def columnCount(self, parent=None):
        return 5

    # pylint: disable=unused-argument
    def rowCount(self, parent=None):
        return len(self.model_data)

    def data(self, index, role=None):
        row, column = index.row(), index.column()

        if role == Qt.DisplayRole:
            if column == 0:
                return "{}".format(
                    seconds_to_datetime(self.model_data[-row - 1][column])
                )
            else:
                return "{}".format(self.model_data[-row - 1][column])
        return None

    def headerData(self, p_int, Qt_Orientation, role=None):
        if role == Qt.DisplayRole and Qt_Orientation == Qt.Horizontal:
            return self.header[p_int]
        elif role == Qt.DisplayRole and Qt_Orientation == Qt.Vertical:
            return p_int + 1
        return None

    def flags(self, index):
        if index.column() <= 2:
            return Qt.ItemIsEnabled
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled


class AttributeSetpointHistoryWidget(Ui_Form, QWidget):
    sigErrorCheck = pyqtSignal("PyQt_PyObject", "PyQt_PyObject")

    def __init__(self, config=None, parent=None):
        QWidget.__init__(self, parent)
        self.config = config
        if config is None:
            self.config = {}
        self.setupUi(self)
        self.table_history_view.doubleClicked.connect(self.on_double_click)
        self.sigErrorCheck.connect(self.slot_check_error)
        self.table_history_view.setModel(_view())
        self.table_history_view.selectionModel().selectionChanged.connect(
            self.current_selection_changed
        )
        self.table_history_view.horizontalHeader().resizeSection(0, 120)
        self.table_history_view.horizontalHeader().resizeSection(3, 200)
        self.button_set_value.setDisabled(True)

    def yaml_mapping(self):
        mapping = super().yaml_mapping()
        del mapping["parent"]
        return mapping

    def set_attribute_value(self):
        try:
            index = self.table_history_view.selectedIndexes()[0]
            row, column = -index.row() - 1, index.column()
            if index.column() >= 3:
                model_data = self.table_history_view.model().model_data
                (
                    _ts,
                    device_id,
                    attribute,
                    _previous_value,
                    _new_setpoint,
                ) = model_data[row]
                question = show_question_dialog(
                    "Do You really want to set {} {} to {} ?".format(
                        device_id, attribute, model_data[row][column]
                    ),
                    parent=self,
                )
                if question:
                    device = kamzik3.session.get_device(device_id)
                    value_in_device_units = device_units(
                        device, attribute, model_data[row][column]
                    )
                    device.set_attribute(
                        attribute + [VALUE],
                        value_in_device_units.m,
                        callback=self.sigErrorCheck.emit,
                    )
        except (KeyError, DeviceError) as e:
            show_error_message(e, parent=self)
        except IndexError:
            show_error_message("Invalid setpoint selection", parent=self)

    @pyqtSlot("PyQt_PyObject", "PyQt_PyObject")
    def slot_check_error(self, attribute, output):
        if attribute == RESPONSE_ERROR:
            show_error_message(output, parent=self)

    @pyqtSlot(QModelIndex)
    def on_double_click(self, index):
        if index.column() >= 3:
            self.set_attribute_value()

    @pyqtSlot(QItemSelection, QItemSelection)
    # pylint: disable=unused-argument
    def current_selection_changed(self, selected, deselected):
        if len(selected) > 0:
            if selected[0].topLeft().column() >= 3:
                self.button_set_value.setEnabled(True)
                return

        self.button_set_value.setEnabled(False)

    def reset(self):
        if show_question_dialog(
            "Do You want to reset setpoint history?",
            title="Reset setpoint history",
            parent=self,
        ):
            AttributeDeviceDisplayWidget.setpoints_history.clear()
            self.refresh()

    @pyqtSlot()
    def refresh(self):
        self.table_history_view.model().layoutChanged.emit()

    def showEvent(self, a0: QShowEvent) -> None:
        self.refresh()
        super().showEvent(a0)
